---
title: Repo Wiki Ingest SKILL.md 設計
type: research
date: 2026-05-02
tags:
  - SKILL-md
  - repo-wiki
  - knowledge-base
  - ingest
  - git
status: draft
reference: https://github.com/SamurAIGPT/llm-wiki-agent
---

# Repo Wiki Ingest SKILL.md 設計

> [!abstract] 這個檔案是什麼
> 這是 `repo-wiki/skills/ingest/SKILL.md` 的設計稿。
> Ingest 是知識庫成長的主要管道，**多態接收三種輸入**：git diff（自上次起的新 commit）、conversational context（user 直接講）、document import（指定外部檔案）。
>
> 核心原則：**文件是給 AI 看的，人類用 `/repo-wiki:query` 詢問就好。**

---

## 設計脈絡

決策 8 拍板：v1 ingest 多態接收輸入，避免 user 撞「git 抓不到的知識怎麼進得去」的牆。

決策 12：ingest 在 git mode 是 idempotent 的——讀 log.md 取上次 SHA，只處理新 commit。

決策 9：page 建立用描述性 heuristic，不寫硬數字。

---

## SKILL.md 完整內容

把以下內容存為 `repo-wiki/skills/ingest/SKILL.md`：

````markdown
---
name: ingest
description: |
  Use when: updating the knowledge base after code changes, capturing
  tribal knowledge, or importing external design documents. Triggers on
  "update knowledge", "ingest changes", "capture context",
  "remember that <X>", "import this doc", "/repo-wiki:ingest".
  Do NOT trigger for: first-time setup (use /repo-wiki:init),
  answering questions (use /repo-wiki:query).
---

# Repo Wiki — Ingest Workflow

The .repo-wiki/ directory is owned entirely by repo-wiki skills.
Source layer (src/**) is immutable — never modify code files.

## Prerequisite Check

Read `.repo-wiki/index.md`. If it does not exist:
> "Knowledge base not initialized. Run /repo-wiki:init first."
Exit cleanly.

## Step 0: Mode Dispatch

Detect input mode from the user's invocation using this **exact dispatch
algorithm** — do not infer mode from heuristics outside this list:

### Dispatch algorithm

1. **No argument** → `git` mode
2. **Explicit import marker present** AND **valid path resolvable** → `doc-import` mode
3. **Otherwise** → `context` mode (default for any non-git arg, even if
   the arg mentions a path)

### Explicit import markers (case-insensitive)

doc-import mode requires one of these markers in the argument. Without
a marker, even an argument containing a real path is treated as context.

| Lang | Markers |
|---|---|
| EN | `import`, `import doc`, `import the doc at`, `from file`, `from this doc`, `read this doc`, `ingest doc`, `ingest the doc at`, `the doc at` |
| JP | `読み込んで`, `インポート`, `この doc を取り込んで`, `この設計書を` |
| ZH | `匯入`, `讀取`, `import`, `這個文件`, `這份設計`, `把這個文件` |

### Path extraction

When an import marker is present, extract the path:

1. Look for tokens after the marker (e.g., `import doc: <path>`)
2. Path token criteria: contains `/` OR ends in known doc extension
   (`.md`, `.txt`, `.rst`, `.adoc`, `.pdf`, `.org`)
3. Verify path exists (`fs.existsSync` or equivalent)
4. If verification fails → ask user: "I see an import marker but
   couldn't find the file at `<extracted-path>`. Did you mean a
   different path?"

### Examples

**doc-import mode** (marker present + valid path):
- `/repo-wiki:ingest "import design doc: docs/postgres.md"` → ✓
- `/repo-wiki:ingest "讀取 docs/auth-design.md 做為設計參考"` → ✓
- `/repo-wiki:ingest "import the doc at /Users/kouko/notes/foo.md"` → ✓

**context mode** (no marker, even when path mentioned):
- `/repo-wiki:ingest "AuthModule's gotcha is documented in /Users/x/notes/foo.md"` → context
- `/repo-wiki:ingest "remember that auth.ts has a comment saying X"` → context
- `/repo-wiki:ingest "the file src/auth/jwt.ts handles validation"` → context

**git mode**:
- `/repo-wiki:ingest` (no arg) → git

**Ambiguous → ask user**:
- Marker present but multiple candidate paths in arg → ask which one
- Marker present but no path token found → ask for path

### Why explicit-marker required

Without a marker, mentioning a path is not the same as importing it.
Defaulting to context mode for path-mentioning text avoids accidental
file reads. Users intending doc-import learn the marker once; users
intending context capture never trip into doc-import unintentionally.

## Step 1: Gather Input

### Git mode
- Read `.repo-wiki/log.md`, find the last `init` or `ingest:git` entry
- Extract the recorded `last commit SHA`
- Run `git log <last_sha>..HEAD --oneline --stat`
- If empty: print "No new commits since last ingest" and exit
- If present: capture commits + paths for downstream processing

### Context mode
- The argument text IS the input payload
- Optionally let the user expand it through follow-up dialog if it's a
  short note that needs context

### Doc-import mode
- Extract the file path from the argument
- Verify file exists; if not, ask for correct path
- Read the full file content as input payload

## Step 2: Read Current Wiki State

Read `.repo-wiki/index.md` (catalog) and `.repo-wiki/overview.md`
(architecture summary) to ground the new input in existing structure.

## Step 3: Create Source Page

Filename and frontmatter vary by mode:

### Git mode → `.repo-wiki/sources/YYYY-MM-DD-<slug>.md`

```markdown
---
title: "<Short description of change>"
type: source
origin: git
date: YYYY-MM-DD
commits: ["<sha>", "<sha>"]
modules_affected: ["auth", "api"]
---

## What Changed
2-4 sentences synthesizing the batch.

## Key Decisions
- Decision and reason (extract from commit message bodies)
- Alternative considered, if any

## Connections
- [EntityName](../entities/EntityName.md) — how this change affected this module
- [ConceptName](../concepts/ConceptName.md) — pattern this implements/changes

## Contradictions / Breaks
- (Optional) Breaks [ConceptName](../concepts/ConceptName.md)'s assumption about X
```

### Context mode → `.repo-wiki/sources/YYYY-MM-DD-manual-<slug>.md`

```markdown
---
title: "<Topic of context capture>"
type: source
origin: manual
date: YYYY-MM-DD
captured_via: ingest-context-mode
---

## Context
<The user-supplied text, lightly cleaned but preserving wording>

## Why This Matters
<1-2 sentences: where this knowledge belongs in the codebase>

## Connections
- [EntityName](../entities/EntityName.md) — entity this context refines
- [ConceptName](../concepts/ConceptName.md) — pattern this context illuminates
```

### Doc-import mode → `.repo-wiki/sources/YYYY-MM-DD-doc-<slug>.md`

```markdown
---
title: "<Document title>"
type: source
origin: doc-import
date: YYYY-MM-DD
source_path: <path/to/imported/file>
source_mtime: <file mtime>
---

## Summary
2-4 sentences capturing the document's main thesis.

## Key Decisions / Claims
- Decisions or claims relevant to the codebase

## Connections
- [EntityName](../entities/EntityName.md) — entity affected by this doc
- [ConceptName](../concepts/ConceptName.md) — pattern this doc establishes
```

## Step 4: Update or Create Entity Pages

For each module/service the input touches:

- If entity page exists (`.repo-wiki/entities/<ModuleName>.md`): update relevant
  sections (Gotchas, Dependencies, Related Decisions). Update
  `last_updated` and append the new source slug to `sources` frontmatter.
- If entity page does NOT exist: create one ONLY IF the module is
  meaningfully load-bearing across multiple sources. Use judgment, not a
  hard count — but err toward not creating skeletal pages from a single
  isolated change.

**`paths:` maintenance (critical for query verification — Decision 13)**:
- Git mode: if commits in this batch added new files in this module's
  area, append the new path to `paths:`. If commits renamed/moved a
  tracked path (`git log --diff-filter=R --name-status`), update `paths:`
  accordingly. If a path was deleted, remove it from `paths:`.
- Context / doc-import modes: if user input mentions a specific
  src/ path that doesn't appear in `paths:`, ask: "Should I add
  <path> to <EntityName>'s paths?" before adding.

**Entity name derivation**: apply the **Entity Name Normalization Rule**
in SCHEMA.md to derive entity name from the primary path. This MUST
match what init produces — init and ingest using the same rule guarantees
no duplicate-named entities.

Before creating a new entity, check whether an entity with the same name
(per the normalization rule) already exists. If yes → update that one,
do NOT create a new file. If you detect that two distinct paths would
normalize to the same name (collision), append a disambiguator from the
stripped prefix (e.g., `Auth` from `src/auth/`, `LibAuth` from `lib/auth/`).

Entity page format:

```markdown
---
title: "<ModuleName>"
type: entity
tags: []
sources: ["<source-slug-1>", "<source-slug-2>"]
last_updated: YYYY-MM-DD
paths:
  - src/auth/
  - src/middleware/auth.ts
---

## Responsibility
What this module does and — critically — what it does NOT do.
(Best-effort cache; src/ is authoritative — query verifies at key moments.)

## Architecture Snapshot
Key classes / services / entry points and their relationships.
Write WHY, not WHAT. Code speaks for itself; docs explain intent.

## Gotchas & Non-Obvious Design
- Why X is named Y (if confusing)
- Historical constraints that still apply
- Easy misuse patterns

## Common Entry Points
Functions / classes that an LLM will most often need to find.

## Dependencies
- Depends on: [OtherModule](OtherModule.md)
- Depended on by: [AnotherModule](AnotherModule.md)

## Related Decisions
- [ConceptName](../concepts/ConceptName.md) — pattern that governs this module
```

## Step 5: Update or Create Concept Pages

Same descriptive heuristic: if input introduces / modifies / violates a
pattern that is meaningfully cross-cutting, update or create the concept
page. Avoid creating concepts for one-off decisions.

```markdown
---
title: "<PatternName or DecisionName>"
type: concept
tags: []
sources: ["<source-slug>"]
last_updated: YYYY-MM-DD
---

## Summary
One paragraph: what this pattern/decision is and why it exists.

## When to Apply
- Apply when: ...
- Do NOT apply when: ...

## Canonical Example
[EntityName](../entities/EntityName.md) — implements this pattern in X way.

## Known Violations / Exceptions
- [EntityName](../entities/EntityName.md) violates this because of legacy constraint Y
```

## Step 6: Update Index, Log, Overview

### index.md

Append any newly created pages under the right section.

### log.md

Append a new entry. Mode is encoded in the operation name:

```
## [YYYY-MM-DD] ingest:git | <description>
- Commits: <sha range>
- Last commit SHA: <new HEAD sha>   ← critical for next ingest
- Sources created: .repo-wiki/sources/<slug>.md
- Entities updated: <list>
- Concepts updated: <list>
```

```
## [YYYY-MM-DD] ingest:manual | <topic>
- Source: .repo-wiki/sources/<slug>.md
- Entities updated: <list>
- Concepts updated: <list>
```

```
## [YYYY-MM-DD] ingest:doc-import | <doc title>
- Imported from: <source_path>
- Source: .repo-wiki/sources/<slug>.md
- Entities updated: <list>
- Concepts updated: <list>
```

### overview.md

Update only if the input changed something architecture-level (new module
added, major refactor, removed subsystem). Routine ingests do NOT touch
overview.md.

## Step 7: Validation + Summary

Before finishing:
- Verify every link added today points to a page listed in index.md
- Print summary:
  ```
  ✓ Ingest (mode: <git|manual|doc-import>) complete.
    - Source page: <path>
    - Entities updated: <list>
    - Concepts updated: <list>
    - Overview updated: <yes|no>
  ```

## Rules

NEVER:
- Modify any file under src/
- Delete .repo-wiki/ pages (only update or append)
- Auto-ingest without explicit user invocation
- Copy-paste code into knowledge pages (describe intent, not implementation)
- Use `[[wikilinks]]` — only standard markdown links: `[Name](path)`
- Forget to record the new HEAD SHA in log.md (git mode) — it breaks
  the next ingest's idempotency

ALWAYS:
- Write WHY not WHAT
- Update log.md on every operation, with mode-specific entry format
- Keep entity pages module-bounded (one module = one entity page)
- Use descriptive judgment for page creation, not numeric thresholds
````

---

## 設計筆記

> [!tip] 為什麼三種模式共用同一個 skill
> 三種 mode 的下游 pipeline 完全相同：寫 source page → propagate 到 entity/concept → update index + log。
> 唯一差別是 input 從哪來。一個 skill 包三種 input 反而比三個小 skill 各自實作一份 pipeline 簡潔。

> [!important] log.md 的 last commit SHA 是 idempotency 的關鍵
> Git mode 必須在 log.md 寫下這次 ingest 處理到的 HEAD SHA。下次 ingest 才能精準從那個 SHA 之後跑。
> 如果 LLM 寫 log.md 時忘了 SHA，下次 ingest 會找不到 anchor，可能整段重跑或漏跑——所以 Step 6 的 SHA 行被列為 hard rule。

> [!warning] 不要為了滿足數字門檻硬建 entity
> 過去版本寫「模組出現於 2+ source pages 才建 entity」——LLM 會為了滿足規則去 grep 計數，慢且常常算錯（同模組不同 path、rename 過、partial match）。
> v1 改用描述性判斷：「meaningfully load-bearing across multiple changes」。LLM 從 source page 內容直觀判斷比較準確。

> [!note] Context mode 跟 git-memory 的關係
> 同 repo 的 [dev-workflow:git-memory](../../../dev-workflow/skills/git-memory/SKILL.md) 處理「commit 時的 decision context」。
> Ingest context mode 處理「沒附在 commit 上的 context」（會議結論、tribal knowledge、past incident）。
> 兩者互補：commit 時的 WHY 寫進 commit message、由 git mode 抓進來；非 commit 時的 WHY 直接 context mode 進 KB。
