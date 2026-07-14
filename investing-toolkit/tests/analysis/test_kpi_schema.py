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
