# Character extraction — whole-book pre-pass for character profiles

> **Implementation source-of-truth**: `scripts/lib/character_extractor.py`
> (`load_book_manifest`, `build_character_extraction_prompt`,
> `parse_character_extraction_response`, `run_pre_pass_characters`).
> This protocol owns the **EXTRACTOR role contract** that
> `world-glossary-extraction.md` cross-references — read this protocol first
> if you're working with either pre-pass.
> Test fixtures live in `scripts/tests/test_character_extractor.py`.

## Pattern stack — when this protocol applies

Tier 2 of the `translation-novel` pipeline (v0.3.0+). The pre-pass runs
**once per book**, **before** the per-chapter scene-level translation loop
in `protocols/scene-window-context.md`. Output is a single
`characters.json` artifact stamped with `book_manifest_hash` so a stale
artifact (a chapter file changed after extraction) can be detected on
subsequent runs.

The pre-pass walks chapters in name-order, dispatching one EXTRACTOR
subagent per chapter with **the accumulated state of all prior chapters**
as input. Each chapter's subagent runs in **fresh context** — no
cross-context leakage between chapters except through the explicit
accumulated-state JSON the orchestrator passes in.

## EXTRACTOR role behavioral contract

> **Canonical owner**: this section is the SoT for the EXTRACTOR role
> across both `character-extraction.md` and
> `world-glossary-extraction.md`. The world-glossary protocol
> cross-references this section instead of re-stating it.

### Fresh context per chapter — no cross-context leakage

Each chapter's EXTRACTOR runs in a fresh subagent context. The agent does
NOT carry conversation memory from prior chapters; it sees only:

1. The canonical extractor prompt (role + schema + rules).
2. The intake spec (source/target locale, register, etc.).
3. The accumulated character JSON from prior chapters (rendered as
   structured input).
4. The current chapter's full text.

Why fresh context? Long-running conversations drift — the EXTRACTOR loses
discipline around the schema, starts inventing fields, mixes prior-chapter
observations into current-chapter outputs. A fresh subagent per chapter
keeps each invocation deterministic and auditable.

### Subagent dispatch contract — paths, not content

The orchestrator (`run_pre_pass_characters`) is responsible for:

- Loading the chapter file from disk.
- Rendering the EXTRACTOR prompt with the accumulated state.
- Invoking the subagent at the routed model
  (`resolve_model_for_role(model, "extractor")` — usually a cheap model
  per Decision D).
- Parsing the response.
- Merging into accumulated state.

The EXTRACTOR subagent receives a **rendered prompt string + a model
identifier**. It does NOT receive file paths to walk. This isolates the
orchestrator's I/O concerns from the subagent's reasoning concern.

### Cache invalidation contract

The artifact JSON carries `book_manifest_hash` (sha256 over joined
`filename || file_sha256`). On subsequent runs:

- If the artifact does not exist → run the pre-pass.
- If the artifact exists and the hash matches → caller MAY skip the
  pre-pass (orchestrator does not auto-skip; that's a caller decision).
- If the artifact exists and the hash MISMATCHES → orchestrator emits
  `UserWarning` via `warnings.warn(...)` and **proceeds to overwrite**.
  The caller decides whether to suppress the warning, abort, or accept
  the rerun.

The warning is the signal — never silently re-run, never silently keep
stale data.

## Character schema (Decision G)

```json
{
  "schema_version": "0.3.0",
  "book_manifest_hash": "sha256:...",
  "extracted_at": "2026-05-07T...",
  "extractor_model": "claude-haiku-4-5",
  "characters": [
    {
      "canonical_name": "メロス",
      "canonical_target": "Melos",
      "aliases": [
        {"source": "メロス", "target": "Melos"},
        {"source": "彼", "target": "he"},
        {"source": "妹の婿", "target": null}
      ],
      "voice_notes": "earnest, impulsive, friend-loyalty motif",
      "first_seen_chapter": 1,
      "last_seen_chapter": 1
    }
  ]
}
```

### Paired aliases structure

Aliases are **`{"source": ..., "target": ...}` pairs**, NOT bare strings.
Each alias may have its own target rendering — "彼" maps to "he", but
"メロス" (the canonical katakana) maps to "Melos". The L1.5 lookup
(`scripts/lib/glossary.py::_lookup_l1_5_prepass`) inspects each pair so a
hit on the alias `source` returns the alias-specific `target`.

`alias.target` MAY be `null` when the translator hasn't yet decided how
to render the alias (e.g. an honorific that depends on register decisions
made later). L1.5 lookup treats a null-target alias hit as a **miss**, so
it falls through to L2 / L3 / L4.

### voice_notes — observation, not interpretation

`voice_notes` is a single sentence capturing **observable speech traits**:
register, archaism, motifs, recurring tics. NOT subjective interpretation.

- ✅ "uses 候 archaic verb ending; addresses friend in plain form"
- ❌ "feels formal" / "seems like an old soul"

Why? The downstream WRITER consumes voice_notes to maintain register
fidelity across scenes. Observable traits are actionable; interpretive
labels are noise.

### canonical_target null semantics

`canonical_target` MAY be `null` when:
- The character's target rendering is uncertain (rare names, ambiguous
  romanization).
- The translator hasn't decided yet (multiple candidate readings).

A null `canonical_target` causes L1.5 to **miss** that character at
canonical-name-hit time, falling through to alias matching, then L2 / L3
/ L4. The translator can refine the artifact (or override via L1 project
glossary) at any time.

## Character merge rules (across chapters)

When a character extracted in chapter N already exists in the
accumulated state (matched on `canonical_name`, exact case-sensitive):

- **Aliases**: append-only. Dedup on `alias.source` (paired-structure
  collisions on the source string are dropped — first-write wins).
- **voice_notes**: replaced if incoming is non-empty. The EXTRACTOR is
  expected to emit the **refined voice_notes string in full**, not a
  delta — orchestrator does not stitch.
- **canonical_target**: replaced only if accumulated value was `null` and
  incoming is non-null (avoids overwriting a translator-confirmed
  mapping with a model guess).
- **last_seen_chapter**: max of accumulated and incoming.
- **first_seen_chapter**: min of accumulated and incoming (earliest wins).

Unmatched incoming entries are appended verbatim. Insertion order is
preserved: original characters in their original order, new characters
in chapter order.

## L1.5 integration

The `characters.json` artifact, merged with `world-glossary.json` (see
`protocols/world-glossary-extraction.md`), is passed to
`scripts/lib/glossary.py::lookup` via the `prepass_artifacts` kwarg:

```python
prepass = {
  "characters": [...],
  "world_glossary": {"places": [...], "organizations": [...],
                      "world_terms": [...], "cultural_references": [...]},
}
hit = lookup(glossary_dir, source_lang, target_lang, term,
             prepass_artifacts=prepass)
```

Resolution order: **L1 → L1.5 → L2 → L3 → L4**. L1.5 is searched first so
book-specific canonical decisions override the bundled-pair generic
glossary. L1.5 hits return `audit_path = "L1.5.character"` — the audit
trail records the tier so reviewers can trace where a translation
decision came from.

## What is NOT covered here

- **World-glossary extraction** — see
  `protocols/world-glossary-extraction.md`. World-glossary extraction
  shares the EXTRACTOR role contract above; the world-glossary protocol
  cross-references this section rather than duplicating it.
- **Per-scene glossary scoping** — see `protocols/scene-window-context.md`
  §"Glossary scope per scene". The pre-pass is BOOK-level; scoping at
  scene level is the runtime caller's job.
- **Cultural references** — handled by the `world_glossary` extractor
  under `cultural_references[]`, not by character extraction.

## See also

- `scripts/lib/character_extractor.py` — implementation source-of-truth
- `scripts/lib/glossary.py` — `lookup` with L1.5 tier integration
- `scripts/canonical/prompts/extract-characters.md` — canonical EXTRACTOR
  prompt (frontmatter + body)
- `references/prompt-extract-characters.md` — distributed functional copy
- `protocols/world-glossary-extraction.md` — companion four-class protocol
- `protocols/scene-window-context.md` — runtime consumer of L1.5 hits
- `references/glossary-resolution-spec.md` — full L1 → L4 resolution order
