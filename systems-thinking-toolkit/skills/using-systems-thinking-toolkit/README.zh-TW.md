[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# using-systems-thinking-toolkit

入口 / 路由 skill — 用一個問題「你想做什麼？」找出最符合情境的系統思考方法。

## 使用時機

- 你懷疑某個系統思考方法可用，但不確定要叫哪個。
- 使用者描述一個模糊型樣（「事情一直變糟」、「我們把花費翻倍但營收不動」）— 在伸手撈特定 skill 之前，讓路由器先分類。

## 啟動方式

`/systems-thinking-toolkit:stt`

（並沒有真正叫 "stt" 的 skill — 這個 slash command 就是觸發這個路由 skill。）

## 你會得到

- 一個一問一答意圖表，把問題路由到當前 7 個功能 skill（cld-craft / cld-archetypes / cld-overlay / team-mental-model / simulation-modeling / strategy-lever-and-cascade / manager-personality-quadrant）。v0.6 將 `innovaction-martian-test` 吸收進 strategy Step 5；v0.4 將 loop-and-link-primitives 吸收進 cld-craft Step 11。
- 誠實的「不要拼湊多種方法」規則 + 不確定時預設給 **`cld-craft`**（carry-1 prose→CLD 製造者）的兜底。

## 邊界條件

- 已經知道要哪個方法的人不用走 — 直接叫 per-skill 命令。
- 不是方法本身的替代品 — 路由器只推薦並交棒，不解釋方法。
- 不是每個問題都需要系統思考 — 若沒有方法符合，路由器會誠實這樣說。

## 參照

- 完整路由邏輯：[SKILL.md](SKILL.md)
- 完整 plugin 地圖：[`../../INDEX.md`](../../INDEX.md)

## 來源

這個入口 skill 是 monkey-skills 內部用的（仿照 `using-philosophers-toolkit` 樣式）。被路由的 9 個 skill 是從 Dennis Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002) 蒸餾而來。
