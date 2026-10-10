import os
import sys
import time
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "screenshots"))
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def run_ui_audit():
    print("Starting Playwright UI Audit on http://localhost:8501...")
    print(f"Saving screenshots to: {SCREENSHOT_DIR}")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1.5,
        )
        page = context.new_page()

        # Step 1: Initial load on http://localhost:8501 (Direct Command Deck & Mission Briefings)
        print("Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=45000)
        time.sleep(3)

        p1 = os.path.join(SCREENSHOT_DIR, "01_initial_hero_command_deck.png")
        page.screenshot(path=p1, full_page=True)
        print("Captured: 01_initial_hero_command_deck.png (Pure Product Primary Mission View)")

        # Step 2: Sidebar Target Selection View
        print("Capturing sidebar target selection view...")
        time.sleep(1)
        p2 = os.path.join(SCREENSHOT_DIR, "02_sidebar_target_selection.png")
        page.screenshot(path=p2, full_page=True)
        print("Captured: 02_sidebar_target_selection.png (Target Selection & Parameters)")

        # Step 3: Trigger Autonomous Investigation on Landmark Target
        print("Clicking 'Launch Autonomous Investigation'...")
        page.locator("button:has-text('Launch Autonomous Investigation')").first.click()

        # Wait for investigation streaming and rerun hydration
        print("Waiting for LangGraph OSINT Swarm to complete...")
        page.get_by_role("tab", name="🎯 Autonomous Geoguessr Mode").wait_for(state="visible", timeout=45000)
        time.sleep(3)  # Hydrate Folium map and charts

        p3 = os.path.join(SCREENSHOT_DIR, "03_command_deck_overview_with_twin.png")
        page.screenshot(path=p3, full_page=True)
        print("Captured: 03_command_deck_overview_with_twin.png (Overview with twin matcher & quick export)")

        # Step 4: Click Autonomous Geoguessr Mode Sub-Tab
        print("Switching to Autonomous Geoguessr Mode sub-tab...")
        page.get_by_role("tab", name="🎯 Autonomous Geoguessr Mode").click()
        time.sleep(2)
        p4 = os.path.join(SCREENSHOT_DIR, "04_deck_geoguessr_mode.png")
        page.screenshot(path=p4, full_page=True)
        print("Captured: 04_deck_geoguessr_mode.png (5000 pts scorecard & 4-stage tightening)")

        # Step 5: Click Chronological Provenance Sub-Tab
        print("Switching to Chronological Provenance sub-tab...")
        page.get_by_role("tab", name="⏱️ Chronological Provenance").click()
        time.sleep(2)
        p5 = os.path.join(SCREENSHOT_DIR, "05_deck_chronology_timeline.png")
        page.screenshot(path=p5, full_page=True)
        print("Captured: 05_deck_chronology_timeline.png")

        # Step 6: Click Citation Ledger Sub-Tab
        print("Switching to Verifiable Citations sub-tab...")
        page.get_by_role("tab", name="🔗 Verifiable Citations").click()
        time.sleep(2)
        p6 = os.path.join(SCREENSHOT_DIR, "06_deck_citation_ledger.png")
        page.screenshot(path=p6, full_page=True)
        print("Captured: 06_deck_citation_ledger.png")

        # Step 7: Click OSINT Dorks Sub-Tab
        print("Switching to OSINT Dorks sub-tab...")
        page.get_by_role("tab", name="🕵️ OSINT Dorks").click()
        time.sleep(2)
        p7 = os.path.join(SCREENSHOT_DIR, "07_deck_osint_dorks.png")
        page.screenshot(path=p7, full_page=True)
        print("Captured: 07_deck_osint_dorks.png")

        # Step 8: Click Executive Dossier Sub-Tab
        print("Switching to Executive Dossier sub-tab...")
        page.get_by_role("tab", name="📄 Executive Dossier").click()
        time.sleep(2)
        p8 = os.path.join(SCREENSHOT_DIR, "08_deck_executive_dossier.png")
        page.screenshot(path=p8, full_page=True)
        print("Captured: 08_deck_executive_dossier.png")

        # Step 9: Reset and Select Rental Scam Target for Fraud Unmasking
        print("Resetting investigation for Rental Scam fraud demo...")
        page.locator("button:has-text('New Investigation')").first.click()
        time.sleep(2)

        print("Selecting Vacation Rental Fraud scenario in sidebar...")
        sidebar_sb = page.locator("section[data-testid='stSidebar'] div[data-testid='stSelectbox']").first
        inp = sidebar_sb.locator("input").first
        inp.click()
        time.sleep(1)
        inp.fill("Marketplace")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)
        print(f"Selected target: {inp.input_value()}")

        print("Launching Fraud Investigation...")
        page.locator("button:has-text('Launch Autonomous Investigation')").first.click()
        page.locator("text=HIGH CONFIDENCE FRAUD DETECTION").wait_for(state="visible", timeout=45000)
        time.sleep(3)
        p9 = os.path.join(SCREENSHOT_DIR, "09_fraud_anomaly_unmasking.png")
        page.screenshot(path=p9, full_page=True)
        print("Captured: 09_fraud_anomaly_unmasking.png ([FRAUD ALERT])")

        print("\nPlaywright UI automation audit completed successfully!")
        browser.close()


if __name__ == "__main__":
    run_ui_audit()
