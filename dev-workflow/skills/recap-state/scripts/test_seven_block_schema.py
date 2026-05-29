"""
Tests for dev-workflow/skills/recap/references/seven-block-schema.md

Asserts:
  - 7 H2/H3 block headings (Situation, Background, Assessment, User messages,
    Why-this-question, Pending, Synthesis-check) are present (case-insensitive)
  - 5 共通核心原則 anchors present: structured-schema, quote-not-paraphrase,
    all-user-messages, synthesis-check, plain-language
  - 1 good-example block + 1 bad-example block
  - Bad example demonstrates BOTH paraphrase-creep AND jargon-creep

WHY: The seven-block-schema.md is the SSOT for the Recap skill's output contract.
     Every principle must be machine-verifiable at test time so schema drift
     (someone editing the file and dropping a block) is caught immediately —
     before SKILL.md routing breaks silently at runtime.
"""

import pathlib
import re

BUNDLE_PATH = (
    pathlib.Path(__file__).parent.parent / "references" / "seven-block-schema.md"
)

# ── helpers ─────────────────────────────────────────────────────────────────


def load_bundle() -> str:
    """Load bundle file; fail with a clear message if missing (RED state)."""
    assert BUNDLE_PATH.exists(), (
        f"Bundle file not found: {BUNDLE_PATH}\n"
        "This is the expected RED state — create the file to go GREEN."
    )
    return BUNDLE_PATH.read_text(encoding="utf-8")


def heading_present(text: str, keyword: str) -> bool:
    """
    Return True if any H2/H3 heading contains `keyword`.
    Case-insensitive. Accepts zh-TW / ja alongside English.
    A heading line is one that starts with ## or ###.
    """
    pattern = re.compile(
        r"^#{2,3}\s+.*" + re.escape(keyword) + r".*$",
        re.IGNORECASE | re.MULTILINE,
    )
    return bool(pattern.search(text))


def anchor_present(text: str, anchor: str) -> bool:
    """
    Return True if `anchor` appears as a markdown anchor target or
    as a heading/bold keyword in the file.
    We look for the anchor string with optional surrounding formatting
    (bold, heading markers, or bare text). Case-insensitive.
    """
    pattern = re.compile(re.escape(anchor), re.IGNORECASE)
    return bool(pattern.search(text))


# ── main test ────────────────────────────────────────────────────────────────


def test_all_seven_blocks_and_five_principles_present() -> None:
    """
    Verify the bundle ships:
      1. All 7 V1 block headings (case-insensitive; multilingual-friendly)
      2. All 5 共通核心原則 anchors
      3. A good-example block
      4. A bad-example block
      5. Bad example mentions BOTH paraphrase-creep AND jargon-creep
         (so the 5th plain-language principle has visible coverage)

    WHY each check matters:
      Blocks: the fixed schema is the user-visible value; any dropped block
              silently breaks the agent's output structure.
      Principles: the 5 principles are the WHY behind each schema rule;
                  dropping one removes the rationale that makes the rule
                  memorable and enforceable in downstream reviews.
      Examples: without a concrete good/bad pair the schema is abstract;
                the contrast is the primary teaching mechanism.
      Dual-vice: paraphrase-creep alone or jargon-creep alone only covers
                 half the plain-language principle; both must be present.
    """
    text = load_bundle()

    # ── 7 block headings ────────────────────────────────────────────────────
    required_headings = [
        "Situation",
        "Background",
        "Assessment",
        # "User messages" — allow partial match; "User" is the key token
        "User",
        # "Why-this-question" — allow partial match; "Why" is the key token
        "Why",
        "Pending",
        "Synthesis",
    ]
    for keyword in required_headings:
        assert heading_present(text, keyword), (
            f"Expected H2/H3 heading containing '{keyword}' not found.\n"
            f"All 7 V1 blocks (Situation / Background / Assessment / "
            f"User messages / Why-this-question / Pending / Synthesis-check) "
            f"must appear as section headings."
        )

    # ── 5 共通核心原則 anchors ───────────────────────────────────────────────
    required_anchors = [
        "structured-schema",
        "quote-not-paraphrase",
        "all-user-messages",
        "synthesis-check",
        "plain-language",
    ]
    for anchor in required_anchors:
        assert anchor_present(text, anchor), (
            f"Expected principle anchor '{anchor}' not found.\n"
            f"All 5 共通核心原則 (structured-schema / quote-not-paraphrase / "
            f"all-user-messages / synthesis-check / plain-language) must be "
            f"present. The 5th (plain-language) is skill-specific per the "
            f"2026-05-26 brief amendment."
        )

    # ── good-example block ───────────────────────────────────────────────────
    assert re.search(r"good.example|good example", text, re.IGNORECASE), (
        "Expected a 'good example' section not found. "
        "The good/bad contrast is the primary teaching mechanism for the schema."
    )

    # ── bad-example block ────────────────────────────────────────────────────
    assert re.search(r"bad.example|bad example", text, re.IGNORECASE), (
        "Expected a 'bad example' section not found. "
        "The bad example must demonstrate paraphrase-creep + jargon-creep."
    )

    # ── bad example covers BOTH paraphrase-creep AND jargon-creep ───────────
    # Locate bad-example section first so we only scan that subsection.
    bad_section_match = re.search(
        r"(?:bad.example|bad example).*",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    assert bad_section_match, "Bad-example section not found (already checked above)."
    bad_section_text = bad_section_match.group(0)

    assert re.search(r"paraphrase", bad_section_text, re.IGNORECASE), (
        "Bad example must mention 'paraphrase' (paraphrase-creep vice). "
        "This provides visible coverage for principle 2 (quote-not-paraphrase) "
        "and principle 5 (plain-language) contrast."
    )
    assert re.search(r"jargon", bad_section_text, re.IGNORECASE), (
        "Bad example must mention 'jargon' (jargon-creep vice). "
        "This provides visible coverage for principle 5 (plain-language)."
    )
