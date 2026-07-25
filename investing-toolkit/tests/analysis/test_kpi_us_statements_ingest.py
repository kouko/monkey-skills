"""Tests for analysis-kpi/scripts/kpi_us_statements_ingest.py — US
statement-pack envelope -> kpi_store driver (plan Task 9,
docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md).

Mirrors test_kpi_tw_ingest.py: the `ingest` verb is exercised end-to-end
through its CLI subprocess, the durable store redirected to a tmp dir via
KPI_STORE_DIR (the ~/.local/share store is never touched).

No `@req` tags: this dispatch's plan (docs/loom/plans/2026-07-26-us-as-
reported-statement-lane.md) traces work by named plan Tasks, NOT registered
loom-spec REQ-ids — so `@req` is omitted per the implementer contract.
"""
from __future__ import annotations

import json
import os
import subprocess

from conftest import KPI_STORE_SCRIPT, SKILLS

INGEST_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statements_ingest.py"


def _pack(facts, source_kind="xbrl-companyfacts", include_source_kind=True, company="Apple Inc."):
    # PIN shape (plan ## Notes — "PIN — statement pack envelope").
    envelope = {
        "pack": "statement-backfill",
        "ticker": "AAPL",
        "fetched_at": "2026-07-26T00:00:00Z",
        "company": company,
        "facts": facts,
        "coverage": {"skipped_rows": []},
    }
    if include_source_kind:
        envelope["source_kind"] = source_kind
    return envelope


def _duration_fact(
    concept: str,
    start: str,
    end: str,
    value: float,
    accession: str = "0000320193-25-000079",
    filed: str = "2025-10-31",
) -> dict:
    return {
        "concept": concept,
        "period_start": start,
        "period_end": end,
        "period_kind": "duration",
        "value": value,
        "unit": "USD",
        "accession": accession,
        "filed": filed,
        "form": "10-K",
    }


def _run_ingest(filing_path, env) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(INGEST_SCRIPT), "ingest", "--filing", str(filing_path)],
        capture_output=True,
        text=True,
        timeout=90,
        env=env,
    )


def _run_dump(company, env) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(KPI_STORE_SCRIPT), "dump", "--company", company],
        capture_output=True,
        text=True,
        timeout=90,
        env=env,
    )


def _total_observations(payload: dict) -> int:
    return sum(
        len(entry["observations"])
        for series in payload["series"]
        for entry in series["periods"]
    )


def test_valid_envelope_appends_points_and_second_ingest_is_idempotent(tmp_path):
    """A valid envelope appends every point into a tmp store, and a SECOND
    ingest of the SAME envelope is a no-op (the store's 5-tuple dedup key
    re-derives identically — no duplicate points)."""
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack = _pack(
        [
            _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0),
            _duration_fact(
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "2024-01-01",
                "2024-12-31",
                2000.0,
            ),
        ]
    )
    filing_path = tmp_path / "pack.json"
    filing_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(filing_path, env)
    assert result.returncode == 0, (
        f"ingest failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    summary = json.loads(result.stdout)
    assert summary["company"] == "Apple Inc."
    assert summary["appended"] == 2
    assert summary["kpi_ids"] == sorted(
        [
            "us-gaap:Revenues",
            "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        ]
    )

    assert store_dir.exists(), "ingest did not write to the tmp KPI_STORE_DIR"
    assert list(store_dir.glob("*.json")), "no series file written to tmp store"

    dump = _run_dump("Apple Inc.", env)
    assert dump.returncode == 0, (
        f"dump failed: stdout={dump.stdout!r} stderr={dump.stderr!r}"
    )
    payload = json.loads(dump.stdout)
    observations_after_first = _total_observations(payload)
    assert observations_after_first == summary["appended"]

    result2 = _run_ingest(filing_path, env)
    assert result2.returncode == 0, (
        f"second ingest failed: stdout={result2.stdout!r} stderr={result2.stderr!r}"
    )
    dump2 = _run_dump("Apple Inc.", env)
    payload2 = json.loads(dump2.stdout)
    assert _total_observations(payload2) == observations_after_first, (
        "second ingest of the same envelope must be idempotent (no duplicate points)"
    )


def test_rejected_pack_writes_nothing(tmp_path):
    """An envelope declaring an untrusted source_kind is rejected before any
    point is built or written — the store dir gains no series file, and the
    CLI exits non-zero (fail loud, never a silent swallow)."""
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack = _pack(
        [_duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)],
        source_kind="llm-located",
    )
    filing_path = tmp_path / "pack.json"
    filing_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(filing_path, env)
    assert result.returncode != 0
    assert "llm-located" in result.stderr

    assert not store_dir.exists() or not list(store_dir.glob("*.json")), (
        "a rejected pack must write nothing to the store"
    )


def test_source_kind_absent_key_defaults_and_succeeds(tmp_path):
    """An envelope with NO `source_kind` key at all is undeclared, not
    malformed — it defaults to the PIN's mandatory trusted literal and the
    ingest succeeds."""
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack = _pack(
        [_duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)],
        include_source_kind=False,
    )
    filing_path = tmp_path / "pack.json"
    filing_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(filing_path, env)
    assert result.returncode == 0, (
        f"ingest failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    summary = json.loads(result.stdout)
    assert summary["appended"] == 1


def test_source_kind_explicit_empty_is_rejected_not_defaulted(tmp_path):
    """An envelope carrying an EXPLICIT empty-string `source_kind` is a
    malformed envelope, not an undeclared one — it must be rejected by name,
    never silently stamped with the default."""
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack = _pack(
        [_duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)],
        source_kind="",
    )
    filing_path = tmp_path / "pack.json"
    filing_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(filing_path, env)
    assert result.returncode != 0
    assert not store_dir.exists() or not list(store_dir.glob("*.json"))


def test_missing_company_is_a_malformed_envelope(tmp_path):
    """An envelope with no `company` cannot key the store — rejected loud,
    nothing written."""
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack = _pack(
        [_duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)],
        company=None,
    )
    filing_path = tmp_path / "pack.json"
    filing_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(filing_path, env)
    assert result.returncode != 0
    assert not store_dir.exists() or not list(store_dir.glob("*.json"))


def test_later_malformed_fact_leaves_the_earlier_points_unwritten(tmp_path):
    """The partial-write case the other rejection tests cannot reach: a
    MULTI-fact pack whose EARLIER fact is valid and whose LATER fact lacks
    `accession`.

    `test_rejected_pack_writes_nothing` and
    `test_missing_filed_date_is_a_missing_as_of` both reject on the pack's
    ONLY fact, so neither ever reaches "reject after N-1 points were already
    appended". kpi_store.append's own `_require_provenance` fires INSIDE the
    per-point drain loop and each append commits independently, so a guard
    that lived only there would durably write fact #1 and then raise on
    fact #2 — a partial write into an append-only store.

    The claim under test is about what LANDED, not about what was raised, so
    the assertion is on the STORE's contents: zero observations for the
    company after a non-zero exit.
    """
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    good = _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)
    bad = _duration_fact("us-gaap:Assets", "2024-01-01", "2024-12-31", 2000.0)
    del bad["accession"]
    pack = _pack([good, bad])
    filing_path = tmp_path / "pack.json"
    filing_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(filing_path, env)
    assert result.returncode != 0, (
        f"a pack with a malformed later fact must fail loud: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "accession" in result.stderr

    dump = _run_dump("Apple Inc.", env)
    assert dump.returncode == 0, (
        f"dump failed: stdout={dump.stdout!r} stderr={dump.stderr!r}"
    )
    payload = json.loads(dump.stdout)
    assert _total_observations(payload) == 0, (
        "the EARLIER valid fact must not have been committed before the "
        "later fact was rejected — an append-only store cannot un-write it"
    )


def test_missing_filed_date_is_a_missing_as_of(tmp_path):
    """A fact with no `filed` date yields no derivable `as_of` — the driver
    rejects the whole pack loud rather than writing a partial store."""
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    fact = _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)
    fact["filed"] = None
    pack = _pack([fact])
    filing_path = tmp_path / "pack.json"
    filing_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(filing_path, env)
    assert result.returncode != 0
    assert not store_dir.exists() or not list(store_dir.glob("*.json"))
