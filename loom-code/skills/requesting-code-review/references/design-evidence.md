Source: `requesting-code-review/SKILL.md` and `loom-code/agents/code-reviewer.md` — maintainer-facing evidence extracted from SKILL.md's §Verdict structure and §Process, and from the agent contract's dimension sections — serves `requesting-code-review`.

# Design evidence — author-facing, do NOT load at runtime

This file is author-facing: it exists for maintainers reviewing or redesigning this skill's panel-width and aggregation decisions. Runtime agents executing `requesting-code-review` do NOT load this file at runtime — the rules these fragments qualify already stay inline in their own host — SKILL.md, or the agent contract each entry names; only the supporting citations and archaeology live here.

## Exit clause (originally §Verdict structure)

**Exit clause**: if false positives start accumulating, or the two arms are persistently byte-redundant (no incremental recall from the second arm), re-evaluate panel width against the G4 baseline.

## Panel union — supporting evidence (originally the tail of the §Verdict structure "Panel union" note)

The rule sentence itself ("each arm's own `verdict:` is advisory only — the gate verdict is produced by applying the aggregation rule above to the union of both arms' findings, never by picking one arm's verdict") stays inline in SKILL.md — it is pinned. This is its evidence tail: Evidence: G4 A/B — a single-Sonnet verdict missed the correct call 1-of-2 times, while union-aggregation over both arms reproduced the correct verdict with zero false positives across all 4 tested arms (`docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md`).

## Process Step 2 — calibration note

The historical G4 measurement used inherited session models. Current dispatch
policy is the portable profile in `using-loom-code/references/dispatch-profile.md`;
that evidence does not prescribe a host model or override its resolved tier.

## Process Step 3 — union-merge supporting evidence

The rule it qualifies ("no cross-arm adjudication layer is needed") stays inline in SKILL.md §Process Step 3. Its supporting parenthetical: zero false positives measured across G4's 4 arms, report §Scorecard, plus the two same-day panel deployments recorded in PR #503/#504.

## Deletion-first no-op-bar — supporting evidence (originally `agents/code-reviewer.md`, deletion-first dimension)

The rule it qualifies ("a diff that adds or changes any docstring or comment line makes this dimension never a no-op") stays inline in `agents/code-reviewer.md`. Its evidence tail: a measured run on the code arm scored a dimension PASS with no findings in a way indistinguishable from never applying the lens (`docs/loom/specs/2026-08-22-code-as-spec-lens-no-op-bar.md` §Decision).

## Correctness — runnable-claim precedent (originally `agents/code-reviewer.md`, correctness dimension)

The rule it qualifies ("a stated count is one shape of runnable claim, and returns, flags, orderings and exit codes are the rest") stays inline in `agents/code-reviewer.md`. Its precedent: two reviewers imported a metric a document quoted and ran it (`docs/loom/memory/a-number-in-prose-needs-a-test-that-recomputes-it.md`).
