# OpenCode v2 acceptance report suite-label fix — plan
intent: 2026-09-29-opencode-v2-report-mislabel-fix@48267532a
charter: 1.1

## Current State Evidence
- Forward: acceptance-test-report.md A1 line says "完整套件測試：506/506 測試通過" — the loader-only suite is not the complete package suite; `python3 -m pytest scripts/ -q` passes 698. (docs/loom/2026-09-29-opencode-v2-scalar-reverify/acceptance-test-report.md:14)
- Reverse: the evidence file already distinguishes the full suite (698) from the loader-specific suite (506); only the report's A1 line retains the mislabel. (docs/loom/2026-09-29-opencode-v2-scalar-reverify/evidence/acceptance-test-evidence.md:20-22)
- Error: codex Round 3 flagged exactly this line as the sole persisting important finding; loom PASSed. No other defect known.
- Data: `python3 -m pytest scripts/ -q` → 698 passed; `python3 -m pytest scripts/test_opencode_loaders.py -q` → 506 passed (both verified this session).
- Boundary: report and evidence must stay Traditional Chinese; loader fix, probes, and attestation stay untouched.

## Task DAG

**W1-01** Fix the A1 suite label in the acceptance test report  —  acceptance: 1, 2, 3
- Files: docs/loom/2026-09-29-opencode-v2-scalar-reverify/acceptance-test-report.md
- Test: A1 positive: loader-specific or full suite stated; negative: not 完整套件測試506; A2 positive: fresh review PASS; negative: codex no A1 flag; A3 positive: only this file changed; boundary: no code test probe modified
- Risk: Wording-only fix; full suite = 698 verified via pytest scripts/ -q.

## Questions asked
- ① — what — 開新 slim episode 修正 acceptance report A1 那一行（「完整套件測試：506/506」→ 載入器專用套件），使用者選「開新 slim episode (Recommended)」

## Simplicity check
- Single-task documentation wording fix — taken

## Risks
1. Fresh closing-review episode gets new 3-digest budget.
2. Prior attestation (de23ae4e0) stale; finalize-review rebuilds on new digest before Ship.