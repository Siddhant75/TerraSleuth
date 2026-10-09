import os
import tempfile
import numpy as np
from PIL import Image, ImageDraw
import pytest

from backend.app.services.object_separation_service import ObjectSeparationService


def test_segment_synthetic_flatlay_image():
    """Verify segmentation of distinct non-background geometric objects."""
    img = Image.new("RGB", (600, 600), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)

    # 1. Top-left shape (e.g. blue rectangle)
    draw.rectangle([50, 50, 200, 200], fill=(30, 80, 180))
    # 2. Top-right shape (e.g. red circle)
    draw.ellipse([350, 60, 480, 190], fill=(200, 40, 40))
    # 3. Bottom-center shape (e.g. dark oval)
    draw.ellipse([200, 350, 400, 520], fill=(40, 40, 40))

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img.save(f.name)
        temp_path = f.name

    try:
        objects = ObjectSeparationService.segment_image(temp_path, max_objects=5)
        assert len(objects) >= 3, f"Expected at least 3 distinct objects, found {len(objects)}"
        for obj in objects:
            assert len(obj.bounding_box) == 4
            ymin, xmin, ymax, xmax = obj.bounding_box
            assert 0.0 <= ymin < ymax <= 1.0
            assert 0.0 <= xmin < xmax <= 1.0
            assert obj.confidence >= 0.80
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_segment_download_clothing_moodboard():
    """Verify segmentation against real-world test moodboard download (1).jpeg if present."""
    target_path = "tests/live-test/clothing/download (1).jpeg"
    if not os.path.exists(target_path):
        pytest.skip(f"Test moodboard image not found at {target_path}")

    objects = ObjectSeparationService.segment_image(target_path, max_objects=6)
    assert len(objects) >= 5, f"Expected at least 5 segmented items, got {len(objects)}"

    labels = [o.label for o in objects]
    assert any("dress" in l or "garment" in l for l in labels)
    assert any("handbag" in l for l in labels)
    assert any("shoes" in l for l in labels)
    assert any("earrings" in l or "accessory" in l for l in labels)


def test_segment_nonexistent_image_fallback():
    """Verify graceful empty return on missing file."""
    results = ObjectSeparationService.segment_image("nonexistent_path_xyz.jpg")
    assert results == []
