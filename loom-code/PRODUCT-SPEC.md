# PRODUCT-SPEC — loom-code

> **Owner**: planning (cross-domain — process methodology + knowledge integration)
> **Companion**: [TECH-SPEC.md](TECH-SPEC.md) — plugin layout / hooks / SSOT mechanics (code-team owned)
> **Source of design**: `<obsidian-vault>/research/2026-05-15 Superpowers vs code-team 架構比較研究.md`（two-axis comparison: 流程紀律 vs 知識權威）
> **Roadmap**: [ROADMAP.md](ROADMAP.md) — v0.1.0 → v1.0.0 phase plan

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1.0-draft | 2026-05-15 | kouko | Initial spec extracted from comparison research note + 4-question Q-lock |

---

## 1. Background & Opportunity

### 1.1 Current pain points (Why)

monkey-skills 已有 `domain-teams:code-team`（v5.6.0），具備完整的 8 本書 grounding + MUST/SHOULD/MAY gate + worker/evaluator 角色分離。但實際使用 code-team 時暴露三個結構性缺口：

| 缺口 | 現象 | 根因 |
|---|---|---|
| **冷啟動空轉** | 每次新 session 都要使用者「主動想到要呼叫 code-team」；忘記就回去無紀律寫 code | code-team 沒有 SessionStart hook；靠 description trigger 在「我先快速改一下」的情境下不可靠 |
| **「先寫 code 再補測試」常態化** | TDD 被當建議，被「我先試一下」合理化掉 | code-team 的 `tdd-standard.md` 是規範文件，沒有 Superpowers 那種「Delete it. Start over.」的鐵律措辭 |
| **沒有任務切割 → SDD 串接** | 大功能丟給 agent 一次寫完，context 爆掉、品質失控 | code-team 有 spec → test → code 順序，但缺少 Superpowers 風格的 plan-切-小-任務 + subagent 串接執行 |

**核心問題**：**code-team 解決「合不合格」（知識權威），但不解決「怎麼一步步走到合格」（流程紀律）**。產出品質仰賴使用者紀律和 agent 自願呼叫 — 這是 Superpowers 用 SessionStart hook + 鐵律措辭 + SDD 子代理串接漂亮解掉的問題。

### 1.2 Why now

- **monkey-skills marketplace 起穩定**：15 plugin shipped；plugin convention（3-lang README / flat subfolder / SSOT-and-functional-copy / marketplace description byte-identical）已成熟可直接 reuse
- **SSOT-and-functional-copy 機制已驗證**：`dev-workflow:complexity-critique` bundle `code-team` mindset、`legal-toolkit` Phase 1.10 用 `scripts/canonical/` + `distribute.py` + drift gate — Option A「自包含知識層」的工程基底已備齊
- **Superpowers v5.1.0 公開**：source 可直接學，但採 zero-dependency + 純英文 + 8-harness pluggin.json — 不適合直接 fork；需要本地化版本
- **個人 dogfood 累積**：5 個 toolkit（legal / investing / copywriting / gws / translation）+ domain-teams 5.6.0 累積的 code-team grounding 已經 ready，需要一個「主動建構」入口把它們組起來

### 1.3 Opportunity framing

> 給個人開發者（資料分析師 / App 設計師）一個 **process-discipline + canon-grounded 雙層的程式開發 toolkit**：上層是 Superpowers 風格的 7 階段工作流（brainstorm → plan → SDD → TDD 鐵律 → code-review → finish-branch）+ SessionStart hook 自動注入，下層是 code-team 八本書一級來源 grounding（Clean Code / Pragmatic / SOLID / Beck 2002 / Fowler 2018 / Feathers 2004 / OWASP ASVS / 徳丸本 Ch.6）做為 reviewer 評分依據。**讓 agent 不能用「我快速一下」鑽過去**，每一條鐵律都有 Beck 2002 Preface 級別的權威可引。

---

## 2. Target Users

### 2.1 Primary user

| 維度 | 值 |
|---|---|
| **角色** | 個人開發者 — 資料分析師 / App 設計師（kouko 本人 + 同類型開發者） |
| **規模** | 個人專案 / 小團隊（≤3 人） |
| **技術棧** | Python / TypeScript / Swift / SQL / dbt — 跨語言、不假設特定 framework |
| **使用情境** | Claude Code CLI（主力） / Codex CLI（次力） |
| **使用頻率** | 每個編碼 session（session-start hook 等於每天觸發 N 次） |

### 2.2 Secondary user

- 其他 monkey-skills 使用者 — 透過 marketplace 安裝
- 開源社群 — 想要 Superpowers UX 但需要中日多語 trigger + 一級書目 grounding 的開發者

### 2.3 誰決策 / 誰付費

- **決策者** = 使用者本人
- **付費** = 無（免費 open-source，monkey-skills marketplace 公開）
- **責任歸屬** = 使用者自負其責（Skills 是建議流程，最終決策仍在人）

### 2.4 Job Story

> 當我（個人開發者）打開 Claude Code 想加新功能，**我想要** session 啟動就被注入流程鐵律（不靠我主動呼叫 skill），agent 必須先 brainstorm 設計 → 切原子任務 → 每任務 SDD 三段審查（implementer / spec-reviewer / code-quality-reviewer），TDD 不能跳，**讓我** 不會在凌晨兩點看到 agent 寫了 600 行沒測試的 code 直接 commit。

---

## 3. Goals & Non-Goals

### 3.1 Goals (MVP v0.1.0)

| # | Goal | 衡量 |
|---|---|---|
| G1 | Plugin installable from monkey-skills marketplace（Claude Code + Codex CLI） | `/plugin install loom-code` 跑得通 + `using-loom-code` 出現在 skill 列表 + Codex CLI 也能載入 |
| G2 | SessionStart hook 自動注入 `using-loom-code`（不靠 agent 主動呼叫） | 開新 Claude / Codex session，第一條訊息送 "Let's add a feature to X" → agent 自動 trigger brainstorming（沒要寫 code） |
| G3 | TDD 鐵律生效 | 對 agent 下「跳過測試直接 implement」指令，agent 拒絕並引用 `tdd-iron-law` + Beck 2002 Preface |
| G4 | SDD 三段子代理串接跑通 | 給定一個 4-task plan，agent 自動 dispatch 12 個 subagent（4 × {implementer, spec-reviewer, code-quality-reviewer}）並回報 4 種狀態 |
| G5 | 知識層 SSOT-and-functional-copy 通過 drift gate | `loom-code/standards/*` 與 `domain-teams/skills/code-team/standards/*` byte-identical；`scripts/verify-drift.py` 綠燈 |
| G6 | 3-lang README + flat subfolder 通過 monkey-skills CI | `check-marketplace-description-sync.py` + `check-skill-structure.py` + `validate-skill-folder-structure.sh` 全綠 |

### 3.2 Non-Goals

| 非目標 | 為什麼拒絕 |
|---|---|
| ❌ 取代 `domain-teams:code-team` | code-team 並存 — 它是被動 gate 評分入口；loom-code 是主動建構入口。兩個用途不同 |
| ❌ 跨 7 個 harness（Gemini / Cursor / Copilot / OpenCode / Droid） | Phase 1-3 只做 Claude Code + Codex CLI；其他 harness 等使用者要求再加 |
| ❌ 自己重寫 8 本書的 standards | 走 SSOT-and-functional-copy：canonical 留在 `domain-teams:code-team/standards/`，loom-code 用 distribute.py 拷過來 |
| ❌ Visual brainstorming / brainstorm server（Superpowers 5.1.0 的新 feature） | Phase 4+；MVP 不做。Superpowers 自己也是後加的 |
| ❌ 取代 `dev-workflow:complexity-critique` | complexity-critique 已存在；loom-code 在 brainstorming 階段可選擇性引用，但不重複實作 |
| ❌ 取代 `dev-workflow:git-memory` | git-memory 已是 commit 前的 gate；loom-code `finishing-a-development-branch` 直接 delegate 過去 |
| ❌ 取代 `skill-dev-toolkit:skill-creator-advance` / `skill-judge` / `skill-refactor` | 那些是「寫 skill」的 meta toolkit；loom-code 是「寫 code」的 toolkit。不重疊 |
| ❌ 全套等同 Superpowers v5.1.0 的所有 skill（11 個） | MVP 只做 4 個；Phase 2-3 補到 9 個。`dispatching-parallel-agents` / `receiving-code-review` 列觀察名單 |

---

## 4. Differentiation vs Superpowers / code-team

### 4.1 對 Superpowers 的差異

| 維度 | Superpowers v5.1.0 | loom-code v0.1.0 (目標) |
|---|---|---|
| 語言 | 純英文 | 英文骨架 + 中日多語 trigger phrase（與 monkey-skills 慣例對齊） |
| Grounding | 不引書目，靠 measure 強度 | 每條鐵律附 Beck 2002 / Martin 2008 / Fowler 2018 章節引用 |
| Harness | 8 個（Claude / Codex / Cursor / Gemini / Copilot / OpenCode / Droid + Codex App） | 2 個（Claude Code + Codex CLI） |
| Knowledge layer | 無 | 8-source 一級來源 + JP preamble（character-encoding-security） |
| 治理模型 | Apache-style 嚴格 PR 政策（94% 拒絕率） | 個人 dogfood + monkey-skills marketplace 開放 |

### 4.2 對 `domain-teams:code-team` 的差異

| 維度 | `domain-teams:code-team` | loom-code |
|---|---|---|
| 入口模型 | 被動 — agent / 使用者主動呼叫 | 主動 — SessionStart hook 自動注入 |
| 主要產出 | gate verdict（PASS / NEEDS_REVISION） | 從 brainstorm 到 PR 的完整流程 artifact |
| 子代理使用 | worker + evaluator 兩角色 | implementer + spec-reviewer + code-quality-reviewer 三角色（Superpowers 風格） |
| Skill 數量 | 1 skill（code-team） | 4-9 skill（依 Phase） |
| 適用情境 | 已有產出要審查 | 從零開始的功能 / bug fix / refactor |

### 4.3 兩者並存的協作模式

```
使用者: "幫我加一個 feature X"
  ↓ session-start hook 注入 using-loom-code
loom-code:brainstorming → 探索意圖 → spec
loom-code:writing-plans → 切原子任務
loom-code:subagent-driven-development → 每任務 dispatch 3 subagent
  ↓ spec-reviewer / code-quality-reviewer 內部呼叫
  ↓ 載入 loom-code/standards/* (functional copy of code-team SSOT)
  ↓ 載入 loom-code/rubrics/quality-gate.md
  ↓ 評分 PASS / PASS_WITH_NOTES / NEEDS_REVISION
loom-code:finishing-a-development-branch → PR / merge
  ↓ 內部 delegate dev-workflow:git-memory commit gate
```

---

## 5. Risks & Mitigations

| 風險 | 影響 | Mitigation |
|---|---|---|
| **Drift**：code-team 改了 standards，loom-code 沒同步 | reviewer 用過時規則評分 | `scripts/verify-drift.py` CI gate（mirror legal-toolkit Phase 1.10 模式） |
| **Hook 干擾**：SessionStart hook 注入太多 token，每個 session 都付 cost | session 啟動慢 / token 成本 | hook 只注入 `hooks/router-card.md`（~600 tokens；0.24.0 起 SKILL.md 全文改由 Skill tool lazy load）；其他 skill 走 lazy load |
| **與既有 skill 衝突**：使用者也裝了 `obra/superpowers` | 雙 hook 同時注入；trigger 互搶 | README 明寫 conflict；提供 `loom-code-only-mode` env var |
| **Codex CLI plugin schema 變動**：OpenAI 更新 plugin spec | Codex 載入失敗 | Phase 1 只發 Claude Code；Phase 2 才 ship Codex variant 並寫 integration test |
| **「鐵律措辭」過度** | 使用者覺得煩；關掉 hook | measure 強度匹配真實壓測結果（Phase 1.5 dogfood）；提供 `--soft-mode` flag |
| **subagent context 爆掉** | 大任務切不夠細，SDD 失效 | `writing-plans` 強制每任務 ≤5 分鐘；implementer 回報 BLOCKED 時 fall back 切更細 |
| **與 `dev-workflow:complexity-critique` / `git-memory` 重疊** | 使用者搞混入口 | router skill `using-loom-code` 內附決策表，明示何時 delegate 出去 |

---

## 6. Success Metrics

### 6.1 v0.1.0 MVP

- ✅ `/plugin install loom-code` 在 Claude Code 跑得通
- ✅ SessionStart hook 注入率 100%（5 次新 session 測試）
- ✅ TDD 鐵律對抗測試：給 agent 5 個「跳過測試」誘導，5 次都拒絕
- ✅ SDD 對 4-task demo plan 跑完 0 stall
- ✅ verify-drift.py CI 綠燈
- ✅ 3-lang README 完整

### 6.2 v1.0.0 GA

- ✅ Codex CLI 也能完整跑（Q1 已選擇支援）
- ✅ 累積 ≥10 個個人 dogfood session 紀錄（`research/dogfood-*.md`）
- ✅ 至少一個外部使用者 issue / PR
- ✅ `domain-teams:code-team` 並存無回報衝突

---

## 7. Open Questions（v0.1.0-draft 未鎖）

| Q | 問題 | Phase |
|---|---|---|
| OQ-1 | TDD 鐵律 `--soft-mode` flag 怎麼實作？env var / 對話切換 / plugin config？ | Phase 1.5 |
| OQ-2 | systematic-debugging 是 MVP 必備還是 Phase 2 補？目前傾向 Phase 2 | Phase 2 |
| OQ-3 | brainstorming skill 要不要強制呼叫 `dev-workflow:complexity-critique` 做 deletion-first 檢查？ | Phase 2 |
| OQ-4 | finishing-a-development-branch 與 `dev-workflow:git-memory` 的呼叫順序：先 memory 還是先 finish？ | Phase 3 |
| OQ-5 | 是否提供 `loom-code-only-mode` env var 來關掉 hook（給已裝 Superpowers 的使用者）？ | Phase 1.5 |

---

## 8. Q-Lock（已鎖定決定）

| Q | 決定 | 理由 |
|---|---|---|
| Q1 (Harness) | **Claude Code + Codex CLI** | 比照 Superpowers 主力雙平台；不過度承諾 |
| Q2 (code-team 去留) | **並存** — loom-code 主動建構入口，code-team 被動 gate 入口 | 兩用途不衝突；不破壞既有 `dev-workflow:complexity-critique` 對 code-team mindset 的 SSOT 指向 |
| Q3 (啟動方式) | **先寫設計文件（PRODUCT-SPEC / TECH-SPEC / ROADMAP）** | 規模夠大需要先把 SSOT 邊界 / Phase 切分定下來，避免 Phase 1 蓋到一半發現要重做 |
| Q4 (工作位置) | **新開 git worktree `feat/loom-code-design`** | 不影響 main；後續 Phase 拆 PR 容易 |
| Q5 (Knowledge layer SSOT) | **SSOT 留 `domain-teams:code-team/standards/`；loom-code 用 `scripts/distribute.py` 拷 byte-identical functional copy** | 符合 monkey-skills 既有慣例（legal-toolkit Phase 1.10）；避免雙份維護 |
| Q6 (Skill naming) | **Superpowers 風格** — `using-loom-code` / `brainstorming` / `writing-plans` / `subagent-driven-development` / `tdd-iron-law` 等 | 使用者要求「使用方式類似 superpowers」 |
| Q7 (TDD 措辭強度) | **保留 Superpowers 的「Delete it. Start over.」措辭** + **附 Beck 2002 Preface 引用** | 雙重保險：行為層 + 知識層；既有牙齒也有依據 |
| Q8 (Subagent 角色) | **三角色** — implementer / spec-reviewer / code-quality-reviewer（沿用 Superpowers SDD） | 評分切面與 code-team gate file 對映（spec-reviewer → spec-consistency / code-quality-reviewer → quality-gate + arch-gate + security-checklist） |
