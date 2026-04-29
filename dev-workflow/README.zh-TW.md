# dev-workflow

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Claude Code 的 developer workflow plugin — skill 建立、評分、refactor、tuning、deletion-first 的 critique gate，以及 git-native 的 project memory。

**Version**：2.0.0 ・ **Part of**：[monkey-skills](https://github.com/kouko/monkey-skills) ・ **License**：MIT

## Background

為 Claude Code 開發 skill 是反覆的工作。你 draft 一個 skill 後上線，發現它太長、或輸出 tone 偏掉，想改進它 — 但 *如何* 改進取決於變更的種類。**token / structure 的 refactor** 可機械驗證（變更後輸出應相同）。**output quality 的 tuning** 是 taste-sensitive（哪個 variant 比較好只有人類能判斷）。像 `darwin-skill` 那樣把兩者塞進同一個 rubric，會讓 LLM-as-judge 朝著偏離人類偏好的方向 hill-climb（Goodhart drift）。

`dev-workflow` 圍繞兩個架構決定提供一組 skill：

1. **Two Hats split for skills**（把 Fowler 的 refactor-vs-feature 套用到 skill authoring）— `skill-refactor`（Phase A：behavior-preserving、auto-evaluable）與 `skill-tuning`（Phase B：taste-sensitive、human-judged）分開。
2. **critique-gate 線** — 在 proposal 變成 commit 之前介入：`proposal-critique`（多項目 triage）→ `complexity-critique`（單一變更 deletion-first gate）→ simplify（實作後 review，存在於 Anthropic 自己的 toolkit）。

plugin 還附帶 `skill-creator-advance`（建立 + 大幅重設計）、`skill-judge`（advisory 八維品質 rubric，不修改）、`git-memory`（寫進 commit trailer 與 PR 內文的可攜 project memory，任何能讀 git 的工具都能還原）。

完整設計理由：[`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md)。運維治理：[`docs/skill-governance.md`](docs/skill-governance.md)。季度健康檢查：[`docs/quarterly-audit-runbook.md`](docs/quarterly-audit-runbook.md)。

## Skills

| Skill | 角色 |
|---|---|
| [`skill-creator-advance`](skills/skill-creator-advance/) | 建立新 skill 或對既有 skill 做大幅重設計（新增 / 拆分 / 合併 phase、改 agent 分解、改 input/output contract）。含 description optimization 的反覆 eval-driven development。 |
| [`skill-refactor`](skills/skill-refactor/) | 既有 skill 的 token / structure refactor，**保留 output behavior**。三道 gate：equivalence（multi-judge ensemble）+ token reduction（≥10%）+ invariant preservation。判定 PROCEED / RESHAPE / REJECT，搭配 git ratchet（失敗自動 revert）。 |
| [`skill-tuning`](skills/skill-tuning/) | 既有 skill 的 output quality A/B — 產生 variant 並以 blind 方式跑，捕捉人類 preference（A / B / both / neither）。Constitution 是地板，taste 是天花板。preference log 累積為 RLHF-lite 資料集。 |
| [`skill-judge`](skills/skill-judge/) | Advisory 八維設計 rubric（Knowledge Delta・Mindset+Procedures・Anti-Pattern・Spec Compliance・Progressive Disclosure・Freedom Calibration・Pattern Recognition・Practical Usability），0–120 分 + A–F 等級。不修改。 |
| [`proposal-critique`](skills/proposal-critique/) | 把多項目 proposal（list / plan / 散文建議）以 evidence grounding 與 YAGNI triage 為 KEEP / DEFER / DROP。 |
| [`complexity-critique`](skills/complexity-critique/) | 用三個 deletion-first 問題對單一具體提案做 gate：最小可達狀態、before/after LOC、什麼會 obsolete。判定 PROCEED / PROCEED-WITH-CAVEAT / RESHAPE / REJECT。 |
| [`git-memory`](skills/git-memory/) | 把決策的 context（不是 diff，而是 **why**）寫進 commit trailer 與 PR 內文，讓未來任何 session — Claude Code、Cursor、Codex、aider 或人類 — 只用 `git log` 就能重建 project knowledge。 |

七個 skill 全為 **Active**。lifecycle 狀態與所有權：[`docs/skill-governance.md`](docs/skill-governance.md)。

## critique 線

三個 skill 組成一條 deletion-first 的 review pipeline，分別對應不同的 proposal 形狀：

```
proposal-critique           complexity-critique           Anthropic simplify
─────────────────           ─────────────────────         ──────────────────
多項目的 proposal           單一具體的提案變更            實作後的 diff review
（list / plan / 散文）       （refactor、新增 feature、
                            debt cleanup，或
                            「該不該做這個」）

triage：每項判為            gate：三個 deletion-first     上線後的 review：
  KEEP / DEFER / DROP         questions                     reuse、品質、效率
依 evidence + YAGNI         • 最小可達狀態
                              • before/after LOC
                              • 什麼會 obsolete

判定：KEEP / DEFER          判定：PROCEED /              （位於本 plugin 之外）
       / DROP                      PROCEED-WITH-CAVEAT
                                   / RESHAPE / REJECT
```

拿到 backlog 或編號 plan 時用 `proposal-critique`。檯面上是一個具體變更時用 `complexity-critique`。變更上線之後用 Anthropic 的 `simplify`。

## skill-evolution architecture

`skill-creator-advance`、`skill-refactor`、`skill-tuning`、`skill-judge` 涵蓋一個 skill 的完整生命週期，依 **變更尺寸 × 評估模式** 切分：

```
size →    small                medium                large                new
       ┌────────────────┐  ┌────────────────┐  ┌──────────────────────────────┐
       │ skill-tuning   │  │ skill-refactor │  │ skill-creator-advance        │
       │                │  │                │  │ (建立 + 大幅重設計)          │
       │ output quality │  │ token / struct │  │                              │
       │ A/B variants   │  │ 同樣 behavior  │  │ spec-first 重設計 / 新建     │
       │                │  │                │  │                              │
       │ HUMAN judge    │  │ LLM equiv.     │  │ 使用者主導的 iteration loop  │
       │ each iteration │  │ + git ratchet  │  │ + 可選 AI A/B comparator     │
       └────────────────┘  └────────────────┘  └──────────────────────────────┘

       skill-judge：advisory 0–120 分，不修改，隨時可跑
```

這個切分由 evaluation 成本決定：機械性變更（refactor）容許 auto-evaluation，因為 LLM-as-judge 對 binary equivalence 可信；taste-sensitive 變更（tuning）必須由人類判斷，因為 LLM-as-judge 對 style、voice、persuasive force、design feel 並不可靠。選哪個 skill 是「做哪種變更」的問題，不是「要多少自動化」的問題。

## git-memory 三大支柱

`git-memory` 立基於三個主張：

1. **Carrier — git artifact 本身**。commit message 與 PR 內文就是 substrate。任何能讀 git 的工具都能讀到 memory。`git clone` 會把 memory 一起帶來。沒有 server，沒有 embedding store，沒有 vendor lock-in。
2. **Structure — commit trailer**。結構化事實搭乘 git trailer — 與 `Co-Authored-By:`、`Signed-off-by:` 同樣的機制。三個 trailer 涵蓋約 80% 的價值：`Decision:`（為什麼用這個方式）、`Learning:`（過程中發現什麼）、`Gotcha:`（給未來自己的陷阱提示）。
3. **Content — 不是 code，而是決策的 context**。diff 已經呈現 *什麼* 變了。memory 記錄 *why*。目標是六個月後原始 context 已遺失時仍有價值的 entry — 而非與 code 重複的 entry。

`git-memory` 補強（而非取代）Claude Code 原生的 `~/.claude/.../MEMORY.md`。原生 memory 保存跨 project 的 user-level 偏好；`git-memory` 在 repo 內保存 project 決策。

## Upstream chain

七個 skill 中有三個源自 MIT-licensed 的 upstream。完整 attribution 在各 skill 的 `NOTICE` 檔案。

| Skill | Upstream chain |
|---|---|
| `skill-creator-advance` | Anthropic [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) → AllanYiin（尹相志）[`skill-creator-advanced`](https://github.com/AllanYiin/Amon) → monkey-skills |
| `skill-judge` | Leonardo Flores [`skill-judge`](https://github.com/softaworks/agent-toolkit) → monkey-skills |
| `complexity-critique` | joshuadavidthomas [`reducing-entropy`](https://github.com/joshuadavidthomas/agent-skills/tree/main/skills/reducing-entropy) → softaworks fork → monkey-skills（`reducing-entropy` 改名為 `complexity-critique`） |

`skill-refactor`、`skill-tuning`、`proposal-critique`、`git-memory` 為原創設計。`skill-refactor` 與 `skill-tuning` 在概念上致謝 `alchaincyf/darwin-skill`（MIT）與 Andrej Karpathy 的 `autoresearch`（MIT）對 autonomous-loop + git-ratchet 模式的啟發，但 architecture、gate function、evaluation rubric 為獨立設計。詳情見各 skill 的 `NOTICE`。

## Repository 結構

```
dev-workflow/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── complexity-critique.md
│   ├── skill-creator-advance.md
│   ├── skill-refactor.md
│   └── skill-tuning.md
├── docs/
│   ├── skill-evolution-architecture.md
│   ├── skill-governance.md
│   ├── quarterly-audit-runbook.md
│   └── telemetry-setup.md
├── skills/
│   ├── complexity-critique/
│   ├── git-memory/
│   ├── proposal-critique/
│   ├── skill-creator-advance/
│   ├── skill-judge/
│   ├── skill-refactor/
│   └── skill-tuning/
├── CHANGELOG.md
├── README.md
├── README.ja.md
└── README.zh-TW.md       (本檔案)
```

## 安裝

`dev-workflow` 以 [monkey-skills](https://github.com/kouko/monkey-skills) marketplace 的一部分發行。加入 marketplace 並安裝 plugin：

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install dev-workflow@monkey-skills
```

## 使用

plugin 內附四個 slash command：

```
/skill-creator-advance      # 新建 或 大幅重設計既有 skill
/skill-refactor             # token / structure refactor、保留 equivalence
/skill-tuning               # 由人類判定的輸出 A/B
/complexity-critique        # 對具體變更執行 deletion-first gate
```

其餘三個 skill（`skill-judge`、`proposal-critique`、`git-memory`）會由自然語言 auto-trigger — 例如：

```
「用八維 rubric 幫這個 skill 評分」               → skill-judge
「critique 這份 12 項的 plan」                    → proposal-critique
「我準備 commit — 幫我寫 trailer」               → git-memory
```

關於 Two-Hats split（refactor vs tuning）的演練，見 [`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md) §2。

## 貢獻

貢獻遵守整個 repo 的 convention（repo 根目錄的 [`CLAUDE.md`](../CLAUDE.md)）。

- **問題**：在 [kouko/monkey-skills](https://github.com/kouko/monkey-skills/issues) 開 GitHub Discussion 或 issue。
- **PR**：從 `main` 切 branch，遵守 Conventional Commits，push 前先在本機跑 convention-drift CI script（`scripts/check-shared-conventions-drift.py`）。
- **skill 內部 README** 由 skill owner 直接撰寫，遵守較輕量的 rule set（見 [`docs/skill-governance.md`](docs/skill-governance.md) §README Authoring Discipline）。plugin 層級 README（本檔案及翻譯版本）需經 `domain-teams:docs-team`。
- **新增 shared convention** 時，須在同一個 PR 內更新 [`docs/skill-governance.md`](docs/skill-governance.md) 的 SSOT registry，並在 drift CI manifest 加上對應 pair。

## License

MIT。具有 MIT-licensed upstream 的 skill（`skill-creator-advance`、`skill-judge`、`complexity-critique`）在各 skill 的 `LICENSE` 與 `NOTICE` 中完整保留 copyright chain。

repo 根目錄的 umbrella license 見 [LICENSE](../LICENSE)。
