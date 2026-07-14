"""Tests for analysis-kpi/scripts/kpi_memo_feed.py — the memo-feed contract
assembly (operational-kpi capability, slice 8, final offline slice).

Task 1 ships the module scaffold + `build_memo_feed(company, schema_version,
kpi_series, generated_at)`: a PURE-ASSEMBLY function (mirrors kpi_validate.py
— no `_store_fs`, no store-dir resolution, no file locking/writing) that
reuses `kpi_gate.is_trusted` (slice 5's reliability gate, same-skill import)
for the trust verdict and takes the series data as a caller-supplied
argument rather than querying `kpi_store` directly.

The store dir is redirected to a tmp path via the `KPI_STORE_DIR` env
override (shared by kpi_store/review_queue/kpi_schema/kpi_gate/kpi_memo_feed
— same durable DATA dir kpi_gate.is_trusted reads its gate record from).

No `@req` tags: this dispatch's plan/spec trace work by named change-folder
Requirements (operational-kpi / "Memo-feed contract is an explicit
artifact"), NOT by registered loom-spec REQ-ids — so `@req` is omitted per
the implementer contract (mirrors test_kpi_gate.py's rationale).
"""
from __future__ import annotations

import importlib.util
import sys

from conftest import KPI_GATE_SCRIPT, KPI_MEMO_FEED_SCRIPT


def _load_kpi_memo_feed_module():
    """Load kpi_memo_feed.py as an importable module.

    Its same-dir import shim does a plain `import kpi_gate`, which must
    resolve to THE SAME `kpi_gate` module object this test uses to set up
    gate state (add_labels/evaluate) — so we first ensure the scripts dir
    is on sys.path and a real "kpi_gate" module is imported/cached under
    its real name before loading kpi_memo_feed, rather than loading kpi_gate
    under a test-only alias (mirrors test_kpi_gate.py's fixture, but keeps
    the two modules' view of KPI_STORE_DIR-backed state consistent).
    """
    scripts_dir = str(KPI_GATE_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_gate", None)
    import kpi_gate  # noqa: E402

    sys.modules.pop("kpi_memo_feed_test", None)
    spec = importlib.util.spec_from_file_location("kpi_memo_feed_test", KPI_MEMO_FEED_SCRIPT)
    assert spec is not None and spec.loader is not None
    kpi_memo_feed = importlib.util.module_from_spec(spec)
    sys.modules["kpi_memo_feed_test"] = kpi_memo_feed
    spec.loader.exec_module(kpi_memo_feed)
    return kpi_memo_feed, kpi_gate


def test_build_memo_feed_trusted_vs_withheld(tmp_path, monkeypatch):
    """build_memo_feed must fail-closed on the reliability gate:

    (a) a company with a recorded TRUSTED verdict (set up via kpi_gate.
        add_labels + evaluate, mirroring test_kpi_gate.py's TRUSTED case)
        -> status TRUSTED, kpi_feeds bundles the supplied kpi_series
        verbatim, no withheld_reason.
    (b) a never-evaluated company -> status WITHHELD, kpi_feeds == [] (NO
        series values leaked), and withheld_reason carries kpi_gate's own
        fail-closed verdict string.

    Why this matters: the memo-feed contract is the last gate before an
    LLM-authored narrative sees extracted figures — if a below-bar or
    never-evaluated company's numbers leaked through anyway, the whole
    point of the reliability gate (slice 5) would be silently bypassed at
    the one seam that actually reaches the memo.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    kpi_memo_feed, kpi_gate = _load_kpi_memo_feed_module()

    # --- (a) TRUSTED setup, mirroring test_kpi_gate.py's TRUSTED case ---
    labels = [
        {"kpi_id": f"kpi_{i}", "period": "2024-Q1", "value": 100 + i}
        for i in range(5)
    ]
    kpi_gate.add_labels("MEMOCO", labels)
    kpi_gate.evaluate(
        "MEMOCO", "v1", [dict(label) for label in labels],
        threshold=0.95, min_samples=5, evaluated_at="2026-07-14T00:00:00Z",
    )
    assert kpi_gate.is_trusted("MEMOCO", "v1") is True, (
        "test setup sanity: MEMOCO/v1 must be TRUSTED before exercising build_memo_feed"
    )

    kpi_series = [
        {
            "kpi_id": "kpi_0",
            "points": [{"period": "2024-Q1", "value": 100}],
            "provenance": {"source_accession": "0000320193-24-000123"},
        },
    ]
    trusted_feed = kpi_memo_feed.build_memo_feed(
        "MEMOCO", "v1", kpi_series, generated_at="2026-07-14T00:00:00Z",
    )
    assert trusted_feed["_memo_feed_schema_version"] == "1.0"
    assert trusted_feed["company"] == "MEMOCO"
    assert trusted_feed["schema_version"] == "v1"
    assert trusted_feed["status"] == "TRUSTED"
    assert trusted_feed["kpi_feeds"] == kpi_series
    assert trusted_feed["generated_at"] == "2026-07-14T00:00:00Z"
    assert "withheld_reason" not in trusted_feed

    # --- (b) never-evaluated company -> WITHHELD, no series values ---
    withheld_feed = kpi_memo_feed.build_memo_feed(
        "NEVERCO", "v1", kpi_series, generated_at="2026-07-14T00:00:00Z",
    )
    assert withheld_feed["_memo_feed_schema_version"] == "1.0"
    assert withheld_feed["company"] == "NEVERCO"
    assert withheld_feed["schema_version"] == "v1"
    assert withheld_feed["status"] == "WITHHELD"
    assert withheld_feed["kpi_feeds"] == [], (
        "a WITHHELD feed must carry NO series values"
    )
    assert withheld_feed["withheld_reason"] == "WITHHELD"
    assert withheld_feed["generated_at"] == "2026-07-14T00:00:00Z"
