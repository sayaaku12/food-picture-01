#!/usr/bin/env python3
"""food-picture-01 entry: copy the bundled food picture to the output dir.

The image (entry.png, a 1024x1024 PNG) is a photorealistic overhead
shot of a steaming bowl of tonkotsu ramen: glossy golden broth, a
swirl of noodles, glistening chashu pork, a halved soft-boiled egg
with a jammy orange yolk, scallions, chili-oil swirls, sesame and
nori, in a dark ceramic bowl on dark slate. It was generated once
with an image model and is shipped in this repository. This program
only copies it verbatim: no network, no randomness, no timestamps,
so repeated runs produce identical bytes.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Fail loudly instead of shipping a truncated copy.
    if os.path.getsize(dst) != os.path.getsize(src):
        raise RuntimeError("entry.png copy is incomplete")


if __name__ == "__main__":
    main()
