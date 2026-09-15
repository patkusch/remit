#!/usr/bin/env python3
"""Regenerate docs/hero.png: a real screenshot of the control room, dark theme, at 2x.

    python dashboard/build.py            # refresh dashboard/index.html from the records
    pip install playwright && python -m playwright install chromium
    python docs/make_hero.py

It opens dashboard/index.html as built, opens the OpsPilot row, and photographs the systems
list. Pass --full for the whole page.
Nothing on screen is staged: every number and gap is what the page computes from the records.
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "dashboard" / "index.html"
OUT = ROOT / "docs" / "hero.png"
FULL = "--full" in sys.argv


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1240, "height": 900},
                                device_scale_factor=2, color_scheme="dark")
        page.goto(PAGE.as_uri())
        page.locator(".srow", has_text="OpsPilot").click()
        if FULL:
            page.screenshot(path=str(OUT), full_page=True)
        else:
            # Crop to the systems list, from its heading to the bottom of the opened row
            # (6px below it, short of the next row, which starts 8px down).
            page.evaluate("window.scrollTo(0, 0)")
            top = page.locator("h2", has_text="Systems").bounding_box()
            row = page.locator(".sys", has_text="OpsPilot").bounding_box()
            y = top["y"] - 28
            clip = {"x": 0, "y": y, "width": 1240, "height": row["y"] + row["height"] + 6 - y}
            page.screenshot(path=str(OUT), full_page=True, clip=clip)
        browser.close()
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
