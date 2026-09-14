import asyncio
from patchright.async_api import async_playwright


# ── تنظیمات ──
URL = "https://nanswap.com/nano-faucet?utm_source=chatgpt.com"
OUTPUT = "screenshot.png"

VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# مختصات کلیک
CLICK_X = 1037
CLICK_Y = 294

# متن مورد نظر برای تایپ
TEXT_TO_TYPE = "nano_3ceqfkc938yatyguppk6xh7dj9adhymjytnbtxxzroqp4pk8qnzirnr611qj"

# ثانیه صبر قبل از اسکرین‌شات نهایی
WAIT_BEFORE_SHOT = 10


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

        # ── ۱. باز کردن سایت ──
        print(f"→ باز کردن {URL} ...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        # ── ۲. کلیک روی مختصات (1037, 294) ──
        print(f"→ کلیک روی ({CLICK_X}, {CLICK_Y})")
        await page.mouse.click(CLICK_X, CLICK_Y)
        await page.wait_for_timeout(500)

        # ── ۳. کشیدن دایره‌ی ریز دور نقطه‌ی کلیک‌شده ──
        print("→ رسم دایره‌ی ریز")
        await page.evaluate(f"""
            () => {{
                const cx = {CLICK_X};
                const cy = {CLICK_Y};
                const r = 20;

                const circle = document.createElement('div');
                circle.style.position = 'absolute';
                circle.style.left = (cx - r) + 'px';
                circle.style.top = (cy - r) + 'px';
                circle.style.width = (2 * r) + 'px';
                circle.style.height = (2 * r) + 'px';
                circle.style.border = '3px solid red';
                circle.style.borderRadius = '50%';
                circle.style.pointerEvents = 'none';
                circle.style.zIndex = '999999';
                circle.style.boxShadow = '0 0 8px rgba(255,0,0,0.8)';

                document.body.appendChild(circle);
            }}
        """)

        # ── ۴. تایپ کردن متن ──
        print("→ تایپ متن ...")
        await page.keyboard.type(TEXT_TO_TYPE, delay=30)

        # ── ۵. صبر ۱۰ ثانیه ──
        print(f"→ صبر {WAIT_BEFORE_SHOT} ثانیه ...")
        await page.wait_for_timeout(WAIT_BEFORE_SHOT * 1000)

        # ── ۶. اسکرین‌شات ──
        await page.screenshot(path=OUTPUT, full_page=False)
        print(f"✓ اسکرین‌شات ذخیره شد: {OUTPUT}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(take_screenshot())
