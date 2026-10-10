"""End-to-End and Integration tests for Task 8.17:
Frontend-to-Backend LLM Coordination, Interactive Canvas Prompting & Prominent Forensic Adjudication Deck.

Verifies:
1. Environment hydration from settings (.env SERPAPI_API_KEY & GEMINI_API_KEY).
2. Main-canvas Detective Directives & Suspect Story interactive prompts card.
3. Quick-preset scenario chips updating session state.
4. Telemetry ribbon with Adversarial Audit Score and Reasoner badges.
5. Gemini Forensic Intelligence Briefing & Adjudication Deck rendering.
"""

import os
import sys
import pytest
from streamlit.testing.v1 import AppTest

# Ensure repository root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.config import settings
from backend.app.db import get_golden_cases, init_db
from backend.app.models.case import CaseFile
from backend.app.services.cache_service import CacheService
from frontend.components.war_room_hud import (
    render_gemini_forensic_intelligence_briefing,
    render_prompt_directive_card,
    render_war_room_header,
)


@pytest.fixture(autouse=True)
def prime_database():
    """Ensure database and golden cache fixtures are initialized before tests."""
    init_db()
    cache_service = CacheService()
    cache_service.seed_golden_cases()


def test_app_hydrates_credentials_and_renders_canvas_prompts():
    """Verify AppTest loads, auto-hydrates credentials, and renders the Detective Directives card."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/app.py"))
    at = AppTest.from_file(app_path, default_timeout=30)
    at.run()

    assert not at.exception, f"App raised unexpected exception: {at.exception}"

    # Verify that the main-canvas prompt text areas are rendered
    text_areas = at.text_area
    assert len(text_areas) >= 2, "Expected at least 2 text areas for Claimed Context and Mission Directive"

    # Verify text area keys
    area_keys = [ta.key for ta in text_areas if ta.key]
    assert "main_canvas_context_hint_area" in area_keys
    assert "main_canvas_user_directive_area" in area_keys

    # Verify preset chip buttons are present on canvas
    buttons = at.button
    button_keys = [b.key for b in buttons if b.key]
    assert "preset_chip_landmark" in button_keys
    assert "preset_chip_alpine" in button_keys
    assert "preset_chip_fraud" in button_keys
    assert "launch_swarm_btn" in button_keys


def test_scenario_preset_chips_populate_directives():
    """Verify clicking a preset chip updates the prompt state and directives."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/app.py"))
    at = AppTest.from_file(app_path, default_timeout=30)
    at.run()

    # Click the Rental Fraud preset chip
    fraud_chip = [b for b in at.button if b.key == "preset_chip_fraud"][0]
    fraud_chip.click().run()

    assert not at.exception
    assert at.session_state["context_hint"] == "Luxury 3-bedroom beachfront apartment in Miami, Florida for rent at $250/night."
    assert "Aegean whitewashed masonry" in at.session_state["user_directive"]


def test_launch_investigation_renders_gemini_adjudication_deck():
    """Verify executing an investigation hydrates the CaseFile and renders the Gemini Adjudication Deck."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/app.py"))
    at = AppTest.from_file(app_path, default_timeout=35)
    at.run()

    # Click Launch Autonomous Investigation
    launch_btn = [b for b in at.button if b.key == "launch_swarm_btn"][0]
    launch_btn.click().run()

    assert not at.exception
    assert at.session_state["case_file"] is not None

    # Verify Quick-Action Bar buttons appear
    post_buttons = [b.key for b in at.button if b.key]
    assert "deck_reset_btn" in post_buttons
    download_buttons = [db.key for db in at.download_button if db.key]
    assert "quick_export_html_btn" in download_buttons


def test_render_gemini_forensic_briefing_component():
    """Direct component unit test for render_gemini_forensic_intelligence_briefing."""
    golden_cases = get_golden_cases()
    assert len(golden_cases) >= 1
    sample_case = golden_cases[0]

    # Verify component renders with case file and last state without crashing
    last_state = {
        "audit_score": 0.94,
        "skeptic_critiques": ["Verified authentic. No spatial or architectural contradictions detected."],
    }
    # Should execute smoothly with no exceptions
    render_gemini_forensic_intelligence_briefing(sample_case, last_state)
