from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "loom-workflow/skills/recap-state/SKILL.md"
SCHEMA_PATH = (
    REPO_ROOT
    / "loom-workflow/skills/recap-state/references/seven-block-schema.md"
)


def test_entrypoint_preserves_goal_grounded_sections_and_synthesis_gate():
    text = SKILL_PATH.read_text(encoding="utf-8")

    essence = {
        "in-session routing": [
            "in-session re-orientation",
            "away-summary",
            "cross-session",
            "HANDOFF",
        ],
        "natural output boundary": [
            "Keep planning internal",
            "Never output `<thinking>` or `<recap>` tags",
            "Never expose `Block N` labels",
            "natural headings in the conversation language",
        ],
        "schema before every recap": [
            "Read `references/seven-block-schema.md`",
            "full L3 template",
            "What to do",
        ],
        "verbatim preservation": [
            "quote-not-paraphrase",
            "spec-critical user phrases",
            "file paths",
            "error messages",
            "command names",
            "verbatim",
        ],
        "visual thresholds": [
            "Gap and assessment defaults to 2-col key:value",
            "2+ options",
            "items have metadata",
            "flatten ≥3 sub-items",
            "compare ≥2 options",
            "real topology",
            "known to render Mermaid",
            "unknown or terminal client",
            "Support counts as known only",
            "ASCII",
        ],
        "synthesis stop": [
            "Synthesis-check",
            "confirm or redirect",
            "wait",
            "does not continue until user responds",
        ],
        "five principles": [
            "structured-schema",
            "quote-not-paraphrase",
            "all-user-messages",
            "synthesis-check",
            "plain-language",
        ],
    }
    for contract, needles in essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    schema_read = text.index("Read `references/seven-block-schema.md`")
    render_contract = text.index("natural headings in the conversation language")
    assert schema_read < render_contract

    template_start = text.index("### Purpose and current position", render_contract)
    template_end = text.index("3. Apply", template_start)
    rendered_template = text[template_start:template_end]
    sections = (
        "### Purpose and current position",
        "### Essential background",
        "### Gap and current assessment",
        "### Why confirmation is needed now",
        "### Pending work",
        "### Align purpose and next step",
    )
    positions = [text.index(section, template_start) for section in sections]
    assert positions == sorted(positions)
    for forbidden in ("<thinking>", "</thinking>", "<recap>", "</recap>", "Block "):
        assert forbidden not in rendered_template

    assert SCHEMA_PATH.is_file()


def test_entrypoint_grounds_goal_and_closes_the_alignment_loop():
    text = SKILL_PATH.read_text(encoding="utf-8")

    required = (
        "current purpose is mandatory",
        "ground it in explicit conversation evidence",
        "broader purpose only when explicitly established",
        "do not invent short-, medium-, or long-term goals",
        "purpose is not yet aligned",
        "purpose, current position, and proposed next step",
    )
    missing = [needle for needle in required if needle not in text]
    assert not missing, f"goal-grounded loop contract missing: {missing}"
