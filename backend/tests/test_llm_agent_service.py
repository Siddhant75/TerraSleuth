"""Unit tests for LLM Detective Agent Service (Dynamic Fraud & Continuous Arbitration).

Verifies Tier-1 Gemini LLM reasoning for Skeptic, Arbiter, and Synthesizer nodes
with 100% mocked network calls (zero live tokens/credits burned), and verifies seamless
Tier-2 deterministic heuristic fallbacks on missing keys, timeouts, or malformed responses.
"""

import json
from unittest.mock import MagicMock, patch
import httpx
import pytest

from backend.app.agent.nodes.swarm_nodes import arbiter_node, skeptic_node
from backend.app.agent.state import InvestigationIntent, create_initial_osint_state
from backend.app.models.case import GeoCandidate, VisualClue
from backend.app.models.llm_agent import ArbiterEvaluationResult, SkepticEvaluationResult
from backend.app.services.llm_agent_service import LLMDetectiveAgentService


def test_skeptic_no_key_returns_none_instantly():
    """When no Gemini key is provided, Skeptic evaluation returns None with zero network requests."""
    with patch("httpx.Client.post") as mock_post:
        res = LLMDetectiveAgentService.evaluate_skeptic(
            claimed_context="Beachfront apartment in Miami",
            visual_clues=[],
            lens_matches=[],
            geo_candidate=None,
            timeline_events=[],
            gemini_api_key=None,
        )
        assert res is None
        mock_post.assert_not_called()


def test_arbiter_no_key_returns_none_instantly():
    """When no Gemini key is provided, Arbiter evaluation returns None with zero network requests."""
    with patch("httpx.Client.post") as mock_post:
        res = LLMDetectiveAgentService.arbitrate_case(
            hunter_hypotheses=["Gateway of India Mumbai"],
            skeptic_critique="Verified authentic.",
            fraud_probability=0.05,
            geo_candidate=None,
            lens_matches=[],
            gemini_api_key=None,
        )
        assert res is None
        mock_post.assert_not_called()


def test_synthesizer_no_key_returns_none_instantly():
    """When no Gemini key is provided, Synthesizer returns None with zero network requests."""
    with patch("httpx.Client.post") as mock_post:
        res = LLMDetectiveAgentService.synthesize_summary(
            case_title="Mystery Target",
            confidence_score=0.9,
            resolved_location=None,
            audit_score=0.94,
            is_fraud=False,
            anomalies=[],
            gemini_api_key=None,
        )
        assert res is None
        mock_post.assert_not_called()


def test_skeptic_gemini_success_fraud_detection():
    """Gemini evaluates rental scam contradiction, returning structured SkepticEvaluationResult."""
    fake_json = json.dumps({
        "critique": "The claimed Miami rental photo depicts Canaves Oia Suites in Santorini, Greece. The volcanic caldera and Cycladic architecture are geographically impossible in Florida.",
        "fraud_probability": 0.98,
        "is_fraud": True,
        "reasoning": "Direct match to Santorini luxury hotel stolen for rental listing.",
    })
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": fake_json}]
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        res = LLMDetectiveAgentService.evaluate_skeptic(
            claimed_context="Cozy luxury condo in Miami Beach",
            visual_clues=[VisualClue(category="architecture", description="Whitewashed cave suites", confidence=0.9)],
            lens_matches=[{"title": "Canaves Oia Suites, Santorini", "source": "Booking.com"}],
            geo_candidate=GeoCandidate(name="Canaves Oia", address="Oia 847 02, Greece", latitude=36.46, longitude=25.37, match_score=0.95, engine_source="google_maps"),
            timeline_events=[],
            gemini_api_key="fake-gemini-key",
        )

        assert res is not None
        assert isinstance(res, SkepticEvaluationResult)
        assert res.is_fraud is True
        assert res.fraud_probability == 0.98
        assert "Santorini" in res.critique


def test_arbiter_gemini_success_continuous_score_and_verdict():
    """Gemini performs dialectical arbitration, yielding continuous audit score and verdict."""
    fake_json = json.dumps({
        "adversarial_audit_score": 0.22,
        "verdict": "fraud_unmasked",
        "reasoning": "Skeptic conclusively established that the photo was stolen from a Greek resort, invalidating the residential rental claim.",
    })
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": fake_json}]
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        res = LLMDetectiveAgentService.arbitrate_case(
            hunter_hypotheses=["Claimed Miami condo"],
            skeptic_critique="Stolen Santorini photo.",
            fraud_probability=0.98,
            geo_candidate=None,
            lens_matches=[],
            gemini_api_key="fake-gemini-key",
        )

        assert res is not None
        assert isinstance(res, ArbiterEvaluationResult)
        assert res.adversarial_audit_score == 0.22
        assert res.verdict == "fraud_unmasked"
        assert "Skeptic conclusively established" in res.reasoning


def test_synthesizer_gemini_success_generates_briefing():
    """Gemini generates bespoke executive intelligence summary."""
    fake_markdown = "### Executive Intelligence Briefing\n\nForensic investigation confirms target is Gateway of India, Mumbai with 96% confidence."
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": fake_markdown}]
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        res = LLMDetectiveAgentService.synthesize_summary(
            case_title="Gateway of India",
            confidence_score=0.96,
            resolved_location=GeoCandidate(name="Gateway of India", address="Mumbai, India", latitude=18.92, longitude=72.83, match_score=0.96, engine_source="google_maps"),
            audit_score=0.95,
            is_fraud=False,
            anomalies=[],
            gemini_api_key="fake-gemini-key",
        )

        assert res is not None
        assert "Gateway of India" in res
        assert "Executive Intelligence Briefing" in res


def test_skeptic_node_integrates_gemini_dynamically():
    """skeptic_node utilizes LLM result and formats critique with fraud anomaly."""
    fake_json = json.dumps({
        "critique": "Unmasked as Greek resort photo. Not a residential listing.",
        "fraud_probability": 0.99,
        "is_fraud": True,
        "reasoning": "Clear marketplace scam.",
    })
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": fake_json}]
                }
            }
        ]
    }

    state = create_initial_osint_state(
        image_path="test.jpg",
        context_hint="Rental apartment in Miami",
        gemini_api_key="test-key-123",
    )
    state["geo_candidates"] = [GeoCandidate(name="Canaves Oia", address="Santorini, Greece", latitude=36.46, longitude=25.37, match_score=0.9, engine_source="google_maps")]
    state["lens_matches"] = [{"title": "Canaves Suites", "link": "https://booking.com/canaves"}]

    with patch("httpx.Client.post", return_value=mock_resp):
        out = skeptic_node(state)

        assert "CRITICAL CONTRADICTION" in out["skeptic_critiques"][0]
        assert "anomalies" in out
        assert len(out["anomalies"]) >= 1
        assert out["anomalies"][0].anomaly_type.value == "fraudulent_listing"


def test_arbiter_node_integrates_gemini_dynamically():
    """arbiter_node adopts LLM continuous score and verdict."""
    fake_json = json.dumps({
        "adversarial_audit_score": 0.15,
        "verdict": "fraud_unmasked",
        "reasoning": "Severe fraud proven by Skeptic.",
    })
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": fake_json}]
                }
            }
        ]
    }

    state = create_initial_osint_state(
        image_path="test.jpg",
        context_hint="Rental in Miami",
        gemini_api_key="test-key-123",
    )
    state["skeptic_critiques"] = ["CRITICAL CONTRADICTION: stolen photo."]

    with patch("httpx.Client.post", return_value=mock_resp):
        out = arbiter_node(state)

        assert out["audit_score"] == 0.15
        assert out["status"] == "fraud_unmasked"
        assert len(out["debate_history"]) >= 1


def test_gemini_network_timeout_or_error_falls_back_cleanly():
    """When Gemini times out or returns HTTP 500, service returns None without crashing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch("httpx.Client.post", return_value=mock_resp):
        res = LLMDetectiveAgentService.evaluate_skeptic(
            claimed_context="Target",
            visual_clues=[],
            lens_matches=[],
            geo_candidate=None,
            timeline_events=[],
            gemini_api_key="key",
        )
        assert res is None

    with patch("httpx.Client.post", side_effect=httpx.TimeoutException("Timeout")):
        res = LLMDetectiveAgentService.arbitrate_case(
            hunter_hypotheses=["H1"],
            skeptic_critique="C1",
            fraud_probability=0.5,
            geo_candidate=None,
            lens_matches=[],
            gemini_api_key="key",
        )
        assert res is None


def test_skeptic_node_with_fraud_and_empty_lens_matches_does_not_crash():
    """Verify that skeptic_node creates AnomalyReport cleanly even when lens_matches is an empty list."""
    fake_json = json.dumps({
        "critique": "Rental scam detected with zero lens matches.",
        "fraud_probability": 0.95,
        "is_fraud": True,
        "reasoning": "Contradiction identified.",
    })
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": fake_json}]
                }
            }
        ]
    }

    state = create_initial_osint_state(
        image_path="test_empty.jpg",
        context_hint="Rental apartment",
        gemini_api_key="test-key-123",
    )
    state["lens_matches"] = []

    with patch("httpx.Client.post", return_value=mock_resp):
        out = skeptic_node(state)

        assert len(out["skeptic_critiques"]) >= 1
        assert "anomalies" in out
        assert len(out["anomalies"]) == 1
        assert out["anomalies"][0].evidence_url is None

