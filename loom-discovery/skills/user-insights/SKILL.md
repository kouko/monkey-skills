---
name: user-insights
description: |
  The problem-space research verb of loom-discovery — map, with recorded
  evidence, WHAT users need and which needs are worth serving, before any
  design or spec work. Two modes: opportunity-space mapping (knowledge work —
  research the world, never interrogate the user for researchable facts) and
  value commitment (a value judgment — the agent proposes a recommendation and
  writes the commitment only after the user ratifies it). Produces
  user-insights.md + evidence.md + per-question research/ reports under
  docs/loom/discovery/<date>-<slug>/. Problem-space-pure: states needs and
  outcomes, never solutions. Delegates heavyweight research to
  research-toolkit:deep-deep-research. Use for: user needs / what do users need
  / needs research / 使用者需求 / 使用者洞察 / ユーザーインサイト. Not for
  business worth-it verdicts (that is business-value) nor for designing the
  solution (that is loom-interface-design / loom-spec).
version: 0.1.0
---

# user-insights

The core research verb of the loom-discovery station. The job: **when I bring a
product-shaped idea to loom, establish — with recorded evidence — what problem
exists, for whom, and which needs are worth serving**, so downstream stations
consume verified needs instead of whatever was in my head.

This skill is **problem-space-pure**. It states WHAT users need and the outcomes
they want; it never states HOW to solve them (Intercom rule — no solution
content). Solutions are the job of loom-interface-design, loom-spec, loom-code.

## Two modes — assigned per work nature

The skill runs in two distinct modes. Which one applies is decided by the nature
of the work, not by preference. Both can run in one session (map first, then
commit); keep them separated because their **ground truth lives in different
places**.

### Mode 1 — Opportunity-space mapping (KNOWLEDGE work)

Mapping the space of needs is a knowledge question: the ground truth is **in the
world** (users, competitors, prior art, the repo). Therefore this is
**research/explore mode**.

- **Never interrogate the user for facts that are researchable** in the world or
  in the repo. Grilling the user for what a search or a repo read can answer is
  the anti-pattern this station exists to replace (grill-me's own author demoted
  user-interrogation in favor of domain grounding).
- Output: the **Opportunity space** section of `user-insights.md` — each need as
  a job story ("When …, I want …, so I can …"), evidence-linked, with its
  context / journey stage and today's workaround.
- Every asserted need cites a claim row in `evidence.md`. A need with no evidence
  is an open question, not a finding.

### Mode 2 — Value commitment (VALUE JUDGMENT)

Deciding **which** needs to serve is not a knowledge question — it is a value
judgment, and its ground truth is **with the user**. Therefore this is
**research-then-"my take"** mode, the same protocol as loom-code brainstorming
Axis 4.

**Commitment interaction contract:**

1. The agent presents the mapped opportunity space with its evidence, then makes
   an **explicit recommendation** in the Axis-4 shape:
   - **Recommend** — which needs to serve, stated plainly.
   - **Why** — the evidence and reasoning behind it.
   - **Conditional reversal** — what fact, if true, would flip the call.
2. The commitment is written into `user-insights.md` **only after the user
   ratifies** it (mark it "ratified by user on <date>").
3. **Agents never self-commit on the user's behalf.** Mapping and proposing is
   the agent's job; deciding is the user's. A commitment written without
   ratification is a contract violation, not a shortcut.

## Research delegation boundary

Pick the research path by scope (resolves the brief's Open Q2):

- **Delegate to `research-toolkit:deep-deep-research`** when the discovery needs
  **more than 3 research questions**, OR when **external evidence or direct user
  evidence** is required. Pass paths + seed context per the cross-plugin
  delegation contract (monkey-skills `CLAUDE.md` §Cross-Plugin Delegation
  Contract) — pass file paths and a structured seed, never inline analysis; the
  delegate loads its own standards, runs its own pipeline, returns findings.
- **Inline WebSearch** otherwise (small scopes, ≤3 questions, world-researchable).
  Run **EN + JA** queries every round (single-language search is sampling bias);
  cite both, labelled by source language. If a language returns 0 hits, surface
  that as a finding.

Either way, findings land as claim rows in `evidence.md` and as `research/`
reports — never as unsourced assertions.

## Artifact set

All under `docs/loom/discovery/<date>-<slug>/`:

| File | Role |
|---|---|
| `user-insights.md` | The insights + ratified commitment (per `assets/user-insights-template.md`). |
| `research/` | One intermediate report **per research question**: goals → method → findings → insights skeleton. Kept for audit and re-understanding. |
| `evidence.md` | Claims-to-evidence registry (per `assets/evidence-template.md`). |

### Evidence-chain doctrine

```
evidence.md (facts) → research/ (reports) → user-insights.md (insights + commitment)
```

**Evidence outlives any single report** (ResearchOps atomic-research model). A
`research/` report can be re-run or discarded; the underlying facts stay in
`evidence.md`. This is what makes the discovery re-understandable months later
and is the user's explicit drift-prevention requirement.

## Downstream consumers

What this artifact feeds (state it in problem-space terms, let each consumer
translate):

- **Value-commitment outcomes** → `PRINCIPLES.md` `— check:` material for
  loom-product-principles (falsifiable checks derive from committed outcomes).
- **Needs + journey stage** → loom-interface-design flow seeds.
- **Job stories** → loom-spec acceptance-criteria seeds.

## Agent behavioral contract

- user-insights agents **map needs and propose commitments**; they may **NOT
  render investment / worth-it verdicts** — that is business-value's profession.
  Professional isolation is contract-level: the two skills share no artifact and
  no agent.
- Agents never self-commit (see Mode 2). Writer ≠ decider on the commitment.

## Workflow

1. **Frame** the problem (what + why now + whose) into `user-insights.md`
   §Problem framing. No solutions.
2. **Map** the opportunity space (Mode 1): research the world / repo, record
   claims in `evidence.md`, write each need as an evidence-linked job story.
   Route research per the delegation boundary above.
3. **Propose** the commitment (Mode 2): present the space + an explicit
   Recommend / Why / Conditional-reversal recommendation.
4. **Ratify**: write the commitment into §Value commitment only after the user
   agrees; mark the ratification date.
5. **Close** with §Risks & open questions; unsupported claims live there, never
   in Opportunity space as if settled.

## References

- `assets/user-insights-template.md` — the artifact skeleton.
- `assets/evidence-template.md` — the claims-to-evidence registry.
- loom-code brainstorming `references/axis4-research-protocol.md` — the
  research-then-"my take" protocol Mode 2 reuses (EN+JA queries, recommendation
  shape).
