---
title: wiki-ingest zero-prompt default + oldest-first auto-batching — design
date: 2026-05-17
status: design-approved
target_skill: obsidian/skills/wiki-ingest
target_branch: feat/wiki-ingest-zero-prompt-oldest-first
upstream_spec: ~/kouko-obsidian-vault/research/2026-05-17 wiki-ingest 預設行為改造——oldest-first auto-batching 設計筆記.md
brainstorming_skill: code-toolkit:brainstorming
---

# wiki-ingest zero-prompt default + oldest-first auto-batching — design

本 design doc 接續 vault 內的設計筆記（`upstream_spec` frontmatter），補上 4 個未拍板的架構決定 + commit 切分 + 測試/檔案配置。**設計筆記是 source of truth for product behavior**；本 doc 是 source of truth for implementation architecture。

## Problem

跑 catch-up `/wiki-ingest` 時被 STEP 1 的 `AskUserQuestion` 三選一打斷，但只想要「直接跑、按時間順序補齊歷史」。長尾 vault（4508 NEW，最舊 2018-08-30）每次都得手動選 scope + cap 處理方式，認知負擔過高；若每次選「最近的研究」則 wiki 變成最近偏見、舊筆記永遠不會被 ingest。

JTBD（Klement format）：
> *When* I run `/wiki-ingest` on a vault with thousands of un-ingested notes,
> *I want* the skill to auto-pick a sensible batch and proceed,
> *so I can* keep the wiki current without per-run scope micro-management.

## Users

kouko（vault 已累積 4508 NEW；熟悉流程，AskUserQuestion 是雜訊）。其他 monkey-skills obsidian plugin 使用者亦適用，但設計以 kouko's vault 為實證 dogfood 標的。

## Smallest End State

`/wiki-ingest`（無參數）= zero-prompt → whole-vault delta → 按 oldest-first 取 cap 跑 → STEP 6 報告含「下一批預告」。Scope/order 可被 prompt hint（path / 單檔 / `latest|oldest|backfill`）或 config (`OBSIDIAN_WIKI_BATCH_ORDER`) override。Topic word（無 path/無 time-keyword）→ topic filter on filename + frontmatter。

## Current State Evidence

- **Forward**：`obsidian/skills/wiki-ingest/SKILL.md:45-65` STEP 1 現況 — `AskUserQuestion` 三選一（whole vault / specific path / research only）+ 含糊的 cap 處理（"ask user to confirm or batch"）。
- **Reverse**：`obsidian/skills/wiki-ingest/SKILL.md:67-85` STEP 2 — 已有 `NEW/MODIFIED/UNCHANGED` summary + `Cap: N pages per run` 行 + `Proceed?` gate。
- **Error**：`obsidian/skills/wiki-ingest/SKILL.md:96-101` Auto-research gate — `frontmatter.status` decision tree；本次設計 CC-15 必須對接此 gate（topic filter 後仍要過此 status check）。
- **Data**：`obsidian/skills/wiki-ingest/references/delta-tracking.md:1-30` — MODIFIED 語意 = SHA-256 hash 不同（content-based，idempotent）。Manifest schema：`{sha256, last_ingested, wiki_pages}` per source。
- **Boundary**：`obsidian/skills/wiki-ingest/scripts/scan-vault.sh` — 既有，emit 絕對路徑一行一個；POSIX-portable；auto-sources `.obsidian-wiki.config`。本次設計透過 stdin 接力到新 `select-batch.py`。
- **Plugin layout**：`obsidian/` 目前**無 tests/ 資料夾**；其他 plugins（code-toolkit / legal-toolkit / investing-toolkit）已用 pytest。

Evidence paths appendix：
- `obsidian/skills/wiki-ingest/SKILL.md`
- `obsidian/skills/wiki-ingest/scripts/scan-vault.sh`
- `obsidian/skills/wiki-ingest/references/delta-tracking.md`
- `obsidian/skills/wiki-ingest/references/source-scope.md`
- `obsidian/skills/wiki-setup/SKILL.md`

## Decision — architecture deltas from spec

### §1 STEP 結構（新）

| STEP | 變動 |
|---|---|
| Pre-flight | 不變 |
| **STEP 1** Determine ingest scope | **行為換掉**：取消 `AskUserQuestion` default；Claude 讀 user 最近 message + decision table → `(scope, order, source)` 三元組；印一行 summary |
| **STEP 2** Scan and hash | **微擴**：scan-vault.sh + 可選 topic filter → SHA-256 → bucket NEW/MODIFIED/UNCHANGED |
| **STEP 3** Select batch | **新增**：呼叫 `scripts/select-batch.py` → sort NEW+MOD by date → 取 cap → emit `(batch, remaining)` JSON |
| **STEP 4** Per-source ingest loop | 編號 shift（原 STEP 3），內文不動 |
| **STEP 5** Update hot.md | 編號 shift（原 STEP 4） |
| **STEP 6** Report + 下一批預告 | 編號 shift（原 STEP 5）+ 末段加 1 行預告 |

Rationale：乾淨分離 recon（hash+bucket）與 decision（sort+cap）。`batching-policy.md` 命名為 STEP 3 的 reference 才名正言順。

### §2 STEP 1 — Decision table

Claude 讀 user 最近一條 message，套以下表格：

| Prompt 模式 | scope | order |
|---|---|---|
| 純 `/wiki-ingest` | whole_vault | from config（default `oldest-first`） |
| Path（含 `/` 的 token，如 `research/`） | path | from config |
| 單檔（`.md` 結尾） | single_file | n/a（不分批） |
| 時間關鍵字：`latest` / `recent` / `newest` / `最新` / `近期` | whole_vault | newest-first（**本次 override**） |
| 時間關鍵字：`oldest` / `backfill` / `最舊` / `從頭` / `舊筆記` | whole_vault | oldest-first（**本次 override**） |
| Topic word（無 path、無 time-keyword、非單檔） | whole_vault + `topic_filter` | from config |

**判定規則細節**：
- *Path*：token 含 `/` 且不以 `.md` 結尾（e.g. `research/`、`investing/2026/`）
- *單檔*：token 以 `.md` 結尾（路徑或單純 basename 皆可）
- *時間關鍵字*：對 token 做 case-insensitive substring match（ASCII keyword）+ 直接相等（CJK keyword，無大小寫概念）
- *Topic word*：上述都不符且 token 非空 → 視為 topic substring filter，case-insensitive（ASCII）

STEP 1 first-line summary：

```
Scope: <whole_vault | path:<p> | single_file:<f>>  (filtered by topic '<t>' if any)
Order: <oldest-first | newest-first>
Source: <config | prompt hint | default>
```

使用者看到後可 Ctrl+C 中斷再 re-run with explicit hint；否則默默走下去。**取代** spec risk 表第 1 列（scope hint 誤判緩解）。

### §3 `scripts/select-batch.py` — 契約

```
INPUT
  stdin                  vault-relative candidate paths, one per line
  env BATCH_ORDER        oldest-first | newest-first      (commit 1: hardcoded oldest-first)
  env BATCH_CAP          int (default 15)
  env MANIFEST_PATH      <vault-root>/wiki/.manifest.json
  env VAULT_ROOT         absolute vault path (for resolving candidates)
  env TOPIC_FILTER       optional topic substring          (commit 2)

OUTPUT (stdout, JSON)
  {
    "batch": ["research/2019-06-16 X.md", ...],         // ≤ cap, sorted by order
    "remaining": ["research/2019-06-17 Y.md", ...],     // deferred
    "skipped_unchanged": 32,
    "scope_summary": {
      "first_date": "2019-06-16",
      "last_date":  "2019-07-02",
      "remaining_count": 4493,
      "remaining_first_date": "2019-07-03",
      "remaining_last_date":  "2019-12-31"
    }
  }

EXIT CODES
  0   normal
  2   invalid env / unreadable manifest

DEPS  Python ≥ 3.10 stdlib only (re, os, json, hashlib, pathlib, datetime, sys)
```

**Date resolution order**（per spec）：
1. Filename `YYYY-MM-DD` 前綴
2. Frontmatter `date` / `upload_date` / `processed_at`（first match wins）
3. File mtime（fallback；排批次尾）

**Bucket logic（inside script）**：
- 讀 manifest → 對每個 candidate 算 SHA-256 → 對比 manifest entry → 分 NEW / MODIFIED / UNCHANGED
- *注意*：script 內重新 hash 是 idempotent；STEP 2 已 hash 一次後可以選擇傳已知 hash 進來 avoid 重算（commit 2 優化，commit 1 直接重算 OK）。

### §4 Test harness

**位置**：`obsidian/tests/wiki_ingest/test_select_batch.py`

**框架**：pytest（與 code-toolkit / legal-toolkit / investing-toolkit 一致）

**設置**：
- `obsidian/pyproject.toml` 新增：
  ```toml
  [project.optional-dependencies]
  dev = ["pytest>=7"]
  ```
- `.github/workflows/test-obsidian.yml`（仿 code-toolkit 既有）

**Coverage**：CC-01 → CC-15（per spec），用 `@pytest.mark.parametrize` 攤平。每個 case = `(fixture_name, expected_batch, expected_remaining, expected_summary)`。

Fixture 結構：
```
obsidian/tests/wiki_ingest/fixtures/
  cc01_all_dated_filename/
    vault/
      research/2019-06-16 A.md
      research/2019-06-17 B.md
      ...
    .manifest.json
    expected.json
```

### §5 Config

`.obsidian-wiki.config` 加：

```
# Batch order when NEW + MODIFIED > cap.
# Override per-run by including 'latest' / 'recent' / 'oldest' / 'backfill' / 最新 / 最舊
# in your /wiki-ingest prompt.
OBSIDIAN_WIKI_BATCH_ORDER=oldest-first
```

`obsidian/skills/wiki-setup/SKILL.md` 的 config 範本同步。

### §6 `references/batching-policy.md`

新檔，按 spec 大綱 8 節寫完：
1. Purpose（cap 政策 + batch order resolution）
2. Date resolution algorithm（決策樹）
3. Cap semantics（source 數而非 wiki page 數）
4. NEW vs MODIFIED interaction（合併排序 + 合計取 cap）
5. Order override matrix（prompt > config）
6. Undated files behavior（mtime fallback 語意）
7. Three worked examples（CC-01 / CC-03 / CC-07）
8. `/loop` 整合說明（暫不支援，rationale）

### §7 Commit 切分（候選 — writing-plans 階段微調）

| # | 包含 | LOC 估 |
|---|---|---|
| 1 | STEP 1 decision table + summary line / select-batch.py 第一版（sort+cap+date resolution，hardcoded oldest-first，無 topic filter）/ STEP 2 不動 / STEP 3 新增（呼叫 script）/ STEP 4-6 重編號 / pytest harness + CC-01→CC-08 | ~250 |
| 2 | `OBSIDIAN_WIKI_BATCH_ORDER` config 讀取 / select-batch.py 加 `topic_filter` / wiki-setup 範本 / `references/batching-policy.md` / CC-09→CC-13 | ~150 |
| 3 | STEP 6 加下一批預告 / CC-14→CC-15 / dogfood on `~/kouko-obsidian-vault`（驗證接續 4493 NEW oldest 15）| ~80 |

### §8 PR 命名

- Branch：`feat/wiki-ingest-zero-prompt-oldest-first`（已開）
- PR title：`wiki-ingest: zero-prompt default + oldest-first auto-batching (v3.10.0)`
- 版本號跳 minor（v3.9.0 → v3.10.0）— 行為改變但不破壞既有 explicit 用法

## What Becomes Obsolete

- **`AskUserQuestion` 三選一 default**：移除 default 觸發；保留作為 SKILL.md 內可選 fallback（罕用）。
- **STEP 2 內 `Proceed?` gate**：自動取 cap 後不再問 confirm；改為 STEP 1 first-line summary 讓使用者視認後自行中斷。
- **`SKILL.md:57` "If scope exceeds it, ask user to confirm or batch"** 這句 vague 規範 — 被 STEP 3 + batching-policy.md 取代。

同 PR 內移除上述死碼。

## Alternatives Considered

### Cap 套用時機（已拍板 B）

- **A. Hash all → sort all candidates → take cap**：sort 在 hash 前；但 cap on NEW+MOD 需要先知道 bucket 結果，邏輯矛盾。Reject。
- **B. Hash all → bucket → sort NEW+MOD → take cap** ✅ — 採用。最 explicit、最易測。
- **C. Pre-hash sort → hash one-by-one → early break at cap NEW+MOD**：UNCHANGED 過多時仍要掃很久；optimisation 邊際效益小（kouko vault 初次 4508-file hash 是一次性）。Reject。
- **D. Pre-hash sort → hash cap-many → 從中挑 NEW+MOD**：cap-many 可能整批 UNCHANGED → 空跑；不可靠。Reject。

### Scope-hint parsing layer（已拍板 A）

- **A. Claude in-context 判讀（SKILL.md decision table）** ✅ — 採用。與 wiki-* family 既有 convention 一致；零 script、零 plumbing；多語言 robust。
- **B. `scan_intent.py` regex 解析 user message**：plumbing 麻煩（怎麼傳 user message 進 script？）；多語言 keyword 維護累。Reject。
- **C. Hybrid Claude propose + `validate_intent.py` allowlist 檢查**：路徑不存在 STEP 2 scan-vault.sh 自然處理；over-engineered。Reject。

### Script architecture（已拍板 B1）

- **B1. 抽出 `scripts/select-batch.py`，Python stdlib only** ✅ — 採用。可獨立 pytest；與 scan-vault.sh 同層；JSON over stdin/stdout 乾淨。
- **B2. SKILL.md inline Python heredoc**：~80 行 code 撐胖 SKILL body（超 repo convention `<6000 tokens`）；無法獨立測試。Reject。
- **B3. Bash 重寫**：frontmatter parse 在 bash 醜（sed 撈 `---` block + awk parse YAML）。Reject。
- **B4. SKILL.md 純描述演算法讓 Claude 用 Bash+jq 拼**：cap-application 是中心邏輯；不應讓 Claude 每次重複拼。Reject。

### Test harness（已拍板 A）

- **A. pytest** ✅ — 採用。與 monkey-skills 主流一致；parametrize 對 CC-01→CC-15 友善。
- **B. stdlib unittest**：零 dep 但 subTest() 語法繁、不如 parametrize 直覺。Defer。
- **C. dogfood-only no unit tests**：regression catch 差；CC-01→CC-15 只能靠記憶。Reject。
- **D. bats**：bats wrap Python (`python3 -c "..."`) 醜。Reject。

### Topic-only hint 詮釋（已拍板 A2）

- **A1. Filename grep only**：最輕量但 catch 不到「檔名不含 keyword 但內容是」。Defer（可未來擴展）。
- **A2. Filename + frontmatter tags/aliases grep** ✅ — 採用。Light frontmatter scan，可與 select-batch.py 的 date resolution 共用 parser。
- **A3. 全文語意判斷**：要讀 4500 檔 frontmatter+body；貴且不可靠。Reject。
- **B. 不處理 topic、fall back to whole-vault**：使用者明確指定卻被忽略，UX 退步。Reject。

### `AskUserQuestion` fallback 觸發（修訂 spec）

Spec 原寫「Topic without path → ambiguous → AskUserQuestion」。Brainstorm 釐清：**使用者只要指定題目或路徑，都應依指定內容開始**。改為：
- Path / 單檔 / 時間關鍵字 / topic → 都按 decision table 直接跑。
- AskUserQuestion 完全移除為 default；SKILL.md 仍可選擇性提供 fallback，但無強制觸發條件（自由心證，罕用）。

## Out of Scope

- 自動 `/loop` 整合 — spec 已拍板（每批要寫 ~30 wiki page 需人腦判斷品質）。
- Folder priority — spec 已拍板（保持泛用，不假設使用者 vault 資料夾語意）。
- 修 scan-vault.sh 第一次 4500-file 掃描效能 — spec 已拍板（既存問題，本次不解決）。
- 多級 priority queue（per-source priority weight） — 未列入 spec，YAGNI。
- Topic filter 的語意 search（A3） — 已 reject。
- Cross-skill 改動：wiki-cross-linker / wiki-lint / wiki-auto-research 不變。
- **Agent self-judging cap（deferred → Phase 2 future PR）** — 由 agent 基於品質訊號 / context 餘裕自行判斷單次處理量。本次設計討論評估了 4 個選項（A 純靜態 cap / B 純 agent self-judging / C hybrid early-stop / E token-budget cap），拍板 Phase 1 維持 deterministic 固定 cap（A），Phase 2 future PR 加 Option C（最小侵入：純 SKILL.md guidance edit，零 script 改、零 fixture 影響）。**Phase 2 觸發條件**：Phase 1 dogfood 1-2 週後若實際出現「15 個太多/太少」friction、或 4500-NEW 場景的 batch 處理品質有觀察到 degradation。詳細選項分析見本 doc git log 訊息 `Decision:` trailer（或 conversation transcript）。

## Open Questions（送 writing-plans / review 階段）

1. **Manifest hash 重算避免**：select-batch.py commit 1 直接重 hash candidates；commit 2 可優化讓 STEP 2 把 hash 結果序列化傳進來。是否值得在 commit 2 做？或留待後續 perf PR？
2. **CC-15 (wiki-auto-research status) 對接點**：CC-15 是「auto-research status != reviewed-accept 仍套用 batch order，但 STEP 4 (原 STEP 3a) 仍 skip 並記 log」。fixture 涉及跨 skill output 模擬 — 需在 plan 階段確認 fixture 邊界（mock frontmatter 即可，不需真跑 wiki-auto-research）。
3. **CI workflow 命名**：`.github/workflows/test-obsidian.yml` 還是 `test-obsidian-skills.yml`？等 plan 階段對齊既有 workflow naming pattern。

## References

- Upstream spec：`~/kouko-obsidian-vault/research/2026-05-17 wiki-ingest 預設行為改造——oldest-first auto-batching 設計筆記.md`
- Current SKILL.md：`obsidian/skills/wiki-ingest/SKILL.md`（v3.9.0 head）
- Delta-tracking contract：`obsidian/skills/wiki-ingest/references/delta-tracking.md`
- Scan script：`obsidian/skills/wiki-ingest/scripts/scan-vault.sh`
- Plugin pyproject convention：`code-toolkit/pyproject.toml`（仿用 dev deps 寫法）
- CI workflow convention：`.github/workflows/test-code-toolkit.yml`（仿用 step layout）
