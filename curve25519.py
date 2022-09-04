MOD = (1 << 255) - 19
ORDER = 2 ** 252 + 27742317777372353535851937790883648493


def valid(x, y):
    return y ** 2 % MOD == x * (1 + 486662 * x + (x * x % MOD)) % MOD


def scale(x, z):
    return x * pow(z, MOD - 2, MOD) % MOD


def double_add(p2, p3, X1=9):
    """
    compute
        - p4 = 2 * p2
        - p5 = p3 + p2
    assuming that p2 - p3 = (X1 : 1)

    formula from
        - https://www.hyperelliptic.org/EFD/g1p/auto-montgom-xz.html#ladder-mladd-1987-m
        - https://eprint.iacr.org/2017/293.pdf 4.6
    """
    X2, Z2 = p2
    X3, Z3 = p3

    a = 486662
    a24 = (a + 2) // 4  # careful, a24 != (a - 2) // 4

    A = X2 + Z2
    AA = A ** 2 % MOD
    B = X2 - Z2
    BB = B ** 2 % MOD
    E = AA - BB
    C = X3 + Z3
    D = X3 - Z3
    DA = D * A % MOD
    CB = C * B % MOD
    X5 = (DA + CB) ** 2 % MOD
    Z5 = X1 * (DA - CB) ** 2 % MOD
    X4 = AA * BB % MOD
    Z4 = E * (BB + a24 * E) % MOD

    return (X4, Z4), (X5, Z5)


def add(p1, p2):
    """Point addition"""
    # https://crypto.stackexchange.com/a/75879/56838
    a = 486662
    x1, y1 = p1
    x2, y2 = p2
    alpha = scale(y2 - y1, x2 - x1)
    x3 = alpha * alpha % MOD - a - x1 - x2
    y3 = alpha * (x1 - x3) % MOD - y1
    return x3 % MOD, y3 % MOD


def double(X1):
    """compute (X1 : 1) + (X1 : 1)"""
    a = 486662
    XX1 = X1 ** 2 % MOD
    X3 = (XX1 - 1) ** 2
    Z3 = 4 * X1 * (XX1 + a * X1 + 1)
    return X3, Z3


def mult(k, x):
    """
    Montgomery ladder to compute k . (x : 1)
    note: Montgomery's PRAC is faster
    """
    r0 = (x, 1)
    r1 = double(x)
    for i in bin(k)[3:]:
        if i == "0":
            r0, r1 = double_add(r0, r1, x)
        else:
            r1, r0 = double_add(r1, r0, x)
    return scale(*r0)


def recover(Q, S):
    """
    Okeya-Sakurai recovery from https://eprint.iacr.org/2017/212.pdf 4.3
    find yQ from:
        - x coordinates of P, Q, S := P+Q
        - y coordinate of P

    we only implemented the case P = (9 : 1)
    """
    XQ, ZQ = Q
    XS, ZS = S
    xP = 9
    yP = 14781619447589544791020593568409986887264606134616475288964881837755586237401
    A, B = 486662, 1

    v1 = xP * ZQ % MOD
    v2 = XQ + v1
    v3 = XQ - v1
    v3 = v3 ** 2 % MOD
    v3 = v3 * XS % MOD
    v1 = 2 * A * ZQ % MOD
    v2 = v2 + v1
    v4 = xP * XQ % MOD
    v4 = v4 + ZQ
    v2 = v2 * v4 % MOD
    v1 = v1 * ZQ % MOD
    v2 = v2 - v1
    v2 = v2 * ZS % MOD
    Y = v2 - v3
    v1 = 2 * B * yP % MOD
    v1 = v1 * ZQ % MOD
    v1 = v1 * ZS % MOD
    X = v1 * XQ % MOD
    Z = v1 * ZQ % MOD
    # assert scale(X, Z) == scale(XQ, ZQ)
    return scale(X, Z), scale(Y, Z)


def curve25519(k, *, include_y=False):
    """
    Compute k * P with P the base point.

    https://eprint.iacr.org/2017/212.pdf
    """
    r0 = (9, 1)
    x2 = 14847277145635483483963372537557091634710985132825781088887140890597596352251
    r1 = (x2, 1)
    for i in bin(k)[3:]:
        if i == "0":
            r0, r1 = double_add(r0, r1)
        else:
            r1, r0 = double_add(r1, r0)
    return recover(r0, r1) if include_y else scale(*r0)


if __name__ == "__main__":
    # Basic tests
    assert curve25519(ORDER) == 0
    assert curve25519(ORDER + 1, include_y=True) == curve25519(1, include_y=True)
