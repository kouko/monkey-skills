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
import shutil
import subprocess
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


# --- sandboxDir per-segment allow-list (whole-branch-review fix) ------------

def test_sandbox_dir_segment_allow_list_present():
    text = _text()
    # sandboxDir is interpolated into the SAME grading-courier Bash string as
    # runLabel (composes artifactPath/gradeTxtPath) — a leading-'/' check
    # alone lets values like "/tmp/x;evil" through. It must be validated
    # per path segment against the same allow-list pattern reused from the
    # runLabel guard, not just checked for a leading '/'.
    assert text.count("RUN_LABEL_ALLOWED_PATTERN.test(") >= 2, (
        "sandboxDir segments must be validated against RUN_LABEL_ALLOWED_PATTERN "
        "(reused from the runLabel guard) — expected a second .test( call "
        "beyond the existing runLabel one"
    )
    assert re.search(r"sandboxDir\.split\(", text), (
        "sandboxDir must be split into path segments for per-segment validation"
    )
    assert "segment" in text.lower(), (
        "error message should name the offending segment/value, mirroring the "
        "runLabel guard's style"
    )


# --- stage-throw guard: a stage that THROWS must degrade to a failed row ---
# (2026-07-11 fix — brief docs/loom/specs/2026-07-11-replay-matrix-stage-guard.md)
#
# Observed in the committed calibration baseline: in 2/3 real matrix runs the
# grading courier failed schema-forced output and the stage THREW. The
# existing `if (!g)` null-guard only covers `agent()` RESOLVING to null, not
# the stage throwing — an uncaught throw let `pipeline()` drop that seed's
# row to null entirely (silently corrupting the pass table). Both stage
# bodies (Replay, Grade) must wrap their logic in try/catch and degrade to a
# failed row on catch, mirroring the existing null-guards' row shape.

def test_stage_throw_guard_present_in_both_stages():
    text = _text()
    # The args guard already has one try/catch (JSON.parse of a string
    # args payload) — the fix adds one more try and one more catch (e),
    # one per pipeline stage (Replay, Grade), for >=3 total each.
    assert text.count("try {") >= 3, (
        "expected the pre-existing args-guard try plus one try each in the "
        "Replay and Grade stage bodies (>=3 total 'try {' occurrences)"
    )
    assert text.count("catch (e)") >= 3, (
        "expected the pre-existing args-guard catch plus one catch each in "
        "the Replay and Grade stage bodies (>=3 total 'catch (e)' occurrences)"
    )


def test_stage_throw_guard_error_message_literals():
    text = _text()
    assert "replay: stage error — " in text, (
        "Replay stage's catch must produce a degraded row with a "
        "'replay: stage error — <message>' miss, mirroring the existing "
        "artifactPath-missing guard's row shape"
    )
    assert "grade: stage error — " in text, (
        "Grade stage's catch must produce a degraded row with a "
        "'grade: stage error — <message>' miss"
    )


def test_existing_null_guards_still_present_untouched():
    # The fix adds catches for THROWN stage errors — it must not remove or
    # rewrite the pre-existing guards for `agent()` RESOLVING to null/no
    # artifact.
    text = _text()
    assert "replay: no artifact produced" in text
    assert "grade: courier produced no result" in text


# --- Task 2 (plan 2026-07-12-principles-mechanical-seed-gate.md): replay
# prompt gains an inventory-authoring step (Write-only, before drafting),
# and a self-check courier stage runs check_seed_traceability.py against
# that inventory, riding the same per-seed row as ADDITIVE telemetry only
# — the Grade stage's own oracle-based `pass` computation stays untouched.

def _extract_agent_prompt(text: str, schema_name: str) -> str:
    """Extract the template-literal prompt text of the `agent(...)` call
    whose options object names `schema: <schema_name>` — mirrors
    test_improve_loop_workflow.py's fixer-prompt extraction, but bounds the
    schema search to each call's own span (up to the NEXT `agent(`
    occurrence, or EOF): with multiple agent() calls now in this file, an
    unbounded lazy scan can walk PAST one call's closing paren and match a
    LATER call's schema name, misattributing that later call's schema to
    an earlier call's prompt text."""
    starts = [m.start() for m in re.finditer(r"agent\(", text)]
    assert starts, "no agent() calls found"
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        chunk = text[start:end]
        prompt_m = re.match(r"agent\(\s*`(.*?)`\s*,", chunk, re.DOTALL)
        if prompt_m and re.search(r"schema:\s*" + re.escape(schema_name) + r"\b", chunk):
            return prompt_m.group(1)
    raise AssertionError(f"agent() call with schema: {schema_name} not found")


def test_inventory_step_and_selfcheck_courier_present():
    text = _text()

    # --- inventory step lives in the REPLAY prompt, BEFORE drafting -----
    replay_prompt = _extract_agent_prompt(text, "REPLAY_SCHEMA")
    assert "named_anchors:" in replay_prompt
    assert "deferred_items:" in replay_prompt
    # never-negative warning: the checker's third key means "must be
    # absent" — using it in a seed-extracted inventory would be wrong.
    assert re.search(r"NEVER[^\n]*negative:", replay_prompt), (
        "replay prompt must explicitly warn never to use a `negative:` key "
        "in the inventory"
    )
    assert ";`-separated" in replay_prompt or "list of exact-match tokens" in replay_prompt
    assert "none in this seed" in replay_prompt
    assert "${inventoryPath}" in replay_prompt
    assert "${seed.id}-inventory.md" in text
    assert re.search(r"BEFORE drafting", replay_prompt), (
        "inventory step must run before the artifact is drafted"
    )
    # replay agent stays Write-only — still forbidden from running scripts.
    assert (
        "Do NOT run the validator or the traceability checker yourself"
        in replay_prompt
    )

    # --- self-check courier: invokes ONLY the checker (never the validator) ---
    selfcheck_prompt = _extract_agent_prompt(text, "SELF_CHECK_SCHEMA")
    assert "check_seed_traceability.py" in selfcheck_prompt
    assert "validate_principles_output.py" not in selfcheck_prompt
    assert "exitCode" in text
    assert "missLines" in text

    # --- per-seed row gains ADDITIVE fields; Grade's oracle verdict intact ---
    assert text.count("selfCheckExit") >= 2
    assert text.count("selfCheckMisses") >= 2
    assert re.search(r"validatorExit\s*===\s*0", text), (
        "Grade stage's pass computation must stay validatorExit===0 && "
        "checkerExit===0 — self-check fields must never feed it"
    )
    assert re.search(r"checkerExit\s*===\s*0", text)

    # --- oracle isolation: neither NEW prompt may name the seed-corpus dir
    # or the word "oracle" (existing Grade prompt legitimately does, via
    # `seed.oracle`, and is exempt — only the two NEW prompts are pinned) ---
    for prompt in (replay_prompt, selfcheck_prompt):
        assert "2026-07-10-principles-flow-seed-corpus" not in prompt
        assert "oracle" not in prompt.lower()

    # --- dry-parse still passes ---
    if shutil.which("node"):
        result = subprocess.run(
            ["node", "--check", str(WORKFLOW)], capture_output=True, text=True
        )
        assert result.returncode == 0, f"node --check failed: {result.stderr}"
