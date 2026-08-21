---
name: reading-code-and-running-code-fail-differently
description: Whole-branch review and a cold-agent walkthrough catch disjoint defect classes, so rounds of the first never substitute for one of the second — six review rounds plus 1789 passing tests missed two fail-OPEN defects that three cold agents found in ten minutes, because a reviewer reads the path the author intended and a stranger types the path they guess; conversely the reviewers found unreachable code and prose describing rejected designs, which run perfectly
type: practice
origin: north-star-serves-link / dissolve-direction-layer (2026-08-21) — the user asked for an end-to-end dogfood after six review rounds; its first finding outranked everything the six rounds had produced
---

What six rounds of reading, and 1789 passing tests, did not find:

- `backlog_index.py --store <typo>` printed `OK — every invariant holds`
  at exit 0. An absent directory globs to no entries, so every invariant
  holds **vacuously**. `--ready` reported an empty queue; `--write`
  generated an empty index. A green bought with a typo.
- `--write --store <other-repo>` overwrote the STANDING repo's
  `BACKLOG.md` with the other store's entries, because `--output`
  defaulted to a cwd-relative literal. It destroyed this repo's own
  `BACKLOG.md` during the dogfood.

Neither is subtle. Every reviewer read that code closely; none of them
typed a wrong path, because a reviewer reads toward the author's intent.

The converse holds and matters as much: the reviewers found an unreachable
`raise`, a docstring describing a design the commit had rejected, and a
count that was stale — all of which **run perfectly** and no dogfood would
ever surface.

**Why:** the two methods have different blind spots by construction.
Tests encode the situations the author thought of; review encodes what a
careful reader can infer from the text. Neither covers "what does a
stranger, who does not know the right answer, actually type?"

**One later refinement, from the code-as-spec arc (2026-08-22):** the
converse above holds only for prose with nothing to run. A docstring can
carry an *executable* claim — "an entry whose `name` disagrees with its
stem surfaces under the stem" — and that one was false: the code reads
`frontmatter.get("name", path.stem)`, so the name wins whenever present.
Four people read it without noticing; two reviewers who called the
function found it independently within one round. So split docstring
defects by whether the claim can be produced: a rejected-design
description has no outcome to run and only reading finds it, while a
returns/flag/count/exit-code claim is caught by running it and reliably
missed by reading. Same split as
[[a-number-in-prose-needs-a-test-that-recomputes-it]], one level wider
than numbers.

**How to apply:** on any arc that ships a user-facing surface, run at least
one cold-agent walkthrough before close-out, and give it a real sandbox
with no hints and no permission to ask questions. Two design rules learned
the hard way: tell the agent that a validator rejecting its input is a
finding about the DOCUMENTATION, not its own mistake (otherwise it patches
around the gap and reports success — see
[[dogfood-operator-patches-mask-bugs]]); and sandbox it properly, because
the dogfood's first command destroyed a real file in the host repo. When a
dogfood finding becomes a regression test, that finding stops being a
dogfood — the test locks in one known defect and will never find the next
unknown one. Related: [[a-data-probe-is-not-a-pipeline-dogfood]],
[[process-mechanism-dogfood-via-coldreader-real-commits]].
