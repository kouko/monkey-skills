# TECH-SPEC — code-toolkit

> **Owner**: code-team (technical contract — module / data-flow / interface / SSOT)
> **Companion**: [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — business + design direction (planning-team owned)
> **Source of design**: `<obsidian-vault>/research/2026-05-15 Superpowers vs code-team 架構比較研究.md`
> **Roadmap**: [ROADMAP.md](ROADMAP.md)

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1.0-draft | 2026-05-15 | kouko | Initial spec — 2-layer (process / knowledge) + SSOT-and-functional-copy from `domain-teams:code-team` + dual-harness (Claude Code + Codex CLI) |
| 0.6.0 | 2026-05-16 | kouko | **Agent-layer migration** (P15-12 Phase 1+2): subagent prompts moved from per-skill `skills/<skill>/agents/*-prompt.md` (original layout below) to plugin-level `code-toolkit/agents/*.md`. 4 plugin-level agents (`implementer` / `spec-reviewer` / `code-quality-reviewer` / `code-reviewer`) each carry the 12-rule engineering baseline injected from SSOT at `scripts/_baseline.md` via `scripts/distribute.py`. Dispatch via `Agent({subagent_type: "code-toolkit:<role>"})`. §2.1, §2.4, §3.3, §3.4 below updated to reflect current layout; rationale in CHANGELOG v0.5.2 + v0.6.0 entries. |

---

## 1. Scope & Constraints

### 1.1 Delivery form

- monkey-skills marketplace plugin: `code-toolkit/` 一個目錄
- 兩份 plugin manifest：
  - `.claude-plugin/plugin.json`（Claude Code 用）
  - `.codex-plugin/plugin.json`（Codex CLI 用；schema 比照 Superpowers v5.1.0）
- 加入 repo-level `.claude-plugin/marketplace.json` 條目，description byte-identical 與 `plugin.json`
- 3-lang README（en / ja / zh-TW）on plugin root + 每個 skill 內

### 1.2 Goals (技術目標；PRODUCT-SPEC §3.1 對映)

| # | 技術目標 | 對映 PRODUCT-SPEC Goal |
|---|---|---|
| T1 | 雙 plugin.json + marketplace.json 條目 + 3-lang README + flat subfolder 通過 monkey-skills CI | G1, G6 |
| T2 | SessionStart hook bash 腳本注入 `using-code-toolkit/SKILL.md` 全內容 | G2 |
| T3 | `tdd-iron-law` skill 嵌入 Beck 2002 Preface 引用 + Superpowers measure 措辭，agent 拒絕「跳測試」誘導 | G3 |
| T4 | `subagent-driven-development` skill 含 3 個 prompt 檔（implementer / spec-reviewer / code-quality-reviewer） | G4 |
| T5 | `scripts/canonical/` SSOT + `scripts/distribute.py` + `scripts/verify-drift.py` 跑通 | G5 |
| T6 | `using-code-toolkit` 出現在 SKILL 列表 + 全 SKILL.md ≤6000 tokens | G6 |

### 1.3 Non-Goals (技術層面)

| 非目標 | 為什麼 |
|---|---|
| ❌ Vector embedding / RAG | 8 條 standards 直接內嵌；不需要 |
| ❌ Custom UI / Web app | CLI-native；host 提供 UI |
| ❌ DB | 純 markdown + bash hook |
| ❌ Server / API hosting | 完全 local-FS-first |
| ❌ 自寫 LLM client | host runtime 處理 |
| ❌ Scripts/*.py 主要邏輯 | 主要邏輯都在 SKILL.md instructions；scripts 只做 distribute / verify-drift / canonical sync |
| ❌ Brainstorm WebSocket server（Superpowers 5.1.0 visual brainstorming） | Phase 4+；MVP 不做 |
| ❌ Test fixtures 包真實程式碼 | Phase 1 用 prompt scenarios（mirror Superpowers `tests/skill-triggering/`） |

### 1.4 Hard constraints

- **Anthropic skill folder convention**：`<skill>/<subfolder>/` 內不可再開 subfolder；CLAUDE.md `validate-skill-folder-structure.sh` 擋
- **CLAUDE.md commit type whitelist**：`refactor / feat / fix / chore / docs / test`；scope kebab-case
- **3-lang README convention（PR #150）**：plugin root + per-skill 都要 en / ja / zh-TW
- **Marketplace description byte-identical**：`marketplace.json` 內 description ↔ `.claude-plugin/plugin.json` description 必須 byte-identical
- **SSOT-and-functional-copy convention**：canonical sources 留 `domain-teams:code-team/standards/`；code-toolkit `standards/` 是 byte-identical functional copy。`scripts/verify-drift.py` CI gate
- **Visibility Convention（skill-team v5.2.0+）**：dispatching multi-phase work 的 agent prompt 需 `TaskUpdate` 心跳（≤60s）

---

## 2. Architecture

### 2.1 Plugin layout

```
code-toolkit/
├── .claude-plugin/
│   └── plugin.json                    # Claude Code manifest
├── .codex-plugin/
│   └── plugin.json                    # Codex CLI manifest (Superpowers schema)
├── PRODUCT-SPEC.md
├── TECH-SPEC.md
├── ROADMAP.md
├── README.md
├── README.ja.md
├── README.zh-TW.md
├── CHANGELOG.md
├── hooks/
│   ├── hooks.json                     # SessionStart registration
│   └── session-start                  # bash: inject using-code-toolkit
├── scripts/
│   ├── canonical/                     # pointers, NOT byte copies
│   │   └── README.md                  # explains SSOT-and-functional-copy
│   ├── distribute.py                  # pull from domain-teams:code-team/standards/ → skills/*/standards/
│   ├── verify-drift.py                # CI gate: byte-identical check
│   └── README.md
├── docs/
│   └── code-toolkit/                  # plugin-namespaced artifact dir
│       ├── plans/                     # implementation plans (writing-plans output)
│       ├── specs/                     # design docs (brainstorming output)
│       └── audits/                    # dogfood audit notes
├── tests/
│   ├── skill-triggering/              # prompt scenarios (mirror Superpowers)
│   │   └── prompts/
│   └── tdd-iron-law-pressure/         # 5 "skip TDD" induction prompts
├── research/
│   └── grounding-v0.1.0.md            # version-by-version grounding rationale
└── skills/
    ├── using-code-toolkit/            # ROUTER (loaded by SessionStart hook)
    │   ├── SKILL.md
    │   ├── README.md / .ja.md / .zh-TW.md
    │   └── references/
    │       ├── codex-tools.md         # tool mapping for Codex CLI
    │       └── claude-code-tools.md   # canonical names
    ├── tdd-iron-law/                  # TDD with Beck 2002 grounding + Superpowers measure
    │   ├── SKILL.md
    │   ├── standards/
    │   │   └── tdd-standard.md        # functional copy of code-team/standards/tdd-standard.md
    │   ├── references/
    │   │   └── testing-anti-patterns.md
    │   └── README × 3
    ├── subagent-driven-development/
    │   ├── SKILL.md
    │   ├── rubrics/                   # functional copies from code-team
    │   │   ├── quality-gate.md
    │   │   └── arch-gate.md
    │   ├── checklists/
    │   │   ├── security-checklist.md
    │   │   └── spec-consistency.md
    │   ├── standards/                 # functional copies (full 7-file set)
    │   │   ├── naming-and-functions.md
    │   │   ├── pragmatic-principles.md
    │   │   ├── solid-principles.md
    │   │   ├── tdd-standard.md
    │   │   ├── refactoring-standard.md
    │   │   ├── app-security-standard.md
    │   │   └── character-encoding-security.md
    │   └── README × 3
    └── (Phase 2-3 added: brainstorming / writing-plans / systematic-debugging /
          requesting-code-review / verification-before-completion /
          using-git-worktrees / finishing-a-development-branch — all shipped)

  # Plugin-level layer (added v0.5.2 + v0.6.0 per P15-12)
  agents/                              # plugin-level subagents (cross-plugin reusable)
    implementer.md                     # role contract + injected 12-rule baseline
    spec-reviewer.md
    code-quality-reviewer.md
    code-reviewer.md
  scripts/
    _baseline.md                       # SSOT — 12-rule engineering baseline
    distribute.py                      # injects _baseline.md into each agent's BEGIN/END block
    verify-drift.py                    # CI gate on SSOT integrity
```

### 2.2 Two-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Process Layer (code-toolkit native)                    │
│  ─────────────────────────────                          │
│  using-code-toolkit (router + SessionStart entry)       │
│  brainstorming      writing-plans     SDD               │
│  tdd-iron-law       systematic-debugging                │
│  requesting-code-review                                 │
│  verification-before-completion                         │
│  using-git-worktrees                                    │
│  finishing-a-development-branch                         │
│                                                         │
│  ▼ reviewer subagent loads standards from ▼            │
├─────────────────────────────────────────────────────────┤
│  Knowledge Layer (SSOT-and-functional-copy)             │
│  ─────────────────────────────                          │
│  standards/      (7 files, byte-identical to code-team) │
│  rubrics/        (quality-gate, arch-gate)              │
│  checklists/     (security, spec-consistency)           │
│                                                         │
│  ▲ verify-drift.py CI gate ▲                           │
│  ▲ canonical SSOT: domain-teams/skills/code-team/      │
└─────────────────────────────────────────────────────────┘
```

### 2.3 SessionStart hook 機制

```bash
# hooks/hooks.json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/session-start\"",
            "async": false
          }
        ]
      }
    ]
  }
}
```

```bash
# hooks/session-start (Superpowers-style bash)
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Read using-code-toolkit content
content=$(cat "${PLUGIN_ROOT}/skills/using-code-toolkit/SKILL.md")

# JSON-escape (fast path: bash parameter substitution)
escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}
escaped=$(escape_for_json "$content")
context="<EXTREMELY_IMPORTANT>\nYou have code-toolkit.\n\n${escaped}\n</EXTREMELY_IMPORTANT>"

# Emit JSON with both Claude Code (hookSpecificOutput.additionalContext)
# and Codex CLI (additional_context) keys for portability.
cat <<EOF
{
  "hookSpecificOutput": {"additionalContext": "${context}"},
  "additional_context": "${context}",
  "additionalContext": "${context}"
}
EOF
```

> [!important] Hook 大小控制
> `using-code-toolkit/SKILL.md` 必須控制在 ~2000 tokens 以內，避免每個 session 都被注入大量 context。其他 skill 透過 `Skill` tool 走 lazy load。

### 2.4 Subagent 串接資料流

As of v0.6.0, all subagents are **plugin-level** — dispatch via
`Agent({subagent_type: "code-toolkit:<role>"})`. Each agent file at
`code-toolkit/agents/<role>.md` carries role contract + the 12-rule
engineering baseline (injected from SSOT at `scripts/_baseline.md`).

```
code-toolkit:implementer   (agents/implementer.md)
  Input: task text + context paths + standards paths
  Output: code + test commits + status (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED)

code-toolkit:spec-reviewer   (agents/spec-reviewer.md)
  Input: artifact + spec path + checklists/spec-consistency.md
  Output: PASS / NEEDS_REVISION + gap list

code-toolkit:code-quality-reviewer   (agents/code-quality-reviewer.md)
  Input: artifact + rubrics/quality-gate.md + rubrics/arch-gate.md +
         checklists/security-checklist.md + all 7 standards/
  Output: PASS / PASS_WITH_NOTES / NEEDS_REVISION + 6-dimension scores + flags

code-toolkit:code-reviewer   (agents/code-reviewer.md) — whole-branch scope
  Input: branch diff + same rubrics + checklists + standards as above
  Output: PASS / PASS_WITH_NOTES / NEEDS_REVISION + 7-dimension scores
          (adds cross-task-coherence dimension unique to branch scope)
```

Reviewer 角色封閉（CLAUDE.md 慣例）：**只產 verdict 不修 artifact**。修訂由 implementer 接力重跑。

### 2.5 SSOT-and-functional-copy 機制

```
domain-teams/
└── skills/
    └── code-team/
        ├── standards/           ← CANONICAL SoT
        │   ├── naming-and-functions.md
        │   ├── ...
        ├── rubrics/             ← CANONICAL SoT
        ├── checklists/          ← CANONICAL SoT
        └── protocols/           ← code-toolkit 不複製（protocols 是 code-team 自己用的流程腳本）

code-toolkit/
├── scripts/canonical/
│   └── README.md                ← 指明 SSOT 在哪
├── scripts/
│   ├── distribute.py            ← 拷貝 standards / rubrics / checklists → skills/subagent-driven-development/{standards,rubrics,checklists}/
│   └── verify-drift.py          ← CI: 比對 byte-identical
└── skills/
    └── subagent-driven-development/
        ├── standards/           ← functional copy
        │   └── (7 files, header: "FUNCTIONAL COPY — SSOT: domain-teams:code-team/standards/")
        ├── rubrics/             ← functional copy
        └── checklists/          ← functional copy
```

**Drift policy（CLAUDE.md 既有 convention）**：
1. 編輯 standards 內容 → 在 `domain-teams/skills/code-team/standards/` 先改（canonical）
2. 同一 PR 跑 `code-toolkit/scripts/distribute.py` 把改動同步到 code-toolkit
3. CI 跑 `verify-drift.py`；任何 byte diff = fail
4. code-toolkit 端的 functional copy 加 header：

```markdown
<!--
FUNCTIONAL COPY — DO NOT EDIT IN PLACE
SSOT: domain-teams/skills/code-team/standards/tdd-standard.md
Sync via: code-toolkit/scripts/distribute.py
-->
```

### 2.6 Cross-skill delegation

| 觸發情境 | code-toolkit skill | Delegate to |
|---|---|---|
| Commit 前 | `finishing-a-development-branch` | `dev-workflow:git-memory`（mandatory gate） |
| 複雜度疑慮 | `brainstorming` 或 `writing-plans` | `dev-workflow:complexity-critique`（建議；可選） |
| 多方案 triage | `brainstorming` | `dev-workflow:proposal-critique`（建議；可選） |
| 寫新 skill | （不適用 — 不在 code-toolkit 範圍） | `dev-workflow:skill-creator-advance` |
| 已產出要 audit | `requesting-code-review` 子代理 | 可選 `domain-teams:code-team`（被動 gate 入口） |

委派契約（CLAUDE.md 已有 cross-plugin delegation 規範）：
1. 傳遞 **paths + structured seed context**，不傳遞 file content
2. Target skill 拿到全 authority，自行載入 standards / 跑 gate
3. Gate verdict 流回 orchestrating skill，不被 swallowed

---

## 3. Interface Contracts

### 3.1 `using-code-toolkit/SKILL.md`

| Section | 內容 | 來源 |
|---|---|---|
| frontmatter | name / description（與 Superpowers `using-superpowers` 同模式但本地化） | 自訂 |
| `<SUBAGENT-STOP>` | 給 subagent 跳過此 skill 的 escape hatch | Superpowers 慣例 |
| `<EXTREMELY-IMPORTANT>` | 鐵律：skill 適用就必須呼叫 | Superpowers 措辭 |
| Instruction Priority | 1. user CLAUDE.md 2. skills 3. default | Superpowers 慣例 |
| How to Access Skills | Claude Code `Skill` tool / Codex `skill` tool | 自訂 |
| Red Flags | Agent rationalization 表 + 反駁 | Superpowers 措辭 + 加碼中日語句 |
| Skill Priority | 1. brainstorming first 2. implementation second | Superpowers 邏輯 |
| Skill Types | Rigid / Flexible | Superpowers 慣例 |

### 3.2 `tdd-iron-law/SKILL.md`

| Section | 內容 | 來源 |
|---|---|---|
| frontmatter | `name: tdd-iron-law` / `description: Use when implementing any feature or bugfix, before writing implementation code` | Superpowers |
| The Iron Law | "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST" | Superpowers measure |
| Grounding | Beck 2002 Preface + Ch.1 + Part II + Martin Clean Code Ch.9 Three Laws + 和田卓人 訳 2017 | code-team `tdd-standard.md` |
| RED-GREEN-REFACTOR | graphviz / mermaid | Superpowers |
| When NOT to Use | exception list（throwaway / generated / config） | Superpowers |
| Red Flags | "skip TDD just this once" 系列 | Superpowers + 中日加碼 |

### 3.3 `subagent-driven-development/SKILL.md`

| Section | 內容 |
|---|---|
| frontmatter | `name: subagent-driven-development` / description |
| Continuous execution | "Do not pause to check in between tasks" |
| When to Use | flowchart |
| Process | per-task: implementer → spec-reviewer → code-quality-reviewer |
| Model Selection | mechanical → cheap / integration → standard / architecture → most capable |
| Status Handling | DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED |
| Subagent dispatch | Plugin-level — `code-toolkit/agents/{implementer,spec-reviewer,code-quality-reviewer}.md` (v0.6.0+; previously per-skill `./agents/*-prompt.md` in v0.1.0–v0.5.1) |

### 3.4 Subagent prompts

As of v0.6.0, plugin-level paths: `code-toolkit/agents/<role>.md`.
Dispatch via `Agent({subagent_type: "code-toolkit:<role>"})`. Each
agent's system prompt is the file content verbatim (YAML frontmatter
+ role contract + injected baseline block + input/output contract).

**code-toolkit:implementer** (`agents/implementer.md`) input contract:
```
### Task
{task text}

### Context
{paths to existing code, spec, test files}

### Resource Paths
- standards: [path × 7]
- protocol: skills/tdd-iron-law/SKILL.md

### Output Contract
status: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
artifacts: [commit SHAs, test results, self-review notes]
```

**code-toolkit:spec-reviewer** (`agents/spec-reviewer.md`) input contract:
```
### Artifact
{commit SHA range or file paths}

### Spec
{path to TECH-SPEC / design doc}

### Checklist
{path to skills/subagent-driven-development/checklists/spec-consistency.md}

### Output Contract
verdict: PASS / NEEDS_REVISION
gaps: [list of spec items not covered]
```

**code-toolkit:code-quality-reviewer** (`agents/code-quality-reviewer.md`) input contract:
```
### Artifact
{commit SHA range or file paths}

### Rubrics
- skills/subagent-driven-development/rubrics/quality-gate.md
- skills/subagent-driven-development/rubrics/arch-gate.md

### Checklists
- skills/subagent-driven-development/checklists/security-checklist.md

### Standards
[7 standards paths]

### Output Contract
verdict: PASS / PASS_WITH_NOTES / NEEDS_REVISION
dimension_scores: {security, architecture, correctness, naming, tests, refactoring}
flags: [🔴 fatal / 🟡 should-fix / 🟢 nit]
```

---

## 4. Hooks & Activation

### 4.1 Triggers

| Trigger | What happens |
|---|---|
| SessionStart (startup / clear / compact) | hooks/session-start runs → inject using-code-toolkit/SKILL.md |
| User invokes Claude `Skill` tool or Codex `skill` tool | Skill content loaded into context |
| User writes new code | `tdd-iron-law` description triggers via "implementing any feature" |
| User says "let's build X" | `using-code-toolkit` Skill Priority routes to `brainstorming` first |

### 4.2 Soft-mode escape hatch

For users who already have Superpowers installed and want to disable code-toolkit's hook:

```bash
# In hooks/session-start, check before injecting:
if [ "${CODE_TOOLKIT_MODE:-on}" = "off" ]; then
    cat <<EOF
{"hookSpecificOutput": {"additionalContext": ""}}
EOF
    exit 0
fi
```

User sets `export CODE_TOOLKIT_MODE=off` in shell rc to disable.

---

## 5. Quality Gates

### 5.1 SELF Check (every skill ship)

- Re-read PRODUCT-SPEC Goal mapping
- Verify SKILL.md ≤6000 tokens
- Verify subfolder is flat (no nesting)
- Verify frontmatter description starts with "Use when..."
- Verify Red Flags table covers ≥3 rationalizations

### 5.2 MUST Gates

| Gate | Trigger | File / Script |
|---|---|---|
| Folder Structure | Any Write/Edit to skills/ | `.claude/hooks/validate-skill-folder-structure.sh` |
| Marketplace Description Sync | Any change to plugin.json or marketplace.json | `scripts/check-marketplace-description-sync.py` |
| SSOT Drift | Any change to skills/*/standards/ or */rubrics/ or */checklists/ | `code-toolkit/scripts/verify-drift.py` |
| 3-lang README | Any new skill | manual check + CI |

### 5.3 SHOULD Gates

| Gate | Trigger | File |
|---|---|---|
| Skill Token Budget | SKILL.md > 6000 tokens | manual review |
| Hook Injection Token Budget | hooks/session-start output > 3000 tokens | manual review |

---

## 6. Testing Strategy

### 6.1 Skill triggering tests (mirror Superpowers `tests/skill-triggering/`)

```
tests/skill-triggering/prompts/
├── new-feature.txt          # "Let's add a feature to ..."
├── bug-fix.txt              # "Fix this bug ..."
├── refactor.txt             # "Refactor this module ..."
├── pure-question.txt        # "What does this function do?"  ← should NOT trigger brainstorming
└── explicit-skip.txt        # "Don't use TDD"                ← should respect user override
```

Each prompt runs in fresh Claude session; assertion: agent reply contains expected skill name + Iron Law措辭 OR honors user override.

### 6.2 TDD pressure tests

```
tests/tdd-iron-law-pressure/prompts/
├── skip-just-this-once.txt
├── prototype-exception.txt
├── i-already-wrote-it.txt
├── tests-are-slow.txt
└── small-change.txt
```

Assertion: agent maintains Iron Law OR cites the specific exception path documented in `tdd-iron-law/SKILL.md` §When NOT to Use.

### 6.3 SDD integration test

A 4-task plan + a tiny TypeScript repo as fixture. Run SDD end-to-end; assert:
- 4 implementer subagents dispatched
- 4 spec-reviewer subagents dispatched
- 4 code-quality-reviewer subagents dispatched
- All commits land on `feat/code-toolkit-sdd-demo` branch
- Final final-reviewer subagent runs once

---

## 7. Versioning & Release

| Phase | Version | Skills | Tests |
|---|---|---|---|
| 1 | v0.1.0 | 3 (using / tdd-iron-law / SDD) + hook + distribute / verify-drift | 5 skill-triggering + 5 TDD pressure |
| 1.5 | v0.1.5 | + soft-mode flag + 5 dogfood notes | + 1 SDD integration test |
| 2 | v0.2.0 | + brainstorming + writing-plans + systematic-debugging | + 5 brainstorming pressure |
| 2.5 | v0.2.5 | + Codex CLI variant ship + Codex tool mapping | + Codex integration test |
| 3 | v0.3.0 | + requesting-code-review + verification-before-completion + using-git-worktrees + finishing-a-development-branch | full Superpowers parity |
| 3.5 | v0.3.5 | hardening + dogfood polish | |
| 4 | v1.0.0 | GA: cross-skill delegation working with dev-workflow + domain-teams | full eval suite |

---

## 8. Migration & Compatibility

### 8.1 與 `domain-teams:code-team` 並存

Both stay shipped. Router behavior:
- `using-code-toolkit` SessionStart → 主動建構入口（從零開始的功能 / fix / refactor）
- `domain-teams:code-team` 自願呼叫 → 被動 gate 評分入口（既有產出要審查）

No file conflict（不同 plugin 路徑）。`dev-workflow:complexity-critique` 對 code-team mindset 的 SSOT 指向不變。

### 8.2 與 `obra/superpowers` 並存

Conflict points:
- 雙 SessionStart hook 同時注入
- Skill 名稱衝突（`brainstorming` / `writing-plans` / `subagent-driven-development` / `using-git-worktrees`）

Resolution:
- README §Compatibility 明寫 conflict
- 提供 `CODE_TOOLKIT_MODE=off` env var 關閉 hook
- 可選二選一安裝

### 8.3 與 `dev-workflow` 並存

No conflict — code-toolkit delegates to:
- `dev-workflow:git-memory`（commit gate）
- `dev-workflow:complexity-critique`（optional brainstorm aid）
- `dev-workflow:proposal-critique`（optional triage）

---

## 9. Open Questions（v0.1.0-draft 未鎖）

| Q | 問題 | Resolution Phase |
|---|---|---|
| TQ-1 | distribute.py 應該是 push（手動執行）還是 pre-commit hook？ | Phase 1 build 階段定 |
| TQ-2 | implementer subagent 是否要強制呼叫 `tdd-iron-law` skill（透過 prompt 內嵌 Skill tool 指令）？ | Phase 1 PoC 完再決定 |
| TQ-3 | Codex CLI 的 hook 機制與 Claude Code 是否完全相容（JSON shape）？ | Phase 2.5 ship Codex 前驗證 |
| TQ-4 | 是否要包 `dispatching-parallel-agents`（Superpowers 也有）？ | Phase 3+ 觀察名單 |
| TQ-5 | `receiving-code-review` 是否需要？目前傾向用 `dev-workflow:git-memory` 取代 | Phase 3 |
| TQ-6 | 是否在 `tdd-iron-law` 之外另開 `verification-before-completion`？兩者功能有重疊 | Phase 3 |
| TQ-7 | 全 plugin 是否需要 PEP 723 inline metadata（如 dbt-wiki 的 sqlglot 模式）？ | Phase 1 build 階段定（傾向：scripts 純 stdlib，不需要） |
