"""Tests for report-equity-memo/scripts/pack_inventory.py.

Pure stdlib CLI: turns a data-markets pack JSON into a machine-readable
section inventory (present/kind/rows|keys per top-level section, plus a
one-level-down breakdown of `mops` when present). This is ground truth the
memo-writing LLM checks "data was unavailable" claims against — a weak-model
run once falsely claimed TW T86/margin data was missing when Layer 1 had
already fetched it (mops.income_statement was populated in the pack).

Coverage:
  - --help runs
  - Happy path on the bundled TW memo-fetch fixture (mops present + subsections)
  - Empty/null section -> present: false
  - Missing input file -> exit 64
  - Malformed JSON -> exit 64
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "report-equity-memo" / "scripts" / "pack_inventory.py"
TW_FIXTURE = ROOT / "tests" / "data" / "fixtures" / "data-tw-memo-fetch-sample.json"


def _run(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_help_runs():
    cp = _run(["--help"])
    assert cp.returncode == 0
    assert "input" in cp.stdout.lower() or "pack" in cp.stdout.lower()


def test_tw_fixture_happy_path():
    cp = _run(["--input", str(TW_FIXTURE)])
    assert cp.returncode == 0, cp.stderr
    out = json.loads(cp.stdout)

    sections = out["sections"]
    assert "_normalized" not in sections  # underscore-prefixed meta key excluded
    assert "_partial" not in sections

    mops = sections["mops"]
    assert mops["present"] is True
    assert mops["kind"] == "dict"
    assert mops["keys"] == 9

    mops_sub = out["mops_subsections"]
    assert mops_sub["income_statement"]["present"] is True
    assert mops_sub["income_statement"]["kind"] == "dict"
    assert mops_sub["income_statement"]["keys"] == 4

    history = sections["history"]
    assert history["kind"] == "list"
    assert history["rows"] == 5

    assert out["_status"] is None
    assert out["_meta"] == {
        "generated_from": "data-tw-memo-fetch-sample.json",
        "tool": "pack_inventory",
    }


def test_empty_and_null_sections_present_false(tmp_path):
    pack = {
        "pack": "memo-fetch",
        "empty_dict_section": {},
        "empty_list_section": [],
        "null_section": None,
        "_status": "partial",
    }
    input_path = tmp_path / "synthetic_pack.json"
    input_path.write_text(json.dumps(pack), encoding="utf-8")

    cp = _run(["--input", str(input_path)])
    assert cp.returncode == 0, cp.stderr
    out = json.loads(cp.stdout)

    sections = out["sections"]
    assert sections["empty_dict_section"]["present"] is False
    assert sections["empty_dict_section"]["kind"] == "dict"
    assert sections["empty_dict_section"]["keys"] == 0

    assert sections["empty_list_section"]["present"] is False
    assert sections["empty_list_section"]["kind"] == "list"
    assert sections["empty_list_section"]["rows"] == 0

    assert sections["null_section"]["present"] is False
    assert sections["null_section"]["kind"] == "scalar"

    assert out["_status"] == "partial"


def test_all_failed_section_is_not_present(tmp_path):
    pack = {
        "pack": "memo-fetch",
        "error_only_section": {
            "error": "fetch failed",
            "requested": 6,
            "succeeded": 0,
            "failed": 6,
        },
        "status_failed_section": {
            "_status": "failed",
            "data": {"foo": "bar"},
        },
        "underscore_error_section": {
            "_error": "boom",
        },
        "partially_succeeded_section": {
            "requested": 6,
            "succeeded": 3,
            "failed": 3,
            "data": {"foo": "bar"},
        },
    }
    input_path = tmp_path / "synthetic_pack.json"
    input_path.write_text(json.dumps(pack), encoding="utf-8")

    cp = _run(["--input", str(input_path)])
    assert cp.returncode == 0, cp.stderr
    out = json.loads(cp.stdout)
    sections = out["sections"]

    assert sections["error_only_section"]["present"] is False
    assert sections["error_only_section"]["kind"] == "dict"
    assert sections["error_only_section"]["keys"] == 4  # keys count unaffected

    assert sections["status_failed_section"]["present"] is False
    assert sections["underscore_error_section"]["present"] is False

    # a section that actually succeeded at least once stays present
    assert sections["partially_succeeded_section"]["present"] is True


def test_missing_input_file_exits_64(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    cp = _run(["--input", str(missing)])
    assert cp.returncode == 64
    assert cp.stderr.strip()
    assert len(cp.stderr.strip().splitlines()) == 1


def test_malformed_json_exits_64(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    cp = _run(["--input", str(bad)])
    assert cp.returncode == 64
    assert cp.stderr.strip()
    assert len(cp.stderr.strip().splitlines()) == 1
