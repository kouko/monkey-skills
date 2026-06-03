---
name: deep-read
description: Deeply understand ONE large document or book — build a structured understanding (sections, claims, methodology, caveats, argument-structure) of a single source, depth-on-one-source vs deep-research's breadth-across-many. Use when the user wants to thoroughly comprehend one long document, paper, or book, run inside any coding agent host using the host's own tools (zero API-key setup).
version: 0.1.0
---

# deep-read

Deeply understand **ONE** large document, paper, or book. Where
`deep-research` goes **broad** (many sources, adversarially fact-checked),
deep-read goes **deep on a single source** — it builds a structured
*understanding* of that one document: its sections, claims (each grounded
in a verbatim quote), methodology, caveats, and argument structure.

This skill reuses exactly two of `deep-research`'s extract primitives —
`schemas.py` (`EXTRACT_SCHEMA`) and `prompts.py` (`fetch_prompt`) — as
**byte-identical copies** (kept in sync with the deep-research SSOT by the MD5
CI check). It carries neither `rank.py` nor `dedup.py`: deep-read has no quorum
step and its cross-chunk claim merge rolls its own claim-text dedup, so copying
them would be dead code. It adds a stdlib chunker (`chunker.py`) plus
the deep-read-specific schemas + cross-chunk synthesis + report renderer
(`deepread.py`).

## Executor model — who does what

**You (the agent running this skill) are the executor.** You supply the LLM
reasoning and the read capability:

- **LLM reasoning** — you read each chunk, classify its section role,
  extract its claims with supporting quotes, and synthesize the merged
  understanding, emitting JSON that conforms to a bundled schema.
- **Read capability** — your host's own tools (`Read`, `WebFetch`, …) to
  turn the source into text, plus the parallel fan-out for per-chunk work.

The bundled `scripts/*.py` supply **only deterministic logic** — markdown
chunking, prompt text, JSON schemas, claim-dedup, cross-chunk merge, and
markdown rendering. They make **no network calls and read no API keys.**
They are stdlib-only and run with plain `python`.

**No API key is required.** This skill borrows the host agent's own LLM +
read tools (your existing subscription) — there is no key to set, no
separate program to install, no per-call API cost.

**No adversarial verify.** Unlike deep-research's 3-vote quorum, deep-read
does **not** cross-examine claims against other sources — there is only one
source, so quorum has nothing to vote against. Grounding here is
**per-claim verbatim quotes**: every extracted claim carries the exact
sentence from the source that supports it, so a reader can check it against
the original. That is the single-source analogue of deep-research's quorum.

Run all `python scripts/…` commands from the skill's own `scripts/`
directory (paths below are relative to it).

## Portable fan-out convention

The per-chunk extraction (Step 3) does the same work across N independent
chunks. Do this **in parallel by dispatching N subagents**, per
`code-toolkit:dispatching-parallel-agents`: one fresh subagent per chunk,
dispatched in a single assistant message with multiple agent calls so the
harness runs them concurrently.

Describe and dispatch this work **abstractly as "dispatch N subagents"** —
do **not** hard-code the Claude Code Workflow tool. Stated abstractly, the
fan-out maps onto whatever concurrent-subagent primitive the host agent
provides (Claude Code, Codex, Cursor, …); binding to one harness's workflow
primitive would break agent-portability. Each per-chunk subagent is
independent (disjoint chunk, no shared files) — exactly the case the
fan-out convention is for.

---

## Step 1 — Ingest (content-agnostic)

deep-read processes **text**. Get the source as text by **whatever your
host can read** — the format is the host's problem, not deep-read's. *If
the host can read it to text, deep-read can process it.*

- **Local `.md` / `.txt` / PDF** → host `Read` tool (it reads PDFs to text).
- **A URL** → host `WebFetch`, or `obsidian:defuddle` for clean markdown
  with the page chrome stripped.
- **An EPUB** → `tsundoku:book-extract` to convert it into chapter-split
  markdown (one file per chapter).

These are **optional skill-composition pointers**, not dependencies of
deep-read. deep-read itself only needs the text; how you obtained it does
not matter. Use whichever your host supports for the source at hand.

## Step 2 — Chunk

Split the document into ordered chunks so each can be reasoned over
independently.

```
echo '<the document markdown>' | python scripts/chunker.py
```

stdin: markdown text → stdout: a JSON array of chunks, each
`{heading, text, ordinal}`:

- `heading` — the `#`-line that starts the chunk (`""` for any preamble
  before the first heading).
- `text` — the chunk body up to the next **section-level** heading. The
  chunker picks the section level automatically (the shallowest heading level
  that repeats, else the shallowest present), so a lone `#` title + several
  `##` sections splits into one chunk per `##` section (each `##` swallows its
  nested `###` subsections) — not one giant chunk under the title.
- `ordinal` — 0-based index in document order.

A heading-less document collapses to **one** chunk. **If the source is
already chapter-split files** (e.g. `tsundoku:book-extract` output), skip
the chunker and treat **each file as one chunk** — `heading` = the chapter
title, `ordinal` = the file's order.

## Step 3 — Per-chunk extract (fan out)

For each chunk, read it and pull out its claims. This is per-chunk
independent work — **fan out one subagent per chunk** (see the fan-out
convention above) so the chunks are read concurrently.

Each subagent reasons over its single chunk and emits a **chunk
extraction** conforming to the `CHUNK_EXTRACT_SCHEMA` shape — a
module-level dict in `scripts/deepread.py` (read it directly; it has no
print subcommand, mirroring how cite-check exposes `EXTRACT_CITED_CLAIMS`).

Shape (`CHUNK_EXTRACT_SCHEMA`): `{section, claims: [{claim, quote,
importance}], methodology?, caveats?, openQuestions?}` —

- `section` — this chunk's structural role (e.g. `"Methods"`,
  `"Conclusion"`); usually its `heading`.
- `claims` — each a concrete statement plus a **verbatim `quote`** from the
  chunk that supports it, rated `importance ∈ high | medium | low`.
- `methodology` / `caveats` / `openQuestions` — optional section-local
  notes folded into the merged understanding.

This per-chunk shape is **richer** than deep-research's
`schemas.py extract` (it adds the section role + methodology/caveats). You
may reuse the `prompts.py fetch` framing and the `schemas.py extract` claim
fields as a base, but the binding shape is `CHUNK_EXTRACT_SCHEMA`:

```
python scripts/prompts.py fetch --source '<chunk-as-source JSON>' \
  --label deep-read --question "What does this chunk establish?"
python scripts/schemas.py extract
```

## Step 4 — Hierarchical synthesis

Collect every chunk extraction into one JSON array, then merge them into a
single understanding.

```
echo '[<chunk extractions>]' | python scripts/deepread.py merge
```

stdin: the array of chunk extractions → stdout: a merged understanding
conforming to `READ_SCHEMA` (also a module dict in `scripts/deepread.py`).
The merge **dedups claims across chunks** (near-duplicate claims collapse
to the first occurrence), assembles `sections` in chunk order with each
claim tagged by its source `section`, and concatenates
methodology/caveats/openQuestions. Shape: `{sourceQuality, sections[],
claims[] (each {claim, quote, importance, section}), methodology, caveats,
openQuestions, argumentStructure}`.

## Step 5 — Render the report

```
echo '<merged understanding JSON>' | python scripts/deepread.py report
```

stdin: the merged understanding → stdout: a markdown **READ report** — a
sections outline, a claims table (claim · section · importance · quote),
then methodology / caveats / open-questions blocks. Hand this back to the
user as the structured understanding.

---

## Boundary — what deep-read is NOT

- **`tsundoku:book-distill`** turns a book into executable *skills* and
  explicitly **skips comprehension** — it mines for reusable procedures.
  deep-read instead produces a structured *understanding* of the source.
- **`obsidian:wiki-ingest`** ingests *vault notes* into a knowledge wiki.
  deep-read works on one arbitrary document and emits an understanding
  report, not vault pages.

Use deep-read when the goal is to *understand one long source deeply*.

## Script-invocation quick reference

| Step | Command | stdin → stdout |
|---|---|---|
| 2 | `chunker.py` | markdown → chunk array `{heading, text, ordinal}` |
| 3 | `deepread.py` (`CHUNK_EXTRACT_SCHEMA` shape) | — → per-chunk schema (in source) |
| 3 | `prompts.py fetch --source S --label deep-read --question Q` | — → extract prompt (framing reuse) |
| 3 | `schemas.py extract` | — → extract schema (claim-field reuse) |
| 4 | `deepread.py merge` | chunk extractions → merged understanding (`READ_SCHEMA`) |
| 5 | `deepread.py report` | merged understanding → markdown READ report |
