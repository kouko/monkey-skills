# Brief — framework-audit library: clean-slate citation-grounded blind-spots (2-axis) + domain-gap filing

date: 2026-06-13
branch: feat/deep-deep-research-vs-angle-selector
skill: research-toolkit/skills/deep-deep-research
status: brief (brainstorming output → writing-plans)

## Problem

The framework-audit lever's universal meta-check — the "Collective blind-spots (12, meta-level)" list in `references/framework-audit-library.md` — is the **only** section of the library with **zero citations** (every framework cell has a source). Three research rounds established it is an *ad-hoc reinvention* of mature canon, and the experiment/eval surfaced both a taxonomy question and a scope error. The job: **rebuild the universal meta-list from scratch, citation-grounded, organized on a 2-axis backbone**, AND **correct a scope leak** — two field-found gaps that are domain-specific were mis-filed as universal.

JTBD: *When the framework-audit lever runs its final universal meta-check after the framework walk, I want each "all frameworks miss this" dimension to be canon-grounded and genuinely domain-independent, so the audit is defensible and doesn't mis-fire a domain item on an out-of-domain question.*

## Users

The deep-deep-research agent running the framework-audit lever (`framework_audit.py audit_prompt` step 4), and the human maintainer reading/extending the library. Downstream: any host agent invoking the skill. The meta-list is applied to **every** audited question regardless of domain (unlike the routed framework cells), so universality is load-bearing.

## Smallest End State

1. The library's universal blind-spots section is **rebuilt from canon** (not retrofitted onto the existing 12), organized 2-axis (structural-frame omissions / cognitive omissions), every item + the section anchored on a real source with confidence-appropriate attribution.
2. The two **domain-specific** gaps are filed into the correct **domain framework cells** (not the universal list).
3. The `BLIND_SPOT_COUNT` coupling (script int + library header + test assertion) is updated once, consistently.
4. Suite green; siblings green; zero synced-primitive drift; library stays English-only.

## Current State Evidence

- **Forward** — `references/framework-audit-library.md` L212-231: current "Collective blind-spots (12, meta-level)" section, 12 numbered items, **no citations**. The Routing table (L32-47) + cell-block grouping `### Universal / cross-domain` (L79) vs domain sections (`### Business strategy` L125, `### Investment / finance` L137, `### Economics / policy` L165) already cleanly separate domain-routed vs universal — the meta-list is the *universal* layer.
- **Reverse (SSOT/coupling)** — `scripts/framework_audit.py` L112-115 `BLIND_SPOT_COUNT: int = 12`; interpolated into `audit_prompt` (L172-178) twice + builds the section title `"Collective blind-spots ({BLIND_SPOT_COUNT}, meta-level)"`. The library header literal `## Collective blind-spots (12, meta-level)` (L212) **must match** the prompt-built title → both move together. `audit_prompt` step-4 examples "(time-decay, base rates, second-order, unknown-unknowns …)" survive in the new list, so example text stays valid. **NOT a synced primitive** — `framework_audit.py` is house code (verified: not in `scripts/{schemas,rank,prompts,dedup}.py` sync set), safe to edit.
- **Error/Boundary** — `scripts/test_framework_audit.py` L153-155: `assert "blind-spot" in lower …` + `assert "12" in prompt` — the count assertion couples to `BLIND_SPOT_COUNT`; must update to the new count. `test_module_source_is_english_only` (CJK guard) covers the library → all new prose English-only.
- **Domain-cell homes already exist**: Economic Moat cell (L144-147, already notes the "moat narrowing" time dim), Equity Risk Taxonomy (L149-152, company-specific operating/governance risk), DCF+Comparables (L159-163 — **already carries the relative-valuation execution discipline**, so that eval backlog item needs no new work). Wardley appears in routing (L42/47) but has no standalone cell-block → platform-risk attaches to the Business strategy section.

Evidence paths: `references/framework-audit-library.md`, `scripts/framework_audit.py`, `scripts/test_framework_audit.py`. Design SSOT: the 5 vault notes (rounds 1-3 + purpose-fit + eval), esp. `research/2026-06-13 完整性稽核器的盲點 canon — 第三輪…md`.

## Decision

**Build a clean-slate universal meta-list from canon, 2-axis by omission-source, RESHAPED to ~7 numbered items** (complexity-critique RESHAPE verdict: original 11 was net-neutral vs the shipped 12 and *amplifies the lever's own known failure mode* — the purpose-fit experiment proved completeness crowds out relevance; RAND RR-1408 "box-checking ≠ coverage"; JP「項目肥大＝網羅錯覚」「思考停止」). An item earns a numbered universal slot only if it passes **all three**: (a) universal (any domain), (b) **NOT already done by the framework walk that just ran**, (c) high-yield. Lower-yield / conditional / framework-walk-redundant dimensions are demoted to notes, not numbered slots. Old 12 used only as a coverage-regression cross-check (no item silently lost — relocated, folded, or demoted, never dropped). Concrete design:

**Section anchor (replaces old #8 instrument-bias as the rationale):** Any single framework structurally sees only what its cells encode (Maslow law-of-instrument; Munger; multi-framing: Bolman-Deal "each frame… a product of blind spots", Morgan, Allison). After a framework walk, two omission classes remain regardless of domain. The recognized **self-applied** completeness canons are **Decision Quality's six-element chain (Spetzler/SDG 2016)** and the **IC analytic standards (ICD 203)**; the cognitive layer's root is **Kahneman's WYSIATI** ("what you see is all there is" — the mind treats present info as complete; unknown-unknowns is its limit case). Honest notes: "what frameworks collectively miss" is *not itself a named canon* (this list synthesizes the above; cite per item, don't claim the category is canonical); items can cross axes (Cooper); a motivation/social layer exists (Kunda) → folded into the guardrail. (Kahneman-Lovallo-Sibony 2011 is *not* the section anchor — its scope is evaluators judging others' proposals; it is demoted to an Axis-B pointer.)

**Axis A — Structural / frame omissions** (no cell for it, any domain; anchors: DQ chain / ICD 203 / multi-framing) — **3 numbered:**
- A1 **Time & dynamics** — static snapshot; no cell for evolution, lag, or when the conclusion/premise expires. (Systems/CLD delay; Mintzberg prediction-fallacy; JP 入山 premise-obsolescence.)
- A2 **Second-order / reflexivity** — stops at first-order; others adapt, the system re-equilibrates, the act changes the analyzed thing. (Marks; Soros reflexivity; general-equilibrium.)
- A3 **Feasibility, power & reversibility** — assumes the best option is adopted; misses who vetoes, whether it can be executed, and how hard to undo (one-way vs two-way door). (DQ "commitment to action"; Pfeffer-Sutton knowing-doing; Kingdon/stakeholder; **Bezos reversibility** — the universal home for the eval's reversibility gap.)

**Axis B — Cognitive omissions** (mind treats present info as all there is — WYSIATI, any framework; anchors: Kahneman / ICD 203 Std 2-3) — **4 numbered:**
- B1 **Outside view / base rates** — anchored on the case, omitting the reference-class distribution; salient features crowd out absent/unattended ones. (Base-rate neglect, K-T 1979; reference-class forecasting = **Flyvbjerg 2004/2006**, NOT L-K 2003; outside-view concept K-T 1979 / K-L 1993; focusing-illusion/unattended-factors folded in here, Kahneman & Schkade 1998.)
- B2 **Disconfirming evidence & rival hypotheses** — sought confirmation, didn't generate/test alternatives. (Confirmation bias, Wason; ACH.)
- B3 **Uncertainty & evidence quality** — confidence unmarked; source independence/reliability unchecked. (ICD 203 Std 2 uncertainty + Std 3 assumptions-vs-judgments; SAT Quality-of-Information Check.)
- B4 **Unknown-unknowns** — the omission no cell maps to; what kills you isn't on any list → run a structured surfacing technique. (WYSIATI limit case; pre-mortem/Klein; what-if.)

**Demoted to notes (NOT numbered slots):**
- **Values / normative** → conditional note "for high-stakes / normative questions, add the ethical lenses + stakeholder ethics" (mirrors today's conditional #10). (DQ "clear values & tradeoffs".)
- **Distribution / tails** → sub-bullet "aggregates hide who-wins-who-loses and the tail — check distribution, esp. for risk/policy". (CBA distribution.)
- **Frame & alternatives unquestioned** → NOT a blind-spot — it is the framework walk's own job (MECE/issue-tree/ACH/SCQA are the general-start frameworks). Mention in the section's "how to use" lead-in, not the list. (Fails test (b).)
- **Granularity / level** → folded into B1's "unattended" + the distribution note; levels-of-analysis is already a general-start framework (fails (b) unconditionally).

**Guardrail (not numbered):** audit-as-justification / 思考停止 — an empty gap is a legitimate honest result; don't let "ran the audit" become the goal or a post-hoc rationalization. Western primary evidence: **RAND RR-1408** (devil's-advocacy can backfire; SAT coverage gains are *preliminary*; box-checking ≠ coverage). JP: 思考停止 / 形骸化. Motivation/social layer (self-interest / affect / groupthink — Kunda; KLS-2011 Qs) is mostly out of scope for a framework-completeness auditor; flag only when the analyst has a stake.

**Coverage cross-check vs old 12** (no regression — every old item relocated/folded/demoted, none dropped): time-decay→A1, second-order→A2, power/feasibility→A3, execution-gap→A3, base-rates→B1, distribution→A1-note + B1, subsegment/granularity→B1 + demoted note, unknown-unknowns→B4, evidence-quality→B3, uncertainty→B3, normative→demoted conditional note, instrument-bias→section anchor, frame/alternatives→"how to use" (framework-walk's job).

**Domain-gap filing (this brief):**
- **Talent / key-person concentration** (eval: Nvidia) → Economic Moat cell (moat durability depends on retaining the architects/talent) + Equity Risk Taxonomy (key-person as a company-specific risk).
- **Platform / external-dependency obsolescence** (eval: macOS) → Business strategy section (the entitlement/API you depend on gets cut; attach near Wardley evolution/commoditization).
- (Relative-valuation execution discipline → already present in the DCF+Comparables cell; no action. Triangulation/Denzin → optional one-line note in DCF+Comparables/evidence; low priority.)

**Count target:** 7 universal items (3 structural + 4 cognitive). `BLIND_SPOT_COUNT` 12→7; library header `(12, meta-level)`→`(7, meta-level)`; test `assert "12"`→`assert "7"`. `audit_prompt` step-4 examples "(time-decay, base rates, second-order, unknown-unknowns …)" all survive as numbered items → example text stays valid. Final count pinned in plan if item granularity shifts during implementation.

## Out of Scope

- The purpose-fit / relevance-floor lens (Thread A) — separate parked thread.
- Opening the branch as a PR.
- Any change to synced primitives (`schemas/rank/prompts/dedup.py`), VS mode, default scope path, default synthesis prose, `mode_route.py` §三-C ZH citations.
- The 3 "needs-reverify" eval candidates (TestFlight distribution, FX conversion, NVLink interconnect mechanism) — deferred.
- Building a 3rd axis (motivation/social) — user chose 2-axis; motivation folded into guardrail.
- Runtime auto-write / learning-loop for the list (positioning settled: human-promote only).

## Alternatives Considered

- **Retrofit citations onto the existing 12** — rejected: the 12 are an ad-hoc reinvention; canon-first gives a defensible spine (rounds 1+3).
- **Anchor the section on Kahneman-Lovallo-Sibony 2011** — rejected (round 3): scope-mismatch (evaluator-judging-others, not self-applied completeness); demoted to Axis-B pointer. DQ chain + ICD 203 are the purpose-matched self-applied canons.
- **Add talent / platform to the universal list** — rejected (user catch): domain-specific (from domain-specific eval RUNs); belongs in domain cells, else mis-fires on out-of-domain questions.
- **3-axis (+ motivation/social)** — rejected by user; 2-axis as 1st-order simplification with honest cross-axis note (Cooper).
- **Reorganize spine by the DQ six-element chain instead of 2-axis** — noted as a fallback in round-3 note; not chosen (user committed to 2-axis), but DQ elements anchor the Axis-A items.

## What Becomes Obsolete

The uncited 12-item list (replaced wholesale). The old #8 instrument-bias item (promoted to the section's framing rationale, not a numbered item). No external runbook depends on the exact item numbering.

## Open Questions

- Exact final item granularity (7 ± 1 — e.g. whether B4 unknown-unknowns stays numbered or folds into the WYSIATI framing line) — pin in plan; whatever it is, sync all three coupling points (`BLIND_SPOT_COUNT` + library header + test).
- Platform-risk exact placement (standalone Wardley note vs Business-strategy line) — plan decides; both are domain-section edits.
