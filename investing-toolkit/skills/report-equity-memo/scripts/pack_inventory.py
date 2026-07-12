#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""pack_inventory.py — Machine-readable section inventory for a data-markets pack.

Reads a data-markets pack JSON (any of the 5 pack types emitted by
data-markets/scripts/pack.py) and emits a JSON inventory of its top-level
sections to stdout: which sections are present, their shape (dict/list/
scalar), and their size (keys for dicts, rows for lists).

Ground truth for the memo-writing LLM: report-equity-memo passes this
inventory alongside the raw pack so a claim like "T86/margin data was
unavailable" can be checked against what Layer 1 actually fetched, instead
of trusting the LLM's own read of a large JSON blob.

PURE FUNCTION — no HTTP, no subprocess, no env access. Input is a
pre-fetched pack JSON path; output goes to stdout.

Underscore-prefixed top-level keys (_provenance, _partial, _normalized, ...)
are pack metadata, not analysis sections, and are excluded from `sections`.
`_status` (if the pack carries one) is echoed verbatim at the top level.

`mops` (TW pack's MOPS/公開資訊觀測站 bundle) is a dict-of-dicts; when present,
its immediate children get their own one-level-down inventory under
`mops_subsections`, using the same present/kind/rows|keys shape.

Exit codes: 0 success, 64 (EX_USAGE) on missing/unreadable/unparseable input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EX_USAGE = 64


_COUNT_TRIPLE_KEYS = ("requested", "succeeded", "failed")

# Keys that only ever carry failure METADATA, never analysis data, across
# this pack family's actual error-producing shapes:
#   - pack_us.py run_client's three failure branches (timeout / non-zero-exit
#     / invalid-json, pack_us.py:201-224): error, _cmd, _returncode, script,
#     args, returncode, stderr, detail, stdout_head.
#   - pack_tw.py's mops `{_tier, _source, _action, data|_error, _stderr,
#     _cmd}` wrapper envelope (pack_tw.py:175,468,581-582): _tier, _source,
#     _action, _error, _stderr (_cmd/error already covered above).
# A dict carrying an error marker is "failed" only if EVERY one of its keys
# is in this set; any other key alongside the marker is real sibling data
# (F1 fix — see phase4-seed-contract.md:9,36-39).
_ERROR_ENVELOPE_KEYS = frozenset({
    "error", "_error",
    "_cmd", "_returncode", "script", "args", "returncode", "stderr",
    "detail", "stdout_head",
    "_tier", "_source", "_action", "_stderr",
})


def _is_failed_section(section: dict) -> bool:
    """Shape-based predicate: does this section report no usable data?

    A section reports no data when it declares `_status: "failed"`, reports
    a {requested, succeeded, failed} count triple with `succeeded == 0`, or
    carries an `error`/`_error` marker with NO other key beyond
    `_ERROR_ENVELOPE_KEYS` (i.e. the whole dict IS the error envelope).

    An `error`/`_error` marker sitting ALONGSIDE a non-envelope key (real
    data) means the section is PARTIAL, not absent — e.g. `sec_facts` is a
    MERGED dict where the `facts` subprocess can time out while its
    `concepts`/`canonical_dcf` siblings (~10 separate subprocess calls)
    succeed. Generic on purpose — no section-name special-casing — so any
    future section (any market) gets this for free.
    """
    if section.get("_status") == "failed":
        return True
    if all(key in section for key in _COUNT_TRIPLE_KEYS) and section["succeeded"] == 0:
        return True
    if "error" in section or "_error" in section:
        return all(key in _ERROR_ENVELOPE_KEYS for key in section)
    return False


def _classify(value: object) -> dict:
    """Return the {present, kind, rows|keys} entry for one section value."""
    if isinstance(value, dict):
        keys = len(value)
        present = keys > 0 and not _is_failed_section(value)
        return {"present": present, "kind": "dict", "keys": keys}
    if isinstance(value, list):
        rows = len(value)
        return {"present": rows > 0, "kind": "list", "rows": rows}
    return {"present": value is not None, "kind": "scalar"}


def _inventory(section: dict) -> dict:
    return {key: _classify(value) for key, value in section.items()}


def build_inventory(pack: dict, input_path: Path) -> dict:
    top_level = {k: v for k, v in pack.items() if not k.startswith("_")}
    result: dict = {
        "sections": _inventory(top_level),
        "_status": pack.get("_status"),
        "_meta": {"generated_from": input_path.name, "tool": "pack_inventory"},
    }
    mops = pack.get("mops")
    if isinstance(mops, dict):
        result["mops_subsections"] = _inventory(mops)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Turn a data-markets pack JSON into a machine-readable section inventory.",
    )
    parser.add_argument("--input", required=True, help="Path to the pack JSON file")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"pack_inventory: input file not found: {input_path}", file=sys.stderr)
        return EX_USAGE

    try:
        text = input_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"pack_inventory: cannot read input file: {exc}", file=sys.stderr)
        return EX_USAGE

    try:
        pack = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"pack_inventory: malformed JSON in input file: {exc}", file=sys.stderr)
        return EX_USAGE

    if not isinstance(pack, dict):
        print("pack_inventory: input JSON must be an object at top level", file=sys.stderr)
        return EX_USAGE

    print(json.dumps(build_inventory(pack, input_path), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
