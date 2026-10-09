import time
import pytest

from backend.app.agent.state import InvestigationIntent
from backend.app.services.intent_service import IntentClassificationService


def test_classify_intent_fashion_domain_and_keywords():
    mock_lens_data = {
        "knowledge_graph": {
            "title": "Summer Denim Midi Dress",
            "type": "Clothing",
        },
        "visual_matches": [
            {
                "title": "SHEIN MOD Women's Vintage Denim Dress",
                "link": "https://www.shein.com/women-vintage-denim-dress-p-12345.html",
                "source": "SHEIN",
                "snippet": "Shop Women's Vintage Denim Dress with front buttons and pockets.",
            },
            {
                "title": "Zara Retro Blue Jean Skirt Outfit",
                "link": "https://www.zara.com/us/en/retro-blue-jean-outfit-p04.html",
                "source": "ZARA",
                "snippet": "Trending summer apparel collection.",
            },
        ],
    }

    start = time.perf_counter()
    intent = IntentClassificationService.classify_intent(mock_lens_data)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert intent == InvestigationIntent.FASHION_PRODUCT
    assert elapsed_ms < 25.0, f"Intent classification should be ultra-fast (<25ms), got {elapsed_ms:.2f}ms"


def test_classify_intent_geospatial_landmark():
    mock_lens_data = {
        "knowledge_graph": {
            "title": "Gateway of India",
            "type": "Monument in Mumbai, India",
        },
        "visual_matches": [
            {
                "title": "Gateway of India - Wikipedia",
                "link": "https://en.wikipedia.org/wiki/Gateway_of_India",
                "source": "Wikipedia",
                "snippet": "The Gateway of India is an arch-monument built to commemorate the landing of King George V in Bombay.",
            },
            {
                "title": "Apollo Bunder Waterfront - TripAdvisor",
                "link": "https://www.tripadvisor.com/Attraction_Review-Gateway_of_India.html",
                "source": "Tripadvisor",
                "snippet": "Historic landmark overlooking the Arabian Sea.",
            },
        ],
    }

    intent = IntentClassificationService.classify_intent(mock_lens_data)
    assert intent == InvestigationIntent.GEOSPATIAL_LANDMARK


def test_classify_intent_fraud_signals():
    mock_lens_data = {
        "visual_matches": [
            {
                "title": "Luxury Cliffside Villa in Santorini - Booking.com",
                "link": "https://www.booking.com/hotel/gr/santorini-villa.html",
                "source": "Booking.com",
                "snippet": "5-star cliffside resort in Oia, Santorini, Greece.",
            }
        ]
    }

    intent = IntentClassificationService.classify_intent(
        mock_lens_data, context_hint="Rental scam inquiry: Beachfront house in Miami"
    )
    assert intent == InvestigationIntent.FRAUD_DISINFORMATION


def test_classify_intent_fallback_to_geospatial_on_empty():
    intent = IntentClassificationService.classify_intent({})
    assert intent == InvestigationIntent.GEOSPATIAL_LANDMARK
