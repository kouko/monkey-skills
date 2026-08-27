# Behavioral complexity lens

Apply this lens after Phase ③'s existing cell-level lenses. Assess the
objects, roles, states, paths, NFRs, and obligations that remain after
expansion. No upstream complexity note is required: perform the local
assessment from the current seed and proposal whenever optional evidence is
absent.

Use the existing `KEEP` / `FLAG` / `DROP` semantics. Mark retained and
justified behavioral complexity with the user or system value that requires it.
Record deletions for redundant, impossible, or speculative cells; do not carry
speculative scope forward. Flag remaining downstream risks or ambiguity for the
existing blind-spots
section rather than inventing a new behavioral contract.
Only `DROP` a cell as simplification when the remaining behavior still achieves
the required user or system outcome; otherwise expose the lost outcome as a
scope decision.

Record the assessment in the existing `## Path × edge matrix`, `## Provenance`,
and `## Blind spots — needs human/field input` proposal sections. Do not add an
eighth proposal section, a universal schema, or behavioral guards; this lens
summarizes the burden that survived pruning, while the existing spec workflow
continues to own the requirement and scenario detail.
