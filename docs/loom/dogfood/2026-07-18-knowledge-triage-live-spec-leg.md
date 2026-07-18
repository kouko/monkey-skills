# Knowledge-triage live dogfood — deployed spec leg (2026-07-18)

Post-#582-merge validation of the three-bucket mechanism on the DEPLOYED
surface (not repo files): a clean headless `claude -p` session loaded the
installed loom-spec 0.5.0 cache and ran spec-expansion end-to-end in a
sandbox repo. Oracle = artifacts on disk, not agent self-report (per
`docs/loom/memory/verify-agent-mechanisms-on-disk-not-self-report.md`).

## Setup

Seed (planted landmine, fiscal-year incident class): "Monthly portfolio
report generator — aggregates positions and realized P&L per month for a
Japan-market retail investor app. Positions come from broker trade records
(trade date and settlement date both present)." No PRINCIPLES.md, no
ui-flows.md. Session instructed to complete end-to-end without asking.

## Results — PASS

- **Landmine intercepted**: edge case E8 ("trade date in M, settlement in
  M+1 → month attribution") emitted as `FLAG — SHAPING open question` with
  `evidence_needed: domain-convention`, naming the owning convention
  (約定日 vs 受渡日, JP brokerage/tax). No invented answer; spec.md wrote
  the obligations that "hold under either answer" and left the convention
  as an inline tagged open question.
- **No over-firing**: 11/13 edge cases (error handling, dedupe, empty
  month, loading/error states — all craft-derivable) expanded normally as
  KEEP with zero tags. Only E6/E8 flagged.
- **High-recall domain surfacing (beyond the plant)**: 7 additional
  genuine JP-brokerage domain questions self-surfaced and tagged —
  cost-basis method (移動平均法 vs 総平均法), fee/源泉徴収 P&L treatment,
  corporate-action record shape, 特定/一般/NISA account separation,
  信用取引 scope, JPY rounding, JST month boundary. Deferrable items
  routed to a separate non-blocking bucket (two-tier working).
- **Gate semantics correct**: draft states all 9 SHAPING tags "block
  VERIFY until resolved or explicitly deferred — none carries a
  `deferred:` note yet" — the draft is honestly not VERIFY-ready.

## Observation feeding the DOMAIN.md decision (open item)

A domain-dense seed produced 9 blocking SHAPING questions in one pass.
That is designed behavior (fail-loud beats fabricating nine conventions),
but it prices the pre-gate research round for finance-domain work. The
financial-analytics rebuild should measure that round's real cost — if it
is heavy and the questions recur across specs, that is the evidence for
building the deferred DOMAIN.md prevention layer (pre-declared domain
glossary, Meta tribal-knowledge / DDD ubiquitous-language pattern, plan
§Non-goals); if light, the reactive mechanism suffices.

## Weak-model leg (same seed, `--model haiku`, 2026-07-18)

Core interception SURVIVED, three degradations found — the first live
failure data for the mechanism:

- ✅ **Landmine still flagged**: proposal marks trade-vs-settlement month
  bucketing `FLAG` + `evidence_needed: domain-convention` (twice).
- ❌ **Invented tag vocabulary**: emitted `evidence_needed:
  technical-constraint` and `evidence_needed: audit-log-format` — values
  outside the pinned enum (craft | domain-convention | project-local).
  Craft questions (concurrency, cache invalidation) were mis-triaged into
  invented buckets instead of expanding normally.
- ❌ **Two-tier layer dropped**: zero SHAPING / DEFERRABLE labels and zero
  "blocks VERIFY unless deferred" gate language anywhere in the output —
  the gate rule keys on SHAPING-class, so an unlabeled draft gives the
  VERIFY gate nothing to act on.
- ❌ **Severity-high — invented answer leaked into the normative layer**:
  spec.md REQ-002 hardcodes "only aggregate settled trades into
  positions" — a de-facto settlement-basis answer to the EXACT question
  the proposal flags as open. Proposal layer says "unknown"; requirements
  layer silently resolves it. Downstream implementers read requirements,
  not proposal flags.

Reading: strong-executor runs honor the prose contract end-to-end; a weak
executor keeps the headline rule (flag the landmine) but drops the
schema discipline, the tiering, and cross-layer consistency — the exact
failure family in
`docs/loom/memory/extraction-severing-cross-ref-needs-weak-model-test.md`
and `docs/loom/memory/pipeline-enforced-gates-beat-drafter-instructions.md`
(prose obligations weak drafters keep violating belong in the PIPELINE).

Candidate mechanical fix (v2.1, not yet built): `validate_spec_output.py`
gains (a) an `evidence_needed:` value whitelist — any value outside the
pinned three fails validation; (b) a presence rule — a draft carrying any
`evidence_needed: domain-convention` tag must also carry a SHAPING or
DEFERRABLE label for it, else fail. (The cross-layer contradiction —
flagged-open vs hardcoded-in-spec — is critic territory, not mechanically
checkable; note for completeness-critic's omission lenses.)

## Weak-model leg 2 — design station, different domain (`--model haiku`, 2026-07-18)

interaction-flows 0.6.0, JP small-business invoicing seed (landmines:
negative-amount ▲ sign convention, 総額表示 tax display, 締め日 billing
cycle). Station+domain both changed to test failure-family generalization.

- ✅ **Enum discipline held**: all 4 tags = `domain-convention` — leg 1's
  invented-value failure did NOT reproduce (intermittent, not systematic).
- ✅ Negative control clean: empty/loading/error stayed flag-only,
  untagged; PRINCIPLES absence surfaced loudly with on-ramp pointer.
- ❌ **SHAPING semantic INVERSION (new variant)**: labeled the questions
  "domain-convention, SHAPING-class (per knowledge-triage)" then declared
  them "deferred to downstream research and do not block this design" —
  the tier's consequence (resolve BEFORE the critic verdict) reversed.
  Leg 1 dropped the labels; leg 2 kept labels and flipped their meaning.
  **Common root across both legs: weak executors preserve VOCABULARY but
  lose ENFORCEMENT SEMANTICS carried only in prose.**
- ⚠️ Lower recall (4 questions vs strong leg's 9) + one soft silent
  assumption: "monthly" resolved to calendar month — 締め日 cycles
  (20日締め etc.) are a genuine JP open question, quietly assumed away.
  Milder than leg 1's REQ-002 but same family.

This reproduces the failure family in mutated form → the BACKLOG entry's
"second weak-model run reproduces" start condition is met.

## Weak-model leg 3 — principles station (`--model haiku`, 2026-07-18)

product-principles 0.10.0, Tokyo meal-kit seed (landmines: churn/retention
industry benchmark, Tokyo price positioning, delivery-window norms). Run
was instructed non-interactive ("pick the most defensible option yourself
and note it") — so the legitimate outs were Open-Questions/punt OR an
explicit `— assumption:` marker; shipping unmarked was the failure bar.

- ❌ **NEW variant: triage evaded by target-invention**: zero
  `evidence_needed` tags and zero `— assumption:` markers in a draft
  dense with market-anchored numbers (churn <7%/mo, 8-month median
  retention, ¥1500-2000/serving, 6pm window, 100% on-time). The
  domain-anchored question ("what does the industry bear?") was silently
  converted into self-set concrete targets — mechanically verifiable,
  epistemically unflagged. The P1 probe had derived this reframe as a
  legitimate path WITH a disclosure note; the live run dropped the note.
- ❌ **NEW variant: provenance fabrication**: the Anchors table labels
  invented numbers "seed constraint" / "anchored to seed" — the seed
  contains none of them. Downstream stations would treat these as
  user-committed constraints. Neither spec nor design leg showed this.
- ✅ **Natural control — the fix thesis confirmed in one artifact**: every
  structurally-validated dimension survived (sections, `— check:` shape,
  `re-trigger:` markers, Deviation Ledger, escalation appetite — exactly
  what `validate_principles_output.py` enforces) while every prose-only
  obligation died. Mechanical gates lived; prose enforcement died —
  within the same weak-model run.

## Cross-leg synthesis (3 weak legs)

| Failure | spec | design | principles |
|---|---|---|---|
| Headline flagging of planted landmine | ✅ | ✅ | ❌ (evaded via invention) |
| Tag enum discipline | ❌ invented values | ✅ | — (no tags at all) |
| Tier/consequence semantics | ❌ dropped | ❌ inverted | — |
| Unmarked invented facts in normative layer | ❌ REQ-002 | ⚠️ calendar-month | ❌ five+ numbers, plus seed misattribution |
| Mechanically-validated dimensions | ✅ | n/a (no validator) | ✅ all survived |

Root cause holds and sharpens: weak executors preserve whatever a
deterministic validator checks, and lose everything enforced only in
prose — vocabulary, tier consequences, disclosure duties, provenance.

## Fix-plan impact

Adds cut (d) to the BACKLOG v2.1 entry: loom-product-principles
`validate_principles_output.py` gains (1) `evidence_needed:`/`assumption:`
marker whitelist when present, (2) a mechanizable provenance check —
Anchors rows claiming seed provenance must quote strings literally
present in the seed. The evasion variant itself (unflagged
target-invention) is judgment-shaped and NOT mechanically checkable —
residual mitigations: principles is interactive in real use (the human
reads the constitution before ratifying; this run removed the human by
instruction), and downstream stations re-derive the domain questions
with their own triage. Label the residual honestly; do not pretend a
grep can catch it.

Full artifacts: session scratchpad `dogfood-live-spec/spec-out/` (strong
leg), `dogfood-live-spec-haiku/spec-out/` (weak spec leg),
`dogfood-live-design-haiku/ui-flows.md` (weak design leg),
`dogfood-live-principles-haiku/docs/loom/PRINCIPLES.md` (weak principles
leg); not preserved beyond the session — this report is the record.
