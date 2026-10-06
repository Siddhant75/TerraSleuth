"""Unit tests for Geoguessr UI and Blueprint views.

Validates that component rendering helpers and HTML generation execute cleanly.
"""

from unittest.mock import MagicMock, patch
from backend.app.models.case import CaseFile, GeoCandidate
from frontend.components.blueprint_views import (
    render_implementation_roadmap_view,
    render_screenshot_critique_view,
    render_serpapi_features_view,
)
from frontend.components.geoguessr_view import render_geoguessr_challenge_view


def test_blueprint_views_execute_without_errors():
    """Verify all 3 blueprint showcase tabs render markdown without exceptions."""
    with patch("streamlit.markdown") as mock_md:
        render_screenshot_critique_view()
        assert mock_md.called
        assert "Playwright Visual Audit" in mock_md.call_args[0][0]

    with patch("streamlit.markdown") as mock_md:
        render_serpapi_features_view()
        assert mock_md.called
        assert "SerpApi Multi-Engine Portfolio" in mock_md.call_args[0][0]

    with patch("streamlit.markdown") as mock_md:
        render_implementation_roadmap_view()
        assert mock_md.called
        assert "Execution Roadmap" in mock_md.call_args[0][0]


def test_geoguessr_challenge_view_renders_scorecard():
    """Verify Geoguessr scorecard and 4 tightening stages are rendered."""
    with patch("streamlit.markdown") as mock_md, patch("streamlit.columns") as mock_cols:
        col_mock = MagicMock()
        mock_cols.return_value = [col_mock, col_mock, col_mock, col_mock]

        render_geoguessr_challenge_view(
            guess_lat=18.92200,
            guess_lon=72.83470,
            truth_lat=18.92198,
            truth_lon=72.83465,
            target_name="Gateway of India",
        )

        assert mock_md.called
        # Check that score card markdown was emitted
        emitted_html = "".join(str(call[0][0]) for call in mock_md.call_args_list if call[0])
        assert "AUTONOMOUS GEOGUESSR OSINT CHALLENGE" in emitted_html
        assert "5,000 / 5,000 PTS" in emitted_html
        assert "Distance Error" in emitted_html


def test_geoguessr_challenge_view_handles_none_coords():
    """Verify graceful handling when coordinates are None."""
    with patch("streamlit.info") as mock_info:
        render_geoguessr_challenge_view(
            guess_lat=None,
            guess_lon=None,
            truth_lat=18.9220,
            truth_lon=72.8347,
        )
        assert mock_info.called
        assert "coordinates missing" in mock_info.call_args[0][0]
