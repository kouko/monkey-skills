# 4dx-d1-wig-formulation（topic router）

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> D1 WIG 形成の topic-router。scope（個人 / team-leader / team-member）と verb（define / select / comprehend）が曖昧なときに起動する。

## このルーターの役割

「WIG どうしよう」のような actor + verb 未指定の質問を捕捉し、Socratic な (scope, verb) 1 問で釐清して、3 つの atomic D1 skill のいずれかに振り分ける。WIG protocol 本体は走らせない。

## 起動するとき

- "Help me with my WIG" / "How do I set a WIG?" / "WIG selection" / "Pick the right goal"
- 「WIG を決めたい」「WIG の作り方」「WIG をどう選ぶ」「目標 (WIG) の作成」
- 「幫我搞 WIG」「怎麼設 WIG」「怎麼選 WIG」「目標太多怎麼挑」
- actor + verb のいずれも明示されていない WIG 形成質問

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| scope + verb 明示（「自分の WIG: From X to Y」） | `4dx-d1-wig-formulation` に直接 |
| 「組織の Primary WIG を Battles 2x2 で」 | `4dx-d1-wig-formulation` に直接 |
| 「上司から降りてきた WIG」 | `4dx-d1-wig-formulation` に直接 |
| whirlwind / 時間 audit | `4dx-meta-whirlwind-triage` |
| 下位 N team への cascade | `4dx-d1-wig-cascade` |
| lead measure / scoreboard / cadence | D2 / D3 / D4 |

## 配下の atomic skill

| Slug | Scope | Verb | Returns |
|---|---|---|---|
| `4dx-d1-wig-formulation` | 個人（solo） | Define | From-X-to-Y-by-When 形式の personal WIG 1 本 |
| `4dx-d1-wig-formulation` | Team-leader | Select | Battles 2x2 で組織レベルの Primary WIG |
| `4dx-d1-wig-formulation` | Team-member | Comprehend | 上位 team WIG が自分の日々の slice にどう降りてくるかの理解 |

## 関連

- [`SKILL.md`](SKILL.md) に完全な routing logic + Socratic 決定木 + hand-off スクリプト
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) は cold-start / 4DX 圏外質問を担当
