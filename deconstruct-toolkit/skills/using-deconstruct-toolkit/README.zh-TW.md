# using-deconstruct-toolkit

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 為眼前的作品挑選正確的解構 skill 與 lens combination。

router。根據使用者帶來的內容與想要被揭露的面向，挑選正確的解構
skill（`artifact-deconstruct` / `argument-deconstruct` /
`assumption-surface`）與正確的 lens combination。
當你還不知道該用哪個 sibling skill 時，使用此 skill。

## 何時使用

觸發語句（任何語言）：

- 「help me deconstruct this」/「拆解這份」/「脱構築したい」
- 「這份文案 / 頁面 / playbook 背後的設計是什麼」
- 「這個 argument 實際上在主張什麼」
- 「找出隱藏的假設」/「stress-test 這些主張」
- 「我有一份作品，但不知道該用哪個 skill」

何時跳過：

- 使用者已指定特定 sibling skill（例如 `/deconstruct-toolkit:artifact-deconstruct`）— 直接 invoke 那個 skill
- 對象是原始碼或 build artifact — 改用 `sourceatlas`
- 使用者想釐清自己的問題 — 改用 `philosophers-toolkit`
- 使用者想 **產出** 新文案 / 文件 / 設計 — 改用 `copywriting-toolkit` / `docs-team` / `design-team` / `slides-toolkit`

## 先做邊界檢查

在 routing 進入此 toolkit 之前，router 會先執行三項邊界檢查，
將被誤導向的請求重新導引：

| 問題 | 若 yes，導向 |
|---|---|
| 對象是原始碼嗎？ | `sourceatlas`（impact / flow / overview / pattern / deps） |
| 自我思考（你自己的問題，而非外部作品）嗎？ | `philosophers-toolkit` |
| 前向產出（撰寫新文案 / 文件 / 設計）嗎？ | `copywriting-toolkit` / `docs-team` / `design-team` / `slides-toolkit` |

三項皆為「no」之後，routing 才會繼續。

## 雙軸 routing

### 軸 1 — 作品類型

| 作品 | 預設 skill | 預設 lens combo |
|---|---|---|
| 行銷文案 / LP / 廣告 | `artifact-deconstruct` | persuasion + rhetoric |
| 文件包 / playbook / SOP / 新進員工流程 | `artifact-deconstruct` | genre + 6-dim full |
| UI / app 新手導引 / 網站畫面 | `artifact-deconstruct` | ux + persuasion |
| 長篇 argument / op-ed / 提案 / 政治論述 | `argument-deconstruct` | Toulmin + Burke + warrant surface |
| 策略備忘錄 / 政策 brief / SNS thread（懷疑有隱藏假設）| `assumption-surface` | reverse-Toulmin + symptomatic reading |
| 演說 / 政治演講 | `artifact-deconstruct` | rhetoric + frame |
| 文學 / 電影 / 廣告意象 | `artifact-deconstruct` | semiotic + frame |
| 簡報投影片 / presentation | `artifact-deconstruct` | rhetoric + genre |

### 軸 2 — 使用者意圖（覆蓋軸 1）

| 使用者說 | 覆蓋為 |
|---|---|
| 「deconstruct the design」/「為什麼這份寫得這麼好」 | `artifact-deconstruct`（full 6-lens × 6-dim） |
| 「find hidden assumptions」/「這在 *假設* 什麼」 | `assumption-surface`（atomic、快速） |
| 「find the warrant」/「這個 argument 是否成立」 | `argument-deconstruct`（Toulmin focus） |
| 「我在這裡被什麼操弄」/「找出黑暗模式」 | `artifact-deconstruct` 搭配 persuasion + ux |

若作品類型與使用者意圖不一致，**使用者意圖勝出**。

## dispatch 前的三道過濾

| 過濾 | 意義 |
|---|---|
| 長度過濾 | 少於 200 字且非結構化 argument → 設計量不足；告知使用者，不 dispatch |
| 純資訊過濾 | 純參考資料（Wikipedia / 辭典 / 原始資料）→ 沒有可還原的設計；告知使用者，不 dispatch |
| 多模態過濾 | 影像為主 + 你無法直接檢視影像 → 請使用者描述文字，或先以 OCR / defuddle 預先抽取 |

## 文化變體偵測（v0.2.0+）

dispatch 前，router 會判斷：

1. **主要語言** — 英語 / 日語 / 中文（繁體 vs 簡體）/ 混合 / 其他
2. **文化語境** — 學術 / 商業 / 文學 / 政治 / 消費者行銷
3. **翻譯來源** — 這是翻譯嗎？

這些 signals 會傳給接收的 skill，使其能依據
`artifact-deconstruct/protocols/lens-variant-selection.md`，
routing 到 `lens-rhetoric` / `lens-persuasion` / `lens-genre` / `lens-frame`
的正確文化變體。

依 [ADR-0004](../../docs/adr/0004-cultural-lens-variants.md)，
plugin scope 永久限定為 EN / JA / ZH。
其他語言以 **明確警示** 退回 `-anglo` fallback，
而非暗示完整覆蓋。

## 你會得到什麼（output）

一段 1-3 句的 dispatch：

> 「Dispatching to `artifact-deconstruct` with `lens-persuasion +
> lens-rhetoric` preselected，language=Japanese，
> register=consumer-marketing → variants `-ja`。Running now。」

接著 dispatch 出去的 sibling skill 開始執行。

## 規則

- 不要在此 skill 內執行解構 — 只負責 routing
- 不要解釋 lens 內容 — 交給被 dispatch 的 skill
- 只 recommend 一個 skill，不是多個
- 使用者已指定 skill 時，跳過 routing 直接 invoke
- 若沒有 skill 適合，誠實說出 — 不是每件作品都值得被解構

## 延伸參考

- [`SKILL.md`](SKILL.md) — full canon
- 姊妹 skill：[`artifact-deconstruct`](../artifact-deconstruct/) | [`argument-deconstruct`](../argument-deconstruct/) | [`assumption-surface`](../assumption-surface/)
- 文化變體 routing：[`../artifact-deconstruct/protocols/lens-variant-selection.md`](../artifact-deconstruct/protocols/lens-variant-selection.md)
- Plugin overview：[`../../README.md`](../../README.md)
