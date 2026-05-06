"""Tests for scripts/lib/scene_chunker.py — scene-aware chapter chunker.

Covers Phase A of translation-toolkit v0.2.0 novel-mode plan:
  1. test_explicit_marker_split           — '* * *', '***', '―――', '◇◇◇'
  2. test_blank_gap_split                 — >=2 blank lines between paragraphs
  3. test_heading_split                   — H2/H3 starts new scene
  4. test_fallback_token_fill             — no markers + oversize -> greedy fill
  5. test_real_novel_fixture              — inline 青空文庫-style JP excerpt
"""
from __future__ import annotations

import sys
from pathlib import Path

# tests/ -> scripts/
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.scene_chunker import Scene, chunk_chapter_into_scenes  # noqa: E402


# -------------------- 1. explicit marker --------------------

def test_explicit_marker_split() -> None:
    """All four allow-listed markers split, and the round-trip property holds:
    consumed-boundary text + concatenated scene source_text == original input.
    """
    chapter = (
        "First scene paragraph one.\n"
        "First scene paragraph two.\n"
        "\n"
        "* * *\n"
        "Second scene after stars.\n"
        "\n"
        "***\n"
        "Third scene after compact stars.\n"
        "\n"
        "―――\n"
        "Fourth scene after em-dashes.\n"
        "\n"
        "◇◇◇\n"
        "Fifth scene after diamonds.\n"
    )
    scenes = chunk_chapter_into_scenes(chapter)

    assert len(scenes) == 5
    assert scenes[0].source_text.startswith("First scene paragraph one.")
    assert "Second scene after stars." in scenes[1].source_text
    assert "Third scene after compact stars." in scenes[2].source_text
    assert "Fourth scene after em-dashes." in scenes[3].source_text
    assert "Fifth scene after diamonds." in scenes[4].source_text

    # Marker lines are consumed: no scene's source_text should contain them.
    for scene in scenes:
        for marker in ("* * *", "***", "―――", "◇◇◇"):
            assert marker not in scene.source_text, (
                f"Scene {scene.index} unexpectedly contains marker {marker!r}"
            )

    # Boundary tags: scenes 1-4 are bounded by an explicit marker on their
    # leading edge; scene 0 inherits the same tag (its trailing edge is an
    # explicit marker).
    assert all(s.boundary_type == "explicit_marker" for s in scenes)

    # Strict round-trip property: walk scenes in order, locate each
    # source_text as a contiguous slice of the input, and collect the gaps
    # between them. The collected gaps == the consumed boundary bytes.
    cursor = 0
    consumed_segments: list[str] = []
    for scene in scenes:
        idx = chapter.find(scene.source_text, cursor)
        assert idx >= cursor, f"Scene {scene.index} not found in order"
        consumed_segments.append(chapter[cursor:idx])
        cursor = idx + len(scene.source_text)
    consumed_segments.append(chapter[cursor:])  # trailing tail (if any)
    consumed = "".join(consumed_segments)

    # The byte-conservation invariant: input == sources + consumed bytes.
    # I.e. every byte of `chapter` is accounted for either in a scene or
    # in a consumed-boundary segment.
    assert sum(len(s.source_text) for s in scenes) + len(consumed) == len(chapter)

    # Each marker glyph must appear in the consumed text (markers were
    # consumed, not retained in any source_text).
    for marker_line in ("* * *\n", "***\n", "―――\n", "◇◇◇\n"):
        assert marker_line in consumed, f"Expected {marker_line!r} in consumed boundaries"
    # Consumed text should be only marker + whitespace characters.
    consumed_stripped = consumed
    for marker in ("* * *", "***", "―――", "◇◇◇"):
        consumed_stripped = consumed_stripped.replace(marker, "")
    assert consumed_stripped.strip() == "", (
        f"consumed text contains non-marker non-blank bytes: {consumed_stripped!r}"
    )


# -------------------- 2. blank-gap --------------------

def test_blank_gap_split() -> None:
    """>=2 blank lines (i.e. >=3 newlines) between paragraphs splits scenes.
    A single blank line is just a paragraph separator and does NOT split.
    """
    chapter = (
        "Paragraph one.\n"
        "\n"
        "Paragraph two of scene one.\n"  # single blank above => same scene
        "\n"
        "\n"
        "Paragraph one of scene two.\n"  # double blank above => new scene
        "\n"
        "\n"
        "\n"
        "Paragraph one of scene three.\n"  # triple blank => still new scene
    )
    scenes = chunk_chapter_into_scenes(chapter)

    assert len(scenes) == 3
    assert "Paragraph one." in scenes[0].source_text
    assert "Paragraph two of scene one." in scenes[0].source_text
    assert "Paragraph one of scene two." in scenes[1].source_text
    assert "Paragraph one of scene three." in scenes[2].source_text
    assert all(s.boundary_type == "blank_gap" for s in scenes)

    # Round-trip: the consumed bytes between scenes must be only blank
    # lines (whitespace + newlines), nothing else.
    cursor = 0
    consumed_segments: list[str] = []
    for scene in scenes:
        idx = chapter.find(scene.source_text, cursor)
        assert idx >= cursor
        consumed_segments.append(chapter[cursor:idx])
        cursor = idx + len(scene.source_text)
    consumed_segments.append(chapter[cursor:])
    consumed = "".join(consumed_segments)
    assert consumed.strip() == "", (
        f"blank-gap consumed text must be all whitespace: {consumed!r}"
    )
    assert sum(len(s.source_text) for s in scenes) + len(consumed) == len(chapter)


def test_single_blank_line_does_not_split() -> None:
    """A single blank line is paragraph separation, not a scene boundary."""
    chapter = (
        "Para A.\n"
        "\n"
        "Para B.\n"
        "\n"
        "Para C.\n"
    )
    scenes = chunk_chapter_into_scenes(chapter)
    assert len(scenes) == 1
    assert "Para A." in scenes[0].source_text
    assert "Para B." in scenes[0].source_text
    assert "Para C." in scenes[0].source_text


# -------------------- 3. heading --------------------

def test_heading_split() -> None:
    """H2 and H3 lines start new scenes; the heading line stays with its scene."""
    chapter = (
        "# Chapter One\n"
        "\n"
        "Opening paragraph under chapter title.\n"
        "\n"
        "## Section A\n"
        "Body of section A.\n"
        "\n"
        "### Subsection A.1\n"
        "Body of subsection.\n"
    )
    scenes = chunk_chapter_into_scenes(chapter)

    assert len(scenes) == 3
    assert scenes[0].source_text.startswith("# Chapter One\n")
    assert "Opening paragraph" in scenes[0].source_text
    assert scenes[1].source_text.startswith("## Section A\n")
    assert "Body of section A." in scenes[1].source_text
    assert scenes[2].source_text.startswith("### Subsection A.1\n")
    assert "Body of subsection." in scenes[2].source_text
    assert all(s.boundary_type == "heading" for s in scenes)


# -------------------- 4. fallback token-fill --------------------

def test_fallback_token_fill_when_no_markers() -> None:
    """No markers + oversize content -> greedy paragraph-boundary fill."""
    # Build a chapter with many paragraphs and no markers/headings/blank-gaps.
    # ~150 chars/paragraph * 30 paragraphs = ~4500 chars => ~1500 tokens.
    paragraph = "This is a long paragraph that contains enough words to add up. " * 3
    chapter = "\n\n".join(f"Paragraph {i}: {paragraph}" for i in range(30))

    # Force fallback by setting a small ceiling.
    scenes = chunk_chapter_into_scenes(chapter, max_scene_tokens=200)

    assert len(scenes) >= 2, "small ceiling should force multiple sub-scenes"
    assert all(s.boundary_type == "fallback_token_fill" for s in scenes)
    # Each scene approximately respects the budget (token_count is approx;
    # a single oversize paragraph could exceed, but our paragraphs are
    # ~600 chars / 200 tokens which fits within ceiling).
    for s in scenes:
        assert s.token_count <= 250, f"Scene {s.index} too large: {s.token_count}"

    # Round-trip: with fallback only, no boundary text is consumed -> exact
    # concatenation must reproduce the input.
    rejoined = "".join(s.source_text for s in scenes)
    assert rejoined == chapter


def test_fallback_within_marker_run() -> None:
    """An oversize marker-bounded run sub-splits via fallback; the first
    sub-chunk keeps the marker tag, later ones get fallback_token_fill.
    """
    big_para = "Long paragraph content. " * 50  # ~1200 chars => ~400 tokens
    chapter = (
        f"{big_para}\n\n{big_para}\n\n{big_para}\n"
        "* * *\n"
        "Short final scene.\n"
    )
    scenes = chunk_chapter_into_scenes(chapter, max_scene_tokens=500)

    # First marker-run is oversize (~1200 tokens) and should split into >=2
    # scenes; final scene is the short one after the marker.
    assert len(scenes) >= 3
    assert scenes[0].boundary_type == "explicit_marker"
    assert any(s.boundary_type == "fallback_token_fill" for s in scenes[1:-1])
    assert scenes[-1].boundary_type == "explicit_marker"
    assert "Short final scene." in scenes[-1].source_text


# -------------------- 5. real-novel fixture (inline JP) --------------------

def test_real_novel_fixture_jp() -> None:
    """Inline 青空文庫-style JP fragment exercises the chunker end-to-end.

    Self-contained per Phase A spec; Phase D bundles a public-domain fixture
    file with attribution.
    """
    chapter = (
        "# 第一章 春の朝\n"
        "\n"
        "桜の花がはらはらと散っていた。少年は縁側に座り、\n"
        "庭の池を見つめていた。風が吹くと、水面に小さな波が立った。\n"
        "\n"
        "「もう春か」と少年はつぶやいた。\n"
        "去年の春は、まだ祖父が生きていた。\n"
        "\n"
        "* * *\n"
        "\n"
        "午後になって、母が呼びに来た。\n"
        "「お客さまよ」と母は言った。\n"
        "少年は立ち上がり、玄関へ向かった。\n"
        "\n"
        "## 第二節 来訪者\n"
        "\n"
        "玄関には見知らぬ男が立っていた。\n"
        "黒い帽子を深くかぶり、顔はよく見えなかった。\n"
        "「君が太郎君かい」と男は静かに言った。\n"
    )
    scenes = chunk_chapter_into_scenes(chapter)

    # Expect at least 3 scenes: H1+opening, post-marker block, H2+block.
    assert len(scenes) >= 3, f"expected >=3 scenes, got {len(scenes)}"

    # Each scene has a sane token_count via char/3 heuristic.
    for s in scenes:
        assert s.token_count >= 1
        assert s.token_count == max(1, len(s.source_text) // 3)
        assert s.source_text  # non-empty

    # Byte-conservation: scene sources appear in order as contiguous slices.
    cursor = 0
    for s in scenes:
        idx = chapter.find(s.source_text, cursor)
        assert idx >= cursor, f"scene {s.index} not in order"
        cursor = idx + len(s.source_text)

    # Markers/blank-gap text consumed; headings preserved.
    joined = "".join(s.source_text for s in scenes)
    assert "* * *" not in joined
    assert "# 第一章 春の朝" in joined
    assert "## 第二節 来訪者" in joined


# -------------------- shape sanity --------------------

def test_scene_dataclass_shape() -> None:
    """Scene exposes the four documented fields with correct types."""
    chapter = "Hello world.\n"
    scenes = chunk_chapter_into_scenes(chapter)
    assert len(scenes) == 1
    s = scenes[0]
    assert isinstance(s, Scene)
    assert isinstance(s.index, int)
    assert isinstance(s.source_text, str)
    assert isinstance(s.boundary_type, str)
    assert isinstance(s.token_count, int)
    assert s.index == 0


def test_empty_input_returns_empty_list() -> None:
    assert chunk_chapter_into_scenes("") == []


def test_indices_are_sequential() -> None:
    chapter = "A.\n* * *\nB.\n* * *\nC.\n"
    scenes = chunk_chapter_into_scenes(chapter)
    assert [s.index for s in scenes] == list(range(len(scenes)))
