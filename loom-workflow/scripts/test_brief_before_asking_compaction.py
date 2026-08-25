from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "loom-workflow/skills/brief-before-asking/SKILL.md"
EXAMPLES_PATH = (
    REPO_ROOT
    / "loom-workflow/skills/brief-before-asking/references/EXAMPLES.md"
)
BASELINE_WORDS = 3072


def test_entrypoint_preserves_four_modes_and_briefing_contract_under_word_ceiling():
    text = SKILL_PATH.read_text(encoding="utf-8")

    # These pins protect observable routing, sequencing, and output contracts.
    essence = {
        "four modes": [
            "Mode A — Proactive",
            "Mode B — Reactive on Question",
            "Mode C — Reactive on Explanation",
            "Mode D — Reactive on Stakes",
        ],
        "proactive default": ["DEFAULT for any non-trivial fork", "default path"],
        "turn ordering": [
            "Turn-ordering rule (hard)",
            "next turn",
            "never fire the `AskUserQuestion` dialog in the same turn",
        ],
        "repeated confusion": [
            "2nd consecutive",
            "hard STOP",
            "check-question",
            "Mental Model",
        ],
        "six blocks": [
            "Mental Model",
            "Situation",
            "Why-this-fork",
            "Options",
            "My take",
            "Open ends",
        ],
        "escape hatches": [
            "just decide",
            "too long",
            "expand C",
            "full analysis",
        ],
        "pre-send boundary": [
            "First line",
            "Last line",
            "single thing you need",
        ],
        "conditional examples": ["references/EXAMPLES.md", "optional load"],
    }
    for contract, needles in essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    mode_positions = [text.index(f"Mode {letter} —") for letter in "ABCD"]
    assert mode_positions == sorted(mode_positions)

    block_positions = [
        text.index(label, text.index("## The 6-Block Briefing Structure"))
        for label in (
            "Mental Model",
            "Situation",
            "Why-this-fork",
            "Options",
            "My take",
            "Open ends",
        )
    ]
    assert block_positions == sorted(block_positions)

    assert EXAMPLES_PATH.is_file()
    words = re.findall(r"\S+", text)
    assert len(words) >= 2151, len(words)
    assert len(words) <= 2396, len(words)
