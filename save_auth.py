"""
یک بار این اسکریپت رو لوکال اجرا کن تا فایل auth.json ساخته بشه.
بعد محتوای auth.json رو base64 کن و توی GitHub Secret بذار.
"""
import asyncio
from patchright.async_api import async_playwright


async def save_auth_state():
    async with async_playwright() as p:
        # headless=False چون باید دستی لاگین کنی
        # channel="chrome" چون Patchright با Chrome واقعی بهترین عملکرد رو داره
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome",  # ← از Chrome واقعی نصب‌شده روی سیستم استفاده کن
        )
        context = await browser.new_context(
            viewport={"width": 1366, "height": 900},
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = await context.new_page()

        print("→ در حال باز کردن chatgpt.com ...")
        await page.goto("https://chatgpt.com", wait_until="domcontentloaded")

        print()
        print("=" * 60)
        print("حالا توی مرورگر باز شده:")
        print("  1. لاگین کن")
        print("  2. اگه Cloudflare اومد، تیک 'Verify you are human' رو بزن")
        print("  3. صبر کن تا صفحه‌ی چت کامل لود بشه")
        print("  4. بعد برگرد اینجا و Enter بزن")
        print("=" * 60)
        input("\n>>> بعد از کامل شدن لاگین، Enter بزن: ")

        # ذخیره‌ی کوکی‌ها و localStorage
        await context.storage_state(path="auth.json")
        print(f"\n✓ فایل auth.json ذخیره شد.")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(save_auth_state())
