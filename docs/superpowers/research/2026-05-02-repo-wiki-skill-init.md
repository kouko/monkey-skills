---
title: Repo Wiki Init SKILL.md 設計
type: research
date: 2026-05-02
tags:
  - SKILL-md
  - repo-wiki
  - knowledge-base
  - init
  - bootstrap
status: draft
reference: https://github.com/SamurAIGPT/llm-wiki-agent
---

# Repo Wiki Init SKILL.md 設計

> [!abstract] 這個檔案是什麼
> 這是 `repo-wiki/skills/init/SKILL.md` 的設計稿。
> `/repo-wiki:init` 在 user 安裝 plugin 後第一次跑——一次性 seed .repo-wiki base：scaffold 目錄、寫入 CLAUDE.md drop-in、用 git history 建立第一批 source pages 和 entity stubs。
>
> **v1.1 重構（2026-05-02）**：dogfood feedback 後 init 從「bounded recent activity」改為「complete current state + recent decisions」。新增 Phase 1 (src/ scan + per-module last-5 commits)，Phase 2 維持 90d 全域掃描，Phase 3 (era backfill) 改為 opt-in (`init full-history`)。Plan: [/Users/kouko/.claude/plans/immutable-growing-codd.md]，spec Decision 14 + 15。

---

## v1.1 設計脈絡（2026-05-02 更新）

v1.0 dogfood 後 user 反映「init 只取過去一定量的 git record... 但沒有針對完整的歷史 也沒有解析當前所有的原始碼」。原 90d / 50 commits / 15 source page cap 設計刻意 bounded，但實際使用後發現會漏掉**老舊但仍存在的 module**。

User 拍板折衷：**「預設 scan 整個 repo 原始碼以及每個檔案相關的少數幾個歷史；當使用者明確指定要回溯完整歷史時才做完整歷史回溯」**。

v1.1 三 phase 結構：

| Phase | 預設跑？ | 回答 |
|---|---|---|
| Phase 1 — src/ scan + 每模組 last-5 commits | ✓ | 「這 repo 有哪些 module、每個 module 最近 decision 是什麼」 |
| Phase 2 — 90d global git scan (15 page cap) | ✓ | 「最近的跨模組 / 大型變更是什麼」 |
| Phase 3 — Era-grouped 完整歷史 backfill | 只在 `init full-history` | 「歷史上的重大決策」 |

**關鍵不變**：init 仍然**不讀 src/ 任何檔案內容**（只讀 path metadata + git log）— 維持 Decision 1 (WHY first) + 跟 Greptile 區隔（Decision 14）。

---

## v1.0 原始設計脈絡

決策 2 拍板：v1 用 3 skills 架構（init / ingest / query），init 採 Level 1 強度（git history seed，不掃 src/ 內容）。

核心目標：**讓 user 第一次裝 plugin 跑完 init 就有可用的 .repo-wiki base**——不再面對空目錄、不再撞 "ingest 只抓最近一個 commit" 的死局。

> [!warning] v1.0 設計後續被 v1.1 覆蓋
> 以下 v1.0 SKILL.md 完整內容章節**已被 v1.1 重構取代**。實際 SKILL.md 以 `repo-wiki/skills/init/SKILL.md` 為準，這份 design notes 保留 v1.0 內容作為歷史脈絡參考。

---

## SKILL.md 完整內容

把以下內容存為 `repo-wiki/skills/init/SKILL.md`：

````markdown
---
name: init
description: |
  Use when: setting up repo-wiki for the first time in a repository,
  or re-seeding the knowledge base from scratch. Triggers on
  "init repo-wiki", "set up knowledge base", "seed from git history",
  "/repo-wiki:init". Do NOT trigger for: incremental updates after
  changes (use /repo-wiki:ingest), answering questions (use
  /repo-wiki:query).
---

# Repo Wiki — Init Workflow

One-time bootstrap that seeds the knowledge base from the last 90 days
of git history. After init, use /repo-wiki:ingest for incremental updates.

## Step 1: Sanity Check

```bash
# Must be in a git repo
test -d .git || { echo "Not a git repo. Aborting."; exit 1; }
```

If `.repo-wiki/` already exists, ask the user:
> ".repo-wiki/ already exists. Re-running init will:
>  - Add a new init entry to log.md
>  - Append additional source pages from the scan window
>  - Refresh entity stubs (overwriting earlier auto-generated stubs)
>
>  Continue? (yes/no)"

Abort on "no".

## Step 2: Scaffold Directory Structure

```bash
mkdir -p .repo-wiki/sources
mkdir -p .repo-wiki/entities
mkdir -p .repo-wiki/concepts
mkdir -p .repo-wiki/syntheses
```

Copy plugin templates into `.repo-wiki/`:
- `templates/SCHEMA.md` → `.repo-wiki/SCHEMA.md`
- `templates/index.md` → `.repo-wiki/index.md`
- `templates/log.md` → `.repo-wiki/log.md`
- `templates/overview.md` → `.repo-wiki/overview.md`

(Template path is the plugin's bundled `templates/` directory — resolve
relative to the SKILL.md location.)

## Step 3: CLAUDE.md Drop-in

Read or create `CLAUDE.md` in the repo root. The drop-in block is:

```markdown
<!-- repo-wiki:start -->
## .repo-wiki/ Directory

`.repo-wiki/` is managed by the repo-wiki plugin.

- Do NOT edit files in `.repo-wiki/` directly — run `/repo-wiki:ingest`
- To query the codebase: `/repo-wiki:query "<question>"`
- To re-seed from git history: `/repo-wiki:init`

Schema rules: `.repo-wiki/SCHEMA.md`
<!-- repo-wiki:end -->
```

Write rules:
- If CLAUDE.md doesn't exist: create it with just this block
- If CLAUDE.md exists but has no `<!-- repo-wiki:start -->` marker: append
- If CLAUDE.md exists and has the markers: replace the block between
  `<!-- repo-wiki:start -->` and `<!-- repo-wiki:end -->` (idempotent)

Never touch CLAUDE.md content outside the marked block.

## Step 4: Bounded Git Scan

Default window: last 90 days OR last 50 commits, whichever hits first.
User may override via natural-language arg:
- "init from last year" → 365 days
- "init last 100 commits" → 100 commit cap
- "init from 2026-01-01" → date floor

```bash
git log --since='90 days ago' --max-count=50 \
  --pretty=format:'%H|%ai|%an|%s' \
  --name-only --stat
```

Capture for each commit:
- SHA, ISO date, author, subject (the WHY signal)
- Changed paths (with insertions/deletions for size sense)

If git log is empty (brand-new repo): skip Steps 5-7, write a log entry
noting "no history to seed", and finish.

## Step 5: Logical Batching

### Initial grouping
Group commits into batches by:
- **Branch boundary**: merge commits act as separators (the merge commit
  itself goes into the batch with the larger side)
- **Time gap**: >3 days idle between consecutive commits = new batch
- **File overlap**: consecutive commits sharing >50% of changed paths
  belong to the same batch (use Jaccard similarity on path sets)

### Hard cap: 15 source pages per init

Init MUST NOT produce more than 15 source pages in a single run. If
initial grouping yields >15 batches, downsample in this order:

1. **Widen time gap**: try 7-day threshold instead of 3-day. Re-group.
2. **Widen further**: try 14-day threshold. Re-group.
3. **Hard truncate**: if still >15 after 14-day threshold, keep the 15
   batches with the most total lines changed (sum of insertions+deletions).
   Other batches' commits are summarized in a single
   `YYYY-MM-DD-init-overflow.md` source page noting "<N> additional
   batches were observed but not individually documented; re-run
   /repo-wiki:ingest after browsing to capture specific decisions."

### Edge cases
- **Empty git history**: skip Steps 5-7 entirely; log "no history to seed"
- **Only one commit**: produce exactly one source page
- **Only merge commits** (rare): treat the entire merge graph as one batch
- **Single-batch widen**: if all commits fall into one batch even with
  3-day threshold (e.g., a 90-day project with continuous daily work),
  accept the single batch — don't artificially split

For each batch, create `.repo-wiki/sources/YYYY-MM-DD-<slug>.md`:

```markdown
---
title: "<Short description, derived from leading commit subject>"
type: source
origin: git
date: <date of latest commit in batch>
commits: ["<sha>", "<sha>", ...]
modules_affected: ["<top-level-path>", ...]
---

## What Changed
2-4 sentences synthesizing the batch (from commit subjects + bodies).

## Key Decisions
- Decision and reason (extract from commit message bodies; if absent,
  state "WHY not captured in commit messages — consider /repo-wiki:ingest
  with context to add")

## Connections
- [ModuleName](../entities/ModuleName.md) — how this batch affected this module

## Notes
- Generated by /repo-wiki:init seed pass; refine via future /repo-wiki:ingest
```

## Step 6: Entity Stub Derivation

Count how many batches touched each top-level module (e.g., `src/auth/`,
`src/api/`). For modules appearing in 3+ batches, create
`.repo-wiki/entities/<ModuleName>.md`.

**Critical**: every entity MUST have `paths:` frontmatter — query uses
this for verification (Decision 13). Populate from git stat: list the
top 1-3 most-touched paths for this module.

```markdown
---
title: "<ModuleName>"
type: entity
tags: []
sources: ["<source-slug-1>", "<source-slug-2>", ...]
last_updated: <today>
paths:
  - <most-touched-path-1>
  - <most-touched-path-2>
---

## Responsibility
<Derived from path name + commit subjects. Mark uncertain claims with TODO.
Note: this is a best-effort cache. src/ is authoritative for current
behavior — query verifies at key moments per Decision 13.>

## Architecture Snapshot
TODO — refine via /repo-wiki:ingest after working with this module.

## Gotchas & Non-Obvious Design
TODO — these surface during real work; capture via
/repo-wiki:ingest "context: <observation>".

## Common Entry Points
<List 1-3 most-touched files in this module from git stat output.>

## Dependencies
TODO

## Related Decisions
<Link to source pages where this module was central.>
```

Naming: apply the **Entity Name Normalization Rule** in SCHEMA.md exactly.
Examples from that rule:
- `src/auth/` → `Auth.md`
- `src/auth/middleware/` → `AuthMiddleware.md`
- `src/utils/jwt-handler/` → `UtilsJwtHandler.md`
- `lib/email/` → `Email.md`

Init never adds suffixes like `Module` / `Service` — name is path-derived
so init and ingest produce the same name for the same path.

Stubs are intentionally skeletal — they are seeds, not complete entities.
The next /repo-wiki:ingest cycle (or context-mode capture) fills them in.
The `paths:` field, however, must be populated immediately — without it,
query verification falls back to slow grep-based discovery.

## Step 7: Overview Synthesis

Write `.repo-wiki/overview.md`:

```markdown
---
title: Codebase Overview
type: overview
last_updated: <today>
seeded_from: "git log --since='90 days ago' (N commits)"
---

## Repository
<One paragraph: pull from README.md if present; otherwise describe from
top-level directory structure.>

## Active Modules (last 90 days)
<List entity stubs created in Step 6, with one-line descriptions.>

## Recent Themes
<2-4 themes synthesized from source pages — what kinds of changes have
been happening.>

## What Lives Here vs Elsewhere
- .repo-wiki/sources/ — change history (with WHY)
- .repo-wiki/entities/ — module knowledge (currently mostly stubs)
- .repo-wiki/concepts/ — patterns / ADRs (empty after init; grows via ingest)
- .repo-wiki/syntheses/ — saved query answers (empty after init)
```

## Step 8: Index + Log

Update `.repo-wiki/index.md` to list all created pages:

```markdown
# Knowledge Base Index

## Overview
- [Overview](overview.md) — living codebase synthesis

## Sources (recent → old)
- [<date> <slug>](sources/<file>.md) — one-line summary

## Entities
- [<ModuleName>](entities/<file>.md) — one-line description

## Concepts
(none yet — created via /repo-wiki:ingest as patterns are observed)

## Syntheses
(none yet — created when /repo-wiki:query offers to save an answer)
```

Append to `.repo-wiki/log.md`:

```
## [<date>] init | seeded from last 90d
- Window: 90 days, max 50 commits (override: <if user customized>)
- Last commit SHA: <HEAD sha at scan time>
- Source pages created: N
- Entity stubs created: M
- Overview written: yes
- CLAUDE.md drop-in: <created | appended | replaced>
```

Recording the "last commit SHA" is critical — /repo-wiki:ingest uses this
to know where to start incrementally.

## Step 9: Summary Report

Print to user:

```
✓ Knowledge base initialized at .repo-wiki/

  Created:
    - N source pages (.repo-wiki/sources/)
    - M entity stubs (.repo-wiki/entities/)
    - overview.md, index.md, log.md, SCHEMA.md
    - CLAUDE.md drop-in (<created/appended/replaced>)

  Next steps:
    1. Skim .repo-wiki/overview.md and entity stubs
    2. Capture tribal knowledge:
       /repo-wiki:ingest "context: <something WHY-related>"
    3. After your next feature, run /repo-wiki:ingest

  Entity stubs are skeletal — they fill in via real work, not by guessing.
```

## Rules

NEVER:
- Modify any file under src/
- Write content into entity stubs that the LLM cannot ground in
  commit messages or path structure (don't fabricate WHY)
- Touch CLAUDE.md content outside the `<!-- repo-wiki:start/end -->` block
- Use `[[wikilinks]]` — only standard markdown links

ALWAYS:
- Bound the scan (90d / 50 commits default)
- Mark uncertain entity claims with TODO
- Record the last commit SHA in log.md (ingest needs it)
- Make CLAUDE.md drop-in idempotent
````

---

## 設計筆記

> [!important] Init 不是 ingest 的特殊形式
> Init 解 "first impression" 問題：user 裝完插件第一次跑，要立刻有 KB 可看。
> Ingest 解 "incremental update" 問題：每次有新 commit 或 context 進來增量加。
> 兩者輸入不同（init 寬窗口，ingest 自上次起），輸出 schema 相同（都產 source page、entity 更新）。

> [!tip] Entity stub 為什麼留 TODO
> Init 從 git history 推 entity 內容是「low-quality bootstrapping」——commit messages 通常只說做了什麼，少說為什麼。寫進 entity 的內容如果不確定，就誠實留 TODO，等真正的 ingest 流程（搭配 user 提供的 context）來填。
> 反例：LLM 看 path 是 `src/auth/` 就猜「This module handles authentication using JWT tokens」——這是憑空捏造，違反 WHY-not-WHAT。

> [!warning] Bounded scan 的必要性
> 5 年的 repo 不限制就會掃出幾千筆 commit、爆 token 預算。預設 90d/50 commits 是「夠看出近期 active 區域」+「不爆」的平衡。
> User 想要更深的 history 可以明確說「init from last 2 years」——這時 LLM 知道是 user 的 explicit choice，可以放手做。

> [!note] CLAUDE.md drop-in 的 idempotent 設計
> User 可能會：
> 1. 第一次 init → 建 CLAUDE.md
> 2. 隔天手動編 CLAUDE.md 加自己的東西
> 3. 一週後 re-init（譬如試新版 plugin）
>
> Step 3 的 marker-replace 邏輯保證第 3 步只動 marker 之間的部分，user 的自訂內容安全。
