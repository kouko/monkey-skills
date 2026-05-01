# 4dx-audit（consultant-mode エントリーポイント）

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 4DX plugin の consultant-mode エントリー skill — ユーザーが既に持っている資料を構造化された 4DX audit ＋ 順序付き next-move roadmap に統合する。

## この skill は何をするか

本 plugin の他の 11 skill は **coach-mode**：Socratic 対話、ステップ・バイ・ステップ、ゼロから。この skill は **consultant-mode**：ユーザーが strategy doc / OKR / KPI dashboard / scoreboard / 議事録を渡すと、skill が全部読み、4DX 5-layer フレームワークで診断し、3-5 個の優先順位付き next move を出力する — 各 move は対応する coach-mode D-skill に route される。

5 ステップ：

1. **Inventory** — 提供された artifact を列挙
2. **Map** — 内容を 5 layer（L1 WIG / L2 Lead measure / L3 Scoreboard / L4 Cadence / L5 Substrate）に対応付け
3. **Diagnose** — 各 layer を `well-formed` / `malformed` / `absent` / `wrong-shape` でラベル付け、書籍の standard を引用
4. **Gap ＋ risk の特定** — 順序、Goodhart、参加崩壊、capacity 崩壊、frame 混同
5. **Prescribe** — 3-5 個の優先行動、各々を具体的な coach skill に route

## いつ起動するか

- **EN** — "Here's our strategy doc — help me 4DX it", "Audit our 4DX given this context"
- **JP** —「策略 doc を 4DX 視点で診断して」「うちの OKR を 4DX に整理したい」「資料を渡すから 4DX 視点で見て」「4DX 入れたが何が抜けてる？」
- **zh-TW** —「這是我們的策略 doc，幫看 4DX 怎麼套」「資料都在這，幫我用 4DX 框架釐清」

起動シグネチャ：**artifact が豊富な query ＋ 明示的な 4DX-framing ask**。artifact なしの cold-start query は `using-four-dx-coach` へ。

## 使わない場面

| 状況 | 代わりに |
|---|---|
| Cold-start、artifact なし | `using-four-dx-coach`（router が scope triage）|
| 単一 discipline ＋ その discipline の full context | 該当 D-skill を直接（例：`4dx-d1-wig-formulation`）|
| Socratic step-by-step coaching を希望 | coach-mode D-skill、audit ではない |
| 非 4DX framework の audit（OKR / BSC / agile retro）| 範囲外 — `using-four-dx-coach` で handoff |
| 別の coach skill 進行中 | audit reframing で中断しない |
| 純粋な venting / 4DX-framing 意図なし | router か他のサポート |

## 出力フォーマット（簡略版）

```markdown
# 4DX Audit — [context label / 日付]

## Inventory
- [読んだ artifact]

## Layer status
| Layer | Status | Finding |
|---|---|---|
| L1 WIG | malformed | [理由 ＋ standard 引用] |
| ... |

## Gaps ＋ risks
- [layer 横断の問題]

## Recommendations（優先順）
1. **[行動]** — [理由] → run `[skill-slug]`
2. ...

## 推奨 next move
[最初にどの skill を走らせるか ＋ 理由]
```

## Source citation

The 4 Disciplines of Execution（2nd ed., 2021）— McChesney / Covey / Huling / Thele / Walker。横断的引用（Foreword ＋ Ch 1 framing ＋ Ch 6 selection ＋ Ch 10 sustaining）。

Consultant-craft 参考は [`references/industry-grounding.md`](references/industry-grounding.md) を参照：Block（*Flawless Consulting* 3rd ed. 2011）、Schein（*Process Consultation* 1969 ／ *Helping* 2009）、Maister-Green-Galford（*The Trusted Advisor* 2000）、Adler ＆ Van Doren（*How to Read a Book* rev. 1972）。

## 関連

- [`SKILL.md`](SKILL.md) — 完全な audit protocol（5 ステップ ＋ 各 layer の診断 standard）
- Plugin router [`using-four-dx-coach`](../using-four-dx-coach/) — cold-start ／ 非 4DX query
- 11 個の coach-mode D-skill — audit が route する deep-dive 先
