"""Structural grep-test guarding ascii-ui-patterns.md.

Two properties are pinned:

  1. The `## Conventions` bullets no longer instruct hand-drawing box borders
     unconditionally; instead they carry the availability-guarded generation
     instruction (Pin C of docs/loom/plans/2026-08-11-visualization-trigger-
     layer.md, transcribed verbatim) plus a Channel-rule-SSOT pointer sentence
     appended to `## When ASCII vs when Mermaid`.
  2. Every fenced skeleton in Patterns 1-4 is internally width-consistent:
     within one fenced block, every line whose first non-space character is
     one of `┌ ├ └ │` renders to the same display width. Labels in this file
     are all-ASCII, so `len()` equality per block is the oracle (box-drawing
     characters are width-1 codepoints).

Grep-pin discipline: assert FULL phrases (never lone tokens); `count()` the
load-bearing phrases to pin uniqueness
(docs/loom/memory/substring-assertions-must-pin-the-phrase-their-message-names.md).
"""

import re
from pathlib import Path

DOC = (
    Path(__file__).parents[2]
    / "skills"
    / "interaction-flows"
    / "references"
    / "ascii-ui-patterns.md"
)

BORDER_STARTS = ("┌", "├", "└", "│")

CHANNEL_SSOT_SENTENCE = (
    "Channel rule SSOT: `loom-code/hooks/family-relay.md §(b) Visual defaults`."
)

OLD_HAND_DRAW_BULLET = (
    "Use box-drawing characters (`┌ ─ ┐ │ └ ┘ ├ ┤ ┬ ┴ ┼`) for region borders."
)


def _text() -> str:
    assert DOC.is_file(), f"ascii-ui-patterns.md is absent at {DOC}"
    return DOC.read_text(encoding="utf-8")


def _normalize(text: str) -> str:
    """Collapse markdown hard-wrapping/list-continuation whitespace so a
    verbatim multi-line pin can be located as a phrase regardless of bullet
    indentation."""
    return re.sub(r"[ \t]*\n[ \t]*", " ", text)


def _fenced_blocks(text: str) -> list[str]:
    return re.findall(r"```\n(.*?)```", text, re.DOTALL)


# --- Conventions bullet swap -------------------------------------------------

def test_generation_guard_full_phrases_present():
    text = _text()
    norm = _normalize(text)

    assert OLD_HAND_DRAW_BULLET not in text, (
        "the unconditional hand-drawing bullet must be removed from "
        "## Conventions"
    )

    # Pin C core sentences (verbatim, whitespace-normalized for hard-wrap).
    for phrase in (
        "Generate every skeleton with the `ascii-graph` skill (ascii-graph-toolkit) "
        "when that skill is available in the session",
        "its width-aware generators and verify loop keep box borders aligned",
        "When the toolkit is absent (it ships separately and may not be "
        "installed): hand-drawing is permitted only when every label is "
        "plain ASCII",
        "a skeleton needing CJK labels degrades to a labeled markdown table "
        "or a prose region list",
        "never hand-drawn CJK box art (eyeballed full-width padding breaks "
        "silently)",
        "This absence is environmental (an optional sibling plugin), not an "
        "undelivered artifact of this plugin.",
    ):
        assert phrase in norm, f"Pin C phrase missing (verbatim): {phrase!r}"

    # Load-bearing uniqueness: the guard is stated exactly once.
    assert norm.count("Generate every skeleton with the `ascii-graph` skill") == 1

    # The Channel-rule-SSOT pointer sentence must appear at the end of
    # ## When ASCII vs when Mermaid.
    assert text.count(CHANNEL_SSOT_SENTENCE) == 1, (
        "Channel rule SSOT sentence must appear exactly once"
    )
    when_section_match = re.search(
        r"## When ASCII vs when Mermaid.*?(?=\n## )", text, re.DOTALL
    )
    assert when_section_match, "## When ASCII vs when Mermaid section must exist"
    assert CHANNEL_SSOT_SENTENCE in when_section_match.group(0), (
        "Channel rule SSOT sentence must be inside "
        "## When ASCII vs when Mermaid"
    )

    # Other Conventions bullets stay intact.
    for phrase in (
        "Wrap every skeleton in a plain fenced code block",
        "Label each region with a short uppercase tag",
        "Keep skeletons coarse",
        "One skeleton per distinct screen layout",
    ):
        assert phrase in text, f"existing Conventions bullet dropped: {phrase!r}"


# --- Skeleton width alignment -------------------------------------------------

def test_skeleton_border_lines_equal_width_per_block():
    text = _text()
    blocks = _fenced_blocks(text)
    assert len(blocks) >= 4, (
        f"expected at least 4 fenced skeletons (Patterns 1-4), found {len(blocks)}"
    )
    for i, block in enumerate(blocks):
        border_lines = [
            line
            for line in block.split("\n")
            if line.lstrip() and line.lstrip()[0] in BORDER_STARTS
        ]
        assert border_lines, f"block {i} has no border-starting lines to check"
        lengths = {len(line) for line in border_lines}
        assert len(lengths) == 1, (
            f"block {i} has misaligned border lines (lengths {sorted(lengths)}): "
            f"{border_lines}"
        )


def test_skeleton_blocks_have_no_trailing_whitespace():
    """Guards against the invisible-padding class of bug directly: a line
    that ends in whitespace inside a fenced skeleton re-breaks silently on
    the next trim-on-save (docs/loom/plans/2026-08-11-visualization-trigger-
    layer.md wave-1 fixup, Fix 4)."""
    text = _text()
    blocks = _fenced_blocks(text)
    assert len(blocks) >= 4
    for i, block in enumerate(blocks):
        for line in block.split("\n"):
            assert line == line.rstrip(), (
                f"block {i} has a line with trailing whitespace: {line!r}"
            )
