# 4DX D3 — Team Lead Scoreboard Design

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> Team-leader スコープ — team が自分で build する public な players' scoreboard を facilitate する。Team WIG + 2-3 lead を載せ、≤4 要素 / 5-second test、leader は veto はするが dictate しない。

## このスキルが起動するとき

- 「team の scoreboard を設計したい」「チーム全員が見える進捗の出し方」
- 「Team WIG と lead はあるが、scoreboard をどう作る？」
- 「team が目標は知っているが dashboard が motivating でない」
- 「壁 / TV / pinned channel / SharePoint どれに載せる？」
- 「幫我設計 team 的 scoreboard」「怎麼讓全隊都看得到進度」

## 何をするか（プロトコル概要）

leader と Socratic facilitation を行う — agent が scoreboard を設計しない。leader が team に持ち帰って build するための spec を生成する。

1. **Team WIG + 2-3 leads が既に存在することを確認** — 欠けていれば D1 / D2 に戻す
2. **leader が team に build させる意思を確認** — Step 3 のアンチパターン（leader 自作の board は 4 週目で死ぬ）を名指す
3. **公開表示場所を確定** — 壁 / TV / pinned channel / 4DX app（分散 team）
4. **leader が守る 4 つの硬いルール** — ≤4 要素 / visible / lead+lag 双方に target line / 5 秒で「勝っているか」が分かる
5. **team-build session を計画** — 書の 4 手順（Theme → Design → Build → Keep Updated）、leader は facilitator、author ではない
6. **更新リチュアルを確定** — 誰が、いつ、どの頻度（≥ 週次）、team が手で更新する（leader でも純自動 feed でもない）
7. **出力** — spec + 議題 + 議論を引き戻すための一文セット。inertia 防止のため 7 日以内の開催を推奨

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| solo / 個人専用 scoreboard | `4dx-d3-personal-scoreboard` |
| member が既存の team scoreboard を読む | `4dx-d3-member-scoreboard-reading` |
| enterprise BI / multi-team rollup | coach's scoreboard / drill-down — plugin 範囲外 |
| Team WIG / lead が未定義 | `4dx-d1-team-primary-wig-selection` / `4dx-d2-team-lead-measure-facilitation` |
| stroke-of-pen な team goal | scoreboard ではなく project plan |
| reactive / on-call team（whirlwind 自体が strategic 作業） | phantom guilt の温床、skip |

## 出典

*The 4 Disciplines of Execution*（2nd ed.）第 4 章 + 第 14 章より蒸留。3 つの anchor case: Serena's Event Management team（教科書的 3 要素 board: WIG/lag + Lead 1 per-associate + Lead 2 90% 持続線）、juice-bottling 各シフト（public visibility が peer accountability を生む、management push 不要）、Northrop Grumman / Hurricane Katrina で倒れた stadium scoreboard（可視 score は engagement の基礎）。Industry grounding: Tufte 1983/2001（data-ink）、Few 2006/2013（dashboard vs database）、Macey & Schneider 2008（公開 feedback による state + behavioral engagement）。

team scale の coach's-as-players' substitution（CE-08）、leader-authored アンチパターン、communication-board drift、dispersed-team excuse、high-context culture（JP / ZH / KR）における person-vs-person 比較の face-loss 緩和は [`SKILL.md`](SKILL.md) を参照。
