# Recap state natural output
originator: kouko
kind: engineering
needs-design: no — this changes a skill contract, which the repository classifies as an engineering artifact rather than an interface surface
status: confirmed 2026-09-12

## Problem
The recap-state skill currently instructs agents to show internal planning tags and numbered template labels directly in chat. Users see private planning scaffolding, closing tags, and discontinuous numbering instead of a natural recap.

## Proposed outcome
Replace the exposed template skeleton with a goal-grounded alignment loop. Keep planning internal, present the recap through six natural sections, anchor current state and remaining work to an explicit current purpose, and end by checking the purpose, position, and proposed next step together.

## Acceptance
1. A recap uses six natural sections that move from purpose and current position through evidence, gap, decision need, and pending work to a final alignment check.
2. A recap never displays thinking or recap XML tags, closing tags, or `Block N` template labels.
3. The current purpose is always grounded in conversation evidence; broader purposes appear only when explicitly established, and an unknown purpose is reported rather than invented.
4. The final check restates the purpose, current position, and proposed next step, then waits for the user to confirm or redirect.
5. The three localized READMEs explain the Goal-Grounded Alignment Loop with a Mermaid diagram.
6. Runtime diagrams remain optional and information-compressing: use Mermaid only when rendering support is known, otherwise ASCII; never replace the six natural-language sections with a diagram.
7. Regression tests reject internal output markers and retain exact quoting, plain-language, visual-threshold, and stop-gate requirements.
8. The authoritative reference and examples agree with the corrected output and architecture contracts.

## Constraints
- Keep the change independent from the active capture-intent, write-spec, and write-plan scope-control change.
- Use test-first implementation and make the smallest coherent change.
- Do not add stations, checker rules, identifier schemas, or review loops.
- Do not push, open a pull request, or merge.
- Do not require short-, medium-, and long-term goals when the conversation does not establish them.

## Out of scope
- Changing recap-state routing, activation phrases, cross-session handoff behavior, or the built-in `/recap` distinction.
- Redesigning other Loom skills or historical evidence records.
- Adding a client-detection subsystem or assuming that every Codex host renders Mermaid.
- Publishing the branch.

## Open questions
- none
