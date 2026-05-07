"""Tests for scripts/lib/character_extractor.py — Phase D of v0.3.0 Tier 2.

Covers (per plan ``docs/superpowers/plans/2026-05-07-translation-toolkit-v0.3.0-tier2.md``
§"Tests — character_extractor.py (9 tests)"):

  1. test_book_manifest_hash_stable
  2. test_book_manifest_orders_chapters
  3. test_build_character_prompt_includes_accumulated
  4. test_build_character_prompt_includes_schema
  5. test_parse_character_response_round_trips
  6. test_run_pre_pass_writes_artifact
  7. test_run_pre_pass_merges_across_chapters
  8. test_run_pre_pass_uses_extractor_model
  9. test_run_pre_pass_stale_cache_warns
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

from lib.character_extractor import (  # noqa: E402
    BookManifest,
    build_character_extraction_prompt,
    load_book_manifest,
    parse_character_extraction_response,
    run_pre_pass_characters,
)


# -------------------- helpers --------------------


def _write_chapter(book_dir: Path, name: str, body: str) -> Path:
    p = book_dir / name
    p.write_text(body, encoding="utf-8")
    return p


def _canned_response(characters: list[dict]) -> str:
    return json.dumps({"characters": characters}, ensure_ascii=False)


# -------------------- 1. manifest hash stability --------------------


def test_book_manifest_hash_stable(tmp_path):
    """Same dir → same hash; mutating a file → different hash."""
    _write_chapter(tmp_path, "chapter-01.md", "hello\n")
    _write_chapter(tmp_path, "chapter-02.md", "world\n")
    h1 = load_book_manifest(tmp_path).manifest_hash

    # Re-load → identical hash.
    h2 = load_book_manifest(tmp_path).manifest_hash
    assert h1 == h2

    # Mutate one file → different hash.
    (tmp_path / "chapter-02.md").write_text("WORLD\n", encoding="utf-8")
    h3 = load_book_manifest(tmp_path).manifest_hash
    assert h1 != h3


# -------------------- 2. chapter ordering --------------------


def test_book_manifest_orders_chapters(tmp_path):
    """Files must be ordered by name (ASCII sort)."""
    # Write deliberately out-of-natural-order names.
    _write_chapter(tmp_path, "chapter-03.md", "c\n")
    _write_chapter(tmp_path, "chapter-01.md", "a\n")
    _write_chapter(tmp_path, "chapter-02.md", "b\n")

    manifest = load_book_manifest(tmp_path)
    assert [p.name for p in manifest.chapters] == [
        "chapter-01.md", "chapter-02.md", "chapter-03.md",
    ]


def test_book_manifest_raises_on_empty_dir(tmp_path):
    with pytest.raises(ValueError, match="no \\*\\.md chapter files"):
        load_book_manifest(tmp_path)


# -------------------- 3. prompt includes accumulated --------------------


def test_build_character_prompt_includes_accumulated():
    accumulated = [
        {
            "canonical_name": "メロス",
            "canonical_target": "Melos",
            "aliases": [{"source": "彼", "target": "he"}],
            "voice_notes": "earnest, impulsive",
            "first_seen_chapter": 0,
            "last_seen_chapter": 0,
        }
    ]
    prompt = build_character_extraction_prompt(
        chapter_text="A new chapter.",
        chapter_index=1,
        accumulated_characters=accumulated,
        intake_spec={"source_locale": "ja-JP", "target_locale": "en-US"},
    )
    # Accumulated state shows up in the prompt as JSON.
    assert "メロス" in prompt
    assert "earnest, impulsive" in prompt
    assert "Melos" in prompt
    # Header for accumulated section.
    assert "Accumulated characters from prior chapters" in prompt


# -------------------- 4. prompt includes schema --------------------


def test_build_character_prompt_includes_schema():
    """The canonical schema body — including paired aliases + voice_notes —
    must be in the rendered prompt body."""
    prompt = build_character_extraction_prompt(
        chapter_text="X",
        chapter_index=0,
        accumulated_characters=[],
        intake_spec={},
    )
    assert "canonical_name" in prompt
    assert "canonical_target" in prompt
    assert "aliases" in prompt
    assert "voice_notes" in prompt
    assert "first_seen_chapter" in prompt
    assert "last_seen_chapter" in prompt
    # Paired-structure alias example.
    assert '"source"' in prompt
    assert '"target"' in prompt


# -------------------- 5. response parser round-trip --------------------


def test_parse_character_response_round_trips():
    payload = {
        "characters": [
            {
                "canonical_name": "メロス",
                "canonical_target": "Melos",
                "aliases": [
                    {"source": "メロス", "target": "Melos"},
                    {"source": "彼", "target": "he"},
                    {"source": "妹の婿", "target": None},
                ],
                "voice_notes": "earnest, impulsive, friend-loyalty motif",
                "first_seen_chapter": 1,
                "last_seen_chapter": 1,
            }
        ]
    }
    parsed = parse_character_extraction_response(
        json.dumps(payload, ensure_ascii=False)
    )
    assert len(parsed) == 1
    entry = parsed[0]
    assert entry["canonical_name"] == "メロス"
    assert entry["canonical_target"] == "Melos"
    assert len(entry["aliases"]) == 3
    assert entry["aliases"][0] == {"source": "メロス", "target": "Melos"}
    assert entry["aliases"][2] == {"source": "妹の婿", "target": None}
    assert entry["voice_notes"].startswith("earnest")
    assert entry["first_seen_chapter"] == 1


def test_parse_character_response_handles_fenced_code_block():
    """Models sometimes wrap JSON in a ```json fence. Parser must tolerate it."""
    payload = {"characters": []}
    fenced = f"```json\n{json.dumps(payload)}\n```"
    parsed = parse_character_extraction_response(fenced)
    assert parsed == []


def test_parse_character_response_rejects_missing_required_keys():
    bad = {"characters": [{"canonical_name": "X"}]}  # missing voice_notes etc.
    with pytest.raises(ValueError, match="missing required key"):
        parse_character_extraction_response(json.dumps(bad))


# -------------------- 6. write artifact --------------------


def test_run_pre_pass_writes_artifact(tmp_path):
    _write_chapter(tmp_path, "chapter-01.md", "Chapter one body.\n")
    _write_chapter(tmp_path, "chapter-02.md", "Chapter two body.\n")
    manifest = load_book_manifest(tmp_path)

    canned_responses = [
        _canned_response([
            {
                "canonical_name": "Alice",
                "canonical_target": "アリス",
                "aliases": [{"source": "Alice", "target": "アリス"}],
                "voice_notes": "polite, formal",
                "first_seen_chapter": 0,
                "last_seen_chapter": 0,
            }
        ]),
        _canned_response([]),  # ch2 yields no new characters
    ]
    call_log: list[tuple[str, str]] = []

    def mock_dispatch(*, prompt: str, model: str) -> str:
        call_log.append((prompt, model))
        return canned_responses[len(call_log) - 1]

    output_path = tmp_path / "out" / "characters.json"
    artifact = run_pre_pass_characters(
        book_manifest=manifest,
        intake_spec={"source_locale": "en-US", "target_locale": "ja-JP"},
        output_path=output_path,
        dispatch_subagent=mock_dispatch,
    )

    assert output_path.exists()
    on_disk = json.loads(output_path.read_text(encoding="utf-8"))

    for required in ("schema_version", "book_manifest_hash",
                      "extracted_at", "extractor_model", "characters"):
        assert required in on_disk, f"missing {required}"
    assert on_disk["schema_version"] == "0.3.0"
    assert on_disk["book_manifest_hash"] == manifest.manifest_hash
    assert on_disk["characters"][0]["canonical_name"] == "Alice"
    # Returned dict matches on-disk content.
    assert artifact["characters"] == on_disk["characters"]


# -------------------- 7. cross-chapter merge --------------------


def test_run_pre_pass_merges_across_chapters(tmp_path):
    _write_chapter(tmp_path, "chapter-01.md", "ch1\n")
    _write_chapter(tmp_path, "chapter-02.md", "ch2\n")
    manifest = load_book_manifest(tmp_path)

    # Chapter 1: char A introduced.
    ch1_resp = _canned_response([
        {
            "canonical_name": "メロス",
            "canonical_target": "Melos",
            "aliases": [{"source": "メロス", "target": "Melos"}],
            "voice_notes": "earnest",
            "first_seen_chapter": 0,
            "last_seen_chapter": 0,
        }
    ])
    # Chapter 2: char A refined (new alias + new voice_notes); char B added.
    ch2_resp = _canned_response([
        {
            "canonical_name": "メロス",
            "canonical_target": "Melos",
            "aliases": [
                {"source": "彼", "target": "he"},
            ],
            "voice_notes": "earnest, impulsive, friend-loyalty motif",
            "first_seen_chapter": 0,
            "last_seen_chapter": 1,
        },
        {
            "canonical_name": "セリヌンティウス",
            "canonical_target": "Selinuntius",
            "aliases": [],
            "voice_notes": "loyal, silent",
            "first_seen_chapter": 1,
            "last_seen_chapter": 1,
        },
    ])
    responses = [ch1_resp, ch2_resp]

    def mock_dispatch(*, prompt, model):
        return responses.pop(0)

    output_path = tmp_path / "characters.json"
    artifact = run_pre_pass_characters(
        book_manifest=manifest,
        intake_spec={},
        output_path=output_path,
        dispatch_subagent=mock_dispatch,
    )

    assert len(artifact["characters"]) == 2
    melos = next(c for c in artifact["characters"]
                 if c["canonical_name"] == "メロス")
    # Merged aliases: original + new.
    assert {a["source"] for a in melos["aliases"]} == {"メロス", "彼"}
    # Voice notes refined.
    assert "impulsive" in melos["voice_notes"]
    # last_seen_chapter advanced.
    assert melos["last_seen_chapter"] == 1
    # first_seen_chapter preserved (earliest wins).
    assert melos["first_seen_chapter"] == 0
    # Second character present.
    assert any(
        c["canonical_name"] == "セリヌンティウス"
        for c in artifact["characters"]
    )


# -------------------- 8. extractor model routing --------------------


def test_run_pre_pass_uses_extractor_model(tmp_path):
    """``model: {default: opus, extractor: haiku}`` → mock invoked with haiku."""
    _write_chapter(tmp_path, "chapter-01.md", "ch1\n")
    manifest = load_book_manifest(tmp_path)

    invoked_models: list[str] = []

    def mock_dispatch(*, prompt, model):
        invoked_models.append(model)
        return _canned_response([])

    run_pre_pass_characters(
        book_manifest=manifest,
        intake_spec={
            "model": {
                "default": "claude-opus-4-7",
                "extractor": "claude-haiku-4-5",
            }
        },
        output_path=tmp_path / "characters.json",
        dispatch_subagent=mock_dispatch,
    )
    assert invoked_models == ["claude-haiku-4-5"]


def test_run_pre_pass_uses_default_model_when_no_extractor_override(tmp_path):
    _write_chapter(tmp_path, "chapter-01.md", "x\n")
    manifest = load_book_manifest(tmp_path)
    invoked_models: list[str] = []

    def mock_dispatch(*, prompt, model):
        invoked_models.append(model)
        return _canned_response([])

    run_pre_pass_characters(
        book_manifest=manifest,
        intake_spec={"model": "claude-opus-4-7"},
        output_path=tmp_path / "characters.json",
        dispatch_subagent=mock_dispatch,
    )
    assert invoked_models == ["claude-opus-4-7"]


# -------------------- 9. stale cache warning --------------------


def test_run_pre_pass_stale_cache_warns(tmp_path):
    """Existing artifact whose stamped hash mismatches → UserWarning."""
    _write_chapter(tmp_path, "chapter-01.md", "v1\n")
    manifest_v1 = load_book_manifest(tmp_path)

    output_path = tmp_path / "characters.json"

    def mock_dispatch(*, prompt, model):
        return _canned_response([])

    # First run — writes a clean artifact.
    run_pre_pass_characters(
        book_manifest=manifest_v1,
        intake_spec={},
        output_path=output_path,
        dispatch_subagent=mock_dispatch,
    )
    assert output_path.exists()

    # Mutate the chapter so the manifest hash will differ.
    (tmp_path / "chapter-01.md").write_text("v2\n", encoding="utf-8")
    manifest_v2 = load_book_manifest(tmp_path)
    assert manifest_v1.manifest_hash != manifest_v2.manifest_hash

    # Second run with stale artifact on disk → expect UserWarning.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        run_pre_pass_characters(
            book_manifest=manifest_v2,
            intake_spec={},
            output_path=output_path,
            dispatch_subagent=mock_dispatch,
        )
    stale_warnings = [
        w for w in caught
        if "stale" in str(w.message).lower()
        or "manifest_hash" in str(w.message)
    ]
    assert stale_warnings, (
        f"expected stale-cache UserWarning, got: {[str(w.message) for w in caught]}"
    )
