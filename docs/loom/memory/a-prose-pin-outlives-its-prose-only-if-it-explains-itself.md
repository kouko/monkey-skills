---
name: a-prose-pin-outlives-its-prose-only-if-it-explains-itself
description: A test pinning a rule's wording is a golden test at string granularity, and golden tests die by being re-approved rather than investigated — so when an unrelated refactor deletes the prose, the pin goes red and is deleted in the same commit as noise; the only available defence is wording, since no tooling detects it, so the pin's docstring and every failure message must say what the reader is about to delete and that removing it needs an intent
type: practice
sources:
  - resource: 2026-09-11, memory-timing arc — the 2026-07-08 timing rule was enforced by instructions in a skill plus a test pinning them; the loom 1.0 cutover deleted the skill and both went out together, unnoticed, and the rule survived only as prose no installed plugin ever read
  - resource: 2026-09-11 verification of industry practice — asserting that prose still contains required phrases has no established name or practice; the nearest documented relative is golden/snapshot testing, whose known failure mode is blind update
---

A rule was written into a station's text and pinned by a test. Fourteen
months later a cutover deleted that station. The instruction and the test
left in the same commit, nothing went red, and nobody noticed for two more
changes — each of which reached merge before anyone thought about the rule
the deleted test had been protecting.

**This is the documented failure mode, not bad luck.** A phrase-presence
assertion over prose is a golden test whose granularity happens to be a
string. The literature on golden and snapshot tests names one way they
die: a red one gets re-approved instead of investigated, because the
cheapest response to *"the file no longer contains X"* is to stop asking
for X. When the refactor deleting the prose is unrelated to the rule, that
response looks obviously correct to the person making it — they are
removing a file, and the test is an artifact of the file.

**No tooling exists for this.** The practice has no name. Prose linters
enforce term substitution, not required-phrase presence; docs-as-code
testing targets links, builds and code samples; license-header checks are
the one accepted required-text case, and they work because the text is
legally fixed and never edited for quality. A rule statement is not that.
So the defence has to be carried by the test's own words.

**What survives is a test that argues with its deleter.**

1. The docstring states **why the clause exists** and **that it has been
   lost before**, with the dates and change numbers. A reader deleting it
   should have to read a history first.
2. Every failure message says what is missing *and* that removing it
   deliberately is a contract change needing an intent — not a nit to be
   silenced.
3. Pin required **elements after flattening whitespace**, never whole
   sentences, so a rewording that keeps the rule stays green. A pin that
   fires on legitimate edits trains the reader to ignore it, which is the
   same death by a faster road.
4. Pair it with a reader. A string assertion detects deletion and nothing
   else; a clause kept but drained of force stays green forever. Dilution
   needs a cold agent given only that clause and one real case.

**How to apply.** When a rule must live in shipped prose, ship three
things together: the clause, a pin that explains itself, and a frozen
cold-reader run. Two of the three are not enough — the pin alone misses
dilution, and the eval alone does not run on every push.

Related: [[a-doc-pin-makes-a-prose-defect-permanent]] — the opposite
hazard, a pin protecting a sentence that is false; here the sentence is
true and the pin is what goes missing. Also
[[a-prose-literal-assertion-is-false-green-until-it-flattens-whitespace]]
(the mechanical prerequisite for any of this) and
[[a-pin-that-cannot-see-markdown-reshapes-the-prose-it-pins]].
