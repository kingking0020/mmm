"""
اسکرین‌شات از یک URL با Patchright.
پیش‌فرض: فقط viewport (مثل مرورگر واقعی)، نه کل صفحه.
"""

import asyncio
import os
import sys
from patchright.async_api import async_playwright


async def take_screenshot(
    url: str,
    output_path: str = "screenshot.png",
    full_page: bool = False,
    wait_seconds: int = 5,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
):
    async with async_playwright() as p:
        # ── Launch ──
        browser = await p.chromium.launch(headless=True)

        # ── Context ──
        # viewport اندازه‌ی مانیتور واقعی رو شبیه‌سازی می‌کنه
        context = await browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=1,
            locale="en-US",
            timezone_id="America/New_York",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        # ── Navigate ──
        print(f"→ باز کردن {url} ...")
        print(f"  Viewport: {viewport_width}x{viewport_height}")
        print(f"  Full page: {full_page}")

        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # صبر برای لود محتوای داینامیک
        await page.wait_for_timeout(wait_seconds * 1000)

        # ── Screenshot ──
        await page.screenshot(path=output_path, full_page=full_page)
        print(f"✓ اسکرین‌شات ذخیره شد: {output_path}")

        await browser.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    out = sys.argv[2] if len(sys.argv) > 2 else "screenshot.png"
    full = (sys.argv[3].lower() == "true") if len(sys.argv) > 3 else False
    wait = int(sys.argv[4]) if len(sys.argv) > 4 else 5

    # viewport از متغیرهای محیطی (برای CI)
    vw = int(os.environ.get("VIEWPORT_W", "1920"))
    vh = int(os.environ.get("VIEWPORT_H", "1080"))

    asyncio.run(
        take_screenshot(
            url=url,
            output_path=out,
            full_page=full,
            wait_seconds=wait,
            viewport_width=vw,
            viewport_height=vh,
        )
    )
