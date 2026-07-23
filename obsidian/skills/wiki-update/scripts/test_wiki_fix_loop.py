"""Static-assertion tests for the wiki-update fix-loop Workflow engine
(``obsidian/skills/wiki-update/scripts/wiki_fix_loop.js``, plan Task 3,
docs/loom/plans/2026-07-23-wiki-update-loop.md, brief Decision 3,
docs/loom/specs/2026-07-23-wiki-update-maintenance-loop.md).

Mirrors loom-product-principles/scripts/test_improve_loop_workflow.py:
this suite never EXECUTES the Workflow script (ambient runtime globals
``agent``/``phase``/``workflow``/``log``/``args`` only exist inside
Claude Code's Workflow sandbox) — assertions are regex/marker checks on
the committed .js TEXT, one ``node --check`` dry-parse, and ``node -e``
extraction runs of the pure guard functions (same technique as
test_improve_loop_workflow.py's assertStationPath extraction).

Contract anchors verified here:
- handover contract (1): brake call sequencing after each grader run is
  ratchet -> compare -> stuck -> plateau -> budget, pinned by the
  BRAKE_ORDER literal + classifyBrakeExit routing.
- handover contract (2): a ratchet breach (exit 8) means the executor
  deleted content it was structurally forbidden to touch — routed as a
  STUCK-level stop (STUCK_EXECUTOR_OVERREACH) + blockers report, never
  retried.

Stdlib only; no fixtures/ subdir (flat-folder repo convention).
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parent / "wiki_fix_loop.js"


def _text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def _run_node(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(["node", "-e", script], capture_output=True, text=True)


def test_engine_parses_and_guards():
    """Plan Task 3 RED anchor: engine present, args-guarded, resume-safe."""
    assert WORKFLOW.exists(), f"workflow script missing: {WORKFLOW}"
    text = _text()

    # --- meta literal, expected name, phases ---
    assert "export const meta = {" in text
    assert "name: 'wiki-fix-loop'" in text
    assert "title: 'Freeze'" in text
    assert "title: 'Fix'" in text
    assert "title: 'Report'" in text

    # --- args guard: runLabel + every path arg allow-listed per segment ---
    assert "^[A-Za-z0-9._-]+$" in text
    assert "runArgs.runLabel" in text
    assert "runArgs.sandboxDir" in text
    assert "runArgs.vaultDir" in text
    assert "runArgs.validatorScript" in text
    assert "runArgs.verdictScript" in text
    assert ".split('/')" in text, "path args must be validated per segment"

    # --- resume-safe: no wall-clock / randomness anywhere (a Workflow run
    # resumes from a journal; either call would desync on resume) ---
    assert "Date.now" not in text
    assert "Math.random" not in text
    assert "new Date(" not in text

    # --- verdict exit-code map mirrors loop_verdict.py's global codes ---
    for marker in ["NO_WIN: 1", "MALFORMED: 2", "PLATEAU: 3", "BUDGET: 4",
                   "STUCK_FINGERPRINT: 5", "STUCK_NO_NEW_INFO: 6",
                   "STUCK_REGRESSION: 7", "RATCHET_BREACH: 8"]:
        assert marker in text, f"verdict exit map missing {marker!r}"


@pytest.mark.skipif(shutil.which("node") is None, reason="node not available")
def test_workflow_file_dry_parses():
    assert WORKFLOW.exists(), f"workflow script missing: {WORKFLOW}"
    result = subprocess.run(
        ["node", "--check", str(WORKFLOW)], capture_output=True, text=True
    )
    assert result.returncode == 0, f"node --check failed: {result.stderr}"


def test_freeze_preflight_markers():
    """Brief Decision 3: criteria freeze — violations snapshot + check-config
    hash recorded before round 1; mid-loop hash change → hard stop; the
    check-config hash is over the VALIDATOR SCRIPT's own content."""
    text = _text()

    assert "shasum -a 256" in text, "check-config hash must be sha256 of the validator script"
    assert "frozenCheckConfigHash" in text
    assert "round0" in text, "baseline violations snapshot must be a round0 file"
    assert "freeze.json" in text, "frozen criteria must be persisted"
    # drift → hard stop (throw), pre-executor AND at every grader run
    assert re.search(r"CONFIG DRIFT", text), "hash drift must be named as CONFIG DRIFT"
    assert re.search(r"throw new Error\([\s\S]{0,200}?CONFIG DRIFT", text), (
        "check-config hash drift must hard-stop via throw"
    )

    # non-git vault → explicit refusal (proposal exit requires a git repo)
    assert "rev-parse --is-inside-work-tree" in text
    assert re.search(r"not a git repo", text, re.IGNORECASE), (
        "non-git vault must be refused with an explicit error"
    )


def test_safe_tier_allowlist_and_no_deletion():
    """Design constraint 3 (goal-loop brief §Design constraints, by
    reference): action tiering fixed at design time — safe actions are an
    allow-list; deletions are structurally excluded from the executor
    contract, never a runtime judgment call."""
    text = _text()

    # allow-list constant with the three safe action classes
    assert "SAFE_ACTIONS" in text
    for action in ["retarget", "alias", "derivable"]:
        assert action in text, f"safe-tier allow-list missing {action!r} action"

    # executor prompt: structural deletion prohibition
    executor_m = re.search(r"You are the EXECUTOR([\s\S]*?)Return: ", text)
    assert executor_m, "executor agent() prompt not found"
    prompt = executor_m.group(1)
    assert re.search(r"MUST NOT delete", prompt), (
        "executor contract must structurally forbid deletion"
    )
    for noun in ["line", "section", "page"]:
        assert noun in prompt, f"deletion prohibition must name {noun}s"

    # unsafe-only classes → work-order file, class skipped, never retried
    assert "classUnsafeOnly" in text
    assert "work-orders.jsonl" in text
    assert "skippedClasses" in text


def test_one_class_per_round_pick_is_deterministic_executable():
    """One violation class per round, chosen by CODE from the previous
    round's by_check counts (Rule 5: never an LLM routing decision)."""
    text = _text()
    fn_m = re.search(
        r"function pickNextClass\(byCheck, skippedClasses\) \{[\s\S]*?\n\}\n", text)
    assert fn_m, "pickNextClass function not found"
    if shutil.which("node") is None:
        pytest.skip("node not available")
    script = (
        fn_m.group(0) + "\n"
        "const r1 = pickNextClass({L01: 5, L07: 3}, []);\n"
        "const r2 = pickNextClass({L01: 5, L07: 3}, ['L01']);\n"
        "const r3 = pickNextClass({L04: 3, L01: 3}, []);\n"
        "const r4 = pickNextClass({L01: 5}, ['L01']);\n"
        "console.log(JSON.stringify([r1, r2, r3, r4]));\n"
    )
    result = _run_node(script)
    assert result.returncode == 0, f"node -e failed: {result.stderr}"
    assert result.stdout.strip() == '["L01","L07","L01",null]', (
        "pickNextClass must pick the largest class, honor the skip list, "
        f"tie-break lexicographically, and return null when exhausted: {result.stdout}"
    )


def test_check_id_guard_executable():
    """Class ids flow from courier-returned validator output into prompts,
    commit messages, and ledger lines — allow-list them before use."""
    text = _text()
    fn_m = re.search(r"function assertCheckId\(checkId\) \{[\s\S]*?\n\}\n", text)
    assert fn_m, "assertCheckId function not found"
    if shutil.which("node") is None:
        pytest.skip("node not available")
    script = (
        fn_m.group(0) + "\n"
        "assertCheckId('L01'); assertCheckId('PARSE'); console.log('VALID_OK');\n"
        "try { assertCheckId('x; rm -rf /'); console.log('NOT_REJECTED') }\n"
        "catch (e) { console.log('REJECTED_SHELL') }\n"
        "try { assertCheckId('../evil'); console.log('NOT_REJECTED') }\n"
        "catch (e) { console.log('REJECTED_TRAVERSAL') }\n"
    )
    result = _run_node(script)
    assert result.returncode == 0, f"node -e failed: {result.stderr}"
    assert "VALID_OK" in result.stdout
    assert "REJECTED_SHELL" in result.stdout
    assert "REJECTED_TRAVERSAL" in result.stdout
    assert "NOT_REJECTED" not in result.stdout


def test_brake_ordering_and_routing_executable():
    """Handover contract (1): ratchet (safety first) -> compare -> stuck ->
    plateau -> budget, and every non-zero exit routes by code. Handover
    contract (2): ratchet breach (8) = executor overreach = STUCK-level
    stop. Both pinned by extracting BRAKE_ORDER + classifyBrakeExit and
    exercising them in a throwaway node run."""
    text = _text()

    # ordered literal — the round loop iterates this array
    assert re.search(
        r"BRAKE_ORDER = \['ratchet', 'compare', 'stuck', 'plateau', 'budget'\]",
        text), "BRAKE_ORDER literal must pin the handover-contract sequence"

    const_m = re.search(r"const VERDICT_EXIT = \{[\s\S]*?\}\n", text)
    fn_m = re.search(
        r"function classifyBrakeExit\(stage, exitCode\) \{[\s\S]*?\n\}\n", text)
    order_m = re.search(r"const BRAKE_ORDER = \[[^\]]+\]\n", text)
    assert const_m and fn_m and order_m, "brake routing pieces not found"
    if shutil.which("node") is None:
        pytest.skip("node not available")
    script = (
        const_m.group(0) + order_m.group(0) + fn_m.group(0) + "\n"
        "function route(exits) {\n"
        "  let noWin = false;\n"
        "  for (const stage of BRAKE_ORDER) {\n"
        "    const d = classifyBrakeExit(stage, exits[stage]);\n"
        "    if (d.kind === 'stop') return d.terminal;\n"
        "    if (d.kind === 'no-win') noWin = true;\n"
        "  }\n"
        "  return noWin ? 'REVERT_CONTINUE' : 'ACCEPT';\n"
        "}\n"
        "const out = [\n"
        "  route({ratchet:0, compare:0, stuck:0, plateau:0, budget:0}),\n"
        "  route({ratchet:8, compare:0, stuck:0, plateau:0, budget:0}),\n"
        "  route({ratchet:8, compare:0, stuck:7, plateau:0, budget:0}),\n"
        "  route({ratchet:0, compare:1, stuck:0, plateau:0, budget:0}),\n"
        "  route({ratchet:0, compare:1, stuck:7, plateau:0, budget:0}),\n"
        "  route({ratchet:0, compare:1, stuck:0, plateau:3, budget:0}),\n"
        "  route({ratchet:0, compare:0, stuck:0, plateau:0, budget:4}),\n"
        "  route({ratchet:2, compare:0, stuck:0, plateau:0, budget:0}),\n"
        "];\n"
        "console.log(JSON.stringify(out));\n"
    )
    result = _run_node(script)
    assert result.returncode == 0, f"node -e failed: {result.stderr}"
    assert result.stdout.strip() == (
        '["ACCEPT","STUCK_EXECUTOR_OVERREACH","STUCK_EXECUTOR_OVERREACH",'
        '"REVERT_CONTINUE","STUCK","PLATEAU","BUDGET","MALFORMED"]'
    ), (
        "brake routing broke a handover contract: ratchet-first precedence, "
        "no-win = revert-and-continue (plateau can still fire later), "
        f"stuck/plateau/budget stop codes, malformed fails loud: {result.stdout}"
    )


def test_verdict_cli_invocations_use_default_strikes():
    """All five verdict verbs invoked against T2's CLI; `stuck` relies on
    the CLI's default --strikes 3 (dispatch spec) rather than passing it."""
    text = _text()
    assert "ratchet --baseline" in text
    assert "compare --baseline" in text
    assert "stuck --rounds" in text
    assert "plateau --rounds" in text
    assert "budget --round" in text
    assert "--strikes" not in text, "stuck must use the CLI default (3)"
    assert "--max-rounds" in text


def test_ratchet_breach_and_stuck_write_blockers_report():
    """Handover contract (2): breach = executor overreach → STUCK-level
    stop + blockers report; STUCK stops also produce the report."""
    text = _text()
    assert "STUCK_EXECUTOR_OVERREACH" in text
    assert "blockers-report.md" in text
    assert re.search(r"overreach", text, re.IGNORECASE)
    # never retried: no re-dispatch of the executor after a breach —
    # the breach path must lead to a stop, not a loop continue
    assert re.search(r"breach[\s\S]{0,400}?stop", text, re.IGNORECASE), (
        "ratchet breach must be a stop path"
    )


def test_size_circuit_breaker_and_scorecard():
    """Design constraints 1-2 (by reference): structural scorecard leads;
    cumulative diff size over threshold stops the loop requesting a split."""
    text = _text()
    assert "maxDiffLines" in text
    assert "SIZE_SPLIT" in text
    assert "--numstat" in text, "diff size must come from git numstat, not prose"
    assert re.search(r"split", text, re.IGNORECASE)
    # structural scorecard fields
    for key in ["diffLines", "diffFiles", "violationDelta", "rounds",
                "terminal", "baselineViolations", "finalViolations"]:
        assert key in text, f"scorecard missing structural field {key!r}"
    assert "scorecard.json" in text


def test_ledger_appended_per_round():
    text = _text()
    assert "ledger.jsonl" in text
    assert "ROUND_LEDGER" in text
    assert "recordRoundLedgerEntry" in text
    for key in ["round", "checkId", "action", "violationsBefore",
                "violationsAfter", "reason"]:
        assert f"'{key}'" in text, f"ledger entry shape missing key {key!r}"


def test_proposal_exit_never_merges_or_pushes():
    """Brief Decision 3: proposal-branch exit — local commits on a branch
    in the VAULT repo; the engine has no merge/push/upload capability."""
    text = _text()
    assert "checkout -b" in text, "must open a proposal branch"
    assert "wiki-fix/" in text, "proposal branch namespace marker"
    assert "git merge" not in text
    assert "git push" not in text
    assert "gh pr " not in text
    # commit message carried via file, never as an inline -m argument
    # (vault commands are `git -C <vault> commit -F <path>`)
    assert re.search(r"git -C [^\n]* commit -F ", text), (
        "must commit via a message file (commit -F)"
    )
    assert not re.search(r"^\s*\d+\.\s*git commit\b[^\n]*-m\b", text, re.MULTILINE), (
        "no courier instruction may pass commit text as a -m argument"
    )
    # never stage the whole tree (repo memory: never `git add -A`)
    assert "git add -A" not in text
    assert re.search(r"git add wiki", text), "staging must be scoped to wiki/"


def test_no_bare_report_md_basename():
    """Harness guard: bare `report.md` basenames trip the subagent-summary
    guard — only prefixed names (fix-loop-report.md / blockers-report.md)."""
    text = _text()
    assert "fix-loop-report.md" in text
    assert not re.search(r"(?<![\w-])report\.md", text), (
        "must never create a file with bare basename report.md"
    )


def test_untrusted_data_wrapped_in_inert_markers():
    """Courier prompts embedding validator/ledger-derived JSON must wrap it
    in explicit inert-data delimiters (same discipline as the precedent's
    EDITS_DATA/ROW_SET_DATA markers)."""
    text = _text()
    assert "INERT" in text or "inert" in text
    assert "DATA_BEGIN_MARKER" in text and "DATA_END_MARKER" in text
    assert re.search(r"never (execute|treat|follow)", text, re.IGNORECASE)
