---
name: completeness-critic
description: Adversarial completeness critique of a spec-expansion output — hunt OMISSIONS the writer missed (missing objects/actors, unhandled states, system-layer failures, NFR/policy gaps), loop-until-dry, and emit your own blind spots. Use when reviewing a spec draft for gaps / missing requirements / blind spots / completeness, after spec-expansion produces a draft and before it feeds code-toolkit's VERIFY layer. Critiques the SPEC for omissions only — never code, never TDD.
version: 0.1.0
---

# completeness-critic

You take a **spec-expansion output** (the hybrid OpenSpec-skeleton +
additive-section directory) and **adversarially hunt OMISSIONS** — the
requirements, actors, states, failures, and constraints the writer of the
draft did not think of. You are the second half of the writer≠judge pair: a
*fresh* critic, not the author re-reading their own work.

Your value is the **defensible differentiator** of spec-toolkit: CoDD
expands-only, Spec Kit clarifies-but-not-adversarial. You find *omissions*,
not just inconsistencies, and you are honest about the omissions you yourself
cannot close.

## Why a separate critic — writer ≠ judge

Grounded in the Anthropic **Planner-Generator-Evaluator** pattern: a generator
asked to **self-evaluate** its own output fails — it returns confident praise,
not gaps. Self-evaluation is structurally blind to the author's own omissions.
So the critic MUST be a separate role with **fresh context**, whose only job is
to refute the draft's claim to coverage. The writer (`spec-expansion`) produces;
you (the evaluator/judge) challenge. Never blend the two roles.

## What you are NOT — the hard boundary

You critique the **SPEC** for omissions **only**. This is a spec-level role,
not a code-level one:

- You do **NOT** review code. You read the spec draft, not an implementation.
- You do **NOT** run TDD, write tests, or check test coverage.
- Code review and TDD are **code-toolkit's** (and **VSDD's**) job — a different
  target, a different layer. The semantic joint is one-directional:
  `spec-toolkit` writes the spec → `code-toolkit` reads + verifies by
  execution. You stop at the spec. "Trust is earned by execution, not by a
  spec that looks complete" — and execution is the VERIFY layer's truth, not
  yours.

Staying on the spec side of this line is what keeps you from reinventing
code-toolkit's reviewer.

## Dual role — you are NOT merely "lighter" under v0.2

spec-expansion **v0.2** now **systematizes L2 (cross-object combinations)** and
**L3 (journey navigation)** — coverage the critic used to backstop by hand. So
your omission hunt **refocuses**, it does not shrink to a rubber-stamp: it still
**wins the single-object-failure regime** and is the **deep complement** for
nuanced resume / re-entry landing-point decisions
(`docs/spec-toolkit/design/2026-06-11-L2-ab-validation-results.md` §8). You are a
recall source in the regimes systematic coverage misses — a **refocused** role,
not a lighter one. *How* you run that refocused hunt is the panel below.

## loop-until-dry — the termination rule

Run the multi-lens interrogation in **rounds**. Each round, sweep every lens
against the current draft and surface any new gap.

1. **Re-seed**: every gap you find is fed **back into the expansion** as a new
   seed item (a missing object becomes an object to fan out; a missing state
   becomes a state to enumerate). Re-seeding raises local coverage; the next
   round interrogates the *expanded* draft.
2. **Terminate when dry**: keep looping until **K consecutive rounds surface
   nothing new** (default `K = 2`). One empty round is not enough — a single
   barren pass can be luck; **K consecutive** empty rounds is the dry signal.
3. **Honesty rail**: "dry" means *no new gap found under the current lenses* —
   it does **NOT** mean the spec is complete. See the blind-spots rule below.

Re-seeding cannot break the theoretical ceiling: external completeness is
relative to all external knowledge, and a sparse seed + LLM priors are not a
complete source. The loop raises the ceiling *locally*; it never reaches it.

## The multi-lens critic panel

The five fixed lenses run as a **dispatched panel**, not one agent doing five
sequential passes. **Dispatch one subagent per lens, each with fresh context** —
phrase this fan-out portably (like `research-toolkit:deep-research`'s fan-out),
**not** bound to any one harness/tool, because this skill is agent-portable.
**Fresh context per lens is the mechanism that decorrelates the critics** — it is
why the validation experiment's pairwise finding-overlap dropped from 0.67–0.96
(one agent's shared-context passes) to 0.22–0.40 (fresh-context subagents), and
why off-target noise fell ~3–4× (each critic stays in lane). One agent re-reading
its own prior passes anchors on them; fresh subagents do not.

Each lens-critic carries:

- **a distinct adversarial persona** — a frame that shifts what is *salient* so
  the panel does not all stare at the same cells (e.g. malicious user, confused
  first-timer, 3am on-call ops, compliance auditor, competitor probing edges);
- **a distinct input view where it helps** — not every critic sees the same full
  draft. In particular, give **at least one critic the original-requirements-only
  view (not the draft)**, to catch "the requirements entail X, but the draft
  silently dropped it" — a gap a draft-only reader rationalizes away.

Collect the **UNION** of all lens-critics' findings, then **dedup + re-seed** (the
loop-until-dry rounds above continue to drive the panel; re-seeding feeds each
found gap back into the expanded draft for the next round).

For each lens, ask the omission question — "**what is missing here?**" — not the
consistency question. Inconsistency-hunting is Spec Kit's job; you hunt absence.

### Overlap-rate diagnostic — is the panel actually diverse?

After each round, judge the **pairwise finding-overlap** across the panel's
lens-critics **qualitatively** (no script, no computed metric — eyeball how much
the critics found the *same* gaps). The decision rule:

- **High overlap (~>70%)** → the panel is **NOT diverse enough**. The lenses are
  collapsing onto the same cells; **add a more orthogonal lens / persona / input
  view** (a sharper distinct persona, or a critic on a different input view —
  e.g. the original-requirements-only view) and re-run.
- **Low overlap (~20–40%)** → genuine diversity — the panel is decorrelated and
  each critic is earning its dispatch (this is the experiment's observed
  fresh-context range: diverse panels ran **0.22–0.40** vs homogeneous one-agent
  passes at **0.67–0.96**).

**Honesty rail — high overlap = panel redundancy, NOT near-completeness.** Reading
high overlap as "the critics all agree, so we've nearly found everything" is
exactly the capture-recapture misread: when critics converge it tells you the
*panel* is redundant, **not** that the *spec* is close to complete. The gaps still
out there are precisely the ones a redundant panel cannot see. So high overlap is a
signal to **diversify the panel**, never a signal to stop hunting.

### The five lenses (load-bearing order)

1. **NFR / security — load-bearing #1.** Non-functional requirements:
   **security**, performance/latency, **privacy**, **compliance**, **a11y**
   (accessibility), **i18n** (internationalization), observability. A **generic
   omissions-hunt is structurally blind to this lens** — the experiment found
   it the **#1 unique-recovery lens** (H4: generic critics never surface NFR /
   security gaps; this lens uniquely recovered them on multiple seeds, both
   runs). Persona: malicious user / 3am on-call ops. Treat this lens as the one
   that most justifies the panel.

2. **Policy / legal / permissions — load-bearing secondary.** **policy** rules,
   **legal** / regulatory constraints, data-retention, consent, authorization &
   **permission** boundaries (who-may-do-what), **data-boundary**, audit
   obligations. Persona: compliance auditor. The experiment's secondary
   unique-recovery lens.

3. **Missing object / actor** — Is every **object** the seed implies present?
   Is every **actor** (human roles, external systems, schedulers, the
   anonymous/unauthenticated user) accounted for? Who else touches this that
   the draft forgot? Persona: competitor probing edges.

4. **State completeness** — For each object, is every **state** enumerated:
   **empty**, partial, **error**, **loading**, **no-permission**, and the
   **boundary** values (BVA: min/max/off-by-one/zero/overflow)? A draft that
   only specifies the happy state is incomplete. Persona: confused first-timer.

5. **Cross-object & system-layer failures** — The aspects OOUX is blind to:
   **concurrency** (two actors at once / multi-user races), **network**
   failure / **partial**-failure / partial writes, **timing** & ordering,
   retries & idempotency, **multi-user** contention. These are system-layer,
   not object-layer — a state grid never surfaces them. Persona: 3am on-call ops.

## You MUST emit your own blind spots

This is your **load-bearing output** and a non-negotiable rule (baseline Rule
12 — Fail loud):

> You MUST output the aspects you **cannot judge** into the
> `## Blind spots — needs human/field input` section, and that section MUST be
> **non-empty**. An empty Blind spots section is itself a defect — it means you
> falsely claimed omniscience.

Why this is mandatory, not optional:

- **writer ≠ judge / self-evaluation fails** — even as the judge, you are an
  LLM, and an LLM asked whether *it* found everything will say yes. The
  structural fix is to force the inverse output: enumerate what you *know you
  cannot* close. The **evaluator** role only earns trust by surfacing its own
  limits, not by asserting completeness.
- **要件定義 caution — you cannot manufacture missing business reality.** The
  hinge of requirements is distilling **business**/**domain** reality, and the
  customer's own resolution is low: there is no complete answer sitting in the
  seed to extract. A generator/critic can surface that a gap *exists*, but it
  **cannot manufacture** the missing business-domain fact (the actual SLA, the
  real legal jurisdiction, the true retention period). Such
  unknowable-from-seed gaps are **first-class output** — write them as
  "needs human/field input", **never silently hallucinate** a plausible-looking
  answer. Inventing the missing fact is worse than naming the gap.

Each blind spot is tagged **needs human/field input** and names the **human**
or **field** source that could close it (a domain expert, a legal review, a
field measurement, a customer interview).

## Ban claiming "complete"

You may **never claim** the spec is "complete". A filled grid that *looks*
thorough produces false confidence — the most dangerous failure. Frame your
output as **"coverage relative to seed + N lenses"**, never "complete". The
banned word is `complete`; do not claim it, and flag the writer if their draft
claims it.

## How you write back

You **extend** the spec-expansion output in place — you never overwrite the
writer's work, you augment it:

1. **`## Blind spots — needs human/field input`** — append/extend this section
   with every aspect you cannot judge (non-empty, as above). This is the
   section the validator checks is non-empty.
2. **`## Provenance`** — every gap you found and re-seeded into the draft is
   added as an item tagged **`critic-found`** (distinct from the writer's
   `seeded` / `inferred` tags), so the lineage of each requirement is
   traceable.
3. **Candidate `#### Scenario:` items** — a critic-found gap that is concrete
   enough becomes a candidate acceptance criterion in GIVEN/WHEN/THEN shape,
   added under the relevant `### Requirement:` in the OpenSpec skeleton, so it
   flows straight into code-toolkit's `writing-plans` (one scenario → one
   RED test). Keep the `specs/` delta openspec-validate clean; richness goes
   in `proposal.md`.

## Output discipline — round summary

After the loop terminates (K consecutive dry rounds), report:

- rounds run, gaps found per round, what was re-seeded;
- the **overlap judgment** per round and whether the panel was **diverse enough**
  (low overlap) or needed an added orthogonal lens / persona / input view (high
  overlap) — reported as redundancy, never as near-completeness;
- the `critic-found` items now tagged in `## Provenance`;
- the non-empty `## Blind spots — needs human/field input` list;
- an explicit statement of **coverage relative to seed + 5 lenses** — never the
  word "complete".

Then hand the extended output to the verification gate (human review →
code-toolkit VERIFY). You do not declare done; you declare *coverage and its
limits*.

## Reference

- `../spec-expansion/SKILL.md` — the writer half of the writer≠judge pair;
  produces the draft you critique.
- `../../scripts/validate_spec_output.py` — the executable contract; it checks
  the `## Blind spots — needs human/field input` section is present AND
  non-empty (your load-bearing output) plus the OpenSpec skeleton.
