# 4DX D2 — Lead Measure Discovery

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> D2 の中核 — WIG を予測でき *かつ* 自分で動かせる lead measure を 2-3 個発見する。

## このスキルが起動するとき

- 「目標は決まったが、毎日何をすればいい？」
- 「先行指標って何を選べばいい？」「どの指標を見れば正しい道か分かる？」
- 「頑張ってるのに数字が動かない、何が間違ってる？」
- これから 20 個以上の metric を載せた dashboard を作ろうとしている
- 名乗っている lead が実は短周期の lag（週次体重、月次売上）か、自分で動かせない外生変数（market direction）

## 何をするか（プロトコル概要）

Socratic な発見作業 — agent は代筆しない。2 軸とも真でなければならない:

1. **WIG gate check** — WIG を 1 文（X → Y by いつ）で述べてもらう。曖昧なら D1 に差し戻して停止
2. **候補行動を 5-10 個 brainstorm** — counter-intuitive を押し出す（「あなたの目標版『子供の足を測る』は何？」）
3. **2 軸スコアリング（1-5 × 1-5）** — predictive + influenceable、それぞれ 1 文の causal chain 付き
4. **どちらかが ≤3 のものは捨てる** — predictive ≤3 = noise、influenceable ≤3 = rainfall 級
5. **2-3 個に絞る — frequency 1 + quality 1 が canonical** — frequency 系（週 N 回 X をやる）+ quality 系（各 X が基準 Y を満たす）
6. **operational definition** — 各 lead について「何をもって done か」「いつ・どう log するか」「週次 target」を、第三者が質問せず実行できる粒度で書く
7. **causal chain を書面で予測** — 1 段落：「6 週間 lead 目標を達成すれば lag が [Y] まで動くと期待する。理由は……」
8. **出力** — lead 2-3 個 + operational definition + 週次 target → D3（表示）と D4（review）に handoff

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| まだ WIG が定義されていない | 先に `4dx-d1-personal-wig-defining` — 曖昧 WIG の上の lead は noise |
| stroke-of-pen な goal（単一の判断で終わる） | lead measure の概念が当てはまらない |
| 週単位で測れない lag（drug discovery、長編小説） | 週次 lead は theatrical になる。milestone 単位を検討 |
| 表示 / scoreboard の話をしたい | `4dx-d3-personal-scoreboard` |
| lead はあるが 4 週以上 lag が動かない | `4dx-sustain-personal-momentum-rescue`（five optimizing questions） |

## 出典

*The 4 Disciplines of Execution* 第 2 版、第 3 章 Discipline 2: Act on the Lead Measures + 第 13 章より蒸留。3 つの anchor case: 靴の小売チェーン（4,500 店舗で「子供の足を測る」が counter-intuitive な lead と判明）、Younger Brothers Construction（安全 57 → 12 件 / 年）、Towne Park valet（retrieval-time が lead）。

lag-masquerading-as-lead / lead-data-too-hard-so-skipped / Goodhart 対策（frequency × quality の組合せ + 4 週ごとの causal-chain check）を含む完全 RIA++ 展開は [`SKILL.md`](SKILL.md) を参照。
