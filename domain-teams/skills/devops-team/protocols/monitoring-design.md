# Monitoring Design Protocol

Design service monitoring and alerting from scratch, grounded in Google SRE
practice. Produces a monitoring specification (dashboards, SLIs/SLOs, alert
rules, runbook links) that can be implemented in Prometheus/Grafana,
Datadog, CloudWatch, or any similar observability stack.

This protocol **completes the Monitoring & Observability workflow** that
was previously unfinished (Phase 1 marked `--`).

**Primary source reference**: `standards/sre-practices.md` (Google SRE Book Ch. 4, 6; Workbook Ch. 5)
**Also applies**: `standards/twelve-factor.md` §XI (Logs as event streams)

## Phase 1: Identify Critical User Journeys

1. Enumerate the service's **promised capabilities** — what can users do with it?
2. For each capability, identify the **critical path** — the sequence of
   operations that must succeed for the user to consider the capability working
3. Distinguish **critical paths** from **nice-to-haves** — monitoring budget
   is limited; invest in what would cause user-visible pain if broken
4. Document the user journey as a short phrase: "User logs in", "Order is
   placed", "Payment clears", etc.

Each critical user journey becomes a candidate for one or more SLIs in Phase 2.

## Phase 2: Define SLIs

For each critical user journey, pick **1-3 SLIs** from the Four Golden
Signals (see `standards/sre-practices.md` §Four Golden Signals):

- **Latency** — how long does the journey take? (e.g., P95 login duration)
- **Traffic** — how much demand is there? (e.g., logins per second)
- **Errors** — what fraction fail? (e.g., login 5xx rate)
- **Saturation** — how close to capacity? (e.g., auth service CPU utilization)

Use **request-based SLI formulas** wherever possible:

```
SLI = (number of good events) / (total valid events)
```

Example: `login_sli = count(login_success) / count(login_attempt)`

**Rules**:
- Keep SLIs to a minimum — every new SLI is a monitoring + alerting burden
- Prefer user-visible symptoms over internal mechanisms
- Each SLI must map to a specific SLO in Phase 3 (no orphaned SLIs)

## Phase 3: Set SLO Targets

For each SLI, set an achievable, meaningful **SLO**:

1. **Choose a target** — typical values: 99.9%, 99.95%, 99.99%
2. **Choose a window** — rolling 28 days is the SRE Workbook default; use
   shorter windows (7 days) for fast-moving services
3. **Derive the error budget**: `budget = 1 - SLO`
   - 99.9% SLO → 0.1% error budget → ~43 minutes of downtime per month
   - 99.95% SLO → 0.05% → ~22 minutes per month
   - 99.99% SLO → 0.01% → ~4.4 minutes per month
4. **Document the error budget policy** (see `standards/sre-practices.md` §Error Budget)
   - What happens when budget is exhausted? (feature freeze, deployment freeze)
   - Who has authority to invoke the freeze?
   - How is the freeze lifted?

**Do not aim for 100%**. 100% is the wrong target — it leaves no budget for
change, experimentation, or unavoidable infrastructure incidents.

## Phase 4: Instrument Code

Choose an instrumentation stack and add it to the service:

### Preferred stack (2026)
- **OpenTelemetry (OTEL)** — vendor-neutral instrumentation SDK
- **Prometheus** or **OTEL Collector** for metrics export
- **Structured logging** (JSON) with correlation IDs
- **Distributed tracing** (OTEL traces) for multi-service journeys

### Conventions
- Write logs unbuffered to **stdout/stderr** (12-Factor XI; see `standards/twelve-factor.md`)
- Include a **correlation ID** in every log line (`trace_id`, `request_id`)
- Tag metrics with **labels/dimensions** that allow slicing by endpoint,
  status code, and user segment
- Avoid high-cardinality labels (user_id, session_id) — they explode
  metric storage

### Instrumentation checklist
- [ ] Each SLI has a corresponding metric in the chosen system
- [ ] Each metric is labeled with service name and environment
- [ ] Structured logs include correlation IDs
- [ ] Trace propagation works across service boundaries
- [ ] Panel queries in Phase 5 can be written from these metrics

## Phase 5: Design Dashboards

Every service needs at least one **overview dashboard** showing the Four
Golden Signals prominently.

### Dashboard rules (SRE Workbook Ch. 4)
- **≤7 panels per screen** — beyond 7, attention fragments
- **Four Golden Signals at the top** — latency, traffic, errors, saturation
- **SLO burn-rate gauge** — how much error budget has been consumed
- **Link to runbook** — one click from dashboard to the runbook for this service

### Panel layout template
```
Row 1: Latency (P50, P95, P99)  |  Traffic (req/s)
Row 2: Errors (5xx rate)         |  Saturation (CPU, memory)
Row 3: SLO burn rate             |  Recent deploys overlay
```

Advanced dashboards (per-endpoint, per-region, saturation deep-dive) are
separate from the overview and linked from it. The overview must answer
"is this service healthy right now?" in under 5 seconds.

## Phase 6: Configure Alerts

Every alert must be **actionable** — if the response is "ignore it", the
alert is broken and must be fixed or removed.

### Alerting rules (SRE Book Ch. 6)
1. Alert on **symptoms** (user-visible), not causes (internal mechanisms)
2. Use **windowed aggregation** (5-minute average, not single data points)
3. Each alert links to a **runbook URL** (not just a description)
4. Assign **severity** (page, ticket, info) based on user impact
5. Define **escalation** path for unacknowledged alerts

### Burn-rate alerts (SRE Workbook Ch. 5)

For SLO-based alerting, use burn-rate alerts (not raw threshold alerts):

| Alert type | Burn rate | Window | Severity |
|------------|-----------|--------|----------|
| Fast burn | 14.4× | 1 hour | Page immediately |
| Slow burn | 3× | 6 hours | Ticket during business hours |

Fast burn: consuming error budget 14.4× faster than sustainable. At this
rate, a 28-day SLO budget is exhausted in 2 days. Requires immediate response.

Slow burn: consuming budget 3× faster than sustainable. Exhaustion in
~10 days. Can be addressed during business hours.

### Anti-patterns to avoid
- ❌ Alert on "disk is 90% full" (cause, not symptom)
- ❌ Alert on every error (noise)
- ❌ Alert on single data points (flaky)
- ❌ Alert without runbook link (operator can't respond)
- ❌ Alert with severity "info" that pages (wrong severity)

## Phase 7: Runbook Links

Every alert must point to a runbook that a on-call engineer can follow
during an incident. The runbook answers:

- **What does this alert mean?** (1-2 sentences)
- **Who is affected?** (users, services, regions)
- **How do I confirm the problem?** (dashboards to check, commands to run)
- **What is the immediate mitigation?** (turn off feature flag, scale up, rollback)
- **What is the full fix?** (link to issue, owner team)
- **Escalation** (who to wake up if mitigation fails)

Runbooks live in the same repo as the service (`docs/runbooks/` by convention)
or in a separate runbooks repo. They must be version-controlled and
reviewable.

### Runbook template
```markdown
# Runbook: {alert name}

## What this means
{1-2 sentences}

## Impact
{who is affected, how severely}

## Confirm the problem
- [ ] Check {dashboard URL}
- [ ] Run {verification command}

## Immediate mitigation
1. {step}
2. {step}

## Root cause investigation
{commands, logs to check}

## Escalation
- Primary: {team / person}
- Secondary: {team / person}
```

## Rules

- Every SLI maps to at least one SLO
- Every SLO has a documented error budget policy
- Every alert is actionable and links to a runbook
- Use the Four Golden Signals as the default starting point
- Instrument with OpenTelemetry unless there's a strong reason not to
- Dashboards stay under 7 panels per screen
- Burn-rate alerts for SLOs, not raw threshold alerts

## Output Structure

```markdown
# Monitoring Spec: {Service Name}

## 1. Critical User Journeys
- {Journey 1}
- {Journey 2}

## 2. SLIs and SLOs

| User Journey | SLI | SLO Target | Error Budget | Window |
|--------------|-----|------------|--------------|--------|
| ... | ... | 99.9% | 0.1% | 28d rolling |

## 3. Error Budget Policy
{what happens when budget is exhausted}

## 4. Instrumentation
- Stack: OpenTelemetry + Prometheus + Grafana
- Metrics: {list}
- Logs: structured JSON with correlation IDs

## 5. Dashboard Layout
{panel list following Four Golden Signals template}

## 6. Alert Rules

| Alert | Type | Threshold | Window | Severity | Runbook |
|-------|------|-----------|--------|----------|---------|
| ... | fast burn | 14.4× | 1h | page | /runbooks/X.md |

## 7. Runbooks
- /runbooks/{service}-{alert}.md
```
