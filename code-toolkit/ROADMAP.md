# code-toolkit Roadmap (v0.1.0 → v1.0.0)

> **Status**: Design-only (no skill shipped yet)
> **Source of design**: `<obsidian-vault>/research/2026-05-15 Superpowers vs code-team 架構比較研究.md` + Q1-Q4 lock
> **Target**: 個人開發者（資料分析師 / App 設計師），Claude Code + Codex CLI
> **Coexists with**: `domain-teams:code-team`（被動 gate 入口）、`dev-workflow:{git-memory, complexity-critique, proposal-critique}`、`obra/superpowers`（with conflict env var）

---

## 結論

完整 9-skill plugin 從 0 → GA 估 **~25-35 工作天**（focused mode）或 **~3 個月** part-time，分 4 個 phase。Phase 2.5（Codex CLI ship）是 critical path 的相依長尾項，建議 Phase 2 結束後立刻接著做。

---

## Timeline 總覽

```
Phase    v0.x.0   天數     Skill 累計   重點                                              Status
─────    ──────   ──────   ─────────   ─────────────────────────────────────────────  ─────
0        ─        2d        0           Design lock — PRODUCT/TECH/ROADMAP             ⏳ THIS PR
1        0.1.0    6-8d      3           MVP shell — hook + using / tdd-iron-law / SDD  pending
1.5      0.1.5    2d        3 (patches) Soft-mode flag + 5 dogfood notes               pending
2        0.2.0    6-8d      6           brainstorming + writing-plans + sys-debugging  pending
2.5      0.2.5    3-4d      6 (ship CX) Codex CLI variant ship + integration test      pending
3        0.3.0    6-8d      9           Code-review cluster (full Superpowers parity)  pending
3.5      0.3.5    2-3d      9 (polish)  Dogfood polish + eval suite                    pending
4        1.0.0    3-4d      9 (GA)      Cross-skill delegation hardening + release     pending
─────────────────────────────────────  ─── 累計 ~28-37 工作天 ───
```

---

## 完整 Skill 全景（9 個）

| # | Skill | Cluster | Phase | Status | Superpowers 對應 |
|---|---|---|---|---|---|
| 0 | `using-code-toolkit` | router | 1 | planned | `using-superpowers` |
| 1 | `tdd-iron-law` | discipline | 1 | planned | `test-driven-development` |
| 2 | `subagent-driven-development` | workflow | 1 | planned | `subagent-driven-development` |
| 3 | `brainstorming` | discovery | 2 | planned | `brainstorming` |
| 4 | `writing-plans` | planning | 2 | planned | `writing-plans` |
| 5 | `systematic-debugging` | repair | 2 | planned | `systematic-debugging` |
| 6 | `requesting-code-review` | review | 3 | planned | `requesting-code-review` |
| 7 | `verification-before-completion` | review | 3 | planned | `verification-before-completion` |
| 8 | `using-git-worktrees` | workflow | 3 | planned | `using-git-worktrees` |
| 9 | `finishing-a-development-branch` | workflow | 3 | planned | `finishing-a-development-branch` |

**觀察名單（不一定做）**：
- `dispatching-parallel-agents`（Superpowers 有；待 Phase 3 後評估）
- `receiving-code-review`（功能與 `dev-workflow:git-memory` 重疊；待評估）
- `writing-skills`（範圍重疊 `dev-workflow:skill-creator-advance`；不做）
- `visual brainstorming server`（Superpowers 5.1.0 新 feature；MVP 不做）

---

## Phase 0 — Design lock（v0.1.0-draft，2 工作天）⏳ 進行中

**Scope**：把 SSOT 邊界、Phase 切分、Q-lock 全部釘死。

**交付物**：
- ✅ `code-toolkit/PRODUCT-SPEC.md`
- ✅ `code-toolkit/TECH-SPEC.md`
- ✅ `code-toolkit/ROADMAP.md`
- ⏳ `code-toolkit/.claude-plugin/plugin.json`（skeleton）
- ⏳ `code-toolkit/.codex-plugin/plugin.json`（skeleton）
- ⏳ `code-toolkit/README.md` / `.ja.md` / `.zh-TW.md`（skeleton）

**Q-lock**（8 項；見 PRODUCT-SPEC §8）：
- Q1 harness = Claude Code + Codex CLI
- Q2 code-team 並存
- Q3 先寫設計文件
- Q4 worktree `feat/code-toolkit-design`
- Q5 knowledge layer SSOT 留 code-team；functional copy via distribute.py
- Q6 skill naming Superpowers 風格
- Q7 TDD 措辭保留「Delete it. Start over.」 + Beck 2002 grounding
- Q8 subagent 3 角色

**Gate**：使用者 review PRODUCT/TECH/ROADMAP 三件套 → 批准進 Phase 1。

---

## Phase 1 — MVP shell（v0.1.0，6-8 工作天）

**Scope**：最小可運行 plugin — SessionStart hook 跑得通 + 3 個核心 skill。

### 交付物

| 模組 | 檔案 |
|---|---|
| Plugin root | `.claude-plugin/plugin.json` v0.1.0 / 加入 `.claude-plugin/marketplace.json` / `README.{md,ja.md,zh-TW.md}` / `CHANGELOG.md` |
| Spec | （Phase 0 已完成） |
| Hooks | `hooks/hooks.json` + `hooks/session-start` bash |
| Scripts | `scripts/distribute.py` + `scripts/verify-drift.py` + `scripts/canonical/README.md` |
| Router | `skills/using-code-toolkit/{SKILL.md, README×3, references/{codex-tools.md, claude-code-tools.md}}` |
| Discipline | `skills/tdd-iron-law/{SKILL.md, standards/tdd-standard.md (functional copy), references/testing-anti-patterns.md, README×3}` |
| Workflow | `skills/subagent-driven-development/{SKILL.md, agents/{implementer,spec-reviewer,code-quality-reviewer}-prompt.md, rubrics/{quality-gate,arch-gate}.md (functional copy), checklists/{security-checklist,spec-consistency}.md (functional copy), standards/× 7 (functional copy), README×3}` |
| Tests | `tests/skill-triggering/prompts/× 5` + `tests/tdd-iron-law-pressure/prompts/× 5` |
| Research | `research/grounding-v0.1.0.md` |

### Q-lock (Phase 1)

| Q | 決定 |
|---|---|
| P1-A | `using-code-toolkit/SKILL.md` 必須 ≤2000 tokens（hook 注入預算限制） |
| P1-B | `tdd-iron-law` 鐵律措辭 = Superpowers 完整 copy；額外加 Beck 2002 Preface 直接引文（含 ISBN） |
| P1-C | SDD 3 個 subagent prompt 用 frontmatter + Markdown，不用 `.txt`（Superpowers 用 `.md`） |
| P1-D | functional copy 第一行必加 HTML comment header 指 SSOT path |
| P1-E | `distribute.py` 純 stdlib（無 PEP 723）；走 `python3 scripts/distribute.py` |
| P1-F | Phase 1 不 ship Codex CLI variant；只放 `.codex-plugin/plugin.json` skeleton（v0.1.0-draft） |

### Acceptance test

- `/plugin install code-toolkit` 在 Claude Code 跑得通
- 開新 session → `using-code-toolkit` 自動載入（透過 hook）
- 對 agent 下「跳過測試直接 implement」誘導 × 5，5/5 拒絕並引用 Beck 2002
- 對 agent 下 4-task plan → SDD 啟動 12 個 subagent → 全綠
- `scripts/verify-drift.py` 綠燈
- monkey-skills CI 全綠（marketplace sync / skill structure / folder hook）

---

## Phase 1.5 — Soft-mode + dogfood（v0.2.x patches，rolling）

**Scope**：dogfood-driven 微調。Phase 0 規劃時 Phase 1.5 排在 Phase 1 與 Phase 2
之間，假設 v0.1.5 是「Phase 1 寫完後、Phase 2 開工前」的小修。實際開發 cadence
跳過 v0.1.5 直接做 Phase 2 → v0.2.0；Phase 1.5 backlog 改成「v0.2.x patch」rolling
模式 — 每次 ritual 觸發的 dogfood 訊號就累積進來，以 v0.2.1 / 0.2.2 / ... 滾動 ship。

**累積 backlog（更新時間 2026-05-16）**：

| # | Item | 來源 | 狀態 |
|---|---|---|---|
| P15-1 | `hooks/session-start` 加 `CODE_TOOLKIT_MODE=off` 退場條件 | Phase 0 規劃 | ✅ 已 ship（commit 9cba15c，Phase 1 一併做了） |
| P15-2 | `tdd-iron-law` SKILL.md — Feathers (2004) ISBN 978-0131177055 distinction | Phase 1 ritual feedback（`i-already-wrote-it.txt` 沒區分 legacy 與 violation） | ✅ 已 ship（v0.2.1） |
| P15-3 | `systematic-debugging` SKILL.md — description tuning for production-bug auto-fire | Phase 2 ritual feedback（`silence-with-try-except.txt` 沒 auto-load specialist） | ✅ 已 ship（v0.2.1） |
| P15-4 | `--soft-mode` flag for Iron Law strength (OQ-1) | Phase 0 OQ-1 | ⏳ 待真實 dogfood — 不知道哪個 skill 太強 / 何種放鬆規則之前無法設計 |
| P15-5 | `research/dogfood-2026-05-XX.md` × ≥5 | Phase 0 規劃 | ⏳ 待真實使用 session（ritual 不算 — ritual 是 synthetic prompt，dogfood 是 natural flow） |
| P15-6 | `scripts/check-skill-structure.py` allowlist — `agents/` + `scripts/` + `assets/` | Phase 3 verification-before-completion ritual（v0.3.0 close-out） | ✅ 已 ship（v0.3.0 commit 66f6d5a） |
| P15-7 | SKILL.md plugin-rooted-path reframes (SDD + tdd-iron-law) | Phase 3 verification ritual + CHK-SKL-011 | ✅ 已 ship（v0.3.0 commit 66f6d5a） |
| P15-8 | 10 個 skill frontmatter `version:` 與 plugin manifest 對齊（皆 bump 至 v0.4.0-draft） | v0.4.0-draft Phase 2 ritual feedback（version-stamp drift caught by requesting-code-review cross-task-coherence dimension） | ✅ 已 ship（v0.4.0） |
| P15-9 | `tests/integration/test-superpowers-mode-{on,off}.sh` — 區分 installed vs enabled；installed-but-not-enabled SKIP 而非 PASS | v0.4.0-draft Phase 4 ritual Session 4-5（superpowers 在 user 機器 installed 但 `enabledPlugins` 沒包含；coexistence live verification deferred） | ✅ 已 ship（v0.4.0） |
| P15-10 | Router rule #5 "Research before asking" + brainstorming Axis 4 research protocol (WebSearch-grounded alternatives, not imagined) | User pain pattern: 重複手動要求 "先 search 業界實踐"。Option D — minimum-invasive: 1 router rule + 1 Axis 4 inline protocol；無新 skill | ✅ 已 ship（v0.5.0 — ritual PASS + ~12 emergent behaviors） |
| P15-11 | brainstorming Axis 4 §Multilingual coverage — EN + JA minimum；bilingual query patterns table；single-language anti-pattern | User extension request post-P15-10: 9-source rate-limiting bibliography 100% 英文 → 顯示出單語言 sampling bias；Mercari / Cookpad / Qiita / Zenn / 徳丸本 等日文 sources 系統性遺漏 | ✅ 已 ship（v0.5.1-draft，self-check PASS，clean-context ritual pending） |
| P15-12 (Phase 1) | Plugin-level agent files (`code-toolkit/agents/`) + 12-rule engineering baseline SSOT (`scripts/_baseline.md`) + `distribute.py` / `verify-drift.py` extension for in-file baseline-block sync. Phase 1 scope: 1 agent (`implementer.md`) as proof-of-mechanism. | User adopted 12-rule CLAUDE.md template + asked "為何不全部塞 agent file"。Active-enforcement need: baked-into-system-prompt > passive reference doc. SSOT-and-functional-copy pattern extended from whole-file (existing) to in-file section (new). | ✅ 已 ship（v0.5.2-draft，pending SDD ritual） |
| P15-12 (Phase 2) | Promote remaining 4 agents to plugin-level (`spec-reviewer` / `code-quality-reviewer` / `reviewer` / `debugger`)；each gets baseline injection；CHK-SKL-012 false-positive 自然消解（per-skill agents/ 搬空） | Phase 1 ritual PASS 之後執行 — 是 v0.6.0 minor-version scope | ⏳ 排在 v0.6.0 |

**Acceptance（rolling）**：
- ✅ P15-1 / P15-2 / P15-3 / P15-6 / P15-7 / P15-8 / P15-9 / P15-10 / P15-11 / P15-12-Phase1（10 of 12 closed）
- ⏳ P15-4 / P15-5（等真實 dogfood data — v1.0.0 release engineering 階段 unblock）
- ⏳ P15-12-Phase2（v0.6.0 scope，blocked on Phase 1 ritual PASS）

---

## Phase 2 — Discovery + planning skills（v0.2.0，6-8 工作天）

**Scope**：加 3 個 skill — `brainstorming` / `writing-plans` / `systematic-debugging`。

### 交付物

| 新 skill | 檔案 |
|---|---|
| `brainstorming` | `SKILL.md` + `references/visual-companion.md`（沿用 Superpowers） + README×3 |
| `writing-plans` | `SKILL.md` + `references/plan-document-reviewer-prompt.md`（沿用 Superpowers） + README×3 |
| `systematic-debugging` | `SKILL.md` + `references/{root-cause-tracing,defense-in-depth,condition-based-waiting}.md`（沿用 Superpowers） + README×3 |

### Q-lock (Phase 2)

| Q | 決定 |
|---|---|
| P2-A | `brainstorming` HARD-GATE 措辭沿用 Superpowers；加碼「複雜度 critique」可選 delegation 到 `dev-workflow:complexity-critique` |
| P2-B | `writing-plans` 每任務 ≤5 分鐘；BLOCKED 時 fallback 更小切割 |
| P2-C | `systematic-debugging` 4-phase 沿用 Superpowers；新增 `references/character-encoding-debug.md` 連結到 code-team `character-encoding-security.md` |

### Acceptance test

- 「Let's build X」prompt 自動 trigger brainstorming（不寫 code）
- brainstorming 完成後 auto-handoff 到 `writing-plans`
- 5 個 brainstorming pressure prompts（"This is too simple" 系列）全部拒絕跳過

---

## Phase 2.5 — Codex CLI ship（v0.2.5，3-4 工作天）

**Scope**：第二 harness 完整 ship。

### 交付物

**Note 2026-05-16**: Phase 2.5 重新編號至 **v0.4.0**（原規劃 v0.2.5，但 Phase 3 先 ship 為 v0.3.0；Phase 2.5 內容自然落在 v0.4.0 minor bump — 新 harness 是 minor feature）。

| 模組 | 檔案 | v0.4.0 status |
|---|---|---|
| Codex plugin | `.codex-plugin/plugin.json` v0.4.0-draft（含 `interface` block，mirror Superpowers） | ✅ build done |
| Tool mapping | `skills/using-code-toolkit/references/codex-tools.md`（完整 + ⚠️ TBD verify markers） | ✅ build done |
| Hook adapt | `hooks/session-start` 已從 v0.1.0 emit `additional_context` top-level key（已驗證 offline，6717 chars） | ✅ done since v0.1.0 |
| Tests | `tests/codex-cli/test-skill-loading.sh` + `test-hook-injection.sh` + `README.md` | ✅ build done |

### Acceptance test

- ✅ build 完成（v0.4.0-draft 落地）
- ⏳ Codex CLI `plugin install` 跑得通（待使用者跑 verification ritual）
- ⏳ Codex session 啟動 → using-code-toolkit 自動載入（待 ritual）
- ⏳ 在 Codex 跑同樣的 TDD 鐵律壓測 × 5 → 5/5 拒絕（待 ritual）

**Phase 2.5 BUILD vs VERIFICATION 分割**：build artifacts 落地（manifest / docs / scripts）= v0.4.0-draft；verification ritual 跑 PASS = drop -draft → v0.4.0。同 Phase 1 / 2 / 3 的 -draft 慣例。

---

## Phase 3 — Code-review cluster（v0.3.0，6-8 工作天）

**Scope**：加 4 個 review / workflow skill。

### 交付物

| 新 skill | 檔案 |
|---|---|
| `requesting-code-review` | `SKILL.md` + `agents/code-reviewer.md`（review subagent prompt） + README×3 |
| `verification-before-completion` | `SKILL.md` + README×3 |
| `using-git-worktrees` | `SKILL.md` + README×3 |
| `finishing-a-development-branch` | `SKILL.md`（delegate to `dev-workflow:git-memory`） + README×3 |

### Q-lock (Phase 3)

| Q | 決定 |
|---|---|
| P3-A | `requesting-code-review` 的 reviewer subagent 載入 code-toolkit `rubrics/`（不再走 SDD 內嵌 reviewer） |
| P3-B | `verification-before-completion` 強制 `npm test` / `pytest` / `go test` 等套件層級驗證；不靠單一檔案 lint |
| P3-C | `using-git-worktrees` 預設 Native git worktree（不額外 wrapper） |
| P3-D | `finishing-a-development-branch` commit 前 mandatory 走 `dev-workflow:git-memory`；不重複 git-memory 邏輯 |

### Acceptance test

- 完整跑「brainstorm → plan → SDD → review → finish」端到端 demo
- `finishing-a-development-branch` 自動觸發 `git-memory` skill
- 提交一個 PR 用 code-toolkit 完整跑下來

---

## Phase 3.5 — Polish（v0.3.5，2-3 工作天）

**Scope**：dogfood + 補漏。

**交付物**：
- 10 個 dogfood session 紀錄
- 完整 eval suite（mirror Superpowers `tests/skill-triggering/run-all.sh`）
- README 補完使用範例 × 3 種（Python / TypeScript / Swift）

---

## Phase 4 — GA（v1.0.0，3-4 工作天）

**Scope**：cross-skill delegation 硬化 + release。

**交付物**：
- `dev-workflow:complexity-critique` brainstorming-time 整合測試
- `dev-workflow:git-memory` commit-time 整合測試
- `domain-teams:code-team` 並存測試（同一 vault 跑兩個 plugin 無衝突）
- CHANGELOG.md 從 v0.1.0 累積到 v1.0.0
- 公開 announcement 草稿

**Acceptance**：
- 與 Superpowers 並存（CODE_TOOLKIT_MODE=on）測試通過
- 與 Superpowers 並存（CODE_TOOLKIT_MODE=off）測試通過
- 三個 cross-plugin delegation（git-memory / complexity-critique / code-team）全綠

---

## Cross-cutting concerns

### CI gates（每個 PR 都跑）

| Gate | Trigger | Script |
|---|---|---|
| Folder structure | Write/Edit to skills/ | `.claude/hooks/validate-skill-folder-structure.sh` |
| Marketplace description sync | Edit to plugin.json / marketplace.json | `scripts/check-marketplace-description-sync.py` |
| SSOT drift | Edit to skills/*/standards/ etc. | `code-toolkit/scripts/verify-drift.py` |
| Skill structure | New skill or subfolder | `scripts/check-skill-structure.py` |
| Plugin manifest validity | Any change to a skill's frontmatter / plugin.json | `claude plugin validate code-toolkit` |

### Per-Phase release ritual (hybrid testing cadence)

決策（2026-05-16, kouko）：行為層完整測試 defer 到 Phase 3.5 / 4，但每個
Phase 結束**必跑** 3 分鐘最小儀式，避免在錯的 floor 上疊高樓。理由：
toolkit 的價值 = 規律措辭能不能讓 agent 真的照做；靜態 gate 看不到
行為層，越晚發現措辭問題雪球越貴。

每個 Phase 結束時跑：

```bash
# 1. 靜態 validator (30 秒) — 必跑
claude plugin validate code-toolkit

# 2. 重裝到 local (30 秒) — 必跑
claude plugin uninstall code-toolkit
claude plugin install code-toolkit@monkey-skills --scope local

# 3. 1 個壓測 prompt (~90 秒) — 必跑；新 skill 的核心措辭至少壓一次
#    從 code-toolkit/tests/{skill-triggering,tdd-iron-law-pressure}/prompts/
#    挑一個對應新 skill 的最具殺傷力的 prompt，在 fresh session 跑
```

任一步失敗 = 該 Phase 不算完，修到 3 步都過再進下個 Phase。

完整系統性測試（50+ prompt eval suite / 跨 skill 端到端 / Codex 整合 /
≥10 dogfood session / 與 obra/superpowers 並存）集中到 Phase 3.5
（polish）+ Phase 4（GA hardening）。

### Documentation cadence

- 每個 Phase 結束時 push 一個 dogfood note 到 `research/dogfood-vX.X.X.md`
- 每個 Q-lock 都用 markdown table 釘在對應 phase 內
- CHANGELOG.md 用 keep-a-changelog 格式（mirror legal-toolkit）

### Cross-plugin delegation contract（CLAUDE.md 既有 convention）

| Source | Target | Trigger |
|---|---|---|
| `code-toolkit:finishing-a-development-branch` | `dev-workflow:git-memory` | commit gate（必呼） |
| `code-toolkit:brainstorming` | `dev-workflow:complexity-critique` | 複雜度疑慮（建議） |
| `code-toolkit:brainstorming` | `dev-workflow:proposal-critique` | 多方案 triage（建議） |
| `code-toolkit:requesting-code-review` | `domain-teams:code-team` | 既有大產出要 audit（可選） |

---

## Decision Ledger

| ID | 鎖定時間 | 決定 | Phase | 撤回成本 |
|---|---|---|---|---|
| Q1 | 2026-05-15 | harness = Claude Code + Codex CLI | 0 | Low（加 harness 容易） |
| Q2 | 2026-05-15 | code-team 並存 | 0 | High（拆分入口語意成本大） |
| Q3 | 2026-05-15 | 先寫設計文件 | 0 | None |
| Q4 | 2026-05-15 | worktree `feat/code-toolkit-design` | 0 | None |
| Q5 | 2026-05-15 | knowledge layer SSOT = code-team standards；functional copy | 0 | High（改動會帶 drift 風險） |
| Q6 | 2026-05-15 | skill naming Superpowers 風格 | 0 | Medium（rename 要改所有引用） |
| Q7 | 2026-05-15 | TDD 措辭 = Superpowers measure + Beck 2002 grounding | 0 | Low |
| Q8 | 2026-05-15 | subagent = 3 角色（implementer / spec-reviewer / code-quality-reviewer） | 0 | Medium（schema 變動要改 prompts） |
| TC-1 | 2026-05-16 | Hybrid testing cadence — 每 Phase 3 分鐘儀式（validate + reinstall + 1 壓測 prompt）；完整系統測 defer 到 Phase 3.5 / 4 | 1 | Low（policy 決定；可隨時 escalate 到每 Phase 都跑完整 eval suite） |
| P15-Mode | 2026-05-16 | Phase 1.5 從 v0.1.5 單版改為 v0.2.x rolling patches — Phase 1 / Phase 2 完成後才開始累積 backlog；每次 ritual 觸發的 dogfood 訊號 ship 為 v0.2.1 / 0.2.2 / ... | 1.5 | Low（純語義 — 釐清 Phase 1.5 不是固定版本而是 rolling 概念） |
| P1-A | tbd | using-code-toolkit ≤2000 tokens | 1 | Low |
| P1-B | tbd | TDD Beck 2002 Preface 直接引文 + ISBN | 1 | Low |
| P1-C | tbd | subagent prompt = `.md` | 1 | Low |
| P1-D | tbd | functional copy 加 SSOT header HTML comment | 1 | Low |
| P1-E | tbd | distribute.py 純 stdlib | 1 | Low |
| P1-F | tbd | Phase 1 不 ship Codex；只放 skeleton | 1 | Low |
| (more Phase 2-4 decisions tbd) | | | | |
