import asyncio
from patchright.async_api import async_playwright


# ── تنظیمات پیش‌فرض ──
URL = "https://nanswap.com/nano-faucet?utm_source=chatgpt.com"
OUTPUT = "screenshot.png"
FULL_PAGE = False          # False = مثل مرورگر واقعی، True = کل صفحه
WAIT_SECONDS = 5
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080


async def take_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            device_scale_factor=1,
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        print(f"→ باز کردن {URL} ...")
        print(f"  Viewport: {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}")
        print(f"  Full page: {FULL_PAGE}")

        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(WAIT_SECONDS * 1000)

        await page.screenshot(path=OUTPUT, full_page=FULL_PAGE)
        print(f"✓ اسکرین‌شات ذخیره شد: {OUTPUT}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(take_screenshot())
