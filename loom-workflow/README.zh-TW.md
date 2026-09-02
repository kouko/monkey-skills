# loom-workflow

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 適用 Claude Code 與 Codex 的 loom workflow plugin — 決策 brief、deletion-first critique gate、git-native project memory、recap、handoff 與 session distill。

**Version**：1.0.0 ・ **Part of**：[monkey-skills](https://github.com/kouko/monkey-skills) ・ **License**：MIT

## Background

為 Claude Code 開發 skill 是反覆的工作。你 draft 一個 skill 後上線，發現它太長、或輸出 tone 偏掉，想改進它 — 但 *如何* 改進取決於變更的種類。**token / structure 的 refactor** 可機械驗證（變更後輸出應相同）。**output quality 的 tuning** 是 taste-sensitive（哪個 variant 比較好只有人類能判斷）。像 `darwin-skill` 那樣把兩者塞進同一個 rubric，會讓 LLM-as-judge 朝著偏離人類偏好的方向 hill-climb（Goodhart drift）。

`loom-workflow` 源自兩個架構決定，其中一個已經搬走：

1. **Two Hats split for skills**（把 Fowler 的 refactor-vs-feature 套用到 skill authoring）— `skill-refactor`（Phase A：behavior-preserving、auto-evaluable）與 `skill-tuning`（Phase B：taste-sensitive、human-judged）分開。這兩個 skill，連同 `skill-creator-advance` 與 `skill-judge`，已經搬到 `skill-dev-toolkit`；詳見下方「Skill-evolution architecture（已搬遷）」。
2. **critique 閘** — 在 proposal 變成 commit 之前介入：一個 `critique` 兩個鏡頭（`mode: proposal` 做多項目 triage、`mode: complexity` 做單一變更的 deletion-first gate）→ simplify（實作後 review，存在於 Anthropic 自己的 toolkit）。這個決定仍留在 `loom-workflow`。

plugin 還帶著 `git-memory`（寫進 commit trailer 與 PR 內文的可攜 project memory，任何能讀 git 的工具都能還原）。

運維治理：[`docs/skill-governance.md`](docs/skill-governance.md)。季度健康檢查：[`docs/quarterly-audit-runbook.md`](docs/quarterly-audit-runbook.md)。

## 收錄準則（Admission rule）

一個 skill 屬於 `loom-workflow`，條件是它做的是**跨站（cross-station）、跨 session 的協調** — 不是因為它「被好幾個 plugin 用到」就算數。用得廣不是判準；跨 station 協調工作、或跨 session 攜帶狀態，才是判準。`decision-map` 是這條規則的第一個實例：它把一份 decision map（`MAP.md` + ticket）持久化下來，供多個 station 在一個 project 的生命週期中讀寫，正是這個 plugin 存在的理由所對應的跨站、跨 session 形狀。這條規則只 gate **新** 收錄——plugin 裡既有的 utility skill 視為 grandfathered，會在延後的 family-relocation arc 裡一併重新評估。

## Skills

| Skill | 角色 |
|---|---|
| [`critique`](skills/critique/) | 在動手做之前裁決提案：`mode: proposal` 用 evidence grounding 與 YAGNI 把清單、計畫或散文建議分成 KEEP / DEFER / DROP；`mode: complexity` 用 deletion-first 量一個具體改動——before/after LOC、什麼會 obsolete。 |
| [`cot-explain`](skills/cot-explain/) | 把已經存在的推理——user 指名的一份文件、或剛完成的工作——渲染成以 CoT 圖為核心的自包含頁面，每條箭頭都標註「為什麼下一步會這樣接」。 |
| [`dbt-model-style`](skills/dbt-model-style/) | 強制執行 dbt + Redshift model 的 style & structure contract — CTE 角色、zero-logic 的 final CTE、命名、YAML header、註解、syntax。 |
| [`decision-map`](skills/decision-map/) | 在 `docs/loom/maps/<map-id>/` 開一張持久化的 decision map 並持續推進——一個目的地、一份不斷成長的 Decisions-so-far 紀錄，以及一份會在多個 session 中逐步畢業成 ticket 的 Not-yet-specified（fog）清單，而非一次性 plan。 |
| [`distill-sessions`](skills/distill-sessions/) | 從過去的 Claude Code 與 Codex session transcript ＋ `/insights` 中挖掘 friction pattern，整理成逐 skill 的改進提案文件。 |
| [`git-memory`](skills/git-memory/) | 把決策的 context（不是 diff，而是 **why**）寫進 commit trailer 與 PR 內文，讓未來任何 session — Claude Code、Cursor、Codex、aider 或人類 — 只用 `git log` 就能重建 project knowledge。 |
| [`goal-create`](skills/goal-create/) | 起草一個 goal condition — SESSION mode 產出長時間執行 agent run 的四欄位停止條件（Outcome / Constraints / Verification / Stop-when）；ARC mode 產出 repository 的 purpose artifact（`Why` / `Done when`）。 |
| [`handoff`](skills/handoff/) | 把 session 狀態存成結構化的 HANDOFF 檔，讓未來的 agent 能乾淨接手；或讀取／驗證既有的 HANDOFF。 |
| [`independent-advisor`](skills/independent-advisor/) | 對當前的 plan 或決策，向**另一個 executor**——更強的 model、更高的 effort，或另一家廠商——取得 second opinion。換的是 executor，不是 critique 的觀點。 |
| [`recap-state`](skills/recap-state/) | session 內的重新定向——當 user 跟丟話題時，輸出以 Synthesis-check 收尾的結構化 recap。 |

十個 skill 全為 **Active**（八個 loom tool，加上在 loom 流程之外的 `goal-create`、`dbt-model-style` 兩個 standalone skill）。lifecycle 狀態與所有權：[`docs/skill-governance.md`](docs/skill-governance.md)。

## critique 線

一個 skill 的兩個鏡頭，加上 Anthropic 自己的實作後 reviewer，組成一條 deletion-first 的 pipeline，分別對應不同的 proposal 形狀：

```
critique · mode: proposal   critique · mode: complexity   Anthropic simplify
─────────────────────────   ───────────────────────────   ──────────────────
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

拿到 backlog 或編號 plan 時用 `mode: proposal`。檯面上是一個具體變更時用 `mode: complexity`。變更上線之後用 Anthropic 的 `simplify`。

## Skill-evolution architecture（已搬遷）

`skill-creator-advance`、`skill-refactor`、`skill-tuning`、`skill-judge` — 本節過去描述的、依變更尺寸 × 評估模式劃分的生命週期模型 — 已經和 `dogfood-skill-testing` 一起搬到 `skill-dev-toolkit`。`loom-workflow` 已不再收錄它們。原始設計理由（Two Hats split、機械性變更容許 auto-evaluation 但 taste-sensitive 變更需要人類判斷的 evaluation 成本論證）封存在 [`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md)；目前的所有權與後續設計請見 `skill-dev-toolkit` 自己的 README。

## git-memory 三大支柱

`git-memory` 立基於三個主張：

1. **Carrier — git artifact 本身**。commit message 與 PR 內文就是 substrate。任何能讀 git 的工具都能讀到 memory。`git clone` 會把 memory 一起帶來。沒有 server，沒有 embedding store，沒有 vendor lock-in。
2. **Structure — commit trailer**。結構化事實搭乘 git trailer — 與 `Co-Authored-By:`、`Signed-off-by:` 同樣的機制。三個 trailer 涵蓋約 80% 的價值：`Decision:`（為什麼用這個方式）、`Learning:`（過程中發現什麼）、`Gotcha:`（給未來自己的陷阱提示）。
3. **Content — 不是 code，而是決策的 context**。diff 已經呈現 *什麼* 變了。memory 記錄 *why*。目標是六個月後原始 context 已遺失時仍有價值的 entry — 而非與 code 重複的 entry。

`git-memory` 補強（而非取代）Claude Code 原生的 `~/.claude/.../MEMORY.md`。原生 memory 保存跨 project 的 user-level 偏好；`git-memory` 在 repo 內保存 project 決策。

## Upstream chain

十個 skill 中有一個源自 MIT-licensed 的 upstream。完整 attribution 在該 skill 的 `NOTICE` 檔案。（`skill-creator-advance` 與 `skill-judge` 的 upstream attribution 已隨它們一起搬到 `skill-dev-toolkit`。）

| Skill | Upstream chain |
|---|---|
| `critique`（`mode: complexity`） | joshuadavidthomas [`reducing-entropy`](https://github.com/joshuadavidthomas/agent-skills/tree/main/skills/reducing-entropy) → softaworks fork → monkey-skills（`reducing-entropy` 改名為 `complexity-critique`，再併入 `critique`） |

其餘九個 skill 為原創設計，沒有外部 upstream 需要 attribution。詳情見各 skill 的 `NOTICE`（若存在）。

## Repository 結構

```
loom-workflow/
├── .claude-plugin/
│   └── plugin.json
├── docs/
│   ├── skill-evolution-architecture.md
│   ├── skill-governance.md
│   ├── quarterly-audit-runbook.md
│   └── telemetry-setup.md
├── skills/
│   ├── cot-explain/
│   ├── critique/
│   ├── dbt-model-style/
│   ├── decision-map/
│   ├── distill-sessions/
│   ├── git-memory/
│   ├── goal-create/
│   ├── handoff/
│   ├── independent-advisor/
│   └── recap-state/
├── CHANGELOG.md
├── README.md
├── README.ja.md
└── README.zh-TW.md       (本檔案)
```

## 安裝

`loom-workflow` 以 [monkey-skills](https://github.com/kouko/monkey-skills) marketplace 的一部分發行。這是取代 `dev-workflow` 的 hard-cut rename；請將自訂 skill reference 改為 `loom-workflow:<skill>`。加入 marketplace 並安裝 plugin：

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install loom-workflow@monkey-skills
```

## 使用

`loom-workflow` 沒有內附 slash command — 十個 skill 全部由自然語言 auto-trigger。例如：

```
「critique 這份 12 項的 plan」                     → critique（proposal）
「值不值得改」/「該不該做這個」                     → critique（complexity）
「我準備 commit — 幫我寫 trailer」                 → git-memory
「開一張決策地圖」/「chart a decision map」         → decision-map
「wrap up」/「save state」                          → handoff
「where were we」/「我跟丟了」                      → recap-state
「second opinion」/「換一個模型看看」               → independent-advisor
```

關於 `skill-refactor` vs `skill-tuning` 的 Two-Hats split（已搬遷），見上方「Skill-evolution architecture（已搬遷）」。

## 貢獻

貢獻遵守整個 repo 的 convention（repo 根目錄的 [`CLAUDE.md`](https://github.com/kouko/monkey-skills/blob/main/AGENTS.md)）。

- **問題**：在 [kouko/monkey-skills](https://github.com/kouko/monkey-skills/issues) 開 GitHub Discussion 或 issue。
- **PR**：從 `main` 切 branch，遵守 Conventional Commits，push 前先在本機跑 convention-drift CI script（`scripts/check-shared-conventions-drift.py`）。
- **skill 內部 README** 由 skill owner 直接撰寫，遵守較輕量的 rule set（見 [`docs/skill-governance.md`](docs/skill-governance.md) §README Authoring Discipline）。plugin 層級 README（本檔案及翻譯版本）需經 `domain-teams:docs-team`。
- **新增 shared convention** 時，須在同一個 PR 內更新 [`docs/skill-governance.md`](docs/skill-governance.md) 的 SSOT registry，並在 drift CI manifest 加上對應 pair。

## License

MIT。plugin 內唯一具有 MIT-licensed upstream 的 `critique`（其 `mode: complexity` 的一半），在其 `LICENSE` 與 `NOTICE` 中完整保留 copyright chain。（`skill-creator-advance` 與 `skill-judge` 已搬到 `skill-dev-toolkit`，並在那裡保留各自的 copyright chain。）

repo 根目錄的 umbrella license 見 [LICENSE](https://github.com/kouko/monkey-skills/blob/main/LICENSE)。
