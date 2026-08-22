---
name: a-coverage-check-cannot-see-what-the-brief-never-declared
description: brief-item coverage proves every declared item reached a task and is silent about items the brief never declared, so a requirement the repo's own conventions impose — a version bump, a mirrored sibling, an index regen — passes every coverage gate and every plan-review round by being absent rather than unmet
type: process
origin: 2026-08-22 contracts-cite-only-what-ships arc — three rounds of plan review, a 5-of-5 coverage pass and four whole-branch reviewers, and the missing version bump was caught by exactly one arm, in a closing note, after implementation was finished
---

A plan carrying `Brief item covered:` on every task, verified by
`check_scenario_coverage.py`, proves one thing: each identifier the brief
declared is cited by at least one task. It says nothing about whether the
brief declared everything it should have.

That gap has a shape. The requirement most likely to fall through it is one
the repository's own conventions impose rather than the arc's subject matter —
a version bump when a plugin's contracts change, a mirrored edit in a sibling
arm, an index regenerated after a store changes. Nobody writes it into the
Smallest End State because it is not what the arc is *about*; the coverage
gate then reports a clean pass because everything declared was covered.

**Measured on the arc that produced this entry.** Its brief declared five
items; all five were covered; the plan passed three rounds of review, the last
at a higher model tier explicitly asked to find anything left. The plugin's
five contract files changed and `plugin.json` stayed at the old version, which
makes the entire branch a silent no-op after merge. One whole-branch reviewer
found it, in a closing note, after all five tasks were implemented. The
repository already records the specific fact — a PR changing skill content must
bump the plugin version — and had recorded it four times before. Knowing the
fact did not help, because nothing in the pipeline asks the question.

**What to do about it.** At brief time, before the item list is frozen, walk
the change's *shape* rather than its subject: which trees does it touch, and
what does this repo require whenever those trees are touched? A plugin's
`skills/` or `agents/` → a version bump across its coupled sites. A
`docs/loom/` store → its index. One arm of a mirrored pair → the other arm.
Declare those as brief items so that coverage has something to bind to; an
undeclared obligation is invisible to every downstream gate by construction.

The reviewer-side version: when a plan passes coverage, that is evidence about
the plan, not about the brief. Ask what the brief should have contained and did
not — the coverage number cannot raise that question, and three rounds of
review here never did.

Related: [[a-tests-message-explaining-the-contract-marks-what-the-contract-omits]] —
the same shape one layer down, where the missing content was written into the
wrong artifact rather than left out entirely.
