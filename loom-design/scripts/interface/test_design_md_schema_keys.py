"""Guards the frozen spec key sets in `design_md_spec_keys.py`.

`design_md_spec_keys` is the in-repo frozen copy of `@google/design.md`'s
key sets (frozen-copy pattern per `loom-code/scripts/canonical/README.md`,
chosen because the spec format is `alpha` with no compatibility promise and CI
must not depend on the network). This test pins the three frozen sets and the
module's provenance record so any accidental edit to either is caught here
rather than surfacing as silent token loss downstream.

Stdlib only. No network, no `npx` invocation — the whole point of freezing
the sets in-repo is that CI needs neither.
"""

import pathlib
import re
import sys

import pytest

import design_md_spec_keys

SCHEMA_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "skills"
    / "design-system"
    / "references"
    / "design-md-schema.md"
)

_THIS_MODULE = sys.modules[__name__]


def _schema_text() -> str:
    return SCHEMA_PATH.read_text(encoding="utf-8")


def _section(text: str, start_heading: str, end_heading: str) -> str:
    """Slice `text` from `start_heading` up to (not including) `end_heading`."""
    start = text.index(start_heading)
    end = text.index(end_heading, start)
    return text[start:end]


def _fenced_yaml_block(section: str) -> str:
    """Return the contents of the section's first fenced ```yaml block."""
    match = re.search(r"```yaml\n(.*?)```", section, re.DOTALL)
    assert match, "section has no fenced ```yaml block"
    return match.group(1)


def _nested_mapping(yaml_block: str, top_key: str) -> dict:
    """Parse `top_key:`'s two-level nested mapping into {name: {key: value}}.

    LOOM-SIMPLIFY: hand-rolled indentation walker, not a full YAML parser
    (no PyYAML — loom-siblings-ci.yml installs pytest only, matching the
    stdlib-only constraint `design_md_spec_keys.py` already documents for
    this plugin's scripts/). Handles exactly the two-level shape this
    reference emits (`top_key:` -> name -> `key: value`); a third nesting
    level, YAML lists, or multiline scalars under `top_key:` are unsupported.
    A property line indented off the level's established property indent
    (deeper OR shallower) raises `AssertionError` instead of being
    silently dropped — closed 2026-08-10 after T2's code-quality review
    found the drop.
    | ceiling: the fenced yaml block under `typography:` or `components:`
    grows a list, anchor, multiline scalar, or a third nesting level
    (indentation drift within the two supported levels is no longer a
    ceiling — it now raises) | upgrade: add
    `python3 -m pip install pyyaml` to loom-siblings-ci.yml's install step
    and replace this walker with `yaml.safe_load(block)[top_key]`
    | ref: docs/loom/plans/2026-08-10-design-md-spec-conformance.md Task 3
    """
    lines = [line for line in yaml_block.splitlines() if line.strip()]
    top_idx = next(
        (i for i, line in enumerate(lines) if line.strip() == f"{top_key}:"),
        None,
    )
    assert top_idx is not None, f"no `{top_key}:` mapping in yaml block"
    top_indent = len(lines[top_idx]) - len(lines[top_idx].lstrip(" "))

    result: dict = {}
    level_indent = None
    prop_indent = None
    current_name = None
    for line in lines[top_idx + 1 :]:
        indent = len(line) - len(line.lstrip(" "))
        if indent <= top_indent:
            break
        stripped = line.strip()
        if level_indent is None:
            level_indent = indent
        if indent == level_indent:
            current_name = stripped.rstrip(":")
            result[current_name] = {}
            prop_indent = None
        elif indent > level_indent and current_name is not None and ":" in stripped:
            if prop_indent is None:
                prop_indent = indent
            assert indent == prop_indent, (
                f"inconsistent property indentation under '{current_name}': "
                f"expected indent {prop_indent}, got {indent} for line {stripped!r}"
            )
            prop_key, _, prop_value = stripped.partition(":")
            result[current_name][prop_key.strip()] = prop_value.strip()
    return result


def _bullet_line(text: str, key: str) -> str:
    """Return the top-level `- \\`key\\` — ...` bullet line documenting `key`.

    Restricted to bullets that open a line (optionally indented) with the
    backticked key immediately after the dash, so it locates the single
    canonical documentation bullet for that key rather than any incidental
    mention of the same word in prose or a `{key.*}` reference elsewhere.
    """
    match = re.search(rf"^\s*- `{re.escape(key)}`.*$", text, re.MULTILINE)
    assert match, f"no top-level bullet documents `{key}`"
    return match.group(0)


def _header_before_first_bullet(section: str) -> str:
    """The lead-in prose of `section`, from its start up to (not including)
    its first top-level `- \\`key\\`` bullet — i.e. whatever framing text
    introduces the bullet list. Used to check what the header claims about
    the list below it without depending on the bullets' own wording.
    """
    first_bullet = re.search(r"\n- `", section)
    assert first_bullet, "section has no top-level bullets"
    return section[: first_bullet.start()]


def _monkeypatch_schema_text(monkeypatch: pytest.MonkeyPatch, mutator) -> None:
    """Patch `_schema_text()` to return the pristine document run through
    `mutator`, so any caller of `_schema_text()` — including a production
    test function invoked directly below, one level lower in the stack
    than calling a helper in isolation — observes the mutated text.
    """
    mutated = mutator(_schema_text())
    monkeypatch.setattr(_THIS_MODULE, "_schema_text", lambda: mutated)


def test_frozen_sets_carry_provenance():
    assert design_md_spec_keys.TOKEN_GROUPS == {
        "colors",
        "typography",
        "rounded",
        "spacing",
        "components",
    }
    assert design_md_spec_keys.TYPOGRAPHY_PROPERTIES == {
        "fontFamily",
        "fontSize",
        "fontWeight",
        "lineHeight",
        "letterSpacing",
        "fontFeature",
        "fontVariation",
    }
    assert design_md_spec_keys.COMPONENT_SUB_TOKENS == {
        "backgroundColor",
        "textColor",
        "typography",
        "rounded",
        "padding",
        "size",
        "height",
        "width",
    }
    assert "0.4.0" in design_md_spec_keys.PROVENANCE
    assert "npx @google/design.md@0.4.0 spec" in design_md_spec_keys.PROVENANCE


def test_nested_mapping_raises_on_indentation_drift():
    """A property indented deeper than its siblings must not vanish silently.

    Task-2 code-quality review found `_nested_mapping` captured property
    lines only at a level's first-observed indent, so a key indented
    deeper than its siblings was silently dropped from the extracted set
    — a hole that would let T3's exclusivity assertion pass without ever
    grading the dropped key. This pins the fix: a deeper-indented sibling
    must surface as a loud failure, not vanish quietly.
    """
    yaml_block = (
        "components:\n"
        "  button:\n"
        "    backgroundColor: \"{colors.primary}\"\n"
        "      textColor: \"{colors.background}\"\n"  # deeper than sibling
        "    rounded: \"{rounded.md}\"\n"
    )
    with pytest.raises(AssertionError):
        _nested_mapping(yaml_block, "components")


def test_typography_properties_are_all_spec_recognised():
    text = _schema_text()
    section = _section(text, "## Typography", "## Layout")
    yaml_block = _fenced_yaml_block(section)
    levels = _nested_mapping(yaml_block, "typography")

    # (a) structure present: at least one typography level name carries
    # nested keys. This also guards against (b) passing vacuously on an
    # empty extraction.
    assert any(props for props in levels.values()), (
        "no typography level carries nested property keys"
    )

    # (b) properties whitelisted: every key extracted at the nested-under-a-
    # level depth is a member of TYPOGRAPHY_PROPERTIES. Level NAMES
    # themselves are never inspected — the spec leaves that position open.
    extracted_properties = {key for props in levels.values() for key in props}
    unrecognised = extracted_properties - design_md_spec_keys.TYPOGRAPHY_PROPERTIES
    assert not unrecognised, (
        f"typography properties not in the spec whitelist: {unrecognised}"
    )


def _five_group_section(text: str) -> str:
    """The intro section naming the five token-group sections, whitespace-
    normalized. Named `_..._section` (not `_..._paragraph` — it returns
    the WHOLE section including its `##` heading, not one paragraph).
    Scoped via `_section` to just this section (ends at the next `##`
    heading) so the group-name check below can't be satisfied by
    unrelated headings/prose that happen to repeat the same five words
    elsewhere in the document (all five occur as section headings too).
    """
    section = _section(
        text, "## The 8 canonical sections (in order)", "## Overview / Brand"
    )
    return re.sub(r"\s+", " ", section)


def _assert_all_token_groups_named(text_blob: str) -> None:
    """Every TOKEN_GROUPS member must be named in `text_blob`."""
    for group in design_md_spec_keys.TOKEN_GROUPS:
        assert group in text_blob, (
            f"TOKEN_GROUPS member `{group}` not named in: {text_blob!r}"
        )


def _assert_component_tokens_documented(section: str) -> None:
    """Every COMPONENT_SUB_TOKENS member must have its own documentation
    bullet in `section` — scoped via `_bullet_line`, not a bare substring
    check (the fenced yaml example later in the section repeats the same
    words as literal keys/values, so a bare `in` survives a deleted bullet).
    """
    for token in design_md_spec_keys.COMPONENT_SUB_TOKENS:
        _bullet_line(section, token)


def test_non_spec_keys_are_labelled_and_token_groups_named():
    text = _schema_text()

    # (a) extensions labelled: each of the six enumerated loom extensions
    # appears under its own bullet, and that bullet's line states plainly
    # that `export` does not carry it (both words present, case-insensitive).
    for key in LOOM_EXTENSIONS:
        line = _bullet_line(text, key).lower()
        assert "extension" in line, f"`{key}` bullet has no extension label: {line!r}"
        assert "export" in line, f"`{key}` bullet doesn't say export omits it: {line!r}"

    # (b) spec meta keys unlabelled: name/description/version/omitted are
    # documented but their bullets must NOT carry the extension label.
    for key in SPEC_META_KEYS:
        line = _bullet_line(text, key).lower()
        assert "extension" not in line, (
            f"spec meta key `{key}` incorrectly carries the extension label: {line!r}"
        )

    # (c) grounding stamped: the grounding note names the verified spec
    # version.
    grounding = _section(text, "> **Grounding.**", "> **Scope")
    assert "0.4.0" in grounding, "grounding note doesn't name the verified spec version"

    # (d) blanket claim gone at BOTH loci, replaced by the five-group
    # reality (whitespace-normalized so a line-wrapped phrase still matches).
    normalized = re.sub(r"\s+", " ", text)
    assert (
        "Each section carries a short prose rationale plus a YAML token block"
        not in normalized
    ), "blanket per-section token-block claim still present at :41-42"
    assert (
        "Populate each section's YAML token block" not in normalized
    ), "blanket per-section token-block claim still present at :194"
    # scoped to the five-group intro section, NOT the whole file — a
    # whole-file grep is satisfied by the group names' own `##` headings
    # and ordinary prose regardless of what this section actually says
    # (see the mutation tests below).
    _assert_all_token_groups_named(_five_group_section(text))


def test_component_sub_tokens_are_complete_and_exclusive():
    text = _schema_text()
    section = _section(text, "## Components", "## Do's & Don'ts")

    # (a) completeness: every member of COMPONENT_SUB_TOKENS has its own
    # documentation bullet in ## Components — NOT a bare substring check
    # over the whole section, which the fenced yaml example below would
    # satisfy even after the doc bullet is deleted (see the mutation tests
    # below).
    _assert_component_tokens_documented(section)

    yaml_block = _fenced_yaml_block(section)
    components = _nested_mapping(yaml_block, "components")

    # (b) extraction non-empty: the `components:` mapping yields at least
    # one component with nested keys. This guards against (c) passing
    # vacuously on an empty extraction.
    assert any(props for props in components.values()), (
        "no component carries nested property keys"
    )

    # (c) exclusivity: every key at the nested-under-a-component depth is
    # a member of COMPONENT_SUB_TOKENS. Component/variant NAMES
    # themselves (`button`, `button-primary`, `button-primary-hover`, …)
    # and `{...}` brace-reference VALUES are outside the extracted set by
    # construction.
    extracted_keys = {key for props in components.values() for key in props}
    unrecognised = extracted_keys - design_md_spec_keys.COMPONENT_SUB_TOKENS
    assert not unrecognised, (
        f"component keys not in the spec whitelist: {unrecognised}"
    )


# --- Mutation tests: the rescoped assertions above must actually bite ---
#
# The whole-branch reviewer proved by mutation that the OLD whole-file/
# whole-section checks these two tests replaced did NOT catch: (1) blanket
# replacement of the five-group section, (2) rewriting it to claim "all
# eight" sections carry tokens, (3) renaming a group inside that sentence,
# and (4) deleting a component token's documentation bullet. Each test below
# reproduces one such mutation via `_monkeypatch_schema_text` and asserts
# that CALLING THE PRODUCTION TEST FUNCTION ITSELF (not a bypassed helper)
# now raises — one level lower in the stack than calling the helper
# directly, so a production test body reverted to its old, unscoped check
# is caught here rather than leaving the suite green (proven: reverting
# both `test_non_spec_keys_are_labelled_and_token_groups_named`'s and
# `test_component_sub_tokens_are_complete_and_exclusive`'s helper calls to
# their pre-fix whole-file/whole-section checks, with the document
# pristine, used to leave 16/16 passed).


def test_five_group_scoping_catches_blanket_paragraph_replacement(monkeypatch):
    text = _schema_text()
    section = _section(
        text, "## The 8 canonical sections (in order)", "## Overview / Brand"
    )
    _heading, _, paragraph = section.partition("\n\n")
    target = paragraph.strip()

    def mutator(t: str) -> str:
        return t.replace(target, "Each section carries stuff.")

    _monkeypatch_schema_text(monkeypatch, mutator)
    with pytest.raises(AssertionError):
        test_non_spec_keys_are_labelled_and_token_groups_named()


def test_five_group_scoping_catches_all_eight_rewrite(monkeypatch):
    text = _schema_text()
    section = _section(
        text, "## The 8 canonical sections (in order)", "## Overview / Brand"
    )
    _heading, _, paragraph = section.partition("\n\n")
    target = paragraph.strip()

    def mutator(t: str) -> str:
        return t.replace(
            target,
            "**All** eight sections carry a YAML token block, in this order.",
        )

    _monkeypatch_schema_text(monkeypatch, mutator)
    with pytest.raises(AssertionError):
        test_non_spec_keys_are_labelled_and_token_groups_named()


def test_five_group_scoping_catches_group_rename(monkeypatch):
    text = _schema_text()
    assert text.count("`spacing` (Layout)") == 1, (
        "sanity check: this mutation targets the one occurrence of this "
        "exact phrase — if this fails, the source text moved"
    )

    def mutator(t: str) -> str:
        return t.replace("`spacing` (Layout)", "`gaps` (Layout)", 1)

    _monkeypatch_schema_text(monkeypatch, mutator)
    with pytest.raises(AssertionError):
        test_non_spec_keys_are_labelled_and_token_groups_named()


@pytest.mark.parametrize("token", ["size", "height", "padding", "width"])
def test_component_completeness_scoping_catches_deleted_bullet(token, monkeypatch):
    text = _schema_text()
    section = _section(text, "## Components", "## Do's & Don'ts")
    mutated_section = re.sub(
        rf"^\s*- `{re.escape(token)}`.*$\n?", "", section, count=1, flags=re.MULTILINE
    )
    assert token in mutated_section, (
        f"sanity check: `{token}` must still appear in the yaml example "
        "after its doc bullet is deleted — that survival is exactly what "
        "let the old bare `in` check pass"
    )

    def mutator(t: str) -> str:
        return t.replace(section, mutated_section)

    _monkeypatch_schema_text(monkeypatch, mutator)
    with pytest.raises(AssertionError):
        test_component_sub_tokens_are_complete_and_exclusive()


# The six loom extensions named in the brief's closed list — deliberately
# NOT the set-complement of TOKEN_GROUPS, which would also sweep in the
# spec's own meta keys (name/description/version/omitted).
LOOM_EXTENSIONS = (
    "brand_voice",
    "theme",
    "shadows",
    "z_index",
    "border_width",
    "border_style",
)

# Spec meta keys that must be documented WITHOUT the extension label.
SPEC_META_KEYS = ("name", "description", "version", "omitted")

# Display names for TOKEN_GROUPS as they appear in the reference's own
# prose rosters (e.g. the Derivation contract). Source of truth for
# MEMBERSHIP is design_md_spec_keys.TOKEN_GROUPS; this only maps each
# member to how the prose spells it out.
TOKEN_GROUP_DISPLAY_NAMES = {
    "colors": "Colors",
    "typography": "Typography",
    "spacing": "Layout",
    "rounded": "Shapes",
    "components": "Components",
}
assert set(TOKEN_GROUP_DISPLAY_NAMES) == design_md_spec_keys.TOKEN_GROUPS, (
    "TOKEN_GROUP_DISPLAY_NAMES must mirror design_md_spec_keys.TOKEN_GROUPS"
)


_TOTALIZING_SET_SCOPE_RE = re.compile(
    r"\b(?:all|every|each|both)\b[^.!?]{0,30}?\bsets?\b", re.IGNORECASE
)


def _assert_no_blanket_closed_claim_for_component_sub_tokens(doc: str, *, source: str) -> None:
    """`doc` must not claim, however phrased, that COMPONENT_SUB_TOKENS (or
    all three frozen sets taken together) form a closed set — the spec's
    Consumer Behavior for Unknown Content table accepts an unrecognized
    component property with a warning (PROVENANCE-cited), so only
    TOKEN_GROUPS/TYPOGRAPHY_PROPERTIES may be described as closed.

    Property check, not a literal-string ban: split into sentences and flag
    any sentence that scopes closedness over MORE than TOKEN_GROUPS +
    TYPOGRAPHY_PROPERTIES — either (a) it names COMPONENT_SUB_TOKENS
    specifically, or (b) it uses a totalizing quantifier over "sets"
    ("all"/"every"/"each"/"both" within a short span of "set(s)") — AND
    (c) calls the result "closed" without also saying "not closed". This
    survives a full sentence rewrite: neither the exact substring "closed
    key sets" nor the name "component_sub_tokens" need appear — "Every set
    enumerated above is closed" and "All of the sets here are closed" both
    still trip (b), which the old literal ban ("all three sets" / "closed
    key sets" verbatim) did not catch.
    """
    offending = None
    for sentence in re.split(r"(?<=[.!?])\s+", doc):
        lowered = sentence.lower()
        blanket_scope = bool(_TOTALIZING_SET_SCOPE_RE.search(sentence)) or (
            "closed key sets" in lowered
        )
        names_component_tokens = "component_sub_tokens" in lowered
        if (
            (blanket_scope or names_component_tokens)
            and "closed" in lowered
            and "not closed" not in lowered
        ):
            offending = sentence
            break
    assert offending is None, (
        f"{source} docstring sentence claims a closed set covering "
        f"COMPONENT_SUB_TOKENS, however phrased: {offending!r}"
    )


# --- Correctness fixes (reviewer findings C, D, E, F) ---


def test_elevation_section_disambiguates_non_spec_keys():
    """Task C: '## Elevation & Depth' states (two lines up) that elevation
    is not one of the spec's five token groups and both keys below are
    loom extensions, so a bullet-list header inviting spec-confirmation
    would contradict its own prior sentence. Property, not two verbatim
    English sentences: (1) the section carries no fenced yaml block —
    `_fenced_yaml_block` raising IS the structural cash-out of "not YAML
    tokens", robust to any wording of that idea (a meaning-preserving
    reword like "prose only, carrying no YAML token block" must not
    false-RED — see the mutation test below); (2) the header text framing
    the bullet list — everything before the first bullet — carries no
    "confirm ... against the spec" invitation, checked as a collocation
    of both words rather than one exact phrase, so a determiner-reworded
    re-add of the old header ("confirm THESE against the spec") is still
    caught — see the mutation test below.
    """
    text = _schema_text()
    section = _section(text, "## Elevation & Depth", "## Shapes")

    with pytest.raises(AssertionError):
        _fenced_yaml_block(section)

    header = _header_before_first_bullet(section).lower()
    assert not ("confirm" in header and "spec" in header), (
        "the bullet-list header still invites spec-confirmation, which "
        f"contradicts this section's own prior sentence that elevation "
        f"is not one of the spec's five token groups: {header!r}"
    )


def test_elevation_disambiguation_catches_reintroduced_spec_confirmation_header(monkeypatch):
    """Probe (item 4/5, Task C): the OLD pin banned only the literal string
    'Expected token keys (confirm against the spec):'. Re-adding a
    spec-confirmation header with a different determiner —
    'Expected token keys (confirm THESE against the spec):' — evaded that
    literal ban. Proves the NEW property-based check in
    `test_elevation_section_disambiguates_non_spec_keys` catches it.
    """
    text = _schema_text()
    section = _section(text, "## Elevation & Depth", "## Shapes")
    insertion_point = re.search(r"\n- `", section).start()

    def mutator(t: str) -> str:
        mutated_section = (
            section[:insertion_point]
            + "\nExpected token keys (confirm THESE against the spec):"
            + section[insertion_point:]
        )
        return t.replace(section, mutated_section)

    _monkeypatch_schema_text(monkeypatch, mutator)
    with pytest.raises(AssertionError):
        test_elevation_section_disambiguates_non_spec_keys()


def test_elevation_disambiguation_tolerates_meaning_preserving_reword(monkeypatch):
    """Mirror probe (item 4, Task C): the OLD pin required the exact phrase
    'plain prose, not yaml tokens' (lowercased) to survive verbatim.
    Rewording it to an equivalent phrase — 'prose only, carrying no YAML
    token block' — false-REDded that old pin. The NEW property-based
    check must NOT false-RED on this reword: it depends only on the
    structural absence of a fenced yaml block and the absence of a
    spec-confirmation header, neither of which this reword touches.
    """
    text = _schema_text()
    section = _section(text, "## Elevation & Depth", "## Shapes")
    header_region = _header_before_first_bullet(section)

    def mutator(t: str) -> str:
        mutated_header = re.sub(
            r"(?i)plain prose,? not yaml tokens[^\n:]*",
            "prose only, carrying no YAML token block",
            header_region,
        )
        if mutated_header == header_region:
            # The OLD wording is no longer present verbatim in the live
            # doc (e.g. this exact reword has already been adopted) —
            # the regex has nothing left to rewrite. Fall back to an
            # unconditional insertion of the reworded text instead of
            # asserting the current wording, so this probe keeps
            # exercising "does the production check tolerate this
            # phrasing" regardless of what the doc currently says,
            # rather than false-REDing on its own sanity step.
            mutated_header = header_region + "prose only, carrying no YAML token block\n"
        return t.replace(header_region, mutated_header)

    _monkeypatch_schema_text(monkeypatch, mutator)
    test_elevation_section_disambiguates_non_spec_keys()  # must NOT raise


def test_elevation_mirror_probe_survives_document_already_using_new_wording(monkeypatch):
    """Regression (🟡 whole-branch review finding 1): the mirror probe
    above (`test_elevation_disambiguation_tolerates_meaning_preserving_reword`)
    carries its OWN sanity assert requiring the OLD wording ('plain
    prose, not yaml tokens') to still be present, verbatim, in the live
    document for its regex to have something to rewrite. If a maintainer
    actually adopts the exact reword the probe's own docstring names as
    the must-not-false-RED case ('prose only, carrying no YAML token
    block') into the real document, the probe's sanity assert now fails
    — the old wording is gone — so the probe false-REDs the very reword
    it promises to tolerate. Simulate that adopted document (header
    already carrying the new wording) and confirm the mirror probe no
    longer raises.
    """
    text = _schema_text()
    section = _section(text, "## Elevation & Depth", "## Shapes")
    header_region = _header_before_first_bullet(section)
    already_adopted_header = re.sub(
        r"(?i)plain prose,? not yaml tokens[^\n:]*",
        "prose only, carrying no YAML token block",
        header_region,
    )
    assert already_adopted_header != header_region, (
        "sanity check: the reword must actually apply once to set up this scenario"
    )

    def mutator(t: str) -> str:
        return t.replace(header_region, already_adopted_header)

    _monkeypatch_schema_text(monkeypatch, mutator)
    test_elevation_disambiguation_tolerates_meaning_preserving_reword(monkeypatch)  # must NOT raise


def test_prose_scope_clause_removed_at_both_loci():
    """Task D: 'are prose, including <determiner> documented loom
    extensions' contradicts the six labelled extension bullets — some of
    which (`border_width` / `border_style`) live inside `## Shapes`, a
    TOKEN_GROUPS section (`rounded`), not one of the three prose sections.
    Property, not one exact string: (1) no sentence assigns documented
    loom extensions wholesale to prose, tolerant of the determiner word
    between "including" and "documented" — the OLD pin banned only the
    literal "including any documented loom extensions", which a
    determiner swap to "including ALL documented loom extensions" evaded
    (see the mutation test below); (2) the structural fact that makes the
    wholesale claim false still holds — border_width / border_style are
    documented inside ## Shapes, not a prose section.
    """
    text = _schema_text()
    normalized = re.sub(r"\s+", " ", text)
    assert not re.search(
        r"including\s+\S+\s+documented loom extensions", normalized, re.IGNORECASE
    ), (
        "a sentence still assigns documented loom extensions wholesale to "
        "prose (any determiner) — border_width/border_style live in "
        "## Shapes, a token-group section, not a prose section"
    )

    shapes_section = _section(text, "## Shapes", "## Components")
    for key in ("border_width", "border_style"):
        _bullet_line(shapes_section, key)


def test_prose_scope_clause_catches_determiner_reword(monkeypatch):
    """Probe (item 4/5, Task D): restoring the false wholesale claim with a
    different determiner — 'including ALL documented loom extensions' —
    evaded the OLD literal-string pin ("including any documented loom
    extensions"). Proves the NEW determiner-tolerant regex catches it.
    """
    text = _schema_text()
    section = _section(
        text, "## The 8 canonical sections (in order)", "## Overview / Brand"
    )
    _heading, _, paragraph = section.partition("\n\n")
    target = paragraph.strip()

    def mutator(t: str) -> str:
        mutated = target + " Both are prose, including ALL documented loom extensions."
        return t.replace(target, mutated)

    _monkeypatch_schema_text(monkeypatch, mutator)
    with pytest.raises(AssertionError):
        test_prose_scope_clause_removed_at_both_loci()


def test_component_sub_tokens_docstring_not_claimed_closed():
    """Task F: a reviewer re-ran `npx @google/design.md@0.4.0 spec` live —
    its Consumer Behavior for Unknown Content table has a row 'Unknown
    component property | Accept with warning | borderColor', so
    COMPONENT_SUB_TOKENS is the spec's RECOGNISED set, not closed.
    TOKEN_GROUPS/TYPOGRAPHY_PROPERTIES have no such row; 'closed' still
    holds for those two. Property check (see
    `_assert_no_blanket_closed_claim_for_component_sub_tokens`), not the
    literal string "closed key sets" — a full-sentence rewrite ("All
    three sets … are closed: an unrecognized member of any of them is
    rejected by the spec") evaded that literal ban (see the mutation test
    below). Pins the corrected docstring property only — no frozen value
    changes (see test_frozen_sets_carry_provenance).
    """
    doc = design_md_spec_keys.__doc__
    _assert_no_blanket_closed_claim_for_component_sub_tokens(doc, source="design_md_spec_keys")
    assert "COMPONENT_SUB_TOKENS" in doc, (
        "docstring must name COMPONENT_SUB_TOKENS when distinguishing its "
        "recognised/closed status from the other two sets"
    )


def test_component_sub_tokens_docstring_catches_reworded_closed_claim(monkeypatch):
    """Probe (item 4/5, Task F): restoring the false closed-set claim fully
    reworded — 'All three sets … are closed: an unrecognized member of
    any of them is rejected by the spec' — carries neither the literal
    substring "closed key sets" nor the name "COMPONENT_SUB_TOKENS", so
    it evaded the OLD literal-string pin. Proves the NEW property check
    catches it via the "all three" + "closed" (without "not closed")
    collocation.
    """
    mutated_doc = (
        design_md_spec_keys.__doc__
        + "\n\nAll three sets are closed: an unrecognized member of any "
        "of them is rejected by the spec."
    )
    monkeypatch.setattr(design_md_spec_keys, "__doc__", mutated_doc)
    with pytest.raises(AssertionError):
        test_component_sub_tokens_docstring_not_claimed_closed()


def test_component_sub_tokens_docstring_catches_closed_claim_sharing_no_pinned_wording(monkeypatch):
    """Probe (🟡 whole-branch review finding 2): the check was still a
    phrase ban keyed on "all three" / "closed key sets" /
    "component_sub_tokens" — two restatements of the identical false
    claim, sharing NONE of those three substrings, evaded it:
    'Every set enumerated above is closed: an unrecognized member is
    rejected by the spec.' and 'All of the sets here are closed: an
    unrecognized member of any is rejected.' Both must go RED under the
    semantic check (closedness scoped wider than TOKEN_GROUPS +
    TYPOGRAPHY_PROPERTIES), invoked here via the production test
    function itself, not the helper in isolation.
    """
    for false_claim in (
        "Every set enumerated above is closed: an unrecognized member "
        "is rejected by the spec.",
        "All of the sets here are closed: an unrecognized member of "
        "any is rejected.",
    ):
        mutated_doc = design_md_spec_keys.__doc__ + "\n\n" + false_claim
        monkeypatch.setattr(design_md_spec_keys, "__doc__", mutated_doc)
        with pytest.raises(AssertionError):
            test_component_sub_tokens_docstring_not_claimed_closed()


def test_module_docstring_not_claimed_closed():
    """Item 3: this test module's OWN docstring (module-level, describing
    `design_md_spec_keys`'s three sets as "closed key sets") is a SECOND,
    previously-unguarded copy of the same blanket-closed claim Task F
    fixed in `design_md_spec_keys.__doc__` — Task F's original pin only
    scoped to that one module's docstring. Extends the same property
    check to this module's docstring too.
    """
    doc = __doc__
    _assert_no_blanket_closed_claim_for_component_sub_tokens(
        doc, source="test_design_md_schema_keys"
    )


def test_derivation_contract_excludes_elevation():
    """Task E: the Derivation contract's roster clause ('every token in
    <roster> MUST be derivable...') must name exactly the five
    TOKEN_GROUPS sections (by their prose display names) — no more, no
    less. Scoped to the roster clause itself, not the whole section — the
    OLD pin banned the substring "Elevation" anywhere in the section, so
    a clarifying parenthetical added elsewhere in the section
    ("Elevation is excluded — it is not a spec token group") would have
    false-REDded it (see the mutation test below proving the new scoping
    tolerates exactly that addition).
    """
    text = _schema_text()
    section = _section(text, "**Derivation contract:**", "## Colors")
    match = re.search(r"every token in (.+?) MUST be derivable", section, re.DOTALL)
    assert match, "Derivation contract roster clause not found"
    roster = re.sub(r"\s+", " ", match.group(1))
    names = {name.strip() for name in re.split(r"/|,|\band\b", roster) if name.strip()}
    assert names == set(TOKEN_GROUP_DISPLAY_NAMES.values()), (
        "Derivation contract roster must name exactly the five TOKEN_GROUPS "
        f"sections {sorted(TOKEN_GROUP_DISPLAY_NAMES.values())}, got {sorted(names)}"
    )


def test_derivation_contract_roster_catches_elevation_readded(monkeypatch):
    """Probe (item 4/5, Task E): re-adding Elevation to the roster clause
    itself must still go RED under the new scoped check.
    """
    text = _schema_text()
    section = _section(text, "**Derivation contract:**", "## Colors")
    match = re.search(r"every token in (.+?) MUST be derivable", section, re.DOTALL)
    assert match
    roster = match.group(1)
    mutated_roster = roster.rstrip() + " / Elevation"

    def mutator(t: str) -> str:
        mutated_section = section.replace(roster, mutated_roster, 1)
        return t.replace(section, mutated_section)

    _monkeypatch_schema_text(monkeypatch, mutator)
    with pytest.raises(AssertionError):
        test_derivation_contract_excludes_elevation()


def test_derivation_contract_tolerates_clarifying_elevation_note_outside_roster(monkeypatch):
    """Mirror probe (item 4, Task E): a clarifying parenthetical about
    Elevation added OUTSIDE the roster clause (elsewhere in the same
    section) must NOT false-RED — this is exactly what the OLD
    whole-section substring ban on "Elevation" would have done.
    """
    text = _schema_text()
    section = _section(text, "**Derivation contract:**", "## Colors")

    def mutator(t: str) -> str:
        mutated_section = (
            section.rstrip()
            + "\n(Elevation is excluded — it is not a spec token group.)\n\n"
        )
        return t.replace(section, mutated_section)

    _monkeypatch_schema_text(monkeypatch, mutator)
    test_derivation_contract_excludes_elevation()  # must NOT raise


# --- Additional loci (items 1, 6, 7) ---


def test_component_properties_header_not_claimed_closed():
    """Item 1: '## Components' headed its property list "drawn only from
    this closed set (confirm against the spec)" — but a live
    `npx @google/design.md@0.4.0 spec` run (commit 546e9f3a,
    design_md_spec_keys.py:8-13) showed an unrecognized component
    property is accepted with a warning, not rejected: COMPONENT_SUB_TOKENS
    is the spec's RECOGNISED set, not closed. The header must stop
    claiming closedness and stop inviting spec-confirmation of a
    closedness that doesn't exist. `## Typography`'s closed-set claim
    (`:131`) is untouched and must stay — TYPOGRAPHY_PROPERTIES genuinely
    is closed, unlike COMPONENT_SUB_TOKENS.
    """
    text = _schema_text()

    components_section = _section(text, "## Components", "## Do's & Don'ts")
    components_header = _header_before_first_bullet(components_section).lower()
    assert "closed" not in components_header, (
        f"the Components property-list header still claims closedness: {components_header!r}"
    )
    assert not ("confirm" in components_header and "spec" in components_header), (
        "the Components property-list header still invites spec-confirmation "
        f"of a closed set that doesn't exist: {components_header!r}"
    )

    typography_section = _section(text, "## Typography", "## Layout")
    typography_header = _header_before_first_bullet(typography_section).lower()
    assert "closed" in typography_header, (
        "## Typography's closed-set claim must stay — TYPOGRAPHY_PROPERTIES "
        "genuinely is closed, unlike COMPONENT_SUB_TOKENS"
    )


def test_generation_checklist_step3_names_all_token_groups():
    """Item 6: the Generation-checklist step-3 five-group roster is
    deletable today with a fully green suite. Pin it structurally.
    """
    text = _schema_text()
    section = _section(text, "## Generation checklist", "## Anti-patterns")
    step3_match = re.search(r"\n3\.\s.*?(?=\n\d\.|\Z)", section, re.DOTALL)
    assert step3_match, "Generation checklist has no step 3"
    _assert_all_token_groups_named(re.sub(r"\s+", " ", step3_match.group(0)))


def test_shapes_rounded_bullet_states_not_radius():
    """Item 6: the '## Shapes' `rounded` bullet is the sole locus of the
    load-bearing "Token key is `rounded` per the Google DESIGN.md spec
    (not `radius`)" correction. Pin it.
    """
    text = _schema_text()
    section = _section(text, "## Shapes", "## Components")
    line = _bullet_line(section, "rounded").lower()
    assert "radius" in line and "not" in line, (
        f"the `rounded` bullet must keep the not-`radius` correction: {line!r}"
    )


def test_shapes_header_distinguishes_extension_bullets_from_spec_keys():
    """Item 7: '## Shapes' used to head its whole bullet list — including
    the two loom-extension bullets `border_width`/`border_style` — with
    one unscoped "confirm against the spec" hedge, which does not apply
    to keys that aren't spec keys at all. The header must name the
    extensions as extensions rather than fold them under the spec-key
    hedge (Shapes stays a token-group section — this only rescopes the
    hedge, it does not reclassify Shapes as prose).
    """
    text = _schema_text()
    section = _section(text, "## Shapes", "## Components")
    header = _header_before_first_bullet(section).lower()
    assert "extension" in header, (
        "the header above the bullet list must name the loom extensions "
        f"below it as extensions, not fold them under a spec-confirmation "
        f"hedge that doesn't apply to them: {header!r}"
    )


def test_overview_brand_header_distinguishes_extension_bullets_from_spec_keys():
    """Item 7: same fix as Shapes, applied to Overview / Brand's mixed
    frontmatter list (`name`/`description`/`version`/`omitted` spec keys
    plus `brand_voice`/`theme` loom extensions, all previously under one
    unscoped "confirm against the spec" hedge).
    """
    text = _schema_text()
    section = _section(text, "## Overview / Brand", "## Colors")
    header = _header_before_first_bullet(section).lower()
    assert "extension" in header, (
        "the header above the frontmatter bullet list must name the loom "
        f"extensions below it as extensions: {header!r}"
    )


# --- Correctness fixes (whole-branch review findings 3, 4) ---


def _generation_checklist_step(text: str, n: int) -> str:
    section = _section(text, "## Generation checklist", "## Anti-patterns")
    match = re.search(rf"\n{n}\.\s.*?(?=\n\d\.|\Z)", section, re.DOTALL)
    assert match, f"Generation checklist has no step {n}"
    return re.sub(r"\s+", " ", match.group(0)).strip()


def test_generation_checklist_lint_step_does_not_require_stripping_warned_extension_properties():
    """🟡 3: step 5 said "resolve violations before declaring done" —
    unconditional. `## Components` (:211-213) newly establishes that the
    spec ACCEPTS an unrecognized component property with a warning
    rather than rejecting it, so a deliberately-chosen extension
    property that lints with a warning now has two live readings (strip
    it, or keep it) and the checklist said which nowhere.

    Property, not the literal sentence: step 5 must (a) still require
    resolving a genuine lint failure (contrast etc. stay blockers,
    matching '## Lint + accessibility''s own framing at :36-39, untouched
    here), while (b) explicitly carving out a warning on such a
    documented extension property as expected — not something this step
    requires resolving away. Tolerant of how (a)/(b) are worded, as long
    as both concepts are present.
    """
    step5 = _generation_checklist_step(_schema_text(), 5).lower()
    assert "warning" in step5, f"step 5 must mention the warning case: {step5!r}"
    assert "expected" in step5 or "legitimate" in step5, (
        f"step 5 must say the warning is expected/legitimate, not a "
        f"violation to resolve: {step5!r}"
    )
    assert "fail" in step5 or "blocker" in step5, (
        f"step 5 must keep requiring a genuine failure to be resolved: {step5!r}"
    )


def test_generation_checklist_lint_step_catches_reverted_unconditional_resolve(monkeypatch):
    """Probe (🟡 3): reverting step 5 to its OLD unconditional wording —
    'Run `npx @google/design.md` lint and resolve violations before
    declaring done.' — must go RED under the new property check.
    """
    text = _schema_text()
    section = _section(text, "## Generation checklist", "## Anti-patterns")
    match = re.search(r"\n5\.\s.*?(?=\n\d\.|\Z)", section, re.DOTALL)
    assert match
    old_step5 = (
        "\n5. Run `npx @google/design.md` lint and resolve violations "
        "before declaring done."
    )

    def mutator(t: str) -> str:
        mutated_section = section.replace(match.group(0), old_step5)
        return t.replace(section, mutated_section)

    _monkeypatch_schema_text(monkeypatch, mutator)
    with pytest.raises(AssertionError):
        test_generation_checklist_lint_step_does_not_require_stripping_warned_extension_properties()


def test_grounding_note_covers_the_consumer_behavior_claim():
    """🟡 4: the grounding note (:7-13) dates its verification of the
    frozen KEY SETS against `@google/design.md` `0.4.0` on 2026-08-10,
    but the branch also asserts a spec BEHAVIOUR at `## Components`
    (:211-213 — unknown component property -> accept with warning) that
    this citation does not cover, in a document that hedges every other
    spec fact (:15-26). Property, not the literal sentence: the SAME
    dated verified-against-the-spec clause must also cover the
    unrecognized-component-property/warning behaviour — tolerant of how
    the clause is worded, as long as the behaviour is named alongside
    the dated citation.
    """
    text = _schema_text()
    match = re.search(r"> \*\*Grounding\.\*\*.*?(?=\n\n)", text, re.DOTALL)
    assert match, "Grounding note not found"
    note = re.sub(r"\s+", " ", match.group(0)).lower()
    assert "verified against" in note and "0.4.0" in note, (
        f"grounding note must date its verification against the spec version: {note!r}"
    )
    assert "warning" in note and (
        "component property" in note or "consumer behavior" in note
    ), (
        "the same dated verification must also cover the "
        f"unrecognized-component-property/warning behaviour claim: {note!r}"
    )


def test_grounding_note_catches_reverted_key_sets_only_scope(monkeypatch):
    """Probe (🟡 4): reverting the grounding note's last sentence to its
    OLD scope — covering only the three frozen key sets, silent on the
    Consumer-Behavior warning claim — must go RED.
    """
    text = _schema_text()
    match = re.search(r"> \*\*Grounding\.\*\*.*?(?=\n\n)", text, re.DOTALL)
    assert match, "Grounding note not found"
    note = match.group(0)
    old_last_sentence_re = re.compile(
        r"The frozen key sets\n> this reference checks against.*?on 2026-08-10\.",
        re.DOTALL,
    )
    old_last_sentence = (
        "The frozen key sets\n> this reference checks against "
        "(`design_md_spec_keys.py`) were verified against\n> "
        "`@google/design.md` version `0.4.0` on 2026-08-10."
    )

    def mutator(t: str) -> str:
        mutated_note = old_last_sentence_re.sub(old_last_sentence, note)
        assert mutated_note != note, "sanity: the OLD-scope sentence must replace the current one"
        return t.replace(note, mutated_note)

    _monkeypatch_schema_text(monkeypatch, mutator)
    with pytest.raises(AssertionError):
        test_grounding_note_covers_the_consumer_behavior_claim()


def test_update_procedure_covers_consumer_behavior_row():
    """🟡 4 (second locus): `design_md_spec_keys.py`'s module docstring
    (:15-17) instructs re-checking the three frozen key sets on a spec
    bump, but says nothing about re-checking the Consumer Behavior for
    Unknown Content row that its own docstring (:8-13) and `PROVENANCE`
    assert a BEHAVIOUR from (COMPONENT_SUB_TOKENS -> accept with
    warning) — a spec bump could silently invalidate that behaviour claim
    with no check in the loop. Property: the Update-procedure paragraph
    must also instruct re-checking that row.
    """
    doc = design_md_spec_keys.__doc__
    match = re.search(r"Update procedure:.*?(?=\n\n|\Z)", doc, re.DOTALL)
    assert match, "Update procedure paragraph not found"
    procedure = re.sub(r"\s+", " ", match.group(0)).lower()
    assert "consumer behavior" in procedure, (
        "Update procedure must also instruct re-checking the Consumer "
        f"Behavior for Unknown Content row: {procedure!r}"
    )


def test_update_procedure_catches_reverted_three_sets_only_scope(monkeypatch):
    """Probe (🟡 4): reverting the Update-procedure paragraph to its OLD
    scope — diff the three sets only, no Consumer-Behavior recheck —
    must go RED.
    """
    doc = design_md_spec_keys.__doc__
    match = re.search(r"Update procedure:.*?(?=\n\n|\Z)", doc, re.DOTALL)
    assert match, "Update procedure paragraph not found"
    old_procedure = (
        "Update procedure: re-run the derivation command below against a newer\n"
        "spec version, diff the three sets, and bump `PROVENANCE` in the same\n"
        "commit as any value change."
    )
    mutated_doc = doc.replace(match.group(0), old_procedure)
    assert mutated_doc != doc, "sanity: the OLD-scope paragraph must replace the current one"
    monkeypatch.setattr(design_md_spec_keys, "__doc__", mutated_doc)
    with pytest.raises(AssertionError):
        test_update_procedure_covers_consumer_behavior_row()
