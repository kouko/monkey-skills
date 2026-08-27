"""
Structural tests for SKILL.md, the skill's entry point (Task 5).

Four tests:
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

Every polarity-bearing assertion is scoped to a heading section or a
sentence, never to a raw character window (a legitimate rewording that
shifts word count must not flip these). No assertion enumerates the
words a rule forbids; each binds its negation to the structural section
it governs instead.
"""

import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SKILL_PATH = SKILL_DIR / "SKILL.md"
GOAL_LINT_PATH = SKILL_DIR / "scripts" / "goal_lint.py"
PURPOSE_TEMPLATE_PATH = (
    SKILL_DIR.parent.parent.parent / "loom-code" / "scripts" / "templates" / "PURPOSE.md"
)


def _read_skill_md() -> str:
    assert SKILL_PATH.exists(), f"SKILL.md does not exist at {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


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
    assert intro_pin in text, (
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
    assert confirmation_pin in arc_body, (
        "ARC's confirmation-required sentence changed — update this pin "
        "if the reword is deliberate."
    )

    # --- The not-applicable path: named condition, named reason, no scaffolding. ---
    not_applicable_sentence = (
        "ARC is conditional. When the repository has neither a "
        "`docs/loom/PURPOSE.md`\nnor any `docs/loom/` store directory at "
        "all, ARC reports itself not\napplicable, names which of the two "
        "is missing, and scaffolds nothing —\ncreating the store is "
        "`loom-init`'s job, not this skill's."
    )
    assert not_applicable_sentence in arc_body, (
        "ARC's not-applicable sentence changed — update this pin if the "
        "reword is deliberate (must still: name the two conditions, "
        "require naming the missing one, and forbid scaffolding)."
    )


def test_reference_pointers_resolve():
    text = _read_skill_md()

    # Structural extraction: every backticked `references/...` or
    # `scripts/...` path token in the document, wherever it appears.
    paths = re.findall(r"`((?:references|scripts)/[^`\s]+)`", text)
    assert paths, "No relative reference/script paths found in SKILL.md"

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
