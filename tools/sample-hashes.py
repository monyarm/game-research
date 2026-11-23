#!/usr/bin/env python3
"""Print detection metadata for one or more sample files.

For each file this prints the three values a detection table needs:

- the exact size in bytes,
- the MD5 of the first 5,000 bytes, which is the hash ScummVM detection
  tables pair with the file size,
- the SHA-256 of the whole file, which is this repository's sample identity.

Usage:
    python3 tools/sample-hashes.py FILE [FILE ...]        # markdown rows
    python3 tools/sample-hashes.py --plain FILE [...]    # plain text

The output rows are ready to paste under a `| File | Size (bytes) |
MD5 (first 5,000 bytes) | SHA-256 |` header. Use the Markdown form unless a
plain listing is easier to read.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

HEAD_BYTES = 5000
CHUNK = 1024 * 1024


def hashes(path: Path) -> tuple[int, str, str]:
    """Return (size, md5 of the first 5,000 bytes, sha256 of the whole file)."""
    size = path.stat().st_size

    head_md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    remaining_head = HEAD_BYTES

    with path.open("rb") as handle:
        while True:
            chunk = handle.read(CHUNK)
            if not chunk:
                break
            sha256.update(chunk)
            if remaining_head > 0:
                head = chunk[:remaining_head]
                head_md5.update(head)
                remaining_head -= len(head)

    return size, head_md5.hexdigest(), sha256.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print size, MD5 of the first 5,000 bytes, and SHA-256 for sample files."
    )
    parser.add_argument("--plain", action="store_true", help="print plain text instead of table rows")
    parser.add_argument("files", nargs="+", metavar="FILE")
    args = parser.parse_args()

    if not args.plain:
        print("| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |")
        print("| --- | ---: | --- | --- |")

    for name in args.files:
        path = Path(name)
        if not path.is_file():
            print(f"not a file: {name}", file=sys.stderr)
            return 1

        size, head_md5, sha256 = hashes(path)

        if args.plain:
            print(f"{path.name}\tsize={size}\tmd5_first_5k={head_md5}\tsha256={sha256}")
            if size < HEAD_BYTES:
                print(f"  note: file is smaller than {HEAD_BYTES} bytes, so the MD5 covers the whole file", file=sys.stderr)
        else:
            print(f"| `{path.name}` | {size} | `{head_md5}` | `{sha256}` |")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
