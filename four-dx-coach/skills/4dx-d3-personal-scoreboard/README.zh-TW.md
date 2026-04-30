# 4DX D3 — Personal Scoreboard

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> D3 的核心 — 為一個人設計一張「一眼看得出勝負」的 players' scoreboard（≤4 個元素、lead + lag + where-you-should-be line、通過 5 秒測試）。

## 何時觸發這個 skill

- 「我做了一個 Notion 追蹤表，可是都沒在看」
- 「我的 fitness app 顯示太多東西，沒一個能讓我動起來」
- 「怎麼讓進度看得見？」「sticky note / whiteboard / app 哪個好？」
- D1 + D2 都做完了但 2-4 週後 momentum 在掉（多半是缺 scoreboard，不是意志力問題）
- 現在用的追蹤物明顯是 coach's scoreboard（多 tab 試算表、Gantt、project plan）

## 它做什麼（protocol 摘要）

Socratic 設計對話 — 輸出是「今天就要貼在工作視野裡的 scoreboard spec」，不是討論追蹤哲學：

1. **確認 WIG + lead measure 都已定義** — 兩個都要書面化。缺的話退回 D1 / D2
2. **依使用者真實一天選顯示媒介** — 一天視線會自然落上 3-5 次的地方。「我會打開那個 app」直接退件
3. **設計 lead measure 視覺化** — 週 bar / 連續天數 streak / 打勾格 / 累積計數，30 秒內能更新
4. **lag 視覺化必須加 where-you-should-be line** — pacing line / target marker / "goat"，沒這條線就只看到「現在在哪」、看不出「我贏了沒」
5. **5 秒測試** — 用冷描述讀回去，使用者要能毫不猶豫說「贏」或「輸」。猶豫就刪元素，最終 ≤4 個
6. **鎖定顯示位置 + 更新 cadence** — 一行 commitment：「我會把這張貼在 [位置]，[lead] 每天更新 / [lag] 每週更新」
7. **輸出: 規格 + 今天就動手的物理動作** — 印出來、貼上、whiteboard 畫上去。「這週末再做」不接受（這個 skill 存在就是要擋住 inertia）

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| 你管的 team 的全組織 BI / KPI dashboard | coach's scoreboard 是另一個問題，本來就該複雜 |
| WIG 或 lead measure 還沒定 | 先去 `4dx-d1-personal-wig-defining` / `4dx-d2-personal-lead-measure-discovery` |
| stroke-of-pen goal（買 / 雇 / 決定就好） | 沒有東西可以 scoreboard |
| reactive / on-call 領域，whirlwind 本身是戰略 | 有 phantom guilt 風險，請看 `4dx-meta-personal-strategy-triage` |
| 高 context 文化的團隊脈絡（公開比較會 face-loss） | 書中 shift-vs-shift 範例對 JP / ZH / KR 不太適用 |

## 出處

蒸餾自 *The 4 Disciplines of Execution*（2nd ed.）第 4 章 Discipline 3: Keep a Compelling Scoreboard + 第 14 章。三個 anchor case：Northrop Grumman（被颶風吹倒的體育場 scoreboard 比喻）、加拿大遠端工廠（只是把 shift-level 的 board 弄得看得見，品質 74 → 94）、戰鬥機開發團隊（"project plan is not a scoreboard"；兩種成果物應該並存）。

完整 RIA++ 渲染（含 coach's-as-players' substitution（CE-08）、status-without-trajectory（CE-09）、Goodhart / 虛榮指標漂移、manual-update-as-feature 設計規則）見 [`SKILL.md`](SKILL.md)。
