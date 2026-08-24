# Plan: Review binding remediation

Goal: make every reviewer consume immutable, correctly scoped evidence, and make
the two host confirmation paths use the same convergence meaning.

Stage: verification:integration

| Step | Status | Depends on |
|---|---|---|
| T1 | pending | — |
| T2 | pending | T1 |
| T3 | pending | — |
| T4 | pending | T1 |
| T5 | pending | T4 |
| T6 | pending | T2, T3, T5 |
| T7 | pending | T6 |

## Task 1 — Require repo-relative paths for immutable reviewer reads

- Brief item covered: BI-1
- Status: claimed(@root)

Description:

- Define the reviewer input contract so every artifact path is repo-relative
  before it is read from the reviewed commit SHA.

RED:

- Add `test_reviewer_artifact_paths_are_repo_relative_before_sha_reads` to
  `loom-code/scripts/test_reviewer_discipline.py`; it fails while contracts
  permit absolute paths or mutable fallback reads.

GREEN:

- Update the shared reviewer discipline reference plus the code, docs, spec,
  and quality reviewer prompts to pass only repo-relative artifact paths to
  `git show <reviewed-sha>:<path>`.

Files:

- `loom-code/scripts/_reviewer-discipline.md`
- `loom-code/agents/code-reviewer.md`
- `loom-code/agents/docs-reviewer.md`
- `loom-code/agents/spec-reviewer.md`
- `loom-code/agents/code-quality-reviewer.md`
- `loom-code/scripts/test_reviewer_discipline.py`

Acceptance criteria:

- The named test passes and each reviewer prompt prohibits absolute artifact
  paths and mutable worktree fallback for reviewed evidence.

## Task 2 — Derive code-review evidence from the reviewed SHA

- Brief item covered: BI-5
- Status: claimed(@root)

Description:

- Keep code-reviewer policy, principles, and simplification evidence inside
  the reviewed snapshot rather than reading the caller’s current worktree.

RED:

- Add `test_code_reviewer_principles_and_simplifications_use_reviewed_sha` to
  `loom-code/scripts/test_reviewer_discipline.py`; it fails while D8 or D9
  permits mutable path discovery or `grep` over the worktree.

GREEN:

- Update `code-reviewer.md` so D8 and D9 discover and read their evidence
  using reviewed-SHA Git commands and repo-relative paths only.

Files:

- `loom-code/agents/code-reviewer.md`
- `loom-code/scripts/test_reviewer_discipline.py`

Acceptance criteria:

- The named test passes and D8/D9 have no mutable-filesystem evidence command.

## Task 3 — Scope per-task reviewers to their declared task files

- Brief item covered: BI-2
- Status: claimed(@root)

Description:

- Make the parallel-development reviewer prompt inspect the task packet’s
  declared files, not the entire branch change population.

RED:

- Add `test_sdd_per_task_reviewer_scope_uses_declared_task_files` to
  `loom-code/scripts/test_subagent_driven_development_skill.py`; it fails while
  the prompt makes per-task review use `review_scope.py` as its only scope.

GREEN:

- Update the SDD process to pass declared task files as the reviewer scope;
  retain full-branch scope only for the whole-branch review station.

Files:

- `loom-code/skills/subagent-driven-development/SKILL.md`
- `loom-code/scripts/test_subagent_driven_development_skill.py`

Acceptance criteria:

- The named test passes and the prompt distinguishes task-scoped and
  whole-branch review populations.

## Task 4 — Define one portable convergence contract

- Brief item covered: BI-3
- Status: claimed(@root)

Description:

- State one host-neutral confirmation packet and verdict mapping, including
  original findings and delta evidence for a fresh confirmation reviewer.

RED:

- Add `test_codex_confirmation_packet_is_consistent_with_binding_convergence_contract`
  to `loom-code/scripts/test_requesting_docs_review_skill.py`; it fails while the
  docs skill and reviewer prompt prescribe incompatible confirmation flows.

GREEN:

- Add a binding convergence reference and make the docs-review skill plus
  docs-reviewer prompt require that packet and its verdict mapping.

Files:

- `loom-code/skills/requesting-docs-review/SKILL.md`
- `loom-code/skills/requesting-docs-review/references/convergence-contract.md`
- `loom-code/agents/docs-reviewer.md`
- `loom-code/scripts/test_requesting_docs_review_skill.py`

Acceptance criteria:

- The named test passes and both host paths have identical inputs and outcome
  semantics.

## Task 5 — Correct Codex’s reviewer-agent path mapping

- Brief item covered: BI-3
- Status: claimed(@root)

Description:

- Point Codex instructions at the public loom-code reviewer prompt location
  so isolated installs load the same reviewed contracts.

RED:

- Add `test_codex_post_fix_maps_to_public_reviewer_agent_paths` to
  `loom-code/scripts/test_codex_adapter_contract.py`; it fails while the adapter
  points to a nonexistent skill-local `agents/` directory.

GREEN:

- Update `codex-tools.md` to reference `loom-code/agents/*.md` and the
  convergence contract defined in T4.

Files:

- `loom-code/skills/using-loom-code/references/codex-tools.md`
- `loom-code/scripts/test_codex_adapter_contract.py`

Acceptance criteria:

- The named test passes and every reviewer-agent path exists in an isolated
  loom-code installation.

## Task 6 — Align simplification-marker policy with the ledger

- Brief item covered: BI-4
- Status: claimed(@root)

Description:

- Permit a valid nonempty simplification ledger to mint its marker while
  retaining the existing invalid-ledger blocking behavior.

RED:

- Add `test_valid_nonempty_simplification_ledger_mints_marker` to
  `loom-code/scripts/test_review_scope_and_loop.py`; it fails while the review
  skill limits marker minting to an empty ledger.
- Add `review-pass` cases for valid and malformed nonempty ledgers; they fail
  while the marker writer ignores ledger evidence.

GREEN:

- Update the whole-branch review skill to accept valid, nonempty ledger
  entries under rules that the marker gate independently validates.
- Refuse marker minting when a nonempty ledger has missing fields, is marked
  invalid, or reports a failed immutable snapshot read.

Files:

- `loom-code/skills/requesting-code-review/SKILL.md`
- `loom-code/scripts/test_review_scope_and_loop.py`
- `loom-code/scripts/test_review_scope_stations.py`
- `loom-code/scripts/loom_gate_markers.py`
- `loom-code/scripts/test_loom_gate_markers.py`

Acceptance criteria:

- The named test passes and valid ledger evidence is sufficient to mint the
  simplification marker.
- The marker writer itself refuses malformed ledger evidence, including a
  failed immutable snapshot read.

## Task 7 — Retire obsolete mutable Claude sandbox instructions

- Brief item covered: BI-6
- Status: claimed(@root)

Description:

- Remove superseded sandbox and config-directory flags from active Part 4
  implementation records now that the fixed test profile owns that behavior.

RED:

- Add `test_part4_runner_contract_has_no_removed_claude_sandbox_flags` to
  `loom-code/scripts/test_live_host_review_gate.py`; it fails while the
  active Part 4 records document removed runner flags.

GREEN:

- Update the Part 4 brief and plan to name the fixed `~/.claude-test` profile
  and the supported runner invocation without obsolete flags.

Files:

- `loom-code/scripts/test_live_host_review_gate.py`
- `docs/loom/specs/2026-08-24-cross-host-review-gate-hardening-part-4.md`
- `docs/loom/plans/2026-08-24-cross-host-review-gate-hardening-part-4.md`

Acceptance criteria:

- The named test passes and active runner documentation contains no removed
  mutable-sandbox or config-directory flag.

## Open Questions

N/A — no unresolved question: the user explicitly authorized remediation of the whole-branch review findings on 2026-08-24.

## Notes

- Re-run the live-host gate after any runner or host-contract change.
- Whole-branch docs and code review must run again before branch completion.
