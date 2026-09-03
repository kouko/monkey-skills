# docs/loom/ index

A human index of what is in this directory and whether it is live. The
layout itself is explained in [`README.md`](README.md); this file only
answers "what is in there, and how much of it". Nothing regenerates
this file — the living-spec index generator that used to own it was
deleted at loom 1.0.

## Live

| Path | Count | Note |
|---|---|---|
| [`intent/`](intent/) | 1 | one file per change; `status:` line says whether it is open, confirmed or closed |
| `2026-09-02-simple-loom-flow/` | — | the loom 1.0 change folder: concept model, spec, plan, `review.json`, `evidence/` |
| [`evidence/`](evidence/) | 152 | repo-level evidence — see the breakdown below |
| [`memory/`](memory/) | 258 | practice-memory store, one fact per file ([charter](memory/README.md)) |
| [`maps/`](maps/) | 1 map | `family-relocation` |
| [`KICKOFF-DEFAULTS.md`](KICKOFF-DEFAULTS.md) | 5 keys | this repo's standing answers |
| [`PURPOSE.md`](PURPOSE.md) | — | why this repo exists and what it rules out |

### Inside `evidence/`

| Path | Count | What it is |
|---|---|---|
| [`mechanisms.yaml`](evidence/mechanisms.yaml) | — | the mechanism inventory the recompute gate diffs a branch against |
| [`attack-catalogue.md`](evidence/attack-catalogue.md) | — | the adversarial catalogue the review station attacks from |
| [`audits/`](evidence/audits/) | 23 | audit reports and changesets |
| [`dogfood/`](evidence/dogfood/) | 94 | dogfood and A/B run records |
| [`research/`](evidence/research/) | 20 | research notes behind loom design decisions |
| [`references/`](evidence/references/) | 3 | runbooks and reference maps |
| [`firing-corpus/`](evidence/firing-corpus/) | 4 | skill firing-test corpus |
| [`task-batch-review/`](evidence/task-batch-review/) | 3 | the batch-review proposal record (the mechanism itself was deleted at 1.0) |
| [`outcome-map-v3/`](evidence/outcome-map-v3/) | 3 | the outcome-map v3 proposal record |

## Frozen — read-only, no station reads them

Each carries an `ARCHIVED.md`. See [`README.md`](README.md#frozen-stores--read-only-history)
for why they were frozen rather than converted.

| Path | Count | Span |
|---|---|---|
| [`plans/`](plans/) | 268 | 2026-05-18 → 2026-09-01 |
| [`specs/`](specs/) | 260 | 2026-05-18 → 2026-09-01, plus 1 undated |
| [`backlog/`](backlog/) + [`BACKLOG.md`](BACKLOG.md) | 182 entries indexed, 16 still open | 2026-07-02 → 2026-09-01 |
| [`design/`](design/) | 5 | 2026-06-11 → 2026-08-29 |
| [`archive/`](archive/) | 2 change folders | 2026-07-18, 2026-08-28 |
| [`2026-07-12-us-sec-primary-source-layer/`](2026-07-12-us-sec-primary-source-layer/) | 4 | old change folder |
| [`2026-07-19-8k-prose-kpi-intake/`](2026-07-19-8k-prose-kpi-intake/) | 4 | old change folder |
