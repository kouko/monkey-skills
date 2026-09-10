---
name: a-checker-allow-list-is-enabled-by-charter-policy-ids-and-fails-closed-on-an-unknown-one
description: A rule that permits a class of edits reads the permitted classes as stable ids from the charter row in contract/manifest.yaml, implements one branch per id, blocks an id it does not implement, and pins the implemented set equal to the manifest's — a new allowance is a new id (vendors-gain-entries), never a widened existing branch, because the rule's prose and the manifest then agree by construction
type: practice
sources:
  - resource: 2026-09-05-artifact-charter-boundaries-and-edit-rights — two readers found the first plan-edits rule hard-coded its five allowances (a second drift surface beside the charter), and a later fix let `vendors` ride on the four other arrays' id without any policy naming it
---

The first implementation enumerated the allowed edits as Python branches
and checked only that a plan carried the charter stamp. Both fresh readers
called that a second drift surface: change the charter row and the code
stays; change the code and the row stays. Parsing the row's prose would be
brittle, so the row gained `{id, text}` entries and the code enables
branches by id.

The pattern was then broken once, quietly: an exhaustive rewrite added
`vendors` to the accreting arrays gated by the id that names four other
arrays. Both readers caught it in the same round.

**Why:** the manifest is the copy humans and other plugins read; the checker
is the copy that runs. Ids are the only join that a test can pin from both
sides, and an unknown id failing closed is what makes a manifest edit
without a code edit visible.

**How to apply:** when a rule needs a new allowance, add an id to the
charter row and a branch that checks exactly that id; extend the
implemented-ids test; never fold the new case into an existing id's
branch. Read the rule's own description line afterwards — if it still says
"byte-equal" about a field that now accretes, the description is the
second drift surface.
