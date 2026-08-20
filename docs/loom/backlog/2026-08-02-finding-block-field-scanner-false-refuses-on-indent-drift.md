---
name: 2026-08-02-finding-block-field-scanner-false-refuses-on-indent-drift
description: loom_gate_markers' per-finding field scanner anchors on one column, so two shapes of benign indentation drift refuse a well-formed verdict and blame the wrong field
status: open
origin: Task 1 of the finding-origin-attribution arc (docs/loom/plans/2026-08-02-finding-origin-attribution.md), code-quality review of the column-anchoring hardening round
start: when a real reviewer verdict is refused for a reason its author cannot locate, or when the scanner is next opened for any reason
---

## What happens

`_finding_problems` in `loom-code/scripts/loom_gate_markers.py` decides
which lines inside a `- severity:` block are that finding's own fields by
**column**: it takes the indent of the first non-blank line after
`- severity:` and accepts `where:` / `dimension:` / `origin:` only on
lines whose indent string equals it exactly.

That anchor closed a verified fail-open — a `dimension:` or `origin:`
line nested inside a `note: |` block scalar used to count as a sibling
field, which granted the docs-arm exemption (or satisfied the origin
requirement) off quoted text. Findings in this repo routinely quote
verdict schemas, and a quoted schema contains the literal line
`dimension: <which of the 7 above>`, so the hole was reachable in
ordinary use.

The anchor introduced two false-refusal shapes in exchange. Both were
executed against `_finding_problems` by the reviewer, both return
`['finding at line N: no origin: line']` on input that is well-formed:

1. **Outlier first field.** The first field line is indented deeper than
   its true siblings, so `column` locks to the outlier and every real
   field is skipped.
2. **Tab against spaces.** One field line is indented with a tab where
   its siblings use spaces. The comparison is raw string equality, so
   lines that align identically in an editor are different columns.

A third shape — a blank line immediately after `- severity:` — was fixed
in the same arc (the scanner now skips blank lines when choosing the
anchor); these two were left deliberately.

## Why they were left

The remedy the reviewer proposed is to infer the intended column from
the distribution of candidate field indents — a mode, or a
loosen-on-zero-matches fallback. That turns a line scanner into a parser
that guesses, and the guess would sit inside the predicate whose entire
purpose is to fail closed. The honest larger fix is to parse the verdict
as YAML rather than by line regex, which is a different and bigger
decision than this arc was scoped for.

Both remaining shapes fail in the **safe** direction — over-refusal,
never a fail-open escape — and a refusal is loud: the author sees a
blocked mint. The cost is diagnostic, not correctness: the message names
the missing field rather than the indentation slip that hid it, so the
author is pointed at the wrong repair.

## Cheapest partial fix, if this is picked up before the YAML question

Make the refusal self-diagnosing rather than making the scanner smarter:
when no line matches the anchor column but a line matching the field
regex exists at a *different* column inside the block, say so in the
message. That is a message change, not a matching-rule change, so it
cannot re-open the fail-open the anchor closed.

## Same weakness, wider blast radius

The `where:` check shares the anchor (deliberately — leaving two
conventions in one scanner is worse than the bug), so both shapes above
refuse a finding whose `where:` is present but off-column, not just one
whose `origin:` is.
