---
name: 2026-07-28-whole-branch-review-round-ledger-bad-fix-re-check-planned-parked-before
description: Whole-branch review round ledger + bad-fix re-check — planned but not yet implemented
status: PARKED
origin: `docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md` §3.2, planned in full as the (P1+P2) slice of the three-slice review-mechanism plan. Brief: `docs/loom/specs/2026-07-29-review-round-ledger-and-bad-fix-recheck.md`. Plan: `docs/loom/plans/2026-07-30-review-round-ledger-and-bad-fix-recheck.md` (8 tasks, depth 5, plan-document-reviewer returned NEEDS_REVISION with five narrow fixes, listed below). Both artifacts were left on branch `feat-review-round-ledger`, uncommitted and unmerged.
start: re-evaluate **after** the docs-review blocking-class change ships and one prose-heavy branch has closed out under it. If that branch's review still runs past ~3 rounds, unpark and build the ledger. If prose branches converge in 1-2 rounds, the ledger has no unbounded loop left to instrument — close this entry instead.
---

- Start: re-evaluate **after** the docs-review blocking-class change ships and one prose-heavy
  branch has closed out under it. If that branch's review still runs past ~3 rounds, unpark and
  build the ledger. If prose branches converge in 1-2 rounds, the ledger has no unbounded loop
  left to instrument — close this entry instead.
- Origin: `docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md` §3.2, planned in full as
  the (P1+P2) slice of the three-slice review-mechanism plan. Brief:
  `docs/loom/specs/2026-07-29-review-round-ledger-and-bad-fix-recheck.md`. Plan:
  `docs/loom/plans/2026-07-30-review-round-ledger-and-bad-fix-recheck.md` (8 tasks, depth 5,
  plan-document-reviewer returned NEEDS_REVISION with five narrow fixes, listed below). Both
  artifacts were left on branch `feat-review-round-ledger`, uncommitted and unmerged.
- **Why parked rather than shipped**: the slice instruments an unbounded review loop; the
  blocking-class change addresses the same loop's *cause*. Shipping the instrument first would
  measure a loop we are about to stop running. The user's call, 2026-07-30.
- What the plan would have built (recoverable without re-deriving):
  1. `loom_gate_markers.py review-pass` appends one entry per invocation — **including the
     `NEEDS_REVISION` path at `loom-code/scripts/loom_gate_markers.py:268-272`, which today
     exits 3 writing nothing** — to `<git-dir>/loom/review-rounds.json`, branch-keyed,
     append-only, never reset. This is the whole reason the causation question below is
     currently unanswerable.
  2. A trajectory table printed to stderr from round 3 onward. **No numeric round cap** — every
     candidate number was a guess, and six research agents found no source supporting one.
  3. Bad-fix attribution derived from `git diff --name-only <prev head_sha>..HEAD` against the
     previous round's finding citations — mechanical, never a self-reported number.
  4. A bad-fix re-check rule (R4) in `loom-code/scripts/_reviewer-discipline.md`, regenerated
     into the three reviewer agents via `distribute.py`. Named for **bad-fix injection**, never
     Fagan (`docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md:284` records why).
- **Sub-items that outlive the park** (each independently actionable):
  - `arm_overlap` / n_eff independence diagnostic is **not derivable at the mint call site** —
    `requesting-code-review/SKILL.md:100` has the orchestrator union both arms *before* writing
    the verdict file, so the overlap count is computed and discarded upstream. Recording it
    needs either a new orchestrator obligation or a verdict-schema change. Dropped from that
    plan during planning; unbuilt.
  - Best-so-far rollback (reverting remediation commits to the lowest-defect round) is the
    highest-value idea found and the least solved: arXiv 2606.27009 (preprint) measures its
    oracle beating every practical policy by +0.115 Information Score (p≈4e-11) and reframes the
    open problem as "which round is best" rather than "when to stop".
  - The five plan-document-reviewer fixes, if the plan is ever unparked: Task 1/Task 3 both claim
    `Independent: true` while sharing both `Files touched` (Check 14); the brief's emphasized
    `findings_surviving` field is silently renamed to `prev_findings_addressed` with no stated
    equivalence (Check 8); Task 7's RED names no concrete test (Check 6); Task 8's
    `Brief item covered` points at Task 7 rather than the brief (Check 9); Task 8 does not name
    its SSOT the way the schema's worked example does (Check 16).
- **Causation, still unresolved and worth recording**: whether the non-converging-loop failure
  mode is new, and whether loom-* changes caused it, cannot be determined from what this repo
  recorded. Candidates: the review panel becoming default in loom-code 0.26.0 (2026-07-06, but a
  three-week gap to the first pathological loop fits badly); the two check-adding releases
  0.39.0 / 0.40.0 (07-27, 07-28); session-model changes (reviewers inherit the session model by
  design and no dated record of model changes exists here — neither confirmable nor falsifiable);
  and artifact type (both pathological loops ran on prose-heavy branches, and prose has no test
  oracle — audit §7 states plainly that whether the loop fails the same way on code is untested).
  Do not write a causal claim into any shipped artifact.
- **No published like-for-like baseline exists** for the bad-fix-injection rate this slice
  addressed. Capers Jones's ~7%/~25% figures (*The Economics of Software Quality*, 2011) are
  human reviewers fixing human-written code. The nearest LLM-era peer-reviewed fragments are
  structurally different metrics: ICSE 2026 (*Are "Solved Issues" in SWE-bench Really Solved
  Correctly?*) reports regressive patches at 11/77 of a manually inspected suspicious-patch
  sample — the paper's Table 8 (§4.4) names this category "Regressive Patches" verbatim, so
  both the figure and the label are the paper's own, not a transcription. Note a version split
  in the inflation figure this same paper reports elsewhere: the arXiv abstract (v2, the page
  at arxiv.org/abs/2503.15223) states these weaknesses inflate reported resolution rates by 6.2
  absolute percentage points, while the paper's RQ4 body and the ICSE '26 camera-ready abstract
  (software-lab.org/publications/icse2026_SWE-bench-correctness.pdf) both state 6.4 — this
  citation keeps neither number since it is not otherwise used here, but a future editor should
  not "correct" one to the other; they are two live versions, not an error. ASE 2026
  (*Regression Accumulation in Multi-Turn LLM Programming Conversations*)
  reports 40–73% of tasks losing previously-correct behaviour across 8 turns. Neither is a
  like-for-like comparison to the audit's 6-of-9 round-level figure, which remains n=1 branch.
