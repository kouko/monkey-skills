# Conditional execution detail

Read only the section whose trigger fires. The entrypoint remains the
executable contract; this reference explains why the branch exists and how to
handle its less-common cases.

## `ui-flows.md` seed

Read when the seed is a change-folder `ui-flows.md`.

Point to, rather than copy, its surface inventory, flows, entry/exit points,
and density flags. Map inventory and render variants to Phase ②; user flows,
entry, and exit to Phase ③c; transition character to Phase ③ pruning; and an
interaction-density flag to Phase ③b. A rich UI seed still fails the
seed-adequacy gate when a core lifecycle is missing.

## Phase ① navigation edge cases

Read when the journey is not a straightforward multi-stage flow.

The happy-path spine uses `forward` edges. The navigation graph may also use
`back`, `skip`, `abandon`, `resume_reenter`, `error_escape`, and `retry_self`.
A single-surface utility may collapse the backbone to one node; its modal
escapes and resume behavior live in the graph instead of a fabricated linear
journey.

## Phase ③ lens discrimination

Read while pruning when a terse discriminator below is insufficient.

- State-transition legality: preserve legal transitions, expose illegal
  attempts as edge cases, and discard impossible ordering.
- BVA: preserve minimum, maximum, empty, and just-over-boundary cases; one
  nominal interior value is enough.
- CRUD: cover only lifecycle-supported operations performed by real actors.
- Permissions: cover allowed actions and denied attempts; surface unstated
  authorization.
- Empty/error/loading: use for async, network, and collection boundaries, not
  purely synchronous local actions.
- NFR: retain obligations implied by real scale, security, concurrency,
  network, or timing constraints; ask when implied but unquantified.

## Phase ③b combination residue

Read when a stage has four or more co-active objects.

Pairwise generation covers every pair of parameter values but cannot promise
higher-order coverage. List higher-order residue as a blind spot. Never pad it
or describe pairwise output as exhaustive.

## Requirement status and persistent intent

Read when authoring persistent requirements rather than only a per-change
delta. Requirement headings accept `[active]` and `[deferred]`; no suffix means
active. Active requirements are intended for current verification, while
deferred requirements remain aspirational. The active-coverage check belongs
at the merge boundary, not mid-RED. Read `intent-layer.md` for the durable
TOP/MID model, id adoption, and authoring rules.
