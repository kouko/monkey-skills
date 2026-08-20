---
name: 2026-07-24-dbt-wiki-3-3-0-post-rename-follow-ups
description: dbt-wiki 3.3.0 — post-rename follow-ups
status: open
origin: PR for `feat-dbt-wiki-update-rename` (dbt-wiki 3.3.0, sync→update rename + `using-dbt-wiki` router + first CI); whole-branch review round-2 findings N2 and the disclosed pre-existing overage.
start: next substantive touch of dbt-wiki's `query` / `init` / `ingest` SKILL.md, or the next dbt-wiki arc — whichever comes first.
---

- Start: next substantive touch of dbt-wiki's `query` / `init` / `ingest`
  SKILL.md, or the next dbt-wiki arc — whichever comes first.
- Origin: PR for `feat-dbt-wiki-update-rename` (dbt-wiki 3.3.0, sync→update
  rename + `using-dbt-wiki` router + first CI); whole-branch review round-2
  findings N2 and the disclosed pre-existing overage.
- What: (a) **Demotion-stale sibling cross-refs** — six references still name
  `/dbt-wiki:rescan` as the action for "wiki is stale / dbt changed", which
  now contradicts rescan's own narrowed description and the router's
  "`update` is the whole answer": `skills/query/SKILL.md:233,244,343,377`,
  `skills/init/SKILL.md:1136`, `skills/ingest/SKILL.md:16`. They survived
  every rename sweep because they contain no `sync` token — only the
  DEMOTION makes them stale, which no grep for the old name can see. Point
  them at `/dbt-wiki:update`, keeping rescan named as the cheap alternative
  where LLM cost is the stated concern. (b) **`skills/init/SKILL.md` is
  ~6,435 words**, over the repo's ~4,500-word soft cap — pre-existing,
  unrelated to the rename arc; folding a large prose refactor into that
  branch would have been scope creep. Needs its own extract-to-references
  pass.
