# Brief — synthesis calibration-prepend (缺口 1, Option A)

date: 2026-06-15 · skill: deep-deep-research · stage: brainstorming → writing-plans
grounding eval: `docs/skill-dogfood/2026-06-15-synthesis-skeptic-eval/REPORT.md` (8 seeds, cross-model)

## Problem
(Axis 1 — JTBD) The pipeline's single-pass synthesis **launders confidence at the
aggregation step**: a finding merged from a weak/split-vote/single-source claim gets tagged at
the *strongest* claim's confidence, and the summary headline reads more certain than its own
hedged body. A reader acting on the final report then over-relies on a conclusion whose evidence
is weaker than its `high` tag implies. **Job: make the final report's confidence trustworthy —
the tag a reader sees should match the strength of the evidence under it.** This defect lives in
the aggregation layer, which the existing claim-level 3-vote verification (Stage 5) structurally
cannot catch (each claim is individually fine; the defect is in how they're combined).

## Users
(Axis 2) Anyone acting on a deep-deep-research report — especially **high-stakes decisions**
(invest/trim, adopt-tech, migrate) where an over-confident headline misleads; and downstream
skills consuming the report's confidence tags. Job story: *When I read the synthesized report to
make a decision, I want each finding's confidence tag to reflect its actual evidence strength, so
I don't over-weight a conclusion that rests on a single blog or a tied vote.*

## Current State Evidence
- **Forward** (who calls synthesis): `SKILL.md` Stage 6 (L389–564) assembles the synthesis prompt;
  opt-in levers PREPEND directives ahead of the base prompt. Order today: purpose-fit → meta-mode →
  base (`SKILL.md:541-546`).
- **Reverse** (SSOT ownership): `scripts/prompts.py synthesis_prompt` (L137-168) is a **SYNCED
  primitive** — byte-identical to fact-check/cite-check/deep-read behind a CI MD5 gate
  (`distribute.py` / `verify-drift.py`). **MUST NOT edit it.** House lever modules
  (`mode_route.py`, `purpose_fit.py`) are NOT synced and are the additive-extension path.
- **Error** (degradation): meta-mode/purpose-fit both "fall back to the unmodified base synthesis
  prompt — never block synthesis" (`SKILL.md:481, 548`). New lever must match.
- **Data** (shapes): synthesis emits report `{summary, findings:[{claim,confidence,sources,
  evidence,vote?}], caveats, openQuestions}` (`schemas.py:104-126`, SYNCED). The calibration
  directive constrains how `confidence` is assigned — it does NOT change the schema.
- **Boundary** (template to mirror): `mode_route.py` (schema/classify-prompt/stance + CLI, exit
  0/1, fail-safe) and `test_mode_route.py` (flat-import + subprocess CLI round-trip). Calibration
  is SIMPLER — its directive is STATIC (same 3 rules every run), so it needs **no classify, no
  schema** — just a fixed block emitter.

Evidence paths: `research-toolkit/skills/deep-deep-research/{SKILL.md, scripts/mode_route.py,
scripts/purpose_fit.py, scripts/prompts.py, scripts/schemas.py, scripts/test_mode_route.py}`.

## Decision
Build a new house module **`scripts/calibrate.py`** that emits a STATIC calibration directive,
PREPENDED to the synthesis prompt (mirroring meta-mode/purpose-fit; `prompts.py` stays
byte-identical). Opt-in + additive, consistent with sibling levers (default path unchanged).

The directive encodes **3 anti-laundering rules** (the entire material-defect class from the eval,
6/8 seeds, cross-model confirmed):
1. **A merged finding's confidence = its weakest load-bearing claim.** Never tag a finding `high`
   if any claim it rests on is secondary / single-source / blog / split-vote. (high = multiple
   primary + near-unanimous; medium = secondary or split; low = single/blog.)
   *Canon: GRADE anti-averaging + NMA weakest-link (certainty = min(direct, indirect)); the
   "Certainty Bound" formal result (conclusion confidence ≤ weakest chain link).*
2. **Summary confidence ≤ body confidence.** The headline must not state more certainly than the
   findings/caveats it summarizes; a low/medium-confidence figure stays hedged in the summary.
   *Canon: the "spin" / abstract-overstatement literature — ICMJE + CONSORT-A abstract-consistency
   rules; this is the strongest-grounded of the three.*
3. **Never present split/tied votes OR mutually-conflicting confirmed claims as "consensus."** A
   contested/tied claim — or two confirmed claims in genuine tension — is surfaced as contested,
   not smoothed into agreement. (Broadened from "split votes" per the Axis-4 research: LLMs'
   documented default failure is smoothing conflicting evidence into false consensus — this is
   the eval's BURIED_TENSION class, e.g. ASML China 29%.)
   *Canon: GRADE inconsistency-downgrade; "Faithful Summarisation under Disagreement". Distinct
   from meta-mode (which sets stance from the QUESTION's epistemic mode); rule 3 governs
   within-synthesis claim tensions regardless of question mode.*

CLI: `calibrate.py block` → stdout `{"calibration_block": "<directive>"}`. No stdin, no schema,
no classify (static). Exit 0; unknown subcommand → stderr + exit 1 (mirror mode_route).

SKILL.md Stage 6: add an opt-in **"Calibration prepend"** subsection. **Prepend order becomes
purpose-fit → meta-mode → calibration → base** — calibration sits CLOSEST to the base prompt
because it governs the base synthesis's tagging mechanics (freshest when the model assigns
confidence), whereas purpose-fit/meta-mode set stance/emphasis. Degradation: if `calibrate.py`
errors, fall back to the unmodified prompt — never block.

Prior art (Axis 4): this is a **steering-prompt / human-inspired calibration** strategy — an
established family (SteerConf 2503.02863; "Can LLMs Express Their Uncertainty" ICLR 2024
2306.13063; production calibration writeups). Caveat from the literature: calibration prompting
shows *diminishing returns on advanced models* — but our own eval shows this specific
aggregation-laundering defect persists in capable models (sonnet generator, opus+sonnet judges
agree), so a targeted rule is justified rather than a generic "be calibrated" nudge.

## Alternatives Considered (Axis 4)
- **B — full skeptic pass** (opus adversarial review of final synthesis): recall 5/5, precision
  passed (0 cry-wolf on clean Raft), BUT +1 opus pass/run and severity judgment is model-dependent
  noise. Deferred — add only if A proves insufficient (skeptic verified cry-wolf-safe, so it can
  layer on later).
- **C — hybrid** (A always + B opt-in): the thorough endpoint; deferred for the same cost reason.
- **D — don't build**: rejected — null broke (6/8 seeds, cross-model).
- Industry: SteerConf-style steering, top-K alternatives, verbalized scores. We adopt the
  steering-directive shape, scoped to the 3 concrete aggregation rules the eval isolated (not a
  generic confidence-score nudge, which the literature shows is unreliable).

## What Becomes Obsolete (Axis 5)
Nothing is removed (purely additive opt-in lever, same as meta-mode/purpose-fit). Not a YAGNI flag:
the addition is eval-justified against a measured 6/8 defect rate, not speculative.

## Out of Scope
- Editing `prompts.py` / `schemas.py` (SYNCED — forbidden).
- The full skeptic pass (Option B) and hybrid (C) — deferred.
- Changing the report template / `synthesis.py _render_markdown` (that's a separate presentation-side
  thread, not this build).
- Making calibration default-on (ship opt-in like siblings; revisit default-on after more eval).
- Auto-rewriting the synthesis (directive steers generation; no post-hoc rewrite).

## Open Questions
- Default-on vs opt-in: shipping opt-in for consistency; a later A/B (calibration vs none on clean
  seeds like Raft) could justify default-on if it's confirmed harmless.
