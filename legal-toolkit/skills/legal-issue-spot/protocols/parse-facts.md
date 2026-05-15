# Protocol — parse-facts

Step 1 of the `legal-issue-spot` pipeline. LLM reads the user's
free-text fact pattern and extracts structured facts (當事人 / 行為 /
時間 / 金額 / 標的) into a markdown bullet list. This protocol is the
**first runtime write** — it creates `issues.md` if it does not yet
exist and writes the `§事實摘要` section.

## Inputs

- **Free-text fact pattern** from the user (typically 1-3 短段落
  business 描述)
- **No structured schema**, no `profile.yml`, no upstream protocol
  output — this is the first step
- **Output session directory** (already created by SKILL workflow):
  `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-issue-spot/`

## Outputs

Writes the `§事實摘要` section into `issues.md` (creates the file if
it does not exist; does **not** write any later sections — those
belong to Steps 2-6).

Section format:

```markdown
## §事實摘要

- **當事人**: <party-A>（<role>）/ <party-B>（<role>）/ ...
- **行為**: <verb-noun phrase>; <verb-noun phrase>; ...
- **時間**: <ISO 8601 or 自然語; ⏳ 待釐清 if unknown>
- **金額**: <amount + 幣別; — if N/A>
- **標的**: <subject matter / 標的物>
```

Use `—` (em-dash) for a slot that is genuinely N/A (e.g. 金額 in a
non-monetary scenario), and `⏳ 待釐清` for a slot that is **likely
relevant but missing** — `timeline.md` (Step 2) follows up on the
time slot specifically.

## Procedure

1. **Pre-flight halt check** — run the halt + ask test (below). If
   any condition fires, halt and ask the user; do **not** write to
   `issues.md`.
2. **Extract 當事人** — list 自然人 / 法人 / 機關 with their role
   in the scenario (買方 / 賣方 / 員工 / 客戶 / 主管機關 / 第三人).
   Keep the user's own naming ("甲方" / "客戶 A") if given. Single-
   party scenarios (純內部 policy 問題) are valid — write
   `<party>（<role>）/ —` and continue; this is **not** a halt.
3. **Extract 行為** — verb-noun phrases (「我方贈送禮品給客戶聯絡
   人」/「員工申請育嬰假」/「客戶要求刪除個資」). Multiple separated
   by `;`. **Stay factual** — do **not** characterise ("非法地…",
   "違反…"); characterisation is Step 3 (`spot-issues.md`).
4. **Extract 時間** — explicit dates / 期間 verbatim; prefer ISO 8601
   when unambiguous (`2026-01-15`); keep relative phrasing where the
   user used it ("上週" / "下個月底"). No anchor at all → `⏳ 待釐清`.
5. **Extract 金額** — numeric value + 幣別 (NT$ / JPY / USD). 非貨幣
   情境 → `—`. 暗示但未明說 ("一份生日禮物") → `⏳ 待釐清` (many
   構成要件 trigger thresholds where 金額 changes the analysis).
6. **Extract 標的** — subject matter: 物 (生日禮物) / 服務 (顧問
   合約) / 個資 (8000 筆客戶名單) / 智財 (商標授權) / 勞務 (育嬰
   假申請). Multiple 行為 sharing one 標的 → list once; distinct
   標的 per 行為 → list each.
7. **Write to `issues.md`** — open `<session-dir>/issues.md` (create
   if not exists). If the file is new, write a top-level title
   first; then append the `§事實摘要` section per format above.
   No other sections.

```markdown
# Issue Spot — <session-id or YYYY-MM-DD HH:mm>

## §事實摘要

- **當事人**: ...
- **行為**: ...
- **時間**: ...
- **金額**: ...
- **標的**: ...
```

## Halt + ask fallback

Halt and ask the user (do **not** write to `issues.md`) if **any**:

1. **Pattern too short** — fewer than ~30 characters of substantive
   content. Ask: 「請補充事實描述：目前資訊太少，無法做 issue
   spotting。可否說明：誰、做了什麼、跟誰之間？」
2. **Internal contradiction** — pattern asserts X and not-X (e.g.
   「甲方付了錢但沒付錢」/「合約已終止但仍在履行中」). Ask: 「事實
   描述中似有矛盾：『<引述兩段>』。請確認哪一個是實際情況？」**Quote
   the contradicting fragments verbatim** — only the user can resolve.
3. **Missing both 當事人 and 行為** — no identifiable party AND no
   identifiable 行為 (pattern is purely abstract / hypothetical).
   Ask: 「請描述具體情境：涉及哪一方（或哪些方），發生了什麼事？」

For halt types 1 and 3, the re-prompt anchors on "誰 / 做了什麼 /
跟誰之間" — minimum 3-element anchor that unblocks Steps 2-3.

A halt is **not** a failure — re-run this protocol once the user
provides clarification.

## Example

**Input** (raw fact pattern):

> 我們公司想在年底前送一份生日禮物給長期合作的客戶聯絡人 A，預算
> 大約 NT$3,000。對方公司是上市櫃。我們是供應商，過去三年有持續
> 供貨。能不能做？

**Extracted facts → output bullets**:

```markdown
## §事實摘要

- **當事人**: 我方公司（供應商）/ 客戶聯絡人 A（上市櫃公司員工）/ A 所屬公司（上市櫃，客戶）
- **行為**: 我方擬贈送生日禮物給 A
- **時間**: 2026 年底前（預定）
- **金額**: 約 NT$3,000
- **標的**: 生日禮物（物）
```

Note: 行為 stays factual ("擬贈送") — does **not** say "違反公司治理
受贈規範" or similar. That characterisation, if any, is for Step 3
(`spot-issues.md`).
