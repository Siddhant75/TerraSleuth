from PIL import Image
import folium
import pytest

from backend.app.models.case import ClueCategory, GeoCandidate, VisualClue
from frontend.components.geo_map import create_folium_map
from frontend.components.visual_evidence_board import draw_bounding_boxes


def test_draw_bounding_boxes_synthetic_image():
    """Verify Pillow ImageDraw correctly annotates bounding boxes on an image."""
    base_img = Image.new("RGB", (400, 300), color=(50, 50, 50))
    clues = [
        VisualClue(
            category=ClueCategory.ARCHITECTURE,
            description="Basalt waterfront arch",
            bounding_box=[0.1, 0.2, 0.7, 0.8],
            confidence=0.95,
        ),
        VisualClue(
            category=ClueCategory.SIGNAGE,
            description="Devanagari script sign",
            bounding_box=[0.75, 0.3, 0.9, 0.7],
            confidence=0.88,
        ),
    ]

    annotated = draw_bounding_boxes(base_img, clues)

    assert isinstance(annotated, Image.Image)
    assert annotated.size == (400, 300)
    # Ensure image was modified (annotated pixel colors differ from uniform base)
    assert annotated.tobytes() != base_img.tobytes()


def test_draw_bounding_boxes_handles_missing_or_invalid_boxes():
    """Verify bounding box drawer safely skips clues without bounding boxes."""
    base_img = Image.new("RGB", (200, 200), color=(100, 100, 100))
    clues = [
        VisualClue(
            category=ClueCategory.LANDMARK,
            description="Panoramic mountain horizon",
            bounding_box=None,
            confidence=0.7,
        ),
        {"category": "other", "description": "Invalid dict clue", "bounding_box": []},
    ]

    annotated = draw_bounding_boxes(base_img, clues)
    assert isinstance(annotated, Image.Image)
    assert annotated.size == (200, 200)


def test_create_folium_map_with_candidate():
    """Verify creation of a styled Folium map with marker and consensus radius."""
    candidate = GeoCandidate(
        name="Gateway of India",
        address="Apollo Bandar, Colaba, Mumbai",
        latitude=18.9220,
        longitude=72.8347,
        match_score=0.95,
        engine_source="google_maps",
        source_url="https://maps.google.com/?q=18.9220,72.8347",
    )

    m = create_folium_map(candidate, accuracy_radius_meters=200)

    assert isinstance(m, folium.Map)
    assert m.location == [18.9220, 72.8347]

    # Verify rendered HTML contains coordinate markers and popup content
    map_html = m.get_root().render()
    assert "Gateway of India" in map_html
    assert "18.922" in map_html
    assert "72.834" in map_html


def test_create_folium_map_none_candidate_fallback():
    """Verify fallback map creation when candidate is None or has empty coordinates."""
    m = create_folium_map(None)
    assert isinstance(m, folium.Map)
    assert m.location == [20.0, 0.0]


def test_sanitize_url_security():
    """Verify sanitize_url prevents dangerous schemes and XSS injection."""
    from frontend.components.citation_ledger import sanitize_url as ledger_sanitize_url
    from frontend.components.chronology_timeline import sanitize_url as chrono_sanitize_url

    # Dangerous URLs must be rejected
    assert ledger_sanitize_url("javascript:alert(1)") == "#"
    assert chrono_sanitize_url("javascript:alert(1)") is None
    assert ledger_sanitize_url("data:text/html,<script>alert(1)</script>") == "#"
    assert chrono_sanitize_url("file:///etc/passwd") is None

    # Safe HTTP and HTTPS URLs must be permitted
    safe_url = "https://maps.google.com/?q=Mumbai&city=Mumbai"
    assert ledger_sanitize_url(safe_url) == "https://maps.google.com/?q=Mumbai&amp;city=Mumbai"
    assert chrono_sanitize_url(safe_url) == "https://maps.google.com/?q=Mumbai&amp;city=Mumbai"

