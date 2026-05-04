# Fixture: VC pitch memo (synthetic, 2024)

**Source**: Synthetic composite based on common Series A pitch memo
patterns (YC SAFE-stage to Series A, infrastructure / dev-tools sector).
**Status**: Constructed for evaluation purposes.
**Eval target**: argument-deconstruct must produce genre-move map (problem
/ opportunity / solution / traction / ask), at least 1 Burke pentad ratio,
and a mermaid argument map.

---

# Aurora Database — Series A Memo

**Round**: $12M Series A
**Lead requested**: Y / Z (any one)
**Closing**: 6 weeks

## TL;DR

Aurora is a typed query layer for cloud-native databases. We unify the
fragmenting database market (Postgres / NoSQL / multi-model) into a
single typed interface. $2M ARR in 11 months. Raising to triple the
team and capture enterprise.

## Problem

The cloud-native database market has fragmented into three camps:

- **Postgres-loyalists** (Postgres / RDS / Supabase) — strong on
  relational, weak on real-time and document workloads
- **NoSQL evangelists** (Mongo / Dynamo / Firestore) — strong on
  flexibility, weak on transactional integrity
- **Multi-model platforms** (Cosmos / Fauna / SurrealDB) — promising
  but each has its own API, locking customers in

Engineering teams running cloud-native applications now juggle 2–4
database systems per stack. They build glue code (or pay for tooling
like Hasura / PostgREST / FoundationDB) to unify access. The glue
costs more than the databases.

## Opportunity

The market for "database access layers" was $1.4B in 2023 and is
projected at $4.8B by 2027 (Gartner). The fragmentation will not
self-resolve — each camp serves real workloads.

What's missing is a **typed query layer** that compiles to native
queries on each engine, unifying access without forcing migration.
This is the opportunity.

## Solution

Aurora compiles a typed schema-first query language to native queries
across Postgres, MongoDB, DynamoDB, Cosmos, and Fauna. Engineers
write once; deploy across.

Key features:
1. **Type safety** — compiler catches schema mismatches at build time
2. **Engine-agnostic** — same query, different backends
3. **Performance pass-through** — we don't add an orchestration layer; we compile to native

We are 18 months into development, with 47 engineering teams in
production using Aurora today.

## Traction

| Metric | 2023 H2 | 2024 H1 | 2024 H2 (projected) |
|---|---|---|---|
| ARR | $230K | $1.2M | $2.0M |
| Logos | 12 | 31 | 47 |
| Net retention | 110% | 132% | 140% |
| MoM gross retention | 95% | 97% | 98% |

Logo highlights: Robinhood (production for 8 months), Datadog (3
months), 4 of YC W24 batch.

## Team

- **Sarah K., CEO** — ex-Snowflake (5y, scaled Snowpipe to $50M ARR)
- **Tom L., CTO** — ex-Stripe (4y, payments infrastructure team lead)
- **Amir P., Head of Eng** — ex-Cockroach (4y, distributed query planner)

We are 11 engineers, 2 GTM. All seniors. 4 ex-FAANG, 2 ex-unicorn.

## Why now

Three trends converge:

1. **Database fragmentation has accelerated** — multi-model databases
   doubled in number 2022→2024
2. **Type-safe development is mainstream** — TypeScript adoption hit
   78% of new web projects (StackOverflow 2024)
3. **Engineering teams are cost-pressured** — fewer engineers per app,
   pressure to consolidate tooling

A unified typed query layer was impossible 5 years ago (no enterprise
appetite for new abstractions). It is necessary now (multi-engine
glue code is consuming engineering time).

## Use of funds

| Category | $M | Plan |
|---|---|---|
| Engineering | 5.0 | Triple team to 33; build enterprise features (audit logs / RBAC / SOC2) |
| GTM | 4.0 | Hire VP Sales + 4 AEs; build outbound for enterprise |
| Founders / runway | 1.5 | 24-month runway buffer |
| Customer success | 1.5 | Hire CS lead + 2 CSMs for enterprise tier |

## Ask

$12M Series A at $48M post. SAFE conversions clean. Lead taking 30%
of round; pro-rata for existing investors (Sequoia / Initialized).

We're closing in 6 weeks. Decision needed by 2024-09-15.

---

## Annotations for evaluator

The fixture is constructed to contain (so eval can verify):

### Genre move map (Bhatia VC pitch genre)

| Section | Canonical move | Strength |
|---|---|---|
| TL;DR | Establishing credentials + introducing offer | Strong (numbers + ask upfront) |
| Problem | Pain articulation | Strong (segmented, specific) |
| Opportunity | Market sizing | Adequate (relies on Gartner — single backing) |
| Solution | Solution introduction | Strong (3 differentiators named) |
| Traction | Proof | Strong (table + named logos) |
| Team | Authority claim | Strong (specific tenure + outcomes) |
| Why now | Trend convergence | Adequate (3 trends, but warrant about now-vs-5yrs-ago is asserted not argued) |
| Use of funds | Implementation plan | Strong (line-itemed) |
| Ask | Solicit response | Strong (specific terms, deadline) |

All canonical moves present. **No risk register section** — note this
is unusual for late-stage memos but **standard for Series A** (risk
discussion happens in DD, not memo).

### Toulmin (central claim)

| Component | Content |
|---|---|
| Claim | Lead our $12M Series A round |
| Grounds | $2M ARR / 47 logos / 132% net retention / ex-Snowflake-Stripe-Cockroach team / converging trends |
| **Hidden warrant** | "Because Series A traction at this profile (ARR + retention + team pedigree) reliably converts to Series B + acquisition outcomes — Lead investing here gives reasonable probability of meaningful return" |
| Backing | Sequoia + Initialized previous investment (peer signal) |
| Rebuttal acknowledged? | **Implicit only** — "Why now" addresses "why not earlier"; no acknowledgment of "what could go wrong" |
| Qualifier present? | **Missing** explicit — but VC genre tolerates absence (qualifier lives in DD) |

### Burke pentad

- Act: Lead $12M Series A
- Scene: Cloud DB market fragmentation; type-safety mainstreaming
- Agent: Aurora team (ex-Snowflake / Stripe / Cockroach)
- Agency: Typed query layer compiling to native queries
- Purpose: Capture enterprise database access layer market

- **Claimed ratio**: **Agency-Act** ("typed query layer is the technical method that unifies")
- **Actual ratio**: **Agent-Act** (founder credentials are doing the heaviest persuasive work; "ex-Snowflake / Stripe / Cockroach")
- **Discrepancy**: standard for Series A — early-stage VC investing *is* mostly Agent-driven, even when pitched as method-driven. Honest, not deceptive — but worth surfacing.

### Strongest move

Traction table + named logos (Robinhood, Datadog) — provides
verifiable Agent-track-record signals beyond the pitch deck.

### Weakest move

"Why now" trend-convergence section. Three trends are listed but the
*logical* link from trends to "now is the moment" is asserted, not
argued. A skeptical investor would ask: each trend has been true for
2+ years; what changed *this quarter*?

### Hidden warrant most worth contesting

The retention claims (132% net retention, 98% gross) are presented as
self-evidently strong. They are *strong relative to SaaS averages*,
but for *infrastructure SaaS at $2M ARR*, the cohort is small enough
that retention numbers are noisy. A 132% NR could come from 5 expansion
deals among 47 logos — material if those 5 churn. Investors should
contest the warrant "current retention predicts future retention at
larger scale."

### Missing rebuttal that matters most

No discussion of **single-engine substitutes**. Why isn't Postgres-only
sufficient (with read replicas / extensions for document workloads)?
Why isn't a single multi-model engine (Fauna / SurrealDB) sufficient?
The pitch assumes fragmentation is permanent; it could be a transitional
state.

### Verdict

**Strong Series A pitch** — all canonical genre moves present, traction
table backs the ask, team is appropriately credentialed. One exposed
weakness (retention reliability at scale) and one missed rebuttal
(single-engine alternatives). Burke ratio surfaces standard early-stage
agent-driven investing pattern. Memo is genre-faithful and intellectually
honest within VC norms.
