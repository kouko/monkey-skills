# Condition-based waiting — race / heisenbug isolation

> Companion to [`../SKILL.md`](../SKILL.md). Sub-protocol for Phase 1 🟡 Intermittent and Phase 2 time-axis bisection.

## The anti-pattern this replaces

```
// Bad: sleep-based "wait for it to be ready"
await asyncOperation();
Thread.sleep(500);  // ...hopefully enough?
assertEquals(expected, getState());
```

The `sleep(500)` is **the bug telling you about a race condition in production**, not a debugging convenience. Beck (2002) Preface analogue applies: *"if it's hard to test deterministically, it's hard to use deterministically."*

Specifically, sleep-based waits fail F.I.R.S.T (Clean Code Ch.9):
- **Fast**: 500ms × N tests adds up to slow suites.
- **Repeatable**: passes on the dev laptop, fails on slow CI; or vice versa.

## The replacement: poll the condition

```
// Good: condition-based wait
await asyncOperation();
await waitFor(
  () => getState() === expected,
  { timeout: 5000, interval: 50, message: "state did not converge" }
);
```

The poll loop:
- Checks the condition every `interval` (typically 10-50ms).
- Times out after `timeout` (typically 1-10s).
- On timeout, **fails the test loudly** with the message — so the failure is informative, not silent.

The asymmetry matters: the timeout is generous (so transient slowness doesn't fail spuriously), but the poll interval is tight (so the test returns as fast as the condition allows). On a fast machine the test runs in ~50ms; on a slow CI it runs in ~500ms; neither is the sleep-based fixed 500ms cost.

## When the condition has no observable

Sometimes the condition you care about has no direct observable — e.g. *"the cache has been invalidated."* Two options:

1. **Add the observable.** Expose a `cache.size()` or `cache.lastInvalidatedAt` for tests. The cost is one accessor; the value is testability.
2. **Poll a downstream proxy.** If you can't observe the cache, observe the user-visible effect: *"the next read returns fresh data."* Slower but doesn't change production code.

Avoid: polling a sleep substitute (*"wait 100ms then assume cache is clear"*). That's the bug.

## Library helpers

| Language | Idiom |
|---|---|
| JavaScript / TypeScript | `@testing-library/dom` `waitFor`; Playwright `expect.poll`; Vitest `vi.waitFor` |
| Python | `pytest`-`asyncio` await-with-timeout; `tenacity` for retry-with-backoff |
| Go | `assert.Eventually(t, condition, timeout, interval)` from testify; `wait.PollImmediateUntil` from k8s util |
| Java | Awaitility (`Awaitility.await().atMost(...).until(...)`) |
| Rust | `tokio::time::timeout` wrapping the polling future |
| Shell | `until <cmd>; do sleep 1; done` with a max-attempt counter |

## Bisecting a heisenbug

When Phase 1 returns 🟡 Intermittent:

1. **Enumerate the timing axis**. What varies between successful runs and failed runs?
   - CPU load? (run in stress; does the rate change?)
   - Network latency? (run against localhost vs production-like delay; does the rate change?)
   - Disk I/O? (run from RAM-disk vs spinning disk; does the rate change?)
   - GC pauses? (run with `-XX:+PrintGCDetails` / pprof / instruments; correlate GC with failure)

2. **Bound the conditions**. *"Fails ~30% of the time under CPU load >50%; never fails under <20%."* This is the timing axis bisection result — Phase 1 is now 🟢 *"reliable under stress + CPU >50%."*

3. **Move to Phase 2** with the bounded conditions. The race becomes Hypothesizable (Phase 3) once you can predict when it triggers.

## Anti-patterns

- ❌ **`sleep` in production code "to fix" a race.** This is the same bug, dressed up. The race is still there; the sleep is masking it on your machine.
- ❌ **Retry loops without backoff.** Tight retry loops on a transient failure can DOS your downstream and don't fix the root cause.
- ❌ **Catching + retrying the timeout.** If your `waitFor` times out, the assertion failed; catching the exception and retrying without changing inputs is sleep with extra steps.
- ❌ **Skipping condition-based tests "because they're slower."** A condition-based test that runs in 50ms when the system is fast is FASTER than a sleep-based test that always waits 500ms. The slow case (timeout firing) is the FAILURE case — which sleep-based tests would have also failed, just slower and less informatively.

## See also

- [`../SKILL.md`](../SKILL.md) — Phase 1 🟡 / Phase 2 time-axis bisection.
- [`root-cause-tracing.md`](root-cause-tracing.md) — axis #5 time bisect references this file.
- [`../../subagent-driven-development/standards/tdd-standard.md`](../../subagent-driven-development/standards/tdd-standard.md) — F.I.R.S.T properties (Fast + Repeatable) that sleep-based tests violate.
- `obra/superpowers:condition-based-waiting` — Superpowers' upstream version of this protocol; this file is the code-toolkit adaptation.
