# Protocol — counterfactual

Step 5 of `legal-issue-spot`. Reads `issues.md §構成要件涵攝` (written
by `subsumption.md`) and runs **reverse checks** — carve-out / default
rule / 典型反例 — against every `該當` and `⚠️` row, to surface hidden
assumptions that could flip the conclusion. Without this sweep,
LLM 涵攝 systematically over-claims `該當` (a known failure mode);
this protocol is the structured devil's-advocate pass.

## Inputs

- `issues.md §構成要件涵攝` table (must already exist; columns:
  `構成要件 / 事實對應 / 涵攝結論 / 信心`)
- For each row's 構成要件, the matching reference file in
  `references/<file>.md` — read the row's `典型反例` + `典型 carve-out`
  columns:
  - 民法 元素 → `references/請求權基礎-民法.md`
  - 勞動 元素 → `references/構成要件-勞動.md`
  - 個資 元素 → `references/構成要件-個資.md`
- `issues.md §事實摘要` + `§時間軸` (for context when judging whether
  a 反例 / carve-out applies to the actual facts)

## Outputs

- New `§反事實` section in `issues.md`: per-Issue bullet list, one
  bullet per `該當`/`⚠️` row reverse-checked (3-check result + re-grade
  decision in 1-3 lines each).
- In-place updates to `§構成要件涵攝` rows that get re-graded
  (`涵攝結論` and/or `信心` columns).
- Closing `重新評級 (re-grade) 紀錄` sub-table inside `§反事實`
  whenever ≥ 1 row changed — required audit log; missing log = grader
  FAIL.

## Procedure

For each row in `§構成要件涵攝` where `涵攝結論 ∈ {該當, ⚠️}`:

1. **Look up reference** — find the 構成要件 entry in the matching
   `references/<file>.md`; read `典型反例` + `典型 carve-out` columns.
2. **Carve-out check** — does any listed `典型 carve-out` (e.g. 民法
   §148 正當防衛/緊急避難 / 個資法 §8 第 4 項委託處理人責任限縮 /
   勞基法 §11 之 2 預告義務) have factual hooks in `§事實摘要`?
   是 / 部分 / 否 → flag accordingly.
3. **Default rule check** — who carries 舉證責任 by default (主張
   權利者 / 被告 / 雇主)? If the default flips the side the LLM
   assumed, that's a hidden assumption → flag.
4. **典型反例 check** — does the listed `典型反例` squarely match the
   facts? (e.g. "個資外洩 但 委託人有過失時委託處理人不負責" 完全
   match 個資法 §8 第 4 項) → squarely 適用 → flag for downgrade.
5. **Apply re-grade rules** (§Re-grade rules) to decide if
   `信心`/`涵攝結論` updates.
6. **Write bullet** in `§反事實` (3-check summary + re-grade
   decision); keep each Issue's section ≤ ~10 lines.

Rows with `涵攝結論 = 不該當` → **skip** (one-way ratchet).

## Halt + ask fallback

- `§構成要件涵攝` empty or missing → halt; emit:
  > 反事實檢查需要 `§構成要件涵攝` 表格做輸入。請先 re-run
  > `subsumption.md`，或確認 `§Issue 矩陣` 是否有可涵攝的元素。
- All rows `不該當` → no-op; write `§反事實` section header with
  body `> 所有 構成要件 涵攝結論為 不該當，無需反事實檢查。` so
  downstream `risk-grade.md` still finds the section.
- Reference file missing or 元素 not found in reference → halt; emit:
  > 反事實檢查需參考 `references/<file>.md` 的 `典型反例` /
  > `典型 carve-out` 欄位。<元素名> 在 reference 中找不到，請先
  > 補完 reference 或調整 `§Issue 矩陣` 中的元素命名。

## Re-grade rules

| 原結論 | 觸發條件 | 新結論 | 必須附理由 |
|---|---|---|---|
| 該當 | 典型 carve-out 部分支持（部分 fit）| ⚠️ | 是 |
| ⚠️ | 典型反例 squarely 適用 | 不該當 | 是 |
| ⚠️ | carve-out + 默認規則任一強支持 | 不該當 | 是 |
| 不該當 | 任何情況 | **不變**（一向 ratchet） | — |
| 該當 | 典型反例 squarely 適用 | ⚠️（先降一級，避免一步跳兩級）| 是 |

**One-way ratchet rationale**：`不該當` 已是最保守結論；反事實
sweep 旨在抓 over-claim，不該被用來升級保守結論為激進結論。
若反事實 sweep 顯示 `不該當` 應該變 `該當`，這是 `subsumption.md`
的 bug，不是 counterfactual 的職責 — halt 並回報。

**Audit log**：每次 re-grade 都必須在 `§反事實` 結尾的「重新評級
紀錄」表格中留下一行；未留紀錄的 re-grade 視為 grader FAIL（避免
靜默改動 `§構成要件涵攝` 而上游 `subsumption.md` 重跑時 churn）。

## Worked example

Input `§構成要件涵攝`（節錄）：

| 構成要件 | 事實對應 | 涵攝結論 | 信心 |
|---|---|---|---|
| 民法 §184 故意過失 | 員工 A 加班時誤刪客戶資料 | 該當 | 中 |
| 民法 §184 不法侵害 | 客戶資料遭刪無法回復 | 該當 | 高 |

`references/請求權基礎-民法.md` §184「故意過失」: 典型反例 = 純意外 /
不可抗力；典型 carve-out = 民法 §148 緊急避難。

輸出 `§反事實`：

```markdown
### Issue 1 — 員工誤刪客戶資料 反事實檢查

- 民法 §184 故意過失：該當 → 典型反例「純意外」
  事實 fit？部分（加班疲勞下誤刪，介於「過失」與「純意外」邊界；若 UI
  設計不良誘發誤操作則可能落入純意外）。結論：升級 ⚠️。
- 民法 §184 不法侵害：該當 → carve-out「§148 緊急避難」
  事實 fit？否（無第三方信賴外觀；資料刪除是直接損害）。結論：不變。

### 重新評級 (re-grade) 紀錄

| 構成要件 | 原結論 | 新結論 | 理由 |
|---|---|---|---|
| 民法 §184 故意過失 | 該當 | ⚠️ | 過失 vs 純意外 邊界事實未釐清 |
```

`§構成要件涵攝` 同步更新該 row：`涵攝結論 = ⚠️`、`信心 = 低`，供
下游 `risk-grade.md` §6.4 escalation ⚠️ 計數使用。
