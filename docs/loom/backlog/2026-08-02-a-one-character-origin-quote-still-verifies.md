---
name: 2026-08-02-a-one-character-origin-quote-still-verifies
description: the origin field's anti-fabrication property rests on a quote being hard to invent, but the validator accepts any non-blank substring, so a one-character quote verifies against almost any file and counts as a genuine origin
status: CLOSED — SUPERSEDED
origin: Task 2 of the finding-origin-attribution arc (docs/loom/plans/2026-08-02-finding-origin-attribution.md), code-quality review round 2 — routed to the user rather than fixed in-task
---

## Superseded 2026-08-02 — the decision below was taken: no floor

The decision `## The decision to take` asked for has been made, and this
entry is kept as the record of the question rather than as an open item.
The user chose **no length or width floor** (plan
`docs/loom/plans/2026-08-02-finding-origin-attribution.md` §Notes,
"Amendment 2026-08-02, user decision — no length or width floor"), and Tasks
3-5 already shipped that grammar verbatim into `code-reviewer.md`,
`code-quality-reviewer.md`, and `requesting-code-review/SKILL.md`. Option
(b) below was tried — four separate constraint shapes, in fact, not the one
sketched here — and none of them shipped: see
`docs/loom/backlog/2026-08-02-quote-informativeness-needs-corpus-selectivity-not-length.md`
for the measurement that closed the length/width axis entirely and for the
corpus-selectivity mechanism that is now the open successor to this
question.

## What follows is the original entry, kept for context

## The residue

The whole design rests on one property: a reviewer cannot name an upstream
document as the origin of a defect without having read it, because the quote
is grepped. Three shapes have already been closed — an empty quote `""`, a
directory path whose `git show` output is a git-generated tree listing, and the
constant header word `tree` in that listing. Each admitted a well-formed-looking
origin that verified against something other than document prose.

What remains is the general case the closures narrowed but did not remove.
Measured by the reviewer: `origin: docs/l.md :: "e"` mints, at exact tier, and
would enter the pre-registered ≥40-finding tally as a verified origin. Any
short common substring does.

## Why it was not simply fixed

A minimum-length or specificity rule is a change to the field grammar, which
the plan pins and Tasks 3, 4 and 5 transcribe verbatim into three shipped
contracts (`code-reviewer.md`, `code-quality-reviewer.md`,
`requesting-code-review/SKILL.md`). And the threshold itself is arbitrary —
the Axis-4 research behind the matching decision found that unfakeability comes
from a quote's length and specificity plus a narrow search window, but named no
defensible number.

## What the design already relies on

The brief's stop rule does not treat the counter as self-certifying: it keeps
the field only when **at least one non-`none` origin survives a human check**.
A one-character quote fails that check trivially. So the vector may be an
accepted cost rather than a hole — the tally is a screen, not the verdict.

## The decision to take

Either (a) accept it, and say so in the brief so the next reader does not
re-derive the alarm; or (b) constrain the quote — a minimum length, a minimum
word count, or a requirement that the quote span a sentence boundary — and pay
the pinned-grammar sweep across the three contracts. Option (b) is
substantially cheaper before Tasks 3-5 ship the grammar than after.
