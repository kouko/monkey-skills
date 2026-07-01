# Dogfood report — spec→code seam wiring

- **Target:** the spec→code wiring on `feat/loom-code-spec-to-code-wiring` —
  `using-loom-code` Continuous-mode freeze (change-folder entry) +
  `writing-plans` "Consuming a loom-spec change-folder" input contract.
- **Date:** 2026-06-21 · **Method:** 3 probes, 6 subagents, 5 fixtures with real
  `validate_spec_output.py` ground truth.
- **Adaptation:** the feature is NEW BEHAVIOR inside two existing skills (not a new
  routable skill), so Probe A tests **input discrimination** (accept valid / reject
  invalid / don't confuse a brief), not router-level firing.

## Severity summary

| Sev | # | Category | One-line |
|---|---|---|---|
| 🔴 High | F1 | Gate-vs-contract incoherence | MODIFIED/REMOVED-only change-folder is walled off by the freeze validator, yet the contract promises to handle it |
| 🟡 Med-High | F2 | Convention / R6 asymmetry | the brief entry (a) has NO structural gate — accepted on declaration alone, via the shape-recognition R6 forbids for change-folders |
| 🟡 Med | F9 | Doc contradiction | plan output path: `<date>-<change-id>.md` (new section) vs `<topic>.md` (cross-skill table) |
| 🟡 Med | F8 | Jargon-leak / cold-start | undefined "OpenSpec-pure", "OOUX object model", bare "R5/R6" block a first-time reader |
| 🟡 Med | F6 | Output-quality / schema gap | empty-recon has no sentinel; `Files touched` (the parallelism oracle) ends up holding a guessed path |
| 🟢 Low | F3 | Workflow-drift | file-vs-folder (brief vs change-folder) discrimination not licensed by the contract |
| 🟢 Low | F5 | Convention | brief canonical path stated but not enforced |
| 🟢 Low | F7 | Convention | MODIFIED bullet says `### MODIFIED` (H3); validator + OpenSpec use `## MODIFIED Requirements` (H2) |
| 🟢 Low | F10 | Workflow-drift | writing-plans says the folder "must be validate-clean" but never says who runs the validator (ambient) |

**What PASSED (the designed behaviors held):** discrimination accuracy 5/5 across both
Probe-A runs (TPR/TNR 100% on the gate); scenario→RED/GREEN 1:1 full coverage; stable
join key exact form; point-don't-copy (only THEN observables copied); consumer read-only.
The **round-3 recon fix works** — Probe B exec1 actually reconnoitered, found no target
code, and honestly marked `(NEW — no existing target found)` instead of fabricating paths
(blind auditor independently confirmed: SOUND-but-BLOCKED, honest under a degenerate input).

## Findings

### F1 🔴 — MODIFIED/REMOVED-only change-folder is walled off by the freeze validator
- **Probe:** A (run1+run2) + B exec2, all independent.
- **Expected:** a human-approved change-folder whose delta is `## MODIFIED Requirements`
  (valid GIVEN/WHEN/THEN) is handled per writing-plans L184 ("map MODIFIED/REMOVED → change/
  removal tasks").
- **Actual:** `validate_spec_output.py` hard-requires a `## ADDED Requirements` header
  (`_check_added_requirements`, validate_spec_output.py:42,73-81) → a pure-MODIFIED folder
  returns exit 1 → the freeze gate (using-loom-code:80) HALTS before writing-plans is reached.
- **Evidence:** exec2 ran the validator: `INVALID … no delta contains a '## ADDED
  Requirements' header … EXIT 1`. Both Probe-A runs rejected fixture #4 on the validator's
  exit code, noting the contract gives "no contract-level rationale."
- **Root cause:** writing-plans L174 admits "validate_spec_output-clean (exit 0)" change-folders
  AND L184 promises MODIFIED/REMOVED handling — but the borrowed validator makes ADDED
  mandatory. The contract advertises a doorway the validator walls off.
- **Why static review missed it:** the contract reads internally consistent; only running a
  MODIFIED-only folder through the real validator exposes the cross-plugin contradiction.
- **Location:** writing-plans/SKILL.md:184 ↔ loom-spec/scripts/validate_spec_output.py:42,73-81.
- **Fix direction (cross-plugin decision):** EITHER (a) loosen `_check_added_requirements`
  to accept any of `## ADDED / ## MODIFIED / ## REMOVED Requirements` as a valid block, OR
  (b) narrow writing-plans L184 to state MODIFIED/REMOVED deltas only travel **alongside** an
  `## ADDED` block (a pure MODIFIED/REMOVED change-folder is rejected upstream by design).
  (b) is the cheap honest fix on this branch; (a) is a loom-spec scope change (roadmap).

### F2 🟡 — the brief entry has no structural gate (R6 asymmetry)
- **Probe:** A (run1+run2).
- **Expected:** symmetric rigor — if the change-folder entry is gated by presence+validator,
  the brief entry has a comparable check.
- **Actual:** freeze discrimination (using-loom-code:78) scopes its two checkable signals to
  "confirm the change-folder" only. The brief (entry a) is accepted on user declaration alone
  — any `.md` named as "the brief" passes; an empty/malformed brief would too. And classifying
  "this is a brief" by its shape is exactly the content-shape sniffing R6 forbids for change-folders.
- **Evidence:** both runs flagged #5 confidence Medium for this reason; run2: "the contract
  forced me to accept on the user's word with zero verification … the weakest checkpoint."
- **Location:** using-loom-code/SKILL.md:72-80.
- **Fix direction:** make the asymmetry **intentional and documented** — state that the brief is
  a human-authored, human-approved artifact (the approval IS the gate, per the upstream-human-gate
  doctrine), so it needs no machine validation, whereas the change-folder is machine-generated and
  therefore machine-validated. One or two sentences removes the "accidental inconsistency" reading.

### F9 🟡 — plan output-path contradiction
- **Probe:** C (cold-reader).
- **Actual:** the new section writes `docs/loom/plans/<date>-<change-id>.md` (writing-plans:182/186)
  while the Output contract / cross-skill table say `docs/loom/plans/<date>-<topic>.md` /
  `<topic>.md`. Two schemes for one output.
- **Location:** writing-plans/SKILL.md:182/186 vs the Output-contract + cross-skill table.
- **Fix direction:** unify on `<date>-<topic>.md` and state `<change-id>` fills the `<topic>` slot.

### F8 🟡 — jargon blockers for a first-time reader
- **Probe:** C. Undefined: **OpenSpec-pure** (no inline def), **OOUX object model** (acronym
  never expanded — a hard blocker when the section tells you to seed recon from it), bare
  **R5 / R6** (requirement IDs with no legend).
- **Location:** writing-plans/SKILL.md:174,182,178.
- **Fix direction:** gloss OOUX on first use ("OOUX = object/relationship model"), drop or
  define "OpenSpec-pure", and either spell the R5/R6 rules inline (they already are) or drop the
  bare IDs from prose the consumer reads.

### F6 🟡 — empty-recon has no sentinel; the parallelism oracle holds a guess
- **Probe:** B exec1 + blind auditor.
- **Actual:** plan-format requires `Module`/`Files touched`; the contract forbids guessing paths;
  when recon finds nothing, neither bridges. The agent invented `(NEW — no existing target found)`
  and reused one assumed path across both tasks — which `Files touched` also serves as the
  parallelism disjointness oracle (sound here only because both tasks are sequential).
- **Evidence:** auditor: "valid-but-degraded … the oracle is only sound by luck-of-being-sequential."
- **Location:** writing-plans/SKILL.md:182 ↔ references/plan-format.md (Files touched / Independent).
- **Fix direction:** bless a sentinel (`NEW: <proposed-path>` or `greenfield`) in plan-format and
  state such tasks default to `Independent: false` (the oracle can't be trusted on a proposed path).

### F3 / F5 / F7 / F10 🟢 — Low
- **F3:** the contract says "user declares which artifact" but never licenses file→brief /
  folder→change-folder inference (both Probe-A agents made it anyway). One clarifying line.
- **F5:** brief canonical path `docs/loom/specs/<topic>.md` is a hint, not enforced; an off-path
  brief still passes. (Pairs with F2.)
- **F7:** MODIFIED bullet references `### MODIFIED` (H3); the validator + OpenSpec convention use
  `## MODIFIED Requirements` (H2 block). Loose wording — align to `##`.
- **F10:** writing-plans says the change-folder must be "validate-clean" but doesn't say to run
  the validator (contrast: the freeze runs it). State that the freeze already gated it, or that
  writing-plans trusts the freeze's exit-0.

## Non-findings (harness artifacts, not skill defects)
- Blind auditor's "plan-document-reviewer PENDING → blocked" is correct against the contract but
  is an artifact of the **dogfood** deliberately scoping the executor to "produce + self-report"
  rather than run the full self-review loop. Not a skill defect.
- The "no host app → structural blocker" the executor raised is the **fixture's** degeneracy (a
  skills monorepo is not a note-taking app), not a contract defect — and the skill handled it
  honestly (raised the blocker, refused to fabricate).

## Raw outputs
Subagent transcripts under the run's task dir (`…/tasks/`): Probe A run1 `aff526ef…`, run2
`ac550d15…`; Probe B exec1 `aedf5dad…`, exec2 `aab82d17…`; Probe C `a2d6249e…`; blind auditor
`a48010b2…`. Fixtures: `/tmp/loom-dogfood-archive-note` (valid), `/tmp/dogfood-invalid-no-gwt`,
`/tmp/dogfood-invalid-no-spec`, `/tmp/loom-dogfood-modified-delta`, `/tmp/dogfood-plain-brief`.

## Verdict
The wiring's **designed** behaviors are sound and contract-faithful, and the round-3 recon fix
is validated. The dogfood surfaced **1 High** (F1, a real cross-plugin gate/contract contradiction)
and **4 Medium** prose/coherence gaps that build + two review rounds + the T6 one-shot dogfood all
missed — exactly the silent-defect class a blind behavioral dogfood exists to catch. No verdict
stamp is applied (floor-not-ceiling); findings are advisory for the main agent to triage.
