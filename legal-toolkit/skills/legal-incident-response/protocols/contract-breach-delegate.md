# Protocol — contract-breach-delegate

The contract-breach sub-protocol of legal-incident-response. Dispatched after
`protocols/classify-path.md` confirms `inferred_type=contract-breach`. Thin
classifier + handoff emitter — does NOT auto-invoke legal-contract-review
(Q8 Soft delegation; user manually 接力 after the session).

Path A discipline: every step below assumes current in-force Taiwan 民法 +
relevant 民事訴訟法 only. Express discipline by naming the **correct**
statutory citation; do not name forbidden phrasings. The authoritative
forbidden list lives in `scripts/grade_response.py` `PATH_A_ANTIPATTERNS`
(extended by future maintainers there, not in this protocol body).

## Input contract

- working dir: a git repo with `legal-playbook/profile.yml` present
- `path_type`: `"contract-breach"` (locked by classify-path.md)
- Path A discipline + canonical/ §s gate same as other path protocols
- See `legal-toolkit/skills/legal-incident-response/scripts/grade_response.py`
  `PATH_A_ANTIPATTERNS` for forbidden phrasings (single source of truth)

## Cross-skill explicit (Q8 Soft delegation)

- ❌ SP3b does NOT auto-invoke legal-contract-review
- ❌ SP3b does NOT perform deep clause extraction (that is legal-contract-review's
  L2-L7 territory)
- ✅ SP3b emits `handoff-context.json` + a clear "next step" pointer in
  `legal.md §2`
- ✅ User manually invokes `/legal-contract-review` with the handoff context
  in a follow-up session

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

Identify variables not satisfied by profile + classifier signals. Ask the
user in a single batched prompt with profile-derived defaults inline and
ISO 8601 hints for date fields.

#### 2a. Session-supplied (the user must answer)

- `contract_path` — absolute path or repo-relative path to the contract
  document; recorded only (LLM does not read it in SP3b)
- `breach_type` — free-text initial description; e.g.,
  「對方延遲付款 60 天」 /「對方交付瑕疵商品」 /「對方拒絕履約」
- `breach_date` — ISO 8601 (`YYYY-MM-DD`); when the breach occurred
- `discovery_date` — ISO 8601 (`YYYY-MM-DD`); when our side noticed; usually
  ≥ `breach_date`
- `counterparty.name` — 對方公司名稱 或 自然人姓名
- `counterparty.company_id` — optional; 統一編號 if a 公司
- `counterparty.contact_email` — optional
- `alleged_breach_clauses[]` — list of clause refs;
  e.g., `["§3.2", "§4.4"]`; at least 1 required
- `damages_estimate_twd` — optional; integer NT$
- `urgency_level` ∈ {`high` / `moderate` / `low`}
- `notes` — optional; free-text additional context (LLM also stores the
  original `breach_type` free-text here after Step 3 classification)

#### 2b. Profile-derived (auto-populate; no separate ask)

- (none directly used — counterparty info is session-supplied because the
  counterparty is external to our `profile.yml`)

#### 2c. Generated (deterministic; no ask)

- `session_ref` = `legal-outputs/<timestamp>-incident-contract-breach/`
- `from_skill` = `"legal-incident-response"` (constant)
- `to_skill` = `"legal-contract-review"` (constant)
- `schema_version` = `1` (locked per spec §5 / §6.3)

### Step 3: CLASSIFY_BREACH_TYPE

LLM judges from `breach_type` free-text + `alleged_breach_clauses` and maps
to a canonical 民法 article:

| 民法 § | 違約類型 | When applies |
|---|---|---|
| §227 | 不完全給付 | 給付有 (但部分 / 瑕疵 / 不完整) |
| §225 | 給付不能 | 對方完全無法履行 (滅失 / 不可抗力) |
| §234 | 受領遲延 | 對方拒絕受領我方履行 |
| §229 | 給付遲延 | 對方遲延履行（最常見；60 日 未付款常此） |
| §259 | 解除契約效力 | 已啟動解除程序 |

Output: `breach_type` field updated to canonical label
(e.g., `「民法 §229 給付遲延」`). Original free-text retained in `notes` for
context.

**Path A enforcement at CLASSIFY_BREACH_TYPE**: the §number cited MUST be
listed in `legal-toolkit/scripts/canonical/legal-sources.json`
`statute_sources` under 民法 (currently `pcode=B0000001`). If the LLM cannot
classify (genuinely ambiguous): halt, ASK the user to clarify with examples,
OR allow the user to override with a literal 民法 § citation if known.

### Step 4: RENDER_HANDOFF

Fill `assets/template-contract-breach-handoff.json` with session vars + the
classified breach_type. Write to
`legal-outputs/<timestamp>-incident-contract-breach/handoff-context.json`.

Validate against the implicit 10-required-keys schema (grader enforces):

- `schema_version` (= 1)
- `from_skill` (= `"legal-incident-response"`)
- `to_skill` (= `"legal-contract-review"`)
- `contract_path`
- `breach_type` (canonical label after Step 3)
- `alleged_breach_clauses` (non-empty list)
- `breach_date`
- `discovery_date`
- `counterparty` (object with at least `name`)
- `urgency_level` (∈ {`high`, `moderate`, `low`})

Optional fields (not grader-required, but supported by the template):
`damages_estimate_twd`, `session_ref`, `notes`.

### Step 5: ASSEMBLE_LEGAL_MD

```markdown
# 合約違約事件 — 法務記錄

## §1 違約 classification

民法 §{{classified_section}} {{breach_label}}。對方未按照合約
{{alleged_breach_clauses_pretty}} 履行 {{obligation_type}}。

事實簡述：{{breach_type_freetext_original}}

## §時間軸

| 時間 (ISO 8601) | 事件 | 來源 |
|---|---|---|
| {{contract_signing_date_or_unknown}} | 簽約日 | 合約 |
| {{breach_date}} | 違約發生 | 對方 |
| {{discovery_date}} | 我方知悉 | 業務通報 |
| ⏳ 待催告 | 催告日 | 民法 §229 程序 |
| ⏳ 待解除 | 解除日 | 民法 §259 |

## §2 Handoff to legal-contract-review

- contract_path: {{contract_path}}
- 請執行：`/legal-contract-review --contract {{contract_path}}` （在另一 session）
- 可選 seed file：`legal-outputs/{{session_ref}}/handoff-context.json`
- 預期 legal-contract-review 將跑 L0-L7 七層分析

## §3 法源依據

- 民法 §{{classified_section}}：[URL from canonical/legal-sources.json]
- 相關時效：§125（一般時效 15 年）/ §197（侵權時效 2 年 / 10 年）

## §4 compliance
（filled by Step 7 COMPLY_CHECK — placeholder heading during Step 5）
```

**Step 5 assembly notes**:

- §4 (compliance) is a placeholder until Step 7 fills it (same pattern as
  the other path protocols).
- The §時間軸 heading text must match exactly: `## §時間軸` (the grader greps
  for this byte sequence).
- legal.md §2 MUST contain the literal string `legal-contract-review`
  (grader enforces).
- Do NOT include any "NOT <forbidden phrase>" carve-out wording anywhere in
  `legal.md`. The grader's anti-pattern bank checks full file contents.

### Step 6: ASSEMBLE_BUSINESS_MD

```markdown
# 合約違約事件 — 業務摘要

## §1 違約事件 1-句

對方違反合約 {{alleged_breach_clauses_pretty}} 之 {{obligation_summary}}，
已逾 {{days_since_breach}} 天。

## §2 Top 3 即時動作

1. **保存證據** — 合約原件 + 違約事實 records + 對方所有通訊（email / 訊息 /
   會議紀錄）。建議今日完成。
2. **聯絡對方確認違約事實** — 避免事實爭執；建議書面 (email) 方式留存。
3. **評估救濟方式** — 催告 / 解除 / 賠償 / 訴訟。
   **轉 legal-contract-review 深度分析**獲得具體建議。

## §3 後續流程

轉 legal-contract-review (L0-L7 分析) → 救濟決定 → 寄發催告函（民法 §254）
或解除契約通知。

## §4 deadline 警示

- ⚠️ **民法 §125 一般時效 15 年** — 請求權因 15 年不行使消滅
- ⚠️ **民法 §197 侵權行為時效 2 年 / 10 年** — 若違約同時構成侵權，2 年內
  須行使
- 建議：本案訴訟或催告應於 ⏳ {{recommended_action_deadline}} 前啟動
```

Same anti-pattern discipline applies: plain language; no GDPR terminology.

### Step 7: COMPLY_CHECK

Read `checklists/compliance-contract-breach.md`. For each
`- [ ] <item> — **{{verdict}}**` entry, evaluate the assembled `legal.md` +
`business.md` + `handoff-context.json` against the requirement and emit
one of:

- **PASS** — verified satisfied; cite the section / sentence that satisfies it
- **FAIL** — item not satisfied; explicit reason

Render the verdict-substituted checklist into `legal.md §4 compliance`.

### Step 8: SELF_GRADE

```bash
python3 legal-toolkit/skills/legal-incident-response/scripts/grade_response.py \
  legal-outputs/<timestamp>-incident-contract-breach/ contract-breach
```

Expected: exit 0 with `OK: structural grading PASS`.

The grader checks:

- Both files present (legal.md + business.md)
- `handoff-context.json` present + parses + has 10 required schema fields
- Byte counts > truncation thresholds
- `## §時間軸` heading present in legal.md
- legal.md mentions `legal-contract-review`
- `alleged_breach_clauses` non-empty list
- `from_skill` = `"legal-incident-response"` and
  `to_skill` = `"legal-contract-review"`
- Every `TBD_*` id used in legal.md / business.md is in canonical OPEN list
- No Path A anti-patterns in legal.md or business.md

If exit 1: read the stderr reasons; identify which check failed; patch the
offending file; re-run COMPLY_CHECK + SELF_GRADE until PASS.

### Step 9: OUTPUT

Write to `legal-outputs/<timestamp>-incident-contract-breach/`:

- `legal.md`
- `business.md`
- `handoff-context.json`

Print summary:

```
Contract-breach handoff complete:
  Legal record:   legal-outputs/<timestamp>-incident-contract-breach/legal.md
  Business memo:  legal-outputs/<timestamp>-incident-contract-breach/business.md
  Handoff seed:   legal-outputs/<timestamp>-incident-contract-breach/handoff-context.json

違約類型: 民法 §{{classified_section}} {{breach_label}}
Urgency:  {{urgency_level}}

Next step (user 接力):
  /legal-contract-review --contract {{contract_path}}
  （可餵 handoff-context.json 作為 seed file）
```

## Failure modes

- Profile invalid → halt at Step 1
- `alleged_breach_clauses` empty → halt at Step 2 (required field)
- LLM cannot classify `breach_type` to a canonical 民法 § → halt at Step 3;
  ASK user
- `handoff-context.json` missing a required key → caught by
  `grade_response.py`
- Path A anti-pattern leaks into legal.md / business.md → caught by
  `grade_response.py`; rephrase using correct statutory citation
- legal.md doesn't mention `legal-contract-review` → caught by
  `grade_response.py`
- `from_skill` / `to_skill` constants wrong → caught by `grade_response.py`

## Notes for implementers

- Thin classifier + handoff emitter; NOT deep clause analysis. Deep clause
  analysis lives in `legal-contract-review` (L0-L7).
- User manually invokes `/legal-contract-review` after this session — Q8
  Soft delegation; SP3b does not auto-chain.
- `handoff-context.json` `schema_version` is locked to `1`; future skill
  versions (v0.4.3+) may add `--seed` consumption to `legal-contract-review`.
- 民法 §s referenced here (§225 / §227 / §229 / §234 / §259 / §125 / §197 /
  §254) are all covered by canonical/legal-sources.json under 民法
  (`pcode=B0000001`); never invent §numbers outside the canonical statute_sources.
- Anti-pattern discipline lives in `scripts/grade_response.py`
  `PATH_A_ANTIPATTERNS` (full bank); do NOT inline forbidden phrasings into
  this protocol or the checklist, even in "NOT X" form.
