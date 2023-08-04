import json
import os
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen

zokrates_dir = Path(__file__).parent.parent / "zokrates"


def patch_verifier(path):
    with open(path, "r") as f:
        code = f.read()
    # https://ethereum.stackexchange.com/q/115375/5101
    code = code.replace("using Pairing for *;", "")
    with open(path, "w") as f:
        f.write(code)


def compile(name, *, debug=False, force=False):
    subdir = (zokrates_dir / name).resolve()
    if (
        not force
        and (subdir / "out").exists()
        and os.path.getmtime(subdir / "main.zok") < os.path.getmtime(subdir / "out")
    ):
        return
    p = Popen(
        [
            "zokrates",
            "compile",
            "-i",
            "main.zok",
        ]
        + ["--debug"] * debug,
        cwd=subdir,
        stdout=PIPE,
        stderr=STDOUT,
    )
    p.wait()
    if p.returncode != 0:
        print(p.stdout.read().decode())
        raise Exception("Compilation failed")
    p = Popen(
        [
            "zokrates",
            "setup",
        ],
        cwd=subdir,
        stdout=PIPE,
        stderr=STDOUT,
    )
    p.wait()
    if p.returncode != 0:
        print(p.stdout.read().decode())
        raise Exception("Setup failed")
    p = Popen(
        [
            "zokrates",
            "export-verifier",
        ],
        cwd=subdir,
        stdout=PIPE,
        stderr=STDOUT,
    )
    p.wait()
    if p.returncode != 0:
        print(p.stdout.read().decode())
        raise Exception("Setup failed")
    patch_verifier(subdir / "verifier.sol")


def encode(x):
    if isinstance(x, list):
        return [encode(y) for y in x]
    if isinstance(x, int):
        return str(x)
    assert False


def prove(name, args):
    subdir = zokrates_dir / name
    out = encode(args)
    out = json.dumps(out)
    p = Popen(
        [
            "zokrates",
            "compute-witness",
            "--abi",
            "--stdin",
        ],
        cwd=subdir,
        stdin=PIPE,
        stdout=PIPE,
    )
    p.stdin.write(out.encode())
    p.stdin.close()
    p.wait()
    if p.returncode != 0:
        print(p.stdout.read().decode())
        raise Exception("Witness computation failed")
    p = Popen(
        [
            "zokrates",
            "generate-proof",
        ],
        cwd=subdir,
        stdin=PIPE,
        stdout=PIPE,
    )
    p.stdin.write(out.encode())
    p.stdin.close()
    p.wait()
    with open(subdir / "proof.json", "r") as f:
        proof = json.load(f)

    return proof
