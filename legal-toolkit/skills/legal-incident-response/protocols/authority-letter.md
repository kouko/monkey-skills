# Protocol — authority-letter

The authority-letter sub-protocol of legal-incident-response. Dispatched by the
main pipeline after `protocols/classify-path.md` confirms
`inferred_type=authority-letter`.

Pure-LLM authoring: NO template files. The LLM generates 公文格式 output
directly from session inputs (incoming letter content + profile-derived
contact block + extracted 法源 / 要求項目 / deadline). Compare to PII-breach
which renders 3 templates; here the LLM has more discretion, so the procedural
discipline matters more.

Path A discipline: every step below assumes current in-force Taiwan PDPA +
relevant 行政 / 公司 / 證券 / 公平 法 only. Express discipline by naming
the **correct** statutory citation (e.g., 「即時」 per 施行細則 §22); do not
name forbidden phrasings. The authoritative forbidden list lives in
`scripts/grade_response.py` `PATH_A_ANTIPATTERNS` (extended by future
maintainers there, not in this protocol body).

## Input contract

- working dir: a git repo with `legal-playbook/profile.yml` present
- `path_type`: `"authority-letter"` (locked by classify-path.md)
- `incoming_letter_text` OR `incoming_letter_summary` (one required)
- `incoming_authority` (主管機關 name — e.g., 金管會 / 證交所 / 個資組
  (PDPC 籌備處) / 公平會 / 法務部 等)
- `incoming_date` (ISO 8601 — when the letter was received)
- `deadline` (ISO 8601 — when reply is due; from incoming letter's 期限 clause)
- `requested_items[]` (LLM-extractable list of specific items)
- `mode` ∈ {`函覆` / `補件` / `不服救濟`}

## Pipeline (sequential, no parallelism)

### Step 1: LOAD_PROFILE

```bash
python3 legal-toolkit/skills/legal-incident-response/scripts/load_profile.py \
  legal-playbook/profile.yml
```

Expected: exit 0 with `OK: profile valid; company=<name>`.

If exit 1: surface the stderr error list to the user and halt — fix
`profile.yml` before re-running.

### Step 2: ASK_GAPS

Identify variables not satisfied by profile + classifier signals. Ask the user
in a single batched prompt with profile-derived defaults inline and ISO 8601
hints for date fields.

#### 2a. Session-supplied (the user must answer)

- `incoming_letter_text` (full pasted text) OR `incoming_letter_summary` (LLM
  summary if user prefers not to paste verbatim)
- `incoming_authority` — 主管機關 name; cross-reference
  `profile.regulatory_authorities` if user has populated it
- `incoming_date` — ISO 8601 (`YYYY-MM-DD`)
- `deadline` — ISO 8601 (`YYYY-MM-DD`); from incoming letter's 期限 / 限期 clause
- `requested_items[]` — list of specific items the authority requests;
  LLM-extractable from Step 3 EXTRACT, but ASK to confirm if extraction is unclear
- `mode` — default `函覆`; alternatives `補件` (when authority asks for
  additional materials) / `不服救濟` (when this is a defensive reply to an
  adverse finding)
- `expected_external_counsel_review` (bool) — if `true`, surface
  `external_counsel_block` from profile into legal.md

#### 2b. Profile-derived (auto-populate; no separate ask)

- `{{company_name}}` ← `profile.company.name`
- `{{company_id}}` ← `profile.company.tax_id` 或 `profile.company.id` (統一編號)
- `{{registered_address}}` ← `profile.company.registered_address` (公司登記地址)
- `{{dpo_name}}` / `{{dpo_email}}` / `{{dpo_phone}}` ← `profile.dpo.*`
- `{{external_counsel_block}}` ← `profile.external_counsel` (render only if
  `expected_external_counsel_review = true`)

#### 2c. Generated (deterministic; no ask)

- `{{document_reference_number}}` — fallback pattern
  `<COMPANY_INIT>-FY<YYYY>-LR-<NN>` (LR = letter-reply); user may override
- `{{reply_date}}` — defaults to today's calendar date in `YYYY-MM-DD`; user
  may override (e.g., when drafting in advance)

ISO 8601 reminder: date-only fields use `YYYY-MM-DD`. The reply letter body
uses calendar dates; timeline anchors in §時間軸 use ISO 8601 dates.

### Step 3: EXTRACT

LLM reads `incoming_letter_text` (if provided; else uses
`incoming_letter_summary`) and extracts a structured record:

```
incoming_extracted = {
  authority:        <主管機關 name>,
  ref_number:       <字號 verbatim, e.g., "金管證字第 1100123 號">,
  statute_basis[]:  <list of cited §s, each as {law: "...", article: "..."}>,
  requested_items[]: <list with verbatim quote 或 summary per item>,
  deadline:         <ISO 8601 date>,
  sanction_risk:    <"行政處分 imminent" / "罰鍰可能" / "信譽風險" / "無明示處罰提示">,
}
```

**Path A enforcement at EXTRACT**: every cited statute in `statute_basis[]`
**MUST** be present in `legal-toolkit/scripts/canonical/legal-sources.json`
`statute_sources`. If the incoming letter cites a statute not in canonical
(e.g., 主管機關 cites a 條例 the firm hasn't pre-vetted), halt and surface
to the user with: 「來文引用之法源 `<法源 name>` 未列於 canonical/legal-sources.json，
請確認後再續行。」 The user may either (1) add the statute to canonical and
re-run, or (2) confirm the citation is informational-only and proceed with a
note in §2 法源依據.

Cross-check the EXTRACT `deadline` against the session-supplied `deadline`
input from Step 2a. If they disagree, ask the user to reconcile before
proceeding to DRAFT.

### Step 4: DRAFT

LLM writes 函覆 body in 公文格式 (Taiwan administrative letter format,
公文結構齊備):

```
受文者：{{incoming_authority}}
發文字號：{{document_reference_number}}
主旨：本公司 [一句話 summary 函要求重點 + 本公司回應方向]
說明：
  一、來文要求：[verbatim quote 或 condensed summary of each 要求項目，逐點列舉]
  二、本公司回應：[point-by-point 對應每一個 來文要求項目]
  三、法源依據：[cite each relevant § from canonical/legal-sources.json with URL]
  四、後續行動：[next-step commitments if applicable，如：n 日內補件 / 配合調查]
附件清單：[list of attached supporting documents, or 「無」 if none]

落款：
  {{company_name}}（{{company_id}}）
  代表：{{dpo_name}}（DPO）
  電子郵件：{{dpo_email}}
  電話：{{dpo_phone}}
  公司登記地址：{{registered_address}}
  日期：{{reply_date}}
```

**Path A enforcement at DRAFT**:

- 法源 §s in 「三、法源依據」 MUST come from canonical/legal-sources.json
  `statute_sources`. If the LLM wants to cite an unverified statute, halt at
  this step + surface to user (same procedure as EXTRACT halt).
- Use 「即時」 per 施行細則 §22 when discussing PDPA notification timing in
  the reply body (only if 函詢事項 touches 個資).
- Use 「委託者／受託者」 model phrasing (個資法 §4) if the matter touches
  委託處理。
- 成年年齡 → 「未滿十八歲」 per 民法 §13（若當事人保護議題出現）。

Each cited statute in 「三、法源依據」 includes its `law.moj.gov.tw`
LawSingle URL per canonical/legal-sources.json `single_article_url_template`.

Mode-specific tone:

- `函覆` (default) — neutral, declarative; reaffirm cooperation
- `補件` — apologize for delay if applicable; itemize attachments
- `不服救濟` — formal objection language; cite 救濟管道 法源 only after
  user-confirmed external-counsel review (set `expected_external_counsel_review
  = true`); statute citations must follow the same canonical-source rule (any §
  not in canonical/legal-sources.json must be flagged to user per Step 3
  EXTRACT halt procedure)

### Step 5: ASSEMBLE_LEGAL_MD

Consolidate the EXTRACT record + DRAFT body + timeline into `legal.md`:

```markdown
# 主管機關函覆——法務記錄

## §1 incoming 函要求摘要
（factual 1-paragraph summary: authority + ref_number + 收文日 + 主要要求 +
deadline + 是否提及處罰風險）

## §時間軸

| 時間 (ISO 8601) | 事件 | 來源 |
|---|---|---|
| {{incoming_date}} | 收文 | {{incoming_authority}} |
| {{reply_date}} | 我方擬定回函日 | 內部 SOP |
| {{deadline}} | 主管機關 deadline | 主管機關來文 |
| ⏳ 待 | 主管機關處分（如有） | TBD |

## §2 法源依據
（verbatim list of statutes the authority cited + statutes we cite in reply,
each with law.moj.gov.tw LawSingle URL sourced from canonical/legal-sources.json）

## §3 函覆草稿
（full 公文 from Step 4，公文結構齊備：受文者 / 發文字號 / 主旨 / 說明 / 附件清單 / 落款）

## §4 compliance
（filled by Step 7 COMPLY_CHECK — placeholder heading during Step 5）

## §5 TBD migration tracker
（filled by Step 7 COMPLY_CHECK if any TBD canonical id applies; otherwise
this section is omitted — typically only applies when the 函詢事項 touches
PII-breach overlap, e.g., authority is PDPC 籌備處 asking about 個資 sub-reg
specifics that depend on as-yet-unpublished 施行細則）
```

**Step 5 assembly notes**:

- Leave §4 (compliance) and §5 (TBD migration tracker) as placeholder headings
  — they are filled by Step 7 (COMPLY_CHECK).
- The §時間軸 heading text must match exactly: `## §時間軸` (the grader greps
  for this byte sequence).
- Do NOT include any "NOT <forbidden phrase>" carve-out wording anywhere in
  `legal.md`. The grader's anti-pattern bank checks full file contents.

### Step 6: ASSEMBLE_BUSINESS_MD

Audience: non-法務 stakeholders (CEO / CFO / 業務窗口). Format:

```markdown
# 主管機關函覆——業務摘要

## §1 函要求 1-line
（authority + deadline + 主要要求 一句話）

## §2 Top 3 即時動作
1. 確認 函要求範圍 與 本公司資料完整度（owner + deadline）
2. 內部核稿：法務 + 業務窗口（CTO / GC / CEO 視風險，owner + deadline）
3. 寄發回函（建議 deadline 前 2-3 日完稿；owner + deadline）

## §3 deadline 警示
（color-coded by remaining days as of {{reply_date}}）：
  🔴 < 3 天 (0-2 天)：緊急；外部律師立即啟動
  🟡 3-7 天 (含)：加速；內部 fast-track
  🟢 > 7 天：標準 SOP

## §4 風險摘要
（1-3 sentences 描述 worst case：行政處分 / 罰鍰金額區間 / 信譽損害 / 後續調查擴大可能性）
```

Same anti-pattern discipline applies: plain language; no legalese; no GDPR
terminology; no SOP-specific 小時 thresholds in body.

### Step 7: COMPLY_CHECK

Read `checklists/compliance-authority-letter.md`. For each
`- [ ] <item> — **{{verdict}}**` entry, evaluate the assembled `legal.md` +
`business.md` against the requirement and emit one of:

- **PASS** — verified satisfied; cite the section / sentence in `legal.md`
  that satisfies it
- **FAIL** — item not satisfied; explicit reason
- **TBD_<canonical_id>** — depends on a canonical OPEN entry; use ONLY ids
  from `references/pdpa-current-state.md` (grader rejects fabricated ids).
  TBD applies only when there is PII-breach overlap (e.g., authority is
  PDPC 籌備處 asking about §12 sub-reg specifics).

Render the verdict-substituted checklist into `legal.md §4 compliance`.
Summarize any TBD entries into `legal.md §5 TBD migration tracker`; omit §5
entirely if no TBD entries apply.

### Step 8: SELF_GRADE

```bash
python3 legal-toolkit/skills/legal-incident-response/scripts/grade_response.py \
  legal-outputs/<timestamp>-incident-authority-letter/ authority-letter
```

Expected: exit 0 with `OK: structural grading PASS`.

The grader checks:

- Both files present (legal.md + business.md)
- Byte counts > truncation thresholds
- `## §時間軸` heading present in legal.md
- Every `TBD_*` id used in legal.md / business.md is in canonical OPEN list
- No Path A anti-patterns in legal.md or business.md
- **Authority-letter specific**: 函覆 OR 回函 string present in legal.md;
  ISO 8601 date (`YYYY-MM-DD`) present in legal.md

If exit 1: read the stderr reasons; identify which check failed; patch the
offending file; re-run COMPLY_CHECK + SELF_GRADE until PASS.

### Step 9: OUTPUT

Write to `legal-outputs/<timestamp>-incident-authority-letter/`:

- `legal.md`
- `business.md`

Print summary:

```
Authority-letter response complete:
  Legal record:  legal-outputs/<timestamp>-incident-authority-letter/legal.md
  Business memo: legal-outputs/<timestamp>-incident-authority-letter/business.md

Deadline: {{deadline}}  (buffer {{deadline - reply_date}} 天)

Verdict counts:
  PASS: <N>
  FAIL: <N>
  TBD:  <N>  (see legal.md §5 if any)

Next steps:
- DPO / 法務 寄送回函 至 {{incoming_authority}} 於 deadline 前 2-3 日完稿
- 若風險摘要 raise 行政處分 imminent → 同步通知 CEO / 外部律師
- 內部存檔 incident-authority-letter folder
```

## Failure modes

- Profile invalid → halt at Step 1
- Incoming letter cites statute not in canonical/legal-sources.json → halt at
  Step 3 (EXTRACT); ASK user to either add to canonical or confirm
  informational-only
- LLM invents §number in DRAFT → halt at Step 4; ASK user for verification
- EXTRACT deadline ≠ session-supplied deadline → halt at Step 3; ASK user to
  reconcile
- Path A anti-pattern leaks into legal.md / business.md → caught by
  grade_response.py; rephrase using correct statutory citation
- ISO 8601 date missing from legal.md → caught by grade_response.py
- 函覆 / 回函 string missing → caught by grade_response.py (typically means
  the DRAFT was framed as something other than a reply letter)

## Notes for implementers

- Pure-LLM authoring — no template files; LLM generates from session inputs +
  EXTRACT record + profile.
- 法源 §s MUST be in `legal-toolkit/scripts/canonical/legal-sources.json`
  `statute_sources` (currently: 民法 / 民事訴訟法 / 公司法 / 證券交易法 /
  公平交易法 / 個人資料保護法 / 營業秘密法 / 著作權法 / 勞動基準法 /
  消費者保護法 / 涉外民事法律適用法 / 仲裁法). Never invent.
- 公文結構齊備（header + body + sign-off）：受文者 / 發文字號 / 主旨 / 說明（含一/二/三/四項細分）
  / 附件清單 / 落款。
- Anti-pattern discipline lives in `scripts/grade_response.py`
  `PATH_A_ANTIPATTERNS` (full bank); do NOT inline forbidden phrasings into
  this protocol or the checklist, even in "NOT X" form.
- TBD canonical ids: applicable only when there is PII-breach overlap (e.g.,
  authority is PDPC 籌備處 asking about §12 sub-reg specifics). For non-PII
  authority letters (e.g., 證交所 重訊查詢 / 金管會 監理函詢) TBD section
  typically does not apply.
- The `mode` ∈ {函覆 / 補件 / 不服救濟} affects tone in DRAFT step but not
  the structural skeleton (公文結構齊備 always required).
