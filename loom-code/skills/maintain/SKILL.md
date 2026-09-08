---
name: maintain
description: |
  Routes an incident or regression into an existing or new intent and requires a permanent failing case before the fix. Use for CI failures, bug reports, alerts, or dogfood incidents.
version: 1.1.0
---

# Maintain

Maintenance changes how work enters Loom, not how it is published.

1. Reproduce the incident and capture the smallest permanent regression case.
2. Attach it to the matching open intent, or create one with
   `originator: maintenance-loop` when none exists.
3. Record which existing check should have caught it. Add a new mechanism only
   when a deterministic regression test earns its ongoing cost.
4. Hand the confirmed intent to Write Plan and continue through Build, one
   closing Review, generated attestation, and fast Ship.

Do not create review rounds, dispatch records, probe ledgers, or SHA alignment
work during incident intake.
