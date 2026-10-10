"""Unit tests for Multi-Modal Vision LLM Object Detection & HITL Detective Directive.

Verifies Tier-1 Gemini Vision 2D bounding-box spatial detection, user directive
injection, 0-1000 coordinate normalization, and Tier-2 zero-cost OpenCV fallbacks
on timeouts, errors, and absent credentials with 100% mocked network calls.
"""

import json
from unittest.mock import MagicMock, patch
import httpx
import pytest

from backend.app.agent.nodes.swarm_nodes import fashion_hunter_node, hunter_node
from backend.app.agent.state import DetectedObject, InvestigationIntent, create_initial_osint_state
from backend.app.services.object_separation_service import ObjectSeparationService


import os
import tempfile
from PIL import Image, ImageDraw


@pytest.fixture
def sample_image_path():
    """Create a temporary synthetic image for segmentation testing."""
    img = Image.new("RGB", (400, 400), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], fill=(20, 50, 150))
    draw.ellipse([200, 200, 350, 350], fill=(150, 20, 50))

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img.save(f.name)
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_gemini_vision_object_detection_success(sample_image_path):
    """Gemini Vision returns structured JSON array with 2D bounding boxes normalized in [0.0, 1.0]."""
    mock_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps([
                                {
                                    "label": "Dior Saddle Bag",
                                    "category": "accessory",
                                    "box_2d": [0.25, 0.65, 0.45, 0.90],
                                    "confidence": 0.96,
                                },
                                {
                                    "label": "Denim Shirt Dress",
                                    "category": "apparel",
                                    "box_2d": [0.10, 0.15, 0.70, 0.60],
                                    "confidence": 0.98,
                                },
                            ])
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch.object(httpx.Client, "post", return_value=mock_resp) as mock_post:
        objects = ObjectSeparationService.segment_image(
            image_path=sample_image_path,
            gemini_api_key="mock_gemini_key",
        )

        assert mock_post.called
        call_url = mock_post.call_args[0][0]
        call_headers = mock_post.call_args[1]["headers"]
        assert "key=" not in call_url, "API key must not be passed in URL query string"
        assert call_headers.get("x-goog-api-key") == "mock_gemini_key"

        assert len(objects) == 2
        assert objects[0].label == "Dior Saddle Bag"
        assert objects[0].category == "accessory"
        assert objects[0].bounding_box == [0.25, 0.65, 0.45, 0.90]
        assert objects[1].label == "Denim Shirt Dress"


def test_gemini_vision_scale_1000_normalization(sample_image_path):
    """Automatically converts Google 0-1000 integer box coordinates to [0.0, 1.0] floats."""
    mock_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps([
                                {
                                    "label": "Gold Chronograph Watch",
                                    "category": "jewelry",
                                    "box_2d": [350, 620, 480, 800],
                                    "confidence": 0.91,
                                }
                            ])
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch.object(httpx.Client, "post", return_value=mock_resp):
        objects = ObjectSeparationService.segment_image(
            image_path=sample_image_path,
            gemini_api_key="mock_gemini_key",
        )

        assert len(objects) == 1
        assert objects[0].label == "Gold Chronograph Watch"
        assert objects[0].category == "jewelry"
        # 350/1000 = 0.35, 620/1000 = 0.62, 480/1000 = 0.48, 800/1000 = 0.80
        assert pytest.approx(objects[0].bounding_box[0], 0.01) == 0.35
        assert pytest.approx(objects[0].bounding_box[1], 0.01) == 0.62
        assert pytest.approx(objects[0].bounding_box[2], 0.01) == 0.48
        assert pytest.approx(objects[0].bounding_box[3], 0.01) == 0.80


def test_gemini_vision_user_directive_in_prompt(sample_image_path):
    """User mission directive is dynamically injected into the Gemini Vision prompt."""
    mock_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps([
                                {
                                    "label": "Targeted Handbag",
                                    "category": "accessory",
                                    "box_2d": [0.2, 0.2, 0.5, 0.5],
                                    "confidence": 0.95,
                                }
                            ])
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch.object(httpx.Client, "post", return_value=mock_resp) as mock_post:
        ObjectSeparationService.segment_image(
            image_path=sample_image_path,
            user_directive="Focus specifically on the vintage handbag",
            gemini_api_key="mock_gemini_key",
        )

        assert mock_post.called
        payload_data = mock_post.call_args[1]["json"]
        text_prompt = payload_data["contents"][0]["parts"][0]["text"]
        assert "Focus specifically on the vintage handbag" in text_prompt


def test_gemini_vision_timeout_falls_back_to_opencv(sample_image_path):
    """When Gemini Vision times out, seamlessly falls back to OpenCV without throwing."""
    with patch.object(httpx.Client, "post", side_effect=httpx.TimeoutException("Read timeout")):
        objects = ObjectSeparationService.segment_image(
            image_path=sample_image_path,
            gemini_api_key="mock_gemini_key",
        )
        assert isinstance(objects, list)
        assert len(objects) >= 1


def test_gemini_vision_invalid_json_falls_back_to_opencv(sample_image_path):
    """When Gemini Vision returns raw invalid JSON, falls back to OpenCV gracefully."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "I see a dress and some shoes!"}]}}]
    }

    with patch.object(httpx.Client, "post", return_value=mock_resp):
        objects = ObjectSeparationService.segment_image(
            image_path=sample_image_path,
            gemini_api_key="mock_gemini_key",
        )
        assert isinstance(objects, list)
        assert len(objects) >= 1


def test_no_gemini_key_executes_opencv_instantly_with_zero_network_calls(monkeypatch, sample_image_path):
    """With no key, OpenCV executes instantly with zero network calls."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("backend.app.services.object_separation_service.settings.GEMINI_API_KEY", None)
    with patch.object(httpx.Client, "post") as mock_post:
        objects = ObjectSeparationService.segment_image(
            image_path=sample_image_path,
            gemini_api_key=None,
        )
        mock_post.assert_not_called()
        assert isinstance(objects, list)
        assert len(objects) >= 1


def test_hunter_node_filters_selected_object_labels(sample_image_path):
    """hunter_node filters detected objects when selected_object_labels is specified in state."""
    state = create_initial_osint_state(
        image_path=sample_image_path,
        user_directive="Focus on handbag",
        selected_object_labels=["designer_handbag"],
    )
    state["intent"] = InvestigationIntent.FASHION_PRODUCT

    mock_objects = [
        DetectedObject(label="primary_garment", category="apparel", bounding_box=[0.1, 0.1, 0.8, 0.6], confidence=0.9),
        DetectedObject(label="designer_handbag", category="accessory", bounding_box=[0.2, 0.7, 0.5, 0.9], confidence=0.95),
    ]

    with patch.object(ObjectSeparationService, "segment_image", return_value=mock_objects):
        res = hunter_node(state)
        active_objects = res["detected_objects"]
        assert len(active_objects) == 1
        assert active_objects[0].label == "designer_handbag"


def test_fashion_hunter_node_enforces_quota_cap_max_5(sample_image_path):
    """fashion_hunter_node caps regional Google Lens queries to max 5 items to defend quota."""
    mock_objects = [
        DetectedObject(label=f"item_{i}", category="accessory", bounding_box=[0.1, 0.1, 0.2, 0.2], confidence=0.9)
        for i in range(8)
    ]

    state = create_initial_osint_state(
        image_path=sample_image_path,
    )
    state["detected_objects"] = mock_objects

    mock_lens = MagicMock()
    mock_lens.invoke.return_value = {"visual_matches": []}

    with patch("backend.app.agent.nodes.swarm_nodes.tool_lens_search", mock_lens):
        res = fashion_hunter_node(state)
        # Should call tool_lens_search at most 5 times
        assert mock_lens.invoke.call_count <= 5
        assert len(res["itemized_dossier"]) <= 5


def test_hitl_unmatched_label_filter_results_in_zero_quota_burn(sample_image_path):
    """When user provides HITL labels that match none of the detected items, zero searches occur."""
    mock_objects = [
        DetectedObject(label="primary_garment", category="apparel", bounding_box=[0.1, 0.1, 0.8, 0.6], confidence=0.9),
        DetectedObject(label="designer_handbag", category="accessory", bounding_box=[0.2, 0.7, 0.5, 0.9], confidence=0.95),
    ]

    state = create_initial_osint_state(
        image_path=sample_image_path,
        selected_object_labels=["completely_unrelated_item"],
    )
    state["detected_objects"] = mock_objects

    mock_lens = MagicMock()

    with patch("backend.app.agent.nodes.swarm_nodes.tool_lens_search", mock_lens):
        res = fashion_hunter_node(state)
        # No searches should execute because 0 items matched the user's strict selection
        assert mock_lens.invoke.call_count == 0
        assert len(res["itemized_dossier"]) == 0

