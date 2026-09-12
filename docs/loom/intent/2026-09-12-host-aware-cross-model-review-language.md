# Host-aware cross-model review language
originator: maintenance-loop
kind: product
needs-design: yes — changes user-facing review prompts and the multi-host provider-selection behavior they describe
evidence: [loom-design/skills/capture-intent/references/second-vendor.md, loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md, loom-code/scripts/second_vendor_policy.py]
status: confirmed 2026-09-12
publication: automatic — authorized 2026-09-12 by kouko

## Problem
When Loom runs in Codex, it can ask whether to use Codex for the independent review even though Codex is already doing the work. The wording also calls this a second reader, which hides the real purpose: getting an independent review from a different model family.

## Proposed outcome
Make every review prompt identify an available tool whose model family differs from the current host, describe the capability directly as an independent review by another model family, and present the message as a simple one-column Markdown table with one heading and one descriptive cell.

## Acceptance
1. When Loom runs in Codex, any cross-model review prompt or suggestion names Claude Code or another available non-Codex model family, never Codex itself.
2. When Loom runs in Claude Code, any cross-model review prompt or suggestion names Codex or another available non-Claude model family, never Claude Code itself.
3. User-facing Loom text describes the option as an independent review from another model family and no longer calls it a second reader.
4. Automated regression cases prove the host is excluded for both Codex and Claude Code paths while preserving the existing ask, suggest, and fixed-choice behavior.
5. Every user-facing cross-model review suggestion uses a one-column Markdown table containing only a heading and one descriptive cell, leaves two blank lines before and after the table, and remains readable when shown as raw Markdown.
6. Ask mode uses the host's native question interface when available; if that interface requires a recommended option, it recommends not using an external reviewer for this change, while still offering the runnable different-model-family tool as an explicit choice.

## Constraints
- Keep provider use explicit and preserve the current non-blocking behavior of suggest mode.
- A separate invocation of the same model family does not satisfy the cross-model independence goal.
- Use observed, runnable CLI availability; do not install, authenticate, or silently substitute a tool.
- Keep the single-column table readable in narrow terminals without adding secondary fields or decorative rows; preserve the two surrounding blank lines even when composing it beside other decision-point text.
- When a native question interface is unavailable, ask mode must retain a readable, blocking fallback without pretending the host supplied a native control.

## Value case
GO — the current prompt can recommend no actual model diversity, defeating the feature's core purpose and misleading the user at the decision point.

## Out of scope
- Comparing model quality or choosing a specific model version within a provider.
- Running multiple external model families in the same review.
- Changing review verdict, attestation, or publication semantics.

## Open questions
- none
