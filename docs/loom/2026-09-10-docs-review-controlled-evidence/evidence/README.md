# Docs-review Luna controlled experiment

## Result

In this fixed three-document corpus, all four human-ratified defects come from
the initial drafts. Luna found seven of eight per-run opportunities (87.5%)
with one unmatched observation among eight observations (12.5%). The two runs
agreed on three of four oracle classes (75% Jaccard agreement).

This is a narrow internal result, not a production benchmark. For ratified
defects in this corpus, initial-draft quality is the primary source. Total
review churn remains unquantified because the unmatched observation was not
adjudicated false. The replay separately shows detection variance: one miss,
one unmatched observation, and a red/yellow severity disagreement.

## Frozen design

- Corpus: the exact Git blobs at `2aae5d8b4c1e3aaf5aac4f8c121af275f70abce2`,
  before the intervention cutoff. `input.txt` is the byte-exact stdin supplied
  to both runs. `corpus-manifest.json` records its SHA-256 digest and each
  source blob; the three `=== DOCUMENT <label> ===` lines are the separators.
- Reviewer: `gpt-5.6-luna`, requested through `codex-cli 0.151.0`. This is
  requested-model CLI evidence; the backend did not directly attest the model.
- Prompt: byte-fixed in `prompt.txt` and fingerprinted in the manifest.
- Repeats: `run-1.json` and `run-2.json` retain the final raw response, usage,
  return code, CLI version, limitation, and observed elapsed time.
- Judgment: `oracle.json` freezes the human grouping and origin decision;
  `metrics.json` exposes numerator, denominator, null populations, and cost.

## Revision attribution

In the pre-rebase lineage, the business and strategy artifacts were both born
in `2aae5d8b…` and have no later modifying commit through this experiment. The
preserved source branch carries the byte-equivalent birth commit as
`7a179e2c…`; `provenance.md` records the lineage mapping. Therefore the four
ratified defects cannot be remediation-introduced: they are present in the
initial revision. The replay separately records detection variance: run 2
missed O2, run 1 added one unmatched observation, and the shared O1 finding
changed severity from red to yellow.

## Limits

- Three hard, related artifacts from one repository are not routine-work
  prevalence evidence.
- The technical artifact had zero ratified expected findings, so its finding
  rate is null rather than 0% or 100%.
- The oracle was adjudicated after seeing both runs, so it is suitable for this
  internal diagnostic but not a blinded external benchmark.
- No Claude cohort was run after the approved pivot; cross-host comparison is
  unavailable rather than silently inferred.
- Raw evidence here preserves the model's final JSON response, not a production
  provider trace. The runner hardening needed for stronger provenance was
  explicitly dropped by the pivot.
