# Execution card — wiki-fix-loop smoke run (orchestrator: run as-is)

## Workflow call

- scriptPath: `/Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-update/scripts/wiki_fix_loop.js`
- args (JSON, verbatim — timestamps enter via `runLabel` per the engine's
  resume-safe contract; every path already passes the engine's per-segment
  allow-list):

```json
{
  "runLabel": "smoke-2026-07-23",
  "sandboxDir": "/private/tmp/claude-501/-Users-kouko-GitHub-monkey-skills/50f049ad-d514-4d70-a0d5-6e6a333953b2/scratchpad/wiki-smoke-runs",
  "vaultDir": "/private/tmp/claude-501/-Users-kouko-GitHub-monkey-skills/50f049ad-d514-4d70-a0d5-6e6a333953b2/scratchpad/wiki-smoke-vault",
  "validatorScript": "/Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-lint/scripts/wiki_lint_check.py",
  "verdictScript": "/Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-update/scripts/loop_verdict.py",
  "maxRounds": 8,
  "maxDiffLines": 1500
}
```

Notes:
- runDir `<sandboxDir>/smoke-2026-07-23` is pre-created (the grader courier
  shell-redirects `round0.jsonl` into it before any Write-tool call).
- `maxRounds: 8` — 6 seeded violation classes; the default 5 would force a
  BUDGET stop before every class gets its round.
- Headless run: set `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` (known 600s trap).
- Vault base commit (frozen): `d8f3c4fef8a68302b59535934ac4dc690252140e`.

## Post-run verification checklist

1. Terminal state legal: scorecard `terminal` ∈
   {CONVERGED, PLATEAU, STUCK (with `blockers-report.md` present)} per plan T9;
   WORK_ORDERS_ONLY / BUDGET = honest stop, inspect ledger before accepting;
   STUCK_EXECUTOR_OVERREACH / MALFORMED = smoke FAIL.
2. Monotone violations: in `ledger.jsonl`, every `action: "accept"` row has
   `violationsAfter < violationsBefore`; no accepted row ever increases;
   scorecard `finalViolations` ≤ 10 and `violationDelta` ≥ 0.
3. Zero-deletion: every accepted round's `ratchetExit` = 0, AND
   `git -C <vaultDir> diff --diff-filter=D --name-only d8f3c4f..HEAD -- wiki`
   is empty (no file deleted), AND re-running the validator shows no per-file
   conservation counter (words/links/headings) below its before value.
4. Artifacts exist in runDir: `freeze.json`, `round0.jsonl`, `ledger.jsonl`,
   `scorecard.json`, `fix-loop-report.md`; `work-orders.jsonl` iff any class
   was unsafe-only (expected: L02/L03 at least); `blockers-report.md` iff
   terminal ∈ {STUCK, STUCK_EXECUTOR_OVERREACH, MALFORMED}.
5. Proposal branch: `git -C <vaultDir> branch --list 'wiki-fix/*'` shows
   `wiki-fix/smoke-2026-07-23` with ≥1 local commit iff any round accepted;
   no remote configured, so never-push holds structurally.
6. Freeze honored: `freeze.json.checkConfigHash` equals
   `cat wiki_lint_check.py loop_verdict.py | shasum -a 256`.
