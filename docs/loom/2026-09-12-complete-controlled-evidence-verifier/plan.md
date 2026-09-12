# Complete the controlled evidence verifier — plan
intent: 2026-09-12-complete-controlled-evidence-verifier@a4a98bbb9
charter: 1.0

## Current State Evidence
- Forward: `evidence/verify_evidence.py:main` checks selected hashes, counts, elapsed time, and unmatched-observation semantics.
- Reverse: prior terminal reviewers found published rates, token totals, source blobs, and lineage incompletely recomputed.
- Error: `verify_evidence.py:52` subtracts one from a derived count but never runs verification against mutated evidence.
- Data: `evidence/metrics.json` contains aggregate rates, per-run rates, agreement, elapsed time, and four token totals.
- Boundary: `evidence/provenance.md` pins pre-rebase and preserved commits; the verifier remains local to this fixed experiment.

## Task DAG

### Wave 1 — complete the fixed-record verifier

**W1-01 Recompute the complete published record**  acceptance: 1,2
- Files: docs/loom/2026-09-10-docs-review-controlled-evidence/evidence/verify_evidence.py
- Test: A1 positive: pinned-inputs; negative: manifest-codrift. A2 positive: all-metrics-recomputed; negative: altered-rate-or-token.
- Risk: agent-decided — pin only this experiment's approved constants and derive every reported value from raw evidence; avoid a generalized framework.

**W1-02 Verify lineage and real mutation rejection**  after: W1-01  acceptance: 3,4,5
- Files: docs/loom/2026-09-10-docs-review-controlled-evidence/evidence/verify_evidence.py
- Test: A3 positive: lineage-and-blobs; negative: wrong-mapping. A4 positive: mutations-rejected; negative: coupled-change. A5 positive: scoped-probe; boundary: forbidden-paths-absent.
- Risk: agent-decided — use temporary copied records for mutations and read Git objects only by pinned identifiers; never inspect excluded paths.

## Questions asked
1 — what — 請確認：你要補齊這個固定實驗的 verifier，讓它獨立驗證固定 SHA、全部 metrics、來源 lineage 與真實 mutation rejection；不重跑 Luna、不恢復 production runner、不碰 `dbt-redshift` 或 `.transactions/`。Review 通過後，授權非強制 push 並建立 Ready PR；merge 仍另行決定。對嗎？（答：對）
1 — what — 這個新 intent 仍然不使用 Claude 作為跨 vendor 第二讀者，對嗎？（答：不用第二讀者）

## Risks
1. The verifier executes Git reads for pinned objects; missing historical objects must fail clearly rather than weakening lineage validation.
2. Mutation checks must alter temporary copies only, leaving the committed experiment record unchanged.
