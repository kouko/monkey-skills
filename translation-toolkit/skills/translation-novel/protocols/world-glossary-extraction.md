# World-glossary extraction — whole-book pre-pass for places / orgs / terms / cultural references

> **Implementation source-of-truth**: `scripts/lib/world_glossary_extractor.py`
> (`build_world_glossary_extraction_prompt`,
> `parse_world_glossary_extraction_response`,
> `run_pre_pass_world_glossary`).
> Test fixtures live in `scripts/tests/test_world_glossary_extractor.py`.

## EXTRACTOR role contract — see character-extraction.md

> This protocol shares the EXTRACTOR role / dispatch / cache rules defined
> in `protocols/character-extraction.md` §"EXTRACTOR role behavioral
> contract". **Read that first.** Specifically the following are identical
> across both pre-passes:
>
> - Fresh subagent context per chapter (no cross-context leakage).
> - Subagent receives a rendered prompt + model identifier, NOT file paths.
> - Cache invalidation via `book_manifest_hash` + `UserWarning` on
>   mismatch (orchestrator overwrites; caller decides).
> - Per-role model routing via
>   `resolve_model_for_role(model, "extractor")`.

This protocol covers ONLY what's specific to world-glossary extraction:
the four-class schema, the closed-enum constraints, and the merge rules
that differ from character extraction (append-only for places /
organizations / cultural_references; refine-notes for world_terms).

## Pattern stack — when this protocol applies

Tier 2 of the `translation-novel` pipeline (v0.3.0+). Runs alongside
character extraction as a sibling pre-pass — both walk the same chapter
manifest, both emit a single artifact stamped with `book_manifest_hash`,
both feed the L1.5 tier of `glossary.lookup`. They are independent: a
caller may run only character extraction, only world-glossary extraction,
or both. The runtime L1.5 lookup gracefully tolerates missing classes
(empty list / missing key → that class skipped).

## World-glossary schema (Decision G)

```json
{
  "schema_version": "0.3.0",
  "book_manifest_hash": "sha256:...",
  "extracted_at": "2026-05-07T...",
  "extractor_model": "claude-haiku-4-5",
  "places": [
    {"canonical_source": "シラクサ",
     "canonical_target": "Syracuse",
     "first_seen_chapter": 1}
  ],
  "organizations": [],
  "world_terms": [
    {"canonical_source": "暴君",
     "canonical_target": "tyrant",
     "notes": "context-dependent — could be 'despot' depending on register",
     "first_seen_chapter": 1}
  ],
  "cultural_references": [
    {
      "source_phrase": "信実とは決して空虚な妄想ではなかった",
      "category": "literary_quotation",
      "handling_hint": "borrow",
      "first_seen_chapter": 1
    }
  ]
}
```

### The four classes — what goes where

| Class | What | Example |
|---|---|---|
| `places` | Named geographic locations (cities, regions, mountains, rivers) | `シラクサ → Syracuse` |
| `organizations` | Named groups (governments, companies, guilds, factions) | `元老院 → Senate` |
| `world_terms` | Domain / world-specific vocabulary that is NOT a proper noun (concepts, ranks, period objects) | `暴君 → tyrant` (with register-shading `notes`) |
| `cultural_references` | Literary quotations, idioms, religious / food / historical references | `信実とは… → borrow` (literary_quotation) |

Generic locations / groups (`the mountains` / `the soldiers`) are NOT
extracted unless given a recurring proper-noun identifier. The EXTRACTOR
prompt enforces this filter.

### `cultural_references[].category` — closed enum

```
literary_quotation | idiom | religious_term | food_term |
place_culture | historical_reference | other
```

The parser (`parse_world_glossary_extraction_response`) **rejects unknown
values** with a `ValueError`. Use `other` for references that don't fit
any of the named buckets — do NOT invent new categories. If a recurring
new bucket emerges, propose extending the enum in a follow-up rather
than letting it leak in.

### `handling_hint` semantics — borrow / explain / approximate

`handling_hint` is also a closed enum:

- **`borrow`** — render verbatim in target (loanword / italicized
  romanization / footnote on first use). Use for literary quotations,
  proper-noun cultural items where target reader is expected to learn
  the foreign term.
- **`explain`** — paraphrase or inline-gloss in target. Use when the
  reference is load-bearing for plot/theme but unfamiliar to target
  reader.
- **`approximate`** — substitute a target-culture analog. Use when the
  reference is decorative and a literal borrow would distract.

The hint is **a recommendation for the IMPROVE pass**, not a binding
decision. IMPROVE may override based on per-scene register / mode /
strategy. The audit trail records both the hint and the actual decision.

## World-glossary merge rules

When an entry extracted in chapter N already exists in the accumulated
state, behavior **differs by class**:

- **`places` / `organizations` / `cultural_references`** — append-only.
  Dedup on `canonical_source` (places / organizations) or
  `source_phrase` (cultural_references). First occurrence wins;
  subsequent re-introductions are silently dropped. `first_seen_chapter`
  is therefore **always the chapter that first introduced the entry**.
- **`world_terms`** — dedup on `canonical_source`. If matched:
  - `notes`: replaced if incoming is non-empty (orchestrator does not
    stitch; EXTRACTOR emits the refined notes string in full).
  - `canonical_target`: replaced only if accumulated was `null` and
    incoming is non-null (mirrors character `canonical_target` rule).
  - `first_seen_chapter` preserved (earliest wins).

Why the asymmetry? Places / organizations / cultural_references are
**discrete identifiers** — once you know "シラクサ → Syracuse", the
target is fixed. World_terms carry **register / context shading** that
genuinely refines as later chapters reveal new uses ("暴君" reading
neutral in ch1 might shade "despot" in ch5 once the political setup is
clearer); the `notes` field captures that.

## Difference from L2 (bundled glossary)

| Layer | Scope | Source | Lifecycle |
|---|---|---|---|
| L1 | Project | `<repo>/docs/i18n/glossary-*.md` | Authored by user / project |
| **L1.5** | **Per-book** | **`pre-pass/{characters, world-glossary}.json`** | **Generated per book; invalidated by `book_manifest_hash`** |
| L2 | Locale-pair | `scripts/canonical/glossary-*--*.md` | Bundled with toolkit; locale-pair generic |
| L3 | Web | search hits | Per-term ad-hoc |
| L4 | LLM | model fallback | Per-term ad-hoc |

L2 is **locale-pair generic** — "tyrant" in en-US ↔ ja-JP is captured
without book context. L1.5 is **book-specific** — "暴君 → tyrant" with
this book's register cue. When both fire, L1.5 wins because the
book-specific decision is more informed than the generic pair.

## What is NOT covered here

- **EXTRACTOR role contract** — see `protocols/character-extraction.md`
  §"EXTRACTOR role behavioral contract". This protocol explicitly does
  NOT duplicate that section.
- **Character profiles** — `protocols/character-extraction.md`. Voice
  notes / paired-structure aliases are character-specific.
- **Scene-level scoping at runtime** — see
  `protocols/scene-window-context.md`. The pre-pass is BOOK-level; the
  runtime caller decides which L1.5 hits to surface in any given scene's
  prompt.
- **Untranslatability decisions** — `cultural_references[].handling_hint`
  is a recommendation; the actual borrow/explain/approximate decision is
  recorded by the I1 untranslatability gate (see
  `references/verification-gates.md`).

## See also

- `scripts/lib/world_glossary_extractor.py` — implementation source-of-truth
- `scripts/lib/glossary.py` — `lookup` with L1.5 tier integration
- `scripts/canonical/prompts/extract-world-glossary.md` — canonical
  EXTRACTOR prompt (frontmatter + body)
- `references/prompt-extract-world-glossary.md` — distributed functional copy
- `protocols/character-extraction.md` — companion protocol; canonical
  owner of the EXTRACTOR role contract
- `protocols/scene-window-context.md` — runtime consumer of L1.5 hits
- `references/glossary-resolution-spec.md` — full L1 → L4 resolution order
- `references/verification-gates.md` — I1 untranslatability gate
