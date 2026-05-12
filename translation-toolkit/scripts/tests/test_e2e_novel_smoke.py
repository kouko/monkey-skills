"""End-to-end smoke tests for translation-toolkit v0.2.0 novel mode (Phase D).

These exercise scene chunking + scene-window prompt building on a real
public-domain Japanese chapter excerpt, but DO NOT invoke any LLM. They
verify the structural Tier 1 acceptance:

- Fixture loads cleanly as UTF-8.
- chunk_chapter_into_scenes produces >=2 scenes with the expected
  boundary types (the fixture has both an H1 heading and an explicit
  ``* * *`` marker).
- Scene shape (non-empty, within max_scene_tokens budget).
- Draft prompts contain Decision 4's six H1 sections.
- Glossary lookup machinery runs without error against terms drawn from
  the chapter (positive coverage NOT asserted -- canonical glossary is
  i18n-biased; project_glossary is the caller's responsibility).
- Total v0.2.0 prompt-token cost across the chapter is well under the
  v0.1.0 whole-document-windowing baseline (the headline cost-reduction
  claim of the v0.2.0 plan).

Real LLM validation is deferred to Phase E live-test.
"""
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
ROOT = SCRIPTS_DIR.parent
CANONICAL = SCRIPTS_DIR / "canonical"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
NOVEL_FIXTURE = FIXTURES / "sample-novel-chapter-ja.md"

sys.path.insert(0, str(SCRIPTS_DIR))

from lib.scene_chunker import chunk_chapter_into_scenes, approx_tokens
from lib.novel_prompts import build_scene_draft_prompt
from lib.glossary import lookup


# Decision 4: the six H1 section headings the DRAFT prompt must contain.
_DECISION_4_SECTIONS = (
    "# Translation parameters",
    "# Glossary terms",
    "# Previous scene",
    "# CURRENT SCENE",
    "# Next scene opening",
    "# Output requirements",
)

# Approximate per-scene scaffold cost for the v0.1.0 baseline prompt:
# v0.1.0 wraps the whole document inside <DOCUMENT>...</DOCUMENT>, marks the
# active chunk with <TRANSLATE_THIS>, and re-emits Translation parameters +
# Glossary terms + Output requirements alongside it. This is roughly the same
# scaffold the v0.2.0 scene-window prompt carries minus the prev/next windows.
# Treated as a flat ~150-token overhead so the cost comparison measures
# prompt-vs-prompt instead of prompt-vs-raw-source.
_V01_PROMPT_OVERHEAD_PER_SCENE = 150


def _load_fixture() -> str:
    return NOVEL_FIXTURE.read_text(encoding="utf-8")


def test_novel_smoke_fixture_exists_and_loads() -> None:
    """Fixture file ships with the repo, opens as UTF-8, has substantive prose."""
    assert NOVEL_FIXTURE.exists(), f"missing fixture: {NOVEL_FIXTURE}"
    text = _load_fixture()
    assert len(text) >= 1000, f"fixture too short ({len(text)} chars)"
    # Attribution comment in place.
    assert "青空文庫" in text
    assert "太宰治" in text
    # No BOM smuggled in.
    assert not text.startswith("﻿"), "fixture has UTF-8 BOM"


def test_novel_smoke_chunks_into_multiple_scenes() -> None:
    """Chunker produces >=2 scenes; explicit-marker + heading boundaries detected."""
    text = _load_fixture()
    scenes = chunk_chapter_into_scenes(text)
    assert len(scenes) >= 2, f"expected >=2 scenes, got {len(scenes)}"

    boundary_types = {s.boundary_type for s in scenes}
    # Fixture has both an H1 (`# Chapter 1 ...`) and a `* * *` marker line --
    # both structural classes must appear; assert each individually so a
    # regression on one class can't be masked by the other.
    assert "explicit_marker" in boundary_types, (
        f"missing explicit_marker boundary, got {boundary_types}"
    )
    assert "heading" in boundary_types, (
        f"missing heading boundary, got {boundary_types}"
    )


def test_novel_smoke_scene_total_chars_reasonable() -> None:
    """Each scene has non-empty source_text and stays within the default token budget."""
    text = _load_fixture()
    scenes = chunk_chapter_into_scenes(text)
    for s in scenes:
        assert s.source_text, f"scene {s.index} has empty source_text"
        assert s.token_count <= 2000, (
            f"scene {s.index} token_count {s.token_count} exceeds default 2000 budget"
        )


def test_novel_smoke_draft_prompt_contains_decision_4_sections() -> None:
    """A non-first scene's DRAFT prompt contains all six Decision 4 H1 sections."""
    text = _load_fixture()
    scenes = chunk_chapter_into_scenes(text)
    assert len(scenes) >= 2, "need >=2 scenes to test prev-window rendering"

    target_scene = scenes[1]
    prev_scene_v2 = scenes[0].source_text  # stand-in for v2; structural test only
    next_scene_source = scenes[2].source_text if len(scenes) >= 3 else None

    prompt = build_scene_draft_prompt(
        scene=target_scene,
        prev_scene_v2=prev_scene_v2,
        next_scene_source=next_scene_source,
        intake_spec={
            "source_locale": "ja-JP",
            "target_locale": "zh-TW",
            "mode": "faithful",
            "register": "literary",
            "domain": "novel",
        },
        glossary_hits=[],
    )
    for section in _DECISION_4_SECTIONS:
        assert section in prompt, f"missing Decision 4 section: {section!r}"


def test_novel_smoke_glossary_lookup_machinery_no_crash() -> None:
    """Glossary lookup machinery runs cleanly on terms drawn from the chapter.

    Verifies machinery, not coverage. Most narrative-prose JP terms are not in
    the canonical glossary (which is biased toward i18n / typography
    terminology). Project-supplied glossaries are the caller's job and
    out of scope for Phase D. We only assert that ``lookup`` returns a
    dict-or-None for each probe (no exceptions) and surface any hit
    informationally for the test runner.
    """
    probes = ["メロス", "王", "妹"]
    hits: list[str] = []
    for term in probes:
        result = lookup(CANONICAL, "ja-JP", "zh-TW", term)
        assert result is None or isinstance(result, dict), (
            f"lookup({term!r}) returned unexpected type {type(result)!r}"
        )
        if result is not None:
            hits.append(f"{term} -> {result['target_term']}")
    if hits:
        # Surfaced via -s; informational only.
        print(f"\n  unexpected canonical glossary hits: {hits}")


def test_novel_smoke_cost_reduction_under_50k_tokens() -> None:
    """v0.2.0 scene-window prompts cost < 50K tokens AND < v0.1.0 baseline.

    v0.1.0 windowing re-emits the entire chapter inside <DOCUMENT>...</DOCUMENT>
    once per chunk, so its baseline cost over N scenes is roughly
    ``N * approx_tokens(full_chapter)``.

    v0.2.0 emits prev (~500 tok) + current scene + next (~200 tok) per
    scene, so cost is roughly linear in chapter size.

    Both numbers are printed (visible with ``pytest -s``) so the ratio is
    auditable per the v0.2.0 plan's cost-reduction headline.
    """
    text = _load_fixture()
    scenes = chunk_chapter_into_scenes(text)
    assert scenes, "fixture chunked to zero scenes"

    intake_spec = {
        "source_locale": "ja-JP",
        "target_locale": "zh-TW",
        "mode": "faithful",
        "register": "literary",
        "domain": "novel",
    }

    total_v02_tokens = 0
    for i, scene in enumerate(scenes):
        prev_scene_v2 = scenes[i - 1].source_text if i > 0 else None
        next_scene_source = scenes[i + 1].source_text if i + 1 < len(scenes) else None
        prompt = build_scene_draft_prompt(
            scene=scene,
            prev_scene_v2=prev_scene_v2,
            next_scene_source=next_scene_source,
            intake_spec=intake_spec,
            glossary_hits=[],
        )
        total_v02_tokens += approx_tokens(prompt)

    # v0.1.0 baseline: every chunk's prompt re-emits the whole document inside
    # <DOCUMENT>...</DOCUMENT> and carries the same per-call scaffold the
    # v0.2.0 prompt does (Translation parameters + Glossary + Output
    # requirements), minus the prev/next windows. Cost ~ len(scenes) *
    # (full_doc + scaffold). Without the scaffold term the comparison would
    # measure prompt-vs-raw-source rather than prompt-vs-prompt.
    full_doc_tokens = approx_tokens(text)
    total_v01_tokens = len(scenes) * (full_doc_tokens + _V01_PROMPT_OVERHEAD_PER_SCENE)

    # Surface for -s capture.
    ratio = (total_v02_tokens / total_v01_tokens) if total_v01_tokens else 0.0
    print(
        f"\n  v0.2.0 prompt tokens: {total_v02_tokens}"
        f"\n  v0.1.0 baseline tokens: {total_v01_tokens}"
        f"\n  ratio v0.2.0 / v0.1.0: {ratio:.3f}"
        f"\n  scenes: {len(scenes)}"
    )

    # Plan headline: total under 50K tokens for the chapter.
    assert total_v02_tokens < 50_000, (
        f"v0.2.0 cost {total_v02_tokens} >= 50K -- regression in scene-window prompt sizing"
    )
    # Tighter: v0.2.0 strictly cheaper than v0.1.0 baseline.
    assert total_v02_tokens < total_v01_tokens, (
        f"v0.2.0 ({total_v02_tokens}) not cheaper than v0.1.0 baseline ({total_v01_tokens})"
    )
