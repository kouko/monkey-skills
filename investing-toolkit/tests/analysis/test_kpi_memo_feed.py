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
import json
import os
import subprocess
import sys

from conftest import KPI_GATE_SCRIPT, KPI_MEMO_FEED_SCRIPT

import pytest


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
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                "source_cell_ref": "r5c2",
            }],
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


def test_trusted_feed_refuses_provenanceless_point(tmp_path, monkeypatch):
    """Task 2: in the TRUSTED path, build_memo_feed must REFUSE loud
    (ValueError naming the missing field + kpi_id) if ANY series-point in
    the supplied kpi_series lacks complete provenance
    (source_accession/source_table_id/source_cell_ref — absent/None/empty
    any counts as missing). A fully-provenanced TRUSTED series still
    builds fine.

    Why this matters: the memo-feed contract is the last seam before an
    LLM-authored narrative sees extracted figures — an unattributed value
    bundled into a TRUSTED feed would be untraceable to its source cell,
    defeating the whole point of primary-source anchoring at the one
    boundary the memo actually reads from.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    kpi_memo_feed, kpi_gate = _load_kpi_memo_feed_module()

    labels = [
        {"kpi_id": f"kpi_{i}", "period": "2024-Q1", "value": 100 + i}
        for i in range(5)
    ]
    kpi_gate.add_labels("PROVCO", labels)
    kpi_gate.evaluate(
        "PROVCO", "v1", [dict(label) for label in labels],
        threshold=0.95, min_samples=5, evaluated_at="2026-07-14T00:00:00Z",
    )
    assert kpi_gate.is_trusted("PROVCO", "v1") is True, (
        "test setup sanity: PROVCO/v1 must be TRUSTED before exercising build_memo_feed"
    )

    provenanceless_series = [
        {
            "kpi_id": "kpi_0",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                # source_cell_ref missing entirely
            }],
        },
    ]
    with pytest.raises(ValueError) as excinfo:
        kpi_memo_feed.build_memo_feed(
            "PROVCO", "v1", provenanceless_series, generated_at="2026-07-14T00:00:00Z",
        )
    assert "source_cell_ref" in str(excinfo.value)
    assert "kpi_0" in str(excinfo.value)

    # An empty-string cell ref must also count as missing (not just absent).
    empty_cell_ref_series = [
        {
            "kpi_id": "kpi_1",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                "source_cell_ref": "",
            }],
        },
    ]
    with pytest.raises(ValueError):
        kpi_memo_feed.build_memo_feed(
            "PROVCO", "v1", empty_cell_ref_series, generated_at="2026-07-14T00:00:00Z",
        )

    # A WHITESPACE-ONLY provenance value is also rejected — a blank-looking
    # cite is effectively unattributed (same class as the whitespace-identity
    # bypass; `not x` alone would wrongly let "   " through).
    whitespace_ref_series = [
        {
            "kpi_id": "kpi_1",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                "source_cell_ref": "   ",
            }],
        },
    ]
    with pytest.raises(ValueError):
        kpi_memo_feed.build_memo_feed(
            "PROVCO", "v1", whitespace_ref_series, generated_at="2026-07-14T00:00:00Z",
        )

    # A fully-provenanced TRUSTED series builds fine.
    good_series = [
        {
            "kpi_id": "kpi_0",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                "source_cell_ref": "r5c2",
            }],
        },
    ]
    good_feed = kpi_memo_feed.build_memo_feed(
        "PROVCO", "v1", good_series, generated_at="2026-07-14T00:00:00Z",
    )
    assert good_feed["status"] == "TRUSTED"
    assert good_feed["kpi_feeds"] == good_series


def test_cli_build_memo_feed_roundtrip(tmp_path):
    """Task 3: the kpi_memo_feed.py CLI's `build` subcommand is a thin
    wrapper over build_memo_feed, exercised via real `uv run --script`
    subprocess invocations (mirrors test_kpi_gate.py's CLI roundtrip).

    Sets up a TRUSTED gate via kpi_gate's own CLI (same KPI_STORE_DIR),
    then drives kpi_memo_feed.py build:
      (a) a provenanced kpi_series for the TRUSTED company -> status
          TRUSTED feed on stdout, exit 0.
      (b) a never-evaluated company -> status WITHHELD, exit 0 (a validly-
          withheld company is not a CLI error).
      (c) a provenance-less TRUSTED point -> exit 1 (ValueError).
      (d) malformed JSON -> exit 2, no raw traceback.
      (e) --help lists `build`.
    """
    env = {**os.environ, "KPI_STORE_DIR": str(tmp_path)}

    labels = [
        {"kpi_id": f"kpi_{i}", "period": "2024-Q1", "value": 100 + i}
        for i in range(5)
    ]
    add_labels_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_GATE_SCRIPT), "add-labels",
            "--company", "CLIMEMOCO",
        ],
        input=json.dumps(labels),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert add_labels_result.returncode == 0, (
        f"add-labels setup failed: stdout={add_labels_result.stdout!r} "
        f"stderr={add_labels_result.stderr!r}"
    )

    evaluate_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_GATE_SCRIPT), "evaluate",
            "--company", "CLIMEMOCO", "--schema-version", "v1",
            "--threshold", "0.95", "--at", "2026-07-14T00:00:00Z",
        ],
        input=json.dumps([dict(label) for label in labels]),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert evaluate_result.returncode == 0, (
        f"evaluate setup failed: stdout={evaluate_result.stdout!r} "
        f"stderr={evaluate_result.stderr!r}"
    )
    assert json.loads(evaluate_result.stdout)["verdict"] == "TRUSTED"

    good_series = [
        {
            "kpi_id": "kpi_0",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                "source_cell_ref": "r5c2",
            }],
        },
    ]

    # (a) TRUSTED company + provenanced series -> status TRUSTED, exit 0.
    trusted_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "build",
            "--company", "CLIMEMOCO", "--schema-version", "v1",
            "--generated-at", "2026-07-14T00:00:00Z",
        ],
        input=json.dumps(good_series),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert trusted_result.returncode == 0, (
        f"build (TRUSTED) failed: stdout={trusted_result.stdout!r} "
        f"stderr={trusted_result.stderr!r}"
    )
    trusted_feed = json.loads(trusted_result.stdout)
    assert trusted_feed["status"] == "TRUSTED"
    assert trusted_feed["kpi_feeds"] == good_series

    # (b) never-evaluated company -> status WITHHELD, exit 0 (not an error).
    withheld_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "build",
            "--company", "CLINEVERCO", "--schema-version", "v1",
            "--generated-at", "2026-07-14T00:00:00Z",
        ],
        input=json.dumps(good_series),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert withheld_result.returncode == 0, (
        f"build (WITHHELD) must exit 0, not error: stdout={withheld_result.stdout!r} "
        f"stderr={withheld_result.stderr!r}"
    )
    withheld_feed = json.loads(withheld_result.stdout)
    assert withheld_feed["status"] == "WITHHELD"
    assert withheld_feed["kpi_feeds"] == []

    # (c) provenance-less TRUSTED point -> exit 1.
    bad_series = [
        {
            "kpi_id": "kpi_0",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                # source_cell_ref missing
            }],
        },
    ]
    provenance_fail_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "build",
            "--company", "CLIMEMOCO", "--schema-version", "v1",
            "--generated-at", "2026-07-14T00:00:00Z",
        ],
        input=json.dumps(bad_series),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert provenance_fail_result.returncode == 1, provenance_fail_result.stderr
    assert "source_cell_ref" in provenance_fail_result.stderr

    # (d) malformed JSON -> exit 2, no raw traceback.
    malformed_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "build",
            "--company", "CLIMEMOCO", "--schema-version", "v1",
        ],
        input="{not valid json",
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert malformed_result.returncode == 2, malformed_result.stderr
    assert "Traceback" not in malformed_result.stderr, (
        "malformed build input must fail cleanly, not with a raw traceback"
    )

    # (e) --help lists the `build` subcommand.
    help_result = subprocess.run(
        ["uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert help_result.returncode == 0
    assert "build" in help_result.stdout
