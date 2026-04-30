# 4DX D1 — Whirlwind Triage

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> D1 の前提作業 — WIG を書く *前* に、7 日間の time audit で BAU と WIG の容量を可視化する。

## このスキルが起動するとき

- 「日常業務に追われて目標に手がつかない」「忙しすぎて目標が進まない」
- 「いつも雑用ばかりで本当にやりたいことが進まない」
- 前回の WIG が死んで、4DX が悪いのか自分が「もっと頑張る」べきなのか分からない
- これから `4dx-d1-personal-wig-defining` を呼ぼうとしているが、whirlwind と WIG の区別をまだ明示していない

## 何をするか（プロトコル概要）

1. **7 日間の time audit ログを立ち上げる** — 起きている間の 30 分 block を全部 `WHIRLWIND` / `WIG` / `NEITHER` で tag。完了基準: 7 日連続 + 起床 block の 80% 以上 tag 済み。
2. **比率を計算する** — tag ごとに合計し WHIRLWIND% / WIG% / NEITHER% を書き出す。期待と実測の gap に対する一行のリアクションも書く。
3. **whirlwind を theater 監査する** — 各 WHIRLWIND block を `BAU-real`（やめると現場が壊れる）/ `BAU-theater`（やめると自分の image だけ壊れる）に再 tag。
4. **WIG 最低割当を決める** — 書籍の anchor は ~20%（週 40h なら 8h）。数値 N + 具体的な calendar block + protector を commitment として書く。
5. **handoff または terminate** — `4dx-d1-personal-wig-defining` に渡す。逆に step 1 で reactive role が露呈したなら、この目標で 4DX を使わない決断をはっきり下す。

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| burnout / 慢性的な疲弊 / 抑うつ | コーチングや臨床へ — time audit は逆効果 |
| 本質的に reactive な役割（on-call SRE、ER、乳児育児） | whirlwind 自体が戦略価値 — `4dx-meta-personal-strategy-triage`（CE-26） |
| stroke-of-pen / 単発タスク（「今週末に確定申告」） | 4DX 自体が不要 |
| productivity-tool 比較（Notion vs Sunsama） | tool 選定で、capacity 診断ではない |

## 出典

*The 4 Disciplines of Execution* 第 2 版（2021）第 1 章 The Real Problem with Execution より蒸留。アンカー事例: Plant Manager of the Year（12 priorities → 1）と Towne Park Miami（土曜日に concrete wall を撤去した話）。

reading / interpretation / Parkinson's-Law devouring trap / most-important-confusion 警告など完全 RIA++ 展開は [`SKILL.md`](SKILL.md) を参照。
