# 4dx-d4-cadence（multi-scope skill）

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> D4 每週 Cadence of Accountability（WIG Session）的 multi-scope coach。涵蓋使用者可能身處的 4 種角色：solo（參與者）/ team-leader（facilitator）/ team-member（session 前 prep / session 後 debrief）。

## 這個 skill 做什麼

從 query 偵測 scope（role + timing），載入 `protocols/` 下對應的 protocol。Account → Review → Plan 三段語法 4 mode 共用；agent 的 voice 隨 mode 切換（solo = peer-witness、facilitator = consultant-to-leader、member = personal-coach）。4 個 protocol 共用 standards（`account-review-plan-agenda`、`commitment-shape`、`whirlwind-exclusion`、`sacred-cadence`）。

## 背景 — 為什麼合併

原本 5 個 skill（atomic D4 × 4 + topic-router × 1）。router 是 4 個 R/I/E/B 共用 80%+ 內容、幾乎對稱的 protocol 之間的薄分歧層。合併成一個 multi-file scope-flex skill：執行細節全保留、standards 去重、audit footer 與 trigger 清單整合成單一份。SKILL.md orchestrator 直接負責 scope 偵測 + protocol 分派，不再另立 router skill。

## 配下的 protocol

| Mode | Protocol | Agent voice |
|---|---|---|
| solo、session 進行中 | [`protocols/solo-session.md`](protocols/solo-session.md) | peer-witness |
| team-leader、session 進行中 | [`protocols/team-leader-session.md`](protocols/team-leader-session.md) | consultant-to-leader |
| team-member、session 前 | [`protocols/member-prep.md`](protocols/member-prep.md) | personal coach to member |
| team-member、session 後 | [`protocols/member-debrief.md`](protocols/member-debrief.md) | personal coach to member |

## 何時觸發

- **Solo** — "Run my weekly WIG Session" /「毎週の WIG Session を回したい」/「想要每週固定 review 維持目標進度」
- **Team-leader** — "Facilitate our team WIG meeting" /「チームの WIG Session を運営する」/「帶我們團隊的 weekly WIG Session」
- **Member-prep** — "Prepare my commitment for next WIG Session" /「次の WIG Session の commitment を準備したい」/「下次 WIG Session 我要準備 commitment」
- **Member-debrief** — "I missed my commitment last week" /「先週の commitment 果たせなかった、どう振り返る？」/「上週 commitment 沒達成，怎麼面對？」
- EN / JP / zh-TW 全 mode 涵蓋（完整 trigger 清單見 SKILL.md）

如 (role, timing) 不明，會先問一個涵蓋 4 mode 的 Socratic disambiguation 問題再分派。

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| cadence 已經斷好幾週 | `4dx-sustain-momentum-rescue`（先 rescue 再 restart） |
| 還沒有 WIG / lead measure / scoreboard | 先做 D1 / D2 / D3，D4 沒東西可跑 |
| sprint review / PI planning / OKR check-in / 1-on-1 / status report | 4DX 範圍外 — `using-four-dx-coach` |
| daily stand-up / scrum daily | cadence 錯（每日 ≠ 每週）、format 錯 |
| 年度 / 季度 retro | cadence scope 錯 |
| member 不知道 team 的 WIG / lead measure | 先 `4dx-d1-wig-formulation` |
| member 連續 3 次以上 miss | commitment 設計問題；用 member-prep mode 重新設計，不是 debrief |

## 來源

《The 4 Disciplines of Execution》第 2 版（2021）— McChesney / Covey / Huling / Thele / Walker。Ch. 5（Discipline 4: Create a Cadence of Accountability）、Ch. 10（Sustaining 4DX — Susan/Marcus dialogue）、Ch. 15（Applying Discipline 4）。

Industry grounding 整合於 [`references/industry-grounding.md`](references/industry-grounding.md)：Rogelberg、Lencioni、Reinertsen、Edmondson（× 2）、Pfeffer、Drucker、Cialdini、Eurich、Wiseman。

## 延伸

- [`SKILL.md`](SKILL.md) — 完整 scope 偵測 logic + 分派表 + cross-mode boundary 的 orchestrator
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) 處理 cold-start / 4DX 範圍外問題
