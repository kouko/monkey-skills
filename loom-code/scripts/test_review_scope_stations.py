"""Structural grep-window test guarding requesting-code-review's adoption
of the `review_scope.py` resolver (Task 5 of
`docs/loom/plans/2026-08-03-review-scope-resolver.md`).

SKILL.md is a prompt/contract artifact, not executable code: nothing
importable observes whether the orchestrator actually calls the resolver
instead of running its own `git diff`. This file IS the instruction the
orchestrator reads at each call site, so its correctness condition is
the PRESENCE of the load-bearing resolver-call phrases and the ABSENCE
of the raw `git diff main...HEAD` invocations it replaces -- same
convention as `test_docs_review_mode.py`.

Three call sites, three separate windows (the direct-entry step in
§Push-as-trigger, the routing step at Process Step 1, and the
marker-sweep step at Process Step 4) must each name the resolver -- a
whole-file substring check would pass if only one site were converted.

The absence check covers all three historical spellings recorded in the
plan's §Notes ("A fourth call site..."): no `--name-only` (§Push-as-
trigger Step 3, `:85`), the flag trailing (Process Step 1, `:96`), and
the flag leading -- reversed order -- inside the grep substitution
(Process Step 4, `:106`). `test_forbidden_pattern_catches_all_three_
historical_shapes` proves the oracle actually catches all three shapes
on synthetic strings, independent of the real file, before trusting it
against the file (the exact trap this arc's dispatch packet calls out:
an oracle that only matches the `--name-only` form passes while an old
computation survives elsewhere).

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILL_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "requesting-code-review"
    / "SKILL.md"
)

# The two pinned contracts, transcribed verbatim from
# docs/loom/plans/2026-08-03-review-scope-resolver.md §Notes, normalized
# the same way the file text is normalized before comparison.
REFUSAL_CONTRACT = (
    "A stale base, or any failure to establish freshness, REFUSES. "
    "The resolver never returns a file list it cannot vouch for, and a "
    "station that receives a refusal STOPS before dispatching anything."
)
PASS_DOWN_CONTRACT = (
    "The delegating station hands the delegate the resolved scope as "
    "`resolved-scope` in the dispatch packet. The delegate resolves "
    "scope itself ONLY when no `resolved-scope` was supplied."
)

# The three historical git-diff spellings this task replaces (plan
# §Notes "A fourth call site" + Task 5 Acceptance).
HISTORICAL_SHAPES = [
    "git diff main...HEAD",  # :85 -- no --name-only
    "git diff main...HEAD --name-only",  # :96 -- flag trailing
    "git diff --name-only main...HEAD",  # :106 -- flag leading (reversed)
]

FORBIDDEN_PATTERNS = [
    re.compile(r"git diff( --name-only)? main\.\.\.HEAD"),
    re.compile(r"git diff --name-only main\.\.\.HEAD"),
]

# The operative hand-off phrase a `resolved-scope` mention must appear
# inside of -- bare token presence is not enough (code-quality review,
# Task 5 round 2, finding F2): a bullet can carry the literal token
# `resolved-scope` in a trailing aside while instructing nothing to be
# carried. Requires a hand-off verb (hand/hands/handing) followed,
# within 80 chars, by the labelled `resolved-scope` payload -- the
# CONCEPT (verb-then-labelled-payload), not the literal pronoun "it"
# or the literal word "as". Round 3: the prior pattern hardcoded
# `hand(?:ing|s)?\s+it\s+...as\s+` and false-failed two operationally-
# correct rewordings that drop "it" ("hands the docs arm the resolved
# scope, naming the payload `resolved-scope`") or reorder the object
# ("hands the resolved scope to the docs arm as `resolved-scope`").
# Both of the round-2 wrong strings below are still rejected: the
# bare-token-in-a-parenthetical mutation carries no hand-off verb at
# all, and the mixed-branch prose-mention variant's only "hand" occurs
# AFTER an un-backticked "resolved-scope" (in "hand-down"), never
# before a backticked one -- so the verb-then-token order still
# discriminates without needing "it".
HANDOFF_PATTERN = re.compile(
    r"hand(?:ing|s)?\b.{0,80}?`resolved-scope`", re.DOTALL
)

# A second, live invocation of the resolver inside the marker-sweep
# step's fenced code block (code-quality review, Task 5 round 2,
# finding F1): Step 4 must reuse Step 1's already-resolved file list,
# never re-run review_scope.py -- a second invocation is a second
# network fetch, forbidden by the brief's §Resolved Questions 2.
RESOLVER_CALL_PATTERN = re.compile(r"python3\s+\S*review_scope\.py")


def _text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _numbered_step_section(text: str, start_pattern: str, label: str) -> str:
    """Isolate one numbered-list step: from the column-0 line matching
    `start_pattern` to the next column-0 `<digit>. ` line, or EOF."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if re.match(start_pattern, line):
            start = i
            break
    assert start is not None, (
        f"requesting-code-review/SKILL.md carries no '{label}' line -- "
        "the step must be findable, not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\d+\.\s", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def _direct_entry_section(text: str) -> str:
    """§Push-as-trigger Step 3 -- 'Offer to run review now'."""
    return _numbered_step_section(
        text,
        r"^3\.\s+\*\*Offer to run review now",
        "3. **Offer to run review now**",
    )


def _routing_section(text: str) -> str:
    """§Process Step 1 -- 'Determine diff scope, then route by file type'."""
    return _numbered_step_section(
        text,
        r"^1\.\s+\*\*Determine diff scope",
        "1. **Determine diff scope**",
    )


def _marker_sweep_section(text: str) -> str:
    """§Process Step 4 -- the LOOM-SIMPLIFY: harvest."""
    return _numbered_step_section(
        text,
        r"^4\.\s+\*\*Harvest the deliberate-simplification ledger",
        "4. **Harvest the deliberate-simplification ledger**",
    )


def _fenced_code_blocks(section: str) -> list[str]:
    """Every ``` ... ``` fenced block inside a section, contents only."""
    return re.findall(r"```\n?(.*?)```", section, re.DOTALL)


def _mixed_branch_docs_arm_clause(routing_section: str) -> str:
    """Isolate the docs-arm hand-off clause inside the 'Mixed branch'
    bullet: from 'the `.md` files go to the docs arm' up to the next
    sentence, 'The orchestrator unions' -- scoping the resolved-scope
    check to the clause that actually sends files to the docs arm, not
    the whole bullet (a mention anywhere in the bullet is not the same
    as a hand-off in THIS clause)."""
    start_marker = "the `.md` files go to the docs arm"
    end_marker = "The orchestrator unions"
    start = routing_section.find(start_marker)
    assert start != -1, (
        "Process Step 1 must still carry the 'Mixed branch' bullet's "
        "docs-arm hand-off clause ('the `.md` files go to the docs arm')"
    )
    end = routing_section.find(end_marker, start)
    assert end != -1, (
        "the docs-arm hand-off clause must be followed by the "
        "orchestrator's union sentence ('The orchestrator unions')"
    )
    return routing_section[start:end]


def test_resolver_named_at_all_three_call_sites():
    """Each of the three converted call sites must name the resolver
    script -- naming it at only one or two sites would leave a reader
    unable to tell the remaining site(s) still route through it."""
    text = _text()

    direct_entry = _direct_entry_section(text)
    routing = _routing_section(text)
    marker_sweep = _marker_sweep_section(text)

    assert "review_scope.py" in direct_entry, (
        "the direct-entry step (§Push-as-trigger Step 3) must name "
        "review_scope.py as its scope source"
    )
    assert "review_scope.py" in routing, (
        "the routing step (Process Step 1) must name review_scope.py "
        "as its scope source"
    )
    assert "review_scope.py" in marker_sweep, (
        "the marker-sweep step (Process Step 4) must name review_scope.py "
        "-- reusing the resolved scope, not recomputing it"
    )


def test_delegation_step_names_resolved_scope_as_operative_handoff():
    """The docs-only delegation bullet in Process Step 1 must hand the
    delegate the resolved scope via an OPERATIVE hand-off phrase --
    'hand(ing/s) it ... as `resolved-scope`' -- not merely contain the
    bare token somewhere on the line. Code-quality review (Task 5 round
    2, finding F2) demonstrated a mutation that keeps the token in a
    trailing aside ("the passed payload is called `resolved-scope`")
    while removing the instruction to carry it, and the old
    bare-presence check passed it anyway. Per §Pinned pass-down
    contract, this is the pin Task 6's implementer transcribes the
    other half of -- naming it any other way would let that
    implementer name the same payload differently and still pass its
    own grep-window test."""
    text = _text()
    routing = _routing_section(text)

    docs_only_line = None
    for line in routing.splitlines():
        if "Docs-only branch" in line:
            docs_only_line = line
            break
    assert docs_only_line is not None, (
        "Process Step 1 must still carry its 'Docs-only branch' bullet"
    )
    assert HANDOFF_PATTERN.search(docs_only_line), (
        "the docs-only delegation bullet must carry an operative "
        "hand-off phrase ('hand(ing/s) it ... as `resolved-scope`'), "
        "not just the bare token"
    )


def test_delegation_handoff_oracle_rejects_bare_token_mention():
    """Prove HANDOFF_PATTERN actually discriminates -- the F2 mutation
    (token survives, hand-off instruction removed) must fail the
    check, not pass it by accident of a whole-line substring search."""
    wrong_line = (
        "   - **Docs-only branch** — the file list is non-empty AND "
        "every file in it ends in `.md` → **delegate the WHOLE review "
        "to `requesting-docs-review`**: invoke that skill and stop "
        "here — do not dispatch the code-reviewer panel below. "
        "(Elsewhere in this repo the passed payload is called "
        "`resolved-scope`.)"
    )
    assert "resolved-scope" in wrong_line, (
        "sanity check: the synthetic wrong line must still carry the "
        "bare token, to prove the OLD bare-presence check would have "
        "passed it"
    )
    assert not HANDOFF_PATTERN.search(wrong_line), (
        "the operative-handoff oracle must reject a line that mentions "
        "`resolved-scope` without an instruction to hand it off"
    )


# Round-3 pin: two operationally-correct rewordings of the hand-off
# bullets that a code author might plausibly write, neither of which
# uses the literal pronoun "it" -- reviewer-demonstrated live against
# the pre-round-3 pattern as false rejections (see HANDOFF_PATTERN's
# comment above).
OPERATIONAL_REWORDS_WITHOUT_IT = [
    "hands the docs arm the resolved scope, naming the payload "
    "`resolved-scope`",
    "hands the resolved scope to the docs arm as `resolved-scope`",
]


def test_handoff_oracle_accepts_reword_dropping_the_pronoun_it():
    """HANDOFF_PATTERN must accept a legitimate paraphrase of the
    hand-off bullets that drops the literal pronoun "it" -- proves the
    round-3 loosening (verb-then-labelled-payload, not verb-then-
    pronoun-then-`as`) actually fixes the brittleness, not just that
    the old cases still pass."""
    for reword in OPERATIONAL_REWORDS_WITHOUT_IT:
        assert HANDOFF_PATTERN.search(reword), (
            f"the hand-off oracle must accept the operationally-"
            f"correct reword {reword!r} without requiring the literal "
            "pronoun `it`"
        )


def test_handoff_oracle_still_rejects_both_round2_wrong_strings():
    """The loosened HANDOFF_PATTERN must still reject the two wrong
    strings that motivated it in the first place (round 2's bare-token
    mutation and the mixed-branch prose-mention variant) -- proves the
    fix didn't trade brittleness for a false pass. Both strings are the
    same ones test_delegation_handoff_oracle_rejects_bare_token_mention
    and test_mixed_branch_handoff_oracle_rejects_prose_mention_without_handoff
    already pin against the file; this test pins the pattern directly,
    independent of SKILL.md's current text."""
    bare_token_mutation = (
        "invoke that skill and stop here — do not dispatch the "
        "code-reviewer panel below. (Elsewhere in this repo the "
        "passed payload is called `resolved-scope`.)"
    )
    mixed_branch_prose_mention = (
        "its own mint step does not fire here; this mirrors the "
        "docs-only bullet's resolved-scope hand-down)."
    )
    assert not HANDOFF_PATTERN.search(bare_token_mutation), (
        "the loosened oracle must still reject a bare `resolved-scope` "
        "mention with no hand-off verb in the string at all"
    )
    assert not HANDOFF_PATTERN.search(mixed_branch_prose_mention), (
        "the loosened oracle must still reject a mention where the "
        "only hand-off verb occurrence trails an UN-backticked "
        "'resolved-scope', never precedes a backticked one"
    )


def test_refusal_stops_station_before_dispatch():
    """§Pinned refusal contract must be transcribed VERBATIM somewhere
    in the file -- not paraphrased -- so the 'refusal STOPS before
    dispatching anything' rule is unambiguous to a reader who has not
    seen the plan."""
    text = _text()
    norm = _norm(text)

    assert REFUSAL_CONTRACT in norm, (
        "the §Pinned refusal contract must appear VERBATIM (normalized "
        "whitespace only) -- paraphrasing it is not sufficient"
    )


def test_pass_down_contract_transcribed_verbatim():
    """§Pinned pass-down contract must be transcribed VERBATIM -- this
    is the pin Task 6's implementer transcribes the other half of, in
    parallel; a paraphrase here can silently diverge from Task 6's
    copy even though both grep-window tests independently pass."""
    text = _text()
    norm = _norm(text)

    assert PASS_DOWN_CONTRACT in norm, (
        "the §Pinned pass-down contract must appear VERBATIM (normalized "
        "whitespace only) -- paraphrasing it is not sufficient"
    )


def test_no_historical_git_diff_invocation_survives():
    """No line anywhere in the file may match either forbidden pattern
    -- all three historical shapes (no flag / flag trailing / flag
    leading) must be gone, not just the most obvious one."""
    text = _text()
    for lineno, line in enumerate(text.splitlines(), start=1):
        for pattern in FORBIDDEN_PATTERNS:
            assert not pattern.search(line), (
                f"line {lineno} still matches {pattern.pattern!r}: "
                f"{line.strip()!r} -- an old branch-diff computation "
                "survives the resolver migration"
            )


def test_forbidden_pattern_catches_all_three_historical_shapes():
    """Prove the oracle in test_no_historical_git_diff_invocation_survives
    actually catches all three historical shapes, on synthetic strings,
    BEFORE trusting it against the real file -- an oracle that only
    matches the `--name-only` form would pass while an old computation
    survives in a different shape elsewhere in the file (the exact trap
    named in this task's dispatch packet)."""
    for shape in HISTORICAL_SHAPES:
        assert any(p.search(shape) for p in FORBIDDEN_PATTERNS), (
            f"the forbidden-pattern oracle must catch {shape!r}, one of "
            "the three historical invocation shapes"
        )

    # And a mutation-of-shape (different branch name) must NOT trip it
    # -- proves the oracle is sensitive to `main...HEAD` specifically,
    # not to `git diff` in general (which appears legitimately elsewhere
    # in the file for the explicit-commit-range override).
    unrelated = "git diff <SHA1>..<SHA2>"
    assert not any(p.search(unrelated) for p in FORBIDDEN_PATTERNS), (
        "the forbidden-pattern oracle must not flag the unrelated "
        "explicit-commit-range override syntax"
    )


def test_marker_sweep_does_not_reinvoke_resolver():
    """The marker-sweep step's fenced code block must not carry a
    second, live invocation of review_scope.py. Code-quality review
    (Task 5 round 2, finding F1) demonstrated that mutating the grep to
    `$(python3 review_scope.py)` still passed the old
    `"review_scope.py" in marker_sweep` check, because that check
    matched the surrounding prose sentence, not the code block. A
    second invocation is a second network fetch (git fetch) -- Step 4
    must reuse Step 1's already-resolved file list, never recompute it."""
    text = _text()
    marker_sweep = _marker_sweep_section(text)
    blocks = _fenced_code_blocks(marker_sweep)
    assert blocks, (
        "the marker-sweep step must still carry its fenced grep command"
    )
    for block in blocks:
        assert not RESOLVER_CALL_PATTERN.search(block), (
            f"the marker-sweep code block re-invokes review_scope.py: "
            f"{block!r} -- Step 4 must reuse Step 1's already-resolved "
            "file list, never recompute it"
        )


def test_resolver_reinvocation_oracle_catches_demonstrated_mutation():
    """Prove RESOLVER_CALL_PATTERN actually catches the exact mutation
    the code-quality reviewer demonstrated (F1) on a synthetic string,
    before trusting it against the real file -- and that it leaves the
    placeholder text (which only REFERS to review_scope.py's output,
    never calls it) alone."""
    mutated_block = 'grep -rn "LOOM-SIMPLIFY:" $(python3 review_scope.py)\n'
    assert RESOLVER_CALL_PATTERN.search(mutated_block), (
        "the reinvocation oracle must catch a second "
        "`python3 ... review_scope.py` call inside the marker-sweep "
        "code block"
    )
    placeholder = (
        'grep -rn "LOOM-SIMPLIFY:" '
        "<files from Step 1's review_scope.py output>\n"
    )
    assert not RESOLVER_CALL_PATTERN.search(placeholder), (
        "the oracle must not flag the placeholder text that only "
        "REFERS to review_scope.py's already-resolved output"
    )


def test_mixed_branch_hands_docs_arm_its_resolved_scope_subset():
    """The 'Mixed branch' bullet must hand the docs arm its `.md`
    subset as `resolved-scope`, via the same operative hand-off shape
    required of the docs-only bullet. Without this, a mixed branch
    dispatches requesting-docs-review with NO `resolved-scope` in the
    packet; its Step 1 falls into 'resolve it yourself', the resolver
    returns the FULL branch file list (not the `.md` subset), that
    list's own non-`.md` files trip requesting-docs-review's own
    docs-only predicate, and it routes straight back to
    requesting-code-review -- a mixed-branch routing cycle."""
    text = _text()
    routing = _routing_section(text)
    clause = _mixed_branch_docs_arm_clause(routing)
    assert HANDOFF_PATTERN.search(clause), (
        "the 'Mixed branch' bullet's docs-arm hand-off clause must "
        "carry an operative hand-off phrase naming `resolved-scope` as "
        "what the docs arm receives -- a mention anywhere else in the "
        "bullet (e.g. near the mint-marker sentence) does not tell the "
        "reader THIS clause hands it down"
    )


def test_mixed_branch_handoff_oracle_rejects_prose_mention_without_handoff():
    """Prove the check above discriminates -- a plausible WRONG bullet
    that mentions `resolved-scope` only in a trailing parenthetical
    (not as the object of a hand-off verb in the docs-arm clause) must
    fail, not pass by accident of a whole-bullet substring search."""
    wrong_routing = (
        "   - **Mixed branch** — the list contains both `.md` and "
        "non-`.md` files → per-file split: the non-`.md` files go to "
        "the code-reviewer panel below (Steps 2-3, diff scoped to "
        "those files); the `.md` files go to the docs arm per "
        "`requesting-docs-review`'s panel contract (its "
        "two-`docs-reviewer` dispatch + aggregation, run to produce a "
        "verdict — its own mint step does not fire here; this mirrors "
        "the docs-only bullet's resolved-scope hand-down). The "
        "orchestrator unions both arms' findings for the surfaced "
        "report..."
    )
    clause = _mixed_branch_docs_arm_clause(wrong_routing)
    assert "resolved-scope" in clause, (
        "sanity check: the synthetic wrong clause must still carry the "
        "bare token, to prove a bare-presence check would have passed it"
    )
    assert not HANDOFF_PATTERN.search(clause), (
        "the operative-handoff oracle must reject a clause that "
        "mentions `resolved-scope` without an instruction to hand it "
        "off within this clause"
    )
