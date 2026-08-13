---
name: a-silently-skipped-edit-reports-as-a-completed-one
description: Tools that no-op on a non-match instead of erroring turn a skipped fix into a reported one — a Python str.replace whose search string differed by one word left a correction applied to one of two files while the run reported success, and a mutation-battery slice that matched the wrong `EOF` produced syntactically broken mutants whose failures were reported as kills; prefer the tool that errors on a non-match, and verify the fix landed rather than that the command exited
type: practice
origin: mechanize-memory-store-integrity-gate whole-branch review (2026-07-31), rounds 3-4
---

Two instances in one branch, both in the *verification* layer rather than the code under test:

1. **A prose correction applied to one of two files.** The same wrong citation appeared in a hook and its test module. A Python script did `t.replace(old, new)` on both. The hook's actual text read `followed the prose`; the search string said `followed prose`. `str.replace` returns the string unchanged on a non-match, so the script printed "corrections applied" while the hook kept the wrong citation. Review caught it a round later — by then the two files stated the same history two incompatible ways.

2. **A mutation battery reporting kills that were syntax errors.** The battery cut a heredoc with `orig.index('EOF\n', start)`, which matches the `EOF` in the *opening* `cat >&2 <<EOF` line, not the closing delimiter. Every "mutant" was a script with its heredoc head removed and its body promoted to shell commands. The reported `2 red` was bash failing, not an assertion discriminating — and it was cited in a comment as evidence that two assertions were load-bearing. Re-run with the correct delimiter (`'\nEOF\n'`), the honest result was `1 red`, and the mutation that actually isolates those assertions is a different one entirely.

**Why:** both tools fail by doing nothing, and doing nothing is indistinguishable from success at the call site — the script exits 0, the batch prints its summary, the suite still runs. The damage is worse than a plain miss because the run *produces a report*, and the report is then quoted downstream: a comment asserting test coverage, a convergence claim to a reviewer. Neither instance was caught by the thing that should catch it — the first survived a whole review round, the second was caught only because a reviewer traced which stream `$REPORT` reaches.

**How to apply:** (1) For file edits, prefer the tool that errors on a non-match (this harness's `Edit` refuses; `str.replace`/`sed -i` do not) — and when a script must do it, assert the text changed, don't assume. (2) After any batch edit, grep for what should now be *absent*; "applied" is not evidence, absence is. (3) A mutation battery is code under test too: check each mutant still parses (`bash -n`, `py_compile`) before believing its result, or a broken mutant reads as a kill. (4) When a mutation is cited as proof that an assertion is load-bearing, confirm the assertion is the one that failed — not merely that the suite went red, since an earlier assertion failing first hides the one you meant to test.
(5) **When the edited artifact is DERIVABLE from a source of truth — a diagram
from `Dependencies` fields, an index from entries, a mirror from an SSOT —
regenerate it and assert set equality in BOTH directions, rather than patching
and grepping.** Rule (2) is necessary but not sufficient here: an absence grep
finds residue that survived, and is structurally blind to an element that was
silently never written. Both failure modes shipped together in one edit and
only one was greppable — see the third instance below. Related:
[[a-test-can-be-correct-and-still-unable-to-fail]],
[[construction-guaranteed-invariant-proves-nothing]],
[[a-shared-index-file-is-regenerated-from-entries-never-hand-merged]] (the same
regenerate-don't-patch instinct on a different artifact).

**Third instance (2026-08-13, brief-item-addressability arc): the entry existed
and did not prevent the recurrence, and it under-specified the remedy.** A
plan's task-flow diagram was renumbered by `str.replace`. Two defects shipped
from one edit:

- a `:113 → :121` substitution that **matched nothing** and was then reported
  in a delta packet and a commit message as though it had — instance 1 of this
  entry, verbatim, one arc later;
- a rename pattern that matched arrows *into* the old labels but not arrows
  *from* them, leaving two phantom source nodes AND silently dropping one edge
  the `Dependencies` fields declared.

Rule (2) would have caught the phantom nodes (grep the old label). **Nothing
would have surfaced the dropped edge** — no residue was left to find. The fix
that catches both is rule (5): the diagram was regenerated from the
`Dependencies` fields and `drawn == declared` asserted, 19 edges, before
commit.

**Not in this entry, deliberately:** a third edit in the same arc retitled a
Notes bullet and thereby deleted the antecedent its own next sentence depended
on. That replacement *fired correctly*; the damage was collateral to
surrounding prose, and its detection is re-reading the neighbours, not an
absence grep. It belongs with
[[a-rule-edit-falsifies-the-unchanged-prose-composed-with-it]]. Folding a
no-op failure and a semantic-neighbourhood failure under one "string surgery"
heading would blur two classes with different detections — a distinction drawn
by the reviewer who declined to let this entry absorb it.
