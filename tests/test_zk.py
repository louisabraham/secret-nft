import random

from brownie import Verifier, accounts, zkEscrow_keccak, zkEscrow_sha256
from zokrates_pycrypto.eddsa import PrivateKey, PublicKey

from secret_nft.utils import Namespace, int_to_u32_array, keccak256, sha256
from secret_nft.zk_utils import prove


def _test_zk(use_keccak):
    use_keccak = False
    if use_keccak:
        hash = keccak256
        name = "keccak"
        zkEscrow = zkEscrow_keccak
    else:
        hash = sha256
        name = "sha256"
        zkEscrow = zkEscrow_sha256

    Public = Namespace()
    Alice = Namespace()
    Bob = Namespace()
    total_gas = 0

    # Alice wants to send a secret `secret` with  hash `fingerprint` to Bob.
    Alice.secret = random.randrange(2**256)
    Public.fingerprint = hash(Alice.secret)

    Bob.private_key = PrivateKey.from_rand()
    Public.public_key = PublicKey.from_private(Bob.private_key)

    alice = accounts[0]
    bob = accounts[1]
    eve = accounts[2]
    amount = "10 ether"

    verifier = Verifier.deploy({"from": eve})
    print("Verifier deployment used", verifier.tx.gas_used)

    escrow = zkEscrow.deploy(
        verifier.address,
        int_to_u32_array(Public.fingerprint),
        [Public.public_key.p.x.n, Public.public_key.p.y.n],
        {"from": bob, "value": amount},
    )
    print("Escrow deployment used", escrow.tx.gas_used)
    total_gas += escrow.tx.gas_used

    Alice.salt = PrivateKey.from_rand()
    Public.public_salt = PublicKey.from_private(Alice.salt)

    Alice.mask = hash(Public.public_key.p.mult(Alice.salt.fe).compress())
    Public.msg = Alice.secret ^ Alice.mask

    proof = prove(
        name,
        [
            Alice.salt.fe.n,
            int_to_u32_array(Public.fingerprint),
            [Public.public_key.p.x.n, Public.public_key.p.y.n],
            int_to_u32_array(Public.msg),
            [Public.public_salt.p.x.n, Public.public_salt.p.y.n],
        ],
    )

    tx = escrow.alice(
        int_to_u32_array(Public.msg),
        [Public.public_salt.p.x.n, Public.public_salt.p.y.n],
        (proof["proof"]["a"], proof["proof"]["b"], proof["proof"]["c"]),
        {"from": alice},
    )
    print("Alice used", tx.gas_used)
    total_gas += tx.gas_used

    # Bob decrypts the message
    Bob.mask = hash(Public.public_salt.p.mult(Bob.private_key.fe).compress())
    Bob.secret = Public.msg ^ Bob.mask

    # Bob has got the correct secret
    assert Bob.secret == Alice.secret

    print("Total escrow gas", total_gas)
    print("Total gas", total_gas + verifier.tx.gas_used)


def test_zk_sha256():
    _test_zk(False)


def test_zk_keccak():
    _test_zk(True)
