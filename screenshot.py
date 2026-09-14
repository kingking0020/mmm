import asyncio
import hashlib
import secrets
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from patchright.async_api import async_playwright


# ══════════════════════════════════════════════════
#  👇 تنظیمات اصلی
# ══════════════════════════════════════════════════
URL = "https://nanswap.com/nano-faucet?utm_source=chatgpt.com"       # آدرس سایت
OUTPUT_FOLDER = "nano_addresses"       # پوشه‌ی ذخیره‌ی اسکرین‌شات‌ها
# ══════════════════════════════════════════════════

# ── مرورگر ──
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080
CLICK_X = 1037
CLICK_Y = 294
WAIT_BEFORE_SHOT = 10

# ── تولید ──
NUM_ADDRESSES = 1        # ← فقط یک آدرس

RESULTS_FILE = Path("results.txt")


# ── Nano ──
NANO_ALPHABET = "13456789abcdefghijkmnopqrstuwxyz"


def _encode_bits(bits: str) -> str:
    return "".join(
        NANO_ALPHABET[int(bits[i:i + 5], 2)]
        for i in range(0, len(bits), 5)
    )


def ed25519_pubkey(private_key_bytes: bytes) -> bytes:
    sk = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    return sk.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def nano_address(public_key: bytes) -> str:
    bits = "0000" + "".join(f"{b:08b}" for b in public_key)
    encoded_key = _encode_bits(bits)
    checksum = hashlib.blake2b(public_key, digest_size=5).digest()[::-1]
    checksum_bits = "".join(f"{b:08b}" for b in checksum)
    return "nano_" + encoded_key + _encode_bits(checksum_bits)


def address_from_seed_index(seed: bytes, index: int) -> str:
    pk = hashlib.blake2b(seed + index.to_bytes(4, "big"), digest_size=32).digest()
    return nano_address(ed25519_pubkey(pk))


def generate_address():
    """یک seed و یک آدرس می‌سازه."""
    seed_hex = secrets.token_hex(32).upper()
    seed = bytes.fromhex(seed_hex)
    address = address_from_seed_index(seed, 0)
    return seed_hex, address


async def process_address(page, address: str, shot_path: Path):
    print(f"  → باز کردن {URL} ...")
    await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(3000)

    print(f"  → کلیک روی ({CLICK_X}, {CLICK_Y})")
    await page.mouse.click(CLICK_X, CLICK_Y)
    await page.wait_for_timeout(500)

    print("  → رسم دایره")
    await page.evaluate(f"""
        () => {{
            const cx = {CLICK_X}, cy = {CLICK_Y}, r = 20;
            const c = document.createElement('div');
            c.style.position = 'absolute';
            c.style.left = (cx - r) + 'px';
            c.style.top = (cy - r) + 'px';
            c.style.width = (2 * r) + 'px';
            c.style.height = (2 * r) + 'px';
            c.style.border = '3px solid red';
            c.style.borderRadius = '50%';
            c.style.pointerEvents = 'none';
            c.style.zIndex = '999999';
            c.style.boxShadow = '0 0 8px rgba(255,0,0,0.8)';
            document.body.appendChild(c);
        }}
    """)

    print(f"  → تایپ آدرس: {address}")
    await page.keyboard.type(address, delay=20)

    print(f"  → صبر {WAIT_BEFORE_SHOT} ثانیه ...")
    await page.wait_for_timeout(WAIT_BEFORE_SHOT * 1000)

    await page.screenshot(path=str(shot_path), full_page=False)
    print(f"  ✓ اسکرین‌شات ذخیره شد: {shot_path}")


async def main():
    # ساخت پوشه
    output_dir = Path(OUTPUT_FOLDER)
    output_dir.mkdir(exist_ok=True)

    # ── تولید یک آدرس ──
    print("→ تولید seed و آدرس ...")
    seed_hex, address = generate_address()
    print(f"  SEED:    {seed_hex}")
    print(f"  ADDRESS: {address}")

    # ── ذخیره در results.txt ──
    RESULTS_FILE.write_text(
        f"SEED: {seed_hex}\nADDRESS: {address}\n",
        encoding="utf-8",
    )
    print(f"✓ نتایج ذخیره شد: {RESULTS_FILE}")

    # ── نام فایل = خود آدرس ──
    shot_path = output_dir / f"{address}.png"

    # ── اجرای مرورگر ──
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

        await process_address(page, address, shot_path)

        await browser.close()

    print()
    print(f"✓ تمام شد. اسکرین‌شات: {shot_path}")


if __name__ == "__main__":
    asyncio.run(main())
