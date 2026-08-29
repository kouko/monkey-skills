---
name: 2026-08-28-decide-whether-the-prose-assertion-volume-itself-should-shrink
description: The pin-granularity branch made the ~740 markdown assertions accurate but not fewer; the original concern was that there are too many of them, and that question is still open
status: closed
origin: pin-granularity migration (2026-08-28) — the branch answered "are these pins accurate?" and left "are there too many of them?" untouched
start: next time the prose-test suite feels expensive to maintain, or before adding a new class of prose test
---

Closed: amnesty-2026-08-30 (bulk cleanup, not per-entry adjudicated)

## What is open

The maintainer's original question was about VOLUME: over a thousand
assertions against skill prose, with no evidence they earn their keep. The
work that followed measured ACCURACY instead and acted on that — the branch
converted wording pins to invariant pins, ending at 481 test functions
(unchanged) and ~738 markdown assertions (down ~57, and most of that
difference is assertions rewritten into a form the counter does not see, not
assertions removed). Nothing about the volume question was settled.

## What is already known, so the next pass does not re-measure it

- **Mutation measurement (n=11 cells, 3 skills).** Wording pins produced 4
  false alarms and **0 blind spots**. 8 of 12 mutations changed no behaviour
  at all: a rule survives losing any single sentence because neighbouring
  sentences carry it. Only rule-level deletion or inversion moved behaviour.
- **The two real regressions were caught by prose pins and by nothing else.**
  A structural-only suite (frontmatter, headings, naming) would have caught
  0 of 2. That is the argument against a straight cull.
- **Industry has no precedent for any of it.** Three independent surveys:
  Anthropic's own `anthropics/skills` ships 20 skills with no CI at all;
  14 of 18 third-party plugins installed locally ship no tests; the 2 that
  assert on SKILL.md check frontmatter and heading structure only. Nobody
  pins rule sentences. `claude plugin eval` exists in the CLI (2.1.247) but
  is early-access-gated for this org and could not be run.
- **Raw material**: `PROTOCOL.md`, `PROPERTIES.md`, `FINDINGS.md` and the
  per-variant outputs from that measurement were scratch-only and are gone;
  the numbers above are the surviving summary.

## The actual options

- **B2 — align with industry**: delete nearly all prose-content assertions,
  keep structural checks. Cheap to do, lowest resulting complexity, and the
  measurement says it would have missed both real regressions.
- **Behavioural evals**: what everyone else does instead. Needs
  `claude plugin eval` enablement, or a home-grown `claude -p` transcript
  harness. Costs tokens per CI run, unlike every current test.
- **Do nothing**: the pins are now accurate; the cost is maintenance volume,
  not false alarms.

Deciding this needs a number nobody has: how many of the ~738 assertions have
ever failed on a real change. Git history over the test files plus CI logs
could estimate it, and that estimate is the cheapest next step — not another
migration.

Related: `docs/loom/memory/an-absence-pin-and-a-presence-pin-want-opposite-scopes.md`,
`docs/loom/memory/a-doc-pin-makes-a-prose-defect-permanent.md`.
