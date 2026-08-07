"""G1 Task 3 — the real, quota-spending e2e run against the SPARSE-comment variant.

The W1 harness proved dbt-wiki scores 5/5 on the full-comment fixture
(`test_e2e_validation.py`). This test isolates comment density as the single
changed variable: it materializes a sparse-comment copy of the SAME fixture via
`build_sparse_variant` (Task 2 — every `models/**.sql` has its inline comments
stripped, every `.yml`/seed/config left byte-identical), then drives a blind
headless `claude -p` through `/dbt-wiki:init` -> `/dbt-wiki:pack` -> answering
the 5 gold questions against that copy, and grades its answers through the
UNCHANGED `grader.py` against the UNCHANGED, original `gold-questions.yml`. A
lower score than W1's 5/5 is itself the deliverable finding of this increment,
not a harness failure.

Reuse: the containment/parse/cleanup helpers are variant-agnostic and imported
from `test_e2e_validation`. Only `_build_report` is rewritten here because W1's
carries a W1 task label and lacks this run's `baseline_comparison` field.

Containment: unlike W1 (whose fixture lives inside this public repo), the sparse
variant lands in a fresh pytest `tmp_path` OUTSIDE the repo, so no init/pack
byproduct can reach version control by construction. We still give it its own
temporary git root so `/dbt-wiki:init`'s `git rev-parse --show-toplevel`
resolves inside the copy, and still run the belt-and-suspenders repo-root leak
check, mirroring the W1 precedent exactly.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

import grader
import runner
from build_sparse_variant import build_sparse_variant
from test_e2e_validation import (
    _CANNED_MARKER,  # noqa: F401 — re-exported so this run's authenticity check shares W1's marker
    _bundles_in,
    _cleanup_run_byproducts,
    _flag_bearing_grade,
    _parse_run_output,
    _repo_root,
    snapshot_repo_root_byproducts,
)

TESTS_DIR = Path(__file__).parent
FIXTURE_DIR = TESTS_DIR / "fixtures" / "l2-harness"
GOLD_QUESTIONS = FIXTURE_DIR / "gold-questions.yml"
REPORT_PATH = TESTS_DIR / "reports" / "g1-sparse-comment-run.json"
W1_REPORT_PATH = TESTS_DIR / "reports" / "w1-e2e-run.json"

RUN_TIMEOUT_SECONDS = 600


def _w1_baseline() -> dict:
    """W1's real full-comment result for direct comparison. Read from the W1
    report if present (it is gitignored, so may be absent on a fresh checkout),
    else fall back to the recorded fact: 5/5, 100%."""
    try:
        w1 = json.loads(W1_REPORT_PATH.read_text())
        return {
            "score": w1["score"],
            "accuracy_pct": w1["accuracy_pct"],
            "passed_count": w1["passed_count"],
            "total": w1["total"],
            "source": str(W1_REPORT_PATH),
        }
    except (OSError, KeyError, json.JSONDecodeError):
        return {
            "score": 1.0,
            "accuracy_pct": 100.0,
            "passed_count": 5,
            "total": 5,
            "source": "hardcoded W1 result (report absent)",
        }


def _build_report(
    cmd: list[str],
    sparse_dir: Path,
    run_meta: dict,
    parse_error: str | None,
    raw_answers: dict,
    report_grade: grader.GradeReport,
    is_real_output: bool,
    final_message: str,
    landing: dict,
) -> dict:
    """Assemble the G1 audit report, including the W1 baseline_comparison."""
    results = [
        {
            "trap": r.trap,
            "expected": r.expected,
            "actual": r.actual,
            "value_correct": r.value_correct,
            "invariant_failures": r.invariant_failures,
            "passed": r.passed,
        }
        for r in report_grade.results
    ]
    baseline = _w1_baseline()
    g1_accuracy = round(report_grade.score * 100, 2)
    return {
        "task": "G1 sparse-comment fixture ablation — Task 3 real validation run",
        "variant": (
            "sparse-comment: every models/**.sql has inline `--`/`/* */` comments "
            "stripped; all .yml descriptions, seeds, and config left byte-identical"
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": cmd,
        "cwd": str(sparse_dir),
        "run": run_meta,
        "parse_error": parse_error,
        "raw_answers": raw_answers,
        "results": results,
        "score": report_grade.score,
        "accuracy_pct": g1_accuracy,
        "passed_count": report_grade.passed_count,
        "total": report_grade.total,
        # Advisory, never folded into `score` — see the W1 report builder.
        "invariant_flag_count": report_grade.invariant_flag_count,
        "is_real_model_output": is_real_output,
        "final_message_excerpt": final_message[:2000],
        "governance": {
            "note": (
                "pack bundle must NEVER be committed into this public repo "
                "(dbt-wiki/skills/pack/SKILL.md). Sparse variant built in a "
                "tmp_path OUTSIDE the repo with its own temporary git root so "
                "init/pack output stays fully contained + is cleaned up."
            ),
            "landing": landing,
        },
        "trace_caveat": (
            "trace = final assistant message only (--output-format json exposes "
            "no full SQL transcript); prohibition-invariant verdicts are advisory."
        ),
        "baseline_comparison": {
            "w1_variant": "full-comment (original committed fixture)",
            "w1": baseline,
            "g1_variant": "sparse-comment (this run)",
            "g1_score": report_grade.score,
            "g1_accuracy_pct": g1_accuracy,
            "delta_accuracy_pct": round(g1_accuracy - baseline["accuracy_pct"], 2),
            "note": (
                "W1 scored 5/5 (100%) on the full-comment fixture. This G1 run "
                "grades the SAME fixture with model inline comments stripped, "
                "isolating comment density as the only changed variable. A lower "
                "score here is the deliverable finding, not a harness failure."
            ),
        },
    }


def test_sparse_report_carries_the_advisory_flag_count():
    """Same pin as W1's — the G1 builder is equally e2e-gated (round 3)."""
    report = _build_report(
        cmd=["claude", "-p"],
        sparse_dir=Path("/nonexistent-sparse-dir"),
        run_meta={},
        parse_error=None,
        raw_answers={},
        report_grade=_flag_bearing_grade(),
        is_real_output=True,
        final_message="",
        landing={"fixture_bundles": [], "repo_root_bundles": [], "repo_root_dbt_wiki": False},
    )

    assert report["accuracy_pct"] == 100.0, "precondition: the flag-blind shape"
    assert report["invariant_flag_count"] == 2


@pytest.mark.e2e
def test_sparse_comment_variant_scores_the_blind_agent(tmp_path):
    # --- RED precondition: the report must not exist before this run. ---
    assert not REPORT_PATH.exists(), (
        f"{REPORT_PATH} already exists — this is a one-shot real run; "
        "delete the stale report before re-running."
    )

    repo_root = _repo_root()
    questions = yaml.safe_load(GOLD_QUESTIONS.read_text())
    assert questions, "gold-questions.yml is empty — Task 8 fixture missing"

    # Materialize the sparse-comment copy OUTSIDE the repo, in pytest's tmp_path.
    sparse_dir = tmp_path / "l2-harness-sparse"
    build_sparse_variant(FIXTURE_DIR, sparse_dir)

    cmd = runner.build_command(sparse_dir, questions, skip_permissions=True)

    # A fresh tmp_path never had a git root or CLAUDE.md of its own, so every
    # init/pack byproduct is unambiguously ours to remove.
    preexisting_git = False
    preexisting_claude_md = False
    # The repo root, however, is the maintainer's — snapshot what was already
    # there so teardown never removes a real `.dbt-wiki/` or bundle.
    preexisting_repo_byproducts = snapshot_repo_root_byproducts(repo_root)

    landing = {"fixture_bundles": [], "repo_root_bundles": [], "repo_root_dbt_wiki": False}
    run_meta: dict = {}

    try:
        # Contain init/pack output by giving the sparse copy its own git root.
        subprocess.run(["git", "init", "-q"], cwd=sparse_dir, check=True)

        proc = subprocess.run(
            cmd,
            cwd=sparse_dir,
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT_SECONDS,
        )
        run_meta = {
            "returncode": proc.returncode,
            "stdout_len": len(proc.stdout),
            "stderr_tail": proc.stderr[-2000:],
        }

        # Record where init/pack actually wrote, BEFORE cleanup removes it.
        landing["fixture_bundles"] = [str(p) for p in _bundles_in(sparse_dir)]
        landing["repo_root_bundles"] = [str(p) for p in _bundles_in(repo_root)]
        landing["repo_root_dbt_wiki"] = (repo_root / ".dbt-wiki").exists()

        raw_answers, parse_error, final_message, is_real_output = _parse_run_output(
            proc.stdout
        )

        answers = {
            trap: {"value": value, "trace": final_message}
            for trap, value in raw_answers.items()
        }
        report_grade = grader.grade(answers, GOLD_QUESTIONS)

        report = _build_report(
            cmd,
            sparse_dir,
            run_meta,
            parse_error,
            raw_answers,
            report_grade,
            is_real_output,
            final_message,
            landing,
        )
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    finally:
        _cleanup_run_byproducts(
            sparse_dir,
            repo_root,
            preexisting_git,
            preexisting_claude_md,
            preexisting_repo_byproducts,
        )

    # --- GREEN assertions: report exists, produced by a real (non-canned) run,
    #     and no bundle leaked into the public repo's version control. ---
    assert REPORT_PATH.exists()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    leaked = [
        line
        for line in status.splitlines()
        if "-analytics/" in line or ".dbt-wiki/" in line
    ]
    assert not leaked, f"pack bundle / .dbt-wiki leaked into version control: {leaked}"
    assert is_real_output, (
        "run did not produce genuine model output (empty or canned transcript). "
        f"returncode={run_meta.get('returncode')}, stderr_tail={run_meta.get('stderr_tail')!r}"
    )
