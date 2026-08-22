---
name: a-tests-message-explaining-the-contract-marks-what-the-contract-omits
description: when a test's assertion message has to explain what the contract means — naming a referent, a dimension, or a scope the contract text never states — the author knew the missing piece and wrote it into the wrong artifact; the test passes, the contract ships ambiguous, and the reader who actually executes it never sees the message
type: gotcha
origin: 2026-08-22 code-as-spec-lens-no-op-bar arc — a mirrored rule sentence shipped saying "this dimension" into an arm that has no such dimension, while the pinning test's own assert message read "must bar declaring the omission dimension a no-op"; two whole-branch reviewers found it independently, and one cited the test message as the evidence that the intent existed
---

A rule sentence was mirrored from one reviewer contract into another. The
trigger clause was carefully localized — the arms govern different material,
and the implementer was told to adapt it. The referent was not: the sentence
still said "this dimension", and in the receiving arm no such dimension
exists.

The tell was sitting in the test the same commit added. Its assertion message
read: *"docs-reviewer.md's code-as-spec lens must bar declaring the **omission**
dimension a no-op"*. The word `omission` — the missing referent — was written
down. In the test. In a string the reviewer executing the contract never sees.

**The generalisation: a test message that explains what the contract means is
a marker for what the contract failed to say.** The author held the correct
reading, needed it to make the assertion legible, and put it in the artifact
that was convenient rather than the artifact that is read. The test then goes
green, so nothing surfaces the gap.

Two things follow.

*When writing the test,* notice when the assert message is doing explanatory
work — naming which dimension, which scope, which of two readings is meant.
That sentence belongs in the contract. Move it there and let the message
merely locate the failure.

*When reviewing,* read the test's messages against the text it pins. A message
richer than the pinned text is a finding about the text, not about the test.
The reviewer who found this one quoted the message as evidence that the intent
existed and had simply landed in the wrong file.

A cheap structural version of the same check: a rule sentence moved between
two documents must be re-read for every pronoun and every bare noun phrase —
"this dimension", "the section above", "that check" — because the referent
travels only if the surrounding structure does. Here the code arm's copy sat
under a `#### D10 — Deletion-First` heading that supplied the antecedent; the
docs arm's copy sat under a top-level section that supplied nothing.

Related: [[a-subtractive-rule-relicenses-everything-it-keeps]] and
[[an-exemption-clause-splits-a-reviewer-population-in-two]], both from the same
family of defects — rule text that reads correctly to its author and fails in
the hands of the agent that must execute it.
