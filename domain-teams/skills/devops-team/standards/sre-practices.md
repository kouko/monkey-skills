# SRE Practices (Shared Standard)

Site Reliability Engineering practices as authoritative reference for
devops-team. Both worker (when designing monitoring/deployment) and evaluator
(when reviewing) reference this file. All terms trace to Google's *Site
Reliability Engineering* (Beyer, Jones, Petoff, Murphy, O'Reilly 2016).

Primary source: [sre.google/sre-book/](https://sre.google/sre-book/)
Companion: [sre.google/workbook/](https://sre.google/workbook/) (2018)

## SLI / SLO / SLA

From *Site Reliability Engineering* Chapter 4 — the three service-level
terms are distinct and must not be conflated.

| Term | Definition (Google SRE Book verbatim) | Example |
|------|----------------------------------------|---------|
| **SLI** (Service Level Indicator) | "A carefully defined quantitative measure of some aspect of the level of service that is provided" | Request latency, error rate, throughput, availability, durability |
| **SLO** (Service Level Objective) | "A target value or range of values for a service level that is measured by an SLI" | "99% of `Get` RPC calls will complete in less than 100 ms" |
| **SLA** (Service Level Agreement) | "An explicit or implicit contract with your users that includes consequences of meeting (or missing) the SLOs they contain" | "Service uptime ≥ 99.9% or customer receives service credit" |

**Key insight**: Most SLIs are "the ratio of two numbers: the number of good
events divided by the total number of events."

SLA > SLO > SLI — the SLA is the business contract, the SLO is the internal
target (usually tighter than the SLA), and the SLI is the actual measurement.

## Error Budget

From SRE Book Chapter 3: **"100% is the wrong reliability target for basically
everything."** An error budget is derived directly from the SLO:

> **Error budget = 1 − SLO**

Example: SLO of 99.9% → error budget of 0.1% of requests may fail before the
SLO is violated.

### Error Budget Policy

Every SLO must have an associated error budget policy defining what happens
when the budget is exhausted:

- **Feature freeze** — no new features until the budget is replenished
- **Deployment freeze** — no production deploys that are not bug fixes
- **Prioritized reliability work** — team focus shifts to reliability
- **Post-mortem + remediation** — mandatory blameless retrospective

The error budget converts reliability from a conflict ("devs want speed, ops
want stability") into a shared target ("we have X amount of unreliability to
spend; let's spend it wisely").

## Four Golden Signals

From SRE Book Chapter 6 (Monitoring Distributed Systems), the four signals
that should be monitored for every user-facing service:

| Signal | Definition | Example metric |
|--------|------------|----------------|
| **Latency** | The time it takes to service a request | P50/P95/P99 request duration |
| **Traffic** | How much demand is being placed on your system | Requests per second, active sessions |
| **Errors** | The rate of requests that fail | HTTP 5xx rate, failed RPC count |
| **Saturation** | How "full" your service is | CPU utilization, memory pressure, queue depth |

If you can only measure four things on your user-facing systems, measure
these four. Dashboards should highlight them prominently.

## Toil Reduction

From SRE Book Chapter 5: **toil** is "the kind of work tied to running a
production service that tends to be manual, repetitive, automatable,
tactical, devoid of enduring value, and that scales linearly as a service
grows."

### Google's 50% Toil Cap

Google caps toil at 50% of an SRE's time. The other 50% is reserved for
engineering work that reduces future toil. Teams that exceed 50% toil are
**structurally unsustainable**.

### Identifying Toil

A task is toil if it matches ≥3 of these criteria:
- Manual (a human must execute it)
- Repetitive (you've done it before and will do it again)
- Automatable (a machine could do it as well as a human)
- Tactical (interrupt-driven, not strategic)
- No enduring value (the system is in the same state after you finish)
- Scales linearly with service growth

**Overhead ≠ toil**. Meetings, HR paperwork, 1:1s are overhead, not toil.
Toil is specifically operational work that a machine could do.

## Alerting Philosophy

From SRE Book Chapter 6 and Workbook Chapter 5:

> **"Every alert should be actionable."**

Alerts that do not require human response should be **eliminated**, not
muted. If an alert fires and the response is "ignore it" or "no action
needed," the alert is broken.

### Symptoms over Causes

Alert on **symptoms** (user-visible failure) not **causes** (internal
mechanisms). Causes change; symptoms are stable.

- ❌ Alert on "disk is 90% full"
- ✅ Alert on "write latency has exceeded SLO for 5 minutes"

The disk-full alert fires on every disk even when the service is healthy;
the latency alert fires only when users are affected.

### Burn-Rate Alerts (SRE Workbook Ch. 5)

For SLO-based alerting, burn-rate alerts measure **how fast you are
consuming your error budget**. A burn rate of 1.0 means you will exhaust
the budget exactly at the SLO window boundary; higher burn rates mean
exhaustion sooner.

Typical burn-rate alert thresholds:
- **Fast burn** (14.4× over 1 hour) — page immediately
- **Slow burn** (3× over 6 hours) — ticket during business hours

## Sources

- [*Site Reliability Engineering* — Ch. 4 SLOs](https://sre.google/sre-book/service-level-objectives/) — SLI/SLO/SLA definitions, error budget
- [*Site Reliability Engineering* — Ch. 5 Eliminating Toil](https://sre.google/sre-book/eliminating-toil/) — toil definition and reduction
- [*Site Reliability Engineering* — Ch. 6 Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) — Four Golden Signals, alerting philosophy
- [*Site Reliability Workbook* — Ch. 5 Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) — burn-rate alerts
- [Google Cloud Blog — SRE fundamentals: SLIs, SLAs and SLOs](https://cloud.google.com/blog/products/devops-sre/sre-fundamentals-slis-slas-and-slos)
