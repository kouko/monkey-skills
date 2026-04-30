# 4dx-d4-cadence（multi-scope skill）

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> D4 週次 Cadence of Accountability（WIG Session）の multi-scope coach。ユーザーが置かれる 4 つの役割すべてに対応：solo（参加者）/ team-leader（ファシリテーター）/ team-member（session 前 prep / session 後 debrief）。

## このスキルがすること

クエリから scope（role + timing）を検出し、`protocols/` 配下の対応 protocol を load する。Account → Review → Plan の 3 段グラマーは 4 mode 共通；agent の voice は mode ごとに切り替え（solo = peer-witness、facilitator = consultant-to-leader、member = personal-coach）。4 protocol すべてが共通 standards（`account-review-plan-agenda`、`commitment-shape`、`whirlwind-exclusion`、`sacred-cadence`）を参照する。

## 背景 — なぜマージしたか

元は 5 skill（atomic D4 × 4 + topic-router × 1）。router は 80% 以上の R/I/E/B を共有するほぼ対称な 4 protocol への薄い分岐ステップだった。1 つの multi-file scope-flex skill にマージ：execution 詳細はすべて維持、standards を重複排除、audit footer + trigger リストを 1 本化。SKILL.md orchestrator が scope 検出 + protocol routing を直接担当し、router skill を別立てしない。

## 配下の protocol

| Mode | Protocol | Agent voice |
|---|---|---|
| solo、session 最中 | [`protocols/solo-session.md`](protocols/solo-session.md) | peer-witness |
| team-leader、session 最中 | [`protocols/team-leader-session.md`](protocols/team-leader-session.md) | consultant-to-leader |
| team-member、session 前 | [`protocols/member-prep.md`](protocols/member-prep.md) | personal coach to member |
| team-member、session 後 | [`protocols/member-debrief.md`](protocols/member-debrief.md) | personal coach to member |

## 起動するとき

- **Solo** — "Run my weekly WIG Session" /「毎週の WIG Session を回したい」/「想要每週固定 review 維持目標進度」
- **Team-leader** — "Facilitate our team WIG meeting" /「チームの WIG Session を運営する」/「帶我們團隊的 weekly WIG Session」
- **Member-prep** — "Prepare my commitment for next WIG Session" /「次の WIG Session の commitment を準備したい」/「下次 WIG Session 我要準備 commitment」
- **Member-debrief** — "I missed my commitment last week" /「先週の commitment 果たせなかった、どう振り返る？」/「上週 commitment 沒達成，怎麼面對？」
- EN / JP / zh-TW 全 mode 対応（trigger 一覧は SKILL.md 参照）

(role, timing) が曖昧な場合は 4 mode をカバーする Socratic 質問を 1 つ投げて分岐する。

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| 数週間 cadence が崩れている | `4dx-sustain-momentum-rescue`（再起動より rescue が先） |
| WIG / lead measure / scoreboard 未整備 | まず D1 / D2 / D3、D4 は載せる対象がない |
| sprint review / PI planning / OKR check-in / 1-on-1 / status report | 4DX 圏外 — `using-four-dx-coach` |
| daily stand-up / scrum daily | 間違った cadence（毎日 ≠ 毎週）、間違った format |
| 年次 / 四半期レトロ | cadence scope が違う |
| member が team の WIG / lead measure を知らない | まず `4dx-d1-wig-formulation` |
| member が 3 週連続で miss | commitment 設計の問題；debrief ではなく member-prep mode で再設計 |

## ソース

『The 4 Disciplines of Execution』第 2 版（2021）— McChesney / Covey / Huling / Thele / Walker。Ch. 5（Discipline 4: Create a Cadence of Accountability）、Ch. 10（Sustaining 4DX — Susan/Marcus dialogue）、Ch. 15（Applying Discipline 4）。

Industry grounding は [`references/industry-grounding.md`](references/industry-grounding.md) に統合：Rogelberg、Lencioni、Reinertsen、Edmondson（× 2）、Pfeffer、Drucker、Cialdini、Eurich、Wiseman。

## 関連

- [`SKILL.md`](SKILL.md) — 完全な scope 検出 logic + 分岐表 + cross-mode boundary を含む orchestrator
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) は cold-start / 4DX 圏外質問を担当
