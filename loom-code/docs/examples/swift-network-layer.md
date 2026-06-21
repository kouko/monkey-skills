# Worked example — Swift: refactor network layer to async/await

> **Stack**: Swift 5.9 + iOS 17 + URLSession + XCTest
> **Persona**: iOS developer maintaining a 3-year-old client app
> **Task complexity**: ~4 hours, refactoring existing untested code → Feathers (2004) characterization-test pattern applies
> **Demonstrates**: `tdd-iron-law` §Legitimate legacy-code backfill + `systematic-debugging` for a flaky test surfaced during refactor
> **Skills exercised**: full flow + Feathers 2004 legacy backfill + `systematic-debugging` 4-phase REPRODUCE→ISOLATE→HYPOTHESIZE→VERIFY

## The user's initial prompt

```
Our APIClient.swift uses URLSession with completion handlers — 600
lines of nested closures from before async/await. Refactor to modern
Swift Concurrency. Existing code has ZERO tests (legacy from before
my time).
```

---

## Stage 1 — `brainstorming`

Agent recognizes "ZERO tests + legacy refactor" → Feathers (2004) Working Effectively with Legacy Code applies. Brief:

```markdown
# Brief: refactor APIClient to async/await

## Problem (JTBD)
When future-me / next-developer adds a new endpoint, I want the
network layer to use modern Swift Concurrency idioms (async / await /
throws), so I can write callsites in 3 lines instead of 15-line
nested closure cascades.

## Users
This iOS app's developers (currently me + 2 contractors). Indirectly:
end users (faster crash recovery — async/await + structured cancel
beats completion-handler retain cycles + leaked tasks).

## Smallest End State
APIClient exposes async/await methods. Old completion-handler methods
remain TEMPORARILY (callsites migrate incrementally). New endpoints
use ONLY async path. After all callsites migrated, completion handlers
deleted (separate ticket; out of scope for this brief).

## Decision
Three pieces:
1. Characterization tests (Feathers Ch.13) for current completion-
   handler behavior — pin down what it does, INCLUDING any bugs
2. New async-path implementation of same endpoints
3. Tests for new async path (proper TDD; failing-test-first)

## Out of Scope
- Migrating callsites (separate ticket per callsite-file; phased rollout)
- Deleting old completion-handler methods (after all callsites migrated)
- Adding new endpoints (this is refactor, not feature)
- Changing the request/response models (data layer unchanged)

## Alternatives Considered
1. Rewrite from scratch in one PR — REJECTED: "delete + start over"
   is Iron Law's remediation for "you wrote it without tests"; but
   this code is INHERITED, not your own violation → Feathers backfill
   is the legitimate path (per tdd-iron-law §Legitimate legacy-code
   backfill)
2. Migrate callsites first, refactor APIClient last — REJECTED: changes
   the network surface twice (callsites would migrate to old API, then
   migrate again to new API)
3. Use Combine instead of async/await — REJECTED: app targets iOS 15+;
   async/await is the standard idiom now

## What Becomes Obsolete
- Eventually: 600 lines of completion-handler code in APIClient.swift
  (deletion deferred to post-migration ticket)
- Internal docs section "Working with our network layer (completion
  handlers)" — keep until migration complete

## Open Questions
(none — Feathers pattern explicit + scope tight)
```

---

## Stage 2 — `writing-plans`

```markdown
# Plan: APIClient async/await refactor

**Source brief**: docs/code-toolkit/specs/2026-05-16-apiclient-refactor.md
**Total tasks**: 4 (≤5 ✓)
**Execution order**: sequential (each task depends on prior)
**Plan-document-reviewer verdict**: PASS

## Task 1 — Characterization tests for existing completion-handler API
- Description: For the 4 most-used endpoints (login / fetchProfile /
  postEvent / uploadAsset), write XCTest cases that capture CURRENT
  observable behavior — including any bugs the existing code has.
  These tests must pass against the existing code AS-IS. Per Feathers
  (2004) Ch.13 Characterization Tests.
- Module: `Tests/APIClientCharacterizationTests.swift` (new file)
- Acceptance:
  - RED → not applicable in characterization mode (tests are pinning
    EXISTING behavior; first run should PASS, not FAIL)
  - Done condition: 4 tests, each calling existing completion-handler
    API + asserting observed behavior (status codes, response shape,
    error mapping)
- Dependencies: none
- Brief item covered: Decision #1 — characterization tests
- Note: this is NOT tdd-iron-law's RED-GREEN cycle; this is Feathers
  Ch.13 pin-down. The next tasks (new async implementation) DO follow
  RED-GREEN.

## Task 2 — Async wrapper around existing completion-handler API
- Description: Add `async throws` methods that call the existing
  completion-handler methods via `withCheckedThrowingContinuation`.
  This is the minimum-viable async surface; it doesn't yet replace
  the implementation, just wraps it.
- Module: `Sources/APIClient+Async.swift` (new file)
- Acceptance:
  - RED: `APIClientAsyncTests > login async returns same as completion-handler`
  - GREEN: 4 tests pass (one per endpoint, asserting parity with
    completion-handler behavior)
- Dependencies: Task 1 complete (characterization tests serve as oracle
  for parity assertion)
- Brief item covered: Decision #2 — async path; Decision #3 — async tests

## Task 3 — Add request cancellation via Task.cancel()
- Description: New async methods should respect Task cancellation
  (call URLSession.dataTask cancel() in withCheckedThrowingContinuation's
  cancel handler).
- Module: `Sources/APIClient+Async.swift` (modified)
- Acceptance:
  - RED: `APIClientAsyncTests > login throws CancellationError when Task cancelled`
  - GREEN: cancel test passes; existing 4 tests still pass
- Dependencies: Task 2
- Brief item covered: implicit in "modern Swift Concurrency" — Task
  cancellation IS what async/await affords over completion handlers

## Task 4 — Internal docs note on migration path
- Description: Update `docs/network-layer.md` — keep "Working with
  completion handlers" section (until migration done) + ADD "New
  endpoints: use async/await" section. Document the migration ticket
  reference.
- Module: `docs/network-layer.md`
- Acceptance:
  - GREEN: section added with example callsite code; migration ticket
    linked
- Dependencies: Task 3 complete (need to know final async surface)
- Brief item covered: Out of Scope "Deleting old completion-handler
  methods (after all callsites migrated)" — docs explain the path
```

---

## Stage 3-4 — `subagent-driven-development` + `tdd-iron-law`

Task 1 (Feathers characterization) is **distinct** from Iron Law cycle. The SDD implementer subagent loads `tdd-iron-law/SKILL.md` and recognizes §Legitimate legacy-code backfill applies: the code being characterized was written by a previous developer (before this session), so it's legacy by Feathers's definition. Characterization tests pin current behavior; Iron Law's RED-GREEN cycle then applies to Tasks 2-3 which add NEW behavior on top.

Task 1 implementer dispatch — characterization tests:

```swift
// Tests/APIClientCharacterizationTests.swift
import XCTest
@testable import App

final class APIClientCharacterizationTests: XCTestCase {

    /// Pins current behavior of login() — NOT testing what it SHOULD do,
    /// testing what it DOES do. Per Feathers (2004) Ch.13.
    func test_login_success_returns_user_with_token() {
        let expectation = expectation(description: "login completes")
        let client = APIClient(baseURL: URL(string: "https://api.test")!)
        // Mock: 200 with valid token payload
        MockURLProtocol.requestHandler = { request in
            let response = HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: nil)!
            let body = #"{"user": {"id": 1, "email": "a@b.c"}, "token": "abc"}"#.data(using: .utf8)!
            return (response, body)
        }

        client.login(email: "a@b.c", password: "x") { result in
            switch result {
            case .success(let response):
                // Pin CURRENT behavior: response is (User, String) tuple
                XCTAssertEqual(response.user.id, 1)
                XCTAssertEqual(response.token, "abc")
            case .failure:
                XCTFail("expected success")
            }
            expectation.fulfill()
        }
        wait(for: [expectation], timeout: 1)
    }

    // ... 3 more characterization tests (fetchProfile / postEvent / uploadAsset)
}
```

Run: 4/4 PASS. These tests now constitute the "oracle" for Task 2's parity assertion.

Task 2 implementer dispatch — async wrapper under Iron Law cycle:

```swift
// Tests/APIClientAsyncTests.swift — FAILING TEST FIRST
func test_login_async_returns_same_as_completion_handler() async throws {
    let client = APIClient(baseURL: URL(string: "https://api.test")!)
    MockURLProtocol.requestHandler = { /* same as above */ }

    let response = try await client.loginAsync(email: "a@b.c", password: "x")

    // Parity assertion: result matches characterization test for the
    // completion-handler counterpart
    XCTAssertEqual(response.user.id, 1)
    XCTAssertEqual(response.token, "abc")
}
// First run: COMPILE FAIL — loginAsync doesn't exist
// ✓ RED confirmed
```

```swift
// Sources/APIClient+Async.swift — minimum implementation
extension APIClient {
    func loginAsync(email: String, password: String) async throws -> LoginResponse {
        try await withCheckedThrowingContinuation { continuation in
            self.login(email: email, password: password) { result in
                continuation.resume(with: result)
            }
        }
    }
    // ... 3 more wrappers
}
// Re-run: PASS
// ✓ GREEN
```

REFACTOR step (extract common continuation wrapper) — omitted for brevity.

### Stage 5 — `systematic-debugging` (REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY)

During Task 3 implementation, the `cancel` test passes locally but **fails intermittently on CI** (1 in ~20 runs). systematic-debugging fires per the §When to use trigger "intermittent failure."

**Phase 1 — REPRODUCE**:
- Local: never fails
- CI: ~5% fail rate
- 🟡 Intermittent → use `references/condition-based-waiting.md` to bound conditions

Phase 1 returns 🟡 bounded conditions: fails when CI runner has CPU > 80%.

**Phase 2 — ISOLATE**:
- Time-axis bisection (per `root-cause-tracing.md` axis #5)
- Pinpoint: failure happens when `continuation.resume(throwing: CancellationError())` is called BEFORE the URLSession task's cancel handler fires
- Race between Task.cancel propagating + URLSession dataTask cancellation

**Phase 3 — HYPOTHESIZE**:
- If the race is between Task.cancel and URLSession cancel handler, then forcing the URLSession dataTask to cancel BEFORE calling continuation.resume should eliminate the race
- Falsifiable prediction: with cancel-then-resume order, the test should pass 100/100 on the stress-CI runner

**Phase 4 — VERIFY**:
- Apply fix: in cancel handler, call `dataTask.cancel()` synchronously, THEN `continuation.resume(throwing: ...)`
- Re-run on stress-CI: 100/100 PASS
- ✓ Hypothesis confirmed; fix applied
- Per `references/defense-in-depth.md` blast-radius assessment: low (single function, no security surface) → just the fix + regression test, no monitoring layer needed

---

## Stage 6-8 — review + verify + finish

`requesting-code-review` PASS_WITH_NOTES (🟡 the loginAsync wrapper has duplicated continuation-resume pattern vs the 3 other endpoint wrappers — Rule of Three triggered after Task 2 ships 4 wrappers; recommend extract a generic wrapper helper). User extracts; re-review → PASS.

`verification-before-completion`:
```
$ xcodebuild test -scheme App
... 67 tests passed (4 characterization + 5 async + 58 pre-existing) ...
Test Suite 'All tests' passed at 2026-05-16 14:32:11.234.
   Executed 67 tests, with 0 failures (0 unexpected) in 4.821 seconds
```

PASS.

`finishing-a-development-branch` runs the 7-step flow. `git-memory` writes:
- Decision: Feathers 2004 characterization path chosen over rewrite-from-scratch because code is inherited, not own-violation — loom-code's tdd-iron-law §Legitimate legacy-code backfill explicitly authorizes this path
- Decision: async wrappers ship BEFORE deleting completion-handler implementations — phased callsite migration is safer than big-bang switch
- Learning: continuation cancel-then-resume order matters under CPU pressure (intermittent on CI < 5% before fix; 0% after)
- Gotcha: future async wrapper additions should reuse the extracted continuation helper (introduced in Task 2's REFACTOR step) to avoid Rule-of-Three re-fire

---

## What this example demonstrates (NEW vs Python + TypeScript examples)

| Aspect | Demonstrated |
|---|---|
| `tdd-iron-law` §Legitimate legacy-code backfill | Inherited untested code → Feathers (2004) Ch.13 Characterization Tests; distinct from Iron Law violation |
| Distinction between Feathers backfill vs Iron Law violation | Task 1 is characterization (pin current behavior); Tasks 2-3 are NEW behavior under RED-GREEN cycle. Tdd-iron-law SKILL.md table row applies: "you inherit 50K lines of untested COBOL from a previous team and need to add a new feature" — same shape, different decade |
| `systematic-debugging` 4-phase flow | Intermittent CI failure during Task 3 → Phase 1 (🟡 bounded conditions: CPU > 80%) → Phase 2 (time-axis bisect; race condition isolated) → Phase 3 (falsifiable hypothesis: cancel-then-resume ordering) → Phase 4 (stress-CI 100/100 verify) |
| `defense-in-depth.md` blast-radius proportionality | Low blast → fix + regression test only; no monitoring layer added |
| Multi-trailer commit | git-memory wrote 2 Decision: + 1 Learning: + 1 Gotcha: trailers for this branch |

## See also

- [`python-csv-export.md`](python-csv-export.md) — simple all-clean case
- [`typescript-react-toast.md`](typescript-react-toast.md) — multi-module + SDD child-test fallback
- [`../../skills/tdd-iron-law/SKILL.md`](../../skills/tdd-iron-law/SKILL.md) §Legitimate legacy-code backfill — the Feathers 2004 distinction this example exercises
- [`../../skills/systematic-debugging/SKILL.md`](../../skills/systematic-debugging/SKILL.md) — 4-phase framework
- [`../../skills/systematic-debugging/references/condition-based-waiting.md`](../../skills/systematic-debugging/references/condition-based-waiting.md) — heisenbug bisection on CPU-axis
- [`../../skills/systematic-debugging/references/defense-in-depth.md`](../../skills/systematic-debugging/references/defense-in-depth.md) — blast-radius proportionality rule
