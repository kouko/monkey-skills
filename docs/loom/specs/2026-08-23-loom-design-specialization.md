# Brief: specialize loom-design while preserving optional composition

## Goal

Make loom-design independently executable by giving it design-specific orchestration and review semantics, while preserving loom-code handoffs only where work genuinely crosses into implementation.

## Current State Evidence

- Whole-artifact review found unconditional loom-code calls in loom-design's relay and spec-expansion contracts.
- The pipeline driver still constructs a monorepo-shaped `loom-design/scripts/...` path that fails from an arbitrarily named isolated install root.
- The isolated-layout tests prove filesystem boundaries and public-name composition, but do not execute the packaged commands used by core workflows.
- Requirement identifiers are a shared artifact grammar, but loom-code currently reaches into loom-design to obtain that grammar.

## Smallest End State

- loom-design owns a local design-panel dispatch contract and a design-artifact relay contract.
- Cross-stage identifier grammar has one neutral repository source and deterministic plugin-local copies.
- loom-code and loom-design consume only their own packaged identifier copy.
- Pipeline commands resolve from the installed loom-design root rather than a repository parent or directory name.
- Isolated tests exercise the commands and absence branches that standalone operation requires.

## Brief Items

- BI-1 — Replace unconditional design-side use of loom-code dispatch/review behavior with loom-design-owned contracts.
- BI-2 — Preserve public loom-code handoffs only for genuine implementation-stage transitions and the explicitly combined conductor.
- BI-3 — Package shared identifier grammar into both plugins from one neutral source.
- BI-4 — Remove loom-code's runtime need to invoke loom-design for requirement-identifier semantics.
- BI-5 — Resolve pipeline scripts from the installed loom-design root without assuming the root directory is named `loom-design`.
- BI-6 — Prove standalone behavior with executable isolated-root probes, not lexical assertions alone.
- BI-7 — Resolve every interactive loom-design station command from the installed plugin root, not a checkout-shaped path.
- BI-8 — Represent pipeline command arguments without shell re-interpretation of consumer-controlled values.

## Alternatives Considered

- Merge loom-code and loom-design: rejected because it removes packaging boundaries but not the distinct design/code review, dispatch, and artifact semantics.
- Mirror every loom-code skill in loom-design: rejected because it creates shallow duplicate abstractions and two drifting implementations.
- Keep public sibling calls with fallback text everywhere: rejected for design review and dispatch because their judgment rules and deliverables differ materially from code work.

## Decisions

- Design-specific behavior stays inside loom-design; no generic mirrored `requesting-*` or `dispatching-*` skill is added unless it earns a direct user-facing trigger later.
- Shared artifact grammar is synchronized at build time, never loaded from a sibling plugin at runtime.
- Full `using-loom-pipeline` remains an optional two-plugin integration feature and keeps its entry-time availability gate.
- Interactive loom-design stations and ordinary loom-code workflows remain independently executable.

## Queue relation

unqueued — user explicitly selected the specialization direction during the active independent-plugin change

## Design-side on-ramp

not fired — this is a refactor of existing loom-design behavior with reviewed failure evidence, not a new product-design detour
