# Plan: loom-code mechanical gates (audit follow-up A+C)

- **Brief**: `docs/loom/audits/2026-07-04-harness-engineering-audit.md` §Recommendations items 1, 2, 3, 6 (item 5 verified already-in-CI: loom-code-ci.yml runs `pytest loom-code/scripts/` which includes `test_shipped_corpus_validates`)
- **Home decision**: loom-code plugin `hooks/` (rule and enforcement co-located; existing hooks.json + `LOOM_CODE_MODE=off` escape-hatch convention)
- **Design adaptation vs audit**: completion gate moves from Stop hook to the push choke point (see §Design fork) — PENDING user confirmation
- **Version**: loom-code 0.22.1 → 0.23.0 (new behavior)

## Design: marker-file protocol

Hooks can only check disk state; review/verification verdicts today live in conversation. Protocol:

- `.git/loom/review-pass.json` — written by the ORCHESTRATOR when requesting-code-review returns PASS/PASS_WITH_NOTES: `{branch, head_sha, verdict, written_at}`. Lives under `.git/` (never committed, per-checkout).
- `.git/loom/verified.json` — written when verification-before-completion's package-level test run passes: `{head_sha, suite_line, written_at}` (head_sha chosen over tree_hash per T3's simplest-sound-rule note; the close-out flow re-mints at the final HEAD).
- `.git/loom/waiver.json` — written ONLY on explicit user instruction to skip review ("直接 push 不用 review"): `{scope, reason, written_at}`. Keeps human-in-the-loop for the escape path; hook logs waiver use to stderr (visible, never silent).

The marker WRITE stays prompt-driven (SKILL.md instruction), but the gate flips the failure mode: forgetting review now fails LOUDLY at push instead of silently succeeding. This is the TDD-Guard insight applied: the hook guarantees the check fires; judgment stays with the existing review machinery.

## Design fork (needs user call)

Audit item 3 said "Stop hook runs package tests". Deviation proposed: fold the completion gate into the SAME PreToolUse push gate (require `verified.json` fresh against current tree) instead of a Stop hook, because:
1. Stop fires on EVERY turn end in EVERY repo for EVERY loom-code installer — running pytest per-stop is the approval-fatigue/bypass scenario the industry warns about;
2. arbitrary repos have arbitrary suite runtimes — hook timeouts would kill legitimate stops;
3. push is the natural single choke point ("verified before ship"), rare enough that a marker check costs nothing.

## Tasks (atomic, TDD each)

1. **T1 `hooks/git-guard.py`** — PreToolUse(Bash matcher) script: parse tool-input JSON; block `git commit --no-verify` (exit 2 + reason). Graceful pass: non-git cwd, `LOOM_CODE_MODE=off`.
2. **T2 push gate in same script** — block `git push` / `gh pr create` / `gh pr merge` when `.git/loom/review-pass.json` absent OR `head_sha` ≠ current HEAD; honor `waiver.json` (log to stderr). Same graceful passes as T1 + repos with no `.git/loom/` history-of-use → warn-once-then-allow vs hard-block: START hard-block, revisit on fatigue evidence.
3. **T3 verified gate in same script** — push also requires `verified.json` with `tree_hash` == current `git rev-parse HEAD^{tree}`… NOTE: tests run pre-commit produce a different tree after commit; use HEAD tree at verification time — define freshness as "verified tree is an ancestor-equal of push tree OR same HEAD" — implement simplest sound rule: `head_sha` match, same as T2.
4. **T4 SKILL.md wiring** — requesting-code-review: on PASS write review-pass marker (one §, cap-tested); verification-before-completion: on green package run write verified marker; finishing-a-development-branch: mention both. brainstorming/using-loom-code untouched.
5. **T5 verdict schema validation** — CONSOLIDATED into `scripts/loom_gate_markers.py review-pass` (validates standards_version / verdict enum / dimension_scores / findings[].where BEFORE minting the marker — the marker can only exist if a schema-valid verdict existed; a separate validate_review_verdict.py would duplicate the same parse). Wired into requesting-code-review Process step 3.
6. **T6 hooks.json wiring** — add PreToolUse entry (`matcher: "Bash"`) pointing at git-guard via `${CLAUDE_PLUGIN_ROOT}`; keep SessionStart untouched.
7. **T7 ship chores** — plugin.json 0.23.0 + codex manifest sync + README row (3 languages) + CHANGELOG if present.

## Test strategy

Hook scripts are Python (precedent: `.claude/hooks/` pairs .sh with pytest; here pure-Python for JSON parsing) — pytest fixtures feed PreToolUse JSON payloads via stdin simulation; assert exit codes + stderr text. All tests land in `loom-code/scripts/` (CI-covered path).

## Out of scope

- TDD Guard pilot (BACKLOG: bound to first real SDD venue — komado-Viewfinder batch6 / Segment-3 first run)
- Stop-hook telemetry/observability pipeline
- README-drift CI (option B re-trigger)
