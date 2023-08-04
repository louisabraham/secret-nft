// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

contract eccEscrow {
    uint256 constant MOD = (1 << 255) - 19;
    uint256 Y1 =
        14781619447589544791020593568409986887264606134616475288964881837755586237401;
    address Alice;
    address Bob;
    uint256[2] public M;
    uint256 public xA;
    uint256[2] public B;
    uint256 public xR;
    uint256 public m1;
    uint256 public amount;

    constructor(
        uint256[2] memory _M,
        uint256 _xA,
        address _Bob,
        uint256 _amount
    ) {
        // Alice inits
        Alice = msg.sender;
        M = _M;
        xA = _xA;
        Bob = _Bob;
        amount = _amount;
    }

    function bob(
        uint256[2] calldata _B,
        uint256 _xR,
        uint256 _m1
    ) external payable {
        require(msg.sender == Bob);
        require(msg.value == amount);
        B = _B;
        xR = _xR;
        m1 = _m1;
    }

    function _expmod(uint256 base, uint256 e) public view returns (uint256 o) {
        assembly {
            // define pointer
            let p := mload(0x40)
            // store data assembly-favouring ways
            mstore(p, 0x20) // Length of Base
            mstore(add(p, 0x20), 0x20) // Length of Exponent
            mstore(add(p, 0x40), 0x20) // Length of Modulus
            mstore(add(p, 0x60), base) // Base
            mstore(add(p, 0x80), e) // Exponent
            mstore(add(p, 0xa0), MOD) // Modulus
            if iszero(staticcall(sub(gas(), 2000), 0x05, p, 0xc0, p, 0x20)) {
                revert(0, 0)
            }
            // data
            o := mload(p)
        }
    }

    function _mul(uint256 a, uint256 b) public pure returns (uint256) {
        return mulmod(a, b, MOD);
    }

    function _add(uint256 a, uint256 b) public pure returns (uint256 ans) {
        ans = a + b;
        if (ans > MOD) ans -= MOD;
    }

    function _sub(uint256 a, uint256 b) public pure returns (uint256) {
        if (a >= b) return a - b;
        else return a + MOD - b;
    }

    function _divmod(uint256 a, uint256 b) public view returns (uint256 ans) {
        ans = _mul(a, _expmod(b, MOD - 2));
    }

    function _double_add(
        uint256 X2,
        uint256 Z2,
        uint256 X3,
        uint256 Z3
    ) public pure returns (uint256 X4, uint256 Z4, uint256 X5, uint256 Z5) {
        uint256 A_ = _add(X2, Z2);
        uint256 AA = _mul(A_, A_);
        uint256 B_ = _sub(X2, Z2);
        uint256 BB = _mul(B_, B_);
        uint256 E = _sub(AA, BB);
        uint256 C = _add(X3, Z3);
        uint256 D = _sub(X3, Z3);
        uint256 DA = _mul(D, A_);
        uint256 CB = _mul(C, B_);
        X5 = _mul(DA + CB, DA + CB);
        Z5 = _mul(9, _mul(_sub(DA, CB), _sub(DA, CB)));
        X4 = _mul(AA, BB);
        Z4 = _mul(E, (BB + _mul(121666, E)));
    }

    function _add(
        uint256 x1,
        uint256 y1,
        uint256 x2,
        uint256 y2
    ) public view returns (uint256) {
        uint256 alpha = _divmod(_sub(y2, y1), _sub(x2, x1));
        return _sub(_sub(_sub(_mul(alpha, alpha), 486662), x1), x2);
        // y3 = _sub(mul(alpha, _sub(x1, x3)), y1);
    }

    function _curve25519(uint256 k) public view returns (uint256) {
        uint256 X0 = 9;
        uint256 Z0 = 1;
        uint256 X1 = 14847277145635483483963372537557091634710985132825781088887140890597596352251;
        uint256 Z1 = 1;
        uint256 bit = 1 << 255;
        while (bit & k == 0) bit >>= 1;
        bit >>= 1;
        while (bit != 0) {
            if (bit & k != 0) (X1, Z1, X0, Z0) = _double_add(X1, Z1, X0, Z0);
            else (X0, Z0, X1, Z1) = _double_add(X0, Z0, X1, Z1);
            bit >>= 1;
        }
        return _divmod(X0, Z0);
    }

    function alice(uint256 m2) public {
        require(msg.sender == Alice);
        require(_curve25519(m2) == _add(M[0], M[1], B[0], B[1]));
        payable(Alice).transfer(address(this).balance);
    }
}
