"""Whole-book character pre-pass extractor (Phase D of v0.3.0 Tier 2).

Plan reference: ``docs/superpowers/plans/2026-05-07-translation-toolkit-v0.3.0-tier2.md``
§"Decision G — Pre-pass artifact schemas (characters + world-glossary)".

The pre-pass walks every chapter of a book in order and produces a single
``characters.json`` artifact recording every named character together with
aliases, voice notes, and first/last chapter indices. The artifact lives at
chapter-set level (not scene-level) and is consumed at runtime by
``glossary.lookup`` as the **L1.5** tier — sitting between L1 (project
glossary) and L2 (bundled-pair glossary) in the resolution order.

Why a separate file from ``world_glossary_extractor`` even though they share
shape? Their **prompts diverge**: character extraction needs voice notes and
paired-structure aliases (each alias has its own target rendering); world
glossary entries need place/organization/term/cultural-reference type tagging
plus a closed-enum ``handling_hint``. Keeping them in separate files keeps
the prompts and the schema-validation logic readable.

Public API:

- :class:`BookManifest` — chapter ordering + manifest hash dataclass
  (also re-exported via :mod:`world_glossary_extractor` for shared use).
- :func:`load_book_manifest` — walk a directory of chapter ``.md`` files.
- :func:`build_character_extraction_prompt` — render the EXTRACTOR prompt.
- :func:`parse_character_extraction_response` — parse the JSON response.
- :func:`run_pre_pass_characters` — orchestrate whole-book extraction with
  per-chapter accumulated state.

Design notes
------------
The actual subagent-dispatch happens at the SKILL.md / Claude Code Agent-tool
layer; this module accepts a ``dispatch_subagent`` callable so unit tests can
inject a mock without touching the network. The callable signature is
``(prompt: str, model: str) -> str`` — input is the rendered prompt and the
model identifier to invoke; output is the raw response text (which we then
parse via :func:`parse_character_extraction_response`).

Stale-cache contract: at the start of :func:`run_pre_pass_characters`, if
``output_path`` exists and its ``book_manifest_hash`` does NOT match the
freshly-computed hash, we emit a :class:`UserWarning` via :mod:`warnings`
and proceed to re-run the extraction (overwriting the artifact). We do not
auto-re-run silently; the warning is the signal so the caller (or the test)
can decide what to do with it.

This module lives at plugin-level ``translation-toolkit/scripts/lib/`` and
is independent of any skill folder.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from lib._pre_pass_helpers import (
    _check_stale_cache,
    _extract_json_object,
    _format_intake_spec_compact,
)
from lib.model_routing import resolve_model_for_role
from lib.novel_prompts import _load_canonical_prompt

__all__ = [
    "BookManifest",
    "load_book_manifest",
    "build_character_extraction_prompt",
    "parse_character_extraction_response",
    "run_pre_pass_characters",
]


SCHEMA_VERSION = "0.3.0"


@dataclass(frozen=True)
class BookManifest:
    """Ordered chapter list + manifest hash for cache invalidation.

    Attributes
    ----------
    chapters
        Ordered list of chapter file paths (sorted by name; ASCII sort matches
        zero-padded numeric ordering for ``chapter-01.md`` style filenames).
    manifest_hash
        ``"sha256:<hex>"`` over the joined ``filename || file_sha256`` strings
        of every chapter. Caller stamps this into the artifact JSON; a fresh
        run computes a new manifest and compares against the stamped value
        to decide whether the artifact is stale.
    """

    chapters: list[Path]
    manifest_hash: str


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def load_book_manifest(book_dir: Path) -> BookManifest:
    """Walk ``book_dir`` for ``*.md`` files; sort by name; compute manifest hash.

    Sorting is by filename only (not full path) so identical chapter sets in
    different parent directories produce the same manifest. Hash inputs are
    ``filename`` + ``"\n"`` + ``sha256(file content)`` joined per chapter and
    delimited by ``"\n\n"`` between chapters; the outer ``sha256()`` is then
    rendered as ``sha256:<hex>``.

    Raises :class:`ValueError` if the directory contains no ``*.md`` files —
    a pre-pass with no chapters is almost certainly a misconfiguration.
    """
    book_dir = Path(book_dir)
    chapters = sorted(book_dir.glob("*.md"), key=lambda p: p.name)
    if not chapters:
        raise ValueError(
            f"book_dir {book_dir!s} contains no *.md chapter files"
        )
    parts: list[str] = []
    for ch in chapters:
        parts.append(f"{ch.name}\n{_file_sha256(ch)}")
    digest = hashlib.sha256("\n\n".join(parts).encode("utf-8")).hexdigest()
    return BookManifest(chapters=chapters, manifest_hash=f"sha256:{digest}")


def build_character_extraction_prompt(
    *,
    chapter_text: str,
    chapter_index: int,
    accumulated_characters: list[dict],
    intake_spec: dict,
) -> str:
    """Render the canonical ``prompts/extract-characters.md`` template body
    plus the per-chapter substitution block.

    Layout (after the canonical prompt body):

        # Translation parameters    -- intake spec
        # Accumulated characters    -- JSON list from prior chapters
        # Current chapter (index N)
        <CHAPTER>
        ...chapter_text...
        </CHAPTER>

    The accumulated state is rendered as JSON so the extractor sees a
    structured record (rather than free-form prose) and merging is
    self-documenting.
    """
    template_body = _load_canonical_prompt("extract-characters.md")
    accumulated_json = json.dumps(
        accumulated_characters, ensure_ascii=False, indent=2
    )
    return (
        f"{template_body}\n"
        "\n"
        "# Translation parameters\n"
        f"{_format_intake_spec_compact(intake_spec)}\n"
        "\n"
        "# Accumulated characters from prior chapters (extend / refine — do NOT discard)\n"
        f"{accumulated_json}\n"
        "\n"
        f"# Current chapter (index {chapter_index})\n"
        "<CHAPTER>\n"
        f"{chapter_text}\n"
        "</CHAPTER>"
    )


def parse_character_extraction_response(response: str) -> list[dict]:
    """Parse the EXTRACTOR JSON response into a list of character dicts.

    Validates per Decision G:

    - Top-level shape: ``{"characters": [<entries>]}``.
    - Each entry has the required keys: ``canonical_name``, ``aliases``,
      ``voice_notes``, ``first_seen_chapter``, ``last_seen_chapter``.
      ``canonical_target`` is required as a key but may be ``null``.
    - ``aliases`` is a list of dicts with ``source`` (string, non-empty) and
      ``target`` (string or null).

    Raises :class:`ValueError` on schema violations. Tolerates models that
    omit optional keys by inserting ``None`` defaults; rejects entries
    missing required keys.
    """
    data = _extract_json_object(response)
    if "characters" not in data or not isinstance(data["characters"], list):
        raise ValueError(
            "character extraction response missing top-level 'characters' list"
        )
    out: list[dict] = []
    for raw in data["characters"]:
        if not isinstance(raw, dict):
            raise ValueError(
                f"character entry must be a dict, got {type(raw).__name__}"
            )
        for key in ("canonical_name", "voice_notes",
                    "first_seen_chapter", "last_seen_chapter"):
            if key not in raw:
                raise ValueError(
                    f"character entry missing required key {key!r}: {raw!r}"
                )
        canonical_target = raw.get("canonical_target", None)
        aliases_raw = raw.get("aliases", [])
        if not isinstance(aliases_raw, list):
            raise ValueError(
                f"character {raw['canonical_name']!r} aliases must be a list"
            )
        aliases: list[dict] = []
        for a in aliases_raw:
            if not isinstance(a, dict):
                raise ValueError(
                    f"alias must be a paired-structure dict, got "
                    f"{type(a).__name__}"
                )
            if "source" not in a:
                raise ValueError(
                    f"alias missing 'source' key: {a!r}"
                )
            if not a["source"]:
                raise ValueError(
                    f"alias 'source' must be non-empty: {a!r}"
                )
            aliases.append({
                "source": a["source"],
                "target": a.get("target", None),
            })
        out.append({
            "canonical_name": raw["canonical_name"],
            "canonical_target": canonical_target,
            "aliases": aliases,
            "voice_notes": raw["voice_notes"],
            "first_seen_chapter": raw["first_seen_chapter"],
            "last_seen_chapter": raw["last_seen_chapter"],
        })
    return out


def _merge_character_entries(
    accumulated: list[dict], incoming: list[dict]
) -> list[dict]:
    """Merge incoming character entries into accumulated state.

    Match key: ``canonical_name`` (case-sensitive exact match). When matched:

    - Append any new aliases (de-duped on ``alias.source``).
    - Replace ``voice_notes`` if incoming is non-empty (caller sees this as
      "REFINE"; the EXTRACTOR is expected to emit the refined voice_notes
      string in full, not a delta).
    - Replace ``canonical_target`` only if accumulated value was None and
      incoming is non-None (don't overwrite a translator-confirmed mapping).
    - Update ``last_seen_chapter`` to max of both.
    - Keep ``first_seen_chapter`` from accumulated (earliest wins).

    Unmatched incoming entries are appended verbatim.
    """
    by_name: dict[str, dict] = {e["canonical_name"]: e for e in accumulated}
    for entry in incoming:
        name = entry["canonical_name"]
        if name not in by_name:
            by_name[name] = dict(entry)
            continue
        existing = by_name[name]
        existing_alias_sources = {a["source"] for a in existing.get("aliases", [])}
        for a in entry.get("aliases", []):
            if a["source"] not in existing_alias_sources:
                existing["aliases"].append(a)
                existing_alias_sources.add(a["source"])
        if entry.get("voice_notes"):
            existing["voice_notes"] = entry["voice_notes"]
        if (
            existing.get("canonical_target") is None
            and entry.get("canonical_target") is not None
        ):
            existing["canonical_target"] = entry["canonical_target"]
        existing["last_seen_chapter"] = max(
            existing.get("last_seen_chapter", entry["last_seen_chapter"]),
            entry["last_seen_chapter"],
        )
        existing["first_seen_chapter"] = min(
            existing.get("first_seen_chapter", entry["first_seen_chapter"]),
            entry["first_seen_chapter"],
        )
    # Preserve insertion order: accumulated first (in original order), then
    # any new names in incoming order.
    out: list[dict] = []
    seen: set[str] = set()
    for e in accumulated:
        out.append(by_name[e["canonical_name"]])
        seen.add(e["canonical_name"])
    for entry in incoming:
        if entry["canonical_name"] not in seen:
            out.append(by_name[entry["canonical_name"]])
            seen.add(entry["canonical_name"])
    return out


def run_pre_pass_characters(
    *,
    book_manifest: BookManifest,
    intake_spec: dict,
    output_path: Path,
    dispatch_subagent: Callable[[str, str], str],
) -> dict:
    """Orchestrate whole-book character extraction.

    For each chapter in ``book_manifest.chapters`` (in order):

    1. Build the EXTRACTOR prompt with current accumulated state.
    2. Dispatch the subagent (fresh context) at
       ``model = resolve_model_for_role(intake_spec.get('model', 'claude-opus-4-7'), 'extractor')``.
    3. Parse the response and merge into accumulated state.

    After all chapters: write JSON artifact at ``output_path`` with
    ``schema_version`` / ``book_manifest_hash`` / ``extracted_at`` /
    ``extractor_model`` / ``characters`` keys. Returns the same dict.

    ``dispatch_subagent`` signature: ``(prompt: str, model: str) -> str``.
    The implementation calls it with ``prompt=`` and ``model=`` keyword
    arguments so tests can assert on either.
    """
    output_path = Path(output_path)
    _check_stale_cache(output_path, book_manifest.manifest_hash)

    model_field = intake_spec.get("model", "claude-opus-4-7")
    extractor_model = resolve_model_for_role(model_field, "extractor")

    accumulated: list[dict] = []
    for idx, chapter_path in enumerate(book_manifest.chapters):
        chapter_text = chapter_path.read_text(encoding="utf-8")
        prompt = build_character_extraction_prompt(
            chapter_text=chapter_text,
            chapter_index=idx,
            accumulated_characters=accumulated,
            intake_spec=intake_spec,
        )
        response = dispatch_subagent(prompt=prompt, model=extractor_model)
        incoming = parse_character_extraction_response(response)
        accumulated = _merge_character_entries(accumulated, incoming)

    artifact: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "book_manifest_hash": book_manifest.manifest_hash,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "extractor_model": extractor_model,
        "characters": accumulated,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return artifact
