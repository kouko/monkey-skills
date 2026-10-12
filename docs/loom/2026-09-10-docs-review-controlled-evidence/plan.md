# Preserve the controlled docs-review experiment — plan
intent: 2026-09-10-docs-review-controlled-evidence@a3d0be7f9
charter: 1.0

## Current State Evidence
- Forward: `docs/loom/dogfood/2026-09-01-docs-review-luna-controlled-experiment/README.md` on `codex/docs-review-baseline` states the controlled result and limits.
- Reverse: `corpus-manifest.json` on the source branch maps the frozen input to three source blobs at revision `2aae5d8b`.
- Error: source `run-*.json` records return codes, usage, elapsed time, raw responses, and the missing backend model attestation.
- Data: source `oracle.json` and `metrics.json` preserve human grouping, numerators, denominators, null populations, and cost attribution.
- Boundary: current `origin/main` omits the old runner and reusable store; this change preserves evidence only.

## Task DAG

### Wave 1 — preserve and verify the experiment

**W1-01 Preserve the immutable experiment record**  acceptance: 1,4
- Files: docs/loom/2026-09-10-docs-review-controlled-evidence/evidence/*
- Test: A1 positive: required-record-set; boundary: source-byte-digests. A4 positive: evidence-only-diff; negative: forbidden-runner-or-environment-change.
- Risk: agent-decided — copy the source records into the current evidence tree without restoring deleted tooling; provenance pins the old branch and commit.

**W1-02 Recompute and document the result**  after: W1-01  acceptance: 2,3
- Files: docs/loom/2026-09-10-docs-review-controlled-evidence/evidence/README.md, docs/loom/2026-09-10-docs-review-controlled-evidence/evidence/metrics.json
- Test: A2 positive: independent-metric-recompute; negative: altered-observation. A3 positive: attribution-supported; boundary: narrow-corpus-limit.
- Risk: agent-decided — retain the original arithmetic and qualify the conclusion; do not generalize beyond this fixed corpus.

## Questions asked
1 — what — 你要的是：把舊實驗遷移成符合目前 Loom 的純證據變更；保留固定 corpus、Luna、prompt、原始輸入輸出、重跑、人工 oracle、metrics 與 revision attribution，並回答成本主要來自初稿品質還是 review；不恢復 production runner、不碰 `dbt-redshift` 或 `.transactions/`。對嗎？（答：對）
1 — what — 這次要不要用 Claude 當第二位讀者？（答：不需要）

## Risks
1. The records contain approved public vendor identifiers; this cycle permits them, while a future privacy-policy change remains separate.
2. The human oracle was informed by both runs, so the result supports internal diagnosis rather than an externally blinded benchmark.
