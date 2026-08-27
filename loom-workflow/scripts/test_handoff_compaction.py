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

    # Round 2 tried sentence-granularity marker matching ("they can invoke
    # ... themselves" + "never invokes it" in the same sentence) and it
    # broke both ways: a sentence can contain both markers and the mention
    # while "it" grammatically fails to refer to the skill (false PASS —
    # the check doesn't know what "it" points to), and an abbreviation-
    # unaware sentence splitter fragments a legitimate insertion like
    # "(i.e. the goal-capture skill)" into two pieces, separating the
    # mention from its own markers (false FAILURE). Whether a sentence
    # actually disclaims agency is a semantic question; no regex or
    # sentence splitter can decide it. So stop inferring meaning and pin
    # the sentence this test controls verbatim, exactly as the file's own
    # sentence-pinning idiom does elsewhere (see
    # test_entrypoint_preserves_prepare_resume_verification_and_stop).
    #
    # Trade-off, accepted deliberately: any rewording of this sentence —
    # even a faithful one, even inserting a harmless clarifying aside —
    # now FAILS this test. That is the point, not a defect: the sentence
    # carries a user-agency contract, so changing its wording must force
    # a conscious update to this pin rather than silently keep passing.
    # Nothing except this exact string can satisfy an exact match, so no
    # pronoun shuffle or rephrasing can pass while failing to say what it
    # says.
    disclaimer_sentence = (
        "If the user also wants this session's intent captured as an "
        "explicit goal with\nits own acceptance condition rather than "
        "only saved state, `loom-workflow:goal-create`\nis a separate "
        "option they can invoke themselves; Prepare mode only names it "
        "and\nnever invokes it."
    )
    # Anchor to the END of the Prepare-mode section (not just "somewhere in
    # it") so an extra sentence appended after the disclaimer — e.g. an
    # injected imperative telling the reader to invoke the skill anyway —
    # also fails: an unanchored substring check would let such trailing
    # prose ride along after an intact, unmodified pin.
    assert prepare_section.rstrip().endswith(disclaimer_sentence), (
        "Prepare mode's goal-create disclaimer sentence no longer matches "
        "the pinned text verbatim as the last content before Resume mode. "
        "If this is a deliberate, faithful reword of the disclaimer, "
        "update the pin above to match; if it isn't, the disclaimer "
        "regressed or something was appended after it."
    )
