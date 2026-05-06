# Novel quality checklist — 6-item roundtrip

> Run after Layer 5 reassemble (per-scene v2 concatenation), before emit.
> Any unchecked item halts the run with a clear actionable message; do not
> silently degrade.
>
> All six items run in one pass over the assembled chapter target plus the
> recorded scene-boundary metadata. None require an additional LLM call —
> they're cheap byte-equality / count / lookup checks.

## The 6 items

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
      dropped. The chunker's round-trip contract (per
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

## When to run

| Step | Items |
|---|---|
| Immediately after Layer 5 scene-v2 concatenation, before emit | 1, 2, 3, 4, 5, 6 |

All six items run in one pass after assembled-chapter target is built —
none require a separate LLM call.

## What this checklist does NOT cover

- **Placeholder count parity** — that's M1 (`references/verification-gates.md`
  §M1). M1 runs per-scene before this checklist; if M1 fails the run
  halts before reassemble, so this checklist never sees a placeholder-
  count mismatch. (For prose-only novels with protect-pass off, M1 is a
  no-op — there are no `⟦P:NN⟧` tokens to count.)
- **Per-scene glossary compliance** — that's M2 (HARD). Item 5 in this
  checklist is the **chapter-level** double-check across scenes.
- **Translation quality** — that's the 4D reflection axes
  (`references/4d-reflection.md`) and the S1 / S2 SHOULD gates per
  scene.
- **Markdown AST structure** — novel mode does not parse the chapter
  as markdown AST (per `SKILL.md` Layer 2). Code blocks / math / mermaid
  / frontmatter checks live in `translation-doc/checklists/doc-quality-
  checklist.md`.
- **Cross-chapter character-arc consistency** — Tier 2 deferred from
  v0.2.0. Within a chapter, item 5 catches name drift; across chapters
  the project glossary + caller workflow is the safety net.

## See also

- `protocols/scene-chunking.md` — round-trip contract (items 1, 2, 4)
- `protocols/scene-window-context.md` — prev/next window truncation rules (item 6)
- `references/verification-gates.md` §M1 / §M2 — placeholder + glossary
  gates that run before this checklist
- `references/audit-trail-spec.md` — where checklist results are
  recorded on a halt
