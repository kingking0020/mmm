import asyncio
import sys
from patchright.async_api import async_playwright


async def take_screenshot(
    url: str,
    output_path: str = "screenshot.png",
    full_page: bool = True,
    wait_seconds: int = 10,
):
    async with async_playwright() as p:
        # نکته کلیدی: از channel="chrome" استفاده کن، نه chromium
        # چون Cloudflare به chromium خالی حساس‌تره
        browser = await p.chromium.launch(
            headless=True,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1366, "height": 900},
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = await context.new_page()

        print(f"→ باز کردن {url} ...")
        await page.goto(url, wait_until="domcontentloaded", timeout=90000)

        # صبر کن تا چالش Cloudflare حل بشه
        # اگه صفحه‌ی چالش بود، تا 30 ثانیه صبر می‌کنیم
        for _ in range(15):
            title = await page.title()
            content = await page.content()
            if "Just a moment" not in title and "Verify you are human" not in content:
                break
            print("⏳ منتظر عبور از Cloudflare ...")
            await page.wait_for_timeout(2000)

        await page.wait_for_timeout(wait_seconds * 1000)

        await page.screenshot(path=output_path, full_page=full_page)
        print(f"✓ اسکرین‌شات ذخیره شد: {output_path}")

        await browser.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://chatgpt.com"
    out = sys.argv[2] if len(sys.argv) > 2 else "screenshot.png"
    asyncio.run(take_screenshot(url, out))
