"""Tests for scripts/lib/novel_prompts.py — scene-window prompt builders.

Covers Phase B of translation-toolkit v0.2.0 novel-mode plan. Verifies the
six-section Decision 4 layout, prev/next-window edge cases (None and
truncation), glossary rendering, and the reflect/improve prompts.
"""
from __future__ import annotations

import sys
from pathlib import Path

# tests/ -> scripts/
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.novel_prompts import (  # noqa: E402
    build_scene_draft_prompt,
    build_scene_improve_prompt,
    build_scene_reflect_prompt,
)
from lib.scene_chunker import Scene  # noqa: E402


def _scene(text: str = "彼女は窓を開けた。風が部屋を満たした。") -> Scene:
    return Scene(
        index=0,
        source_text=text,
        boundary_type="heading",
        token_count=len(text) // 3,
    )


def _intake() -> dict:
    return {
        "source_locale": "ja-JP",
        "target_locale": "en-US",
        "mode": "faithful",
        "register": "literary",
        "domain": "general",
    }


# -------------------- DRAFT --------------------


def test_draft_prompt_contains_decision_4_sections() -> None:
    """All 6 H1 sections present in correct order per Decision 4."""
    prompt = build_scene_draft_prompt(
        scene=_scene(),
        prev_scene_v2=None,
        next_scene_source=None,
        intake_spec=_intake(),
        glossary_hits=[],
    )
    headers = [
        "# Translation parameters",
        "# Glossary terms -- USE THESE, do not invent alternatives (only those that hit in current scene + prev/next windows)",
        "# Previous scene (last ~500 tokens) -- for continuity",
        "# CURRENT SCENE -- translate ALL of this",
        "# Next scene opening (first ~200 tokens) -- for narrative flow context",
        "# Output requirements",
    ]
    positions = [prompt.find(h) for h in headers]
    assert all(p >= 0 for p in positions), f"missing headers: {positions}"
    assert positions == sorted(positions), f"out-of-order headers: {positions}"


def test_draft_prompt_first_scene_no_prev() -> None:
    """prev_scene_v2=None → '(none -- first scene)' marker, not literal None."""
    prompt = build_scene_draft_prompt(
        scene=_scene(),
        prev_scene_v2=None,
        next_scene_source="次のシーンの始まり。",
        intake_spec=_intake(),
        glossary_hits=[],
    )
    assert "(none -- first scene of chapter)" in prompt
    assert "None" not in prompt.split("# CURRENT SCENE")[0]


def test_draft_prompt_truncates_long_prev() -> None:
    """prev_scene_v2 with >500 tokens → only last ~500 tokens visible."""
    # 500 tokens ≈ 1500 chars. Build 3000 chars; expect ~1500-char tail.
    head = "A" * 3000
    tail = "TAIL_MARKER_END"
    prev = head + tail
    prompt = build_scene_draft_prompt(
        scene=_scene(),
        prev_scene_v2=prev,
        next_scene_source=None,
        intake_spec=_intake(),
        glossary_hits=[],
    )
    # Tail must appear, head's leading bytes must NOT.
    assert tail in prompt
    # The first 1000 'A' chars should not all be present (we kept only last 1500 chars).
    head_leading = "A" * 2000
    assert head_leading not in prompt
    # Quick sanity: the prev section block bytes shouldn't exceed ~1500 + tail.
    prev_section = prompt.split("# Previous scene")[1].split("# CURRENT SCENE")[0]
    assert len(prev_section) < 2000


def test_draft_prompt_short_prev_kept_intact() -> None:
    """prev_scene_v2 within budget is included verbatim, no truncation."""
    short_prev = "前のシーンの最後の段落です。"
    prompt = build_scene_draft_prompt(
        scene=_scene(),
        prev_scene_v2=short_prev,
        next_scene_source=None,
        intake_spec=_intake(),
        glossary_hits=[],
    )
    assert short_prev in prompt


def test_draft_prompt_last_scene_no_next() -> None:
    """next_scene_source=None → '(none -- last scene)' marker."""
    prompt = build_scene_draft_prompt(
        scene=_scene(),
        prev_scene_v2=None,
        next_scene_source=None,
        intake_spec=_intake(),
        glossary_hits=[],
    )
    assert "(none -- last scene of chapter)" in prompt


def test_draft_prompt_truncates_long_next() -> None:
    """next_scene_source with >200 tokens → only first ~200 tokens visible."""
    # 200 tokens ≈ 600 chars. Build 1500 chars; expect ~600-char head.
    head_marker = "HEAD_MARKER_BEGIN"
    body = "B" * 1500
    nxt = head_marker + body
    prompt = build_scene_draft_prompt(
        scene=_scene(),
        prev_scene_v2=None,
        next_scene_source=nxt,
        intake_spec=_intake(),
        glossary_hits=[],
    )
    assert head_marker in prompt
    # Most of the trailing 'B' filler should NOT be present.
    assert ("B" * 1000) not in prompt
    next_section = prompt.split("# Next scene opening")[1].split(
        "# Output requirements"
    )[0]
    assert len(next_section) < 800


def test_draft_prompt_renders_glossary_hits() -> None:
    """glossary_hits=[3 entries] → all 3 source/target terms appear in output."""
    hits = [
        {
            "source_term": "桜",
            "target_term": "cherry blossom",
            "notes": "season:spring",
            "audit_path": "direct",
        },
        {
            "source_term": "侍",
            "target_term": "samurai",
            "notes": "",
            "audit_path": "direct",
        },
        {
            "source_term": "刀",
            "target_term": "katana",
            "notes": "weapon",
            "audit_path": "pivot.en-US (via 'sword')",
        },
    ]
    prompt = build_scene_draft_prompt(
        scene=_scene(),
        prev_scene_v2=None,
        next_scene_source=None,
        intake_spec=_intake(),
        glossary_hits=hits,
    )
    glossary_section = prompt.split("# Glossary terms")[1].split(
        "# Previous scene"
    )[0]
    for hit in hits:
        assert hit["source_term"] in glossary_section
        assert hit["target_term"] in glossary_section


def test_draft_prompt_drops_malformed_glossary_hits() -> None:
    """Entries with empty source_term or target_term are silently dropped."""
    hits = [
        {
            "source_term": "桜",
            "target_term": "cherry blossom",
            "notes": "",
            "audit_path": "direct",
        },
        {
            # Missing source_term -- should be dropped.
            "source_term": "",
            "target_term": "samurai",
            "notes": "",
            "audit_path": "direct",
        },
        {
            # Missing target_term -- should be dropped.
            "source_term": "刀",
            "target_term": "",
            "notes": "",
            "audit_path": "direct",
        },
    ]
    prompt = build_scene_draft_prompt(
        scene=_scene(),
        prev_scene_v2=None,
        next_scene_source=None,
        intake_spec=_intake(),
        glossary_hits=hits,
    )
    glossary_section = prompt.split("# Glossary terms")[1].split(
        "# Previous scene"
    )[0]
    # Well-formed entry present.
    assert "桜" in glossary_section
    assert "cherry blossom" in glossary_section
    # Malformed entries dropped: their unique target / source terms must be absent.
    assert "samurai" not in glossary_section
    assert "刀" not in glossary_section
    # No malformed line shape leaks through.
    assert "- ->" not in glossary_section
    assert "->  " not in glossary_section


def test_draft_prompt_empty_glossary() -> None:
    """glossary_hits=[] → section says (none) rather than dangling header."""
    prompt = build_scene_draft_prompt(
        scene=_scene(),
        prev_scene_v2=None,
        next_scene_source=None,
        intake_spec=_intake(),
        glossary_hits=[],
    )
    glossary_section = prompt.split("# Glossary terms")[1].split(
        "# Previous scene"
    )[0]
    assert "(none" in glossary_section


def test_draft_prompt_preserves_scene_source_verbatim() -> None:
    """scene.source_text byte-identical inside <TRANSLATE_THIS> markers."""
    text = "段落一です。\n\n段落二です。\n\n段落三です。"
    prompt = build_scene_draft_prompt(
        scene=_scene(text),
        prev_scene_v2=None,
        next_scene_source=None,
        intake_spec=_intake(),
        glossary_hits=[],
    )
    inside = prompt.split("<TRANSLATE_THIS>\n")[1].split("\n</TRANSLATE_THIS>")[0]
    assert inside == text


def test_draft_prompt_includes_intake_spec() -> None:
    """All five intake spec keys render into the parameters section."""
    prompt = build_scene_draft_prompt(
        scene=_scene(),
        prev_scene_v2=None,
        next_scene_source=None,
        intake_spec=_intake(),
        glossary_hits=[],
    )
    params = prompt.split("# Translation parameters")[1].split("# Glossary")[0]
    for key in ("source_locale", "target_locale", "mode", "register", "domain"):
        assert key in params


# -------------------- REFLECT --------------------


def test_reflect_prompt_4d_axes() -> None:
    """All 4 axes named: Accuracy / Fluency / Style / Terminology."""
    prompt = build_scene_reflect_prompt(
        scene=_scene(),
        draft_v1="She opened the window. Wind filled the room.",
        intake_spec=_intake(),
        glossary_hits=[],
    )  # kwargs-only per build_scene_reflect_prompt signature
    for axis in ("Accuracy", "Fluency", "Style", "Terminology"):
        assert axis in prompt
    # JSON output schema is described.
    assert '"accuracy"' in prompt
    assert '"terminology"' in prompt


# -------------------- IMPROVE --------------------


def test_improve_prompt_includes_critique() -> None:
    """critique_json renders into prompt; v1 included; ⟦P:NN⟧ note present."""
    critique = {
        "accuracy": [{"issue": "drops 'silently'", "suggestion": "add 'quietly'"}],
        "fluency": [],
        "style": [],
        "terminology": [],
    }
    draft_v1 = "She opened the window. Wind filled the room."
    prompt = build_scene_improve_prompt(
        scene=_scene(),
        draft_v1=draft_v1,
        critique_json=critique,
    )
    # Draft v1 appears verbatim.
    assert draft_v1 in prompt
    # Critique fields rendered.
    assert "drops 'silently'" in prompt
    assert "add 'quietly'" in prompt
    # Placeholder preservation reminder present.
    assert "⟦P:NN⟧" in prompt
