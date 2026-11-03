import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
ARTIFACTS_DIR = ROOT / "artifacts" / "task1"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not Path(CHROME_PATH).exists():
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

print(f"Using browser binary: {CHROME_PATH}")
print(f"Artifacts output dir: {ARTIFACTS_DIR}")

# 1. Start backend process
print("Starting backend uvicorn on port 8000...")
backend_proc = subprocess.Popen(
    [str(BACKEND_DIR / ".venv" / "Scripts" / "uvicorn.exe"), "app.main:app", "--port", "8000"],
    cwd=str(BACKEND_DIR),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

# 2. Start frontend process (using npm run start)
print("Starting frontend next start on port 3000...")
frontend_proc = subprocess.Popen(
    ["npm.cmd", "start", "--", "-p", "3000"],
    cwd=str(FRONTEND_DIR),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

try:
    # Wait for services to respond
    import urllib.request
    print("Waiting for backend and frontend to become ready...")
    for _ in range(30):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as r:
                if r.status == 200:
                    print("Backend ready!")
                    break
        except Exception:
            time.sleep(1)
    else:
        print("Backend failed to start in time!")

    for _ in range(30):
        try:
            with urllib.request.urlopen("http://127.0.0.1:3000", timeout=2) as r:
                if r.status == 200:
                    print("Frontend ready!")
                    break
        except Exception:
            time.sleep(1)
    else:
        print("Frontend failed to start in time!")

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        # Mobile viewport: 390x844 (iPhone 12/13/14)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            device_scale_factor=2,
        )
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print("\n--- 1. Brief at 24h ---")
        page.goto("http://127.0.0.1:3000", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Check horizontal overflow
        scroll_w = page.evaluate("() => document.documentElement.scrollWidth")
        inner_w = page.evaluate("() => window.innerWidth")
        print(f"Brief 24h: scrollWidth={scroll_w}, innerWidth={inner_w}, overflow={scroll_w > inner_w}")
        page.screenshot(path=str(ARTIFACTS_DIR / "brief_24h.png"), full_page=False)
        print("Saved brief_24h.png")

        print("\n--- 2. Brief at 7d ---")
        # Click 7d button if available
        button_7d = page.locator("button:has-text('7d')")
        if button_7d.count() > 0:
            button_7d.first.click()
            page.wait_for_timeout(2000)
        page.screenshot(path=str(ARTIFACTS_DIR / "brief_7d.png"), full_page=False)
        print("Saved brief_7d.png")

        print("\n--- 3. Watch with live quotes ---")
        # Click Watch on bottom nav
        watch_nav = page.locator("button:has-text('Watch')")
        if watch_nav.count() > 0:
            watch_nav.first.click()
            page.wait_for_timeout(2500)
        scroll_w = page.evaluate("() => document.documentElement.scrollWidth")
        inner_w = page.evaluate("() => window.innerWidth")
        print(f"Watch: scrollWidth={scroll_w}, innerWidth={inner_w}, overflow={scroll_w > inner_w}")
        page.screenshot(path=str(ARTIFACTS_DIR / "watch_live_quotes.png"), full_page=False)
        print("Saved watch_live_quotes.png")

        print("\n--- 4. Alerts / Signals ---")
        # Scroll or click to see alerts
        alerts_heading = page.locator("h2:has-text('Signal Alerts'), h3:has-text('Alerts'), button:has-text('Alerts')")
        if alerts_heading.count() > 0:
            alerts_heading.first.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
        page.screenshot(path=str(ARTIFACTS_DIR / "alerts_signals.png"), full_page=False)
        print("Saved alerts_signals.png")

        print("\n--- 5. Research Hub ---")
        research_nav = page.locator("button:has-text('Research')")
        if research_nav.count() > 0:
            research_nav.first.click()
            page.wait_for_timeout(2000)
        scroll_w = page.evaluate("() => document.documentElement.scrollWidth")
        inner_w = page.evaluate("() => window.innerWidth")
        print(f"Research: scrollWidth={scroll_w}, innerWidth={inner_w}, overflow={scroll_w > inner_w}")
        page.screenshot(path=str(ARTIFACTS_DIR / "research_hub.png"), full_page=False)
        print("Saved research_hub.png")

        print("\n--- 6. Backend Down Error State ---")
        # Kill backend process
        backend_proc.terminate()
        backend_proc.wait(timeout=5)
        print("Backend terminated.")

        # Go back to Watch
        if watch_nav.count() > 0:
            watch_nav.first.click()
            page.wait_for_timeout(1000)
            
        # Click Retry button if present or reload
        retry_btn = page.locator("button:has-text('Retry')")
        if retry_btn.count() > 0:
            retry_btn.first.click()
            page.wait_for_timeout(2000)
        else:
            page.reload()
            page.wait_for_timeout(2000)
            if watch_nav.count() > 0:
                watch_nav.first.click()
                page.wait_for_timeout(1000)

        page.screenshot(path=str(ARTIFACTS_DIR / "watch_backend_down.png"), full_page=False)
        print("Saved watch_backend_down.png")

        print("\nConsole errors captured during run:", console_errors)
        browser.close()

finally:
    try:
        backend_proc.terminate()
    except Exception:
        pass
    try:
        frontend_proc.terminate()
    except Exception:
        pass
    print("Cleaned up backend and frontend subprocesses.")

