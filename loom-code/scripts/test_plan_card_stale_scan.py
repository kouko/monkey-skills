"""Tests for plan_card.py --stale-scan — the all-done-but-never-finished sweep.

Task 1 of docs/loom/plans/2026-08-10-terminal-state-gates.md: every
intermediate stage has a flip duty but the terminal flip was
un-mandated, so merged arcs stranded mid-flight. `--stale-scan
<plans-dir>` lists every plan whose tasks are ALL `done(...)` while its
`Stage:` never reached `finishing` — the exact signature of the two
real victims repaired on 2026-08-10 (all-done at `sdd:wave-1`, all-done
at `review:round-1`), reproduced here as fixtures.

Advisory by design (plan-gate advisory N1): the verb ALWAYS exits 0 —
all-done + review:round-N is a legitimate transient state of a live
parallel arc, and a red exit would teach people to ignore the gate.
The "exit 0 even WHEN candidates exist" assertion below IS that
contract.

False-green discipline: the existence assert comes first; every
subprocess assert pins a positive fact only a real run produces (the
exact candidate line, the `stale-scan: clean` line) — never a bare
exit-code check. Mutation probes (docs/loom/memory/
a-mutation-test-must-run-the-production-assertion.md) mutate the
FIXTURE INPUT and re-invoke the PRODUCTION verb via subprocess —
the stale predicate is never re-implemented beside it.
"""

import subprocess
import sys
from pathlib import Path

PLAN_CARD_SCRIPT = Path(__file__).resolve().parent / "plan_card.py"


def _plan_text(*, stage: str | None, statuses: list[str | None]) -> str:
    """A minimal plan in the writing-plans shape: header lines, one
    `## Task N — <name>` per status, per-task `- Status:` bullets
    (None = old-format task without one), plus a trailing `## Notes`
    section so parsing must stop at section boundaries."""
    lines = ["# Plan: stale-scan fixture", "", "Goal: fixture goal."]
    if stage is not None:
        lines.append(f"Stage: {stage}")
    lines.append("")
    for number, status in enumerate(statuses, start=1):
        lines.append(f"## Task {number} — task {number}")
        lines.append("")
        lines.append("- Description: fixture task body.")
        if status is not None:
            lines.append(f"- Status: {status}")
        lines.append("")
    lines.extend(["## Notes", "", "Fixture notes — never a task.", ""])
    return "\n".join(lines)


VICTIM_SDD = "2026-08-01-victim-sdd.md"
VICTIM_REVIEW = "2026-08-02-victim-review.md"
VICTIM_SDD_LINE = f"{VICTIM_SDD}: stage=sdd:wave-1 (all 2 tasks done)"
VICTIM_REVIEW_LINE = f"{VICTIM_REVIEW}: stage=review:round-1 (all 3 tasks done)"


def _write_victim_fixtures(plans_dir: Path) -> None:
    """Today's two real victim signatures, one finishing-stage all-done
    plan (must NOT be listed), and one old-format plan (silently
    skipped)."""
    plans_dir.mkdir(exist_ok=True)
    (plans_dir / VICTIM_SDD).write_text(
        _plan_text(stage="sdd:wave-1", statuses=["done(abc1234)", "done(def5678)"]),
        encoding="utf-8",
    )
    (plans_dir / VICTIM_REVIEW).write_text(
        _plan_text(
            stage="review:round-1",
            statuses=["done(1111111)", "done(2222222)", "done(3333333)"],
        ),
        encoding="utf-8",
    )
    (plans_dir / "2026-08-03-shipped.md").write_text(
        _plan_text(stage="finishing", statuses=["done(abc1234)"]),
        encoding="utf-8",
    )
    (plans_dir / "2026-07-01-old-format.md").write_text(
        _plan_text(stage="sdd:wave-1", statuses=[None, None]),
        encoding="utf-8",
    )


def _run_scan(plans_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PLAN_CARD_SCRIPT), "--stale-scan", str(plans_dir)],
        capture_output=True,
        text=True,
    )


def test_stale_scan_lists_both_victim_signatures_and_only_them(tmp_path):
    """(1) The two 2026-08-10 victim signatures are each listed with the
    pinned line shape; the finishing-stage plan and the old-format plan
    contribute nothing — stdout is byte-exactly the two candidate lines
    (filename-sorted), stderr silent (old-format skip is SILENT)."""
    assert PLAN_CARD_SCRIPT.is_file(), f"missing script at {PLAN_CARD_SCRIPT}"
    plans_dir = tmp_path / "plans"
    _write_victim_fixtures(plans_dir)

    result = _run_scan(plans_dir)

    assert result.stdout == f"{VICTIM_SDD_LINE}\n{VICTIM_REVIEW_LINE}\n", (
        result.stdout + result.stderr
    )
    assert result.stderr == "", result.stderr
    assert result.returncode == 0, result.stdout + result.stderr


def test_stale_scan_exits_zero_even_when_candidates_exist(tmp_path):
    """(2) The advisory contract (plan-gate advisory N1): candidates
    found is NOT a failure — all-done + review:round-N is a legitimate
    transient state of a live parallel arc. Positive fact first: a
    candidate line IS present, and the exit code is still 0."""
    assert PLAN_CARD_SCRIPT.is_file(), f"missing script at {PLAN_CARD_SCRIPT}"
    plans_dir = tmp_path / "plans"
    _write_victim_fixtures(plans_dir)

    result = _run_scan(plans_dir)

    assert VICTIM_REVIEW_LINE in result.stdout, result.stdout + result.stderr
    assert result.returncode == 0, (
        "advisory contract broken: --stale-scan must exit 0 even when "
        f"candidates exist, got {result.returncode}\n"
        + result.stdout
        + result.stderr
    )


def test_stale_scan_clean_when_no_candidates(tmp_path):
    """(3) A directory holding only a finishing-stage all-done plan and
    an old-format plan yields the single pinned clean line."""
    assert PLAN_CARD_SCRIPT.is_file(), f"missing script at {PLAN_CARD_SCRIPT}"
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir()
    (plans_dir / "2026-08-03-shipped.md").write_text(
        _plan_text(stage="finishing", statuses=["done(abc1234)"]),
        encoding="utf-8",
    )
    (plans_dir / "2026-07-01-old-format.md").write_text(
        _plan_text(stage="sdd:wave-1", statuses=[None]),
        encoding="utf-8",
    )

    result = _run_scan(plans_dir)

    assert result.stdout == "stale-scan: clean\n", result.stdout + result.stderr
    assert result.returncode == 0, result.stdout + result.stderr


def test_stale_scan_degrades_loud_on_unparsable_status_and_continues(tmp_path):
    """(4) A plan WITH Status lines but an unparsable value must not
    crash the scan: it degrades loudly per-file on stderr (naming the
    file), the other candidates still list, and the exit is still 0."""
    assert PLAN_CARD_SCRIPT.is_file(), f"missing script at {PLAN_CARD_SCRIPT}"
    plans_dir = tmp_path / "plans"
    _write_victim_fixtures(plans_dir)
    (plans_dir / "2026-08-04-corrupt.md").write_text(
        _plan_text(stage="sdd:wave-1", statuses=["done(abc1234)", "wat"]),
        encoding="utf-8",
    )

    result = _run_scan(plans_dir)

    assert "2026-08-04-corrupt.md" in result.stderr, (
        result.stdout + result.stderr
    )
    assert VICTIM_SDD_LINE in result.stdout, result.stdout + result.stderr
    assert VICTIM_REVIEW_LINE in result.stdout, result.stdout + result.stderr
    assert "2026-08-04-corrupt.md" not in result.stdout, result.stdout
    assert result.returncode == 0, result.stdout + result.stderr


def test_mutation_stage_flipped_to_finishing_drops_the_line(tmp_path):
    """(5) Mutation probe A, production assertion path: the pre-mutation
    scan lists the victim (positive fact — the absence assert below
    cannot be vacuous); flipping ONLY that fixture's Stage to finishing
    and re-running the PRODUCTION verb drops exactly that line while the
    untouched victim stays listed."""
    assert PLAN_CARD_SCRIPT.is_file(), f"missing script at {PLAN_CARD_SCRIPT}"
    plans_dir = tmp_path / "plans"
    _write_victim_fixtures(plans_dir)
    before = _run_scan(plans_dir)
    assert VICTIM_SDD_LINE in before.stdout, before.stdout + before.stderr

    victim = plans_dir / VICTIM_SDD
    mutated = victim.read_text(encoding="utf-8").replace(
        "Stage: sdd:wave-1", "Stage: finishing", 1
    )
    assert "Stage: finishing" in mutated  # the mutation really landed
    victim.write_text(mutated, encoding="utf-8")

    after = _run_scan(plans_dir)
    assert VICTIM_SDD_LINE not in after.stdout, after.stdout + after.stderr
    assert VICTIM_REVIEW_LINE in after.stdout, after.stdout + after.stderr
    assert after.returncode == 0, after.stdout + after.stderr


def test_mutation_one_task_flipped_to_pending_drops_the_line(tmp_path):
    """(6) Mutation probe B, production assertion path: flipping ONE
    task of an all-done victim back to pending and re-running the
    PRODUCTION verb drops exactly that line — not-all-done is never
    stale, whatever the stage."""
    assert PLAN_CARD_SCRIPT.is_file(), f"missing script at {PLAN_CARD_SCRIPT}"
    plans_dir = tmp_path / "plans"
    _write_victim_fixtures(plans_dir)
    before = _run_scan(plans_dir)
    assert VICTIM_REVIEW_LINE in before.stdout, before.stdout + before.stderr

    victim = plans_dir / VICTIM_REVIEW
    mutated = victim.read_text(encoding="utf-8").replace(
        "- Status: done(2222222)", "- Status: pending", 1
    )
    assert "- Status: pending" in mutated  # the mutation really landed
    victim.write_text(mutated, encoding="utf-8")

    after = _run_scan(plans_dir)
    assert VICTIM_REVIEW_LINE not in after.stdout, after.stdout + after.stderr
    assert VICTIM_SDD_LINE in after.stdout, after.stdout + after.stderr
    assert after.returncode == 0, after.stdout + after.stderr


def test_stale_scan_skips_pre_stage_era_plans_silently(tmp_path):
    """(7) T1 spec-review 🟡: a plan WITH a Status ledger but WITHOUT a
    `Stage:` header — this repo ships six such pre-Stage-era plans —
    is skipped SILENTLY: not listed, and NO stderr line. A plan without
    a Stage header cannot be stage-stale by definition; per-sweep noise
    for known-benign files is the dismissed-gate spiral the advisory
    design forbids."""
    assert PLAN_CARD_SCRIPT.is_file(), f"missing script at {PLAN_CARD_SCRIPT}"
    plans_dir = tmp_path / "plans"
    _write_victim_fixtures(plans_dir)
    pre_stage = _plan_text(stage="sdd:wave-1", statuses=["done(abc1234)"])
    pre_stage = "\n".join(
        line for line in pre_stage.splitlines() if not line.startswith("Stage:")
    ) + "\n"
    assert "- Status:" in pre_stage and "Stage:" not in pre_stage
    (plans_dir / "2026-07-01-pre-stage-era.md").write_text(
        pre_stage, encoding="utf-8"
    )

    result = _run_scan(plans_dir)

    assert "2026-07-01-pre-stage-era.md" not in result.stdout, result.stdout
    assert "2026-07-01-pre-stage-era.md" not in result.stderr, result.stderr
    assert result.stderr == "", result.stderr  # zero degrade noise
    assert VICTIM_SDD_LINE in result.stdout, result.stdout
    assert result.returncode == 0, result.stdout + result.stderr


def test_stale_scan_survives_an_unreadable_file(tmp_path):
    """(8) Whole-branch review 🟡: a single non-UTF-8 `.md` must not
    crash the sweep — it degrades to one stderr line and every other
    candidate still lists, exit stays 0. Pre-fix behavior was a
    UnicodeDecodeError traceback, empty stdout, exit 1: the exact
    'one corrupt plan hides the rest' outcome the posture forbids."""
    assert PLAN_CARD_SCRIPT.is_file(), f"missing script at {PLAN_CARD_SCRIPT}"
    plans_dir = tmp_path / "plans"
    _write_victim_fixtures(plans_dir)
    (plans_dir / "2026-08-01-binary-garbage.md").write_bytes(
        b"\xff\xfe\x00garbage not utf-8\x9c"
    )

    result = _run_scan(plans_dir)

    assert "2026-08-01-binary-garbage.md" in result.stderr, result.stderr
    assert VICTIM_SDD_LINE in result.stdout, result.stdout + result.stderr
    assert VICTIM_REVIEW_LINE in result.stdout, result.stdout + result.stderr
    assert result.returncode == 0, result.stdout + result.stderr
