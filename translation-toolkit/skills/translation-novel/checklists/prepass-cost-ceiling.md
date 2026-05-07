# Pre-pass cost ceiling — Decision E #2 acceptance bar

> **Caller-facing reference.** This checklist documents the
> `prepass_tokens / single_chapter_translation_tokens ≤ 0.5` acceptance
> criterion that v0.3.0 Tier 2 ships behind. The bar is a hard-fail in
> the project's own E2E smoke test (Phase F's
> `test_cost_ceiling_assertion`); callers translating real books should
> understand when it holds, when it legitimately does not, and what to
> do in either case.
>
> Source: v0.3.0 Tier 2 plan §Decision E #2 — see
> `docs/superpowers/plans/2026-05-07-translation-toolkit-v0.3.0-tier2.md`.

## The criterion

> With a cheap-model `extractor` override (e.g.
> `model={'default': '<standard>', 'extractor': 'claude-haiku-4-5'}`),
> the whole-book pre-pass token cost on a multi-chapter book is **≤ 50%
> of the expected single-chapter scene-translation cost**, asserted via
> `scripts.lib.scene_chunker.approx_tokens` math (no real LLM calls).

In symbols:

```
ratio = prepass_tokens / single_chapter_translation_tokens
ratio <= 0.5            # acceptance bar
```

On a multi-chapter book the ratio drops further as the pre-pass
amortizes — the bar is set for the smallest realistic case (the
project's 走れメロス fixture: 2 chapters, ~1,500 + ~1,500 chars).

## How to compute the assertion

### 1. `prepass_tokens`

Sum across all chapters in `book_manifest.chapters` of the per-chapter
EXTRACTOR-prompt token estimate:

```python
from scripts.lib.scene_chunker import approx_tokens

prepass_tokens = sum(
    approx_tokens(chapter_text)
    + approx_tokens(canonical_extractor_prompt)
    + approx_tokens(accumulated_state_json_for_this_chapter)
    for chapter_text in book_manifest.chapter_texts
)
```

The pre-pass dispatches **once per chapter** during Layer 1.5 (per
`protocols/character-extraction.md` §"Subagent dispatch contract"). The
accumulated-state JSON grows monotonically across chapters; for a
2-chapter fixture it's small but non-zero on chapter 2.

The `_helper` math in the smoke test approximates this by counting
chapter-text tokens only and bounding the prompt + state overhead — see
`scripts/tests/test_e2e_smoke.py` for the exact computation when the
v0.3.0 Phase F smoke ships.

### 2. `single_chapter_translation_tokens`

Per-scene cost summed across one chapter, using the largest chapter as
the denominator (worst-case single-chapter run):

```python
single_chapter_translation_tokens = sum(
    # DRAFT: parameters + glossary + prev_v2 (~500 tok) + scene + next_src (~200 tok) + reqs
    + approx_tokens(scene.source_text)
    + 500 + 200
    + approx_tokens(canonical_draft_prompt_overhead)
    # REFLECT 5d-literary: same window + draft v1
    + approx_tokens(scene.source_text) * 2  # source + draft v1
    + 500 + 200
    + approx_tokens(canonical_reflect_5d_literary_prompt_overhead)
    # IMPROVE: same window + critique
    + approx_tokens(scene.source_text)
    + approx_tokens(critique_estimate)
    + approx_tokens(canonical_improve_prompt_overhead)
    for scene in chapter.scenes
)
```

The constants (~500 / ~200) come from `protocols/scene-window-context.md`
§3 + §5; the `* 3` factor in the simplified bound below comes from one
DRAFT + one REFLECT + one IMPROVE call per scene per
`references/core-loop.md`.

### 3. Assert

```python
assert prepass_tokens <= 0.5 * single_chapter_translation_tokens, (
    f"pre-pass cost ratio {prepass_tokens / single_chapter_translation_tokens:.3f} "
    f"exceeds 0.5 — see checklists/prepass-cost-ceiling.md for expected-failure cases"
)
```

Per Decision E #2, this is a **hard-fail** in v0.3.0's own acceptance
test. Callers may run the same assertion as a sanity-check on their
own books; failure means inspect the expected-failure cases below.

## When the bar is expected to hold

- **Multi-chapter books** (≥ 2 chapters of comparable length). The
  pre-pass is `O(total_chars)`; per-chapter translation is also
  `O(chapter_chars)` but multiplied by ~3 LLM calls (DRAFT + REFLECT +
  IMPROVE) per scene plus the ~500 + ~200 token window overhead per
  scene. Even on a 2-chapter book the ratio is typically ~0.3 with a
  cheap extractor.
- **Cheap-model extractor override active.** The cost-ceiling math
  assumes the EXTRACTOR runs on a haiku-class (or cheaper) model. The
  `approx_tokens` math is model-agnostic, but the **price-per-token**
  argument that motivates the ceiling collapses without the cheap-model
  override. For the assertion expressed in raw tokens, the ratio
  depends only on the input shape and extractor prompt overhead —
  cheap-model split tightens the *dollar* ratio further.
- **Books with non-trivial recurring entities.** Pre-pass is most
  valuable when characters / places / world terms recur across chapters
  — that's where Layer 1.5 amortization shines. A book with 1
  character + 0 places per chapter still passes the bar but the
  *quality-payoff* per pre-pass token shrinks.

## When the bar is expected to fail (legitimately)

These are the documented expected-failure cases. Callers hitting them
should understand the result is not a regression — it's a degenerate
input shape.

1. **Single-chapter input** (`book_manifest` has 1 file or
   `book_manifest` not supplied). In single-chapter mode the
   denominator collapses — `prepass_tokens` includes the full chapter
   plus prompt overhead, and `single_chapter_translation_tokens` is
   the same chapter's per-scene cost. Ratio approaches or exceeds 1.0.
   This is **expected** and the v0.3.0 acceptance test does not run on
   single-chapter inputs. Caller workaround: skip the cost-ceiling
   assertion in this mode; the pre-pass still works (artifacts produced
   correctly), the cost argument simply does not apply.
2. **No cheap-model override** — `model` passed as a plain string, or
   `model.extractor` not specified (falls through to `default`). The
   *raw-token* ratio still holds (extractor prompt overhead is small),
   but the **dollar** ratio doubles or worse. Caller workaround: pass
   `model={'default': '<standard>', 'extractor': '<cheap>'}`. The
   intake validator warns when the dict-form is missing `extractor`.
3. **Pathologically short chapters (< ~1,000 chars each).** The
   per-chapter EXTRACTOR prompt overhead dominates. The 走れメロス
   fixture's 2-chapter setup uses `~1,500 char` chapters precisely to
   stay above this threshold — see plan §Phase F's chapter-02 stub
   spec ("≥ 50% of chapter 1 length"). Caller workaround: if your
   chapters are very short (e.g. flash-fiction collections), expect
   the ratio to bunch above 0.5 even with cheap-model split. The bar
   is calibrated for novel-shaped chapters.
4. **Very large prompt-overhead growth** (extractor prompt + accumulated
   state grow nonlinearly because the book has hundreds of recurring
   entities). The `accumulated_state_json` grows with every chapter's
   character/world additions; on a 30-chapter epic with 100+ named
   characters the per-chapter prompt grows substantially. The bar
   should still hold (denominator grows with chapter count too) but
   inspect the absolute numbers if the ratio approaches 0.5.

## What to do when the assertion fails

1. **Inspect the inputs.** Is `book_manifest` single-file or
   degenerately small? Skip the assertion; pre-pass still works.
2. **Check `model` argument shape.** Did you pass a dict with
   `extractor` overridden to a cheap model? If not, the assertion was
   measuring against a configuration the cost-ceiling argument does not
   cover.
3. **Check chapter sizes.** Below ~1,000 chars / chapter the prompt
   overhead dominates. This is a real signal — pre-pass at this scale
   does not amortize meaningfully.
4. **Inspect the manifest-hash chain.** A stale manifest causes
   `book_manifest_hash` mismatches that surface elsewhere (Layer 1.5
   `WARN` + checklist item 7), not as a cost-ceiling failure — but
   confirm the pre-pass actually re-ran on a stale-cache scenario.
5. **If none of the above apply** the failure is a real regression —
   surface to the toolkit maintainer with the input shapes and the
   computed `prepass_tokens / single_chapter_translation_tokens` ratio.

## What this checklist does NOT cover

- **Pre-pass content quality.** This checklist is about token
  *quantity*, not extracted-content correctness. EXTRACTOR-output
  quality is enforced by M2 (HARD per-scene), checklist item 5
  (chapter-level glossary consistency), and downstream translator
  review of `<repo>/.translations/*.json`.
- **Per-scene M3 / S1 / S2 cost.** Layer 4 gate cost is part of
  `single_chapter_translation_tokens` indirectly (S1 dispatches a
  full back-translation per chunk) but the cost-ceiling assertion
  uses a deterministic approximation that does not separately budget
  S1 dispatch overhead. M3 is fully deterministic so contributes ~0.
- **Live API pricing comparisons.** The bar uses `approx_tokens`
  (char/3 heuristic) — no real LLM calls. Convert to dollars using
  your provider's pricing if needed; the ratio in *tokens* maps
  near-linearly to *dollars* when the cheap-model split puts a haiku-
  class on EXTRACTOR.

## See also

- `docs/superpowers/plans/2026-05-07-translation-toolkit-v0.3.0-tier2.md`
  §Decision E — full Tier 2 acceptance criteria
- `protocols/character-extraction.md` §"Subagent dispatch contract" —
  per-chapter EXTRACTOR dispatch shape (drives `prepass_tokens`)
- `protocols/scene-window-context.md` §6-section layout — drives
  per-scene cost in `single_chapter_translation_tokens`
- `references/core-loop.md` — DRAFT / REFLECT / IMPROVE call count per
  scene
- `references/orthogonal-axes.md` §Model routing — `model` dict shape +
  `extractor` cheap-model split
- `scripts/lib/scene_chunker.py` — `approx_tokens` (char/3 heuristic)
- `checklists/novel-quality-checklist.md` — sibling roundtrip checklist
  (item 7 is the freshness counterpart to this cost bar)
