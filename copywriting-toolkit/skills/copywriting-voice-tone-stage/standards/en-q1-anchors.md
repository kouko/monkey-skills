---
title: EN Voice Anchors — Q1 Authority-Reason (Router Index)
tier: 2
schema_version: router-v1
migrated_date: 2026-04-21
---

# Q1 Authority-Reason — EN Anchor Router

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q1"` AND `brief.output_language == "en"`. Router index.

## Overview

Q1 = Authority × Reason. EN canonical:
- **Reason-why DR tradition** (Claude Hopkins → Ogilvy)
- **Plain-style canonical** (Strunk & White, Orwell)
- **New Yorker longform authority** (McPhee)
- **Iceberg / compressed minimalism** (Hemingway, Carver, Hempel) — toward-Q4 edge
- **DDB-era plain style** (Bernbach)

## Landmark: center

- **David Ogilvy — Rolls-Royce 1958 + Hathaway Man** (CW, 1911-1999) — [anchor-en-ogilvy-rolls-royce-reason-why.md](anchor-en-ogilvy-rolls-royce-reason-why.md)
  - Slug: `en-ogilvy-rolls-royce-reason-why`

- **Martin Puris — BMW engineering-precision** (CW, Ammirati & Puris 1975-1996) — [anchor-en-martin-puris-bmw-engineering-precision.md](anchor-en-martin-puris-bmw-engineering-precision.md)
  - Slug: `en-martin-puris-bmw-engineering-precision`
  - Recast from "BMW Ultimate Driving Machine" campaign entry.

- **David Abbott — Economist Aphoristic Register** (named CW/ECD, AMV BBDO co-founder 1977) — [anchor-en-david-abbott-economist-aphoristic.md](anchor-en-david-abbott-economist-aphoristic.md)
  - Slug: `en-david-abbott-economist-aphoristic`
  - Register: 6-12 word finished-thought aphorism; flattery of implied-intelligent-peer; white-out-of-red template; long-copy discipline as counter-weight
  - ⚠ Over-mimic HIGH: most-imitated intelligent-brand register 1990-2020
  - Recast from: AMV BBDO The Economist campaign anchor (v1.3.x) → named CW David Abbott (v1.8.0)

**Moved to format-templates**:
- Economist institutional (post-Abbott brand voice, separate from AMV ad campaigns) → [en-institutional-and-platform-aggregate.md](../../../../docs/anchor-references/en-institutional-and-platform-aggregate.md) §Economist

## Landmark: extreme

- **Claude Hopkins — Scientific Advertising** (CW, 1866-1932) — [anchor-en-hopkins-scientific-reason-why.md](anchor-en-hopkins-scientific-reason-why.md)
  - Slug: `en-hopkins-scientific-reason-why`

**Moved to format-templates**:
- WebMD / Reuters / Bloomberg wire-reference register → [en-institutional-and-platform-aggregate.md](../../../../docs/anchor-references/en-institutional-and-platform-aggregate.md)

## Landmark: toward-Q2

- **Bill Bernbach / DDB — VW "Think Small"** (ECD) — [anchor-en-bernbach-ddb-confession-plain-style.md](anchor-en-bernbach-ddb-confession-plain-style.md)
  - Slug: `en-bernbach-ddb-confession-plain-style`

- **Jason Fried + DHH — Basecamp contrarian manifesto** (named author duo) — [anchor-en-basecamp-fried-dhh-contrarian-manifesto.md](anchor-en-basecamp-fried-dhh-contrarian-manifesto.md)
  - Slug: `en-basecamp-fried-dhh-contrarian-manifesto`
  - Register: 2-3 sentence chapter openers; antithesis-as-headline ("Meetings are toxic"); aphorism→cost→pivot 3-beat rhythm; plain-style contrarian startup voice
  - Dual placement: Q1 toward-Q2 (manifesto mode) + Q4 center (plain-practical mode)
  - Recast from: Basecamp Rework manifesto + center brand anchors (v1.3.x) → named authors Fried + DHH (v1.8.0)

## Landmark: toward-Q4

- **John McPhee — New Yorker longform** (author) — [anchor-en-mcphee-new-yorker-detail-reportage.md](anchor-en-mcphee-new-yorker-detail-reportage.md)
  - Slug: `en-mcphee-new-yorker-detail-reportage`

- **Hemingway iceberg-minimalism** (author) — [anchor-en-hemingway-iceberg.md](anchor-en-hemingway-iceberg.md)
  - Slug: `en-hemingway-iceberg`
  - ⚠ Over-mimic HIGH: "He was tired. The whisky was cold." + he-said/she-said chains. Meta-core mitigation: "pair with Carver/Didion; forbid dialogue-tag chains >2".
  - Safe substitute available (v1.11.0): `anchor-en-carver-working-class-precision.md` carries `safe_substitute_for: [Hemingway]` — documented iceberg-descendant at LOWER risk (MEDIUM-HIGH vs HIGH); Pass 3 auto-suggests when user names Hemingway.

- **Raymond Carver — working-class precision** (author) — [anchor-en-carver-working-class-precision.md](anchor-en-carver-working-class-precision.md)
  - Slug: `en-carver-working-class-precision`
  - `safe_substitute_for: [Hemingway]` — see substitute note on Hemingway entry above.

- **Amy Hempel — compressed minimalism** (author, Lish lineage) — [anchor-en-hempel-compressed-minimalism.md](anchor-en-hempel-compressed-minimalism.md)
  - Slug: `en-hempel-compressed-minimalism`

- **Strunk & White / E.B. White** (author duo) — [anchor-en-strunk-white-plain-style.md](anchor-en-strunk-white-plain-style.md)
  - Slug: `en-strunk-white-plain-style`

- **George Orwell — "Politics and the English Language"** (author) — [anchor-en-orwell-politics-english-plain-style.md](anchor-en-orwell-politics-english-plain-style.md)
  - Slug: `en-orwell-politics-english-plain-style`

## Cross-references

- **JP Q1**: `anchor-jp-soseki-yoyu-ha-dry-observer.md` / `anchor-jp-itami-juzo-keimyou-shadatsu.md` + format-templates (天声人語 / 東洋経済 / 日経社説)
- **zh-TW Q1**: register-references (天下 / 報導者 / 商業周刊); individual-creator gap-flagged

## Migration history

- **v1.0-v1.5.x**: aggregate with 13 inline entries (Ogilvy + AMV Economist + BMW + Economist institutional + WebMD/Reuters/Bloomberg + Hopkins + Bernbach + Basecamp + McPhee + Hemingway + Carver + Hempel + Strunk&White + Orwell)
- **v1.6.0** (this file): 10 individual-creator entries moved to flat `anchor-*.md`; 3 institutional entries moved to format-templates aggregate; AMV Economist + Basecamp recast deferred (v1.7.0+)
