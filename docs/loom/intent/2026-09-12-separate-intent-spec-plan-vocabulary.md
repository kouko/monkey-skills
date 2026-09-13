# 分離 intent、spec 與 plan 的詞彙邊界

originator: kouko
kind: engineering
needs-design: no — only internal skill instructions and their contract tests change
status: confirmed 2026-09-12

## Problem
The three Loom stations use overlapping words such as need, requirement, and Acceptance. A model can therefore mistake an early request whose solution is still unknown for missing input, or expand an intent into product behaviour and implementation detail before those decisions belong.

## Proposed outcome
Each station states its own decision boundary with consistent terms: capture-intent owns the problem, desired outcome, value, success conditions, and scope; write-spec owns observable product behaviour; write-plan owns the simplest reversible implementation.

## Acceptance
1. capture-intent treats an expressed problem or desired outcome as valid input even when the user has not chosen a feature or implementation, and defines intent Acceptance as outcome-level success conditions.
2. write-spec says it translates confirmed outcomes into observable, verifiable product behaviour without adding a new outcome, value, or scope.
3. write-plan says it chooses the simplest reversible implementation for the confirmed specification and returns product gaps instead of silently inventing behaviour.

## Constraints
- Keep each station's definition local and short; do not add a shared glossary dependency.
- Do not rename artifact fields or add IDs, checker rules, stations, subagents, or review loops.
- Preserve the existing artifact schemas and plan structure.

## Out of scope
- Renaming intent `Acceptance` to `Success conditions`.
- Redesigning the capture-intent interview, write-spec format, or write-plan task model.
- Fixing unrelated cold-reader findings or changing publication behaviour.

## Open questions
- none
