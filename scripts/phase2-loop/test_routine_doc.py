"""Structural-completeness test for the execution-stage routine doc.

`ROUTINE.md` is a documentation artifact (the checklist a scheduled,
unattended invocation follows), so its RED/GREEN is structural, not
behavioral: this test `Read`s the doc and asserts — via deterministic
substring checks — that every load-bearing safety rail the brief and plan
require is actually present in the prose, and that nothing this
execution-only stage must NOT invoke (brainstorming / SDD authoring) leaked
in as something the routine drives itself.

See docs/loom/specs/2026-07-28-phase2-loop-execution-only.md (brief) and
docs/loom/plans/2026-07-28-phase2-loop-execution-only.md Task 3.
"""

from pathlib import Path

ROUTINE_PATH = Path(__file__).parent / "ROUTINE.md"


def _routine_text() -> str:
    return ROUTINE_PATH.read_text(encoding="utf-8")


def test_routine_doc_covers_required_steps():
    assert ROUTINE_PATH.is_file(), f"{ROUTINE_PATH} does not exist yet"
    content = _routine_text()
    lower = content.lower()

    # (1) kill-switch sentinel, named by its renamed path.
    assert "docs/loom/PHASE2_LOOP_PAUSED" in content

    # (2-3,6,8) all four batch_queue.py subcommands the routine drives,
    # each in a form specific enough that `mark-running` cannot satisfy the
    # `mark` check nor vice-versa.
    assert "batch_queue.py reconcile" in content
    assert "batch_queue.py next" in content
    assert "mark-running" in content
    assert "mark <id> done" in content
    assert "mark <id> failed" in content

    # (7) the earlier-halt precedent, pointed at by path (not restated).
    assert (
        "loom-code/skills/using-loom-code/references/continuous-mode.md"
        in content
    )

    # fail-closed / never-retry discipline on any failure.
    assert "fail closed" in lower
    assert "never retry" in lower

    # (11) never-merge / never-PR / never-touch-main terminal boundary.
    assert "never merge" in lower
    assert "never open a pr" in lower
    assert "never touch" in lower and "main" in lower

    # (10) no version pre-bump — plugin.json / VERSION are off-limits.
    assert "plugin.json" in content
    assert "VERSION" in content

    # the execution/planning split: this stage never authors a queue entry.
    assert "propose_queue_entry" in content

    # This stage only ever dispatches segment 3 / already-frozen work — it
    # must not name brainstorming or the SDD authoring skill as something it
    # invokes itself.
    assert "brainstorming" not in content
    assert "subagent-driven-development" not in content


def test_routine_doc_scope_guard_step_is_executable():
    """Step 4's guard must name a real input source and a real state exit.

    Whole-branch review found Step 4 unexecutable: it called the guard on
    "<picked entry's description>", a field that exists in no dispatch
    payload, no accepted queue-entry shape, and no emitter — so an unattended
    executor had to improvise the one input a fail-closed guard must never
    receive by guess. Its skip path also prescribed no state transition,
    stranding the entry RUNNING with a live worktree.
    """
    content = _routine_text()

    # The guard's input comes from a named callable, not a hand-waved field.
    assert "lookup_backlog_description" in content
    # ...and the phantom field is gone.
    assert "picked entry's description" not in content

    # The skip path transitions queue state instead of stranding it RUNNING.
    assert "force-fail" in content

    # Every helper the routine calls is module-qualified, journal writer
    # included (it was the only unqualified one).
    assert "journal_writer" in content

    # Tooling failure — not just dispatched-item failure — has a defined rule.
    assert "nonzero" in content.lower()
