---
name: using-dbt-wiki
description: |
  Family-entry router for dbt-wiki — the knowledge base distilled from a dbt project (manifest + compiled SQL + column lineage) into .dbt-wiki/. Use when unsure which dbt-wiki skill applies: first-time setup, bringing the wiki up to date, asking a dbt question, or certifying pages. Triggers: 'dbt wiki', 'dbt 知識庫', 'dbt ドキュメント', '不知道該用哪個 dbt-wiki', 'どの dbt-wiki を使えばいい'. Do NOT use for an Obsidian vault wiki (obsidian:using-obsidian) or a source-repo wiki (repo-wiki).
---

# Using dbt-wiki

Ask first: **"Are you setting it up, updating it, reading it, or shipping
it to someone else?"** That answer picks the skill.

`.dbt-wiki/` has two layers: an **evidence layer** (mechanical — manifest
+ sqlglot lineage, no LLM) and a **knowledge layer** (LLM-distilled
business meaning, human-certifiable). Most skills below touch one layer;
`update` is the one that keeps both current.

## Routing table

### Setup — once per project

| Skill | Use when |
|-------|----------|
| `init` | First time. Scaffolds `.dbt-wiki/` from `manifest.json` + `compiled/*.sql`. Run `dbt parse && dbt compile` first. |

### Input — record what the manifest can't know

| Skill | Use when |
|-------|----------|
| `ingest` | You want tribal knowledge on a model page — sort_key rationale, dialect gotchas, incident links. Survives every update. |

### Maintain — the main line

| Skill | Use when |
|-------|----------|
| **`update`** | **The default maintenance verb.** "Bring my wiki up to date" after dbt models changed. One pass, every mechanical step: (optional) ingest a note you brought → rescan evidence → asks before spending on a re-distill (and only for pages whose evidence changed in *meaning*) → **phantom-column lint gate** (pages citing a column their model lacks) → hands you the **`review` queue** → scorecard. It stops where human judgment starts: it never certifies a page itself. |
| `rescan` | *Advanced* — `update` runs this for you. Reach for it alone only to refresh evidence with **zero LLM cost** and defer the semantic half. |
| `redistill` | *Advanced* — `update` runs this for you. Reach for it alone only when evidence is already current and you just want the stale knowledge pages rewritten. |

### Read — the payoff

| Skill | Use when |
|-------|----------|
| `query` | Any dbt question: model structure, column lineage, config, refactor/rename impact, ingested notes. Use it **before** reading `dbt/` files. |

### Certify — human in the loop

| Skill | Use when |
|-------|----------|
| `review` | Pages start `developing` (LLM-written). A human reads and confirms → `mature`. Lists what needs review, prioritized by risk. |

### Export — hand it off

| Skill | Use when |
|-------|----------|
| `pack` | Emit a portable, warehouse-agnostic analytics Agent Skill a teammate can use with their own warehouse tool — no dbt project required. |

## Quick Start

```
dbt parse && dbt compile     ← dbt's own step, not ours; init needs its output
        ↓
init → update → query → review
        ↑
   (ingest — any time after init, whenever you have a note)
```

- **No `.dbt-wiki/` yet?** Every skill except `init` needs it to exist.
  They check on entry and send you back to `init` rather than guessing.
- **New project**: `init` (after `dbt parse && dbt compile`).
- **Models changed**: `update`. That is the whole answer — don't pick
  between `rescan` and `redistill` unless you are optimizing LLM cost.
- **Someone asks a dbt question**: `query`.
- **Trust the pages enough to rely on them**: `review` to certify.

## Not this family

- Obsidian vault notes → `obsidian:using-obsidian` (`wiki-*` skills).
- A source-code repository's wiki → `repo-wiki`.
- dbt SQL style/authoring → `dev-workflow:dbt-model-style`.
