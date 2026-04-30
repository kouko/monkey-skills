# 4DX D3 — Team Lead Scoreboard Design

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Team-leader 範疇 — facilitate team 自己 build 一個 public 的 players' scoreboard，承載 Team WIG + 2-3 個 lead。≤4 個元素、5-second test，leader 用 veto 不 dictate。

## 何時觸發這個 skill

- 「幫我設計 team 的 scoreboard」「怎麼讓全隊都看得到進度」
- 「我們有 Team WIG 跟 lead，scoreboard 該長怎樣？」
- 「team 有目標但儀表板沒人在看」
- 「掛在 SharePoint vs 牆上 vs Slack pin？」
- 「team の scoreboard を設計したい」「チーム全員が見える進捗の出し方」

## 它做什麼（protocol 摘要）

跟 leader 做 Socratic facilitation — agent 不幫 leader 畫 scoreboard；產出 spec，leader 帶回 team 建。

1. **確認 Team WIG + 2-3 個 lead 已存在** — 缺哪個就退回 D1 / D2
2. **確認 leader 會讓 team 自己 build** — 點名 Step 3 反 pattern（leader 自製的板第 4 週就死）
3. **鎖定公開展示位置** — 牆 / TV / pinned channel / 4DX app（分散 team）
4. **leader 守住四條硬規則** — ≤4 元素 / visible / lead+lag 都有 target line / 5 秒看出在贏
5. **規劃 team-build 會議** — 書中 4 步驟（Theme → Design → Build → Keep Updated），leader 是 facilitator 不是作者
6. **鎖定 update ritual** — 誰更新 / 什麼時候 post / ≥ 每週；team 親手更新（不是 leader、不是純自動 feed）
7. **輸出** — spec + 議程 + leader 在會中拉回主線的句子；建議 7 天內開會（inertia 是這個 skill 要防的失敗模式）

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| solo / 自己用的 scoreboard | `4dx-d3-personal-scoreboard` |
| member 讀已有的 team scoreboard | `4dx-d3-member-scoreboard-reading` |
| enterprise BI / 多 team rollup | coach's scoreboard / drill-down — 超出 plugin |
| Team WIG / lead 還沒定 | `4dx-d1-team-primary-wig-selection` / `4dx-d2-team-lead-measure-facilitation` |
| stroke-of-pen team goal | 該用 project plan，不是 scoreboard |
| reactive / on-call team（whirlwind 就是策略工作） | 會製造 phantom guilt — 跳過 |

## 出處

蒸餾自 *The 4 Disciplines of Execution*（2nd ed.）第 4 章 + 第 14 章。三個 anchor case：Serena Event Management team（教科書級三元素板：WIG/lag + Lead 1 per-associate + Lead 2 90% 持續線）、juice-bottling 班次（純可見性製造 peer accountability，不需管理推力）、Northrop Grumman / Hurricane Katrina 倒下的球場記分板（可見分數是 engagement 的根基）。Industry grounding：Tufte 1983/2001（data-ink）、Few 2006/2013（dashboard vs database）、Macey & Schneider 2008（公開 feedback 觸發 state + behavioral engagement）。

team 規模 coach's-as-players' 取代失敗（CE-08）、leader-authored 反 pattern、communication-board drift、dispersed team 的藉口、以及高 context 文化下「人對人」比較變成 face-loss 的軟化建議，見 [`SKILL.md`](SKILL.md)。
