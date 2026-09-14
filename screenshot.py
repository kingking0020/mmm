import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

NANO_ALPHABET = "13456789abcdefghijkmnopqrstuwxyz"

def _encode_bits(bits):
    return "".join(NANO_ALPHABET[int(bits[i:i+5], 2)] for i in range(0, len(bits), 5))

def ed25519_pubkey(sk_bytes):
    sk = Ed25519PrivateKey.from_private_bytes(sk_bytes)
    return sk.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

def nano_address(pub):
    bits = "0000" + "".join(f"{b:08b}" for b in pub)
    key = _encode_bits(bits)
    cs = hashlib.blake2b(pub, digest_size=5).digest()[::-1]
    cs_bits = "".join(f"{b:08b}" for b in cs)
    return "nano_" + key + _encode_bits(cs_bits)

# تست با seed نمونه
seed = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000")
for i in range(3):
    pk = hashlib.blake2b(seed + i.to_bytes(4, "big"), digest_size=32).digest()
    addr = nano_address(ed25519_pubkey(pk))
    print(i, addr)
