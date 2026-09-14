import asyncio
import sys
from playwright.async_api import async_playwright


async def take_screenshot(
    url: str,
    output_path: str = "screenshot.png",
    full_page: bool = True,
    wait_seconds: int = 5,
):
    async with async_playwright() as p:
        # در CI همیشه headless=True
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        print(f"→ باز کردن {url} ...")
        await page.goto(url, wait_until="networkidle", timeout=60000)

        # صبر برای محتوای داینامیک
        await page.wait_for_timeout(wait_seconds * 1000)

        await page.screenshot(path=output_path, full_page=full_page)
        print(f"✓ اسکرین‌شات ذخیره شد: {output_path}")

        await browser.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://chatgpt.com"
    out = sys.argv[2] if len(sys.argv) > 2 else "screenshot.png"
    asyncio.run(take_screenshot(url, out))
