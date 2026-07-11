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
    # (shape pins for selfCheckExit/selfCheckMisses live in the dedicated
    # test below — count-only pins here would pass even on two accidental
    # occurrences, per docs/loom/memory/count-only-regression-pins-false-confidence.md)
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


# --- Task 2 round-2 security fix: the self-check courier call site must
# receive the LOCALLY-computed, allow-listed `artifactPath` const, never
# `replayResult.artifactPath` (the REPLAY agent's own schema-echoed,
# unconstrained string) — the latter flows straight into the courier's
# Bash instruction text (docs/loom/plans/2026-07-12-principles-mechanical-
# seed-gate.md round-2 review finding).

def test_selfcheck_courier_receives_local_artifact_path_not_agent_echo():
    text = _text()
    assert "runSelfCheckCourier(seed, artifactPath, inventoryPath)" in text, (
        "self-check courier call site must pass the local artifactPath const"
    )
    assert "runSelfCheckCourier(seed, replayResult.artifactPath" not in text, (
        "self-check courier must never receive the agent's schema-echoed "
        "artifactPath field"
    )


def test_selfcheck_courier_executable_probe_marker_path_lands_verbatim():
    """Executable pin mirroring test_improve_loop_workflow.py's SEC-1
    precedent: extract the real runSelfCheckCourier function from the
    committed .js and eval it in a throwaway `node -e` with stubbed
    agent()/log() globals, proving whatever path is passed as the 2nd
    argument lands verbatim in the Bash instruction text the courier
    receives — independent of the static pin above (which proves the call
    SITE passes the right argument; this proves the function's own
    plumbing doesn't mangle or drop it)."""
    if shutil.which("node"):
        text = _text()
        fn_m = re.search(
            r"async function runSelfCheckCourier\(seed, artifactPath, inventoryPath\) \{[\s\S]*?\n\}\n",
            text,
        )
        assert fn_m, "runSelfCheckCourier function not found"
        script = (
            "const ROOT = '/x';\n"
            "const SELF_CHECK_SCHEMA = {};\n"
            "let capturedPrompt = null;\n"
            "async function agent(prompt, opts) { capturedPrompt = prompt; return { exitCode: 0, missLines: [] } }\n"
            "function log() {}\n"
            + fn_m.group(0)
            + "(async () => {\n"
            "  const marker = '/MARKER/seedX/PRINCIPLES.md';\n"
            "  await runSelfCheckCourier({ id: 'seedX' }, marker, '/tmp/inv.md');\n"
            "  console.log(capturedPrompt.includes(marker) ? 'MARKER_LANDED' : 'MARKER_MISSING');\n"
            "})();\n"
        )
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
        assert "MARKER_LANDED" in result.stdout, f"{result.stdout}{result.stderr}"


# --- 🟢 fix: count-only pins (`text.count("selfCheckExit") >= 2`) pass even
# if both occurrences are accidental (e.g. two comments, or one row
# duplicated) — per docs/loom/memory/count-only-regression-pins-false-
# confidence.md. Pin the field to two DISTINCT, load-bearing row shapes:
# a degraded row and the success row, each anchored by unique surrounding
# context so the assertion can only pass if that SPECIFIC site carries it.

def test_selfcheck_fields_present_in_degraded_and_success_rows():
    text = _text()

    # degraded row: Replay stage's "no artifact produced" branch must still
    # carry selfCheckExit: null / selfCheckMisses: [] right after its other
    # null fields — not just present somewhere in the file.
    degraded_row = re.search(
        r"misses:\s*\['replay: no artifact produced'\],\s*"
        r"artifactPath:\s*null,\s*"
        r"gradeTxtPath:\s*null,\s*"
        r"selfCheckExit:\s*null,\s*"
        r"selfCheckMisses:\s*\[\],",
        text,
    )
    assert degraded_row, (
        "the Replay stage's 'no artifact produced' degraded row must carry "
        "selfCheckExit: null / selfCheckMisses: [] immediately after its "
        "other null fields"
    )

    # success row: computed from the self-check courier's actual result,
    # not a hardcoded placeholder. (Task 3 extracted these from inline
    # return-object ternaries into named consts, so the fix-round gate
    # below can branch on `selfCheckExit` — same dynamic-computation
    # semantics, relocated.)
    success_row = re.search(
        r"const selfCheckExit = selfCheck\s*&&\s*typeof\s*selfCheck\.exitCode\s*===\s*'number'\s*"
        r"\?\s*selfCheck\.exitCode\s*:\s*null\s*\n"
        r"\s*const selfCheckMisses = selfCheck\s*&&\s*Array\.isArray\(selfCheck\.missLines\)\s*"
        r"\?\s*selfCheck\.missLines\s*:\s*\[\]",
        text,
    )
    assert success_row, (
        "the Replay stage's success path must compute selfCheckExit/"
        "selfCheckMisses from the actual self-check courier result "
        "(selfCheck.exitCode / selfCheck.missLines), not a placeholder"
    )

    # Grade stage must read the SAME fields back off `replay` (carrying
    # Replay-stage telemetry through), anchored on its distinct
    # extraction-from-replay context.
    carry_through = re.search(
        r"const selfCheckExit = replay && typeof replay\.selfCheckExit === 'number' "
        r"\? replay\.selfCheckExit : null\s*\n"
        r"\s*const selfCheckMisses = replay && Array\.isArray\(replay\.selfCheckMisses\) "
        r"\? replay\.selfCheckMisses : \[\]",
        text,
    )
    assert carry_through, (
        "the Grade stage must read selfCheckExit/selfCheckMisses back off "
        "its `replay` argument (carrying Replay-stage telemetry through), "
        "not recompute or drop it"
    )


# --- Task 3 (plan 2026-07-12-principles-mechanical-seed-gate.md): on a hard
# self-check MISS (exitCode === 1) the pipeline dispatches ONE fresh fix
# agent (additive-patch, Write/Edit only) then re-runs the self-check
# courier ONCE (fix bound = 1, Decision Log 2) — never a loop. The row
# gains additive telemetry selfCheckFixed/selfCheckExitAfterFix; the Grade
# stage's own oracle-based `pass` computation stays untouched.

def test_fix_round_wired_and_bounded():
    text = _text()

    # --- fix agent dispatched ONLY on self-check exit 1 (conditional marker) ---
    gate_m = re.search(
        r"if \(selfCheckExit === 1\) \{([\s\S]*?)\n      \}\n",
        text,
    )
    assert gate_m, (
        "fix round must be gated on `if (selfCheckExit === 1)` — never "
        "dispatched when self-check already passed (exit 0) or degraded "
        "(courier threw, exit null)"
    )
    gate_body = gate_m.group(1)
    assert "runFixAgent(" in gate_body, (
        "the fix agent must be dispatched from inside the exit-1 gate body"
    )

    # --- exactly ONE re-check: no loop construct wraps the fix leg -------
    # the file's ONLY pre-existing loop is the args-guard's sandboxDir
    # per-segment validation (unrelated to the Replay pipeline stage) — the
    # fix round must be a single conditional re-check, never a loop.
    assert text.count("for (") == 1, (
        "expected exactly the one pre-existing 'for (' (sandboxDir segment "
        "guard) — a fix-round loop would add a second one, breaking the "
        "fix-bound-1 invariant (plan Decision Log 2)"
    )
    assert "while (" not in text
    assert "runSelfCheckCourier(" in gate_body, (
        "the bounded re-check must call runSelfCheckCourier again, inside "
        "the SAME exit-1 gate (never a separate loop construct)"
    )
    # runSelfCheckCourier: one function definition + exactly two call sites
    # (the initial check + the one bounded re-check).
    assert text.count("runSelfCheckCourier(") == 3

    # --- telemetry fields pinned at their construction sites --------------
    assert re.search(r"let selfCheckFixed = 0\b", text), (
        "selfCheckFixed must default to 0 (rows whose self-check passed "
        "first time never enter the fix branch)"
    )
    assert re.search(r"let selfCheckExitAfterFix = null\b", text), (
        "selfCheckExitAfterFix must default to null (rows whose self-check "
        "passed first time never run a re-check)"
    )
    return_row = re.search(
        r"return \{\s*\.\.\.replayResult,[\s\S]{0,400}?artifactPath,\s*selfCheckExit,\s*"
        r"selfCheckMisses,\s*selfCheckFixed,\s*selfCheckExitAfterFix,?\s*\}",
        text,
    )
    assert return_row, (
        "the Replay stage's success-path return row must carry "
        "selfCheckFixed/selfCheckExitAfterFix alongside the existing "
        "selfCheckExit/selfCheckMisses fields"
    )
    # Grade stage must carry both new fields through too (mirroring its
    # existing selfCheckExit/selfCheckMisses carry-through), or the fields
    # would be computed and immediately dropped before reaching the final
    # per-seed row.
    # T3 round-2 correctness fix: selfCheckFixed can now be an explicit
    # `null` (unknown — re-check courier errored), distinct from its `0`
    # default — the Grade-stage carry-through must preserve that null
    # rather than coercing it back to 0 via a bare `typeof ... === 'number'`
    # check (which would silently undo the fix one stage later).
    grade_carry = re.search(
        r"const selfCheckFixed = replay && \(typeof replay\.selfCheckFixed === 'number' "
        r"\|\| replay\.selfCheckFixed === null\) \? replay\.selfCheckFixed : 0\s*\n"
        r"\s*const selfCheckExitAfterFix = replay && typeof replay\.selfCheckExitAfterFix === 'number' "
        r"\? replay\.selfCheckExitAfterFix : null",
        text,
    )
    assert grade_carry, (
        "the Grade stage must read selfCheckFixed/selfCheckExitAfterFix "
        "back off its `replay` argument, preserving an explicit `null` "
        "selfCheckFixed rather than coercing it to 0, same carry-through "
        "discipline as the existing selfCheckExit/selfCheckMisses fields"
    )
    assert text.count("selfCheckFixed,") >= 4, (
        "selfCheckFixed must ride all Grade-stage return rows (hard-miss, "
        "courier-null, success, stage-error), not just the success path"
    )
    assert text.count("selfCheckExitAfterFix,") >= 4

    # --- null-guard on the fix agent's own result --------------------------
    null_guard = re.search(r"if \(!fixResult \|\| !fixResult\.edited\) \{([\s\S]*?)\n\s*\}", text)
    assert null_guard, "fix agent result must be null-guarded (fixResult can be null or edited:false)"
    assert "selfCheckExitAfterFix = 1" in null_guard.group(1), (
        "a null/failed fix agent result must degrade selfCheckExitAfterFix "
        "to 1 (still-a-miss), never crash the stage"
    )

    # --- provenance: fix agent + re-check receive LOCAL path constants -----
    assert "runFixAgent(seed, artifactPath, selfCheckMisses)" in text, (
        "fix agent call site must pass the local, allow-listed artifactPath "
        "const — never replayResult.artifactPath (the agent's own echo)"
    )
    assert "runFixAgent(seed, replayResult.artifactPath" not in text
    assert re.search(r"runSelfCheckCourier\(seed, artifactPath, inventoryPath\)", gate_body), (
        "the bounded re-check must reuse the SAME local artifactPath/"
        "inventoryPath constants as the initial self-check, never an "
        "agent-echoed path"
    )

    # --- fix prompt: oracle-exclusion + inert-data boundary + wording warning ---
    fix_prompt = _extract_agent_prompt(text, "FIX_SCHEMA")
    assert "2026-07-10-principles-flow-seed-corpus" not in fix_prompt
    assert "oracle" not in fix_prompt.lower()
    assert "MISS_LINES_DATA_BEGIN_MARKER" in text
    assert "MISS_LINES_DATA_END_MARKER" in text
    assert "MISS_LINES_DATA_BEGIN_MARKER" in fix_prompt
    assert "MISS_LINES_DATA_END_MARKER" in fix_prompt
    assert re.search(r"inert", fix_prompt, re.IGNORECASE), "must label the miss-lines blob inert data"
    assert re.search(r"never|not.*instruction", fix_prompt, re.IGNORECASE), (
        "must instruct the fix agent never to follow embedded instruction-shaped text"
    )
    assert "preamble-wording-is-contract-surface" in fix_prompt, (
        "fix prompt must carry the wording-is-contract-surface warning "
        "(docs/loom/memory/preamble-wording-is-contract-surface.md)"
    )
    assert re.search(r"additive", fix_prompt, re.IGNORECASE), (
        "fix prompt must state the additive-only patch rule"
    )
    assert "(agent-decided)" in fix_prompt
    assert "## Anchors" in fix_prompt
    assert "## Open Questions" in fix_prompt
    assert "re-trigger" in fix_prompt
    assert "Write" in fix_prompt and "Edit" in fix_prompt
    assert re.search(r"not run bash|no bash|do not run any bash|never.*bash", fix_prompt, re.IGNORECASE), (
        "fix agent must be explicitly forbidden from using Bash (Write/Edit "
        "tools only per plan Task 3 step 2)"
    )

    # --- dry-parse still passes ---------------------------------------------
    if shutil.which("node"):
        result = subprocess.run(
            ["node", "--check", str(WORKFLOW)], capture_output=True, text=True
        )
        assert result.returncode == 0, f"node --check failed: {result.stderr}"


# --- T3 round-2 security fix (🔴): dot-segment traversal in the args guard's
# own per-segment allow-list. RUN_LABEL_ALLOWED_PATTERN's char class includes
# '.', so a segment that is exactly '.' or '..' passes the regex test even
# though it is a path-traversal segment — a reviewer live-probe demonstrated
# `/tmp/sandbox/../../etc` as an ACCEPTED sandboxDir pre-fix. Backports the
# sibling guard in principles-improve-loop.js's assertStationPath :213-218
# (same char-class hole, already fixed there) to BOTH runLabel and the
# sandboxDir per-segment loop, plus a NEW structural check inside
# runFixAgent (the 🟡 architecture fix below).

def test_sandbox_dir_dot_segment_rejection_present():
    text = _text()
    # Two distinct sites must reject '.'/'..' explicitly: the sandboxDir
    # args-guard loop AND the runFixAgent structural scope-check (below) —
    # a count-only pin here is intentional BECAUSE both sites independently
    # matter (defense in depth, not just one shared helper).
    assert text.count("segment === '..'") >= 2, (
        "expected '..' rejection at both the sandboxDir args-guard loop and "
        "the runFixAgent structural scope-check"
    )
    assert text.count("segment === '.'") >= 2, (
        "expected '.' rejection at both the sandboxDir args-guard loop and "
        "the runFixAgent structural scope-check"
    )


def test_run_label_dot_segment_rejected():
    text = _text()
    assert "runArgs.runLabel === '.'" in text, (
        "runLabel becomes a whole path segment (sandboxDir/runLabel/seed.id/...) "
        "— a runLabel of exactly '.' or '..' passes the char-class regex and "
        "must be explicitly rejected"
    )
    assert "runArgs.runLabel === '..'" in text


def _extract_args_guard_block(text: str) -> str:
    """Extract the top-level args-guard statements (from `let runArgs = args`
    through the sandboxDir per-segment loop) so they can be eval'd standalone
    in a throwaway `node -e` with a synthetic `args` — mirrors this file's
    existing executable-pin precedent
    (test_selfcheck_courier_executable_probe_marker_path_lands_verbatim),
    applied to the top-level guard instead of an async function."""
    start_marker = "let runArgs = args"
    end_marker = "let seedPairs = DEFAULT_SEEDS"
    start = text.index(start_marker)
    end = text.index(end_marker)
    assert start < end, "expected the args-guard block to precede the seeds block"
    return text[start:end]


def test_traversal_probe_rejects_dot_dot_sandbox_dir_accepts_clean_path():
    """Executable pin mirroring the reviewer's live probe (T3 round-2
    security finding): a sandboxDir containing a '..' segment
    (`/tmp/sandbox/../../etc`, the reviewer's exact repro) must be REJECTED
    by the args guard, while a clean absolute sandboxDir is ACCEPTED.
    Evaluates the REAL args-guard block extracted from the committed .js,
    standalone in node — independent of the static literal pins above."""
    if not shutil.which("node"):
        return
    text = _text()
    guard_block = _extract_args_guard_block(text)

    def run_probe(sandbox_dir: str) -> str:
        script = (
            "function log() {}\n"
            f"const args = {{ runLabel: 'run1', sandboxDir: {sandbox_dir!r} }};\n"
            "try {\n"
            + guard_block
            + "\n  console.log('ACCEPTED');\n"
            "} catch (e) {\n"
            "  console.log('REJECTED: ' + e.message);\n"
            "}\n"
        )
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
        return (result.stdout + result.stderr).strip()

    traversal_output = run_probe("/tmp/sandbox/../../etc")
    assert traversal_output.startswith("REJECTED"), (
        f"reviewer's exact repro '/tmp/sandbox/../../etc' must be REJECTED, "
        f"got: {traversal_output!r}"
    )

    clean_output = run_probe("/tmp/sandbox")
    assert clean_output.startswith("ACCEPTED"), (
        f"a clean absolute sandboxDir must still be ACCEPTED (no regression "
        f"on the legitimate path), got: {clean_output!r}"
    )


# --- T3 round-2 architecture fix (🟡): runFixAgent trusted its caller
# completely before building an Edit-authorizing prompt. It must now assert,
# independently, that artifactPath is provably under
# sandboxDir/runLabel/ AND every remaining segment passes the (now
# dot-rejecting) allow-list — mirrors principles-improve-loop.js's
# assertStationPath :201-226, adapted to this file's sandboxDir/runLabel
# prefix instead of a fixed STATION_DIR.

def test_run_fix_agent_has_structural_scope_check():
    text = _text()
    assert "function assertArtifactPathWithinSandbox(" in text
    # the check must run as the FIRST statement inside runFixAgent's try
    # block — before any Edit-authorizing prompt is built — so a bad path
    # never reaches the agent() call at all.
    gated = re.search(
        r"async function runFixAgent\(seed, artifactPath, missLines\) \{\s*\n"
        r"\s*try \{\s*\n"
        r"\s*assertArtifactPathWithinSandbox\(artifactPath\)",
        text,
    )
    assert gated, (
        "runFixAgent must call assertArtifactPathWithinSandbox(artifactPath) "
        "as the first statement in its try block, before constructing the "
        "Edit-authorizing prompt"
    )
    # the helper degrades through runFixAgent's EXISTING catch (e) — never a
    # separate crash path — consistent with every other stage's guard
    # conventions in this file.
    assert text.count("async function runFixAgent") == 1
    assert text.count("catch (e) {") >= 3


# --- T3 round-2 correctness fix (🟡): selfCheckFixed miscounts on a
# re-check courier error. runSelfCheckCourier's catch returns a synthetic
# 1-line missLines array; the arithmetic
# `selfCheckMisses.length - reCheckMisses.length` then reports a phantom
# partial fix (e.g. 3 real misses vs 1 synthetic line -> a false fixed=2).
# The courier-error case must be tagged (`errored: true`) and, in that
# branch, selfCheckFixed must be `null` (unknown — not re-verified),
# keeping selfCheckExitAfterFix's existing degraded (1) value.

def test_recheck_courier_error_yields_unknown_selfcheck_fixed_not_phantom_count():
    text = _text()

    # runSelfCheckCourier's catch must tag its synthetic fallback distinctly.
    assert re.search(
        r"return \{ exitCode: null, missLines: \[.*?\], errored: true \}",
        text,
    ), "runSelfCheckCourier's catch must set errored: true on its synthetic fallback row"

    # the re-check consumption must branch on reCheck.errored — never
    # blindly subtract missLines lengths regardless of whether the re-check
    # courier itself errored.
    recheck_branch = re.search(
        r"selfCheckExitAfterFix = reCheckExit === null \? 1 : reCheckExit\s*\n"
        r"[\s\S]{0,800}?"
        r"selfCheckFixed = \(reCheck && reCheck\.errored\)\s*\n"
        r"\s*\? null\s*\n"
        r"\s*: Math\.max\(0, selfCheckMisses\.length - reCheckMisses\.length\)",
        text,
    )
    assert recheck_branch, (
        "the re-check branch must set selfCheckFixed to null when "
        "reCheck.errored is true, and only otherwise compute the "
        "misses-length diff — selfCheckExitAfterFix keeps its existing "
        "degraded (1) value in both cases"
    )
