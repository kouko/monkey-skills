[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# Using Systems Thinking Toolkit (Router)

`systems-thinking-toolkit` plugin 的意圖不明時 router。

## 使用時機

以下情況用 `/systems-thinking-toolkit:stt`：

- 不知道哪個方法適合你的情境
- 有東西在 spiral / oscillate / 撞天花板
- 卡在 vicious cycle / death spiral / boom-and-bust
- 想把一個糾結的情況畫出來，但不確定該叫哪個方法

如果你已經知道要叫哪個方法（`cld-craft` / `cld-archetypes` / `cld-overlay` / `simulation-modeling` / `strategy-lever-and-cascade` / `team-mental-model` / `manager-personality-quadrant`），就不需要 router — 直接呼叫 per-skill 命令。

## 你會得到

- 一個一問一答的意圖表，把問題路由到 7 個功能 skill（`cld-craft` / `cld-archetypes` / `cld-overlay` / `team-mental-model` / `simulation-modeling` / `strategy-lever-and-cascade` / `manager-personality-quadrant`）的其中一個。
- 每一列都附 EN + zh-TW + JA 觸發語（v0.5 加入）。
- 「I have a CLD」段落的前提條件清楚標示（v0.4 patch）。
- 真的判斷不出意圖時，預設兜底到 **`cld-craft`**。

## 邊界條件

- 已經知道要哪個方法的人不用走 — 直接叫 per-skill 命令。
- 不是方法本身的替代品 — router 只推薦並交棒，不解釋方法。
- 不是用來把多個方法湊在一個 workflow 裡 — 選一個；下一個方法需要時再呼叫 router 一次。

## 預設兜底

narrowing question 跑完後意圖仍然不明，就預設導到 **`cld-craft`**。它是 carry-1 的 prose → CLD 翻譯器，是下游 skill 共用的基礎；就算最後其實需要別的下游 skill，先把 diagram 做出來這件事很難算錯。

## 相關

- 完整路由表：[`SKILL.md`](SKILL.md)
- Plugin 概要：[`../../README.md`](../../README.md)
- 完整 skill 地圖：[`../../INDEX.md`](../../INDEX.md)

## 來源

這個入口 skill 是 monkey-skills 內部用的（仿照 `using-philosophers-toolkit` 樣式）。被路由的 7 個功能 skill 是從 Dennis Sherwood《Seeing the Forest for the Trees》(Nicholas Brealey, 2002) 蒸餾而來。
