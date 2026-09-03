# Monkey Skills

## Skill Development Conventions

### File Paths
- SKILL.md 內引用 bundled files 時使用相對路徑（相對於 skill 目錄）
- Good: `checklists/security-checklist.md`, `protocols/code-brainstorming.md`
- Bad: `domain-teams/skills/code-team/checklists/security-checklist.md`
- 原因：Claude Code 提供 Base Path，bundled files 從 skill 目錄相對解析

### 兩份文件：intent.md 與 spec.md（loom 1.0）
- `docs/loom/intent/<change-id>.md`（capture-intent／write-plan 擁有）— 使用者語言：Problem、Proposed outcome、Acceptance（每條可被盲跑證明）、Constraints、Out of scope、Open questions
- `docs/loom/<change-id>/spec.md`（write-spec 擁有）— 工程語言：`REQ-<n> — <name>` 每條對回 intent 的 Acceptance 編號、Design decision（標 agent-decided／user-decided）、Current state evidence、UI flows
- spec.md 只在 `needs-design: yes` 時存在；spec 一律 reference 它的 intent，不重述

### Skill Structure（CRITICAL — Anthropic 規範，違規會被 hook 擋）

**MUST：skill 資料夾扁平 — subfolder 內不可再嵌 subfolder。**

```
✅ OK（subfolder 是單層）:
skills/init/SKILL.md
skills/init/assets/SCHEMA.md
skills/init/assets/extract_lineage.py
skills/init/scripts/build.py
skills/init/agents/worker.md
skills/init/references/spec.md
skills/init/protocols/code-review.md
skills/init/checklists/security.md

❌ NOT OK（subfolder 內又開 subfolder）:
skills/init/assets/scripts/foo.py     ← assets/ 下開 scripts/
skills/init/agents/sub/worker.md      ← agents/ 下開 sub/
skills/init/references/v1/spec.md     ← references/ 下開 v1/
```

- 每個 skill 是自包含目錄：SKILL.md + 任意數量的**單層** subfolder（assets/、protocols/、agents/、scripts/、references/、checklists/、rubrics/、standards/ 等）
- 任一 subfolder 內**不可再開 subfolder**（這是 Anthropic 官方 skill convention）
- SKILL.md body 硬上限 ~6,000 tokens（約 4,500 words）；軟目標 ~5,000 tokens（約 3,750 words，對齊官方建議）；超過軟目標需在 PR 註明一行理由。Anthropic 官方建議 <500 lines，本 repo 改用 token 計量因為行數密度差異大
- Domain knowledge 用目錄慣例 + 描述性檔名路由，不用靜態清單
- Reference files 從 SKILL.md 直接引用，路徑都是 `<subfolder>/<file>` 一層 deep
- **違規會被 `.claude/hooks/validate-skill-folder-structure.sh` 擋下**（PostToolUse on Write|Edit）

### Contract Citations

**MUST：執行期散文契約不得引用本 repo 的開發紀錄** — a runtime prose
contract under the loom skill and agent trees must not cite one of this
repository's development records under `docs/`.

- 原因：派出去的 agent 讀的是**它當下所在的 repo**，所以這種引用只在本
  repo 解得開。這是可攜性缺陷，不是風格偏好
- 豁免一 **loom-scaffolded store directories**：loom 為任何 adopting repo 定義
  的協定路徑（store 目錄、協定檔名、文法佔位符）——那是 schema，不是引用
- 豁免二 **`.py`/`.sh` provenance comments**：出處註解沒有 model 會讀到，
  除非它主動開檔
- 用 `loom-code/scripts/check_contract_citations.py` 檢查；違規的完整定義在
  該腳本裡，這裡不重複（重複＝第二個漂移面）
- **既有債務是分階段清的**：腳本裡的 `DEBT_LIST` 記著規則上線時就已違規的
  檔案，清單只能變短。在清單上的檔案仍算違規，只是尚未清理——新的違規
  在任何地方都會即刻被擋。看到一個 on-list 檔案裡還有引用，那是待辦，
  不是規則的例外

### Quality Gates

**loom 家族（loom-code／loom-design／loom-workflow）**：品質只有三種驗證動作，
其餘都是形式（concept-model §6）。

| 動作 | 誰做 | 產出 |
|---|---|---|
| **讀** | ≥2 個 fresh-context reviewer，按型別選鏡頭（code 11 維／docs 5 維／spec-conformance／design-conformance／principles-conformance） | verdict → `review.json` |
| **盲跑** | 乾淨環境照 intent 的 Acceptance 逐條試，寫成使用者看得懂的盲跑報告 | 報告 ＋ `probes[]` |
| **對抗** | mutation／fuzz，或對抗 agent 自寫 ≥3 個可執行的 abuse／邊界案例並逐筆自跑 | `probes[]`（`kind: adversarial`） |

- 三者跑在 **checkpoint review**（review 站）上，不是逐 task 三臂審查；寫的人不能自己驗
- 決定性的閘只有一支 **checker**：`python3 loom-code/scripts/loom_checker.py --list-rules`
  是規則清單的 SSOT（規則全部是「重算」，不是宣稱）；這裡不重列規則 id，重列＝第二個漂移面
- 散文不當閘：只有 SKILL.md／reference 內以 `<!-- gate: <id> -->` 標記的段落算閘，
  沒標記的散文不得當閘用
- 其他 plugin（domain-teams、投資／研究 toolkit 等）仍用四級系統 SELF / MUST / SHOULD / MAY；
  gate 定義明確指定檔案路徑（相對路徑），verdict 約束內嵌於 PASS_WITH_NOTES 定義

### loom 1.0 flow
- 七站：capture-intent → write-spec →（write-plan → build → review → ship），maintain 回頭開 intent
- 三個人類決策點：①覆述並確認 intent（含單向門問法）②product 的可見行為確認（spec）③盲跑報告驗收
- 入口與完整站序：`docs/loom/README.md`；概念模型：`docs/loom/2026-09-02-simple-loom-flow/concept-model.md`

### Agent Behavioral Rules
- worker：produces artifacts, does NOT produce gate verdicts
- evaluator：produces verdicts, does NOT modify artifacts
- **reviewer ≠ implementer 是重算出來的，不是宣告出來的**：checker 從 `review.json`
  的 `dispatch[]` 記錄比對，任何 reviewer／blind-runner／adversary 同時是 implementer
  就擋（規則 `push.reviewer-ne-implementer`）。writer≠judge 靠 fresh-context 派工記錄保證，
  不靠「不改檔案」保證
- Knowledge access is open（行為限制，非閱讀限制）

### Agent Launch Convention
- 傳遞 **檔案路徑** 給 agent（不是檔案內容）
- Agent 用 Read 工具自行讀取資源
- 路徑在 SKILL.md 中用相對路徑定義，launch 時解析為絕對路徑
- Worker Input Contract: Resource Paths → Task → Input
- Evaluator Input Contract: Resource Paths → Artifact → Requirements

### Cross-Plugin Delegation Contract

首例：`investing-toolkit:investment-memo-writer` → `domain-teams:investing-team`

**規則**：
1. **Delegation = pass paths + structured seed context** — 不傳遞 file content，不內嵌分析結果
2. **Delegation target receives full authority** — 被委派的 skill 自行載入 standards、執行 gates、產生 verdict；委派方不干涉
3. **Data layer stays in toolkit, analysis layer stays in domain-teams** — investing-toolkit 只負責 data fetch + pipeline orchestration；investing-team 負責分析、primary-source anchoring、gate enforcement
4. **Gate verdicts flow back** — delegation target 的 gate 結果（PASS / NEEDS_REVISION）回傳給 orchestrating skill，不被 swallowed
5. **Cross-plugin path resolution** — 委派時使用 plugin name + skill path（e.g. `domain-teams:investing-team`），不使用檔案系統絕對路徑

**Pattern（investing-toolkit → domain-teams）**：
```
investing-toolkit skill
  → data-fetcher agent (I/O only)
  → domain-teams:{team} skill (analysis + gates)
  → domain-teams:docs-team (formatting, optional)
```

**禁止**：
- 不可在 toolkit skill 內自行執行 investing-team 的 gate logic（避免 gate bypass）
- 不可把 domain-teams standards 複製到 toolkit skill（避免 drift）
- data-fetcher agent 不可做分析（I/O only）
