# TBD migration template — Phase 2.5 patch guide

When PDPC sub-regulations or 行政院 announcements resolve a TBD item, follow this guide to patch templates + checklists. Each entry below corresponds to a canonical TBD id in `pdpa-current-state.md`.

## TBD_PDPC_pending

**Current state**: PDPC remains 籌備處 (preparatory office); no operational notification mechanism verified.

**Trigger to update**: PDPC website (www.pdpc.gov.tw) transitions from 籌備處 to 正式委員會; or 法務部 announces operational date.

**Patch action**:
1. Update `pdpc_status` in `legal-toolkit/scripts/canonical/legal-sources.json` from "籌備處" to "正式委員會"
2. Run `python3 legal-toolkit/scripts/distribute.py`
3. Edit `assets/template-privacy.md` and `assets/template-dpa.md` — update 個資外洩通報 section if specific mechanism announced
4. Edit `checklists/compliance-privacy.md` + `checklists/compliance-dpa.md` — replace TBD_PDPC_pending with PASS criteria
5. Bump skill version per Phase 2.5 patch convention
6. Update `references/pdpa-current-state.md` — move TBD_PDPC_pending from OPEN list to RESOLVED section

## TBD_PDPC_threshold

**Current state**: Art. 12 §2 通報範圍 undefined; "一定通報範圍" 由主管機關公告。

**Trigger to update**: PDPC publishes 通報辦法 (likely under 個資法施行細則 §12 expansion).

**Patch action**:
1. Read PDPC 通報辦法 to extract numeric / categorical thresholds
2. Edit `assets/template-privacy.md` Section 8 — replace safe-default language with threshold-aware language
3. Edit `checklists/compliance-privacy.md` — replace TBD_PDPC_threshold with PASS criteria for "threshold disclosure in privacy policy"
4. Same for `assets/template-dpa.md` (DPA mode references mirroring obligation)

## TBD_PDPC_timeframe

**Current state**: 施行細則 §22 says "即時"; specific hour-count授權 sub-reg.

**Trigger to update**: PDPC publishes 通報辦法 specifying timeframe (likely 72hr or 24hr).

**Patch action**:
1. Edit `assets/template-privacy.md` Section 8 — replace "即時" with specific timeframe (e.g., "於發現後 X 小時內")
2. Edit `assets/template-dpa.md` — same for 受託人 → 委託人 notification
3. Edit `checklists/compliance-privacy.md` — update §22 verdict criteria
4. Update `references/pdpa-current-state.md` — note the locked timeframe

## TBD_PDPC_notification_url

**Current state**: pdpc.gov.tw 籌備處 site JS-rendered; notification form / email / URL not extracted.

**Trigger to update**: PDPC publishes operational notification entry (form / hotline / portal).

**Patch action**:
1. Read PDPC announcement to extract notification URL / form / email
2. Update `pdpc_url` in `legal-toolkit/scripts/canonical/legal-sources.json` to the operational entry (not just the homepage)
3. Run `python3 legal-toolkit/scripts/distribute.py`
4. Edit `assets/template-privacy.md` + `assets/template-dpa.md` — embed the operational URL in通報 contact section

## TBD_PDPA_effective_date

**Current state**: 2025/11 amendments promulgated 2025-11-11; 施行日期未定 (set by行政院).

**Trigger to update**: 行政院 announces 施行日期 in 行政院公報.

**Patch action**:
1. Update `amendment_note` in `legal-toolkit/scripts/canonical/legal-sources.json` to "公布 2025-11-11; 施行 YYYY-MM-DD"
2. Run `python3 legal-toolkit/scripts/distribute.py`
3. For each affected article (Art. 12 / 20-1 / 21-1~5 / 47-48), audit templates + checklists: if the new article is now in force, replace safe-default text with the new statutory language
4. Re-run draft on in-use documents (privacy / dpa) to validate the migration
5. Phase 2.5 release notes documenting the new effective date

## TBD_PDPA_audit_framework

**Current state**: Art. 20-1 audit framework promulgated, not effective.

**Trigger to update**: When Art. 20-1 effective date arrives + PDPC publishes 稽核辦法.

**Patch action**:
1. Edit `assets/template-privacy.md` §9 安全維護 — add audit-framework subsection per Art. 20-1
2. Edit `checklists/compliance-privacy.md` — add new checklist items for audit framework
3. Update `references/pdpa-current-state.md` to move Art. 20-1 from "promulgated not yet effective" to "in force"

## TBD_GOV_CLOUD_restrictions

**Current state**: Mainland-China cloud / ICT restrictions for government scope likely live in 政府採購法 / 資通安全管理法, NOT PDPA per Mondaq guide; not Tier-A verified in SP2.

**Trigger to update**: Sourced primary statute located (e.g., 行政院 procurement 法規 specific article).

**Patch action**:
1. Add government-procurement-relevant statute to `legal-toolkit/scripts/canonical/legal-sources.json` `statute_sources`
2. Run `python3 legal-toolkit/scripts/distribute.py`
3. Edit `assets/template-tos.md` (if SaaS service has 政府 customer scope) — add 政府採購注意 section
4. Edit `checklists/compliance-tos.md` — add new checklist item

## How to add a new TBD

If implementation discovers a new deferred item not in this list:
1. Add a row to `references/pdpa-current-state.md` "Canonical TBD OPEN list"
2. Add a corresponding migration block to this file
3. Re-run `grade_draft.py` self-tests to confirm the new id is recognized
