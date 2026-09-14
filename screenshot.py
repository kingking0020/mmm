import asyncio
import hashlib
import secrets
from pathlib import Path

from nanopy import Account
from patchright.async_api import async_playwright


# ── تنظیمات سایت ──
URL = "https://your-website.com"
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# مختصات کلیک
CLICK_X = 1037
CLICK_Y = 294

# ثانیه صبر قبل از هر اسکرین‌شات
WAIT_BEFORE_SHOT = 10

# ── تنظیمات تولید آدرس ──
NUM_SEEDS = 3                # ۳ بار حلقه
ADDRESSES_PER_SEED = 3       # هر بار ۳ آدرس از یک seed

# ── مسیرهای خروجی ──
OUTPUT_DIR = Path("screenshots")
RESULTS_FILE = Path("results.txt")


def generate_addresses():
    """۳ بار حلقه می‌زنه، هر بار ۱ seed + ۳ آدرس می‌سازه."""
    results = []

    for seed_number in range(1, NUM_SEEDS + 1):
        seed = secrets.token_hex(32).upper()
        entry = {"seed": seed, "addresses": []}

        print("=" * 70)
        print(f"SEED #{seed_number}: {seed}")

        for index in range(ADDRESSES_PER_SEED):
            private_key = hashlib.blake2b(
                bytes.fromhex(seed) + index.to_bytes(4, "big"),
                digest_size=32,
            ).hexdigest().upper()

            account = Account(sk=private_key)
            address = account.addr

            entry["addresses"].append(address)
            print(f"  [{index}] {address}")

        results.append(entry)

    return results


async def process_address(page, address, shot_path: Path):
    """کلیک، رسم دایره، تایپ آدرس، صبر ۱۰ ثانیه، اسکرین‌شات."""

    # ۱. باز کردن صفحه‌ی تازه برای هر آدرس
    print(f"  → باز کردن {URL} ...")
    await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(3000)

    # ۲. کلیک روی مختصات
    print(f"  → کلیک روی ({CLICK_X}, {CLICK_Y})")
    await page.mouse.click(CLICK_X, CLICK_Y)
    await page.wait_for_timeout(500)

    # ۳. کشیدن دایره‌ی ریز دور نقطه
    print("  → رسم دایره")
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

    # ۴. تایپ آدرس
    print(f"  → تایپ آدرس: {address}")
    await page.keyboard.type(address, delay=20)

    # ۵. صبر ۱۰ ثانیه
    print(f"  → صبر {WAIT_BEFORE_SHOT} ثانیه ...")
    await page.wait_for_timeout(WAIT_BEFORE_SHOT * 1000)

    # ۶. اسکرین‌شات
    await page.screenshot(path=str(shot_path), full_page=False)
    print(f"  ✓ اسکرین‌شات: {shot_path}")


async def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # ── تولید آدرس‌ها ──
    print("→ تولید seed و آدرس‌ها ...")
    results = generate_addresses()

    # ── ذخیره در results.txt ──
    lines = []
    for i, entry in enumerate(results, 1):
        lines.append("=" * 70)
        lines.append(f"SEED #{i}: {entry['seed']}")
        for j, addr in enumerate(entry["addresses"]):
            lines.append(f"  [{j}] {addr}")
        lines.append("")

    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ نتایج ذخیره شد: {RESULTS_FILE}")

    # ── اجرای مرورگر و اسکرین‌شات ──
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

        counter = 0
        for seed_idx, entry in enumerate(results, 1):
            for addr_idx, address in enumerate(entry["addresses"]):
                counter += 1
                print()
                print(f"── [{counter}] seed #{seed_idx} / address #{addr_idx} ──")
                shot_path = OUTPUT_DIR / f"shot_{counter:02d}.png"
                await process_address(page, address, shot_path)

        await browser.close()

    print()
    print("✓ همه‌چیز تمام شد.")


if __name__ == "__main__":
    asyncio.run(main())
