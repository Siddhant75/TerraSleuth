"""LLM Detective Agent Service for dynamic fraud analysis, dialectical arbitration, and narrative synthesis.

Provides autonomous multi-agent LLM reasoning across Skeptic, Arbiter, and Synthesizer
nodes using Google AI Studio (Gemini 1.5 Flash), while strictly preserving a zero-credit
deterministic fallback when credentials are absent or network requests time out.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
import httpx
from pydantic import ValidationError

from backend.app.config import settings
from backend.app.models.llm_agent import ArbiterEvaluationResult, SkepticEvaluationResult

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

SKEPTIC_SYSTEM_PROMPT = """You are an elite forensic OSINT debunker and adversarial investigator (Skeptic Agent).
Your mission is to cross-examine suspect evidence and identify any fraud, misinformation, geographic impossibilities, architectural contradictions, or media recycling.

You are given:
- User Claimed Context / Caption (e.g. "Residential beachfront rental in Miami")
- Visual Forensic Clues extracted from the photo
- SerpApi Google Lens visual matches & authoritative domains
- SerpApi Google Maps resolved location & coordinates
- SerpApi Google News timeline & historical milestones

Analyze the evidence meticulously:
1. Does the claimed caption contradict the authoritative location? (e.g. Mediterranean caldera architecture in Greece claimed as Miami, Florida)
2. Is this an authentic location, a marketplace vacation rental scam, or recycled viral media?
3. Formulate a sharp, professional forensic critique citing specific evidentiary mismatches.

Respond strictly with valid JSON conforming to this schema:
{
  "critique": "Forensic critique detailing specific contradictions or confirming authenticity.",
  "fraud_probability": 0.95,
  "is_fraud": true,
  "reasoning": "1-2 sentence chain-of-thought rationale."
}
"""

ARBITER_SYSTEM_PROMPT = """You are the Chief Intelligence Arbiter (Lead Detective Judge).
Your mission is to weigh the Hunter agent's affirmative hypothesis against the Skeptic agent's adversarial critique, evaluate all SerpApi proof, and certify the final verdict.

You are given:
- Hunter's proposed geographic / entity hypotheses
- Skeptic's adversarial critique & fraud probability
- SerpApi Google Maps resolution confidence & address
- SerpApi Google Lens visual twin correspondence

Determine:
1. "adversarial_audit_score": A continuous float between 0.0 (total fabrication / malicious fraud) and 1.0 (impeccable verified ground truth).
2. "verdict": Exactly one of:
   - "fraud_unmasked": If Skeptic conclusively exposed a fraudulent rental listing, stolen photo, or disinformation.
   - "debate_certified": If Hunter's hypothesis withstood adversarial scrutiny with strong consensus.
   - "refining_debate": If evidence is genuinely ambiguous, conflicting, and requires further disambiguation.
3. "reasoning": A definitive judicial summary explaining your determination.

Respond strictly with valid JSON conforming to this schema:
{
  "adversarial_audit_score": 0.35,
  "verdict": "fraud_unmasked",
  "reasoning": "Detailed justification weighing Hunter evidence vs Skeptic critique."
}
"""

SYNTHESIZER_SYSTEM_PROMPT = """You are an elite forensic intelligence officer writing the final executive summary for a court-ready OSINT case file.
You are given the certified case facts: target entity, coordinates, visual clues, audit score, and fraud status.

Write a concise, high-impact executive intelligence briefing (2-3 paragraphs in Markdown) summarizing:
1. Primary entity identification and geographic ground truth coordinates.
2. Evidence chain of custody (Google Lens visual twins, Google Maps spatial consensus, Google News archival timeline).
3. Final adjudication (fraud unmasked vs verified authentic landmark).

Write in an authoritative, objective intelligence agency tone. Do NOT wrap in code blocks.
"""


def _mask_key(key: Optional[str]) -> str:
    """Mask API key for safe logging."""
    if not key or len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"


def _clean_json_markdown(text: str) -> str:
    """Clean markdown code fences (```json ... ```) from LLM output."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


class LLMDetectiveAgentService:
    """Autonomous LLM reasoning service for dynamic fraud detection, arbitration, and dossier synthesis."""

    @staticmethod
    def _call_gemini(
        api_key: str,
        system_prompt: str,
        user_prompt: str,
        timeout_seconds: float = 8.0,
    ) -> Optional[str]:
        """Dispatch a single prompt generation request to Google AI Studio Gemini REST endpoint."""
        masked = _mask_key(api_key)
        logger.info("Dispatching LLM agent call to Gemini 1.5 Flash (key: %s)", masked)

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\nEvidence Context:\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1024,
            },
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        }

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(GEMINI_API_URL, json=payload, headers=headers)
                if resp.status_code != 200:
                    logger.warning("Gemini API call failed with status %d: %s", resp.status_code, resp.text[:200])
                    return None

                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return None

                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    return None

                raw_text = parts[0].get("text", "")
                return raw_text.strip() if raw_text else None

        except (httpx.TimeoutException, httpx.RequestError) as exc:
            logger.warning("Gemini API request error / timeout: %s", exc)
            return None
        except Exception as exc:
            logger.warning("Unexpected error during Gemini API request: %s", exc)
            return None

    @classmethod
    def evaluate_skeptic(
        cls,
        claimed_context: Optional[str],
        visual_clues: List[Any],
        lens_matches: List[Dict[str, Any]],
        geo_candidate: Optional[Any],
        timeline_events: List[Any],
        gemini_api_key: Optional[str] = None,
        timeout_seconds: float = 8.0,
    ) -> Optional[SkepticEvaluationResult]:
        """Dynamically evaluate forensic evidence for contradictions and fraud using Gemini."""
        resolved_key = gemini_api_key or os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        if not resolved_key or not resolved_key.strip():
            return None

        # Build context prompt
        evidence_lines = [
            f"- Claimed Context / Caption: {claimed_context or 'None provided (uncaptioned photo)'}",
            f"- Visual Clues: {len(visual_clues)} clues detected",
        ]
        for c in visual_clues[:3]:
            desc = getattr(c, "description", str(c))
            cat = getattr(c, "category", "clue")
            evidence_lines.append(f"  * [{cat}] {desc}")

        evidence_lines.append(f"- Google Lens Matches: {len(lens_matches)} matches")
        for m in lens_matches[:4]:
            t = m.get("title", "Unknown")
            s = m.get("source", "Web")
            evidence_lines.append(f"  * Title: '{t}' (Source: {s})")

        if geo_candidate:
            name = getattr(geo_candidate, "name", "Unknown")
            addr = getattr(geo_candidate, "address", "Unknown")
            lat = getattr(geo_candidate, "latitude", None)
            lon = getattr(geo_candidate, "longitude", None)
            coords = f"{lat}, {lon}" if lat is not None and lon is not None else "Unresolved"
            evidence_lines.append(f"- Google Maps Resolved Place: {name} (Address: {addr}, Coords: {coords})")

        if timeline_events:
            evidence_lines.append(f"- Google News Timeline: {len(timeline_events)} articles verified")
            for ev in timeline_events[:2]:
                title = getattr(ev, "title", str(ev))
                date = getattr(ev, "date", "Archived")
                evidence_lines.append(f"  * [{date}] {title}")

        user_prompt = "\n".join(evidence_lines)

        raw_output = cls._call_gemini(
            api_key=resolved_key.strip(),
            system_prompt=SKEPTIC_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            timeout_seconds=timeout_seconds,
        )
        if not raw_output:
            return None

        try:
            cleaned = _clean_json_markdown(raw_output)
            parsed = json.loads(cleaned)
            return SkepticEvaluationResult(**parsed)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning("Failed to parse Skeptic LLM JSON: %s (raw: %s)", exc, raw_output[:120])
            return None

    @classmethod
    def arbitrate_case(
        cls,
        hunter_hypotheses: List[str],
        skeptic_critique: str,
        fraud_probability: float,
        geo_candidate: Optional[Any],
        lens_matches: List[Dict[str, Any]],
        gemini_api_key: Optional[str] = None,
        timeout_seconds: float = 8.0,
    ) -> Optional[ArbiterEvaluationResult]:
        """Dynamically weigh debate evidence and compute Adversarial Audit Score using Gemini."""
        resolved_key = gemini_api_key or os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        if not resolved_key or not resolved_key.strip():
            return None

        evidence_lines = [
            "- Hunter Hypotheses:",
        ]
        for h in hunter_hypotheses:
            evidence_lines.append(f"  * {h}")

        evidence_lines.append(f"- Skeptic Adversarial Critique:\n  {skeptic_critique}")
        evidence_lines.append(f"- Skeptic Estimated Fraud Probability: {fraud_probability:.2f}")

        if geo_candidate:
            name = getattr(geo_candidate, "name", "Unknown")
            score = getattr(geo_candidate, "match_score", 0.0)
            evidence_lines.append(f"- Google Maps Candidate: {name} (Match Score: {score:.2f})")

        evidence_lines.append(f"- Google Lens Visual Twins: {len(lens_matches)} matches recorded")

        user_prompt = "\n".join(evidence_lines)

        raw_output = cls._call_gemini(
            api_key=resolved_key.strip(),
            system_prompt=ARBITER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            timeout_seconds=timeout_seconds,
        )
        if not raw_output:
            return None

        try:
            cleaned = _clean_json_markdown(raw_output)
            parsed = json.loads(cleaned)
            return ArbiterEvaluationResult(**parsed)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning("Failed to parse Arbiter LLM JSON: %s (raw: %s)", exc, raw_output[:120])
            return None

    @classmethod
    def synthesize_summary(
        cls,
        case_title: str,
        confidence_score: float,
        resolved_location: Optional[Any],
        audit_score: Optional[float],
        is_fraud: bool,
        anomalies: Optional[List[Dict[str, Any]]],
        gemini_api_key: Optional[str] = None,
        timeout_seconds: float = 8.0,
    ) -> Optional[str]:
        """Generate a bespoke executive intelligence summary narrative using Gemini."""
        resolved_key = gemini_api_key or os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        if not resolved_key or not resolved_key.strip():
            return None

        evidence_lines = [
            f"- Case Title: {case_title}",
            f"- Confidence Score: {int(confidence_score * 100)}%",
            f"- Adversarial Audit Score: {int((audit_score or 0.9) * 100)}%",
            f"- Fraud Unmasked: {'YES (CRITICAL CONTRADICTION)' if is_fraud else 'NO (AUTHENTIC LOCATION)'}",
        ]
        if resolved_location:
            name = getattr(resolved_location, "name", "Unknown")
            addr = getattr(resolved_location, "address", "Unknown")
            lat = getattr(resolved_location, "latitude", None)
            lon = getattr(resolved_location, "longitude", None)
            coords = f"{lat}, {lon}" if lat is not None and lon is not None else "Unresolved"
            evidence_lines.append(f"- Geographic Ground Truth: {name} ({addr}) at WGS84 [{coords}]")

        if anomalies:
            evidence_lines.append(f"- Flagged Anomalies: {len(anomalies)} anomalies")
            for a in anomalies:
                evidence_lines.append(f"  * {a.get('title')}: {a.get('description')}")

        user_prompt = "\n".join(evidence_lines)

        return cls._call_gemini(
            api_key=resolved_key.strip(),
            system_prompt=SYNTHESIZER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            timeout_seconds=timeout_seconds,
        )
