---
name: fact-check
description: Lightweight single-claim adversarial verdict — supported / refuted / inconclusive with cited evidence. Use when one factual claim needs checking mid-conversation — the host agent gathers a little evidence and runs the same adversarial quorum as deep-research, returning a verdict (not a report), using the host's own WebSearch/WebFetch + LLM with zero API-key setup.
version: 0.1.0
---

# fact-check

A **lightweight, single-claim** adversarial verifier. You hand it one factual
claim; it gathers a little evidence, runs the *same* adversarial quorum
deep-research uses, and returns a **verdict** — `supported` / `refuted` /
`inconclusive` with cited evidence and a confidence — **not** a multi-page
report.

This is the **point-check** counterpart to `deep-research`. Where
deep-research fans out across 3–6 angles and dozens of sources to synthesize a
breadth report, fact-check spends a small budget on **one** claim and stops at
the verdict. It reuses deep-research's verify + quorum primitives directly:
`schemas.py`, `rank.py`, `prompts.py`, `dedup.py` in this skill's `scripts/`
are **byte-identical copies** of deep-research's (kept in sync by a repo-level
MD5 drift check). Only `factcheck.py` — the Stage-C verdict mapper — is new.

## Executor model — who does what

**You (the agent running this skill) are the executor.** You supply the LLM
reasoning, the web tools, and the per-voter fan-out:

- **LLM reasoning** — you rank search hits, extract supporting/contradicting
  quotes, and cast the adversarial votes yourself, emitting JSON that conforms
  to a bundled schema.
- **Web search** — your host `WebSearch` tool.
- **Web fetch** — your host `WebFetch` tool.
- **Fan-out** — you dispatch the parallel verifier voters (see below).

The bundled `scripts/*.py` supply **only deterministic logic** — prompt text,
JSON schemas, URL-dedup, ranking, quorum, the verdict mapping. They make **no
network calls and read no API keys.** They are stdlib-only and run with plain
`python`.

**No API key is required.** This skill borrows the host agent's own LLM + web
tools (your existing subscription) — there is no key to set, no separate
program to install, no per-call API cost. The reasoning and I/O ride on the
agent you are already in.

Run all `python scripts/…` commands from this skill's own `scripts/`
directory (paths below are relative to it).

## Portable fan-out convention

Stage B casts `VOTES_PER_CLAIM = 3` independent verifier votes. Do these **in
parallel by dispatching 3 subagents**, per
`code-toolkit:dispatching-parallel-agents`: one fresh subagent per
`voter_idx`, dispatched in a single assistant message with multiple agent
calls so the harness runs them concurrently.

Describe and dispatch this work **abstractly as "dispatch N subagents"** — do
**not** hard-code the Claude Code Workflow tool. Stated abstractly, the fan-out
maps onto whatever concurrent-subagent primitive the host agent provides
(Claude Code, Codex, Cursor, …); binding to one harness's workflow primitive
would break agent-portability. The three voters are independent (same claim,
disjoint `voter_idx`, no shared files), exactly the case the fan-out is for.

---

## Stage A — Gather evidence

Spend a **small** budget confirming *and* disconfirming the one claim.

1. Run host `WebSearch` **once or twice**: one query phrased to *confirm* the
   claim, one phrased to *disconfirm* it (e.g. `"<claim>"` and
   `"<claim> debunked OR false OR contradicted"`). Keep it to 1–2 queries —
   this is a point-check, not a breadth sweep.

2. Rank/filter the raw hits into structured results. Treat the claim as a
   single search angle. Get the ranking prompt:

   ```
   python scripts/prompts.py search --angle '{"label":"claim","query":"<q>"}' --question "<the claim>"
   ```

   Reason over it and emit results conforming to:

   ```
   python scripts/schemas.py search
   ```

   Shape: `{results: [...]}`, each result carrying at least `url` and a
   `relevance` rank.

3. Dedup and cap to a **small** fetch budget — **≤6 sources** for a
   point-check (well under deep-research's `MAX_FETCH = 15`). The dedup script
   normalizes URLs (strips `www.`, trailing `/`, lowercases host+path) so
   `www.X.com/a/` and `x.com/a` collapse to one:

   ```
   echo '{"results": [...], "seen": {}, "fetch_slots": 6}' | python scripts/dedup.py
   ```

   stdin `{results, seen, fetch_slots}` → stdout `{novel, seen, slots}`:
   `novel` is the deduped, budget-capped sources to fetch. High-relevance hits
   are never budget-dropped, so a strongly-sourced claim can exceed the slot
   count slightly — that is fine for a point-check.

4. For **each novel source**, fetch it with host `WebFetch` and extract a
   supporting **or** contradicting quote bearing on the claim. Get the
   extraction prompt:

   ```
   python scripts/prompts.py fetch --source '{"url":"<url>","title":"<title>"}' --label "claim" --question "<the claim>"
   ```

   Reason over the fetched content and emit an extraction object conforming to:

   ```
   python scripts/schemas.py extract
   ```

   Shape: `{sourceQuality, publishDate, claims}` — tag each extracted item with
   its `sourceQuality` and `importance`. Collect the per-source quote, URL, and
   quality tag into one small evidence pool for the claim.

If **no evidence** is found (every search empty, every fetch paywalled/dead),
skip to Stage C with an empty verdict list — the mapper returns
`inconclusive`.

---

## Stage B — Verify (adversarial quorum)

The one claim faces **`VOTES_PER_CLAIM = 3`** independent adversarial voters
whose job is to *refute* it, each grounded in the Stage-A evidence. **Fan out
one subagent per `voter_idx` (0, 1, 2)** per the convention above.

For each `voter_idx`:

1. Get that voter's prompt (the per-voter `--voter-idx` diversifies the three
   votes so they do not echo):

   ```
   python scripts/prompts.py verify --claim '{"claim":"<the claim>","sourceUrl":"<url>","sourceQuality":"<tag>","quote":"<quote>"}' --voter-idx <i> --question "<the claim>"
   ```

2. The voter reasons (it may run its own `WebSearch`/`WebFetch` to hunt
   counter-evidence) and emits a verdict conforming to:

   ```
   python scripts/schemas.py verdict
   ```

   Shape: `{refuted: bool, evidence, confidence, counterSource?}`. A voter that
   fails or returns nothing is an **abstention** — record its vote as `null`,
   not as a non-refutation.

3. Collect the three votes into an array (abstentions as `null`).

---

## Stage C — Verdict

Map the three votes to the 3-way taxonomy with `factcheck.py`:

```
echo '[<verdict>, <verdict-or-null>, <verdict>]' | python scripts/factcheck.py verdict
```

stdin: the verdicts array → stdout a JSON object
`{verdict, confidence, valid_count, refuted_count}`:

- **`supported`** — survives the quorum (`rank.quorum_survives`: ≥2 valid
  votes AND fewer than `REFUTATIONS_REQUIRED = 2` of them refute it).
- **`refuted`** — ≥`REFUTATIONS_REQUIRED` valid votes carry `refuted: true`.
- **`inconclusive`** — anything else. This covers the three weak cases:
  **all-abstain** (`[null, null, null]`), **fewer than 2 valid votes**, and
  **empty input** (`[]` — no evidence was found in Stage A). The valid-count
  check gates first, so an all-abstain claim is never falsely "supported" on a
  refuted-count of 0.

`confidence` is the strongest confidence among the non-refuting valid votes
(else `low`).

Return the verdict to the user as a short answer: the claim, the
`supported`/`refuted`/`inconclusive` label, the confidence, and the cited
quotes + source URLs from Stage A that back it. Do **not** synthesize a full
report — that is deep-research's job.

---

## Script-invocation quick reference

| Stage | Command | stdin → stdout |
|---|---|---|
| A | `prompts.py search --angle A --question Q` | — → search prompt |
| A | `schemas.py search` | — → search schema |
| A | `dedup.py` | `{results, seen, fetch_slots}` → `{novel, seen, slots}` |
| A | `prompts.py fetch --source S --label L --question Q` | — → fetch prompt |
| A | `schemas.py extract` | — → extract schema |
| B | `prompts.py verify --claim C --voter-idx I --question Q` | — → verify prompt |
| B | `schemas.py verdict` | — → verdict schema |
| C | `factcheck.py verdict` | verdicts array → `{verdict, confidence, valid_count, refuted_count}` |
