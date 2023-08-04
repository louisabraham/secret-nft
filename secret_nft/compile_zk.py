import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import sys

from secret_nft.zk_utils import compile

if __name__ == "__main__":
    help = "--help" in sys.argv or "-h" in sys.argv
    if help:
        print("Usage: python compile_zk.py [-f|--force] [-d|--debug]")
    force = "--force" in sys.argv or "-f" in sys.argv
    debug = "--debug" in sys.argv or "-d" in sys.argv
    compile("sha256", debug=debug, force=force)
    compile("keccak", debug=debug, force=force)
