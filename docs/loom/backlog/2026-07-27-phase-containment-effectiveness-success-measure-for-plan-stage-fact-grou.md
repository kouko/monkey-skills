---
name: 2026-07-27-phase-containment-effectiveness-success-measure-for-plan-stage-fact-grou
description: Phase Containment Effectiveness — success measure for plan-stage fact grounding
status: OPEN
origin: `docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md` Open Question 1 — "How is success measured? … Without this the change ships unfalsifiable." Plan Task 9 (`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md:452-455`) fixes the measure's cheapest viable form. Evidence: `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` §2 (root-cause taxonomy) and §3 (arc-by-arc dossier).
start: evaluate at the close-out (whole-branch review and/or live dogfood) of each investing-toolkit arc that ships AFTER the plan-stage fact-grounding change (`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md`) lands. The baseline cannot be computed yet — see the Baseline note below and the reconciliation entry that follows this one.
---

- Start: evaluate at the close-out (whole-branch review and/or live dogfood) of each
  investing-toolkit arc that ships AFTER the plan-stage fact-grounding change
  (`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md`) lands. The baseline cannot be
  computed yet — see the Baseline note below and the reconciliation entry that follows this
  one.
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
  - **Baseline: cannot be computed from the current audit.** The source document
    (`docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`) contains four
    internally inconsistent claims about the same Category-A instances, so any count or
    close-out/pre-close-out split drawn from it right now would be unreliable — see the
    reconciliation entry immediately below for the specific inconsistencies and their
    citations. Do not compute or assert a PCE number until that entry is resolved.
