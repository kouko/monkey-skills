# 4dx-d3-scoreboard（topic router）

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> D3 scoreboard 的 topic-router。當 role（solo / leader-designer / member-reader）不明確時觸發。

## 這個 router 做什麼

捕捉「幫我搞 scoreboard」這類沒講清楚 role + verb（build vs read）的問題，用 Socratic 一問釐清，分派到 3 個 atomic D3 skill 之一。本身不跑 D3 protocol。

## 何時觸發

- "Help me with the scoreboard" / "How should I track this?" / "Dashboard advice" / "Players' scoreboard"
- 「scoreboard を設計したい」「どう可視化すれば」「ダッシュボードの相談」
- 「幫我搞 scoreboard」「怎麼追蹤」「儀表板要怎麼設計」「球員視角記分板」
- 任何沒指明 role + verb 的 D3 scoreboard 詢問

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| role + verb 明示（「我自己的 scoreboard」） | 直接 `4dx-d3-personal-scoreboard` |
| role + verb 明示（「設計 team 的 scoreboard」） | 直接 `4dx-d3-team-lead-scoreboard-design` |
| role + verb 明示（「讀 team 的 scoreboard」） | 直接 `4dx-d3-member-scoreboard-reading` |
| WIG / lead 還沒定 | 先 `4dx-d1-wig-formulation` / `4dx-d2-lead-measures` |
| cadence / WIG Session | `4dx-d4-cadence` topic-router |
| enterprise BI（Tableau / PowerBI / 跨 team rollup） | 4DX 範圍外 — `using-four-dx-coach` |

## 配下的 atomic skill

| Slug | Role | Verb | 產出 |
|---|---|---|---|
| `4dx-d3-personal-scoreboard` | Solo | Design own | 一眼可讀的 personal scoreboard（≤4 元素 / 5-second test） |
| `4dx-d3-team-lead-scoreboard-design` | Team-leader | Facilitate team-built | 公開 team scoreboard，由 team 親手 build（veto 不 dictate） |
| `4dx-d3-member-scoreboard-reading` | Team-member | Read + locate | member 的 read + 個人貢獻定位 + 板子壞掉的升報腳本 |

## 延伸

- [`SKILL.md`](SKILL.md) 完整 routing logic + Socratic 決策樹 + hand-off scripts
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) 處理 cold-start / 4DX 範圍外問題
- 姊妹 topic-router [`4dx-d2-lead-measures`](../4dx-d2-lead-measures/) 處理 D2 lead-measure 的 role 釐清
