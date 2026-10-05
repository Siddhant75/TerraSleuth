import pytest
from backend.app.models.anomaly import AnomalySeverity, AnomalyType
from backend.app.models.case import GeoCandidate, TimelineEvent
from backend.app.services.anomaly_service import AnomalyService


def test_detect_rental_scam_fraud():
    """Verify that a rental listing claim pointing to a Santorini luxury resort triggers fraud detection."""
    resolved_loc = GeoCandidate(
        name="Canaves Oia Suites & Luxury Resort",
        address="Oia, Santorini 847 02, Greece",
        latitude=36.4618,
        longitude=25.3753,
        place_id="ChIJx7-dummy",
        match_score=0.98,
        engine_source="google_maps",
        source_url="https://maps.google.com/?cid=123",
    )
    lens_matches = [
        {
            "title": "Canaves Oia Suites - Luxury Hotel in Santorini",
            "source": "booking.com",
            "link": "https://www.booking.com/hotel/gr/canaves-oia.html",
        }
    ]

    # Case 1: Context hint claims a rental listing in Miami
    anomalies = AnomalyService.detect_anomalies(
        context_hint="Rental listing for luxury beachfront apartment in Miami, Florida",
        image_path="case_market_scam.jpg",
        resolved_location=resolved_loc,
        lens_matches=lens_matches,
    )

    assert len(anomalies) >= 1
    fraud_alert = next((a for a in anomalies if a.anomaly_type == AnomalyType.FRAUDULENT_LISTING), None)
    assert fraud_alert is not None
    assert fraud_alert.severity == AnomalySeverity.CRITICAL
    assert "Santorini" in fraud_alert.authoritative_truth
    assert fraud_alert.confidence >= 0.95


def test_detect_recirculated_disaster_media():
    """Verify that an image claimed to be breaking in 2026 but dating to 2021 is flagged as recirculated."""
    timeline = [
        TimelineEvent(
            date="June 14, 2021",
            title="Severe Flash Flooding Submerges Historic Center",
            source="reuters.com",
            snippet="Record rainfall inundates coastal districts.",
            is_origin=True,
        )
    ]

    anomalies = AnomalyService.detect_anomalies(
        context_hint="Breaking disaster news happening right now in 2026",
        timeline_events=timeline,
    )

    assert len(anomalies) >= 1
    recirc_alert = next((a for a in anomalies if a.anomaly_type == AnomalyType.RECIRCULATED_MEDIA), None)
    assert recirc_alert is not None
    assert recirc_alert.severity == AnomalySeverity.WARNING
    assert "2021" in recirc_alert.title
    assert recirc_alert.confidence >= 0.90


def test_no_anomalies_for_legitimate_landmark():
    """Verify that a legitimate landmark case without conflicting claims triggers zero fraud alerts."""
    resolved_loc = GeoCandidate(
        name="Gateway of India",
        address="Apollo Bunder, Colaba, Mumbai, Maharashtra 400001",
        latitude=18.9220,
        longitude=72.8347,
        match_score=0.96,
        engine_source="google_maps",
    )
    lens_matches = [
        {"title": "Gateway of India - Historic Arch", "source": "en.wikipedia.org"}
    ]
    timeline = [
        TimelineEvent(date="December 4, 1924", title="Inauguration", source="wikipedia.org", snippet="Opened.")
    ]

    anomalies = AnomalyService.detect_anomalies(
        context_hint="Historic archway monument by the waterfront",
        resolved_location=resolved_loc,
        lens_matches=lens_matches,
        timeline_events=timeline,
    )

    assert len(anomalies) == 0
