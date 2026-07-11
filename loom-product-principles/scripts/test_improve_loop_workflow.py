"""Static-assertion tests for the L3 principles-improve-loop Workflow script
(`.claude/workflows/principles-improve-loop.js`, plan Task 3,
docs/loom/plans/2026-07-11-principles-replay-l3-loop.md, brief §Smallest End
State items 1-2, docs/loom/specs/2026-07-11-principles-replay-l3-loop.md).

Mirrors test_replay_matrix_workflow.py's approach: this suite never
EXECUTES the Workflow script (ambient runtime globals `agent`/`phase`/
`pipeline`/`workflow`/`log`/`args` only exist inside Claude Code's Workflow
sandbox) — assertions are regex/marker checks on the committed .js TEXT,
plus one dry-parse check.

DRY-PARSE CHOICE: test_replay_matrix_workflow.py has no parse-check test to
reuse (grepped — none present), so one is added here per the plan Task 3
acceptance criterion. `node --check <file>` run DIRECTLY (no wrap) on the
sibling .claude/workflows/principles-replay-matrix.js — which shares this
file's `export const meta = {...}` + top-level `await` + top-level `return`
shape — was confirmed live (2026-07-11) to exit 0: Node auto-detects the
file as a module from the `export` token, and its CJS-compatible top-level
`return` handling does not trip `--check` the way `node --input-type=module`
via stdin does. This file has the same shape, so the same direct check
applies (no loom-pipeline-style function-wrap needed here).

Stdlib only; no fixtures/ subdir (flat-folder repo convention).
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".claude" / "workflows" / "principles-improve-loop.js"


def _text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_meta_seed_split_and_guards_present():
    assert WORKFLOW.exists(), f"workflow script missing: {WORKFLOW}"
    text = _text()

    # --- meta literal, expected name ---
    assert "export const meta = {" in text
    assert "name: 'principles-improve-loop'" in text

    # --- runLabel + sandboxDir path-arg allow-list (mirrors matrix :57-97) ---
    assert "^[A-Za-z0-9._-]+$" in text
    assert "runArgs.runLabel" in text
    assert "runArgs.sandboxDir" in text
    assert "sandboxDir.split(" in text, "path arg must be validated per segment"

    # --- maxRounds: optional integer, allow-listed to 1-3, default 3 ---
    assert "runArgs.maxRounds" in text
    assert "[1, 2, 3]" in text, "maxRounds must be allow-listed (not range-compared)"
    assert "let maxRounds = 3" in text, "default value 3 must be explicit"

    # --- seed split: HELD_OUT members excluded from VISIBLE by construction ---
    assert "HELD_OUT_SEED_IDS" in text
    assert "'cold-operator'" in text
    assert "'seed5'" in text
    assert "VISIBLE_SEED_IDS" in text
    # exclusion-derived: VISIBLE comes from .filter() over the full corpus,
    # never an independently hardcoded 4-element array that could drift.
    assert re.search(r"VISIBLE_SEED_IDS\s*=\s*ALL_SEED_IDS\.filter\(", text), (
        "VISIBLE_SEED_IDS must be derived by EXCLUSION (.filter over "
        "ALL_SEED_IDS), never an independent hardcoded list"
    )
    assert "['seed1', 'seed2', 'seed3', 'seed4']" not in text, (
        "VISIBLE must not also exist as an independently hardcoded literal "
        "that could drift out of sync with HELD_OUT_SEED_IDS"
    )

    # --- Baseline phase: nests the matrix by name, x2 runs, aggregated ---
    assert "workflow('principles-replay-matrix'" in text
    assert "BASELINE_RUN_COUNT = 2" in text, "x2-run loop marker"
    assert "bySeed" in text, "aggregation must be per-seed, never a single scalar"

    # --- guard obligations (workflow-agent-results-and-courier-args-need-guards.md) ---
    # (1) every nested-workflow() result null-guarded before being dereferenced
    assert "if (!result)" in text or "!run || !Array.isArray(run.rows)" in text
    assert "if (!run || !Array.isArray(run.rows))" in text, (
        "aggregation must null-guard EVERY nested-workflow result before "
        "reading its .rows"
    )
    # (2) stage is async with `return await` INSIDE the try (a sync
    # try/catch around a returned promise can't catch its rejection)
    assert "async function runBaselineOnce" in text
    assert "return await workflow(" in text
    assert "catch (e)" in text

    # --- Fix / Verify phases present as stubs (Task 4/5 wire the bodies) ---
    assert "title: 'Fix'" in text
    assert "title: 'Verify'" in text
    assert "stub" in text.lower()


@pytest.mark.skipif(shutil.which("node") is None, reason="node not available")
def test_workflow_file_dry_parses():
    assert WORKFLOW.exists(), f"workflow script missing: {WORKFLOW}"
    result = subprocess.run(
        ["node", "--check", str(WORKFLOW)], capture_output=True, text=True
    )
    assert result.returncode == 0, f"node --check failed: {result.stderr}"
