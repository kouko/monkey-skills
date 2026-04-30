# 4dx-d4-cadence（topic router）

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> D4 週次 cadence の topic-router。role（solo / leader / member）と timing（前 / 最中 / 後）が曖昧なときに起動する。

## このルーターの役割

「WIG Session どうしよう」のような role + timing 未指定の質問を捕捉し、Socratic な (role, timing) 1 問で釐清して、4 つの atomic D4 skill のいずれかに振り分ける。session protocol 本体は走らせない。

## 起動するとき

- "Help with my WIG Session" / "Weekly cadence advice" / "WIG Session prep" / "Set up the cadence"
- 「WIG Session のこと」「weekly cadence の運営」「毎週の WIG ミーティング」「週次レビューの相談」
- 「WIG Session 怎麼跑」「每週節奏」「WIG 週會」「每週 review」「weekly 開會」
- role + timing いずれも明示されていない cadence 質問

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| 「自分一人の session を回す」 | `4dx-d4-personal-wig-session` に直接 |
| 「team の session を facilitate」 | `4dx-d4-team-wig-session-lead` に直接 |
| 「明日の session 用に commitment を準備」 | `4dx-d4-member-commitment-prep` に直接 |
| 「session 終わった、commitment を落とした」 | `4dx-d4-member-account-debrief` に直接 |
| 数週間 cadence が崩れている | `4dx-sustain-personal-momentum-rescue`（再起動より rescue が先） |
| WIG / lead / scoreboard 未整備 | まず D1 / D2 / D3、D4 は載せる対象がない |
| sprint review / OKR check-in / 1-on-1 | 4DX 圏外 — `using-four-dx-coach` |

## 配下の atomic skill

| Slug | Role | Timing | Returns |
|---|---|---|---|
| `4dx-d4-personal-wig-session` | Solo（agent = peer-witness） | 最中 | 20-30 分の Account → Review → Plan、自選 1-2 commitment |
| `4dx-d4-team-wig-session-lead` | Team-leader（facilitator） | 最中 | commitments-not-assignments + veto-not-dictate 規範下のアジェンダ + Socratic 問い |
| `4dx-d4-member-commitment-prep` | Team-member | 前 | 具体的・influenceable・single-step commitment、口頭で言える形 |
| `4dx-d4-member-account-debrief` | Team-member | 後 | 正直な self-account: 達成 / 部分 / 未達 + 診断（次回 prep へ feedback） |

## 関連

- [`SKILL.md`](SKILL.md) に完全な routing logic + Socratic 決定木 + hand-off スクリプト
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) は cold-start / 4DX 圏外質問を担当
