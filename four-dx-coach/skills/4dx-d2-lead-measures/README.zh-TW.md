# 4dx-d2-lead-measures（topic router）

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> D2 lead-measure 的 topic-router。當 role（solo / leader-facilitator / member-influencer）不明確時觸發。

## 這個 router 做什麼

捕捉「幫我找 lead measure」這類沒講清楚 role 的問題，用 Socratic 一問釐清 role，分派到 3 個 atomic D2 skill 之一。本身不跑 D2 protocol。

## 何時觸發

- "Help me with lead measures" / "How do I find lead measures?" / "Daily action that drives the goal"
- 「lead measure を決めたい」「lead measure の探し方」「先行指標の選び方」
- 「幫我找 lead measure」「怎麼挑領先指標」「每天該做什麼才會推動目標」
- 任何沒指明 role 的 D2 lead-measure 詢問

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| role 明示（「我自己的 lead 給我自己的 goal」） | 直接 `4dx-d2-personal-lead-measure-discovery` |
| role 明示（「帶 team 挑 lead」） | 直接 `4dx-d2-team-lead-measure-facilitation` |
| role 明示（「老闆訂的 lead」） | 直接 `4dx-d2-member-lead-measure-influence` |
| WIG 還沒定 | 先 `4dx-d1-wig-formulation` |
| scoreboard / 顯示問題 | `4dx-d3-scoreboard` topic-router |
| 週 cadence / WIG Session | `4dx-d4-cadence` topic-router |

## 配下的 atomic skill

| Slug | Role | Verb | 產出 |
|---|---|---|---|
| `4dx-d2-personal-lead-measure-discovery` | Solo | Discover | 2-3 個 personal lead（兩軸 + Goodhart 自檢） |
| `4dx-d2-team-lead-measure-facilitation` | Team-leader | Facilitate | 2-3 個 team-owned lead（veto 不 dictate），對齊 team WIG |
| `4dx-d2-member-lead-measure-influence` | Team-member | Influence-map | per-lead 0-5 評分 + 1-2 focus lead + 「我這沒影響力」升報路徑 |

## 延伸

- [`SKILL.md`](SKILL.md) 完整 routing logic + Socratic 決策樹 + hand-off scripts
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) 處理 cold-start / 4DX 範圍外問題
- 姊妹 topic-router [`4dx-d3-scoreboard`](../4dx-d3-scoreboard/) 處理 D3 scoreboard 的 role 釐清
