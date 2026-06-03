# Brief: deep-read skill (research-toolkit)

Date: 2026-06-03 · Plugin: research-toolkit · Sibling of: deep-research
Batch: 3 of 3 (fact-check / cite-check / deep-read) — recommended build order #3 (heaviest: book-scale synthesis + cross-plugin reuse)

## Problem (Axis 1)

`deep-research` goes BROAD across many web sources (URL-only, ≤5 claims per
source). The user's need is the opposite and at a scale deep-research cannot
reach: **deeply understand ONE large document — up to an entire book** — and
produce a structured understanding (argument structure, key claims, findings,
methodology, caveats), grounded in source locations.

Critically, the repo's `tsundoku:book-distill` explicitly **skips comprehension**
— its frontmatter says "❌ Skip: book summaries / book reviews"; it turns a
book's methodology into *executable skills* (RIA-TV++), a different output.
`tsundoku:book-extract` only chunks EPUB→Markdown (a pre-processor).
`obsidian:wiki-ingest` is vault-coupled note ingestion. So "structured
understanding of a large document" is a genuine, unowned gap.

JTBD: *When I have a large document or a whole book I need to understand
deeply, I want a structured, location-grounded comprehension — argument
structure, claims, findings, methodology, caveats — without it being diluted
into a multi-source breadth sweep (deep-research) or turned into skills
(book-distill).*

## Users (Axis 2)

Repo owner (kouko), reading large expository works / papers / reports. Job
story: *When I own an EPUB (or have a long markdown/PDF/URL), I run
`deep-read <source>`, so the agent reads it section-by-section at book scale
and returns a structured understanding I can navigate, not a flat summary.*

## Smallest End State (Axis 3)

A `research-toolkit/skills/deep-read/` skill that, given one large source,
returns a structured **read report**
`{sourceQuality, sections[], claims[], methodology, caveats, openQuestions,
argumentStructure}` (claims keep deep-research's `{claim, quote, importance}`
shape, plus a location/section locator):

- **Ingest**: EPUB → delegate to `tsundoku:book-extract` (pandoc/NCX chapter
  split); local markdown/txt → Read; URL → `obsidian:defuddle` (clean markdown)
  with WebFetch fallback. (PDF/docx → defer or via pandoc.)
- **Chunk**: section/chapter-aware (book-extract already chunks EPUB by chapter).
- **Per-chunk extract**: reuse `fetch_prompt` + `EXTRACT_SCHEMA` with the ≤5
  cap LIFTED and extra fields (methodology / caveats / section role).
- **Hierarchical synthesis (the real new logic)**: map-reduce across hundreds
  of pages — merge/dedup claims, build argument structure, maintain coherence.
- **Render**: structured read report (vault-agnostic; NOT skills, NOT vault notes).

## Current State Evidence

- **Forward / Reuse**: `research-toolkit/skills/deep-research/scripts/prompts.py:66`
  (`fetch_prompt` — the per-source extractor), `scripts/schemas.py:71`
  (`EXTRACT_SCHEMA`) + `:157` (`ExtractedClaim`), `scripts/dedup.py` (merge/dedup
  claims across chunks). Cross-plugin: `tsundoku:book-extract` (EPUB ingestion),
  `obsidian:defuddle` (URL→clean markdown).
- **Genuinely NEW (substantial — this is why it's a real skill, not glue)**:
  (1) book-scale **chunking + section-aware reading** (deep-research never
  chunks; caps at 5 claims/source); (2) **hierarchical/map-reduce synthesis**
  across hundreds of pages maintaining coherence; (3) **local-file / non-URL
  input** adapter; (4) richer extraction schema (methodology / caveats /
  argument structure) absent from `EXTRACT_SCHEMA`.
- **Boundary (sharp, verified by reading the skills)**:
  - vs `tsundoku:book-distill` — book-distill OUTPUT = executable skills, and it
    *explicitly skips summaries/comprehension*; deep-read OUTPUT = structured
    understanding. No overlap; complementary (could even run before book-distill).
  - vs `tsundoku:book-extract` — REUSE it as the EPUB front-end; don't rebuild
    chunking.
  - vs `obsidian:wiki-ingest` — wiki-ingest writes vault-coupled notes (frontmatter,
    wikilinks, manifest, no web); deep-read is vault-agnostic, single-shot, URL-capable.
  - vs `obsidian:defuddle` — defuddle only cleans a web page; deep-read calls it
    for ingestion, then does the extraction defuddle doesn't.
- **Risk / coupling**: format deps (EPUB/PDF) break deep-research's stdlib-only,
  zero-dependency promise — but `book-extract` already carries pandoc, so reuse
  rather than re-add. research-toolkit → tsundoku/obsidian cross-plugin reuse
  follows CLAUDE.md's cross-plugin contract; must be explicit, not implicit.

## Decision

Build `deep-read` as a standalone depth-complement skill scoped to **large-document
comprehension** (up to book scale). Reuse deep-research's extract primitive +
`tsundoku:book-extract` (EPUB) + `obsidian:defuddle` (URL); the new, load-bearing
work is book-scale chunking + hierarchical synthesis + a richer read schema.
Output is a vault-agnostic structured read report (NOT skills like book-distill,
NOT vault notes like wiki-ingest). Build LAST of the three (heaviest new logic +
cross-plugin coupling); validate the sibling-reuse pattern on fact-check first.

## Alternatives Considered (Axis 4 — research-grounded)

Single-source deep reading is well-precedented and distinct from breadth.
Sources (EN): GPT Researcher (local-document research, LangChain chunking),
arXiv 2603.14629 (ResearchPilot — per-paper extraction as a distinct module),
2509.20493 (InsightGUIDE — guided critical reading of one paper), Anara/SciSpace
(per-paper methodology extraction + passage grounding). (JA): NotebookLM (ground
strictly in the uploaded source, inline passage citations — mirrors deep-read's
"go deep on ONE source"), laxuai (Abstract/Method/Results sectioned-prompt
practice). **Alternatives rejected**: (a) make it a deep-research `--single-source`
mode — rejected because book-scale chunking + hierarchical synthesis is too much
to bolt onto deep-research without muddying its breadth identity, and the user
wants a distinct trigger for "understand this book"; (b) drop it / use wiki-ingest
— rejected because wiki-ingest is vault-coupled and book-distill skips
comprehension, leaving the gap genuinely unowned.

## Open Questions

- OQ1: Does deep-read keep any adversarial verify? (single-source self-verify is
  weak — lean: drop verify, lean on grounding + quotes instead.)
- OQ2: Chunking ownership — reuse book-extract for EPUB; for other long docs,
  LLM-native sectioned reading vs a chunker lib (affects portability).
- OQ3: Local file formats — text/markdown free; PDF/docx need pandoc (via
  book-extract?) — scope to text+EPUB first?
- OQ4: Output contract — make the read report a superset of `REPORT_SCHEMA` so a
  deep-read result could feed INTO a deep-research run as a pre-read source?
- OQ5: Cross-plugin reuse mechanism — how does research-toolkit invoke
  `tsundoku:book-extract` / `obsidian:defuddle` cleanly (delegation contract)?

## Out of Scope

- Turning the book into skills (that is `tsundoku:book-distill`).
- Writing into an Obsidian vault (that is `obsidian:wiki-ingest`).
- Multi-source breadth research (that is `deep-research`).
- Author-persona role-play.
