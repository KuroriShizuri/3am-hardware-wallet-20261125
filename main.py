#!/usr/bin/env python3
"""The 3 AM Excuse — make.fun entry (program/v1).

Writes one line, the excuse a hardware wallet gives for refusing to sign
a transaction at 3 AM, to /output/entry.txt (or $MAKEFUN_OUTPUT_DIR).

Gate: /output/entry.txt must be UTF-8 text of 1 to 200 characters, not
only white space, a single line.
"""

import os
import sys

ENTRY = (
    "You bought a dog coin at 3 AM once and cried into my seed phrase "
    "for a week. My buttons are on strike until sunrise."
)

MAX_CHARS = 200


def validate(line: str) -> None:
    """Raise ValueError unless the line passes the competition gate."""
    if not line or not line.strip():
        raise ValueError("entry is empty or only white space")
    if "\n" in line or "\r" in line:
        raise ValueError("entry must be a single line")
    if len(line) > MAX_CHARS:
        raise ValueError(
            f"entry is {len(line)} characters, over the {MAX_CHARS} limit"
        )


def output_path() -> str:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return os.path.join(out_dir, "entry.txt")


def run() -> str:
    validate(ENTRY)
    path = output_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = (ENTRY + "\n").encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    with open(path, "rb") as f:
        back = f.read()
    if back != data:
        raise ValueError("read-back mismatch: entry.txt is not byte-identical")
    # Runtime re-validation: decode what is actually on disk and re-check
    # the gate against the decoded text, not just the in-memory constant.
    decoded = back.decode("utf-8")
    if decoded.endswith("\n"):
        decoded = decoded[:-1]
    validate(decoded)
    if decoded != ENTRY:
        raise ValueError("re-validation: on-disk text differs from ENTRY")
    if len(decoded.encode("utf-8")) != len(data) - 1:
        raise ValueError("re-validation: byte length mismatch")
    return path


def self_test() -> bool:
    """Validate the line in memory and through a full write/read-back."""
    validate(ENTRY)
    path = run()
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if text.rstrip("\n") != ENTRY or text.count("\n") != 1:
        raise ValueError("self-test: entry.txt content mismatch")
    print(f"self-test ok: {len(ENTRY)} chars -> {path}")
    return True


def check() -> bool:
    """Validate the already-written /output/entry.txt against the gate."""
    path = output_path()
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    line = text.rstrip("\n")
    if text.count("\n") > 1 or "\r" in text:
        raise ValueError("check: entry.txt is not a single line")
    validate(line)
    if line != ENTRY:
        raise ValueError("check: entry.txt does not match the entry line")
    print(f"check ok: {len(line)} chars in {path}")
    return True


def main(argv) -> int:
    try:
        if "--self-test" in argv:
            self_test()
        elif "--check" in argv:
            check()
        else:
            path = run()
            print(f"wrote {len(ENTRY)} chars to {path}")
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
