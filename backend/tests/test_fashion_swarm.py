import os
import tempfile
from unittest.mock import MagicMock, patch
from PIL import Image, ImageDraw
import pytest

from backend.app.agent.graph import create_dialectical_osint_graph, route_after_hunter
from backend.app.agent.nodes.swarm_nodes import fashion_hunter_node, hunter_node
from backend.app.agent.state import (
    DetectedObject,
    InvestigationIntent,
    create_initial_osint_state,
)


def test_route_after_hunter_branching():
    state_fashion = create_initial_osint_state("test.jpg")
    state_fashion["intent"] = InvestigationIntent.FASHION_PRODUCT
    assert route_after_hunter(state_fashion) == "fashion_hunter"

    state_geo = create_initial_osint_state("test.jpg")
    state_geo["intent"] = InvestigationIntent.GEOSPATIAL_LANDMARK
    assert route_after_hunter(state_geo) == "skeptic"


def test_fashion_hunter_node_quota_cap_and_dossier():
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(b"fake image data")
        temp_img_path = f.name

    try:
        state = create_initial_osint_state(temp_img_path)
        # Supply 7 detected objects to test the hard cap at 5
        state["detected_objects"] = [
            DetectedObject(
                label=f"item_{i}",
                category="apparel" if i == 0 else "accessory",
                bounding_box=[0.1 * i, 0.1 * i, 0.1 * i + 0.1, 0.1 * i + 0.1],
                confidence=0.92,
            )
            for i in range(7)
        ]

        mock_lens_res = {
            "visual_matches": [
                {
                    "title": "Designer Denim Item",
                    "link": "https://fashion.example.com/item",
                    "source": "Fashion Boutique",
                }
            ]
        }

        mock_tool = MagicMock()
        mock_tool.invoke.return_value = mock_lens_res

        with patch("backend.app.agent.nodes.swarm_nodes.tool_lens_search", mock_tool):
            result = fashion_hunter_node(state)

            # Ensure it capped at max 5 items to defend quota
            assert mock_tool.invoke.call_count == 5
            assert len(result["itemized_dossier"]) == 5
            assert len(result["citations"]) == 5
            assert len(result["debate_history"]) == 5
            assert result["status"] == "fashion_analysis_completed"

            top_item = result["itemized_dossier"][0]
            assert top_item["title"] == "Designer Denim Item"
            assert top_item["source"] == "Fashion Boutique"
    finally:
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)


def test_fashion_swarm_end_to_end_pipeline():
    """Verify that a fashion image routes cleanly through the dialectical swarm to case synthesis."""
    # Create a small synthetic image
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 30, 80, 80], fill=(20, 60, 160))

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img.save(f.name)
        temp_img_path = f.name

    try:
        graph = create_dialectical_osint_graph()
        initial_state = create_initial_osint_state(
            image_path=temp_img_path,
            context_hint="Summer dress outfit collection",
            max_budget=8,
        )

        mock_lens_res = {
            "knowledge_graph": {"title": "Summer Denim Dress", "type": "Clothing"},
            "visual_matches": [
                {
                    "title": "Vintage Summer Denim Dress",
                    "link": "https://shein.com/dress",
                    "source": "shein.com",
                    "snippet": "Vintage summer dress.",
                }
            ],
        }

        mock_tool = MagicMock()
        mock_tool.invoke.return_value = mock_lens_res

        with patch("backend.app.agent.nodes.swarm_nodes.tool_lens_search", mock_tool):
            final_state = graph.invoke(initial_state)

            assert final_state["status"] == "case_closed"
            assert final_state["intent"] == InvestigationIntent.FASHION_PRODUCT
            case_file = final_state.get("final_case_file")
            assert case_file is not None
            assert case_file.intent == "FASHION_PRODUCT"
            assert len(case_file.itemized_dossier) > 0
            # Maps triangulation should have been bypassed (resolved_location is None)
            assert case_file.resolved_location is None
            assert case_file.confidence_score >= 0.85
            assert "Itemized Wardrobe" in case_file.case_summary
    finally:
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
