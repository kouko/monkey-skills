from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "loom-workflow/skills/handoff/SKILL.md"
SCHEMA_PATH = (
    REPO_ROOT / "loom-workflow/skills/handoff/references/handoff-schema.md"
)
BASELINE_WORDS = 1448


def test_entrypoint_preserves_prepare_resume_verification_and_stop_under_word_ceiling():
    text = SKILL_PATH.read_text(encoding="utf-8")

    essence = {
        "mode routing": [
            "Prepare mode",
            "Resume mode",
            "in-session re-orientation",
            "recap-state",
        ],
        "schema before artifact work": [
            "Before authoring any HANDOFF artifact",
            "Before interpreting any HANDOFF artifact",
            "read `references/handoff-schema.md` fully",
        ],
        "prepare state commands": [
            "git rev-parse HEAD",
            "git rev-parse --abbrev-ref HEAD",
            "git status --short",
            "git log --oneline -5",
            "claude --version",
        ],
        "ten blocks": [
            "all 10 blocks",
            "All user messages",
            "Recent decisions",
            "Verification commands",
            "Confidence flags",
        ],
        "launcher": [
            "Resume Launcher",
            "thin pointer",
            "USER DIRECTIVE:",
            "conversation_language",
        ],
        "resume verification": [
            "ls -t .claude/handoffs/ | head -1",
            "run every command",
            "verbatim output",
            "expected output",
            "If the schema read is unavailable",
            "missing expected output",
        ],
        "tier mismatch policy": [
            "[T1]",
            "[T2]",
            "untagged command is treated as [T1]",
            "REFUSE TO CONTINUE",
            "known benign drift",
        ],
        "synthesis stop": [
            "Synthesis-check",
            "Do not act until the user responds",
        ],
        "principles": [
            "structured-schema",
            "quote-not-paraphrase",
            "all-user-messages",
            "synthesis-check",
            "technical-precision",
        ],
    }
    for contract, needles in essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    prepare = text.index("## Prepare mode")
    prepare_schema = text.index("read `references/handoff-schema.md` fully", prepare)
    prepare_author = text.index("2. Write", prepare)
    assert prepare_schema <= prepare_author

    resume = text.index("## Resume mode")
    resume_schema = text.index("read `references/handoff-schema.md` fully", resume)
    resume_interpret = text.index("2. Read", resume)
    assert resume_schema <= resume_interpret

    assert SCHEMA_PATH.is_file()
    words = re.findall(r"\S+", text)
    assert len(words) >= int(BASELINE_WORDS * 0.75), len(words)
    assert len(words) <= 1187, len(words)
