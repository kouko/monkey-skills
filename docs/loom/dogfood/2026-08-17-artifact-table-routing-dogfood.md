# Cold-reader A/B: artifact-layer table routing (brief table · spec matrix tables · diagram semantics)

Date: 2026-08-17 · Branch: `loom-doc-container` at `ce31e0eb` (all 8 plan tasks DONE) vs `main` (`e0d432ae`) as baseline
Plan under test: `docs/loom/plans/2026-08-17-artifact-table-routing.md` (BI-2 brief table, BI-3 spec matrix tables + validator, BI-9 diagram semantics)
Method: `docs/loom/memory/process-mechanism-dogfood-via-coldreader-real-commits.md` — a fresh, context-blind agent is given ONLY the governing reference file (baseline copy from `git show main:…` vs the branch's working copy, both placed in a neutral scratch dir) + a seed file, told to read nothing else, and asked to write the artifact section. Judged mechanically (`score.py`: table separator-row regex per section; `-->|` labelled-edge count; `<br/>` two-layer-node count; candidate spec outputs wrapped into a minimal change-folder and run through the branch's `validate_spec_output.py`).
Not a full skill run — no `brainstorming` / `spec-expansion` invocation, no hooks, no web research; this certifies that a writer who reads the template file follows the new slot, not that the whole skill pipeline reaches that file. Session-tier writers (the real case) are not sampled — sonnet is the floor here, haiku the weakest-tier sanity check.

## Probe 0 — reception preload carries the new §(b) bullet (mechanical)

`CLAUDE_PLUGIN_ROOT=<repo>/loom-code bash loom-code/hooks/session-start` from the branch → the injected reception contains "The same fork rule binds written artifacts" (runtime extraction of `### (b)` → `### (c)`, per `session-start:81-87`). Verified.

## Probe 1 — brief writer: `## Alternatives Considered` (seed: CSV export, 3 pre-researched alternatives, chosen #1)

| Leg | Model | Run | `## Alternatives Considered` form | Governing sentence the writer cited |
|---|---|---|---|---|
| baseline (main template) | sonnet | 1 | numbered list | "Format: numbered list, each with a one-sentence rejection rationale." |
| baseline | sonnet | 2 | numbered list | same |
| candidate (branch template) | sonnet | 1 | **table** (3 rows incl. the chosen path, N/A cell) | Pin B "Format: a markdown comparison table — one row per alternative, columns …" |
| candidate | sonnet | 2 | **table** | same |
| candidate | haiku | 1 | **table** (2 rejected rows; chosen path omitted — acceptable, the template says "one row per alternative") | same |

Result: **0/2 → 3/3**. The template slot binds the writer at both tiers.

## Probe 2 — spec Phase ③ / ③b: `## Path × edge matrix` + `## Cross-object combinations` (seed: cart/order/payment backbone, 3 lenses)

| Leg | Model | Run | Path × edge | Cross-object | Branch validator on the wrapped output | Columns |
|---|---|---|---|---|---|---|
| baseline (main SKILL.md) | sonnet | 1 | table | table | exit 1 — **unrelated** pre-existing check (`evidence_needed: domain-convention` tier label missing), not the table check | writer-invented (`Stage | CTA | Transition | Lens | Verdict | Provenance`) |
| baseline | sonnet | 2 | table | table | exit 0 | writer-invented |
| candidate (branch SKILL.md) | sonnet | 1 | table | table | exit 0 | Pin C-1 / C-2 columns verbatim |
| candidate | sonnet | 2 | table | table | exit 0 | Pin C-1 / C-2 columns verbatim |
| candidate | haiku | 1 | table | table | exit 0 | Pin C-1 / C-2 columns (haiku renamed `State` → `Initial state`) |

Result: **no table-vs-prose delta in this probe** — the word "matrix" already pulls a cold sonnet/haiku toward tables when Phase ③ is the only thing in context. The candidate's measurable delta is (a) a standardized column schema across runs and tiers, and (b) mechanical enforcement: the branch validator now rejects a prose body (checked separately in `test_validate_spec_output.py`; the shipped `docs/loom/2026-07-19-8k-prose-kpi-intake` proposal — a real full-skill output — fails it, `docs/loom/2026-07-12-…` passes). The seed note's real-corpus finding (26% of specs table-bearing; two shipped proposals with prose matrix bodies) is what this probe cannot reproduce: full-skill runs carry far more context than a two-file cold read, and that is exactly where the validator, not the doctrine, is the guarantee.

## Probe 3 — brief `## Diagrams` slot: Mermaid flowchart (seed: this arc's own mechanism, 5 pieces)

| Leg | Model | Run | Edges labelled | Nodes two-layer (`<br/>`) | Character of edge labels |
|---|---|---|---|---|---|
| baseline (main visual-companion) | sonnet | 1 | 9/9 | 0 | *what* ("binds at write-time", "flags the violation") |
| baseline | sonnet | 2 | 13/13 | 0 | *what* |
| candidate (branch visual-companion) | sonnet | 1 | 8/8 | 7/7 | *why* ("binding at write-time doesn't stop drift after writing", "a wording change in one plugin would silently desync the other") |
| candidate | sonnet | 2 | 8/8 | 7/7 | *why* |

Result: edge labelling is not the delta (sonnet labels edges either way); **two-layer nodes 0 → 7/7** and edge labels shift from action verbs to reasons — the intended effect of Pin D. Both candidate writers cited §Diagram semantics verbatim.

## Verdict

- BI-2 (brief table): **behavioral PASS**, 3/3 vs 0/2, both tiers.
- BI-9 (diagram semantics): **behavioral PASS**, node two-layer 7/7 vs 0/0, why-labels present.
- BI-3 (spec tables): **doctrine adopted 3/3, but the probe is not discriminating** (baseline also tabular in cold-read); the load-bearing guarantee is the validator (Task 4), which is test-covered and demonstrably fails a real shipped prose proposal.
- Probe 0 (preload): PASS.

## Limits (state them, don't hide them)

- Cold-read of the reference file ≠ the skill's real invocation path; hooks/preload/web research not exercised.
- n=2 per sonnet leg, n=1 haiku, one seed each — direction is unambiguous where it flipped (0→3, 0→7), not a rate estimate.
- Spec baseline behavior in the real corpus (prose) was not reproduced; treat BI-3's behavioral evidence as the validator tests, not this probe.
- Evidence anchors the commits it ran against (`ce31e0eb`); per `docs/loom/memory/dogfood-evidence-anchors-shipped-commit.md`, any later wording change re-runs the touched probe.

Artifacts: scratchpad `dogfood/{base,cand,seeds,out,score.py}` (session-local, not committed).

## Addendum — reader-comprehension A/B (table vs prose, same facts)

Question the seed note left open: does the *form* change what a model reader understands? Controlled probe: one brief, two variants differing ONLY in `## Alternatives Considered` (rest byte-identical, program-checked) — 5 alternatives × 5 axes as a markdown table vs as a numbered list carrying the same facts. Fresh readers got one variant + a 10-question set (3 single-fact lookups, 5 cross-row comparisons incl. a 5-way ordering, 1 absent-fact trap, 1 two-reason "why"), document-only, and were scored against a pre-written gold key by a rule-based checker.

| Form | Reader | n | Score |
|---|---|---|---|
| table | haiku-4-5 | 4 | 10/10 × 4 |
| prose | haiku-4-5 | 4 | 10/10 × 4 |
| table | sonnet | 2 | 10/10 × 2 |
| prose | sonnet | 2 | 10/10 × 2 |

Result: **ceiling on both forms, both tiers — no measurable comprehension difference at this scale** (≈4.6 KB document, 5-row comparison, 10 questions). Consistent with the seed note's literature read (frontier readers are format-indifferent; harm shows up in small models *writing* structured output, not reading it) and with the arc's premise: the table rule buys human readability, and the model reader is neither helped nor hurt. A discriminating test would need larger comparisons (≳12 rows × 6 axes with near-duplicate values), distractor length, and aggregation questions (counts / sums across rows) — the regime where the table-multi-step-reasoning weakness is documented; not run here.

> **Annotation 2026-08-19 — the clause "the model reader is neither helped
> nor hurt" above is retracted; the rest of this paragraph stands.** It
> contradicts the same sentence's own "ceiling" observation: all 12 readers
> scored full marks on both forms, so this run licenses "no difference
> detected at this difficulty" and cannot license "no effect". The
> paragraph is left as written because it is the record of what this arc
> concluded on 2026-08-17; the corrected reading lives in
> `docs/loom/memory/model-readers-are-form-agnostic-at-loom-doc-scale.md`,
> and the evidence that prompted the retraction in
> `docs/loom/research/2026-08-19-cot-diagram-plus-prose-evidence.md`.
> This result also compared two TEXT CONTAINERS; it has been cited for a
> diagram, which it does not cover.
