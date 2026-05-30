"""
Structural tests for handoff-schema.md bundle.

Tests verify:
- All 10 H2/H3 block headings present (case-insensitive)
- All 5 principle anchors present
- Good-example block present
- Bad-example block present + demonstrates BOTH paraphrase-creep AND plain-language-creep
- No Markdown links pointing to dev-workflow/skills/recap/ (skill-independence guarantee)

WHY: These tests encode the structural contract for the HANDOFF v0.1 schema bundle.
Any drift in heading names, missing principles, or cross-skill references would
break the SKILL.md routing and the L2 audience contract.
"""

import re
from pathlib import Path

BUNDLE_PATH = (
    Path(__file__).parent.parent / "references" / "handoff-schema.md"
)

REQUIRED_HEADINGS = [
    "frontmatter",
    "situation",
    "background",
    "all user messages",
    "recent decisions",
    "pending",
    "critical files",
    "do not touch",
    "verification",
    "confidence",
]

REQUIRED_PRINCIPLE_ANCHORS = [
    "structured-schema",
    "quote-not-paraphrase",
    "all-user-messages",
    "synthesis-check",
    "technical-precision",
]

FORBIDDEN_CROSS_LINK = "dev-workflow/skills/recap"

# Regex pattern for H2/H3 headings.
# Use a plain r-string (not f-string) to avoid {2,3} being interpreted
# as an f-string expression. The heading text is appended via string concat.
_H2_H3_PREFIX = r"^#{2,3}\s+.*"


def _read_bundle() -> str:
    """Read the bundle file; fail with a descriptive message if missing."""
    assert BUNDLE_PATH.exists(), (
        f"Bundle file not found: {BUNDLE_PATH}\n"
        "This is expected at RED stage. Create the bundle to make this test pass."
    )
    return BUNDLE_PATH.read_text(encoding="utf-8")


def test_all_ten_blocks_and_five_principles_present() -> None:
    """
    Main structural gate: 10 block headings + 5 principle anchors + good/bad
    examples + bad-example demonstrates both paraphrase-creep and
    plain-language-creep + skill-independence (no recap cross-links).

    WHY: This test encodes the T1 Acceptance criteria from the plan verbatim.
    Splitting into sub-functions would lose the single-commit gate contract.
    """
    content = _read_bundle()
    content_lower = content.lower()

    # --- 10 block headings (case-insensitive) ---
    # Build pattern by string concat: _H2_H3_PREFIX + escaped heading.
    # Cannot use f-string here because {2,3} in rf"^#{2,3}..." would be
    # evaluated as an f-string expression, producing '^#(2, 3)...' instead
    # of the intended regex quantifier '^#{2,3}...'.
    missing_headings = []
    for heading in REQUIRED_HEADINGS:
        pattern = _H2_H3_PREFIX + re.escape(heading)
        if not re.search(pattern, content_lower, re.MULTILINE):
            missing_headings.append(heading)
    assert not missing_headings, (
        f"Missing block headings (case-insensitive): {missing_headings}\n"
        "All 10 blocks must appear as H2 or H3 headings in the bundle."
    )

    # --- 5 principle anchors ---
    missing_anchors = []
    for anchor in REQUIRED_PRINCIPLE_ANCHORS:
        # anchor appears as a markdown heading or inline anchor/bold
        if anchor not in content_lower:
            missing_anchors.append(anchor)
    assert not missing_anchors, (
        f"Missing principle anchors: {missing_anchors}\n"
        "All 5 共通核心原則 anchors must appear in the bundle."
    )

    # --- good-example block present ---
    assert "good example" in content_lower, (
        "Good-example block not found.\n"
        "The bundle must contain a section demonstrating correct HANDOFF."
    )

    # --- bad-example block present ---
    assert "bad example" in content_lower, (
        "Bad-example block not found.\n"
        "The bundle must contain a section demonstrating HANDOFF failures."
    )

    # --- bad example demonstrates paraphrase-creep ---
    assert "paraphrase-creep" in content_lower, (
        "'paraphrase-creep' not found in bundle.\n"
        "The bad-example section must explicitly demonstrate paraphrase-creep."
    )

    # --- bad example demonstrates plain-language-creep (L2-specific anti-pattern) ---
    assert "plain-language-creep" in content_lower, (
        "'plain-language-creep' not found in bundle.\n"
        "The bad-example section must explicitly demonstrate plain-language-creep "
        "(over-simplifying for an AI reader who needs precision — L2-specific anti-pattern, "
        "opposite of jargon-creep in recap)."
    )

    # --- skill-independence: no cross-links to recap bundle ---
    cross_link_hits = [
        line.strip()
        for line in content.splitlines()
        if FORBIDDEN_CROSS_LINK in line
    ]
    assert not cross_link_hits, (
        f"Found {len(cross_link_hits)} cross-link(s) to recap skill:\n"
        + "\n".join(f"  {line}" for line in cross_link_hits)
        + "\nHandoff bundle must be self-contained (Anthropic skill-independence rule)."
    )


def test_resume_launcher_section_present_and_constrained() -> None:
    """
    v0.2.0 gate: the schema documents the Resume Launcher (init prompt) as a
    prepare-mode output, with its three load-bearing properties and a USER
    DIRECTIVE field, plus good/bad examples.

    WHY: The launcher is the cross-session entry point. Drift here (dropping the
    thin / portable / no-stale-embeds constraints, or the USER DIRECTIVE field)
    would let prepare mode emit a context-re-dump blob that goes stale — the
    exact failure the bad example warns against.
    """
    content = _read_bundle()
    content_lower = content.lower()

    # --- Resume Launcher section heading present ---
    assert re.search(_H2_H3_PREFIX + re.escape("resume launcher"),
                     content_lower, re.MULTILINE), (
        "Resume Launcher section heading not found.\n"
        "§6 must document the init prompt prepare mode emits."
    )

    # --- USER DIRECTIVE field present (the optional first-task slot) ---
    assert "user directive" in content_lower, (
        "'USER DIRECTIVE' field not found in the Resume Launcher spec.\n"
        "The launcher must end with a blank USER DIRECTIVE line."
    )

    # --- three load-bearing property anchors present ---
    missing_props = [p for p in ("thin", "portable", "no stale embeds")
                     if p not in content_lower]
    assert not missing_props, (
        f"Missing Resume Launcher property anchors: {missing_props}\n"
        "The launcher spec must name all three constraints (thin / portable / "
        "no-stale-embeds)."
    )

    # --- both good and bad launcher examples present ---
    assert "good example — resume launcher" in content_lower, (
        "Good Resume Launcher example not found."
    )
    assert "bad example — resume launcher" in content_lower, (
        "Bad Resume Launcher example (anti-pattern) not found."
    )
