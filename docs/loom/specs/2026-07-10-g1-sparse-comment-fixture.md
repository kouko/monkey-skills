# G1 (partial) — sparse-comment fixture variant to stress-test dbt-wiki's comments-as-source-of-truth assumption

## Problem

dbt-wiki treats inline SQL comments as its primary source of truth when
distilling knowledge from a dbt project. W1 (the L2 e2e harness, shipped
2026-07-10) proved dbt-wiki answers correctly on ONE happy-path fixture:
English, DuckDB, moderate/mixed comment density (Task 7 even varied
comment density across 5 filler models, but every trap model that gates
the actual gold-question scoring still carries an explanatory comment).
The campaign doc's own Phase 3 language names the real risk directly:
"distillation quality on comment-poor projects is the predicted weak spot
— dbt-wiki treats comments as source of truth." Nobody has yet run the
harness against a project where comments are genuinely sparse or absent.
The job here is: **catch the "comments-as-truth breaks under sparse
documentation" failure mode now, via the harness, before it surfaces on
a real customer project.**

## Users

The dbt-wiki maintainer (kouko), running manual/session-driven eval
sweeps — Phase 4 (nightly/unattended loop) does not exist yet, so every
real e2e run is a deliberate, supervised, quota-spending action (Task 11
took ~7.5 minutes of real headless-agent time for one run). Any new
fixture variant must not become a second thing to hand-maintain in
parallel with the W1 fixture as both evolve.

## Smallest End State

Reuse W1's entire proven harness UNCHANGED: same 5 gold questions
(`gold-questions.yml`), same `runner.py` / `grader.py`, same 10 committed
models + seeds. Add exactly one new capability: a comment-stripping step
that derives a low/zero-comment variant of the SAME fixture project at
test time (not a hand-maintained parallel copy), then re-run the same
Task-11-style real e2e validation against that stripped variant and
compare its score against W1's baseline (5/5).

This isolates exactly one variable — comment density — per run. G1's
other two dimensions (Snowflake/BigQuery dialect targets, 100+ model
scale) are explicitly deferred to separate future G1 sub-cells: bundling
them into one experiment would confound results (a score drop couldn't
be attributed to comment density vs. dialect vs. scale).

## Current State Evidence

N/A — this reuses existing, already-reviewed infrastructure rather than
touching new code paths. The one new artifact (a comment-stripping
utility + one new e2e test) has no prior implementation to cite against;
its integration points (`runner.py`'s `build_command`, `grader.py`'s
`grade`, `gold-questions.yml`) are all committed and stable as of this
session (commits a2c75941 through 9262b250 on
`feat/dbt-wiki-w1-l2-e2e-harness`).

## Decision

Build a comment-stripping step (see Alternatives below for the chosen
mechanism) that generates a sparse/zero-comment variant of the W1 fixture
at test time, run a second real e2e validation against it (same 5 gold
questions, same grader), and record the resulting score in the campaign
journal alongside W1's 5/5 baseline — whether it holds, degrades, or
fails outright is itself the deliverable finding for this increment.

We will NOT build the Snowflake/BigQuery dialect cell or the 100+ model
scale cell in this increment — those are separate G1 sub-cells with their
own brainstorming pass when picked up.

## Out of Scope

- G1's dialect dimension (Snowflake/BigQuery compile targets)
- G1's scale dimension (100+ model fixture)
- G2 (probing every matrix cell + triaging failures into Phase 2 backlog)
- G3 (gold-question difficulty ladder)
- Any change to the W1 fixture's committed baseline models/seeds/gold
  questions — the sparse variant is derived, not a replacement

## Alternatives Considered

Researched via WebSearch (EN + JA), since this is a real technical fork
(how to build a comment-density ablation) not a solved problem in
training data:

1. **Full duplicate + hand-stripped copy** — reject. Golden-dataset
   practice (Statsig, Maxim, DeepEval, EvidentlyAI — EN) and a Qiita
   RAG-eval writeup + an Azure golden-dataset piece (JA) converge on the
   same warning: hand-maintained parallel copies of a dataset drift as
   the base evolves. Exactly the failure mode this would risk as W1's
   fixture keeps changing.
2. **Parametrized single-source with a strip step at test time**
   (recommended) — matches the industry "derive variants
   programmatically from one curated source, never duplicate" consensus.
   Keeps `gold-questions.yml` / `runner.py` / `grader.py` fully shared,
   nothing new to hand-maintain. Ablation-study methodology for
   LLM/documentation-dependency testing (AbGen, arXiv 2507.13300;
   DocAgent's context-stripping ablations, arXiv 2504.08725) validates
   this general "strip one input, measure the delta" approach, and
   "Code Needs Comments" (arXiv 2402.13013) empirically confirms comment
   density is a real variable affecting LLM code-understanding
   performance — this isn't testing a strawman.
3. **Synthetic/templated project generator emitting both variants from
   one declarative spec** — reject as over-engineering for a 10-model
   fixture; building and validating a generator is a bigger effort than
   the thing it's meant to test, and any generator bug becomes a
   confound in dbt-wiki's own results.

**My take**: Recommend #2. Caveat from the research: don't let the strip
step reformat the SQL (e.g. `sqlglot`'s `.sql(comments=False)` re-renders
the whole statement and has documented edge-case bugs — GitHub issues
#3794/#3439/#3810) — that would ablate comments AND formatting at once,
confounding the experiment. Prefer a literal-aware comment-only stripper
(e.g. operate on sqlglot's tokenizer output, or a regex that correctly
skips comment-like substrings inside string literals) that changes
nothing but the comments.

Sources (labeled by language):
- [EN] arxiv.org/abs/2507.13300 (AbGen — LLM ablation-study design)
- [EN] arxiv.org/pdf/2504.08725 (DocAgent — context-stripping ablations)
- [EN] arxiv.org/html/2402.13013v1 ("Code Needs Comments")
- [EN] github.com/tobymao/sqlglot issues #3794, #3439, #3810
- [EN] statsig.com/perspectives/golden-datasets-evaluation-standards
- [EN] deepeval.com/docs/evaluation-datasets
- [JA] qiita.com/teppei_nakano/items/15df8f370b245d5184ce
- [JA] blog.vonxai.co.jp/post/llm-mutation-testing-meta-experiment (adjacent: coverage/quality-of-signal drives LLM effectiveness, not just presence)

## What Becomes Obsolete

Nothing existing is removed — this is additive test-coverage expansion,
which is the legitimate shape of work for this campaign phase (Phase 3 is
explicitly about coverage, not consolidation). Flag for the future,
contingent on the actual score: if the sparse-comment run scores
significantly below W1's 5/5 baseline, that is a signal dbt-wiki's core
"comments as source of truth" design assumption may itself need
revisiting — that would become a new Phase 2/3 backlog item, not
something resolved in this increment.

## Open Questions

- Exact "sparse" definition for the stripped variant: zero inline
  comments everywhere, or a defined-but-low density (e.g. keep only
  `.yml` `description:` fields, strip all inline SQL `--` comments)?
  Recommend the harder test first (zero SQL comments, YAML descriptions
  intact — since `.yml` files are a distinct, already-structured
  metadata channel dbt-wiki also reads) — defer a middle-density variant
  to a later increment if the zero-comment run's result warrants finer
  granularity.
