"""Tests for analysis-kpi/scripts/kpi_schema.py — the KPI schema
propose-then-confirm lifecycle (operational-kpi capability, slice 3).

This slice's Task 2 ships the module scaffold + `propose(company, kpi_defs,
review_item_id)`: on a company's first propose, writes a per-company schema
file (version 1, status PROPOSED, kpi_defs stored verbatim) AND enqueues a
`subject_type="kpi-schema"` review-item via `review_queue.enqueue` so a human
can later confirm it (Task 3) through the existing review-queue seam. The
store dir is redirected to a tmp path via the `KPI_STORE_DIR` env override
(shared by kpi_store/review_queue/kpi_schema — same durable DATA dir).

The library function is exercised by loading `kpi_schema.py` via importlib
(same convention as test_review_queue.py's `review_queue_module` fixture);
`review_queue.list_open` is called directly (not re-implemented) to confirm
the enqueue side-effect through the same tmp store.

No `@req` tags: this dispatch's plan/spec trace work by named change-folder
Requirements (operational-kpi / "KPI schema propose-then-confirm lifecycle"),
NOT by registered loom-spec REQ-ids — so `@req` is omitted per the
implementer contract (mirrors test_review_queue.py's rationale).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

from conftest import KPI_SCHEMA_SCRIPT, REVIEW_QUEUE_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_schema_module():
    """Load kpi_schema.py as an importable module for unit tests of its
    library surface (propose/...) before confirm/amend/CLI are added
    (Tasks 3-6).
    """
    spec = importlib.util.spec_from_file_location("kpi_schema_test", KPI_SCHEMA_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_schema_test"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def review_queue_module():
    """Load review_queue.py the same way, so the test can confirm the
    propose-side-effect enqueue through the real `list_open` — not a
    reimplementation of the queue read.
    """
    spec = importlib.util.spec_from_file_location(
        "review_queue_for_kpi_schema_test", REVIEW_QUEUE_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["review_queue_for_kpi_schema_test"] = module
    spec.loader.exec_module(module)
    return module


def test_propose_stores_proposed_schema_and_enqueues(
    kpi_schema_module, review_queue_module, tmp_path, monkeypatch
):
    """propose(company, kpi_defs, review_item_id) must:
      (a) durably store a per-company schema record — version 1,
          status PROPOSED, kpi_defs stored verbatim (the LLM produced them
          upstream — this module must not reshape or drop any field);
      (b) enqueue a subject_type="kpi-schema" review-item, OPEN, so a human
          can later confirm it through the review queue's existing
          human-confirm seam (Task 3) — reused, not reimplemented.

    Why this matters: without (a) a proposed schema has nowhere durable to
    live for confirm/amend to transition later; without (b) a proposed
    schema would silently bypass the human-in-the-loop gate the whole
    propose-then-confirm lifecycle exists to enforce.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    kpi_defs = [
        {
            "kpi_id": "iphone_units",
            "label": "iPhone units sold",
            "unit": "units",
            "locate_hint": "Segment Information, Products and Services table",
        },
        {
            "kpi_id": "services_revenue",
            "label": "Services revenue",
            "unit": "USD",
            "locate_hint": "Segment Information, Products and Services table",
        },
    ]

    record = kpi_schema_module.propose(
        "AAPL", kpi_defs, review_item_id="rev-schema-0001"
    )

    # (a) schema file exists for the company, version 1, PROPOSED, kpi_defs
    # stored verbatim.
    assert record["company"] == "AAPL"
    assert record["version"] == 1
    assert record["status"] == "PROPOSED"
    assert record["kpi_defs"] == kpi_defs
    assert record["confirmed_by"] is None
    assert record["confirmed_at"] is None

    schema_files = [
        p for p in tmp_path.rglob("*.json") if p.name != "review-queue.json"
    ]
    assert len(schema_files) == 1, (
        f"expected exactly one schema file, found {schema_files}"
    )
    envelope = json.loads(schema_files[0].read_text(encoding="utf-8"))
    assert isinstance(envelope.get("versions"), list)
    assert len(envelope["versions"]) == 1
    stored = envelope["versions"][0]
    assert stored["version"] == 1
    assert stored["status"] == "PROPOSED"
    assert stored["kpi_defs"] == kpi_defs

    # (b) a kpi-schema review-item is OPEN in the review queue, referencing
    # the new schema, carrying the caller-supplied review_item_id.
    open_items = review_queue_module.list_open()
    assert len(open_items) == 1, f"expected exactly one OPEN item, got {open_items}"
    item = open_items[0]
    assert item["review_item_id"] == "rev-schema-0001"
    assert item["subject_type"] == "kpi-schema"
    assert item["subject_id"] == stored["schema_id"]
    assert item["status"] == "OPEN"


def test_confirm_transitions_to_confirmed_via_human_seam(
    kpi_schema_module, review_queue_module, tmp_path, monkeypatch
):
    """confirm(company, adjudicated_by, adjudicated_at) must:
      (a) locate the latest PROPOSED schema version and its OPEN review-item,
          adjudicate it through `review_queue.adjudicate` (the REUSED
          human-confirm seam — an empty/whitespace `adjudicated_by` must be
          rejected BY that seam, not reimplemented here) BEFORE flipping the
          schema, so a rejected identity leaves the schema PROPOSED and the
          review-item still OPEN;
      (b) on a valid identity, transition the schema version to CONFIRMED
          with confirmed_by/confirmed_at set, and resolve the review-item
          (no longer OPEN);
      (c) reject loud a second confirm once the head is already CONFIRMED
          (confirm-once), and a confirm for a company with no schema at all.

    Why this matters: propose-then-confirm is a human-in-the-loop gate — if
    an empty identity could slip through, or a second confirm could silently
    no-op/duplicate, the whole point of the seam (no pipeline self-confirm,
    no double-confirmation) would be defeated.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    kpi_defs = [
        {
            "kpi_id": "iphone_units",
            "label": "iPhone units sold",
            "unit": "units",
            "locate_hint": "Segment Information, Products and Services table",
        },
    ]
    record = kpi_schema_module.propose(
        "AAPL", kpi_defs, review_item_id="rev-schema-0002"
    )
    schema_files = [
        p for p in tmp_path.rglob("*.json") if p.name != "review-queue.json"
    ]
    assert len(schema_files) == 1
    schema_file = schema_files[0]

    # Empty / whitespace adjudicated_by is rejected BY review_queue.adjudicate
    # (the reused seam) — the schema must stay PROPOSED, unchanged.
    with pytest.raises(ValueError):
        kpi_schema_module.confirm("AAPL", adjudicated_by="", adjudicated_at="2024-01-01")
    with pytest.raises(ValueError):
        kpi_schema_module.confirm("AAPL", adjudicated_by="   ", adjudicated_at="2024-01-01")

    envelope = json.loads(schema_file.read_text(encoding="utf-8"))
    stored = envelope["versions"][0]
    assert stored["status"] == "PROPOSED"
    assert stored["confirmed_by"] is None
    assert stored["confirmed_at"] is None
    assert len(review_queue_module.list_open()) == 1, (
        "a rejected confirm attempt must leave the review-item OPEN"
    )

    confirmed = kpi_schema_module.confirm(
        "AAPL", adjudicated_by="alice", adjudicated_at="2024-01-01"
    )
    assert confirmed["status"] == "CONFIRMED"
    assert confirmed["confirmed_by"] == "alice"
    assert confirmed["confirmed_at"] == "2024-01-01"

    envelope = json.loads(schema_file.read_text(encoding="utf-8"))
    stored = envelope["versions"][0]
    assert stored["status"] == "CONFIRMED"
    assert stored["confirmed_by"] == "alice"
    assert stored["confirmed_at"] == "2024-01-01"
    assert review_queue_module.list_open() == [], (
        "the schema's review-item must no longer be OPEN once confirmed"
    )

    # Confirm-once: already-CONFIRMED head raises loud, nothing changes.
    with pytest.raises(ValueError):
        kpi_schema_module.confirm("AAPL", adjudicated_by="bob", adjudicated_at="2024-01-02")

    # No schema at all for this company -> raises loud.
    with pytest.raises(ValueError):
        kpi_schema_module.confirm("MSFT", adjudicated_by="alice", adjudicated_at="2024-01-01")


def test_confirmed_schema_scopes_kpi_ids(
    kpi_schema_module, review_queue_module, tmp_path, monkeypatch
):
    """confirmed_kpi_ids(company) / is_kpi_in_confirmed_schema(company, kpi_id)
    must scope extraction to ONLY the company's CONFIRMED schema version:
      (a) before confirm, a PROPOSED-only schema yields no confirmed kpi_ids
          (extraction stays blocked until a human confirms it);
      (b) after confirm, confirmed_kpi_ids lists exactly the confirmed
          version's kpi_ids, and is_kpi_in_confirmed_schema is True for a
          listed id, False for an unlisted one.

    Why this matters: this is the schema-scoped extraction boundary — a
    later extraction step must never read from a PROPOSED (unreviewed)
    schema, and must never accept a KPI id the human never confirmed.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    kpi_defs = [
        {"kpi_id": "a", "label": "A", "unit": "units", "locate_hint": "hint a"},
        {"kpi_id": "b", "label": "B", "unit": "units", "locate_hint": "hint b"},
    ]
    kpi_schema_module.propose("AAPL", kpi_defs, review_item_id="rev-schema-0003")

    # (a) PROPOSED-only -> blocked, no confirmed kpi_ids.
    assert kpi_schema_module.confirmed_kpi_ids("AAPL") == []
    assert kpi_schema_module.is_kpi_in_confirmed_schema("AAPL", "a") is False

    kpi_schema_module.confirm("AAPL", adjudicated_by="alice", adjudicated_at="2024-01-01")

    # (b) CONFIRMED -> scoped to exactly this version's kpi_ids.
    assert kpi_schema_module.confirmed_kpi_ids("AAPL") == ["a", "b"]
    assert kpi_schema_module.is_kpi_in_confirmed_schema("AAPL", "a") is True
    assert kpi_schema_module.is_kpi_in_confirmed_schema("AAPL", "zzz") is False


def test_amend_new_version_and_superseded_blocks(
    kpi_schema_module, review_queue_module, tmp_path, monkeypatch
):
    """amend(company, new_kpi_defs, review_item_id) must:
      (a) propose a NEW version (version 2, PROPOSED) through the SAME
          store+enqueue path as propose — a fresh OPEN review-item appears
          for it, and confirmed_kpi_ids is still scoped to the OLD (v1)
          CONFIRMED version until the new one is confirmed;
      (b) on confirming the new version, the prior CONFIRMED version (v1)
          transitions to SUPERSEDED (only ONE CONFIRMED version at a time)
          and confirmed_kpi_ids now reflects the new (v2) kpi_defs;
      (c) a company whose only non-PROPOSED version is SUPERSEDED (no
          CONFIRMED successor) yields no confirmed kpi_ids — consistent
          with Task 4's PROPOSED-blocks behavior (the orphaned-supersede
          scenario re-proposes rather than silently extracting stale ids).

    Why this matters: amend is how a company's schema evolves without
    losing history; the supersede transition is what keeps "only one
    CONFIRMED version" true so confirmed_kpi_ids never has to choose
    between two simultaneously-CONFIRMED versions.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    v1_defs = [{"kpi_id": "a", "label": "A", "unit": "units", "locate_hint": "hint a"}]
    kpi_schema_module.propose("AAPL", v1_defs, review_item_id="rev-schema-0004")
    kpi_schema_module.confirm("AAPL", adjudicated_by="alice", adjudicated_at="2024-01-01")
    assert kpi_schema_module.confirmed_kpi_ids("AAPL") == ["a"]

    v2_defs = [
        {"kpi_id": "a", "label": "A", "unit": "units", "locate_hint": "hint a"},
        {"kpi_id": "c", "label": "C", "unit": "units", "locate_hint": "hint c"},
    ]
    amended = kpi_schema_module.amend("AAPL", v2_defs, review_item_id="rev-schema-0005")
    assert amended["version"] == 2
    assert amended["status"] == "PROPOSED"
    assert amended["kpi_defs"] == v2_defs

    # (a) new OPEN review-item for v2; v1 still the confirmed one.
    open_items = review_queue_module.list_open()
    assert len(open_items) == 1
    assert open_items[0]["review_item_id"] == "rev-schema-0005"
    assert kpi_schema_module.confirmed_kpi_ids("AAPL") == ["a"]

    confirmed_v2 = kpi_schema_module.confirm(
        "AAPL", adjudicated_by="bob", adjudicated_at="2024-02-01"
    )

    # (b) v2 CONFIRMED, v1 SUPERSEDED, confirmed_kpi_ids reflects v2.
    assert confirmed_v2["version"] == 2
    assert confirmed_v2["status"] == "CONFIRMED"
    assert kpi_schema_module.confirmed_kpi_ids("AAPL") == ["a", "c"]

    schema_files = [
        p for p in tmp_path.rglob("*.json") if p.name != "review-queue.json"
    ]
    assert len(schema_files) == 1
    envelope = json.loads(schema_files[0].read_text(encoding="utf-8"))
    versions_by_number = {v["version"]: v for v in envelope["versions"]}
    assert versions_by_number[1]["status"] == "SUPERSEDED"
    assert versions_by_number[2]["status"] == "CONFIRMED"

    # (c) a company whose ONLY version is SUPERSEDED (no CONFIRMED
    # successor — e.g. hand-constructed here to exercise the orphaned-
    # supersede scenario directly) yields no confirmed kpi_ids: blocked,
    # signalling re-propose rather than silently extracting stale ids.
    orphan_path = kpi_schema_module._schema_path("ORCL")
    orphan_path.write_text(
        json.dumps({
            "_kpi_schema_meta": {"version": "1.0"},
            "versions": [{
                "schema_id": "ORCL:v1",
                "company": "ORCL",
                "version": 1,
                "status": "SUPERSEDED",
                "kpi_defs": [{"kpi_id": "stale", "label": "Stale", "unit": "units", "locate_hint": "n/a"}],
                "confirmed_by": "alice",
                "confirmed_at": "2023-01-01",
            }],
        }),
        encoding="utf-8",
    )
    assert kpi_schema_module.confirmed_kpi_ids("ORCL") == []


def test_rejected_amend_confirm_leaves_prior_confirmed_intact(
    kpi_schema_module, review_queue_module, tmp_path, monkeypatch
):
    """The load-bearing supersede-ordering property: when an amended version's
    confirm is REJECTED (bad identity), the in-memory supersede of the prior
    CONFIRMED version must be DISCARDED — v1 stays CONFIRMED, v2 stays
    PROPOSED, nothing persisted. (The single _atomic_write runs only after
    adjudicate succeeds; a rejection raises before it.)
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    v1_defs = [{"kpi_id": "a", "label": "A", "unit": "u", "locate_hint": "h"}]
    kpi_schema_module.propose("NVDA", v1_defs, review_item_id="rev-nv-1")
    kpi_schema_module.confirm("NVDA", adjudicated_by="alice", adjudicated_at="2024-01-01")
    assert kpi_schema_module.confirmed_kpi_ids("NVDA") == ["a"]

    v2_defs = v1_defs + [{"kpi_id": "b", "label": "B", "unit": "u", "locate_hint": "h"}]
    kpi_schema_module.amend("NVDA", v2_defs, review_item_id="rev-nv-2")

    # A rejected identity (whitespace) must change nothing on disk.
    with pytest.raises(ValueError):
        kpi_schema_module.confirm("NVDA", adjudicated_by="   ")

    # v1 still CONFIRMED (NOT superseded), v2 still PROPOSED, confirmed set unchanged.
    schema_files = [p for p in tmp_path.rglob("*.json") if p.name != "review-queue.json"]
    envelope = json.loads(schema_files[0].read_text(encoding="utf-8"))
    by_num = {v["version"]: v for v in envelope["versions"]}
    assert by_num[1]["status"] == "CONFIRMED", "rejected confirm must not supersede v1"
    assert by_num[2]["status"] == "PROPOSED", "rejected confirm must not confirm v2"
    assert kpi_schema_module.confirmed_kpi_ids("NVDA") == ["a"]
    # v2's review-item stays OPEN (adjudication was rejected).
    assert any(i["review_item_id"] == "rev-nv-2" for i in review_queue_module.list_open())


def test_cli_propose_confirm_status_roundtrip(tmp_path):
    """Task 6: the kpi_schema.py CLI's `propose`, `confirm`, and `status`
    subcommands round-trip a schema through real subprocess invocations (not
    the library surface directly) — the CLI is a thin wrapper over
    propose/confirm/confirmed_kpi_ids, not a reimplementation, mirroring
    test_review_queue.py::test_cli_enqueue_list_adjudicate_roundtrip.

    propose (stdin kpi_defs JSON list) -> status shows PROPOSED with no
    confirmed_kpi_ids -> confirm -> status shows CONFIRMED with
    confirmed_kpi_ids populated.

    ALSO a fail-loud CLI assertion: `propose` given a non-list JSON body
    (a JSON object instead of an array) must exit 2, write nothing, and
    never leak a raw traceback to stderr — mirrors
    test_review_queue.py::test_cli_enqueue_fail_loud_exit_codes.
    """
    env = {**os.environ, "KPI_STORE_DIR": str(tmp_path)}
    kpi_defs = [
        {"kpi_id": "a", "label": "A", "unit": "units", "locate_hint": "hint a"},
        {"kpi_id": "b", "label": "B", "unit": "units", "locate_hint": "hint b"},
    ]

    def run_status(company="AAPL"):
        result = subprocess.run(
            ["uv", "run", "--script", str(KPI_SCHEMA_SCRIPT), "status", "--company", company],
            capture_output=True, text=True, timeout=60, env=env,
        )
        assert result.returncode == 0, (
            f"status subcommand failed: stdout={result.stdout!r} "
            f"stderr={result.stderr!r}"
        )
        return json.loads(result.stdout)

    propose_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_SCHEMA_SCRIPT), "propose",
            "--company", "AAPL", "--review-item-id", "rev-cli-schema-0001",
        ],
        input=json.dumps(kpi_defs),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert propose_result.returncode == 0, (
        f"propose subcommand failed: stdout={propose_result.stdout!r} "
        f"stderr={propose_result.stderr!r}"
    )

    proposed_status = run_status()
    assert proposed_status["company"] == "AAPL"
    assert proposed_status["versions"] == [{"version": 1, "status": "PROPOSED"}]
    assert proposed_status["confirmed_kpi_ids"] == [], (
        "an unconfirmed (PROPOSED) schema must report no confirmed_kpi_ids"
    )

    confirm_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_SCHEMA_SCRIPT), "confirm",
            "--company", "AAPL", "--by", "alice", "--at", "2024-01-01",
        ],
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert confirm_result.returncode == 0, (
        f"confirm subcommand failed: stdout={confirm_result.stdout!r} "
        f"stderr={confirm_result.stderr!r}"
    )

    confirmed_status = run_status()
    assert confirmed_status["versions"] == [{"version": 1, "status": "CONFIRMED"}]
    assert confirmed_status["confirmed_kpi_ids"] == ["a", "b"]

    # Fail-loud: a non-list JSON body (an object) must exit 2, nothing
    # written, no raw traceback.
    fail_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_SCHEMA_SCRIPT), "propose",
            "--company", "MSFT", "--review-item-id", "rev-cli-schema-0002",
        ],
        input=json.dumps({"x": 1}),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert fail_result.returncode == 2, fail_result.stderr
    assert "Traceback" not in fail_result.stderr, (
        "a non-list kpi_defs body must fail cleanly, not with a raw traceback"
    )
    msft_status = run_status("MSFT")
    assert msft_status["versions"] == [], (
        "a rejected non-list propose must write nothing for MSFT"
    )
