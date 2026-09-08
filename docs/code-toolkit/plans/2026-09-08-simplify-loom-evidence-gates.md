# Plan: simplify Loom evidence gates

**Source brief**: docs/code-toolkit/specs/2026-09-08-simplify-loom-evidence-gates.md
**Total tasks**: 27
**Critical-path depth**: 5
**Execution order**: sequential
**Plan-document-reviewer verdict**: PENDING

## Task 1 — Declare publication-only paths
- **Description**: Add one failing manifest test, then declare the generated evidence path pattern.
- **Module**: `loom-code/contract/manifest.yaml`
- **Files touched**: `loom-code/contract/manifest.yaml`, `loom-code/scripts/test_contract_manifest.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/contract/manifest.yaml`
- **Acceptance**:
  - **RED**: `test_contract_manifest.py::test_manifest_declares_publication_only_paths`
  - **GREEN**: the manifest declares the repo-neutral generated-evidence path pattern.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: “manifest-declared publication-only paths.”

## Task 2 — Define the attestation template
- **Description**: Add one failing template test, then replace the manual ledger template with minimal generated fields.
- **Module**: `loom-code/contract/templates/attestation.json`
- **Files touched**: `loom-code/contract/templates/attestation.json`, `loom-code/scripts/test_review_json_template.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/contract/templates/review.json`
- **Acceptance**:
  - **RED**: `test_review_json_template.py::test_attestation_has_only_generated_evidence_fields`
  - **GREEN**: the template has digest, executions, verdicts, and findings but no rounds, dispatch, cost, or entry SHAs.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: “a generated `attestation.json` becomes the per-change verification record.”

## Task 3 — Ignore publication paths in content identity
- **Description**: Add one failing reuse test, then exclude manifest-declared paths from content identity.
- **Module**: `loom-code/scripts/loom_checker.py`
- **Files touched**: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_attestation.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/scripts/loom_checker.py`, `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/contract/manifest.yaml`
- **Acceptance**:
  - **RED**: `test_loom_attestation.py::test_functional_digest_ignores_declared_publication_paths`
  - **GREEN**: publication-only edits preserve identity and no hard-coded repository path controls exclusion.
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: “unchanged functional content reuses that attestation, while any functional mutation invalidates it.”

## Task 4 — Validate finalize inputs
- **Description**: Add one failing malformed-input test, then strictly parse reviewer and adversarial input files.
- **Module**: `loom-code/scripts/loom_checker.py`
- **Files touched**: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_attestation.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/contract/templates/attestation.json`
- **Acceptance**:
  - **RED**: `test_loom_attestation.py::test_finalize_rejects_malformed_or_nonpassing_inputs`
  - **GREEN**: invalid or non-passing required input produces no attestation.
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: “structured reviewer inputs.”

## Task 5 — Run and record functional verification
- **Description**: Add one failing execution test, then make finalize run each declared package/probe command once.
- **Module**: `loom-code/scripts/loom_checker.py`
- **Files touched**: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_attestation.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/scripts/loom_checker.py`
- **Acceptance**:
  - **RED**: `test_loom_attestation.py::test_finalize_runs_each_required_execution_once`
  - **GREEN**: every required command runs once and any failure prevents output.
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Brief item covered**: “generated from actual checker-owned executions.”

## Task 6 — Write the attestation atomically
- **Description**: Add one failing atomic-output test, then emit deterministic JSON bound to the current digest.
- **Module**: `loom-code/scripts/loom_checker.py`
- **Files touched**: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_attestation.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/contract/templates/attestation.json`
- **Acceptance**:
  - **RED**: `test_loom_attestation.py::test_finalize_writes_matching_attestation_atomically`
  - **GREEN**: successful finalization atomically writes deterministic matching evidence.
- **Dependencies**: Task 5 completes first
- **Independent**: false
- **Brief item covered**: “automatically generated attestation.”

## Task 7 — Validate rather than replay at push
- **Description**: Add one failing no-replay test, then make push accept matching evidence without verification subprocesses.
- **Module**: `loom-code/scripts/loom_checker.py`
- **Files touched**: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_attestation.py`, `loom-code/scripts/test_loom_checker_push.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/scripts/loom_checker.py`
- **Acceptance**:
  - **RED**: `test_loom_attestation.py::test_push_reuses_matching_attestation_without_subprocesses`
  - **GREEN**: push rejects stale/malformed evidence and accepts matching evidence without suite or probe execution.
- **Dependencies**: Task 6 completes first
- **Independent**: false
- **Brief item covered**: “publication gate ... never reruns functional verification.”

## Task 8 — Delete the review-only rule
- **Description**: Add one failing inventory test, then remove `push.review-only-head`.
- **Module**: `loom-code/scripts/loom_checker.py`
- **Files touched**: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_checker_cli.py`, `docs/loom/evidence/mechanisms.yaml`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/docs/loom/evidence/mechanisms.yaml`
- **Acceptance**:
  - **RED**: `test_loom_checker_cli.py::test_review_only_head_rule_is_not_listed`
  - **GREEN**: the rule ID, implementation, and mechanism entry are absent.
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: “delete the review-only commit, exact-SHA, dispatch-accounting, append-only-round, and unconditional replay mechanisms.”

## Task 9 — Retire the checker copy
- **Description**: Add one failing setup test, then remove the worktree-local checker-copy prerequisite.
- **Module**: `loom-code/scripts/codex_scaffold.py`
- **Files touched**: `loom-code/scripts/codex_scaffold.py`, `loom-code/scripts/loom_record_fire.py`, `loom-code/scripts/test_codex_scaffold.py`, `loom-code/scripts/test_codex_trust_station_text.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/hooks/hooks.json`
- **Acceptance**:
  - **RED**: `test_codex_scaffold.py::test_installed_hook_needs_no_checker_copy`
  - **GREEN**: Loom setup relies on the installed plugin hook and creates no checker copy.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: “Per-worktree Loom checker scaffolding and its hook-firing ledger ... obsolete.”

## Task 10 — Skip privacy judge for public identifiers
- **Description**: Add one failing public-identifier test, then specify deterministic non-escalation.
- **Module**: `loom-workflow/skills/git-memory/protocols/privacy-judge-spec.md`
- **Files touched**: `loom-workflow/skills/git-memory/protocols/privacy-judge-spec.md`, `loom-workflow/skills/git-memory/scripts/test_loom_delegation.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-workflow/skills/git-memory/protocols/privacy-judge-spec.md`
- **Acceptance**:
  - **RED**: `test_loom_delegation.py::test_public_identifiers_do_not_dispatch_privacy_judge`
  - **GREEN**: public repo, PR, Task, and vendor identifiers explicitly skip the judge.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: “invokes the semantic privacy judge only for ambiguous private-party text.”

## Task 11 — Add commit-carrier privacy bypass
- **Description**: Add one failing commit-protocol test, then require a semantic false-positive audit reason.
- **Module**: `loom-workflow/skills/git-memory`
- **Files touched**: `loom-workflow/skills/git-memory/SKILL.md`, `loom-workflow/skills/git-memory/protocols/compose-commit.md`, `loom-workflow/skills/git-memory/protocols/compose-pr.md`, `loom-workflow/skills/git-memory/scripts/test_loom_delegation.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-workflow/skills/git-memory/protocols/compose-commit.md`
- **Acceptance**:
  - **RED**: `test_loom_delegation.py::test_commit_privacy_bypass_requires_reason`
  - **GREEN**: commit text proceeds on semantic false positives only with a reason; secret findings still block.
- **Dependencies**: Task 10 completes first
- **Independent**: false
- **Brief item covered**: “an explicit reasoned bypass is auditable.”

## Task 12 — Rewrite the Review station core
- **Description**: Add one failing station test, then replace ledger editing in the main Review skill with finalization.
- **Module**: `loom-code/skills/review/SKILL.md`
- **Files touched**: `loom-code/skills/review/SKILL.md`, `loom-code/scripts/test_review_station_text.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/skills/review/SKILL.md`
- **Acceptance**:
  - **RED**: `test_review_station_text.py::test_review_finalizes_generated_attestation_once`
  - **GREEN**: the main Review skill uses one closing review and finalize command without ledger editing.
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: “generated `attestation.json`.”

## Task 13 — Rewrite Ship around fast publication
- **Description**: Add one failing station test, then remove checkpoint, nit-confirmation, and replay instructions.
- **Module**: `loom-code/skills/ship/SKILL.md`
- **Files touched**: `loom-code/skills/ship/SKILL.md`, `loom-code/scripts/test_ship_station_text.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/skills/ship/SKILL.md`
- **Acceptance**:
  - **RED**: `test_ship_station_text.py::test_ship_uses_matching_attestation_and_fast_gate`
  - **GREEN**: Ship uses matching evidence and contains no old close-out ceremony.
- **Dependencies**: Task 12 completes first
- **Independent**: false
- **Brief item covered**: “publication edits loop only through the fast gate.”

## Task 14 — Align the Build station
- **Description**: Add one failing station test, then replace Build's review-ledger references.
- **Module**: `loom-code/skills`
- **Files touched**: `loom-code/skills/build/SKILL.md`, `loom-code/scripts/test_build_station_text.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/skills/write-plan/SKILL.md`
- **Acceptance**:
  - **RED**: `test_build_station_text.py::test_build_defers_generated_attestation_to_review`
  - **GREEN**: Build records no dispatch ledger and hands completed content to Review.
- **Dependencies**: Task 12 completes first
- **Independent**: false
- **Brief item covered**: “one repo-neutral contract.”

## Task 15 — Synchronize plugin version
- **Description**: Add one failing version assertion, then update the three plugin manifest surfaces.
- **Module**: `loom-code public contract`
- **Files touched**: `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `loom-code/scripts/test_sync_codex_manifest.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/README.md`
- **Acceptance**:
  - **RED**: `test_sync_codex_manifest.py::test_loom_code_version_is_synchronized`
  - **GREEN**: all plugin manifests expose one incremented version.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: the complete Smallest End State is the supported public contract.

## Task 16 — Run the full package suite once
- **Description**: Run the declared package command once and retain its result for finalization.
- **Module**: `integration verification`
- **Files touched**: none
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/docs/loom/intent/2026-09-08-simplify-loom-evidence-gates.md`
- **Acceptance**:
  - **RED**: the package command reports any failing test.
  - **GREEN**: the declared full package command exits zero exactly once during close-out.
- **Dependencies**: Task 15 completes first
- **Independent**: false
- **Brief item covered**: “one end-to-end dogfood run of this change” and “this migration uses the new flow.”

## Task 17 — Invalidate digest on functional mutation
- **Description**: Add one failing mutation test, then make every non-excluded tree mutation change the digest.
- **Module**: `loom-code/scripts/loom_checker.py`
- **Files touched**: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_attestation.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/scripts/loom_checker.py`
- **Acceptance**:
  - **RED**: `test_loom_attestation.py::test_functional_mutation_invalidates_digest`
  - **GREEN**: blob, path, mode, and undeclared evidence mutations change the digest or fail closed.
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Brief item covered**: “any functional mutation invalidates it.”

## Task 18 — Reject forged attestations
- **Description**: Add one failing forgery test, then validate checker-owned command identity and evidence structure.
- **Module**: `loom-code/scripts/loom_checker.py`
- **Files touched**: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_attestation.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/scripts/loom_checker.py`
- **Acceptance**:
  - **RED**: `test_loom_attestation.py::test_well_formed_forged_attestation_fails_closed`
  - **GREEN**: a structurally valid record with invented execution identity is rejected.
- **Dependencies**: Task 6 completes first
- **Independent**: false
- **Brief item covered**: “forgery ... fail closed.”

## Task 19 — Delete remaining ledger rule families
- **Description**: Add one failing inventory test, then remove exact-SHA, dispatch, append-only, and replay rule families.
- **Module**: `loom-code/scripts/loom_checker.py`
- **Files touched**: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_checker_cli.py`, `docs/loom/evidence/mechanisms.yaml`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/docs/loom/evidence/mechanisms.yaml`
- **Acceptance**:
  - **RED**: `test_loom_checker_cli.py::test_remaining_ledger_rule_families_are_not_listed`
  - **GREEN**: the obsolete rule IDs, calls, and mechanism entries are absent.
- **Dependencies**: Task 8 completes first
- **Independent**: false
- **Brief item covered**: “exact-SHA, dispatch-accounting, append-only-round, and unconditional replay mechanisms.”

## Task 20 — Retire the hook-firing ledger
- **Description**: Add one failing setup test, then remove Loom's firing-ledger writer and prerequisite text.
- **Module**: `loom-code/scripts/loom_record_fire.py`
- **Files touched**: `loom-code/scripts/loom_record_fire.py`, `loom-code/scripts/test_codex_trust_station_text.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/scripts/loom_record_fire.py`
- **Acceptance**:
  - **RED**: `test_codex_trust_station_text.py::test_loom_has_no_hook_firing_ledger_prerequisite`
  - **GREEN**: no live Loom setup path writes or requires `.loom-hook-fired`.
- **Dependencies**: Task 9 completes first
- **Independent**: false
- **Brief item covered**: “hook-firing ledger ... obsolete.”

## Task 21 — Escalate ambiguous private-party text
- **Description**: Add one failing ambiguity test, then dispatch the semantic judge only for that classification.
- **Module**: `loom-workflow/skills/git-memory/protocols/privacy-judge-spec.md`
- **Files touched**: `loom-workflow/skills/git-memory/protocols/privacy-judge-spec.md`, `loom-workflow/skills/git-memory/scripts/test_loom_delegation.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-workflow/skills/git-memory/protocols/privacy-judge-spec.md`
- **Acceptance**:
  - **RED**: `test_loom_delegation.py::test_ambiguous_private_party_text_dispatches_judge`
  - **GREEN**: ambiguous identifying text dispatches; malformed judge output blocks only that carrier.
- **Dependencies**: Task 10 completes first
- **Independent**: false
- **Brief item covered**: “ambiguous private-party text does.”

## Task 22 — Add PR-carrier privacy bypass
- **Description**: Add one failing PR-protocol test, then require the same semantic false-positive audit reason.
- **Module**: `loom-workflow/skills/git-memory/protocols/compose-pr.md`
- **Files touched**: `loom-workflow/skills/git-memory/protocols/compose-pr.md`, `loom-workflow/skills/git-memory/scripts/test_loom_delegation.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-workflow/skills/git-memory/protocols/compose-pr.md`
- **Acceptance**:
  - **RED**: `test_loom_delegation.py::test_pr_privacy_bypass_requires_reason`
  - **GREEN**: PR text follows the same audited bypass and cannot bypass secret findings.
- **Dependencies**: Task 11 completes first
- **Independent**: false
- **Brief item covered**: “an explicit reasoned bypass is auditable.”

## Task 23 — Align Review reference pages
- **Description**: Add one failing cross-reference test, then remove ledger and replay instructions from Review references.
- **Module**: `loom-code/skills/review/references`
- **Files touched**: `loom-code/skills/review/references/adversarial.md`, `loom-code/skills/review/references/fix-rounds.md`, `loom-code/skills/review/references/lane-switch.md`, `loom-code/scripts/test_review_station_text.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/skills/review/references/adversarial.md`
- **Acceptance**:
  - **RED**: `test_review_station_text.py::test_review_references_use_generated_evidence`
  - **GREEN**: live Review references describe generated inputs and no old ledger ceremony.
- **Dependencies**: Task 12 completes first
- **Independent**: false
- **Brief item covered**: “manual ledger updates ... obsolete.”

## Task 24 — Align Write Plan and Maintain
- **Description**: Add one failing summary test, then replace their obsolete artifact and push-rule names.
- **Module**: `loom-code/skills`
- **Files touched**: `loom-code/skills/write-plan/SKILL.md`, `loom-code/skills/maintain/SKILL.md`, `loom-code/scripts/test_station_summary_table.py`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/skills/write-plan/SKILL.md`
- **Acceptance**:
  - **RED**: `test_station_summary_table.py::test_write_plan_and_maintain_name_attestation_contract`
  - **GREEN**: both station summaries name generated evidence and the fast publication gate.
- **Dependencies**: Task 12 completes first
- **Independent**: false
- **Brief item covered**: “one repo-neutral contract.”

## Task 25 — Synchronize live public prose
- **Description**: Add one failing citation/contract assertion, then update README, TECH-SPEC, changelog, and generated instructions.
- **Module**: `loom-code public prose`
- **Files touched**: `AGENTS.md`, `claude/.claude/CLAUDE.md`, `loom-code/README.md`, `loom-code/TECH-SPEC.md`, `loom-code/CHANGELOG.md`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/README.md`
- **Acceptance**:
  - **RED**: `test_station_summary_table.py::test_public_prose_names_one_attestation_flow`
  - **GREEN**: all live prose describes one generated-evidence mechanism and no old flow.
- **Dependencies**: Task 15 completes first
- **Independent**: false
- **Brief item covered**: the complete Smallest End State is the public contract.

## Task 26 — Obtain independent branch review
- **Description**: Give the cumulative diff and acceptance criteria to independent reviewers and resolve functional findings.
- **Module**: `integration review`
- **Files touched**: none
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/docs/loom/intent/2026-09-08-simplify-loom-evidence-gates.md`
- **Acceptance**:
  - **RED**: any reviewer reports an unresolved functional or security defect.
  - **GREEN**: required independent reviewers return passing verdicts with no open functional findings.
- **Dependencies**: Task 25 completes first
- **Independent**: false
- **Brief item covered**: “independent CI remains the external trust boundary” and preserved reviewer quality.

## Task 27 — Finalize and prove no-replay reuse
- **Description**: Generate this change's attestation, make one publication-only edit, and verify push starts no functional subprocess.
- **Module**: `integration verification`
- **Files touched**: `docs/loom/2026-09-08-simplify-loom-evidence-gates/attestation.json`
- **Context paths**: `/Users/kouko/GitHub/monkey-skills/.worktrees/2026-09-08-simplify-loom-evidence-gates/loom-code/scripts/loom_checker.py`
- **Acceptance**:
  - **RED**: push rejects before a matching generated attestation exists.
  - **GREEN**: finalization writes matching evidence and publication-only reuse executes no suite or probe.
- **Dependencies**: Task 26 completes first
- **Independent**: false
- **Brief item covered**: “one end-to-end dogfood run” and “this migration uses the new flow.”

## Notes

- This bootstrap does not use old `review.json`, checkpoint, exact-SHA, unconditional privacy-judge, or old push-gate ceremony as a prerequisite.
- Sequential execution resolves shared-file ordering; dependencies record behavior prerequisites and have maximum depth five.
- Frozen historical Loom records remain untouched.
