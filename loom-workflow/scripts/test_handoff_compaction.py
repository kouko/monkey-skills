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

    # Naming it must not slide into firing it. A fixed character window
    # is bypassable two ways: (a) a new sentence elsewhere in the window
    # can name-and-fire the skill with a verb no blacklist enumerated,
    # riding on an unrelated disclaimer elsewhere in the window; (b) a
    # content-neutral reorder that keeps the mention and the disclaiming
    # clause verbatim can push them past a fixed distance and fail
    # compliant prose. Work at sentence granularity instead: split into
    # sentences, and require EVERY sentence that mentions the skill to
    # itself carry the user-agency markers — not "somewhere within N
    # characters", but within the same sentence. That is invariant to
    # both reordering (the clause travels with its sentence) and to the
    # verb used by an injected sentence (an added sentence naming the
    # skill has to earn its own markers; no verb list to dodge).
    sentences = re.split(r"(?<=[.!?])\s+", prepare_section)
    mentioning = [s for s in sentences if "loom-workflow:goal-create" in s]
    assert mentioning, "expected a sentence mentioning loom-workflow:goal-create"

    # User-agency markers: the skill must read as an option the USER may
    # take, not an instruction directed at whoever is reading. Every
    # sentence that names the skill must carry both.
    user_invokes = re.compile(r"\bthey can invoke\b.{0,60}\bthemselves\b", re.IGNORECASE)
    assistant_never = re.compile(r"\bnever invokes it\b", re.IGNORECASE)

    for sentence in mentioning:
        assert user_invokes.search(sentence), (
            "sentence mentioning goal-create lacks the 'user invokes it "
            f"themselves' marker in the SAME sentence: {sentence!r}"
        )
        assert assistant_never.search(sentence), (
            "sentence mentioning goal-create lacks the 'never invokes it' "
            f"marker in the SAME sentence: {sentence!r}"
        )

    # NOTE (residual gap, stated plainly): this still checks membership in
    # a fixed marker SET ("they can invoke ... themselves" / "never
    # invokes it") rather than a semantic understanding of user-agency —
    # it is a whitelist too, just one operating on marker phrases instead
    # of verbs, and at sentence (not character-window) granularity. A
    # rewrite of SKILL.md that disclaims agency in different words would
    # need this test updated. What sentence granularity buys over a
    # character window is specifically immunity to (a) an added sentence
    # riding on a distant disclaimer, and (b) reordering that separates
    # mention from disclaimer beyond a fixed distance — not immunity to
    # a differently-worded disclaimer.
