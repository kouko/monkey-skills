"""Static-assertion tests for the L1 principles replay-matrix Workflow script
(`.claude/workflows/principles-replay-matrix.js`, plan Task 4 / brief §Level 1,
docs/loom/specs/2026-07-10-principles-replay-loop.md).

Workflow scripts run inside Claude Code's Workflow-tool sandbox (ambient
runtime globals `agent`/`phase`/`pipeline`/`log`/`args` injected at run
time — see `.claude/workflows/code-toolkit-sweep.js` and
`loom-pipeline/scripts/driver_10_guard.js` for the only other in-repo
evidence of this contract, plus the in-context Workflow tool schema
captured 2026-07-10). They are not Python-importable and this suite
never executes the file — every assertion here is a STATIC check on the
committed .js TEXT: the meta block, the 6 committed seed pairs, and the
grade-stage's deterministic verdict inputs (validator + traceability
checker only — no LLM opinion in the verdict path), plus the Workflow
runtime's determinism constraint (no `Date.now()`/`Math.random()` — a
Workflow run can be paused and resumed from a journal, and either call
would desync a resumed run from what was journaled).

Stdlib only; no fixtures/ subdir (flat-folder repo convention).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".claude" / "workflows" / "principles-replay-matrix.js"

SEED_CORPUS_DIR = "docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus"
COLD_OPERATOR_SEED = (
    "docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/seed.md"
)


def _text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


# --- the RED test (fails until the .js file exists) -------------------------

def test_meta_block_and_deterministic_grade_stage():
    text = _text()

    # meta block: pure literal, expected name, both phase titles.
    assert "export const meta = {" in text
    assert "name: 'principles-replay-matrix'" in text
    assert "title: 'Replay'" in text
    assert "title: 'Grade'" in text

    # Replay stage dispatches on haiku.
    assert "model: 'haiku'" in text

    # Workflow-runtime determinism constraint: no non-deterministic calls
    # anywhere (a resumed run would desync from its journal otherwise).
    assert "Date.now(" not in text
    assert "Math.random(" not in text


# --- all 6 committed seed pairs present --------------------------------------

def test_all_six_seed_pairs_present():
    text = _text()
    # The seed-corpus directory is a single DRY constant the per-seed entries
    # interpolate into (`${SEED_CORPUS_DIR}/seedN-input.md`), so the literal
    # directory string appears once and each seedN filename appears per-seed.
    assert SEED_CORPUS_DIR in text, "seed-corpus directory constant missing"
    for n in range(1, 6):
        assert f"seed{n}-input.md" in text, f"seed{n} input filename missing"
        assert f"seed{n}-oracle.md" in text, f"seed{n} oracle filename missing"
    # cold-operator: the SAME file is both input and oracle (a living doc,
    # not a synthetic pair) — its full path constant is assigned once and
    # then referenced at least twice (once per pipeline field).
    assert COLD_OPERATOR_SEED in text
    assert text.count("COLD_OPERATOR_SEED") >= 2, (
        "cold-operator seed constant must be referenced at least twice "
        "(once as input, once as oracle)"
    )


# --- grade stage is a mechanical courier: ONLY the two scripts -------------

def test_grade_stage_names_only_the_two_verdict_scripts():
    text = _text()
    assert "validate_principles_output.py" in text
    assert "check_seed_traceability.py" in text

    # Every `python3 ...py` invocation in the file must be one of exactly
    # the two verdict scripts — no other script may act as a verdict input.
    py_calls = re.findall(r"python3\s+\S+\.py", text)
    assert py_calls, "expected at least one python3 invocation (the grade stage)"
    for call in py_calls:
        assert (
            "validate_principles_output.py" in call
            or "check_seed_traceability.py" in call
        ), f"unexpected python invocation as a verdict source: {call!r}"

    # The verdict itself must be computed from the two exit codes, not an
    # LLM self-report — the script-side pass expression references both.
    assert "validatorExit" in text
    assert "checkerExit" in text
    assert re.search(r"validatorExit\s*===\s*0", text), (
        "expected the script to compute pass from validatorExit === 0"
    )
    assert re.search(r"checkerExit\s*===\s*0", text), (
        "expected the script to compute pass from checkerExit === 0"
    )


# --- plain JavaScript, no TypeScript syntax ---------------------------------

def test_no_typescript_syntax():
    text = _text()
    assert "interface " not in text
    assert ": Array<" not in text
    assert "as unknown as" not in text
    assert "import type" not in text


# --- grade stage guards a null courier result (round-2 fix) -----------------

def test_grade_courier_null_guard_present():
    text = _text()
    assert "courier produced no result" in text, (
        "grade stage must guard against agent() returning null/skipped for "
        "the grading courier — mirroring the existing Replay-stage guard"
    )


# --- runLabel path-segment allow-list (round-2 fix) -------------------------

def test_run_label_allow_list_present():
    text = _text()
    assert "^[A-Za-z0-9._-]+$" in text, (
        "runLabel is interpolated as a path segment and into courier Bash "
        "instructions — it must be validated against an allow-list pattern "
        "mirroring driver_10_guard.js's changeId guard"
    )
