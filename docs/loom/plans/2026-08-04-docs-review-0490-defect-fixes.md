# Plan: docs-review 0.49.0 adjudicated defect fixes

**Source brief**: docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md
**Total tasks**: 12
**Critical-path depth**: 4 (T1→T2→T11→T12; all other chains shorter)
**Execution order**: sequential (most tasks share `requesting-docs-review/SKILL.md`; no parallel-eligible pair)
**Plan-document-reviewer verdict**: PASS (2026-08-04, round 3; rounds 1-2 NEEDS_REVISION fixed — Module single-path, RED test names, obligation tasks T11/T12)

## Population data (recon, this session — line numbers current at branch point f61837ed; re-locate by quoted text)

- Claim-copy sweeps already run for all 11 target phrases (`scripts/claim_copy_sweep.py`, 2777 .md files). Operative copies are confined to: the two contract files, `requesting-code-review/SKILL.md`, `requesting-code-review/references/gate-markers-spec.md:94`, the `docs/loom/` tree (spec/backlog/handoff/memory/audit), and one cross-plugin sibling. **Named leaks**: the `.py` module docstring is outside the .md sweep (`loom_gate_markers.py:57` carries the third "never biased" copy); synonyms stay invisible to any sweep.
- **No README / i18n / router-card / loom-pipeline surface quotes any edited rule** (verified negative). No retro-sweep tasks needed there.
- **Zero existing tests pin** `prior_findings_check`, `reviewed_sha`, `out_of_scope`, `read_context_findings`, `Round scope`, `unbounded`, `delta-scoped` (verified by grep over `loom-code/scripts/*.py`). All RED tests for D1/D2/D4/D5 are new.
- Pinned needles that MUST survive edits (existing tests, else update the test in the same task): `test_requesting_docs_review_skill.py::test_convergence_directives` needles incl. `findings verbatim`, `resurfaces after being fix-verified`, `re-raising a closed finding in new words is forbidden`; `_convergence_window` = banner→first numbered step; `test_window_precision` boundary assertions; `test_docs_reviewer_agent.py` output-contract tests pin `class: instruction | evidence` literally; `test_docs_review_mode.py` polarity guard pins `worse of the two arm verdicts` (Step 1 — a DIFFERENT rule from Step 3's per-dimension score; do not touch).
- **Same-name trap**: `requesting-docs-review/SKILL.md:77` "resolve it yourself" belongs to the Step 1 scope resolver (pinned by `test_review_scope_docs_station.py`) — NOT the reviewed_sha fallback. D4 touches only `agents/docs-reviewer.md`.
- **Word caps** (`check-skill-structure.py` CHK-SKL-010, hard 4500): `requesting-code-review/SKILL.md` = 4496 (**4 words headroom**); `requesting-docs-review/SKILL.md` = 4189 (311 headroom).
- **Version-bump quartet** (stable across #645/#646): `loom-code/.claude-plugin/plugin.json` + `loom-code/.codex-plugin/plugin.json` + `loom-code/CHANGELOG.md` + rewrite `test_docs_review_blocking_class.py::test_plugin_version_and_changelog_at_0_49_0`. `sync_codex_manifests.py --check` enforces the mirror. Editing the `.py` docstring alone already demands a bump (`check_version_bump.py` covers `<plugin>/scripts/**` production files).
- Cross-plugin sibling: `copywriting-toolkit/agents/copywriter-evaluator.md:102-103` carries the same `prior_findings_check` template (own test pins `restated verbatim`). Out of scope; divergence is deliberate and noted in the PR body.
- The brief (`docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md`) and the gitignored HANDOFF quote every defective phrase BY DESIGN (they document the defects) — never "fix" them.

## Task 1 — D1: prior-findings carrier becomes every-round-after-round-1

- **Description**: Generalize the prior-findings carrier from "round 2 only" to every round after round 1, in both contract files: the round-2 handoff sentence becomes a round-N handoff (round N's packet carries round N-1's surviving findings verbatim), the verdict-schema comment `# round 2 only; omit on round 1` becomes `# every round after round 1; omit on round 1`, docs-reviewer's input section `### Prior-round findings (round 2 only)` and output-template comment likewise, and Directive 1 option (a) states that the authorized verification round receives the surviving findings it verifies. This makes `resurfaced` reachable at round ≥3 and Directive 3's oscillation stop executable.
- **Module**: loom-code/skills/requesting-docs-review/SKILL.md (the agent contract mirrors it — the arc's recurring defect is editing one surface without the other, so this task edits both; see Files touched)
- **Files touched**: loom-code/skills/requesting-docs-review/SKILL.md, loom-code/agents/docs-reviewer.md, loom-code/scripts/test_requesting_docs_review_skill.py, loom-code/scripts/test_docs_reviewer_agent.py
- **Context paths**:
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§D1)
  - loom-code/scripts/test_requesting_docs_review_skill.py (window helpers; needles that must survive)
- **Acceptance**:
  - **RED**: new `test_requesting_docs_review_skill.py::test_prior_findings_carrier_every_later_round` (window-scoped: verdict-structure fence + Directive 2) and new `test_docs_reviewer_agent.py::test_prior_findings_carrier_every_later_round` (input + output contract windows) assert the round-N wording and assert `round 2 only` is absent from those windows — both fail against current content (prove RED against `git show HEAD:<file>` per memory `grep-tests-scope-to-measured-neighborhood`)
  - **GREEN**: both new tests pass; existing `test_convergence_directives` needles (`findings verbatim`, `resurfaces after being fix-verified`) still pass; full file-pair test modules pass
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: "D1 — prior-findings carrier generalized to every round after round 1 (was: 'round 2 only')"

## Task 2 — I2: restatement in prior_findings_check becomes a one-line scalar

- **Description**: In the same template blocks Task 1 edits, change the restatement instruction so a prior finding is restated as a one-line scalar (`finding: <one-line summary>`), never as the original `- severity:` block — because `_FINDING_RE` matches `- severity:` at any indent and a verbatim block lands in the origin ledger a second time as a later-round finding. Keep the fix-verification duty (quote current text) intact.
- **Module**: loom-code/skills/requesting-docs-review/SKILL.md (agent contract mirrored in the same task; see Files touched)
- **Files touched**: loom-code/skills/requesting-docs-review/SKILL.md, loom-code/agents/docs-reviewer.md, loom-code/scripts/test_requesting_docs_review_skill.py, loom-code/scripts/test_docs_reviewer_agent.py
- **Context paths**:
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§I2)
  - loom-code/scripts/loom_gate_markers.py (`_FINDING_RE` — the regex the wording must not feed)
- **Acceptance**:
  - **RED**: new `test_requesting_docs_review_skill.py::test_prior_findings_restated_as_scalar` and `test_docs_reviewer_agent.py::test_prior_findings_restated_as_scalar`, each window-scoped to its file's `prior_findings_check:` fence, asserting the one-line-scalar instruction present and no `- severity:` line inside the fence — fail against current "restated verbatim" wording (prove RED via `git show HEAD:<file>`)
  - **GREEN**: new tests pass; `copywriting-toolkit` suite untouched and green (its own `restated verbatim` pin is a different plugin's contract — do not edit it)
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: "I2 — restatement in prior_findings_check must not be ledger-parseable"

## Task 3 — D4: reviewed_sha fallback goes fail-closed; input template gets the HEAD-sha slot

- **Description**: In `agents/docs-reviewer.md` only: (a) replace the output-contract fallback "if the packet did not state one, resolve it yourself" with fail-closed reporting — `reviewed_sha: unresolved` plus one sentence noting the next round then runs unbounded per the skill's range rule; (b) add the missing `HEAD sha` slot to the input-contract template (the skill's Step 3 requires the packet to state it; the template has no field). Do NOT touch `requesting-docs-review/SKILL.md:77`'s "resolve it yourself" — that is the Step 1 scope resolver's rule (same words, different mechanism, pinned by `test_review_scope_docs_station.py`).
- **Module**: loom-code/agents/docs-reviewer.md
- **Files touched**: loom-code/agents/docs-reviewer.md, loom-code/scripts/test_docs_reviewer_agent.py
- **Context paths**:
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§D4)
  - loom-code/skills/requesting-docs-review/SKILL.md (Step 3 packet requirement + Directive 2 unbounded rule — read-only context)
- **Acceptance**:
  - **RED**: new `test_docs_reviewer_agent.py::test_reviewed_sha_fail_closed_no_self_resolve` asserting (window-scoped to the output contract) `unresolved` wording present and `resolve it yourself` absent, and (input-contract window) a HEAD-sha slot present — fails against current content
  - **GREEN**: new test passes; `test_review_scope_docs_station.py` untouched and green (proves the Step 1 twin survived)
- **Dependencies**: none (shares docs-reviewer.md with Tasks 1-2 — execution stays sequential in listed order, but there is no semantic dependency)
- **Independent**: false
- **Brief item covered**: "D4 — reviewed_sha fallback goes fail-closed; input template gets the field"

## Task 4 — D2: the ledger-recording contract fixed at all three copies

- **Description**: State invocation semantics correctly everywhere the ledger contract is described: (a) `requesting-docs-review/SKILL.md` Directive 2's "it holds only the last **minted** round" → the ledger appends on every `review-pass` INVOCATION (including refuse paths), and an entry can still be stale because rounds that never invoke the CLI (mixed-branch docs rounds; failing rounds nobody minted) append nothing; (b) `loom_gate_markers.py` module docstring's unconditional "so the sample of recorded findings is never biased by which rounds happened to pass" → conditional capability ("unbiased only if every round invokes it; shipped orchestration invokes on mint attempts, so the recorded sample is invocation-skewed"); (c) the same claim's prose mirror in `requesting-code-review/references/gate-markers-spec.md`; (d) the backlog entry `2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session.md`'s "records mint attempts" wording → invocation semantics (exit-4 retries append again; mixed-branch rounds never appear).
- **Module**: loom-code/scripts/loom_gate_markers.py (its two prose mirrors and the backlog record are corrected in the same task; see Files touched)
- **Files touched**: loom-code/skills/requesting-docs-review/SKILL.md, loom-code/scripts/loom_gate_markers.py, loom-code/skills/requesting-code-review/references/gate-markers-spec.md, docs/loom/backlog/2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session.md, loom-code/scripts/test_loom_gate_markers.py, loom-code/scripts/test_requesting_docs_review_skill.py
- **Context paths**:
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§D2)
  - loom-code/scripts/loom_gate_markers.py (`_record_origin_ledger_round` call site before exit-3/4 returns — the code truth the prose must match)
- **Acceptance**:
  - **RED**: new `test_loom_gate_markers.py::test_module_docstring_states_conditional_ledger_bias` asserting the docstring names the invocation condition and no longer carries the unconditional "never biased" claim; new `test_requesting_docs_review_skill.py::test_directive2_states_invocation_semantics` asserting Directive 2 states invocation semantics ("minted round" claim absent from the Directive-2 window) — both fail against current content
  - **GREEN**: both pass; docstring edit changes no behavior (`test_loom_gate_markers.py` behavioral suite still green); `python3 scripts/backlog_index.py --check` still OK (entry body edit, title unchanged — if the title must change, regenerate with `--write`)
- **Dependencies**: none (shares SKILL.md with earlier tasks — execution sequential in listed order; no semantic dependency)
- **Independent**: false
- **Brief item covered**: "D2 — the ledger-recording contract told three ways; fix both lying sides"

## Task 5 — D3: retract "round accounting continues, it does not reset"

- **Description**: Rewrite the already-reviewed-branch bullet in `requesting-docs-review/SKILL.md` to the truth: round accounting is carried by the orchestrator within one session; across a session boundary nothing restores it and the count restarts — the 2-round cap then guards each session independently, which is weaker than continuous accounting; state that plainly instead of claiming continuity. Extend the existing backlog entry `2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session.md` to record that the round COUNT shares the sha's carrier gap (one entry, both facets — do not open a duplicate).
- **Module**: loom-code/skills/requesting-docs-review/SKILL.md
- **Files touched**: loom-code/skills/requesting-docs-review/SKILL.md, docs/loom/backlog/2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session.md, loom-code/scripts/test_requesting_docs_review_skill.py
- **Context paths**:
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§D3)
- **Acceptance**:
  - **RED**: new `test_requesting_docs_review_skill.py::test_round_accounting_is_session_scoped`, window-scoped to the already-reviewed-branch bullet, asserting the session-scoped wording present and `round accounting continues, it does not reset` absent — fails against current content (prove RED via `git show HEAD:<file>`)
  - **GREEN**: test passes; `backlog_index.py --check` OK
- **Dependencies**: Task 4 completes first (shares SKILL.md and the backlog entry file)
- **Independent**: false
- **Brief item covered**: "D3 — retract 'round accounting continues, it does not reset'"

## Task 6 — D5: retract "deferred on the record" for out_of_scope; open the mechanism backlog entry

- **Description**: Fix the out_of_scope honesty in both contract files: `requesting-docs-review/SKILL.md` §out_of_scope prose ("deferred on the record") and the same claim inside its verdict fence, plus `agents/docs-reviewer.md`'s "recorded so it is not lost" → surfaced to the user with the verdict, persisted nowhere; deferral survives only if the user or orchestrator acts on it. Keep docs-reviewer's completeness counter-instruction ("a silently dropped observation is invisible…"). Open a NEW backlog entry proposing the persistence mechanism (a severity-less ledger block type riding the existing every-invocation append; note `validate_verdict_text` gaining a `reviewed_sha` check as a sibling candidate), then regenerate `docs/loom/BACKLOG.md` via `python3 scripts/backlog_index.py --write` (GENERATED file — never hand-edit).
- **Module**: loom-code/skills/requesting-docs-review/SKILL.md (agent contract mirrored + backlog entry opened in the same task; see Files touched)
- **Files touched**: loom-code/skills/requesting-docs-review/SKILL.md, loom-code/agents/docs-reviewer.md, docs/loom/backlog/2026-08-04-out-of-scope-deferrals-have-no-durable-record.md (new), docs/loom/BACKLOG.md (regenerated), loom-code/scripts/test_requesting_docs_review_skill.py, loom-code/scripts/test_docs_reviewer_agent.py
- **Context paths**:
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§D5)
  - docs/loom/backlog/README.md (entry format charter)
- **Acceptance**:
  - **RED**: new `test_requesting_docs_review_skill.py::test_out_of_scope_not_claimed_persisted` (two windows: the §out_of_scope prose paragraph and the verdict fence) asserting `deferred on the record` absent and the honest surfaced-not-persisted wording present; new `test_docs_reviewer_agent.py::test_out_of_scope_not_claimed_persisted` (output-contract window) asserting `recorded so it is not lost` absent and the honest wording present — both fail against current content (prove RED via `git show HEAD:<file>`)
  - **GREEN**: tests pass; `backlog_index.py --check` OK after `--write`
- **Dependencies**: none (shares SKILL.md with earlier tasks — execution sequential in listed order; no semantic dependency)
- **Independent**: false
- **Brief item covered**: "D5 — retract 'deferred on the record' for out_of_scope"

## Task 7 — I1: panel union recomputes dimension scores from the union

- **Description**: Close the verdict/dimension_scores contradiction in BOTH copies of the mixed-branch aggregation parenthetical: `requesting-docs-review/SKILL.md` Step 4 and `requesting-code-review/SKILL.md` Step 3 ("per-dimension score = the worse of the two arms' scores") → per-dimension score is re-derived by re-running the aggregation rule on the union's findings in that dimension (worse-of-arms understates when two arms contribute different findings to one dimension). CONSTRAINTS: `requesting-code-review/SKILL.md` has 4 words of headroom against the 4500 hard cap — the edit must be net ≤ +4 words there (trim in place if needed); do NOT touch Step 1's `worse of the two arm verdicts` (different rule, polarity-guard-pinned); do not introduce any of `test_docs_review_blocking_class.py`'s negative-pin phrases into requesting-code-review/SKILL.md.
- **Module**: loom-code/skills/requesting-docs-review/SKILL.md (the rule's source copy is corrected in the same task; see Files touched)
- **Files touched**: loom-code/skills/requesting-docs-review/SKILL.md, loom-code/skills/requesting-code-review/SKILL.md, loom-code/scripts/test_requesting_docs_review_skill.py, loom-code/scripts/test_docs_review_mode.py
- **Context paths**:
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§I1)
  - loom-code/scripts/test_requesting_docs_review_skill.py (`test_per_dimension_score_is_worse_of_two_arms`, `_assert_per_dimension_worse_score` — to be rewritten RED-first)
- **Acceptance**:
  - **RED**: rewrite `test_per_dimension_score_is_worse_of_two_arms` (and its helper) to assert union-recompute wording in both files — fails against current "worse of the two arms' scores" text
  - **GREEN**: rewritten tests pass; `test_docs_review_mode.py` Step 1 polarity guard untouched and green; `check-skill-structure.py` passes (word cap)
- **Dependencies**: none (shares requesting-docs-review/SKILL.md with earlier tasks — execution sequential in listed order; no semantic dependency)
- **Independent**: false
- **Brief item covered**: "I1 — panel union: recompute dimension_scores from the union"

## Task 8 — I3: the two unsourced figures leave the delta-scope rationale

- **Description**: Rewrite the delta-scope rationale sentence in `requesting-docs-review/SKILL.md` (currently "round 1's fixes were a broad rewrite … round 2's were four one-to-two-sentence edits and carried none") to carry only what the cited audit records — direction without magnitude (the audit records that round-2's delta-scoped arms re-found both control findings and that the misread-sampling correction killed the per-round design; it carries neither "broad rewrite" nor an edit count). The sentence sits inside `_convergence_window` — existing needles must survive.
- **Module**: loom-code/skills/requesting-docs-review/SKILL.md
- **Files touched**: loom-code/skills/requesting-docs-review/SKILL.md, loom-code/scripts/test_requesting_docs_review_skill.py
- **Context paths**:
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§I3)
  - docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md (what the audit actually carries — read before writing the replacement)
- **Acceptance**:
  - **RED**: new `test_requesting_docs_review_skill.py::test_delta_scope_rationale_carries_no_unsourced_magnitudes`, asserting `four one-to-two-sentence edits` and `broad rewrite` absent from `_convergence_window` — fails against current content (prove RED via `git show HEAD:<file>`)
  - **GREEN**: test passes; `test_convergence_directives` still green
- **Dependencies**: none (shares SKILL.md — execution sequential in listed order; no semantic dependency)
- **Independent**: false
- **Brief item covered**: "I3 — delete or source the two unsourced figures"

## Task 9 — I4: one honest sentence on the inherited threshold

- **Description**: Add exactly this sentence (verbatim) to `requesting-docs-review/SKILL.md` §Aggregation, after the thresholds statement: "These thresholds are inherited unexamined from `requesting-code-review`, where they sit on top of a passing test suite — no docs-specific evidence sets them; revisit if the docs arm's false-positive economics prove different." Keep the `instruction-class findings only` needle intact; no threshold change.
- **Module**: loom-code/skills/requesting-docs-review/SKILL.md
- **Files touched**: loom-code/skills/requesting-docs-review/SKILL.md, loom-code/scripts/test_requesting_docs_review_skill.py
- **Context paths**:
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§I4)
- **Acceptance**:
  - **RED**: new `test_requesting_docs_review_skill.py::test_threshold_provenance_sentence` asserting the literal `inherited unexamined` inside the `_heading_window("Aggregation rule")` window — fails against current content (prove RED via `git show HEAD:<file>`)
  - **GREEN**: test passes; `test_aggregation_instruction_class_only` still green
- **Dependencies**: none (shares SKILL.md — execution sequential in listed order; no semantic dependency)
- **Independent**: false
- **Brief item covered**: "I4 — one-sentence docs-specific threshold rationale"

## Task 10 — I5: judged-vs-defaulted class provenance marker

- **Description**: Allow the optional `(defaulted)` annotation on fail-closed class tags in both contract files: the finding schema's `class:` line may read `class: instruction (defaulted)` when the reviewer could not tell and fail-closed defaulted; include this sentence (verbatim) in both files' definitions: "A `(defaulted)` tag is treated exactly as `instruction` by the aggregation rule." Directive 1's option (c) guidance tells the user defaulted-only findings are the ones to scrutinize before choosing (c). CONSTRAINT: the literal needle `class: instruction | evidence` is pinned by `test_findings_carry_class_taxonomy` and `test_verdict_structure_prose_dimensions` — the annotation must be introduced without breaking that literal (annotate in an adjacent comment/sentence, or update the pinning tests in the same commit RED-first).
- **Module**: loom-code/skills/requesting-docs-review/SKILL.md (agent contract mirrored in the same task; see Files touched)
- **Files touched**: loom-code/skills/requesting-docs-review/SKILL.md, loom-code/agents/docs-reviewer.md, loom-code/scripts/test_requesting_docs_review_skill.py, loom-code/scripts/test_docs_reviewer_agent.py
- **Context paths**:
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§I5)
- **Acceptance**:
  - **RED**: new `test_requesting_docs_review_skill.py::test_class_default_provenance_marker` and `test_docs_reviewer_agent.py::test_class_default_provenance_marker`, each asserting the literals `(defaulted)` and `treated exactly as` within the verdict-structure / output-contract windows — fail against current content (prove RED via `git show HEAD:<file>`)
  - **GREEN**: new tests pass; `test_findings_carry_class_taxonomy` and `test_class_taxonomy_fail_closed` green
- **Dependencies**: none (shares both contract files with earlier tasks — execution sequential in listed order; no semantic dependency)
- **Independent**: false
- **Brief item covered**: "I5 — judged-vs-defaulted class provenance marker"

## Task 11 — version bump 0.50.0 + CHANGELOG + suite-wide close

- **Description**: Bump `loom-code/.claude-plugin/plugin.json` and `loom-code/.codex-plugin/plugin.json` to 0.50.0 (run `python3 scripts/sync_codex_manifests.py loom-code` and verify with `--check`); add the `## [0.50.0]` CHANGELOG entry summarizing the ten fixes; rewrite `test_docs_review_blocking_class.py::test_plugin_version_and_changelog_at_0_49_0` → `..._at_0_50_0` (its docstring says it is rewritten by every bump). Run the full repo suite + `check-skill-structure.py` + `check_version_bump.py` + `backlog_index.py --check` + `check_loom_memory_integrity.py`.
- **Module**: loom-code/.claude-plugin/plugin.json (Codex mirror, CHANGELOG and version test move in the same task; see Files touched)
- **Files touched**: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- **Context paths**:
  - loom-code/CHANGELOG.md (entry format of 0.48.0/0.49.0)
- **Acceptance**:
  - **RED**: rewritten version test (`..._at_0_50_0`) fails before the bump lands
  - **GREEN**: full suite green (`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q`); `sync_codex_manifests.py --check --all` clean; `wc -w loom-code/skills/requesting-docs-review/SKILL.md` measured and reported against the branch-point figure (4189) — net growth near zero, or the one-line justification for the PR body is drafted and reported (soft target 5000-token/~3750-word repo convention; hard cap enforced by `check-skill-structure.py`)
- **Dependencies**: Tasks 1-10 complete first
- **Independent**: false
- **Brief item covered**: "Bump loom-code to 0.50.0 (contract semantics change…)" (brief §Decision); brief §Constraints "net word growth must stay near zero — measure with `wc -w` before and after"

## Task 12 — evidence-class trap probe + ship-gate record (ORCHESTRATOR-EXECUTED)

- **Description**: Run the evidence-class trap probe per `docs/loom/dogfood/2026-07-30-requesting-docs-review-dogfood.md` §D3 recipe (round-1 findings with one evidence-class defect, a remediation that rephrases it in place, one cold docs-reviewer dispatch; expected: not-fixed + no re-litigation + passing verdict) and write the record to a new dogfood file, labeling WHICH contract version actually ran (subagents load the installed plugin cache — expected 0.49.0, not this branch's edits; memory `agent-contract-edits-do-not-reach-this-sessions-subagents`). The record also carries the two PR-body statements the brief obliges: (a) agent-contract edits on this branch are behaviorally unverified in-session, ship gate is static review + the new grep pins; (b) the word-budget measurement or its one-line justification from Task 11. EXECUTION NOTE: the probe dispatch is performed by the ORCHESTRATOR directly, not by an implementer subagent — subagents cannot dispatch agents (no Agent tool; recorded gotcha). The implementer role for this task is limited to assembling the record file from the orchestrator-supplied probe transcript if the orchestrator chooses to delegate the write; otherwise the orchestrator writes the record and this task is closed by the file-existence diagnostic.
- **Module**: docs/loom/dogfood/2026-08-04-docs-review-0490-fix-trap-probe.md
- **Files touched**: docs/loom/dogfood/2026-08-04-docs-review-0490-fix-trap-probe.md (new)
- **Context paths**:
  - docs/loom/dogfood/2026-07-30-requesting-docs-review-dogfood.md (§D3 recipe)
  - docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md (§Constraints — the obligations this record closes)
- **Acceptance**:
  - **RED**: diagnostic — `test -f docs/loom/dogfood/2026-08-04-docs-review-0490-fix-trap-probe.md` exits 1 (file absent)
  - **GREEN**: the file exists and contains: the probe verdict (expected passing + not-fixed + no re-litigation), the contract version that ran (from the plugin cache path), and both PR-body statements; any probe outcome OTHER than expected is surfaced to the user as a contract-wording defect before ship (fix the wording, not the reviewer)
- **Dependencies**: Task 11 completes first
- **Independent**: false
- **Brief item covered**: brief §Constraints "Before ship, run the evidence-class trap probe … and the probe result must be labeled with which contract version actually ran" + "state this in the PR"

## Notes

- Kickoff decision: retract-claim vs add-mechanism for the two carrier gaps (D3 round count, D5 out_of_scope) → retract + backlog entry, user-authorized this session after a complexity briefing (documented decision; not re-briefed per kickoff-briefing §d / judgment-rubrics §3(c)). No PRINCIPLES.md in this repo; zero unbriefed one-way-door hits and zero open implementation forks remain — every wording choice with contract weight is pinned verbatim in its task Description.
- Kickoff decision: D5 mechanism direction → option ② (honest wording now, severity-less ledger block type proposed in a new backlog entry) — committed interpretation stated to the user in-chat before planning.
- Whole-branch routing observation (NOT a per-task `Review-weight:` marker — no task in this plan declares one): the branch is mixed (.md contracts + .py docstring + .py tests), so close-out review routes through `requesting-code-review` Step 1's mixed-branch rule, with the docs arm covering the contract prose.
- Agent-contract edits (Tasks 1,2,3,6,10) are behaviorally unverifiable in-session (installed cache runs 0.49.0) — ship gate is static review + the new grep pins. Task 12 owns the trap-probe regression and the PR-body statements.
- The brief file and gitignored HANDOFF intentionally quote the defective phrases; they are documentation of the defects, not copies to fix. `copywriting-toolkit`'s `prior_findings_check` template is a separate plugin contract — out of scope, divergence noted in PR body.
- Sequencing: most tasks share `requesting-docs-review/SKILL.md` or `docs-reviewer.md` and run sequentially in listed order. Task 3 (docs-reviewer.md only) is file-disjoint from Tasks 4,5,7,8,9 but is deliberately left unmarked (`Independent: false`): Tasks 1/2/10 edit the same agent file, and single-file sequential execution avoids index races on a shared tree (memory `parallel-implementers-shared-tree-need-index-race-guard`). Dependencies edges are semantic only (T1→T2 same fence; T4→T5 same backlog entry; T11 after all edits; T12 after T11).
