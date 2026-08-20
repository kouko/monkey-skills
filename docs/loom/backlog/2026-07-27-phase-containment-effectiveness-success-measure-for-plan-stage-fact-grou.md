---
name: 2026-07-27-phase-containment-effectiveness-success-measure-for-plan-stage-fact-grou
description: Phase Containment Effectiveness — success measure for plan-stage fact grounding
status: open
origin: `docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md` Open Question 1 — "How is success measured? … Without this the change ships unfalsifiable." Plan Task 9 (`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md:452-455`) fixes the measure's cheapest viable form. Evidence: `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` §2 (root-cause taxonomy) and §3 (arc-by-arc dossier).
start: FORWARD half only — evaluate at the close-out (whole-branch review and/or live dogfood) of each investing-toolkit arc that ships AFTER the plan-stage fact-grounding change (`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md`) lands. The HISTORICAL BASELINE half is WONTDO as of 2026-08-03 — see the decision block at the top of the body; do not re-open it without new grounds.
---

## WONTDO 2026-08-03 — the historical baseline, decided by the user

**Only the historical-baseline half is closed. The forward-recording half above
is untouched and still stands** — a per-arc "of this arc's planning-origin
defects, how many were caught before close-out" is a standalone number and
never needed a historical baseline to be meaningful.

Three grounds, in order of weight:

1. **The comparison's other side is empty and unscheduled.** This entry scopes
   the evaluation population to *investing-toolkit* arcs. Every arc shipped
   since the plan-stage fact-grounding change (loom-code 0.39.0, 2026-07-28)
   has been a loom-code process arc, so the "after" side holds zero qualifying
   arcs and will keep holding zero until the population is widened — itself an
   unscheduled item. Computing the expensive "before" first, under a retention
   deadline, to feed a comparison whose other side does not exist, inverts the
   order.
2. **The result would not be a rate.** The population is eight arcs, Category A
   falls in three of them, and the Category-A count is itself contested in the
   source audit (§1's scoreboard against §3.7's enumeration — see the
   reconciliation entry). A percentage over that is an anecdote with decimal
   places.
3. **The useful half was answered more cheaply.** PCE existed to say whether
   the plan-stage gates catch anything and which class they miss.
   `docs/loom/audits/2026-08-03-remediation-candidate-status-and-live-population.md`
   answered the "which class" half case by case, at zero dispatch cost and
   without reading a single transcript. What PCE would add is the ratio, which
   ground 2 disqualifies.

**Also corrected here**: the cost figure this decision was nearly made on was
wrong. The close-out entry recorded "~35 MB" of session transcripts; measured
2026-08-03, the 2026-07-22→07-27 window holds 954 transcript files totalling
303 MB across all project directories (731 of them in the three monkey-skills
directories). Re-measure rather than citing either figure.

**The input was NOT preserved.** Copying those transcripts out of
`~/.claude/projects/` before they age out (roughly 2026-08-21, on a ~30-day
retention inferred from the oldest surviving file in the main project
directory) was offered and not taken up. If this entry is ever re-opened, the
baseline is unreconstructible — that is a known, accepted consequence of this
decision, not an oversight.

- Start: FORWARD half only — evaluate at the close-out (whole-branch review and/or live
  dogfood) of each investing-toolkit arc that ships AFTER the plan-stage fact-grounding
  change (`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md`) lands. The HISTORICAL
  BASELINE half is WONTDO as of 2026-08-03 — see the decision block at the top of the body;
  do not re-open it without new grounds.
- Origin: `docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md` Open Question 1 —
  "How is success measured? … Without this the change ships unfalsifiable." Plan Task 9
  (`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md:452-455`) fixes the measure's
  cheapest viable form. Evidence: `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`
  §2 (root-cause taxonomy) and §3 (arc-by-arc dossier).
- What: **Phase Containment Effectiveness (PCE)** — the share of planning-origin defects
  caught BEFORE close-out (whole-branch review or live dogfood) rather than AT close-out.
  **Planning-origin defect** (the audit's Category A, "計畫事實錯"), defined inline so a
  future reader can classify without re-reading the audit: a defect where the PLAN ITSELF
  asserted a false technical claim — a wrong formula/identity, an instruction to reuse a
  semantically incompatible helper, a cited measurement that doesn't support its conclusion,
  a field count that doesn't match the code, or a brief requirement that never made it into a
  task. This is distinct from the audit's Category B (tests that pass without discriminating
  power — fixtures that coincidentally mask a bug) and Category C (ordinary
  implementation-vs-plan mismatches); PCE counts Category A only, because A is the one that
  survives every downstream conformance check (spec-reviewer checks output against plan, and
  the plan is the thing that's wrong).
  - **Cheap classification rule (deliberately narrow)**: for each confirmed Category-A
    instance, classify only whether it reached close-out or was caught before close-out — a
    binary call. Do NOT attribute the earlier catches to a specific stage (plan review vs.
    per-task review vs. implementation-time refusal, etc.) — that per-instance stage
    attribution requires forensic tracing of each defect's exact catch point across every
    task, which is not the cheap form this measure is supposed to take. It is also not this
    measure's job: PCE only needs to answer whether close-out is where the defect surfaced,
    not which earlier mechanism would have caught it. Do NOT attempt this classification for
    Category B or C defects either; they are cheap to catch regardless of category, so
    classifying them buys nothing toward this measure.
  - **Formula**: PCE = (confirmed planning-origin defects caught before close-out) / (total
    confirmed planning-origin defects).
  - **Arcs to evaluate over**: seven already-shipped investing-toolkit arcs — KPI tearsheet
    (PR #605), TW 背書保證 iXBRL (PR #610), US XBRL→store producer (PR #611), TW store
    producer (PR #612), 公司總營收兩線 (PR #616), kpi_id injective (PR #618), US as-reported
    線 (PR #619) — plus one **in-progress** arc, the as-filed reconstruction (branch
    `feat-sec-submissions-pagination`), whose audit coverage is explicitly incomplete
    (audit header §Scope, and §1's scoreboard — task-level PASS/PASS_WITH_NOTES counts are unfilled for
    this arc, only the NEEDS_REVISION count is known, because it hasn't shipped).
  - **Baseline: cannot be computed from the current audit — and, as of 2026-08-03, will not
    be computed at all** (see the WONTDO block at the top of this file). The source document
    (`docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`) carries
    internally inconsistent claims about the same Category-A instances — its own erratum says
    三處 live, a fourth filed and struck WITHDRAWN — so any count or close-out/pre-close-out
    split drawn from it would be unreliable. The specific inconsistencies and their citations
    are in `docs/loom/backlog/2026-07-27-investing-toolkit-arc-defect-provenance-audit-internal-inconsistencies-n.md`
    (named, not "the entry below" — one entry per file now, and the generated index orders it
    ahead of this one). **Scope of the prohibition**: do not compute or assert a HISTORICAL
    BASELINE from this audit. It does NOT block the forward-recording half, which measures a
    single arc's own defects at that arc's close-out and never reads this audit.
