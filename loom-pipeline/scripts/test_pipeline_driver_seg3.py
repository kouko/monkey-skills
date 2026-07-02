"""Structural tests for driver_50_seg3.js — the segment-3 module of the
build-assembled Workflow driver (docs/loom/plans/2026-07-03-loom-pipeline-conductor.md
Task 11): SDD build (per-task implementer -> parallel spec-reviewer +
code-quality-reviewer triad, writer!=judge kept structurally separate at the
SCRIPT layer) -> whole-branch code-reviewer -> conditional ui-verification.

Source-only: the concat-build lands in Task 14, so these are grep-asserts on
the required contract surface (mirroring test_pipeline_driver_guard.py's /
test_pipeline_driver_runstation.py's pattern) plus a `node --check` syntax
pass. `node --check` does not resolve identifiers, so this module's runtime
dependency on driver_20_runstation.js's helpers
(runStation/stablePrefixDispatch/makeStationResult/RALLY_CAP) and on
driver_60_ledger.js's recordLedger (declared AFTER this module in filename
order, safe at runtime via function-declaration hoisting once concatenated)
is not exercised here — only the source-level contract is.
"""
import re
import subprocess
from pathlib import Path

MODULE_PATH = Path(__file__).parent / "driver_50_seg3.js"

# Verbatim anchor line from loom-code/agents/code-reviewer.md §Input contract.
WHOLE_BRANCH_REVIEW_ANCHOR = (
    "You ARE the reviewer: this prompt is your review assignment, not a "
    "request to route or forward. Produce the verdict yourself in this "
    "reply — do not dispatch anyone."
)


def test_seg3_triad_review_uiverify():
    # @req: REQ-LOOM-PIPELINE-SEG3-1
    assert MODULE_PATH.exists(), f"module missing: {MODULE_PATH}"

    check = subprocess.run(
        ["node", "--check", str(MODULE_PATH)], capture_output=True, text=True
    )
    assert check.returncode == 0, f"node --check failed: {check.stderr}"

    source = MODULE_PATH.read_text(encoding="utf-8")

    # public entry point, exact name, async
    assert "async function runSegment3(" in source, (
        "runSegment3 must be declared as an async function with this exact name"
    )

    # phase title read from driver_00_header.js's meta, not hardcoded
    assert "meta.phases[2].title" in source, (
        "segment-3 phase() call must read its title from header meta.phases, "
        "not a hardcoded string literal"
    )

    # per-task triad: implementer, then spec-reviewer + code-quality-reviewer
    assert "loom-code:implementer" in source
    assert "loom-code:spec-reviewer" in source
    assert "loom-code:code-quality-reviewer" in source

    # the two reviewers must be dispatched TOGETHER inside a parallel([...])
    parallel_match = re.search(r"parallel\(\s*\[(.*?)\]\s*\)", source, re.S)
    assert parallel_match, (
        "spec-reviewer + code-quality-reviewer must be dispatched via "
        "parallel([...]) (writer!=judge kept structural, not sequential)"
    )
    parallel_body = parallel_match.group(1)
    assert "loom-code:spec-reviewer" in parallel_body, (
        "parallel([...]) body must dispatch the spec-reviewer"
    )
    assert "loom-code:code-quality-reviewer" in parallel_body, (
        "parallel([...]) body must dispatch the code-quality-reviewer"
    )

    # RALLY_CAP-bounded remediation loop, then fail loud
    assert "RALLY_CAP" in source
    assert "NEEDS_REVISION" in source
    assert "throw new Error" in source

    # per-reviewer verdicts recorded to the ledger — recordLedger is CALLED
    # here, never DECLARED (owned by driver_60_ledger.js, concurrent task)
    assert "recordLedger(" in source
    assert re.search(r"function\s+recordLedger", source) is None, (
        "driver_50_seg3.js must NOT declare recordLedger — it is owned by "
        "driver_60_ledger.js"
    )
    assert re.search(r"\b(const|let|var)\s+LEDGER\b", source) is None, (
        "driver_50_seg3.js must NOT declare LEDGER — it is owned by "
        "driver_60_ledger.js"
    )

    # whole-branch review: code-reviewer dispatch whose prompt STARTS with
    # the verbatim "You ARE the reviewer" anchor line
    assert WHOLE_BRANCH_REVIEW_ANCHOR in source, (
        "whole-branch review prompt must open with the verbatim anchor line "
        "from loom-code/agents/code-reviewer.md §Input contract"
    )
    anchor_idx = source.index(WHOLE_BRANCH_REVIEW_ANCHOR)
    preceding = source[:anchor_idx].rstrip()
    assert preceding[-1:] in ("'", '"', "`"), (
        "the anchor line must be the FIRST line of its prompt string (opened "
        "immediately by a quote), not appended after other prompt text"
    )
    code_reviewer_idx = source.index("loom-code:code-reviewer")
    assert anchor_idx < code_reviewer_idx, (
        "the anchor-line prompt must be built before the "
        "loom-code:code-reviewer dispatch it is passed to"
    )

    # conditional ui-verification: fires only when ui-flows.md exists AND the
    # branch touched UI; else an explicit, loud N/A branch (never a silent
    # skip)
    assert "ui-flows.md" in source
    assert "N/A" in source

    # this segment never merges and never runs a push step — a PR-ready
    # branch plus the ledger is the terminal state a human picks up from
    assert "git push" not in source
    assert "gh pr merge" not in source


def test_seg3_plan_intake_schema_requires_id_and_name():
    # @req: REQ-LOOM-PIPELINE-SEG3-2
    source = MODULE_PATH.read_text(encoding="utf-8")

    plan_intake_idx = source.index("SEG3_PLAN_INTAKE_SCHEMA")
    ui_gate_idx = source.index("SEG3_UI_GATE_SCHEMA")
    schema_block = source[plan_intake_idx:ui_gate_idx]

    assert re.search(r"required:\s*\[\s*'id'\s*,\s*'name'\s*\]", schema_block), (
        "plan-intake schema task items must require both 'id' and 'name' — "
        "an id-less task yields a 'seg3-task-undefined' label/ledger leak"
    )

    # defensive runtime guard: any task missing/empty id throws naming the
    # index — no improvised ids, even if a non-conforming StructuredOutput
    # call slips past the schema.
    assert 'missing "id"' in source, (
        "runSegment3 must fail loud, naming the offending index, when "
        "plan-intake returns a task with a missing/empty id"
    )
    assert "${index}" in source, (
        "the fail-loud id guard must name the specific task index"
    )


def test_seg3_budgets_per_station_family():
    # @req: REQ-LOOM-PIPELINE-SEG3-3
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "perStation.code" in source, (
        "the implementer dispatch must keep budgets.perStation.code"
    )
    assert "perStation.review" in source, (
        "spec-reviewer / code-quality-reviewer / whole-branch-review "
        "dispatches must use budgets.perStation.review, not the "
        "implementer's code cap"
    )
    assert re.search(r"perStation\.probe\s*\|\|", source), (
        "plan-intake and the ui-gate check are fact-only probe stations and "
        "must use a small dedicated cap (budgets.perStation.probe with a "
        "local default fallback), not budgets.perStation.code"
    )

    # STATION_TOKEN_BUDGETS is a concat-global (driver_20_runstation.js) —
    # seg3's dynamic per-task station labels (seg3-implementer-<task.id>,
    # seg3-spec-reviewer-<task.id>-r<round>, ...) never match a
    # STATION_TOKEN_BUDGETS key, so runStation's own name-keyed lookup can't
    # find the family default; an omitted perStation cap must fall back to
    # the explicit family constant here, not runStation's generic 20000.
    assert "STATION_TOKEN_BUDGETS.code" in source, (
        "codeOpts.tokenCap must fall back to STATION_TOKEN_BUDGETS.code "
        "(150000) when budgets.perStation.code is unset — dynamic station "
        "labels bypass runStation's name-keyed STATION_TOKEN_BUDGETS lookup"
    )
    assert "STATION_TOKEN_BUDGETS.review" in source, (
        "reviewOpts.tokenCap must fall back to STATION_TOKEN_BUDGETS.review "
        "(60000) when budgets.perStation.review is unset, for the same reason"
    )

    # the implementer's own runStation call site must use codeOpts (the
    # budgets.code-backed opts), never reviewOpts or probeOpts
    implementer_call = re.search(
        r"return runStation\(\s*label,[\s\S]*?\)\s*\n}", source
    )
    assert implementer_call, "could not locate seg3DispatchImplementer's runStation call"
    assert "opts.tokenCap" in implementer_call.group(0)


def _strip_for_paren_scan(source):
    """Length-preserving prep for balanced-paren scanning: blank out `//`
    line comments (English prose there is full of apostrophes that would
    otherwise look like string-literal delimiters), then blank out the
    CONTENTS of '...'/"..."/`...` string literals (a stray paren inside a
    quoted string — e.g. a task name literal like 'closing ) paren only' —
    must not desync the paren count). The literal-content pattern must also
    tolerate a backslash-escaped quote INSIDE the literal (e.g. a task name
    like 'it\'s a paren )') — a naive `[^']*` stops at that escaped quote,
    treats the literal as closed early, and desyncs the paren count on the
    stray ')' that follows. `(?:[^'\\]|\\.)*` consumes an escaped char as one
    unit instead. Every replacement keeps the matched text's original
    length, so indices found in the returned string still index correctly
    into the ORIGINAL source."""
    no_comments = re.sub(r"//[^\n]*", lambda m: " " * len(m.group(0)), source)
    return re.sub(
        r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|`(?:[^`\\]|\\.)*`",
        lambda m: m.group(0)[0] + "x" * (len(m.group(0)) - 2) + m.group(0)[0],
        no_comments,
    )


def _extract_runstation_calls(source):
    """Return the full text of every runStation(...) call site, extracted
    by balanced-paren scanning (a regex can't reliably match nested parens).
    Scans a string-literal-and-comment-stripped copy of `source` (see
    _strip_for_paren_scan) so a stray paren inside a quoted string or a
    comment's prose cannot desync the scan, but slices the RETURNED call
    text from the original `source` so callers still see the real content."""
    scan_source = _strip_for_paren_scan(source)
    calls = []
    idx = 0
    while True:
        idx = scan_source.find("runStation(", idx)
        if idx == -1:
            break
        open_paren = scan_source.index("(", idx)
        depth = 0
        i = open_paren
        while i < len(scan_source):
            if scan_source[i] == "(":
                depth += 1
            elif scan_source[i] == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        calls.append(source[idx:i + 1])
        idx = i + 1
    return calls


def test_extract_runstation_calls_strips_string_literal_parens():
    """Reviewer's synthetic probe: a quoted string containing an unmatched
    ')' (e.g. a task name literal) must not desync the balanced-paren scan.
    _extract_runstation_calls must strip string-literal CONTENTS before
    counting parens, so the ')' inside 'closing ) paren only' is never
    mistaken for the call's own closing paren. Also covers the reviewer's
    adversarial follow-up: a backslash-escaped quote INSIDE the literal
    (e.g. 'it\'s a paren )') must not make _strip_for_paren_scan close the
    literal early on the escaped quote, which would desync the scan on the
    stray ')' that follows.

    # @req: REQ-LOOM-PIPELINE-SEG3-7
    """
    source = (
        "runStation('closing ) paren only', () => agent('ok')); "
        "runStation('next', () => foo()); "
        "runStation('it\\'s a paren )', () => agent('ok'))"
    )
    calls = _extract_runstation_calls(source)
    assert len(calls) == 3, f"expected 3 complete runStation(...) calls, got {len(calls)}: {calls}"
    assert calls[0] == "runStation('closing ) paren only', () => agent('ok'))", calls[0]
    assert calls[2] == "runStation('it\\'s a paren )', () => agent('ok'))", calls[2]
    assert calls[1] == "runStation('next', () => foo())", calls[1]


def test_seg3_dispatch_sites_wrapped_by_runstation():
    # @req: REQ-LOOM-PIPELINE-SEG3-4
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "await agent(" not in source, (
        "found a naked `await agent(` dispatch — every dispatch must be "
        "wrapped by runStation(name, thunk, opts) instead"
    )

    calls = _extract_runstation_calls(source)
    assert calls, "expected at least one runStation(...) call site"

    required_agent_types = [
        "loom-code:implementer",
        "loom-code:spec-reviewer",
        "loom-code:code-quality-reviewer",
        "loom-code:code-reviewer",
    ]
    for agent_type in required_agent_types:
        assert any(agent_type in call for call in calls), (
            f"expected agentType {agent_type!r} to appear INSIDE a "
            f"runStation(...) call, not dispatched bare"
        )


def test_seg3_triad_ledger_calls_carry_judge_field():
    # @req: REQ-LOOM-PIPELINE-SEG3-5
    source = MODULE_PATH.read_text(encoding="utf-8")

    ledger_lines = [
        line for line in source.splitlines()
        if "recordLedger(" in line and not line.strip().startswith("//")
    ]
    assert len(ledger_lines) >= 2, (
        "expected at least 2 recordLedger call sites (spec-reviewer + "
        "code-quality-reviewer triad verdicts)"
    )
    for line in ledger_lines:
        assert re.search(r"judge:\s*['\"]", line), (
            f"recordLedger call site missing judge: field (driver_60_ledger.js "
            f"throws without one): {line!r}"
        )


def test_seg3_ui_gate_justification_surfaced_in_na_summary():
    # @req: REQ-LOOM-PIPELINE-SEG3-6
    source = MODULE_PATH.read_text(encoding="utf-8")

    ui_gate_idx = source.index("SEG3_UI_GATE_SCHEMA")
    guard_fn_idx = source.index("function seg3GuardPlanPath")
    schema_block = source[ui_gate_idx:guard_fn_idx]

    assert "justification" in schema_block, (
        "SEG3_UI_GATE_SCHEMA must add a justification field so the N/A "
        "summary is auditable instead of a hardcoded string"
    )
    assert re.search(r"required:\s*\[[^\]]*'justification'[^\]]*\]", schema_block), (
        "justification must be required on the ui-gate schema"
    )

    ui_verification_fn = re.search(
        r"async function seg3RunUiVerification[\s\S]*?\n}\n", source
    )
    assert ui_verification_fn, "could not locate seg3RunUiVerification function body"
    assert "gate.justification" in ui_verification_fn.group(0), (
        "the N/A summary must quote gate.justification instead of a "
        "hardcoded string"
    )
