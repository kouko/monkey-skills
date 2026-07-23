"""Tests for loop_verdict.py — verdict CLI for the wiki-update fix loop.

Input contract SSOT: wiki_lint_check.py JSONL output (violation records
+ conservation counters + summary), see
obsidian/skills/wiki-lint/scripts/wiki_lint_check.py.
No registered REQ-ids exist for this arc — @req tags intentionally omitted.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "loop_verdict.py"


# ---------------------------------------------------------------- helpers

def viol(check_id="L01", file="entities/A.md", severity="error",
         line=1, detail="d"):
    return {"type": "violation", "check_id": check_id, "severity": severity,
            "file": file, "line": line, "detail": detail}


def ctr(file="entities/A.md", words=100, links=5, headings=3):
    return {"type": "counters", "file": file, "words": words,
            "links": links, "headings": headings}


def write_round(path, violations=(), counters=(), summary_override=None,
                raw_lines=None):
    """Write one wiki_lint_check.py-shaped JSONL round file."""
    if raw_lines is not None:
        path.write_text("\n".join(raw_lines) + "\n", encoding="utf-8")
        return path
    violations = list(violations)
    counters = list(counters)
    by_check = {}
    for v in violations:
        by_check[v["check_id"]] = by_check.get(v["check_id"], 0) + 1
    summary = {
        "type": "summary",
        "files": len(counters),
        "violations": len(violations),
        "errors": sum(1 for v in violations if v["severity"] == "error"),
        "warnings": sum(1 for v in violations if v["severity"] == "warning"),
        "by_check": dict(sorted(by_check.items())),
    }
    if summary_override:
        summary.update(summary_override)
    lines = ([json.dumps(v, ensure_ascii=False) for v in violations]
             + [json.dumps(c, ensure_ascii=False) for c in counters]
             + [json.dumps(summary, ensure_ascii=False)])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_verdict(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *[str(a) for a in args]],
        capture_output=True, text=True,
    )


# ---------------------------------------------------------------- compare

def test_compare_win(tmp_path):
    base = write_round(tmp_path / "r1.jsonl",
                       [viol(), viol(check_id="L07", file="entities/B.md")],
                       [ctr()])
    cand = write_round(tmp_path / "r2.jsonl", [viol()], [ctr()])
    r = run_verdict("compare", "--baseline", base, "--candidate", cand)
    assert r.returncode == 0, r.stderr


def test_compare_no_win_on_equal_counts(tmp_path):
    base = write_round(tmp_path / "r1.jsonl", [viol()], [ctr()])
    cand = write_round(tmp_path / "r2.jsonl",
                       [viol(check_id="L02", file="entities/C.md")], [ctr()])
    r = run_verdict("compare", "--baseline", base, "--candidate", cand)
    assert r.returncode == 1, r.stderr


def test_compare_counts_parse_lane_violations(tmp_path):
    """PARSE (error-lane, outside the SSOT check list) MUST count as a
    violation: 1 baseline L01 vs 1 candidate PARSE is no-win (1 vs 1) —
    if PARSE were excluded the candidate would count 0 and win."""
    base = write_round(tmp_path / "r1.jsonl", [viol()], [ctr()])
    cand = write_round(
        tmp_path / "r2.jsonl",
        [viol(check_id="PARSE", file="entities/bad.md", line=None,
              detail="unreadable")],
        [ctr()])
    r = run_verdict("compare", "--baseline", base, "--candidate", cand)
    assert r.returncode == 1, r.stderr


# ---------------------------------------------------------------- plateau

def _rounds_with_counts(tmp_path, counts):
    paths = []
    for i, n in enumerate(counts):
        vs = [viol(detail=f"r{i}-v{j}", line=j + 1) for j in range(n)]
        paths.append(write_round(tmp_path / f"p{i}.jsonl", vs, [ctr()]))
    return paths


def test_plateau_stops_after_k_rounds_no_improvement(tmp_path):
    paths = _rounds_with_counts(tmp_path, [5, 5, 6, 6])  # last 3 transitions never improve
    r = run_verdict("plateau", "--rounds", *paths, "--k", 3)
    assert r.returncode == 3, (r.returncode, r.stderr)


def test_plateau_continues_on_recent_improvement(tmp_path):
    paths = _rounds_with_counts(tmp_path, [5, 5, 5, 4])
    r = run_verdict("plateau", "--rounds", *paths, "--k", 3)
    assert r.returncode == 0, r.stderr


def test_plateau_continues_when_history_shorter_than_k(tmp_path):
    paths = _rounds_with_counts(tmp_path, [5, 5])
    r = run_verdict("plateau", "--rounds", *paths, "--k", 3)
    assert r.returncode == 0, r.stderr


# ---------------------------------------------------------------- budget

def test_budget_exhausted_on_round_cap():
    r = run_verdict("budget", "--round", 5, "--max-rounds", 5)
    assert r.returncode == 4, (r.returncode, r.stderr)


def test_budget_within_caps():
    r = run_verdict("budget", "--round", 3, "--max-rounds", 5,
                    "--spent-tokens", 900, "--max-tokens", 1000)
    assert r.returncode == 0, r.stderr


def test_budget_exhausted_on_token_cap():
    r = run_verdict("budget", "--round", 1, "--max-rounds", 5,
                    "--spent-tokens", 1001, "--max-tokens", 1000)
    assert r.returncode == 4, (r.returncode, r.stderr)


def test_budget_lone_token_arg_is_malformed():
    r = run_verdict("budget", "--round", 1, "--max-rounds", 5,
                    "--spent-tokens", 10)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "error:" in r.stderr


# ---------------------------------------------------------------- stuck

def test_stuck_three_strikes_and_ratchet(tmp_path):
    """Same failure signature — hash of the (check_id, file) set — for 3
    consecutive rounds => stuck-fingerprint; and a net decrease of
    conservation counters without a justification file => ratchet breach."""
    sig_rounds = []
    for i in range(3):
        vs = [viol(detail=f"round{i}", line=i + 10),
              viol(check_id="L07", file="entities/B.md",
                   detail=f"round{i}", line=i + 20)]
        sig_rounds.append(write_round(tmp_path / f"s{i}.jsonl", vs, [ctr()]))
    r = run_verdict("stuck", "--rounds", *sig_rounds)
    assert r.returncode == 5, (r.returncode, r.stderr)

    base = write_round(tmp_path / "rb.jsonl", [],
                       [ctr(words=200, links=10, headings=5)])
    cand = write_round(tmp_path / "rc.jsonl", [],
                       [ctr(words=150, links=10, headings=5)])
    r = run_verdict("ratchet", "--baseline", base, "--candidate", cand)
    assert r.returncode == 8, (r.returncode, r.stderr)


def test_stuck_no_new_info_round(tmp_path):
    vs = [viol(), viol(check_id="L07", file="entities/B.md")]
    a = write_round(tmp_path / "a.jsonl", vs, [ctr()])
    b = write_round(tmp_path / "b.jsonl", vs, [ctr()])
    r = run_verdict("stuck", "--rounds", a, b)
    assert r.returncode == 6, (r.returncode, r.stderr)


def test_stuck_regression_takes_precedence(tmp_path):
    a = write_round(tmp_path / "a.jsonl", [viol()], [ctr()])
    b = write_round(tmp_path / "b.jsonl",
                    [viol(), viol(check_id="L02", file="entities/C.md")],
                    [ctr()])
    r = run_verdict("stuck", "--rounds", a, b)
    assert r.returncode == 7, (r.returncode, r.stderr)


def test_stuck_fingerprint_precedes_no_new_info(tmp_path):
    vs = [viol()]
    paths = [write_round(tmp_path / f"i{i}.jsonl", vs, [ctr()])
             for i in range(3)]
    r = run_verdict("stuck", "--rounds", *paths)
    assert r.returncode == 5, (r.returncode, r.stderr)


def test_stuck_healthy_history_not_stuck(tmp_path):
    a = write_round(tmp_path / "a.jsonl",
                    [viol(), viol(check_id="L07", file="entities/B.md")],
                    [ctr()])
    b = write_round(tmp_path / "b.jsonl", [viol()], [ctr()])
    r = run_verdict("stuck", "--rounds", a, b)
    assert r.returncode == 0, r.stderr


# ---------------------------------------------------------------- ratchet

def test_ratchet_ok_with_justification(tmp_path):
    base = write_round(tmp_path / "rb.jsonl", [],
                       [ctr(words=200, links=10, headings=5)])
    cand = write_round(tmp_path / "rc.jsonl", [],
                       [ctr(words=150, links=10, headings=5)])
    note = tmp_path / "justification.md"
    note.write_text("intentional prune of duplicated section",
                    encoding="utf-8")
    r = run_verdict("ratchet", "--baseline", base, "--candidate", cand,
                    "--justification", note)
    assert r.returncode == 0, r.stderr


def test_ratchet_missing_justification_file_is_malformed(tmp_path):
    base = write_round(tmp_path / "rb.jsonl", [],
                       [ctr(words=200)])
    cand = write_round(tmp_path / "rc.jsonl", [],
                       [ctr(words=150)])
    r = run_verdict("ratchet", "--baseline", base, "--candidate", cand,
                    "--justification", tmp_path / "nope.md")
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "error:" in r.stderr


def test_ratchet_ok_when_counters_do_not_decrease(tmp_path):
    base = write_round(tmp_path / "rb.jsonl", [],
                       [ctr(words=200, links=10, headings=5)])
    cand = write_round(tmp_path / "rc.jsonl", [],
                       [ctr(words=200, links=12, headings=5)])
    r = run_verdict("ratchet", "--baseline", base, "--candidate", cand)
    assert r.returncode == 0, r.stderr


# ------------------------------------------------- healthy progress: no stop

def test_healthy_progress_triggers_no_stop_code(tmp_path):
    """A healthy improving history triggers none of the stop verdicts."""
    counts = [3, 2, 1]
    paths = []
    for i, n in enumerate(counts):
        vs = [viol(check_id=cid, file=f"entities/F{i}{j}.md")
              for j, cid in enumerate(["L01", "L02", "L07"][:n])]
        paths.append(write_round(
            tmp_path / f"h{i}.jsonl", vs,
            [ctr(words=100 + i, links=5 + i, headings=3)]))
    assert run_verdict("compare", "--baseline", paths[1],
                       "--candidate", paths[2]).returncode == 0
    assert run_verdict("plateau", "--rounds", *paths, "--k", 2).returncode == 0
    assert run_verdict("budget", "--round", 3,
                       "--max-rounds", 10).returncode == 0
    assert run_verdict("stuck", "--rounds", *paths).returncode == 0
    assert run_verdict("ratchet", "--baseline", paths[1],
                       "--candidate", paths[2]).returncode == 0


# ---------------------------------------------------------------- malformed

def test_missing_round_file_is_malformed(tmp_path):
    ok = write_round(tmp_path / "ok.jsonl", [viol()], [ctr()])
    r = run_verdict("compare", "--baseline", tmp_path / "absent.jsonl",
                    "--candidate", ok)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "error:" in r.stderr


def test_invalid_json_line_is_malformed(tmp_path):
    bad = write_round(tmp_path / "bad.jsonl",
                      raw_lines=['{"type": "violation"', "{}"])
    ok = write_round(tmp_path / "ok.jsonl", [viol()], [ctr()])
    r = run_verdict("compare", "--baseline", bad, "--candidate", ok)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "error:" in r.stderr


def test_summary_count_mismatch_is_malformed(tmp_path):
    """Truncation guard: summary['violations'] must equal the number of
    violation records actually present in the file."""
    bad = write_round(tmp_path / "bad.jsonl", [viol()], [ctr()],
                      summary_override={"violations": 7})
    ok = write_round(tmp_path / "ok.jsonl", [viol()], [ctr()])
    r = run_verdict("compare", "--baseline", bad, "--candidate", ok)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "error:" in r.stderr


def test_missing_summary_record_is_malformed(tmp_path):
    bad = write_round(tmp_path / "bad.jsonl",
                      raw_lines=[json.dumps(viol()), json.dumps(ctr())])
    ok = write_round(tmp_path / "ok.jsonl", [viol()], [ctr()])
    r = run_verdict("compare", "--baseline", bad, "--candidate", ok)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "error:" in r.stderr


# ---------------------------------------------------------------- meta

def test_origin_note_present():
    """Acceptance: adapted-copy disclosure (bounded duplication) in header."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert "improve_loop_verdict.py" in text
    assert "adapted" in text.lower()


def test_stdlib_only_imports():
    """Plugin self-containment: no third-party and no repo-level imports."""
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "relative (repo-level) import found"
            mods.add(node.module.split(".")[0])
    non_stdlib = mods - set(sys.stdlib_module_names)
    assert not non_stdlib, f"non-stdlib imports: {sorted(non_stdlib)}"
