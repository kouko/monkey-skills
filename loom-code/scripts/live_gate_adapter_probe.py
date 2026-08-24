#!/usr/bin/env python3
"""Deterministically exercise live-host adapter refusal boundaries.

This gate-only executable turns two prose adapter rules into observable
process results.  It never resolves review context, invokes a station, or
writes a marker.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REFUSAL_TYPE = "loom.live-gate.adapter-refusal"
REFERENCE_NAMES = {
    "claude": "claude-code-tools.md",
    "codex": "codex-tools.md",
}
SHA_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


def _emit(kind: str, case: str, reason: str) -> int:
    print(json.dumps({"type": kind, "case": case, "reason": reason}, sort_keys=True))
    return 3 if kind == REFUSAL_TYPE else 0


def _loaded_reference(host: str, raw_path: str) -> int:
    path = Path(raw_path)
    if not path.is_absolute():
        return _emit(
            REFUSAL_TYPE,
            "invalid-reference",
            "loaded-reference-path-not-absolute",
        )
    try:
        reference_is_invalid = path.is_symlink() or not path.is_file()
    except OSError:
        reference_is_invalid = True
    if reference_is_invalid:
        return _emit(
            REFUSAL_TYPE,
            "invalid-reference",
            "loaded-reference-not-regular",
        )
    if path.name != REFERENCE_NAMES[host]:
        return _emit(
            REFUSAL_TYPE,
            "invalid-reference",
            "loaded-reference-host-mismatch",
        )
    try:
        canonical_reference = path.resolve(strict=True)
        plugin_root = canonical_reference.parents[3]
    except (IndexError, OSError):
        return _emit(
            REFUSAL_TYPE,
            "invalid-reference",
            "loaded-reference-root-unresolvable",
        )
    expected_reference = (
        plugin_root
        / "skills"
        / "using-loom-code"
        / "references"
        / REFERENCE_NAMES[host]
    )
    if canonical_reference != expected_reference:
        return _emit(
            REFUSAL_TYPE,
            "invalid-reference",
            "loaded-reference-layout-invalid",
        )
    try:
        root_is_invalid = not (plugin_root / "scripts/review_context.py").is_file()
    except OSError:
        root_is_invalid = True
    if root_is_invalid:
        return _emit(
            REFUSAL_TYPE,
            "invalid-reference",
            "loaded-reference-root-unresolvable",
        )
    return _emit(
        "loom.live-gate.adapter-acceptance",
        "valid-reference",
        "loaded-reference-accepted",
    )


def _post_fix_sha(initial_sha: str, post_fix_sha: str) -> int:
    if not SHA_RE.fullmatch(initial_sha) or not SHA_RE.fullmatch(post_fix_sha):
        return _emit(
            REFUSAL_TYPE,
            "unchanged-post-fix",
            "reviewed-sha-invalid",
        )
    if initial_sha == post_fix_sha:
        return _emit(
            REFUSAL_TYPE,
            "unchanged-post-fix",
            "post-fix-sha-unchanged",
        )
    return _emit(
        "loom.live-gate.adapter-acceptance",
        "changed-post-fix",
        "post-fix-sha-changed",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)

    reference = subparsers.add_parser("loaded-reference")
    reference.add_argument("--host", choices=tuple(REFERENCE_NAMES), required=True)
    reference.add_argument("--loaded-reference-path", required=True)

    post_fix = subparsers.add_parser("post-fix-sha")
    post_fix.add_argument("--initial-sha", required=True)
    post_fix.add_argument("--post-fix-sha", required=True)

    args = parser.parse_args(argv)
    if args.operation == "loaded-reference":
        return _loaded_reference(args.host, args.loaded_reference_path)
    return _post_fix_sha(args.initial_sha, args.post_fix_sha)


if __name__ == "__main__":
    raise SystemExit(main())
