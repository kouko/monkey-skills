---
name: 2026-07-27-investing-toolkit-arc-defect-provenance-audit-internal-inconsistencies-n
description: investing-toolkit arc defect-provenance audit — internal inconsistencies need reconciliation
status: OPEN
origin: found while writing the Phase Containment Effectiveness BACKLOG entry (Task 9, `docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md:452-455`), round 3, after a prior round's attempt to compute a baseline from this audit produced a four-bucket per-instance attribution that both reviewers rejected as out of scope. Re-checking the source turned up the inconsistencies below.
start: before computing the Phase Containment Effectiveness baseline (entry above) — that measure depends on a trustworthy Category-A count and close-out determination from this document.
---

- Start: before computing the Phase Containment Effectiveness baseline (entry above) — that
  measure depends on a trustworthy Category-A count and close-out determination from this
  document.
- Origin: found while writing the Phase Containment Effectiveness BACKLOG entry (Task 9,
  `docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md:452-455`), round 3, after a prior
  round's attempt to compute a baseline from this audit produced a four-bucket per-instance
  attribution that both reviewers rejected as out of scope. Re-checking the source turned up
  the inconsistencies below.
- What: `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` makes four
  internally inconsistent claims about its own Category-A ("計畫事實錯") findings for PR #619
  and the audit's overall detectability claim:
  (Citations below use **section anchors**, not line numbers: adding the audit's erratum
  header pushed every line under it down, which invalidated this entry's original pointers
  in the same change set that catalogued citation drift. The shift's magnitude is
  deliberately not stated — a self-referential count is a claim that must be re-measured on
  every edit, and failing to re-measure it is exactly how the previous remediation round
  broke this passage. See the "what 0.39.0 does NOT close" entry, item 3.)
  1. **Scoreboard count vs. dossier count mismatch.** §1's scoreboard reports PR #619 as
     `A×2`; §3.7 enumerates three A-instances (A-1 the equity-identity probe, A-2 the reused
     selector, A-3 the retired-numbers doc).
  2. **"Only detectable at close-out" contradicted by the audit's own dossier.** §5's
     sentence "A 類的偵測面只有兩個，都在收尾" (grep for it; it is the lead-in to that
     section's bullet pair, not its closing line) asserts A-class defects are
     structurally detectable ONLY at close-out; §3.7 (a quality reviewer's
     spontaneous cross-read at per-task review), §3.8 (an implementer's
     task-level refusal before any code was written), and §6 (citing that
     refusal as a positive counterexample) all document earlier catches.
  3. **"Caught before merge" contradicted by a shipped defect.** §6 states
     every A-defect was caught before merge; §3.7's A-3 states the wrong text
     ("GOOGL from 2014, DIS from 2018" — as `analysis-kpi/SKILL.md` read at the time of the
     audit, 2026-07-27; that text has since been corrected to 2012/2016, so the pointer no
     longer greps) shipped — i.e. was
     NOT caught before merge.
  4. ~~**Self-contradicting count within one sentence.**~~ **WITHDRAWN** — not a
     contradiction. §3.8's opening reads "A 類三連…implementer 拒絕動工並回報四項量測":
     three Category-A defects, and four measurements reported by the implementer. Two
     different quantities in one sentence, not one quantity stated twice. Withdrawn on
     whole-branch review of `feat-plan-fact-grounding`, which read the line rather than the
     summary of it — the same failure this branch's own cross-read rule exists to catch,
     committed while writing the entry that catalogues it. Left visible rather than deleted:
     the reconciliation task must not re-derive a phantom item, and the miss is the point.
  - **Why it matters**: the Phase Containment Effectiveness measure (entry above) needs a
    reliable Category-A count and a reliable close-out/pre-close-out split per confirmed
    instance. Items 1-3 cannot be trusted as-is. Reconcile by re-reading the
    underlying session transcripts this audit was extracted from (audit header §Method) and correcting
    the audit's prose, then recompute the PCE baseline from the corrected document.
