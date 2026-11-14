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

After copying, the output is verified before the program reports
success: the output must be a structurally valid PNG exactly
1024x1024 px, its bytes must hash identically to the bundled image,
and it must be within the 1 MiB bounty cap. Any mismatch fails
loudly with a non-zero exit code instead of shipping a corrupt
or wrong picture.
"""
import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1024 * 1024  # bounty cap: image <= 1 MiB
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print("ERROR: " + message, file=sys.stderr)
    raise SystemExit(1)


def png_dimensions(data):
    """Return (width, height) from a PNG's IHDR chunk, or None if invalid."""
    if len(data) < 33 or data[:8] != PNG_SIGNATURE:
        return None
    # IHDR chunk: length (4 bytes) + type "IHDR" (4 bytes) + 13 bytes data.
    length, chunk_type = struct.unpack(">I4s", data[8:16])
    if chunk_type != b"IHDR" or length != 13:
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def verify(data, label, reference_hash=None):
    """Check a PNG's structure, dimensions, size, and hash. Fail loudly."""
    dims = png_dimensions(data)
    if dims is None:
        fail(label + " is not a valid PNG (bad signature or IHDR)")
    if dims != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        fail(
            "%s is %dx%d, expected %dx%d"
            % (label, dims[0], dims[1], EXPECTED_WIDTH, EXPECTED_HEIGHT)
        )
    if len(data) > MAX_BYTES:
        fail("%s is %d bytes, over the 1 MiB cap" % (label, len(data)))
    digest = sha256_hex(data)
    if reference_hash is not None and digest != reference_hash:
        fail(
            "%s sha256 %s does not match bundled image %s"
            % (label, digest, reference_hash)
        )
    return digest


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")

    with open(src, "rb") as f:
        src_bytes = f.read()
    # Verify the bundled image itself first: never copy a bad source.
    src_hash = verify(src_bytes, "bundled entry.png")

    # Write via a temp file + atomic rename, so a run killed mid-write
    # can never leave a partial entry.png at the destination. The temp
    # file is verified (hash + IEND trailer, i.e. the PNG is complete)
    # before the rename, and the final file is verified once more.
    tmp = dst + ".tmp"
    with open(tmp, "wb") as f:
        f.write(src_bytes)
        f.flush()
        os.fsync(f.fileno())
    with open(tmp, "rb") as f:
        tmp_bytes = f.read()
    if not tmp_bytes.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82"):
        fail("temporary entry.png is truncated (missing IEND chunk)")
    verify(tmp_bytes, "temporary entry.png", reference_hash=src_hash)
    os.replace(tmp, dst)
    with open(dst, "rb") as f:
        out_bytes = f.read()
    out_hash = verify(out_bytes, "output entry.png", reference_hash=src_hash)

    print(
        "entry.png verified: 1024x1024, %d bytes, sha256 %s"
        % (len(out_bytes), out_hash)
    )


if __name__ == "__main__":
    main()
