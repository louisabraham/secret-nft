# Secret NFT

The goal of this repository is to be able to provably share secrets in presence of an arbitrator.

We implement two protocols in the form of Ethereum smart contracts.

In both cases, A(lice) wants to share a `secret` with B(ob).


The protocols are explained in [this blog post](https://louisabraham.github.io/articles/secret-nft/).

|                                   | ECC protocol                                           | ZK protocol                                                  |
| --------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| `fingerprint`                     | curve25519(`secret`)                                   | `SHA256(secret)` or `keccak(secret)`                         |
| Elliptic Curve                    | [Curve25519](https://en.wikipedia.org/wiki/Curve25519) | [Baby Jubjub](https://eips.ethereum.org/EIPS/eip-2494)       |
| Need of a trusted setup           | No                                                     | [Yes](https://zokrates.github.io/toolbox/trusted_setup.html) |
| Need for client-side verification | Yes                                                    | No                                                           |
| Number of messages                | 3 (A B A) when there is no cheating                    | 2 (B A)                                                      |
| Gas consumption                   | 1.5M                                                   | 900k                                                         |
| Dependencies                      | None                                                   | ZoKrates                                                     |

## Usage

### Setup

```sh
# Install ZoKrates
curl -LSfs get.zokrat.es | sh
# Install Python dependencies
pip install -r requirements.txt
```

### Compilation

```sh
python secret_nft/compile_zk.py
```

### Test

```sh
# -s to display full output
pytest -s
```

## Note

We did not implement the protocol that allows Alice to claim Bob cheated in their first message.
The verification is however simple to implement in Solidity by reproducing the `ecies_check` function.

A practical use does not necessarily require it as Bob could be allowed to claim back their funds after some time.
Alice would need to check that the contract still has a positive balance to avoid disclosing the secret without payment.

