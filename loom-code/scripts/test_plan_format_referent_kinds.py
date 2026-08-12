"""Structural pin for the `Brief item covered` referent kinds in
`writing-plans/references/plan-format.md` (Task 2 of
`docs/loom/plans/2026-08-13-brief-item-addressability.md`).

plan-format.md is a prompt/contract artifact, not executable code: nothing
importable observes whether a plan author discovers, from the schema alone,
that (c) a `BI-<n>` id declared by the source brief is an accepted referent,
that `none — <reason>` is a legal no-requirement value with a MANDATORY
reason, and how a two-item tie breaks. This file IS the schema the author
reads, so its correctness condition is the presence of those three rules in
the `Brief item covered` definition.

Scope discipline: every assertion runs against a SLICE of the file — the
per-task schema's `- **Brief item covered**:` field block, and the
`#### `Brief item covered`` prose section — never the whole file. plan-format.md
is long and carries worked examples that mention the field, so a whole-file
grep would stay green after the definition itself was gutted
(docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md). The slices
are fence-aware so a heading inside a ```markdown example cannot end a slice.

The companion pin `test_traceability_generalization.py` forbids a SECOND
traceability field; everything asserted here therefore rides inside the ONE
existing field.

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

PLAN_FORMAT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-format.md"
)


def _text() -> str:
    assert PLAN_FORMAT_MD.is_file(), f"plan-format.md is absent at {PLAN_FORMAT_MD}"
    return PLAN_FORMAT_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _field_block(text: str) -> str:
    """The per-task schema's `Brief item covered` field entry: the line
    starting `- **Brief item covered**:` plus its continuation lines, ending
    at the next `- **<Field>**:` entry or the fence close."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("- **Brief item covered**:"):
            start = i
            break
    assert start is not None, (
        "the per-task schema no longer carries a `- **Brief item covered**:` "
        "field entry"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        stripped = lines[j].strip()
        if stripped.startswith("```") or re.match(r"^- \*\*[^*]+\*\*:", stripped):
            end = j
            break
    return "\n".join(lines[start:end])


def _section(text: str, heading_prefix: str) -> str:
    """Fence-aware slice of the section opened by `heading_prefix`, ending at
    the next heading of the same or shallower depth OUTSIDE a code fence."""
    lines = text.splitlines()
    depth = len(heading_prefix) - len(heading_prefix.lstrip("#"))
    start = None
    in_fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if start is None and line.startswith(heading_prefix):
            start = i
            continue
        if start is not None:
            m = re.match(r"^(#{1,6}) ", line)
            if m and len(m.group(1)) <= depth:
                return "\n".join(lines[start:i])
    assert start is not None, (
        f"plan-format.md carries no section opened by {heading_prefix!r} — the "
        "`Brief item covered` definition must state the BI referent kind, the "
        "`none — <reason>` value, and the tie-break rule in its own subsection"
    )
    return "\n".join(lines[start:])


def _per_task_region(text: str) -> str:
    """The `### Per-task block` region — the schema section a plan author reads
    to learn the per-task fields, ending at the next `###`/`##` heading. The
    field's prose subsection is sliced from HERE, not from the whole file, so
    the same prose relocated to another part of plan-format.md (out of the
    schema a field-reader consults) does not keep this pin green."""
    return _section(text, "### Per-task block")


def _definition(text: str) -> str:
    """Everything that defines the field: the schema entry + its prose section."""
    region = _per_task_region(text)
    return _field_block(region) + "\n" + _section(region, "#### `Brief item covered`")


def _sentences(block: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", _norm(block)) if s]


def _sentence_with(block: str, needle: str) -> str:
    hits = [s for s in _sentences(block) if needle.lower() in s.lower()]
    assert hits, f"no sentence in the definition mentions {needle!r}"
    return hits[0]


# --- addition 1: the BI-<n> referent kind ----------------------------------

# Vocabulary the id convention (handoff-brief-format.md §Brief item
# identifiers) owns. Pointing at that section is required; restating what it
# says is the regression — so these phrases must NOT appear in the definition.
# Negative assertions misfire when a banned phrase has a legitimate second
# sense, so each is chosen for a sense only a rules-copy carries, and the
# two-word forms are deliberate:
#   "monotonic"          — names the numbering invariant; the word has no other
#                          use in a plan schema.
#   "next unused"        — how a new item's number is picked; only a copy of
#                          the assignment rule needs to say it.
#   "never reused" /     — the two immutability clauses. Banned as phrases, not
#   "never renumbered"     as bare `reused` / `renumber`, because a plan's own
#                          TASKS are legitimately renumbered and one referent is
#                          legitimately reused by two tasks (both probed by
#                          test_a_non_copying_neighbour_sentence_still_passes).
#   "slugified" /        — the mechanism words of the authored-not-derived
#   "never derived" /      clause; nothing else here derives anything.
#   "authored-not-derived"
#   "number is retired" /— the retirement clause, anchored on `number` because
#   "numbers are retired"  the shipped POINTER legitimately says the rules for
#                          ids "formed, assigned, retired" live elsewhere, and
#                          a bare `retired` would flag that pointer itself.
# Residual gap, stated rather than hidden: a restatement that paraphrases every
# one of these away would still pass. The pin raises the cost of copying and
# catches the realistic copy-paste, it does not decide prose intent.
_ID_RULE_VOCABULARY = (
    "monotonic",
    "next unused",
    "never reused",
    "never renumbered",
    "slugified",
    "never derived",
    "authored-not-derived",
    "number is retired",
    "numbers are retired",
)


def _assert_bi_referent_kind(definition: str) -> None:
    low = definition.lower()
    assert "bi-" in low, (
        "the definition must name the `BI-<n>` identifier as an accepted "
        "referent kind"
    )
    assert "(c)" in low, (
        "the referent-kind enumeration must reach a third kind `(c)` — the "
        "`BI-<n>` id — alongside the existing quote (a) and join-key (b) kinds"
    )
    assert "handoff-brief-format.md" in low, (
        "the BI referent kind must POINT at the brief schema that owns the "
        "convention (handoff-brief-format.md §Brief item identifiers), not "
        "restate its rules — SSOT discipline"
    )
    assert "brief item identifiers" in low, (
        "the pointer must name the owning section, `§Brief item identifiers`"
    )
    normalized = _norm(definition).lower()
    for phrase in _ID_RULE_VOCABULARY:
        assert phrase not in normalized, (
            f"SSOT discipline: found {phrase!r} — vocabulary the id convention "
            "owns — inside the `Brief item covered` definition. The pointer at "
            "handoff-brief-format.md §Brief item identifiers must REPLACE the "
            "rules, not sit next to a copy of them; a copy drifts from the "
            "schema that owns it while this pin stays green"
        )
    bi_sentence = _sentence_with(definition, "BI-")
    for negation in ("is not an accepted", "is never an accepted",
                     "is not a valid referent", "is not accepted"):
        assert negation not in bi_sentence.lower(), (
            f"the BI referent kind is declared ACCEPTED; found {negation!r} "
            f"in: {bi_sentence!r}"
        )


# --- addition 2: the `none — <reason>` value -------------------------------

def _assert_none_value(definition: str) -> None:
    norm = _norm(definition)
    assert "none — <reason>" in norm, (
        "the definition must declare the legal no-requirement value "
        "`none — <reason>` verbatim"
    )
    reason_sentence = _sentence_with(definition, "none — <reason>")
    window = _norm(
        " ".join(s for s in _sentences(definition)
                 if "none" in s.lower() or "reason" in s.lower())
    ).lower()
    assert "mandatory" in window or "is required" in window, (
        "the reason must be declared MANDATORY — found no mandatory/required "
        f"wording in: {window!r}"
    )
    assert "optional" not in window, (
        "the reason is mandatory, never optional — found `optional` in the "
        f"none-value wording: {window!r}"
    )
    assert "empty" in window and "whitespace" in window, (
        "the definition must state that an empty or whitespace-only reason is "
        f"invalid; got: {window!r}"
    )
    assert "false citation" in window, (
        "the definition must state WHY the value exists: a task delivering no "
        "brief outcome must not be forced into a false citation, which looks "
        f"satisfied and is worse than no citation. Got: {window!r}"
    )
    assert reason_sentence, "unreachable"


# --- addition 3: the tie-break rule ----------------------------------------

def _assert_tiebreak(definition: str) -> None:
    low = _norm(definition).lower()
    assert "tie-break" in low, (
        "the definition must carry a tie-break rule for a task that plausibly "
        "delivers two brief items"
    )
    primary = _sentence_with(definition, "primary referent")
    plow = primary.lower()
    assert "red test" in plow, (
        "the primary referent is the item the task's RED test asserts; that "
        f"sentence does not name the RED test: {primary!r}"
    )
    assert "files touched" not in plow, (
        "the primary referent must NOT be anchored on `Files touched` — that "
        f"alternative is the REJECTED one: {primary!r}"
    )
    rationale = _norm(
        " ".join(s for s in _sentences(definition)
                 if "files touched" in s.lower() or "definition of done" in s.lower())
    ).lower()
    assert "definition of done" in rationale, (
        "the tie-break rationale must say the RED test is this repo's "
        f"definition of done — the least arbitrary anchor. Got: {rationale!r}"
    )
    assert "files touched" in rationale and "effort" in rationale, (
        "the rationale must name the rejected alternative (the item most of "
        f"`Files touched` serves) as tracking effort, not outcome: {rationale!r}"
    )


def test_bi_referent_none_value_and_tiebreak_are_declared():
    """plan-format.md's `Brief item covered` definition declares all three:
    the `BI-<n>` referent kind (c) pointing at the brief schema, the legal
    `none — <reason>` value with a mandatory reason, and the RED-test
    tie-break for the primary referent."""
    definition = _definition(_text())
    _assert_bi_referent_kind(definition)
    _assert_none_value(definition)
    _assert_tiebreak(definition)


def _mutated(definition: str, paragraph: str) -> str:
    """The shipped definition with `paragraph` added next to it — the shape of
    the regression this pin exists to catch: the pointer sentence kept verbatim
    AND the pointed-at rules copied in beside it."""
    return definition + "\n\n" + paragraph


# The reviewer's mutation, verbatim in shape: the id-formation rules restated
# in `plan-format.md` while the pointer sentence stays untouched.
_ID_RULES_COPIED_IN = (
    "**How a `BI-<n>` id is formed, assigned and retired.** The brief's author "
    "types the identifier; it is never derived by slugifying the item's "
    "heading. A new item takes the next unused number, monotonic across the "
    "brief. Items already present are never renumbered, and when an item is "
    "deleted its number is retired and never reused."
)


def test_copying_the_id_rules_beside_the_pointer_is_rejected():
    """A future author who keeps the pointer AND restates the id rules must
    trip the pin. Runs the PRODUCTION assertion (`_assert_bi_referent_kind`)
    against the mutant, not a stand-in, so the pin's real wording is what is
    being measured."""
    mutant = _mutated(_definition(_text()), _ID_RULES_COPIED_IN)
    try:
        _assert_bi_referent_kind(mutant)
    except AssertionError:
        return
    raise AssertionError(
        "the definition may point at handoff-brief-format.md §Brief item "
        "identifiers but must not restate its rules; a full copy of the "
        "formation/assignment/retirement rules pasted beside the pointer was "
        "accepted"
    )


# A sentence that legitimately uses the *subjects* of the banned phrases
# without restating any rule — the false-positive probe for the negative
# assertion above. Each clause is one a future author could reasonably write
# in this file: plan tasks (not brief items) do get renumbered, one referent
# can be reused across tasks, and a retired id is a thing this file's
# tie-break prose may legitimately mention.
_LEGITIMATE_NEIGHBOUR = (
    "Renumbering a plan's tasks never changes a cited `BI-<n>` referent. Two "
    "tasks may reuse the same referent only when neither is the primary. A "
    "citation naming an id the brief has retired must fail loudly rather than "
    "resolve to the nearest surviving item."
)


def test_a_non_copying_neighbour_sentence_still_passes():
    """The negative assertion must not fire on prose that merely talks about
    renumbering, reuse or retirement without restating the convention — a
    banned-phrase pin whose phrases are too broad blocks correct edits."""
    _assert_bi_referent_kind(_mutated(_definition(_text()), _LEGITIMATE_NEIGHBOUR))


def test_still_one_traceability_field():
    """Guard the hard constraint from the same slice: the three additions ride
    inside `Brief item covered`; no competing field name appears."""
    low = _text().lower()
    for stray in ("spec item covered", "scenario covered",
                  "requirement covered", "change-folder covered"):
        assert stray not in low, f"a second traceability field appeared: {stray!r}"
