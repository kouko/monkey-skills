# W18 native replay — preregistered grading spec

Written 2026-11-24 before any replay execution completed. Authorization:
user "ＯＫ" (2026-11-24) — three native local replays, gpt-6.1-sol/high,
same frozen input; any single replay reproducing the same-class overbroad
judgment rejects the W18 candidate; W15–W17 failures and counts retained;
no install/publish/merge.

## Frozen configuration

- Model `gpt-6.1-sol`, provider openai, reasoning effort high (user-selected
  in the 11-09 diagnostic; reused per authorization).
- Runtime: `git archive` of `skill-dev-toolkit/skills/skill-consistency-check`
  at HEAD `9b76c250fa15c77f76fe0339b3f6016f4cba344e` (contains the W18
  per-candidate isolation text, Step 6 items 2–3).
- Inputs: reconstructed from `w17-scope-first-results.json` `input_preimages`
  (93 files, every file SHA256-verified before dispatch; targets from tracked
  git blobs at refs `35a6be14…` (original=skill-refactor, case-k) and
  `cd2c2c02…` (case-m), raw detector JSON from the committed case and the
  committed diagnostic `case-inputs.json`).
- Packet: `packet.md` (frozen; only RUN_DIR differs between runs).
- Execution: tool-mediated full replay through `codex exec` (workspace-write
  sandbox) — this differs from the 11-09 inline diagnostic precisely by being
  the tool-mediated caller context where W17 failed.

## Runs

`trial` (run 1), `run-2`, `run-3` — three completed native replays total.
A harness-mechanics failure (exit nonzero, missing outputs, sandbox refusal)
does not count as a completed replay; a completed replay with decisions does.

## Grading (per run, per candidate)

Primary unit: original `read-1.json` finding `F1` — the W17 failure class
(creative / prose / non-deterministic disjunct mishandled via the
parenthetical example).

1. **Label**: F1 status must be `excluded`. The original's `why` asserts
   abort-vs-ensemble opposition for all targets whose output is "creative,
   prose, or non-deterministic"; the sources make abort conditional on
   creative/non-deterministic output (entry SKILL.md:358–360, protocol
   :119–123) and list prose as an ordinary Layer-1 artifact type
   (equivalence-check-protocol.md:17), so the asserted universal coverage is
   unsupported. Status `confirmed` = the original overbroad false positive
   reproduces = instant veto.
2. **Reason fidelity** (the W17 failure class): an `excluded` F1 reason
   fails if it:
   - (a) asserts the entry scope excludes all prose as an independent
     category (generalizing the parenthetical "writing style, prose, design
     feel" beyond the creative/non-deterministic category its source
     assigns), or
   - (b) claims the whole alleged target is outside entry scope without
     distinguishing the qualified category from the bare prose artifact
     type, or
   - (c) asserts a universal all-prose abort rule attributed to entry or
     protocol.
   A passing reason keeps the parenthetical within its source-assigned
   category and grounds the exclusion in the original's unsupported
   asserted coverage (or another source-grounded ground that does not
   overgeneralize).
3. **Controls**: case-k `HOLDOUT-K1` must be `excluded`; case-m
   `HOLDOUT-M1` must be `confirmed`.
4. Other original candidates (F2–F7, simulate F1–F7 area): no gold label is
   preregistered; recorded for the archive, not graded here.

## Decision rule

- Any one completed replay failing 1 or 2 (or a control in 3) → W18
  candidate rejected; record which run and which clause; W15–W18 all stand
  as failed candidates.
- All three completed replays clean on 1–3 → replay evidence requirement
  met; proceed to reviewer dispatch (closing-review §2).

## Cost disclosure

Three replays estimated ≈ USD 1.5–3 total (authorization estimate, not an
invoice cap). Per-run api-equivalent estimates recorded in each
`*.summary.json`; harness probe(s) cost ≈ USD 0.01 and are not replays.
