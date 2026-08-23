# Design panel dispatch

Use this contract when design work benefits from parallel perspectives. The
unit of dispatch follows the design artifact, not a code module:

- Object modeling: assign one worker per object.
- Journey analysis: assign one worker per journey.
- Critique: assign one worker per lens.

Dispatch all independent workers in one host-neutral fan-out, then wait for
all results before synthesis. Host adapters may express the operation with
their native subagent call shape; this contract does not require a particular
tool name or sibling plugin.

## Role boundary

A writer expands or changes the artifact. A critic only reports omissions,
contradictions, and risks; a critic never rewrites the artifact it judges.
Do not let one worker serve as both writer and critic for the same review
round.

## Artifact ownership

The orchestrating station is the artifact owner. Workers return bounded
findings and do not write the shared artifact directly. This keeps parallel
work from racing and leaves one accountable integration point.

## Join rule

At the join, form the union of all findings, preserve the source object,
journey, or lens, and deduplicate only substantively equivalent findings.
Resolve contradictions explicitly; do not silently choose one worker's view.
The artifact owner applies the accepted union in one deterministic edit.
