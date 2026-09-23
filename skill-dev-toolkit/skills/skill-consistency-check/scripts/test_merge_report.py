"""Tests for merge_report.py (stdlib + pytest; fixtures built in tmp_path)."""
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("merge_report.py")


def _side(file, lines, quote="q"):
    return {"file": file, "lines": lines, "quote": quote}


def _finding(fid, conf, a, b, ftype="direct", why="w"):
    return {"id": fid, "type": ftype, "confidence": conf,
            "side_a": a, "side_b": b, "steps": [], "why": why}


def _plan(target, grouped=False, over_limit=False, uncovered_pairs=None):
    return {"target": str(target), "limit": 30000, "group_max": 25000,
            "files": [{"path": "SKILL.md", "tokens": 10, "core": True}],
            "total_tokens": 10, "core_tokens": 10,
            "grouped": grouped, "over_limit": over_limit,
            "groups": {"read": [["SKILL.md"]], "simulate": [["SKILL.md"]]},
            "uncovered_pairs": uncovered_pairs or []}


def _setup(tmp_path, findings_by_file, plan_kwargs=None):
    target = tmp_path / "skill"
    target.mkdir()
    (target / "SKILL.md").write_text("x\n")
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps(_plan(target, **(plan_kwargs or {}))))
    paths = []
    for name, findings in findings_by_file.items():
        p = tmp_path / name
        p.write_text(json.dumps({"findings": findings}))
        paths.append(str(p))
    return target, plan, paths


def _run(target, plan, findings, out, model="Claude Sonnet 4"):
    cmd = [sys.executable, str(SCRIPT), "--target", str(target),
           "--plan", str(plan), "--findings", *findings,
           "--model", model, "--out", str(out)]
    return subprocess.run(cmd, capture_output=True, text=True)


def _report(out):
    return (json.loads((out / "consistency-report.json").read_text()),
            (out / "consistency-report.md").read_text())


def _tree(path):
    return sorted(str(p.relative_to(path)) for p in path.rglob("*"))


# --- Acceptance 1 -----------------------------------------------------------

def test_high_gives_needs_revision(tmp_path):
    target, plan, f = _setup(tmp_path, {"read.json": [
        _finding("F1", "high", _side("SKILL.md", [3]), _side("a.md", [9])),
        _finding("F2", "low", _side("SKILL.md", [30]), _side("b.md", [1]))]})
    out = tmp_path / "out"
    r = _run(target, plan, f, out)
    assert r.returncode == 1, r.stderr
    data, md = _report(out)
    assert data["verdict"] == "needs-revision"
    assert data["counts"] == {"high": 1, "medium": 0, "low": 1}
    assert "needs-revision" in r.stdout
    assert str(out / "consistency-report.md") in r.stdout


def test_medium_low_only_pass(tmp_path):
    target, plan, f = _setup(tmp_path, {"read.json": [
        _finding("F1", "medium", _side("SKILL.md", [3]), _side("a.md", [9])),
        _finding("F2", "low", _side("SKILL.md", [30]), _side("b.md", [1]))]})
    out = tmp_path / "out"
    r = _run(target, plan, f, out)
    assert r.returncode == 0, r.stderr
    data, _ = _report(out)
    assert data["verdict"] == "pass"
    assert [x["confidence"] for x in data["findings"]] == ["medium", "low"]


def test_findings_sorted_high_first_and_md_sections(tmp_path):
    target, plan, f = _setup(tmp_path, {"read.json": [
        _finding("F1", "low", _side("SKILL.md", [50]), _side("c.md", [2])),
        _finding("F2", "high", _side("SKILL.md", [3], "must X"),
                 _side("a.md", [9], "never X"), why="X both required and banned")]})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    data, md = _report(out)
    assert [x["confidence"] for x in data["findings"]] == ["high", "low"]
    assert "SKILL.md:3" in md and "a.md:9" in md
    assert "must X" in md and "never X" in md and "X both required and banned" in md
    assert md.index("SKILL.md:3") < md.index("SKILL.md:50")


# --- merge ------------------------------------------------------------------

def test_duplicates_across_files_merge_keep_higher_confidence(tmp_path):
    target, plan, f = _setup(tmp_path, {
        "read.json": [_finding("R1", "medium", _side("SKILL.md", [10]),
                               _side("a.md", [20]))],
        "simulate.json": [_finding("S4", "high", _side("a.md", [22]),
                                   _side("SKILL.md", [8]))]})
    out = tmp_path / "out"
    r = _run(target, plan, f, out)
    data, _ = _report(out)
    assert len(data["findings"]) == 1
    m = data["findings"][0]
    assert m["confidence"] == "high"
    assert {(s["file"], s["id"]) for s in m["sources"]} == {
        ("read.json", "R1"), ("simulate.json", "S4")}
    assert r.returncode == 1


def test_findings_three_lines_apart_stay_separate(tmp_path):
    target, plan, f = _setup(tmp_path, {
        "read.json": [_finding("R1", "medium", _side("SKILL.md", [10]),
                               _side("a.md", [20]))],
        "simulate.json": [_finding("S1", "medium", _side("SKILL.md", [13]),
                                   _side("a.md", [20]))]})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    data, _ = _report(out)
    assert len(data["findings"]) == 2


def test_different_file_pair_not_merged(tmp_path):
    target, plan, f = _setup(tmp_path, {"read.json": [
        _finding("R1", "medium", _side("SKILL.md", [10]), _side("a.md", [20])),
        _finding("R2", "medium", _side("SKILL.md", [10]), _side("b.md", [20]))]})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    data, _ = _report(out)
    assert len(data["findings"]) == 2


# --- Acceptance 4 -----------------------------------------------------------

def test_limits_and_models_listed(tmp_path):
    target, plan, f = _setup(tmp_path, {"read.json": []})
    out = tmp_path / "out"
    r = _run(target, plan, f, out, model="claude-sonnet-4-5")
    assert r.returncode == 0, r.stderr
    data, md = _report(out)
    assert data["model"] == "claude-sonnet-4-5"
    assert data["reference"] == {"model": "Claude Sonnet (200k context)",
                                 "max_validated_tokens": 25000}
    assert len(data["blind_spots"]) == 2
    assert any("conditional" in b for b in data["blind_spots"])
    assert any("multi-step" in b for b in data["blind_spots"])
    assert "Known limits" in md
    for b in data["blind_spots"]:
        assert b in md
    assert ("Model used: claude-sonnet-4-5 — validated on: Claude Sonnet "
            "(200k context), packages up to 25,000 tokens") in md


def test_model_mismatch_warning(tmp_path):
    target, plan, f = _setup(tmp_path, {"read.json": []})
    out1, out2 = tmp_path / "o1", tmp_path / "o2"
    _run(target, plan, f, out1, model="gpt-5-codex")
    data, md = _report(out1)
    assert data["model_matches_reference"] is False
    assert "Accuracy with this model is not validated" in md
    _run(target, plan, f, out2, model="Claude SONNET 4.5")
    data, md = _report(out2)
    assert data["model_matches_reference"] is True
    assert "Accuracy with this model is not validated" not in md


def test_uncovered_pairs_and_over_limit_reported(tmp_path):
    target, plan, f = _setup(
        tmp_path, {"read.json": []},
        {"grouped": True, "over_limit": True,
         "uncovered_pairs": [["references/a.md", "references/b.md"]]})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    data, md = _report(out)
    assert data["grouped"] is True and data["over_limit"] is True
    assert data["uncovered_pairs"] == [["references/a.md", "references/b.md"]]
    assert "Not checked together" in md
    assert "references/a.md" in md and "references/b.md" in md
    assert "over" in md.lower() and "limit" in md.lower()


def test_not_grouped_has_no_uncovered_section(tmp_path):
    target, plan, f = _setup(tmp_path, {"read.json": []})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    _, md = _report(out)
    assert "Not checked together" not in md


# --- Acceptance 5 -----------------------------------------------------------

def test_out_outside_target_written(tmp_path):
    target, plan, f = _setup(tmp_path, {"read.json": []})
    before = _tree(target)
    out = tmp_path / "reports" / "run1"
    r = _run(target, plan, f, out)
    assert r.returncode == 0, r.stderr
    assert (out / "consistency-report.json").is_file()
    assert (out / "consistency-report.md").is_file()
    assert _tree(target) == before


def test_out_inside_target_refused(tmp_path):
    target, plan, f = _setup(tmp_path, {"read.json": [
        _finding("F1", "high", _side("SKILL.md", [3]), _side("a.md", [9]))]})
    link = tmp_path / "link"
    os.symlink(target, link)
    before = _tree(target)
    cases = [target, target / "sub", target / "sub" / "deeper",
             tmp_path / "elsewhere" / ".." / "skill" / "x",
             link, link / "inside"]
    for out in cases:
        r = _run(target, plan, f, out)
        assert r.returncode == 2, (out, r.stdout, r.stderr)
        assert r.stderr.strip(), out
        assert _tree(target) == before, out
    assert not (tmp_path / "elsewhere").exists()


def test_bad_findings_file_exit_2(tmp_path):
    target, plan, _ = _setup(tmp_path, {})
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    out = tmp_path / "out"
    r = _run(target, plan, [str(bad)], out)
    assert r.returncode == 2
    assert not out.exists()
