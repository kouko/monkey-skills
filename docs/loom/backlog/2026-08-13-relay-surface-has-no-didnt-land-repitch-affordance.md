---
name: 2026-08-13-relay-surface-has-no-didnt-land-repitch-affordance
description: loom can explain something badly and nothing in the system notices — the relay surface has no user-invoked "that didn't land, re-pitch it" affordance, which is the one place a register instruction has a real detector (the reader) and immediate judgment
status: open
origin: 2026-08-13 discussion of whether to declare a lightweight writing register in loom's document schemas — the register idea was sound but misplaced, because the third-party skill it came from works by firing at a detected failure moment, and a document schema has no such moment
start: the blinded-panel harness from the 2026-08-13 authoring-form arc exists and has produced one result, OR the next substantive touch of requesting-code-review/references/relay-phrasing.md — whichever comes first
---

- Start: the blinded-panel harness from the 2026-08-13 authoring-form arc
  exists and has produced one result, OR the next substantive touch of
  requesting-code-review/references/relay-phrasing.md — whichever comes first

- Origin: 2026-08-13 discussion of whether to declare a lightweight writing
  register in loom's document schemas — the register idea was sound but
  misplaced, because the third-party skill it came from works by firing at a
  detected failure moment, and a document schema has no such moment

- **What**: a user-invoked affordance on the relay surface — the moment loom
  explains something to the reader — that the reader triggers when an
  explanation did not land, and which re-pitches the same content in a plainer
  register. Shape borrowed (not text) from a third-party skill that does
  exactly this in one phrase, with no rules and no checker. Its licence was
  not checked, and does not need to be unless text is lifted; only the shape
  is wanted.

- **Why here and not in the document schemas**: the affordance works because a
  human has just said "I did not understand that". That gives it a trigger
  moment and an immediate judge. Placed instead as a standing declaration in
  `handoff-brief-format.md` or `plan-format.md`, it would have neither — it
  becomes descriptive discipline prose sitting permanently in context, which
  this repo measured at 0/2 for changing behaviour
  (`docs/loom/memory/imperative-trigger-cards-beat-descriptive-preloads.md`).
  It would also pull against the precision discipline those documents carry
  (hedged claims, evidence grades, the literal unverified-assumption label at
  `plan-format.md:225`), and would teach future authors that a schema file is
  a place to put style declarations.

- **This is a measurement candidate, not a free-ride assertion.** The whole
  point of the 2026-08-13 arc is that authoring-form rules get measured before
  they get legislated. A one-line register instruction is cheap enough to
  tempt a "just add it" — resist that. Run it through the same blinded panel
  with matched controls (cases where re-pitching plainer would LOSE
  information the reader needs), and honour the pre-registered gate.

- **Where it would live**: `requesting-code-review/references/relay-phrasing.md`
  owns relay form today, and `loom-pipeline/hooks/family-relay.md` owns the
  cross-family relay discipline. Either is a plausible home; that choice is
  part of the work, not settled here.

- **Related**: the 2026-08-13 authoring-form brief
  (`docs/loom/specs/2026-08-13-authoring-form-evidence.md`) explicitly scopes
  the relay surface OUT — this entry is that exclusion, recorded.
