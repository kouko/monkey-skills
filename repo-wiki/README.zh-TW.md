# repo-wiki

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 把 Karpathy 的 LLM Wiki Pattern 套到 code repo。隱藏的 `.repo-wiki/` 知識庫由 src/ 完整目錄掃描（每個 module 都有 entity stub）+ 每 module 最近 5 commits + 90 天 bounded global git scan seed。從變更與對話中成長，用自然語言 query。`src/` 永遠是當前狀態的權威 — wiki 在關鍵時刻自動 verify cache。

**Version**: 1.1.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## 背景

AI coding 工具只在單一 session 內理解 codebase。下次 session 從零開始。既有解法分兩極：

- **SaaS 語意搜尋**（Greptile、DeepWiki、Cursor @Codebase）— 程式碼離開機器、知識不在 repo 裡
- **平鋪 Markdown context**（CLAUDE.md、AGENTS.md、Memory Bank）— 全文注入、repo 大則 token 爆炸、沒有合成的 WHY

`repo-wiki` 補上這個空缺：**持久化在 repo 裡、合成過的知識**，AI agent 可 query 而不需全文注入、不需 SaaS 依賴。

[Karpathy LLM Wiki Pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 對應到 code repo：

```
raw/      (general wiki)  →  src/**       (code repo)
wiki/     (general wiki)  →  .repo-wiki/  (code repo)
ingest    (general wiki)  →  /repo-wiki:ingest
query     (general wiki)  →  /repo-wiki:query
```

## Skills

| Skill | 何時用 | 主要輸入 |
|---|---|---|
| [`/repo-wiki:init`](skills/init/) | 每個 repo 一次（重跑安全） | Phase 1：`git ls-files`（src/ 完整目錄）+ 每 module 最近 5 commits。Phase 2：90 天 global git scan（最多 50 commits / 15 source pages）。Phase 3（`init full-history` opt-in）：era 分組完整歷史 backfill。 |
| [`/repo-wiki:ingest`](skills/ingest/) | 完成有意義變更後 OR 想捕捉 context 時 | 自上次 ingest 起的 git diff、文字 arg、或檔案路徑 |
| [`/repo-wiki:query`](skills/query/) | 想問 codebase 任何問題時 | `.repo-wiki/index.md` + 相關頁面，關鍵時刻自動讀 `src/` 驗證 |

## 快速上手

從 [monkey-skills marketplace](https://github.com/kouko/monkey-skills) 安裝後：

```bash
# 在你的 repo 根目錄，第一次：
/repo-wiki:init

# 完成下一個 feature 後：
/repo-wiki:ingest

# 問 codebase 任何問題：
/repo-wiki:query "AuthModule 是怎麼運作的？"
```

`init` 會 scaffold `.repo-wiki/`（含 `SCHEMA.md` + `index.md` + `log.md` + `overview.md`），掃描整個 src/ 目錄建立完整 entity 覆蓋（每個偵測到的 module 都建 stub：`paths` + `Common Entry Points` + 最近 5 commits 作為 `Recorded Decisions` seed），接著跑 90 天 bounded global git scan 產生跨模組變更的 source page。同時在 `CLAUDE.md` 寫入一個小的 idempotent 區塊，讓未來的 session 知道 `.repo-wiki/` 是 AI 擁有的。

`init` **重跑安全**：保留 `log.md` 歷史、ingest 累積的 entity 段（`Responsibility`、`Architecture Snapshot`、`Gotchas`、`Dependencies`）、`overview.md` 的 `## Repository` 自定義段。重跑只 refresh init-owned 資料（paths、entry points、seeded 最近 commits），用 `log.md` 的 last commit SHA 增量處理新 commit。

**預設模式**（`/repo-wiki:init`）涵蓋實用 80%：完整當前狀態 + 最近活動。**完整歷史模式**（`/repo-wiki:init full-history`，也可用 `"full backfill"` / `"完整歷史"`）加上 Phase 3：era 分組（6 個月一段）的歷史性 major commit backfill。Era pages 不受 15-page Phase 2 cap 限制。

**init 永遠不讀**：src/ 任何檔案內容。只用 `git ls-files` 路徑、entry-point 檔案路徑、`git log` metadata。維持 WHY-not-WHAT 原則，跟 Greptile/DeepWiki 風格的 code 摘要工具區隔。

## ingest 是多態的

同一個 skill 從 arg 自動判斷三種輸入模式：

```bash
# Git mode（預設）— 從上次 ingest 的 commit SHA 開始增量處理
/repo-wiki:ingest

# Context mode — 捕捉沒進 commit 的 tribal knowledge
/repo-wiki:ingest "AuthModule 命名怪是因為 2020 年從 old-auth-service migration 過來"

# Doc-import mode — 匯入外部設計文件（**需要明示 import marker**）
/repo-wiki:ingest "import design doc: docs/architecture/postgres-decision.md"
```

文字裡**有提到路徑但沒有 import marker**（`import`、`import doc`、`讀取`、`匯入`、`読み込んで` 等）會留在 context mode — 避免意外讀檔。

**Volume-triggered 分類（git mode，commits ≥ 5）**：當 ingest 跨越大量 commits（例如停一個月後 catch-up），commits 會做 entropy 分類——HIGH（動到 config / 跨模組 / `feat`/`refactor` / 新增 top-level 目錄）獨立成 source page；MEDIUM（`fix`+ 本文 / 動到多 entity）依檔案重疊度批次；LOW（純 test / 純 docs / `chore`）合併成 roll-up。Source-page 預算是 `min(15, ceil(commits/5))`。少量 ingest（commits < 5）跳過分類，產出單一 page——保留 v1.1 在「做完 feature 順手 ingest」場景的行為。

## `.repo-wiki/` 是 AI 擁有，但 `src/` 才是當前權威

最重要的設計決策：**`.repo-wiki/` 是 best-effort cache，不是真實的源頭**。entity page 裡的實作描述會 stale。為了讓這件事誠實，`/repo-wiki:query` 跑一個 **Eager verification** pipeline：

下列任何 trigger 命中 → query 主動讀 `src/` 比對當前行為的 claim：

| ID | Trigger |
|---|---|
| T1 | 載入的 page `last_updated > 60 天` |
| T2 | 問題包含「currently」「now」「still」「現在」「目前」「今」 |
| T3 | 答案會用來寫新 code（action 動詞 OR 最近有 Edit/Write） |
| T4 | 載入的 source page 有 TODO / 「subject to change」/「待確認」 |
| T5 | 多個載入的 page 互相矛盾 |
| T6 | 純粹問過去決策（負面 trigger — skip verification） |
| T7 | User 明示要求驗證 |

Trigger 命中時，答案以 **分段格式** 呈現：

```markdown
## Verified Claims (against src/)
- AuthModule 用 jose 做 JWT signing — 已對 src/auth/jwt.ts:12 驗證

## Unverified Claims (from .repo-wiki/ cache)
- AuthModule 依賴 SessionStore — 來自 AuthModule.md，本次未驗證

## Discrepancies Found
- entity 寫 "throws AuthError" 但 src/auth/jwt.ts:42 throw 的是 JwtError
  → 建議：/repo-wiki:ingest "AuthError 已 rename 為 JwtError"
```

純決策問題（「為什麼當初選 Postgres」）不會 trigger verification — 過去決策不會回溯改變。

## 日常工作流

```
1. 完成 feature → /repo-wiki:ingest
   AI 讀 git log + diff
   → 寫 sources/2026-05-02-add-payment.md (origin: git)
   → 更新 entities/PaymentService.md
   → 必要時建立 concepts/IdempotencyKey.md
   → 更新 index.md + log.md

2. 收到 tribal knowledge → /repo-wiki:ingest "PaymentService retry 5 次因為 <原因>"
   → 寫 sources/2026-05-02-manual-payment-retries.md (origin: manual)
   → 更新 entities/PaymentService.md gotchas

3. 有問題 → /repo-wiki:query "PaymentService 的錯誤處理邏輯"
   → 讀 index.md → 載入 PaymentService entity + 近期 sources
   → trigger verification（T2 if「現在」; T1 if stale; etc.）
   → 分段答案 + src/ 指標
   → 問是否要存 synthesis
```

## 為什麼不用其他工具

| 工具 | 缺點 |
|---|---|
| Greptile / DeepWiki | SaaS、程式碼離開機器、無法離線 |
| Code-Index-MCP | 語意搜尋好，但不做 WHY 整理 |
| Roo Memory Bank | 全文注入、沒有 page type、沒有 verification |
| RepoAgent | auto-commit 知識更新（多人協作風險） |
| SamurAIGPT/llm-wiki-agent | 通用文件、不懂 git/code |
| `dev-workflow:git-memory` | 捕捉 **commit 當下** 的決策；`repo-wiki` 處理 **跨 commit 的整體架構知識** — 互補不衝突 |

`repo-wiki` 的獨特組合：**git-aware ingest + 多態 context capture + 結構化 WHY 知識 + AI-owned wiki + verification-fenced reads + 零外部依賴**。

## 設計哲學

五個原則：

1. **Synthesize at ingest time, not query time** — 知識在 ingest 時整理；query 只負責讀
2. **WHY first, WHAT is best-effort cache** — 允許實作描述但永遠不是權威
3. **Verify at key moments** — Trigger 命中時 query 讀 `src/`；分段輸出讓不確定性明確
4. **Gap is feedback** — query 找不到 page 或發現過期，會建議具體的 `/repo-wiki:ingest`
5. **Multi-source input** — git 是 default，conversational context 跟外部文件也走同一條 ingest pipeline

## Schema 在 v2.0 之前 freeze

`.repo-wiki/SCHEMA.md` 的 page type、frontmatter shape、命名規則在 v1.x 系列**不會改變**。重大 schema 改動配 migration script 一起在 v2.0 出。v1 user 不需要在 v1.x 內 plan migration。

## v2 backlog

- `knowledge/inputs/` — 正式的人類可編輯 input 區
- 多人協作 CI workflow（AI 提案，人類用 PR comment 審核）
- `/repo-wiki:lint` — 健康檢查（broken links、git-aware staleness、orphan concepts）
- `/repo-wiki:graph` — 從 markdown link 建知識圖譜
- Monorepo 支援（per-app `.repo-wiki/` 子目錄）
- AGENTS.md drop-in（vendor-neutral 散播）
- v1.x 穩定後的獨立 repo graduation

## 靈感與致謝

- [Karpathy LLM Wiki Pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — 概念源頭
- [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) — `raw/ → wiki/` 架構參照
- [llmrix/llm-wiki-skill](https://github.com/llmrix/llm-wiki-skill) — SKILL.md 實作參照
