from random import randrange
from Crypto.Hash import keccak

from curve25519 import valid, ORDER, add, mult, curve25519


def make_secret():
    # https://cr.yp.to/ecdh.html
    return randrange(2 ** 251, 2 ** 252) << 3


def normalize_secret(x):
    """
    Finds the "normalized" secret key, as in the output of make_secret
    associated to a number modulo ORDER

    Simply solves the system:
    0 <= k < 2^251
    output = 8 * (2^251 + k)
    x = output % ORDER
    """
    inv8 = pow(8, ORDER - 2, ORDER)
    k = (x * inv8 % ORDER - 2 ** 251) % ORDER
    bit = 1 << 251
    # the key space has only 2^252 keys and is slightly smaller than ORDER
    assert not bit & k
    return (bit | k) << 3


def keccak256(x):
    k = keccak.new(digest_bits=256)
    k.update(x.to_bytes(32, "big"))
    return int.from_bytes(k.digest(), "big")


def ecies_encrypt(b, r, xA):
    return b ^ keccak256(mult(r, xA))


def ecies_decrypt(m1, xR, a):
    return m1 ^ keccak256(mult(a, xR))


def ecies_check(xA, xR, m1, xB, r):
    return xR == curve25519(r) and curve25519(m1 ^ keccak256(mult(r, xA))) == xB


class Namespace:
    pass


if __name__ == "__main__":

    # We use `Curve25519` with generator `G`.
    # Capital letters (eg `A`) denote multiplications of `G`
    # by the associated lowercase letter (eg `a G`).
    # `xA` is the x coordinate of point `A`.
    # `A` is the full point `(xA, yA)`
    # `k . xA` is the x coordinate of `k A`
    # (Note: we cannot know its sign because the y coordinate is missing)

    # Alice wants to send a private key `m` associated with the public key `M` to Bob.
    # She has a private key `a` and a public key `xA`
    Public = Namespace()
    Alice = Namespace()
    Bob = Namespace()

    Alice.m = make_secret()
    Public.M = curve25519(Alice.m, include_y=True)

    Alice.a = make_secret()
    Public.xA = curve25519(Alice.a)

    # Bob generates a secret `b` and publishes `B`.
    Bob.b = make_secret()
    Public.B = Public.xB, _ = curve25519(Bob.b, include_y=True)

    # Bob sends `b` securely to Alice using ECIES
    # https://en.wikipedia.org/wiki/Integrated_Encryption_Scheme
    Bob.r = make_secret()
    Public.xR = curve25519(Bob.r)
    Public.m1 = ecies_encrypt(Bob.b, Bob.r, Public.xA)

    # Alice checks that `B` is valid
    assert valid(*Public.B)
    # Alice decrypts `b` and checks that it corresponds to B
    Alice.b = ecies_decrypt(Public.m1, Public.xR, Alice.a)
    assert curve25519(Alice.b) == Public.xB, "A claims the value is false"

    # If Alice claims that the value is false, Bob can make r public
    Public.r = Bob.r
    assert ecies_check(Public.xA, Public.xR, Public.m1, Public.xB, Public.r)
    del Public.r

    # Alice publishes m2
    Public.m2 = (Alice.m + Alice.b) % ORDER

    Bob.m = normalize_secret(Public.m2 - Bob.b)

    # Bob has got the correct secret
    assert Bob.m == Alice.m
    # Anyone can see that m was sent to Bob
    assert curve25519(Public.m2, include_y=True) == add(Public.M, Public.B)
