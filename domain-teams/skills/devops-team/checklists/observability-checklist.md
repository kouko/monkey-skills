# Observability Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's output.
You MUST give `PASS`, `FAIL_FIXABLE`, or `NOT_APPLICABLE` for each item, with specific evidence.
The failure type for each item is defined below -- use the type specified.

## Checklist

- [ ] **CHK-OBS-001 (Logging)** [FIXABLE]: Logs use structured format (JSON or key-value). Correlation IDs are present for request tracing across services. Logs are sent to a centralized store (not only local files). Log levels are used correctly (ERROR for failures, WARN for degraded, INFO for state changes, DEBUG for troubleshooting).
- [ ] **CHK-OBS-002 (Metrics)** [FIXABLE]: Key metrics are defined for the service: latency (p50, p95, p99), error rate, throughput, and saturation (CPU, memory, disk, connections). Metrics are exposed via a standard interface (Prometheus endpoint, StatsD, OTEL).
- [ ] **CHK-OBS-003 (Alerting)** [FIXABLE]: Alerts are defined for critical paths with clear thresholds. Each alert includes: escalation policy (who gets paged), runbook reference (how to investigate), and severity level. No alert fires on a single data point (use windowed aggregation).

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
