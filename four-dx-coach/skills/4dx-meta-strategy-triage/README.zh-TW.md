# 4dx-meta-strategy-triage（multi-scope skill）

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 「該不該用 4DX？」的多 scope gate —— 在 install D1-D4 **之前** 判斷 4DX 是否適配當前情境。偵測 scope（個人 vs team-leader）並載入對應的 triage protocol。

## 這個 skill 做什麼

從 user query 偵測 scope（solo vs team-leader），載入 `protocols/` 中對應的 protocol。跑 Socratic triage，從 rubric 回傳一個 discrete verdict —— **APPLICABLE / TEAM-APPLICABLE**（往 D1 走）或多個 redirect verdict 之一（導向更適合的方法論）。在不適合時拒絕 4DX 才是這個 skill 的工作，而不是把 goal 凹回 4DX 的形狀。

## 為何合併

原本是 3 skill（atomic triage 2 + topic-router 1）。router 是 2 個共享 Ch 1 stroke-of-pen / behavioral-change 區別的 protocol 上面薄薄一層 disambiguation step。整併成 multi-file scope-flex skill：保留所有 execution detail、把 6-verdict rubric 與 Ch 1 區別 deduplicate、audit footer + trigger-list 一元化。SKILL.md orchestrator 直接負責 scope detection + protocol routing。

## 配下的 protocol

| Mode | Load protocol | Agent voice |
|---|---|---|
| Solo 個人 | [`protocols/personal-mode.md`](protocols/personal-mode.md) | personal coach |
| Team-leader（3-12 直屬團隊） | [`protocols/team-mode.md`](protocols/team-mode.md) | leader 的 consultant |

（member scope 刻意不收 —— member 是繼承 WIG 的一方，不 triage 方法論-fit。member 的 query 由 SKILL.md edge-case 導向 `4dx-d1-wig-formulation`。）

## 何時觸發

- **Solo** — "Should I use 4DX for X?" / 「4DX 適合我這個目標嗎？」「我這個目標可以用 4DX 嗎？」
- **Team-leader** — "Should our team adopt 4DX?" / 「我們團隊適合導入 4DX 嗎？」「我這個團隊用 4DX 有用嗎？」
- **曖昧 scope fallback** — "Is 4DX a good fit?" / 「4DX 適合嗎？」「4DX 會不會太重？」（actor 未明示）
- 各 mode 多語言（EN / JP / zh-TW）—— 完整 trigger 清單見 SKILL.md

scope 不明的 query，會用涵蓋兩種 mode 的 Socratic 一問釐清後再分流。

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| 已決定用 4DX，問「怎麼開始？」 | D1 skills（whirlwind-triage / primary-wig-selection / wig-formulation） |
| 特定 discipline 問題（lead measure / scoreboard / WIG session） | 對應的 D-skill |
| 是 member、繼承上面定的 WIG | `4dx-d1-wig-formulation`（member 不 triage） |
| 企業 multi-team 部署（cascading WIGs） | 直接讀 book Ch 6-10 + `4dx-d1-wig-cascade` |
| 非 4DX 方法論（OKR / agile / habit-stacking） | plugin router `using-four-dx-coach` |

## 來源

The 4 Disciplines of Execution（第 2 版, 2021）— McChesney / Covey / Huling / Thele / Walker。Chapter 1（The Real Problem With Execution — stroke-of-pen vs behavioral-change 的區別）、Chapter 6（Choosing Where to Focus — Strategy Map; goal-shape carve）。

industry grounding 集中在 [`references/industry-grounding.md`](references/industry-grounding.md)：Kotter（urgency upstream）、Heath & Heath（Path environment）、March（exploration vs exploitation）、Galbraith（STAR alignment）、Schein（assumption-layer culture-fit）。

## 延伸

- [`SKILL.md`](SKILL.md) —— orchestrator 含完整 scope-detection logic + routing table + cross-mode boundary
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) 處理 cold-start / 4DX 圈外問題
