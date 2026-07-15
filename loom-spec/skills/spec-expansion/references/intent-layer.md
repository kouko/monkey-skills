# The persistent intent layer — consuming it as prior-state, authoring it

> Companion to [`../SKILL.md`](../SKILL.md). Two halves: §Consuming (read the
> layer as prior-state before Phase ①) and §Authoring (write/extend the
> durable spec root). Load whichever half the run needs.

## Consuming — prior-state intake (READ-ONLY)

When the capability you are spec-ing already has a persisted intent layer,
read it as prior-state so this cycle extends the last one rather than
re-deriving it from scratch. This closes the spec→spec loop: loom-spec reads
its own persisted output as the seed-context for the next change.

**Point-don't-copy.** REFERENCE the persisted files by path and link back to
the named sections — NEVER copy their content into the change-folder. A copy
is a second source of truth that drifts from the layer it duplicates; the
persisted layer stays the single source, and the change-folder points at it.
This read path never authors or edits the persisted layer (that is
§Authoring's job).

Map each persisted prior-state to the phase it feeds (read each WHEN PRESENT):

| persisted prior-state | feeds |
|---|---|
| MID `docs/loom/spec/<capability>/README.md` (intent / why / scope) | Phase ① seed-adequacy + USM backbone |
| TOP `docs/loom/spec/MODEL.md` `## Object state machines` | Phase ② OOUX object/state model (extend, don't redefine) |
| TOP `MODEL.md` `## Invariants` | Phase ③ matrix guard-rule lenses |
| TOP `MODEL.md` `## Out of scope` | Phase ③ pruning (don't fan deliberately-excluded paths) |
| the generated INDEX (capability→req→test), when present | the fan boundary — fan NET-NEW only (#406 semantics) |

**The empty base case — prior-state intake is ADDITIVE and may be empty.** A
net-new capability (or a repo mid-adoption with no layer or index yet) reads
whatever exists, possibly nothing. An empty or absent layer is never
authoritative — there is no cold-start deadlock: if no persisted layer
exists, skip this intake and treat the input as a generic seed. The INDEX in
particular lives at a later (capstone) repo location, so reference it when
present; its absence is covered by this base case.

## Authoring — the durable spec root

The hybrid change-folder output is the per-change artifact (consumed once by
VERIFY then frozen). The persistent intent layer is the durable spec root
that outlives any single change — the cross-cutting model and per-capability
intent that tests cannot encode. It lives in two altitudes:

- **TOP** — `docs/loom/spec/MODEL.md`: the cross-cutting model that spans
  capabilities (system-wide invariants, object lifecycles, the global scope
  boundary).
- **MID** — `docs/loom/spec/<capability>/README.md`: one per capability,
  carrying that capability's intent / why / scope.

**TOP `MODEL.md` carries exactly these three canonical sections** (the header
text is load-bearing — the plugin root's `scripts/validate_intent_layer.py`
enforces it via `_TOP_SECTIONS`, so match it verbatim):

```
## Invariants
## Object state machines
## Out of scope
```

`## Invariants` are the rules that must always hold across capabilities;
`## Object state machines` are the cross-cutting object lifecycles; `## Out of
scope` is the global boundary of what the system deliberately does not do.

**MID `README.md`** carries the capability's **intent / why / scope** — the
reason this capability exists and what it is responsible for, not how any one
flow behaves.

**Cut rule #4 — TOP vs MID placement.**
Ask: *"remove this capability — does this content get deleted?"*
- **YES** → it belongs in the capability's **MID** `README.md`.
- **NO** (it survives the capability's removal because it spans others) → it
  belongs in **TOP** `MODEL.md`.

**Anti-pattern — MID must NOT restate behavior a test owns.** A MID `README.md`
that re-describes step-by-step what a flow does duplicates what the `####
Scenario:` acceptance tests already own — the residual-rot surface: the prose
and the tests drift apart, and the prose silently goes stale. Keep MID at the
intent/why/scope altitude; let the tests be the single source of truth for
behavior. This discipline is **human-reviewed, NOT a CI gate** — no script
detects restated behavior, so a reviewer must hold the line at authoring time.

## Requirement status — semantics beyond the declaration

(Declaration syntax lives in `../SKILL.md` §Requirement status; this section
carries the authority framing and the merge-boundary behavior.)

**Canonical vs inspirational (Tessl framing).** A requirement's status maps onto
Tessl's spec-authority distinction — tests are what turn an *inspirational* spec
into a *canonical* one:

- a **verified `active`** requirement (has passing tests bound via `@req`) =
  **canonical** — authority from test-binding;
- a **`deferred` or unverified** requirement = **inspirational** — intent stated,
  not yet test-bound.

**Merge-boundary gate behavior.** The `active`-coverage check is a
**post-finishing, pre-merge required PR check** (it needs `@req` resolution +
test results, so it is merge-pinned, not run on req emission and not mid-RED):

- **`active` + 0 passing tests = FAIL** — blocks the merge. By the merge boundary
  the TDD RED must have gone GREEN; this is **not** failed mid-RED, where a
  freshly-specced `active` req legitimately has 0 tests (failing it then would
  invert the iron law).
- **`deferred` + 0 tests = surfaced** — shown in the index as *inspirational*,
  **never** a FAIL.
