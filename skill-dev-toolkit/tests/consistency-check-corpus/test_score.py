"""Tests for score.py, the regression-corpus scorer (Acceptance 2)."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import score  # noqa: E402


def test_T_score_recorded_round8_union_6of6():
    recorded = sorted((HERE / "multi" / "recorded").glob("*.json"))
    assert len(recorded) == 4
    out = subprocess.run(
        [sys.executable, str(HERE / "score.py"), str(HERE / "multi"), *map(str, recorded)],
        capture_output=True, text=True, check=True,
    )
    result = json.loads(out.stdout)
    caught = {p["id"] for p in result["plants"] if p["caught"]}
    assert caught == {"X1", "X2", "X3", "X4", "X5", "X6"}
    assert result["recall"] == {"caught": 6, "total": 6}
    # TRIAGE-R8 judged son.sim.s2 F1 a REAL conflict missing from the answer
    # key: unmatched-high is a triage queue, not a list of false findings.
    assert [(f["source"], f["id"]) for f in result["unmatched_high"]] == [
        ("son.sim.s2.json", "F1")]


def test_T_score_flags_fabricated_high_false(tmp_path):
    fake = tmp_path / "fake.json"
    fake.write_text(json.dumps({"findings": [{
        "id": "F9", "type": "direct", "confidence": "high",
        "side_a": {"file": "references/writing-lean.md", "lines": [3], "quote": "x"},
        "side_b": {"file": "references/mermaid-usage-guidelines.md", "lines": [5], "quote": "y"},
        "why": "fabricated",
    }]}))
    result = score.score(HERE / "multi", [fake])
    assert not any(p["caught"] for p in result["plants"])
    assert result["recall"] == {"caught": 0, "total": 6}
    assert [f["id"] for f in result["unmatched_high"]] == ["F9"]


def test_single_file_set_takes_doc_from_filename(tmp_path):
    f = tmp_path / "doc_4.read.s1.json"
    f.write_text(json.dumps({"findings": [{
        "id": "F1", "type": "direct", "confidence": "high",
        "side_a": {"lines": [147], "quote": "x"},
        "side_b": {"lines": [271], "quote": "y"},
        "why": "delete vs keep sandbox",
    }]}))
    result = score.score(HERE / "single-a", [f])
    by_id = {p["id"]: p["caught"] for p in result["plants"]}
    assert by_id == {"P1": True, "P2": False, "P3": False}
    assert result["unmatched_high"] == []
