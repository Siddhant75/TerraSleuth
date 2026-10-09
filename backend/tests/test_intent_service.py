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


def test_classify_intent_landscape_with_marketplace_link_does_not_false_positive_fashion():
    """Ensure landscape/nature images with general marketplace links (e.g. Etsy maple seeds) route to GEOSPATIAL_LANDMARK."""
    mock_lens_data = {
        "visual_matches": [
            {
                "title": "The sun shining through the leaves of a tree - Free Photo on Unsplash",
                "link": "https://unsplash.com/photos/tree-123",
                "source": "Unsplash",
            },
            {
                "title": "Beautiful Green Spring Tree | Flickr",
                "link": "https://www.flickr.com/photos/stanzim/123",
                "source": "Flickr",
            },
            {
                "title": "Sanzen-in Temple : r/KyotoTravel",
                "link": "https://www.reddit.com/r/KyotoTravel/comments/sanzenin",
                "source": "Reddit",
            },
            {
                "title": "Moonrise full moon japanese maple tree (acer shirasawanum) - Etsy",
                "link": "https://www.etsy.com/listing/1780509550/moonrise-full-moon-japanese-maple-tree",
                "source": "Etsy",
            },
        ]
    }
    intent = IntentClassificationService.classify_intent(mock_lens_data, image_path="tests/live-test/location/test1..jpeg")
    assert intent == InvestigationIntent.GEOSPATIAL_LANDMARK


def test_classify_intent_clothing_on_general_marketplace_classified_as_fashion():
    """Ensure marketplace listings WITH clothing keywords are properly recognized as FASHION_PRODUCT."""
    mock_lens_data = {
        "visual_matches": [
            {
                "title": "Vintage Linen Summer Midi Dress with Pockets - Etsy",
                "link": "https://www.etsy.com/listing/987654/vintage-linen-dress",
                "source": "Etsy",
                "snippet": "Handmade linen dress and outfit wardrobe for women.",
            },
            {
                "title": "Boho Style Women's Clothing and Apparel - Pinterest",
                "link": "https://www.pinterest.com/pin/123456/",
                "source": "Pinterest",
                "snippet": "Trending dresses and accessories.",
            },
        ]
    }
    intent = IntentClassificationService.classify_intent(mock_lens_data)
    assert intent == InvestigationIntent.FASHION_PRODUCT


def test_classify_intent_word_boundaries_prevent_false_positives():
    """Ensure substring matches do NOT trigger false positives (e.g. 'spring' -> 'ring', 'address' -> 'dress')."""
    # 1. "spring season" should NOT trigger FASHION_PRODUCT because of "ring"
    intent1 = IntentClassificationService.classify_intent({}, context_hint="spring season mountain trail")
    assert intent1 == InvestigationIntent.GEOSPATIAL_LANDMARK  # from "mountain" or "trail", not fashion!

    # 2. "network address" should NOT trigger FASHION_PRODUCT because of "dress"
    intent2 = IntentClassificationService.classify_intent({}, context_hint="network ip address setup")
    assert intent2 == InvestigationIntent.GEOSPATIAL_LANDMARK  # fallback, never fashion!

    # 3. "snowflake" should NOT trigger FRAUD_DISINFORMATION because of "fake"
    intent3 = IntentClassificationService.classify_intent({}, context_hint="snowflake on winter pine branch")
    assert intent3 == InvestigationIntent.GEOSPATIAL_LANDMARK

    # 4. "comfortable home" should NOT trigger GEOSPATIAL_LANDMARK because of "fort"
    mock_general_data = {
        "visual_matches": [
            {
                "title": "Comfortable home living room interior design",
                "link": "https://example.com/home-decor",
            }
        ]
    }
    intent4 = IntentClassificationService.classify_intent(mock_general_data, context_hint="comfortable home living room")
    assert intent4 != InvestigationIntent.FRAUD_DISINFORMATION
    assert intent4 != InvestigationIntent.FASHION_PRODUCT


