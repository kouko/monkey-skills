# Evidence-based modular implementation decisions
originator: kouko
kind: engineering
needs-design: no — this changes internal Loom skill and reviewer behavior without changing a declared user interface
status: confirmed 2026-09-13
publication: automatic — authorized 2026-09-13 by kouko

## Problem
Loom mentions module boundaries but does not give agents enough evidence-based guidance to distinguish a meaningful module from a long file split into smaller files. People using Loom can therefore receive either tangled implementations that consume unnecessary agent context or fragmented implementations that add navigation without reducing dependencies.

## Proposed outcome
People using Loom receive implementations organized around meaningful, independently understandable and testable boundaries when the current change provides evidence that separation helps, while cohesive code remains together regardless of file length.

## Acceptance
1. A fresh Loom run facing separable responsibilities can choose and implement a boundary that reduces the context and dependencies needed for the requested change.
2. A fresh Loom run facing a long but cohesive file does not split it solely because of its length.
3. Closing review identifies a physical file split that leaves responsibilities, state, testing, or change scope coupled.
4. Ordinary feature development receives this judgment through the existing Loom flow without another user decision or a separate mandatory skill.
5. Committed regression evaluations distinguish meaningful extraction, cohesive-long-file, and shallow-file-split cases while the existing Loom package suite remains green.

## Constraints
- File length is a warning signal, never a universal pass/fail threshold.
- The existing write-plan, build, and review responsibilities remain the delivery path.
- Any blocking fact remains mechanically recomputed; semantic boundary quality remains reviewer judgment backed by executable evidence.
- The net mechanism count does not increase without the existing declared exception process.

## Out of scope
- A repository-wide legacy modularization or refactoring skill.
- Universal line, token, function, or file-count limits across languages and repositories.
- Refactoring code unrelated to the requested feature.
- Requiring users to choose module boundaries or review implementation structure.

## Open questions
- none
