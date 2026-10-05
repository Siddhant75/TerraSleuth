import os
import sys
import time
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "screenshots"))
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def run_ui_audit():
    print(f"Starting Playwright UI Audit on http://localhost:8501...")
    print(f"Saving screenshots to: {SCREENSHOT_DIR}")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1.5,
        )
        page = context.new_page()

        # Step 1: Initial Dashboard State
        print("Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=45000)
        time.sleep(3)

        p1 = os.path.join(SCREENSHOT_DIR, "01_initial_dashboard.png")
        page.screenshot(path=p1, full_page=True)
        print("Captured: 01_initial_dashboard.png")

        # Step 2: Target Selected State
        p2 = os.path.join(SCREENSHOT_DIR, "02_target_selected.png")
        page.screenshot(path=p2, full_page=True)
        print("Captured: 02_target_selected.png")

        # Step 3: Trigger Autonomous Investigation
        print("Clicking 'Launch Autonomous Investigation'...")
        page.locator("button:has-text('Launch Autonomous Investigation')").click()

        # Wait for investigation streaming and completion alert
        print("Waiting for LangGraph OSINT Swarm to complete...")
        page.wait_for_selector("text=Investigation Concluded", timeout=35000)
        time.sleep(3)  # Hydrate Folium map and charts

        p3 = os.path.join(SCREENSHOT_DIR, "03_investigation_complete.png")
        page.screenshot(path=p3, full_page=True)
        print("Captured: 03_investigation_complete.png")

        # Step 4: Click each evidence tab via get_by_role('tab')
        tab_filenames = [
            "04_tab_1_geospatial_map.png",
            "04_tab_2_visual_evidence.png",
            "04_tab_3_chronology_timeline.png",
            "04_tab_4_citation_chain.png",
            "04_tab_5_markdown_dossier.png",
        ]

        tabs = page.get_by_role("tab").all()
        print(f"Detected {len(tabs)} tabs via get_by_role('tab').")

        for idx, tab in enumerate(tabs):
            filename = tab_filenames[idx] if idx < len(tab_filenames) else f"04_tab_{idx+1}.png"
            clean_label = tab.inner_text().encode("ascii", "ignore").decode("ascii").strip()
            print(f"Switching to Tab {idx+1}: '{clean_label}'...")
            tab.click()
            time.sleep(3)  # Allow Folium / Pillow / Markdown widgets to re-render

            target_path = os.path.join(SCREENSHOT_DIR, filename)
            page.screenshot(path=target_path, full_page=True)
            print(f"Captured: {filename}")

        print("\nPlaywright UI automation audit completed successfully!")
        browser.close()


if __name__ == "__main__":
    run_ui_audit()
