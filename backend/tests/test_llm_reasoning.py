"""Unit tests for Dynamic LLM-Based Intent & Entity Disambiguation (Hybrid Architecture).

Verifies Tier-1 LLM semantic reasoning across Gemini and OpenAI with 100% mocked
network calls (zero live tokens/credits burned), and verifies seamless Tier-2
deterministic heuristic fallbacks on timeouts, HTTP errors, or missing keys.
"""

from unittest.mock import MagicMock, patch
import httpx
import pytest

from backend.app.agent.nodes.swarm_nodes import hunter_node
from backend.app.agent.state import InvestigationIntent, create_initial_osint_state
from backend.app.models.llm import SemanticDisambiguationResult
from backend.app.services.intent_service import IntentClassificationService
from backend.app.services.llm_reasoning_service import LLMReasoningService


@pytest.fixture
def sample_lens_data():
    return {
        "knowledge_graph": {
            "title": "Sanzen-in Temple",
            "type": "Buddhist temple in Kyoto, Japan",
        },
        "visual_matches": [
            {
                "title": "the sun shining through the leaves of a tree - free photo on unsplash",
                "source": "Unsplash",
                "link": "https://unsplash.com/photos/123",
            },
            {
                "title": "Sanzen-in Temple : r/KyotoTravel",
                "source": "Reddit",
                "link": "https://reddit.com/r/KyotoTravel/comments/abc",
                "snippet": "Visiting Sanzen-in Temple in Ohara, Kyoto in summer.",
            },
            {
                "title": "moonrise full moon japanese maple tree - etsy",
                "source": "Etsy",
                "link": "https://etsy.com/listing/seed-123",
            },
        ],
    }


def test_no_api_key_returns_none_immediately_with_zero_network_calls(sample_lens_data):
    """When no LLM keys are configured, disambiguate returns None immediately without HTTP requests."""
    with patch("httpx.Client.post") as mock_post:
        result = LLMReasoningService.disambiguate(
            lens_data=sample_lens_data,
            gemini_api_key=None,
            openai_api_key=None,
        )
        assert result is None
        mock_post.assert_not_called()


def test_gemini_disambiguate_success(sample_lens_data):
    """When Gemini returns valid JSON, parses into SemanticDisambiguationResult cleanly."""
    gemini_response_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "{\n"
                                '  "intent": "GEOSPATIAL_LANDMARK",\n'
                                '  "primary_entity": "Sanzen-in Temple Kyoto",\n'
                                '  "target_query": "Sanzen-in Temple Kyoto Japan",\n'
                                '  "reasoning": "While match 1 is a stock photo and match 3 is maple seeds, match 2 links the garden and bridge to Sanzen-in Temple.",\n'
                                '  "confidence": 0.96\n'
                                "}"
                            )
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = gemini_response_payload

    with patch.object(httpx.Client, "post", return_value=mock_resp) as mock_post:
        result = LLMReasoningService.disambiguate(
            lens_data=sample_lens_data,
            gemini_api_key="test_gemini_key",
        )

        assert mock_post.called
        call_url, call_kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
        assert "key=" not in call_url, "API key must not be passed in URL query string"
        assert call_kwargs["headers"].get("x-goog-api-key") == "test_gemini_key"

        assert result is not None
        assert isinstance(result, SemanticDisambiguationResult)
        assert result.intent == InvestigationIntent.GEOSPATIAL_LANDMARK
        assert result.primary_entity == "Sanzen-in Temple Kyoto"
        assert result.target_query == "Sanzen-in Temple Kyoto Japan"
        assert result.confidence == 0.96
        assert "Sanzen-in" in result.reasoning


def test_gemini_disambiguate_markdown_code_fence(sample_lens_data):
    """Handles markdown ```json code blocks gracefully."""
    gemini_response_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "```json\n"
                                "{\n"
                                '  "intent": "FASHION_PRODUCT",\n'
                                '  "primary_entity": "Dior Saddle Bag Outfit",\n'
                                '  "target_query": "Dior Saddle Bag Blue Oblique",\n'
                                '  "reasoning": "Fashion wardrobe composition.",\n'
                                '  "confidence": 0.92\n'
                                "}\n"
                                "```"
                            )
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = gemini_response_payload

    with patch.object(httpx.Client, "post", return_value=mock_resp):
        result = LLMReasoningService.disambiguate(
            lens_data=sample_lens_data,
            gemini_api_key="test_gemini_key",
        )
        assert result is not None
        assert result.intent == InvestigationIntent.FASHION_PRODUCT
        assert result.primary_entity == "Dior Saddle Bag Outfit"


def test_gemini_timeout_returns_none(sample_lens_data):
    """Timeout during Gemini call returns None and does not crash."""
    with patch.object(httpx.Client, "post", side_effect=httpx.TimeoutException("Read timed out")):
        result = LLMReasoningService.disambiguate(
            lens_data=sample_lens_data,
            gemini_api_key="test_gemini_key",
        )
        assert result is None


def test_gemini_http_500_returns_none(sample_lens_data):
    """HTTP 500 from Gemini returns None gracefully."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch.object(httpx.Client, "post", return_value=mock_resp):
        result = LLMReasoningService.disambiguate(
            lens_data=sample_lens_data,
            gemini_api_key="test_gemini_key",
        )
        assert result is None


def test_gemini_malformed_json_returns_none(sample_lens_data):
    """Garbage non-JSON response from LLM returns None gracefully."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "I am not returning JSON today!"}]}}]
    }

    with patch.object(httpx.Client, "post", return_value=mock_resp):
        result = LLMReasoningService.disambiguate(
            lens_data=sample_lens_data,
            gemini_api_key="test_gemini_key",
        )
        assert result is None


def test_openai_fallback_success(sample_lens_data):
    """OpenAI fallback executes cleanly when openai_api_key is provided and Gemini key is absent."""
    openai_response_payload = {
        "choices": [
            {
                "message": {
                    "content": (
                        "{\n"
                        '  "intent": "GEOSPATIAL_LANDMARK",\n'
                        '  "primary_entity": "Sanzen-in Temple Kyoto",\n'
                        '  "target_query": "Sanzen-in Temple Kyoto Japan",\n'
                        '  "reasoning": "Matches point to Kyoto garden.",\n'
                        '  "confidence": 0.95\n'
                        "}"
                    )
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = openai_response_payload

    with patch.object(httpx.Client, "post", return_value=mock_resp):
        result = LLMReasoningService.disambiguate(
            lens_data=sample_lens_data,
            openai_api_key="test_openai_key",
        )
        assert result is not None
        assert result.intent == InvestigationIntent.GEOSPATIAL_LANDMARK
        assert result.primary_entity == "Sanzen-in Temple Kyoto"


def test_classify_and_disambiguate_tier1_success(sample_lens_data):
    """classify_and_disambiguate returns LLM fields when Tier-1 succeeds."""
    mock_llm_result = SemanticDisambiguationResult(
        intent=InvestigationIntent.GEOSPATIAL_LANDMARK,
        primary_entity="Sanzen-in Temple Kyoto",
        target_query="Sanzen-in Temple Kyoto Japan",
        reasoning="Semantic deduction from visual matches.",
        confidence=0.97,
    )

    with patch.object(LLMReasoningService, "disambiguate", return_value=mock_llm_result):
        intent, entity, query, reasoning = IntentClassificationService.classify_and_disambiguate(
            lens_data=sample_lens_data,
            gemini_api_key="valid_key",
        )
        assert intent == InvestigationIntent.GEOSPATIAL_LANDMARK
        assert entity == "Sanzen-in Temple Kyoto"
        assert query == "Sanzen-in Temple Kyoto Japan"
        assert "Semantic deduction" in reasoning


def test_classify_and_disambiguate_tier2_heuristic_fallback(sample_lens_data):
    """classify_and_disambiguate seamlessly falls back to heuristics when LLM is unavailable."""
    with patch.object(LLMReasoningService, "disambiguate", return_value=None):
        intent, entity, query, reasoning = IntentClassificationService.classify_and_disambiguate(
            lens_data=sample_lens_data,
            gemini_api_key=None,
        )
        # Should execute deterministic heuristics
        assert intent == InvestigationIntent.GEOSPATIAL_LANDMARK
        assert entity is None
        assert query is None
        assert reasoning is None


def test_hunter_node_adopts_llm_disambiguated_query():
    """hunter_node adopts LLM target_query and records semantic thought when LLM succeeds."""
    mock_llm_result = SemanticDisambiguationResult(
        intent=InvestigationIntent.GEOSPATIAL_LANDMARK,
        primary_entity="Sanzen-in Temple Kyoto",
        target_query="Sanzen-in Temple Kyoto Japan",
        reasoning="Semantic analysis connects garden to Ohara Kyoto.",
        confidence=0.98,
    )

    mock_lens_tool_result = {
        "visual_matches": [
            {
                "title": "the sun shining through the leaves of a tree - free photo on unsplash",
                "source": "Unsplash",
                "link": "https://unsplash.com/photos/123",
            },
            {
                "title": "Sanzen-in Temple : r/KyotoTravel",
                "source": "Reddit",
                "link": "https://reddit.com/r/KyotoTravel/comments/abc",
            },
        ]
    }

    state = create_initial_osint_state(
        image_path="test_image.jpg",
        image_url="https://example.com/test.jpg",
        gemini_api_key="mock_gemini_key",
    )

    mock_lens_tool = MagicMock()
    mock_lens_tool.invoke.return_value = mock_lens_tool_result

    mock_maps_tool = MagicMock()
    mock_maps_tool.invoke.return_value = {
        "candidates": [
            {
                "place_id": "sanzen_in",
                "latitude": 35.1215,
                "longitude": 135.8342,
                "rating": 4.6,
                "title": "Sanzen-in Temple",
                "address": "Ohara, Kyoto, Japan",
            }
        ]
    }

    with patch("backend.app.agent.nodes.swarm_nodes.tool_lens_search", mock_lens_tool), \
         patch.object(LLMReasoningService, "disambiguate", return_value=mock_llm_result), \
         patch("backend.app.agent.nodes.swarm_nodes.tool_maps_triangulate", mock_maps_tool):

        result = hunter_node(state)

        assert result["intent"] == InvestigationIntent.GEOSPATIAL_LANDMARK
        # Check that target_query was passed to Google Maps and candidate created
        candidates = result["geo_candidates"]
        assert len(candidates) >= 1
        assert "Sanzen-in" in candidates[0].name or "Sanzen-in" in candidates[0].address
        # Check that semantic LLM thought was recorded in debate history
        debate = result["debate_history"]
        thought_entries = [d for d in debate if "Semantic LLM Reasoning" in str(d.get("thought", "")) or "Semantic LLM Reasoning" in str(d.get("content", ""))]
        assert len(thought_entries) >= 1
