---
name: 2026-08-03-origin-arc-close-out-residue
description: small claim-accuracy items filed at the finding-origin-attribution arc's close-out, each a one-clause edit that a fifth review round would have cost more to catch than to fix later
status: open
origin: the finding-origin-attribution arc (loom-code 0.45.0), whole-branch review rounds 4-5 — carried forward under the PASS_WITH_NOTES rule rather than fixed, to stop a fix-generates-findings loop
start: the next time anyone opens one of the named files for another reason
---

Five whole-branch review rounds ran on this arc. Round 5 returned PASS on the
code arm with zero findings and PASS_WITH_NOTES on the docs arm; the union
auto-proceeds under `finishing-a-development-branch`'s rule, carrying the
notes forward. These are those notes.

Every earlier round's findings were born in prose the previous fix pass wrote
while justifying itself. Each item below is a one-clause edit, and each edit
would write new prose — which is why they are filed rather than applied on the
way out the door.

## ✅ RESOLVED — the plan's `Reuse-adequacy` bullet cited a policy its source does not state

**Struck 2026-08-03.** The bullet now says outright that
`plan-format.md` §`Reuse-adequacy` records no refresh policy in either
direction, that its present-tense `Observed` wording if anything leans the
other way, and that as-of-authoring is **this plan's own recorded choice**
(`docs/loom/plans/2026-08-02-finding-origin-attribution.md:78-95`). The
prescribed clause is what shipped — and, exactly as this entry's own preamble
predicted, it arrived alongside new prose: two line-range citations and a
verbatim quote. No marker was refreshed. Kept as a struck record rather than
deleted because the three 🟢 below are still open under this same entry. The
original finding read:

`docs/loom/plans/2026-08-02-finding-origin-attribution.md:80` explains why the
plan's eight `read <file>:<line>` markers are deliberately not refreshed
against HEAD, and attributes the convention to
`writing-plans/references/plan-format.md` §`Reuse-adequacy`. That section
states no refresh policy either way — and its "State, in the present tense,
what the helper does **today**" leans the other direction.

The decision is defensible; the attribution is invented. Reviewer's own words:
*"a correct decision propped up by an invented attribution"* — this arc's
recurring shape in miniature. The fix is one clause: say that `plan-format.md`
records no refresh policy and that as-of-authoring is this plan's own recorded
choice.

## 🟢 One surviving twin of a narrowed absolute

`loom-code/CHANGELOG.md:42` still says verification runs "ahead of every early
return". Narrowed correctly twelve lines below (`:54`) and in
`gate-markers-spec.md:91`, but this copy survived. One early return does
precede recording — an unreadable verdict file returns 4 first. The same
narrowing already written below closes it.

## 🟢 One raw count in the dogfood is not re-runnable as printed

`docs/loom/dogfood/2026-08-02-transcript-corpus-feasibility-probe.md:12` now
correctly scopes its re-runnability claim to raw counts, but the
`639 PASS / 138 NEEDS_REVISION` split at `:77` is not among them — `scan()`
increments one counter and `main()` prints a total, so re-running reproduces
777 and not the split. Disclosure-shaped, not misleading.

## 🟢 A stale numeral in a warning helper

`loom-code/scripts/loom_gate_markers.py:488-491` says "the three observed
shapes" and then lists four. The list is correct — it is exactly the four
cases the narrowed lock catch handles — and only the numeral is stale. It
predates the round-4 delta, so rounds 1-4 saw it; recorded here so the next
person to open that hunk fixes it in passing.

## Also carried: two items reviewers rated next-touch rather than defects

- The ledger's unlocked fallback is lossy by design and the artifact does not
  say so — twelve forced-fallback processes recorded six rounds numbered
  contiguously, so a later reader sees a clean sequence with no gap. A
  `"lock": "unlocked-fallback"` key on the round envelope would make the
  sample's lossiness legible to the consumer the ledger exists to serve.
- A duplicate `dimension:` is recorded byte-identically to an absent one,
  where duplicate `origin:` earned its own label. Both fail closed to the code
  arm and both now refuse the mint, so nothing is wrong; the asymmetry is
  simply unexplained.
