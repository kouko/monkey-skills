---
name: section-gate-must-flag-entry-lookalikes-not-just-matches
description: A section-scoped gate that matches one entry marker (e.g. `- OQ-<n>`) reports clean on unresolved content when the author used a different bullet (`*`, `1.`) — the matcher accepted only its exact grammar and silently treated every non-matching look-alike as prose, so a full unresolved section read as empty; a gate's job is to flag malformed/look-alike entries, not only to confirm well-formed ones
type: gotcha
origin: feat/open-question-dispatch-gate (whole-branch review fix bfb1b79a, 2026-08-14)
---

`check_open_questions.py` scans a plan's `## Open Questions` section and
exits 1 while any entry is unresolved. Its entry matcher accepted only
lines beginning `- OQ-<n> [TOKEN] — …`. The arc's own plan, however,
had authored its open questions with `*` and `1.` bullets instead of
`-`. Every one of those lines fell through `_LOOKS_LIKE_ENTRY` to
ignored-prose, the section read as having no entries, and the gate
exited **0 — clean** on a plan whose questions were all still `[OPEN]`.

The whole-branch review caught it because it read the plan's body, not
the gate's exit code. The per-task suite had not — every fixture used
the exact `- OQ-<n>` grammar, so the look-alike path was never
exercised.

**Why this is a false negative, not a miss.** The scanner ran, the
section existed, the entries were present — the gate simply did not
recognize them as entries. A green here is a *false receipt* of the
same family as [[a-mechanical-check-can-go-green-by-skipping]]: exit 0
quoted as "the plan is clean" retires the very question the gate
stopped answering.

**The general shape.** Any section-scoped gate of the form *"match
entries of grammar G, fail while any is unresolved"* has a third
failure mode beyond agree/disagree: **the author wrote something that
looks like an entry but isn't grammar G** — a different bullet, a
different identifier prefix, a soft-wrapped marker. A matcher that
only confirms well-formed G-lines silently classifies every look-alike
as prose and the section as empty.

**What to do**

- A gate that recognizes one entry marker must ALSO flag lines that
  structurally resemble an entry (a bullet + something bracket-like +
  text) but don't match the exact grammar — those are malformed entries,
  not prose. The matcher's job is to flag look-alikes, not only to
  confirm matches.
- Exercise the look-alike path in the test suite: a fixture using the
  wrong bullet / prefix must turn the gate red, not be silently passed.
- When a section-scoped scanner is new, run it against a real artifact
  of the system (the arc's own plan document) as a fixture — the
  author's actual bullet habits surface there, not in hand-authored
  tests that all copy the "correct" grammar.

Related: [[a-mechanical-check-can-go-green-by-skipping]] — the same
false-receipt family; [[subprocess-red-tests-go-false-green-before-the-script-exists]]
— a sibling false-green, different mechanism.