# DORA Metrics (Shared Standard)

DORA (DevOps Research and Assessment) Four Key Metrics as authoritative
reference for measuring DevOps performance over time. **DORA metrics describe
organizational maturity, not individual artifact quality.** They must be
observed over a period (typically 3-6 months), not gated on a single deploy.

Primary source: [dora.dev](https://dora.dev/)
Book: *Accelerate: The Science of Lean Software and DevOps* (Forsgren, Humble, Kim — IT Revolution Press, 2018)

## The Four Key Metrics

| Metric | Definition | Measures |
|--------|------------|----------|
| **Deployment Frequency** | How often an organization successfully releases to production | Throughput (speed of delivery) |
| **Lead Time for Changes** | Elapsed time from code commit to code running in production | Throughput (change cycle speed) |
| **Change Failure Rate** | Percentage of deployments causing a failure in production requiring remediation (hotfix, rollback, patch) | Stability (release quality) |
| **Time to Restore Service** (MTTR) | How long it takes to recover from a failure in production | Stability (incident response) |

DORA research (State of DevOps Reports 2014-2024) has consistently shown
that these four metrics, and only these four, strongly correlate with both
software delivery performance and organizational performance (profitability,
market share, customer satisfaction).

## Performer Tiers (DORA 2023-2024 benchmarks)

DORA classifies organizations into four tiers. Numbers below are drawn from
the most recent public DORA State of DevOps Report.

| Tier | Deployment Frequency | Lead Time | Change Failure Rate | MTTR |
|------|---------------------|-----------|---------------------|------|
| **Elite** | Multiple deploys per day (on-demand) | Less than 1 hour | 0–15% | Less than 1 hour |
| **High** | Between once per day and once per week | 1 day – 1 week | 0–15% | Less than 1 day |
| **Medium** | Between once per week and once per month | 1 week – 1 month | 16–30% | 1 day – 1 week |
| **Low** | Between once per month and once every 6 months | 1 month – 6 months | 16–30% | 1 week – 1 month |

Source: [State of DevOps Report](https://dora.dev/research/) (latest annual edition)

## Measurement Approach

Each metric has a standard measurement path that does not require
specialized tooling:

### Deployment Frequency
**How to measure**: Count successful production deploys per time window.
Source: CI/CD deploy logs, release tags, production deploy audit trail.
Formula: `deploys_to_prod / window_days`

### Lead Time for Changes
**How to measure**: For a sample of recent commits that reached production,
compute `production_deploy_time - commit_time`.
Source: `git log` + CI/CD deploy timestamps.
Caveats: For trunk-based development, lead time ≈ build + test + deploy pipeline
duration. For branch-based, add the branch-lifetime from first commit to merge.

### Change Failure Rate
**How to measure**: Count deploys that triggered an incident, rollback,
hotfix, or patch, divided by total deploys in the same window.
Source: Incident tracker (PagerDuty, Opsgenie), rollback records, hotfix PRs.
Formula: `failed_deploys / total_deploys`

### Time to Restore Service (MTTR)
**How to measure**: For each production incident, record the time from
detection (first alert or customer report) to resolution (service fully
restored). Average or use median.
Source: Incident tracker timestamps.
Formula: `mean(resolution_time - detection_time)` across incidents

## DORA Capabilities Model

*Accelerate* identifies **24 capabilities** that drive improvement in the
Four Key Metrics. They fall into five categories:

1. **Continuous delivery** capabilities (8) — version control, deployment automation, continuous integration, trunk-based development, test automation, test data management, shift-left security, continuous delivery
2. **Architecture** capabilities (2) — loosely coupled architecture, empowered teams
3. **Product and process** capabilities (4) — customer feedback, value stream visibility, working in small batches, team experimentation
4. **Lean management and monitoring** capabilities (5) — change approval, monitoring, proactive notification, WIP limits, visualizing work
5. **Cultural** capabilities (5) — Westrum culture, supporting learning, collaboration, job satisfaction, transformational leadership

**devops-team focuses primarily on the Continuous Delivery and Monitoring
capability categories** — the rest are organizational/cultural and sit
outside a technical skill's scope.

## Important: DORA Metrics Are Not Gates

**DORA metrics are not per-artifact quality gates.** They describe
organizational delivery performance observed over time, typically measured
monthly or quarterly.

A single commit or deploy cannot be evaluated against "Change Failure Rate"
— that metric requires many deploys to compute. Similarly, "Deployment
Frequency" has no meaning for a single deploy.

devops-team uses DORA metrics through the **DORA Metrics Baseline workflow**:
a measurement task that produces a `DORA-BASELINE.md` report describing the
current state of the four metrics, recommended improvements, and targeted
capability areas from the 24 capabilities model.

The baseline report is **diagnostic**, not **prescriptive**. Improving
DORA performance requires capability-level changes (e.g., adopting
trunk-based development) that happen over months, not hours.

## Sources

- [dora.dev](https://dora.dev/) — official DORA research site
- [State of DevOps Report](https://dora.dev/research/) — annual benchmark data
- [DORA Four Keys](https://dora.dev/guides/dora-metrics-four-keys/) — measurement guide
- [DORA Capabilities](https://dora.dev/capabilities/) — 24 capabilities model
- Forsgren, N., Humble, J., Kim, G. *Accelerate: The Science of Lean Software and DevOps*. IT Revolution Press, 2018. ISBN 978-1942788331
