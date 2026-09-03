# Critique

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 在動手做之前先裁決提案，一個 skill 兩個鏡頭：
> `mode: proposal` 把清單分成 KEEP / DEFER / DROP，
> `mode: complexity` 用「先刪再加」量一個具體改動。

使用者主動呼叫的 **gate skill**。當 plan、backlog 或某個提案看起來比
問題本身還大時，在任何人動工之前先強制跑一次批判性檢查。

這份 README 給在 GitHub 上讀這個 skill 的人。Claude 實際載入的
operational 檔案是 [`SKILL.md`](SKILL.md)。

---

## 為什麼需要這個 skill？

兩種失敗模式，同一個根源：沒有機制逼每個項目掙到自己的位置。

**過於寬容的清單。** 被要求規劃時，Claude 會生出七個項目、三個選項、
一份實際上是「全部都做」只是披著優先度的 P0/P1/P2 backlog。多數項目
grounding 很弱（「業界標準」「為未來預留」），必要性也含糊（「有比較
好」）。沒有人推回去，這份膨脹的提案就變成計畫。

**加法預設。** 每個改動都被問成「要加什麼」，很少問「可以不加什麼」，
更少問「這個改動讓什麼變成多餘」。結果 codebase 往熵增走——更多檔案、
更多為未知未來準備的彈性、更多沒人要求的行數。

`mode: proposal` 抓前者，`mode: complexity` 抓後者。

---

## 怎麼運作

**先選 mode。** 清單、計畫，或帶兩個以上支持論據的散文式推薦 →
`proposal`。單一具體改動（refactor、在既有 code 上加 feature、還技術債、
指名的 greenfield feature）→ `complexity`。三個以上互相獨立的提案：先
triage，再對每個存活者分別跑 `complexity`。

### mode: proposal

每個項目給兩個值——**evidence grounding**（`GROUNDED` / `HEURISTIC-OK` /
`SPECULATIVE`）與**必要性**（`ESSENTIAL` / `SPECULATIVE`）——經 triage
matrix 對映到 `KEEP`、`KEEP-WITH-CAVEAT`、`DEFER`、`DROP`。說不出重新
觸發條件的 `DEFER` 一律落到 `DROP`，緩議區才不會變成停車場。

### mode: complexity

先從 [`references/`](references/) 讀一份 mindset 並指名，再依序問三題：

1. **Q1 — 最小的 end state。** 不是最小的改動，而是改完之後 codebase
   該長什麼樣，包含「不做」這個選項。
2. **Q2 — 總程式碼量會變少嗎。** 行數、函式、檔案的 before / after。
   可以變多，但必須指名理由並算出代價。
3. **Q3 — 可以刪掉什麼。** 隨這次改動一起發生的實際刪除，不是日後的
   承諾。

verdict 恰好一個：`PROCEED`、`PROCEED-WITH-CAVEAT`、`RESHAPE`、`REJECT`。

---

## 它不做的事

主張不等於證據；不確定要講出來，不能編造；不會為了好聽把 `DROP` 悄悄
改成 `DEFER`；也不會把該自己跑的閘丟回給使用者。

不適用：單純問答、沒有主張行動的說明條列、瑣碎改名、把已經寫好的 diff
變小、完成前的 verification。

---

## Attribution

`mode: complexity` 承襲一串 MIT 授權的上游專案（`reducing-entropy`）。
完整鏈路、各環節的貢獻與授權全文在 [`NOTICE`](NOTICE) 與
[`LICENSE`](LICENSE)。內附的四份 mindset 追隨
`domain-teams:code-team/standards/` 的 canonical 版本。
