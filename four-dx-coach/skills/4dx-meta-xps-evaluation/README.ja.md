# 4DX Meta — Team XPS Evaluation

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 書本準拠の XPS（4 component × max 1.0 = max 4.0）でチームの 4DX 実行品質を audit し、band を判定、最弱 component を名指し、fix priority を 1 つ立てる。

## このスキルが起動するとき

- 「チームの 4DX 実行品質を評価」「うちの 4DX 機能してる？」「XPS 出して」
- 「4DX ちゃんと回ってるか診断して」
- 6-12 週運用後の四半期中 / 四半期末ヘルスチェック
- WIG が動かないとき、WIG が間違いと結論する前に execution を audit
- 「4DX をやっている」チームを引き継いだ外部 coach が baseline を取る

## 何をするか（プロトコル概要）

Auditor / consultant 声 — 事実、スコア、fix priority のみ。coaching も激励もしない:

1. **audit 対象を確定** — 1 team、WIG 明示、稼働週数。XPS は team 横断集計しない
2. **Component 1 — Establishing a Cadence（0.0-1.0）** — held / expected × meeting-discipline multiplier、書標準 100%
3. **Component 2 — Fulfilling High-Impact Commitments（0.0-1.0）** — fulfillment × specificity multiplier、書標準 90%+
4. **Component 3 — Optimizing Lead-Measures（0.0-1.0）** — 5 つの optimizing question + scoreboard 健全性、書標準 weekly 90%+
5. **Component 4 — Achieving Lag-Measure Results（0.0-1.0）** — actual / required、上限 1.0
6. **合計 + band 判定** — 3.6-4.0 excellence / 3.2-3.59 good / 2.5-3.19 fair / 0-2.49 significant concern
7. **fix priority（1-3 アクション）** — 最低 component から、同点は C1 > C2 > C3 > C4
8. **XPS report 配信** — `Components → Total → Band → Weakest → Fix priority`

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| solo / personal-coach モード | `4dx-sustain-momentum-rescue` |
| 今週の WIG session を回す（過去の audit ではない） | `4dx-d4-cadence` |
| 「そもそも 4DX を使うべきか」 | `4dx-meta-strategy-triage` |
| team 間の head-to-head ランキング | XPS は intra-team 自己診断、leaderboard ではない |
| 結果に対する権限 / 意図がない | audit-without-action は禁忌 |

## 出典

*The 4 Disciplines of Execution* 第 10 章 Sustaining 4DX Results and Engagement より蒸留。2 anchor case: Marriott（XPS が 70K-leader rollout の operating heartbeat — 週 7M+ commitments / 97%+ follow-through）、Susan/Bianca/Marcus（XPS で最弱 component を診断し targeted intervention — 「もっと頑張れ」ではない）。

no-compensation rule（各 component の上限は 1.0、好調が不調を masking 不可）と CE-32 〜 CE-37（averaging 違反 / cadence theater / lead-measure platitude / lag 駆動自己欺瞞 / audit-as-punishment / 5 番目 column 発明）を含む完全 RIA++ 展開は [`SKILL.md`](SKILL.md) を参照。
