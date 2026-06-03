---
name: cite-check
description: Audit an existing document's cited claims — fetch each cited source and check it actually supports the claim; flag unsupported / misattributed / dead-link citations. Use when the user wants to verify that a document's citations hold up, run inside any coding agent host using the host's own LLM + web tools (zero API-key setup).
version: 0.1.0
---

# cite-check

Audit the citations in a document **you did not write**. For every claim that
carries a citation, fetch the cited source and check whether that source
*actually supports the claim* — then flag the ones that don't (unsupported /
misattributed / dead-link). The output is an audit report, not a rewrite.

This skill reuses `deep-research`'s fetch + extract primitives (the bundled
`prompts.py` / `schemas.py` / `dedup.py` are **byte-identical copies** of
deep-research's, kept in sync) and adds a citation-specific parser
(`parse_doc.py`) and support-verdict + audit-report logic (`citecheck.py`).

## Executor model — who does what

**You (the agent running this skill) are the executor.** You supply the LLM
reasoning and the web tools:

- **LLM reasoning** — you bind each cited anchor to the claim it supports,
  read each fetched source, and decide whether it supports the claim, emitting
  JSON that conforms to a bundled schema.
- **Web fetch** — your host `WebFetch` tool, used to retrieve each cited
  source.

The bundled `scripts/*.py` supply **only deterministic logic** — markdown
citation parsing, prompt text, JSON schemas, URL-dedup, support-verdict
normalization, and markdown rendering. They make **no network calls and read
no API keys.** They are stdlib-only and run with plain `python`.

**No API key is required.** This skill borrows the host agent's own LLM + web
tools (your existing subscription) — there is no key to set, no separate
program to install, no per-call API cost.

Run all `python scripts/…` commands from the skill's own `scripts/` directory
(paths below are relative to it).

## Scope — correctness, not faithfulness

This skill checks **correctness**: *does the cited source support the claim it
is cited for?* It does **not** check **faithfulness** (*did the author actually
rely on that source when writing?*) — author-reliance is unknowable for a
foreign document you did not produce (cf. arXiv 2412.18004, "Correctness is not
Faithfulness in RAG Attributions").

Two v1 boundaries:

- **Non-URL references** (DOIs, book titles, bare author-year) are
  **flagged and skipped** — they surface in the report as `citedRef` rows but
  are not fetched or verified. Resolving them is a deferred sub-system.
- **Unsourced claims** (a claim-bearing line that cites nothing) are reported
  as a **separate class** (`unsourced`), not audited. The auditor names them
  so the reader sees what was *not* backed, but makes no support call.

The default verifier is a **single voter** — citation-support is more
deterministic than open-web fact-checking, so one read is usually enough. For
high-stakes audits you may opt into the copied `rank.py quorum` (3 voters,
same mechanics as deep-research Stage 5).

---

## Stage 1 — Parse the document

Get the deterministic citation scaffold, then bind each cited anchor to its
claim.

1. Feed the document's markdown to the parser:

   ```
   echo '<the document markdown>' | python scripts/parse_doc.py
   ```

   stdin: markdown text → stdout: a JSON array of **anchors**, each one of:
   - `{type:"inline",  citedUrl, anchorText, locator}` — a `[text](url)` link.
   - `{type:"footnote", citedRef, citedUrl, locator}` — a `[^n]`/`[n]` marker
     resolved (where possible) to its reference-list URL; `citedUrl` is `null`
     if the reference carried no URL.
   - `{type:"unsourced", anchorText, locator}` — a claim-bearing line with no
     citation. `locator` is a 1-based line number, stable against the doc.

2. **Bind anchors to claims (LLM).** The parser gives you *where* the citations
   are; you decide *what claim each one backs*. Reason over the document +
   anchors and emit a binding object conforming to the `EXTRACT_CITED_CLAIMS`
   schema — a module-level dict in `scripts/citecheck.py` (read it directly;
   it has no print subcommand).

   Shape (`EXTRACT_CITED_CLAIMS`): `{claims: [{claim, citedUrl|citedRef,
   locator}]}` — one entry per cited claim, carrying exactly one of `citedUrl`
   (audit it) or `citedRef` (non-URL → flag-and-skip). Carry the `unsourced`
   anchors straight through to the report; do not bind them.

---

## Stage 2 — Fetch each cited source

For every **distinct cited URL** in the bound claims, retrieve what the source
actually says. This is per-source independent work — **fan out one subagent per
source** (per `code-toolkit:dispatching-parallel-agents`) when there are
several.

1. **Dedup the cited URLs first** so the same source is fetched once even if it
   is cited for several claims:

   ```
   echo '{"results": [{"url": "<cited url>"}, ...], "seen": {}, "fetch_slots": 50}' \
     | python scripts/dedup.py
   ```

   stdin `{results, seen, fetch_slots}` → stdout `{novel, seen, slots}`. It
   normalizes URLs (strips `www.`, trailing `/`, lowercases) so
   `www.X.com/a/` and `x.com/a` collapse to one fetch.

2. For each distinct URL, fetch it with host `WebFetch`, then extract what the
   source says. Get the extraction prompt (pass the **claim being audited** as
   `--question` so the extraction is anchored to what you need to check):

   ```
   python scripts/prompts.py fetch --source '<source JSON>' \
     --label cite-check --question "<the claim this source is cited for>"
   ```

   Reason over the fetched content and emit an extraction object conforming to:

   ```
   python scripts/schemas.py extract
   ```

   Shape: `{sourceQuality, publishDate, claims}` — what the source itself
   asserts, which you compare against the cited claim in Stage 3.

3. A URL that is **dead, paywalled, or 404** cannot be checked → carry it into
   Stage 3 as `unresolvable` (do not guess support from the citation text).

---

## Stage 3 — Support verdict (per claim × source)

For each (claim, cited-source) pair, answer one focused question: **does THIS
cited source support THIS claim?** This is a narrower judgment than
deep-research's adversarial refutation — you are checking attribution, not
hunting the open web.

Reason over the bound claim and the Stage-2 extraction, and emit a verdict
conforming to the `SUPPORT_VERDICT` shape in `citecheck.py`:

- `support ∈ supported | partial | unsupported` — the **3-way** call: does the
  source fully back, partially back, or fail to back the claim.
- `misattributed: bool` — the source is about a *different* claim than the one
  it was cited for (a flag, not a support state; the support call still
  stands).
- `unresolvable: bool` — the source could not be fetched (Stage 2 dead-link).
- `evidence` — a verbatim quote from the source backing your support call.

`citecheck.py`'s `classify_support` normalizes these: `unresolvable` overrides
the support state, and a missing support call with no citation collapses to
`unsourced`. With quorum opted in, collect 3 such verdicts and reduce them via
`python scripts/rank.py quorum` exactly as deep-research Stage 5 does.

---

## Stage 4 — Audit report

Collect every per-citation result row (each a `SUPPORT_VERDICT` object,
optionally carrying `claim` / `citedUrl` / `citedRef` for display, plus the
`unsourced` rows) into one JSON array and render the audit:

```
echo '[<result rows>]' | python scripts/citecheck.py report
```

stdin: the result-row array → stdout: a markdown **audit report** — a
per-citation verdict table (claim · cited source · verdict · note/flags)
followed by a summary of the **six counts**: supported / partial / unsupported
/ misattributed / unresolvable / unsourced.

For just the summary counts (no table):

```
echo '[<result rows>]' | python scripts/citecheck.py verdict
```

stdin: the same array → stdout `{counts: {<six buckets>: int}, total: int}`.

Hand the rendered markdown report back to the user as the audit result.

---

## Script-invocation quick reference

| Stage | Command | stdin → stdout |
|---|---|---|
| 1 | `parse_doc.py` | markdown → citation anchors array |
| 1 | `citecheck.py` (EXTRACT_CITED_CLAIMS shape) | — → binding schema (in source) |
| 2 | `dedup.py` | `{results, seen, fetch_slots}` → `{novel, seen, slots}` |
| 2 | `prompts.py fetch --source S --label cite-check --question CLAIM` | — → fetch prompt |
| 2 | `schemas.py extract` | — → extract schema |
| 3 | `citecheck.py` (SUPPORT_VERDICT shape) | — → verdict schema (in source) |
| 3 | `rank.py quorum` (opt-in) | verdicts array → `true`/`false` |
| 4 | `citecheck.py report` | result rows → markdown audit report |
| 4 | `citecheck.py verdict` | result rows → summary counts JSON |
