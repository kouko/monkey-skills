# loom family backlog

> SSOT for cross-plugin open items. Convention: one entry per item with
> **start/re-trigger condition**, **origin** (PR / ledger / discussion),
> and **status** (`COMMITTED-NEXT` | `OPEN` | `PARKED` | `UPSTREAM`).
> Plugin-local parks stay in each plugin's README (§parked items with
> re-triggers); this file holds items that cross plugin boundaries or
> have no plugin home yet. Claude-side session memory keeps only a
> pointer here — this file is the durable truth (versioned, host-agnostic,
> greppable). Completed items are deleted, not archived — git history is
> the archive.

## Mechanical-gates v2 candidates (loom-code 0.23.0 follow-ups)
- Status: OPEN
- Start: first fatigue evidence from daily use of the push gate, or next
  git-guard touch — whichever comes first
- Origin: PR #492 final verdict (2 🟢 next-touch) + its Decision trailers
- What: (a) waiver `scope` field checked on the read side (single-scope
  today); (b) git-guard docstring limitations list gains the
  `git -c core.hooksPath` route; (c) **patch-id relaxation** of the
  strict-HEAD-sha review marker — today ANY post-verdict commit forces
  re-review or waiver, which is correct for content changes but costly
  for message-only amends; relax to diff patch-id match if re-review-on-
  amend proves too expensive. First candidate friction datum
  (2026-07-04): docs-only microbranches face the same full
  review-or-waiver cost as code branches.

## TDD Guard pilot + TDD-mining tightenings
- Status: OPEN
- Start: first real SDD venue — same trigger as G4 / Segment-3
  (komado-Viewfinder batch6)
- Origin: harness-engineering audit rec 4
  (docs/loom/audits/2026-07-04-harness-engineering-audit.md) + the
  2026-07-04 three-route TDD-miss mining
- What: mount nizos/tdd-guard (or a loom-built equivalent: hook
  guarantees the check fires, LLM judges) on one real SDD run; measure
  latency / spend / false-block rate → adopt-vs-build decision. Bundle
  the two mining-derived tightenings into the same touch: reviewer
  tests-dimension must flag a zero-new-test feature branch on
  non-carve-out code (miss 3: whole-branch PASS never flagged it), and
  tdd-iron-law carve-outs must be DECLARED before coding, not claimed
  post-hoc (miss 2: "legacy backfill" framing for code shipped untested
  under the workflow's own banner).

## G4 — Sonnet-vs-Fable gate quality A/B
- Status: OPEN
- Start: after the first REAL change runs through the pipeline
- Origin: PR #476 open question; protocol documented in
  loom-pipeline/README.md §G4
- What: same branch reviewed by both model tiers; compare verdict tokens
  + finding severity distributions against a human review. Also settles
  whether the two-valued verdict scheme inflates (untested house
  hypothesis, flagged in the industry research doc).

## validate_design_output.py dual-root mode
- Status: UPSTREAM (loom-interface-design)
- Start: next loom-interface-design touch
- Origin: live-verify finding 4 (report
  docs/loom/dogfood/2026-07-04-loom-pipeline-v1-live-verify.md); the
  validator assumes DESIGN.md + ui-flows.md are colocated, but the
  sanctioned layout (audit #472) splits product-level vs per-change —
  exit 1 is structurally guaranteed. Needs --design-root/--flows-root
  (or equivalent) arguments.

## Segment-3 first live run
- Status: OPEN
- Start: first real change (deliberately NOT burned on a toy — agreed
  2026-07-04; dispatch machinery already proven by the F5 spike and the
  2026-07-03 dogfood)
- What: SDD triads via agentType + whole-branch review + conditional
  ui-verification, driven by the merged driver against a real repo.

## loom-spec station briefing gate (#475 parity)
- Status: OPEN (original 值得做 list item 3, half-covered)
- Origin: 2026-07-03 dogfood — spec station resolved a product decision
  (ending-controls) inline. The pipeline's human gate (b) now covers
  DRIVER runs; loom-spec itself still lacks the brief-before-asking
  escalation for INTERACTIVE use.

## duration-override test affordance → interaction-flows enumeration
- Status: OPEN (original 值得做 list item 4)
- Origin: ui-verification first live run (PR #477 dogfood note) — 4
  states untestable behind a 25-minute wait; pipeline-produced apps
  should be required at design time to expose a test affordance.
  Candidate enumeration item for loom-interface-design:interaction-flows.

## Goal-oriented firing-corpus `expected` narrower than design
- Status: OPEN
- Start: next reuse of docs/loom/firing-corpus/goal-oriented.jsonl, or
  next firing-harness touch
- Origin: PR #489 residual; transcript-check requirement documented as
  trap #6 in the loom-code/scripts/loom_firing_harness.py module
  docstring
- What: every goal-oriented record expects `loom-code:using-loom-code`,
  so fired-skill grading alone cannot catch a design-side on-ramp
  regression (deleting brainstorming's Axis 0 would not move a single
  record off EXACT/FAMILY). The corpus's real acceptance criterion —
  whether the design-side recommendation SURFACES in the transcript —
  is not automated; any reuse must run the F3-style transcript check,
  or the corpus needs `expected` widened to the design-sanctioned set.

## Sibling plugin SKILL.md frontmatter versions lag plugin.json
- Status: OPEN
- Start: next version bump of any sibling plugin, or next touch of the
  manifest-drift tooling (.claude/hooks/check-codex-manifest-drift.sh)
- Origin: PR #490 loom-interface-design agent flag — drift lives in
  SKILL.md frontmatter, not READMEs, so #490's README pass left it
  unfixed
- What: SKILL.md frontmatter `version:` is stale across all three
  siblings (verified 2026-07-06): loom-interface-design 4× 0.3.0 vs
  plugin.json 0.4.1; loom-product-principles 0.3.0/0.1.0 vs 0.4.0;
  loom-spec 0.2.2/0.2.1/0.1.0 vs 0.4.1. Decide the contract
  (frontmatter tracks plugin version vs deliberate per-skill semver),
  then either sync or add a drift gate next to the codex-manifest one.

## #468 reviewer next-touch nits (loom-code TECH-SPEC + CI)
- Status: OPEN
- Start: next loom-code/TECH-SPEC.md touch
- Origin: PR #468 whole-branch reviewer 🟢 next-touch nits (2026-07-02)
- What: freshness-checked 2026-07-06 — (a) dimension-count drift STILL
  PRESENT: TECH-SPEC.md:420 `dimension_scores` lists 6 keys and :261
  says "7-dimension scores" for code-reviewer, whose actual contract is
  10 dimensions (agents/code-reviewer.md description); (b) dual
  path-presentation styles (mixed backtick/plain paths) STILL PRESENT
  in TECH-SPEC.md; (c) loom CI steps sharing one `run:` block appears
  ALREADY FIXED — all four loom-*-ci.yml workflows now run one command
  per step; confirm and drop sub-item (c) at next touch.

## Living-spec deferred debt bundle
- Status: OPEN
- Start: next living-spec script touch
  (loom-code/scripts/living_spec_*.py or check-living-spec-index.py)
- Origin: living-spec index slices 1–4 + capstone G (#447–#455)
  deferred-debt ledger
- What: (a) regex suffix-vocab lockstep — two regexes must move
  together when the suffix vocabulary changes; (b) drift-lane
  tokenize-ization; (c) Rule-of-Three `_matched_files` extraction;
  (d) Open-Q6 ready-signal binding for BOTH merge-boundary gates
  (verify-index + active-coverage).
