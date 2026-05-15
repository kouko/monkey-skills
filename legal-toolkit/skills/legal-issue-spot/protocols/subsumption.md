# Protocol — subsumption

The **core IRAC step** for legal-issue-spot. Per Issue identified in
Step 3, looks up the element list (構成要件) from the relevant
reference file and 涵攝 (subsume) each element against the parsed
fact pattern. Output: a 4-column 涵攝 table written to `issues.md
§構成要件涵攝`. ⚠️ markings here are consequential — they drive
counterfactual reverse-checks (Step 5), risk-grade escalation
(Step 6 §6.4), and the cross-skill handoff to `/legal-research`.

## Inputs

- `issues.md §Issue 矩陣` (written by `spot-issues.md`) — list of
  Issues, each tagged with statute domain (民法 / 勞動 / 個資) and
  candidate 條文 (e.g. 民法 §184 / 個資法 §27)
- `issues.md §事實摘要` (written by `parse-facts.md`) — structured
  facts: 當事人 / 行為 / 時間 / 金額 / 標的
- One or more reference files (selected per Issue domain):
  - `references/請求權基礎-民法.md` for 民法 issues (§184 / §227 / §767 / §179)
  - `references/構成要件-勞動.md` for 勞動 issues (勞基法 §11 / §14 / §16 + 性平法 §13)
  - `references/構成要件-個資.md` for 個資 issues (個資法 §5 / §8 / §9 / §27 / §29)

## Outputs

Appends `§構成要件涵攝` section to `issues.md` containing one table
per Issue. Each table:

```markdown
### Issue 1: <Issue 名稱> — <條文號>

| 構成要件 | 事實對應 | 涵攝結論 | 信心 (理由) |
|---|---|---|---|
| 故意或過失 | A 公司未檢查欄位… | 該當 | 高 — 事實摘要已明示未檢查 |
| 不法侵害 | … | ⚠️ | 中 — 「適當安全措施」標準需 PDPC 函釋確認 |
| 因果關係 | … | 不該當 | 高 — 損害發生於 B 公司內部離職員工，非本案行為導致 |
```

Column values are constrained:

- **構成要件**: lifted verbatim from the reference file element list
- **事實對應**: 1-2 sentence summary of which 事實摘要 fact matches
  this 構成要件 (or "⏳ 待釐清" if no fact present)
- **涵攝結論**: exactly one of `該當` / `不該當` / `⚠️`
- **信心 (理由)**: confidence level (`高` / `中` / `低`) + 1-line
  reasoning

## Procedure

### Step 1: Verify inputs

Read `issues.md`. Confirm both `§Issue 矩陣` and `§事實摘要` sections
exist and are non-empty. If either is missing or empty → halt (see
Halt + ask fallback below).

### Step 2: For EACH Issue in §Issue 矩陣

#### Step 2.1: Select reference file by domain

| Issue domain tag | Reference file |
|---|---|
| 民法 | `references/請求權基礎-民法.md` |
| 勞動 (勞基法 / 性平法) | `references/構成要件-勞動.md` |
| 個資 (個資法) | `references/構成要件-個資.md` |

If an Issue spans 2 domains (e.g. one fact triggers both 民法 §184
and 個資法 §27), treat as 2 separate Issues and look up each
domain's element list independently.

#### Step 2.2: Read the relevant element list

In the chosen reference file, locate the 條文 section matching the
Issue's 條文號 (e.g. for 民法 §184, find the §184 block). Extract
the element list — typically 3-5 構成要件 with 1-line 白話 + 反例 +
carve-out.

#### Step 2.3: Per element, perform 涵攝

For each 構成要件 in the element list:

1. Scan `§事實摘要` for a fact that matches the element's 白話
   description
2. Decide 涵攝結論 per the Confidence rules below
3. Write 1-line 事實對應 (which fact) + 1-line 信心理由

#### Step 2.4: Append the table to §構成要件涵攝

Use the table format shown in §Outputs above. Header per Issue:
`### Issue N: <Issue 名稱> — <條文號>`.

### Step 3: Tally for downstream protocols

After all Issues processed, count total ⚠️ rows across all tables.
This count drives:

- `counterfactual.md` Step 1 (per ⚠️ row, run reverse check)
- `risk-grade.md` §6.4 escalation logic (≥ 2 ⚠️ → MUST recommend
  律師 escalation)
- `business.md §建議下一步` query strings (≥ 1 ⚠️ → emit
  `/legal-research` handoff query per ⚠️ row)

Do NOT inline the tally count in `issues.md` — downstream protocols
re-count from the table.

## Halt + ask fallback

If `issues.md §Issue 矩陣` is empty or missing → halt and emit:

```
⚠️ §Issue 矩陣 empty — cannot run 涵攝 without identified Issues.
請重跑 spot-issues.md 或確認 §事實摘要 是否包含可識別的法律行為。
```

If `issues.md §事實摘要` is empty or missing → halt and emit:

```
⚠️ §事實摘要 empty — cannot 涵攝 without parsed facts.
請重跑 parse-facts.md。
```

If a referenced 條文 (e.g. Issue says 民法 §999) is NOT found in
any reference file → mark that Issue's row with `⚠️ 條文超出
references/ 範圍` and ASK user whether to (a) skip this Issue or
(b) extend references first.

## Confidence rules (when to mark ⚠️ vs 該當/不該當)

The skill is **conservative-by-design** — when in doubt, mark ⚠️.
Downstream §6.4 escalation prefers false-positive 律師 referral
over false-negative.

| Situation | Mark |
|---|---|
| Clear fact in §事實摘要 directly satisfies the 構成要件 白話 | `該當` (信心: 高) |
| Clear fact in §事實摘要 directly contradicts the 構成要件 (e.g. fact says A is B's employee, but 構成要件 requires A be a third party) | `不該當` (信心: 高) |
| 構成要件 hinges on factual details NOT in §事實摘要 (e.g. 「故意或過失」 needs a 主觀 fact, but 事實摘要 only describes the 客觀 行為) | `⚠️` (信心: 中/低 — 需要更多事實) |
| 構成要件 references undefined-standard wording (「適當」/「合理」/「必要」/「相當因果關係」 etc.) and the threshold is fact-sensitive | `⚠️` (信心: 中 — 需要 research 函釋 / 判決) |
| Fact pattern straddles a known judicial split or 學說對立 (e.g. 不完全給付 vs 加害給付 carve-out) | `⚠️` (信心: 中 — 學說對立) |
| Reference file's 反例 directly matches the fact pattern | `不該當` (信心: 高 — 反例命中) |
| Reference file's carve-out directly matches the fact pattern | `⚠️` (信心: 中 — carve-out 適用待確認) |

**Rule of thumb**: only use `該當` / `不該當` when the fact maps
unambiguously onto the 白話 description AND the reference file's
反例 / carve-out columns do not introduce doubt. Otherwise `⚠️`.

## Reference file selection rules

| Issue 條文 prefix | Reference file | Notes |
|---|---|---|
| 民法 §184 / §227 / §767 / §179 | `references/請求權基礎-民法.md` | 4 大請求權基礎 |
| 勞基法 §11 / §14 / §16 | `references/構成要件-勞動.md` | 解雇 / 終止 / 預告 |
| 性平法 §13 | `references/構成要件-勞動.md` | 雇主性騷擾責任 |
| 個資法 §5 / §8 / §9 / §27 / §29 | `references/構成要件-個資.md` | 蒐集 / 告知 / 安措 / 賠償 (Path A: 委託/受託 + 即時) |

If the Issue cites a 條文 outside this scope (e.g. 公司法 / 證交法
/ 公平法) → mark `⚠️ 條文超出 references/ 範圍` and emit a
research handoff query in `business.md §建議下一步`. Do NOT
fabricate 構成要件 from training memory — the §6.3 disclaimer
relies on 構成要件 being grounded in references/.

## Worked example

**Issue 1**: A 公司外洩客戶資料，B 客戶請求 民法 §184 侵權行為 損害賠償

Reading `references/請求權基礎-民法.md` §184 element list:
1. 故意或過失
2. 不法侵害他人權利
3. 因果關係
4. 損害發生

Parsed §事實摘要 highlights:
- 當事人: A 公司 (蒐集者) / B 客戶 (個資當事人)
- 行為: A 公司未驗證 API 欄位過濾，導致 B 客戶資料被惡意爬取
- 時間: 2025-08-15 發現
- 金額: B 客戶主張 NT$10,000 慰撫金
- 標的: B 客戶之姓名+電話+購買紀錄

涵攝 table:

```markdown
### Issue 1: 民法 §184 侵權行為 損害賠償 — A 公司 vs B 客戶

<!-- [draft — for 法務 review; Phase 4.5 GC outreach validation]
     The 學說 framing below (人格權說 vs 隱私權說 for §184 「權利」)
     is controller-drafted from training knowledge. 法務 SME should
     validate the framing + alignment with current TW 學說 通說 +
     最高法院 leading 判決 trend. The element list itself comes from
     references/請求權基礎-民法.md (Task 3); review there too. -->

| 構成要件 | 事實對應 | 涵攝結論 | 信心 (理由) |
|---|---|---|---|
| 故意或過失 | A 公司未驗證 API 欄位過濾 | 該當 | 高 — 「未驗證」屬具體過失行為 |
| 不法侵害他人權利 | B 客戶之姓名+電話+購買紀錄被外洩 | ⚠️ | 中 — 「個資」是否該當 民法 §184 「權利」需依 個資法 §29 + 學說（人格權說 vs 隱私權說），有 學說對立 |
| 因果關係 | 外洩 → B 客戶受垃圾簡訊騷擾 | 不該當 | 高 — §事實摘要 未敘述 B 客戶受任何具體損害（僅請求慰撫金），相當因果關係缺漏 |
```

→ 1 ⚠️ → counterfactual.md will reverse-check 「個資是否屬 §184 權利」 → business.md will emit `/legal-research --query="個資 民法 §184 權利說 學說對立"` handoff → risk-grade.md treats as 🟡 (1 ⚠️，未達 §6.4 ≥ 2 觸發門檻).
