---
name: deep-deep-research
description: Deep research harness — fan-out web searches, fetch sources, adversarially verify claims, synthesize a cited report. Use when the user wants a deep, multi-source, fact-checked research report on any topic, run inside any coding agent host using the host's own LLM + web tools (zero API-key setup).
version: 0.1.0
---

# deep-deep-research

A multi-source, adversarially-verified research pipeline that produces a
cited report. It reproduces the content of Claude Code's built-in
`deep-research` workflow (scope → search → dedup → fetch → 3-vote verify →
synthesize) as an **inspectable, editable skill** you run with the host
agent's own tools.

## Executor model — who does what

**You (the agent running this skill) are the executor.** You supply all the
LLM reasoning, the web tools, and the parallel fan-out:

- **LLM reasoning** — you scope the question, extract claims, vote on
  verdicts, and write the report yourself, emitting JSON that conforms to a
  bundled schema.
- **Web search** — your host `WebSearch` tool.
- **Web fetch** — your host `WebFetch` tool.
- **Fan-out** — you dispatch parallel subagents for per-angle and per-claim
  work (see below).

The bundled `scripts/*.py` supply **only deterministic logic** — prompt text,
JSON schemas, URL-dedup, ranking, quorum, stats/markdown. They make **no
network calls and read no API keys.** They are stdlib-only and run with plain
`python`.

**No API key is required.** This skill borrows the host agent's own
LLM + web tools (your existing subscription) — there is no key to set, no
separate program to install, no per-call API cost. That is the whole point
versus a headless Python port: the reasoning and I/O ride on the agent you
are already in.

Run all `python scripts/…` commands from the skill's own `scripts/`
directory (paths below are relative to it).

## Portable fan-out convention

Several stages do the same work across N independent inputs (one search per
angle, three verifier votes per claim). Do these **in parallel by dispatching
N subagents**, per `code-toolkit:dispatching-parallel-agents`: one fresh
subagent per independent input, dispatched in a single assistant message with
multiple agent calls so the harness runs them concurrently.

Describe and dispatch this work **abstractly as "dispatch N subagents"** — do
**not** hard-code the Claude Code Workflow tool. Stated abstractly, the fan-out
maps onto whatever concurrent-subagent primitive the host agent provides
(Claude Code, Codex, Cursor, …); binding to one harness's workflow primitive
would break agent-portability. Each per-input subagent is independent (disjoint
inputs, no shared files), which is exactly the case the fan-out convention is
for.

---

## Stage 1 — Scope

Turn the user's question into 3–6 distinct research **angles**.

1. Get the scope prompt:

   ```
   python scripts/prompts.py scope --question "<the user's question>"
   ```

2. Reason over that prompt and emit a scope object as JSON. It must conform to
   the schema printed by:

   ```
   python scripts/schemas.py scope
   ```

   Shape: `{question, summary, angles}` where `angles` is **3–6** items, each
   `{label, query, ...}`. The `query` is the WebSearch string for that angle;
   the `label` tags everything downstream.

Keep the angles genuinely distinct — they become the parallel search fan-out.

### Opt-in: Verbalized Sampling (VS) scope mode

This is an **opt-in alternative** to the default 3–6-angle scope above. The
default Stage 1 (the `scope`/`scope_prompt` path) is **unchanged** and remains
the standard route — use VS mode only when you want a wider candidate pool
that deliberately surfaces *non-obvious* angles alongside the obvious ones
(Verbalized Sampling: over-generate, tier by typicality, then keep a
high-typicality "head" plus a low-typicality "tail"). VS mode produces angles
in the **same shape** the default scope emits, so Stage 2 onward is untouched.

1. **Over-generate candidates.** Get the VS scope prompt:

   ```
   python scripts/scope_vs.py prompt --question "<the user's question>"
   ```

   Reason over it and emit ~`CANDIDATE_COUNT` (**12**) candidate angles
   conforming to the schema printed by:

   ```
   python scripts/scope_vs.py schema
   ```

   Shape: `{question, summary, candidates}` where each candidate is
   `{label, query, rationale, relevance, typicality_tier}` —
   `relevance` ∈ `high`/`medium`/`low`, and `typicality_tier` ∈
   `most-obvious`/`mid`/`least-obvious` (ranked **relatively within this one
   call**, scored blind to authorship).

2. **Self-consistency (calibration).** Re-run the scope reasoning
   `SELF_CONSISTENCY_RUNS` (**2**) times — text-only, no fetch, so it is cheap
   — and keep only candidates whose `typicality_tier` is **stable across the
   runs**. This is the over-confidence guard: a candidate whose tier flips
   between runs has an unreliable self-rated typicality and should not be
   trusted to fill a head or tail slot.

3. **Face-validity check** (the #1 risk — typicality self-eval reliability).
   Before trusting the tiers, **print the candidates with their tiers** and
   eyeball whether the `least-obvious` picks are genuinely non-obvious yet
   still relevant. If a "surprise" angle is actually off-topic or trivially
   obvious, drop or re-tier it — the selector trusts the tiers you feed it.

4. **Select head + tail.** Feed the calibrated candidates to the deterministic
   selector:

   ```
   echo '{"candidates": [...], "head_k": 3, "tail_k": 2}' \
     | python scripts/vs_select.py
   ```

   stdin `{candidates, head_k, tail_k}` → stdout `{angles}`. It applies a
   high-typicality **head** floor plus a low-typicality **tail** of surprises,
   relevance-floored (drops `low`), deduped by label/normalized-query, with the
   tail lexically de-redundified, capped at **≤ 6** angles. Each returned angle
   is stripped to `{label, query, rationale}` — the **same shape** the default
   scope emits.

5. **Feed Stage 2 unchanged.** Hand the returned `angles` into the **unchanged
   Stage 2 (Search + dedup)** exactly as you would the default scope angles.
   Nothing downstream of Stage 1 changes.

**Eval pointer.** After running both arms (VS vs the default baseline) over a
question set, `python scripts/metric_novelty.py` computes the two-arm metric —
how much of the VS arm's confirmed evidence the baseline never fetched
(novel-AND-confirmed contribution rate) plus a per-question win direction. It
reads the two arms' per-question data on stdin as JSON and writes the aggregate
on stdout. This is **eval tooling**, not part of the live research pipeline.

### Opt-in: Framework completeness-audit

This is an **opt-in, ADDITIVE pass** that runs **after Stage 1 and before
Stage 2** — it tops up the angle set rather than replacing it. It works after
**either** the default scope path **or** VS mode (both emit the same angle
shape), and the **default path is unchanged**: skip this pass and Stage 2 sees
the original angles untouched. The framework is an **AUDITOR, not a
generator** — the free-form/VS scope stays the angle generator; this pass only
walks analytical-framework cells against the angles you already have and
proposes gap-fill angles for the cells nothing covers.

1. **Classify the question type.** Get the type-classify prompt:

   ```
   python scripts/framework_audit.py classify-prompt --question "<q>"
   ```

   Reason over it against the **routing table** in
   `references/framework-audit-library.md` and pick **2–3** audit frameworks
   for this question's type (add one reinforcement framework only if the
   route's cells feel thin).

2. **Walk cells + propose gaps.** Get the cell-walk audit prompt, passing the
   angles you already have **and the 2–3 frameworks you picked in step 1**
   (omit `--frameworks` only to fall back to the general any-question route):

   ```
   python scripts/framework_audit.py audit-prompt \
     --angles '<angles JSON>' --frameworks '["<framework>", ...]' --question "<q>"
   ```

   Reason over the chosen frameworks' cell-blocks in
   `references/framework-audit-library.md`: walk each framework **cell by
   cell** against the angle set, and for every **uncovered** cell propose one
   gap-fill angle conforming to the schema printed by:

   ```
   python scripts/framework_audit.py schema
   ```

   Shape: `{question, gaps}` where each gap is
   `{label, query, framework, cell, rationale?}`. Finish with a pass over the
   **7 collective blind-spots** at the bottom of the library (the dimensions
   *all* frameworks structurally miss). An empty gap list is a valid, honest
   result — don't pad it.

3. **Select within budget.** Feed the gaps + the existing angles to the
   deterministic selector:

   ```
   echo '{"gap_angles": [...], "existing_angles": [...], \
          "fetch_slots": <remaining MAX_FETCH>}' \
     | python scripts/framework_audit.py select
   ```

   stdin `{gap_angles, existing_angles, fetch_slots}` → stdout `{angles}`. It
   dedups each gap against the existing angles (and earlier gaps) by
   case-folded label / normalized query, caps survivors to the remaining
   `fetch_slots`, and strips each to the `{label, query, rationale?}` angle
   shape — the **same shape** Stage 2 always sees. `fetch_slots <= 0` → `[]`.

4. **Feed Stage 2 unchanged.** Append the returned gap `angles` to the
   original angle set and hand the augmented set into the **unchanged Stage 2
   (Search + dedup)**. Nothing downstream of Stage 1 changes.

5. **Verify-backfill check (POST-pipeline).** After the pipeline runs through
   Stage 5 (verify), confirm each gap-fill angle actually *landed* evidence —
   the fix for a flagged structural cell that research silently dropped.
   Collect `confirmed_labels` = the set of angle **labels** whose claims
   survived Stage-5 quorum (each confirmed claim traces to its angle's label,
   since the label tags everything downstream). Then run:

   ```
   echo '{"gap_angles": [...], "confirmed_labels": [...]}' \
     | python scripts/framework_audit.py backfill
   ```

   Pass the **TAGGED gap angles** (the `audit-prompt` output, which still
   carries `framework` + `cell` — **not** the `select` output, which stripped
   them) so the report can name which framework cell came up empty. stdin
   `{gap_angles, confirmed_labels}` → stdout
   `{unlanded, landed_count, unlanded_count}`. For each `unlanded` gap, either
   **re-search that angle within the remaining `MAX_FETCH` budget**, **or**
   surface it in the report as an explicitly-flagged known gap (*"dimension X
   was flagged important but no reliable evidence was found"*). Degradation:
   empty `unlanded` → nothing to do.

**Cost.** Steps 1–2 are **one text-only LLM pass each — no fetch**; the agent
reasons over the bundled library only. Gap angles cost fetches **only if
added**, and that is gated to the remaining budget in step 3. **Empty gaps →
proceed with the original angles** (degradation contract: the audit never
blocks the pipeline).

---

## Stage 2 — Search + dedup

**Fan out: one subagent per angle.** For each of the 3–6 angles, dispatch a
subagent that does the following for its single angle, then returns its novel
sources:

1. Run host `WebSearch` on the angle's `query`.

2. Rank/filter the raw hits into structured results. Get the ranking prompt:

   ```
   python scripts/prompts.py search --angle '<angle JSON>' --question "<q>"
   ```

   Reason over it and emit results conforming to:

   ```
   python scripts/schemas.py search
   ```

   Shape: `{results: [...]}`, each result carrying at least `url` and a
   `relevance` rank.

3. Remove already-seen sources and enforce the global fetch budget
   (`MAX_FETCH = 15`) with the dedup script — it normalizes URLs
   (strips `www.`, trailing `/`, lowercases host+path) so `www.X.com/a/` and
   `x.com/a` collapse to one:

   ```
   echo '{"results": [...], "seen": {...}, "fetch_slots": <remaining>}' \
     | python scripts/dedup.py
   ```

   stdin `{results, seen, fetch_slots}` → stdout `{novel, seen, slots}`:
   `novel` is the deduped, budget-capped sources to fetch; `seen` is the
   updated seen-map; `slots` is the remaining budget. The budget only drops
   medium/low-relevance results — **high-relevance hits are never
   budget-dropped**, so a flooded angle can exceed the nominal slot count.

The `seen` map and `fetch_slots` are **shared across angles** — they are the
budget. Thread them sequentially through the dedup calls (merge each
subagent's results into the running `seen`/`slots`) rather than letting two
angles each spend the full budget. The per-angle WebSearch + ranking is the
parallel part; the dedup accounting reconciles the shared budget.

---

## Stage 3 — Fetch + extract

For each **novel** source surfaced by Stage 2, fetch it and extract claims.
This is again per-source independent work — **fan out one subagent per source**
(or per small batch) when there are several.

1. Fetch the page with host `WebFetch` (use the source `url`).

2. Extract claims from the fetched text. Get the extraction prompt:

   ```
   python scripts/prompts.py fetch --source '<source JSON>' \
     --label "<angle label>" --question "<q>"
   ```

   Reason over the fetched content and emit an extraction object conforming
   to:

   ```
   python scripts/schemas.py extract
   ```

   Shape: `{sourceQuality, publishDate, claims}`. Tag the **sourceQuality** of
   the page and, per claim, its **importance** — these tags carry forward into
   ranking and verification.

Collect every extracted claim (with its source URL, quote, and quality tag)
into one pool. That pool is the input to the ranking + adversarial verify
stages.

---

## Stage 4 — Rank

Flatten **every** claim from every angle's every source into one JSON array,
then rank it. This is a **barrier**: all the Stage-3 fan-out subagents must
have returned before you rank, because ranking is global across the whole
pool.

```
echo '[<all claims>]' | python scripts/rank.py
```

stdin: the claims array → stdout: the top **`MAX_VERIFY_CLAIMS = 25`** claims,
stable-sorted by (importance, sourceQuality). Lower-priority claims past the
cap are dropped — you only adversarially verify the ranked survivors.

---

## Stage 5 — Verify (adversarial quorum)

Each ranked claim faces **`VOTES_PER_CLAIM = 3`** independent adversarial
voters whose job is to *refute* it. **Fan out one subagent per
`(claim, voter_idx)` pair** — for 25 claims that is up to 75 independent
voter subagents, dispatched per the fan-out convention.

For each `(claim, voter_idx)`:

1. Get that voter's prompt (note the per-voter `--voter-idx` so the three
   votes diversify rather than echo):

   ```
   python scripts/prompts.py verify --claim '<claim JSON>' \
     --voter-idx <i> --question "<q>"
   ```

2. The voter reasons (it may run its own `WebSearch`/`WebFetch` to hunt
   counter-evidence) and emits a verdict conforming to:

   ```
   python scripts/schemas.py verdict
   ```

   Shape: `{refuted: bool, evidence, confidence, counterSource?}`. A voter
   that fails or returns nothing is an **abstention** — record its vote as
   `null`, not as a non-refutation.

3. Collect the claim's three votes into an array (abstentions as `null`) and
   decide survival:

   ```
   echo '[<verdict>, <verdict-or-null>, <verdict>]' \
     | python scripts/rank.py quorum
   ```

   stdin: the verdicts array → stdout: `true` / `false`. A claim **survives
   only if ≥2 valid (non-null) votes AND fewer than `REFUTATIONS_REQUIRED = 2`
   of them refute it.** The valid-count check gates first, so an
   **all-abstain claim is killed** (0 valid votes < 2), never falsely
   survived on a refuted-count of 0.

Partition the ranked claims into **confirmed** (survived) and **killed**
(refuted/insufficient) by their `quorum` result.

---

## Stage 6 — Synthesize

1. Build the prompt blocks from the verify results:

   ```
   echo '{"ranked_claims": [...], "vote_results": [<bool>...], \
          "verdicts_per_claim": [[<verdict>...], ...]}' \
     | python scripts/synthesis.py blocks
   ```

   stdin: the ranked claims, the per-claim survival booleans (Stage-5
   `quorum` results, same order), and each claim's verdict list → stdout
   `{confirmed_block, killed_block}` (two pre-formatted markdown strings).

2. Get the synthesis prompt, passing those two blocks back as strings plus the
   confirmed count:

   ```
   python scripts/prompts.py synthesis --question "<q>" \
     --confirmed-block '<confirmed_block>' \
     --killed-block '<killed_block>' \
     --confirmed-count <N>
   ```

3. Reason over that prompt and emit the final report conforming to:

   ```
   python scripts/schemas.py report
   ```

   Shape: `{summary, findings: [{claim, confidence, sources, evidence, vote?}],
   caveats, openQuestions?}`.

### Opt-in: Meta-mode synthesis-stance routing

This is an **opt-in, ADDITIVE** wrap on Stage 6 steps 2–3. The **default
synthesis path is unchanged**: skip this and the base synthesis prompt from
`prompts.py synthesis` (step 2) drives synthesis as written. When enabled, you
classify the question's epistemic mode **from the verified evidence** (not the
question text) and **PREPEND** a one-paragraph stance directive ahead of that
base prompt. **CRITICAL — wrap, never modify:** `prompts.py` is a synced SSOT
primitive behind a CI MD5 gate; you **PREPEND** the stance block to the base
synthesis prompt string and do **NOT** edit `prompts.py`. The base prompt stays
**byte-identical**.

It fixes the base prompt's *false-consensus bias* (it instructs "answer the
question + give high confidence to consistent findings", which on a genuinely
contested question silently promotes one position to the headline).

After Stage 5 you have the `confirmed_block` / `killed_block` from
`synthesis.py blocks` (step 1). Then:

1. **Classify the mode from the evidence.** Get the classify prompt:

   ```
   python scripts/mode_route.py classify-prompt \
     --confirmed-block '<CB>' --killed-block '<KB>' --question "<q>"
   ```

   Reason over it — judge by the evidence's **stance spread**, not the
   question framing (an "X vs Y" phrasing biases toward over-calling
   contested) — and emit a verdict conforming to the schema printed by:

   ```
   python scripts/mode_route.py schema
   ```

   Shape: required `mode_binary` (`settled` / `unsettled`) plus optional soft
   `mode_label` (`clear` / `complicated` / `complex` / `chaotic`). The robust
   signal is **settled-vs-unsettled**; the `mode_label` sub-distinction is a
   **low-confidence soft signal** (model-dependent noise — never hinge hard
   behavior on it). When unsure, **fail-safe to `unsettled`**.

2. **Get the stance directive:**

   ```
   echo '{"mode_binary":"<settled|unsettled>","mode_label":"<optional>"}' \
     | python scripts/mode_route.py stance
   ```

   stdin `{mode_binary, mode_label?}` → stdout `{stance_block}`. Behavior:
   **settled** → state the consensus clearly, don't over-hedge a fact into
   false uncertainty; **unsettled** → don't force a verdict, map competing
   positions, calibrate confidence DOWN; **chaotic** (via `mode_label`) →
   additionally flag volatility / recency. Unknown / missing `mode_binary`
   fail-safes to the unsettled directive.

3. **PREPEND, then synthesize.** Prepend the returned `stance_block` string
   ahead of the **byte-identical** base synthesis prompt from step 2, and
   reason over the combined prompt to emit the same report schema (step 3).
   You do **not** edit `prompts.py` — the stance directive is a prefix only.

**Degradation.** If classify fails or returns nothing, fall back to the
**unmodified** base synthesis prompt — never block synthesis.

### Opt-in: Purpose-fit relevance-floor

This is an **opt-in, ADDITIVE** end-check on Stage 6. The **default 360° path
is unchanged**: skip this and the base synthesis runs exactly as written
above. When enabled, it operates on the **Stage-5 confirmed claims** and
classifies them against an *inferred decision purpose* — a relevance **floor**,
not a filter: a claim that scores `not_relevant` is **down-weighted in
emphasis, never deleted**. It fixes the base prompt's tendency to weight every
confirmed claim equally regardless of whether it bears on the decision the
asker is actually trying to make.

It reads the decision-frame catalog `references/purpose-frames.md` (the
question type's analytical frames) when running in **multi-frame** mode.

After Stage 5 you have the `confirmed_block` from `synthesis.py blocks`
(step 1). Then:

1. **Infer the purpose + confidence, classify the claims.** Get the prompt:

   ```
   python scripts/purpose_fit.py purpose-classify-prompt \
     --question "<q>" --confirmed-block '<CB>'
   ```

   Reason over it: infer the decision purpose behind the question and attach a
   `confidence`; then bucket **every** Stage-5 confirmed claim into
   `decisive` / `contextual` / `not_relevant` per frame — **without deleting
   any** (a demoted claim is RETAINED and LABELED, never removed). Emit a
   verdict conforming to the schema printed by:

   ```
   python scripts/purpose_fit.py schema
   ```

   Shape: required `inferred_purpose`, `confidence`, `mode`
   (`consolidated` / `multi-frame`), `mooting_factors`, and `frames` (each
   with `decisive` / `contextual` / `not_relevant` claim-ref arrays). High
   confidence → `consolidated` (foreground the one decision-frame); low /
   ambiguous → `multi-frame` (read `references/purpose-frames.md`, present the
   frames evenly).

2. **Render the directive:**

   ```
   echo '{"inferred_purpose":"...","confidence":"...","mode":"...", \
          "mooting_factors":[...],"frames":[...]}' \
     | python scripts/purpose_fit.py block
   ```

   stdin verdict (`purpose_fit.py schema`) → stdout `{purpose_fit_block}`.
   **moot-hoist:** any `mooting_factors` — confirmed claims that could SETTLE
   the decision OUTRIGHT — are surfaced as a top-level callout **ABOVE** the
   frames, never buried inside a frame bucket.

3. **PREPEND, then synthesize.** Prepend `purpose_fit_block` ahead of the
   synthesis prompt. When both this lever and meta-mode are enabled the prepend
   order is **purpose-fit → meta-mode → base synthesis prompt** (base
   `prompts.py synthesis` stays **byte-identical**). **CRITICAL — wrap, never
   modify:** never edit `prompts.py` — same discipline as meta-mode; the
   purpose-fit directive is a prefix only.

**Degradation.** If classify fails or returns nothing, fall back to the
**unmodified** base synthesis prompt — never block synthesis.

---

**Final render (base Stage 6 — runs in all modes).** After synthesis (with or
without the opt-in meta-mode / purpose-fit prepends above), produce stats + the
rendered markdown:

   ```
   echo '{"report": {...}, "ranked_claims": [...], "angles": [...], \
          "all_claims": [...], "confirmed": [...], "killed": [...]}' \
     | python scripts/synthesis.py report
   ```

   stdin keys as shown → stdout `{stats, markdown}`. `markdown` is the final
   cited report to hand back to the user; `stats` is the pipeline summary
   (angles / sourcesFetched / claimsExtracted / claimsVerified / confirmed /
   killed / agentCalls).

---

## Degradation — never crash, always return a partial report

Three stages can come up empty. In each case **return a partial report**, do
not error out:

1. **No claims extracted / ranked** (Stage 4 yields an empty array — every
   fetch failed, was paywalled, or surfaced nothing) → return a *"no claims
   found"* report: state the question, that no verifiable claims were
   gathered, and what was attempted. Skip verify + synthesis.

2. **All claims refuted** (Stage 5 leaves the confirmed set empty — every
   ranked claim was killed by quorum) → return an *"all claims refuted —
   inconclusive"* report: surface the killed claims (the `killed_block` is
   already formatted for this) and mark the finding inconclusive rather than
   asserting anything.

3. **Synthesis fails** (Stage 6 step 3 produces no valid report object) →
   **salvage the confirmed claims unmerged**: emit them as a flat list (claim
   + source + evidence) with a note that automatic synthesis failed, rather
   than discarding verified work.

---

## Script-invocation quick reference

| Stage | Command | stdin → stdout |
|---|---|---|
| 1 | `prompts.py scope --question Q` | — → scope prompt |
| 1 | `schemas.py scope` | — → scope schema |
| 1 | `framework_audit.py schema` | — → gap-angle schema |
| 1 | `framework_audit.py classify-prompt --question Q` | — → type-classify prompt |
| 1 | `framework_audit.py audit-prompt --angles A --question Q` | — → cell-walk audit prompt |
| 1 | `framework_audit.py select` | `{gap_angles, existing_angles, fetch_slots}` → `{angles}` |
| 5 | `framework_audit.py backfill` | `{gap_angles, confirmed_labels}` → `{unlanded, landed_count, unlanded_count}` |
| 2 | `prompts.py search --angle A --question Q` | — → search prompt |
| 2 | `schemas.py search` | — → search schema |
| 2 | `dedup.py` | `{results, seen, fetch_slots}` → `{novel, seen, slots}` |
| 3 | `prompts.py fetch --source S --label L --question Q` | — → fetch prompt |
| 3 | `schemas.py extract` | — → extract schema |
| 4 | `rank.py` | claims array → ranked (≤25) array |
| 5 | `prompts.py verify --claim C --voter-idx I --question Q` | — → verify prompt |
| 5 | `schemas.py verdict` | — → verdict schema |
| 5 | `rank.py quorum` | verdicts array → `true`/`false` |
| 6 | `synthesis.py blocks` | `{ranked_claims, vote_results, verdicts_per_claim}` → `{confirmed_block, killed_block}` |
| 6 | `prompts.py synthesis --question Q --confirmed-block CB --killed-block KB --confirmed-count N` | — → synthesis prompt |
| 6 | `mode_route.py schema` | — → mode-verdict schema |
| 6 | `mode_route.py classify-prompt --confirmed-block CB --killed-block KB --question Q` | — → epistemic-mode classify prompt |
| 6 | `mode_route.py stance` | `{mode_binary, mode_label?}` → `{stance_block}` |
| 6 | `purpose_fit.py schema` | — → purpose-fit verdict schema |
| 6 | `purpose_fit.py purpose-classify-prompt --question Q --confirmed-block CB` | — → purpose-fit classify prompt |
| 6 | `purpose_fit.py block` | `{inferred_purpose, confidence, mode, mooting_factors, frames}` → `{purpose_fit_block}` |
| 6 | `schemas.py report` | — → report schema |
| 6 | `synthesis.py report` | `{report, ranked_claims, angles, all_claims, confirmed, killed}` → `{stats, markdown}` |
