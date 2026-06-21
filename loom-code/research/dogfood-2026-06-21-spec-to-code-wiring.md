# Dogfood — spec→code seam wiring (2026-06-21)

Behavioral validation (Task 6) of the loom-spec → loom-code wiring. A marker
test asserts the contract *prose*; this dogfood asserts a fresh agent actually
*follows* it. Method: build a real validated change-folder, then dispatch a
fresh agent given ONLY the new writing-plans input contract + the change-folder
(not told the expected answer), and inspect what it produced.

## Fixture

A sample OpenSpec-pure change-folder, change-id `archive-note`, 1 Requirement /
2 Scenarios (`/tmp/loom-dogfood-archive-note/`). Gate:

```
$ python3 loom-spec/scripts/validate_spec_output.py /tmp/loom-dogfood-archive-note
OK: ... conforms to the OpenSpec skeleton.   # exit 0
```

So the freeze's reused validator (R4) accepts it — the entry gate's
named-artifact-presence + validate_spec_output-exit-0 confirmation (R6) holds.

## What the fresh agent produced (the 4 designed behaviors — all clean, zero guessing)

| Behavior | Result |
|---|---|
| **Scenario → RED/GREEN, full coverage (R3)** | ✅ 2 `#### Scenario:` → 2 tasks, 1:1; every scenario maps to ≥1 task's RED/GREEN. One Requirement fanned to 2 tasks (2 assertions = 2 tasks). |
| **Stable join-key traceability (R5)** | ✅ Both tasks: `archive-note / Requirement: Note archival / Scenario: <name>` — exact contract form (SKILL.md). |
| **Verbatim-copy carve-out (R2/R8)** | ✅ THEN observable copied verbatim into GREEN; Requirement prose + proposal narrative linked, not copied. |
| **Consumer read-only (R7)** | ✅ Only Read the change-folder; wrote its own plan elsewhere; no edit to proposal.md / spec.md. |

The four things we explicitly designed worked with **zero forced guesses**.

## Gap found → fixed (the dogfood's payoff)

**An OpenSpec-pure change-folder carries the WHAT (behavior) but no WHERE.** It
has no file/module/path info — yet `plan-format.md` makes `Module` and
`Files touched` REQUIRED (and `Files touched` is the parallelism disjointness
oracle). The "Consuming a loom-spec change-folder" section did not say how to
populate them, so the agent was **forced to guess** placeholder paths
(`src/note-archival.<ext>`).

**Fix (committed this branch):** the section now states the consumer fills
`Module` / `Files touched` / `Context paths` by **reconnaissance of the target
repo** (grep / Read / Explore — the same Current-State-Evidence recon
brainstorming does), seeded by the proposal's `## OOUX object model`; plus a
bullet mapping `### MODIFIED` / `### REMOVED` deltas to change/removal tasks +
test updates. Guarded by `test_changefolder_codetarget_fields_via_recon`.

## Minor notes (not gaps)

- **Output path in the dogfood was `/tmp/...`** because the fixture is detached
  from any target repo. In real use the change-folder lives at
  `docs/loom/<change-id>/` inside the target repo and the plan is its sibling
  `docs/loom/plans/<date>-<change-id>.md` — no contract gap, a fixture artifact.
- **MODIFIED/REMOVED deltas** were absent in this ADDED-only fixture; now
  addressed by the fix's bullet.

## Verdict

The wiring works end-to-end: a validated change-folder flows into a correct,
fully-traceable plan, and the freeze gate recognizes it — without breaking the
brief path, the STOP contract, or never-auto-merge. The one real gap
(code-target fields) was found by *dispatching* a consumer, not by marker tests,
and is fixed in the same branch.
