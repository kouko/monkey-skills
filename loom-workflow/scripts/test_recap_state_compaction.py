from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "loom-workflow/skills/recap-state/SKILL.md"
SCHEMA_PATH = (
    REPO_ROOT
    / "loom-workflow/skills/recap-state/references/seven-block-schema.md"
)


def test_entrypoint_preserves_l3_blocks_verbatim_rules_and_synthesis_gate():
    text = SKILL_PATH.read_text(encoding="utf-8")

    essence = {
        "in-session routing": [
            "in-session re-orientation",
            "away-summary",
            "cross-session",
            "HANDOFF",
        ],
        "sibling tags": [
            "exactly two sibling top-level tags",
            "<thinking>",
            "<recap>",
            "The first output character is `<`",
            "Do not add prose before `<thinking>`",
            "Do not wrap either tag in a Markdown fence",
        ],
        "schema before every recap": [
            "Read `references/seven-block-schema.md`",
            "full V1 template",
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
            "Block 3 Assessment defaults to 2-col key:value",
            "2+ options",
            "items have metadata",
            "flatten ≥3 sub-items",
            "compare ≥2 options",
            "real topology",
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
    render_contract = text.index("exactly two sibling top-level tags")
    assert schema_read < render_contract

    template_start = text.index("<recap>", render_contract)
    template_lead = text[text.index("2. Output exactly", schema_read) : template_start]
    assert "```" not in template_lead, "literal output skeleton must not model a fence"
    blocks = (
        "### Block 1 — Situation",
        "### Block 2 — Background",
        "### Block 3 — Assessment",
        "### Block 5 — Why-this-question",
        "### Block 6 — Pending",
        "### Block 7 — Synthesis-check",
    )
    positions = [text.index(block, template_start) for block in blocks]
    assert positions == sorted(positions)
    assert "### Block 4" not in text[template_start : text.index("</recap>", template_start)]

    assert SCHEMA_PATH.is_file()
