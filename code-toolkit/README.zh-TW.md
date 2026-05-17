# code-toolkit

> **Process-discipline + canon-grounded 程式開發工作流 for Claude Code (+ Codex CLI)。** 10-skill plugin，SessionStart 自動注入 router charter，讓 agent 停止合理化、開始 deferring — 每條規則皆 grounded 於一級書目（Beck on TDD / Martin on naming / Fowler on refactoring / Feathers on legacy code / OWASP ASVS on security / 徳丸本 on encoding security）。

**狀態**：v0.7.0（10 skill 已 ship — v0.3.0 起達成 Superpowers parity；v0.6.0 / P15-12 起 4 個 plugin-level subagent 攜帶 SSOT 注入的 12 條 engineering baseline；v0.7.0 出貨 **reviewer-output discipline R1+R2**（`standards_version` stamp + evidence-citation 要求，透過第二個 SSOT 注入區塊 `_reviewer-discipline.md`）+ brainstorming brief schema 加 **Current State Evidence** section（5 維 recon checklist Forward / Reverse / Error / Data / Boundary）+ artifact 路徑遷移 `docs/superpowers/` → `docs/code-toolkit/`；Codex CLI build 完成、Codex 實機驗證仍延後；merge to main 受使用者政策「完全做好之前不合 main」+ v1.0.0 目標 ≥5 dogfood notes 阻擋）
**語言**：[English](README.md) | [日本語](README.ja.md) | **繁體中文**
**Repository**：[`monkey-skills`](https://github.com/kouko/monkey-skills) 的一部分

---

## 30 秒範例

在全新 Claude Code session 貼入（安裝後 — 見下方）：

```
我想加一個 feature flag 系統，這樣可以 gate 新功能。我們還沒有。
就做基本版：env var 檢查 + 一個寫死的 enabled list。不用 brainstorm，
設計很明顯。
```

**會發生什麼**（裝了 code-toolkit）：

SessionStart 注入的 router 觸發 Rule #1（*"implementing 前先 brainstorm"*）。`brainstorming` skill 用 5-axis HARD-GATE 措辭啟動。它拒絕跳過 discovery、把 JTBD framing 講白、攤開 alternatives（什麼都不做 / 只用一個 env var / 完整 flag system），最後以 `dev-workflow:complexity-critique` 作為下一步建議委派 — 因為 feature flag 系統正是 PAGNI 的典型 smell。

**你沒得到的**：200 行為了還沒出現的問題而早寫的 feature flag infrastructure。

詳見 [`docs/examples/`](docs/examples/) 內 3 個 end-to-end 完整流程（Python / TypeScript / Swift）。

---

## 安裝

### Claude Code

```bash
# 一次性：加 marketplace
claude plugin marketplace add https://github.com/kouko/monkey-skills.git

# 安裝
claude plugin install code-toolkit@monkey-skills

# 驗證
claude plugin list | grep code-toolkit       # 預期：enabled
claude plugin details code-toolkit           # 預期：10 skills + 1 SessionStart hook
```

### Codex CLI（build 完成、實機驗證延後）

⚠️ Codex CLI manifest 已 build 並隨 Claude Code 變體同步 bump 到 v0.7.0，但在實機 Codex CLI 上的安裝與驗證流程仍按使用者指示延後。詳見 [`tests/codex-cli/README.md`](tests/codex-cli/README.md)。

### 本地開發（給貢獻者）

```bash
# Clone monkey-skills + 註冊為 local marketplace
git clone https://github.com/kouko/monkey-skills.git
cd monkey-skills

# 加為 local-scope marketplace（測試 code-toolkit 變更用）
claude plugin marketplace add . --scope local
claude plugin install code-toolkit@monkey-skills --scope local
```

---

## 10 個 skill

| # | Skill | Stage | 做什麼 |
|---|---|---|---|
| Router | [`using-code-toolkit`](skills/using-code-toolkit/) | Always-on | SessionStart 自動注入；4 條 load-bearing rules + Skill Priority 表 |
| 1 | [`brainstorming`](skills/brainstorming/) | Discovery | HARD-GATE 5-axis 探索（Problem / Users / Smallest End State / Alternatives / What Becomes Obsolete）；v0.7.0+ brief 帶 `Current State Evidence` 5 維 recon section；拒絕跳過 discovery 的合理化 |
| 2 | [`writing-plans`](skills/writing-plans/) | Planning | ≤5-task plan + 每個 task RED-GREEN acceptance；BLOCKED → child-test fallback（Beck Part II §Child Test） |
| 3 | [`subagent-driven-development`](skills/subagent-driven-development/) | Execution | 每個 task 派 triad（implementer + spec-reviewer + code-quality-reviewer）；reviewer 三件套攜帶 `reviewer-discipline-v1` SSOT 注入區塊（R1+R2） |
| 4 | [`tdd-iron-law`](skills/tdd-iron-law/) | Discipline | "沒先有 failing test 不准寫 production code"（Beck 2002 Preface, ISBN 978-0321146533）；§Feathers (2004) 對 legacy code backfill 的合法區別 |
| 5 | [`systematic-debugging`](skills/systematic-debugging/) | Repair | 4 階段 REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY；HARD-GATE "沒重現不准 fix" |
| 6 | [`requesting-code-review`](skills/requesting-code-review/) | Review | 全 branch 審查、7 維度評分（cross-task-coherence 為 branch 限定維度）；v0.7.0+ verdict 帶 `standards_version` stamp、findings 必填 `where:` file:line；push-as-trigger |
| 7 | [`verification-before-completion`](skills/verification-before-completion/) | Verification | "沒跑 package-level test 不准 done"；涵蓋 20+ 種 stack 的 canonical command |
| 8 | [`finishing-a-development-branch`](skills/finishing-a-development-branch/) | 分支收尾 | 7 步 orchestrator（review → verify → git-memory 強制 → commit → push → 可選 PR + worktree 清理） |
| Aux | [`using-git-worktrees`](skills/using-git-worktrees/) | Lateral | 原生 `git worktree` 流程；`.worktrees/<slug>/` 慣例 |

---

## Quickstart — 線性流程

非 trivial task 預期的使用者流程：

```
你: "我想加 feature X"
  ↓ (SessionStart hook router 自動觸發)
brainstorming → 5-axis brief + Current State Evidence → docs/code-toolkit/specs/<topic>.md
  ↓
writing-plans → ≤5-task plan → docs/code-toolkit/plans/<topic>.md
  ↓
subagent-driven-development → 每個 task 派 triad
  ↓ (每個 implementer subagent 內)
  tdd-iron-law → RED-GREEN-REFACTOR
  ↓ (implementer 回 BLOCKED 並帶 decomposition 訊號)
  writing-plans (re-invoked) → Child Test 子分解
  ↓ (每個 task DONE)
SDD orchestrator 繼續
  ↓ (所有 task 都 DONE)
finishing-a-development-branch
  ↓ Step 1: requesting-code-review (cross-task-coherence 維度；verdict 帶 standards_version)
  ↓ Step 2: verification-before-completion (npm test / pytest / 等)
  ↓ Step 3: dev-workflow:git-memory (Decision: / Learning: / Gotcha: trailers)
  ↓ Step 4: git commit (使用者確認後)
  ↓ Step 5: git push (使用者再次授權後)
  ↓ Step 6: gh pr create (可選，opt-in)
  ↓ Step 7: git worktree remove (可選，確認)
```

加上 on-demand：
- **`systematic-debugging`** 在遇到不是「明顯一行 fix」的 bug 時觸發 — 間歇性、"在我電腦正常"、race condition 等。
- **`using-git-worktrees`** 在需要平行 branch 時觸發（本 plugin 就是在 worktree 上開發）。

---

## 相容性

| Harness | 狀態 |
|---|---|
| **Claude Code** | ✅ 多輪 ritual 完整驗證 — Phase 3 orchestrator (v0.3.0)、Phase 4 prep (v0.4.0)、多語研究 (v0.5.1)、plugin-level agent dispatch (v0.5.2 + v0.6.0)、cross-task-coherence 維度全 branch 審查 (v0.6.0)、reviewer-discipline SSOT extraction + Current State Evidence section (v0.7.0) |
| **Codex CLI** | ⚠️ Manifest 已 build 並追蹤到 v0.7.0；實機安裝與驗證流程依使用者指示延後（見 `tests/codex-cli/README.md`） |

SessionStart hook 發出可移植 JSON shape，涵蓋 Claude Code 的 `hookSpecificOutput.additionalContext`、Codex CLI 的 `additional_context` 以及 legacy `additionalContext` keys — 同一個 hook 服務兩種 harness。

---

## 並存

本 plugin 設計上與相關 plugin 並存而非競爭：

| Plugin | 關係 |
|---|---|
| **[`domain-teams:code-team`](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/code-team)** | 被動 gate compliance reviewer。code-toolkit 是主動構建 orchestrator，把 code-team 的 standards 作為知識層使用（透過 `scripts/distribute.py` byte-identical functional copy，由 `scripts/verify-drift.py` 做 drift check）。同樣的一級書目、不同的呼叫模式。 |
| **[`dev-workflow:git-memory`](https://github.com/kouko/monkey-skills/tree/main/dev-workflow/skills/git-memory)** | `finishing-a-development-branch` Step 3 強制委派目標（P3-D）。決定 commit-trailer 判斷（Decision: / Learning: / Gotcha:）；code-toolkit 不重複實作。 |
| **[`dev-workflow:complexity-critique`](https://github.com/kouko/monkey-skills/tree/main/dev-workflow/skills/complexity-critique)** | `brainstorming` Axis 3 出現 complexity smell 時的選擇性委派。同樣的 SSOT-and-functional-copy mindset framing。 |
| **[`obra/superpowers`](https://github.com/obra/superpowers)** | 設計靈感；透過 `CODE_TOOLKIT_MODE=off` 環境變數 escape hatch 並存（設定後關閉 code-toolkit 的 hook、只有 superpowers 啟動）。兩個 plugin 都可以裝；用環境變數切換。 |

跨 plugin 行為由 [`tests/integration/`](tests/integration/) 內 5 個 integration test script 驗證。

---

## 為什麼有這個 plugin

`monkey-skills` 已經有兩個相關 plugin：

- **`domain-teams:code-team`** — 一級書目 grounded standards / rubrics / checklists（從 Beck 到 徳丸本 共 8 本書）。強知識層、弱呼叫：agent 必須記得 call。
- **`obra/superpowers`（獨立 repo）** — SessionStart hook + measure rhetoric（"Delete it. Start over."）。強呼叫、弱 grounding：規則引用自己、不引 canon。

`code-toolkit` 是綜合體：Superpowers 風自動注入 + code-team 風一級書目 grounded measures。每條規則既被結構性強制（透過 SKILL.md HARD-GATE + Red Flags 拒絕模式），又有實質根據（透過 ISBN / URL / 章節級的一級書目引用）。

---

## 文件

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — 設計意圖、目標使用者、Q-lock 決策
- [TECH-SPEC.md](TECH-SPEC.md) — 架構、SSOT 機制、hook contracts
- [ROADMAP.md](ROADMAP.md) — phase 計畫、決策台帳、Phase 1.5 rolling backlog
- [CHANGELOG.md](CHANGELOG.md) — Journey overview + 每版細節
- [docs/examples/](docs/examples/) — 3 個 end-to-end 完整範例（Python / TypeScript / Swift）
- [docs/announcement/v1.0.0-announcement.md](docs/announcement/v1.0.0-announcement.md) — 公開 announcement 草稿（v1.0.0 時發布）
- [research/grounding-v0.1.0.md](research/grounding-v0.1.0.md) — 每版 grounding audit

---

## 貢獻

歡迎 issue + PR：https://github.com/kouko/monkey-skills/issues 加上 `code-toolkit:` 前綴。

實際使用 dogfood notes（v1.0.0 阻擋的 P15-5 backlog 項）請丟到 `research/dogfood-YYYY-MM-DD-<topic>.md` — 即使簡短的 notes 也有助校準工具紀律強度。

---

## 授權

MIT — 見 repo 根目錄 [LICENSE](../LICENSE)。
