// SPDX-License-Identifier: UNLICENSED
import "../zokrates/sha256/verifier.sol";

pragma solidity ^0.8.0;

contract zkEscrow_sha256 {
    uint32[8] public fingerprint;
    uint256[2] public publicKey;
    uint256 public amount;
    address public verifier;

    constructor(
        address _verifier,
        uint32[8] memory _fingerprint,
        uint256[2] memory _publicKey
    ) payable {
        // Bob inits and pays the price
        verifier = _verifier;
        fingerprint = _fingerprint;
        publicKey = _publicKey;
        amount = msg.value;
    }

    function alice(
        uint32[8] calldata message,
        uint256[2] calldata public_salt,
        Verifier.Proof calldata proof
    ) external {
        uint[20] memory input;
        for (uint i = 0; i < 8; i++) input[i] = fingerprint[i];
        for (uint i = 0; i < 2; i++) input[i + 8] = publicKey[i];
        for (uint i = 0; i < 8; i++) input[i + 10] = message[i];
        for (uint i = 0; i < 2; i++) input[i + 18] = public_salt[i];
        if (!Verifier(verifier).verifyTx(proof, input)) revert();
        payable(msg.sender).transfer(amount);
    }
}
