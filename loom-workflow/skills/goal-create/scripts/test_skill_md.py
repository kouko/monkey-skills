"""
Structural tests for SKILL.md, the skill's entry point (Task 5).

Five tests:
  1. test_declares_two_modes_and_conditional_arc — the RED/GREEN driver:
     both mode names (SESSION, ARC) appear as headings; ARC's
     user-lands-it rule; ARC's not-applicable path names its reason
     requirement; ARC's no-scaffolding rule.
  2. test_reference_pointers_resolve — cross-seam probe: every relative
     `references/*` and `scripts/*` path written in SKILL.md (Task 2's
     seam) resolves on disk relative to the skill directory.
  3. test_floor_invocation_line_names_the_script — cross-seam probe:
     the invocation line SKILL.md gives for the mechanical floor names
     Task 3's script path, and that path exists.
  4. test_arc_points_at_the_purpose_template_without_restating_it — ARC
     cites the purpose artifact's format by pointer (its path, or its
     `Done when:` anchor) and reproduces none of the purpose template's
     own field text verbatim — that template is the format SSOT.
  5. test_invocation_contract_is_offer_not_trigger — Task 6: the
     description states this skill never auto-fires; an `## Invocation`
     section names the three offer points where it is surfaced (never
     invoked) and states the ordering rule against `brainstorming`.

Every polarity-bearing assertion is scoped to a heading section or a
sentence, never to a raw character window (a legitimate rewording that
shifts word count must not flip these). Verbatim pins are compared
after whitespace normalisation (runs of whitespace collapsed to a
single space on both the pin and the searched text), so a pure
re-wrap — line breaks moved, words unchanged — still matches; a
genuine reword still fails. No assertion enumerates the words a rule
forbids; each binds its negation to the structural section it governs
instead.

The reference-path check (`test_reference_pointers_resolve`) finds
every `references/*` and `scripts/*` path in SKILL.md regardless of
form — backticked, inside a markdown link (with or without a title),
or bare in prose — and strips a trailing `#anchor` fragment before
resolving.
"""

import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SKILL_PATH = SKILL_DIR / "SKILL.md"
GOAL_LINT_PATH = SKILL_DIR / "scripts" / "goal_lint.py"
# loom 1.0 moved the templates into loom-code's contract package.
PURPOSE_TEMPLATE_PATH = (
    SKILL_DIR.parent.parent.parent / "loom-code" / "contract" / "templates" / "PURPOSE.md"
)


def _read_skill_md() -> str:
    assert SKILL_PATH.exists(), f"SKILL.md does not exist at {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


def _normalize_ws(s: str) -> str:
    """Collapse runs of whitespace to a single space. Used to compare a
    pinned sentence against SKILL.md prose so a pure re-wrap (line
    breaks moved, words unchanged) still matches, while a genuine
    reword (words added/removed/changed) still fails."""
    return re.sub(r"\s+", " ", s).strip()


def _frontmatter(text: str) -> str:
    """Return the YAML frontmatter body (between the two `---` fences).
    Structural scoping — never a character-distance slice."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "No YAML frontmatter found in SKILL.md"
    return match.group(1)


def _section(text: str, heading: str) -> str:
    """Return the body of one `## <heading>` section: from just after the
    heading line to the next `##` heading or end of text. Structural
    scoping — never a character-distance slice."""
    pattern = re.compile(
        r"^##\s+" + re.escape(heading) + r"\s*$\n(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    assert match, f"No '## {heading}' section found in SKILL.md"
    return match.group(1)


def test_declares_two_modes_and_conditional_arc():
    text = _read_skill_md()

    # --- Both mode names appear as their own sections. ---
    session_body = _section(text, "SESSION mode")
    arc_body = _section(text, "ARC mode")

    # --- Mode choice is by what the user asks, not agent inference. ---
    # Pinned verbatim: this sentence is the whole point of the two-mode
    # split — a rewording that drops "chosen by" or "never by the agent
    # guessing" must fail this test so the next editor updates the pin
    # deliberately instead of drifting the rule silently.
    intro_pin = (
        "Which mode runs is\nchosen by what the user asks for — a goal for "
        "this run, or a purpose for\nthe repository — never by the agent "
        "guessing from context."
    )
    assert _normalize_ws(intro_pin) in _normalize_ws(text), (
        "The mode-choice sentence changed — if this is a deliberate "
        "reword, update this pin to match (see module docstring)."
    )

    # --- SESSION emits the four-field goal (structural: its own section). ---
    assert "four-field goal" in session_body

    # --- ARC never writes the file without the user's confirmation. ---
    # Pinned verbatim for the same reason as above: this is the one rule
    # standing between ARC and silently landing an unconfirmed file.
    confirmation_pin = (
        "ARC never writes that file itself; the\ndraft is only ever "
        "landed by the user's own confirmation."
    )
    assert _normalize_ws(confirmation_pin) in _normalize_ws(arc_body), (
        "ARC's confirmation-required sentence changed — update this pin "
        "if the reword is deliberate."
    )

    # --- The not-applicable path: named condition, named reason, no
    # scaffolding. The condition is a CONJUNCTION — no store AND no
    # purpose file — not "no purpose file" alone: `check_north_star_link.py`
    # checks `store.is_dir()` and `purpose_path.is_file()` as two
    # independent conditions with different exits, and `loom-init`
    # commonly scaffolds the store while leaving the purpose file
    # unanswered, which is a real, handled, ARC-applicable case, not a
    # not-applicable one.
    #
    # NOTE — this exact sentence is also pinned verbatim in
    # loom-workflow/scripts/test_goal_create_compaction.py
    # (`arc_not_applicable`). A change here requires the same change
    # there, or that test breaks on its own next run.
    not_applicable_sentence = (
        "ARC is conditional. When the repository has no "
        "`docs/loom/` store and no\n`docs/loom/PURPOSE.md` file — "
        "nothing yet scaffolded to hold one — ARC\nreports itself not "
        "applicable, names the reason, and scaffolds nothing — creating "
        "the store is\n`loom-init`'s job, not this skill's."
    )
    assert _normalize_ws(not_applicable_sentence) in _normalize_ws(arc_body), (
        "ARC's not-applicable sentence changed — update this pin if the "
        "reword is deliberate (must still: name the missing-store-AND-"
        "missing-purpose-file condition as a conjunction, require naming "
        "the reason, and forbid scaffolding) — and update the twin pin in "
        "loom-workflow/scripts/test_goal_create_compaction.py."
    )


def test_reference_pointers_resolve():
    text = _read_skill_md()

    # Extraction covers every form the docstring claims: backticked,
    # inside a markdown link (titled or not), and bare in prose. The
    # path-character class stops at whitespace, backtick, `)`, or `"` —
    # the delimiters each of those forms actually uses — so it doesn't
    # reach past the path into surrounding punctuation.
    raw_matches = re.findall(r"(?:references|scripts)/[^`\s)\"]+", text)
    assert raw_matches, "No relative reference/script paths found in SKILL.md"

    paths = []
    for raw in raw_matches:
        # Strip a trailing sentence period (paths here never bare-end
        # in '.') and an #anchor fragment before resolving.
        candidate = raw[:-1] if raw.endswith(".") else raw
        candidate = candidate.split("#", 1)[0]
        paths.append(candidate)

    for rel_path in paths:
        resolved = SKILL_DIR / rel_path
        assert resolved.exists(), f"Reference path does not resolve: {rel_path}"

    # The two reference files this task points at must both be named.
    assert "references/goal-shape.md" in paths
    assert "references/input-floor.md" in paths


def test_floor_invocation_line_names_the_script():
    text = _read_skill_md()

    assert GOAL_LINT_PATH.exists(), f"Floor script missing: {GOAL_LINT_PATH}"

    # Structural: find the fenced code block that names goal_lint.py —
    # that is the invocation line, not prose mentioning the script.
    invocation_blocks = re.findall(r"```\n(.*?)\n```", text, re.DOTALL)
    matching = [block for block in invocation_blocks if "scripts/goal_lint.py" in block]
    assert matching, "No fenced invocation line names scripts/goal_lint.py"

    invocation_line = matching[0]
    assert "python3 scripts/goal_lint.py" in invocation_line

    # Honest statement: the floor checks structure only, the bar stays
    # judgement — required somewhere in the SESSION mode section.
    session_body = _section(text, "SESSION mode")
    assert "structure only" in session_body
    assert "judgement" in session_body or "judgment" in session_body

    # --- Lint-result rule: what to do with the checker's exit code.
    # Structural: bind the obligation to the ONE sentence that states it,
    # not to a character-distance window over the whole section.
    session_sentences = [
        s.strip()
        for s in re.split(r"(?<=\.)\s+", re.sub(r"\s+", " ", session_body))
        if s.strip()
    ]
    rewrite_sentence = next(
        (
            s
            for s in session_sentences
            if "exit 1" in s and "rewritten" in s
        ),
        None,
    )
    assert rewrite_sentence, (
        "SESSION mode must state what to do on exit 1: the draft is "
        "rewritten and re-checked."
    )
    # Positive-obligation check: "never" must bind to "shown" within the
    # sentence that states the user-facing consequence — a mutant that
    # drops the "never shown until 0" obligation (e.g. "may be shown
    # anyway") must fail this.
    never_shown_sentence = next(
        (s for s in session_sentences if "shown" in s and "0" in s), None
    )
    assert never_shown_sentence, (
        "SESSION mode must state a draft is never shown until the "
        "checker exits 0."
    )
    assert re.search(r"\bnever\b.*\bshown\b", never_shown_sentence), (
        "Expected 'never ... shown' bound within one sentence — a draft "
        "must not be presented before the checker exits 0."
    )


def test_arc_points_at_the_purpose_template_without_restating_it():
    text = _read_skill_md()
    arc_body = _section(text, "ARC mode")

    # --- Pointer present: the artifact's path AND its Done when: anchor. ---
    assert "docs/loom/PURPOSE.md" in arc_body
    assert "`Done when`" in arc_body or "Done when:" in arc_body

    # --- Never restated: the template's own field-label text must not
    # appear verbatim in this skill's ARC section. ---
    assert PURPOSE_TEMPLATE_PATH.exists(), (
        f"Purpose template missing at {PURPOSE_TEMPLATE_PATH} — "
        "cannot verify non-restatement against it"
    )
    template_text = PURPOSE_TEMPLATE_PATH.read_text(encoding="utf-8")

    # Extract the template's field-label lines (the SSOT prose this
    # skill must point at, never copy) and confirm none of them shows
    # up verbatim in ARC's own section.
    field_lines = [
        line.strip()
        for line in template_text.splitlines()
        if line.strip().startswith("**Why:**") or line.strip().startswith("**Done when:**")
    ]
    assert field_lines, "Could not locate the template's field-label lines"

    for field_line in field_lines:
        assert field_line not in arc_body, (
            f"ARC section restates the purpose template's field text verbatim: {field_line!r}"
        )


def test_invocation_contract_is_offer_not_trigger():
    text = _read_skill_md()

    # --- The description states this skill never auto-fires. ---
    # Pinned verbatim: this is the one sentence standing between this
    # skill and a description that silently claims auto-fire behavior
    # it does not have — update this pin if a reword is deliberate.
    never_fire_description_pin = (
        "This skill never fires on its own; it must be invoked by name."
    )
    assert never_fire_description_pin in _frontmatter(text)

    invocation_body = _section(text, "Invocation")

    # --- Named at exactly three offer points, each stated as a pointer
    # the caller must actively invoke, never as auto-fire sites. ---
    # Pinned verbatim for the same reason as above.
    offer_points_pin = (
        "It is named as an available\n"
        "option at exactly one point where the need for a goal is already\n"
        "visible: `loom-workflow:handoff`'s Prepare mode, when a user closes a\n"
        "session without capturing an explicit goal. That surface names this\n"
        "skill as an option the user can invoke; it never invokes it."
    )
    assert _normalize_ws(offer_points_pin) in _normalize_ws(invocation_body), (
        "The offer-points sentence changed — if this is a deliberate "
        "reword, update this pin to match (see module docstring)."
    )

    # --- Ordering rule against `brainstorming`: discovery stays with
    # brainstorming; this skill runs only after its brief exists. ---
    # Pinned verbatim for the same reason as above.
    ordering_pin = (
        "When `loom-design:capture-intent` is already running for the same "
        "work,\nthat station keeps discovery and this skill runs only after "
        "its intent\nexists, rather than competing for the same turn."
    )
    assert _normalize_ws(ordering_pin) in _normalize_ws(invocation_body), (
        "The brainstorming-ordering sentence changed — if this is a "
        "deliberate reword, update this pin to match (see module docstring)."
    )


# The token the Invocation section must contain for each surface that
# offers this skill. The surfaces themselves are read out of the repo,
# never from this map; an entry here only says how the section is
# expected to refer to one. A scanned path missing from this map fails
# loudly, because a new offer site the section has never heard of is the
# exact drift this test exists for.
# loom 1.0 deleted the purpose-link check and the finishing station, so
# handoff is the only surviving offer site.
_OFFER_SITE_MARKERS = {
    "loom-workflow/skills/handoff/SKILL.md": "loom-workflow:handoff",
}
_COUNT_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def _scan_offer_sites() -> set[str]:
    """Every runtime surface outside this skill that names it to a user.

    Every plugin in the repo is scanned, not the two that happen to offer
    it today — the Invocation section's claim is about the repo, so
    narrowing the scan to the known answer would make it unfalsifiable.
    Tests are excluded: a test asserting an offer exists is not itself an
    offer. So are READMEs and changelogs, which describe rather than run.
    """
    root = SKILL_DIR.parent.parent.parent
    plugins = sorted(p.parent for p in root.glob("*/.claude-plugin"))
    assert plugins, "no plugin directories found; the scan would pass vacuously"
    found = set()
    for plugin in plugins:
        for path in plugin.rglob("*"):
            if path.suffix not in {".md", ".py"} or not path.is_file():
                continue
            if SKILL_DIR in path.parents or path == SKILL_DIR:
                continue
            if path.name.startswith(("README", "CHANGELOG", "test_")):
                continue
            if "loom-workflow:goal-create" in path.read_text(encoding="utf-8"):
                found.add(path.relative_to(root).as_posix())
    return found


def test_invocation_section_counts_the_offer_sites_that_exist():
    """The stated number of offer points must be the number that exist.

    `test_invocation_contract_is_offer_not_trigger` pins that sentence
    verbatim, which guards its wording and nothing about its arithmetic.
    The count went stale the moment a third surface started naming this
    skill, and a verbatim pin cannot notice that — it is satisfied by the
    stale sentence surviving unedited. This reads the sites out of the
    repo instead, so adding one forces the sentence to be re-counted.
    """
    sites = _scan_offer_sites()
    unknown = sites - set(_OFFER_SITE_MARKERS)
    assert not unknown, (
        f"{sorted(unknown)} names this skill but the Invocation section has "
        "never been told about it; name it there and add its marker to "
        "_OFFER_SITE_MARKERS"
    )

    invocation_body = _section(_read_skill_md(), "Invocation")
    # "one point", "two points" — the sentence has to read as English.
    expected = (
        f"exactly {_COUNT_WORDS[len(sites)]} point"
        + ("" if len(sites) == 1 else "s")
    )
    assert expected in invocation_body, (
        f"{len(sites)} surfaces offer this skill "
        f"({sorted(sites)}), but the Invocation section does not say "
        f"{expected!r}"
    )
    for site in sorted(sites):
        assert _OFFER_SITE_MARKERS[site] in invocation_body, (
            f"{site} offers this skill but the Invocation section never "
            f"names it (looked for {_OFFER_SITE_MARKERS[site]!r})"
        )
