# writing-plans / SDD: name "deterministic sync-script output" as an explicit mechanical-exemption category

## Problem

The `Review-weight: mechanical` exemption (writing-plans, `plan-format.md`)
already covers "an identical or near-identical edit reproducible from an
exact spec." A recurring task shape this session hit twice (PR #519's
CI-drift-fix commit: `research-toolkit/scripts/sync-primitives.sh` +
`scripts/sync_codex_manifests.py`) — running an established, deterministic
sync/mirror script and committing its output, verified by a checksum or an
existing drift-detection test — plausibly already qualifies under that
wording, but nothing names it explicitly. Per this repo's own precedent
(machine-local memory `feedback_compressing_exemption_section_flips_polarity.md`:
two confirmed incidents where under-specified exemption wording caused real
misapplication), an ambiguous-but-technically-covered category is exactly
the kind of gap that invites either (a) an implementer wrongly claiming the
exemption for something that isn't actually reproducible-from-exact-spec, or
(b) a reviewer wrongly rejecting a legitimate mechanical case because the
category wasn't named. The job: make this specific, real, recurring case
explicit — not change what the exemption means.

## Users

Whoever authors a writing-plans plan (human or the orchestrating agent) for
a task that is "run an established sync script, commit its deterministic
output" — and the `plan-document-reviewer` / SDD orchestrator that
validates/executes the `Review-weight: mechanical` marker on that task.

## Smallest End State

Add one named example category to the existing definition, not a new
mechanism:

1. `writing-plans/references/plan-format.md` — extend the `Review-weight`
   section's qualifying description with an explicit second bullet:
   "an established, deterministic sync/mirror script's output, verified by
   checksum or an existing drift-detection test" — alongside a short
   concrete example (mirrors the existing copyright-year-bump worked
   example already in the file).
2. `subagent-driven-development/SKILL.md` — the mechanical exemption's
   **Content match** self-check currently assumes the implementer names a
   literal string/diff target *in the task description in advance*. A
   sync-script task's exact output isn't known in advance (it's computed by
   the script) — so add a second, alternative Content-match shape: "for a
   task whose spec is 'run script X, commit its deterministic output,' the
   check is: re-run script X and confirm zero diff against what was
   committed (or the script's own paired drift-detection test exits 0)."
   This is an additional verification SHAPE, not a loosening of the
   existing one — both still require zero hand-written logic and a
   deterministic, re-runnable check.

No new file, no new opt-in flag, no change to Check 16 (it already checks
"reads as reproducible from an exact spec" generically, which this category
satisfies without a check-level change).

## Current State Evidence

- **Forward** (who reads these sections): `plan-format.md`'s Review-weight
  section is read by whoever authors a plan task (`writing-plans/SKILL.md`
  §The splitting framework) and by `plan-document-reviewer-prompt.md` Check
  16 (`loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md:48`)
  when validating a plan. `subagent-driven-development/SKILL.md:108-111`
  is read by the SDD orchestrator at task-dispatch time to decide whether to
  skip the reviewer triad.
- **Reverse**: neither file is a distributed/synced functional copy (unlike
  `standards/`/`rubrics/`/`checklists/`, which mirror `code-team` via
  `scripts/distribute.py`) — confirmed no `distribute.py`/`sync.sh`
  reference to either file. Edits here have no SSOT-mirror obligation.
- **Error path**: today, a task like "ran sync-primitives.sh, committed the
  output" has no clean way to satisfy the Content-match self-check
  (`subagent-driven-development/SKILL.md:110`) as currently worded, since
  it requires a pre-stated literal string/diff — so such a task would
  either be mis-marked mechanical and fail Check 16's spirit, or be forced
  through the full triad for zero-logic, deterministic output.
- **Data/Boundary**: N/A — pure documentation, no runtime data shape
  changes.

Evidence paths:
`loom-code/skills/writing-plans/references/plan-format.md`,
`loom-code/skills/subagent-driven-development/SKILL.md`.

## Decision

Add the named example + the alternative Content-match verification shape in
both files, in one small direct edit (not a full SDD dispatch — two files,
one coherent concept, matches how Task 1's SKILL.md-only prose fix was
handled directly earlier in this session). Verify via a fresh-context
cold-read per `judgment-rubrics.md` §5 (same method used for the earlier
SKILL.md-only fix this session), since this is documentation, not code with
a pytest surface.

## Out of Scope

- Any other new mechanical-exemption category (only the sync-script-output
  case, which is the one with real recurring evidence this session).
- Changing Check 16 itself.
- Touching `plan-document-reviewer-prompt.md` (its check is already
  general enough to cover this case without edits).
- Retroactively re-marking the two PR #519 CI-fix commits as mechanical —
  they already shipped under the full/direct-implementation path; this is
  forward-looking only.

## Alternatives Considered

Narrow — this is a documentation-clarity fix, not a design choice:
- **Do nothing, rely on the existing general wording** — rejected per the
  polarity-flip precedent: ambiguous-but-technically-covered is exactly
  the failure shape that has bitten this repo twice before.
- **Add a whole new opt-in flag distinct from `Review-weight: mechanical`**
  — rejected as over-engineering; this is squarely the same category
  ("reproducible from an exact spec"), just under-exemplified, not a
  different kind of exemption.

## What Becomes Obsolete

Nothing removed; purely additive documentation.
