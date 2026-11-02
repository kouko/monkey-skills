# Repair skill-dev-toolkit — plan
intent: 2026-11-02-repair-skill-dev-toolkit@3b1b225d
spec: docs/loom/2026-11-02-repair-skill-dev-toolkit/spec.md@33b186cc
charter: 1.1

## Task DAG

### Wave 1 — Restore executable paths and repair reproduced comparisons

**W1-01 Restore creator command implementations** after: none acceptance: 1
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/package_skill.py` (entry), `skill-dev-toolkit/skills/skill-creator-advance/scripts/aggregate_benchmark.py` (entry), `skill-dev-toolkit/skills/skill-creator-advance/scripts/run_loop.py` (entry), `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A1 positive: creator_commands_valid; negative: creator_commands_invalid. Run `python3 -m pytest skill-dev-toolkit/tests/test_creator_commands.py -q`.
- Risk: REQ-1; agent-decided selective historical recovery, not whole-commit reversion. Defect class: executable modules replaced with prose; searched all creator scripts and advertised commands. Use offline backends only.

**W1-02 Enforce ordered structural tool traces** after: W1-01 acceptance: 2
- Files: `skill-dev-toolkit/skills/skill-refactor/scripts/equivalence_check.py` (entry), `skill-dev-toolkit/skills/skill-refactor/references/equivalence-check-protocol.md`, `skill-dev-toolkit/tests/test_equivalence_order.py`.
- Test: A2 positive: ordered_trace_tolerance; negative: reordered_trace_rejected. Run `python3 -m pytest skill-dev-toolkit/tests/test_equivalence_order.py -q`.
- Risk: REQ-2; agent-decided preserve count tolerance and vocabulary while enforcing relative order. Defect class: sequence discarded; searched trace loader/comparator and equivalence protocol. Preserve Layer 2.

**W1-03 Keep truncated full-output viewing blind** after: W1-02 acceptance: 3
- Files: `skill-dev-toolkit/skills/skill-tuning/scripts/ab_harness.py` (entry), `skill-dev-toolkit/skills/skill-tuning/references/ab-harness-protocol.md`, `skill-dev-toolkit/tests/test_blind_harness.py`.
- Test: A3 positive: blind_full_view_same_choice; negative: identity_path_not_displayed. Run `python3 -m pytest skill-dev-toolkit/tests/test_blind_harness.py -q`.
- Risk: REQ-3; agent-decided neutral ordinary-file copies and identity-free records for unconfirmed picks. Defect class: identity-bearing metadata; searched display, retrieval, invalid/clarification inputs, session recording and truncation instructions. Decode identity only after choice lock-in.

### Wave 2 — Align instruction consumers without new workflow roles

**W2-01 Align description authorities and judge budget** after: W1-03 acceptance: 5, 7
- Files: `skill-dev-toolkit/skills/skill-creator-advance/SKILL.md` (entry), `skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md`, `skill-dev-toolkit/skills/skill-judge/SKILL.md` (entry), `skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py`.
- Test: A5 positive: description_authorities_agree; negative: forbidden_description_policy_detected. A7 positive: resolved_reference_checks; boundary: judge_word_budget. Run explicit hidden description suite and toolkit structure checker.
- Risk: REQ-5/7; agent-decided preserve current reference ownership. Existing hidden description tests preserve semantic coverage, replace stale placement assertions; preserve all judge dimensions. Defect class: policy-copy drift; searched creator/judge/reference/test authority consumers.

**W2-02 Correct creator metadata lookup contract** after: W2-01 acceptance: 5
- Files: `skill-dev-toolkit/skills/skill-creator-advance/references/schemas.md` (entry), `skill-dev-toolkit/tests/test_creator_metadata_contract.py`.
- Test: A5 positive: shared_case_metadata; negative: run_local_metadata_not_required. Run `python3 -m pytest skill-dev-toolkit/tests/test_creator_metadata_contract.py -q`.
- Risk: REQ-5; agent-decided keep existing grader explicit input and per-case ownership. Defect class: mismatched metadata location; searched schema, grader and evaluation protocol. Fixed baseline semantics remain unchanged.

**W2-03 Reconcile refactor entrypoint and detailed policies** after: W2-02 acceptance: 5
- Files: `skill-dev-toolkit/skills/skill-refactor/SKILL.md` (entry), `skill-dev-toolkit/skills/skill-refactor/references/ablation-mode.md`, `skill-dev-toolkit/skills/skill-refactor/references/refactor-moves-catalog.md`, `skill-dev-toolkit/skills/skill-refactor/scripts/test_package_mode_contract.py`, `skill-dev-toolkit/tests/test_refactor_policy.py`.
- Test: A5 positive: refactor_policy_consistent; negative: unsafe_refactor_policy_rejected. Run focused refactor policy and existing package-mode contract tests.
- Risk: REQ-5; agent-decided preserve reducer, package accounting and historical prototype. Existing package-mode tests preserve protected outcomes; replace obsolete root-AGENTS advertisement only. Defect class: conflicting instructions; searched entrypoint, ensemble, extraction, ablation and package consumers.

**W2-04 Align human-agreement and multi-pick outcomes** after: W2-03 acceptance: 5
- Files: `skill-dev-toolkit/skills/skill-tuning/SKILL.md` (entry), `skill-dev-toolkit/skills/skill-tuning/references/ab-harness-protocol.md`, `skill-dev-toolkit/tests/test_tuning_policy.py`.
- Test: A5 positive: human_decision_policy; boundary: ties_never_adopt. Run `python3 -m pytest skill-dev-toolkit/tests/test_tuning_policy.py -q`.
- Risk: REQ-5; agent-decided existing 70% threshold and DEFER policy prevail. Defect class: conflicting adoption outcomes; searched entrypoint and harness agreement, verdict, atomicity and fallback clauses. No new vote mechanism.

**W2-05 Separate blind artifact rubric from informed trajectory check** after: W2-04 acceptance: 5
- Files: `skill-dev-toolkit/skills/dogfood-skill-testing/SKILL.md` (entry), `skill-dev-toolkit/skills/dogfood-skill-testing/references/defect-taxonomy.md`, `skill-dev-toolkit/skills/dogfood-skill-testing/templates/dogfood-report-template.md`, `skill-dev-toolkit/skills/dogfood-skill-testing/test_skill_structure.py`.
- Test: A5 positive: explicit_blind_rubric; negative: trajectory_not_in_blind_context. Run `python3 -m pytest skill-dev-toolkit/skills/dogfood-skill-testing/test_skill_structure.py -q`.
- Risk: REQ-5; agent-decided retain existing two roles. Existing structure tests retain taxonomy/resource coverage. Defect class: missing or forbidden review inputs; searched Probe B, firewall, trajectory guardrails, taxonomy and report template.

### Wave 3 — Complete accounting and relevant verification routing

**W3-01 Export explicit baseline preferences consistently** after: W2-05 acceptance: 4
- Files: `skill-dev-toolkit/skills/skill-tuning/scripts/preference_log.py` (entry), `skill-dev-toolkit/skills/skill-tuning/scripts/judge_train_stub.py` (entry), `skill-dev-toolkit/skills/skill-tuning/references/preference-log-schema.md`, `skill-dev-toolkit/skills/skill-tuning/references/self-trained-judge-pipeline.md`, `skill-dev-toolkit/skills/skill-tuning/SKILL.md`, `skill-dev-toolkit/tests/test_preference_export.py`.
- Test: A4 positive: explicit_single_preferences_export; negative: unusable_preferences_not_ready. Run `python3 -m pytest skill-dev-toolkit/tests/test_preference_export.py -q`.
- Risk: REQ-4; agent-decided 1000 usable records, separate pair counts. Defect class: preference filtering/count drift; searched both extractors, schema, pipeline outline and entrypoint. Preserve raw logs and inactive training.

**W3-02 Qualify all oversized groups without changing splits** after: W3-01 acceptance: 6
- Files: `skill-dev-toolkit/skills/skill-consistency-check/scripts/plan_groups.py` (entry), `skill-dev-toolkit/skills/skill-consistency-check/scripts/merge_report.py` (entry), `skill-dev-toolkit/skills/skill-consistency-check/scripts/test_plan_groups.py`, `skill-dev-toolkit/skills/skill-consistency-check/scripts/test_merge_report.py`, `skill-dev-toolkit/skills/skill-consistency-check/SKILL.md`, `skill-dev-toolkit/skills/skill-consistency-check/README.md`, `skill-dev-toolkit/skills/skill-consistency-check/README.zh-TW.md`, `skill-dev-toolkit/skills/skill-consistency-check/README.ja.md`.
- Test: A6 positive: nominal_size_notice; boundary: split_threshold_preserved. Run focused planner/report tests.
- Risk: REQ-6; agent-decided distinguish nominal notice from empirical failure. Existing planner/report tests preserve grouping/coverage behavior; update validated-fixture notice intentionally. Defect class: misleading validation-bound reporting; searched planner, report and all user-facing copies.

**W3-03 Run toolkit checks on relevant changes** after: W3-02 acceptance: 7
- Files: `.github/workflows/skill-dev-toolkit-ci.yml` (entry), `skill-dev-toolkit/skills/skill-consistency-check/scripts/test_skill_text.py`.
- Test: A7 positive: toolkit_verification_routed; negative: broken_entrypoint_detected. Execute plugin, explicit hidden, structure, shared-convention drift and manifest checks; existing repository package suite runs at Build completion.
- Risk: REQ-7; agent-decided follow existing path-filtered workflow pattern, no generic runner. Existing text tests retain protocol checks. Defect class: verification coverage omission; searched workflow jobs, plugin discovery and wrapper tests.

**W3-04 Prepare patch-release metadata** after: W3-03 acceptance: 7
- Files: `skill-dev-toolkit/.claude-plugin/plugin.json`, `skill-dev-toolkit/.codex-plugin/plugin.json`, `skill-dev-toolkit/CHANGELOG.md`.
- Test: A7 positive: manifests_synchronized; negative: missing_patch_bump_rejected. Run existing manifest drift and version-bump checks; release metadata only, no new tests.
- Risk: REQ-7; agent-decided patch release follows existing `.github/workflows/skill-structure.yml` version-bump job. No installed-plugin updates or unrelated manifest edits.

### Wave 4 — Close adversarial single-choice filtering gap

**W4-01 Reject ambiguous preference-choice tokens** after: W3-04 acceptance: 4
- Files: `skill-dev-toolkit/skills/skill-tuning/scripts/preference_log.py` (entry), `skill-dev-toolkit/tests/test_preference_export.py`.
- Test: A4 positive: explicit_single_preferences_export; negative: preferences_nonsingle_rejected. Run focused preference tests and the committed adversarial single-choice program.
- Risk: REQ-4; agent-decided validate normalized single-choice labels without fabricating winners. Defect class: non-single tokens counted as single; searched changed files, shared eligibility, both consumers, harness labels, schemas and adversarial cases. Raw data remains unchanged.

**W4-02 Graduate the single-choice regression into continuous checks** after: W4-01 acceptance: 4, 7
- Files: `docs/loom/2026-11-02-repair-skill-dev-toolkit/evidence/probes/test_preferences_single_choice.py`, `scripts/test_preferences_single_choice.py` (entry), `.github/workflows/skill-dev-toolkit-ci.yml`, `skill-dev-toolkit/skills/skill-consistency-check/scripts/test_skill_text.py`.
- Test: A4 positive: graduated_probe_green; negative: original_defect_pinned. A7 positive: continuous_probe_selected; negative: missing_probe_route_detected. Run moved probe unchanged and focused CI-routing tests.
- Risk: REQ-4/7; agent-decided move the adversary-owned portable program byte-identically into the declared suite, and route that suite in toolkit CI. Defect class: regression omitted from later checks; searched suite discovery and workflow path filters.

## Simplicity check
- none found

## Questions asked
① — what — 以上就是這次要完成的範圍，對嗎？

## Risks
1. Historical recovery is not optimizer correctness; REQ-1 offline fixtures validate orchestration without claiming paid-provider or live-host behavior.
2. Existing JSONL remains read only. Neutral viewing files and reports are new artifacts, not migrations; REQ-3/4 tests check preservation.
3. REQ-5 text assertions cannot alone establish agent behavior; independent realistic execution must exercise voting, deferral, extraction accounting and audit evidence separation before closing acceptance.
4. Unknown model/effort uses the dispatch resolver's atomic inheritance fallback; no exact model identity or cross-vendor evidence is fabricated.
5. User authorized non-forced publication and Ready PR after checks; merge remains separate. No external reviewer was selected; second-vendor stays suggest.
