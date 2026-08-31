"""RED-first tests for prose_selfsweep_tally.py — the A/B tally scorer.

Scores only; renders no verdict. See docs/loom/plans/
2026-09-01-prose-edit-self-sweep.md Task 3 for the input/output spec.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "prose_selfsweep_tally.py"


def _record(case_id="c1", arm="A", rep=1, causes=None, hedge_marks=0,
            draft_tokens=100, review_rounds=1):
    return {
        "case_id": case_id,
        "arm": arm,
        "rep": rep,
        "gating_findings": [
            {"cause": c, "class": "instruction"} for c in (causes or [])
        ],
        "hedge_marks": hedge_marks,
        "draft_tokens": draft_tokens,
        "review_rounds": review_rounds,
    }


def _write(tmp_path: Path, records: list[dict]) -> Path:
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps(records), encoding="utf-8")
    return fixture


def _run(fixture: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(fixture)],
        capture_output=True,
        text=True,
    )


def test_valid_two_arm_fixture_prints_table_with_both_arms_totals(tmp_path):
    records = [
        _record(case_id="c1", arm="A", rep=1, causes=["A", "B"], hedge_marks=2,
                draft_tokens=100, review_rounds=1),
        _record(case_id="c1", arm="A", rep=2, causes=["A"], hedge_marks=1,
                draft_tokens=200, review_rounds=2),
        _record(case_id="c1", arm="B", rep=1, causes=["C"], hedge_marks=0,
                draft_tokens=150, review_rounds=1),
        _record(case_id="c1", arm="B", rep=2, causes=[], hedge_marks=1,
                draft_tokens=150, review_rounds=1),
    ]
    fixture = _write(tmp_path, records)

    result = _run(fixture)

    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr
    assert "A" in result.stdout and "B" in result.stdout
    # Table shape: a markdown table has header separator rows.
    assert "---" in result.stdout or "| --" in result.stdout
    # No verdict / interpretive wording anywhere in the output.
    for banned in ("improved", "worse", "better", "regressed", "verdict"):
        assert banned not in result.stdout.lower(), (
            f"output contains interpretive wording {banned!r}:\n{result.stdout}"
        )
    # Value-level assertions on per-arm computed totals — catches an
    # aggregation mutant that folds every record into one arm's bucket.
    # Arm A: findings [A,B],[A] -> total 3, cause A=2, cause B=1;
    #   hedge_marks 2+1=3; draft_tokens mean (100+200)/2=150.0.
    # Arm B: findings [C],[] -> total 1, cause C=1; hedge_marks 0+1=1;
    #   draft_tokens mean (150+150)/2=150.0.
    assert "| gating findings (total) | 3 | 1 |" in result.stdout
    assert "| gating findings (cause A) | 2 | 0 |" in result.stdout
    assert "| gating findings (cause C) | 0 | 1 |" in result.stdout
    assert "| hedge marks (total) | 3 | 1 |" in result.stdout
    assert "| draft tokens (mean) | 150.0 | 150.0 |" in result.stdout


def test_unknown_arm_exits_nonzero_naming_the_record(tmp_path):
    records = [
        _record(case_id="c1", arm="C", rep=1, causes=["A"]),
    ]
    fixture = _write(tmp_path, records)

    result = _run(fixture)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    combined = result.stdout + result.stderr
    assert "c1" in combined
    assert "C" in combined


def test_unknown_cause_code_exits_nonzero_naming_the_record(tmp_path):
    records = [
        _record(case_id="c1", arm="A", rep=1, causes=["Z"]),
    ]
    fixture = _write(tmp_path, records)

    result = _run(fixture)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    combined = result.stdout + result.stderr
    assert "c1" in combined
    assert "Z" in combined


def test_duplicate_case_arm_rep_exits_nonzero(tmp_path):
    records = [
        _record(case_id="c1", arm="A", rep=1, causes=["A"]),
        _record(case_id="c1", arm="A", rep=1, causes=["B"]),
    ]
    fixture = _write(tmp_path, records)

    result = _run(fixture)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    combined = result.stdout + result.stderr
    assert "c1" in combined and "A" in combined


def test_evidence_class_finding_does_not_inflate_gating_total(tmp_path):
    record = _record(case_id="c1", arm="A", rep=1, causes=[])
    record["gating_findings"] = [
        {"cause": "A", "class": "instruction"},
        {"cause": "B", "class": "evidence"},
    ]
    fixture = _write(tmp_path, [record])

    result = _run(fixture)

    assert result.returncode == 0, result.stderr
    # Only the instruction-class finding counts toward the gating metric.
    assert "| gating findings (total) | 1 | 0 |" in result.stdout
    assert "| gating findings (cause A) | 1 | 0 |" in result.stdout
    assert "| gating findings (cause B) | 0 | 0 |" in result.stdout


def test_missing_finding_class_exits_nonzero_naming_the_record(tmp_path):
    record = _record(case_id="c1", arm="A", rep=1, causes=[])
    record["gating_findings"] = [{"cause": "A"}]
    fixture = _write(tmp_path, [record])

    result = _run(fixture)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    combined = result.stdout + result.stderr
    assert "c1" in combined


def test_unknown_finding_class_exits_nonzero_naming_the_record(tmp_path):
    record = _record(case_id="c1", arm="A", rep=1, causes=[])
    record["gating_findings"] = [{"cause": "A", "class": "bogus"}]
    fixture = _write(tmp_path, [record])

    result = _run(fixture)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    combined = result.stdout + result.stderr
    assert "c1" in combined and "bogus" in combined


def test_rep_int_vs_str_treated_as_duplicate(tmp_path):
    records = [
        _record(case_id="c1", arm="A", rep=1, causes=["A"]),
        _record(case_id="c1", arm="A", rep="1", causes=["B"]),
    ]
    fixture = _write(tmp_path, records)

    result = _run(fixture)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    combined = result.stdout + result.stderr
    assert "c1" in combined


def test_non_list_top_level_json_exits_nonzero_without_traceback(tmp_path):
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

    result = _run(fixture)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert result.stderr.strip() != ""


def test_record_missing_draft_tokens_exits_nonzero_named_not_silent_zero(tmp_path):
    record = _record(case_id="c1", arm="A", rep=1, causes=["A"])
    del record["draft_tokens"]
    fixture = _write(tmp_path, [record])

    result = _run(fixture)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    combined = result.stdout + result.stderr
    assert "c1" in combined
    assert "draft_tokens" in combined


def test_non_dict_record_exits_nonzero_without_traceback(tmp_path):
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps(["not-a-dict"]), encoding="utf-8")

    result = _run(fixture)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert result.stderr.strip() != ""
