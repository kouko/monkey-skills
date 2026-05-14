# legal-toolkit SP3b — v0.4.3 dogfood patches design

**Status**: Design (implementation-ready)
**Date**: 2026-05-14
**Authors**: kouko + Claude (post-merge dogfood session on PR #286 / v0.4.2)
**Predecessor**: legal-toolkit v0.4.2 (SP3b PR #286), v0.4.1 (SP3a dogfood patches PR #279), v0.4.0 (SP3a PR #277)
**Target version**: legal-toolkit v0.4.3
**Sub-project**: SP3b dogfood patches — v0.4.2 contract bugs surfaced via end-to-end PII-breach + authority-letter dogfood
**Skill scope**: 2 skills touched (`legal-incident-response` primary; `legal-document-draft` parity via canonical/ schema bump); canonical SoT bumped (profile-schema v1→v2, legal-sources +1 statute); 5-site doc alignment

---

## 1. Goal

Patch 2 P0 contract bugs + 3 P1 doc/schema drifts surfaced by SP3b v0.4.2 post-merge dogfood (audit at `/tmp/legal-toolkit-sp3b-dogfood/AUDIT-v0.4.2.md`). Keep v0.4.2 functional surface unchanged; the visible artifact is profile-schema v1 → v2 (adds `dpo.phone` field), 5 doc sites stop lying about "v2 schema", and authority-letter Step 2b stops referencing non-existent nested paths.

Defer P2 polish (§8 第六款 reframe / TBD label split / classifier examples / grader template-orphan check) to v0.4.4 per dogfood audit ranking.

## 2. Why

**Dogfood trigger** — applied [[feedback_grader_structural_vs_semantic]] + [[feedback_dogfood_authoring_drift]] from MEMORY. Both grader runs PASSed (structural ✓ / classifier ✓ / 0 Path A anti-patterns ✓ / 6 TBD ids canonical ✓), but semantic audit caught:

| audit ref | severity | what broke | where |
|---|---|---|---|
| P0-1 | CRITICAL | `dpo.phone` schema↔template contract bug | profile-schema `dpo: required [name, email] + additionalProperties: false` rejects `phone`, yet 6 doc sites (template + 2 protocols + 2 checklists + binding tables) assume `dpo.phone` exists. SP3a `legal-document-draft` has zero `dpo_phone` references → bug is SP3b-introduced only. |
| P0-2 | CRITICAL | authority-letter Step 2b uses nested `profile.company.*` paths | actual schema is top-level `company_name` / `company_id` / `registered_address`; protocol L70-72 says `profile.company.name` / `.tax_id` / `.id` / `.registered_address`. Implementer reading this as authoritative → silent empty 落款 or fabricated path. |
| P1-1 | IMPORTANT | "v2 schema" claim across 5 doc sites | SKILL.md + 3 READMEs (en/ja/zh-TW) + L26-28 / L57-59 in each assert "v2 schema" + "v2-added fields backward-compat v1 profiles". Reality: schema declares `const: 1`; even fixture `profile-v2.yml` has `schema_version: 1`. SP3a does not carry this claim — SP3b copy-paste'd it from cross-task review aspiration. |
| P1-2 | IMPORTANT | 行政程序法 cited in IR statute reference but missing from canonical SoT | `references/statute-citations.md` L42-46 cites 行政程序法 §49 (pcode A0030055) for authority-letter 回函時程基準; the file's own header says canonical/legal-sources.json is SoT. But canonical only has 12 statutes, no 行政程序法. authority-letter Step 3 EXTRACT will HALT on legitimate incoming letters citing 行政程序法. |
| P1-3 | IMPORTANT | `profile-v2.yml` fixture misnamed (content is v1) | fixture name signals v2 intent; contents have `schema_version: 1`. Drift accumulator. |

**Why patch now vs roll into v0.5.0** — Phase 3 IRAC cluster (`legal-issue-spot` + `legal-research`; 8-12d subagent-driven) is next milestone. Shipping v0.4.3 first eliminates 5 known-bad doc sites that future Phase 3 authors would copy-paste from. Cost: 1 session (~6 commits). Benefit: clean v0.4.x platform before Phase 3 lands.

**Why schema v2 bump vs schema-v1 workaround** — Two paths considered:
- **Path α** (chosen): bump canonical/profile-schema.yml v1 → v2, add `dpo.phone` to dpo.properties, make the 5 doc sites tell the truth, ship one coherent narrative.
- Path β (rejected): drop `dpo_phone` from 6 doc sites, rewire templates to `general_contact.phone`, keep schema v1, fix 5 v2 claims to "v1". Higher LOC churn (6 sites vs 1 schema file), conceptually wrong (DPO 個人聯絡電話 ≠ 公司總機 — they may differ in practice for outsourced DPO arrangements), and aspiration-vs-reality conflict still festers.

**Why bundle SP3a parity in same release** — canonical/profile-schema.yml is byte-identical to SP3a `legal-document-draft/assets/profile-schema.yml` (verified via shasum). distribute.py routes canonical → both skills. Schema bump auto-propagates; SP3a inherits `dpo.phone` field availability for free with zero protocol change (SP3a never used `dpo_phone`, so v2 is purely additive for it). No SP3a-side test regression expected.

## 3. Locked decisions

| # | Decision | Choice | Reasoning |
|---|---|---|---|
| 1 | Schema direction | Bump v1 → v2 (additive: add `phone: { type: string }` to `dpo.properties`; keep `additionalProperties: false`; keep `dpo: required [name, email]` — phone optional) | Additive bump = zero migration burden; existing v1 profiles remain valid; only `schema_version: const` changes from `1` to `2` |
| 2 | Cross-skill propagation | SP3a `legal-document-draft` also updates to v2 via distribute.py auto-sync; SP3a tests must remain green (regression check in Task 6) | Schemas are byte-identical via canonical SoT; divergence would create drift; SP3a doesn't use `dpo.phone` so v2 is no-op functionally |
| 3 | `general_contact.phone` vs `dpo.phone` | Keep `general_contact.phone` (already in schema; 公司總機); also add `dpo.phone` (個人 DPO 聯絡電話) | Two semantically distinct fields; templates 落款 use `dpo.phone` (個人聯絡 DPO 通常較總機優先) |
| 4 | P0-2 nested-path fix | Edit 3 lines in authority-letter.md Step 2b only; no other code change | Pure doc bug; pii-breach.md is already correct |
| 5 | P1-2 canonical 行政程序法 entry | Add to `canonical/legal-sources.json` `statute_sources` only; distribute.py auto-syncs to `legal-contract-review/assets/legal-sources.json` | Single-file edit; statute-citations.md already cites it (it's the consumer not the SoT) |
| 6 | P1-3 fixture | Rename `profile-v2.yml` to keep the filename + bump `schema_version: 2` + add `dpo.phone` example (so the fixture demonstrates v2 affordance) | Keep filename to avoid downstream test path edits; promote contents to real v2 |
| 7 | P2 deferrals | Defer P2-1 / P2-2 / P2-3 / P2-4 to v0.4.4 per audit bundle E | v0.4.3 stays focused on P0+P1; P2-3 grader template-orphan check is the right safety net but logically pairs with v0.4.4 rather than racing it |
| 8 | Version bump scope | v0.4.2 → v0.4.3 (patch); not v0.5.0 | Additive schema bump + doc fixes; no behavioral surface change; semver patch is correct |
| 9 | Backward-compat | v1 profiles must still validate after v2 bump | Test in Task 3: load existing `profile-minimal.yml` (currently `schema_version: 1`) and confirm it validates against v2 schema (additive change → still valid) |
| 10 | Migration doc | Add `references/profile-schema-v2-migration.md` (1 short page) explaining v1 → v2 delta + when to populate `dpo.phone` | Future readers see schema_version: 2 + need to know what changed; doc lives in canonical/ + distributes to both skills |

## 4. Architecture diff (v0.4.2 → v0.4.3)

```
                               v0.4.2                              v0.4.3
                               ──────                              ──────
canonical/profile-schema.yml   schema_version: const: 1            schema_version: const: 2
                               dpo: {required[name,email],         dpo: {required[name,email],
                                    additionalProperties: false,        additionalProperties: false,
                                    properties: {name, email}}          properties: {name, email, phone}}

canonical/legal-sources.json   12 statute_sources                  13 statute_sources (+行政程序法)

canonical/profile-schema-v2-   (absent)                            v1 → v2 migration note (1 page)
  migration.md                                                     distributed to both skills

skills/legal-incident-         "v2 schema" + "v2-added fields      "schema v2; dpo.phone optional";
  response/{SKILL,             backward-compat v1 profiles"        "external_counsel + regulatory_
  README*}.md                  (5 sites lying)                     authorities optional"
                                                                   (5 sites now true)

skills/legal-incident-         Step 2b: profile.company.name /     Step 2b: top-level company_name /
  response/protocols/          .tax_id / .id /                     company_id / registered_address
  authority-letter.md          .registered_address                 (matches pii-breach binding)
                               (3 broken lines)

tests/fixtures-document-       profile-v2.yml has                  profile-v2.yml has
  draft/profile-v2.yml         schema_version: 1                   schema_version: 2 + dpo.phone

SP3a legal-document-draft      profile-schema.yml                  profile-schema.yml
                               schema_version: 1 (via canonical)   schema_version: 2 (via canonical;
                                                                   purely additive; no protocol change)
```

No new files / no new tasks / no behavioral change to either skill's output. Surface-area bump is **profile.yml schema authors may now declare `dpo.phone`**; functional copy distribution handles the rest.

## 5. Files touched

### canonical/ (SoT — single edit, auto-distribute)

- Edit: `legal-toolkit/scripts/canonical/profile-schema.yml` — `schema_version` const 1 → 2; `dpo.properties` add `phone`
- Edit: `legal-toolkit/scripts/canonical/legal-sources.json` — add 行政程序法 (pcode A0030055) to statute_sources; bump `verified_at`
- Create: `legal-toolkit/scripts/canonical/profile-schema-v2-migration.md` — 1-page v1→v2 delta

### legal-incident-response/ (SP3b primary)

- Edit: `legal-toolkit/skills/legal-incident-response/protocols/authority-letter.md` — Step 2b L70-72 nested-path → top-level path
- Edit: `legal-toolkit/skills/legal-incident-response/SKILL.md` L26-28 — "v2 schema" claim now true; reword "v2-added fields backward-compat v1" → "v2 schema; optional fields documented in references/profile-schema-v2-migration.md"
- Edit: `legal-toolkit/skills/legal-incident-response/README.md` L57-59 + `README.ja.md` L59-61 + `README.zh-TW.md` L57-59 — same alignment, language-specific

### legal-document-draft/ (SP3a parity)

Auto-synced via distribute.py — no manual edits. Regression test required (Task 6) to confirm 226-test baseline holds.

### tests/

- Modify: `legal-toolkit/scripts/tests/test_distribute.py` — add test for new `profile-schema-v2-migration.md` ROUTE entry
- Modify: existing `test_load_profile.py` (if exists; otherwise inline `tests/test_canonical_profile_schema.py`) — add 3 new tests:
  - `test_v2_schema_accepts_dpo_phone()` — v2 profile with `dpo.phone` validates
  - `test_v1_profile_invalid_under_v2_schema_version()` — `schema_version: 1` fails `const: 2`
  - `test_v1_profile_structure_still_valid_under_v2_schema_after_version_bump()` — copy v1 profile, change schema_version to 2, validate (additive bump means structure is fwd-compat)
- Modify: `legal-toolkit/tests/fixtures-document-draft/profile-v2.yml` — bump `schema_version: 2` + add `dpo.phone: "02-1234-5678"` example
- Modify: `legal-toolkit/tests/fixtures-document-draft/profile-minimal.yml` + `profile-full.yml` — bump `schema_version: 1` → `2` (v1 schema dropped from CI; or split fixture set into v1-compat + v2 if backward-compat coverage matters — see Q below)

### Plugin metadata

- Edit: `legal-toolkit/.claude-plugin/plugin.json` — version 0.4.2 → 0.4.3; description append "v0.4.3: profile-schema v2 (dpo.phone) + dogfood patches"
- Edit: `.claude-plugin/marketplace.json` — sync description verbatim per [[feedback_plugin_json_location_and_description_sync]]
- Edit: `legal-toolkit/ROADMAP.md` — v0.4.3 marked DONE under Phase 2 closeout addendum
- Edit: `legal-toolkit/README.md` / `README.ja.md` / `README.zh-TW.md` — version badge 0.4.2 → 0.4.3

## 6. Open questions

**Q1 — Fixture v1-compat coverage**: Should we keep a `profile-v1.yml` fixture testing v1 schema continues to validate UNDER v2 schema (forward-compatibility regression net), or drop v1 entirely and ship only v2 fixtures? **Decision**: drop v1 schema support entirely (v2 const) but keep `profile-v1-shape.yml` fixture as v2-validated proof that pure-v1 STRUCTURE (no dpo.phone, no new fields) still validates when version bumped. Locks in additive-bump promise.

**Q2 — Should P2-3 grader template-orphan check ship in v0.4.3 as a safety net**: Risk = some other `{{...}}` orphan we haven't surfaced. Reward = locks in dogfood discipline. **Decision**: defer per audit — v0.4.3 already touches enough surface; v0.4.4 P2 bundle E is the right home. Document in v0.4.4 backlog explicitly.

**Q3 — SP3a coordination**: Does this need to spec a SP3a parity acceptance gate? **Decision**: yes — Task 6 includes SP3a regression check (all 226 SP3b tests + SP3a equivalent suite pass) as a mandatory gate before commit. If SP3a test fails on v2 bump → triage before merge.

## 7. Risks

- **R1** — Schema bump regression on SP3a: Mitigated by Task 6 regression gate. Additive nature of bump means risk is theoretical, but verify.
- **R2** — Existing user profile.yml (live deployment) declares `schema_version: 1`: They'd fail v2 schema's `const: 2`. **Mitigation**: migration doc (Task 5) explicitly tells them to bump `schema_version: 1 → 2` in their profile.yml; rest of file unchanged. 1-character edit for any live user.
- **R3** — `dpo.phone` doc creep: Future maintainer may rebind `general_contact.phone` template path back to `dpo.phone` even when DPO and 公司總機 share a phone. **Mitigation**: migration doc clarifies semantic difference (DPO 個人聯絡 vs 公司總機); checklist worded as "phone of person on duty, not general line".
- **R4** — Cross-PR race with Phase 4.5 outreach: User is sending outreach in parallel. No PR overlap expected (outreach is human work, not code). Surface: none.

## 8. Out of scope

- P2-1: compliance-pii-breach §8 第六款 framing — v0.4.4
- P2-2: `tbd_data_subject_notify_label` semantic split — v0.4.4
- P2-3: grader template-orphan check — v0.4.4 (with new test fixture)
- P2-4: classify-path.md non-finance examples — v0.4.4
- Phase 3 IRAC cluster (legal-issue-spot + legal-research) — v0.5.0
- Pearson calibration backlog from Phase 1.6 — separate work
- legal-playbook clauses for IR (v0.4.2 SKILL.md §Limitations defers to "v0.4.3 dogfood-driven design") — **explicitly defer further**: dogfood surfaced 2 P0 + 3 P1 contract bugs but NO signal for playbook clauses (no recurring stance pattern observed). Re-evaluate after live IR usage produces ≥3 sessions worth of stance-reuse signal.

## 9. Acceptance criteria

A v0.4.3 PR is mergeable when:

1. Both v0.4.2 dogfood scenarios (PII-breach + authority-letter, scenarios A + B in audit) re-run with a **schema-clean profile.yml that DECLARES dpo.phone** produce orphan-free output (no `{{dpo_phone}}` literal anywhere in legal.md / business.md).
2. `grade_response.py` PASSes both runs.
3. SP3b 226-test baseline holds + 3 new tests for v2 schema pass.
4. SP3a equivalent test suite (whatever the count is) holds.
5. `canonical/profile-schema.yml` + 2 skill copies are byte-identical (CI verify_drift.py green).
6. `canonical/legal-sources.json` has 13 statute_sources entries (12 + 行政程序法).
7. All 5 "v2 schema" doc sites reflect schema reality (grep `v2 schema` returns matches that are now accurate).
8. `plugin.json` + `marketplace.json` versions == `0.4.3` and descriptions match verbatim.
9. CI green on first push.

## 10. References

- Audit (this session): `/tmp/legal-toolkit-sp3b-dogfood/AUDIT-v0.4.2.md`
- v0.4.2 design spec: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3b-incident-response-design.md`
- v0.4.2 plan: `docs/superpowers/plans/2026-05-13-legal-toolkit-sp3b-incident-response.md`
- SP3a v0.4.1 dogfood-patches PR: #279 (analog precedent: P0 + 3×P1 patch shipped same-session)
- SP1 SSOT design: `docs/superpowers/specs/2026-05-12-legal-toolkit-sp1-sources-canonical-refactor-design.md`
- Methodology memory: [[feedback_grader_structural_vs_semantic]], [[feedback_dogfood_authoring_drift]], [[feedback_future_annotations_importlib_dataclass_trap]], [[feedback_subagent_driven_development_validated]], [[feedback_cc_type_whitelist]], [[feedback_plugin_json_location_and_description_sync]]
