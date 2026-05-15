# Protocol — spot-issues

Step 3 of the `legal-issue-spot` pipeline. LLM reads `§事實摘要` from
`issues.md` (written by `parse-facts.md`) and identifies candidate
構成要件 **seeds** across 3 statute domains — 民法 / 勞動 / 個資 —
emitting an Issue 矩陣 table to `issues.md §Issue 矩陣`.

This protocol identifies **which Issues exist** (the seeds). It does
NOT do the per-element 構成要件 涵攝 — that is `subsumption.md`'s job.
Each Issue row only carries: Issue label / 涉及法條 / 對應事實 / 備註.

## Inputs

- **Required**: `issues.md §事實摘要` (must exist and non-empty),
  written by `protocols/parse-facts.md` Step 1
- **No external fetch**; pure-LLM mapping from facts to candidate 法條

## Outputs

Append to `issues.md`:

```markdown
## §Issue 矩陣

| Issue | 涉及法條 | 對應事實 | 備註 |
|---|---|---|---|
| <issue-1> | <statute §X> | <fact ref> | <optional note> |
| ... | ... | ... | ... |
```

- **Multi-issue is normal** — one fact pattern often spans 民法 + 勞動 + 個資
- One Issue row **per (issue × 涉及法條)** combination — if Issue A triggers
  both 民法 §184 + 個資法 §29, emit 2 rows (one per statute)
- 法條 format: `民法 §184` (NOT `民法 184條`) per repo style
- `對應事實` references the fact summary (e.g. "事實 ②" or short quote);
  keep < 60 字
- `備註` optional; reserved for cross-jurisdiction flags + downstream
  signals (see Procedure Step 4)

## Procedure

### Step 1 — Verify input

Read `issues.md §事實摘要`. If the section is missing OR empty
(only headers / whitespace) → **halt + ask** (see fallback below).

### Step 2 — Per fact, scan 3 statute domains

For each fact in `§事實摘要` (each 當事人 / 行為 / 標的 / 金額 /
時間 entry), ask: which 構成要件 *seed* might this trigger?

**民法 (請求權基礎)** — most common seeds:

| 線索 (in fact) | Candidate 法條 |
|---|---|
| 損害 / 故意過失 / 加害行為 / 第三人受害 | 民法 §184 (侵權行為) |
| 契約已存在 / 給付有瑕疵 / 給付遲延 / 拒絕受領 | 民法 §227 (不完全給付) |
| 占有他人物 / 妨害所有權 / 拒不返還 | 民法 §767 (物上請求權) |
| 無法律上原因取得利益 / 給付目的不達 | 民法 §179 (不當得利) |

**勞動 (勞基 + 性平)** — most common seeds:

| 線索 (in fact) | Candidate 法條 |
|---|---|
| 雇主終止 / 解雇 / 資遣 | 勞基法 §11 (合法解雇事由) |
| 勞工終止 / 不續約 / 因雇主違法而離職 | 勞基法 §14 (勞工終止事由) |
| 終止前未通知 / 預告期間爭議 | 勞基法 §16 (預告期間) |
| 性騷擾 / 工作場所敵意環境 / 雇主未防治 | 性平法 §13 (性騷擾雇主責任) |

**個資 (個資法)** — most common seeds:

| 線索 (in fact) | Candidate 法條 |
|---|---|
| 蒐集個資 / 目的外利用 / 過度蒐集 | 個資法 §5 (蒐集原則) |
| 未告知當事人 / 蒐集時遺漏告知事項 | 個資法 §8-§9 (告知義務) |
| 外洩 / 未採加密 / 未備份 / 缺乏存取控制 | 個資法 §27 (適當安全措施) |
| 當事人受損害 / 求償 | 個資法 §29 (損害賠償) |

A single fact may trigger 0, 1, or multiple seeds. Err toward **over-inclusion**
at this stage — `subsumption.md` will filter out 不該當 elements downstream.

### Step 3 — Emit Issue 矩陣 table

Compose one row per (Issue × 涉及法條). Issue label is short (≤ 20 字),
business-readable (e.g. "客戶資料外洩責任", "解雇程序合法性",
"贈品收受是否構成違約").

If multiple statutes target the same Issue, emit one row per statute (do
NOT collapse "民法 §184 + 個資法 §29" into a single cell — downstream
`subsumption.md` looks up element lists per 法條).

### Step 4 — Cross-jurisdiction flag (optional 備註)

If the fact pattern explicitly mentions a non-TW counterparty or
non-TW data subject (US / EU / CN / JP / KR / HK), flag in 備註:
`跨境議題：建議另諮詢` — but **do NOT remove the row from the matrix**.
Path A discipline: this skill analyzes TW law; cross-border lives
elsewhere.

### Step 5 — Self-check

Before writing, verify:
- [ ] At least 1 Issue row emitted (if 0, fallback to halt + ask — facts
      may be too thin to spot anything)
- [ ] No 法條 typo (`§184` not `184條`; `勞基法` not `勞動基準法`)
- [ ] No row does its own 涵攝 (備註 column carries flags + cross-refs,
      NOT 該當/不該當 verdicts — that is `subsumption.md`)
- [ ] If only 1 statute domain triggered, double-check by re-scanning
      facts against the other 2 domains (multi-issue is the norm,
      single-issue is the exception)

## Halt + ask fallback

Trigger conditions:

1. `§事實摘要` section missing from `issues.md`
2. `§事實摘要` is empty (no fact entries)
3. `§事實摘要` contains only `⏳ 待釐清` markers (no extracted facts)
4. After Step 2 scan, 0 candidate seeds match (facts may be out-of-scope
   for 民法 / 勞動 / 個資)

Halt action — emit to user:

```
⚠️ spot-issues 無法執行：

原因：{1-line explanation, e.g. "§事實摘要 為空 / 僅含待釐清項目"}

請先重跑 protocols/parse-facts.md 補齊事實，或直接補充事實細節後重試。

範例最低資訊：
- 當事人 (誰對誰?)
- 行為 (做了什麼?)
- 時間 (大致時點，年月日 OK)
- 標的 (對象是物 / 資料 / 金錢 / 服務?)
```

Do NOT proceed to write a partial / empty Issue 矩陣.

## Worked example

**Input** — `issues.md §事實摘要`:

> ① 公司於 2026-04-15 將 8000 筆客戶 email 提供給外部行銷顧問 X 進行 EDM 推播
>   - 蒐集當下未告知客戶 email 將被外部使用
>   - 顧問 X 為日本法人（跨境傳輸）
> ② 顧問 X 於 2026-05-10 將該 email 名單外洩至公開論壇
>   - 已有 12 位客戶來信投訴並要求賠償
> ③ 公司未與顧問 X 簽訂 個資 委託處理書面契約

**Output** — `issues.md §Issue 矩陣`:

```markdown
## §Issue 矩陣

| Issue | 涉及法條 | 對應事實 | 備註 |
|---|---|---|---|
| 客戶資料外洩責任 | 個資法 §27 | 事實 ②（顧問 X 外洩） | 跨境議題：建議另諮詢（顧問 X 為日本法人） |
| 客戶資料外洩責任 | 個資法 §29 | 事實 ②（12 位客戶來信求償） | — |
| 蒐集目的外利用 | 個資法 §5 | 事實 ①（未告知 email 外部使用） | — |
| 告知義務缺失 | 個資法 §8 | 事實 ①（蒐集當下未告知） | — |
| 委託處理契約缺失 | 個資法 §27 | 事實 ③（未簽委託書面） | 與「客戶資料外洩責任」共用 §27，不同事實 |
| 損害賠償請求 | 民法 §184 | 事實 ②（外洩→ 12 位客戶受損） | 與個資法 §29 競合，待 subsumption 釐清 |
```

Notes on this example:
- 6 rows across **2 statute domains** (個資 + 民法) — 勞動 not triggered
- 個資法 §27 appears twice (different 對應事實 → different Issue
  framing); downstream `subsumption.md` 涵攝 each row independently
- 跨境議題 flagged in 備註 but row retained
- `備註` carries a **競合** signal for downstream `subsumption.md` /
  `counterfactual.md` to consult — does NOT pre-judge 該當/不該當

## Downstream consumers

This protocol's `§Issue 矩陣` is consumed by:

- **`protocols/subsumption.md`** — per Issue row, looks up element
  list from `references/<file>.md` and emits 該當/不該當/⚠️ verdict
- **`protocols/counterfactual.md`** — per Issue, sweeps reverse
  scenario (carve-out / default rule / 反例)

If you find yourself writing 該當/不該當 here, stop — that is the
downstream job. Stay at the **seed identification** layer.
