# 4dx-d2-lead-measures（topic router）

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> D2 lead-measure の topic-router。role（solo / leader-facilitator / member-influencer）が曖昧なときに起動する。

## このルーターの役割

「lead measure をどうしよう」のような role 未指定の質問を捕捉し、Socratic な 1 問で role を釐清して、3 つの atomic D2 skill のいずれかに振り分ける。D2 protocol 本体は走らせない。

## 起動するとき

- "Help me with lead measures" / "How do I find lead measures?" / "Daily action that drives the goal"
- 「lead measure を決めたい」「lead measure の探し方」「先行指標の選び方」
- 「幫我找 lead measure」「怎麼挑領先指標」「每天該做什麼才會推動目標」
- role が明示されない D2 lead-measure 質問

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| role 明示（「自分の goal の自分の lead」） | `4dx-d2-lead-measures` に直接 |
| role 明示（「team の選定を facilitate」） | `4dx-d2-lead-measures` に直接 |
| role 明示（「上司から降りてきた lead」） | `4dx-d2-lead-measures` に直接 |
| WIG が未定義 | 先に `4dx-d1-wig-formulation` |
| scoreboard / 可視化の質問 | `4dx-d3-scoreboard` topic-router |
| 週 cadence / WIG Session | `4dx-d4-cadence` topic-router |

## 配下の atomic skill

| Slug | Role | Verb | Returns |
|---|---|---|---|
| `4dx-d2-lead-measures` | Solo | Discover | 2-3 個 personal lead（2 軸 + Goodhart self-check） |
| `4dx-d2-lead-measures` | Team-leader | Facilitate | 2-3 個 team-owned lead（veto-not-dictate）、team WIG に整合 |
| `4dx-d2-lead-measures` | Team-member | Influence-map | per-lead 0-5 score + 1-2 focus lead + no-influence escalation |

## 関連

- [`SKILL.md`](SKILL.md) に完全な routing logic + Socratic 決定木 + hand-off スクリプト
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) は cold-start / 4DX 圏外質問を担当
- 姉妹 topic-router [`4dx-d3-scoreboard`](../4dx-d3-scoreboard/) は D3 scoreboard の role 釐清を担当
