# Protocol — draft

The main LLM-executed pipeline for legal-document-draft. Triggered by `using-legal-toolkit` router Q2 dispatch.

## Input contract

- `mode`: "privacy" | "tos" | "dpa" | "nda"
- working dir: a git repo with `legal-playbook/profile.yml` present (may also have `legal-playbook/<clause>.md` files)

## Pipeline (sequential, no parallelism)

### Step 1: LOAD_PROFILE

Run:

```bash
python3 legal-toolkit/skills/legal-document-draft/scripts/load_profile.py legal-playbook/profile.yml
```

Expected: exit 0 with `OK: profile valid; company=<name>`.

If exit 1:
- Read the error list from stderr.
- Surface to user: "Profile validation failed. Fix `legal-playbook/profile.yml` first, then re-run."
- Do NOT proceed.

### Step 2: SELECT_TEMPLATE

Read `assets/template-<mode>.md` (mode from input).

### Step 3: SCAN_PLAYBOOK

For each variable in the template that has a corresponding clause in `legal-playbook/`, read the clause and extract the stance default.

Mapping (current — extend as playbook grows):

| Template variable | Source playbook clause | Field |
|---|---|---|
| `{{survival_years}}` (nda) | `legal-playbook/confidentiality.md` | `survival_period` (years) |
| `{{liquidated_damages}}` (nda) | `legal-playbook/confidentiality.md` | `liquidated_damages` |
| `{{return_days}}` (nda) | `legal-playbook/confidentiality.md` | `return_days` |
| `{{audit_notice_days}}` (dpa) | `legal-playbook/data-protection-dpa.md` | `audit_notice` (days) |
| `{{post_termination_disposal_days}}` (dpa) | `legal-playbook/data-protection-dpa.md` | `disposal_period` (days) |
| `{{preferred_court}}` (all) | `legal-playbook/governing-law-jurisdiction.md` | `preferred_court` |
| `{{liability_cap_months}}` (tos) | `legal-playbook/limitation-of-liability/_clause.md` | `cap_months` |

If a playbook clause is missing → variable falls through to ASK_GAPS.

### Step 4: ASK_GAPS

Identify all template variables NOT satisfied by profile + playbook. Ask the user in a single batched interactive prompt:

```
我需要以下資訊以完成 {{mode}} draft：

1. {{var_1_human_label}}: ?
2. {{var_2_human_label}}: ?
...
```

Provide:
- Profile/playbook-derived defaults inline (e.g., "preferred_court (legal-playbook 預設: 臺灣臺北地方法院, 按 Enter 使用)")
- Human-friendly labels (not raw variable names)
- Sensible suggestions / examples per variable

Per-mode required vars (variables NOT in profile.yml):

**privacy**: collection_purposes / collected_categories / retention_period / usage_regions / third_party_categories / processing_methods / product_or_service_name / product_url_or_app / third_party_sdks / special_category_handling

**tos**: service_name / service_description / pricing_summary / billing_cycle / payment_methods / liability_cap_months / privacy_policy_url / company_url

**dpa**: client_company_name / processor_company_name / processor_data_categories / processing_purpose / processing_methods / processing_period / processor_security_measures / audit_notice_days / post_termination_disposal_days / client_dpo_email / processor_dpo_contact / preferred_court

**nda**: party_a_name / party_b_name / purpose_of_disclosure / survival_years / liquidated_damages / return_days / preferred_court / effective_date

### Step 5: MERGE

Resolve final variable values; precedence: session input > playbook default > profile field > template-implied default.

Apply safe defaults for TBD variables:
- privacy: §8 通報 → "即時" (NOT 72hr); §20-1 audit framework → TBD_PDPA_audit_framework marker; minor → 民法 §12-13 cite
- dpa: §22 通報 → "即時"
- nda: no TBDs
- tos: no required TBDs

LLM fills the skeleton with values. Optional sections (e.g., 第三方 SDK in privacy when none used) get adapted text instead of empty placeholders.

### Step 6: COMPLY_CHECK

Read `checklists/compliance-<mode>.md`. For each `- [ ]` item, evaluate the draft and emit one of:
- **PASS** — verified the item is satisfied
- **FAIL** — item not satisfied; surface explicit reason
- **TBD_<id>** — item depends on a canonical OPEN list entry (see `references/pdpa-current-state.md`); cite the migration template entry

Render `compliance.md` by substituting each `{{verdict}}` with the determined verdict + a short rationale.

### Step 7: SELF_GRADE

Run:

```bash
python3 legal-toolkit/skills/legal-document-draft/scripts/grade_draft.py \
  legal-outputs/<timestamp>-<mode>/ <mode>
```

Expected: exit 0 with `OK: structural grading PASS`.

If exit 1:
- Read failure reasons from stderr.
- Identify which check failed (orphan / verdict / TBD / truncation / missing file).
- Patch and re-run COMPLY_CHECK + SELF_GRADE until exit 0.

### Step 8: OUTPUT

Write final files:

```
legal-outputs/<timestamp>-<mode>/
├── <doc-type>.md     (privacy.md | tos.md | dpa.md | nda.md)
└── compliance.md
```

Print summary to user:

```
Draft complete:
  Document: legal-outputs/<timestamp>-<mode>/<doc-type>.md
  Compliance: legal-outputs/<timestamp>-<mode>/compliance.md

Verdict counts:
  PASS: <N>
  FAIL: <N>
  TBD: <N> (see compliance.md TBD migration section)

Next steps:
- Review compliance.md before publishing
- For TBD items, monitor references/tbd-migration-template.md for upgrade triggers
- Patch legal-playbook/<clause>.md if a session value should become the default for future drafts
```

## Failure modes

- Profile invalid → halt at Step 1
- Template mode unknown → halt at Step 2
- LLM-fill produces malformed markdown (broken headers, etc.) → grade_draft catches in Step 7
- User abandons session mid-way → drafts in `legal-outputs/<timestamp>-<mode>/` may be partial; safe to delete

## Notes for implementers

- This protocol is LLM-executed; the Python scripts (load_profile / grade_draft) are deterministic safety nets, not the primary logic.
- The MERGE step must respect "safe defaults" semantics: do NOT hardcode 72hr / GDPR-style content; defer to施行細則 §22 "即時" + TBD_PDPC_* tracking.
- TBD verdicts must use canonical ids from `references/pdpa-current-state.md`; fabricated ids fail SELF_GRADE.
