---
name: 2026-08-21-code-as-spec-writing-rule-and-its-deferred-ab
description: the standing recommendation for this defect class is the code-as-spec writing rule (Ousterhout's interface-vs-implementation split), replacing the superseded entry's two checkers; its direction-changing layer — applying the rule to skill bodies — is deferred to a pre-designed A/B experiment
status: open
origin: 2026-08-21 code-as-spec-writing-rule arc — supersedes docs/loom/backlog/2026-08-21-checkers-for-load-bearing-superlatives-and-existence-claims.md, whose two checkers this arc did not build
start: the pre-designed A/B experiment on whether the writing rule extends to skill bodies, run against writing-plans's queue-relation-gate paragraph (loom-code/skills/writing-plans/SKILL.md) as the test case
---

- Recommendation, superseding the entry this replaces: the code-as-spec
  writing rule, in Ousterhout's interface-versus-implementation
  formulation. Prose may state what the code cannot show — intent,
  invariants, bounds, trade-offs, rejected alternatives. Prose may not
  restate what the code does show — structure, counts, branches, call
  sites.

- Checker 1 (the superseded entry's proposal requiring a pin on any
  load-bearing superlative in mechanism prose) is DROPPED, not filed.
  It is judgment-type (a human must decide whether a given superlative
  is load-bearing), carries a high false-positive rate, and its
  back-test over-fitted the historical measurement behind it:
  superlatives are not a dominant sub-kind of the defect class it was
  built to catch.

- Checker 2 (the superseded entry's proposal requiring an existence
  claim to be a resolvable path) is DEMOTED, not dropped: extend
  `loom-code/scripts/check_doc_citations.py` rather than build a new
  checker. It stays filed, not built.

- Where the oracle's own capability claims about itself are now pinned
  as standing tests, replacing the probes that used to live only in an
  ephemeral scratchpad:
  `loom-code/scripts/test_oracle_capability_claims.py`.

- The full comparison against every alternative this arc considered —
  RFC 2119, Checker 1, Checker 2, OpenSpec's `/opsx:verify`, and
  applying the rule to skill bodies now — is not restated here; read it
  at `docs/loom/specs/2026-08-21-code-as-spec-writing-rule.md`.

- The deferred A/B, written down here because it existed nowhere in the
  repo. Question it settles: does a skill body lose behavioural force when
  its mechanism sentences are removed under this rule? Subject: the
  queue-relation-gate paragraph of `loom-code/skills/writing-plans/SKILL.md`
  — chosen because its exit-code enumeration has drifted twice, so it is
  where the rule would bite hardest.

- Arms. **A** is the paragraph as it ships today: the four causes of exit 1
  enumerated inline with their remedies. **B** is shape only — which class
  each exit code belongs to, with the detail left to stderr and `--help`.
  Nothing else differs; the surrounding skill is byte-identical across arms.

- Subjects and measure. Cold agents at `haiku` AND `sonnet`, no prior
  context, in a sandbox rigged to make the gate exit 1. The measure is
  behavioural, not stylistic: did the agent fix the thing the gate objected
  to, rather than bypassing the gate, weakening the check, or self-signing a
  pass? Record the transcript, not a self-report.

- Outcomes, committed in advance so the result cannot be re-read after the
  fact: both tiers hold → the rule extends to skill bodies, open that arc.
  `haiku` fails and `sonnet` holds → keep one action sentence per exit code
  and shrink the arc to that. Both fail → do not touch skill bodies; the
  deferral becomes the decision.

- What this experiment CANNOT settle, stated so a later reader does not
  over-read it. A behavioural A/B binds the exact wording that ran
  (`docs/loom/memory/a-behavioral-ab-binds-the-exact-wording-it-tested.md`),
  and its verdict scopes to the string it varied, not to the concept the
  string names
  (`docs/loom/memory/an-ab-verdict-scopes-to-the-string-it-varied-not-its-namesake.md`).
  One paragraph of one skill licenses a change to THAT paragraph. Licensing
  "skill prose" as a class needs several paragraphs across several skills,
  chosen for different prose shapes — an exit-code enumeration, a refusal
  list, a step sequence. Whether to pay for the wider study or accept the
  narrow verdict is a decision for whoever picks this up; it is not decided
  here.
