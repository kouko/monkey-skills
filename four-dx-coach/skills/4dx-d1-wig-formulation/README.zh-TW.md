# 4dx-d1-wig-formulation（topic router）

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> D1 WIG 形成的 topic-router。當 scope（個人 / team-leader / team-member）和 verb（define / select / comprehend）都不明確時觸發。

## 這個 router 做什麼

捕捉「幫我搞 WIG」這種 actor + verb 都沒講清楚的問題，用 Socratic 的 (scope, verb) 一問釐清後，分派到 3 個 atomic D1 skill 之一。本身不跑 WIG protocol。

## 何時觸發

- "Help me with my WIG" / "How do I set a WIG?" / "WIG selection" / "Pick the right goal"
- 「WIG を決めたい」「WIG の作り方」「WIG をどう選ぶ」「目標 (WIG) の作成」
- 「幫我搞 WIG」「怎麼設 WIG」「怎麼選 WIG」「目標太多怎麼挑」
- 任何沒指明 actor + verb 的 WIG 形成詢問

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| scope + verb 都明示（「我自己的 WIG: From X to Y」） | 直接 `4dx-d1-wig-formulation` |
| 「組織 Primary WIG，用 Battles 2x2」 | 直接 `4dx-d1-wig-formulation` |
| 「老闆給的 WIG」 | 直接 `4dx-d1-wig-formulation` |
| whirlwind / 時間 audit | `4dx-meta-whirlwind-triage` |
| 往下 cascade 到 N 個 sub-team | `4dx-d1-wig-cascade` |
| lead measure / scoreboard / cadence | D2 / D3 / D4 |

## 配下的 atomic skill

| Slug | Scope | Verb | 產出 |
|---|---|---|---|
| `4dx-d1-wig-formulation` | Personal（solo） | Define | From-X-to-Y-by-When 格式的個人 WIG 一條 |
| `4dx-d1-wig-formulation` | Team-leader | Select | Battles 2x2 挑出組織級 Primary WIG |
| `4dx-d1-wig-formulation` | Team-member | Comprehend | member 對繼承 team WIG 如何落到自己日常的理解 |

## 延伸

- [`SKILL.md`](SKILL.md) 完整 routing logic + Socratic 決策樹 + hand-off scripts
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) 處理 cold-start / 4DX 範圍外問題
