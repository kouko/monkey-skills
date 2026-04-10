# Observability Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's output.
You MUST give `PASS`, `FAIL_FIXABLE`, or `NOT_APPLICABLE` for each item, with specific evidence.
The failure type for each item is defined below -- use the type specified.

Based on Google SRE Book §6 (Monitoring Distributed Systems) and §4
(Service Level Objectives). See `standards/sre-practices.md` for the
Four Golden Signals and error budget concepts.

## Checklist

- [ ] **CHK-OBS-001 (Logging)** [FIXABLE]: Logs use structured format (JSON or key-value). Correlation IDs are present for request tracing across services. Logs are sent to a centralized store (not only local files). Log levels are used correctly (ERROR for failures, WARN for degraded, INFO for state changes, DEBUG for troubleshooting). Aligns with 12-Factor XI (Logs as event streams).
- [ ] **CHK-OBS-002 (Four Golden Signals)** [FIXABLE]: The **Four Golden Signals** from SRE Book §6 are all defined for the service: **latency** (p50, p95, p99), **traffic** (requests per second), **errors** (5xx rate or failure count), and **saturation** (CPU, memory, queue depth). Metrics are exposed via a standard interface (Prometheus endpoint, StatsD, OpenTelemetry).
- [ ] **CHK-OBS-003 (Alerting)** [FIXABLE]: Alerts are defined for critical paths with clear thresholds. Each alert includes: escalation policy (who gets paged), runbook reference (how to investigate), and severity level. No alert fires on a single data point (use windowed aggregation). Alert on symptoms (user-visible failures), not causes (internal mechanisms) — per SRE Book §6.
- [ ] **CHK-OBS-004 (SLO Definition)** [FIXABLE]: The service has at least one documented **SLO** with a numeric target (e.g., "99.9% of requests complete in <200ms over 28 days") and a defined **error budget policy** (what happens when budget is exhausted: feature freeze, deployment freeze, etc.). See `standards/sre-practices.md` §Error Budget Policy.

## Verdict Rules

- Any `FAIL_FIXABLE` items -> final verdict is `PASS_WITH_NOTES` (trigger auto-revise)
- All items are `PASS` or `NOT_APPLICABLE` -> final verdict is `PASS`

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES",
  "checklist_results": [
    {
      "id": "CHK-OBS-001",
      "status": "PASS | FAIL_FIXABLE | NOT_APPLICABLE",
      "evidence": "Specific config reference or finding",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```
