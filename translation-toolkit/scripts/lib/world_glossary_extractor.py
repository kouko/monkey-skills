"""Whole-book world-glossary pre-pass extractor (Phase D of v0.3.0 Tier 2).

Plan reference: ``docs/superpowers/plans/2026-05-07-translation-toolkit-v0.3.0-tier2.md``
§"Decision G — Pre-pass artifact schemas (characters + world-glossary)".

Companion to :mod:`character_extractor`. Walks every chapter of a book in
order and produces a ``world-glossary.json`` artifact partitioning entries
into four classes:

- ``places`` — named geographic locations.
- ``organizations`` — named groups (governments, factions, guilds, etc.).
- ``world_terms`` — domain / world-specific vocabulary that is NOT a proper
  noun (concepts, ranks, period objects); each carries a free-form ``notes``
  field for register / context.
- ``cultural_references`` — literary quotations, idioms, religious / food /
  historical references; each carries a closed-enum ``category`` (validated
  on parse) plus a ``handling_hint`` (``borrow`` / ``explain`` /
  ``approximate``).

The artifact is consumed at runtime by ``glossary.lookup`` as the **L1.5**
tier alongside the character profiles. Together they form the book-specific
canonical layer that overrides L2 (bundled-pair generic glossary) and L3
(web search) for the duration of one book's translation.

This module deliberately mirrors :mod:`character_extractor`'s API shape so
callers can swap between them without learning a second dispatch protocol.
The two extractors live in separate files because their PROMPTS diverge
(voice notes vs four-class type tagging) — keeping them flat per-extractor
keeps the prompt + schema-validation logic readable.

Public API:

- :func:`load_book_manifest_for_world_glossary` — convenience re-export of
  :func:`character_extractor.load_book_manifest`. Same manifest format.
- :func:`build_world_glossary_extraction_prompt` — render the EXTRACTOR
  prompt.
- :func:`parse_world_glossary_extraction_response` — parse the JSON
  response, including closed-enum validation for
  ``cultural_references[].category``.
- :func:`run_pre_pass_world_glossary` — orchestrate whole-book extraction.

This module lives at plugin-level ``translation-toolkit/scripts/lib/`` and
is independent of any skill folder.
"""
from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from lib.character_extractor import (
    BookManifest,
    _check_stale_cache,
    _extract_json_object,
    _format_intake_spec_compact,
    load_book_manifest,
)
from lib.model_routing import resolve_model_for_role
from lib.novel_prompts import _load_canonical_prompt

__all__ = [
    "BookManifest",
    "load_book_manifest_for_world_glossary",
    "build_world_glossary_extraction_prompt",
    "parse_world_glossary_extraction_response",
    "run_pre_pass_world_glossary",
    "CULTURAL_REFERENCE_CATEGORIES",
    "HANDLING_HINTS",
]


SCHEMA_VERSION = "0.3.0"

# Closed enums from Decision G. Validators reject any value not in these sets.
CULTURAL_REFERENCE_CATEGORIES: frozenset[str] = frozenset({
    "literary_quotation",
    "idiom",
    "religious_term",
    "food_term",
    "place_culture",
    "historical_reference",
    "other",
})

HANDLING_HINTS: frozenset[str] = frozenset({
    "borrow",
    "explain",
    "approximate",
})

# Re-export under the world-glossary name so callers don't have to import
# from character_extractor for this convenience.
load_book_manifest_for_world_glossary = load_book_manifest


def _empty_world_glossary() -> dict[str, list[dict]]:
    return {
        "places": [],
        "organizations": [],
        "world_terms": [],
        "cultural_references": [],
    }


def build_world_glossary_extraction_prompt(
    *,
    chapter_text: str,
    chapter_index: int,
    accumulated_world_glossary: dict[str, list[dict]],
    intake_spec: dict,
) -> str:
    """Render the canonical ``prompts/extract-world-glossary.md`` template
    body plus the per-chapter substitution block.

    Layout (after the canonical prompt body):

        # Translation parameters     -- intake spec
        # Accumulated world-glossary -- JSON dict from prior chapters
        # Current chapter (index N)
        <CHAPTER>
        ...chapter_text...
        </CHAPTER>
    """
    template_body = _load_canonical_prompt("extract-world-glossary.md")
    accumulated_json = json.dumps(
        accumulated_world_glossary, ensure_ascii=False, indent=2
    )
    return (
        f"{template_body}\n"
        "\n"
        "# Translation parameters\n"
        f"{_format_intake_spec_compact(intake_spec)}\n"
        "\n"
        "# Accumulated world-glossary from prior chapters (extend / refine — do NOT discard)\n"
        f"{accumulated_json}\n"
        "\n"
        f"# Current chapter (index {chapter_index})\n"
        "<CHAPTER>\n"
        f"{chapter_text}\n"
        "</CHAPTER>"
    )


def _validate_place_or_org_entry(entry: dict, class_name: str) -> dict:
    if not isinstance(entry, dict):
        raise ValueError(
            f"{class_name} entry must be a dict, got {type(entry).__name__}"
        )
    for key in ("canonical_source", "first_seen_chapter"):
        if key not in entry:
            raise ValueError(
                f"{class_name} entry missing required key {key!r}: {entry!r}"
            )
    if not entry["canonical_source"]:
        raise ValueError(
            f"{class_name} entry has empty canonical_source: {entry!r}"
        )
    return {
        "canonical_source": entry["canonical_source"],
        "canonical_target": entry.get("canonical_target", None),
        "first_seen_chapter": entry["first_seen_chapter"],
    }


def _validate_world_term_entry(entry: dict) -> dict:
    if not isinstance(entry, dict):
        raise ValueError(
            f"world_terms entry must be a dict, got {type(entry).__name__}"
        )
    for key in ("canonical_source", "first_seen_chapter"):
        if key not in entry:
            raise ValueError(
                f"world_terms entry missing required key {key!r}: {entry!r}"
            )
    if not entry["canonical_source"]:
        raise ValueError(
            f"world_terms entry has empty canonical_source: {entry!r}"
        )
    return {
        "canonical_source": entry["canonical_source"],
        "canonical_target": entry.get("canonical_target", None),
        "notes": entry.get("notes", "") or "",
        "first_seen_chapter": entry["first_seen_chapter"],
    }


def _validate_cultural_reference_entry(entry: dict) -> dict:
    if not isinstance(entry, dict):
        raise ValueError(
            f"cultural_references entry must be a dict, got "
            f"{type(entry).__name__}"
        )
    for key in ("source_phrase", "category", "first_seen_chapter"):
        if key not in entry:
            raise ValueError(
                f"cultural_references entry missing required key {key!r}: "
                f"{entry!r}"
            )
    category = entry["category"]
    if category not in CULTURAL_REFERENCE_CATEGORIES:
        raise ValueError(
            f"cultural_references[].category must be one of "
            f"{sorted(CULTURAL_REFERENCE_CATEGORIES)}, got {category!r}"
        )
    handling_hint = entry.get("handling_hint")
    if handling_hint is not None and handling_hint not in HANDLING_HINTS:
        raise ValueError(
            f"cultural_references[].handling_hint must be one of "
            f"{sorted(HANDLING_HINTS)} (or null), got {handling_hint!r}"
        )
    return {
        "source_phrase": entry["source_phrase"],
        "category": category,
        "handling_hint": handling_hint,
        "first_seen_chapter": entry["first_seen_chapter"],
    }


def parse_world_glossary_extraction_response(
    response: str,
) -> dict[str, list[dict]]:
    """Parse the EXTRACTOR JSON response into a four-class dict.

    Validates per Decision G:

    - Top-level shape: ``{"places": [...], "organizations": [...],
      "world_terms": [...], "cultural_references": [...]}``. Missing classes
      default to empty lists.
    - Each entry has its required keys (per class).
    - ``cultural_references[].category`` MUST be in
      :data:`CULTURAL_REFERENCE_CATEGORIES` — unknown categories raise
      :class:`ValueError`.
    - ``cultural_references[].handling_hint`` MUST be in
      :data:`HANDLING_HINTS` if provided.

    Tolerates models that omit optional ``canonical_target`` or ``notes``
    keys by inserting empty defaults; rejects entries missing required keys.
    """
    data = _extract_json_object(response)
    out = _empty_world_glossary()

    for class_name in ("places", "organizations"):
        raw_list = data.get(class_name, [])
        if not isinstance(raw_list, list):
            raise ValueError(
                f"world_glossary {class_name!r} must be a list"
            )
        for entry in raw_list:
            out[class_name].append(
                _validate_place_or_org_entry(entry, class_name)
            )

    raw_terms = data.get("world_terms", [])
    if not isinstance(raw_terms, list):
        raise ValueError("world_glossary 'world_terms' must be a list")
    for entry in raw_terms:
        out["world_terms"].append(_validate_world_term_entry(entry))

    raw_refs = data.get("cultural_references", [])
    if not isinstance(raw_refs, list):
        raise ValueError(
            "world_glossary 'cultural_references' must be a list"
        )
    for entry in raw_refs:
        out["cultural_references"].append(
            _validate_cultural_reference_entry(entry)
        )

    return out


def _merge_world_glossary(
    accumulated: dict[str, list[dict]], incoming: dict[str, list[dict]]
) -> dict[str, list[dict]]:
    """Merge incoming world-glossary entries into accumulated state.

    Merge rules (per Decision G):

    - ``places`` / ``organizations`` / ``cultural_references``: append-only,
      de-duped on ``canonical_source`` (places/orgs) or ``source_phrase``
      (cultural_references). First occurrence wins.
    - ``world_terms``: dedup on ``canonical_source``; if matched, REFINE
      ``notes`` by replacing if incoming non-empty (mirrors character voice_notes
      refinement).
    """
    out = {k: list(v) for k, v in accumulated.items()}

    for class_name in ("places", "organizations"):
        existing_keys = {e["canonical_source"] for e in out[class_name]}
        for entry in incoming.get(class_name, []):
            if entry["canonical_source"] not in existing_keys:
                out[class_name].append(entry)
                existing_keys.add(entry["canonical_source"])

    by_term: dict[str, dict] = {
        e["canonical_source"]: e for e in out["world_terms"]
    }
    for entry in incoming.get("world_terms", []):
        key = entry["canonical_source"]
        if key not in by_term:
            out["world_terms"].append(entry)
            by_term[key] = out["world_terms"][-1]
            continue
        existing = by_term[key]
        if entry.get("notes"):
            existing["notes"] = entry["notes"]
        if (
            existing.get("canonical_target") is None
            and entry.get("canonical_target") is not None
        ):
            existing["canonical_target"] = entry["canonical_target"]

    existing_phrases = {
        e["source_phrase"] for e in out["cultural_references"]
    }
    for entry in incoming.get("cultural_references", []):
        if entry["source_phrase"] not in existing_phrases:
            out["cultural_references"].append(entry)
            existing_phrases.add(entry["source_phrase"])

    return out


def run_pre_pass_world_glossary(
    *,
    book_manifest: BookManifest,
    intake_spec: dict,
    output_path: Path,
    dispatch_subagent: Callable[..., str],
) -> dict:
    """Orchestrate whole-book world-glossary extraction.

    Mirrors :func:`character_extractor.run_pre_pass_characters`. For each
    chapter (in order) build prompt with accumulated four-class state,
    dispatch EXTRACTOR subagent at the resolved model, parse + merge
    response. After all chapters: write JSON artifact with
    ``schema_version`` / ``book_manifest_hash`` / ``extracted_at`` /
    ``extractor_model`` / four-class contents.

    ``dispatch_subagent`` signature: ``(prompt: str, model: str) -> str``.
    """
    output_path = Path(output_path)
    _check_stale_cache(output_path, book_manifest.manifest_hash)

    model_field = intake_spec.get("model", "claude-opus-4-7")
    extractor_model = resolve_model_for_role(model_field, "extractor")

    accumulated = _empty_world_glossary()
    for idx, chapter_path in enumerate(book_manifest.chapters):
        chapter_text = chapter_path.read_text(encoding="utf-8")
        prompt = build_world_glossary_extraction_prompt(
            chapter_text=chapter_text,
            chapter_index=idx,
            accumulated_world_glossary=accumulated,
            intake_spec=intake_spec,
        )
        response = dispatch_subagent(prompt=prompt, model=extractor_model)
        incoming = parse_world_glossary_extraction_response(response)
        accumulated = _merge_world_glossary(accumulated, incoming)

    artifact: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "book_manifest_hash": book_manifest.manifest_hash,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "extractor_model": extractor_model,
        **accumulated,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return artifact
