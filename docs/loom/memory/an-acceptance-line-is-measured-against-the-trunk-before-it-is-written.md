---
name: an-acceptance-line-is-measured-against-the-trunk-before-it-is-written
description: An acceptance line that asserts a property of the system ("X still works without Y") can describe something the trunk never satisfied either — it then cannot be met by any amount of work on the change, and the discovery arrives at the blind run, after the branch is built; measure the property on the trunk first, and when it is already false, write the line as the delta the change actually owns
type: practice
sources:
  - resource: 2026-09-11, loom-memory relocation arc — Acceptance 5 asserted two sibling plugins' suites stay green without a third; verified on origin/main that four pre-existing cross-plugin reads made it false there too, so the line had never been satisfiable
---

An acceptance line is normally a promise about the change. A line of the
form *"A still works without B"* is not: it is a claim about the system,
and the change may have nothing to do with whether it holds.

One such line asserted that two plugins' test suites stay green when a
third is absent. The blind run found them failing — and then found the
same four failures, verbatim, on `origin/main`. Four pre-existing
cross-plugin file reads had always been there. The property had never been
true, so no implementation could have delivered it, and the line's failure
said nothing about the change at all.

**Why this is not caught by review.** Every reviewer checks the line
against the diff. The line is about the *baseline*, and the baseline is the
one artifact a change review never opens. It passes intake, passes
planning, passes implementation, and fails at the blind run — the most
expensive place to learn it, because by then the branch is built.

**The repair is a narrowing, not a deletion.** The honest replacement is
the delta the change actually owns: *"this change does not make it worse"*,
proven by showing the failures are identical before and after. That is
weaker than the original line and it is true, which the original was not.
Deleting the line instead would hide that the property is absent; keeping
it would fail the change for something it does not control.

**How to apply.**
1. Before writing an acceptance line that asserts a property rather than a
   change, **run it against the trunk.** One command, before the intent is
   confirmed.
2. When it is already false there, say so in the intent and write the line
   as a delta — and record the measurement, so the next person does not
   re-derive it.
3. A line that fails identically on the trunk and on the branch is not a
   finding about the change. Verify that identity explicitly rather than
   assuming it; "pre-existing" is a causal claim and is often wrong.
4. The residual property deserves its own intent. Narrowing the line is not
   the same as deciding the property does not matter.

Related: [[a-worker-that-blames-preexisting-state-is-often-naming-its-own-damage]]
— the mirror image: there an agent wrongly *claims* pre-existing breakage,
here the breakage genuinely is pre-existing and nobody had measured it.
Also [[an-absence-claim-in-a-plan-is-a-hypothesis-not-a-fact]].
