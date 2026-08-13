"""Structural grep-tests keeping the three shipped writing-plans READMEs
(README.md / README.ja.md / README.zh-TW.md) in step with the per-task
field list in `references/plan-format.md`. Two schema changes are pinned
here, and the file grows one group per change that reaches the READMEs:

1. `Reuse-adequacy` -- Task 6 of
   docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md, later
   reshaped into the two-slot `Observed` / `Intended` form by
   docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md.
2. `Brief item covered` -- the widening from one referent kind to three
   plus a legal no-requirement value. See the comment above
   `REFERENT_KIND_TOKENS` for what these READMEs owe that field and,
   deliberately, what they do not.

A README is an orientation document, so these pins assert that it does
not MISINFORM and that it routes to the owning schema -- never that it
reproduces the grammar. A pin demanding the full grammar would turn each
README into a second drift surface.

Section scoping (not whole-file grep): each README's field list sits
between its `- **Description**:` bullet (present verbatim, in English,
in all three language variants -- field *names* are not translated,
only the surrounding prose) and the next `## `-level heading. Anchoring
on `- **Description**:` rather than the section's own heading avoids
depending on the heading text, which IS translated per language
(`## What each task carries` / `## 各タスクが持つもの` /
`## 每個任務帶什麼`). Verified no fenced code block sits between the
field-list bullets and the next heading in any of the three files
(README.md / README.ja.md / README.zh-TW.md lines 30-49), so a naive
"next '## ' heading" boundary is safe here -- unlike a sibling test's
fenced-example gotcha elsewhere in this plan's task set.

Limitation this grep cannot catch: it only proves the field *name*
"Reuse-adequacy" appears somewhere inside the scoped field-list section
of each file. It does not verify the surrounding prose actually
describes the field's semantics (behaviour-match claim / why-acceptable
clause) -- plan-format.md §`Reuse-adequacy` is the source of truth for
semantics; the README is a terse index, matching how the other five
pre-existing field bullets are also one-line summaries, not full specs.

Stdlib only (pathlib). Resolve READMEs relative to this test file.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WRITING_PLANS = REPO_ROOT / "skills" / "writing-plans"

READMES = {
    "README.md": WRITING_PLANS / "README.md",
    "README.ja.md": WRITING_PLANS / "README.ja.md",
    "README.zh-TW.md": WRITING_PLANS / "README.zh-TW.md",
}

START_ANCHOR = "- **Description**:"
END_ANCHOR = "\n## "

BRIEF_ITEM_ANCHOR = "- **Brief item covered**:"
BULLET_BOUNDARY = "\n- **"


def _field_list_section(path: Path) -> str:
    assert path.is_file(), f"README is absent at {path}"
    text = path.read_text(encoding="utf-8")
    start = text.index(START_ANCHOR)
    end = text.index(END_ANCHOR, start)
    return text[start:end]


def _brief_item_bullet(path: Path) -> str:
    """Return just the `Brief item covered` bullet of the field list.

    Scoped tighter than `_field_list_section` on purpose: the tokens the
    assertions below look for (`BI-`, `change-folder`) are ordinary words
    elsewhere in this skill's prose, so a section-wide grep would let a
    neighbouring bullet satisfy a claim about THIS field. The bullet runs
    to whichever comes first: the next `- **`-opened bullet, or the blank
    line that closes the list. The blank-line boundary matters because this
    bullet is currently the LAST in the list -- without it the slice would
    swallow the trailing paragraph and let prose outside the field list
    satisfy the assertions.
    """
    section = _field_list_section(path)
    start = section.index(BRIEF_ITEM_ANCHOR)
    body_start = start + len(BRIEF_ITEM_ANCHOR)
    boundaries = [
        idx
        for idx in (
            section.find(BULLET_BOUNDARY, body_start),
            section.find("\n\n", body_start),
        )
        if idx != -1
    ]
    return section[start:] if not boundaries else section[start : min(boundaries)]


def test_readmes_list_reuse_adequacy_field():
    """Each of the three READMEs' per-task field list must mention the
    Reuse-adequacy field Task 2 added to plan-format.md's schema --
    scoped to the field-list section itself (between the `Description`
    bullet and the next heading), not a whole-file grep, so a mention
    elsewhere in the file (e.g. a changelog line) cannot satisfy this."""
    for name, path in READMES.items():
        section = _field_list_section(path)
        assert "Reuse-adequacy" in section, (
            f"{name}: per-task field list does not mention "
            "Reuse-adequacy (scoped to the section between the "
            "Description bullet and the next '## ' heading)"
        )


# The three marker tokens, transcribed verbatim from the ## Notes PIN in
# docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md --
# never translated, never re-derived, checkable character-for-character
# against that one source.
MARKER_TOKENS = [
    "read <repo-relative-path>:<line>",
    "inferred from docstring",
    "unverified assumption — <what would settle it>",
]


def test_readmes_mirror_the_two_slot_shape():
    """The single-line `Reuse-adequacy` schema (behaviour-match claim +
    why-acceptable clause in one author-written field) was replaced in
    plan-format.md by a two-slot block: `Observed` (report, ends in a
    source marker) and `Intended` (specification) -- with no author-side
    adequacy verdict. Each README's field-list section must mirror this:
    name both slots and carry all three marker tokens verbatim (English
    tokens even in the ja/zh-TW locales -- only the surrounding prose is
    localized)."""
    for name, path in READMES.items():
        section = _field_list_section(path)
        assert "Observed" in section, (
            f"{name}: per-task field list does not name the `Observed` slot"
        )
        assert "Intended" in section, (
            f"{name}: per-task field list does not name the `Intended` slot"
        )
        for marker in MARKER_TOKENS:
            assert marker in section, (
                f"{name}: per-task field list is missing the verbatim "
                f"marker token {marker!r}"
            )

        # Presence alone cannot catch a slot swap: a mutant that relabels
        # the report clause `Intended` and the specification clause
        # `Observed` still contains both words and all three marker tokens,
        # so it passes every assertion above -- verified empirically against
        # such a mutant before this assertion was added (Task 7 of
        # docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md).
        # `Observed` (the report, per plan-format.md §`Reuse-adequacy`) must
        # precede `Intended` (the specification), and the source markers --
        # which close out the `Observed` clause -- must sit between the two
        # labels, not after `Intended`.
        #
        # Anchored on the bare word, this over-fires on two legitimate
        # edits (Task 7 revision round 1, reproduced against scratch
        # mutants before this fix): (a) a semantically-faithful rephrasing
        # that *previews* the bare word "Intended" ahead of the real
        # `Observed` clause, with no label/meaning swap; (b) a
        # cross-reference to the word "Intended" inside `Observed`'s own
        # prose -- exactly the phrasing plan-format.md §`Reuse-adequacy`
        # itself uses ("... belongs in `Intended`, not here"), so mirroring
        # the SSOT's own wording into a README would break CI for no
        # defect. Anchoring on the backtick-wrapped label *as it opens its
        # own slot* -- `` `Observed`( `` / `` `Intended`( `` (half- or
        # full-width paren, ja/zh-TW use the full-width `（` with no space)
        # -- ignores bare mentions and cross-references while still
        # catching a real slot swap, since a swap moves which label opens
        # which clause.
        observed_match = re.search(r"`Observed`\s*[(（]", section)
        intended_match = re.search(r"`Intended`\s*[(（]", section)
        assert observed_match, (
            f"{name}: no backtick-wrapped `Observed` slot opener found "
            "(expected `Observed` immediately followed by '(' or full-width '（')"
        )
        assert intended_match, (
            f"{name}: no backtick-wrapped `Intended` slot opener found "
            "(expected `Intended` immediately followed by '(' or full-width '（')"
        )
        observed_idx = observed_match.start()
        intended_idx = intended_match.start()
        assert observed_idx < intended_idx, (
            f"{name}: `Observed` (report) must appear before `Intended` "
            "(specification) -- slot order looks inverted"
        )
        for marker in MARKER_TOKENS:
            marker_idx = section.index(marker)
            assert observed_idx < marker_idx < intended_idx, (
                f"{name}: source marker {marker!r} must sit between the "
                "`Observed` and `Intended` labels (it closes out the "
                "`Observed` report clause) -- found outside that span, "
                "suggesting a slot swap"
            )


# `Brief item covered` was widened from a single referent kind (a quote from
# the brief) to three, plus a legal no-requirement value -- see
# plan-format.md's field block and its §`Brief item covered`. The two tests
# below are the consumer-census pin for that widening: the READMEs are
# orientation documents, so they are NOT required to restate the grammar,
# only to stop describing the field as quote-only and to route the reader to
# the schema that owns it. Anything stricter would make the README a second
# drift surface -- the failure mode
# docs/loom/memory/widening-a-value-grammar-needs-a-consumer-census-at-plan-time.md
# and this file's own `Reuse-adequacy` docstring both warn about.
#
# Tokens are asserted verbatim and untranslated in all three locales, on the
# same rule the MARKER_TOKENS above follow: these are literal strings a plan
# author types into a plan file, not prose to localize.
REFERENT_KIND_TOKENS = {
    "change-folder join key (kind b)": "change-folder",
    "brief-item identifier (kind c)": "BI-",
}
NO_REQUIREMENT_VALUE = "none — <reason>"
SCHEMA_AUTHORITY = "references/plan-format.md"


def test_readmes_state_all_three_brief_item_referent_kinds():
    """The `Brief item covered` bullet must not describe the field as
    accepting only a quote/reference from the brief. All three referent
    kinds are legal, and a reader told otherwise writes a plan that the
    plan-document-reviewer accepts but that silently drops the join-key and
    identifier forms from the author's option set."""
    for name, path in READMES.items():
        bullet = _brief_item_bullet(path)
        for kind, token in REFERENT_KIND_TOKENS.items():
            assert token in bullet, (
                f"{name}: the `Brief item covered` bullet does not mention "
                f"the {kind} referent kind (expected the verbatim token "
                f"{token!r}); the field reads as quote-only"
            )


def test_readmes_state_the_no_requirement_value_and_its_authority():
    """Two further things the bullet must carry: the legal `none — <reason>`
    value (without it, a task delivering no brief outcome gets forced into a
    false citation, which reads as satisfied to every downstream reader), and
    a pointer to plan-format.md as the authority -- the README summarizes the
    grammar, it does not own it."""
    for name, path in READMES.items():
        bullet = _brief_item_bullet(path)
        assert NO_REQUIREMENT_VALUE in bullet, (
            f"{name}: the `Brief item covered` bullet does not carry the "
            f"legal no-requirement value {NO_REQUIREMENT_VALUE!r} verbatim "
            "(em-dash, mandatory reason placeholder)"
        )
        assert SCHEMA_AUTHORITY in bullet, (
            f"{name}: the `Brief item covered` bullet does not point at "
            f"{SCHEMA_AUTHORITY} as the owning schema, so a reader cannot "
            "tell the README is a summary rather than the grammar itself"
        )
