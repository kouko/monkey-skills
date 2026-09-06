---
name: a-probe-that-pins-a-manifest-block-as-a-literal-breaks-when-a-line-is-inserted-inside-it
description: An adversary probe that rewrites a manifest block by matching its exact text pins every line between its first and last anchor; a later change that adds an entry inside that span turns the probe red for a reason unrelated to the behaviour it tests — append new entries after the last pinned line, or make the probe patch by key rather than by literal
type: gotcha
origin: 2026-09-05-artifact-charter-boundaries-and-edit-rights — adding a policy id after the first entry of the review row's edits_after list broke a green probe that patched that block by string replacement; moving the new id to the end of the list restored it
---

The probe simulated the old bare-string `edits_after` shape by replacing
the row's first three entries with plain strings, asserting the patched
text differed from the original. A new id inserted after the first entry
changed the middle of that literal, the replacement matched nothing, and
the probe failed on its own precondition.

**Why:** probes are graduated into the permanent suite and re-run by the
push gate; a probe that encodes the manifest's line order is a hidden
ordering constraint on every later manifest edit.

**How to apply:** when a probe must mutate a manifest block, patch by
key (load the YAML, edit the mapping, dump) or replace only the single
line it needs; when editing a list a probe pins, add at the end. If a
probe goes red after a manifest edit, read its precondition assertion
before the behaviour assertion.
