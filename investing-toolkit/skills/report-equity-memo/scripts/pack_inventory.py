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

# bfe0353e's fix derived this set from ONLY pack_us.py `run_client` +
# pack_tw.py's mops wrap() — it never looked at pack_jp/pack_kr/pack_cn, so
# their error dialects (_stdout_head, stdout_tail, _partial) fell outside
# the set and read as false-presence (round-2 whole-branch review finding).
# Catalogued from ALL FIVE markets' actual failure branches:
#   - pack_us.py run_client (pack_us.py:201-224): error, _cmd, _returncode,
#     script, args, returncode, stderr, detail, stdout_head.
#   - pack_jp.py _run_client (pack_jp.py:152-181): error, _cmd,
#     _stdout_head, _stderr.
#   - pack_kr.py _run (pack_kr.py:179-201): error, _partial, stderr,
#     returncode, stdout_tail, _returncode.
#   - pack_cn.py _run (pack_cn.py:160-178): _error, _cmd, _stderr,
#     _stdout_head.
#   - pack_tw.py run_client + mops wrap() (pack_tw.py:151-186):
#     _error, _cmd, _stderr, _stdout_head, _tier, _source, _action.
# Every one of these diagnostic keys holds a SCALAR (str/int/bool) in every
# market above — this list only needs to gate scalar values (see
# _has_data_signal below for why dict/list values don't need it).
_METADATA_SCALAR_KEYS = frozenset({
    "error", "_error",
    "_cmd", "_returncode", "script", "args", "returncode", "stderr", "_stderr",
    "detail", "stdout_head", "_stdout_head", "stdout_tail",
    "_tier", "_source", "_action", "_partial",
})


def _has_data_signal(section: dict) -> bool:
    """True if `section` carries at least one key with real fetched data.

    Two-part discriminator, justified against all 5 markets' real shapes:
      - A non-empty dict, or a list containing at least one dict, is ALWAYS
        real data (`concepts`, `canonical_dcf`, TW mops's `data`, financial
        statements, price-history rows, ...) — no market's failure branches
        ever nest a dict/list-of-dicts as diagnostic metadata (their `_cmd`/
        `args` lists hold only plain strings, never dicts). Shape alone
        disambiguates here, no key-name list needed — this is what makes the
        allowlist inversion actually more robust than a denylist: a future
        market's new *dict-shaped* data key needs no update to this file.
      - A scalar value (str/int/bool) can't be told apart from a diagnostic
        by shape alone (an error string and a real string field are both
        `str`) — those fall back to the `_METADATA_SCALAR_KEYS` name list.
        This is the one residual surface that still needs updating if a
        future market invents a new scalar-shaped diagnostic key.
    """
    for key, value in section.items():
        if isinstance(value, dict) and value:
            return True
        if isinstance(value, list) and any(isinstance(item, dict) for item in value):
            return True
        if key not in _METADATA_SCALAR_KEYS and value is not None and value != "":
            return True
    return False


def _is_failed_section(section: dict) -> bool:
    """Shape-based predicate: does this section report no usable data?

    A section reports no data when it declares `_status: "failed"`, reports
    a {requested, succeeded, failed} count triple with `succeeded == 0`, or
    carries an `error`/`_error` marker with NO data signal anywhere in the
    dict (see `_has_data_signal`).

    An `error`/`_error` marker sitting ALONGSIDE real data means the section
    is PARTIAL, not absent — e.g. `sec_facts` is a MERGED dict where the
    `facts` subprocess can time out while its `concepts`/`canonical_dcf`
    siblings (~10 separate subprocess calls) succeed. Generic on purpose —
    no section-name special-casing — so any future section (any market)
    gets this for free.
    """
    if section.get("_status") == "failed":
        return True
    if all(key in section for key in _COUNT_TRIPLE_KEYS) and section["succeeded"] == 0:
        return True
    if "error" in section or "_error" in section:
        return not _has_data_signal(section)
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
