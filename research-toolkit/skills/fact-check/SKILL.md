---
name: fact-check
description: |
  Single-claim adversarial verdict — supported / refuted / inconclusive with cited evidence. Use when one factual claim needs checking mid-conversation: 'is it true…?', 'really?', '這個說法對嗎' — even common knowledge. Full report → deep-deep-research.
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

Run all `python scripts/…` commands from this skill's **root** directory (the
examples below keep the `scripts/` prefix, so they resolve as written; the
scripts' flat imports work because Python puts the script's own directory on
`sys.path`). Do **not** add a second `scripts/` by running from inside
`scripts/` — `python scripts/factcheck.py` from there looks for
`scripts/scripts/…` and fails.

## Portable fan-out convention

Stage B casts `VOTES_PER_CLAIM = 3` independent verifier votes. Do these **in
parallel by dispatching 3 subagents**, per
`loom-code:dispatching-parallel-agents`: one fresh subagent per
`voter_idx`, dispatched in a single assistant message with multiple agent
calls so the harness runs them concurrently.

Describe and dispatch this work **abstractly as "dispatch N subagents"** — do
**not** hard-code the Claude Code Workflow tool. Stated abstractly, the fan-out
maps onto whatever concurrent-subagent primitive the host agent provides
(Claude Code, Codex, Cursor, …); binding to one harness's workflow primitive
would break agent-portability. The three voters are independent (same claim,
disjoint `voter_idx`, no shared files), exactly the case the fan-out is for.

**Independence is a GATE, not a nicety.** The quorum only means something if
the three votes come from **independent** contexts — separate parallel
subagents, or (if the host cannot parallelize) three **fresh sequential**
subagent contexts. Reasoning out three "votes" in your **own single context**
is **not** a quorum: the votes echo each other and `factcheck.py` cannot tell
them from one opinion copied three times. If you genuinely cannot achieve
independent fan-out and have to vote in one shared context, you **MUST** pass
`--solo` to Stage C — the verdict will be forced to `inconclusive`
(`reason: no-quorum`). Faking three same-context votes without `--solo` is the
gate-bypass this rule exists to forbid. Prefer real fan-out; `--solo` is a
last resort that yields a deliberately weak verdict.

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
   python scripts/prompts.py search --angle '{"label":"claim","rationale":"why this checks the claim","query":"<q>"}' --question "<the claim>"
   ```

   (`rationale` is optional but include it — omitting it renders a dangling
   "claim — " in the prompt.) Reason over it and emit results conforming to:

   ```
   python scripts/schemas.py search
   ```

   Shape: `{results: [...]}`, each result carrying at least `url`, `title`, and
   `relevance` — an **enum** `{high, medium, low}`, **not** a number (passing an
   integer raises `ValueError: unknown relevance`).

3. Dedup and cap to a **small** fetch budget — **≤6 sources** for a
   point-check (well under deep-research's `MAX_FETCH = 15`). The dedup script
   normalizes URLs (strips `www.`, trailing `/`, lowercases host+path) so
   `www.X.com/a/` and `x.com/a` collapse to one:

   ```
   echo '{"results": [...], "seen": {}, "fetch_slots": 6}' | python scripts/dedup.py
   ```

   stdin `{results, seen, fetch_slots}` → stdout `{novel, seen, slots}`:
   `novel` is the deduped, budget-capped sources to fetch. `dedup.py` itself
   never drops high-relevance hits, so `novel` may come back **longer** than the
   slot count — that is expected; you still cap *fetching* at the budget in
   step 4 (highest-relevance first), not here.

4. For each novel source — **highest-`relevance` first, up to the ≤6 budget**;
   high-relevance overflow past the budget is *optional*, not mandatory (this
   is the point-check's small-budget rule — do not fetch every novel source if
   that blows the budget) — fetch it with host `WebFetch` and extract a
   supporting **or** contradicting quote bearing on the claim. If a fetch fails
   (paywall / dead link / HTTP error), the extraction prompt returns
   `claims: []` with `sourceQuality: "unreliable"` — drop that one source and
   continue; a single dead source is **not** the all-empty case below. Get the
   extraction prompt:

   ```
   python scripts/prompts.py fetch --source '{"url":"<url>","title":"<title>"}' --label "claim" --question "<the claim>"
   ```

   Reason over the fetched content and emit an extraction object conforming to:

   ```
   python scripts/schemas.py extract
   ```

   Shape: `{sourceQuality, publishDate, claims}` — tag each extracted item with
   its `sourceQuality` ∈ {`primary`, `secondary`, `blog`, `forum`,
   `unreliable`} and `importance` ∈ {`central`, `supporting`, `tangential`}.
   Collect the per-source quote, URL, and quality tag into one small evidence
   pool for the claim.

If **no evidence** is found, skip to Stage C with an empty verdict list — the
mapper returns `inconclusive`. **Distinguish two empty cases**, because they
mean opposite things to a reader:

- **No referent** — the claim names a specific entity / event / study and the
  search finds **no trace of it at all** (not just thin coverage — *nothing*).
  For a falsifiable, specific, recent claim, that absence is itself
  disconfirming (a real version would leave a footprint). Pass `--no-referent`
  to Stage C so the verdict is tagged `reason: no-referent`.
- **Insufficient evidence** — the topic is real but coverage is thin,
  paywalled, or conflicting. Do **not** pass the flag; the verdict is tagged
  `reason: insufficient-evidence`.

---

## Stage B — Verify (adversarial quorum)

The one claim faces **`VOTES_PER_CLAIM = 3`** independent adversarial voters
whose job is to *refute* it, each grounded in the Stage-A evidence. **Fan out
one subagent per `voter_idx` (0, 1, 2)** per the convention above.

**First, reduce the Stage-A evidence pool to one claim object.** Stage A
produces a *pool* of extracted items (multiple sources, each with a quote),
but the verify prompt takes a single `{claim, sourceUrl, sourceQuality,
quote}`. Collapse the pool to **one** object: set `claim` to the claim under
check, and `sourceUrl` / `sourceQuality` / `quote` to the **single strongest
supporting** item in the pool — *strongest* = highest `sourceQuality`, ties
broken by `importance` — or, if nothing supports it, the **most relevant
contradicting** item. All three voters receive this **same** object;
they diverge only by `--voter-idx` and by each independently `WebSearch`-ing
for counter-evidence (verify checklist step 2), so a narrow representative
quote does not lose the rest of the pool — the voters re-expand it. This
single-object reduction is the point-check's deliberate narrowing: unlike
`deep-research`, which ranks up to `MAX_VERIFY_CLAIMS = 25` extracted claims
and casts 3 votes on **each**, fact-check casts exactly **one** 3-voter quorum
on the single top-level claim — which is why Stage C's `factcheck.py` takes
exactly three verdicts.

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

   Shape: `{refuted: bool, evidence, confidence, counterSource?}`, where
   `confidence` ∈ {`high`, `medium`, `low`}. A voter that fails or returns
   nothing is an **abstention** — record its vote as `null`, not as a
   non-refutation.

3. Collect the three votes into an array (abstentions as `null`).

---

## Stage C — Verdict

Map the three votes to the 3-way taxonomy with `factcheck.py`. Two opt-in
flags, each set **only** in its specific case: `--no-referent` when Stage A
found the claim has no referent at all (see Stage A's two-empty-cases note),
and `--solo` when Stage B's votes did **not** come from independent contexts
(see Portable fan-out convention → independence gate):

```
echo '[<verdict>, <verdict-or-null>, <verdict>]' | python scripts/factcheck.py verdict
# claim whose named entity/event has zero footprint:
echo '[]' | python scripts/factcheck.py verdict --no-referent
# votes were reasoned in one shared context (no independent fan-out possible):
echo '[<verdict>, <verdict>, <verdict>]' | python scripts/factcheck.py verdict --solo
```

stdin: the verdicts array → stdout a JSON object
`{verdict, reason, confidence, valid_count, refuted_count}`:

- **`supported`** (`reason: quorum-survived`) — survives the quorum
  (`rank.quorum_survives`: ≥2 valid votes AND fewer than
  `REFUTATIONS_REQUIRED = 2` of them refute it).
- **`refuted`** (`reason: quorum-refuted`) — ≥`REFUTATIONS_REQUIRED` valid
  votes carry `refuted: true`.
- **`inconclusive`** — anything else (all-abstain `[null, null, null]`, fewer
  than 2 valid votes, or empty input). The valid-count check gates first, so
  an all-abstain claim is never falsely "supported" on a refuted-count of 0.
  The `reason` field splits this bucket:
  - **`reason: no-referent`** — `--no-referent` was passed: the claim's named
    entity/event has **zero footprint**, so absence is disconfirming. Surface
    this as *"no trace of this exists — likely fabricated"*, **not** a neutral
    "couldn't determine". This is the F-003 guard against under-calling hoaxes.
  - **`reason: no-quorum`** — `--solo` was passed: the votes did not come from
    independent contexts, so the quorum's integrity precondition failed and it
    cannot conclude (F-004). Say plainly that an independent check could not be
    run. This gate fires before the others — non-independent votes never drive
    `supported`/`refuted`.
  - **`reason: insufficient-evidence`** — real topic, thin/conflicting
    evidence: genuine *"not enough to judge"*.

`confidence` ∈ {`high`, `medium`, `low`} is direction-aware: the strongest
confidence among the votes that drove the verdict (non-refuting for
`supported`, refuting for `refuted`); else `low`. **Calibration caveat:** when
the claim uses an absolute quantifier (*never / always / all / none*) but the
evidence only supports a **conditional** version, cap each voter's `confidence`
at `medium` — "honey *never* spoils" is over-stated even when "sealed honey is
shelf-stable" is well-sourced (`factcheck.py` cannot see claim scope, so this
is the voter's call).

Return the verdict to the user as a short answer: the claim, the
`supported`/`refuted`/`inconclusive` label, **and — when `inconclusive` — which
`reason`** (a `no-referent` answer must read as "likely fabricated", not
"undecided"), the confidence, and the cited quotes + source URLs from Stage A
that back it. Do **not** synthesize a full report — that is deep-research's job.

---

## When a step fails

The `scripts/*.py` are deterministic and stdlib-only; failures are almost
always a malformed input you can fix and re-run.

- **A script errors** (traceback / non-zero exit) — it is a bad-input bug, not
  a verdict. Re-read the schema (`python scripts/schemas.py <name>`), fix the
  JSON you piped in (common cause: a value outside an enum, e.g. an integer
  `relevance`), and re-run. Never swallow the error and proceed.
- **A host tool is missing** (no `WebSearch` / `WebFetch`) — this skill cannot
  run without them; say so plainly rather than fabricating evidence. With no
  evidence gathered, the honest output is `inconclusive` /
  `reason: insufficient-evidence`.
- **A single voter subagent fails** — that vote is an **abstention** (`null`),
  per Stage B; do not retry forever or substitute a non-refutation.

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
| C | `factcheck.py verdict [--no-referent] [--solo]` | verdicts array → `{verdict, reason, confidence, valid_count, refuted_count}` |
