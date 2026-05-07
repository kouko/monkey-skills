"""End-to-end smoke tests for translation-toolkit v0.3.0 Tier 2 (Phase F).

Plan reference: ``docs/superpowers/plans/2026-05-07-translation-toolkit-v0.3.0-tier2.md``
§"Phase F — E2E smoke + cost ceiling + version bump + READMEs".

Ten tests, NO real LLM calls. Mocked subagent dispatch returns canned JSON
responses; all prompt-shape and verdict-shape assertions are structural.

The tests exercise four v0.3.0 Tier 2 features end-to-end on a synthetic
two-chapter Japanese-novel fixture (``fixtures/sample-book-ja/``):

  1. Whole-book character pre-pass with cross-chapter merging.
  2. Whole-book world-glossary pre-pass with closed-enum ``cultural_references``
     category seeding.
  3. 5D literary critic prompt structural rendering.
  4. M3 deterministic linter on novel + doc-style targets.
  5. Glossary L1.5 tier resolution from pre-pass artifacts.
  6. Cheap-model split routing for the ``extractor`` role.
  7. Pre-pass cost-ceiling assertion (Decision E #2 — HARD-FAIL).

Real LLM validation is deferred to a manual live-test pass on a long-form
novel batch (translator-user feedback, post-merge).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
ROOT = SCRIPTS_DIR.parent
CANONICAL = SCRIPTS_DIR / "canonical"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
BOOK_DIR = FIXTURES / "sample-book-ja"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.character_extractor import (  # noqa: E402
    load_book_manifest,
    run_pre_pass_characters,
)
from lib.gate_m3_problem_analyze import evaluate_m3  # noqa: E402
from lib.glossary import lookup  # noqa: E402
from lib.novel_prompts import (  # noqa: E402
    build_scene_draft_prompt,
    build_scene_improve_prompt,
    build_scene_reflect_5d_literary_prompt,
)
from lib.scene_chunker import (  # noqa: E402
    approx_tokens,
    chunk_chapter_into_scenes,
)
from lib.world_glossary_extractor import (  # noqa: E402
    build_world_glossary_extraction_prompt,
    run_pre_pass_world_glossary,
)
from lib.character_extractor import (  # noqa: E402
    build_character_extraction_prompt,
)


# --------------------------------------------------------------------------- #
# Canned EXTRACTOR responses for the two-chapter fixture                       #
# --------------------------------------------------------------------------- #


def _ch1_character_response() -> str:
    """Canned character-EXTRACTOR response for chapter 1 (走れメロス opening).

    Surfaces the three principals and one alias. Subset chosen to match what
    a competent extractor would yield on this excerpt — the test asserts on
    canonical names + alias merging, not on exact extraction breadth.
    """
    return json.dumps({
        "characters": [
            {
                "canonical_name": "メロス",
                "canonical_target": "Melos",
                "aliases": [
                    {"source": "メロス", "target": "Melos"},
                    {"source": "彼", "target": "he"},
                ],
                "voice_notes": "earnest, impulsive, friend-loyalty motif",
                "first_seen_chapter": 0,
                "last_seen_chapter": 0,
            },
            {
                "canonical_name": "ディオニス",
                "canonical_target": "Dionysius",
                "aliases": [
                    {"source": "暴君ディオニス", "target": "the tyrant Dionysius"},
                ],
                "voice_notes": "tyrannical, world-weary, paranoid",
                "first_seen_chapter": 0,
                "last_seen_chapter": 0,
            },
            {
                "canonical_name": "セリヌンティウス",
                "canonical_target": "Selinuntius",
                "aliases": [],
                "voice_notes": "loyal stonemason, silent presence",
                "first_seen_chapter": 0,
                "last_seen_chapter": 0,
            },
        ]
    }, ensure_ascii=False)


def _ch2_character_response() -> str:
    """Canned character-EXTRACTOR response for chapter 2 (synthetic).

    Refines voice on Melos (adds ``reflective`` trait) and bumps
    ``last_seen_chapter`` to 1 — exercises cross-chapter merge on the
    canonical-name match path.
    """
    return json.dumps({
        "characters": [
            {
                "canonical_name": "メロス",
                "canonical_target": "Melos",
                "aliases": [
                    {"source": "彼", "target": "he"},
                ],
                "voice_notes": "earnest, impulsive, friend-loyalty motif, reflective",
                "first_seen_chapter": 0,
                "last_seen_chapter": 1,
            },
            {
                "canonical_name": "セリヌンティウス",
                "canonical_target": "Selinuntius",
                "aliases": [],
                "voice_notes": "loyal stonemason, silent presence",
                "first_seen_chapter": 0,
                "last_seen_chapter": 1,
            },
        ]
    }, ensure_ascii=False)


def _ch1_world_glossary_response() -> str:
    return json.dumps({
        "places": [
            {
                "canonical_source": "シラクス",
                "canonical_target": "Syracuse",
                "first_seen_chapter": 0,
            },
        ],
        "organizations": [],
        "world_terms": [
            {
                "canonical_source": "王城",
                "canonical_target": "the royal palace",
                "notes": "ディオニス's residence; site of M's arrest",
                "first_seen_chapter": 0,
            },
        ],
        "cultural_references": [
            {
                "source_phrase": "十字架にかけられて",
                "category": "religious_term",
                "handling_hint": "explain",
                "first_seen_chapter": 0,
            },
        ],
    }, ensure_ascii=False)


def _ch2_world_glossary_response() -> str:
    """Adds ONE new place (アクロポリス) and ONE new cultural reference
    (the synthetic literary maxim) — exercises growth across chapters.
    """
    return json.dumps({
        "places": [
            {
                "canonical_source": "アクロポリス",
                "canonical_target": "the acropolis",
                "first_seen_chapter": 1,
            },
        ],
        "organizations": [],
        "world_terms": [],
        "cultural_references": [
            {
                "source_phrase": "人を信ずるは、剣を磨くよりも難し。",
                "category": "literary_quotation",
                "handling_hint": "borrow",
                "first_seen_chapter": 1,
            },
        ],
    }, ensure_ascii=False)


def _make_dispatch(responses: list[str], invoked_models: list[str] | None = None):
    """Build a mock ``dispatch_subagent`` returning ``responses`` in order.

    If ``invoked_models`` is provided, each call's ``model`` arg is appended
    to it for assertion in the cheap-model-routing test.
    """
    queue = list(responses)

    def _dispatch(*, prompt: str, model: str) -> str:
        if invoked_models is not None:
            invoked_models.append(model)
        if not queue:
            raise AssertionError("dispatch called more times than canned responses")
        return queue.pop(0)

    return _dispatch


_INTAKE_SPEC = {
    "source_locale": "ja-JP",
    "target_locale": "en-US",
    "mode": "faithful",
    "register": "literary",
    "domain": "novel",
}


# --------------------------------------------------------------------------- #
# 1. Pre-pass character extraction across the two-chapter fixture              #
# --------------------------------------------------------------------------- #


def test_pre_pass_extracts_against_fixture(tmp_path):
    """Run ``run_pre_pass_characters`` against ``sample-book-ja/``;
    assert merged result contains the three principals and aliases merged."""
    manifest = load_book_manifest(BOOK_DIR)
    assert [p.name for p in manifest.chapters] == [
        "chapter-01.md", "chapter-02.md",
    ]

    dispatch = _make_dispatch([
        _ch1_character_response(),
        _ch2_character_response(),
    ])
    output = tmp_path / "characters.json"
    artifact = run_pre_pass_characters(
        book_manifest=manifest,
        intake_spec=_INTAKE_SPEC,
        output_path=output,
        dispatch_subagent=dispatch,
    )

    canonical_names = {c["canonical_name"] for c in artifact["characters"]}
    assert canonical_names == {"メロス", "ディオニス", "セリヌンティウス"}, (
        f"expected the three principals, got {canonical_names}"
    )

    melos = next(c for c in artifact["characters"]
                 if c["canonical_name"] == "メロス")
    # Ch1 alias '彼' merged with itself in ch2 (deduped).
    alias_sources = {a["source"] for a in melos["aliases"]}
    assert "メロス" in alias_sources
    assert "彼" in alias_sources
    # Voice notes refined in ch2 to include 'reflective'.
    assert "reflective" in melos["voice_notes"]
    # last_seen_chapter advanced to 1.
    assert melos["last_seen_chapter"] == 1
    # first_seen_chapter preserved at 0.
    assert melos["first_seen_chapter"] == 0


# --------------------------------------------------------------------------- #
# 2. Pre-pass world-glossary extraction                                        #
# --------------------------------------------------------------------------- #


def test_pre_pass_world_glossary_extracts(tmp_path):
    """Run world-glossary pre-pass; assert places + cultural_references seed
    and that ch2 contributes the new アクロポリス place + literary_quotation."""
    manifest = load_book_manifest(BOOK_DIR)
    dispatch = _make_dispatch([
        _ch1_world_glossary_response(),
        _ch2_world_glossary_response(),
    ])
    output = tmp_path / "world-glossary.json"
    artifact = run_pre_pass_world_glossary(
        book_manifest=manifest,
        intake_spec=_INTAKE_SPEC,
        output_path=output,
        dispatch_subagent=dispatch,
    )

    place_sources = {p["canonical_source"] for p in artifact["places"]}
    assert "シラクス" in place_sources, "ch1 place missing"
    assert "アクロポリス" in place_sources, (
        "ch2 should contribute the new place アクロポリス"
    )

    ref_categories = {r["category"] for r in artifact["cultural_references"]}
    assert "religious_term" in ref_categories
    assert "literary_quotation" in ref_categories, (
        "ch2 should contribute a literary_quotation cultural reference"
    )

    # Closed-enum handling_hint values present + valid.
    for ref in artifact["cultural_references"]:
        assert ref["handling_hint"] in {"borrow", "explain", "approximate"}, (
            f"unexpected handling_hint: {ref!r}"
        )


# --------------------------------------------------------------------------- #
# 3. 5D literary critic prompt structure                                       #
# --------------------------------------------------------------------------- #


def test_5d_literary_prompt_renders_for_fixture():
    """Pull a scene from chapter 1, render the 5D-literary critic prompt;
    assert structure + literariness key + sub-concerns enumerated."""
    text = (BOOK_DIR / "chapter-01.md").read_text(encoding="utf-8")
    scenes = chunk_chapter_into_scenes(text)
    assert len(scenes) >= 2, "fixture must yield >=2 scenes for this test"

    target_scene = scenes[1]
    prompt = build_scene_reflect_5d_literary_prompt(
        scene=target_scene,
        draft_v1="(stand-in v1 draft for prompt-shape assertion)",
        intake_spec=_INTAKE_SPEC,
        glossary_hits=[],
        prev_scene_v2=scenes[0].source_text,
        next_scene_source=scenes[2].source_text if len(scenes) >= 3 else None,
    )

    # Five-axis output schema present.
    for axis in ("accuracy", "fluency", "style", "terminology", "literariness"):
        assert f'"{axis}"' in prompt, f"missing JSON key {axis!r} in 5D prompt"

    # Literariness sub-concerns enumerated (per canonical reflect-5d-literary.md).
    for sub in ("Rhythm", "Euphony", "Archaism", "Register-shift fidelity"):
        assert sub in prompt, f"missing literariness sub-concern {sub!r}"

    # Scene-window context wired in.
    assert target_scene.source_text in prompt
    assert "Previous scene" in prompt or "prev" in prompt.lower()


# --------------------------------------------------------------------------- #
# 4-6. M3 on novel + doc fixtures                                              #
# --------------------------------------------------------------------------- #


# Pre-translated EN excerpt of 走れメロス chapter 1 — clean (no JP residual).
# Synthesized for this test from the fixture's narrative content. Length is
# tuned so the JP→EN ratio sits inside the [0.60, 3.00] M3b band (JP→EN
# typically expands; we aim for ratio ~1.0 against the ~913-token JP source).
# Punctuation is en-US ASCII (M3c skips for non-CJK target).
_NOVEL_EN_CLEAN = (
    "Melos was furious. He had resolved that he must, without fail, "
    "remove the king of evil cunning and tyranny. Politics meant nothing "
    "to Melos. Melos was a shepherd of the village. He had spent his "
    "days playing the flute and tending the sheep. Yet against wickedness "
    "he was, more than any other, sensitive. Before dawn this day Melos "
    "had set out from his village, crossed fields and mountains, and "
    "arrived in this city of Syracuse, ten leagues away. Melos had no "
    "father, no mother. He had no wife. He lived alone with his shy "
    "younger sister, sixteen years of age. This sister was, in the near "
    "future, to take as her bridegroom an honest young shepherd of the "
    "village. The wedding day was close at hand. It was for this reason "
    "that Melos had come all the way to the city, to gather the bridal "
    "trousseau and the goods for the wedding feast.\n\n"
    "First, he gathered the wares; then he strolled along the broad "
    "street of the capital. Melos had a friend from his earliest years, "
    "Selinuntius, who now worked as a stonemason in this city of "
    "Syracuse. Melos planned to call on him soon. They had not seen each "
    "other in a long while, and Melos looked forward to the visit. As "
    "he walked, Melos began to think the city felt strange. It was "
    "still. The sun had already set and the streets were dark, but it "
    "seemed something more than the night made the city so unaccountably "
    "lonely. Even Melos, an easygoing man, grew uneasy by degrees. He "
    "stopped a young man on the road and asked what had happened — two "
    "years ago when he had last visited the city, even at night people "
    "had sung in the streets, and the city had been lively. The young "
    "man shook his head and gave no answer.\n\n"
    "* * *\n\n"
    "After walking some way, Melos met an old man, and this time pressed "
    "his question more forcefully. The old man would not answer. Melos "
    "shook the old man by the shoulders and asked again, until at last, "
    "in a voice that feared the surrounding darkness, the old man "
    "replied: \"The king is killing people.\" \"Why does he kill?\" Melos "
    "asked. \"They say it is because they harbor evil hearts. Yet no one "
    "harbors an evil heart.\" \"Has he killed many?\" \"Yes — first the "
    "king's own brother-in-law, then the heir, then his own younger "
    "sister, then the sister's child, then the queen, and then the wise "
    "minister Alexis.\" Hearing this, Melos was furious. \"What an "
    "outrageous king. He cannot be allowed to live.\" Melos was a simple "
    "man. With his purchases still on his back he marched into the royal "
    "palace, and was at once seized by the city watch. Searched, he was "
    "found to be carrying a short sword, and the matter grew serious. "
    "Melos was dragged before the king. \"What did you intend with this "
    "dagger? Speak!\" the tyrant Dionysius demanded, quietly but with "
    "weight. His face was pale, and the lines between his brows had "
    "been carved as if by a knife. \"To save the city from a tyrant's "
    "hand,\" Melos answered without flinching."
)


# Synthetic doc-style EN target — technical-docs prose register.
# Length ratio in band; clean (no JP residual).
_DOC_JA_SOURCE = (
    "本ドキュメントは、translation-toolkit プラグインの設計概要を述べる。"
    "プラグインは i18n / 技術文書 / 広告コピー / 小説章 の翻訳を提供する。"
    "v0.3.0 では novel pre-pass、5D literary critic、M3 deterministic linter、"
    "そして cheap-model split が追加された。"
)
_DOC_EN_CLEAN = (
    "This document describes the design overview of the translation-toolkit "
    "plugin. The plugin provides translation across i18n, technical docs, "
    "ad copy, and novel chapters. v0.3.0 adds: novel pre-pass, 5D literary "
    "critic, M3 deterministic linter, and cheap-model split."
)


def test_m3_passes_clean_target_fixture_novel():
    """M3 on a clean EN target derived from chapter 1 → PASS (no FAIL/WARN)."""
    source_text = (BOOK_DIR / "chapter-01.md").read_text(encoding="utf-8")
    verdict = evaluate_m3(
        source_text=source_text,
        target_text=_NOVEL_EN_CLEAN,
        source_locale="ja-JP",
        target_locale="en-US",
    )
    assert verdict.verdict == "PASS", (
        f"expected PASS on clean EN novel target, got {verdict.verdict}; "
        f"subrules: {[(s.subrule, s.verdict, s.detail) for s in verdict.subrules]}"
    )


def test_m3_fails_seeded_residual_jp_novel():
    """Seed 5% katakana residual into the EN target → m3a HARD FAIL → M3 FAIL."""
    # Inject ~5% JP katakana to trip the 1% residual threshold.
    seeded = (
        _NOVEL_EN_CLEAN
        + " メロスは怒った。シラクスへ向かう。セリヌンティウスを救う。"
    )
    source_text = (BOOK_DIR / "chapter-01.md").read_text(encoding="utf-8")
    verdict = evaluate_m3(
        source_text=source_text,
        target_text=seeded,
        source_locale="ja-JP",
        target_locale="en-US",
    )
    assert verdict.verdict == "FAIL", (
        f"expected FAIL on JP-residual EN target, got {verdict.verdict}"
    )
    m3a = next(s for s in verdict.subrules if s.subrule == "m3a")
    assert m3a.verdict == "FAIL"
    assert m3a.tier == "HARD"


def test_m3_warns_seeded_length_violation_novel():
    """Synthetic short EN target → m3b SHOULD WARN → M3 WARN (no HARD FAIL)."""
    source_text = (BOOK_DIR / "chapter-01.md").read_text(encoding="utf-8")
    # Tiny target: ratio well below 0.6 (the JP→EN low band).
    verdict = evaluate_m3(
        source_text=source_text,
        target_text="Melos was angry.",
        source_locale="ja-JP",
        target_locale="en-US",
    )
    assert verdict.verdict == "WARN", (
        f"expected WARN on too-short EN target, got {verdict.verdict}"
    )
    m3b = next(s for s in verdict.subrules if s.subrule == "m3b")
    assert m3b.verdict == "WARN"
    assert m3b.tier == "SHOULD"


# --------------------------------------------------------------------------- #
# 7. M3 wired in for translation-doc                                           #
# --------------------------------------------------------------------------- #


def test_m3_runs_in_doc_pipeline():
    """Per Decision H, translation-doc Layer 4 invokes M3 in v0.3.0.

    Smoke check: ``evaluate_m3`` accepts a doc-style source/target pair and
    returns a well-formed verdict whose ``subrules`` carry all three subrules
    in order (m3a, m3b, m3c). This is the same library entry point that
    translation-doc's Layer 4 audit-trail step calls — there is no per-skill
    Python wiring (the gate is a sibling lib module, called directly from
    the skill body's reference flow).
    """
    verdict = evaluate_m3(
        source_text=_DOC_JA_SOURCE,
        target_text=_DOC_EN_CLEAN,
        source_locale="ja-JP",
        target_locale="en-US",
    )
    assert verdict.verdict in {"PASS", "WARN", "FAIL"}
    # All three subrules surface in the audit-trail (per Decision H — doc
    # adopts M3 alongside novel; no subrule skipping).
    surfaced = [s.subrule for s in verdict.subrules]
    assert surfaced == ["m3a", "m3b", "m3c"], (
        f"M3 verdict should expose all three subrules in order, got {surfaced}"
    )
    # Doc-style EN target is clean → expect PASS overall on this fixture.
    assert verdict.verdict == "PASS"


# --------------------------------------------------------------------------- #
# 8. Cheap-model split routes to extractor role                                #
# --------------------------------------------------------------------------- #


def test_cheap_model_split_routes_to_extractor(tmp_path):
    """``model: {'default': opus, 'extractor': haiku}`` → mock invoked with haiku."""
    manifest = load_book_manifest(BOOK_DIR)
    invoked_models: list[str] = []
    dispatch = _make_dispatch(
        [_ch1_character_response(), _ch2_character_response()],
        invoked_models=invoked_models,
    )

    run_pre_pass_characters(
        book_manifest=manifest,
        intake_spec={
            **_INTAKE_SPEC,
            "model": {
                "default": "claude-opus-4-7",
                "extractor": "claude-haiku-4-5",
            },
        },
        output_path=tmp_path / "characters.json",
        dispatch_subagent=dispatch,
    )

    assert invoked_models, "dispatch was never invoked"
    assert all(m == "claude-haiku-4-5" for m in invoked_models), (
        f"extractor role should route to haiku, got {invoked_models}"
    )


# --------------------------------------------------------------------------- #
# 9. Glossary L1.5 tier resolves before L2                                     #
# --------------------------------------------------------------------------- #


def test_glossary_l1_5_tier_resolves(tmp_path):
    """Pre-pass JSON → glossary.lookup hits L1.5 before L2; audit_path = L1.5."""
    manifest = load_book_manifest(BOOK_DIR)
    dispatch_chars = _make_dispatch([
        _ch1_character_response(),
        _ch2_character_response(),
    ])
    chars_path = tmp_path / "characters.json"
    chars_artifact = run_pre_pass_characters(
        book_manifest=manifest,
        intake_spec=_INTAKE_SPEC,
        output_path=chars_path,
        dispatch_subagent=dispatch_chars,
    )

    dispatch_world = _make_dispatch([
        _ch1_world_glossary_response(),
        _ch2_world_glossary_response(),
    ])
    world_path = tmp_path / "world-glossary.json"
    world_artifact = run_pre_pass_world_glossary(
        book_manifest=manifest,
        intake_spec=_INTAKE_SPEC,
        output_path=world_path,
        dispatch_subagent=dispatch_world,
    )

    # Build the merged prepass_artifacts dict the glossary lookup expects.
    prepass = {
        "characters": chars_artifact["characters"],
        "world_glossary": {
            "places": world_artifact["places"],
            "organizations": world_artifact["organizations"],
            "world_terms": world_artifact["world_terms"],
            "cultural_references": world_artifact["cultural_references"],
        },
    }

    # Character canonical-name lookup → L1.5 hit on character class.
    hit_char = lookup(
        CANONICAL,
        "ja-JP",
        "en-US",
        "メロス",
        prepass_artifacts=prepass,
    )
    assert hit_char is not None, "expected L1.5 hit on character canonical_name"
    assert hit_char["target_term"] == "Melos"
    assert hit_char["audit_path"] == "L1.5.character", (
        f"expected audit_path 'L1.5.character', got {hit_char['audit_path']!r}"
    )

    # Place canonical_source lookup → L1.5 hit on world_glossary.places.
    hit_place = lookup(
        CANONICAL,
        "ja-JP",
        "en-US",
        "アクロポリス",
        prepass_artifacts=prepass,
    )
    assert hit_place is not None, (
        "expected L1.5 hit on world_glossary.places for アクロポリス"
    )
    assert hit_place["audit_path"] == "L1.5.world_glossary.places"
    assert hit_place["target_term"] == "the acropolis"


# --------------------------------------------------------------------------- #
# 10. Pre-pass cost-ceiling assertion (Decision E #2 — HARD-FAIL)              #
# --------------------------------------------------------------------------- #


# Cheap-model relative cost weight (Haiku-equivalent baseline = 1.0).
# Plan reference: §"Decision D — cheap-model split" + §"Decision E #2".
_CHEAP_MODEL_WEIGHT = 1.0
# Default-model relative cost weight. Set conservatively at 5× the cheap weight
# (Haiku 4.5 vs Sonnet 4-class roughly 1:5; vs Opus class even higher). The
# weight is a *relative* cost unit, not absolute pricing — the assertion is a
# token-volume × cost-class budget check, not a dollar-cost prediction. See
# the failure-message remediation hints for tuning guidance.
_DEFAULT_MODEL_WEIGHT = 5.0
# Decision E #2: pre-pass effective cost must be <= 50% of single-chapter
# scene-translation cost. HARD-FAIL bar — if this trips, the cheap-model split
# is not pulling its weight on this fixture and the user needs to tune the
# fixture, the prompt sizing, or the relative-cost weights.
_COST_CEILING = 0.5


def _build_prepass_total_tokens(manifest, intake_spec):
    """Sum EXTRACTOR-prompt tokens across both chapters × {character,
    world-glossary} extractors with realistic accumulated state.

    The accumulated state grows monotonically as chapters are processed;
    we simulate the worst-case (state at chapter N has all entries from
    chapters 0..N-1) by passing the canned ch1 responses' parsed shape as
    the ch2 accumulated seed. This mirrors what
    ``run_pre_pass_characters`` does internally during a real run.
    """
    # Chapter 0: empty seed.
    acc_chars: list[dict] = []
    acc_world = {
        "places": [],
        "organizations": [],
        "world_terms": [],
        "cultural_references": [],
    }
    total = 0
    for idx, chapter_path in enumerate(manifest.chapters):
        chapter_text = chapter_path.read_text(encoding="utf-8")
        prompt_char = build_character_extraction_prompt(
            chapter_text=chapter_text,
            chapter_index=idx,
            accumulated_characters=acc_chars,
            intake_spec=intake_spec,
        )
        prompt_world = build_world_glossary_extraction_prompt(
            chapter_text=chapter_text,
            chapter_index=idx,
            accumulated_world_glossary=acc_world,
            intake_spec=intake_spec,
        )
        total += approx_tokens(prompt_char) + approx_tokens(prompt_world)
        # Advance state with realistic seed-after-ch1 (only after first iter).
        if idx == 0:
            acc_chars = [
                {
                    "canonical_name": "メロス",
                    "canonical_target": "Melos",
                    "aliases": [
                        {"source": "メロス", "target": "Melos"},
                        {"source": "彼", "target": "he"},
                    ],
                    "voice_notes": "earnest, impulsive, friend-loyalty motif",
                    "first_seen_chapter": 0,
                    "last_seen_chapter": 0,
                },
                {
                    "canonical_name": "ディオニス",
                    "canonical_target": "Dionysius",
                    "aliases": [
                        {
                            "source": "暴君ディオニス",
                            "target": "the tyrant Dionysius",
                        },
                    ],
                    "voice_notes": "tyrannical, world-weary, paranoid",
                    "first_seen_chapter": 0,
                    "last_seen_chapter": 0,
                },
                {
                    "canonical_name": "セリヌンティウス",
                    "canonical_target": "Selinuntius",
                    "aliases": [],
                    "voice_notes": "loyal stonemason, silent presence",
                    "first_seen_chapter": 0,
                    "last_seen_chapter": 0,
                },
            ]
            acc_world = {
                "places": [
                    {
                        "canonical_source": "シラクス",
                        "canonical_target": "Syracuse",
                        "first_seen_chapter": 0,
                    }
                ],
                "organizations": [],
                "world_terms": [
                    {
                        "canonical_source": "王城",
                        "canonical_target": "the royal palace",
                        "notes": "ディオニス's residence; site of M's arrest",
                        "first_seen_chapter": 0,
                    }
                ],
                "cultural_references": [
                    {
                        "source_phrase": "十字架にかけられて",
                        "category": "religious_term",
                        "handling_hint": "explain",
                        "first_seen_chapter": 0,
                    }
                ],
            }
    return total


def _build_single_chapter_translation_tokens(chapter_path, intake_spec):
    """Sum DRAFT + REFLECT (5D-literary) + IMPROVE prompt tokens across all
    scenes of one chapter — matches what the per-scene core loop emits."""
    text = chapter_path.read_text(encoding="utf-8")
    scenes = chunk_chapter_into_scenes(text)
    total = 0
    for i, scene in enumerate(scenes):
        prev_v2 = scenes[i - 1].source_text if i > 0 else None
        next_src = scenes[i + 1].source_text if i + 1 < len(scenes) else None
        p_draft = build_scene_draft_prompt(
            scene=scene,
            prev_scene_v2=prev_v2,
            next_scene_source=next_src,
            intake_spec=intake_spec,
            glossary_hits=[],
        )
        p_reflect = build_scene_reflect_5d_literary_prompt(
            scene=scene,
            draft_v1=scene.source_text,
            intake_spec=intake_spec,
            glossary_hits=[],
            prev_scene_v2=prev_v2,
            next_scene_source=next_src,
        )
        p_improve = build_scene_improve_prompt(
            scene=scene,
            draft_v1=scene.source_text,
            critique_json={
                "accuracy": [],
                "fluency": [],
                "style": [],
                "terminology": [],
                "literariness": [],
            },
        )
        total += (
            approx_tokens(p_draft)
            + approx_tokens(p_reflect)
            + approx_tokens(p_improve)
        )
    return total


def test_prepass_cost_ceiling_assertion():
    """KEY ACCEPTANCE TEST per plan §"Decision E #2" — HARD-FAIL.

    Compute pre-pass effective cost (cheap-model weight × prepass tokens)
    and single-chapter scene-translation effective cost (default-model
    weight × translation tokens for chapter 1). Assert::

        prepass_effective / single_chapter_translation_effective <= 0.5

    Math-only — no LLM calls. The relative weights are *cost-class units*,
    not absolute USD per token: cheap=1.0 (Haiku-equivalent baseline),
    default=5.0 (conservative — actual Haiku-vs-Opus is closer to 1:15).
    The 5× weight is a deliberate floor: if the assertion holds at 1:5
    cost-class spread, it holds at any larger spread. Plan reference:
    §"Decision D — cheap-model split" notes "Haiku-equivalent (1×)"
    for the cheap class.

    Failure of this assertion signals:
        - prompt-template body has grown out of budget (audit
          ``canonical/prompts/extract-*.md``);
        - chapter-02 fixture is too short relative to chapter-01 — reduces
          the denominator below the design ratio (≥50% chapter-2 length);
        - cost-class weights may need recalibration if upstream pricing
          shifts (re-run with current pricing if Decision D is revisited);
        - real cheap-model split is not being exercised — caller passing
          single-string ``model`` form invalidates the cheap-model
          assumption underlying this assertion.
    """
    manifest = load_book_manifest(BOOK_DIR)
    prepass_tokens = _build_prepass_total_tokens(manifest, _INTAKE_SPEC)
    chapter_1_tokens = _build_single_chapter_translation_tokens(
        manifest.chapters[0], _INTAKE_SPEC
    )

    prepass_effective = prepass_tokens * _CHEAP_MODEL_WEIGHT
    chapter_effective = chapter_1_tokens * _DEFAULT_MODEL_WEIGHT
    assert chapter_effective > 0, "chapter translation tokens unexpectedly zero"

    ratio = prepass_effective / chapter_effective

    # Surface for ``pytest -s`` audit.
    print(
        f"\n  prepass tokens (sum, both chapters × {{char, world}}): {prepass_tokens}"
        f"\n  chapter-1 translation tokens (DRAFT+REFLECT_5D+IMPROVE): {chapter_1_tokens}"
        f"\n  cheap_model_weight: {_CHEAP_MODEL_WEIGHT}"
        f"\n  default_model_weight: {_DEFAULT_MODEL_WEIGHT}"
        f"\n  prepass_effective: {prepass_effective:.1f}"
        f"\n  chapter_effective: {chapter_effective:.1f}"
        f"\n  ratio (prepass / chapter): {ratio:.4f}"
        f"\n  ceiling: {_COST_CEILING}"
    )

    assert ratio <= _COST_CEILING, (
        "Pre-pass cost ceiling tripped (Decision E #2 — HARD-FAIL).\n"
        f"  ratio = {ratio:.4f} > {_COST_CEILING} ceiling.\n"
        f"  prepass tokens: {prepass_tokens} × cheap_weight {_CHEAP_MODEL_WEIGHT} "
        f"= {prepass_effective:.1f}\n"
        f"  chapter-1 translation tokens: {chapter_1_tokens} × default_weight "
        f"{_DEFAULT_MODEL_WEIGHT} = {chapter_effective:.1f}\n"
        "Remediation hints:\n"
        "  - Audit canonical/prompts/extract-{characters,world-glossary}.md "
        "for prompt-body bloat; trim non-essential examples / sub-instructions.\n"
        "  - Verify chapter-02 fixture is >= 50% of chapter-01 length (Phase F "
        "design guideline); if it has shrunk, prepass tokens are starving the "
        "denominator.\n"
        "  - Recalibrate _CHEAP_MODEL_WEIGHT / _DEFAULT_MODEL_WEIGHT against "
        "current Anthropic pricing; the 1:5 spread used here is a conservative "
        "floor, the production split (e.g. Haiku vs Opus ~ 1:15) is laxer.\n"
        "  - Verify real callers pass the dict-form `model` field — the cost "
        "ceiling assumes Decision D's cheap-model split is in effect."
    )
