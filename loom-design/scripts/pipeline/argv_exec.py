#!/usr/bin/env python3
"""Decode a shell-safe payload and dispatch a validated batch_queue argv."""

from __future__ import annotations

import base64
import binascii
import json
import re
import sys
from collections.abc import Sequence

import batch_queue


_PAYLOAD_RE = re.compile(r"[A-Za-z0-9_-]+")


def _matches(argv: list[str], pattern: tuple[str | None, ...]) -> bool:
    return len(argv) == len(pattern) and all(
        expected is None or actual == expected
        for actual, expected in zip(argv, pattern)
    )


def _valid_schema(argv: list[str]) -> bool:
    patterns = (
        ("reconcile", "--project", None),
        ("next", "--project", None, "--skills-root", None),
        ("mark-running", None, "--run-id", None, "--session-dir", None,
         "--project", None),
        ("mark", None, "done", "--project", None, "--run-id", None),
        ("mark", None, "failed", "--project", None, "--run-id", None),
        ("reset", None, "--project", None),
        ("reset", None, "--project", None, "--reason", None),
        ("force-fail", None, "--reason", None, "--project", None),
        ("status", "--project", None),
    )
    return bool(argv) and any(_matches(argv, pattern) for pattern in patterns)


def decode_payload(payload: str) -> list[str]:
    """Return validated argv or raise ValueError for any unsafe shape."""
    if not _PAYLOAD_RE.fullmatch(payload):
        raise ValueError("payload must use only the URL-safe base64 alphabet")
    padded = payload + "=" * (-len(payload) % 4)
    try:
        raw = base64.b64decode(padded, altchars=b"-_", validate=True)
        decoded = json.loads(raw.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("payload is not URL-safe base64 JSON") from error
    if not isinstance(decoded, list) or not all(
        isinstance(item, str) for item in decoded
    ):
        raise ValueError("decoded payload must be a JSON list of strings")
    if not _valid_schema(decoded):
        raise ValueError("decoded argv does not match a supported command schema")
    return decoded


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        print("usage: argv_exec.py <URL_SAFE_BASE64_JSON_ARGV>", file=sys.stderr)
        return 2
    try:
        decoded = decode_payload(arguments[0])
    except ValueError as error:
        print(f"argv_exec: {error}", file=sys.stderr)
        return 2
    return batch_queue.main(decoded)


if __name__ == "__main__":
    sys.exit(main())
