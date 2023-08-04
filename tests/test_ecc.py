from brownie import accounts, eccEscrow

from secret_nft.curve25519 import (
    ORDER,
    add,
    curve25519,
    make_secret,
    normalize_secret,
    valid,
)
from secret_nft.ecc import ecies_check, ecies_decrypt, ecies_encrypt
from secret_nft.utils import Namespace


def test():
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
    total_gas = 0

    Alice.m = make_secret()
    Public.M = curve25519(Alice.m, include_y=True)

    Alice.a = make_secret()
    Public.xA = curve25519(Alice.a)

    alice = accounts[0]
    bob = accounts[1]
    amount = "10 ether"
    escrow = eccEscrow.deploy(Public.M, Public.xA, bob, amount, {"from": alice})
    print("Deployment used", escrow.tx.gas_used)
    total_gas += escrow.tx.gas_used

    # Bob generates a secret `b` and publishes `B`.
    Bob.b = make_secret()
    Public.B = Public.xB, _ = curve25519(Bob.b, include_y=True)

    # Bob sends `b` securely to Alice using ECIES
    # https://en.wikipedia.org/wiki/Integrated_Encryption_Scheme
    Bob.salt = make_secret()
    Public.m1 = ecies_encrypt(Bob.b, Bob.salt, Public.xA)

    tx = escrow.bob(Public.B, *Public.m1, {"from": bob, "value": amount})
    print("Bob used", tx.gas_used)
    total_gas += tx.gas_used

    # Alice checks that `B` is valid
    assert valid(*Public.B)
    # Alice decrypts `b` and checks that it corresponds to B
    Alice.b = ecies_decrypt(Public.m1, Alice.a)
    assert curve25519(Alice.b) == Public.xB, "A claims the value is false"

    # If Alice claims that the value is false, Bob can make `salt`` public
    Public.salt = Bob.salt
    assert ecies_check(Public.xA, Public.m1, Public.xB, Public.salt)
    del Public.salt

    # Alice publishes m2
    Public.m2 = (Alice.m + Alice.b) % ORDER

    tx = escrow.alice(Public.m2, {"from": alice})
    print("Alice used", tx.gas_used)
    total_gas += tx.gas_used

    Bob.m = normalize_secret(Public.m2 - Bob.b)

    # Bob has got the correct secret
    assert Bob.m == Alice.m
    # Anyone can see that m was sent to Bob
    assert curve25519(Public.m2, include_y=True) == add(Public.M, Public.B)

    print("Total gas used", total_gas)
