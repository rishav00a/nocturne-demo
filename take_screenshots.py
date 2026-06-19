"""
Take all 14 screenshots of the nocturne-demo project using Playwright.
Saves to /Users/rishav00a/Projects/nocturne-demo/screenshots/
"""

import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

BASE_URL = "http://localhost:8080"
OUT_DIR  = Path("/Users/rishav00a/Projects/nocturne-demo/screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_WIDTH = 1200


def save(page, name, full_page=False):
    path = str(OUT_DIR / name)
    page.screenshot(path=path, full_page=full_page)
    # Crop + resize with Pillow
    img = Image.open(path)
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)
    img.save(path, "PNG", optimize=True)
    size_kb = os.path.getsize(path) // 1024
    print(f"  ✓ {name}  ({img.width}×{img.height}, {size_kb} KB)")
    return path


def login(page):
    page.goto(f"{BASE_URL}/admin/login/")
    page.fill("#id_username", "admin")
    page.fill("#id_password", "admin123")
    page.click("[type=submit]")
    page.wait_for_url(f"{BASE_URL}/admin/")
    print("  Logged in as admin")


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx     = browser.new_context(viewport={"width": 1440, "height": 900})
        page    = ctx.new_page()

        # ── Login ─────────────────────────────────────────────────────────────
        print("\nLogging in…")
        login(page)

        # ── Screenshot 1: Dashboard overview ──────────────────────────────────
        print("\n[1/14] dashboard_overview.png")
        page.goto(f"{BASE_URL}/nocturne/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        save(page, "dashboard_overview.png", full_page=False)

        # ── Screenshot 2: Charts section ─────────────────────────────────────
        print("\n[2/14] dashboard_charts.png")
        page.goto(f"{BASE_URL}/nocturne/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        # Scroll to charts
        page.evaluate("window.scrollTo(0, 450)")
        time.sleep(1)
        save(page, "dashboard_charts.png")

        # ── Screenshot 3: Log distribution / service status / slowest endpoints
        print("\n[3/14] dashboard_log_distribution.png")
        page.evaluate("window.scrollTo(0, 950)")
        time.sleep(1)
        save(page, "dashboard_log_distribution.png")

        # ── Screenshot 4: Anomaly table ───────────────────────────────────────
        print("\n[4/14] dashboard_anomaly_table.png")
        page.evaluate("window.scrollTo(0, 1450)")
        time.sleep(1)
        save(page, "dashboard_anomaly_table.png")

        # ── Screenshot 5: Anomaly modal ───────────────────────────────────────
        print("\n[5/14] anomaly_modal.png")
        page.goto(f"{BASE_URL}/nocturne/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        try:
            # Click first CRITICAL badge in the anomaly table
            page.wait_for_selector("table tbody tr", timeout=5000)
            page.evaluate("window.scrollTo(0, 1450)")
            time.sleep(0.5)
            first_row = page.locator("table tbody tr").first
            first_row.click()
            time.sleep(1.5)
            # Try to find modal
            modal = page.locator(".modal, [role='dialog'], #anomaly-modal")
            if modal.count() > 0:
                save(page, "anomaly_modal.png")
            else:
                save(page, "anomaly_modal.png", full_page=False)
        except Exception as e:
            print(f"    (modal click fallback: {e})")
            save(page, "anomaly_modal.png")

        # ── Screenshot 6: Log explorer ────────────────────────────────────────
        print("\n[6/14] log_explorer.png")
        page.goto(f"{BASE_URL}/nocturne/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 2200)")
        time.sleep(1)
        save(page, "log_explorer.png")

        # ── Screenshot 7: Expanded stacktrace row ─────────────────────────────
        print("\n[7/14] log_stacktrace.png")
        try:
            # Click first ERROR/CRITICAL row in log explorer
            page.wait_for_selector("table", timeout=5000)
            error_rows = page.locator("tr").filter(has_text="ERROR").first
            if error_rows.count() == 0:
                error_rows = page.locator("tr").filter(has_text="CRITICAL").first
            error_rows.click()
            time.sleep(2)
            save(page, "log_stacktrace.png", full_page=False)
        except Exception as e:
            print(f"    (stacktrace fallback: {e})")
            save(page, "log_stacktrace.png")

        # ── Screenshot 8: AI analysis ─────────────────────────────────────────
        print("\n[8/14] log_ai_analysis.png")
        try:
            analyse_btn = page.locator("button", has_text="Analyse").first
            if analyse_btn.count() > 0:
                analyse_btn.click()
                print("    Waiting for AI analysis (up to 30s)…")
                time.sleep(30)
                save(page, "log_ai_analysis.png", full_page=False)
            else:
                save(page, "log_ai_analysis.png")
        except Exception as e:
            print(f"    (AI analysis fallback: {e})")
            save(page, "log_ai_analysis.png")

        # ── Screenshot 9: Webhook activity ────────────────────────────────────
        print("\n[9/14] webhook_activity.png")
        page.goto(f"{BASE_URL}/nocturne/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 3000)")
        time.sleep(1)
        save(page, "webhook_activity.png")

        # ── Screenshot 10: Health trends ──────────────────────────────────────
        print("\n[10/14] health_trends.png")
        page.evaluate("window.scrollTo(0, 3600)")
        time.sleep(1)
        save(page, "health_trends.png")

        # ── Screenshot 11: Timeframe filter (6H) ─────────────────────────────
        print("\n[11/14] timeframe_filter.png")
        page.goto(f"{BASE_URL}/nocturne/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        try:
            btn_6h = page.locator("button, .pill, [data-timeframe]").filter(has_text="6H").first
            if btn_6h.count() == 0:
                btn_6h = page.get_by_text("6H").first
            btn_6h.click()
            time.sleep(2.5)
        except Exception as e:
            print(f"    (6H button fallback: {e})")
        save(page, "timeframe_filter.png")

        # ── Screenshot 12: Admin dashboard ───────────────────────────────────
        print("\n[12/14] admin_dashboard.png")
        page.goto(f"{BASE_URL}/admin/nocturne/logentry/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        save(page, "admin_dashboard.png", full_page=False)

        # ── Screenshot 13: Admin anomaly list ────────────────────────────────
        print("\n[13/14] admin_anomaly_list.png")
        page.goto(f"{BASE_URL}/admin/nocturne/anomalyevent/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        save(page, "admin_anomaly_list.png", full_page=False)

        # ── Screenshot 14: DRF API health ────────────────────────────────────
        print("\n[14/14] api_health.png")
        page.goto(f"{BASE_URL}/nocturne/api/health/?format=json")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        save(page, "api_health.png", full_page=False)

        browser.close()

    print("\n── Summary ──────────────────────────────────────────")
    total_size = 0
    for f in sorted(OUT_DIR.glob("*.png")):
        kb = f.stat().st_size // 1024
        total_size += kb
        print(f"  {f.name:<40} {kb:>5} KB")
    print(f"\n  Total: {total_size} KB  ({total_size//1024} MB)")
    print(f"  Saved to: {OUT_DIR}")


if __name__ == "__main__":
    run()
