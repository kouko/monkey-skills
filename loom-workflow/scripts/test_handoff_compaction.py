import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "loom-workflow/skills/handoff/SKILL.md"
SCHEMA_PATH = (
    REPO_ROOT / "loom-workflow/skills/handoff/references/handoff-schema.md"
)


def test_entrypoint_preserves_prepare_resume_verification_and_stop():
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


def test_prepare_mode_names_goal_create():
    text = SKILL_PATH.read_text(encoding="utf-8")

    prepare = text.index("## Prepare mode")
    resume = text.index("## Resume mode")
    prepare_section = text[prepare:resume]

    assert "loom-workflow:goal-create" in prepare_section
    assert "goal-create" not in text[resume:]

    # Naming it must not slide into firing it. Anchor the check on the
    # text immediately around the mention, not just anywhere in the
    # section, so a rewording that keeps the substring but drops the
    # invariant is caught.
    mention = prepare_section.index("loom-workflow:goal-create")
    window = prepare_section[max(0, mention - 200) : mention + 200]

    # The disclaiming clause — the skill is something the USER invokes,
    # and Prepare mode explicitly disclaims invoking it — must survive.
    assert re.search(r"\bthey can invoke\b.{0,20}\bthemselves\b", window), (
        "expected the 'user invokes it themselves' disclaimer near the "
        "goal-create mention"
    )
    assert re.search(r"\bnever invokes it\b", window), (
        "expected an explicit 'never invokes it' disclaimer near the "
        "goal-create mention"
    )

    # Reject imperative framing directed at the skill itself (an
    # instruction to fire it, e.g. "Invoke `loom-workflow:goal-create`
    # now") rather than at the user ("they can invoke themselves").
    imperative_at_skill = re.compile(
        r"\b(invoke|run|call|execute)\b\s*`?\s*loom-workflow:goal-create",
        re.IGNORECASE,
    )
    assert not imperative_at_skill.search(window), (
        "found an imperative verb directed at goal-create — naming the "
        "skill must not read as an instruction to fire it"
    )
