---
name: enumerate-every-copy-before-editing-a-claim-and-name-the-leaks
description: Before editing a claim that may exist in more than one place, enumerate the population and record the partition instead of describing it — and know what the sweep will miss: this repo's prose is hard-wrapped so a quote split across two lines matches nothing, a proposition restated in synonyms is invisible to any string search, and a count of a string inside the document stating that count is never stable; the leaks are named because a rule that hides them ships as reliable and misses silently
type: practice
origin: the review-scope-resolver arc (2026-08-03) — the repair-side half of the finding-origin-attribution arc's recurring defect, moved here out of a gitignored HANDOFF
---

The finding-origin-attribution arc's recurring defect was a claim that is wrong,
actionable and silent — six instances, each born in the edit that fixed the
previous one. The last fix pass changed method: grep the whole branch for every
copy of a claim before editing any of it. Residual counts fell to single digits.
That method had never been written anywhere git keeps.

**It works, and the evidence is a near-miss.** Planning the review-scope-resolver
arc, a task was drafted as "rename the helper; no reference survives anywhere in
the repo". Taking the count first turned that into an enumerated partition:
eight hits outside the plan itself, of which only three were the symbol. Two of
the rest were a deliberate same-named duplicate inside a stdlib-only push-guard
hook, private precisely so the hook stays dependency-free — the drafted
instruction, executed literally, would have broken that independence. Three more
were the brief's own prose, which implementation work does not refresh. The
count is what converted a plausible instruction into a correct one.

A third leak, learned the hard way in that same partition: **a count of a
string inside the document stating the count is not stable.** Successive
attempts to state the grand total were each wrong, because every correction
added another occurrence of the string it was counting. State the partition
that drives action; do not state a total that includes the sentence stating
it.

**The leaks, all observed live, all in the same session.**

- **Hard-wrapped prose defeats single-line grep.** Sweeping for copies of a
  quoted sentence returned one hit and reported the population as one. There
  were two: the second copy was split across a line break, so no single-line
  pattern could match it. Unwrap before sweeping, or sweep with a multiline
  matcher.
- **Synonyms defeat string matching entirely.** The arc's own record notes a
  proposition restated in different words surviving a string sweep that found
  every literal copy. No string tool closes this one.

**Why:** an edit to a claim is only as correct as the population it was measured
against, and "I grepped it" reads identically whether the population was right
or short. The leaks matter more than the rule: a repairer who trusts a
single-line sweep gets a confident count that is wrong in exactly the direction
that makes the next fix ship a fresh contradiction.

**How to apply.** Before editing any claim that could have copies: (1) run
`python3 scripts/claim_copy_sweep.py --claim "<the sentence>"` — it normalizes
whitespace on both sides, so hard-wrapped copies cannot hide, and it prints the
operative / frozen partition plus its own named leaks. Add `--also "<other
phrasing>"` for every restatement you already know about. **Sweep a phrase, not
a token**: a bare number as the claim returns hits from every document where
those digits meant something else entirely, while a distinctive phrase returns
copies that are actually copies. And **the review's scope is not the claim's
population** — sweeping a stale `file:line` pointer returned copies in documents
a reviewer working from the branch diff never saw, which is the whole reason to
run the tool rather than trust a reader. Neither observation carries a count
here on purpose: this entry is itself in the swept corpus, so any total written
would count its own sentences — leak three, stated below and demonstrated twice
on this arc. (2) write the resulting count into the artifact and
partition it —
which hits change, which must NOT (same-name-different-symbol is the trap), which
are out of scope — rather than writing "every reference"; (3) never state a total that counts
occurrences inside the document making the claim — that number changes with the
sentence stating it, and on this arc every attempt to state one was wrong; and (4) state that the synonym leak stays open, because a rule that
presents itself as complete is worse than one that names its hole.

**This entry is the persistence half only, and that is a deliberate, stated
limit.** The discipline lived until now in a `.claude/handoffs/` file, which
`.gitignore` excludes, plus transcripts that age out — the same "nowhere" answer
that [[an-instrument-can-be-correct-at-every-step-and-still-not-support-its-judgment]]
identifies as the fatal property of a measurement that never persists. Moving it
here fixes where it lives, not what it is.

**The unwrapping half is now mechanised; the obligation half is not.**
`scripts/claim_copy_sweep.py` (2026-08-03) closes the hard-wrap leak. Measured
live on this corpus, re-runnable as printed:

```
grep -rln "architectural blast radius" --include='*.md' .   # contiguous
python3 scripts/claim_copy_sweep.py --claim "architectural blast radius"
```

The sweep returned every file the grep returned **plus** files the grep
reported as clean — one of those being this very entry's sibling
[[verbatim-phrase-guards-break-on-hard-line-wrap]], whose copy of the phrase is
split across a line break. No total is stated here on purpose:
the first attempt at this passage quoted one, and the count moved between two
runs minutes apart because writing the passage added the phrase to the corpus
it was counting. That is leak three, live. Re-run the command rather than
citing a figure.
The sweep additionally separates operative hits from history (plugin
CHANGELOGs, in that run), because
[[big-rename-operative-frozen-sweep]] records an automated sweep rewriting
history into self-contradiction. It reports and never edits, for the same
reason. **Nothing still obliges a repairer to run it** — that was left open
deliberately rather than added as another gate; the synonym leak likewise
stays open by nature, and `--also` only covers restatements you already know
about.
[[pin-shared-wording-in-plan-copies-transcribe-from-pin]] is the prevention-side
sibling: it stops copies from diverging when you already know a wording will fan
out; this entry is for the copies you did not know about.
