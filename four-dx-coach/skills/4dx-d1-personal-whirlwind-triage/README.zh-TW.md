# 4DX D1 — Whirlwind Triage

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> D1 的前置作業 — 在寫 WIG *之前*，用 7 天 time audit 把 BAU 與 WIG 的容量現實攤開來。

## 何時觸發這個 skill

- 「每天都在救火」「日常雜事吃掉所有時間」
- 「想推進的事一直擱置」「想設目標但根本沒空執行」
- 上一次的 WIG 已經死掉，使用者在懷疑是 4DX 不行還是自己「再努力一次」就好
- 即將呼叫 `4dx-d1-personal-wig-defining`，但還沒先把 whirlwind 跟 WIG 的差別講清楚

## 它做什麼（protocol 摘要）

1. **建立 7 天 time audit log** — 醒著的時間每 30 分鐘一個 block，全部 tag 成 `WHIRLWIND` / `WIG` / `NEITHER`。完成標準：連續 7 天，醒著的 block 至少 80% 有 tag。
2. **算比例** — 各 tag 加總，寫下 WHIRLWIND% / WIG% / NEITHER% + 一句話講「我以為是怎樣，實際是怎樣」。
3. **稽核 whirlwind 裡的 theater** — 每個 WHIRLWIND block 重 tag 成 `BAU-real`（停掉現場會壞）或 `BAU-theater`（停掉只是自我形象會壞）。
4. **決定最低 WIG 配額** — 書中 anchor 是 ~20%（週 40h → 8h）。寫成 commitment：數字 N + 具體 calendar block + 一個 protector。
5. **交棒 or 中止** — 送進 `4dx-d1-personal-wig-defining`；若 step 1 已經暴露 role 本質就是 reactive，明確放棄這個目標用 4DX。

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| burnout / 長期過勞 / 憂鬱 | 諮商或臨床 — time audit 只會把覺察武器化 |
| 本質就是反應性角色（on-call SRE、ER、新生兒照護） | whirlwind 本身就是戰略價值 — `4dx-meta-personal-strategy-triage`（CE-26） |
| stroke-of-pen / 一次性事務（「這週末把稅報一報」） | 根本不需要 4DX |
| 在挑生產力工具（Notion vs Sunsama） | 那是工具比較，不是 capacity 診斷 |

## 出處

蒸餾自 *The 4 Disciplines of Execution*（2nd ed., 2021）第 1 章 The Real Problem with Execution。兩個 anchor case：Plant Manager of the Year（12 個優先級收斂到 1 個）、Towne Park Miami（在週六把 concrete wall 拆掉那次）。

完整 RIA++ 渲染（含 Parkinson's-Law devouring trap、most-important-confusion 警告等）見 [`SKILL.md`](SKILL.md)。
