# Worked example — TypeScript: app-wide toast notification system in React

> **Stack**: React 18 + TypeScript 5 + Zustand + Vitest + Testing Library
> **Persona**: web developer building a SaaS dashboard
> **Task complexity**: ~3 hours, touches 4 modules → SDD applies; SDD child-test fallback (Beck Part II §Child Test) triggered on Task 3
> **Demonstrates**: multi-module case + BLOCKED → re-split flow
> **Skills exercised**: full flow + `subagent-driven-development` BLOCKED fallback to `writing-plans` for child-task decomposition

## The user's initial prompt

```
Add app-wide toast notifications — success / warning / error variants,
auto-dismiss after 5s, dismiss-on-click, max 3 stacked.
```

---

## Stage 1 — `brainstorming`

```markdown
# Brief: app-wide toast notifications

## Problem (JTBD)
When the app performs an action (save / error / mutation), I (user) want
non-blocking feedback that confirms the outcome, so I can continue working
without watching for state changes in the UI body.

## Users
End users of the SaaS dashboard. Currently no feedback for ~30% of
mutations (silent success / silent failure).

## Smallest End State
Three variants (success / warning / error); auto-dismiss after 5s;
dismiss-on-click; stack-up-to-3 with FIFO eviction. ONE entry point
(`toast.success(msg)` / `toast.warning(msg)` / `toast.error(msg)`).
Component slots into existing app shell; no route changes; no API
changes.

## Decision
Three pieces:
1. `ToastStore` (Zustand) — queue + add/remove actions
2. `<ToastContainer>` (React component) — renders queue; auto-dismiss timer
3. `toast` (imperative API) — wraps store actions; the thing app code calls

## Out of Scope
- Persistence across page navigation (toasts disappear; this is feedback,
  not notification history)
- Action buttons in toasts (re-enable later if specific use case emerges)
- Animations beyond CSS transition (no Framer Motion etc.)
- Toast position config (fixed top-right)

## Alternatives Considered
1. react-hot-toast / sonner library — rejected: 30KB+ bundle for ~50
   lines of functionality; we control all 3 variants in-house
2. Just `console.log()` for failures — rejected: not user-facing
3. Modal alert() — rejected: blocks UI; user explicitly said "non-blocking"

## What Becomes Obsolete
- Existing scattered `alert()` calls in 3 mutation handlers (delete in
  same PR)

## Open Questions
(none)
```

---

## Stage 2 — `writing-plans`

```markdown
# Plan: app-wide toast notifications

**Source brief**: docs/code-toolkit/specs/2026-05-16-toast.md
**Total tasks**: 4 (≤5 ✓)
**Execution order**: sequential with Task 4 dependent on 1-3
**Plan-document-reviewer verdict**: PASS (2026-05-16, 12/12)

## Task 1 — ToastStore (Zustand)
- Description: New file `src/stores/toast.ts`. Zustand store with
  `toasts: Toast[]`, `add(toast)` (FIFO evict if >3), `remove(id)`.
- Module: `src/stores/toast.ts`
- Acceptance:
  - RED: `toast.test.ts > add() pushes to queue` fails (file doesn't exist)
  - GREEN: 4 unit tests pass (add / remove / FIFO eviction / id uniqueness)
- Dependencies: none
- Brief item covered: "queue + add/remove actions"

## Task 2 — toast imperative API
- Description: New file `src/lib/toast.ts`. Exports `toast.success` /
  `toast.warning` / `toast.error` — all wrap `useToastStore.getState().add()`.
- Module: `src/lib/toast.ts`
- Acceptance:
  - RED: `toast-api.test.ts > toast.success adds with variant=success` fails
  - GREEN: 3 unit tests pass (one per variant)
- Dependencies: Task 1 completes first
- Brief item covered: "ONE entry point ... `toast.success(msg)` / `.warning` / `.error`"

## Task 3 — <ToastContainer> component
- Description: New file `src/components/ToastContainer.tsx`. Reads from
  store; renders each toast with variant class; CSS transition on
  enter/exit; auto-dismiss after 5s; dismiss-on-click; positioned
  top-right.
- Module: `src/components/ToastContainer.tsx`
- Acceptance:
  - RED: `ToastContainer.test.tsx > renders queue contents` fails
  - GREEN: 5 unit tests pass (render / variant class / auto-dismiss
    timer / click-to-dismiss / position)
- Dependencies: Task 1 completes first
- Brief item covered: "auto-dismiss after 5s; dismiss-on-click;
  stack-up-to-3"

## Task 4 — Replace scattered alert() + wire ToastContainer into App
- Description: Delete 3 `alert()` calls in mutation handlers; replace
  with `toast.error(msg)`. Add `<ToastContainer />` to `App.tsx`.
- Module: `src/App.tsx` + 3 mutation-handler files
- Acceptance:
  - RED: `App.test.tsx > renders ToastContainer` fails (not yet wired)
  - GREEN: integration test passes (mutation handler firing toast renders
    visible)
- Dependencies: Tasks 1, 2, 3 complete first
- Brief item covered: "ONE entry point" + Out of Scope wiki deletion

## Notes

Tasks 1, 2 are tightly sequential (2 imports 1). Task 3 is parallelizable
with Task 2 after Task 1 finishes. Task 4 joins after all.
```

---

## Stage 3 — `subagent-driven-development` + Stage 4 — `tdd-iron-law`

Task 1 (ToastStore) ships clean. Task 2 ships clean. **Task 3 (ToastContainer) returns BLOCKED.**

### Task 3 implementer BLOCKED — the child-test fallback flow

```
status: BLOCKED
unblock_step: "task needs to be split smaller"
self_review:
  - 5 distinct test surfaces in one task overshoots ≤5min budget:
    (a) render queue, (b) variant CSS class, (c) auto-dismiss timer,
    (d) click-dismiss, (e) positioning. Each is its own RED-GREEN
    cycle — fixed-position CSS doesn't have any test interaction with
    timer logic. Tried to do them all; 25 min in, still RED on (c)
    because timer testing needs vi.useFakeTimers + flush-promises
    plumbing I haven't set up.
  - Recommend writing-plans re-invocation per Beck (2002) Part II
    §Child Test pattern.
```

### Re-invoke `writing-plans` on Task 3

writing-plans applies the splitting framework to Task 3. Produces child plan at `docs/code-toolkit/plans/2026-05-16-toast-part-3-children.md`:

```markdown
# Plan: Task 3 child decomposition (Beck Child Test pattern)

**Parent task**: Task 3 — <ToastContainer> component
**Parent decomposition rationale**: original task had 5 test surfaces; 25min
implementer effort hit BLOCKED on timer fixture setup. Per Beck (2002)
Part II §Child Test: write smaller tests, get them green, then return.

## Task 3a — ToastContainer render queue
- Description: Component reads from store; renders each toast item with
  toast.message visible. No styling, no timer, no click handler.
- Acceptance:
  - RED: `> renders all queue items` fails (component doesn't exist)
  - GREEN: render assertion passes with 3 mock toasts in store
- Dependencies: none
- Parent: Task 3 (this is child a of 5)

## Task 3b — Variant CSS class
- Description: Add `data-variant={variant}` attribute / `toast-{variant}`
  className. Mock store with 1 toast per variant; assert class.
- Acceptance: RED: `> applies toast-success class for success variant`
- Dependencies: Task 3a
- Parent: Task 3 (child b of 5)

## Task 3c — Auto-dismiss timer
- Description: 5s setTimeout; after timeout, call store.remove(id). Use
  vi.useFakeTimers + vi.advanceTimersByTime(5001) in test.
- Acceptance: RED: `> removes toast after 5s` fails
- Dependencies: Task 3a (needs base component to wrap timer logic)
- Parent: Task 3 (child c of 5)
- Notes: this child unlocks the timer fixture pattern that 3d will reuse

## Task 3d — Dismiss-on-click
- Description: onClick handler on toast item; calls store.remove(id).
- Acceptance: RED: `> removes toast on click` fails
- Dependencies: Task 3a (parallel with 3c)
- Parent: Task 3 (child d of 5)

## Task 3e — Top-right positioning
- Description: Container has fixed position top-4 right-4 (Tailwind);
  z-50.
- Acceptance: RED: `> positioned fixed top-right` fails
- Dependencies: Task 3a (parallel with 3c, 3d)
- Parent: Task 3 (child e of 5)

Parent Task 3 declared DONE when all children DONE.
```

5 children, each ≤5min. SDD dispatches each. All PASS. Parent Task 3 declared DONE. Task 4 unblocks.

---

## Stage 6 — `requesting-code-review`

```
verdict: PASS_WITH_NOTES

dimension_scores:
  security: PASS
  architecture: PASS
  correctness: PASS
  naming: PASS
  tests: PASS
  refactoring: PASS_WITH_NOTES  # ← see findings
  cross-task-coherence: PASS

findings:
  - severity: 🟡 should-fix
    dimension: refactoring
    where: src/components/ToastContainer.tsx:42-55 + src/stores/toast.ts:18-25
    source: code-team/standards/refactoring-standard.md §Rule of Three
    note: Both files have similar "find toast by id" logic (.findIndex
      + .filter pattern). Rule of Three not yet triggered (only 2
      instances), but a future 3rd would warrant extracting a shared
      helper. Note for next refactor pass.

summary:
  - Branch follows brief tightly; no scope creep (no animations
    beyond CSS, no action buttons, no persistence)
  - Child-test split on Task 3 produced cleaner test fixtures than
    a monolithic Task 3 would have — Beck Child Test pattern
    working as designed
  - 3 alert() calls deleted in same PR per brief Axis 5
```

---

## Stage 7 — `verification-before-completion`

```
$ npm test
✓ src/stores/toast.test.ts (4)
✓ src/lib/toast-api.test.ts (3)
✓ src/components/ToastContainer.test.tsx (5)
✓ src/App.test.tsx (1)
... (52 pre-existing tests) ...

Test Files  18 passed (18)
Tests       65 passed (65)
```

65/65 PASS. PASS.

---

## Stage 8 — `finishing-a-development-branch`

Same 7-step flow as Python example. `git-memory` decides Decision: trailer warranted (Rule-of-Three deferral) + Learning: trailer (timer-fixture pattern from Task 3c reusable for any timer-based test).

---

## What this example demonstrates (NEW vs Python example)

| Aspect | Demonstrated |
|---|---|
| SDD BLOCKED → child-test fallback | Task 3 hit ≤5min wall; writing-plans re-invoked; produced 5-child decomposition per Beck Part II |
| Parent-child DONE relationship | Parent Task 3 only declared DONE when all 5 children DONE; SDD orchestrator tracks |
| Cross-task PASS_WITH_NOTES | requesting-code-review surfaced Rule-of-Three deferral as 🟡 (not blocking; informational) |
| Decision: + Learning: trailers | git-memory wrote both — design choice (Rule of Three) + reusable pattern (timer fixture) |

## See also

- [`python-csv-export.md`](python-csv-export.md) — simpler 3-task case with all-clean execution
- [`swift-network-layer.md`](swift-network-layer.md) — refactoring case with Feathers 2004 legacy backfill
- [`../../skills/writing-plans/SKILL.md`](../../skills/writing-plans/SKILL.md) §BLOCKED fallback — the Beck Child Test mechanism this example exercises
- [`../../skills/subagent-driven-development/SKILL.md`](../../skills/subagent-driven-development/SKILL.md) §Status taxonomy — BLOCKED handling
