"""Tests for scripts/lib/world_glossary_extractor.py — Phase D of v0.3.0 Tier 2.

Mirrors test_character_extractor.py but for the four-class world-glossary
schema (places / organizations / world_terms / cultural_references).
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.world_glossary_extractor import (  # noqa: E402
    BookManifest,
    build_world_glossary_extraction_prompt,
    load_book_manifest_for_world_glossary,
    parse_world_glossary_extraction_response,
    run_pre_pass_world_glossary,
)


# -------------------- helpers --------------------


def _write_chapter(book_dir: Path, name: str, body: str) -> Path:
    p = book_dir / name
    p.write_text(body, encoding="utf-8")
    return p


def _empty_world_glossary() -> dict[str, list[dict]]:
    return {
        "places": [],
        "organizations": [],
        "world_terms": [],
        "cultural_references": [],
    }


def _canned_response(body: dict) -> str:
    full = _empty_world_glossary()
    full.update(body)
    return json.dumps(full, ensure_ascii=False)


# -------------------- 1. manifest hash stability (re-uses BookManifest) --------------------


def test_world_glossary_manifest_hash_stable(tmp_path):
    _write_chapter(tmp_path, "chapter-01.md", "a\n")
    _write_chapter(tmp_path, "chapter-02.md", "b\n")
    h1 = load_book_manifest_for_world_glossary(tmp_path).manifest_hash
    h2 = load_book_manifest_for_world_glossary(tmp_path).manifest_hash
    assert h1 == h2

    (tmp_path / "chapter-01.md").write_text("A\n", encoding="utf-8")
    h3 = load_book_manifest_for_world_glossary(tmp_path).manifest_hash
    assert h1 != h3


def test_world_glossary_manifest_orders_chapters(tmp_path):
    _write_chapter(tmp_path, "chapter-03.md", "c\n")
    _write_chapter(tmp_path, "chapter-01.md", "a\n")
    _write_chapter(tmp_path, "chapter-02.md", "b\n")
    manifest = load_book_manifest_for_world_glossary(tmp_path)
    assert [p.name for p in manifest.chapters] == [
        "chapter-01.md", "chapter-02.md", "chapter-03.md",
    ]


# -------------------- 3. prompt includes accumulated --------------------


def test_build_world_glossary_prompt_includes_accumulated():
    accumulated = {
        "places": [
            {"canonical_source": "シラクサ",
             "canonical_target": "Syracuse",
             "first_seen_chapter": 0}
        ],
        "organizations": [],
        "world_terms": [],
        "cultural_references": [],
    }
    prompt = build_world_glossary_extraction_prompt(
        chapter_text="next chapter",
        chapter_index=1,
        accumulated_world_glossary=accumulated,
        intake_spec={},
    )
    assert "シラクサ" in prompt
    assert "Syracuse" in prompt
    assert "Accumulated world-glossary from prior chapters" in prompt


# -------------------- 4. prompt includes schema (all 4 classes) --------------------


def test_build_world_glossary_prompt_includes_schema():
    prompt = build_world_glossary_extraction_prompt(
        chapter_text="X",
        chapter_index=0,
        accumulated_world_glossary=_empty_world_glossary(),
        intake_spec={},
    )
    # All four classes must appear in the schema body.
    for cls in ("places", "organizations", "world_terms",
                 "cultural_references"):
        assert cls in prompt, f"missing class in schema: {cls}"
    # Closed enum hints.
    assert "literary_quotation" in prompt
    assert "borrow" in prompt
    assert "explain" in prompt
    assert "approximate" in prompt


# -------------------- 5. parser round-trip (incl. closed-enum check) --------------------


def test_parse_world_glossary_response_round_trips():
    payload = {
        "places": [
            {"canonical_source": "シラクサ",
             "canonical_target": "Syracuse",
             "first_seen_chapter": 1}
        ],
        "organizations": [],
        "world_terms": [
            {"canonical_source": "暴君",
             "canonical_target": "tyrant",
             "notes": "context-dependent — could be 'despot'",
             "first_seen_chapter": 1}
        ],
        "cultural_references": [
            {
                "source_phrase": "信実とは決して空虚な妄想ではなかった",
                "category": "literary_quotation",
                "handling_hint": "borrow",
                "first_seen_chapter": 1,
            }
        ],
    }
    parsed = parse_world_glossary_extraction_response(
        json.dumps(payload, ensure_ascii=False)
    )
    assert parsed["places"][0]["canonical_source"] == "シラクサ"
    assert parsed["world_terms"][0]["canonical_target"] == "tyrant"
    assert parsed["cultural_references"][0]["category"] == "literary_quotation"
    assert parsed["cultural_references"][0]["handling_hint"] == "borrow"


# -------------------- 6. write artifact --------------------


def test_run_pre_pass_writes_world_glossary_artifact(tmp_path):
    _write_chapter(tmp_path, "chapter-01.md", "ch1\n")
    manifest = load_book_manifest_for_world_glossary(tmp_path)

    response = _canned_response({
        "places": [
            {"canonical_source": "シラクサ",
             "canonical_target": "Syracuse",
             "first_seen_chapter": 0}
        ]
    })

    def mock_dispatch(*, prompt, model):
        return response

    output_path = tmp_path / "out" / "world-glossary.json"
    artifact = run_pre_pass_world_glossary(
        book_manifest=manifest,
        intake_spec={},
        output_path=output_path,
        dispatch_subagent=mock_dispatch,
    )

    assert output_path.exists()
    on_disk = json.loads(output_path.read_text(encoding="utf-8"))
    for required in ("schema_version", "book_manifest_hash",
                     "extracted_at", "extractor_model",
                     "places", "organizations",
                     "world_terms", "cultural_references"):
        assert required in on_disk, f"missing {required}"
    assert on_disk["schema_version"] == "0.3.0"
    assert on_disk["places"][0]["canonical_source"] == "シラクサ"
    assert artifact["places"] == on_disk["places"]


# -------------------- 7. cross-chapter merge --------------------


def test_run_pre_pass_merges_world_glossary_across_chapters(tmp_path):
    _write_chapter(tmp_path, "chapter-01.md", "ch1\n")
    _write_chapter(tmp_path, "chapter-02.md", "ch2\n")
    manifest = load_book_manifest_for_world_glossary(tmp_path)

    ch1_resp = _canned_response({
        "places": [
            {"canonical_source": "シラクサ",
             "canonical_target": "Syracuse",
             "first_seen_chapter": 0}
        ],
        "world_terms": [
            {"canonical_source": "暴君",
             "canonical_target": "tyrant",
             "notes": "neutral",
             "first_seen_chapter": 0}
        ],
    })
    # Ch2: re-introduces same place (must NOT dup); refines world_term notes;
    # adds new cultural_reference.
    ch2_resp = _canned_response({
        "places": [
            {"canonical_source": "シラクサ",
             "canonical_target": "Syracuse",
             "first_seen_chapter": 1}
        ],
        "world_terms": [
            {"canonical_source": "暴君",
             "canonical_target": "tyrant",
             "notes": "context-dependent — could be 'despot'",
             "first_seen_chapter": 1}
        ],
        "cultural_references": [
            {"source_phrase": "信実とは決して空虚な妄想ではなかった",
             "category": "literary_quotation",
             "handling_hint": "borrow",
             "first_seen_chapter": 1}
        ],
    })
    responses = [ch1_resp, ch2_resp]

    def mock_dispatch(*, prompt, model):
        return responses.pop(0)

    output_path = tmp_path / "world-glossary.json"
    artifact = run_pre_pass_world_glossary(
        book_manifest=manifest,
        intake_spec={},
        output_path=output_path,
        dispatch_subagent=mock_dispatch,
    )

    # places: append-only / dedup → exactly 1 entry.
    assert len(artifact["places"]) == 1
    # world_terms: notes refined.
    assert "despot" in artifact["world_terms"][0]["notes"]
    # cultural_references: introduced in ch2.
    assert len(artifact["cultural_references"]) == 1
    assert (
        artifact["cultural_references"][0]["category"]
        == "literary_quotation"
    )


# -------------------- 8. extractor model routing --------------------


def test_run_pre_pass_world_glossary_uses_extractor_model(tmp_path):
    _write_chapter(tmp_path, "chapter-01.md", "ch1\n")
    manifest = load_book_manifest_for_world_glossary(tmp_path)
    invoked_models: list[str] = []

    def mock_dispatch(*, prompt, model):
        invoked_models.append(model)
        return _canned_response({})

    run_pre_pass_world_glossary(
        book_manifest=manifest,
        intake_spec={
            "model": {
                "default": "claude-opus-4-7",
                "extractor": "claude-haiku-4-5",
            }
        },
        output_path=tmp_path / "world-glossary.json",
        dispatch_subagent=mock_dispatch,
    )
    assert invoked_models == ["claude-haiku-4-5"]


# -------------------- 9. unknown category rejected --------------------


def test_parse_world_glossary_rejects_unknown_category():
    payload = {
        "places": [],
        "organizations": [],
        "world_terms": [],
        "cultural_references": [
            {"source_phrase": "X",
             "category": "made_up",
             "handling_hint": "borrow",
             "first_seen_chapter": 0}
        ],
    }
    with pytest.raises(ValueError, match="category"):
        parse_world_glossary_extraction_response(
            json.dumps(payload, ensure_ascii=False)
        )


def test_parse_world_glossary_rejects_unknown_handling_hint():
    payload = {
        "cultural_references": [
            {"source_phrase": "X",
             "category": "idiom",
             "handling_hint": "rewrite_aggressively",
             "first_seen_chapter": 0}
        ],
    }
    with pytest.raises(ValueError, match="handling_hint"):
        parse_world_glossary_extraction_response(
            json.dumps(payload, ensure_ascii=False)
        )


# -------------------- 10. stale cache warning --------------------


def test_run_pre_pass_world_glossary_stale_cache_warns(tmp_path):
    _write_chapter(tmp_path, "chapter-01.md", "v1\n")
    manifest_v1 = load_book_manifest_for_world_glossary(tmp_path)
    output_path = tmp_path / "world-glossary.json"

    def mock_dispatch(*, prompt, model):
        return _canned_response({})

    run_pre_pass_world_glossary(
        book_manifest=manifest_v1,
        intake_spec={},
        output_path=output_path,
        dispatch_subagent=mock_dispatch,
    )

    (tmp_path / "chapter-01.md").write_text("v2\n", encoding="utf-8")
    manifest_v2 = load_book_manifest_for_world_glossary(tmp_path)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        run_pre_pass_world_glossary(
            book_manifest=manifest_v2,
            intake_spec={},
            output_path=output_path,
            dispatch_subagent=mock_dispatch,
        )
    stale = [w for w in caught if "stale" in str(w.message).lower()]
    assert stale, (
        f"expected stale-cache warning, got: "
        f"{[str(w.message) for w in caught]}"
    )
