"""Task 11 — the ONE real, quota-spending end-to-end validation run.

Every other test in this suite is pure/mocked. This one actually spawns a
headless `claude -p` (via the Task 10 `runner.build_command(..., skip_permissions=True)`),
drives it blind through `/dbt-wiki:init` -> `/dbt-wiki:pack` -> answering all 5
gold questions, feeds the answers through the Task 9 grader, and writes an
audit report to `reports/w1-e2e-run.json` (gitignored). Marked `e2e` so the
default `-m "not e2e"` CI run skips it — it must never run unattended.

Containment (governance — `dbt-wiki/skills/pack/SKILL.md` red line: a real pack
bundle must NEVER be committed into this public repo). `init`/`pack` locate the
knowledge base via `git rev-parse --show-toplevel`. Our fixture lives *inside*
this public repo, so an uncontained run would resolve that to the repo root and
scaffold `.dbt-wiki/` (and possibly a `*-analytics/` bundle) into the public
tree. Real dbt-wiki usage is "the dbt project IS the git root", so we make the
fixture its own temporary git root for the run: `.dbt-wiki/`, init's `CLAUDE.md`
stub, and any bundle then land *inside the fixture*, fully contained, and are
removed in teardown. The temporary `.git` is also removed; the agent may still
place the bundle out-of-tree (e.g. `/tmp/<project>-analytics/`) per pack's
"outside the repo" rule, which is governance-compliant. Nothing the run emits is
ever committed.

Trace for the grader's invariant check. `--output-format json` exposes only the
run's FINAL assistant message (its `result` field), not the full multi-turn SQL
transcript. We therefore use that final message text as each answer's `trace`.
The grader's invariant check is a coarse substring/regex scan for a banned
aggregate call (e.g. `AVG(`); against a summary message this is advisory, not
authoritative — a prohibition "failure" may only mean the summary *mentioned*
the banned function. The report records this caveat alongside the raw verdict.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

import grader
import runner

TESTS_DIR = Path(__file__).parent
FIXTURE_DIR = TESTS_DIR / "fixtures" / "l2-harness"
GOLD_QUESTIONS = FIXTURE_DIR / "gold-questions.yml"
REPORT_PATH = TESTS_DIR / "reports" / "w1-e2e-run.json"

# A generous ceiling: the blind agent scaffolds .dbt-wiki/, packages a bundle,
# and answers 5 questions — minutes of real work, not seconds.
RUN_TIMEOUT_SECONDS = 600

# Distinctive text from the Task 10 CANNED transcript (test_runner.py). If the
# real run's result contains this, we did not actually reach a live model.
_CANNED_MARKER = "I ran /dbt-wiki:init then /dbt-wiki:pack, then answered each"


def _repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=TESTS_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip())


def _bundles_in(base: Path) -> list[Path]:
    return sorted(p for p in base.glob("*-analytics") if p.is_dir())


def test_cleanup_preserves_preexisting_repo_root_byproducts(tmp_path):
    """Teardown must not delete a repo-root `.dbt-wiki/` it did not create.

    Whole-branch review: the repo-root sweep was unconditional while the
    fixture-side sweep carefully guarded `.git`/`CLAUDE.md`. Since this repo
    develops the dbt-wiki plugin, a maintainer's real `.dbt-wiki/` (from a
    genuine `dbt-wiki:init`) sat one `-m e2e` invocation away from silent,
    irreversible deletion.
    """
    repo_root = tmp_path / "repo"
    fixture_dir = tmp_path / "fixture"
    fixture_dir.mkdir()

    mine = repo_root / ".dbt-wiki"
    mine.mkdir(parents=True)
    (mine / "index.md").write_text("real knowledge base", encoding="utf-8")
    my_bundle = repo_root / "mine-analytics"
    my_bundle.mkdir()

    preserved = snapshot_repo_root_byproducts(repo_root)

    # ...the run then drops its own bundle at the root.
    run_bundle = repo_root / "fixture-analytics"
    run_bundle.mkdir()

    _cleanup_run_byproducts(fixture_dir, repo_root, False, False, preserved)

    assert mine.is_dir(), "pre-existing .dbt-wiki/ must survive teardown"
    assert (mine / "index.md").read_text(encoding="utf-8") == "real knowledge base"
    assert my_bundle.is_dir(), "pre-existing bundle must survive teardown"
    assert not run_bundle.exists(), "the run's own byproduct must still be removed"


def _parse_run_output(raw_stdout: str) -> tuple[dict, str | None, str, bool]:
    """Extract `(raw_answers, parse_error, final_message, is_real_output)` from
    a real `claude -p --output-format json` run's stdout."""
    try:
        raw_answers = runner.parse_transcript(raw_stdout)
        parse_error = None
    except (ValueError, json.JSONDecodeError) as exc:
        raw_answers = {}
        parse_error = f"{type(exc).__name__}: {exc}"

    # The final assistant message is the trace we hand the grader (see module
    # docstring for why this is advisory for prohibition invariants).
    try:
        final_message = json.loads(raw_stdout).get("result", "") if raw_stdout else ""
    except json.JSONDecodeError:
        final_message = ""

    is_real_output = bool(final_message) and _CANNED_MARKER not in final_message
    return raw_answers, parse_error, final_message, is_real_output


def snapshot_repo_root_byproducts(repo_root: Path) -> set[Path]:
    """Paths at the repo root that a cleanup must NEVER delete.

    Call this BEFORE the run. This repo develops the `dbt-wiki` plugin, so a
    maintainer plausibly has a real `.dbt-wiki/` at the root from a genuine
    `dbt-wiki:init` — deleting it is irreversible and unrelated to the run.
    The fixture side already guards its own `.git`/`CLAUDE.md` this way; this
    extends the same discipline to the repo root.
    """
    return {p for p in [repo_root / ".dbt-wiki", *_bundles_in(repo_root)] if p.exists()}


def _flag_bearing_grade() -> grader.GradeReport:
    """Two value-correct answers that BOTH trip a prohibition invariant.

    The exact shape the advisory rule makes reachable: `passed` ignores flags,
    so `accuracy_pct` reads 100.0 while every answer tripped one.
    """
    return grader.GradeReport(
        results=[
            grader.QuestionResult(
                trap=name,
                value_correct=True,
                expected=1,
                actual=1,
                invariant_failures=["must not take MAX(as_of_date) over all rows"],
            )
            for name in ("amortization", "avg_ratio")
        ]
    )


def test_report_carries_the_advisory_flag_count():
    """The headline report block must not be flag-blind.

    Round-2 review found `invariant_flag_count` defined and documented as the
    human-facing rollup yet emitted by neither builder; round 3 found nothing
    would fail if it were deleted, because both builders are reached only from
    `e2e`-marked tests. This pins it in the default lane instead — the class of
    blindness, not just the instance.
    """
    grade = _flag_bearing_grade()
    report = _build_report(
        cmd=["claude", "-p"],
        fixture_dir=FIXTURE_DIR,
        run_meta={},
        parse_error=None,
        raw_answers={},
        report_grade=grade,
        is_real_output=True,
        final_message="",
        landing={"fixture_bundles": [], "repo_root_bundles": [], "repo_root_dbt_wiki": False},
    )

    assert report["accuracy_pct"] == 100.0, "precondition: the flag-blind shape"
    assert report["invariant_flag_count"] == 2


def _cleanup_run_byproducts(
    fixture_dir: Path,
    repo_root: Path,
    preexisting_git: bool,
    preexisting_claude_md: bool,
    preexisting_repo_byproducts: set[Path] | None = None,
) -> None:
    """Remove every byproduct the run may have written into the fixture, then
    drop the temporary git root. Belt-and-suspenders: also clean any that
    escaped to the repo root — except anything `preexisting_repo_byproducts`
    recorded as already present before the run started."""
    fixture_git = fixture_dir / ".git"
    fixture_claude_md = fixture_dir / "CLAUDE.md"
    preserved = preexisting_repo_byproducts or set()
    for junk in [fixture_dir / ".dbt-wiki", *_bundles_in(fixture_dir)]:
        shutil.rmtree(junk, ignore_errors=True)
    if not preexisting_claude_md:
        fixture_claude_md.unlink(missing_ok=True)
    if not preexisting_git and fixture_git.exists():
        shutil.rmtree(fixture_git, ignore_errors=True)
    for junk in [repo_root / ".dbt-wiki", *_bundles_in(repo_root)]:
        if junk in preserved:
            continue
        shutil.rmtree(junk, ignore_errors=True)


def _build_report(
    cmd: list[str],
    fixture_dir: Path,
    run_meta: dict,
    parse_error: str | None,
    raw_answers: dict,
    report_grade: grader.GradeReport,
    is_real_output: bool,
    final_message: str,
    landing: dict,
) -> dict:
    """Assemble the Task 11 audit report dict written to `REPORT_PATH`."""
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
    return {
        "task": "W1 L2 e2e harness — Task 11 real validation run",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": cmd,
        "cwd": str(fixture_dir),
        "run": run_meta,
        "parse_error": parse_error,
        "raw_answers": raw_answers,
        "results": results,
        "score": report_grade.score,
        "accuracy_pct": round(report_grade.score * 100, 2),
        "passed_count": report_grade.passed_count,
        "total": report_grade.total,
        # Advisory, never folded into `score` — a nonzero count is a prompt to
        # read the traces below, not a failure. Without it the headline block
        # is flag-blind: every answer could trip a prohibition invariant and
        # this summary would still read accuracy_pct 100.0.
        "invariant_flag_count": report_grade.invariant_flag_count,
        "is_real_model_output": is_real_output,
        "final_message_excerpt": final_message[:2000],
        "governance": {
            "note": (
                "pack bundle must NEVER be committed into this public repo "
                "(dbt-wiki/skills/pack/SKILL.md). Fixture given a temporary "
                "git root so init/pack output stays contained + is cleaned up."
            ),
            "landing": landing,
        },
        "trace_caveat": (
            "trace = final assistant message only (--output-format json exposes "
            "no full SQL transcript); prohibition-invariant verdicts are advisory."
        ),
    }


@pytest.mark.e2e
def test_real_end_to_end_run_scores_the_blind_agent():
    # --- RED precondition: the report must not exist before this run. ---
    assert not REPORT_PATH.exists(), (
        f"{REPORT_PATH} already exists — Task 11 is a one-shot real run; "
        "delete the stale report before re-running."
    )

    repo_root = _repo_root()
    questions = yaml.safe_load(GOLD_QUESTIONS.read_text())
    assert questions, "gold-questions.yml is empty — Task 8 fixture missing"

    cmd = runner.build_command(FIXTURE_DIR, questions, skip_permissions=True)

    fixture_git = FIXTURE_DIR / ".git"
    preexisting_git = fixture_git.exists()
    # `init` scaffolds a CLAUDE.md at the git root; track whether the fixture
    # already had one so teardown only removes the one this run created.
    fixture_claude_md = FIXTURE_DIR / "CLAUDE.md"
    preexisting_claude_md = fixture_claude_md.exists()
    # Anything already at the repo root is the maintainer's, not this run's.
    preexisting_repo_byproducts = snapshot_repo_root_byproducts(repo_root)

    landing = {"fixture_bundles": [], "repo_root_bundles": [], "repo_root_dbt_wiki": False}
    run_meta: dict = {}

    try:
        # Contain init/pack output inside the fixture by giving it its own git root.
        if not preexisting_git:
            subprocess.run(["git", "init", "-q"], cwd=FIXTURE_DIR, check=True)

        proc = subprocess.run(
            cmd,
            cwd=FIXTURE_DIR,
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT_SECONDS,
        )
        run_meta = {
            "returncode": proc.returncode,
            "stdout_len": len(proc.stdout),
            "stderr_tail": proc.stderr[-2000:],
        }

        # Record where init/pack actually wrote, for the governance audit,
        # BEFORE any cleanup removes it.
        landing["fixture_bundles"] = [str(p) for p in _bundles_in(FIXTURE_DIR)]
        landing["repo_root_bundles"] = [str(p) for p in _bundles_in(repo_root)]
        landing["repo_root_dbt_wiki"] = (repo_root / ".dbt-wiki").exists()

        # --- Parse the real transcript into {question_id: answer}. ---
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
            FIXTURE_DIR,
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
            FIXTURE_DIR,
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
