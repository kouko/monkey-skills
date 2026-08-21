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
