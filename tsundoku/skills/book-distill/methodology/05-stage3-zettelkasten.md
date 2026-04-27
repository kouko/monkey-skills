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

## Trilingual glossary

| English | 日本語 | 繁體中文 |
|---|---|---|
| depends-on | 前提とする | 依賴 |
| contrasts-with | 対比される | 對比 |
| composes-with | 組み合わせ | 組合 |
| reference graph | 参照グラフ | 引用圖 |
| atomization | 原子化 | 原子化 |
