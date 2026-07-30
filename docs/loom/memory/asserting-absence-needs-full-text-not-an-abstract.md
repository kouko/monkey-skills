---
name: asserting-absence-needs-full-text-not-an-abstract
description: A reviewer finding that says "the source does not contain X" is only as strong as the depth it was checked at — two arms independently called a correct citation unconfirmable after reading only the paper's abstract, the fix they triggered hardened that into an affirmative false denial, and the whole exchange cost two review rounds and shipped a defect worse than the one flagged; assert absence only from full text, and treat a fix prompt that authorises a shallow re-check as the orchestrator's own defect
type: practice
origin: feat-docs-review-blocking-class whole-branch review (2026-07-30), rounds 1-3
---

A `docs/loom/BACKLOG.md` entry cited ICSE 2026 (*Are "Solved Issues" in
SWE-bench Really Solved Correctly?*, arXiv:2503.15223) as reporting
"regressive patches at 11/77 of a manually inspected suspicious-patch
sample". Round 1's two review arms both flagged it 🟡 as unconfirmable —
each had read only the paper's **abstract**, where those terms do not
appear. The orchestrator's fix dispatch then said the abstract was
sufficient ("the PDF returned garbled text for both reviewers, so do not
fight it"), and the implementer wrote an affirmative denial into the
file: *"the paper's own vocabulary throughout is … never 'regressive,'
and its abstract states no '11/77' count."*

Round 2's arm opened `arxiv.org/html/2503.15223` and the ICSE
camera-ready PDF and found **Table 8 (§4.4)**: `Total 77` /
`Incorrect Patches 22 (28.6%)` / `– Regressive Patches 11 (14.3%)`.
"Regressive Patches" is the paper's own category name. The original text
had been correct; the finding was a false positive, and the fix it
triggered was a 🔴 — a stated falsehood where there had been a true
statement. Round 3 reverted it.

A second fact surfaced in the same check and is worth carrying: the
arXiv **abstract-listing page** shows "6.2 absolute percent points" for
both v1 and v2, while the **v2 PDF's own embedded abstract**, the paper's
RQ4 body, and the ICSE camera-ready all say **6.4** — arXiv's metadata
abstract never synced to the corrected version. Two numbers, one paper,
neither wrong: do not "reconcile" them.

**Why:** an absence claim is the strongest shape a citation finding can
take, and it is the one most easily produced by a shallow read — the
searcher sees nothing and reports nothing there. Presence can be proven
by one hit; absence cannot be proven by one miss. This is the audit's own
§4.3 lesson (*"asserting an absolute on the strength of a search whose
results were never read"*) recurring inside the review layer rather than
the authoring layer, and it is the concrete shape of the review-precision
risk measured elsewhere (SWR-Bench, FSE: 16.65% precision for the best
LLM code-reviewer configuration on real PRs) — a false positive did not
merely waste a round, it induced a worse defect than the one it named.

**How to apply:** (1) a reviewer may report "I could not confirm X at the
depth I read" — that is honest and costs nothing; it may **not** report
"X is not in the source" without having read the full text or the
published PDF. Downgrade per R3 instead of asserting absence. (2) When an
orchestrator writes a fix dispatch for a citation finding, never
authorise the shallower re-check that produced the finding — say which
surface must be opened (`arxiv.org/html/<id>`, the venue PDF), and treat
"the abstract is sufficient" in a fix prompt as the orchestrator's own
defect, which is where this instance actually originated. (3) Before
rewriting a cited claim, first ask whether the finding itself is right;
a revert is a legitimate fix and is cheaper than a rewrite that must then
be re-reviewed. (4) When two renderings of one source disagree, record
both with their locations rather than picking one — the next reader will
otherwise "correct" it back.
