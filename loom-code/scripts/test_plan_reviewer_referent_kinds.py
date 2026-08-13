"""Structural row-scoped test for Task 10 of
`docs/loom/plans/2026-08-13-brief-item-addressability.md`.

`plan-document-reviewer-prompt.md` is a prompt/contract artifact, not
executable code: nothing importable observes whether a reviewer applies
Check 3 or Check 9. This file IS the instruction that reviewer reads, so
its correctness condition is the PRESENCE of the load-bearing phrases —
same convention as `test_check16_prose_row.py` /
`test_plan_document_reviewer_check17.py`.

Every assertion slices the check's OWN table row (`| 3 | … |`, `| 9 | … |`)
rather than searching the whole document — the prompt is long, and a
whole-file grep would stay green if the added text migrated into a
neighbouring check's row, which is exactly the edit that silently
un-teaches the check that needed it. Row-slicing precedent:
`test_plan_obligation_sweep.py`'s `^\\|\\s*8\\s*\\|` slice.

Presence alone is not enough. A checks row must enumerate enough to be
executable by a reviewer reading only that table, so the row legitimately
restates part of a grammar that `plan-format.md` owns — and a restatement
that nothing binds to its source is free to desync from it silently. The
second test here therefore pins AGREEMENT rather than absence: the
referent-kind letters and the grammar tokens the prompt carries must equal
the ones `plan-format.md`'s `Brief item covered` field entry declares, so
neither side can move alone. Instrument precedent — a containment pin over
a transcribed table survived a narrowing that desynced the copy, and was
replaced with structural equality against the shipped source:
`docs/loom/memory/a-narrowing-that-leaves-a-substring-passes-every-containment-pin.md`.

Stdlib only (pathlib + re).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PROMPT_MD = (
    REPO_ROOT
    / "loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md"
)

FORMAT_MD = REPO_ROOT / "loom-code/skills/writing-plans/references/plan-format.md"

# A referent-kind enumeration marker: `(a)`, `(b)`, `(c)`. Lower-case only, so
# citation markers like `(R5)` are not mistaken for a fourth kind.
_KIND_LETTER_RE = re.compile(r"\((?P<letter>[a-z])\)")

# A grammar token: a backticked span carrying a `<placeholder>` — the shapes a
# plan author must type verbatim (`BI-<n>`, `none — <reason>`, the join key).
# Backticked PROSE (`plan-format.md`, `Brief item covered`, a bare `none`) has
# no angle brackets and is excluded: only the grammar is SSOT-owned.
_GRAMMAR_TOKEN_RE = re.compile(r"`([^`]*<[^`]*>[^`]*)`")


def _cells(check_number: int) -> tuple[str, str]:
    """Return (check_cell, failure_cell) of one numbered checks-table row.

    Splitting on `|` is safe: the checks table's cells carry no pipes.
    """
    text = PROMPT_MD.read_text(encoding="utf-8")
    match = re.search(rf"^\|\s*{check_number}\s*\|.*$", text, re.MULTILINE)
    assert match, (
        f"expected a Check {check_number} row (`| {check_number} | … |`) in "
        f"the checks table of {PROMPT_MD}"
    )
    parts = [c.strip() for c in match.group(0).strip().strip("|").split("|")]
    assert len(parts) == 3, (
        f"Check {check_number} row does not have exactly 3 cells "
        f"(number / check / failure); got {len(parts)}"
    )
    return parts[1], parts[2]


def _brief_item_field_entry() -> str:
    """Return `plan-format.md`'s `Brief item covered` field-schema entry.

    The entry spans from its own `- **Brief item covered**:` bullet to the
    next top-level field bullet; its continuation lines are indented. The
    `<` anchors on the schema entry, whose value is a placeholder — the
    file's worked-example task blocks repeat the same field name carrying a
    literal quoted value instead.
    """
    lines = FORMAT_MD.read_text(encoding="utf-8").splitlines()
    starts = [
        i
        for i, line in enumerate(lines)
        if line.startswith("- **Brief item covered**: <")
    ]
    assert len(starts) == 1, (
        f"expected exactly one `- **Brief item covered**:` field entry in "
        f"{FORMAT_MD}; found {len(starts)}"
    )
    start = starts[0]
    end = start + 1
    while end < len(lines) and not lines[end].startswith("- **"):
        end += 1
    return "\n".join(lines[start:end])


def test_checks_accept_the_bi_referent_and_the_none_value():
    """Check 3 must enumerate referent kind (c) — the `BI-<n>` identifier —
    alongside (a) and (b), and Check 9 must state that the no-requirement
    value `none — <reason>` satisfies it while a bare `none` or an empty
    reason still fails. Both point at `plan-format.md` as the SSOT for the
    grammar rather than restating it.
    """
    check3, _fail3 = _cells(3)

    # --- Check 3: kind (c) is enumerated in Check 3's OWN row --------------
    assert "(a)" in check3 and "(b)" in check3 and "(c)" in check3, (
        "Check 3 must enumerate all three referent kinds (a), (b) and (c) — "
        f"found: {check3!r}"
    )
    assert "BI-<n>" in check3, (
        "Check 3 must name the `BI-<n>` identifier as referent kind (c); a "
        "reviewer reading only this row would otherwise gap a task that "
        "cites one"
    )
    assert "plan-format.md" in check3, (
        "Check 3 must point at `plan-format.md` as the SSOT for the referent "
        "kinds instead of being the second place the grammar is defined"
    )

    check9, fail9 = _cells(9)

    # --- Check 9: the no-requirement value satisfies the check ------------
    assert "none — <reason>" in check9, (
        "Check 9 must name the no-requirement value `none — <reason>` as "
        "satisfying it — a task delivering no brief outcome is not an orphan"
    )
    assert "plan-format.md" in check9, (
        "Check 9 must point at `plan-format.md` as the SSOT for the value "
        "rather than restating its grammar"
    )
    assert "not an orphan" in check9, (
        "Check 9 must say in its own row that a task carrying the "
        "no-requirement value is NOT an orphan — the check's whole verdict "
        "for that task turns on this"
    )

    # --- the reason stays mandatory: the old gap class is not deleted -----
    assert "mandatory" in check9 and "non-empty reason" in check9, (
        "Check 9 must state that the reason is mandatory and non-empty — a "
        "reason-optional reading turns the value into a silent opt-out from "
        "brief traceability"
    )
    assert "bare `none`" in check9 and "whitespace-only" in check9, (
        "Check 9's own row must still reject a bare `none`, an empty reason "
        "and a whitespace-only reason"
    )
    assert "bare `none`" in fail9, (
        "Check 9's FAILURE cell must still fail a bare `none`; accepting any "
        "non-empty value would delete a real gap class"
    )
    assert "no brief traceability" in fail9, (
        "Check 9's failure cell must keep its original condition — a task "
        "whose field references nothing still fails"
    )


def test_check9_carries_fail_triggers_not_plan_formats_illustrations():
    """Check 9's row states the criteria a reviewer applies; the worked
    examples of what a no-brief-outcome task looks like belong to
    `plan-format.md` §`Brief item covered`, which the row already points at.

    Copying that illustration into the row buys the reviewer nothing — no
    verdict turns on it — while creating a second place it can be edited.
    """
    check9, _fail9 = _cells(9)

    assert "release administration" not in check9, (
        "Check 9's row reproduces `plan-format.md`'s illustrative list of "
        "no-brief-outcome tasks (release administration / version bump / "
        "manifest mirror). No fail-trigger reads it, so it is a gratuitous "
        "second copy — keep the pointer, drop the examples"
    )


def test_referent_grammar_in_the_prompt_agrees_with_plan_format():
    """The prompt's restated grammar must EQUAL what `plan-format.md`
    declares — not merely be contained in it.

    Check 3 must enumerate the same referent kinds the field entry declares
    (a kind added or retired on one side alone is drift), and the grammar
    tokens the two checks make a plan author type must be the same strings
    on both sides (an edited placeholder on one side alone is drift).
    """
    check3, _fail3 = _cells(3)
    check9, _fail9 = _cells(9)
    field_entry = _brief_item_field_entry()

    prompt_kinds = {m.group("letter") for m in _KIND_LETTER_RE.finditer(check3)}
    ssot_kinds = {m.group("letter") for m in _KIND_LETTER_RE.finditer(field_entry)}
    assert ssot_kinds, (
        f"no `(a)`-style referent-kind markers found in {FORMAT_MD}'s "
        "`Brief item covered` entry — the pin has lost its source"
    )
    assert prompt_kinds == ssot_kinds, (
        "Check 3's referent kinds disagree with the `Brief item covered` "
        f"entry in {FORMAT_MD}: prompt has {sorted(prompt_kinds)}, SSOT "
        f"declares {sorted(ssot_kinds)}. A kind added or retired on one side "
        "alone leaves the reviewer applying a grammar the format no longer "
        "has (or missing one it now has)"
    )

    prompt_tokens = set(_GRAMMAR_TOKEN_RE.findall(check3)) | set(
        _GRAMMAR_TOKEN_RE.findall(check9)
    )
    ssot_tokens = set(_GRAMMAR_TOKEN_RE.findall(field_entry))
    assert ssot_tokens, (
        f"no backticked `<placeholder>` grammar tokens found in {FORMAT_MD}'s "
        "`Brief item covered` entry — the pin has lost its source"
    )
    assert prompt_tokens == ssot_tokens, (
        "the referent grammar restated by Checks 3 and 9 disagrees with the "
        f"`Brief item covered` entry in {FORMAT_MD}: prompt carries "
        f"{sorted(prompt_tokens)}, SSOT declares {sorted(ssot_tokens)}. Both "
        "sides must be edited together — a plan author typing the prompt's "
        "form would otherwise fail the format's"
    )
