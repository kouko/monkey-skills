# Protocol — pii-breach

The PII-breach sub-protocol of legal-incident-response. Dispatched by the main
pipeline after `protocols/classify-path.md` confirms `inferred_type=pii-breach`.

Path A discipline: every step below assumes current in-force Taiwan PDPA only.
Express discipline by stating the correct statutory phrasing (e.g., 「即時」 per
施行細則 §22) — do NOT name forbidden phrasings. The authoritative forbidden
list lives in `scripts/grade_response.py` `PATH_A_ANTIPATTERNS`; future
maintainers extend that list, not this protocol body.

## Input contract

- `description` (str): user's free-text incident description
- working dir: a git repo with `legal-playbook/profile.yml` present
- `path_type`: `"pii-breach"` (locked by classify-path.md)

## Pipeline (sequential, no parallelism)

### Step 1: LOAD_PROFILE

```bash
python3 legal-toolkit/skills/legal-incident-response/scripts/load_profile.py \
  legal-playbook/profile.yml
```

Expected: exit 0 with `OK: profile valid; company=<name>`.

If exit 1: surface the stderr error list to the user and halt — fix `profile.yml`
before re-running.

### Step 2: SELECT_TEMPLATES

Read all 3 PII-breach skeletons:

- `assets/template-pii-breach-pdpc-notification.md` (PDPC 通報函)
- `assets/template-pii-breach-data-subject.md` (對當事人通知函)
- `assets/template-pii-breach-incident-record.md` (內部事件記錄)

### Step 3: SCAN_PROFILE

Extract from `profile.yml` (binding for template variables):

| Profile field | Template variable(s) | Notes |
|---|---|---|
| `company_name` | `{{company_name}}` | top-level |
| `dpo.name` / `.email` / `.phone` | `{{dpo_name}}` / `{{dpo_email}}` / `{{dpo_phone}}` | DPO contact for PDPC 通報 |
| `external_counsel` (optional) | `{{external_counsel_block}}` | render block if present, else empty paragraph |
| `cross_border_destinations[]` (optional) | seed for `{{cross_border_assessment}}` + `{{cross_border_detail}}` | LLM derives final 評估 text |
| `regulatory_authorities` (optional) | informational | help LLM decide secondary 通報對象 |

### Step 4: ASK_GAPS

Identify variables NOT satisfied by profile + classifier signals. Ask the user
in a single batched prompt. Provide profile-derived defaults inline, sensible
examples per variable, and ISO 8601 hints for date/datetime fields.

The canonical ASK_GAPS surface is the **union of `{{...}}` tokens across the 3
templates** (currently 65 distinct variables, including the literal `{{name}}`
header-marker token that the LLM does not collect). Organize the ask into 4
groups:

#### 4a. Profile-derived (no user input needed unless profile incomplete)

- `{{company_name}}`
- `{{dpo_name}}` / `{{dpo_email}}` / `{{dpo_phone}}`
- `{{external_counsel_block}}`

#### 4b. Session-supplied (the user must answer)

**Incident timing (ISO 8601 — `YYYY-MM-DDTHH:MM±TZ`)**:
- `{{incident_datetime}}` — 事故實際發生時間
- `{{discovery_datetime}}` — 公司發現時間
- `{{notification_datetime}}` — 本次 PDPC 通報送達時點
- `{{notification_date}}` — derive from `notification_datetime.split("T")[0]`
- `{{incident_date}}` — calendar date used in data-subject notice; derive from `incident_datetime`
- `{{event_discovery_iso}}` / `{{event_initial_response_iso}}` / `{{event_containment_iso}}` — timeline anchors for incident record
- `{{event_pdpc_notify_iso}}` — same instant as `notification_datetime`
- `{{record_created_at}}` / `{{record_last_updated}}` — record-keeping timestamps (ISO 8601)
- `{{version_date}}` — same calendar date as `record_created_at`

**Scope**:
- `{{affected_count}}` — 影響筆數估算（整數；若仍在調查請填「初步估計 ~N」）
- `{{data_categories_bullets}}` — 影響個資類別 bullet list
- `{{data_categories_affected}}` — same set, prose form for 當事人通知

**Severity + classification flags**:
- `{{severity_level}}` — `LOW` / `MEDIUM` / `HIGH` / `CRITICAL`
- `{{special_category_assessment}}` — `是` / `否`（涉及個資法 §6 特種個資）; if 是, also `{{special_category_detail}}`
- `{{cross_border_assessment}}` — `是` / `否`（涉及個資法 §21 跨境傳輸）; if 是, also `{{cross_border_detail}}`
- `{{minor_involvement}}` — `是` / `否`（涉及未滿十八歲當事人，民法 §12 修正 2023-01-01）
- `{{processor_involvement}}` — `是` / `否`（涉及個資法 §4 委託處理場景）; if 是, also `{{processor_detail}}`

**Response actions**:
- `{{containment_actions_bullets}}` — bullet list, PDPC 通報文用
- `{{containment_actions_consumer_facing}}` — plain-language version for 當事人通知
- `{{technical_actions_bullets}}` — 技術措施 (incident record)
- `{{administrative_actions_bullets}}` — 行政措施 (incident record)
- `{{evidence_preservation_bullets}}` — 證據保全 (incident record)
- `{{follow_up_actions_bullets}}` — 後續追蹤 (incident record)
- `{{event_discovery_desc}}` / `{{event_initial_response_desc}}` / `{{event_containment_desc}}` — timeline event descriptions
- `{{event_discovery_source}}` / `{{event_initial_response_source}}` / `{{event_containment_source}}` — evidence source for each timeline entry

**Communication**:
- `{{customer_service_contact}}` / `{{customer_service_hours}}` / `{{customer_account_url}}` — for 當事人通知 footer

**Responsibilities (incident record §責任分工 table)**:
- `{{incident_commander}}` — 事件指揮官 (typically CEO 或指定代理人)
- `{{ceo_name}}` / `{{ceo_contact}}`
- `{{cto_name}}` / `{{cto_contact}}`
- `{{security_lead_name}}` / `{{security_lead_contact}}`
- `{{legal_lead_name}}` / `{{legal_lead_contact}}`
- `{{cs_lead_name}}` / `{{cs_lead_contact}}`

**Versioning**:
- `{{version}}` — record version string, e.g., `1.0`
- `{{version_author}}` — 撰寫人姓名
- `{{version_changes}}` — 本版本變更摘要（首版填「初次建立」）

#### 4c. LLM-derived (computed from session inputs; no separate ask)

- `{{incident_summary}}` — 1-2 段 PDPC 通報用事件摘要
- `{{incident_plain_summary}}` — 1-2 段當事人通知用白話摘要（no 法條 jargon）
- `{{recommended_user_actions}}` — 給當事人的具體保護動作（更改密碼／監控帳單／等等）
- `{{data_subject_notification_plan}}` — 對當事人通知計畫（管道／時程／涵蓋率）
- `{{tbd_data_subject_notify_label}}` — default `TBD_PDPC_threshold` (通報範圍授權子法 §12 §2 most common case); override per session to `TBD_PDPC_timeframe` (時限授權子法 §12 §4) or `TBD_PDPC_pending` (PDPC 籌備處掛牌前) when those are the actual uncertainty axis
- `{{tbd_root_cause_label}}` — `TBD_PDPC_*` label OR `已確認` when root-cause analysis is complete

#### 4d. Generated (deterministic; no ask)

- `{{document_reference_number}}` — fallback pattern `<company-slug>-IR-<YYYY>-<seq>` if user doesn't supply
- `{{incident_id}}` — fallback `INC-<YYYYMMDD>-<short-hash>` if user doesn't supply

ISO 8601 reminder: full timezone-aware form `YYYY-MM-DDTHH:MM±HH:MM` (e.g.,
`2026-05-13T09:30+08:00`). Date-only fields use `YYYY-MM-DD`. The `{{name}}`
token inside the templates is a literal header marker — not collected.

### Step 5: MERGE

Resolve final values. Precedence: session input > profile field > template-implied default.

Path A safe defaults (apply automatically; do not ask):

- 通報時程基準 → 「即時」 per 施行細則 §22 (incident_datetime → notification_datetime
  delta is reported as-is; no specific 小時 SOP threshold appears in the body)
- 委託處理用語 → 「委託者／受託者」 per 個資法 §4
- 成年年齡 → 民法 §12 修正 2023-01-01 起為十八歲；未成年人 → 「未滿十八歲」 per 民法 §13
- 內部 SOP 具體小時數（若公司有自訂） → 不寫入 legal.md / business.md body；只在 §6
  Compliance Checklist 的 TBD migration tracker 註記，待 PDPC §12 §4 授權子法公布
  再 migrate

LLM fills each template skeleton with merged values. Optional sections without data:

- `{{external_counsel_block}}` empty → render `（本事件未委任外部法務）` rather than empty paragraph
- `{{cross_border_assessment}} = 否` → still render the question + 評估 paragraph (audit trail)
- `{{processor_involvement}} = 否` → render `本事件不涉及個資法 §4 委託處理場景` + leave detail empty
- `{{special_category_assessment}} = 否` → render `本事件未涉及個資法 §6 特種個資` + leave detail empty

### Step 6: ASSEMBLE_LEGAL_MD

Consolidate the 3 rendered templates + timeline into a single `legal.md`:

```markdown
# 個資外洩事件法務記錄

## §1 事件摘要
（from incident-record §基本資訊 + §事件分類）

## §時間軸
（from incident-record §時間軸 — ISO 8601 anchors; use `⏳ 待 X` marker for not-yet-realized anchors）

## §2 影響範圍
（from incident-record §影響範圍 — 筆數 / 類別 / 特種個資判斷 / 跨境判斷）

## §3 採取措施
（from incident-record §採取措施 — 技術措施 / 行政措施 / 證據保全 / 後續追蹤）

## §4 PDPC 通報文
（full rendered template-pii-breach-pdpc-notification.md）

## §5 當事人通知文
（full rendered template-pii-breach-data-subject.md）

## §6 Compliance Checklist
（from COMPLY_CHECK Step 8）

## §7 TBD migration tracker
（from compliance checklist TBD entries this session）
```

**Note**: Leave §6 (Compliance Checklist) and §7 (TBD migration tracker) as
placeholder headings during Step 6. They are filled by Step 8 (COMPLY_CHECK)
and Step 8's TBD summarization sub-step. Step 6 produces the legal.md
skeleton; Step 8 fills the verdict + migration content.

The §時間軸 heading text must match exactly: `## §時間軸` (the grader greps
for this byte sequence).

**Critical**: do NOT include any "NOT <forbidden phrase>" carve-out wording in
any section of `legal.md`. The grader's anti-pattern bank checks the full file
contents, not just the body. Express discipline by stating the correct rule
directly: e.g., 「本通報依施行細則 §22「即時」通報原則辦理。」 — not by
naming what we are not doing.

### Step 7: ASSEMBLE_BUSINESS_MD

Audience: non-法務 stakeholders (CEO / CFO / BD / 客服主管). Format:

```markdown
# 個資外洩事件——業務摘要

## §1 事件一句話
（誰／何時／何事件／影響範圍粗估）

## §2 Top 3 即時動作
1. <action 1 — owner — deadline>
2. <action 2 — owner — deadline>
3. <action 3 — owner — deadline>

## §3 對外溝通要點
- 客服話術（一句）
- 媒體 statement（一段，若需要）
- 客戶通知時程

## §4 預估時程
- PDPC 通報：已 / 待送（時點）
- 當事人通知：N 日內
- 內部複盤：N 日內
```

Same anti-pattern discipline applies: plain language; no legalese; no GDPR
terminology; no SOP-specific 小時 thresholds in body (cross-reference §6
compliance section in `legal.md` for those).

### Step 8: COMPLY_CHECK

Read `checklists/compliance-pii-breach.md`. For each `- [ ] <item> — **{{verdict}}**`
entry, evaluate the assembled `legal.md` + `business.md` against the requirement
and emit one of:

- **PASS** — verified satisfied; cite the section / sentence in `legal.md` that
  satisfies it
- **FAIL** — item not satisfied; explicit reason
- **TBD_<canonical_id>** — depends on a canonical OPEN entry; use ONLY ids from
  `references/pdpa-current-state.md` (grader rejects fabricated ids)

Render the verdict-substituted checklist into `legal.md §6 Compliance Checklist`.
Summarize each TBD entry's migration trigger into `legal.md §7 TBD migration tracker`.

### Step 9: SELF_GRADE

```bash
python3 legal-toolkit/skills/legal-incident-response/scripts/grade_response.py \
  legal-outputs/<timestamp>-incident-pii-breach/ pii-breach
```

Expected: exit 0 with `OK: structural grading PASS`.

If exit 1: read the stderr reasons, identify which check failed (anti-pattern /
TBD orphan / missing section / byte truncation), patch the offending file, and
re-run COMPLY_CHECK + SELF_GRADE until PASS.

### Step 10: OUTPUT

Write to `legal-outputs/<timestamp>-incident-pii-breach/`:

- `legal.md`
- `business.md`

Print summary:

```
PII-breach response complete:
  Legal record:  legal-outputs/<timestamp>-incident-pii-breach/legal.md
  Business memo: legal-outputs/<timestamp>-incident-pii-breach/business.md

Verdict counts:
  PASS: <N>
  FAIL: <N>
  TBD:  <N> (see legal.md §7 TBD migration tracker)

Next steps:
- Send PDPC 通報函 (legal.md §4) to 個人資料保護委員會籌備處 — DPO 寄送
- Notify affected data subjects via the channels in §5
- Run internal retrospective; monitor references/tbd-migration-template.md
  triggers for any TBD entries that bind sub-regulations
```

## Failure modes

- Profile invalid → halt at Step 1
- Template orphan (unsubstituted `{{...}}`) → caught by grade_response.py byte-count + section keyword checks; patch and re-grade
- Path A anti-pattern in body → caught by grade_response.py; remove/reword
- Fabricated TBD id → caught by grade_response.py; remap to a canonical id from `references/pdpa-current-state.md`
- User abandons mid-session → partial files in `legal-outputs/<timestamp>-incident-pii-breach/` are safe to delete

## Notes for implementers

- The 3 templates' variable union is the canonical ASK_GAPS source. Re-grep
  `assets/template-pii-breach-*.md` for `{{[a-z_]+}}` whenever templates change
  and update Step 4 lists accordingly.
- Path A enforcement lives in `scripts/grade_response.py` `PATH_A_ANTIPATTERNS`
  (legal.md + business.md scanned). To extend the forbidden list, edit that
  file's regex bank — do NOT inline forbidden phrasings into this protocol.
- TBD verdicts must use canonical ids from `references/pdpa-current-state.md`;
  fabricated ids fail SELF_GRADE.
- Timeline entries use ISO 8601 with the `⏳ 待 X` marker for not-yet-realized
  anchors (e.g., `{{event_pdpc_notify_iso}} = ⏳ 待 PDPC 通報送達`).
