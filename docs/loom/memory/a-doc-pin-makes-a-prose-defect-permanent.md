---
name: a-doc-pin-makes-a-prose-defect-permanent
description: When a test pins prose that describes code and the prose is WRONG about that code, the green test stops being a guard and becomes a guarantee the documentation stays wrong — and because correcting the prose then requires editing an assertion, the ergonomics push toward the two worst outcomes (leave the prose, or delete the pin) and away from the right one, which is strengthening the pin to encode the true distinction and proving by mutation that the old wording now fails
type: gotcha
origin: brief-item-addressability arc, whole-branch review (2026-08-13) — a pin required the substring "non-zero" in a gate sentence whose claim that two modes block by one rule had just been falsified against the code
---

A skill file said a coverage gate ran in a second mode "blocking on a
non-zero exit **exactly as above**". Whole-branch review checked that against
the code: the second mode's exit 1 fires for an unresolvable citation only,
while an item nothing cites is warned and the run exits 0. The two modes do
not block by one rule.

A pin guarded that sentence. It asserted the substring `"non-zero"`, and its
own comment stated the claim under dispute — *"the same block-on-nonzero rule
the change-folder mode carries"*. So the documentation defect and the test
agreed, and the suite went green every day **because** the prose was wrong.

**Why this is its own failure mode.** A doc pin's subject is not behaviour, it
is *a description of behaviour*. That makes it the only kind of test that can
be simultaneously honest (it really does fail if the prose changes) and
actively harmful (what it protects is a false statement). Nothing in a normal
audit reaches it: the assertion is not vacuous, the mutation kills, the pin
fails for the right reason. It is wrong about a fact no assertion can check —
whether the sentence it freezes is TRUE.

**The ergonomic trap, which is the practical half.** Once the prose is known
wrong, fixing it turns the pin red. At that moment three moves are available
and two are bad:

- **leave the prose** — the pin "wins", the defect ships, and the next author
  reads the test as evidence the wording is deliberate;
- **delete the assertion** — the prose gets fixed and the guard is gone, so
  nothing stops the same flattening returning next quarter;
- **strengthen the pin** — rewrite the assertion to encode the TRUE
  distinction, so the corrected prose passes and the old wording fails.

The third is correct and is the one the situation argues against, because it
reads at a glance like editing a test to make a change pass — the exact
anti-pattern every review guard is trained to stop. Say out loud in the commit
and in the delta packet WHY this edit is a strengthening, and prove it: revert
the prose to its old wording and show the pin fails by name. Without that
proof the move is indistinguishable from the anti-pattern, and reviewers are
right to refuse it.

**How to apply.**
1. When a doc pin blocks a documentation fix, do not ask "how do I satisfy
   this pin". Ask **"is the sentence this pin protects true?"** first. If it
   is false, the pin is part of the defect and must change.
2. A pin's comment is a claim, not context — read it and verify it against the
   code. Here the comment stated the falsehood outright, in the file most
   likely to be trusted about it.
3. Prefer pinning the DISTINCTION over pinning a token. `"non-zero"` was a
   token that any wording could carry; asserting that the sentence names both
   what blocks and what does not is a property the false wording cannot
   satisfy.
4. Every strengthened doc pin ships with its mutation: the old sentence
   restored, the pin failing, the name of the failing assertion quoted. That
   evidence is what separates strengthening from weakening.

Related: [[a-test-can-pin-behaviour-with-a-false-rationale]] — there the
assertion is true about the code and the stated REASON is false, so the
production scope inherits the error; here the assertion is true about the
PROSE and the prose is false about the code, so the documentation inherits it.
Same root shape (a justification nobody verified), opposite artifacts, and
neither detection finds the other. Also
[[prose-contract-mechanism-transcribes-from-code]] (the upstream habit that
prevents this: derive the pinned wording FROM the code rather than pinning
whatever the author typed) and
[[splicing-into-a-pinned-sentence-creates-false-readings]].
