# 4dx-audit（consultant-mode 入口）

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 4DX plugin 的 consultant-mode 入口 skill — 把使用者已有的資料整合成結構化的 4DX audit ＋ 排序好的下一步 roadmap。

## 這個 skill 做什麼

本 plugin 另外 11 個 skill 都是 **coach-mode**：Socratic 對話、一步一步、從零開始。這個 skill 是 **consultant-mode**：使用者丟出策略 doc / OKR / KPI dashboard / scoreboard / 會議記錄，skill 全部讀過、用 4DX 五層框架診斷、給出 3-5 個排序好的下一步建議，每個都 route 到對應的 coach-mode D-skill 做深入處理。

五個步驟：

1. **Inventory** — 列出所有提供的資料
2. **Map** — 把內容對應到五層（L1 WIG / L2 Lead measure / L3 Scoreboard / L4 Cadence / L5 Substrate）
3. **Diagnose** — 每層標記 `well-formed` / `malformed` / `absent` / `wrong-shape`，引用書裡的 standard
4. **找 gap 與風險** — 順序、Goodhart、參與崩潰、產能崩潰、框架混淆
5. **Prescribe** — 3-5 個優先行動，每個 route 到具體的 coach skill

## 何時啟動

- **EN** — "Here's our strategy doc — help me 4DX it", "Audit our 4DX given this context"
- **JP** —「策略 doc を 4DX 視点で診断して」「資料を渡すから 4DX 視点で見て」
- **zh-TW** —「這是我們的策略 doc，幫看 4DX 怎麼套」「OKR 翻成 4DX」「資料都在這，幫我用 4DX 框架釐清」「我們導入 4DX 但卡住，幫我診斷」

啟動的判別訊號：**資料豐富的 query ＋ 明確的 4DX 框架 ask**。完全沒有 artifact 的冷啟動 query 走 `using-four-dx-coach`。

## 何時不要用

| 情境 | 改去哪 |
|---|---|
| 冷啟動、沒有 artifact | `using-four-dx-coach`（router 做 scope 分流）|
| 單一 discipline ＋ 該 discipline 的完整 context | 直接 fire 對應的 D-skill（例：`4dx-d1-wig-formulation`）|
| 使用者要 Socratic 一步步被 coach | coach-mode D-skill，不是 audit |
| 非 4DX 框架的 audit（OKR / BSC / agile retro）| 不在範圍 — `using-four-dx-coach` handoff |
| 已經在某個 coach skill 流程中 | 不要中斷去做 audit |
| 純發洩、無 4DX 框架意圖 | router 或其他支援 |

## 輸出格式（簡版）

```markdown
# 4DX Audit — [context 標籤 / 日期]

## Inventory
- [讀過的 artifact]

## Layer status
| 層 | Status | Finding |
|---|---|---|
| L1 WIG | malformed | [理由 ＋ 引用 standard] |
| ... |

## Gaps ＋ risks
- [跨層問題]

## Recommendations（已排序）
1. **[行動]** — [理由] → run `[skill-slug]`
2. ...

## 建議下一步
[先跑哪個 skill ＋ 為什麼]
```

## Source citation

The 4 Disciplines of Execution（2nd ed., 2021）— McChesney / Covey / Huling / Thele / Walker。跨章引用（Foreword ＋ Ch 1 framing ＋ Ch 6 selection ＋ Ch 10 sustaining）。

Consultant-craft 參考見 [`references/industry-grounding.md`](references/industry-grounding.md)：Block（*Flawless Consulting* 3rd ed. 2011）、Schein（*Process Consultation* 1969 ／ *Helping* 2009）、Maister-Green-Galford（*The Trusted Advisor* 2000）、Adler ＆ Van Doren（*How to Read a Book* rev. 1972）。

## 相關

- [`SKILL.md`](SKILL.md) — 完整 audit protocol（5 步驟 ＋ 每層的診斷 standard）
- Plugin router [`using-four-dx-coach`](../using-four-dx-coach/) — 冷啟動 ／ 非 4DX query 走這
- 11 個 coach-mode D-skill — audit 會 route 過去做深入工作
