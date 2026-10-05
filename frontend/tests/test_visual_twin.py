import pytest
from PIL import Image

from frontend.components.visual_twin_comparator import (
    calculate_correspondence_score,
    extract_visual_twin_metadata,
)
from frontend.components.swarm_telemetry_terminal import (
    format_terminal_log_entry,
    generate_swarm_terminal_html,
)


def test_calculate_correspondence_score():
    """Verify correspondence score decays predictably with rank and stays within [0.5, 1.0]."""
    score_top = calculate_correspondence_score(rank=0, base_confidence=0.96)
    score_second = calculate_correspondence_score(rank=1, base_confidence=0.96)
    score_third = calculate_correspondence_score(rank=2, base_confidence=0.96)
    
    assert 0.90 <= score_top <= 1.0
    assert score_top >= score_second >= score_third
    assert 0.50 <= score_third <= 1.0


def test_extract_visual_twin_metadata_valid():
    """Verify metadata extraction with full valid match data."""
    match = {
        "title": "Gateway of India - Historic Monument Mumbai",
        "link": "https://en.wikipedia.org/wiki/Gateway_of_India",
        "source": "Wikipedia",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Gateway_of_India.jpg/300px.jpg",
    }
    
    meta = extract_visual_twin_metadata(match, rank=0, base_confidence=0.96)
    
    assert meta["title"] == "Gateway of India - Historic Monument Mumbai"
    assert "wikipedia" in meta["domain"].lower()
    assert meta["has_thumbnail"] is True
    assert meta["thumbnail_url"] == match["thumbnail"]
    assert "Visual Match" in meta["score_label"] or "Visual Correspondence" in meta["score_label"]
    assert meta["link"] == match["link"]


def test_extract_visual_twin_metadata_empty_or_malformed():
    """Verify graceful fallback with None or empty dictionary."""
    meta_none = extract_visual_twin_metadata(None, rank=0)
    assert meta_none["title"] == "No Visual Twin Identified"
    assert meta_none["has_thumbnail"] is False
    assert meta_none["domain"] == "N/A"
    assert meta_none["link"] == "#"

    meta_empty = extract_visual_twin_metadata({}, rank=0)
    assert meta_empty["title"] == "Unspecified Match"
    assert meta_empty["has_thumbnail"] is False
    assert meta_empty["domain"] == "Unknown Domain"


def test_format_terminal_log_entry():
    """Verify timestamped log formatting."""
    entry = format_terminal_log_entry(
        step_name="lens_hunter",
        deduction="Google Lens identified 12 visual twins with authoritative match.",
        timestamp="18:32:05",
    )
    assert "[18:32:05]" in entry
    assert "[LENS_HUNTER]" in entry
    assert "Google Lens identified" in entry


def test_generate_swarm_terminal_html():
    """Verify terminal HTML generation with dark theme hex codes and XSS escaping."""
    logs = [
        "[18:32:01] [SCENE_DECONSTRUCTOR] 4 clues isolated.",
        "[18:32:02] [LENS_HUNTER] Visual match: <script>alert('xss')</script>",
    ]
    html = generate_swarm_terminal_html(logs)
    
    # Must contain high-contrast dark theme tokens
    assert "#090d16" in html
    assert "#1e293b" in html
    assert "terminal-container" in html
    assert "SCENE_DECONSTRUCTOR" in html
    
    # Must be safely escaped
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
