from Crypto.Hash import SHA256, keccak


def keccak256(x):
    if isinstance(x, int):
        x = x.to_bytes(32, "big")
    k = keccak.new(digest_bits=256)
    k.update(x)
    return int.from_bytes(k.digest(), "big")


def sha256(x):
    if isinstance(x, int):
        x = x.to_bytes(32, "big")
    h = SHA256.new()
    h.update(x)
    return int.from_bytes(h.digest(), "big")


def int_to_u32_array(x):
    return [(x >> (i * 32)) & 0xFFFFFFFF for i in reversed(range(8))]


class Namespace:
    pass
