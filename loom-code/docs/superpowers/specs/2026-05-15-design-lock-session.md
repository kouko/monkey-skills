# 2026-05-15 — loom-code Design Lock Session

> **Type**: Session handoff + decision rationale archive
> **Status**: Phase 0 complete — PRODUCT/TECH/ROADMAP locked, awaiting Phase 1 build
> **Branch**: `feat/loom-code-design`
> **Worktree**: `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/`
> **Purpose**: Capture the conversation arc, decision rationale, and pickup instructions for the next session

---

## 1. How we got here

### 1.1 Origin

Started with a research request to compare:
- `obra/superpowers` — process-discipline framework (SessionStart hook + skill auto-trigger + subagent串接)
- `kouko/monkey-skills/domain-teams/skills/code-team` — canon-grounded framework (8 primary sources + MUST/SHOULD/MAY gates)

Output: `<vault>/research/2026-05-15 Superpowers vs code-team 架構比較研究.md` — concluded the two are **complementary, not competing**:
- Superpowers = 「**流程紀律**」(process as truth)
- code-team = 「**原典權威**」(canon as truth)
- Superpowers 解「怎麼走」；code-team 解「走完合不合格」

### 1.2 The pivot question

After the comparison, user asked: 「**是否有可能依照當前 monkey-skill 專案的模式，做一個 loom-code plugin，整合 superpowers 與 code-team 兩方的優點，使用方式類似 superpowers 的工具？**」

Reply offered 3 design options:
- **Option A**: Standalone `loom-code/` with full knowledge layer self-contained
- **Option B**: Extend `domain-teams/` in place + add hooks
- **Option C**: Thin wrapper plugin, SSOT stays in `code-team`

User picked **Option A**.

### 1.3 Q1-Q4 lock (asked via AskUserQuestion)

| Q | Asked | Answered |
|---|---|---|
| Q1 | Harness scope? (1 / 2 / 全 7) | **Claude Code + Codex CLI** |
| Q2 | domain-teams:code-team 去留? | **並存**（主動 vs 被動入口） |
| Q3 | 啟動方式? (PoC / 全骨架 / 設計文件) | **先寫設計文件** |
| Q4 | 工作位置? (現場 / vault draft / worktree) | **新開 worktree** |

### 1.4 Worktree placement correction

First worktree was created at `/Users/kouko/GitHub/monkey-skills-loom-code/` (sibling layout — git's default). User expected `.worktrees/` subdirectory layout. Checked `.gitignore` — already had `.worktrees/` (plural) rule pre-configured. Moved worktree to current location.

---

## 2. The 8 Q-locks (PRODUCT-SPEC §8)

| Q | 決定 | WHY (rationale beyond the table) |
|---|---|---|
| **Q1** Harness | Claude Code + Codex CLI | Superpowers 自家也是雙平台主力；不過度承諾。Phase 1 只 ship Claude；Codex 排 Phase 2.5 |
| **Q2** code-team 並存 | 並存（不 deprecate） | Mental model 不同 — loom-code = 主動建構入口（從零）；code-team = 被動 gate 入口（已產出）。不衝突 |
| **Q3** 啟動方式 | 先寫設計文件 | 規模夠大（9 skill + hook + SSOT 機制）需先把邊界定下，避免 Phase 1 蓋到一半發現要重做 |
| **Q4** 工作位置 | worktree `feat/loom-code-design` | 隔離 main；後續可拆 PR；user 偏好放 `.worktrees/` 子目錄（已配置 `.gitignore`） |
| **Q5** Knowledge SSOT | SSOT 留 `code-team/`；functional copy via `distribute.py` | 符合既有慣例（legal-toolkit Phase 1.10、complexity-critique-and-mindset）— 雙份維護是地雷 |
| **Q6** Skill naming | Superpowers 風格 | 使用者明確要求「使用方式類似 superpowers」；命名一致才能複用 Superpowers UX 直覺 |
| **Q7** TDD 措辭強度 | Superpowers measure **+** Beck 2002 Preface ISBN 直接引文 | 雙重保險：行為層 + 知識層。既保留「Delete it. Start over.」的牙齒，又用「Beck 2002 Preface 說的」取代「because the skill says so」的權威空洞 |
| **Q8** Subagent 角色 | 3 角色（implementer / spec-reviewer / code-quality-reviewer） | Superpowers 自家驗證過；3 個切面剛好對映 code-team 3 個 gate（spec-consistency / quality-gate / arch-gate+security） |

---

## 3. Architectural commitments（不要在 Phase 1 重新討論）

### 3.1 雙層架構（TECH-SPEC §2.2）

```
Process Layer (loom-code native — Superpowers-style)
  using-loom-code, brainstorming, writing-plans, SDD,
  tdd-iron-law, systematic-debugging, code-review,
  verification-before-completion, using-git-worktrees,
  finishing-a-development-branch
                    ↓
Knowledge Layer (SSOT-and-functional-copy from code-team)
  standards/× 7, rubrics/× 2, checklists/× 2
                    ↑
  Canonical SoT: domain-teams/skills/code-team/
  Drift gate: loom-code/scripts/verify-drift.py
```

### 3.2 SessionStart hook 預算

`using-loom-code/SKILL.md` ≤ **2000 tokens**（hook 注入預算限制）。其他 skill 全部 lazy load via `Skill` tool。

### 3.3 Cross-plugin delegation 契約

| Source (loom-code) | Target | Trigger |
|---|---|---|
| `finishing-a-development-branch` | `dev-workflow:git-memory` | commit gate（必呼） |
| `brainstorming` | `dev-workflow:complexity-critique` | 複雜度疑慮（建議） |
| `brainstorming` | `dev-workflow:proposal-critique` | 多方案 triage（建議） |
| `requesting-code-review` | `domain-teams:code-team` | 既有大產出要 audit（可選） |

### 3.4 與 obra/superpowers 並存

衝突點：雙 SessionStart hook + skill 名稱重疊。Resolution: `LOOM_CODE_MODE=off` env var 退場。

---

## 4. What's NOT decided yet（Phase 1 build 時鎖）

從 PRODUCT-SPEC §7 + TECH-SPEC §9 合併：

| ID | 問題 | When |
|---|---|---|
| OQ-1 / TQ-2 | TDD `--soft-mode` flag 如何實作？implementer subagent prompt 是否強制呼叫 tdd-iron-law？ | Phase 1.5 dogfood 後 |
| OQ-2 | systematic-debugging 排 Phase 1 還 Phase 2？目前 Phase 2 | Phase 2 開工前 |
| OQ-3 | brainstorming 是否強制 delegate complexity-critique？ | Phase 2 |
| OQ-4 | finishing-a-development-branch ↔ git-memory 呼叫順序？ | Phase 3 |
| OQ-5 | `LOOM_CODE_MODE` env var 實作位置？ | Phase 1.5 |
| TQ-1 | distribute.py = push（手動）or pre-commit hook？ | Phase 1 build 階段 |
| TQ-3 | Codex CLI hook JSON shape 與 Claude Code 完全相容嗎？ | Phase 2.5 |
| TQ-4 | dispatching-parallel-agents 要不要做？ | Phase 3+ |
| TQ-5 | receiving-code-review 是否與 git-memory 重疊？ | Phase 3 |
| TQ-6 | verification-before-completion 與 tdd-iron-law 切割？ | Phase 3 |
| TQ-7 | scripts 用 PEP 723 還是純 stdlib？ | Phase 1 build 階段（傾向 stdlib） |

---

## 5. Next session pickup

### 5.1 Files to read FIRST

```
loom-code/PRODUCT-SPEC.md   ← 商業 / 使用者 / Q-lock × 8
loom-code/TECH-SPEC.md      ← 架構 / SSOT / hooks / interface 契約
loom-code/ROADMAP.md        ← Phase 0-4 計畫 / Decision Ledger
loom-code/docs/superpowers/specs/2026-05-15-design-lock-session.md  ← THIS FILE
```

### 5.2 First task: Phase 1 build (v0.1.0 MVP shell)

**Scope**: 3 skill + hook + SSOT scripts. 6-8 工作天估算。

**順序建議**（不在 ROADMAP 內，是這次 session 對話結尾的補充）:

1. **PoC `using-loom-code/SKILL.md`** — 控制 ≤2000 tokens；包含 Red Flags 表 + Skill Priority + 中日英 trigger
2. **PoC `hooks/session-start` + `hooks/hooks.json`** — bash 注入 + JSON 雙 key（Claude Code + Codex 兼容）
3. **Verify hook in fresh session** — 開新 Claude Code session，確認 hook 真的注入了 using-loom-code
4. **`tdd-iron-law/SKILL.md`** — Superpowers measure + Beck 2002 Preface 直接引文 + ISBN
5. **`tdd-iron-law/standards/tdd-standard.md`** — functional copy from code-team
6. **`scripts/distribute.py` + `scripts/verify-drift.py`** — stdlib only；先 PoC 一個檔案的 sync
7. **`subagent-driven-development/SKILL.md` + 3 agent prompts** — implementer / spec-reviewer / code-quality-reviewer
8. **SDD 全部 standards/rubrics/checklists functional copy** — 跑 distribute.py 一次到位
9. **5 個 skill-triggering prompt + 5 個 TDD pressure prompt** — `tests/` 目錄
10. **CHANGELOG.md v0.1.0 條目**

### 5.3 Acceptance criteria（從 ROADMAP §Phase 1）

- `/plugin install loom-code` 在 Claude Code 跑得通
- 開新 session → `using-loom-code` 自動載入（hook 生效）
- 對 agent 下「跳過測試直接 implement」誘導 × 5 → 5/5 拒絕並引 Beck 2002
- 對 agent 下 4-task plan → SDD 啟動 12 個 subagent → 全綠
- `scripts/verify-drift.py` 綠燈
- monkey-skills CI 全綠

### 5.4 Suggested kickoff prompt（複製貼給新 session）

```
我要繼續開發 loom-code plugin（monkey-skills marketplace 新 plugin）。

請先讀這 4 份文件，理解 Phase 0 已鎖定的決策：
1. loom-code/PRODUCT-SPEC.md
2. loom-code/TECH-SPEC.md
3. loom-code/ROADMAP.md
4. loom-code/docs/superpowers/specs/2026-05-15-design-lock-session.md ← 這份是 handoff，先讀！

讀完後：
- 確認你理解 Q1-Q8 鎖定的決策（不要重新討論）
- 確認你理解雙層架構（process layer + knowledge layer SSOT）
- 確認你理解與 domain-teams:code-team / dev-workflow / obra/superpowers 的並存契約

然後進入 Phase 1 build。建議順序見 handoff §5.2。
我們從 hook + using-loom-code/SKILL.md PoC 開始。
```

---

## 6. Things this session deliberately did NOT do

避免新 session 重做：

- ❌ 重新討論 Option A vs B vs C — 已選 A
- ❌ 重新討論 harness 範圍 — 已鎖 Claude Code + Codex
- ❌ 重新討論 SSOT 位置 — 已鎖 code-team 為 canonical
- ❌ 重新討論 skill naming — 已鎖 Superpowers 風格
- ❌ 直接動手寫 `using-loom-code/SKILL.md` — Phase 0 只做設計
- ❌ ship 任何 functional copy — Phase 1 才跑 distribute.py
- ❌ commit 任何檔案 — 等使用者 review 完設計才 commit

---

## 7. Files created in this session

```
loom-code/
├── PRODUCT-SPEC.md                          (Phase 0 deliverable)
├── TECH-SPEC.md                             (Phase 0 deliverable)
├── ROADMAP.md                               (Phase 0 deliverable)
├── README.md  README.ja.md  README.zh-TW.md (Phase 0 deliverable, 3-lang)
├── .claude-plugin/plugin.json               (v0.1.0-draft skeleton)
├── .codex-plugin/plugin.json                (v0.1.0-draft skeleton)
├── scripts/canonical/README.md              (SSOT pointer, 12 functional-copy mapping)
└── docs/superpowers/specs/
    └── 2026-05-15-design-lock-session.md    (THIS FILE)
```

Total: 10 files. 0 commits.

---

## 8. Related external context

- Comparison research (vault): `<vault>/research/2026-05-15 Superpowers vs code-team 架構比較研究.md`
- Superpowers upstream: `https://github.com/obra/superpowers` @ v5.1.0
- code-team SSOT: `<repo>/domain-teams/skills/code-team/` @ domain-teams v5.6.0
- Existing toolkit precedents:
  - `legal-toolkit/` Phase 1.10 — SSOT-and-functional-copy via `scripts/canonical/` + `distribute.py` + `verify-drift.py`
  - `dev-workflow/skills/complexity-critique/` — mindset functional copy from code-team
