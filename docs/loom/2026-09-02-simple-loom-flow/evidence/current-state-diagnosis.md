# loom 目標概念模型 v5（一頁紙草稿）

日期：2026-09-02　狀態：草稿，未批准　對照組：Anthropic「The AI-Native SDLC Playbook」
v0 → v1：採「what/why vs how」切線（C）、loom-code 可獨立、intent schema 定案、新增 §7 准入規則。
v1 → v2：review 站改為 checkpoint review（§3i）；三種驗證動作＋按 artifact 型別觸發（§3j）；Q2 裁定（刪 batch）。
v2 → v3：Q3–Q6 裁定（常駐文件三段式、host hooks＋CI、delivery ticket＝intent、design 維持可選）；證據落點規則（§3k）。
v4 → v5：自審 8 項＋opus 對抗邏輯審 10 項（D1 verdict 入版控給 CI、D2 覆寫後重 probe、D3 kind 限定禁令、D4 拒收非擋 commit、D5 after-task wave 必審、D6 dismissed＋waiver 語意、D7 withdrawn 態、D8 18＋計數規則、D9 刪條件 (c)、D10 名詞數退出 CI）。
v3 → v4：Codex gpt-5.6-sol high 獨立審查（`inventory/independent-advisor-codex-run.md`）：修 5 項事實錯誤；採 #2 open_findings、#3 Task trailer＋兩暫態、#5 spec 先審、#6 action 分類；裁 #1 逃生口保留、#4 BLOCK＋probe＋CI digest、#10 准入改 AND。

## 1. 現況（盤點結果）

| | loom-code | loom-design | loom-workflow | 合計 |
|---|---|---|---|---|
| skill | 14 | 10 | 12 | 36 |
| 寫出的 artifact 種類 | 13 | 11–13 | 14 | ~38 |
| 引入的專有名詞 | 44 | 44 | 25（清單實列約 38，待重數） | ≈113 |
| 不產 artifact 的 skill | 4 | 1 | 5 | 10 |
| 產物沒有下游讀者的 skill（含 router／chat-only／自用檔，非 17 種孤兒 artifact） | 6 | 3 | 8 | 17 |

現況鏈（實際接線，不是文件宣稱）：

```
[對話中的 seed] ─┬─ design 側：discovery(無下游) → PRINCIPLES → DESIGN/ui-flows
                 │            → proposal+specs(+critic 就地增補) → change-folder ─┐
                 └─ code 側：brainstorming → brief(Problem…Decision) ───────────┤
                                                                               ▼
        plan.md（一檔六角色：DAG／Status／Decision Log／Review Batches／Stage／kickoff）
                                                                               ▼
        SDD：task → implementer + 2 reviewers（或 batch packet/receipt）→ commit
                                                                               ▼
        review-pass.json + verified.json + waiver.json ──→ git-guard ──→ push/PR
                                                                               ▼
        finishing：memory／backlog／INDEX／archive
```

對照組（Anthropic）：

```
intent.md(人寫) → spec.md(Claude 寫) → plan.md → diff/PR → review findings → incident→intent.md
   PO 批          PO 批               工程師批    code owner 批   release mgr 批(hook)
治理三層：skills=建議性 ／ hooks=決定性(allow/ask/block) ／ git=稽核軌跡
```

## 2. 六個結構性診斷

1. **intent 沒有家**。design 側 seed 只在對話裡；code 側 intent 混在 brief 裡跟 Decision 同居；backlog entry 是第三個半成品。
2. **plan.md 一檔扛六角色**，五個 skill 用不同腳本改同一檔的不同段——名詞爆炸的物理來源。
3. **審查有六種 reviewer、兩套 critic、一套 batch 機制**，對照組只有「每個 PR 一次相同的 agent 審查 + 一個人批」。
4. **三個 gate marker、一個讀者**（git-guard）。
5. **10 個 skill 不產 artifact**——它們是行為規則，不是流程站，卻和站平起平坐佔 skill 名額。
6. **17 個 skill 的產物沒有自動下游**（其中含 router／chat-only／自用檔；真正宣稱「informs 下游」卻無接線的是 discovery 三檔、completeness-critic verdict、HANDOFF、cot-explain）。

