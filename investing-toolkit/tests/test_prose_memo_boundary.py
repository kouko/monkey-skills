"""Memo-boundary lock: prose-sourced KPI points must NOT surface in the
quarterly memo feed (Slice B walking skeleton, Task 9).

A future tier-① prose-KPI producer will commit points into the append-only
`kpi_store` (see analysis-kpi/scripts/kpi_store.py). This test LOCKS the
existing decoupling that keeps those prose points out of the quarterly memo
feed until a (future) Slice B curation layer exists:

  kpi_memo_feed.build_quarterly_memo_feed(company, series_payload,
  generated_at) reads ONLY its caller-supplied `series_payload` (the XBRL
  `quarterly-series` output) — it does NOT import or query `kpi_store`
  (kpi_memo_feed.py module docstring / "does NOT query kpi_store directly —
  decoupled"). So a prose point living in the store can never leak into the
  memo feed, whose content is exactly the series payload it was handed.

This is a characterization / regression-locking test — there is NO
production change. It pins the invariant so a future edit that made the
feed read the store (leaking un-curated prose points into the memo artifact)
would fail here.

The test carries a positive control (a prose point placed INSIDE the series
payload IS surfaced — proving the assertion has teeth) alongside the
negative lock (a prose point placed only in the store is ABSENT from a feed
built from an XBRL payload that omits it).

No `@req` tags: this dispatch traces work by named plan/spec Requirements
(the Slice B memo-boundary invariant), NOT registered loom-spec REQ-ids —
so `@req` is omitted per the implementer contract (mirrors
test_kpi_memo_feed.py's rationale).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

# tests/test_prose_memo_boundary.py -> parents[1] = investing-toolkit
_SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "skills" / "analysis-kpi" / "scripts"


def _load_modules():
    """Load kpi_store + kpi_memo_feed from the analysis-kpi scripts dir.

    Both do a plain same-dir `import` for their siblings (_store_fs /
    kpi_gate / kpi_xbrl), so the scripts dir must be on sys.path and each
    sibling importable under its real name before exec. kpi_store is loaded
    under its real name so its `import _store_fs` resolves against the same
    module the store writes through.
    """
    scripts_dir = str(_SCRIPTS_DIR)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    sys.modules.pop("kpi_store", None)
    import kpi_store  # noqa: E402

    sys.modules.pop("kpi_memo_feed_boundary_test", None)
    spec = importlib.util.spec_from_file_location(
        "kpi_memo_feed_boundary_test", _SCRIPTS_DIR / "kpi_memo_feed.py"
    )
    assert spec is not None and spec.loader is not None
    kpi_memo_feed = importlib.util.module_from_spec(spec)
    sys.modules["kpi_memo_feed_boundary_test"] = kpi_memo_feed
    spec.loader.exec_module(kpi_memo_feed)
    return kpi_store, kpi_memo_feed


# A distinctive marker so its presence/absence in the feed is unambiguous.
_PROSE_KPI_ID = "prose:iphone_units_boundary_marker"


def _prose_point() -> dict:
    """A prose-sourced KPI point in kpi_store's point shape — what a future
    tier-① prose producer would commit. Carries complete provenance + an
    accession-derived `as_of` so kpi_store.append accepts it, plus a
    `source_kind="prose"` marker distinguishing it from XBRL points."""
    return {
        "company": "AAPL",
        "kpi_id": _PROSE_KPI_ID,
        "period": "2024-Q1",
        "value": 42.0,
        "source_kind": "prose",
        "source_accession": "0000320193-24-000999",
        "source_table_id": "prose-narrative-p1",
        "source_cell_ref": "para-3-sentence-2",
        "as_of": "2024-11-01",
        "as_of_is_wallclock": False,
    }


def _xbrl_series_payload_without_prose() -> dict:
    """A minimal well-formed `quarterly-series` payload containing ONE
    reported XBRL point and NO prose point. Reported points need only a
    non-blank source_accession + kpi_id; coverage_flags=[] skips the DQC
    schema loop — keeping the fixture focused on the boundary invariant."""
    return {
        "series": [
            {
                "signature": {"concept": "us-gaap:Revenues", "dimensions": {}},
                "points": [
                    {
                        "kpi_id": "us-gaap:Revenues",
                        "period": "2024-Q1",
                        "value": 1000.0,
                        "source_accession": "0000320193-24-000123",
                        "source_table_id": "xbrl:dimensional",
                        "source_cell_ref": "us-gaap:Revenues",
                        "source_kind": "xbrl-dimensional",
                    }
                ],
                "derived_points": [],
                "gaps": [],
            }
        ],
        "coverage_flags": [],
    }


def test_prose_point_absent_from_memo_feed(tmp_path, monkeypatch):
    """A prose point committed to kpi_store does NOT surface in a quarterly
    memo feed built from an XBRL series payload that omits it — because
    build_quarterly_memo_feed reads only its `series_payload` argument, never
    the store. Locks the store/feed decoupling against future regression."""
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    kpi_store, kpi_memo_feed = _load_modules()

    prose = _prose_point()

    # Prove the store genuinely holds the prose point (the leak source a
    # regression would draw from).
    kpi_store.append(prose)
    assert (
        kpi_store.query_latest(prose["company"], prose["kpi_id"], prose["period"])
        is not None
    ), "prose point must be present in the store for the boundary test to be meaningful"

    # Positive control: the feed surfaces whatever is in its series_payload
    # argument — a prose point placed INSIDE the payload IS echoed. This
    # proves the absence assertion below has teeth (the feed is not silently
    # empty / stripping by source_kind).
    payload_with_prose = _xbrl_series_payload_without_prose()
    payload_with_prose["series"][0]["points"].append(dict(prose))
    control_feed = kpi_memo_feed.build_quarterly_memo_feed(
        prose["company"], payload_with_prose, generated_at="2026-07-19"
    )
    assert _PROSE_KPI_ID in json.dumps(control_feed), (
        "positive control: a prose point placed inside the series payload must "
        "surface in the feed — otherwise the absence assertion is a tautology"
    )

    # The lock: with the prose point living ONLY in the store (not in the
    # XBRL payload), the feed built from that payload must NOT contain it.
    payload_without_prose = _xbrl_series_payload_without_prose()
    feed = kpi_memo_feed.build_quarterly_memo_feed(
        prose["company"], payload_without_prose, generated_at="2026-07-19"
    )

    # 1. No feed point is prose-sourced.
    feed_points = [
        point
        for entry in feed["series"]
        for point in entry.get("points", []) + entry.get("derived_points", [])
    ]
    assert all(p.get("source_kind") != "prose" for p in feed_points), (
        "a prose-sourced point leaked into the quarterly memo feed — the feed "
        "must read only its series_payload, never kpi_store"
    )

    # 2. The prose marker appears nowhere in the serialized feed.
    assert _PROSE_KPI_ID not in json.dumps(feed), (
        "the store-resident prose kpi_id leaked into the memo feed output"
    )

    # 3. The feed's series is the input payload's series, verbatim — pinning
    #    "the feed's input is the series payload, not the store".
    assert feed["series"] == payload_without_prose["series"]
