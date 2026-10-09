"""LLM Semantic Reasoning Service for dynamic intent & entity disambiguation.

Provides Tier-1 semantic agentic reasoning over Google Lens visual matches
with Google AI Studio (Gemini) and OpenAI, preserving zero-credit deterministic
fallback when credentials are absent or network requests time out.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
import httpx
from pydantic import ValidationError

from backend.app.config import settings
from backend.app.agent.state import InvestigationIntent
from backend.app.models.llm import SemanticDisambiguationResult

logger = logging.getLogger(__name__)

DISAMBIGUATION_SYSTEM_PROMPT = """You are an elite OSINT (Open Source Intelligence) and Geolocation Detective.
You are given visual reverse-image search metadata returned from Google Lens for an uncaptioned mystery image:
- User context hint (if provided)
- Google Lens Knowledge Graph title and type (if present)
- Top visual match titles, source domains, and snippets

Your task is to analyze these visual matches and deduce:
1. "intent": Exactly one of:
   - "GEOSPATIAL_LANDMARK": A physical place, building, landscape, street, monument, temple, church, park, or geographic location.
   - "FASHION_PRODUCT": An outfit, piece of clothing, shoes, handbag, watch, jewelry, or wearable accessory.
   - "FRAUD_DISINFORMATION": A suspicious vacation rental listing, manipulated media, stolen photo, or fraud scam.
   - "GENERAL_OBJECT": A vehicle, plant, animal, tool, artwork, food, or miscellaneous object not tied to a landmark.

2. "primary_entity": The genuine, specific named entity represented by the image (e.g. "Sanzen-in Temple Kyoto", "Gateway of India", "Dior Saddle Bag", "Neuschwanstein Castle").
   CRITICAL: Filter out generic stock photography captions (e.g. "The sun shining through leaves", "Free HD Wallpaper") and commercial seed/plant marketplace noise (e.g. Etsy seed listings).

3. "target_query": The optimal search query to locate this place on Google Maps or find the exact item (e.g. "Sanzen-in Temple Kyoto Japan").

4. "reasoning": A concise 1-2 sentence chain-of-thought rationale explaining why you selected this entity and intent over other matches.

5. "confidence": A float between 0.0 and 1.0 indicating your confidence.

Respond strictly with valid JSON conforming to this schema:
{
  "intent": "GEOSPATIAL_LANDMARK",
  "primary_entity": "Sanzen-in Temple Kyoto",
  "target_query": "Sanzen-in Temple Kyoto Japan",
  "reasoning": "...",
  "confidence": 0.95
}
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


class LLMReasoningService:
    """Multi-provider LLM reasoner for semantic intent & entity disambiguation."""

    @staticmethod
    def disambiguate(
        lens_data: Dict[str, Any],
        context_hint: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        timeout_seconds: float = 8.0,
    ) -> Optional[SemanticDisambiguationResult]:
        """Disambiguate visual matches using an LLM if credentials are present.
        
        Returns None if credentials are missing or if any network / parse errors occur,
        allowing seamless fallback to deterministic heuristics.
        """
        resolved_gemini_key = gemini_api_key or os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        resolved_openai_key = openai_api_key or os.environ.get("OPENAI_API_KEY") or settings.OPENAI_API_KEY

        # If no LLM credentials configured, immediately return None without network calls
        if not resolved_gemini_key and not resolved_openai_key:
            logger.debug("No LLM API keys provided; skipping semantic LLM disambiguation.")
            return None

        # Build prompt evidence from Lens data
        user_prompt = LLMReasoningService._build_evidence_prompt(lens_data, context_hint)

        # 1. Prefer Gemini (Google AI Studio)
        if resolved_gemini_key and resolved_gemini_key.strip():
            result = LLMReasoningService._call_gemini(
                api_key=resolved_gemini_key.strip(),
                system_prompt=DISAMBIGUATION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                timeout_seconds=timeout_seconds,
            )
            if result:
                return result

        # 2. Fallback to OpenAI if configured
        if resolved_openai_key and resolved_openai_key.strip():
            result = LLMReasoningService._call_openai(
                api_key=resolved_openai_key.strip(),
                system_prompt=DISAMBIGUATION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                timeout_seconds=timeout_seconds,
            )
            if result:
                return result

        return None

    @staticmethod
    def _build_evidence_prompt(lens_data: Dict[str, Any], context_hint: Optional[str]) -> str:
        """Format Google Lens metadata into an evidence payload for the LLM."""
        lines = []
        if context_hint:
            lines.append(f"Context Hint: {context_hint}")

        kg = lens_data.get("knowledge_graph") or {}
        if kg:
            kg_title = kg.get("title", "")
            kg_type = kg.get("type", "")
            lines.append(f"Google Lens Knowledge Graph: Title='{kg_title}', Type='{kg_type}'")

        visual_matches = lens_data.get("visual_matches") or []
        lines.append(f"\nTop Google Lens Visual Matches ({len(visual_matches[:12])} shown):")
        for i, m in enumerate(visual_matches[:12], 1):
            title = m.get("title", "No Title")
            source = m.get("source", "Unknown")
            link = m.get("link", "")
            snippet = m.get("snippet", "")
            lines.append(f"{i}. Title: \"{title}\" | Source: {source} | Link: {link}")
            if snippet:
                lines.append(f"   Snippet: \"{snippet}\"")

        return "\n".join(lines)

    @staticmethod
    def _call_gemini(
        api_key: str,
        system_prompt: str,
        user_prompt: str,
        timeout_seconds: float = 8.0,
    ) -> Optional[SemanticDisambiguationResult]:
        """Call Google AI Studio Gemini API via REST with structured JSON response."""
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        }
        logger.debug("Dispatching Gemini semantic disambiguation with key %s", _mask_key(api_key))
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\nEvidence:\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    logger.warning(
                        "Gemini API returned status %d: %s",
                        resp.status_code,
                        resp.text[:200],
                    )
                    return None

                data = resp.json()
                candidates = data.get("candidates") or []
                if not candidates:
                    return None

                text_content = (
                    candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                )
                return LLMReasoningService._parse_result(text_content, provider="Gemini")

        except httpx.TimeoutException:
            logger.warning("Gemini semantic disambiguation timed out after %.1fs", timeout_seconds)
            return None
        except Exception as e:
            logger.warning("Gemini semantic disambiguation request failed: %s", str(e))
            return None

    @staticmethod
    def _call_openai(
        api_key: str,
        system_prompt: str,
        user_prompt: str,
        timeout_seconds: float = 8.0,
    ) -> Optional[SemanticDisambiguationResult]:
        """Call OpenAI chat completion API via REST with JSON mode."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        logger.debug("Dispatching OpenAI semantic disambiguation with key %s", _mask_key(api_key))
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    logger.warning(
                        "OpenAI API returned status %d: %s",
                        resp.status_code,
                        resp.text[:200],
                    )
                    return None

                data = resp.json()
                choices = data.get("choices") or []
                if not choices:
                    return None

                text_content = choices[0].get("message", {}).get("content", "")
                return LLMReasoningService._parse_result(text_content, provider="OpenAI")

        except httpx.TimeoutException:
            logger.warning("OpenAI semantic disambiguation timed out after %.1fs", timeout_seconds)
            return None
        except Exception as e:
            logger.warning("OpenAI semantic disambiguation request failed: %s", str(e))
            return None

    @staticmethod
    def _parse_result(raw_text: str, provider: str) -> Optional[SemanticDisambiguationResult]:
        """Parse and validate JSON into SemanticDisambiguationResult."""
        cleaned = _clean_json_markdown(raw_text)
        try:
            parsed = json.loads(cleaned)
            # Ensure intent string matches enum
            raw_intent = str(parsed.get("intent", "")).upper()
            if hasattr(InvestigationIntent, raw_intent):
                parsed["intent"] = InvestigationIntent[raw_intent]
            elif raw_intent in [i.value for i in InvestigationIntent]:
                parsed["intent"] = InvestigationIntent(raw_intent)
            else:
                parsed["intent"] = InvestigationIntent.GEOSPATIAL_LANDMARK

            result = SemanticDisambiguationResult(**parsed)
            logger.info(
                "[%s Semantic Reasoner] Disambiguated intent=%s, entity='%s', query='%s' (conf=%.2f)",
                provider,
                result.intent.value,
                result.primary_entity,
                result.target_query,
                result.confidence,
            )
            return result
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning("[%s] Failed to parse semantic disambiguation response: %s", provider, str(e))
            return None
