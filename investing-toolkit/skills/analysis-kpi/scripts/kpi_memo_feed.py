#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Memo-feed contract assembly (operational-kpi capability, slice 8 — final
offline slice).

Layer 2 (Analysis) PURE-ASSEMBLY — mirrors kpi_validate.py: stdlib only,
does NOT import `_store_fs`, does NOT resolve a store dir, does NOT lock
or write files. It takes the series data (`kpi_series`) as a caller-
supplied argument rather than querying `kpi_store` directly — decoupled
from the store, like kpi_validate/kpi_series.

Task 1 ships `build_memo_feed(company, schema_version, kpi_series,
generated_at)`: it queries `kpi_gate.is_trusted(company, schema_version)`
(same-skill import, slice 5's reliability gate — reused, NOT
reimplemented) and assembles a typed feed dict:

  - TRUSTED     -> {"_memo_feed_schema_version", "company",
                    "schema_version", "status": "TRUSTED",
                    "kpi_feeds": [...from kpi_series], "generated_at"}
  - NOT TRUSTED -> {..., "status": "WITHHELD",
                    "withheld_reason": <kpi_gate.gate_verdict(...)>,
                    "kpi_feeds": [], "generated_at"} — NO series values
                    bundled: a below-bar or never-evaluated company must
                    never leak extracted figures into the memo artifact.

`kpi_series` shape: a list of dicts, each `{"kpi_id", "points", "provenance"}`
(`points` a list of period/value entries; `provenance` per-point or
per-series metadata) — each entry is bundled into `kpi_feeds` verbatim.

`generated_at` is caller-supplied — this module never reads the wall
clock, mirroring `kpi_schema.confirm`'s / `kpi_gate.evaluate`'s
`evaluated_at` convention.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Resolve same-dir modules without a package (mirrors kpi_gate.py's /
# kpi_store.py's own same-dir import shim), so `import kpi_gate` works both
# under `uv run --script` and under importlib test loading.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import kpi_gate  # noqa: E402

# A feed-shape change here is a detectable migration, not a silent misread
# (mirrors kpi_store.STORE_SCHEMA_VERSION / kpi_schema.SCHEMA_ENVELOPE_VERSION
# / kpi_gate.GATE_ENVELOPE_VERSION).
MEMO_FEED_SCHEMA_VERSION = "1.0"


def build_memo_feed(company: str, schema_version, kpi_series: list, generated_at) -> dict:
    """Assemble the memo-feed contract for `(company, schema_version)`.

    Fail-closed on the reliability gate: only a TRUSTED verdict
    (`kpi_gate.is_trusted`) bundles `kpi_series` into `kpi_feeds`; any other
    verdict (WITHHELD / NOT_EVALUATED / no gate record at all, all of which
    `kpi_gate.is_trusted` reads as False) returns an empty `kpi_feeds` and
    surfaces the gate's own recorded verdict string as `withheld_reason` —
    never fabricated, never silently substituted with a generic message.
    """
    if kpi_gate.is_trusted(company, schema_version):
        return {
            "_memo_feed_schema_version": MEMO_FEED_SCHEMA_VERSION,
            "company": company,
            "schema_version": schema_version,
            "status": "TRUSTED",
            "kpi_feeds": list(kpi_series),
            "generated_at": generated_at,
        }

    return {
        "_memo_feed_schema_version": MEMO_FEED_SCHEMA_VERSION,
        "company": company,
        "schema_version": schema_version,
        "status": "WITHHELD",
        "withheld_reason": kpi_gate.gate_verdict(company, schema_version),
        "kpi_feeds": [],
        "generated_at": generated_at,
    }
