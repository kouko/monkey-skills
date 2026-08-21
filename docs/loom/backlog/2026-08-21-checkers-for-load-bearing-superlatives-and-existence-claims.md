---
name: 2026-08-21-checkers-for-load-bearing-superlatives-and-existence-claims
description: two cheap mechanical checkers against the defect class that cost the dissolve-direction-layer arc four review rounds — a load-bearing superlative (the one / every / always / only) in prose describing a mechanism must carry a pin, and an existence claim (filed as backlog work) must be written as a path a checker resolves; RFC 2119 keyword discipline was evaluated and rejected for this class because it disambiguates obligation strength, not factual accuracy
status: open
origin: 2026-08-21 dissolve-direction-layer close-out — kouko asked whether a writing standard such as RFC 2119 could converge the arc's recurring prose defects; back-testing the arc's own findings put RFC 2119 at 0/8 and these two checkers at 6/8
start: the next time a skill or script's prose is caught by review overclaiming its mechanism, or the next arc that touches the repo's lint/hook layer for any other reason
---

- Start: the next time a skill or script's prose is caught by review
  overclaiming its mechanism, or the next arc that touches the repo's
  lint/hook layer for any other reason

- Origin: 2026-08-21 dissolve-direction-layer close-out — kouko asked
  whether a writing standard such as RFC 2119 could converge the arc's
  recurring prose defects; back-testing the arc's own findings put RFC 2119
  at 0/8 and these two checkers at 6/8

- Why RFC 2119 is the wrong instrument here, recorded so it is not
  re-proposed: it disambiguates OBLIGATION STRENGTH (`MUST` vs `SHOULD` vs
  `MAY`). Every prose defect this arc shipped was a FACTUAL claim about a
  mechanism, stated with complete confidence and wrong — "this is the ONE
  home of the guard" (there were four), "a leg that fails when a script
  grows a read" (it did not), "filed as backlog work" (it was not),
  "validate EVERY entry" (it validated live entries only), "exit 1 for one
  of two causes" (there were four). Capitalising the modal verb rescues
  none of them. The repo's four-level SELF/MUST/SHOULD/MAY gate vocabulary
  stays correct where it is used — quality gates — because obligation
  strength is genuinely what is at stake there.

- Checker 1 — **a load-bearing superlative needs a pin.** When `the one`,
  `every`, `always`, `only`, or `never` appears in prose describing a
  mechanism (a module docstring, a skill's contract paragraph), require a
  test that pins it, or block. Back-test: catches the "ONE home", the
  "validate EVERY entry" reversal, and both revisions of the completeness
  leg — 4 of the arc's 8 prose findings. The mechanism is secondary to the
  effect: being made to write the pin is itself the verification. The
  author who wrote "the ONE home" would have discovered the other three
  copies while writing the test.

- Checker 2 — **an existence claim must be a path.** "Filed as backlog
  work", "documented elsewhere", "covered by a test" must name a path a
  checker resolves. Back-test: catches 1 of 8, and that one shipped in the
  entry filed to be the honest ledger for another finding.

- Not covered by either (2 of 8): a docstring pointing at a callee whose
  contract changed in the SAME commit. That needs a process step, not a
  checker — when a function's contract changes, grep the file for every
  sentence naming it. Recorded in
  `docs/loom/memory/prose-shipped-with-a-mechanism-describes-the-road-not-taken.md`.

- Shape when it happens: both are grep-plus-a-rule, tens of lines, and both
  fit the existing hook layer. Checker 2 is the cheaper and higher-precision
  of the two; do it first. Scope them to contract-class prose (skills,
  agents, script docstrings) — record-class documents under `docs/` are
  narrative and must not be linted this way.
