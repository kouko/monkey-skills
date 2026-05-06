"""Scene-window prompt builders for novel-mode translation (Phase B of v0.2.0).

Replaces the v0.1.0 whole-document windowing
(``<DOCUMENT>...full novel...</DOCUMENT><TRANSLATE_THIS>chunk</TRANSLATE_THIS>``)
with a scene-aware layout:

    prev (~500 tok of prev_scene_v2)
    + current scene (full)
    + next (~200 tok of next_scene_source)

This collapses cost from O(N^2) to O(N) over a chapter while keeping voice
and narrative continuity tied to the actual translation of the previous
scene rather than its source text (Decision 5 of the v0.2.0 plan).

The prompt builder is a pure renderer:
- caller resolves glossary hits via :func:`lib.glossary.lookup` over the
  current + prev + next windows and passes them as ``glossary_hits``.
- caller passes ``prev_scene_v2`` (the *target-language* translation of
  the previous scene, not its source) when available.
- builder formats Decision 4's six-section markdown layout, no I/O.

Three functions mirror the v0.1.0 reflect/improve loop:
- :func:`build_scene_draft_prompt`   -- initial v1 draft.
- :func:`build_scene_reflect_prompt` -- 4D critique JSON.
- :func:`build_scene_improve_prompt` -- apply critique -> v2.
"""
from __future__ import annotations

import json

from lib.scene_chunker import Scene, approx_tokens

__all__ = [
    "build_scene_draft_prompt",
    "build_scene_reflect_prompt",
    "build_scene_improve_prompt",
]


# 3 chars/token heuristic mirrors scene_chunker.approx_tokens.
_CHARS_PER_TOKEN = 3
_PREV_WINDOW_TOKENS = 500
_NEXT_WINDOW_TOKENS = 200


def _truncate_tail(text: str, max_tokens: int) -> str:
    """Return the last ``max_tokens`` worth of text via char-budget slicing."""
    if approx_tokens(text) <= max_tokens:
        return text
    return text[-(max_tokens * _CHARS_PER_TOKEN) :]


def _truncate_head(text: str, max_tokens: int) -> str:
    """Return the first ``max_tokens`` worth of text via char-budget slicing."""
    if approx_tokens(text) <= max_tokens:
        return text
    return text[: max_tokens * _CHARS_PER_TOKEN]


def _format_glossary_hits(glossary_hits: list[dict]) -> str:
    """Render glossary entries as ``- source -> target (notes)`` lines.

    Caller is responsible for filtering hits to those appearing in
    current + prev + next windows; this renderer keeps every entry passed.

    Malformed entries (missing or empty ``source_term`` or ``target_term``)
    are silently dropped: callers may legitimately have partial data, and a
    missing entry is preferable to a malformed prompt line like
    ``- -> target`` that the model could mis-parse.
    """
    if not glossary_hits:
        return "(none -- no in-scope glossary terms)"
    lines: list[str] = []
    for hit in glossary_hits:
        source_term = hit.get("source_term", "")
        target_term = hit.get("target_term", "")
        if not source_term or not target_term:
            continue
        notes = hit.get("notes", "") or ""
        if notes:
            lines.append(f"- {source_term} -> {target_term} ({notes})")
        else:
            lines.append(f"- {source_term} -> {target_term}")
    if not lines:
        return "(none -- no in-scope glossary terms)"
    return "\n".join(lines)


def _format_intake_spec(intake_spec: dict) -> str:
    """Render intake spec as a compact multi-line key/value block."""
    keys = ("source_locale", "target_locale", "mode", "register", "domain")
    lines: list[str] = []
    for key in keys:
        if key in intake_spec:
            lines.append(f"- {key}: {intake_spec[key]}")
    # Keep any extra caller-supplied keys for forward-compat (e.g. strategy).
    for key, value in intake_spec.items():
        if key in keys:
            continue
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) if lines else "(none)"


def build_scene_draft_prompt(
    *,
    scene: Scene,
    prev_scene_v2: str | None,
    next_scene_source: str | None,
    intake_spec: dict,
    glossary_hits: list[dict],
) -> str:
    """Build the DRAFT prompt for a single scene per Decision 4 layout.

    Sections (6, all H1, in this order):
        1. Translation parameters       -- intake spec inline.
        2. Glossary terms               -- caller-resolved hits only.
        3. Previous scene               -- last ~500 tokens of prev_scene_v2,
                                           or '(none -- first scene)' if None.
        4. CURRENT SCENE                -- scene.source_text wrapped in
                                           <TRANSLATE_THIS> markers.
        5. Next scene opening           -- first ~200 tokens of
                                           next_scene_source, or '(none --
                                           last scene)' if None.
        6. Output requirements          -- translate-only-current-scene rules.

    Truncation: ``_truncate_tail`` and ``_truncate_head`` slice by
    ``len(text) // _CHARS_PER_TOKEN`` (mirrors :func:`approx_tokens`); the
    char budgets are 1500 (prev) and 600 (next).
    """
    if prev_scene_v2 is None:
        prev_section = "(none -- first scene of chapter)"
    else:
        prev_section = _truncate_tail(prev_scene_v2, _PREV_WINDOW_TOKENS)

    if next_scene_source is None:
        next_section = "(none -- last scene of chapter)"
    else:
        next_section = _truncate_head(next_scene_source, _NEXT_WINDOW_TOKENS)

    return (
        "# Translation parameters\n"
        f"{_format_intake_spec(intake_spec)}\n"
        "\n"
        "# Glossary terms -- USE THESE, do not invent alternatives (only those that hit in current scene + prev/next windows)\n"
        f"{_format_glossary_hits(glossary_hits)}\n"
        "\n"
        "# Previous scene (last ~500 tokens) -- for continuity\n"
        f"{prev_section}\n"
        "\n"
        "# CURRENT SCENE -- translate ALL of this\n"
        "<TRANSLATE_THIS>\n"
        f"{scene.source_text}\n"
        "</TRANSLATE_THIS>\n"
        "\n"
        "# Next scene opening (first ~200 tokens) -- for narrative flow context\n"
        f"{next_section}\n"
        "\n"
        "# Output requirements\n"
        "- Translate ONLY content inside <TRANSLATE_THIS>\n"
        "- Preserve scene's paragraph breaks exactly\n"
        "- Preserve all ⟦P:NN⟧ placeholder tokens unchanged\n"
        "- Do NOT include translation of prev/next windows\n"
        "- Output ONLY the translation"
    )


def build_scene_reflect_prompt(
    *,
    scene: Scene,
    draft_v1: str,
    intake_spec: dict,
    glossary_hits: list[dict],
) -> str:
    """Build the 4D REFLECT prompt for a scene draft.

    Same shape as the v0.1.0 ``reflect-4d.md`` template (Accuracy /
    Fluency / Style / Terminology), but tied to a scene-window source
    rather than a doc chunk.
    """
    return (
        "You are a translation critic reviewing this scene draft. Produce structured\n"
        "4D critique across these axes (one paragraph per axis, with concrete\n"
        "suggestions where issues found):\n"
        "\n"
        "1. Accuracy -- semantic faithfulness. Are there additions, omissions, distortions?\n"
        "2. Fluency -- does target read naturally? Awkward phrasings?\n"
        "3. Style -- does register/rhythm/rhetoric match source and intended mode/register?\n"
        "4. Terminology -- does it match the glossary? Domain conventions?\n"
        "\n"
        "# Translation parameters\n"
        f"{_format_intake_spec(intake_spec)}\n"
        "\n"
        "# Glossary terms\n"
        f"{_format_glossary_hits(glossary_hits)}\n"
        "\n"
        "# Source scene\n"
        "<SOURCE>\n"
        f"{scene.source_text}\n"
        "</SOURCE>\n"
        "\n"
        "# Draft v1\n"
        "<DRAFT_V1>\n"
        f"{draft_v1}\n"
        "</DRAFT_V1>\n"
        "\n"
        "Output format (JSON):\n"
        "{\n"
        '  "accuracy":   [{"issue": "...", "suggestion": "..."}, ...],\n'
        '  "fluency":    [...],\n'
        '  "style":      [...],\n'
        '  "terminology":[...]\n'
        "}\n"
        "\n"
        "If an axis has no issues, return empty array. Do NOT rewrite the translation --\n"
        "only critique."
    )


def build_scene_improve_prompt(
    scene: Scene,
    draft_v1: str,
    critique_json: dict,
) -> str:
    """Build the REVISER prompt: apply critique to v1 -> produce v2.

    Mirrors v0.1.0 ``improve.md`` -- the critique JSON is rendered inline
    so the model has both the original draft and the structured fixes in
    a single payload.
    """
    critique_str = json.dumps(critique_json, ensure_ascii=False, indent=2)
    return (
        "You are a translation reviser. Given the scene draft v1 and the 4D critique\n"
        "below, produce v2 incorporating the suggestions. Do NOT add new reasoning\n"
        "beyond the critique -- just apply the fixes.\n"
        "\n"
        "Preserve all ⟦P:NN⟧ placeholder tokens unchanged.\n"
        "\n"
        "# Source scene\n"
        "<SOURCE>\n"
        f"{scene.source_text}\n"
        "</SOURCE>\n"
        "\n"
        "# Draft v1\n"
        "<DRAFT_V1>\n"
        f"{draft_v1}\n"
        "</DRAFT_V1>\n"
        "\n"
        "# Critique (JSON)\n"
        f"{critique_str}\n"
        "\n"
        "Output ONLY the revised translation."
    )
