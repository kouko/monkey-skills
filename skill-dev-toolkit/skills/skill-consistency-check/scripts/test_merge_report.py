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


def _setup(tmp_path, findings_by_file, plan_kwargs=None, fill=True):
    """fill=True adds an empty output for every planned group not given."""
    target = tmp_path / "skill"
    target.mkdir()
    (target / "SKILL.md").write_text("x\n")
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps(_plan(target, **(plan_kwargs or {}))))
    findings_by_file = dict(findings_by_file)
    if fill:
        for name in ("read-1.json", "simulate-1.json"):
            findings_by_file.setdefault(name, [])
    paths = []
    for name, findings in findings_by_file.items():
        p = tmp_path / name
        p.write_text(json.dumps({"findings": findings}))
        paths.append(str(p))
    return target, plan, paths


def _run(target, plan, findings, out, model="Claude Sonnet 4"):
    cmd = [sys.executable, "-B", str(SCRIPT), "--target", str(target),
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
    target, plan, f = _setup(tmp_path, {"read-1.json": [
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
    target, plan, f = _setup(tmp_path, {"read-1.json": [
        _finding("F1", "medium", _side("SKILL.md", [3]), _side("a.md", [9])),
        _finding("F2", "low", _side("SKILL.md", [30]), _side("b.md", [1]))]})
    out = tmp_path / "out"
    r = _run(target, plan, f, out)
    assert r.returncode == 0, r.stderr
    data, _ = _report(out)
    assert data["verdict"] == "pass"
    assert [x["confidence"] for x in data["findings"]] == ["medium", "low"]


def test_findings_sorted_high_first_and_md_sections(tmp_path):
    target, plan, f = _setup(tmp_path, {"read-1.json": [
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
        "read-1.json": [_finding("R1", "medium", _side("SKILL.md", [10]),
                               _side("a.md", [20]))],
        "simulate-1.json": [_finding("S4", "high", _side("a.md", [22]),
                                   _side("SKILL.md", [8]))]})
    out = tmp_path / "out"
    r = _run(target, plan, f, out)
    data, _ = _report(out)
    assert len(data["findings"]) == 1
    m = data["findings"][0]
    assert m["confidence"] == "high"
    assert {(s["file"], s["id"]) for s in m["sources"]} == {
        ("read-1.json", "R1"), ("simulate-1.json", "S4")}
    assert r.returncode == 1


def test_findings_three_lines_apart_stay_separate(tmp_path):
    target, plan, f = _setup(tmp_path, {
        "read-1.json": [_finding("R1", "medium", _side("SKILL.md", [10]),
                               _side("a.md", [20]))],
        "simulate-1.json": [_finding("S1", "medium", _side("SKILL.md", [13]),
                                   _side("a.md", [20]))]})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    data, _ = _report(out)
    assert len(data["findings"]) == 2


def test_different_file_pair_not_merged(tmp_path):
    target, plan, f = _setup(tmp_path, {"read-1.json": [
        _finding("R1", "medium", _side("SKILL.md", [10]), _side("a.md", [20])),
        _finding("R2", "medium", _side("SKILL.md", [10]), _side("b.md", [20]))]})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    data, _ = _report(out)
    assert len(data["findings"]) == 2


# --- Acceptance 4 -----------------------------------------------------------

def test_limits_and_models_listed(tmp_path):
    target, plan, f = _setup(tmp_path, {"read-1.json": []})
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
    target, plan, f = _setup(tmp_path, {"read-1.json": []})
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
        tmp_path, {"read-1.json": []},
        {"grouped": True, "over_limit": True,
         "uncovered_pairs": [["references/a.md", "references/b.md"]]})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    data, md = _report(out)
    assert data["grouped"] is True and data["over_limit"] is True
    assert data["uncovered_pairs"] == [["references/a.md", "references/b.md"]]
    assert "Not checked together" in md
    assert "references/a.md" in md and "references/b.md" in md
    assert "exceeds the validated size" in md


def test_not_grouped_has_no_uncovered_section(tmp_path):
    target, plan, f = _setup(tmp_path, {"read-1.json": []})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    _, md = _report(out)
    assert "Not checked together" not in md


# --- Acceptance 5 -----------------------------------------------------------

def test_out_outside_target_written(tmp_path):
    target, plan, f = _setup(tmp_path, {"read-1.json": []})
    before = _tree(target)
    out = tmp_path / "reports" / "run1"
    r = _run(target, plan, f, out)
    assert r.returncode == 0, r.stderr
    assert (out / "consistency-report.json").is_file()
    assert (out / "consistency-report.md").is_file()
    assert _tree(target) == before


def test_out_inside_target_refused(tmp_path):
    target, plan, f = _setup(tmp_path, {"read-1.json": [
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
    target, plan, f = _setup(tmp_path, {})
    Path(f[0]).write_text("not json")
    out = tmp_path / "out"
    r = _run(target, plan, f, out)
    assert r.returncode == 2
    assert not out.exists()


def test_out_case_variant_refused(tmp_path):
    target, plan, f = _setup(tmp_path, {})
    variant = target.parent / target.name.upper()
    if not variant.exists():
        import pytest
        pytest.skip("case-sensitive filesystem")
    before = _tree(target)
    r = _run(target, plan, f, variant / "run")
    assert r.returncode == 2, r.stdout
    assert _tree(target) == before


# --- malformed findings -----------------------------------------------------

def test_malformed_sides_exit_2(tmp_path):
    good = _side("SKILL.md", [1])
    bads = [
        {"id": "X", "confidence": "high", "side_a": "SKILL.md:3", "side_b": good},
        {"id": "X", "confidence": "high", "side_a": _side("SKILL.md", 3), "side_b": good},
        {"id": "X", "confidence": "high", "side_a": {"lines": [1]}, "side_b": good},
        {"id": "X", "confidence": "high", "side_a": good, "side_b": _side(5, [1])},
        {"id": "X", "confidence": "high", "side_a": good, "side_b": _side("a.md", ["1"])},
        {"id": "X", "confidence": "high", "side_a": good, "side_b": _side("a.md", [True])},
    ]
    for i, bad in enumerate(bads):
        base = tmp_path / str(i)
        base.mkdir()
        ok = _finding("OK", "low", good, good)
        target, plan, f = _setup(base, {"read-1.json": [ok, bad]})
        out = base / "out"
        r = _run(target, plan, f, out)
        assert r.returncode == 2, (i, r.stderr)
        assert "Traceback" not in r.stderr, i
        assert not out.exists(), i


# --- findings file naming and group coverage --------------------------------

def test_missing_group_output_refused(tmp_path):
    target, plan, f = _setup(tmp_path, {"read-1.json": []}, fill=False)
    out = tmp_path / "out"
    r = _run(target, plan, f, out)
    assert r.returncode == 2
    assert "simulate-1" in r.stderr
    assert not out.exists()


def test_bad_findings_names_refused(tmp_path):
    for i, name in enumerate(["findings.json", "read-2.json", "read-0.json",
                              "simulate-1-x.json", "write-1.json"]):
        base = tmp_path / str(i)
        base.mkdir()
        target, plan, f = _setup(base, {name: []})
        out = base / "out"
        r = _run(target, plan, f, out)
        assert r.returncode == 2, (name, r.stdout)
        assert not out.exists(), name


def test_thorough_mode_second_run_accepted(tmp_path):
    target, plan, f = _setup(tmp_path, {"read-1-2.json": [], "simulate-1-2.json": []})
    out = tmp_path / "out"
    r = _run(target, plan, f, out)
    assert r.returncode == 0, r.stderr


def test_over_limit_warning_is_cause_neutral(tmp_path):
    target, plan, f = _setup(tmp_path, {}, {"grouped": True, "over_limit": True})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    _, md = _report(out)
    assert "core files alone" not in md
    assert ("At least one group exceeds the validated size (25,000 estimated "
            "tokens) because the core files or a single large file are too "
            "big; results for this run are less reliable.") in md


def test_markdown_only_coverage_note(tmp_path):
    target, plan, f = _setup(tmp_path, {})
    out = tmp_path / "out"
    _run(target, plan, f, out)
    data, md = _report(out)
    note = ("Only Markdown files other than README*.md are checked; "
            "rules in other file types are not.")
    assert data["coverage_note"] == note
    assert len(data["blind_spots"]) == 2 and note not in data["blind_spots"]
    assert note in md[md.index("Known limits"):]


# --- model match ------------------------------------------------------------

def test_model_match_whole_token_and_not_1m(tmp_path):
    target, plan, f = _setup(tmp_path, {})
    cases = {"claude-sonnet-4-5": True, "Claude Sonnet 4": True,
             "notsonnet": False, "claude-sonnet-4-5[1m]": False,
             "sonnet 1M": False, "opus": False,
             "unknown": False, "UNKNOWN": False}
    for i, (model, want) in enumerate(cases.items()):
        out = tmp_path / f"o{i}"
        _run(target, plan, f, out, model=model)
        data, _ = _report(out)
        assert data["model_matches_reference"] is want, model
