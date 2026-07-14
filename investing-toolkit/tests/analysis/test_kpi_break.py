"""Tests for analysis-kpi/scripts/kpi_break.py — break-event detection
(operational-kpi capability, slice 6).

This slice's Task 1 ships `detect_breaks(prev_summary, curr_summary)`: a
PURE-COMPUTE comparison of two consecutive-period KPI summaries that
returns break-event candidates (resegmentation / relabel /
arithmetic-mismatch). No persistence, no `_store_fs` / `review_queue`
calls — those land in Tasks 2-3.

No `@req` tags: this dispatch's plan/spec trace work by named
change-folder Requirements (operational-kpi / "Definition-drift detection
triggers a break-event"), NOT by registered loom-spec REQ-ids — so `@req`
is omitted per the implementer contract (mirrors test_kpi_gate.py's
rationale).
"""
from __future__ import annotations

import importlib.util
import sys

from conftest import KPI_BREAK_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_break_module():
    """Load kpi_break.py as an importable module for unit tests of its
    pure-compute surface (detect_breaks). Mirrors
    test_kpi_gate.py::kpi_gate_module.
    """
    spec = importlib.util.spec_from_file_location("kpi_break_test", KPI_BREAK_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_break_test"] = module
    spec.loader.exec_module(module)
    return module


def test_detect_breaks_flags_each_trigger(kpi_break_module):
    """detect_breaks(prev_summary, curr_summary) must flag exactly the
    three drift triggers the spec defines, and must NOT raise or flag
    anything when there is nothing to flag.

    Why this matters: each trigger maps to a distinct real-world data
    quality event (segments were redrawn / a KPI was renamed / a
    reconciliation stopped summing) that later tasks turn into a
    human-adjudicated break-event — if detect_breaks silently missed one,
    or false-positived on identical/no-reconciliation input, the whole
    downstream adjudication lifecycle would be built on a broken signal.
    """
    detect_breaks = kpi_break_module.detect_breaks

    # (a) segment set changed (count + membership) -> resegmentation.
    prev_resegmentation = {
        "segments": ["iPhone", "Services"],
        "kpi_labels": {},
    }
    curr_resegmentation = {
        "segments": ["iPhone", "Services", "Wearables"],
        "kpi_labels": {},
    }
    candidates = detect_breaks(prev_resegmentation, curr_resegmentation)
    triggers = [c["trigger"] for c in candidates]
    assert "resegmentation" in triggers
    assert triggers.count("resegmentation") == 1

    # (b) a kpi_id present in both, with a changed label -> relabel.
    prev_relabel = {
        "segments": ["iPhone"],
        "kpi_labels": {"iphone_units": "iPhone Units Sold"},
    }
    curr_relabel = {
        "segments": ["iPhone"],
        "kpi_labels": {"iphone_units": "iPhone Unit Sales"},
    }
    candidates = detect_breaks(prev_relabel, curr_relabel)
    triggers = [c["trigger"] for c in candidates]
    assert triggers == ["relabel"]
    relabel_detail = candidates[0]["detail"]
    assert relabel_detail["kpi_id"] == "iphone_units"
    assert relabel_detail["prev_label"] == "iPhone Units Sold"
    assert relabel_detail["curr_label"] == "iPhone Unit Sales"

    # (c) reconciliation parts don't sum to total (beyond 1% rel tol) ->
    # arithmetic-mismatch.
    prev_arith = {"segments": ["iPhone"], "kpi_labels": {}}
    curr_arith = {
        "segments": ["iPhone"],
        "kpi_labels": {},
        "reconciliation": {
            "revenue": {"parts": [40, 40], "total": 100},
        },
    }
    candidates = detect_breaks(prev_arith, curr_arith)
    triggers = [c["trigger"] for c in candidates]
    assert triggers == ["arithmetic-mismatch"]
    arith_detail = candidates[0]["detail"]
    assert arith_detail["kpi_id"] == "revenue"

    # (d) identical summaries -> no candidates at all.
    identical = {
        "segments": ["iPhone", "Services"],
        "kpi_labels": {"iphone_units": "iPhone Units Sold"},
        "reconciliation": {"revenue": {"parts": [50, 50], "total": 100}},
    }
    assert detect_breaks(identical, identical) == []

    # (e) curr summary has NO reconciliation key at all -> no
    # arithmetic-mismatch raised (N/A, not an error).
    prev_no_recon = {"segments": ["iPhone"], "kpi_labels": {}}
    curr_no_recon = {"segments": ["iPhone"], "kpi_labels": {}}
    assert detect_breaks(prev_no_recon, curr_no_recon) == []


def test_flag_break_persists_and_enqueues(kpi_break_module, tmp_path, monkeypatch):
    """flag_break(company, schema_version, candidate, review_item_id) must
    durably persist a FLAGGED break-event record AND enqueue a
    subject_type="break-event" review-item referencing it — the two
    downstream lifecycle steps (Task 3's confirm/dismiss, and a human's
    review-queue-driven adjudication) both depend on this pairing existing
    atomically-enough that a flagged break is always discoverable both by
    direct lookup (get_break/list_breaks) AND by the review queue a human
    actually works from.

    Why this matters: if flag_break wrote the break record but skipped the
    enqueue (or vice versa), a break-event would exist in one system but
    not the other — invisible to whichever path a human or Task 3's
    confirm/dismiss relies on.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    flag_break = kpi_break_module.flag_break
    get_break = kpi_break_module.get_break
    list_breaks = kpi_break_module.list_breaks
    review_queue = kpi_break_module.review_queue

    candidate = {
        "trigger": "resegmentation",
        "detail": {"prev_segments": ["iPhone"], "curr_segments": ["iPhone", "Wearables"]},
    }
    record = flag_break("AAPL", "v1", candidate, review_item_id="ri-break-1")

    assert record["status"] == "FLAGGED"
    assert record["company"] == "AAPL"
    assert record["schema_version"] == "v1"
    assert record["trigger"] == "resegmentation"
    assert record["detail"] == candidate["detail"]
    assert record["mapping"] is None
    break_id = record["break_id"]

    fetched = get_break("AAPL", break_id)
    assert fetched == record

    all_breaks = list_breaks("AAPL")
    assert any(b["break_id"] == break_id for b in all_breaks)

    open_items = review_queue.list_open()
    matching = [item for item in open_items if item.get("subject_id") == break_id]
    assert len(matching) == 1, "exactly one OPEN review-item must reference this break_id"
    assert matching[0]["subject_type"] == "break-event"
    assert matching[0]["review_item_id"] == "ri-break-1"

    # Read-only queries: unknown break_id / company must not raise.
    assert get_break("AAPL", "nonexistent") is None
    assert list_breaks("NOCOMPANY") == []

    # A SECOND flag for the same company gets a DISTINCT break_id (the count-
    # under-lock scheme keeps ids unique); both records persist.
    record2 = flag_break("AAPL", "v1", candidate, review_item_id="ri-break-2")
    assert record2["break_id"] != break_id, "each flag must get a distinct break_id"
    assert len(list_breaks("AAPL")) == 2
