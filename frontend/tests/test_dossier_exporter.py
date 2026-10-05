from PIL import Image
from backend.app.models.case import CaseFile, GeoCandidate, VisualClue, ClueCategory
from frontend.components.dossier_exporter import (
    generate_standalone_html_dossier,
    image_to_base64_data_uri,
    sanitize_url,
)


def test_sanitize_url():
    """Verify strict URL scheme allowlist neutralizes javascript: and data: URIs."""
    assert sanitize_url("javascript:alert(1)") == "#"
    assert sanitize_url("JAVASCRIPT:alert(document.cookie)") == "#"
    assert sanitize_url("data:text/html,<script>alert(1)</script>") == "#"
    assert sanitize_url("vbscript:msgbox(1)") == "#"
    assert sanitize_url(None) == "#"
    assert sanitize_url("") == "#"
    assert sanitize_url("https://www.google.com/maps") == "https://www.google.com/maps"
    assert sanitize_url("http://example.com/source") == "http://example.com/source"


def test_image_to_base64_data_uri():
    """Verify image conversion to base64 data URI."""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    uri = image_to_base64_data_uri(img)
    assert uri is not None
    assert uri.startswith("data:image/jpeg;base64,")


def test_generate_standalone_html_dossier():
    """Verify standalone HTML report generation contains essential OSINT dossier elements."""
    cf = CaseFile(
        case_id="case_test_99",
        title="Apollo Bunder Landmark",
        case_summary="# Test Summary",
        confidence_score=0.96,
        resolved_location=GeoCandidate(
            name="Gateway of India",
            address="Apollo Bunder, Colaba, Mumbai",
            latitude=18.9220,
            longitude=72.8347,
            match_score=0.96,
            engine_source="google_maps",
            source_url="https://maps.google.com/?cid=123",
        ),
        visual_clues=[
            VisualClue(
                category=ClueCategory.ARCHITECTURE,
                description="Indo-Saracenic basalt arch",
                confidence=0.95,
            )
        ],
        anomalies=[
            {
                "anomaly_type": "fraudulent_listing",
                "severity": "critical",
                "title": "Stolen Asset Detected",
                "description": "Image stolen from hotel.",
                "authoritative_truth": "Santorini Resort",
                "evidence_url": "javascript:alert(1)",  # Untrusted malicious URI
            }
        ],
        serp_queries_executed=4,
    )

    img = Image.new("RGB", (200, 150), color=(10, 20, 30))
    html_output = generate_standalone_html_dossier(cf, target_image=img)

    assert "<!DOCTYPE html>" in html_output
    assert "TERRASLEUTH // CASE FILE #case_test_99" in html_output
    assert "Gateway of India" in html_output
    assert "18.92200°N, 72.83470°E" in html_output
    assert "data:image/jpeg;base64," in html_output
    assert "Stolen Asset Detected" in html_output
    assert "Indo-Saracenic basalt arch" in html_output
    # Neutralizes javascript: URI
    assert 'href="javascript:' not in html_output

