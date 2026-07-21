---
name: ticker-to-cik-can-resolve-to-a-decoy-entity
description: A ticker's CURRENT SEC CIK can resolve to a new holding shell / subsidiary / successor entity, not the operating history — a naive historical pull then returns EMPTY (or truncated) with no error; verify CIK continuity before any multi-year fetch, and never stitch across a discontinuity
type: gotcha
origin: feat-8k-earnings-kpi-intake (88-filer 30-year 8-K census, investing-toolkit, 2026-07-19)
---

Resolving a ticker to a SEC CIK today does NOT guarantee that CIK holds the
company's operating filing history. A 30-year census across 88 filers found
several tickers whose current ticker→CIK mapping points at a DECOY entity:
- **XOM** → CIK 2115436, a 2026 holding shell with ~26 filings — the real
  1994-2025 Exxon history is under CIK **34088** (still an active filer).
- **BLK** → CIK 2012383 (a 2024 holdco reorg) — real history under **1364742**
  (public since 1999).
- **BA** → a leasing-subsidiary decoy CIK **711513** exists alongside the
  operating CIK **12927**.
- **GOOGL** → current-ticker Alphabet CIK **1652044** (2015 reorg) truncates the
  predecessor Google Inc. history under **1288776**.
- **ORCL** → current-ticker CIK **1341439** (2005 reincorporation) truncates the
  predecessor under **777676**.

The failure is SILENT: a historical fetch keyed on the decoy CIK returns an
empty or short filing list, not an error — so a pipeline reports "no history"
for a company with 30 years of filings.

**Why:** corporate reorgs (holding-company inversions, redomiciliations,
reincorporation mergers, spin-offs) mint a NEW CIK while the ticker follows the
successor. SEC's ticker→CIK map tracks the current legal entity, not the
history-bearing one. edgartools / companyfacts keyed on the current CIK inherit
this — the aggregation is per-CIK, so the predecessor's years simply are not there.

**How to apply:** before any multi-year historical pull, verify the resolved
CIK actually spans the expected date range (e.g. first-filing year vs the
company's known public-since year); if the history starts suspiciously late,
the ticker resolved to a successor/decoy — look up the predecessor CIK and use
it. Record the discontinuity and DO NOT stitch across it (predecessor and
successor are legally distinct filers; a stitched series conflates two
entities). Relates to
[[sec-companyfacts-frames-api-omits-dimensional-members]] (same "the obvious
single-CIK path silently drops data" class).
