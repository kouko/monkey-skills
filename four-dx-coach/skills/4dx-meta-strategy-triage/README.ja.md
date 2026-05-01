# 4dx-meta-strategy-triage（multi-scope skill）

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 「4DX を使うべき？」を D1-D4 install **前** に判定する multi-scope gate。scope（個人 vs team-leader）を検出し、対応する triage protocol をロードする。

## このスキルの役割

ユーザのクエリから scope（solo vs team-leader）を検出し、`protocols/` の対応 protocol をロード。Socratic な triage を走らせ、rubric から discrete な verdict を 1 つ返す —— **APPLICABLE / TEAM-APPLICABLE**（D1 へ進む）か、より適合した方法論へ振り分ける redirect verdict のいずれか。fit しない 4DX を断ることがこのスキルの仕事であり、ゴールを 4DX 形に曲げ戻すことではない。

## 統合の経緯

元は 3 skill（atomic triage 2 + topic-router 1）。router は Ch 1 の stroke-of-pen / behavioral-change 区別を共有する 2 protocol の上の薄い disambiguation step だった。multi-file scope-flex skill に統合：execution detail を全保持、6-verdict rubric と Ch 1 区別を deduplicate、audit footer + trigger-list を一元化。SKILL.md orchestrator が scope detection + protocol routing を直接担う。

## 配下の protocol

| Mode | Load protocol | Agent voice |
|---|---|---|
| Solo 個人 | [`protocols/personal-mode.md`](protocols/personal-mode.md) | personal coach |
| Team-leader（3-12 直属メンバー） | [`protocols/team-mode.md`](protocols/team-mode.md) | leader への consultant |

（member scope は意図的に不在 —— member は WIG を継承する側で、方法論-fit の triage はしない。member クエリは SKILL.md edge-case で `4dx-d1-wig-formulation` へ振り分け。）

## 起動するとき

- **Solo** — "Should I use 4DX for X?" / 「この目標に 4DX 使える？」「4DX 自分に合ってるか分からない」
- **Team-leader** — "Should our team adopt 4DX?" / 「私たちのチームに 4DX 合うか？」「うちのチームで 4DX 効くかな」
- **曖昧 scope fallback** — "Is 4DX a good fit?" / 「4DX 適してる？」「4DX 合ってる？」（actor 未指定）
- 各 mode で多言語（EN / JP / zh-TW）対応 —— full trigger list は SKILL.md 参照

scope が曖昧なクエリには、両 mode をカバーする Socratic な 1 問で disambiguate してから振り分ける。

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| 4DX 既決で「どう始める？」 | D1 skills（whirlwind-triage / primary-wig-selection / wig-formulation） |
| 特定 discipline の質問（lead measure / scoreboard / WIG session） | 対応の D-skill |
| 上から WIG を渡された member | `4dx-d1-wig-formulation`（member は triage しない） |
| 企業 multi-team rollout（cascading WIGs） | book Ch 6-10 直接 + `4dx-d1-wig-cascade` |
| 4DX 圏外の方法論（OKR / agile / habit-stacking） | plugin router `using-four-dx-coach` |

## ソース

The 4 Disciplines of Execution（第 2 版, 2021）— McChesney / Covey / Huling / Thele / Walker。Chapter 1（The Real Problem With Execution — stroke-of-pen vs behavioral-change の区別）、Chapter 6（Choosing Where to Focus — Strategy Map; goal-shape carve）。

industry grounding は [`references/industry-grounding.md`](references/industry-grounding.md) に集約：Kotter（urgency upstream）、Heath & Heath（Path environment）、March（exploration vs exploitation）、Galbraith（STAR alignment）、Schein（assumption-layer culture-fit）。

## 関連

- [`SKILL.md`](SKILL.md) —— orchestrator with full scope-detection logic + routing table + cross-mode boundary
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) は cold-start / 4DX 圏外の質問を担当
