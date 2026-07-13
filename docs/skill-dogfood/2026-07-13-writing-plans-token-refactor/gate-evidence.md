# writing-plans token refactor — skill-refactor gate evidence (2026-07-13)

Target: `loom-code/skills/writing-plans/SKILL.md` 4,440 → 4,086 words (−8.0%).
Gate: `skill-dev-toolkit:skill-refactor` (Q1 equivalence / Q2 ≥10% / Q3 invariants).
Runners: sonnet (deliberately worker-tier — most wording-sensitive detector, per
the repo's explicit-contract-load-bearing-on-weak-tier evidence). Judges: opus ×3
(utility / content / boundary framings, randomized A/B labels per pair).

## Test prompts

`loom-code/skills/writing-plans/test-prompts.json` — 4 prompts: P1 happy-path
(brief→plan), P2 BLOCKED fallback, P3 depth-ceiling stress, P4 gate-skip pressure.

## Round 1 — verdict REJECT

| Pair | J1 utility | J2 content | J3 boundary |
|---|---|---|---|
| P1 | equivalent | equivalent | equivalent |
| P2 | equivalent | equivalent | equivalent |
| P3 | **not_equivalent** | **not_equivalent** | **not_equivalent** |
| P4 | equivalent | equivalent | equivalent |

P3 replicates (n=2/side): baseline 2/2 re-derived the dependency DAG → depth 5 →
shipped a plan; candidate 2/2 refused (rep1 via depth-7 ceiling + empty-recon
sentinel; rep2 via the "No brief upstream" exemption). Outcome split 2-0 vs 0-2 →
treated as a real shift → candidate reverted (stash) per the Iron Law.

**Root cause found on inspection: the P3 prompt itself was contract-invalid** — a
bare Smallest-End-State list with no Problem/Decisions/Out-of-Scope, so it did not
qualify as a brief under the skill's own input contract (candidate rep2 was the
run that caught this). The baseline runs' depth-collapse also marked ASSUMED paths
`Independent: true`, violating plan-format.md's empty-recon sentinel — i.e. the
baseline behavior the candidate "diverged from" was itself non-compliant. An
invalid prompt cannot arbitrate equivalence → prompt fixed (user-approved option
a): contract-valid brief whose 7 steps are strictly sequential by declared
symbol-consumption.

## Round 2 — P3v2 re-run, verdict all-equivalent

Runs (n=2/side, sonnet): baseline p3v2-a/b and candidate p3v2-a/b ALL took the
same route — derived critical-path depth 7 > ceiling 5, refused to emit a plan,
withheld plan-document-reviewer + kickoff briefing, surfaced the two sanctioned
remediations (route back to brainstorming vs split into two ≤5-depth part-briefs),
and stopped to ask the user.

3-judge opus ensemble over both replicate pairs (randomized A/B):

| Judge | Pair 1 (a) | Pair 2 (b) | Overall |
|---|---|---|---|
| J1 utility | equivalent | equivalent | equivalent |
| J2 content | equivalent | equivalent | equivalent |
| J3 boundary | equivalent | equivalent | equivalent |

Representative reasons: same refusal + same two remediation options + same
withheld gates + same ask-user posture; differences wording/verbosity only
(J1); no load-bearing content gap either direction, both carry the
change-folder N/A caveat (J2); "no check or refusal performed by one is
skipped by the other" (J3).

## Final gate state

- Q1 equivalence: **PASS** — P1/P2/P4 3/3 (round 1) + P3v2 3/3 over 2 replicate pairs (round 2)
- Q2 token reduction: 8.0% — RESHAPE band (5–10%); ~12% of the touchable region
  (the §Consuming seam contract = 34% of the file was frozen by design:
  weak-model contract evidence). **User explicitly accepted the weak win.**
- Q3 invariants: PASS — name/frontmatter/deps/subfolder structure unchanged;
  test-prompts.json added (allowed).

## What was cut vs frozen

Cut (maintainer-facing rationale + dupes): no-time-box arXiv derivation,
why-depth-5 grounding prose, Beck bibliographic detail (ISBN/publisher), inline
worked micro-example + parallel-dispatch field semantics (deduped to
`references/plan-format.md`, which already carried fuller versions), flourishes.
Frozen byte-identical: §Consuming a loom-spec change-folder, Red Flags table,
all verdict/guard wording, SUBAGENT-STOP, splitting-framework table.

## Durable lessons (carried into commit trailers / memory per git-memory)

1. A test prompt that violates the target skill's own input contract cannot
   arbitrate equivalence — validate prompts against the skill's intake contract
   before trusting a non-equivalence verdict.
2. Run replicates before believing a single-run divergence on a non-deterministic
   scenario (round 1's 2-0/0-2 split was the deciding evidence, not the first run).
3. Judge verdicts must be persisted at decision time, not reconstructed later
   (this file exists because the whole-branch reviewer caught the round-2
   verdicts living only in session scratchpad).
