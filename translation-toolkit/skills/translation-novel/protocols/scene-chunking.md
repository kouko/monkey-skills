# Scene chunking — chapter → scene boundary detection

> **Implementation source-of-truth**: `scripts/lib/scene_chunker.py`
> (`chunk_chapter_into_scenes(chapter_text, max_scene_tokens=2000)`).
> This protocol documents the algorithm, the four boundary classes, and the
> round-trip contract that the per-scene reassembler in Layer 5 depends on.
> Test fixtures live under `scripts/tests/test_scene_chunker.py`.

## Pattern stack — when this protocol applies

Layer 2 step 3 of the `translation-novel` pipeline. The chunker runs **after**
the chapter file is read and **before** per-scene glossary resolve / DRAFT.
Input is the raw chapter text (one `.md` file's bytes); output is a
`list[Scene]` where each `Scene` carries `index`, `source_text`,
`boundary_type`, and `token_count` (approximate, via `len(text) // 3`).

The chunker is invoked once per chapter. There is no cross-chapter state — a
20-chapter novel calls the chunker 20 times, once per `book-extract`-produced
chapter file.

## The four boundary classes

Detection priority when multiple markers stack on the same byte position:

```
heading > explicit_marker > blank_gap > fallback_token_fill
```

Heading wins because it's the most explicit narrative-structure signal;
explicit markers beat blank gaps because authors who use `* * *` mean to
break a scene; blank gaps beat token-fill because they're an authorial
intent signal even without a glyph; token-fill is the last-resort split
that only fires when a marker-bounded run exceeds `max_scene_tokens`.

### 1. `heading` — H1 / H2 / H3

Any line matching `^#{1,3} ` (one to three `#` followed by a space). H1 is
typically the chapter title; H2 / H3 introduce sub-sections. **The heading
line is kept with the scene it introduces** — the translator sees the
heading + body as one unit, so the heading's voice / register matches the
scene's body.

```
SOURCE   :
    # Chapter 3 — The Departure

    The morning was cold.

    Tom packed his bag.

SCENES   : 1 scene, boundary_type="heading"
           source_text="# Chapter 3 — The Departure\n\nThe morning was cold.\n\nTom packed his bag.\n"
```

### 2. `explicit_marker` — author-declared scene break

A whole-line match (after `strip()`) against the allow-list:

```
* * *
***
―――
◇◇◇
```

Substring matches do **not** count. Variants like `★★★`, `* *`, or `———`
are NOT recognised in v0.2.0; add to `_EXPLICIT_MARKERS` in
`scene_chunker.py` to extend.

**The marker line is consumed by the chunker** — it does not appear in
either the preceding or following scene's `source_text`. The Layer 5
reassembler must re-emit the marker between target scenes. The chunker
does NOT currently expose consumed boundary text via a first-class API;
reassembler implementations should derive consumed text by diffing the
input chapter against the concatenated `source_text` of all scenes (see
the byte-conservation property tested in
`test_scene_chunker.py::test_explicit_marker_split`). A first-class
`consumed_boundaries` API is deferred to a future release if/when a
concrete Layer 5 implementation lands.

```
SOURCE   :
    Tom turned the page.

    * * *

    Three days later, in another city.

SCENES   : 2 scenes
           [0] boundary_type="explicit_marker"  (scene 0 inherits the tag
               of the next real boundary — its trailing edge is the marker)
               source_text="Tom turned the page.\n"
           [1] boundary_type="explicit_marker"
               source_text="Three days later, in another city.\n"
           consumed: "\n* * *\n\n" between scenes 0 and 1
```

The first run is a chapter-leading prelude with no preceding marker, so
the chunker tags scene 0 with the type of the first downstream boundary
(the trailing edge that split it off). If the chapter has no boundary
markers at all, scene 0 falls back to `"fallback_token_fill"`.

### 3. `blank_gap` — ≥2 consecutive blank lines

A run of two or more consecutive blank lines (`stripped == ""`). A single
blank line is treated as a paragraph separator within a scene, NOT a scene
boundary. Blank-gap whitespace is consumed by the chunker.

```
SOURCE   :
    Tom packed his bag.



    He stepped outside.

SCENES   : 2 scenes
           [0] boundary_type=...  source_text="Tom packed his bag.\n"
           [1] boundary_type="blank_gap"  source_text="He stepped outside.\n"
           consumed: "\n\n\n" between
```

A blank-line run that only counts to 1 keeps the scene intact:

```
SOURCE   :
    Tom packed his bag.

    He stepped outside.

SCENES   : 1 scene  (single blank line = paragraph separator, not boundary)
           source_text="Tom packed his bag.\n\nHe stepped outside.\n"
```

### 4. `fallback_token_fill` — oversize-run sub-split

The only class that can emit **multiple Scenes from a single
marker-bounded run**. When a heading / explicit-marker / blank-gap run
grows past `max_scene_tokens` (default 2000, ~6000 chars under the char/3
heuristic), the chunker greedy-packs it into sub-chunks at paragraph
boundaries (one or more blank lines). The first sub-chunk inherits the
run's original `boundary_type` (it's still bounded by the original marker
on its leading edge); subsequent sub-chunks are tagged
`fallback_token_fill`.

A single oversize paragraph that exceeds `max_scene_tokens` on its own is
emitted as its own scene rather than sliced mid-sentence — the chunker
errs on the side of preserving paragraph integrity over hitting the token
target exactly.

If the chapter has **no boundary markers at all**, the entire chapter is
one run that gets tagged `fallback_token_fill` and sub-split as needed.

## Boundary consumption — what gets dropped vs kept

| Class | Boundary text fate |
|---|---|
| `heading` | KEPT — the `# ...` line is part of the scene's `source_text` |
| `explicit_marker` | CONSUMED — the marker line is dropped from `source_text` |
| `blank_gap` | CONSUMED — the ≥2 blank lines are dropped from `source_text` |
| `fallback_token_fill` | KEPT (paragraph separator) — the splitter pivots on `\n\s*\n` and keeps the separator with the **preceding** chunk (left side); see `_greedy_token_fill` in `scene_chunker.py` for the candidate-then-flush logic |

The Layer 5 reassembler is responsible for **re-emitting** consumed
boundary text between target scenes so the chapter target round-trips
visually. Heading lines do not need re-emission (they're inside the
scene). Explicit-marker lines and blank-gap whitespace do.

## Round-trip contract

> Given `chapter_text` and `scenes = chunk_chapter_into_scenes(chapter_text)`,
> there exists a deterministic reassembler `R` such that
> `R(scenes, consumed_boundary_text) == chapter_text` byte-identically.

Tests in `scripts/tests/test_scene_chunker.py` assert this byte-conservation
property across the four-class fixture set. Any chunker change MUST
preserve this contract; the per-scene reassembler in Layer 5 of
`translation-novel` (and, transitively, checklist item 1 + item 2 of
`checklists/novel-quality-checklist.md`) depends on it.

The reassembler does NOT see the original `chapter_text` — it stitches
target-language scenes plus the chunker-recorded boundary text. Boundary
text is byte-identical between source and target (markers and blank-gap
whitespace are not translation-bearing).

## Token estimation

`approx_tokens(text) = max(1, len(text) // 3)` for non-empty text, else 0.
The 3-char-per-token heuristic over-counts Latin (~4 chars/token actually)
and under-counts CJK (~1.5 chars/token actually); ~3 is a serviceable
middle for mixed JP / ZH / EN novels and is **only used to size budget
windows + decide fallback splits, never to bill anyone**.

`max_scene_tokens` defaults to 2000 — under the heuristic that's ~6000
characters of source. Empirically this puts most marker-bounded scenes in
a single chunk while keeping prompt size ≤ ~10K tokens including
prev/next windows + glossary + intake. Override per-call when novel pacing
runs longer or shorter.

## What is NOT covered here

- **Chapter splitting** — `tsundoku:book-extract` produces one chapter per
  `.md` file; `translation-novel` operates on a chapter at a time. Novel-
  level concerns (character-arc tracking, cross-chapter callback
  consistency) are deferred to Tier 2.
- **Markdown AST structure** — protect-pass + AST handling is `translation-doc`'s
  job; novel mode treats the chapter as prose text. If a chapter contains
  embedded code / math / diagrams (rare), route to `translation-doc`.
- **Scene-window prompt rendering** — see `protocols/scene-window-context.md`.

## See also

- `scripts/lib/scene_chunker.py` — implementation source-of-truth
- `protocols/scene-window-context.md` — Decision 4 prompt layout (consumes scene chunks)
- `checklists/novel-quality-checklist.md` — items 1 + 2 verify the round-trip
- `references/core-loop.md` — DRAFT / REFLECT / IMPROVE contract per scene
