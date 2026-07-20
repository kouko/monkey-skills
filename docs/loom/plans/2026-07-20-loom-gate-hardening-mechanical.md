# Plan: loom Gate Hardening (mechanical / do-real cluster)

Source brief: docs/loom/specs/2026-07-20-loom-gate-hardening-mechanical.md
Total tasks: 11
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible (L1: Tasks 1/2/4/5 concurrent; L2: Tasks 3a/3b/3c/3d/6a/6b concurrent; L3: Task 6c)
Plan-document-reviewer verdict: PASS (2026-07-20, round 2). Post-PASS additive amendments (all schema-safe, DAG depth unchanged at 3, re-review skipped per writing-plans §Amending a PASS plan): (1) Task 1 added to 6a/6b Dependencies + RED wording softened; (2) Tasks 3c/3d added — two more verified-contract caller sites (`verification-before-completion/SKILL.md:56` real mint invocation; `requesting-code-review/SKILL.md:213` pointer) surfaced by a Codex-compat recon; both are pattern-identical clones of the already-reviewed 3a/3b (one file, grep RED, dep Task 2, Independent:true, disjoint Files touched) so they cannot introduce a new check failure.

## Scope change from the signed-off brief (surfaced)

The brief listed FIVE fix areas. During target-repo recon, the **pipeline seg2 validator** fix (originally "the driver runs the validator itself") was found **infeasible as a mechanical fix**: `loom-pipeline/scripts/driver_40_seg2.js` runs inside the Workflow sandbox, which has **no Node/subprocess access** (`seg2ValidatorPreamble` at `driver_40_seg2.js:106-115` can only instruct an *agent* to run the validator and self-report `validator_exit`). Making the gate run the validator itself needs an architecture change (move the validator call to a sandbox-external step), which is design, not mechanical. It is therefore **reclassified to the deferred CI-side/design arc** alongside waiver/review-pass/#8/#6. The batch path is unaffected — `batch_queue.py:311-317` already runs the validator itself because it is sandbox-external Python. This plan implements the remaining four mechanical fixes + their doc/version follow-ups.

## Task 1 — version-bump gate sees `scripts/`
- Description: Add `"scripts"` to `SKILL_CONTENT_DIRS` so a diff touching a plugin's `scripts/` (gate code) demands a version bump.
- Module: scripts/check_version_bump.py
- Files touched: scripts/check_version_bump.py, scripts/test_check_version_bump.py
- Context paths:
  - scripts/check_version_bump.py (`SKILL_CONTENT_DIRS` line 42; `plugins_with_skill_content` 64-)
  - scripts/test_check_version_bump.py (existing test patterns)
- Acceptance:
  - RED: a new test asserting `plugins_with_skill_content(["loom-code/scripts/loom_gate_markers.py"])` returns `{"loom-code"}` — currently returns `set()`.
  - GREEN: that test passes; existing tests (skills/hooks/agents/references still detected) stay green.
- Dependencies: none
- Independent: true
- Brief item covered: "#1 version-bump blind spot — SKILL_CONTENT_DIRS gains 'scripts', so editing gate code demands a bump."

## Task 2 — `verified` binds to a real test run
- Description: Replace `verified`'s self-typed `--suite-line` mint path with `--run "<cmd>"`, which executes the command in `--repo`, captures its real exit code + output tail, and mints `verified.json` **only** on exit 0 (recording the command + captured tail, not a self-asserted claim). Remove the `--suite-line` self-attestation path from the write flow. Design fork resolved: adopt option (a) — CLI runs an explicit `--run` command; residual forgeability (`--run "true"`) is documented honestly, the marker records the command run so a fake is at least auditable.
- Module: loom-code/scripts/loom_gate_markers.py
- Files touched: loom-code/scripts/loom_gate_markers.py, loom-code/scripts/test_loom_gate_markers.py
- Context paths:
  - loom-code/scripts/loom_gate_markers.py (`_cmd_verified` 306-331; `validate_suite_line` 289-303; verified subparser 410-412)
  - loom-code/scripts/test_loom_gate_markers.py (verified tests 252-293 — these encode the OLD `--suite-line` contract and must be rewritten RED→GREEN)
- Acceptance:
  - RED: a new test asserting `verified --run "python3 -c 'import sys; sys.exit(1)'"` (a failing command) writes **no** marker and exits non-zero; and `verified --run "python3 -c 'pass'"` writes `verified.json` whose payload records the real captured result — while a self-typed `--suite-line "999 passed"` with no execution is **no longer accepted** (arg removed / rejected).
  - GREEN: the new run-binding tests pass; the old suite-line-string tests (252-293) are updated to the new contract, not left asserting the removed behavior.
- External surfaces: subprocess execution of an agent-supplied command (Python `subprocess`); capture exit code + bounded output tail; no shell-injection beyond what the orchestrator already controls (document the residual). stdlib `subprocess` preferred — no new dependency.
- Dependencies: none
- Independent: true
- Brief item covered: "`verified` binds to real execution — stops accepting a self-typed --suite-line; captures a real test run's exit code/output instead."

## Task 3a — update the finishing-branch SKILL's verified invocation
- Description: Update the `verified --suite-line` invocation in the finishing-branch SKILL to the new `--run` contract, so the shipped instruction matches the code.
- Module: loom-code/skills/finishing-a-development-branch/SKILL.md
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md
- Context paths:
  - loom-code/skills/finishing-a-development-branch/SKILL.md (line 214 — the `verified --suite-line` invocation)
- Acceptance:
  - RED: `grep -n "suite-line" loom-code/skills/finishing-a-development-branch/SKILL.md` shows the old `verified --suite-line "<tail line>"` invocation (line 214) — the RED state.
  - GREEN: that line describes `verified --run "<test command>"`; no `--suite-line` remains on the verified write-path in this file.
- Dependencies: Task 2 completes first (doc-mirrors-code — the doc must match the shipped contract).
- Independent: true
- Brief item covered: "What Becomes Obsolete: verified's --suite-line free-text parameter … replaced by real-execution binding; remove in the same change."

## Task 3b — update the gate-markers-spec suite-line grammar
- Description: Update the gate-markers reference spec's suite-line grammar to the new `--run` contract (or mark the suite-line grammar vestigial/validate-only if `validate` still accepts it).
- Module: loom-code/skills/requesting-code-review/references/gate-markers-spec.md
- Files touched: loom-code/skills/requesting-code-review/references/gate-markers-spec.md
- Context paths:
  - loom-code/skills/requesting-code-review/references/gate-markers-spec.md (§Suite-line grammar line 30; validate example line 74)
- Acceptance:
  - RED: `grep -n "Suite-line grammar\|verified --suite-line" loom-code/skills/requesting-code-review/references/gate-markers-spec.md` shows the old `verified` write-path grammar — the RED state.
  - GREEN: the spec documents `verified --run`; the `--suite-line` grammar is removed or explicitly scoped to `validate`-only if that subcommand retains it.
- Dependencies: Task 2 completes first (doc-mirrors-code).
- Independent: true
- Brief item covered: "What Becomes Obsolete: verified's --suite-line free-text parameter … replaced by real-execution binding; remove in the same change."

## Task 3c — update the verification-before-completion mint invocation
- Description: Update the actual `verified --suite-line` mint invocation in the verification-before-completion SKILL — the canonical mint site that finishing-a-development-branch delegates to — to the new `--run` contract.
- Module: loom-code/skills/verification-before-completion/SKILL.md
- Files touched: loom-code/skills/verification-before-completion/SKILL.md
- Context paths:
  - loom-code/skills/verification-before-completion/SKILL.md (line 56 — `loom_gate_markers.py verified --suite-line "<summary line>"`)
- Acceptance:
  - RED: `grep -n "verified --suite-line" loom-code/skills/verification-before-completion/SKILL.md` shows the old mint invocation (line 56) — the RED state.
  - GREEN: that step mints via `verified --run "<test command>"`; the "command run, test count, summary line" evidence phrasing is reconciled with the run-binding contract; no `--suite-line` on the verified write-path in this file.
- Dependencies: Task 2 completes first (doc-mirrors-code).
- Independent: true
- Brief item covered: "What Becomes Obsolete: verified's --suite-line free-text parameter … replaced by real-execution binding; remove in the same change."

## Task 3d — update the requesting-code-review pointer line
- Description: Update the one descriptive pointer line in requesting-code-review/SKILL.md that names the reference doc's "suite-line grammar" so it matches the reference's post-change contents (Task 3b).
- Module: loom-code/skills/requesting-code-review/SKILL.md
- Files touched: loom-code/skills/requesting-code-review/SKILL.md
- Context paths:
  - loom-code/skills/requesting-code-review/SKILL.md (line 213 — the gate-markers-spec pointer, naming "suite-line grammar")
- Acceptance:
  - RED: `grep -n "suite-line grammar" loom-code/skills/requesting-code-review/SKILL.md` shows the stale pointer (line 213) — the RED state.
  - GREEN: the pointer names the reference's actual post-change contents (e.g. "run grammar" / "verified-run contract"); no stale "suite-line grammar" description for the verified write-path.
- Dependencies: Task 2 completes first (doc-mirrors-code).
- Independent: true
- Brief item covered: "What Becomes Obsolete: verified's --suite-line free-text parameter … replaced by real-execution binding; remove in the same change."

## Task 4 — batch `_cmd_mark` precursor-state precondition
- Description: Give `_cmd_mark` the precursor-state guard its sibling `_cmd_mark_running` already has — reject terminal-marking (`done`/`failed`) an entry that is not in a valid precursor state (e.g. never-dispatched QUEUED), with a caller-facing stderr message + exit 1 + no state mutation, mirroring `_cmd_mark_running`'s shape.
- Module: loom-pipeline/scripts/batch_queue.py
- Files touched: loom-pipeline/scripts/batch_queue.py, loom-pipeline/scripts/test_pipeline_batch_queue.py
- Context paths:
  - loom-pipeline/scripts/batch_queue.py (`_cmd_mark` 438-464; `_cmd_mark_running` guard 467-483; `effective_entries`/status vocab 221-233)
  - loom-pipeline/scripts/test_pipeline_batch_queue.py (existing mark tests)
- Acceptance:
  - RED: a new test asserting `mark <id> done` on a QUEUED (never-dispatched) entry returns exit 1, writes no state record, and prints a mark-prefixed message — currently exits 0 and records DONE.
  - GREEN: that test passes; a legitimate transition (RUNNING→DONE, or whatever precursor set is chosen) still succeeds; existing mark tests stay green.
- Dependencies: none
- Independent: true
- Brief item covered: "#4 batch precondition — _cmd_mark gains the precursor-state guard _cmd_mark_running already has, so a QUEUED entry cannot jump straight to DONE."

## Task 5 — push-guard action-detection through wrappers
- Description: Make `git-guard.py` recognize a push/merge **action** even when the git/gh invocation is prefixed by a wrapper (`/usr/bin/git`, `env git`, `command git`, `sh -c "git push"`, `gh api …/merge`), rather than only when `toks[0] == "git"`. See-through known wrappers to the real git/gh verb; keep the false-positive surface controlled (do not block legitimate non-push git commands).
- Module: loom-code/hooks/git-guard.py
- Files touched: loom-code/hooks/git-guard.py, loom-code/scripts/test_git_guard.py, scripts/test_codex_git_guard_shim.py
- Context paths:
  - loom-code/hooks/git-guard.py (segment/token loop 366-408; `_parse_git`; `_has_no_verify`)
  - loom-code/scripts/test_git_guard.py (existing rc2/rc0 cases)
  - scripts/test_codex_git_guard_shim.py (shim forwards to git-guard — new matching flows through)
- Acceptance:
  - RED: new tests asserting `/usr/bin/git push`, `env git push`, `sh -c "git push"`, and `gh api repos/o/r/pulls/N/merge -X PUT` each return rc2 (blocked) in a marker-less repo — currently rc0.
  - GREEN: those pass; regression cases stay green — bare `git push` rc2, `gh pr merge N` rc2, a legitimate non-push git command (e.g. `git status`, `/usr/bin/git log`) rc0, and `LOOM_CODE_MODE=off` still fails-open.
- External surfaces: none new (string/token parsing only).
- Dependencies: none
- Independent: true
- Brief item covered: "#3 push-guard — matches a push/merge action anywhere in a git/gh invocation regardless of first-token wrapper, fail-closed on unrecognized wrappers around git."

## Task 6a — bump loom-code plugin version
- Description: Bump the loom-code plugin manifest (its shipped code changed in Tasks 2 and 5) and add its CHANGELOG entry.
- Module: loom-code/.claude-plugin/plugin.json
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/CHANGELOG.md
- Context paths:
  - loom-code/.claude-plugin/plugin.json (current "version": "0.34.0")
  - loom-code/CHANGELOG.md (existing entry format)
- Acceptance:
  - RED: loom-code plugin.json still reads 0.34.0 while its shipped code changed — `check_version_bump --base <branch-base> --head HEAD` reports loom-code needs a bump (exit 1); fires correctly only after Task 1 makes the gate scripts-aware.
  - GREEN: loom-code 0.34.0→0.35.0; CHANGELOG entry added describing the verified-run + push-guard changes.
- Dependencies: Tasks 1, 2, 5 complete first (Task 1 makes the bump-gate able to see the scripts/ + hooks/ changes; Tasks 2, 5 are the loom-code shipped-code changes requiring the bump).
- Independent: true
- Brief item covered: "Decision — version-bump the two plugins whose shipped code changes (loom-code, loom-pipeline)."

## Task 6b — bump loom-pipeline plugin version
- Description: Bump the loom-pipeline plugin manifest (its shipped code changed in Task 4) and add its CHANGELOG entry.
- Module: loom-pipeline/.claude-plugin/plugin.json
- Files touched: loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/CHANGELOG.md
- Context paths:
  - loom-pipeline/.claude-plugin/plugin.json (current "version": "0.9.0")
  - loom-pipeline/CHANGELOG.md (existing entry format)
- Acceptance:
  - RED: loom-pipeline plugin.json still reads 0.9.0 while its shipped code changed — `check_version_bump --base <branch-base> --head HEAD` reports loom-pipeline needs a bump (exit 1); fires correctly only after Task 1.
  - GREEN: loom-pipeline 0.9.0→0.10.0; CHANGELOG entry added describing the batch-precondition change.
- Dependencies: Tasks 1, 4 complete first (Task 1 makes the bump-gate able to see the scripts/ change; Task 4 is the loom-pipeline shipped-code change).
- Independent: true
- Brief item covered: "Decision — version-bump the two plugins whose shipped code changes (loom-code, loom-pipeline)."

## Task 6c — sync marketplace + Codex manifest mirrors
- Description: Regenerate the marketplace listing and Codex manifest mirrors from the bumped plugin manifests, so the release surfaces agree.
- Module: .claude-plugin/marketplace.json
- Files touched: .claude-plugin/marketplace.json (+ Codex manifest mirrors regenerated via scripts/sync_codex_manifests.py)
- Context paths:
  - scripts/sync_codex_manifests.py, scripts/test_sync_codex_manifests.py
  - .claude-plugin/marketplace.json (per-plugin version entries)
- Acceptance:
  - RED: after 6a/6b, `python3 scripts/test_sync_codex_manifests.py` (or a marketplace-version-consistency check) fails — marketplace/Codex mirrors still carry the pre-bump versions.
  - GREEN: marketplace.json + Codex mirrors carry 0.35.0 / 0.10.0; `test_sync_codex_manifests.py` green; a full `check_version_bump --base <branch-base> --head HEAD` exits 0.
- Dependencies: Tasks 6a, 6b complete first (needs the bumped source versions).
- Independent: false
- Brief item covered: "Decision — version-bump the two plugins whose shipped code changes (loom-code, loom-pipeline)."

## Notes

- **Seg2 reclassification** (see §Scope change): moved to the deferred arc; documented, not silently dropped.
- **Test files all exist** (recon-confirmed): test_check_version_bump.py, test_loom_gate_markers.py, test_pipeline_batch_queue.py, test_git_guard.py, test_codex_git_guard_shim.py — no greenfield test scaffolding needed.
- **Honest framing carried from the brief**: every fix is a bar-raise (real execution / precondition / wrapper-aware matching), not cryptographic unforgeability, which is unachievable locally.
