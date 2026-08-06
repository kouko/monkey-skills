# Dogfood: progress-card roadmap view — three-leg haiku cold-read probe

Date: 2026-08-06
Branch: fix-plan-card-ascii-marks (probes by-path at the T5 commit)
Verdict: **3/3 CLEAN** (one honest scope note on leg a)

Probe tier: haiku, one fresh context per leg, written exercises. Leg
(a)'s input was a constructed sample card (CSV-export scenario,
embedded verbatim in the probe prompt), not a repo plan — chosen so
the leg tests card-reading with zero repo context.

| Leg | Surface | Verdict |
|---|---|---|
| a | a titled+glossed rendered card alone | CLEAN (order/parallel/done/remaining) |
| b | family-relay §(a2) frame contract | CLEAN |
| c | wp duty + plan-format schema (language rule) | CLEAN |

## Leg a — card comprehension

From the card alone: execution order and parallelism read correctly
("T1/T2/T3 parallel in step 1; T4 after all three — explicit needs:
annotation; T5 after T4"); done/in-progress/remaining fully correct.
Q3 (what a [!] explanation opens with) was answered by inference from
the card (dependency-blocking) rather than the legislated stop-reason
forms — scope note: that contract lives in §(a2), which leg (a) was
deliberately not given; leg (b) verifies it.

## Leg b — frame contract

All three verbatim: both stop-reason opening forms + the
conversation-language rendering (「需要你的決定：…」／「等待外部條
件：…」for a zh-TW conversation); the grounded-gloss clause ("derived
from that task's own plan fields — cite the source item, never
invent"); the station-narration ban quoted and correctly applied to
refuse a wave/reviewer-arm sentence.

## Leg c — language rule

Both scenarios correct: zh-TW user → zh-TW Steps/Gloss at plan time;
English user → English, nothing hardcodes Chinese ("in the user's
conversation language" quoted from both surfaces). The
never-restatement contract quoted, with a correct violating example
("Implement CSV renderer functionality") contrasted against the
worked example's real gloss.

## Reading

The three failure directions — misreading the roadmap structure,
paraphrasing past the stop-reason opening, and assuming the mechanism
is Chinese-hardcoded — all came back correctly refused at the haiku
tier. Leg (a) additionally confirmed the roadmap layout carries the
order/dependency story without any frame help.
