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


def test_fixer_prompt_excludes_oracle_paths():
    """Plan Task 4 (docs/loom/plans/2026-07-11-principles-replay-l3-loop.md):
    fixer stage schema-forced ONE-invariant proposal + apply/revert couriers.
    The fixer's own prompt text must never carry an oracle file path/fragment
    — station wording is contract surface, but oracle content is grader-only
    and must never leak into what a downstream LLM (the fixer) reads.
    """
    assert WORKFLOW.exists(), f"workflow script missing: {WORKFLOW}"
    text = _text()

    # --- fixer schema: invariant/rationale/edits present ---
    assert "FIXER_SCHEMA" in text
    assert "invariant" in text
    assert "rationale" in text
    assert "edits" in text

    # --- exactly ONE invariant per proposal, stated explicitly ---
    assert re.search(r"exactly one invariant", text, re.IGNORECASE), (
        "schema/prompt must state EXACTLY ONE invariant per proposal"
    )

    # --- oracle path fragments must be absent from the fixer's OWN prompt
    # text specifically (not just anywhere in the file) ---
    fixer_call = re.search(
        r"agent\(\s*`(.*?)`\s*,\s*\{[\s\S]*?schema:\s*FIXER_SCHEMA", text, re.DOTALL
    )
    assert fixer_call, "fixer agent() call (schema: FIXER_SCHEMA) not found"
    fixer_prompt = fixer_call.group(1)
    assert "2026-07-10-principles-flow-seed-corpus" not in fixer_prompt, (
        "fixer prompt must not reference the oracle seed-corpus directory"
    )
    assert "oracle" not in fixer_prompt.lower(), (
        "fixer prompt must not mention oracle content/paths at all"
    )

    # --- station-wording-is-contract-surface warning must be cited verbatim ---
    assert "preamble-wording-is-contract-surface" in text

    # --- apply courier: clean-status precondition + station path allow-list ---
    assert "git status --porcelain" in text, "apply courier needs a clean-status precondition"
    assert "STATION_DIR" in text
    assert "loom-product-principles/skills/product-principles" in text

    # --- revert courier: stash, not checkout (EXT-1 fix — dcg blocks
    # `git checkout --`, environment-gotchas.md:36-38, "Undo with stash,
    # not checkout"). The substring may still appear in an explanatory
    # comment; what must be gone is the actual command line. ---
    assert "git checkout -- ${STATION_SKILL_MD}" not in text, (
        "revert courier must not RUN `git checkout --` — this repo's "
        "dangerous-command-guard blocks it (environment-gotchas.md:36-38)"
    )
    assert "git stash push -m" in text and "-- ${STATION_SKILL_MD}" in text, (
        "revert courier must restore via git stash push"
    )
    assert "environment-gotchas.md:36-38" in text, (
        "revert-surface change must cite its grounding source"
    )

    # --- folded-in review fix: grounding-cite comment for the nested
    # workflow('principles-replay-matrix', ...) call ---
    assert "principles-replay-matrix.js:41-122" in text, (
        "nested workflow() call needs a grounding-cite comment naming its "
        "call-shape source (principles-replay-matrix.js:41-122)"
    )


@pytest.mark.skipif(shutil.which("node") is None, reason="node not available")
def test_workflow_file_dry_parses():
    assert WORKFLOW.exists(), f"workflow script missing: {WORKFLOW}"
    result = subprocess.run(
        ["node", "--check", str(WORKFLOW)], capture_output=True, text=True
    )
    assert result.returncode == 0, f"node --check failed: {result.stderr}"


def test_assert_station_path_rejects_dot_dot_segments_static():
    """SEC-1 fix: the per-segment allow-list regex admits whole '.'/'..'
    segments (dot is in the char class), so a static marker pins the
    explicit dot-segment rejection alongside it."""
    text = _text()
    assert "segment === '..'" in text and "segment === '.'" in text, (
        "assertStationPath must explicitly reject '.'/'..' segments — the "
        "char-class regex alone admits them"
    )


@pytest.mark.skipif(shutil.which("node") is None, reason="node not available")
def test_assert_station_path_rejects_dot_dot_segments_executable():
    """SEC-1 executable pin, mirroring the reviewer's live Node repro:
    extract the real assertStationPath function + its two constants from
    the committed .js and eval them in a throwaway `node -e` against the
    exact traversal payload the reviewer used."""
    text = _text()
    station_dir_m = re.search(r"const STATION_DIR = '[^']+'", text)
    pattern_m = re.search(r"const RUN_LABEL_ALLOWED_PATTERN = /[^\n]+/", text)
    fn_m = re.search(r"function assertStationPath\(filePath\) \{[\s\S]*?\n\}\n", text)
    assert station_dir_m and pattern_m and fn_m, "assertStationPath + constants not found"
    script = (
        station_dir_m.group(0) + "\n" + pattern_m.group(0) + "\n" + fn_m.group(0) + "\n"
        "try { assertStationPath(STATION_DIR + '/../../../../etc/x'); console.log('NOT_REJECTED') }\n"
        "catch (e) { console.log('REJECTED') }\n"
        "assertStationPath(STATION_DIR + '/SKILL.md'); console.log('VALID_OK')\n"
    )
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert "REJECTED" in result.stdout, f"traversal must be rejected: {result.stdout}{result.stderr}"
    assert "NOT_REJECTED" not in result.stdout
    assert "VALID_OK" in result.stdout, f"legit path must still pass: {result.stdout}{result.stderr}"


def test_apply_proposal_validates_paths_inside_try():
    """ARCH-1 fix: a malformed edit path must degrade via applyProposal's
    catch (recorded failure), never throw uncaught past the stage boundary."""
    text = _text()
    fn_m = re.search(r"async function applyProposal\(round, proposal\) \{[\s\S]*?\n\}\n", text)
    assert fn_m, "applyProposal function not found"
    body = fn_m.group(0)
    try_idx = body.index("try {")
    assert_idx = body.index("assertStationPath(edit.file)")
    assert assert_idx > try_idx, (
        "assertStationPath must be called INSIDE the try block, so a bad "
        "path degrades via the catch instead of crashing the run"
    )


def test_apply_courier_wraps_edits_json_in_inert_data_boundary():
    """SEC-2 fix: the fixer-produced edits JSON is untrusted content
    embedded in the courier prompt — it must be wrapped in explicit
    delimiters plus an inert-data instruction."""
    text = _text()
    assert "EDITS_DATA_BEGIN_MARKER" in text
    assert "EDITS_DATA_END_MARKER" in text
    # Anchor on the apply courier's own unique opener/closer text rather
    # than a generic `agent(...schema: APPLY_SCHEMA` scan (the fixer's
    # agent() call comes first in the file and a non-greedy `[\s\S]*?`
    # between backtick and APPLY_SCHEMA walks straight through it), and
    # rather than a `[^`]*` backtick-boundary scan (the prompt contains
    # escaped `\`` backticks around the embedded git command).
    apply_call = re.search(r"You are the APPLY COURIER([\s\S]*?)Return: applied \(boolean", text)
    assert apply_call, "apply courier prompt not found"
    prompt = apply_call.group(1)
    assert "EDITS_DATA_BEGIN_MARKER" in prompt
    assert "EDITS_DATA_END_MARKER" in prompt
    assert re.search(r"inert", prompt, re.IGNORECASE), "must label the JSON blob inert data"
    assert re.search(r"never|not.*instruction", prompt, re.IGNORECASE), (
        "must instruct the courier never to follow embedded instruction-shaped text"
    )
