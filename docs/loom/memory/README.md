# loom family practice-memory store

> Repo-native home for distilled loom-* practices, habits, processes,
> and recurring gotchas — knowledge not bound to a single commit that
> must travel with the repo (any machine, any host, headless agents).
> One fact per file. Machine-local Claude memory keeps only pointers
> here — this folder is the durable truth (versioned, host-agnostic,
> greppable). Stale facts are deleted, not archived — git history is
> the archive.

## Charter — jurisdiction

| Knowledge shape | Home |
|---|---|
| Open item / debt / re-trigger | `docs/loom/BACKLOG.md` (cross-plugin) or plugin README §parked (local) |
| Decision bound to a commit | git-memory trailers (`Decision:`) |
| Distilled practice / habit / process / recurring gotcha | **`docs/loom/memory/`** (this store) |
| One-off event artifact | `docs/loom/{specs,plans,audits,dogfood,research}/` |
| Harness/dcg friction (plugin-shipped) | `loom-code/.../environment-gotchas.md` — stays, NOT migrated |

**Pull, not push.** Nothing auto-loads this folder. Retrieval = read
the index below / grep on demand. This preserves the documented
anti-preload decision (`dev-workflow/skills/git-memory/SKILL.md:193-197`);
evidence: a 2026 ETH Zurich study found always-loaded auto-generated
context files reduced agent task success by ~3% and raised inference
cost by ~20% (`dev-workflow/skills/git-memory/standards/memory-conventions.md`
§Pull retrieval).

## Format — one fact per file

The file is named `<name>.md` — the frontmatter `name` slug IS the
filename, so index links never diverge from filenames.

```markdown
---
name: <kebab-slug>
description: <one-line — used for relevance decisions at pull time>
type: practice | gotcha | process
origin: <PR / session / audit reference>
---

<the fact>

**Why:** <why the behavior matters>

**How to apply:** <the operative rule, readable standalone>
```

## Index

One line per memory: `[<name>](<file>.md) — <description>`.
