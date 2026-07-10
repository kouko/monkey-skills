# Paper-dogfood report — PRINCIPLES construction flow (designer/PM loop)

> **Type**: dogfood run report (grades the frozen `instrument.md` in this folder)
> **Date**: 2026-07-10
> **Run**: real product idea (PIP companion note app, macOS/iOS/iPadOS),
> user in designer/PM persona; full flow Product → Design → Engineering,
> 8 conversation rounds end-to-end. Artifact produced:
> `PRINCIPLES-pip-note.md` (this folder) — passed per-section + total read-back.
> **Verdict**: instrument v0 **works** — all five success criteria pass or
> partially pass; the 4-type-split DEFER bet survives n=1; question set
> needs +1 question and +1 annotation before implementation.

## Grades against the five success criteria

| # | Criterion | Grade | Evidence |
|---|---|---|---|
| 1 | Question-set adequacy | **PARTIAL** | Two ad-hoc probe supplements were needed, both in the same missing area (see FINDING-01, -02) |
| 2 | Candidate breadth | **PASS** | Product: non-head Shape Up offered and chosen as PRIMARY; head JTBD offered and REJECTED by user. Design: Calm Tech / Hara / Bringhurst (non-head) carried the sections. Considered-but-rejected named with reasons every round |
| 3 | Propose-then-react | **PASS** (n=1 caveat) | Round-1 hypothesis ("disposable notes") was WRONG and productively extracted the correction (persistent reference cards). No stalls needing recovery — user was articulate; untested against a true non-technical PM |
| 4 | Falsifiability | **PASS** | All principles in could-lose form; read-back gate caught one agent-FABRICATED deviation (FINDING-04) |
| 5 | Output shape | **PASS** | Pinned canon ×8, deviation ledger ×4, unique principles ×20, per-section + total read-back all produced |

## Findings

**FINDING-01 (instrument gap — question set): no lifecycle/scale question.**
The 7-question set never asks how long content lives or how large it grows.
The operator had to invent the probe ("500 cards later, how do you find
one?") ad hoc — and it produced one of the artifact's most valuable
principles (P6 規模上限是特性). A weaker operator would have missed it.
→ v0.1 candidate: add **Q8 — Lifecycle & scale**: "這些內容會活多久、
長到多大？長大之後怎麼找到一張？"

**FINDING-02 (instrument gap — Q6 annotation): "replace X" answers imply
capability sets.** The success answer "取代 Bear 與 Reminders" smuggled in a
scope fork (does replacing Reminders mean notifications?) that no question
probed. Caught by operator judgment, not by the set.
→ v0.1 candidate: annotate Q6 — when success is phrased as "replaces X",
enumerate X's capabilities and force explicit in/out classification.

**FINDING-03 (flow validation — cross-section propagation).** 3 of 5
Engineering stance questions were partially pre-answered by earlier Product
decisions (iCloud → cost posture; appetite → reversibility affinity). The
operator adapted by converting those briefings into "confirm as durable
stance" — this worked but was improvised.
→ v0.1 candidate: codify in the flow script: before asking an Engineering
question, check whether an earlier section already answered it; if so,
present for confirmation-as-principle, don't re-ask. (Same rule as
judgment-rubrics §3(c), applied inside one session.)

**FINDING-04 (read-back gate value — caught a fabricated deviation).** The
operator inferred deviation D5 ("Bear-like warmth, Swiss objectivity not
fully adopted") from the user's *performance* benchmark ("效能對標 Bear").
Performance parity ≠ aesthetic affinity — the deviation was a hallucinated
inference. The read-back gate surfaced it explicitly and the user deleted
it. Evidence that per-section read-back is load-bearing, not ceremony; keep
it mandatory.

**FINDING-05 (base lists earned their place).** Calm Technology — arguably
the single best-fitting anchor for this product's identity — is a non-head,
easily-missed entry that surfaced via the completeness-audit pass over the
UX list. Concrete instance of the lists changing the output, not just
decorating it. Also: the user REJECTING head-member JTBD as an anchor shows
the propose-don't-impose shape lets user judgment beat popularity bias.

**FINDING-06 (compressed decision format works).** Labeled options let the
user answer five briefings in one line ("1a 2可逆 3確認 4a 5簡報
stack聲明"). Keep option labels stable and terse.

**FINDING-07 (minor instrument gap).** The instrument never says where the
produced PRINCIPLES artifact lands when no product repo exists (paper run).
Resolved ad hoc: saved into the dogfood folder. → specify in v0.1.

**FINDING-08 (tech-stack slot pattern).** The stack declaration worked best
framed as a *derivation* ("your principles already lock this — declaring it
just writes the fact down") rather than a fresh choice. Candidate standing
pattern for the kickoff briefing: when a one-way door is already determined
by principles, present it as derivation-for-confirmation, not as an open
option set.

## Honest limits of this run

1. **n=1, and the persona was played by a technical user.** The Engineering
   briefings — the section designed for a non-engineer — got expert-fast
   answers. The flow's hardest case (a true non-technical PM stalling on
   stance questions) is untested.
2. **Operator = instrument author.** The probing quality (catching the
   Reminders fork, the scale question) partly reflects author knowledge a
   cold operator wouldn't have. The v0.1 additions (FINDING-01, -02) shrink
   exactly that gap; a later cold-operator run (weaker model or fresh
   context) is the real test — consistent with this repo's cold-reader
   discipline.
3. **Type-split bet survives but weakly.** This was one prosumer-tool
   product; the generic set's misses clustered in lifecycle/scale, not in
   type-specific dimensions. The 4-type DEFER re-trigger (see BACKLOG)
   stands unchanged.

## Disposition

- Instrument v0 frozen as-run; v0.1 APPLIED same day → `instrument-v0.1.md`
  (this folder), integrating FINDING-01, -02, -03, -07 and the FINDING-08
  pattern; FINDING-08 also noted in the architecture doc §2.
- Next per BACKLOG COMMITTED-NEXT: decide build order — PRINCIPLES
  construction flow first (this run de-risks it); pipeline-hardening trio
  parallelizable. A cold-operator dogfood round is recommended between
  skill-draft and ship.
