# Seam contracts — cold-reader dogfood (2026-08-25)

Method: 5 fresh-context agents, each given ONLY the shipped contract text
(loom-code 0.100.0 @ feat/seam-contracts HEAD 774671e8 + fix commits) and a
realistic task in a sandbox. Grading is mechanical wherever possible
(check_seam_coverage.py ground truth; grep on artifacts). Per the repo's
established process-mechanism dogfood method (cold reader + real sandbox).

## Scenarios & results

| # | Role under test | Model | Contract surface exercised | Result |
|---|---|---|---|---|
| S1 | plan author | sonnet | plan-format.md `#### Seam` (authoring) | ✅ first-attempt plan passes `check_seam_coverage.py` exit 0 AND field-microstructure exit 0; Seam declared on both dependent tasks, `payload: none` used correctly for the doc task |
| S2a | plan-document-reviewer Check 20 | **haiku** | Check 20 (run-the-script sole-authority form) | ✅ NEEDS_REVISION + exactly the checker's 2 gaps (probe-not-in-Acceptance; missing `from Task 2` bullet) — no misses, no fabrications |
| S2b | plan-document-reviewer Check 20 | sonnet | same | ✅ identical to ground truth, gap text verbatim from checker stderr |
| S3 | SDD orchestrator packet assembly | sonnet | SDD step-1 adjacency rule + implementer.md slot | ✅ Packet A (producer/owner, own Dependencies="none") RECEIVED the bullet naming it `owner:` + the parser/schema path — the whole-branch-review adjacency fix works cold; Packet B got incoming bullet + path; agent refused to fabricate a path the plan didn't supply |
| S4 | implementer | sonnet | `### Seam contracts` slot + fixed enforcement clause | ✅ `report.py` does `from stations_parser import load_stations` — no hand-rolled second reader; probe output correct (2 lines, int counts via the shared parser's cast) |

Ground truth for S2: running `check_seam_coverage.py` on the violation fixture
yields exit 1 with exactly 2 stderr lines (see fixture-s2-bad-plan.md; the
fixture also contains a duplicated `from Task 1` bullet — the checker's
per-edge identity match reports the MISSING `from Task 2` edge rather than
the duplicate itself, which is the designed behavior).

## Findings

1. **Verifiable-action prose survives the weak model.** haiku's Check-20 run
   equals sonnet's and equals the script's ground truth — consistent with the
   repo's standing lesson that prose pointing at a checkable action holds
   where judgment-shaped prose fails.
2. **The adjacency fix is load-bearing and works.** Before the whole-branch
   fix, a producer task with `Dependencies: none` would have received
   `Seam contracts: none`; the cold orchestrator correctly packed the
   owner-naming bullet into Packet A under the fixed wording.
3. **🟢 grammar edge surfaced by S1 (not fixed here):** for a doc-mirrors-code
   seam (README consuming upstream behavior as prose), the author was unsure
   whether `payload:` means programmatic data only. S1 chose `payload: none`
   (reasonable), but plan-format.md `#### Seam` does not say whether
   documentation content counts as payload. Candidate one-line clarification
   on next plan-format touch; filed in this report only.
4. **🟢 S3 nuance:** when a payload-bearing seam's owner parser path is not
   yet resolvable (owner task not implemented), the cold orchestrator wrote
   "none to cite" instead of fabricating — good default, currently
   convention-only (no contract line prescribes it).

## Artifacts

- artifact-s1-authored-plan.md — cold-authored plan (checker exit 0)
- fixture-s2-bad-plan.md — seeded-violation plan (checker ground truth: 2 errors)
- artifact-s3-packets.md — cold-assembled dispatch packets A/B
- artifact-s4-report.py — implementer output importing the shared parser

Verdict: mechanism behaves as contracted across all four roles; 2 🟢
observations recorded above, neither gating.
