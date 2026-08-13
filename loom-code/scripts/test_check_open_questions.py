"""Tests for check_open_questions.py — reads a writing-plans plan document,
scopes the scan to its `## Open Questions` section only (per
`loom-code/skills/writing-plans/references/plan-format.md` §Plan-level
open-questions slot), and exits non-zero while any entry is unresolved or
the slot is absent or malformed.

Exercised as a CLI subprocess (the actual interface: one positional arg,
exit 0 / exit 1) rather than importing internals — same convention as
`test_check_scenario_coverage.py`.

Stdlib only (subprocess + pathlib).
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "check_open_questions.py"
REPO_ROOT = Path(__file__).resolve().parents[2]

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run(plan_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


def _write_plan(tmp_path: Path, body: str) -> Path:
    plan = tmp_path / "plan.md"
    plan.write_text(body, encoding="utf-8")
    return plan


def test_unresolved_question_exit_1(tmp_path):
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [OPEN] — which retry policy should the client use?\n",
    )
    result = _run(plan)
    assert result.returncode == 1, result.stdout
    assert "OQ-1" in result.stderr


def test_all_resolved_exit_0(tmp_path):
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [RESOLVED] — which retry policy? → resolved: exponential backoff\n"
        "- OQ-2 [RESOLVED] — which port? → resolved: 8080\n",
    )
    result = _run(plan)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


def test_wellformed_na_line_exit_0(tmp_path):
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "N/A — no unresolved question: brief left nothing undecided\n",
    )
    result = _run(plan)
    assert result.returncode == 0, result.stderr


def test_absent_heading_exit_1(tmp_path):
    """A missing heading must be diagnosed as ABSENT, not conflated with the
    present-but-empty-section case — a mutant that treats "no heading found"
    as an empty section string exits 1 with the same generic 'Open
    Questions' substring in both cases, so the message is pinned narrowly
    enough to tell the two failure modes apart."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Description: does stuff\n",
    )
    result = _run(plan)
    assert result.returncode == 1
    assert "no '## Open Questions' section found" in result.stderr
    assert "present but empty" not in result.stderr


def test_present_but_bare_section_exit_1(tmp_path):
    """A '## Open Questions' heading with no body at all (no entries, no
    N/A line) is malformed — distinct from the heading being absent
    entirely, and from a well-formed N/A declaration."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "## Task 1 — foo\n"
        "- Description: does stuff\n",
    )
    result = _run(plan)
    assert result.returncode == 1
    assert "present but empty" in result.stderr


def test_na_line_missing_reason_exit_1(tmp_path):
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "N/A — no unresolved question:\n",
    )
    result = _run(plan)
    assert result.returncode == 1
    assert "reason" in result.stderr.lower()


def test_malformed_entry_wrong_token_exit_1(tmp_path):
    """An entry whose bracketed token is neither `[OPEN]` nor `[RESOLVED]`
    is malformed — the grammar names exactly two legal tokens."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [BLOCKED] — which retry policy?\n",
    )
    result = _run(plan)
    assert result.returncode == 1
    assert "OQ-1" in result.stderr


# --- section scoping: an [OPEN]/[RESOLVED] token outside the section must
# never trigger a failure. Three positions, each pinned separately so a
# scanner correctly bounded to the section's slice by construction (not by
# accident) satisfies all three — plan documents in this repo are saturated
# with these tokens in prose describing the grammar itself (see the plan
# this task belongs to: docs/loom/plans/2026-08-13-open-question-dispatch-gate.md).


def test_open_token_in_decision_log_prose_is_out_of_scope(tmp_path):
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "N/A — no unresolved question: nothing outstanding\n\n"
        "## Decision Log\n\n"
        "- chose to spell status tokens [OPEN] and [RESOLVED] against the "
        "reviewer's own vocabulary — cost-of-change: none\n",
    )
    result = _run(plan)
    assert result.returncode == 0, result.stderr


def test_open_token_in_quoted_example_is_out_of_scope(tmp_path):
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "N/A — no unresolved question: nothing outstanding\n\n"
        "## Task 1 — foo\n"
        "- Description: entry form is `- OQ-<n> [OPEN] — <question text>`, "
        "quoted here as an example, not a real entry.\n",
    )
    result = _run(plan)
    assert result.returncode == 0, result.stderr


def test_open_token_in_fenced_code_block_is_out_of_scope(tmp_path):
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "N/A — no unresolved question: nothing outstanding\n\n"
        "## Task 1 — foo\n"
        "```markdown\n"
        "- OQ-1 [OPEN] — example entry inside a fence, never a declaration\n"
        "```\n",
    )
    result = _run(plan)
    assert result.returncode == 0, result.stderr


# --- exercised against a real artifact of this system ---


def test_real_plan_document_open_questions_section_passes():
    """This very plan (the arc that ships this checker) now carries a real
    '## Open Questions' section: two `[RESOLVED]` entries, each soft-wrapped
    across several physical lines, followed by an explanatory paragraph. The
    scanner must accept soft-wrap and prose — the SSOT
    (plan-format.md §Plan-level open-questions slot) specifies the entry
    form and the N/A line but never forbids either, unlike '## Decision
    Log', which pins entries to a single physical line explicitly. A
    scanner stricter than its own grammar is the defect this test guards
    against (found by dogfooding against this exact document).
    """
    plan_path = (
        REPO_ROOT / "docs" / "loom" / "plans"
        / "2026-08-13-open-question-dispatch-gate.md"
    )
    assert plan_path.is_file(), f"fixture plan missing at {plan_path}"

    result = _run(plan_path)
    assert result.returncode == 0, (
        "the real plan's Open Questions section is well-formed (soft-wrapped "
        f"[RESOLVED] entries + prose) and must pass\nstderr:\n{result.stderr}"
    )


def test_absent_open_questions_section_still_fails(tmp_path):
    """Fixture-based regression guard for the absent-heading path, now that
    the real-plan fixture above no longer exercises it (the real plan grew
    its own section). Mirrors test_absent_heading_exit_1 deliberately —
    kept as a separate test so the absent-heading path stays covered
    independently of the real-plan document's contents."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Description: does stuff\n",
    )
    result = _run(plan)
    assert result.returncode == 1
    assert "no '## Open Questions' section found" in result.stderr


def test_softwrapped_resolved_entry_continuation_line_contains_open_token(tmp_path):
    """A soft-wrapped `[RESOLVED]` entry's continuation line is not scanned
    for the entry grammar at all — only the entry's own marker position
    (`- OQ-<n> [TOKEN]`) counts, so a continuation line that happens to
    contain the literal substring `[OPEN]` must not flip the verdict."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [RESOLVED] — which retry policy should the client use? A prior\n"
        "  draft left this [OPEN] but the team settled on exponential backoff.\n"
        "  → resolved: exponential backoff\n",
    )
    result = _run(plan)
    assert result.returncode == 0, result.stderr


def test_explanatory_prose_in_section_containing_open_token(tmp_path):
    """Explanatory prose after the entry list — not itself an entry — must
    be ignored even when it contains the literal substring `[OPEN]`."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [RESOLVED] — which port? → resolved: 8080\n\n"
        "This section discusses the [OPEN] and [RESOLVED] tokens in general "
        "terms, not as a real entry.\n",
    )
    result = _run(plan)
    assert result.returncode == 0, result.stderr


def test_malformed_entry_still_errors_and_names_it(tmp_path):
    """The fix for soft-wrap/prose must NOT regress to 'ignore every line
    that fails to parse' — a line that begins with the entry marker
    (`- OQ-`) but is not well-formed (here: a typo'd token `[OPNE]`) must
    still be reported, by name, as a malformed entry. Silently skipping it
    would let an unresolved question through disguised as prose."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [OPNE] — which retry policy should the client use?\n",
    )
    result = _run(plan)
    assert result.returncode == 1
    assert "OQ-1" in result.stderr
    assert "malformed" in result.stderr.lower()


def test_prose_only_section_with_no_entry_and_no_na_line_fails(tmp_path):
    """A section whose body is prose only — no well-formed entry, no
    well-formed N/A line — must still be an error: fill-or-declare requires
    one or the other, and a prose-only body satisfies neither."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "We discussed several things during planning but never wrote them "
        "up as entries.\n",
    )
    result = _run(plan)
    assert result.returncode == 1, result.stdout


# --- revision round: fatal false negatives (duplicate section, fenced
# heading decoy), the mirror false positive (fence inside section body),
# the reused-identifier warning, and a lowercase-token regression guard.


def test_duplicate_open_questions_sections_exit_1(tmp_path):
    """Two `## Open Questions` sections in one document — the FIRST a
    clean N/A, the SECOND holding a real `[OPEN]` entry. A scanner that
    takes the first heading match unconditionally (the pre-fix defect)
    exits 0, silently swallowing the real unresolved question in the
    second section. plan-format.md requires exactly one such section;
    finding two is a malformed plan and must fail loudly rather than
    picking one."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Task-flow diagram\n\n"
        "N/A — none\n\n"
        "## Open Questions\n\n"
        "N/A — no unresolved question: first clean copy\n\n"
        "## Task 1 — foo\n"
        "- Description: x\n\n"
        "## Open Questions\n\n"
        "- OQ-7 [OPEN] — real unresolved question hidden in duplicate section\n\n"
        "## Task 2 — bar\n",
    )
    result = _run(plan)
    assert result.returncode == 1, result.stdout
    assert "Open Questions" in result.stderr


def test_fenced_open_questions_heading_decoy_does_not_mask_real_section(tmp_path):
    """A fenced code block earlier in the document quoting the grammar —
    a `## Open Questions` heading plus a well-formed entry, as a worked
    example — must not be mistaken for THE section. The real section,
    further down, holding a genuine `[OPEN]` entry, must still be found
    and must still fail. This shape is not hypothetical: plan-format.md
    and this arc's own plan quote the grammar exactly like this."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Task 1 — foo\n\n"
        "Example grammar:\n"
        "```markdown\n"
        "## Open Questions\n\n"
        "- OQ-1 [RESOLVED] — example entry shown for illustration → resolved: n/a\n"
        "```\n\n"
        "## Open Questions\n\n"
        "- OQ-9 [OPEN] — the REAL unresolved question, hidden past the decoy window\n",
    )
    result = _run(plan)
    assert result.returncode == 1, result.stdout
    assert "OQ-9" in result.stderr


def test_fence_inside_section_body_example_entry_ignored(tmp_path):
    """A fenced code block INSIDE the real `## Open Questions` section
    body, quoting an `[OPEN]` example for illustration, must not be read
    as a real entry — the mirror defect of the decoy-heading case above.
    The real entry here is `[RESOLVED]`, so the plan is actually clean
    and must exit 0."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [RESOLVED] — real entry → resolved: yes\n\n"
        "Grammar reminder:\n"
        "```markdown\n"
        "- OQ-2 [OPEN] — example only, inside a fence, not a real declaration\n"
        "```\n\n"
        "## Task 1 — foo\n",
    )
    result = _run(plan)
    assert result.returncode == 0, result.stderr


def test_reused_oq_identifier_warns_but_does_not_change_exit_code(tmp_path):
    """Two entries reusing the same `OQ-<n>` id violates plan-format.md's
    monotonic/never-reused rule for `OQ-<n>` — this arc's plan Notes
    commit this checker to warn on stderr (first-wins), mirroring
    `collect_brief_item_ids`' duplicate-id handling
    (check_scenario_coverage.py:270). Both entries here are otherwise
    well-formed and RESOLVED, so the exit code must stay 0 — a warning
    never changes the exit code; only an [OPEN] entry does that, via the
    existing check."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [RESOLVED] — which port? → resolved: 8080\n"
        "- OQ-1 [RESOLVED] — reused id by mistake → resolved: n/a\n",
    )
    result = _run(plan)
    assert result.returncode == 0, result.stderr
    assert "OQ-1" in result.stderr
    assert "declared twice" in result.stderr


def test_reused_oq_identifier_mixed_open_and_resolved_still_errors(tmp_path):
    """A duplicate id where the SECOND occurrence is [OPEN] (the first is
    [RESOLVED]) must still exit 1 — the duplicate warning's first-wins
    language does not mean the second entry is skipped or ignored. Every
    entry is evaluated for its own status regardless of duplicate-id
    bookkeeping; only the STDERR wording changes what it claims about
    that (fixed by this task — the prior "treated as canonical" phrasing
    implied the repeat was disregarded, which contradicts this exact
    fail-closed behavior)."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [RESOLVED] — which port? → resolved: 8080\n"
        "- OQ-1 [OPEN] — reused id, still unresolved\n",
    )
    result = _run(plan)
    assert result.returncode == 1, result.stderr
    assert "OQ-1" in result.stderr
    assert "declared twice" in result.stderr
    assert "unresolved open question OQ-1" in result.stderr
    assert "treated as canonical" not in result.stderr, (
        "the warning must not claim the repeat is disregarded — it is "
        "still evaluated and can still fail the check, as this exit "
        "code demonstrates"
    )
    assert "first-seen" in result.stderr, (
        "the warning must describe line-first bookkeeping without "
        "implying the later entry goes unevaluated"
    )


# --- widened "looks like an entry" net: non-dash bullets and no-bullet
# lines that attempt an OQ-<n> [TOKEN] entry must still be caught as
# malformed, not silently ignored as prose (the fatal false-negative found
# by whole-branch review: `_LOOKS_LIKE_ENTRY` was anchored `^-`, so any
# other bullet character fell through to the ignored-prose branch).


def test_orchestrator_fixture_mixed_bullets_all_flagged(tmp_path):
    """The exact fixture from whole-branch review: one well-formed
    `[RESOLVED]` entry plus three malformed attempts (star bullet, plus
    bullet, no bullet at all), all `[OPEN]`. Previously this exited 0 with
    'clean — no unresolved entries', silently swallowing three unresolved
    questions. Must now exit 1 and name all three."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [RESOLVED] — settled → resolved: yes\n"
        "* OQ-2 [OPEN] — star bullet\n"
        "+ OQ-3 [OPEN] — plus bullet\n"
        "OQ-4 [OPEN] — no bullet at all\n",
    )
    result = _run(plan)
    assert result.returncode == 1, result.stdout
    assert "OQ-2" in result.stderr
    assert "OQ-3" in result.stderr
    assert "OQ-4" in result.stderr


@pytest.mark.parametrize(
    "bullet",
    ["*", "+", ">", ">-", "> -", ""],
    ids=["star", "plus", "blockquote-nospace", "blockquote-dash",
         "blockquote-dash-space", "no-bullet"],
)
@pytest.mark.parametrize("token", ["OPEN", "RESOLVED"])
def test_non_dash_bullet_entry_is_malformed_regardless_of_token(
    tmp_path, bullet, token
):
    """Every non-`-` bullet variant (star, plus, blockquote in its several
    spellings, and no bullet at all) must route to the malformed-entry
    branch and fail loudly — for BOTH tokens. Malformed is malformed
    regardless of whether the token spells OPEN or RESOLVED; only the
    strict `- OQ-<n> [TOKEN] — text` grammar is well-formed."""
    prefix = f"{bullet} " if bullet else ""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        f"{prefix}OQ-1 [{token}] — bullet variant {bullet!r}\n",
    )
    result = _run(plan)
    assert result.returncode == 1, (
        f"bullet={bullet!r} token={token} should be malformed, got exit 0"
    )
    assert "OQ-1" in result.stderr
    assert "malformed" in result.stderr.lower()


def test_prose_mentioning_oq_id_without_bracket_is_not_flagged(tmp_path):
    """The boundary case: a line that merely MENTIONS an `OQ-<n>` id in
    prose — no bracketed token attempt following it — must stay ignored,
    exit 0. Flagging this would be a new false positive, the opposite
    defect from the one being fixed."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [RESOLVED] — real entry → resolved: yes\n\n"
        "OQ-1 was settled last week after some back-and-forth in review.\n",
    )
    result = _run(plan)
    assert result.returncode == 0, result.stderr


def test_lowercase_token_is_malformed(tmp_path):
    """Regression guard: a mutation that accepts lowercase `[open]` /
    `[resolved]` tokens would silently let an unresolved question through
    disguised as well-formed (or drop it from the malformed-entry
    diagnostic entirely). The grammar pins the token to exactly
    `OPEN`/`RESOLVED`, uppercase — this was previously unguarded and
    survived all 16 tests as a mutant."""
    plan = _write_plan(
        tmp_path,
        "# Plan: x\n\n"
        "## Open Questions\n\n"
        "- OQ-1 [open] — which retry policy should the client use?\n",
    )
    result = _run(plan)
    assert result.returncode == 1
    assert "malformed" in result.stderr.lower()
    assert "OQ-1" in result.stderr
