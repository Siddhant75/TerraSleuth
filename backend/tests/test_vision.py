import os
import tempfile
from PIL import Image
import pytest

from backend.app.agent.nodes.scene_deconstructor import scene_deconstructor_node
from backend.app.agent.state import create_initial_osint_state
from backend.app.models.case import ClueCategory
from backend.app.services.vision_service import VisionService, crop_image_region


@pytest.fixture
def synthetic_test_image():
    """Create a temporary synthetic 200x100 pixel test image for cropping tests."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img_path = f.name

    # Create 200x100 RGB image with gradient/colors
    img = Image.new("RGB", (200, 100), color=(255, 0, 0))
    img.save(img_path, "JPEG")

    yield img_path

    if os.path.exists(img_path):
        try:
            os.remove(img_path)
        except OSError:
            pass


def test_crop_image_region_success(synthetic_test_image):
    """Test standard normalized bounding box cropping."""
    # Crop top-left quadrant [ymin=0.0, xmin=0.0, ymax=0.5, xmax=0.5]
    bbox = [0.0, 0.0, 0.5, 0.5]
    out_path = crop_image_region(synthetic_test_image, bbox)

    assert os.path.exists(out_path)
    with Image.open(out_path) as cropped:
        assert cropped.size == (100, 50)  # 50% width (100) and 50% height (50)

    # Clean up output
    if os.path.exists(out_path):
        os.remove(out_path)


def test_crop_image_region_clamping_and_validation(synthetic_test_image):
    """Test coordinate boundaries, clamping, and error handling in cropping."""
    # Inverted bounding box (ymin >= ymax) must raise ValueError
    with pytest.raises(ValueError, match="Invalid bounding box dimensions"):
        crop_image_region(synthetic_test_image, [0.8, 0.2, 0.3, 0.7])

    # Inverted bounding box (xmin >= xmax) must raise ValueError
    with pytest.raises(ValueError, match="Invalid bounding box dimensions"):
        crop_image_region(synthetic_test_image, [0.1, 0.9, 0.5, 0.4])

    # Malformed array length must raise ValueError
    with pytest.raises(ValueError, match="Bounding box must contain exactly 4 coordinates"):
        crop_image_region(synthetic_test_image, [0.1, 0.2, 0.3])

    # Missing image file must raise FileNotFoundError
    with pytest.raises(FileNotFoundError, match="Source image not found"):
        crop_image_region("non_existent_image_xyz_999.jpg", [0.0, 0.0, 1.0, 1.0])


def test_vision_service_golden_case_gateway_mumbai():
    """Verify deterministic deconstruction of Gateway of India Golden Case."""
    service = VisionService()
    clues = service.deconstruct_scene(
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        context_hint="Waterfront monumental arch",
    )

    assert len(clues) == 4
    categories = [c.category for c in clues]
    assert ClueCategory.ARCHITECTURE in categories
    assert ClueCategory.LANDMARK in categories
    assert ClueCategory.SIGNAGE in categories
    assert ClueCategory.INFRASTRUCTURE in categories

    # All bounding boxes must be valid length 4
    for clue in clues:
        assert len(clue.bounding_box) == 4
        assert 0.0 <= clue.confidence <= 1.0


def test_vision_service_golden_case_neuschwanstein():
    """Verify deterministic deconstruction of Neuschwanstein Castle Golden Case."""
    service = VisionService()
    clues = service.deconstruct_scene(
        image_path="case_neuschwanstein.jpg",
        context_hint="Bavarian alpine castle",
    )

    assert len(clues) == 3
    categories = [c.category for c in clues]
    assert ClueCategory.ARCHITECTURE in categories
    assert ClueCategory.VEGETATION in categories
    assert ClueCategory.LANDMARK in categories


def test_vision_service_heuristic_fallback():
    """Verify offline heuristic fallback for unknown images."""
    service = VisionService()
    clues = service.deconstruct_scene(
        image_path="unknown_building.png",
        context_hint="mysterious clock tower",
    )

    assert len(clues) == 2
    assert "mysterious clock tower" in clues[0].description
    assert clues[0].category == ClueCategory.LANDMARK


def test_scene_deconstructor_node_success():
    """Verify scene_deconstructor_node LangGraph node execution."""
    initial_state = create_initial_osint_state(
        image_path="test_mystery_arch.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        context_hint="Historic arch harbor",
    )

    update = scene_deconstructor_node(initial_state)

    assert update["status"] == "deconstructed"
    assert update["error"] is None
    assert len(update["visual_clues"]) == 4


def test_scene_deconstructor_node_missing_image_error():
    """Verify scene_deconstructor_node returns error state when image is completely missing."""
    # State with non-existent local image and no URL
    state = create_initial_osint_state(
        image_path="completely_nonexistent_local_image_xyz.jpg",
        image_url=None,
    )

    update = scene_deconstructor_node(state)

    assert update["status"] == "error"
    assert "Local image file not found" in update["error"]
    assert "visual_clues" not in update  # Did not crash or produce invalid clues
