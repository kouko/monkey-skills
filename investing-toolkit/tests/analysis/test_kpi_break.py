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
import json
import os
import subprocess
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


def test_confirm_and_dismiss_break_via_human_seam(kpi_break_module, tmp_path, monkeypatch):
    """confirm_break/dismiss_break must route through review_queue.adjudicate
    (the REUSED human-confirm auth boundary) BEFORE flipping the break
    record, so a rejected identity leaves the break FLAGGED and its
    review-item OPEN. A confirm additionally requires a non-empty `mapping`,
    rejected loud before any adjudicate/write.

    Why this matters: if the adjudicate call ran AFTER the record flip (or
    were skipped), an empty/pipeline identity could silently confirm a
    break-event mapping — exactly the self-confirm hole review_queue's auth
    boundary exists to close for kpi_schema.confirm; this test proves
    kpi_break wires the same seam, not a parallel weaker check.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    flag_break = kpi_break_module.flag_break
    confirm_break = kpi_break_module.confirm_break
    dismiss_break = kpi_break_module.dismiss_break
    get_break = kpi_break_module.get_break
    review_queue = kpi_break_module.review_queue

    candidate = {
        "trigger": "resegmentation",
        "detail": {"prev_segments": ["iPhone"], "curr_segments": ["iPhone", "Wearables"]},
    }
    mapping = {"iPhone": "iPhone", "Wearables": "Wearables (new)"}

    # (a) happy path: flag -> confirm(mapping, by="alice") -> CONFIRMED,
    # mapping stored, review-item resolved (no longer OPEN).
    record = flag_break("AAPL", "v1", candidate, review_item_id="ri-confirm-1")
    break_id = record["break_id"]
    confirmed = confirm_break("AAPL", break_id, adjudicated_by="alice", mapping=mapping)
    assert confirmed["status"] == "CONFIRMED"
    assert confirmed["mapping"] == mapping
    assert get_break("AAPL", break_id)["status"] == "CONFIRMED"
    assert not any(
        item.get("subject_id") == break_id for item in review_queue.list_open()
    ), "the break's review-item must no longer be OPEN once confirmed"

    # (b) confirm with an empty mapping -> raises loud, break stays FLAGGED,
    # nothing adjudicated.
    record2 = flag_break("AAPL", "v1", candidate, review_item_id="ri-confirm-2")
    break_id2 = record2["break_id"]
    with pytest.raises(ValueError):
        confirm_break("AAPL", break_id2, adjudicated_by="alice", mapping={})
    assert get_break("AAPL", break_id2)["status"] == "FLAGGED"
    assert any(
        item.get("subject_id") == break_id2 and item.get("status") == "OPEN"
        for item in review_queue.list_open()
    ), "an empty-mapping rejection must not touch the review-item either"

    # (c) confirm with adjudicated_by="" -> rejected BY review_queue.adjudicate
    # (the reused seam) -> break stays FLAGGED, review-item still OPEN.
    record3 = flag_break("AAPL", "v1", candidate, review_item_id="ri-confirm-3")
    break_id3 = record3["break_id"]
    with pytest.raises(ValueError):
        confirm_break("AAPL", break_id3, adjudicated_by="", mapping=mapping)
    assert get_break("AAPL", break_id3)["status"] == "FLAGGED"
    assert any(
        item.get("subject_id") == break_id3 and item.get("status") == "OPEN"
        for item in review_queue.list_open()
    ), "a rejected identity must leave the review-item OPEN"

    # (d) a second confirm/dismiss on an already-resolved break -> illegal
    # transition, raises loud.
    with pytest.raises(ValueError):
        confirm_break("AAPL", break_id, adjudicated_by="bob", mapping=mapping)
    with pytest.raises(ValueError):
        dismiss_break("AAPL", break_id, adjudicated_by="bob")

    # (e) a separate FLAGGED break, dismissed -> DISMISSED.
    record4 = flag_break("AAPL", "v1", candidate, review_item_id="ri-confirm-4")
    break_id4 = record4["break_id"]
    dismissed = dismiss_break("AAPL", break_id4, adjudicated_by="carol")
    assert dismissed["status"] == "DISMISSED"
    assert get_break("AAPL", break_id4)["status"] == "DISMISSED"

    # Unknown break_id -> raises loud for both confirm and dismiss.
    with pytest.raises(ValueError):
        confirm_break("AAPL", "nonexistent", adjudicated_by="alice", mapping=mapping)
    with pytest.raises(ValueError):
        dismiss_break("AAPL", "nonexistent", adjudicated_by="alice")


def test_cli_detect_flag_confirm_roundtrip(tmp_path):
    """Task 4: the kpi_break.py CLI's `detect`/`flag`/`confirm`/`list`
    subcommands round-trip a break-event through real subprocess
    invocations (not the library surface directly) — the CLI is a thin
    argparse wrapper over detect_breaks/flag_break/confirm_break/
    list_breaks, not a reimplementation, mirroring
    test_kpi_schema.py::test_cli_propose_confirm_status_roundtrip.

    flag (stdin candidate JSON) -> list shows it FLAGGED -> confirm (stdin
    mapping JSON) -> list shows CONFIRMED. Also: malformed JSON -> exit 2,
    and --help lists all five subcommands.
    """
    env = {**os.environ, "KPI_STORE_DIR": str(tmp_path)}

    def run_list(company="AAPL"):
        result = subprocess.run(
            ["uv", "run", "--script", str(KPI_BREAK_SCRIPT), "list", "--company", company],
            capture_output=True, text=True, timeout=60, env=env,
        )
        assert result.returncode == 0, (
            f"list subcommand failed: stdout={result.stdout!r} stderr={result.stderr!r}"
        )
        return json.loads(result.stdout)

    candidate = {
        "trigger": "resegmentation",
        "detail": {"prev_segments": ["iPhone"], "curr_segments": ["iPhone", "Wearables"]},
    }
    flag_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_BREAK_SCRIPT), "flag",
            "--company", "AAPL", "--schema-version", "v1",
            "--review-item-id", "ri-cli-1",
        ],
        input=json.dumps(candidate),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert flag_result.returncode == 0, (
        f"flag subcommand failed: stdout={flag_result.stdout!r} stderr={flag_result.stderr!r}"
    )
    flagged_record = json.loads(flag_result.stdout)
    assert flagged_record["status"] == "FLAGGED"
    break_id = flagged_record["break_id"]

    flagged_list = run_list()
    assert len(flagged_list) == 1
    assert flagged_list[0]["break_id"] == break_id
    assert flagged_list[0]["status"] == "FLAGGED"

    mapping = {"iPhone": "iPhone", "Wearables": "Wearables (new)"}
    confirm_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_BREAK_SCRIPT), "confirm",
            "--company", "AAPL", "--break-id", break_id, "--by", "alice",
        ],
        input=json.dumps(mapping),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert confirm_result.returncode == 0, (
        f"confirm subcommand failed: stdout={confirm_result.stdout!r} "
        f"stderr={confirm_result.stderr!r}"
    )
    confirmed_record = json.loads(confirm_result.stdout)
    assert confirmed_record["status"] == "CONFIRMED"
    assert confirmed_record["mapping"] == mapping

    confirmed_list = run_list()
    assert confirmed_list[0]["status"] == "CONFIRMED"
    assert confirmed_list[0]["mapping"] == mapping

    # Fail-loud: malformed JSON on flag -> exit 2, nothing written, no raw
    # traceback.
    fail_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_BREAK_SCRIPT), "flag",
            "--company", "MSFT", "--schema-version", "v1",
            "--review-item-id", "ri-cli-2",
        ],
        input="{not valid json",
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert fail_result.returncode == 2, fail_result.stderr
    assert "Traceback" not in fail_result.stderr, (
        "malformed JSON must fail cleanly, not with a raw traceback"
    )
    assert run_list("MSFT") == [], "a rejected flag must write nothing for MSFT"

    # --help lists every subcommand.
    help_result = subprocess.run(
        ["uv", "run", "--script", str(KPI_BREAK_SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert help_result.returncode == 0
    for subcommand in ("detect", "flag", "confirm", "dismiss", "list"):
        assert subcommand in help_result.stdout, (
            f"--help must list the {subcommand!r} subcommand"
        )
