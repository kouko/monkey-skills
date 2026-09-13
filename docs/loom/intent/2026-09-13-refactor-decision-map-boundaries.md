# Refactor Decision Map boundaries
originator: kouko
kind: engineering
needs-design: no — internal module boundaries only; public commands and stored artifact behavior remain unchanged
status: confirmed 2026-09-13
publication: automatic — authorized 2026-09-13 by kouko

## Problem
Decision Map validation and mutation responsibilities are concentrated in two large, tightly coupled modules. This makes routine changes harder to isolate and raises the chance that a local edit affects unrelated behavior.

## Proposed outcome
Decision Map internals have smaller, explicit responsibility boundaries while preserving their existing public behavior and stored artifact compatibility.

## Acceptance
1. Existing Decision Map commands and Python entry points continue to produce the same observable results for valid and invalid stores.
2. Validation, parsing, persistence, and transaction coordination have explicit module ownership that can be tested independently.
3. The Decision Map package and repository integration suites pass without weakening existing assertions.

## Constraints
- Preserve current command-line behavior, Python entry points, exception behavior, and schema-v3 artifact compatibility.
- Use test-first changes and avoid unrelated cleanup.
- Do not change publication behavior or the Loom workflow contract.

## Out of scope
- New Decision Map features or schema versions.
- Performance optimization without measured evidence.
- Refactoring `check_mechanisms.py` or publication handlers.

## Open questions
- none
