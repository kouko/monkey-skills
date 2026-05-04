# Fixture: Company strategy memo (synthetic, 2024)

**Source**: Synthetic composite based on common SaaS quarterly strategy
memo patterns. Constructed for evaluation purposes.
**Eval target**: assumption-surface must produce a 10–15 row assumption
table, classify each as foundational / load-bearing / decorative, write
falsifiability tests for foundational assumptions, ≥3 counterfactual probes.

---

# Q3 Strategy Memo — Aurora

**Audience**: Exec team
**From**: Sarah K., CEO
**Date**: 2024-09-30

## TL;DR

We are reaching a inflection. Three signals indicate Q4 is when we
shift from PLG-led growth to enterprise-led expansion:

1. ARR has crossed $2M with no marketing spend
2. Three of our top 10 logos requested SOC2 + RBAC features simultaneously
3. Our typed query layer is now used in production at 47 teams

We propose: hire VP Sales by 2024-11-01, build enterprise tier with
SOC2 + RBAC + audit logs by 2024-12-31, raise Series A at $48M post.

## Why now

The cloud-database market has reached **type-safety mainstream**.
TypeScript adoption is at 78% of new web projects. Engineering teams
that already write typed application code expect typed database
access. We are the only player meeting this expectation across
Postgres / MongoDB / DynamoDB.

Our PLG funnel works: developers find us, try us, expand within their
team. But the natural ceiling of bottom-up adoption is mid-market. To
reach enterprise — where contract sizes 10x — we need top-down sales
motion. The longer we wait, the more we cede enterprise ground to
multi-model competitors (Cosmos, Fauna).

## Why this works

We have three durable advantages:

1. **Engineering-led product** — our type system is built by ex-Snowflake
   / Stripe / Cockroach engineers; competitors lack the depth
2. **Multi-engine support** — we don't force migration; we layer over
   existing DBs
3. **Performance** — we compile to native, no runtime overhead

These advantages compound: every enterprise client adds a logo, a case
study, and a multi-engine integration validation.

## What we'll cut

To fund this, we'll deprioritize:

- Mobile-first features (mobile is < 5% of our paying users)
- Free-tier expansion (current free tier converts 8% → paid; further
  expansion has unclear ROI)
- Marketing spend on developer events (PLG works; events are vanity)

## Risks

The main risk is **timing**. If Series A funding is delayed past Q1
2025, we burn cash on enterprise build-out without sales velocity.
Mitigation: we have 18 months runway; we can extend to 22 months by
slowing GTM hires.

A secondary risk is **enterprise execution**. We're a 13-person team
with no enterprise sales experience. Mitigation: VP Sales hire is a
critical path; we'll spend on getting it right.

## Decision needed by 2024-10-15

This memo proposes the strategic shift. Approval triggers:
- Series A pitch deck completion
- VP Sales search kick-off
- Enterprise tier roadmap kick-off

Open for discussion at Friday's exec sync.

---

## Annotations for evaluator

The fixture is constructed to contain (so eval can verify):

### Source claims (10 distinct)

1. We have reached an inflection point in Q3
2. Q4 is the right moment to shift from PLG to enterprise
3. ARR has crossed $2M with no marketing spend
4. Three top-10 logos requested SOC2+RBAC simultaneously
5. Type-safety is now "mainstream" in cloud-database market
6. We are the only player meeting typed-DB-access expectation
7. PLG funnel ceiling is mid-market, not enterprise
8. We have 3 durable advantages (engineering-led / multi-engine / performance)
9. Mobile-first / free-tier / marketing events are appropriate to cut
10. Timing risk is the main risk, mitigatable by runway extension

### Expected assumption table (10–15 rows; foundational ones marked F)

| # | Assumption | Source | Strength |
|---|---|---|---|
| 1 | Assumes "$2M ARR with no marketing spend" indicates organic demand strong enough for enterprise transition (vs. accidental viral moment) | claim 3 | F |
| 2 | Assumes 3 simultaneous SOC2+RBAC requests indicate market readiness, not coordinated pressure from one influential customer or competitor | claim 4 | F |
| 3 | Assumes type-safety "mainstream" implies enterprise demand for typed DB access (mainstream in dev community ≠ mainstream in enterprise procurement) | claim 5, 6 | F |
| 4 | Assumes "PLG ceiling = mid-market" is a structural truth, not a marketing-investment gap | claim 7 | F |
| 5 | Assumes 3 advantages are durable (engineering-led, multi-engine, performance), not commoditizable in 18-24 months | claim 8 | Load-bearing |
| 6 | Assumes mobile is genuinely <5% of *paying* users — measurement methodology not specified | claim 9 | Load-bearing |
| 7 | Assumes free-tier expansion has unclear ROI based on current 8% conversion — but doesn't model the lifetime value of expansion-tier users | claim 9 | Decorative |
| 8 | Assumes events are "vanity" — but events generate qualitative signal (competitive intel, recruiting, partnership leads) not captured by ROI math | claim 9 | Load-bearing |
| 9 | Assumes Series A pricing of $48M post is achievable in current market | claim "raise Series A at $48M post" | F |
| 10 | Assumes VP Sales hiring is critical-path solvable — that the right person can be found, hired, and onboarded in 6 months | claim "VP Sales hire is critical path" | Load-bearing |
| 11 | Assumes "top-down sales motion" can co-exist with PLG without cannibalizing inbound | implicit | F |
| 12 | Assumes Cosmos / Fauna are the right competitive frame (not single-engine substitutes like Postgres+extensions) | "cede enterprise ground to multi-model competitors" | F |

### Foundational assumptions worth challenging (≥3)

**Assumption 3** (type-safety mainstream → enterprise demand): falsifiable
by surveying enterprise procurement decision-makers. If <30% mention
type-safety as a procurement criterion, the warrant collapses.

**Assumption 11** (top-down + bottom-up coexist): falsifiable by examining
PLG cohort retention after enterprise sales motion launches. If 6
months post-launch the bottom-up funnel slows by >20%, top-down is
cannibalizing.

**Assumption 12** (multi-model is the right competitive frame): falsifiable
by mapping where customers actually leave Aurora to. If 60%+ leave
to Postgres+extensions (single-engine), the multi-model framing is
misdirected.

### Counterfactual probes

- If Series A funding is delayed 6 months: does the strategy still
  hold? (Memo addresses this — runway extension. But doesn't model
  what happens if multiple risks compound.)
- If VP Sales hire fails (bad hire, takes 12 months): plan B?
- If a competitor (Fauna) raises mega-round and dramatically
  out-spends: defensibility of the 3 "durable" advantages?

### Acknowledgment-discomforts

- The memo doesn't acknowledge that **the founders have no enterprise
  sales experience**, which is the actual operational risk underneath
  "VP Sales hire is critical path."
- The memo doesn't address what happens if **type-safety hype peaks**
  (TypeScript adoption could plateau, or backlash could emerge — both
  documented in dev-community discussions).
- The memo doesn't address whether **47 teams in production** includes
  paying customers vs free-tier users.

### Verdict

**Strong strategy memo** with explicit risks section, but rests on
**4–6 foundational assumptions** that are not falsifiability-tested in
the document. The most contestable foundational assumption is #11
(PLG + top-down can coexist), because it's an operational claim that
historical evidence often refutes (PLG cultures struggle to integrate
top-down sales without losing bottom-up momentum).

Recommend: use this assumption table in the Friday exec sync to drive
**discussion of falsifiability tests**, not just decision approval.
