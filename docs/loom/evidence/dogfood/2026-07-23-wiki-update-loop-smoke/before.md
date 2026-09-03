# wiki-update loop smoke — before state (T9 prep, RED)

Prepared: 2026-07-24. Sandbox lives in the session scratchpad (NOT committed);
this doc records the frozen before state so the smoke run's delta is auditable.

## Sandbox

- Vault (its own git repo, clean tree, branch `main`):
  `/private/tmp/claude-501/-Users-kouko-GitHub-monkey-skills/50f049ad-d514-4d70-a0d5-6e6a333953b2/scratchpad/wiki-smoke-vault`
- Base commit: `d8f3c4fef8a68302b59535934ac4dc690252140e`
- Run-artifact dir (pre-created, empty):
  `/private/tmp/claude-501/-Users-kouko-GitHub-monkey-skills/50f049ad-d514-4d70-a0d5-6e6a333953b2/scratchpad/wiki-smoke-runs/smoke-2026-07-23`
- 10 pages: 3 clean (`entities/Acme-Corp.md`, `entities/Widget-Standard.md`,
  `concepts/Knowledge-Graph.md`) + 7 seeded.

## Seeded violations (check → file:line, per validator output)

| check | file:line | seed |
|---|---|---|
| L01 | entities/Beta-Industries.md (file-level) | missing `title` (filename-derivable) |
| L01 | journal/2026-07-20.md (file-level) | missing `date` (filename-derivable) |
| L02 | concepts/Data-Pipeline.md:9 | summary 250 chars > 200 |
| L03 | synthesis/Market-Overview.md (file-level) | missing `## Connections` |
| L04 | skills/Wiki-Maintenance.md:18 | path-prefixed `[[entities/Acme-Corp]]` |
| L04 | skills/Wiki-Maintenance.md:19 | `.md` extension `[[Knowledge-Graph.md]]` |
| L07 | synthesis/Market-Overview.md:18 | broken `[[Acme Corp]]` (suggestion: Acme-Corp) |
| L07 | synthesis/Market-Overview.md:19 | broken `[[Nonexistent-Page]]` (no near match) |
| L14 | references/2026-07-19-widget-report.md:12 | error: path-prefixed source link |
| L14 | references/2026-07-18-market-notes.md:12 | warning: stale basename vs source_path stem |

## Validator before numbers

`wiki_lint_check.py <vault>/wiki` → **exit 1**; summary line:
`{"files": 10, "violations": 10, "errors": 9, "warnings": 1, "by_check": {"L01": 2, "L02": 1, "L03": 1, "L04": 2, "L07": 2, "L14": 2}}`
Full JSONL kept at `<scratchpad>/wiki-smoke-runs/before-validator-output.jsonl`.

## RED assertion (plan T9)

The convergence assertion FAILS at this point, as required:

- Validator reports N = 10 > 0 violations (exit 1).
- No ledger / scorecard / freeze record: run dir contains 0 entries.
- No proposal branch: `git branch --list 'wiki-fix/*'` → 0 results
  (only `main` exists); stash list empty.

GREEN is defined by the run card (`run-card.md`, same folder): terminal state
legal, monotone violation counts, zero-deletion diff, ledger + scorecard +
proposal branch present.
