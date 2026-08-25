from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "loom-workflow/skills/distill-sessions/SKILL.md"
RUNTIME_PROTOCOL_PATH = (
    REPO_ROOT
    / "loom-workflow/skills/distill-sessions/references/runtime-protocol.md"
)
BASELINE_WORDS = 3726


def test_entrypoint_preserves_essence_under_word_ceiling():
    text = SKILL_PATH.read_text(encoding="utf-8")

    # These are observable safety and completion contracts, not prose styling pins.
    essence = {
        "bare invocation approval": ["preview", "confirm", "before Stage 3"],
        "privacy boundary": ["Local-only", "No network calls", "subagent dispatch"],
        "observable-data limit": ["observable", "reasoning", "never infer"],
        "required artifacts": ["top.json", "merged.json", "proposal"],
        "stop conditions": ["skip", "warn", "1_000_000"],
        "final verification": ["Human review", "--approved", "atomic"],
        "conditional detail routing": [
            "references/runtime-protocol.md",
            "Read it when",
        ],
    }
    for contract, needles in essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    assert RUNTIME_PROTOCOL_PATH.is_file()
    words = re.findall(r"\S+", text)
    assert len(words) >= int(BASELINE_WORDS * 0.62), len(words)
    assert len(words) <= int(BASELINE_WORDS * 0.72), len(words)
