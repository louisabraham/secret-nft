from .curve25519 import curve25519, mult
from .utils import keccak256


def ecies_encrypt(secret, salt, xPub):
    return curve25519(salt), secret ^ keccak256(mult(salt, xPub))


def ecies_decrypt(msg, a):
    public_salt, msg = msg
    return msg ^ keccak256(mult(a, public_salt))


def ecies_check(public_key, msg, fingerprint, salt):
    public_salt, msg = msg
    secret = msg ^ keccak256(mult(salt, public_key))
    return curve25519(salt) == public_salt and curve25519(secret) == fingerprint
