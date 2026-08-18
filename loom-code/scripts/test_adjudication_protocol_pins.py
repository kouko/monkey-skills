"""Pin test for the adjudication-view protocol SSOT.

Task 0 of docs/loom/plans/2026-08-12-adjudication-view.md. The protocol
file (`loom-code/skills/using-loom-code/protocols/adjudication-view.md`)
is the SSOT every later task (splitter/lint/renderer/wiring) implements
against — this test pins its load-bearing content literally, so a
future edit cannot silently drop a contract clause the other tasks
depend on.
"""

import re
from pathlib import Path

from adjudication_profiles import get_profile

PROTOCOL_PATH = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "using-loom-code"
    / "protocols"
    / "adjudication-view.md"
)


def _section(text: str, heading: str) -> str:
    """Slice out one `## <heading>` section body. Every assertion that
    pins a claim belonging to a specific section MUST run against its
    slice, not the whole document -- tokens like "supported",
    "zh-Hant", "`ja`", "hard-fail" and "warning" each occur in several
    sections, so a document-wide `in text` check keeps passing even
    after the section that owns the claim has been gutted. (Revision
    round 1 found this on the firing condition; revision round 2 found
    the same class on the negation-tier rows -- deleting either tier
    row left both document-wide assertions green.)"""
    assert f"## {heading}" in text, f"section missing: ## {heading}"
    return text.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]


def _table_forms(table: str) -> dict:
    """Parse a two-column markdown modality table into
    `{source modal: [accepted form, ...]}`, splitting a cell's
    alternatives on ` / `. Header and separator rows are dropped by
    requiring the left cell to be a modal we ship."""
    modals = {"must", "must not", "should", "should not", "may"}
    parsed = {}
    for line in table.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and cells[0] in modals:
            parsed[cells[0]] = [f.strip() for f in cells[1].split(" / ")]
    return parsed


def _firing_conditions_section(text: str) -> str:
    """Slice out just the ## Firing conditions section body."""
    return _section(text, "Firing conditions")


def test_protocol_carries_modality_table_and_unit_rule():
    """The protocol file must exist and pin: the fixed modality mapping
    (all five arrow pairs), the unit-1:1 rule, the units-JSON schema
    field list, and both firing conditions — each of these is a
    contract clause a downstream task (split/lint/render/wiring)
    implements against, so a silent drop must fail this test."""
    assert PROTOCOL_PATH.exists(), f"protocol file missing: {PROTOCOL_PATH}"
    text = PROTOCOL_PATH.read_text(encoding="utf-8")

    # Fixed modality mapping table — five arrow pairs, verbatim.
    for pair in ("must→必須", "should→應", "may→可", "must not→不得", "should not→不應"):
        assert pair in text, f"modality mapping missing: {pair}"

    # unit-1:1 rule — one rendition unit per source unit.
    assert "one rendition unit per source unit" in text, "unit-1:1 rule missing"

    # units-JSON schema field list.
    assert (
        "unit id`, `heading`, `source_text`, `anchors`, `rendition`" in text
    ), "units-JSON schema field list missing"

    # Firing conditions — both. The language condition was rewritten in
    # Task 4 to name supported profiles instead of the unkeepable "not
    # English" promise (see test_protocol_names_supported_languages_and_tiers
    # for the full pin on the new wording); this assertion now checks the
    # supported-profile phrasing, not the retired wording. Sliced to the
    # section itself -- see _firing_conditions_section.
    firing = _firing_conditions_section(text)
    assert (
        "supported" in firing and "zh-Hant" in firing
    ), "language firing condition missing"
    assert (
        "verdict mode fires only when findings" in firing
        and "1" in firing
    ), "verdict-mode firing condition missing"


def test_protocol_names_supported_languages_and_tiers():
    """The rewritten firing condition must name the two supported
    profiles (zh-Hant, ja) instead of the unkeepable "not English"
    promise, state each language's negation tier, carry a ja modality
    table, and record both JIS caveats -- "derived from" (never "per")
    plus the 参考 (reference, not normative) label. This pins Task 4's
    honest-firing-condition rewrite so a later edit cannot silently
    re-widen the promise back to "any non-English language"."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    firing = _firing_conditions_section(text)

    # Both supported language tags named in the firing condition itself
    # (sliced -- see _firing_conditions_section).
    assert "zh-Hant" in firing and "`ja`" in firing, "supported language tags missing"

    # The N/A-loud promise: a non-English, non-profile language says so
    # and produces nothing, rather than silently dropping the bullet.
    assert "N/A-loud" in firing, "N/A-loud promise missing"

    # Per-language negation tier, both directions -- asserted as TABLE
    # ROWS inside the section that owns them. A document-wide
    # `"hard-fail" in text` / `"warning" in text` check cannot fail:
    # "hard-fail" also occurs in the Lint-failure discussion and
    # "warning" occurs in the Lint-failure rule, so deleting either
    # tier row (or both) left the old assertions green. Pin the row
    # shape instead, sliced -- see _section.
    tier = _section(text, "Negation tier by language")
    assert re.search(
        r"\|\s*zh-Hant\s*\|\s*hard-fail\s*\|", tier
    ), "zh-Hant hard-fail tier row missing from the negation-tier table"
    assert re.search(
        r"\|\s*ja\s*\|\s*warning\s*\|", tier
    ), "ja warning tier row missing from the negation-tier table"

    # A ja modality table -- at least one JIS-derived form present.
    assert "しなければならない" in text, "ja modality table missing"

    # "derived from", never "per"/"conformant" for the JIS caveat.
    assert "derived from" in text, "'derived from' wording missing"

    # The 参考 caveat, stated plainly.
    assert "参考" in text, "参考 (reference-only) caveat missing"
    assert (
        "この規格で規定する事項ではない" in text
    ), "JIS verbatim 参考 quote missing"


def test_protocol_states_the_invocation_contract():
    """The protocol must tell an executor HOW to invoke the pipeline,
    not just describe it abstractly. Round-2 finding: `--lang` appeared
    nowhere under `loom-code/skills/`, and the protocol never named the
    three scripts -- so an executor at a live Japanese gate invents the
    invocation, omits `--lang`, and both lint and render silently fall
    back to the `zh-Hant` profile, checking Japanese text against the
    Chinese closed negation set at hard-fail tier. That is verbatim the
    stuck-gate bug this arc exists to remove, reintroduced at the only
    site that executes. Pin the contract: the three script names, the
    split step's language-neutrality, the MUST on `--lang` for lint and
    render, and the consequence of omitting it."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    inv = _section(text, "Invocation contract")

    for script in (
        "adjudication_split.py",
        "adjudication_lint.py",
        "adjudication_render.py",
    ):
        assert script in inv, f"invocation contract does not name {script}"

    # Split is language-neutral -- it takes no --lang.
    assert "takes no `--lang`" in inv, "split's language-neutrality not stated"

    # Lint and render MUST be passed --lang, with the two profile tags.
    assert "MUST" in inv, "the --lang duty is not stated as a MUST"
    assert "zh-Hant" in inv and "`ja`" in inv, "profile tags missing from --lang duty"

    # The consequence of omitting it, stated plainly.
    assert "Omitting `--lang`" in inv, "omission consequence not stated"
    assert (
        "default `--lang` to `zh-Hant`" in inv
    ), "the zh-Hant default of the flag is not stated"
    assert (
        "hard-fail" in inv
    ), "omission consequence does not name the hard-fail tier it trips"


def test_warning_lines_have_an_executor_action_and_a_named_channel():
    """WARNING-tier lint output is the ja negation tier's designed
    steady state (plus the modality check on every profile), so the
    protocol must define what the executor DOES with it -- round 2
    found three live readings (regenerate / hand-edit / pass through)
    and the document picked none. It must also name the real channel:
    the checks only `print()` to the orchestrator's stdout, the
    units-JSON schema has no field for a warning, and neither render
    template emits one -- so 'informs the adjudicator' is true only
    because the executor relays it."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    rule = _section(text, "Lint-failure rule")

    # Not a failure: no regeneration, no hand-edit, no gate block.
    assert "WARNING lines are not a failure" in rule, "WARNING action not stated"
    assert "do not regenerate" in rule, "the no-regenerate action is missing"
    assert "do not hand-edit" in rule, "the no-hand-edit action is missing"
    assert "do not block the gate" in rule, "the no-block action is missing"

    # The relay channel, and that it is a duty rather than automatic.
    assert "stdout" in rule, "the stdout channel is not named"
    assert (
        "the executor's duty" in rule
    ), "relaying is not stated as the executor's duty"
    assert (
        "the rendered page does not carry them" in rule
    ), "the renderer's non-carriage of warnings is not stated"

    # And the negation-tier table's 'informs the adjudicator' claim must
    # point at that same relay rather than assert it happens by itself.
    tier = _section(text, "Negation tier by language")
    assert (
        "the executor relays" in tier
    ), "ja tier row still claims the warning reaches the adjudicator by itself"


def test_modality_rule_reads_as_a_set_of_accepted_forms():
    """Round-2 finding: the rule said modals map to a fixed target-
    language *term* while the ja table gives each modal a SET of 2-3
    accepted forms (matching the shipped `modality_map` tuples). Both
    readings were live and only the set reading is true for ja. Pin the
    single rule that covers both profiles -- zh-Hant's one-form entries
    and ja's multi-form entries as instances of it -- while keeping the
    'never a paraphrase / never a synonym swap' force and the pointer
    to adjudication_profiles.py as the transcription source."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    rule = _section(text, "Fixed modality mapping")

    assert (
        "set of accepted target-language forms" in rule
    ), "the modality rule does not read as a set of accepted forms"
    assert (
        "one form per modal" in rule and "two or three" in rule
    ), "the rule does not reconcile zh-Hant's single forms with ja's multiple"
    assert "never a paraphrase" in rule, "the 'never a paraphrase' force was lost"
    assert "never a synonym swap" in rule, "the 'never a synonym swap' force was lost"
    assert (
        "adjudication_profiles.py" in rule
    ), "the transcription-source pointer was lost"


def test_schema_and_purpose_are_not_chinese_only():
    """The view now serves two profiles, so no field description may
    describe the target language as Chinese. `rendition` said "the
    Chinese rendering of the unit"; the field is the rendering in
    whichever profile fired. Pinned as an absence over the whole
    section so any of the five field descriptions re-acquiring a
    zh-only claim fails this test, plus a positive pin on the
    replacement wording."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    schema = _section(text, "Units-JSON schema")

    assert (
        "target-language rendering" in schema
    ), "`rendition` does not describe itself as the target-language rendering"
    assert (
        "Chinese" not in schema
    ), "a units-JSON field description still names Chinese as the target language"

    # Same class, in the section that states who the view is for.
    why = _section(text, "Why this exists")
    assert (
        "Chinese or Japanese" in why
    ), "the purpose section still claims a Chinese-only adjudicator"


def test_ja_modality_table_transcribes_the_shipped_profile():
    """The protocol states its modality forms are transcribed from
    `adjudication_profiles.py`'s `modality_map` -- so the tables must
    not drift from what actually ships. Without this pin the drift is
    invisible: the whole-branch fix that made the ja forms
    verb-independent suffixes (「してはならない」 -> 「てはならない」) and
    dropped bare 「しない」 from must-not left the protocol table still
    listing the retired サ変 forms, and every existing pin stayed
    green. Assert every shipped form of every profile appears in the
    mapping section, and that the retired 「しない」 debt is no longer
    described as carried."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    mapping = _section(text, "Fixed modality mapping")

    for tag, subheading in (("zh-Hant", "### zh-Hant"), ("ja", "### ja")):
        table = mapping.split(subheading, 1)[1].split("\n### ", 1)[0]
        # Exact row equality, not `form in table`: every shipped ja form
        # is a proper SUFFIX of the サ変 form it replaced, so a
        # substring check passes against the stale table it is meant
        # to catch.
        rows = _table_forms(table)
        for term, forms in get_profile(tag).modality_map:
            assert term in rows, f"{tag}: no table row for '{term}'"
            assert rows[term] == list(forms), (
                f"{tag} '{term}': table lists {rows[term]} but "
                f"adjudication_profiles.py ships {list(forms)} -- the "
                "protocol's transcription has drifted from the shipped profile"
            )

    # The forms are suffixes, not whole predicates -- a reader who
    # copies them as-is must know they attach to a preceding verb.
    assert (
        "verb-independent suffix" in mapping
    ), "the protocol does not say the ja forms are verb-independent suffixes"

    # The T2 debt was retired by dropping bare 「しない」; the protocol
    # must not still describe it as a carried debt.
    assert (
        "carried as a known debt" not in mapping
    ), "the protocol still carries the 「しない」 debt that dropping the form retired"
    assert "retire" in mapping, "the protocol does not record the debt's retirement"


def test_invocation_contract_pins_the_shipped_copy():
    """The invocation contract must pin WHICH copy of the pipeline
    scripts an executor runs, and gate delivery on the render stamp.
    Every past silent failure (2026-08-14..18) was a copy the executor
    chose over the one shipped beside this protocol file -- a bare
    filename, a hardcoded plugin-cache version directory, or a
    repo-relative path from the session's cwd. Pin the self-locating
    relative-resolution rule (../../../scripts/ from this file's own
    absolute path), its one exception (a session developing these
    scripts runs its own working tree's copy), and the pre-delivery
    stamp/version check -- all inside the section, and confirm
    CLAUDE_PLUGIN_ROOT is absent (substitution never reaches a
    protocol file opened via Read; the token would survive literally
    and expand to empty in a shell)."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    inv = _section(text, "Invocation contract")

    assert "../../../scripts/" in inv, "self-locating relative script path missing"
    assert "generator" in inv, "pre-delivery generator-stamp check missing"
    assert "CLAUDE_PLUGIN_ROOT" not in inv, (
        "CLAUDE_PLUGIN_ROOT would survive literally in a protocol file "
        "opened via Read and expand to empty in a shell"
    )


def test_invocation_contract_resolves_the_round2_findings():
    """Round 2 docs-review findings on the invocation contract, all
    pinned inside the §Invocation contract slice:

    Finding 1 (inconsistency): the three pipeline bullets show bare
    filenames (`python3 <script>.py`), which the "Which copy runs"
    rule forbids as the actual invocation form. The contradiction is
    resolved by explicitly marking the bullets as order/flag
    documentation, not invocation syntax -- pin that the marker text
    is present.

    Finding 2 (omission): "Before delivering" originally gave a
    failure branch only for "no stamp"; a present-but-mismatched
    stamp had no instruction. Pin that the mismatch branch now says
    do-not-deliver and names the re-run-then-surface fallback.

    Finding 3 (ambiguity): the working-tree-copy exception was
    judgment-shaped ("a session developing these scripts themselves").
    Pin that it is now a checkable test -- the active plan/brief scope
    naming a `loom-code/scripts/adjudication_*.py` file as edited by
    the current task."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    inv = _section(text, "Invocation contract")

    # Finding 1 -- bullets marked as order/flags only, not invocation syntax.
    assert (
        "document invocation ORDER and FLAGS only" in inv
    ), "the pipeline bullets are not marked as order/flag documentation"
    assert (
        "not by the bare filename shown here" in inv
    ), "the bullets do not disclaim the bare-filename form as invocation syntax"

    # Finding 2 -- the mismatch failure branch. Two brittleness classes
    # broke this pin when the section was later reflowed, and the fix
    # treats both; a future reader should not mis-learn which one did the
    # damage. (a) The phrase spanned a hard newline, so the raw slice no
    # longer contained it -- collapsing whitespace fixes that. (b) The
    # revision inserted a clause MID-PHRASE ("... does NOT match --
    # including the literal `unknown` ... -- is the same outcome ..."),
    # which broke contiguity outright; whitespace collapse alone would NOT
    # have saved it. Splitting the claim into two `and`-joined substrings
    # is the load-bearing half. The pin still owns the same claim: proven
    # by mutation -- rewriting the protocol's "do not deliver it" to
    # "deliver it anyway" fails this test.
    inv_flat = " ".join(inv.split())
    assert (
        "version does NOT match" in inv_flat
        and "is the same outcome as no stamp" in inv_flat
    ), "a version-mismatch stamp is not treated as equivalent to no stamp"
    assert (
        "surface the mismatch to the user" in inv_flat
    ), "the re-run-then-surface fallback for a persistent mismatch is missing"

    # Finding 3 -- checkable carve-out, not judgment-shaped prose.
    assert (
        "checkable, not a judgment call" in inv
    ), "the working-tree-copy exception is not marked checkable"
    assert (
        "loom-code/scripts/adjudication_*.py" in inv
        and "current task edits" in inv
    ), "the working-tree-copy exception does not give an operational test"
