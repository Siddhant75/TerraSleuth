import os
import sys
import pytest
from streamlit.testing.v1 import AppTest

# Ensure repository root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.agent.graph import stream_osint_investigation_sync
from backend.app.db import get_golden_cases, init_db
from backend.app.models.case import CaseFile
from backend.app.services.cache_service import CacheService


@pytest.fixture(autouse=True)
def prime_database():
    """Ensure database and golden cache fixtures are initialized before tests."""
    init_db()
    cache_service = CacheService()
    cache_service.seed_golden_cases()


def test_app_loads_without_exceptions():
    """Verify Streamlit dashboard initializes, runs, and renders without unhandled exceptions."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/app.py"))
    at = AppTest.from_file(app_path, default_timeout=30)
    at.run()

    assert not at.exception, f"App raised unexpected exception: {at.exception}"
    # Verify title or header is rendered
    assert len(at.title) > 0 or len(at.header) > 0 or len(at.markdown) > 0


def test_app_sidebar_configuration():
    """Verify sidebar controls, golden case selector, and parameter sliders render properly."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/app.py"))
    at = AppTest.from_file(app_path, default_timeout=30)
    at.run()

    assert not at.exception
    # Check that sidebar radio button for target mode exists
    assert len(at.sidebar.radio) >= 1
    # Check that sliders for budget and hops exist
    assert len(at.sidebar.slider) >= 2


def test_app_investigation_button_click():
    """Verify clicking the investigation button triggers the investigation workflow cleanly."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/app.py"))
    at = AppTest.from_file(app_path, default_timeout=30)
    at.run()

    assert not at.exception
    # Find the 'Launch Autonomous Investigation' button and click it
    launch_buttons = [b for b in at.button if "Launch Autonomous Investigation" in b.label]
    assert len(launch_buttons) == 1, "Expected 'Launch Autonomous Investigation' button"

    launch_buttons[0].click().run()
    assert not at.exception, f"Investigation triggered exception: {at.exception}"


def test_e2e_streaming_pipeline_golden_case_execution():
    """Verify the multi-agent OSINT pipeline executes end-to-end on a Golden Mystery target."""
    golden_cases = get_golden_cases()
    assert len(golden_cases) >= 1

    case = golden_cases[0]
    steps_received = []
    final_case_file = None

    for event in stream_osint_investigation_sync(
        image_path=case["sample_image_path"],
        image_url=case["sample_image_url"],
        context_hint="Waterfront monument",
        max_budget=8,
    ):
        for node_name, node_output in event.items():
            steps_received.append(node_output.get("status"))
            if node_output.get("final_case_file"):
                final_case_file = node_output["final_case_file"]

    # Assert sequential node progression through the LangGraph OSINT swarm
    assert "deconstructed" in steps_received
    assert "lens_searched" in steps_received
    assert "geo_triangulated" in steps_received
    assert "chrono_audited" in steps_received
    assert "case_closed" in steps_received

    # Assert the final compiled CaseFile meets all OSINT evidentiary requirements
    assert isinstance(final_case_file, CaseFile)
    assert final_case_file.confidence_score > 0.70
    assert final_case_file.resolved_location is not None
    assert final_case_file.resolved_location.latitude is not None
    assert final_case_file.resolved_location.longitude is not None
    assert len(final_case_file.visual_clues) >= 1
    assert len(final_case_file.citations) >= 1
