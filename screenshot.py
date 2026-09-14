import asyncio
import sys
from patchright.async_api import async_playwright


async def take_screenshot(
    url: str,
    output_path: str = "screenshot.png",
    full_page: bool = True,
    wait_seconds: int = 5,
):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1366, "height": 900},
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        print(f"→ باز کردن {url} ...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(wait_seconds * 1000)

        await page.screenshot(path=output_path, full_page=full_page)
        print(f"✓ اسکرین‌شات ذخیره شد: {output_path}")

        await browser.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    out = sys.argv[2] if len(sys.argv) > 2 else "screenshot.png"
    full = (sys.argv[3].lower() == "true") if len(sys.argv) > 3 else True
    wait = int(sys.argv[4]) if len(sys.argv) > 4 else 5

    asyncio.run(take_screenshot(url, out, full, wait))
