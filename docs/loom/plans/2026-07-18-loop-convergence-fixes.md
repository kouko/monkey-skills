# Plan: Loop-Convergence Fixes (tier-1 + batch reconcile + critic verdict files)

Source brief: docs/loom/specs/2026-07-18-loop-convergence-tier1-fixes.md
Design SSOT: docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md §4c (facts in the numbered design points are prescriptive; copy exit codes / verb names / file locations verbatim)
Total tasks: 21
Critical-path depth: 5 (T8→T9→T12→T13→T20; equal-length T8→T9→T12→T21→T20)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (round 2, 2026-07-18; round 1 NEEDS_REVISION fix log in Notes)

## Task 1 — completeness-critic outer revision cap
- Description: Add to completeness-critic SKILL.md resolution clause: outer writer↔critic revision cycle capped at 2; on the 2nd consecutive NEEDS_REVISION after a revision, stop re-running and hand back to the user with a plain-language list of unresolved findings (explicit hand-back, never silent proceed). ≤70 added words (file at 3,889/4,500-word hard cap — PR carries the over-soft-target justification).
- Module: loom-spec
- Files touched: loom-spec/skills/completeness-critic/SKILL.md, loom-spec/scripts/test_completeness_critic_skill.py
- Context paths:
  - loom-spec/skills/completeness-critic/SKILL.md (resolution clause ~:433-434)
  - loom-pipeline/scripts/driver_20_runstation.js (:40 RALLY_CAP=2 — the number being aligned to)
- Acceptance:
  - RED: new test in test_completeness_critic_skill.py asserting SKILL.md documents the 2-cycle outer cap and the explicit-hand-back-on-exhaustion clause
  - GREEN: test passes; `python3 -m pytest loom-spec/scripts/test_completeness_critic_skill.py` green
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State item 1 — "outer revision cycle capped at 2 … explicit hand-back, never silent proceed"

## Task 2 — design-critic outer revision cap
- Description: Same cap + hand-back clause for design-critic SKILL.md (resolution clause ~:255-256). No word-budget pressure (2,245 words).
- Module: loom-interface-design
- Files touched: loom-interface-design/skills/design-critic/SKILL.md, loom-interface-design/scripts/test_design_critic_skill.py
- Context paths:
  - loom-interface-design/skills/design-critic/SKILL.md
- Acceptance:
  - RED: new test asserting the 2-cycle outer cap + hand-back clause documented
  - GREEN: test passes
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State item 1

## Task 3 — wire discovery validator into user-insights
- Description: Add mandatory validate step to user-insights SKILL.md: before declaring done, run `scripts/validate_discovery_artifacts.py` on the produced artifact dir; non-zero → fix and re-run, bounded at 2 attempts, then surface to user. Mirror product-principles Step 8 wiring pattern exactly (loom-product-principles/skills/product-principles/SKILL.md:254-264). Step must tolerate greenfield/first-run artifact creation.
- Module: loom-discovery
- Files touched: loom-discovery/skills/user-insights/SKILL.md, loom-discovery/scripts/test_user_insights_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/SKILL.md (Step 8 worked example)
  - loom-discovery/scripts/validate_discovery_artifacts.py
- Acceptance:
  - RED: new test asserting user-insights SKILL.md contains the validate step invoking validate_discovery_artifacts.py with the 2-attempt bound
  - GREEN: test passes
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State item 2

## Task 4 — wire discovery validator into business-value
- Description: Same validate step for business-value SKILL.md.
- Module: loom-discovery
- Files touched: loom-discovery/skills/business-value/SKILL.md, loom-discovery/scripts/test_business_value_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/SKILL.md (Step 8)
  - loom-discovery/scripts/validate_discovery_artifacts.py
- Acceptance:
  - RED: new test asserting business-value SKILL.md contains the bounded validate step
  - GREEN: test passes
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State item 2

## Task 5 — Codex git-guard shim
- Description: Create `.codex/hooks/git-guard-shim.sh` (passes hook stdin through to `loom-code/hooks/git-guard.py`, resolving repo root via `git rev-parse --show-toplevel`; on unparseable/non-Claude-shaped payload: exit 0 + one-line stderr warning "codex payload shape unknown — gate inactive" so the gap is loud, never a hard block of unrelated commands) and register it in `.codex/hooks.json` under a new `PreToolUse` / `Bash` matcher (file currently PostToolUse-only, 19 lines). Live Codex verification is out-of-band (user probe, brief §Out of Scope).
- Module: repo-root .codex
- Files touched: .codex/hooks/git-guard-shim.sh, .codex/hooks.json, scripts/test_codex_git_guard_shim.py
- Context paths:
  - loom-code/hooks/git-guard.py
  - loom-code/scripts/test_git_guard.py (payload fixture shapes)
  - .codex/hooks.json
- External surfaces: Codex hook payload shape — UNVERIFIED upstream surface; shim must fail open with loud stderr on unknown shape (design decision recorded in brief item 3).
- Acceptance:
  - RED: new test feeding the shim (a) a Claude-Code-style PreToolUse JSON for `git push` with no markers → expect exit 2; (b) a malformed payload → expect exit 0 + warning on stderr
  - GREEN: both assertions pass
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State item 3

## Task 6 — SDD NEEDS_CONTEXT cap + continuous-mode cross-ref
- Description: In subagent-driven-development SKILL.md: (a) cap NEEDS_CONTEXT re-dispatches at 2 per task — a 3rd means the spec/plan is missing information, stop and surface to user (mirror the existing 3-round NEEDS_REVISION escalation wording); (b) in the 3-round-cap section, add one cross-reference sentence noting continuous mode deliberately halts one round earlier (points at references/continuous-mode.md).
- Module: loom-code
- Files touched: loom-code/skills/subagent-driven-development/SKILL.md, loom-code/scripts/test_sdd_needs_context_cap.py
- Context paths:
  - loom-code/skills/subagent-driven-development/SKILL.md (:15,102 NEEDS_CONTEXT branch; :151-156 cap)
  - loom-code/agents/implementer.md (:356-363)
- Acceptance:
  - RED: new test file asserting both the NEEDS_CONTEXT 2-cap language and the continuous-mode cross-reference exist
  - GREEN: test passes
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State items 4 + 5 (SDD side)

## Task 7 — continuous-mode deliberate-slack note
- Description: In continuous-mode.md stop-trigger 2a (~:91), document that the 2-round halt is deliberately one round earlier than SDD's 3-round cap (no human pumping → hand back slack early) and cross-reference SDD's cap section. No number changes.
- Module: loom-code
- Files touched: loom-code/skills/using-loom-code/references/continuous-mode.md, loom-code/scripts/test_continuous_mode_router.py
- Context paths:
  - loom-code/skills/using-loom-code/references/continuous-mode.md
  - loom-code/skills/subagent-driven-development/SKILL.md (wording produced by Task 6 — mirror it)
- Acceptance:
  - RED: new assertion in test_continuous_mode_router.py that the deliberate-slack + cross-reference language exists
  - GREEN: test passes
- Dependencies: Task 6 completes first (doc-mirrors-doc: the two cross-references must name each other consistently)
- Independent: false
- Brief item covered: Smallest End State item 5

## Task 8 — batch state I/O locking
- Description: Wrap batch_queue.py state load→modify→save in `fcntl.flock(LOCK_EX)` held across the full read-modify-write, with `tempfile` + `os.replace()` atomic write. macOS constraints: request LOCK_EX directly (never upgrade from LOCK_SH); open the lock target without truncation. Fixes the pre-existing lost-update race (§4c fact 4).
- Module: loom-pipeline
- Files touched: loom-pipeline/scripts/batch_queue.py, loom-pipeline/scripts/test_pipeline_batch_queue.py
- Context paths:
  - loom-pipeline/scripts/batch_queue.py (:154-172 save_state)
- Acceptance:
  - RED: new test spawning two subprocesses that concurrently read-modify-write different entries; without locking one update is lost
  - GREEN: both updates persist; existing batch tests stay green
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State item 6 — "all state I/O under flock(LOCK_EX) + atomic replace"

## Task 9 — dispatched_at + mark-running subcommand
- Description: `_dispatch_entry` records `dispatched_at` (wall-clock ISO timestamp — batch_queue.py is a fresh-process CLI, exempt from Workflow determinism rules); new subcommand `mark-running <id> --run-id <wf_...> --session-dir <path>` records runId + session workflows dir on a RUNNING entry (dispatcher calls it right after Workflow() returns).
- Module: loom-pipeline
- Files touched: loom-pipeline/scripts/batch_queue.py, loom-pipeline/scripts/test_pipeline_batch_queue.py
- Context paths:
  - loom-pipeline/scripts/batch_queue.py (:505-539 _dispatch_entry; :386-387 mark's runId write)
- Acceptance:
  - RED: CLI test — dispatch an entry, invoke mark-running, assert dispatched_at + runId + session-dir persisted on the RUNNING entry
  - GREEN: passes; existing tests green
- Dependencies: Task 8 completes first (uses the locked save path)
- Independent: false
- Brief item covered: Smallest End State item 6 — "dispatched_at + mark-running --run-id --session-dir"

## Task 10 — recovery verbs reset / force-fail + audit trail
- Description: New subcommands `reset <id>` (RUNNING|FAILED → QUEUED, `attempts += 1`, append audit line) and `force-fail <id> --reason <text>` (RUNNING → FAILED, append audit line, counts toward circuit breaker). Per-entry append-only `audit[]` list records {verb, timestamp, reason}. Transitions gate on current status (idempotent; wrong-state invocation = error exit, no mutation).
- Module: loom-pipeline
- Files touched: loom-pipeline/scripts/batch_queue.py, loom-pipeline/scripts/test_pipeline_batch_queue.py
- Context paths:
  - loom-pipeline/scripts/batch_queue.py (:542-587 circuit breaker)
- Acceptance:
  - RED: CLI test — reset re-queues with attempts+1 and audit line; force-fail transitions with audit line and is counted by the circuit breaker; wrong-state invocations exit non-zero without mutation
  - GREEN: passes
- Dependencies: Task 8 completes first
- Independent: false
- Brief item covered: Smallest End State item 6 — "new reset / force-fail verbs with per-entry append-only audit[]"

## Task 11 — wf-record evidence reader
- Description: Pure helper in batch_queue.py: given runId + session-dir, look for `workflows/wf_<runId>.json`; return its terminal `status` (completed/failed/killed) or None (absent/unreadable — undocumented format is opportunistic evidence only; any parse error ⇒ None, never an exception).
- Module: loom-pipeline
- Files touched: loom-pipeline/scripts/batch_queue.py, loom-pipeline/scripts/test_pipeline_batch_queue.py
- Context paths:
  - docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md (§4c observed wf-record fields)
- External surfaces: `~/.claude/projects/<project>/<session>/workflows/wf_*.json` — UNDOCUMENTED host internals; treat unreadable/missing as "no evidence" (fail-safe), never as failure.
- Acceptance:
  - RED: unit test with fixture wf JSONs (completed/failed/killed/corrupt/absent) asserting status or None per case
  - GREEN: passes
- Dependencies: Task 8 completes first (same-file write ordering, intentional)
- Independent: false
- Brief item covered: Smallest End State item 6 — "auto-FAIL only on definitive wf-record evidence"

## Task 12 — reconcile verb + next integration
- Description: New subcommand `reconcile` (also invoked at the top of `next`, never in `status`): for each RUNNING entry — (a) wf-record says failed/killed → force-FAIL with audit line (breaker counts it); (b) wf-record says completed → flag `SUSPECT-COMPLETE` in output, no transition (human confirms via mark); (c) no evidence and stale (dispatched_at beyond grace window, or RUNNING without runId beyond short grace) → list loudly as SUSPECT, no transition. All transitions gate on status == RUNNING.
- Module: loom-pipeline
- Files touched: loom-pipeline/scripts/batch_queue.py, loom-pipeline/scripts/test_pipeline_batch_queue.py
- Context paths:
  - loom-pipeline/scripts/batch_queue.py (:590-684 _cmd_next; :396-441 _cmd_status stays pure)
- Acceptance:
  - RED: CLI test covering (a) auto-FAIL on fixture failed-record, (b) SUSPECT-COMPLETE on completed-record, (c) SUSPECT-only on stale-no-evidence; plus: `status` performs no mutation
  - GREEN: passes
- Dependencies: Tasks 9, 11 complete first
- Independent: false
- Brief item covered: Smallest End State item 6 — "reconciliation in next + new reconcile verb (never status)"

## Task 13 — done derivation + loud enumeration
- Description: `next`'s `{"done": true}` output derives from `terminal_count == total`; when non-terminal entries remain (RUNNING/SUSPECT), done stays false and they are enumerated loudly in the same output.
- Module: loom-pipeline
- Files touched: loom-pipeline/scripts/batch_queue.py, loom-pipeline/scripts/test_pipeline_batch_queue.py
- Context paths:
  - loom-pipeline/scripts/batch_queue.py (:683 done path)
- Acceptance:
  - RED: test — queue with one stranded RUNNING entry: next must NOT print done:true and must enumerate the entry
  - GREEN: passes
- Dependencies: Task 12 completes first (enumeration includes SUSPECT states reconcile produces)
- Independent: false
- Brief item covered: Smallest End State item 6 — "done = terminal_count == total"

## Task 14 — mint_critic_verdict.py (loom-spec)
- Description: New `loom-spec/scripts/mint_critic_verdict.py` per §4c Fix-4 design: `mint --change-folder --verdict-file --files` / `validate --change-folder --files`; sha256 content binding over the covered files; validate exits 0 fresh-PASS_WITH_NOTES / 2 no-verdict / 3 fresh-NEEDS_REVISION / 4 stale-hash; NEEDS_REVISION still mints; overwrite-in-place. Copy argparse skeleton + verdict-text schema checks from loom-code/scripts/loom_gate_markers.py.
- Module: loom-spec
- Files touched: loom-spec/scripts/mint_critic_verdict.py, loom-spec/scripts/test_mint_critic_verdict.py
- Context paths:
  - loom-code/scripts/loom_gate_markers.py (skeleton + validate_verdict_text)
  - docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md (§4c Fix-4 points 1-4)
- Acceptance:
  - RED: test covering all four validate exit codes + NEEDS_REVISION-still-mints + hash staleness after editing a covered file
  - GREEN: passes
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State item 7 — "mint/validate CLI … exits 0/2/3/4; NEEDS_REVISION still mints"

## Task 15 — mint_critic_verdict.py (loom-interface-design)
- Description: Port Task 14's proven script + tests to loom-interface-design/scripts/ (byte-identical logic; only default file lists differ: DESIGN.md,ui-flows.md).
- Module: loom-interface-design
- Files touched: loom-interface-design/scripts/mint_critic_verdict.py, loom-interface-design/scripts/test_mint_critic_verdict.py
- Context paths:
  - loom-spec/scripts/mint_critic_verdict.py (worked example from Task 14)
- Acceptance:
  - RED: same test matrix as Task 14 against the ported script
  - GREEN: passes
- Dependencies: Task 14 completes first (copy the proven pattern — zero drift)
- Independent: true
- Brief item covered: Smallest End State item 7

## Task 16 — completeness-critic mints its verdict
- Description: completeness-critic SKILL.md verdict step additionally runs `mint_critic_verdict.py mint` for the change-folder (both verdict values mint). Keep within word budget (net ≤40 added words; cite mint command, don't re-explain it).
- Module: loom-spec
- Files touched: loom-spec/skills/completeness-critic/SKILL.md, loom-spec/scripts/test_completeness_critic_skill.py
- Context paths:
  - loom-spec/scripts/mint_critic_verdict.py
- Acceptance:
  - RED: test asserting the mint step is documented in the verdict section
  - GREEN: passes; word count still ≤4,500
- Dependencies: Tasks 1, 14 complete first (same file as T1; script must exist)
- Independent: false
- Brief item covered: Smallest End State item 7 (producer side)

## Task 17 — design-critic mints its verdict
- Description: Same mint step for design-critic SKILL.md.
- Module: loom-interface-design
- Files touched: loom-interface-design/skills/design-critic/SKILL.md, loom-interface-design/scripts/test_design_critic_skill.py
- Context paths:
  - loom-interface-design/scripts/mint_critic_verdict.py
- Acceptance:
  - RED: test asserting the mint step documented
  - GREEN: passes
- Dependencies: Tasks 2, 15 complete first
- Independent: false
- Brief item covered: Smallest End State item 7 (producer side)

## Task 18 — spec-expansion consumes the design verdict
- Description: spec-expansion SKILL.md §Consuming-a-ui-flows-seed gains a validate-before-fan-out step: run loom-spec's `mint_critic_verdict.py validate --files DESIGN.md,ui-flows.md`; proceed only on exit 0; on 2/3/4 stop, report which condition blocked (never-ran / critic-blocked / stale), route back accordingly.
- Module: loom-spec
- Files touched: loom-spec/skills/spec-expansion/SKILL.md, loom-spec/scripts/test_spec_expansion_verdict_gate.py
- Context paths:
  - loom-spec/skills/spec-expansion/SKILL.md (§Consuming a ui-flows.md seed, ~:72-99)
  - loom-spec/scripts/mint_critic_verdict.py
- Acceptance:
  - RED: new test asserting the validate-before-fan-out step + per-exit-code routing documented
  - GREEN: passes
- Dependencies: Task 14 completes first
- Independent: true
- Brief item covered: Smallest End State item 7 — "consumers = spec-expansion ui-flows intake … refuse on non-zero"

## Task 19 — writing-plans consumes the spec verdict
- Description: writing-plans SKILL.md §Who-runs-the-validator additionally requires `mint_critic_verdict.py validate` exit 0 for the change-folder (structural-clean ≠ critic-fresh-and-passed), same per-exit-code reporting. Cross-plugin invocation of loom-spec's script follows the existing validate_spec_output.py precedent in the same section.
- Module: loom-code
- Files touched: loom-code/skills/writing-plans/SKILL.md, loom-code/scripts/test_writing_plans_verdict_gate.py
- Context paths:
  - loom-code/skills/writing-plans/SKILL.md (§Who runs the validator, ~:184)
  - loom-spec/scripts/mint_critic_verdict.py
- Acceptance:
  - RED: new test asserting the additional validate requirement + exit-code routing documented
  - GREEN: passes
- Dependencies: Task 14 completes first
- Independent: true
- Brief item covered: Smallest End State item 7 — "consumers = … writing-plans change-folder intake"

## Task 21 — batch dispatcher instructions consume the new verbs
- Description: Update using-loom-pipeline SKILL.md batch-loop steps (~:236-249): after `Workflow()` returns, the dispatcher MUST call `mark-running <id> --run-id <wf_...> --session-dir <path>`; a fresh session taking over a batch runs `reconcile` before `next`; document reset/force-fail verbs and SUSPECT/SUSPECT-COMPLETE handling for the human operator. Also update AGENTS.md's managed command-surface entry for batch_queue.py (`{next|mark|status}` → the full verb set) — command-surface accretion duty for the verbs Tasks 9/10/12 ship. Without this wiring the runId is never recorded and reconcile's definitive-evidence path is dead — the wiring is the teeth.
- Module: loom-pipeline
- Files touched: loom-pipeline/skills/using-loom-pipeline/SKILL.md, loom-pipeline/scripts/test_pipeline_dispatcher_verbs.py, AGENTS.md
- Context paths:
  - loom-pipeline/skills/using-loom-pipeline/SKILL.md (batch loop steps)
  - loom-pipeline/scripts/batch_queue.py (verb semantics from Tasks 9, 10, 12)
- Acceptance:
  - RED: new test asserting the SKILL.md batch steps document mark-running-after-Workflow, reconcile-on-takeover, and the two recovery verbs
  - GREEN: test passes
- Dependencies: Tasks 9, 10, 12 complete first (doc mirrors the shipped verb semantics)
- Independent: false
- Brief item covered: Smallest End State item 6 — §4c point 1 "invoked by the dispatcher immediately after Workflow() returns" (dispatcher-side wiring)

## Task 20 — shipping tax
- Description: Bump plugin versions + CHANGELOG entries for loom-spec, loom-interface-design, loom-discovery, loom-code, loom-pipeline; run `python3 scripts/sync_codex_manifests.py` and the marketplace description sync check; update audit doc Status line (§4 recs 2/5/7/9/10 + §4c both designs → shipped) and brief Status. Full triad review (semver choice and CHANGELOG prose are authored judgment, not mechanical reproduction).
- Module: repo-wide metadata
- Files touched: loom-spec/.claude-plugin/plugin.json, loom-interface-design/.claude-plugin/plugin.json, loom-discovery/.claude-plugin/plugin.json, loom-code/.claude-plugin/plugin.json, loom-pipeline/.claude-plugin/plugin.json, loom-spec/CHANGELOG.md, loom-interface-design/CHANGELOG.md, loom-discovery/CHANGELOG.md, loom-code/CHANGELOG.md, loom-pipeline/CHANGELOG.md, loom-spec/.codex-plugin/plugin.json, loom-interface-design/.codex-plugin/plugin.json, loom-discovery/.codex-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, .claude-plugin/marketplace.json, docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md, docs/loom/specs/2026-07-18-loop-convergence-tier1-fixes.md
- Context paths:
  - scripts/check_version_bump.py
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: `python3 scripts/check_version_bump.py` (and CI equivalents) failing before bumps on the changed plugins
  - GREEN: version-bump check + marketplace sync check + codex manifest sync test pass
- Dependencies: Tasks 1-19, 21 complete first
- Independent: false
- Brief item covered: "Plus the repo's shipping tax …"

## Notes

### Execution incident log (orchestrator-maintained)

- Shared-working-tree commit races (wave 2): Task 15's first commit (8d28d35b) swept Task 18's staged files; Task 15 recovered via reset --soft + restage, which orphaned BOTH 8d28d35b AND Task 11's commit 09dc6bb0 from the branch. Consequences and resolutions: (a) Task 18's files re-committed verbatim by the orchestrator as aff46b69 (content = the dual-reviewed artifact, byte-identical); (b) Task 11's content survived in the working tree and was unknowingly swept into Task 10's round-2 commit a5a86ff6 — verified byte-identical to the dual-reviewed 09dc6bb0 (empty diff on the helper), so Task 11's review verdicts (spec PASS + cq PASS_WITH_NOTES) apply to the landed content. Orchestrator resolution for a5a86ff6's mixed scope (flagged by both T10-r2 reviewers): ACCEPTED WITH DOCUMENTATION — repo squash-merges PRs so per-commit attribution does not survive merge; history surgery was rejected (active implementer on the same file). PR body must note that a5a86ff6 carries Task 10 r2 + Task 11 content.
- Decision (T5, agent-decided, two-way door): shim payload-shape check uses python3 not jq (git-guard already requires python3; jq not guaranteed).
- Decision (T11→T12, agent-decided): `_read_wf_terminal_status` session_dir=None guard fixed inside Task 12 (T11 reviewer recommendation, same files).

- Input is a brainstorming brief (explicit handoff); no loom-spec change-folder bound — change-folder detection not applicable, scenario-coverage script N/A.
- Exact plugin.json paths in Task 20 to be confirmed by the implementer at dispatch (some plugins keep plugin.json at plugin root — follow scripts/check_version_bump.py's expectations).
- Parallel wave 1 candidates (all Independent: true, disjoint files): Tasks 1, 2, 3, 4, 5, 6, 8, 14.
- Parallel wave 2 candidates (post-Task-14, Independent: true, pairwise disjoint): Tasks 15, 18, 19.
- Round-1 reviewer fix log: Task 20 mechanical claim dropped (full triad; semver/CHANGELOG are judgment), its Files touched concretized; Task 11 gained explicit "Task 8 completes first"; Tasks 15/18/19 marked Independent: true per Check-15 advisory.
- Post-PASS amendment 2 (2026-07-18): Task 21 deps extended to "Tasks 9, 10, 12" per the amendment-review's own advisory (T21 documents verbs Task 10 ships); additive and schema-safe, depth unchanged at 5 — re-review skipped per §Amending a PASS plan option (b).
- Post-PASS amendment (2026-07-18): added Task 21 (dispatcher-side wiring for mark-running/reconcile/verbs — kickoff sweep caught that batch_queue.py mechanics shipped with no dispatcher instruction consuming them); Task 20 deps extended; depth recomputed at 5. Re-review dispatched per §Amending a PASS plan option (a).
- Kickoff decision: reconcile grace window for RUNNING-without-runId → 10 minutes (dispatch-to-mark-running is seconds apart in normal operation; 10 min absorbs slow starts).
- Kickoff decision: staleness listing threshold for SUSPECT → 2 hours since dispatched_at (informational only, no transition — safe even though legit runtime is unbounded).
- Kickoff decision: lock target → sidecar `<state-file>.lock` file, not the state file itself (avoids the macOS truncating-open-before-flock trap).
- Kickoff decision: all §4c-pinned facts (verdict-file names/paths, validate exit codes 0/2/3/4, verb names reset/force-fail, audit-line fields verb/timestamp/reason) are prescriptive — implementers copy verbatim, deviations are defects.
