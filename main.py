"""Deliver the finished front page to the grader.

The picture is already drawn and stored in this repository at
assets/entry.png. This program only copies those bytes into the output
folder the grader gives it (MAKEFUN_OUTPUT_DIR, or /output when that
is unset), so running it twice always produces identical output.
"""

import os
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent
PICTURE = REPO / "assets" / "entry.png"


def main():
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PICTURE, target_dir / "entry.png")


if __name__ == "__main__":
    main()
