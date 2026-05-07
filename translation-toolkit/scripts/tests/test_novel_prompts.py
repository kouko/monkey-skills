"""Tests for scripts/lib/novel_prompts.py — scene-window prompt builders.

Covers Phase B of translation-toolkit v0.2.0 novel-mode plan + the v0.3.0
Phase C 5D-literary reflect variant + dispatch. Verifies the six-section
Decision 4 layout, prev/next-window edge cases (None and truncation),
glossary rendering, the reflect/improve prompts, and the 5D-literary
critic with its four sub-concerns.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# tests/ -> scripts/
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.novel_prompts import (  # noqa: E402
    build_scene_draft_prompt,
    build_scene_improve_prompt,
    build_scene_reflect_5d_literary_prompt,
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
    """All 4 axes named: Accuracy / Fluency / Style / Terminology.

    v0.3.0 Decision B flipped novel-mode default to 5d-literary, so 4D is
    now an explicit opt-in via ``intake_spec.reflect_axes='4d'``. We pin
    the test to 4D so the assertion ('"terminology"' as the last JSON
    key with no trailing 'literariness') keeps documenting 4D behaviour.
    """
    intake = {**_intake(), "reflect_axes": "4d"}
    prompt = build_scene_reflect_prompt(
        scene=_scene(),
        draft_v1="She opened the window. Wind filled the room.",
        intake_spec=intake,
        glossary_hits=[],
    )  # kwargs-only per build_scene_reflect_prompt signature
    for axis in ("Accuracy", "Fluency", "Style", "Terminology"):
        assert axis in prompt
    # JSON output schema is described.
    assert '"accuracy"' in prompt
    assert '"terminology"' in prompt
    # 4D critic has NO literariness axis — that's 5D-literary's job.
    assert "literariness" not in prompt.lower()


# -------------------- 5D LITERARY REFLECT (v0.3.0 Phase C) --------------------


def _draft_v1() -> str:
    return "She opened the window. Wind filled the room."


def test_5d_literary_prompt_loads_canonical() -> None:
    """Builder loads canonical ``prompts/reflect-5d-literary.md`` body, not a
    hard-coded inline string.

    The SoT lives at ``scripts/canonical/prompts/reflect-5d-literary.md``;
    each skill's ``references/prompt-reflect-5d-literary.md`` is a
    byte-identical functional copy. We assert distinctive lines from the
    canonical body appear verbatim in the rendered output (so a stale
    hard-coded copy in ``novel_prompts.py`` would fail).
    """
    canonical = (
        SCRIPTS_DIR / "canonical" / "prompts" / "reflect-5d-literary.md"
    ).read_text(encoding="utf-8")
    # Pick a distinctive sentence from the canonical body that the builder
    # cannot synthesize on its own.
    distinctive = (
        "5. Literariness — assess the literary craft of the target:"
    )
    assert distinctive in canonical, "fixture invariant: canonical changed shape"

    # And byte-identical to the distributed copies.
    plugin_root = SCRIPTS_DIR.parent
    for skill in (
        "translation-i18n",
        "translation-doc",
        "translation-creative",
        "translation-audit",
        "translation-novel",
    ):
        copy = plugin_root / "skills" / skill / "references" / "prompt-reflect-5d-literary.md"
        assert copy.exists(), f"missing distributed copy: {copy}"
        assert copy.read_text(encoding="utf-8") == canonical, (
            f"drift between canonical and {skill}/references/"
        )

    prompt = build_scene_reflect_5d_literary_prompt(
        scene=_scene(),
        draft_v1=_draft_v1(),
        intake_spec=_intake(),
        glossary_hits=[],
        prev_scene_v2=None,
        next_scene_source=None,
    )
    assert distinctive in prompt


def test_5d_literary_prompt_includes_5_axes() -> None:
    """All 5 axes named in the rendered prompt body."""
    prompt = build_scene_reflect_5d_literary_prompt(
        scene=_scene(),
        draft_v1=_draft_v1(),
        intake_spec=_intake(),
        glossary_hits=[],
        prev_scene_v2=None,
        next_scene_source=None,
    )
    for axis in ("Accuracy", "Fluency", "Style", "Terminology", "Literariness"):
        assert axis in prompt
    # JSON output schema enumerates all 5 keys.
    for json_key in ('"accuracy"', '"fluency"', '"style"', '"terminology"', '"literariness"'):
        assert json_key in prompt


def test_5d_literary_prompt_lists_subconcerns() -> None:
    """The Literariness axis enumerates 4 sub-concerns: rhythm / euphony /
    archaism / register-shift fidelity."""
    prompt = build_scene_reflect_5d_literary_prompt(
        scene=_scene(),
        draft_v1=_draft_v1(),
        intake_spec=_intake(),
        glossary_hits=[],
        prev_scene_v2=None,
        next_scene_source=None,
    )
    for sub in ("Rhythm", "Euphony", "Archaism", "Register-shift fidelity"):
        assert sub in prompt, f"missing sub-concern: {sub}"


def test_5d_literary_prompt_includes_scene_window() -> None:
    """prev_v2 + current source + next_source all present in scene-window
    layout (Decision B)."""
    prev_marker = "PREV_SCENE_V2_MARKER"
    next_marker = "NEXT_SCENE_SOURCE_MARKER"
    current = "現在のシーン本文。"
    prompt = build_scene_reflect_5d_literary_prompt(
        scene=_scene(current),
        draft_v1=_draft_v1(),
        intake_spec=_intake(),
        glossary_hits=[],
        prev_scene_v2=prev_marker,
        next_scene_source=next_marker,
    )
    assert prev_marker in prompt
    assert current in prompt
    assert next_marker in prompt
    # And the 3 windows appear in order: prev → current → next.
    assert prompt.find(prev_marker) < prompt.find(current) < prompt.find(next_marker)


def test_dispatch_default_is_5d_literary() -> None:
    """intake_spec without ``reflect_axes`` → 5d-literary builder chosen
    (v0.3.0 Decision B default)."""
    intake = _intake()
    assert "reflect_axes" not in intake  # fixture invariant
    prompt = build_scene_reflect_prompt(
        scene=_scene(),
        draft_v1=_draft_v1(),
        intake_spec=intake,
        glossary_hits=[],
    )
    # 5D-literary fingerprint: Literariness axis + sub-concerns.
    assert "Literariness" in prompt
    assert "Rhythm" in prompt
    assert '"literariness"' in prompt


def test_dispatch_4d_when_opted() -> None:
    """intake_spec.reflect_axes='4d' → legacy 4D builder; no Literariness."""
    intake = {**_intake(), "reflect_axes": "4d"}
    prompt = build_scene_reflect_prompt(
        scene=_scene(),
        draft_v1=_draft_v1(),
        intake_spec=intake,
        glossary_hits=[],
    )
    # 4D fingerprint: 4 axes only.
    for axis in ("Accuracy", "Fluency", "Style", "Terminology"):
        assert axis in prompt
    assert "literariness" not in prompt.lower()


def test_dispatch_unknown_raises() -> None:
    """intake_spec.reflect_axes='6d' (or any unsupported value) → ValueError."""
    intake = {**_intake(), "reflect_axes": "6d"}
    with pytest.raises(ValueError, match="reflect_axes"):
        build_scene_reflect_prompt(
            scene=_scene(),
            draft_v1=_draft_v1(),
            intake_spec=intake,
            glossary_hits=[],
        )


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
