# Novel quality checklist — 8-item roundtrip + pre-pass freshness + M3 surface

> Run after Layer 5 reassemble (per-scene v2 concatenation), before emit.
> Any unchecked item halts the run with a clear actionable message; do not
> silently degrade.
>
> All eight items run in one pass over the assembled chapter target plus
> the recorded scene-boundary metadata + the Layer 4 audit-trail. None
> require an additional LLM call — they're cheap byte-equality / count /
> lookup / verdict-presence checks.
>
> Items 7 + 8 were added in v0.3.0 (Tier 2). Item 7 verifies that Layer
> 1.5 pre-pass artifacts are present and not stale; item 8 verifies that
> Layer 4 surfaced an M3 verdict with all three subrule subverdicts.

## The 8 items

- [ ] **1. Scene order preserved.** The concatenated v2 sequence matches
      the source `Scene[i].index` ordering (`0, 1, 2, …, N-1`). No
      duplicate indices, no skipped indices, no reordering. The Layer 5
      reassembler is responsible for emitting in `index` order; this check
      verifies the responsibility was met. A reorder here means the
      chapter target tells the wrong story sequence — halt with the
      first index gap or duplicate.

- [ ] **2. Scene boundary text faithfully consumed.** Explicit-marker
      lines (`* * *`, `***`, `―――`, `◇◇◇`) and blank-gap whitespace
      (≥2 consecutive blank lines) that the chunker consumed on input
      MUST be re-emitted between target scenes by the reassembler — not
      orphaned inside any scene's translated body, and not silently
      dropped. Fallback sub-scenes (`boundary_type ==
      "fallback_token_fill"`) carry their preceding paragraph separator
      inside `source_text` — no boundary text is re-emitted between
      consecutive `fallback_token_fill` sub-scenes (would duplicate the
      separator). The chunker's round-trip contract (per
      `protocols/scene-chunking.md` §"Round-trip contract") guarantees
      that source `chapter_text` decomposes into `scenes + consumed
      boundaries`; the reassembler must mirror this on the target side.
      Halt if any consumed boundary string is missing from the assembled
      target or appears inside a scene's `source_text`-counterpart body.

- [ ] **3. Heading levels match.** The count and depth of `#` / `##`
      / `###` headings in the target chapter is identical to the source.
      Translated heading **text** changes; the **`#` count** must not.
      Headings are kept inside their scene by the chunker (boundary
      class `heading`) so they round-trip naturally — but the WRITER /
      REVISER could silently drop or alter the leading `#` markers. This
      check is the safety net. Surface the first source/target heading
      pair that disagrees on depth.

- [ ] **4. Paragraph breaks within scenes preserved.** Each translated
      scene's paragraph structure (single blank lines between paragraphs)
      MUST match the source scene's paragraph count. Source scene with
      4 paragraphs separated by single blank lines should produce a
      target scene with 4 paragraphs separated by single blank lines —
      not 3 collapsed paragraphs, not 5 with a spurious break. The
      DRAFT prompt's output requirements say "Preserve scene's paragraph
      breaks exactly"; this check verifies. Single blank lines inside a
      scene are paragraph separators, NOT scene boundaries (scene
      boundaries require ≥2 blank lines and are handled by the
      chunker before this checklist runs). Halt with the first source/
      target scene whose paragraph counts disagree.

- [ ] **5. Glossary compliance — character + place names (chapter-
      level).** Every M2-mandated source term in the project glossary
      renders as its mapped target form **consistently across all
      scenes** in the assembled chapter. M2 is HARD per-scene, but a
      per-scene PASS does not guarantee chapter-level consistency: scene
      N could use 「トム」 while scene N+1 uses 「トムソーヤ」 if both
      forms happen to satisfy a permissive glossary entry. This check
      iterates every project-glossary term, locates every source
      occurrence in the chapter, and asserts the corresponding target
      occurrence is byte-identical to the canonical target form across
      all scenes. Halt with the list of `(term, scene_indices, target_
      forms_seen)` triples that drift.

- [ ] **6. No truncation of scene-window leaked into output.** The
      DRAFT prompt's prev/next window sections (last ~500 tokens of
      `prev_scene_v2`, first ~200 tokens of `next_scene_source`) are
      sliced via `len(text) // _CHARS_PER_TOKEN` (codepoint-safe Python
      str slicing — never lands mid-byte). This check is a smoke check:
      assert that no `(none -- first scene of chapter)` or `(none --
      last scene of chapter)` placeholder string, and no obvious
      truncation artifact (trailing `<TRANSLATE_THIS>` / `</TRANSLATE_
      THIS>` markers, isolated H1 sections from the prompt template),
      leaked into the assembled chapter target. A WRITER that
      misunderstands the prompt and emits part of the prev/next window
      verbatim would surface here. Halt with the offending scene index
      and the leaked substring.

- [ ] **7. Pre-pass artifacts present and not stale (v0.3.0).** When
      `book_manifest` was supplied (i.e. Layer 1.5 ran), assert that
      both `<repo>/.translations/characters.json` and
      `<repo>/.translations/world-glossary.json` exist on disk and that
      each artifact's `book_manifest_hash` byte-matches the
      orchestrator's freshly-computed manifest hash for the current
      run. A mismatch means the book changed (chapter file modified,
      added, or removed) since the artifacts were produced — Layer 1.5
      already emitted a `WARN: pre-pass artifacts stale` and overwrote;
      this checklist item is the **post-Layer-5** safety net catching
      the case where the user passed `book_manifest` only on a later
      chapter and the pre-pass never re-ran. Halt with both stamped
      hashes + the freshly-computed hash. Skipped (PASS) when
      `book_manifest` was not supplied (single-chapter mode).

- [ ] **8. M3 verdict surfaced in audit-trail with all 3 subrules
      (v0.3.0).** The Layer 4 audit-trail entry for M3 MUST be present
      and MUST carry a `subrules` list of length 3 with one entry each
      for `m3a` / `m3b` / `m3c`. Every subrule entry MUST have a
      verdict (`PASS` / `WARN` / `FAIL`). This is a structural check on
      the audit-trail, not a re-evaluation of M3 — Layer 4 already ran
      M3 and either blocked emit (m3a FAIL) or recorded WARN / PASS.
      The check exists to catch implementations that silently skip M3
      dispatch on the assembled chapter. Halt with the missing subrule
      ids when subrules are short.

## When to run

| Step | Items |
|---|---|
| Immediately after Layer 5 scene-v2 concatenation, before emit | 1, 2, 3, 4, 5, 6, 7, 8 |

All eight items run in one pass after assembled-chapter target is built —
none require a separate LLM call.

## What this checklist does NOT cover

- **Placeholder count parity** — that's M1 (`references/verification-gates.md`
  §M1). M1 runs per-scene before this checklist; if M1 fails the run
  halts before reassemble, so this checklist never sees a placeholder-
  count mismatch. (For prose-only novels with protect-pass off, M1 is a
  no-op — there are no `⟦P:NN⟧` tokens to count.)
- **Per-scene glossary compliance** — that's M2 (HARD). Item 5 in this
  checklist is the **chapter-level** double-check across scenes.
- **Translation quality** — that's the 5D-literary reflection axes
  (`references/prompt-reflect-5d-literary.md`, default in v0.3.0; or 4D
  via `intake_spec.reflect_axes='4d'` per `references/4d-reflection.md`)
  and the S1 / S2 SHOULD gates per scene.
- **Re-evaluation of M3 subrule metrics.** Item 8 verifies the
  audit-trail entry's *structure* (presence + 3 subrules); it does not
  re-run `evaluate_m3()` on the assembled output. M3 already executed
  in Layer 4 and either blocked emit (m3a FAIL) or recorded its
  verdict.
- **Pre-pass content quality.** Item 7 verifies *artifact freshness*
  (file presence + manifest-hash match). It does not assess whether
  the EXTRACTOR's character/world-glossary extractions are accurate.
  Quality of pre-pass content surfaces through M2 (HARD per-scene),
  item 5 (chapter-level glossary consistency), and downstream
  translator review of `<repo>/.translations/*.json`.
- **Markdown AST structure** — novel mode does not parse the chapter
  as markdown AST (per `SKILL.md` Layer 2). Code blocks / math / mermaid
  / frontmatter checks live in `translation-doc/checklists/doc-quality-
  checklist.md`.
- **Cross-chapter character-arc consistency** beyond pre-pass artifact
  freshness. Layer 1.5's whole-book pre-pass (v0.3.0) addresses
  cross-chapter coreference at the glossary tier (L1.5 — characters /
  places / world terms unified across the book). Within a chapter,
  item 5 catches name drift; across chapters, the L1.5 artifacts +
  project glossary + caller workflow are the safety net.

## See also

- `protocols/scene-chunking.md` — round-trip contract (items 1, 2, 4)
- `protocols/scene-window-context.md` — prev/next window truncation rules (item 6)
- `protocols/character-extraction.md` / `protocols/world-glossary-extraction.md` — pre-pass contract (item 7)
- `checklists/prepass-cost-ceiling.md` — Decision E #2 cost-ceiling acceptance bar
- `references/verification-gates.md` §M1 / §M2 / §M3 — placeholder + glossary
  + deterministic linter gates that run before this checklist (item 8 verifies §M3 surfacing)
- `references/audit-trail-spec.md` — where checklist results are
  recorded on a halt
