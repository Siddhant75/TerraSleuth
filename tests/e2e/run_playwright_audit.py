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

        # Step 1: Initial load on http://localhost:8501 (Tab 1: Screenshot Audit & Critique)
        print("Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=45000)
        time.sleep(3)

        p1 = os.path.join(SCREENSHOT_DIR, "01_tab1_screenshot_critique.png")
        page.screenshot(path=p1, full_page=True)
        print("Captured: 01_tab1_screenshot_critique.png (Playwright Visual Critique)")

        # Step 2: Tab 2: SerpApi Features & Add-ons
        print("Switching to Tab 2: SerpApi Features & Add-ons...")
        page.get_by_role("tab", name="2. ⚡ SerpApi Features & Add-ons").click()
        time.sleep(2)
        p2 = os.path.join(SCREENSHOT_DIR, "02_tab2_serpapi_features.png")
        page.screenshot(path=p2, full_page=True)
        print("Captured: 02_tab2_serpapi_features.png")

        # Step 3: Tab 4: Implementation Roadmap
        print("Switching to Tab 4: Implementation Roadmap...")
        page.get_by_role("tab", name="4. 🗺️ Implementation Roadmap").click()
        time.sleep(2)
        p3 = os.path.join(SCREENSHOT_DIR, "03_tab4_roadmap.png")
        page.screenshot(path=p3, full_page=True)
        print("Captured: 03_tab4_roadmap.png")

        # Step 4: Tab 3: Tactical Command Deck (Initial War Room State)
        print("Switching to Tab 3: Tactical Command Deck...")
        page.get_by_role("tab", name="3. 🕵️ Tactical Command Deck").click()
        time.sleep(2)
        p4 = os.path.join(SCREENSHOT_DIR, "04_tab3_command_deck_initial.png")
        page.screenshot(path=p4, full_page=True)
        print("Captured: 04_tab3_command_deck_initial.png")

        # Step 5: Trigger Autonomous Investigation on Landmark Target
        print("Clicking 'Launch Autonomous Investigation'...")
        page.locator("button:has-text('Launch Autonomous Investigation')").click()

        # Wait for investigation streaming and rerun hydration
        print("Waiting for LangGraph OSINT Swarm to complete...")
        page.get_by_role("tab", name="🎯 Autonomous Geoguessr Mode").wait_for(state="visible", timeout=45000)
        time.sleep(3)  # Hydrate Folium map and charts

        p5 = os.path.join(SCREENSHOT_DIR, "05_deck_overview_with_twin.png")
        page.screenshot(path=p5, full_page=True)
        print("Captured: 05_deck_overview_with_twin.png (Overview with twin matcher beneath image)")

        # Step 6: Click Autonomous Geoguessr Mode Sub-Tab
        print("Switching to Autonomous Geoguessr Mode sub-tab...")
        page.get_by_role("tab", name="🎯 Autonomous Geoguessr Mode").click()
        time.sleep(2)
        p6 = os.path.join(SCREENSHOT_DIR, "06_deck_geoguessr_mode.png")
        page.screenshot(path=p6, full_page=True)
        print("Captured: 06_deck_geoguessr_mode.png (5000 pts scorecard & 4-stage tightening)")

        # Step 7: Click Chronological Provenance Sub-Tab
        print("Switching to Chronological Provenance sub-tab...")
        page.get_by_role("tab", name="⏱️ Chronological Provenance").click()
        time.sleep(2)
        p7 = os.path.join(SCREENSHOT_DIR, "07_deck_chronology_timeline.png")
        page.screenshot(path=p7, full_page=True)
        print("Captured: 07_deck_chronology_timeline.png")

        # Step 8: Click OSINT Dorks Sub-Tab
        print("Switching to OSINT Dorks sub-tab...")
        page.get_by_role("tab", name="🕵️ OSINT Dorks").click()
        time.sleep(2)
        p8 = os.path.join(SCREENSHOT_DIR, "08_deck_osint_dorks.png")
        page.screenshot(path=p8, full_page=True)
        print("Captured: 08_deck_osint_dorks.png")

        # Step 9: Select Rental Scam Target and Demonstrate Fraud Unmasking
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

        # Ensure we are on Tab 3
        page.get_by_role("tab", name="3. 🕵️ Tactical Command Deck").click()
        time.sleep(1)

        print("Launching Fraud Investigation...")
        page.locator("button:has-text('Launch Autonomous Investigation')").click()
        page.locator("text=HIGH CONFIDENCE FRAUD DETECTION").wait_for(state="visible", timeout=45000)
        time.sleep(3)
        p9 = os.path.join(SCREENSHOT_DIR, "09_fraud_anomaly_unmasking.png")
        page.screenshot(path=p9, full_page=True)
        print("Captured: 09_fraud_anomaly_unmasking.png ([FRAUD ALERT])")

        print("\nPlaywright UI automation audit completed successfully!")
        browser.close()


if __name__ == "__main__":
    run_ui_audit()
