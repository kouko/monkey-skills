# Nine review rounds on one docs branch — where the loom-* review loop failed

- **Date**: 2026-07-28
- **Scope**: one branch (`docs-backlog-resequence-around-hierarchy`, 11 commits,
  documentation only) taken through `loom-code:finishing-a-development-branch`.
  Lens: **why the review loop did not converge**, and which of its failures are
  mechanism gaps versus operator error. Not about the branch's subject matter —
  that is `2026-07-28-revenue-chain-and-hierarchy-audit.md`.
- **Method**: the session's own trajectory, reconstructed from the nine review
verdicts and the remediation commits between them. Every claim below is
  checkable from `git log` on that branch plus the verdicts quoted inline.
- **Status**: observation and PROPOSALS. Nothing here is ratified. Occurrence
  counts are stated per finding because this repo's convention is one occurrence
  → record it, two → consider legislating.
- **Relation to prior audits**: EXTENDS `2026-07-04-harness-engineering-audit.md`
  (prompt-constraint vs mechanism-constraint) with a documentation-artifact case,
  and supplies the first real counter-example to the plan-stage fact-grounding
  change shipped as 0.39.0 the same day (see §4.3). Independent of
  `2026-07-18-agent-loop-convergence-audit.md`, which studied agent loops that
  iterate toward a goal; this one studies a review loop that iterated without
  converging.

## Verdict (one line)

The review loop ran nine rounds without converging because it was scoped to the
diff while the branch's whole purpose was correcting claims the diff did not
touch — and nothing in the loop measured its own convergence, so the cost stayed
invisible until the operator volunteered it.

---

## §1 The trajectory

| round | verdict | blocking findings | where the findings came from |
|---|---|---|---|
| 1 | NEEDS_REVISION | 4 🟡 | original text |
| 2 | PASS_WITH_NOTES | 1 🟡 | **round 1's own remediation** |
| 3 | NEEDS_REVISION | 2 🟡 | one original, one from round 2's remediation |
| 4 (focused) | — | 1 defect | **round 3's remediation** |
| 5 | NEEDS_REVISION | 3 🟡 | two original-but-unswept, one from round 4 |
| 6 | NEEDS_REVISION | 2 🟡 | one unswept sibling, one from round 5 |
| 7 | **NEEDS_REVISION** | **1 🔴** + 1 🟡 | **a claim that predated the branch entirely** |
| 8 | NEEDS_REVISION | 4 🟡 | **original text — none traceable to any remediation** |
| 9 | NEEDS_REVISION | 1 🔴 | round 8's remediation, applied to one of two artifacts |

Nine rounds, no PASS. The defect count did not fall (4 → 1 → 2 → 1 → 3 → 2 → 2 →
4 → 1). **Six of the nine** rounds found at least one defect introduced by the
previous round's remediation — but round 8 broke the pattern, finding only
original-text defects, and that is the round where the scope changed (below).

## §2 The finding that matters most

Round 7's 🔴 was a bullet instructing an implementer to derive `kpi_id` from a
canonical field slug. The shipped code does the opposite — the filer's own qname
verbatim, and its module docstring names the divergence explicitly
(`kpi_us_statements.py:16-31`). The bullet had been wrong since 2.38.0 shipped,
days before this branch existed.

**Six rounds did not see it, and the reason is structural: they reviewed the
diff, and the bullet was not in the diff.** It surfaced only when round 7 was
dispatched with an explicit instruction to read the whole file as a document.

The branch's entire purpose was correcting stale claims in this file. A review
scoped to changed lines is, by construction, blind to the defect class the branch
exists to remove.

## §3 Mechanism gaps

### §3.1 Review scope defaults to the diff, with no whole-artifact mode

**Evidence**: §2. Also rounds 5 and 6, whose worst findings were contradictions
between a changed line and an unchanged line 250+ lines away.

**Gap**: `requesting-code-review` reviews the cumulative branch diff. That is
right for code, where unchanged lines are presumed still-correct because tests
cover them. A document has no tests: an unchanged line is not evidence of a
correct line, only of an untouched one.

**Proposal**: when a branch's changed files are documentation, the dispatch
should default to whole-artifact review with the diff as context, not the
reverse. Cheap form: a line in `requesting-code-review` saying so, plus the
reviewer prompt asking "does any UNCHANGED claim in this file contradict the
change, or the current code?"

**Occurrences**: 1 session, but 3 independent findings within it (rounds 5, 6, 7).

### §3.2 The loop has no convergence criterion, and digests silently

**Evidence**: §1. `finishing-a-development-branch` §Default flow instructs that
"NEEDS_REVISION review loops — fix → re-review … digest silently; the user sees
only the terminal verdict, never each iteration."

**Gap**: that rule is correct for a loop that converges. Applied to one that does
not, it hides an unbounded cost from the person paying it. Nothing counts rounds,
compares defect rates across rounds, or asks whether the defects are getting
smaller.

**Proposal**: digest silently for the first two rounds; from the third, surface
the trajectory AND state a hypothesis for why it is not converging — editorial
(the fixes are fine, more remain) versus structural (the artifact's shape is
generating them). The second reading is what ended this loop, and only the
operator noticing the pattern produced it.

**Occurrences**: 1.

### §3.3 Review dimensions are code-shaped; documentation gets shallow default coverage

**Evidence**: of the 10 dimensions, `security` / `architecture` / `tests` /
`refactoring` / `deliberate-simplification` were vacuous PASS in all eight full rounds (round 4 was the
only focused check, and carried no dimension scores). The dimensions that actually caught things — does a citation resolve to
what the text claims, is a measurement's population stated, does an absolute
("only", "never", "zero") hold — are not dimensions at all. They had to be
written into the dispatch prompt by hand, every round.

**Gap**: a docs branch reviewed with the default prompt would have received five
vacuous PASSes and a shallow read of the rest.

**Proposal**: a documentation dimension set, or at minimum a dispatch addendum in
`requesting-code-review` for docs-only branches naming: citation resolution,
claim-vs-evidence, population statements, absolutes, and cross-paragraph
coherence.

**Occurrences**: 1, but the operator wrote the same four instructions into every
full-round dispatch, which is the signal.

### §3.4 Nothing enforces artifact-type jurisdiction

**Evidence**: the memory charter's jurisdiction table routes a one-off
measurement to `docs/loom/{specs,plans,audits,…}/` and keeps `BACKLOG.md` for
open items. Measurements were written into `BACKLOG.md` anyway. Six rounds later
the reviewer diagnosed the adjacency of narrative and prescriptive text as the
cause of the recurring contradictions.

**Gap**: the table is prose. Nothing reads it.

**Proposal**: the cheapest mechanical form — `dev-workflow:git-memory` already
gates every commit; when a commit adds more than N lines to `BACKLOG.md`, have it
ask the jurisdiction question. This is a prompt-level gate, not a script, and it
fires exactly where the decision is being made.

**Occurrences**: 1 here, but this is the same class as
`2026-07-04-harness-engineering-audit.md`'s central finding (prose constraints do
not bind), so the pattern has prior evidence even though this instance is new.

## §4 Operator errors a mechanism could have caught

Separated deliberately. Calling these mechanism gaps would be self-serving.

### §4.1 Mis-filing the artifact

Mine. The charter was available and unread at the moment of writing. §3.4's
proposal would have caught it, which is why it is proposed — not because the
error was the mechanism's fault.

### §4.2 Fixing the named line instead of the population

Repeatedly across the nine rounds, a finding turned out to be the sibling of an
earlier one, left unswept. Three concrete instances: one struck bullet restored verbatim while its sibling ten lines away
stayed abridged; a cancelled SEQUENCE marked while the cancelled MECHANISM one
bullet up stayed live; an ASCII dash corrected while a new one was written in the
correcting text. No mechanism proposed — this is a working practice, and it is
PROPOSED as one in §6 (candidates; not written to the store by this audit).

### §4.3 Committing a subagent's claim without checking its source

The audit asserted a "balance sheet carries two comparatives, i.e. N+1" variant
and attributed it to the brief's §Users. §Users says "three comparative years"
with no statement-type distinction, so the attribution was wrong.

**This section originally stated a second, stronger claim — that nothing in the
repo supported the variant — and that claim was itself false.** A repo-wide grep
returns well over two hundred hits (the exact count drifts with every commit and is not worth pinning) for `comparative`, one of which states the variant verbatim
(`kpi_us_statement_series.py:6-7`). The correction matters more than the original
finding, because it changes the lesson: the failure was not only "a subagent
summary reached a committed artifact unchecked", it was **asserting an absolute
on the strength of a search whose results were never read**. Both audits written
this session made that same move, in the same sentence, about the same grep.

**This is the exact defect class `loom-code` 0.39.0 (plan-stage fact grounding,
PR #625) shipped to prevent, on the day it merged.** It did not fire here because
this branch never went through `writing-plans` — the grounding gate lives in the
plan stage, and a documentation branch has no plan. Worth recording as a scope
observation for that mechanism: **the gate is bound to an artifact type, and the
defect is not.**

## §5 What worked, and is worth generalising

Two mechanical checks, written mid-loop, ended two defect classes permanently:

1. every `~~…~~` quotation string-compared against its base revision — killed the
   silent-abridgement class;
2. every `path:line` citation in the diff parsed and bounds-checked against the
   file it names — 45 citations verified in one command, versus a reviewer
   re-reading them each round.

Neither found the hard defects (§2 needed judgement). But both retired a class
that had recurred three times, at a fraction of a review round's cost.

**Generalisable rule**: for citation-dense documents, ship the check as a script,
not as a review instruction. A reviewer asked to verify 45 citations will do it
once and then trust its own earlier pass; a script does not.

## §6 Candidates for `docs/loom/memory/`

Recorded here as candidates, not written — the durable-store decision is the
user's:

- **Verify the FIX against source, not the finding.** Six of the nine rounds found
  a defect introduced by the previous round's remediation; every one was caught
  by re-reading what was just written rather than what it was meant to change.
- **The named line is not the population.** §4.2.

## §6b The one proposal that was tested inside this audit

§3.1 (review the whole artifact, not the diff) was adopted from round 7 onward
rather than left as a recommendation, so it has a result rather than an argument:

- Round 7, first whole-artifact round: found the 🔴 six diff-scoped rounds had
  missed — a live instruction wrong since before the branch existed.
- Round 8, whole-artifact: found **no** instruction defects at all, and reported
  the class clean. Its four findings were evidence defects in original text.
- Round 9, whole-artifact: independently re-verified round 8's clean finding and
  it held.

So the proposal did what it claimed — it reached a defect class diff scope cannot
see, and then confirmed that class exhausted. It did NOT make the loop converge:
rounds 8 and 9 still blocked, on a class (claims whose evidence does not survive
checking) that is orthogonal to scope. **Scope was one of the two problems, and
fixing it fixed one of them.** §3.2's convergence criterion remains untested.

A second, unflattering result from the same rounds: round 9's 🔴 was a repair
written into one of the two artifacts that carried the claim. §4.2's "the named
line is not the population" recurred AFTER being named in this very audit — which
is evidence that naming a practice in a document does not install it, and mild
support for §3.4's argument that prose does not bind.

## §7 What this audit cannot claim

- It is ONE branch. Every occurrence count in §3 is 1 unless stated otherwise.
  Only ONE of the four proposals (§3.4) cites prior evidence in another audit
  (`2026-07-04-harness-engineering-audit.md`). §3.1, §3.2 and §3.3 rest on this
  session alone — an earlier draft of this line overstated that count.
- It is a DOCUMENTATION branch. Whether the same loop fails the same way on code
  is untested — §3.1's argument explicitly turns on documents having no tests, so
  it should not be generalised to code without evidence.
- The operator and the audit author are the same session. A reader should weigh
  §4's self-assessment accordingly; the round-by-round verdicts in §1 are the
  independent part.
