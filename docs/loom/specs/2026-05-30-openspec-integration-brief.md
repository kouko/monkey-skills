# Brief: code-toolkit × OpenSpec 整合 v0.1

**Date**: 2026-05-30
**Status**: Brief locked, plan pending
**Discussion sessions**: `d1c05c3e-d9d2-47d0-93f5-2dc6ab6f5892.jsonl` (2026-05-27 起) + `668f787c-a8c9-45d2-9db3-a447bb78a5e0.jsonl` (2026-05-28 起)
**Prior research**: Obsidian vault `research/2026-05-26 OpenSpec × code-toolkit 整合 Playbook.md` (`domain-teams:research-team` quick-mode)
**Empirical validation**: OpenSpec v1.3.1 in `/tmp/openspec-test-2026-05-28/`, 12 案例

## 1. TL;DR

把 [OpenSpec](https://github.com/Fission-AI/OpenSpec) (`@fission-ai/openspec`) 作為 **code-toolkit 的 spec 持久化層** hard-couple 進來：規格用 OpenSpec 檔案結構（`openspec/specs/<cap>/spec.md` + `openspec/changes/<id>/{proposal,design,tasks}.md`）取代對話式 brainstorming-only memory；任務追蹤用 OpenSpec 的 `tasks.md` checkbox + `openspec instructions apply --json` API；新建 3 層 lightweight tier (No-Spec / Lite / Full) 對齊 OpenSpec 官方 Lite/Full mode，避免 lightweight 改動被 full ceremony 拖累。Schema 驗證採雙階段 (pre-write `openspec instructions` + post-write `openspec validate`) + task-gate hard enforcement via `safe-archive.sh` wrapper + L2-L5 defense-in-depth。OpenSpec 版本 `~1.3.x` pin (patch auto + minor 手動 PR ritual)。

## 2. Context & motivation

### 解決什麼問題

code-toolkit 現有的 brainstorming / writing-plans 產出**主要活在對話 context 裡**，跨 session、跨工具、跨機器都會失。`docs/loom/{specs,plans}/` 雖然存在但是 free-form Markdown — 沒有 machine-readable schema、沒有 brownfield delta 追蹤、沒有 task-level progress query API。

OpenSpec 解的正是這三件事：
1. **規格檔案化、跨工具持久** — `openspec/specs/<cap>/spec.md` 永久存在
2. **Brownfield delta 追蹤** — `## ADDED / MODIFIED / REMOVED / RENAMED Requirements` markers 讓 `openspec archive` 智慧合併
3. **Machine-readable task tracking** — `openspec instructions apply --change <id> --json` 回傳 `{progress, tasks[], state: ready/blocked/all_done}`

### 為何 hard-couple 而非 dual-default

discussion Q6 鎖定 **A (hard-couple)** 而非 B (dual-default with fallback)：
- A 簡化長期維護成本（user 原話）
- code-toolkit SKILL.md 寫死 `openspec/changes/<date>-<topic>/` layout，避免 condition 分支
- 接受**code-toolkit 從自包含 plugin 變 OpenSpec-coupled plugin** 的 trade-off

### 為何適合分層而非單一 flow

最近 25 個 code-toolkit / dev-workflow PR 分析（discussion Q7 ground truth）：
- 36% 是 `prod_files=0`（README / CHANGELOG / docs 改動）→ 不該跑 OpenSpec
- 20% 是 small bug fix / internal refactor → 適合 Lite (短 proposal + spec + tasks)
- 44% 是新功能 / cross-plugin → 適合 Full (完整 proposal + design + tasks + specs)

→ 3 層映射 No-Spec / Lite / Full，前兩層對齊 OpenSpec 官方 Lite mode 哲學「minimum ceremony」，Full 對齊 OpenSpec 官方 Full mode (cross-team / API contract / migration / security)。

## 3. Locked decisions (Q1-Q9)

| # | 議題 | 鎖定 | 一句話理由 |
|---|---|---|---|
| **Q1** | monorepo 邊界 | **A** 單根 `openspec/` + 檔名 namespace | 簡單；workspaces 是 beta 不需要 |
| **Q2** | CLI 驗證 | 完成 | 發現 `openspec instructions` 是隱性主角 |
| **Q3** | 既有 plans/specs migration | **C1 + (iii)** | Brownfield-first 不 backfill；orphan `wiki-index-human-snapshot` 視同 abandoned |
| **Q4** | CI validate 深度 | **Tier-aware + T1 advisory + auto+label+audit detect + 2 workflow files** | 對齊 Q7 分層；write-time 才是主守門 |
| **Q5** | OpenSpec 版本 pin | **`~1.3.x` + CI cron weekly bump PR + plugin.json+.openspec-version 雙寫 + wrapper+CI 雙保險** | OpenSpec 仍演化期；patch auto + minor 手動 |
| **Q6** | 路徑 default | **A** hard-couple OpenSpec layout | 簡化長期維護 |
| **Q7** | Lightweight tier | **3 層 No-Spec / Lite / Full** 對齊 OpenSpec Lite/Full | Ground truth 20% lite rate 健康 |
| **Q8** | write-time validate gate | **雙階段 + task-gate hard via `safe-archive.sh` + L2-L5 defense** | OpenSpec instructions API 讓第一次就近寫對 |
| **Q9** | empirical validation | **PASS** (v1.3.1 + 12 案例) + 2 wrapper-fix gap 入 v0.1 plan | validate error agent-actionable，archive task-gate 是 soft 需自擋 |

詳細 Q1-Q9 與 sub-question 鎖定在 `memory/project_openspec_code_toolkit_integration.md`（user-level memory）。

## 4. Architecture

### 4.1 3-Tier Lightweight 模型

```
┌──────────────────────────────────────────────────────────────────┐
│ Tier 0: No-Spec  (code-toolkit 擴展，OpenSpec 沒這層)              │
│   觸發: prod_files == 0                                            │
│   commit type: docs: / chore: / style:                            │
│   OpenSpec artifact: 完全不寫                                       │
│   code-toolkit: 跳所有 SDD，直接 commit                             │
├──────────────────────────────────────────────────────────────────┤
│ Tier 1: Lite  (= OpenSpec 官方 Lite mode)                          │
│   觸發 ALL: 不 cross-plugin / 無新 API / commit type ∈ {fix,       │
│   refactor:internal, perf:bugfix}; SHOULD ≤2 prod files & ≤30 LOC │
│   OpenSpec artifact: 短 proposal + 短 delta spec + 短 tasks (1-3)  │
│   code-toolkit: skip brainstorming + writing-plans (1-3 atomic)   │
│                + inline-TDD; keep tdd-iron-law / whole-branch     │
│                review / verification                              │
│   Commit footer MUST: Lightweight-justification: <one line>       │
├──────────────────────────────────────────────────────────────────┤
│ Tier 2: Full  (= OpenSpec 官方 Full mode)                          │
│   觸發 ANY: cross-plugin / 新 API / contract / migration /          │
│             security / ambiguity / user 顯式                       │
│   OpenSpec artifact: 完整 proposal + design + tasks + delta specs  │
│   code-toolkit: 完整 flow (brainstorm → plan → SDD triad → ...)   │
└──────────────────────────────────────────────────────────────────┘
```

**`prod_files` 定義**（skill plugin context）：IN: SKILL.md, agents/*.md, references/*.md, protocols/*.md, checklists/*.md, rubrics/*.md, standards/*.md, scripts/*.py, plugin.json, marketplace.json. OUT: README*.md, CHANGELOG.md, docs/.

### 4.2 Q8 雙階段 write-time gate

```
┌─────────────────────────────────────────────────────────────────┐
│ Pre-write (MUST, fetch schema upfront)                          │
│   openspec instructions <artifact-id> --change <id> --json      │
│   → 拿 {outputPath, instruction, template (with comments),      │
│         dependencies, unlocks}                                   │
│   → agent 第一次就近寫對                                          │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ Post-write (MUST, sanity check)                                 │
│   openspec validate <id> --type change --json                   │
│   1st fail → parse JSON issues → fix → retry                    │
│   2nd fail (= 2 falsifications) → HARD-GATE WebSearch BEFORE   │
│                                    3rd retry                    │
│     Query: "<error message>" openspec <version>                 │
│   3rd fail → BLOCKED, escalate w/ diagnostic bundle            │
│                                                                 │
│   3-4 行 inline 寫進 writing-plans / proposal / specs / tasks    │
│   SKILL.md，引用 systematic-debugging 當 discipline provenance   │
│   (不 invoke 它，避免 cross-skill coupling)                       │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ Task-gate hard enforce (code-toolkit 擋，OpenSpec archive 是 soft)│
│   SDD between tasks:                                            │
│     openspec instructions apply --change <id> --json            │
│     → 找第一個 done==false → dispatch implementer               │
│     → implementer 改 [x]，commit → loop until state="all_done"  │
│                                                                 │
│   Archive (Tier 1 / Tier 2 only):                               │
│     code-toolkit/scripts/safe-archive.sh <id>                   │
│     → wrapper 內 check state=="all_done" 才 openspec archive -y │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 L2-L5 defense-in-depth (archive 守門)

```
L1: OpenSpec 內建 — schema validate hard / task soft (不能依賴)
L2: code-toolkit/scripts/safe-archive.sh wrapper — 主守門
L3: SKILL.md inline fallback — wrapper 不見也擋得住
L4: CI workflow (Q4) — 機器強制，獨立於 finishing-branch flow
L5: requesting-code-review whole-branch reviewer — 第三方審查
```

### 4.4 CI workflow 結構 (Q4 + Q5 整合)

```
.github/workflows/
├── openspec-pr.yml      # on: pull_request, 5 sequential checks
│   1. version actual vs expected (.openspec-version)
│   2. version drift (plugin.json ↔ .openspec-version ↔ README)
│   3. tier detect (auto regex + label override + audit trail)
│   4. openspec validate (Tier-aware: T0 skip / T1 advisory / T2 strict)
│   5. task-state check (state == "all_done" — T2 MUST / T1 advisory)
│
└── openspec-cron.yml    # on: schedule weekly Mon 00:00 UTC
    └── npm registry check → 新 minor → auto-open bump PR with
        changelog link + validate-all result
```

### 4.5 OpenSpec 版本 pin 多源寫法 (Q5)

| 檔案 | 內容 | 誰讀 |
|---|---|---|
| `code-toolkit/.claude-plugin/plugin.json` | 新增 `openspecRequired: "~1.3.1"` field | 主 source of truth；plugin metadata 自然位置 |
| `code-toolkit/.openspec-version` | 單行 `~1.3.1` | wrapper / CI shortcut (不依賴 jq) |
| `code-toolkit/README*.md` §Prerequisites | sync-generated | 給人讀，drift 由 CI 自動 check |

drift 檢查由 `code-toolkit/scripts/sync-version-docs.py` (~20 LOC) 跑進 CI step 2。

## 5. Implementation scope

### 5.1 既有檔修改（Severity 1-5 leak fix，17 檔）

Per discussion turn 23 severity scan (session `d1c05c3e`)：

- **Severity 1** (6 檔 16 行 prescriptive): `code-toolkit/skills/brainstorming/SKILL.md:203` + `references/handoff-brief-format.md:19` + `writing-plans/SKILL.md:24,108,113,148,149` + `writing-plans/references/plan-document-reviewer-prompt.md:17,20` + `writing-plans/references/plan-format.md:21,31,103,108` — 全部 `docs/loom/...` 改為 `openspec/changes/<date>-<topic>/...`
- **Severity 2** (4 檔 documentary): `code-toolkit/README{.md,.ja.md,.zh-TW.md}` + `brainstorming/README.md` — 加 OpenSpec hard requirement Prerequisites
- **Severity 3** (3 檔 examples): `code-toolkit/docs/examples/{python-csv-export,typescript-react-toast,swift-network-layer}.md` — 改 OpenSpec layout
- **Severity 4** (2 檔 agent prompt): `code-toolkit/agents/code-reviewer.md:352` + `code-quality-reviewer.md:340` — 移除 monkey-skills 特定 file path reference + 內嵌 §Resolved Decisions Q4 calibration
- **Severity 5** (2 檔 test fixtures): `code-toolkit/tests/brainstorming-pressure/prompts/index.md` + `writing-plans-pressure/prompts/index.md` — 跟 SKILL.md 同步

### 5.2 新增檔案（6 個）

- `code-toolkit/.openspec-version` — 單行 `~1.3.1`
- `code-toolkit/scripts/safe-archive.sh` — Q8c wrapper (≤15 行 bash, `set -euo pipefail`, `python3 -c` 解 JSON 不依賴 jq)
- `code-toolkit/scripts/sync-version-docs.py` — Q5 README ↔ plugin.json ↔ .openspec-version drift check + auto-patch (~20 LOC)
- `code-toolkit/scripts/check-openspec-version.sh` — Q5 共用 version-check 邏輯（wrapper + CI 都呼叫）
- `code-toolkit/.github/workflows/openspec-pr.yml` — Q4 PR-time 5 step
- `code-toolkit/.github/workflows/openspec-cron.yml` — Q5 cron weekly auto-bump PR

### 5.3 SKILL.md 修改（5 個）

- `code-toolkit/skills/using-code-toolkit/SKILL.md` — 加 §Prerequisites (OpenSpec hard requirement + 安裝指引) + Tier 1→2 升級觸發 + Lightweight tier 設計
- `code-toolkit/skills/brainstorming/SKILL.md` — 5-axis output 路徑改 `openspec/changes/<id>/proposal.md`
- `code-toolkit/skills/writing-plans/SKILL.md` — pre-write `openspec instructions` + post-write `openspec validate` + inline 4 行 HARD-GATE (Q8b)
- `code-toolkit/skills/subagent-driven-development/SKILL.md` — 每 dispatch 前 `openspec instructions apply --json` pick next task
- `code-toolkit/skills/finishing-a-development-branch/SKILL.md` — 用 `scripts/safe-archive.sh` 取代 `openspec archive`；L3 inline fallback；Tier 2 跑 `openspec validate --all --strict`

### 5.4 plugin.json 修改

- `code-toolkit/.claude-plugin/plugin.json` — 新增 `openspecRequired: "~1.3.1"` field (Q5)

### 5.5 PR label setup (manual, repo settings)

- 在 monkey-skills GitHub repo 設定加 3 個 label: `tier-0` / `tier-1` / `tier-2` — Q4 Sub-Q4b label override

## 6. Out of scope (v0.1)

- **多 plugin 全面遷移**：本 v0.1 只動 code-toolkit；dev-workflow / domain-teams / obsidian / 其他 plugin 不動。它們仍用對話式 brainstorming + `docs/<plugin>/{specs,plans}/`
- **OpenSpec workspaces (beta)**：跨 repo workspace 不啟用；monkey-skills 是 monorepo 走 repo-local `openspec/` 即可
- **Custom OpenSpec schemas**：不 fork OpenSpec schema；用官方 `spec-driven` default
- **migrate 既有 31 個 historical plans/specs** 進 `openspec/changes/archive/`：per Q3 brownfield-first，凍結就好
- **PR-time auto-detect tier 的 LLM-based classifier**：用 regex / commit-type / file count，不引 LLM call
- **Wrapper fix Gap 1 (auto-detect type) 與 Gap 2 (scenario conversion template)**：v0.1 plan 階段補；不入 ship gate
- **`openspec/skills/` Anthropic 風格 skill bundle**：OpenSpec init 會生 `.claude/skills/openspec-*` 4 個 skill，但這是 OpenSpec ship 的，code-toolkit 不重寫
- **跨工具相容**：v0.1 只測 Claude Code；Codex / Cursor / Antigravity 跑 OpenSpec 視 future work

## 7. Acceptance criteria

v0.1 ship gate（全部過才 merge）：

### 7.1 結構 acceptance

- [ ] `code-toolkit/.openspec-version` 存在且內容 = `code-toolkit/.claude-plugin/plugin.json` 的 `openspecRequired` field
- [ ] `openspec/` 根目錄存在（`openspec init` 跑過），含 `specs/` + `changes/`
- [ ] `code-toolkit/scripts/safe-archive.sh` 可執行（`chmod +x`）
- [ ] `code-toolkit/.github/workflows/openspec-pr.yml` + `openspec-cron.yml` 存在且 YAML syntax 過

### 7.2 行為 acceptance（用一個 sentinel change 做 e2e dogfood）

- [ ] 建一個 sentinel change `openspec/changes/test-sentinel/`，含 proposal + spec delta + tasks
- [ ] `openspec validate test-sentinel --type change` 通過
- [ ] `openspec instructions apply --change test-sentinel --json` 回 `state == "ready"` 並列出 tasks
- [ ] tasks 全勾 → `state == "all_done"`
- [ ] `bash code-toolkit/scripts/safe-archive.sh test-sentinel` 成功 archive
- [ ] 部分 tasks 沒勾 → `safe-archive.sh test-sentinel` 拒絕 archive 且 exit 1
- [ ] CI `openspec-pr.yml` 跑過 5 step 全綠
- [ ] CI 偵測 `openspec --version` 漂移時 fail（手動改 `.openspec-version` 製造漂移驗證）

### 7.3 SKILL.md acceptance

- [ ] `using-code-toolkit` SKILL.md §Prerequisites 寫死 `Requires OpenSpec ~1.3.x; install: npm install -g @fission-ai/openspec@latest`
- [ ] `writing-plans` SKILL.md 寫死「寫前 fetch `openspec instructions`、寫後 `openspec validate`、2nd fail HARD-GATE WebSearch」
- [ ] `finishing-a-development-branch` SKILL.md 寫死「用 `scripts/safe-archive.sh` 不用 `openspec archive`；L3 inline fallback」

### 7.4 文件 acceptance

- [ ] `code-toolkit/README{.md,.ja.md,.zh-TW.md}` §Prerequisites 由 `sync-version-docs.py` 自動 generate 一致
- [ ] CHANGELOG.md 記 v?.?.0 entry 含此 brief 連結

## 8. Known risks / gaps

### 8.1 OpenSpec wrapper-fix gaps (empirical 發現)

- **Gap 1**：`openspec validate <id>` auto-detect type 在空 change（只有 `.openspec-query.yaml`）回 `"Unknown item"` — Fix: code-toolkit SKILL.md 寫死 `--type change`，wrapper script 包進這個 flag
- **Gap 2**：「`### Requirement:` 緊跟 `- **WHEN**` 但無 `#### Scenario:` 」case，cli-validate self-spec 承諾要 emit 「conversion template」warning，v1.3.1 impl 只回 generic 「must include at least one scenario」 — Fix: code-toolkit pre-commit hook 偵測此 pattern 自加提示，或留待 OpenSpec 後續 minor release 補上

兩個 gap 都不 block ship；都在 v0.1 plan 階段補。

### 8.2 OpenSpec 仍演化期風險

- workspaces 是 beta，v1.4+ 可能改 API
- cli-validate self-spec 跟 v1.3.1 impl 已有微小落差 → minor bump 可能補上但也可能新增其他不一致
- 緩解：Q5 `~minor` pin + CI cron weekly 偵測 + manual review changelog 才 merge bump PR

### 8.3 hard-couple long-term cost

code-toolkit 從「自包含 plugin」變「OpenSpec-coupled plugin」：
- 任何 OpenSpec breaking change（major bump）→ code-toolkit major bump 連動
- 想只用 code-toolkit 的 brainstorming 一個 skill 也需要先 `openspec init`
- 緩解：Q5 multi-source version declaration 早發現 drift；user 接受此 trade-off 換長期維護簡化

### 8.4 task-gate 跨層 defense 過度設計風險

L2 wrapper + L3 inline + L4 CI + L5 reviewer 共 4 層 defense，看似 overlap。緩解：每層守不同失效（L2/L3 靠 agent 自律 / L4 機器強制 / L5 第三方審查），跟 Q7 No-Spec/Lite/Full + write-time/commit-time/CI-time defense 同精神，不算多。

### 8.5 brief 自身循環依賴

本 brief 描述「如何採用 OpenSpec」但本身寫在 pre-OpenSpec `docs/loom/specs/` — Q3 已選擇 freeze archive。下個 OpenSpec change（v0.1 落地的第一個）才走 `openspec/changes/<id>/`。

## 下一步

1. 跑 `code-toolkit:writing-plans` 把 §5 implementation scope 拆原子任務（預計 15-25 個 atomic ≤5min 任務）
2. 跑 `code-toolkit:subagent-driven-development` triad 實作
3. 跑 `requesting-code-review` whole-branch + `verification-before-completion` package-level
4. `finishing-a-development-branch` 收尾

預估 effort：原 brief 規模 + 15-20%（empirical test 帶出的 `openspec instructions` 整合 + L2-L5 defense + wrapper 邏輯）。

---

**Brief locked**: 2026-05-30. Implementation begins after plan stage completes.
