# Stage 3 — Zettelkasten linking + INDEX

## Goal

Make the relations between atomic skills explicit, forming a navigable
network rather than a heap of isolated files.

## Three relation types

1. **`depends-on`**: A presupposes understanding of B
   - Example: "checklist-driven decision" depends on "multi-mental-models"
     (because the checklist's items are sourced from those models)

2. **`contrasts-with`**: A and B are alternative options; choice depends
   on context
   - Example: "forward-reasoning" contrasts-with "inversion-thinking"

3. **`composes-with`**: A and B are typically used together
   - Example: "circle-of-competence-judgment" composes-with
     "margin-of-safety"

## Execution steps

1. Enumerate all skills produced in Stage 2.
2. Pairwise scan; identify if any of the three relation types apply.
3. Populate the `related_skills` frontmatter on each `SKILL.md`:
   ```yaml
   related_skills:
     - slug: multi-mental-models
       relation: depends-on
     - slug: forward-reasoning
       relation: contrasts-with
   ```
4. Append a "Related skills" section to the body of each `SKILL.md`,
   describing the relation in natural prose (in source book language).
5. Generate `<distill-dir>/INDEX.md` from
   `templates/INDEX.md.template`.

## What INDEX.md must include

- Book's basic info (title / author / year / one-line thesis)
- Skills grouped by topic
- Reference graph (mermaid `flowchart` or `graph`)
- Recommended learning order (derived from `depends-on` topology)

## Discipline: do NOT manufacture relations

If two skills genuinely have no `depends-on` / `contrasts-with` /
`composes-with` connection, leave `related_skills` empty.

**Sparse > fake-linked.**

Empirical heuristic: a 10-skill book usually has 8-15 real relations.
< 5 means atomization went too far (units may be wrong); > 25 means
you're stretching connections.

## Output language

- `related_skills` YAML field names — English
- `slug` values — English (matches the `name` of the target skill)
- `relation` values — English (controlled vocabulary: `depends-on` /
  `contrasts-with` / `composes-with`)
- "Related skills" prose section in body — match source book language
- INDEX.md headers (`## Skills by topic`, etc.) — English
- INDEX.md per-skill description — match source book language
- mermaid graph node labels — English slug for stability

## Trilingual glossary (Stage 3 — Zettelkasten linking)

Source: Sönke Ahrens *How to Take Smart Notes* — JP edition 『TAKE NOTES!』
日経BP 二木夢子 訳 / TW edition 《卡片盒筆記》遠流.

| English | 日本語 | 繁體中文 | Note |
|---|---|---|---|
| Zettelkasten | ツェッテルカステン | 卡片盒筆記法 | (loanword in JP — no native term) |
| atomicity | 原子性 | 原子化 | Ahrens |
| linking | リンク（する） | 連結 / 建立連結 | Ahrens |
| permanent note | 永久保存メモ | 永久筆記 | Ahrens |
| literature note | 文献メモ | 文獻筆記 | Ahrens |
| fleeting note | 走り書きメモ | 靈感筆記 | Ahrens |
| depends-on | 前提とする | 依賴 | relation type |
| contrasts-with | 対比される | 對比 | relation type |
| composes-with | 組み合わせる | 組合 | relation type |
| reference graph | 参照グラフ | 引用圖 | |
