# 4dx-d3-scoreboard（topic router）

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> D3 scoreboard の topic-router。role（solo / leader-designer / member-reader）が曖昧なときに起動する。

## このルーターの役割

「scoreboard どうしよう」のような role + verb（build vs read）未指定の質問を捕捉し、Socratic な 1 問で釐清して、3 つの atomic D3 skill のいずれかに振り分ける。D3 protocol 本体は走らせない。

## 起動するとき

- "Help me with the scoreboard" / "How should I track this?" / "Dashboard advice" / "Players' scoreboard"
- 「scoreboard を設計したい」「どう可視化すれば」「ダッシュボードの相談」
- 「幫我搞 scoreboard」「怎麼追蹤」「儀表板要怎麼設計」「球員視角記分板」
- role + verb が明示されない D3 scoreboard 質問

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| role + verb 明示（「自分の scoreboard」） | `4dx-d3-personal-scoreboard` に直接 |
| role + verb 明示（「team の scoreboard を design」） | `4dx-d3-team-lead-scoreboard-design` に直接 |
| role + verb 明示（「team の scoreboard を read」） | `4dx-d3-member-scoreboard-reading` に直接 |
| WIG / lead が未定義 | 先に `4dx-d1-wig-formulation` / `4dx-d2-lead-measures` |
| cadence / WIG Session | `4dx-d4-cadence` topic-router |
| enterprise BI（Tableau / PowerBI / multi-team rollup） | 4DX 圏外 — `using-four-dx-coach` |

## 配下の atomic skill

| Slug | Role | Verb | Returns |
|---|---|---|---|
| `4dx-d3-personal-scoreboard` | Solo | Design own | 一目で読める personal scoreboard（≤4 要素 / 5-second test） |
| `4dx-d3-team-lead-scoreboard-design` | Team-leader | Facilitate team-built | team が build する public scoreboard（veto-not-dictate） |
| `4dx-d3-member-scoreboard-reading` | Team-member | Read + locate | member の read + 個人貢献の locate + 壊れている場合の escalation |

## 関連

- [`SKILL.md`](SKILL.md) に完全な routing logic + Socratic 決定木 + hand-off スクリプト
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) は cold-start / 4DX 圏外質問を担当
- 姉妹 topic-router [`4dx-d2-lead-measures`](../4dx-d2-lead-measures/) は D2 lead-measure の role 釐清を担当
