# OKR-drift detection patterns (4dx-audit reference)

> **Purpose**: cross-layer pattern check used by `4dx-audit` Step 3.6. Detects when a user's claimed-4DX implementation has drifted toward OKR-shaped patterns — but more accurately, toward **bad goal-setting in any framework** (since most "drift to OKR" is actually drift to OKR's own failure modes per Wodtke).
>
> **Loaded by**: `SKILL.md` Step 3.6 only. Not loaded by topic-skill audit-modes (those handle layer-local rule checks; this file handles cross-layer drift pattern).
>
> **Grounded against**: Grove (1983), Doerr (2018), Wodtke (2016/2021), Locke-Latham (1990 / 2006). Full citations in `four-dx-coach/research/okr-primary-sources.md` (research-tier human reference). The four sources establish what canonical OKR is + what OKR's own failure modes are.

---

## Why this check exists

The user may describe their work as "running 4DX" but the artifact stack reveals OKR-flavor patterns: stretch language, multi-WIG framing, KR-shaped "leads," dashboard-shaped "scoreboards," confidence-update cadence instead of hard-commitment cadence. The audit's job is to surface this drift accurately, NOT to frame OKR as the antagonist.

**The unifying insight from cross-source synthesis**: most "drift toward OKR" is actually drift toward **bad OKR shape** that Wodtke's *Radical Focus* would also reject. The signal is "user adopted goal-setting vocabulary without either framework's discipline" — discipline-drift, not framework-drift.

This means audit-mode recommendations should NOT default to "you should pick OKR or 4DX, pick one." They should default to "your current implementation hits failure modes documented in BOTH frameworks; here's what to fix."

---

## OKR-drift signals organized by 4DX layer

### D1 — WIG layer drift signals

| Signal | What it looks like in artifacts | Backing source | What to call it |
|---|---|---|---|
| **Multi-WIG drift** | 3+ "WIGs" listed in user's framing | Wodtke (1-3 max strict) + Doerr (3-5 lenient) | "More than two WIGs = no WIGs" (book Ch 1) AND "setting too many OKRs" (Wodtke OKR failure mode). Drift hits BOTH frameworks' rules. |
| **Aspirational stretch language** | "Aim for" / "stretch goal" / "would be amazing if" / explicit 60-70% achievement target | Doerr Ch 1 (citing Larry Page); Klau Google Ventures 2013 | OKR canonical for **aspirational** OKRs (Doerr's "committed vs aspirational" distinction); 4DX rejects this for WIGs (winnable game). If user is mixing: explicit framework collision. |
| **Objective + KR split format** | Goal written as "Objective: X. KR1: Y, KR2: Z, KR3: W" instead of single "From X to Y by When" | Grove (origin of Object/KR split) + Doerr (modern canonical shape) | Pure OKR shape. If user calls this a "WIG," it's vocabulary drift — they wrote an OKR Objective + KRs, not a WIG. |
| **Sandbagging suspicion** | "WIG" trivially achievable; team obviously hits it; no real stretch | Wodtke OKR failure mode | Bad-OKR shape (Wodtke explicitly names this). Often co-occurs with multi-WIG drift (sandbagging tolerated because "we have 5 WIGs, can't all be hard"). |

### D2 — Lead measure layer drift signals

| Signal | What it looks like in artifacts | Backing source | What to call it |
|---|---|---|---|
| **Outcome-shaped "leads"** | "Lead measures" that are actually lag metrics (NPS, retention, revenue) | Wodtke ("treating KRs as outcome targets" failure mode) | Bad-OKR shape: KRs that ARE the outcome aren't lead measures. Doubly fails 4DX (which wants behavioral leads) AND OKR (which wants KRs that drive the Objective, not duplicate it). |
| **Task-shaped "leads"** | "Lead measures" framed as deliverables ("ship feature X", "complete migration Y") | Wodtke ("treating KRs as task lists" failure mode) | Bad-OKR shape AND bad-4DX shape. Wodtke explicitly rejects this for OKR. 4DX rejects this for leads (tasks ≠ behavioral activities). |
| **Five+ "leads" per WIG** | 5-7 "leads" listed | Doerr KR count (2-5 lenient); 4DX rule (≤2-3 leads per WIG) | Imported OKR's KR-count convention into 4DX without 4DX's stricter cap. If actually OKR-shaped (KRs that ARE the goal), 5+ is fine in OKR; if 4DX-shaped (behaviors), 5+ violates the cognitive-load rule. Often co-occurs with the other D2 drift signals. |
| **Goodhart-vulnerable activity counting** | "Code reviews per week", "tickets closed", "tests written", "PRs merged" | Goodhart 1975 (already grounded) + Lean Beliefs 2014 (verbatim software-engineering Goodhart concern) | The classic software-engineering Goodhart trap. Even if framed as a 4DX lead, it gets gamed (split features, useless tests, trivial PRs). Surface this signal alongside D2 drift, NOT as drift-to-OKR specifically. |

### D3 — Scoreboard layer drift signals

| Signal | What it looks like in artifacts | Backing source | What to call it |
|---|---|---|---|
| **Dashboard with 12+ metrics** | "Scoreboard" is actually an executive-facing BI dashboard with many metrics | Wodtke (focused KR display, not dashboard); Tufte data-ink (already grounded); Few dashboard-vs-database (already grounded) | Bad-OKR shape AND bad-4DX shape. Wodtke and 4DX both want focused display. The "12+ metrics" pattern is OKR-tool-default behavior (Lattice / Workboard / Asana Goals all let you add many KRs to a view) — it's tool-shaped, not framework-canonical. |
| **Read-only / executive-facing** | Scoreboard not built by team; team can't update it; lives in a leadership dashboard | 4DX Ch 4 Players' (not Coaches') rule + Harkin et al. 2016 meta-analysis (team-public + physical recording > private + digital-only) | Direct violation of 4DX Players' rule + the Harkin meta-analysis empirical warrant. Not OKR-canonical either (OKR is org-public BUT teams own their KRs). Drift-to-OKR is misleading framing — drift is to neither framework's canonical. |
| **Lives in OKR tooling only** | Asana Goals / Lattice / Workboard / Notion only; no physical / posted artifact | Harkin et al. 2016 (public + physical recording > private + digital-only, pg. 219) | Drift-to-OKR-tool-default. Note: Wodtke does NOT recommend tool-only either; she recommends visible team artifact. So the drift is to bad-OKR tool-implementation, not to canonical OKR. |

### D4 — Cadence layer drift signals

| Signal | What it looks like in artifacts | Backing source | What to call it |
|---|---|---|---|
| **Quarterly-only cadence** | Team only does quarterly OKR / WIG review; no weekly meeting | Wodtke (Mondays/Fridays); Doerr (Google weekly check-in) | **Drift to bad goal-setting in any framework, NOT drift to OKR**. Both OKR and 4DX have weekly cadence canonically. Quarterly-only fails both frameworks' canonical practice. |
| **Confidence-update cadence (no hard commitment)** | Weekly meeting reviews "are we on track? confidence 0-1.0" but no commitment to specific behavior | Doerr (OKR confidence shape) vs 4DX Account → Review → Plan | Genuine drift signal for "running OKR weekly cadence inside a self-described 4DX implementation." Surface this honestly: the weekly cadence is OKR-flavor (confidence update), not 4DX-flavor (hard commitment). |
| **60+ minute sessions** | WIG Sessions creep past 30-min ceiling | Bravelab.io 2021 verbatim (already grounded in d4-cadence references) | Bad cadence in both frameworks — Doerr/Wodtke endorse short check-ins, 4DX explicitly mandates ≤30 min. Not OKR-drift specifically. |
| **Account → Review → Plan replaced with status report** | Members report "what I worked on" instead of accounting for last week's commitment | 4DX-specific (no direct OKR analog) | Genuine 4DX-specific drift. Audit should flag without claiming OKR endorsement — OKR doesn't strictly mandate Account/Review/Plan structure. |

### Substrate / cross-layer drift signals

| Signal | What it looks like in artifacts | Backing source | What to call it |
|---|---|---|---|
| **"60-70% is healthy" framing** | User explicitly invokes stretch-target culture as defense for missing WIG | Doerr (Larry Page citation) + Locke-Latham 2006 (boundary conditions) | Pure OKR-aspirational culture inserted into 4DX framing. Locke-Latham's 2006 caveat applies: stretch goals only work with adequate ability + commitment + feedback; without those, stretch backfires. If user has none of those supports, the stretch framing isn't OKR best-practice either. |
| **Compensation-tied "WIGs"** | WIG achievement → bonus / promotion criterion | Wodtke (compensation-tied OKRs failure mode) + Doerr (decoupling principle) | Bad-OKR shape (Wodtke explicit) AND bad-4DX shape (creates sandbagging incentive). Drift to old-MBO shape, not to canonical OKR. |
| **Stretch language without commitment / feedback** | Aspirational targets + no weekly check-in + no scoreboard | Locke-Latham 2006 boundary conditions | Empirically-failed goal-setting condition. Cite Locke-Latham as warrant: "stretch goals require commitment + feedback + ability; you have stretch language but missing the supports — this is the Locke-Latham failure condition, not OKR best practice." |
| **"OKR culture" used to rationalize failed cadence** | "We had an OKR retro — that counts as our cadence" | Wodtke + 4DX D4 | Cadence-collapse framing dressed in OKR language. Not OKR-canonical (OKR has weekly check-ins per Wodtke); not 4DX-canonical. The "OKR culture" claim is a rationalization, not a framework choice. |

---

## How to use this checklist in audit-mode (Step 3.6 procedure)

After completing per-layer rule checks (Step 3) and Cindrich 5-mode cross-validation (Step 3.5), run this drift-detection check:

1. **Scan the artifact stack for any of the signals above.** Most user contexts will surface 0-3 signals; very-drifted contexts will surface 5+.
2. **For each signal matched, name it accurately**:
   - "Drift to OKR" framing — only when the pattern is canonical-OKR-shaped (e.g. Objective + KR split, aspirational stretch with proper supports). Rare in practice.
   - "Drift to bad-OKR / bad-4DX shape" framing — when the pattern hits failure modes documented in both frameworks (most common).
   - "Drift to neither framework's canonical" framing — when the pattern is tool-default or compliance theater (e.g. dashboard-shape scoreboard).
3. **Cite the specific source** that backs each named drift (Wodtke / Doerr / Locke-Latham / Harkin / Bravelab / Cindrich).
4. **Surface in the recommendations step** with this language pattern:
   > *"Your implementation has [N] drift signals: [list]. Most are documented failure modes in both 4DX (book Ch X) AND OKR (Wodtke / Doerr). The honest framing is discipline-drift, not framework-drift. To fix [signal], do [specific action] — this is endorsed by [source] regardless of which framework you ultimately commit to."*
5. **Avoid framing OKR as the antagonist.** Both frameworks are valid; both have failure modes; the user's drift is usually to bad shape in any framework.

---

## What this checklist does NOT do

- **Does not classify the user's framework choice.** If user says "we run 4DX," audit-mode does not lecture them to switch to OKR (or vice versa). The job is naming what's actually happening, not prescribing framework identity.
- **Does not assume drift is bad in every case.** Some "drift" signals (e.g. weekly confidence check-in shape) are valid OKR practice; if user is genuinely running OKR not 4DX, those signals are correct OKR. The job is calibrating against what the user CLAIMS to be doing.
- **Does not replace Cindrich 5-mode check (Step 3.5).** Cindrich covers practitioner-named 4DX-specific failure modes; this file covers OKR-shaped drift specifically. Both run; both can match the same artifact stack from different angles.

---

## Cross-references

- Full OKR primary sources + synthesis: `four-dx-coach/research/okr-primary-sources.md`
- Cindrich 5-mode check (Step 3.5): `4dx-audit/references/industry-grounding.md` Source 5
- Cross-source synthesis on horizontal hybrid (engineering OKR + sales 4DX): `four-dx-coach/research/saas-tech-context-and-okr-vs-4dx.md` Part 7
