---
name: 2026-08-18-modal-token-extracted-as-an-anchor-collides-with-the-modality-map
description: adjudication_split extracts a bare modal like MUST as an ALLCAPS anchor, so lint demands it verbatim in the rendition, while the protocol's fixed modality map says must→必須 (translated) — two rules pointing opposite directions at the same token, hit twice independently on 2026-08-18
status: OPEN
origin: 2026-08-18 stale-render arc — hit first by the orchestrator rendering this arc's own brief view (lint reported `missing anchor 'MUST'`), then independently by a cold dogfood agent following the protocol from scratch; both resolved it the same ad-hoc way
start: next adjudication_split.py or adjudication_lint.py touch, or the next time a rendition trips this lint line
---

# A modal token extracted as an anchor collides with the modality map

`adjudication_split.py`'s anchor extraction is mechanical: `ALLCAPS_RE`
pulls any 2+ uppercase run out of `source_text`, so a source sentence
written as "the worker MUST retry" yields `MUST` as an anchor. The lint's
anchor-echo check is a HARD check — the anchor must appear **verbatim** in
the rendition.

The protocol's Fixed modality mapping says the opposite for the same token:
`must` maps to 必須, a translated form, and nothing outside that closed set
counts.

- **Origin**: 2026-08-18 stale-render arc — hit first by the orchestrator rendering this arc's own brief view (lint reported `missing anchor 'MUST'`), then independently by a cold dogfood agent following the protocol from scratch; both resolved it the same ad-hoc way
- **Start**: next adjudication_split.py or adjudication_lint.py touch, or the next time a rendition trips this lint line

## What both parties did

Wrote both forms — 必須 plus a literal `MUST` alongside it. That satisfies
both checks and reads slightly oddly in Chinese. Nobody was following a
rule; both improvised the same workaround, which is the signal that the
rules leave a real hole rather than that one party misread them.

## Why it is not a lint bug

The anchor check is correctly hard, and the modality map is correctly a
closed set. The gap is that neither rule knows the other exists: a modal
verb is the one token class that is BOTH a mechanically-extracted anchor
and a mapped modality.

## Candidate fixes (not yet chosen)

- Exclude the five mapped modals from `ALLCAPS_RE`'s anchor harvest — the
  modality check already covers them, so the anchor check adds nothing but
  a contradiction. Cheapest, and narrows nothing a reader needs.
- Or teach the anchor check that a mapped modal is satisfied by its mapped
  form. More faithful, more machinery.
- Or state the resolution in the protocol so both parties improvise the
  same way ON PURPOSE. Weakest — it documents the collision rather than
  removing it.

Evidence when this is picked up: the two 2026-08-18 occurrences above, both
in this repo's session transcripts.
