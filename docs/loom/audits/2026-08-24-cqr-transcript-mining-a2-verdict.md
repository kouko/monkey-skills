# cqr transcript mining — the A2 verdict (keep the per-task quality arm)

Date: 2026-08-24
Method: mechanical scan of all local code-quality-reviewer subagent
transcripts (agentId joined from Agent tool_use records in
`~/.claude/projects/*/*.jsonl` to `subagents/agent-*.jsonl`), then a
3-agent qualitative classification of a stratified 30-case
NEEDS_REVISION sample (22 sessions). Scan script + row dump lived in the
session scratchpad (`cqr_scan.py` / `cqr_rows.json`, ephemeral); the
method is fully restated here for re-runs.

## Question

A2 from the 2026-08-24 cost analysis: can the per-task
code-quality-reviewer arm be dropped or narrowed (leaving full quality
review to the whole-branch panel), on the hypothesis that its catches
duplicate the spec-reviewer / test suite / branch panel? Prior evidence
pointed that way: `docs/loom/memory/` holds three per-task-review-missed
entries and no independent-catch entry.

## Data

- 614 cqr transcripts (2026-07-23 → 2026-08-23; 179 Jul / 435 Aug).
- Verdicts: PASS 334 (54%) · PASS_WITH_NOTES 169 (28%) ·
  NEEDS_REVISION 89 (14.5%) · no-verdict/delta-confirm 22 (4%).
- Sample: 30 NEEDS_REVISION transcripts, stratified across 22 sessions,
  classified finding-by-finding into QUALITY-UNIQUE / SPEC / SUITE /
  STYLE by three independent sonnet readers (10 cases each).

## Result (n=75 gating findings)

| class | n | share |
|---|---|---|
| QUALITY-UNIQUE (neither spec conformance nor the suite encodes it) | 49 | 65% |
| STYLE (nits that gated via the 2+🟡 rule) | 13 | 17% |
| SPEC (parallel spec-reviewer would also flag) | 11 | 15% |
| SUITE (tests would catch anyway) | 2 | 3% |

Representative QUALITY-UNIQUE catches (from the readers' verbatim
extracts): loom_init.py silently overwriting a hand-written PURPOSE.md;
sec_edgar_client resolving a None accession to a different filing's data
under a fabricated source_form; a pipeline mutation destroying 72% of
leaf-material area with all 225 tests green; multiple mutation-proven
weak regression assertions; a fabricated already-shipped claim in a
durable backlog record refuted against git show.

## Verdict

**A2 is refuted — keep the per-task cqr arm.** 65% of its gating catches
are a defect class nothing else in the pipeline encodes ("spec-conformant,
test-green, and wrong"). The memory-store prior (3 missed / 0 caught) was
survivorship bias: caught defects get fixed and never become memory
entries; only the transcripts hold the denominator.

The 0.75.0 half-decision stands as shipped: cqr stays, already
sonnet-pinned. Remaining cost levers on this arm move elsewhere:

1. STYLE-gating noise (17%): style/citation nits crossing the 2+🟡
   aggregation line force full fix→re-dispatch rounds; a
   severity-class carve-out (style findings recorded, non-gating)
   would cut revision loops without touching the 65%.
2. Reviewer turn/tool budgets (separate arc, already queued from the
   2026-08-24 analysis).

## Honesty about limits

Single-reader classification of the reviewers' own self-reported
verdicts — not re-verified against the underlying diffs. Reader
calibration varied (one group graded 10 style-gating findings, another
zero on comparable cases), so per-class shares carry ±10-point noise;
the 65% headline would not flip within it. Sample is 30/89
NEEDS_REVISION cases; 2 sampled files turned out PASS_WITH_NOTES
(scan-regex noise, flagged by the reader). ~8 borderline items sit on
the SPEC/SUITE/QUALITY line either way.
