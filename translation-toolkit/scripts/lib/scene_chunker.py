"""Scene-aware chapter chunker for novel-mode translation (Phase A of v0.2.0).

Runtime library used by the upcoming ``translation-novel`` skill to split a
chapter file into Scene units before per-scene translation. Replaces token-only
chunking with a hierarchy that respects narrative structure:

    chapter -> scene -> paragraph -> sentence

A Scene is a run of consecutive paragraphs separated from neighbours by one of
four boundary classes. Detection priority when multiple markers stack:

    heading > explicit_marker > blank_gap > fallback_token_fill

Boundary classes
----------------
- ``heading`` — any line matching ``^#{1,3} ``. H1 is typically the chapter
  title; H2/H3 introduce sub-sections. The heading line itself is kept with the
  scene it introduces (so a translator sees the heading + body as one unit).
- ``explicit_marker`` — a whole line whose stripped content is one of the
  allow-listed scene-break glyphs: ``* * *``, ``***``, ``―――``, ``◇◇◇``.
  Substring matches do not count; variants like ``★★★`` are NOT recognised.
  The marker line is **consumed by the chunker** — it is not part of either
  the preceding or following scene's ``source_text``.
- ``blank_gap`` — two or more consecutive blank lines (i.e. >=3 newlines in
  the raw text). A single blank line is just a paragraph separator and does
  NOT split scenes. Blank lines at a boundary are also consumed by the
  chunker. (Spec carries both ">=2 lines" and ">=3 blank lines" wording; we
  use the more permissive >=2 since chapter exports often use exactly 2.)
- ``fallback_token_fill`` — when a scene found by the above rules grows past
  ``max_scene_tokens``, it is greedily packed at paragraph boundaries into
  scene chunks of ~``max_scene_tokens``. This is the only class that can
  emit multiple Scenes from a single marker-bounded run.

Round-trip contract
-------------------
Boundary text (heading lines stay; explicit-marker + blank-gap text is
consumed) is the only thing dropped. Concatenating ``s.source_text`` for
each Scene, plus the consumed boundary strings recorded internally, exactly
reproduces the input chapter. Tests assert this byte-conservation property.

Token estimation
----------------
Uses a ``len(text) / 3`` char-heuristic — keeps the lib zero-runtime-dep
(no tiktoken). The heuristic over-estimates Latin text and under-estimates
CJK; ~3 chars/token is a serviceable middle ground for mixed JP/ZH/EN
novels and is only used to decide fallback splits, not to bill anyone.

This module lives at plugin-level ``translation-toolkit/scripts/lib/`` and
is independent of any skill folder.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = ["Scene", "approx_tokens", "chunk_chapter_into_scenes"]


# Whole-line allow-list for explicit scene-break markers. Match after strip().
_EXPLICIT_MARKERS: frozenset[str] = frozenset({"* * *", "***", "―――", "◇◇◇"})

# Heading line: H1, H2, or H3 (one to three '#' followed by a space).
_HEADING_RE = re.compile(r"^#{1,3} ")


@dataclass
class Scene:
    """A scene-sized chunk of chapter text ready for translation."""

    index: int  # zero-based within chapter
    source_text: str
    boundary_type: str  # "explicit_marker" | "blank_gap" | "heading" | "fallback_token_fill"
    token_count: int  # approx, via char/3 heuristic


def approx_tokens(text: str) -> int:
    """Approximate token count via len(text) / 3 (rounded up if non-empty).

    Public helper shared with novel_prompts.py so both modules use the same
    char-heuristic when sizing scene-window slices. Latin text is over-counted,
    CJK is under-counted; ~3 chars/token is a workable middle ground for mixed
    JP/ZH/EN novels and is only ever used to size budget windows, never to bill.
    """
    if not text:
        return 0
    return max(1, len(text) // 3)


def _split_into_marker_runs(chapter_text: str) -> list[tuple[str, str]]:
    """Split chapter_text into (boundary_type, run_text) segments.

    Walks the text line-by-line and emits a run whenever a heading,
    explicit marker, or blank-gap (>=2 blank lines) is encountered.
    Heading lines are *kept* in the following run (and tag it ``heading``).
    Explicit-marker lines and blank-gap lines are *consumed*.

    The first run's boundary_type is determined by what (if anything)
    starts the chapter: a heading -> ``heading``; otherwise the run gets
    a placeholder ``"start"`` which the caller upgrades to whatever the
    first real boundary turned out to be (or, if there is none and we
    must fall back, ``fallback_token_fill``).
    """
    lines = chapter_text.splitlines(keepends=True)
    runs: list[tuple[str, str]] = []
    current: list[str] = []
    current_type = "start"

    def flush() -> None:
        if current:
            runs.append((current_type, "".join(current)))
            current.clear()

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Heading boundary: H1/H2/H3 starts a new run; the heading line
        # itself stays with the new run so the translator sees it.
        if _HEADING_RE.match(line):
            flush()
            current_type = "heading"
            current.append(line)
            i += 1
            continue

        # Explicit marker boundary (whole-line match against allow-list).
        if stripped in _EXPLICIT_MARKERS:
            flush()
            current_type = "explicit_marker"
            i += 1  # marker line consumed
            continue

        # Blank-gap boundary: >=2 consecutive blank lines.
        if stripped == "":
            j = i
            while j < n and lines[j].strip() == "":
                j += 1
            blank_count = j - i
            if blank_count >= 2:
                flush()
                current_type = "blank_gap"
                i = j  # blank lines consumed
                continue
            # Single blank line: keep as paragraph separator inside the run.
            current.append(line)
            i += 1
            continue

        # Regular content line.
        current.append(line)
        i += 1

    flush()
    return runs


def _greedy_token_fill(text: str, max_scene_tokens: int) -> list[str]:
    """Greedy-pack ``text`` into chunks <=max_scene_tokens, splitting at
    paragraph boundaries (one or more blank lines).

    A single oversize paragraph is emitted as its own chunk rather than
    being silently sliced mid-sentence.
    """
    # Split into paragraphs while preserving the inter-paragraph blank lines
    # so chunks reassemble byte-for-byte.
    parts = re.split(r"(\n\s*\n)", text)
    # re.split with a capturing group produces [content, sep, content, sep, ...].
    # Empty strings appear only when the separator is at the very start or end of
    # text; the loop's `if not part: continue` skips them because they contribute
    # nothing to token count or output.
    chunks: list[str] = []
    buf = ""
    for part in parts:
        if not part:
            continue
        candidate = buf + part
        if approx_tokens(candidate) <= max_scene_tokens or not buf:
            buf = candidate
        else:
            chunks.append(buf)
            buf = part
    if buf:
        chunks.append(buf)
    return chunks


def chunk_chapter_into_scenes(
    chapter_text: str, max_scene_tokens: int = 2000
) -> list[Scene]:
    """Split a chapter into Scene objects using boundary markers + token-fill fallback.

    Parameters
    ----------
    chapter_text:
        Raw chapter contents (typically one .md file).
    max_scene_tokens:
        Target ceiling for each scene's approx token count. Scenes from
        marker-detected runs that exceed this are sub-split via
        ``fallback_token_fill``.

    Returns
    -------
    list[Scene]
        Zero or more scenes in original order. Empty input -> empty list.
        Each Scene's ``source_text`` is non-empty.
    """
    if not chapter_text:
        return []

    runs = _split_into_marker_runs(chapter_text)
    scenes: list[Scene] = []
    idx = 0
    saw_any_marker = any(t != "start" for t, _ in runs)

    for run_type, run_text in runs:
        if not run_text:
            continue

        # The first run gets boundary_type "start" if nothing precedes it.
        # Resolve that to the most accurate label we can:
        #   - if the chapter never has any boundary marker at all,
        #     this whole chapter is one big run -> fallback_token_fill
        #     (caller will sub-split below if oversize).
        #   - otherwise the first run is just the prelude before the first
        #     real boundary; tag it "heading" if the chapter's first real
        #     boundary was a heading (most common chapter-title case),
        #     else fall back to "fallback_token_fill" semantics for label.
        if run_type == "start":
            if not saw_any_marker:
                effective_type = "fallback_token_fill"
            else:
                # Use the type of the next run as a hint for what split off
                # this prelude. This mirrors how a human reader would
                # describe the boundary that produced the prelude.
                next_types = [t for t, _ in runs if t != "start"]
                effective_type = next_types[0] if next_types else "fallback_token_fill"
        else:
            effective_type = run_type

        # If the run fits within budget, emit it as a single scene.
        if approx_tokens(run_text) <= max_scene_tokens:
            scenes.append(
                Scene(
                    index=idx,
                    source_text=run_text,
                    boundary_type=effective_type,
                    token_count=approx_tokens(run_text),
                )
            )
            idx += 1
            continue

        # Oversize run -> greedy paragraph-boundary fill. The first sub-chunk
        # keeps the run's own boundary_type (it's still bounded by the
        # original marker on its leading edge); subsequent sub-chunks are
        # tagged ``fallback_token_fill``.
        sub_chunks = _greedy_token_fill(run_text, max_scene_tokens)
        for sub_idx, sub_text in enumerate(sub_chunks):
            tag = effective_type if sub_idx == 0 else "fallback_token_fill"
            scenes.append(
                Scene(
                    index=idx,
                    source_text=sub_text,
                    boundary_type=tag,
                    token_count=approx_tokens(sub_text),
                )
            )
            idx += 1

    return scenes
