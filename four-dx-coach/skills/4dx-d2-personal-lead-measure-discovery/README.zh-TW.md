# 4DX D2 — Lead Measure Discovery

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> D2 的核心 — 找出 2-3 個 lead measure，必須同時是「能預測 WIG」與「自己每天能動」。

## 何時觸發這個 skill

- 「我有目標了，但不知道每天該做什麼才會有結果」
- 「該追蹤什麼指標才知道我走在對的路上？」「[goal] 的 leading indicator 是什麼？」
- 「我以為我在做對的事，但結果沒變化」
- 即將做一個 20 個以上 metric 的 dashboard
- 目前列的 lead 其實是短週期的 lag（週體重、月營收），或者根本動不了的外生變數（市場走向）

## 它做什麼（protocol 摘要）

Socratic 發現對話 — agent 不代筆。兩軸必須同時為真：

1. **WIG gate check** — 用一句話講 WIG（X → Y by 哪天）。模糊就退回 D1 停止
2. **腦力激盪 5-10 個候選行為** — 推使用者想反直覺的（「你的『量小孩腳尺寸』是什麼？」）
3. **兩軸評分（1-5 × 1-5）** — predictive + influenceable，各附一句 causal chain
4. **任一軸 ≤3 直接砍** — predictive ≤3 = 雜訊；influenceable ≤3 = 雨量級（管不到）
5. **挑 2-3 個，最好 1 個 frequency + 1 個 quality** — frequency 型（每週做 X 幾次）+ quality 型（每個 X 都符合標準 Y）
6. **operational definition** — 每個 lead 寫清楚什麼算 done、何時/如何 log、每週 target，要到第三者不用問就能執行
7. **書面預測 causal chain** — 一段話：「我若連續 6 週達到 lead，預期 lag 會推到 [Y]，因為……」
8. **輸出** — 2-3 個 lead + operational definition + 週 target → 交給 D3（顯示）和 D4（review）

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| WIG 還沒定義 | 先去 `4dx-d1-personal-wig-defining` — 模糊 WIG 上面的 lead 都是雜訊 |
| stroke-of-pen goal（一個決策就完成） | lead measure 不適用 |
| lag 在週單位上測不出來（藥物開發、長篇小說） | 週 lead 會變成表演，改 milestone 制 |
| 想要顯示 / scoreboard 建議 | `4dx-d3-personal-scoreboard` |
| 有 lead 但 lag 4 週以上不動 | `4dx-sustain-personal-momentum-rescue`（五個 optimizing 問題） |

## 出處

蒸餾自 *The 4 Disciplines of Execution*（2nd ed.）第 3 章 Discipline 2: Act on the Lead Measures + 第 13 章。三個 anchor case：鞋類零售（4,500 家店發現「量小孩腳」是反直覺的 lead）、Younger Brothers Construction（事故 57 → 12/年）、Towne Park valet（retrieval-time 作為 lead）。

完整 RIA++ 渲染（含 lag-masquerading-as-lead、lead-data-too-hard-so-skipped、Goodhart 對策＝frequency × quality 配對 + 4 週 causal-chain check）見 [`SKILL.md`](SKILL.md)。
