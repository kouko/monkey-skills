# Repair skill-dev-toolkit — plan
intent: 2026-11-02-repair-skill-dev-toolkit@c5d3e9f7
spec: docs/loom/2026-11-02-repair-skill-dev-toolkit/spec.md@31c52cb2
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

### Wave 5 — Resolve closing-review findings in one fix round

**W5-01 Preserve current-before-baseline aggregation** after: W4-02 acceptance: 1, 7
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/aggregate_benchmark.py` (entry), `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A7 positive: creator_commands_valid; negative: existing_skill_delta_direction. A1 positive: creator_commands_valid; negative: existing_skill_delta_direction. Extend the existing aggregation CLI case for old_skill and assert current-first columns and deltas; run the creator command tests.
- Risk: REQ-1; agent-decided preserve documented configuration semantics. Defect class: reversed existing-skill deltas; searched all changed files and the complete creator acceptance surface, including discovery, summary, Markdown and evaluation protocol. Instances are first-two-config subtraction and column ordering in aggregate_benchmark.py; preserve unrecognized-name fallback.

**W5-02 Read token metrics independently of timing fallback** after: W5-01 acceptance: 1, 7
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/aggregate_benchmark.py` (entry), `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A7 positive: creator_commands_valid; negative: captured_tokens_with_grading_duration. A1 positive: creator_commands_valid; negative: captured_tokens_with_grading_duration. Extend the same aggregation CLI fixture with nonzero grading duration, output_chars and captured sibling tokens; assert JSON statistics and Markdown. Run creator command tests.
- Risk: REQ-1; agent-decided retain grading duration precedence without substituting characters for tokens. Defect class: token metrics suppressed by duration; searched all changed files and creator scripts, schema, grader and evaluation protocol. Instances are conditional sibling loading and output_chars fallback in aggregate_benchmark.py.

**W5-03 Report observed repetition populations** after: W5-02 acceptance: 1, 7
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/aggregate_benchmark.py` (entry), `skill-dev-toolkit/skills/skill-creator-advance/references/schemas.md`, `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A7 positive: creator_commands_valid; boundary: observed_run_population. A1 positive: creator_commands_valid; boundary: observed_run_population. Extend the existing CLI test to assert two observed repeats and honest unequal/empty reporting; run creator command tests.
- Risk: REQ-1; agent-decided qualify unequal/empty counts. Defect class: invented repetition count; searched changed files and creator acceptance surface. Instances: hardcoded metadata and Markdown consumer; schema three remains an example, not a default.

**W5-04 Reconcile labelled preferences before export** after: W5-03 acceptance: 4, 7
- Files: `skill-dev-toolkit/skills/skill-tuning/scripts/preference_log.py` (entry), `skill-dev-toolkit/skills/skill-tuning/references/preference-log-schema.md`, `skill-dev-toolkit/tests/test_preference_export.py`.
- Test: A7 positive: explicit_single_preferences_export; negative: contradictory_label_mapping. A4 positive: explicit_single_preferences_export; negative: contradictory_label_mapping. Extend the current malformed-record parameterization for contradictory and ambiguous picked-label mappings, exercising both export consumers; run preference tests and graduated regression unchanged.
- Risk: REQ-4; agent-decided preserve identity-only compatibility and raw JSONL. Defect class: decoded identity contradicts picked label; searched changed files, tuning producer, schema, eligibility, exporter, trainer and pipeline. Shared eligibility has the unchecked join; harness already joins correctly.

**W5-05 Qualify remaining ensemble escalation consumers** after: W5-04 acceptance: 5, 7
- Files: `skill-dev-toolkit/skills/skill-refactor/references/multi-judge-ensemble.md`, `skill-dev-toolkit/skills/skill-refactor/NOTICE`, `skill-dev-toolkit/skills/skill-refactor/README.md`, `skill-dev-toolkit/skills/skill-refactor/README.ja.md`, `skill-dev-toolkit/skills/skill-refactor/README.zh-TW.md`, `skill-dev-toolkit/tests/test_refactor_policy.py` (entry).
- Test: A7 positive: refactor_policy_consistent; negative: unconditional_escalation_rejected. A5 positive: refactor_policy_consistent; negative: unconditional_escalation_rejected. Extend existing scoped policy coverage to these consumer passages, then run focused policy and package-contract checks.
- Risk: REQ-5; agent-decided preserve reducer/moderate pass. Defect class: disagreement automatically escalated; searched changed files and refactor acceptance surface. Instances: ensemble rationale, NOTICE and three translated Tier 2 rows; preserve concrete-dissent examples and dated history.

**W5-06 Qualify legacy entry-only refactor examples** after: W5-05 acceptance: 5, 7
- Files: `skill-dev-toolkit/skills/skill-refactor/README.md`, `skill-dev-toolkit/skills/skill-refactor/README.ja.md`, `skill-dev-toolkit/skills/skill-refactor/README.zh-TW.md`, `skill-dev-toolkit/tests/test_refactor_policy.py` (entry).
- Test: A7 positive: refactor_policy_consistent; negative: extraction_only_not_package_saving. A5 positive: refactor_policy_consistent; negative: extraction_only_not_package_saving. Extend existing extraction-policy coverage for the three consumer examples; run focused policy and package-contract checks.
- Risk: REQ-5; agent-decided qualify illustrative entry-only calculations rather than invent package savings. Defect class: moving words treated as reduction; searched changed files and complete refactor surface. Instances: three README extraction examples claiming 12.4% PROCEED from relocation alone; preserve actual package-mode rules.

### Wave 6 — Correct the additional independent-review findings

**W6-01 Keep backend failures out of trigger scores** after: W5-06 acceptance: 1, 7
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/run_eval.py` (entry), `skill-dev-toolkit/skills/skill-creator-advance/scripts/run_loop.py` (entry), `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A7 positive: creator_commands_valid; negative: creator_commands_invalid. A1 positive: creator_commands_valid; negative: creator_commands_invalid. Exercise real main/evaluator behavior with an offline backend, including a failed negative query. Run creator command tests.
- Risk: REQ-1/7; agent-decided fail closed. Class: backend errors counted as non-triggers; searched changed files and creator acceptance surface. Instances: future exception False, incomplete/failed query returns including explicit terminal abort reasons, loop all_passed and internal-only evidence.

**W6-02 Align optimizer generation and application with description authority** after: W6-01 acceptance: 1, 5, 7
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/improve_description.py` (entry), `skill-dev-toolkit/skills/skill-creator-advance/scripts/run_loop.py` (entry), `skill-dev-toolkit/skills/skill-creator-advance/references/description-optimization.md`, `skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md`, `skill-dev-toolkit/skills/skill-creator-advance/references/plugin-conventions.md`, `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A1 positive: compliant_optimizer_candidate; boundary: noncompliant_candidate_not_applied. A7 positive: compliant_optimizer_candidate; boundary: noncompliant_candidate_not_applied. A5 positive: compliant_optimizer_candidate; boundary: noncompliant_candidate_not_applied. Extend the command-entry cases with captured offline generation prompts, length exceptions and invalid candidates. Run creator command and hidden description tests.
- Risk: REQ-1/5; agent-decided retain contextual exceptions. Class: optimizer contradicts description authority; searched changed files and creator references/helpers. Instances: prompt, rewrite, selection, application, budget wording and imperative examples in description-design/plugin-conventions. Preserve platform ceiling separately.

**W6-03 Preserve unknown token capture in aggregation** after: W6-02 acceptance: 1, 7
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/aggregate_benchmark.py` (entry), `skill-dev-toolkit/skills/skill-creator-advance/references/schemas.md`, `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A7 positive: creator_commands_valid; boundary: missing_tokens_not_savings. A1 positive: creator_commands_valid; boundary: missing_tokens_not_savings. Extend existing CLI assertions for missing, captured-zero and partial populations; run creator command tests.
- Risk: REQ-1; agent-decided explicit unknowns. Class: missing tokens become measured zeros; searched changed files and creator acceptance surface. Instances: loader defaults, empty statistics, sample collection, run serialization, delta and Markdown formatting. Preserve other metric behavior.

**W6-04 Continue interactive clarification within one blind round** after: W6-03 acceptance: 3, 7
- Files: `skill-dev-toolkit/skills/skill-tuning/scripts/ab_harness.py` (entry), `skill-dev-toolkit/skills/skill-tuning/references/ab-harness-protocol.md`, `skill-dev-toolkit/tests/test_blind_harness.py`.
- Test: A7 positive: blind_full_view_same_choice; boundary: clarification_keeps_mapping. A3 positive: blind_full_view_same_choice; boundary: clarification_keeps_mapping. Extend existing real CLI cases for multiple input lines, invalid one-shot input and EOF; run blind harness tests.
- Risk: REQ-3; agent-decided no resume file. Class: retry loses label mapping; searched changed files and tuning interaction surface. Instances: single input read, fresh assignment, pending record, misleading retry message and side-log guidance. Cross-invocation wrong adoption remains unproven.

**W6-05 Synchronize readiness documentation consumers** after: W6-04 acceptance: 4, 5
- Files: `skill-dev-toolkit/skills/skill-tuning/README.md`, `skill-dev-toolkit/skills/skill-tuning/README.ja.md`, `skill-dev-toolkit/skills/skill-tuning/README.zh-TW.md`, `skill-dev-toolkit/skills/skill-tuning/NOTICE`.
- Test: A5 positive: explicit_single_preferences_export; negative: unusable_preferences_not_ready. A4 positive: explicit_single_preferences_export; negative: unusable_preferences_not_ready. Run existing preference tests and verify all current readiness statements against their shared source; no new prose-only test harness.
- Risk: REQ-4/5; agent-decided retain inactive training. Class: old readiness population; searched changed files and tuning consumers. Instances: three ADOPT-only paragraphs, three limit rows, three stub captions and NOTICE. Keep usable records separate from pairs.

**W6-06 Reconcile optional golden checks with vote outcomes** after: W6-05 acceptance: 5, 7
- Files: `skill-dev-toolkit/skills/skill-refactor/references/golden-anchor-protocol.md`, `skill-dev-toolkit/skills/skill-tuning/references/golden-anchor-protocol.md`, `skill-dev-toolkit/skills/skill-refactor/scripts/golden_compare.py`, `skill-dev-toolkit/skills/skill-refactor/SKILL.md`.
- Test: A7 positive: refactor_policy_consistent; negative: dissent_not_cleared_by_anchor. A5 positive: refactor_policy_consistent; negative: dissent_not_cleared_by_anchor. Run existing refactor/golden checks and shared-convention drift; independently interpret moderate/dissent cases at acceptance.
- Risk: REQ-5; agent-decided comparison cannot authorize adoption. Class: old moderate-vote escalation; searched changed files and refactor/tuning consumers. Instances: both shared protocols, comparator docstring and entry resource caption. Preserve comparison enum and cumulative-drift safeguards.

**W6-07 State the grader metadata input at dispatch** after: W6-06 acceptance: 5
- Files: `skill-dev-toolkit/skills/skill-creator-advance/references/eval-protocol.md`.
- Test: A5 positive: shared_case_metadata; negative: run_local_metadata_not_required. Run existing metadata-contract tests and read the dispatch against grader inputs.
- Risk: REQ-5; agent-decided explicit existing input. Class: grader dispatch omits case metadata; searched changed files, evaluation protocol, schema and grader. Only Step 4.1 lacks the explicit case-level path; preserve per-run outputs.

**W6-08 Correct packaging usage examples** after: W6-07 acceptance: 1
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/package_skill.py` (entry), `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A1 positive: creator_commands_valid; negative: creator_commands_invalid. Extend the existing packaging error case to verify usable module invocation in help; run creator command tests.
- Risk: REQ-1; agent-decided current supported invocation. Class: nonexistent packaging usage path; searched changed files and creator packaging surface. Instances: module docstring, usage text and four examples in package_skill.py. Packaging behavior is unchanged.

**W6-09 Remove redundant workflow path filters** after: W6-08 acceptance: 7
- Files: `.github/workflows/skill-dev-toolkit-ci.yml`, `skill-dev-toolkit/skills/skill-consistency-check/scripts/test_skill_text.py`.
- Test: A7 positive: toolkit_verification_routed; boundary: scripts_glob_preserves_coverage. Update the existing routing assertion without reducing its behavioral coverage; run test_skill_text.py.
- Risk: REQ-7; agent-decided unchanged trigger coverage. Class: redundant script filters; searched changed files and workflow routing tests. Instances: three explicit script paths under scripts/** in both events and their over-specific assertions.

**W6-10 Preserve valid final output across the EOF/exit ordering** after: W6-09 acceptance: 1, 7
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/run_eval.py` (entry), `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A7 positive: real_eof_completion_accepted; negative: failed_completion_not_scored. A1 positive: real_eof_completion_accepted; negative: failed_completion_not_scored. Add one existing-file regression through real command/process-pool/subprocess execution with an offline executable, controlling EOF before exit and newline/no-newline output; rerun creator tests.
- Risk: REQ-1/7; agent-decided preserve completion framing. Class: EOF precedes exit status; searched changed files and creator process consumers. Only run_single_query prematurely rejects EOF. Preserve error/abort/time limits and original task retry continuity.

### Wave 7 — Close the expanded real-host release obligations

**W7-01 Share description eligibility with the packaging entry** after: W6-10 acceptance: 1, 7, 8, 11
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/quick_validate.py` (entry), `skill-dev-toolkit/skills/skill-creator-advance/scripts/improve_description.py`, `skill-dev-toolkit/skills/skill-creator-advance/scripts/run_loop.py`, `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A1 positive: qualified_description_packaged; negative: unjustified_description_not_packaged. A7 positive: qualified_description_packaged; negative: unjustified_description_not_packaged. A11 positive: qualified_description_packaged; negative: unjustified_description_not_packaged. A8 positive: qualified_description_packaged; negative: unjustified_description_not_packaged. Run existing package/optimizer CLI cases across short/long/router qualification.
- Risk: REQ-8/11; agent-decided existing validation module, one policy, no module/function growth. Class: delivery eligibility bypass. Sweep validator, optimizer, selector, packaging caller and authority. Retain W6-02 count1 and contextual admission; mechanical acceptance is not semantic compliance.

**W7-02 Reconcile candidate conflicts in their full context** after: W7-01 acceptance: 5, 9, 11
- Files: `skill-dev-toolkit/skills/skill-consistency-check/references/detector-read.md` (entry), `skill-dev-toolkit/skills/skill-consistency-check/references/detector-simulate.md`, `skill-dev-toolkit/tests/fixtures/detector-context-regressions.json`.
- Test: A5 positive: true_conflict_retained; negative: explicit_exception_not_conflict. A11 positive: true_conflict_retained; negative: explicit_exception_not_conflict. A9 positive: true_conflict_retained; negative: explicit_exception_not_conflict. Preserve failed RED; replay genuine controls with independent artifact judgment.
- Risk: REQ-9/11; agent-decided existing detectors/schema only. Class: context/exception omitted from incompatibility. Sweep both procedures and merge consumers; preserve historical corpus. Positive controls prevent suppress-all success; sampled reruns establish no universal accuracy guarantee.

**W7-03 Keep report model claims within observed evidence** after: W7-02 acceptance: 6, 9, 11
- Files: `skill-dev-toolkit/skills/skill-consistency-check/SKILL.md` (entry), `skill-dev-toolkit/skills/skill-consistency-check/scripts/merge_report.py`, `skill-dev-toolkit/skills/skill-consistency-check/scripts/test_merge_report.py`.
- Test: A6 positive: observed_model_metadata_qualified; negative: alias_not_child_identity. A11 positive: observed_model_metadata_qualified; negative: alias_not_child_identity. A9 positive: observed_model_metadata_qualified; negative: alias_not_child_identity. Extend report CLI caveat/unknown coverage, observe RED, then run report/text tests.
- Risk: REQ-9/11; agent-decided preserve --model and existing JSON fields. Class: requested/parent model inferred as observed child identity. Sweep model-record instructions, renderer, family matcher and consumers. Replace permissive inference wording; no receipt/event architecture or extra required fields.

**W7-04 Define missing-input entry paths using existing setup** after: W7-03 acceptance: 5, 10, 11
- Files: `skill-dev-toolkit/skills/skill-creator-advance/SKILL.md` (entry), `skill-dev-toolkit/skills/skill-creator-advance/references/pre-creation-gates.md`, `skill-dev-toolkit/skills/skill-creator-advance/references/improvement-workflows.md`, `skill-dev-toolkit/skills/skill-creator-advance/references/description-optimization.md`, `skill-dev-toolkit/skills/skill-creator-advance/references/eval-protocol.md`, `skill-dev-toolkit/skills/skill-creator-advance/references/schemas.md`, `skill-dev-toolkit/CHANGELOG.md`.
- Test: A5 positive: available_setup_reused; boundary: absent_input_not_invented. A11 positive: available_setup_reused; boundary: absent_input_not_invented. A10 positive: available_setup_reused; boundary: absent_input_not_invented. Exercise four cold-entry cases in fresh contexts; run existing creator policy checks.
- Risk: REQ-10/11; agent-decided existing setup or bounded stop. Class: unconditional input/capability assumption. Sweep quick/full/redesign/model/timing entries. Preserve unknown tokens; no unsupported null duration or duration-statistics expansion.

**W7-05 Reject known incomplete detector completion** after: W7-04 acceptance: 9, 11
- Files: `skill-dev-toolkit/skills/skill-consistency-check/SKILL.md` (entry).
- Test: A9 positive: completed_groups_merged; negative: known_partial_group_no_verdict. A11 positive: completed_groups_merged; negative: known_partial_group_no_verdict. Preserve the real positive-workflow incomplete hand-back and merge as RED. Exercise the existing retry/stop branch with the recorded hand-back and run clear positive/negative controls; JSON validity alone is insufficient.
- Risk: REQ-11; agent-decided existing single retry/stop only. Class: completed output confused with completed assignment. Sweep dispatch validation, detector completion messages and merger input boundary. No schema, receipt, grouping change or extra mandatory agent.

### Wave 8 — User-confirmed local caller-verification boundary

**W8-01 Verify independent candidates at the existing reporting boundary** after: W7-05 acceptance: 7, 9, 11
- Files: `skill-dev-toolkit/skills/skill-consistency-check/SKILL.md` (entry), `skill-dev-toolkit/skills/skill-consistency-check/references/detector-read.md`, `skill-dev-toolkit/skills/skill-consistency-check/references/detector-simulate.md`, `skill-dev-toolkit/skills/skill-consistency-check/README.md`, `skill-dev-toolkit/skills/skill-consistency-check/README.ja.md`, `skill-dev-toolkit/skills/skill-consistency-check/README.zh-TW.md`, `skill-dev-toolkit/CHANGELOG.md`.
- Test: A7 positive: existing_merger_routes; negative: unchecked_candidate_not_published. A9 positive: genuine_and_schema_conflicts_retained; negative: compatible_exception_removed. A11 positive: raw_preserved_with_accepted_subset; boundary: unavailable_review_no_verdict. Replay unchanged raw controls, including schema false negative, actual-host exception failures and unavailable source; run existing checks.
- Risk: REQ-9/11; existing caller eligibility. Class: unverified findings. Searched caller, detectors, merger, presentation, README copies and tests. Preserve raw/schema/coverage/independence; consolidate checks. W7-02 remains exhausted. No Python, framework, prose-pin tests or external models.

### Wave 9 — User-selected machine-consumed decision boundary

**W9-01 Select report eligibility from complete immutable candidate decisions** after: W8-01 acceptance: 7, 9, 11
- Files: `skill-dev-toolkit/skills/skill-consistency-check/scripts/merge_report.py` (CLI entry), `skill-dev-toolkit/skills/skill-consistency-check/scripts/test_merge_report.py`, `skill-dev-toolkit/skills/skill-consistency-check/scripts/test_skill_text.py`, `skill-dev-toolkit/skills/skill-consistency-check/SKILL.md`, checker and plugin README.md/README.ja.md/README.zh-TW.md, `skill-dev-toolkit/CHANGELOG.md`.
- Test: A7 positive: reviewed_candidates_selected; negative: missing_or_stale_decision_rejected. A9 positive: genuine_action_and_field_conflicts_retained; negative: compatible_exceptions_excluded. A11 positive: raw_bytes_and_audit_preserved; boundary: reviewed_ambiguity_indeterminate. TDD at CLI: coverage/IDs/status/reasons/hash, duplicate basenames, mixed results, unchanged payloads, exits0/1/2/3. Preserve old merger/group/model/target safeguards; replay genuine raw controls separately from deterministic plumbing checks.
- Risk: REQ-9/11; class: eligibility absent from consumed data. Sweep full repository merger callers and outcome consumers. Existing test_merge_report.py coverage widens; former medium-only pass changes intentionally. No new dependency/runtime role. Record production/test/prose cost.

### Wave 10 — Same-episode local cycle 2 review corrections

**W10-01 Preserve creator import and project execution contexts** after: W9-01 acceptance: 1, 7
- Files: `skill-dev-toolkit/skills/skill-creator-advance/SKILL.md` (entry), `skill-dev-toolkit/skills/skill-creator-advance/references/description-optimization.md`, `skill-dev-toolkit/skills/skill-creator-advance/references/eval-protocol.md`, `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A1 positive: optimizer_uses_user_project; negative: project_scripts_cannot_shadow_creator. A7 positive: backend_command_in_project; boundary: creator_tree_unchanged. Extend the existing real-EOF entry case, preserving every old assertion. Record old-context RED safely in an isolated copy, then actual CLI/backend GREEN; no provider calls or new harness.
- Risk: REQ-1/7; class: import and execution contexts conflated. Sweep creator commands, run_loop/evaluator project discovery and backend launch. Existing creator tests widen to real cwd/temporary-command placement; same cases, no production Python or new launcher.

**W10-02 Align extraction's duplicate risk definition** after: W9-01 acceptance: 5
- Files: `skill-dev-toolkit/skills/skill-refactor/SKILL.md` (entry).
- Test: A5 positive: loaded_extraction_catalog_medium; negative: historical_opposing_tiers_remain_detectable. Verify current entry/catalog/ensemble agree while the frozen ordinary fixture remains unchanged. Preserve resource loading, Q1/Q2/Q3, reduction accounting and voting obligations.
- Risk: REQ-5; class: duplicate operation tier. Entry conflicts with authoritative catalog Medium for the same loaded extraction; ensemble consumes catalog. Align summary only, preserve historical inputs and resource/vote policy.

**W10-03 Exercise ordered equivalence through its shipped CLI** after: W9-01 acceptance: 2, 7
- Files: `skill-dev-toolkit/tests/test_equivalence_order.py`.
- Test: A2 positive: ordered_trace_tolerance; negative: reordered_trace_rejected. A7 positive: cli_report_exit_agree; negative: reordered_trace_rejected. Keep all fourteen parameterized cases and existing fixtures; run the actual CLI through the current compare helper, with no additional test functions.
- Risk: REQ-2/7; class: tests bypass public entry. Existing test_equivalence_order.py coverage widens to argv/report/exit with identical cases; remove importlib scaffold, no new test or production change.

### Wave 11 — Local cycle 4 optional report-cohort correction

**W11-01 Render valid optimizer output without a held-out cohort** after: W10-01 acceptance: 1, 7
- Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/generate_report.py` (entry: generate_html, consumed by run_loop and its CLI), `skill-dev-toolkit/tests/test_creator_commands.py`.
- Test: A1 positive: finalized_html_without_holdout; negative: absent_cohort_not_failed_score. A7 positive: zero_and_nonzero_holdout_cli_reports; boundary: backend_failure_not_success. Extend the existing real-EOF entry case, preserving all original EOF/nonzero/context assertions. Generate real HTML; fake only provider and browser launch, never renderer/root discovery. Keep the original failed artifact unchanged.
- Risk: REQ-1/7; class: optional cohort treated as iterable. Sweep renderer history/query/score consumers and loop producer. Existing creator tests widen to real HTML with nullable/nonempty holdout; no new helper framework or production module.

## Simplicity check
- W11 existing renderer boundary and existing real CLI case — taken
- W10 same-cycle existing command docs, one summary cell and existing test helper; no new mechanism — taken
- W9-01 existing merger and tests; fresh reviewer found no simpler shape — taken
- shared validation and existing input paths — taken
- existing caller verification and raw-candidate replay — taken

## Questions asked
① — what — 以上就是這次要完成的範圍，對嗎？
① — consequence — 同意依此只再做一次本機修補與錄製資料重播嗎？ 此階段不增加外部呼叫。

## Risks
1. Historical recovery is not optimizer correctness; REQ-1 offline fixtures validate orchestration without claiming paid-provider or live-host behavior.
2. Existing JSONL remains read only. Neutral viewing files and reports are new artifacts, not migrations; REQ-3/4 tests check preservation.
3. REQ-5 text assertions cannot alone establish agent behavior; independent realistic execution must exercise voting, deferral, extraction accounting and audit evidence separation before closing acceptance.
4. Unknown model/effort uses the dispatch resolver's atomic inheritance fallback; no exact model identity or cross-vendor evidence is fabricated.
5. GitHub publication remains blocked pending explicit destination/content approval; merge remains separate. One additionally authorized Claude review completed; no repeat outside execution is authorized. Its findings are inputs to local correction, not a passing verdict on the corrected tree.
6. Round 1 found five defect classes and an evidence gap; the consumer sweep also found entry-only examples. Fix together, repeat package/probe checks, resume same reviewers. Independent acceptance re-tests affected rows with omitted-output-criterion and skipped-procedure-gate cases; justify retained rows.
7. Additional review exposed real gaps in previously passing evidence. Preserve old results as historical, replace affected acceptance evidence, and use real command entries and the real evaluator. Requirements remain unchanged; these tasks correct their existing obligations.
8. User-confirmed Acceptance8–11 expand earlier scope; risk7 describes an earlier correction. Preserve W6-01/W6-02 count1, W7-02 count2 and historical three-candidate evidence. Fresh pre-build spec+adversarial review passed7aad3646; no accounting reset by rename.
9. Fresh host projects retain explicit model/effort and disclosed non-hard cost estimates. Re-test affected acceptance surfaces in full, including original obligations. No repeat outside code review or publication is authorized; risk5 still applies.
10. If the same class survives bounded attempts or evidence cannot choose a design, consult primary industry sources and mature implementations as user requested. Research resets no retry count and justifies no generic framework.
11. The0b54d256 large positive trial remains failed for incomplete walk-through. W7-05 adds the distinct caller completion precondition, not another semantic detector attempt. Refine the disputed timing oracle transparently; preserve W7-02 continuation counts and frozen corpus.
12. User approved two Claude host cases after disclosure of source/public examples/recorded replies, Anthropic transfer and combined US$2.50 estimated thresholds (not hard limits). Tests only; no additional outside review, installation, publication or merge.
13. User-confirmed2026-11-04: W8-01 owns caller verification, one local candidate/replay only. W7-02 stays exhausted; no review-counter reset, paid calls, installation or publication. Native replay is not fresh Claude validation.
14. Initial candidate f8a68658 completed four native replays and stopped with a named-field false negative. Preserve raw/subset proof and qualified packaging disagreement. The following renewed user instruction governs continuation; release remains blocked.
15. User requested「繼續迭代吧」: W8-01 continuation1 repairs action-only eligibility in SKILL/changelog. Keep all previous counters/failures; replay unchanged four-case inputs. No new task, mechanism, external model call or publication authority; no model escalation inferred from unknown profiles.
16. Source30d local completed trials retain genuine/schema conflicts and exclude exceptions. Preserve malformed first execution and successful same-task retry separately. Independent acceptance: nine works, two partly; fresh Claude workflow evidence still awaits separate execution approval.
17. User answered「同意」to the disclosed preflight and three Claude Code cases: first-party Sonnet5.5/medium, combined USD3.05 estimated thresholds, not hard cap. All four calls completed; no retry, further outside review, installation or publication is authorized by this batch.
18. Source30d real-host results contradict local semantic success: caller replay and larger workflow retain unsupported exception claims; control filters correctly. Preserve failures and W8-01 continuation1/W7-02 exhausted counts. Research informs a bounded next repair; no automatic model escalation or release verdict.
19. User permits five more same-task rounds with Claude Code review. Round1/5 is W8-01 continuation2; preserve older counters. Selected native gpt-6.1-sol/high overrides unknown-profile/default-budget stops; shared rules unchanged. No inferred upgrade or publication authority.
20. Replace broad caller prose with visible dispositions in existing notes/reply. Retain real-host RED; source-first judgment/execution must earn GREEN. No new Python/schema/agent, exception whitelist or prose-pin tests. Outside Sonnet5.5/high reviews require scoped consent/receipts.
21. Round1/5, global continuation2, fae804f5 fails first host replay despite49/715/191/5 checks. Preserve artifacts; stop remaining cases. Outside packet consultation completed, but missing fields prevent accepting its formal report; concrete anchors remain advisory and independently checked.
22. Round2/5 remains W8-01 continuation3. Correct cited-file/governing-source reading, delegation qualifications and original why-claim judgment, not substituted concerns. Replace prose, preserve definitions/raw payloads; no new mechanism. User extension overrides legacy resolver cap; record rejection without resetting counters.
23. Round2 sourcef00 fails medium-effort replay after715/191/5 checks. Round3/5 holds source fixed and tests Sonnet5.5/high; no implementation redispatch or added product complexity. Preserve both profile results. Early stop expensive cases after failure; no source-only claim of semantic success.
24. Round3/5 high effort filters Cowork but removes named-field claim and retains packaging/fallback. Fresh source-first audit challenges classifications. Round4/5 compares first-party Opus5.5/high on unchanged source/data; no product rules, implementation dispatch or counter reset. Window ceiling stays five.
25. Round4 Opus retains schema and excludes Cowork but retains compatible fallback. Round5/5, global implementation continuation4, requires a supported incompatible action scenario after qualifications, separately preserving factual/field contradictions. Replace existing criterion only; preserve all failures and stop after this final round.
26. Five rounds complete. Final ecb9ddb7 replay retains fallback low; outside consultation is inconclusive, not PASS. No sixth candidate/host retry. Finish acceptance/evidence only. Preserve packaging ambiguity, field findings, prior failures and closed budget.
27. User selected local decision-boundary redesign, maximum five cycles. W9-01 changes consumed data and unresolved outcomes; W8-01 remains failed/closed, not renamed. No new outside-model, installation, publication or merge authority. Record cycle counts and unmet semantic obligations.
28. Cycle2 batches the confirmed cwd omission with two bounded review cleanups. Preserve program mechanisms and prior counters. No extra runtime or outside call; update original entry/risk/test authorities only. Full mechanical checks repeat.
29. Cycle3 repairs cycle2's wrong-project regression, same W10-01 continuation1. Scope imports per command, keep project cwd, use existing absolute entries. Preserve counts and old failures. Verify actual offline backend location before same-reviewer fix verification; help is insufficient.
30. Cycle3 correctly preserves project context but actual HTML/holdout0 fails; retain that failure and failed Acceptance1/7. Cycle4 repairs the existing nullable-cohort consumer, not another command launcher. No new outside call, counter reset or release inference.
