# Brief — Measure the declared-vs-actual `Files touched` check

- **Date**: 2026-08-01
- **Branch**: `docs-declared-vs-actual-measurement` (base `f22e9aa1`)
- **Arc position**: P1 of HANDOFF-2026-08-01-013000 — agreed in the prior
  session; the user explicitly approved skipping a research round
  ("skip a research round before the next arc; go straight to measuring
  the declared-vs-actual check").
- **Design-side on-ramp**: N/A — internal gate machinery, not
  product-shaped; Axis 0 negative guard applies.

## Problem

A plan task's `Files touched` field is the **disjointness oracle** that
authorizes parallel dispatch (`plan-format.md:76`), and the one measured
plan shows it wrong in the dangerous direction one time in three: 3 of 7
tasks in `docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md`
under-declared, each miss found by a different accident (an implementer
volunteering, a hook blocking, a manual diff). The distilled evidence is
`docs/loom/memory/files-touched-misses-machinery-coupled-files.md`: the
field reliably names what a task is *about* and misses what it is
mechanically *coupled to* (guard tests pinning altered state, an SSOT
behind a functional copy, a hook-enforced manifest mirror).

A mechanical comparison — the files actually in the task's commit versus
the declared list — needs no judgement and would have caught all three.
Today that comparison exists only as agent-executed prose scoped to
`Review-weight: mechanical` tasks (SDD `SKILL.md:86`), and this repo's
record says agent-executed prose fails silently.

**The job of this arc**: measure the check on an independent fixture with
a frozen answer key, and produce a go/no-go recommendation with numbers —
NOT ship the institutional wiring. The prior arc's BACKLOG entry
("`Reuse-adequacy` got the gate it had been missing (SHIPPED)") records
why: the seven known instances carry a selection effect (they are on the
list because they were found), so retro-fitting on them alone proves
nothing about the rule's behaviour on shapes the corpus lacks.

## Users

- **SDD orchestrators** (any tier) consuming plans in this repo — the
  check's verdict would gate/warn after each task commit.
- **Whole-branch reviewers and `finishing-a-development-branch`** — a
  batch mode over every `done(<sha>)` entry.
- Downstream: every parallel-dispatch decision that trusts declared
  disjointness (`dispatching-parallel-agents` `SKILL.md:127`).

## Smallest End State

1. A comparator script (working name `loom-code/scripts/check_files_touched.py`):
   parses a real plan's per-task `Files touched` + `Status: done(<sha>)`,
   runs `git show --name-only --format= <sha>`, and emits a per-task
   verdict: `OK` / `UNDER` (in diff, not declared) / `OVER` (declared,
   not in diff) / `NO_JOIN` (no `done(<sha>)` to compare against).
   Built TDD-first; the fixture cells below ARE its test corpus.
2. A measurement fixture: a sandbox git repo constructed by the tests
   (real commits, real `git show` output — never hand-typed diffs), plus
   plan documents in both field forms (bolded schema form and the plain
   form real plans use, cf. `check_scenario_coverage.py:64-68`).
3. **Frozen answer key**: every cell's expected verdict is written into
   the audit document and the test file BEFORE the comparator is
   implemented (same discipline as the 8-cell Reuse-adequacy
   measurement).
4. A measurement report `docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md`:
   per-rule-variant confusion table on the independent cells, the
   retro-fit on the three known instances reported separately and
   labeled selection-biased, and a ship/no-ship recommendation
   (including WHERE it should sit — SDD per-task step vs finishing-branch
   batch — argued from the numbers, decided by the user next arc).

### Rule variants measured (all three run over the same cells)

| variant | flags | rationale to test |
|---|---|---|
| R1 strict | any set difference, both directions | simplest possible rule |
| R2 under-only | diff ⊄ declared only | the dangerous direction is under-declaration; OVER may be legitimate drift during a fix round |
| R3 = R2 + standing excludes | R2, minus a fixed exclude list (the plan file itself, `__pycache__/`) | measures whether excludes are even needed given the repo's observed commit discipline |

### Fixture cells (shapes chosen to break the selection effect)

Independent cells — constructed, not copied from the known instances;
answer key frozen per cell × per rule variant:

1. clean exact match → OK everywhere
2. under-declaration, guard-test shape (a test pinning altered state)
3. under-declaration, SSOT-functional-copy shape (canonical declared, regenerated copy not)
4. under-declaration, manifest-mirror shape
5. **over-declaration** (declared file never touched) — a shape absent
   from the known corpus
6. `NEW: <path>` proposed-new token (`plan-format.md:79`) — parser must
   match the created path
7. **missing `done(<sha>)`** → must report `NO_JOIN` loudly; a plan whose
   every task lacks the ledger must NEVER produce an all-clear (the
   citation-checker empty-pass lesson, and
   `docs/loom/memory/a-silently-skipped-edit-reports-as-a-completed-one.md`)
8. rename in the commit (`git show` `old => new` accounting)
9. field-form variance: bolded `**Files touched**:` vs plain
   `- Files touched:` in the same corpus
10. path normalization (leading `./`, trailing spaces, backticked vs bare)

Retro-fit cells (reported separately, never in the headline number): the
three real commits from the reuse-adequacy branch (T3 `c82c93cd`-family,
T4 `0c03c0e8`, T6 manifest commit) replayed against their ORIGINAL
(pre-correction) declarations.

## Current State Evidence

- **Forward** (producer): `loom-code/skills/writing-plans/references/plan-format.md:49`
  — `- **Files touched**: <comma-separated paths the implementer will
  Write / Edit>`; `:76` names it the disjointness oracle; `:79` defines
  the `NEW: <proposed-path>` token (the one non-path token a parser must
  tolerate). `loom-code/skills/writing-plans/SKILL.md:145` writes the
  field UNBOLDED — real plans use the plain form
  (`docs/plans/2026-06-05-daily-brief-continuity-hardening.md:39`).
- **Reverse** (consumers): SDD `SKILL.md:79` (fan-out on disjoint sets),
  `:84-86` (the prose subset rule, mechanical-path only), `:92`
  (fail-closed prose substitution reads "any file that actually appears
  in the task's diff" — the only place actual-diff language exists
  today); router `using-loom-code/SKILL.md:64` (auto-suggest);
  `dispatching-parallel-agents/SKILL.md:123,127`; plan-document-reviewer
  Checks 13–16 (`plan-document-reviewer-prompt.md:45-48`) — **all four
  compare declarations against other declarations, none against
  reality**. SSOT direction verified: `loom-code/scripts/distribute.py:54-99`
  ROUTE regenerates loom-code copies FROM `domain-teams/skills/code-team/`
  canonical (`:24-26` mandates same-commit regeneration).
- **Error** (today's failure mode): no script, hook, test, or checklist
  compares declared vs actual (`grep -rn "show --stat"` hits only prose;
  `.claude/settings.json:5-21` registers four hooks, none reads a plan;
  `spec-consistency.md` CHK-SPEC-008 is presence-of-sibling-field only).
  Near-misses: SDD `SKILL.md:86`;
  `loom-code/scripts/test_review_weight_prose.py:160-164` (a test that
  names under-declaration as the anticipated attack);
  `loom-code/scripts/check_version_bump.py:60` `changed_paths()` (an
  existing diff harness to copy).
- **Data** (join key): task→commit join is the plan ledger
  `Status: done(<sha>)` (`plan-format.md:106`), an OPTIONAL field
  (`:68-71`, default omitted); commit messages carry NO task id
  (`commit-convention.md:183`; verified empirically — zero subject-initial
  "Task N" matches repo-wide). One commit per task (SDD `SKILL.md:79`,
  `:117`).
- **Boundary** (noise profile): verified on the 12 commits of the
  reuse-adequacy branch — task commits do NOT contain the plan file
  (ledger updates land as separate `docs(loom)` commits), and version
  bumps land in a separate final commit (`commit-convention.md:78-79`),
  so neither is task-commit noise. Regenerated functional copies and
  codex-mirror manifests land in the SAME commit by mandate
  (`distribute.py:24-26`, hook `.claude/settings.json:13`) — these are
  the under-declaration TARGET, never an exclude.

### Evidence paths appendix

- `docs/loom/memory/files-touched-misses-machinery-coupled-files.md` — the three instances + the proposed check verbatim
- `docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md:205-217, 256-269` — the durable in-plan record
- `docs/loom/BACKLOG.md` § "`Reuse-adequacy` got the gate it had been missing (SHIPPED)" — the seven-vs-zero caveat and this arc's mandate
- `loom-code/scripts/check_scenario_coverage.py:62-68,125,141,169` — the parser idioms to reuse (bold-optional field regex, section boundary, join-key collector, CLI shape)

## Decision

Build the measurement, not the institution. TDD-first comparator +
constructed fixture corpus with a frozen answer key + audit report with
a ship/no-ship recommendation. Use `git show --name-only --format=` as
the mechanical form (the memory file's `--stat` phrasing is human
shorthand; `--name-only` is the stable machine surface — rename handling
measured in cell 8; amended at kickoff to add `--no-renames` so a rename
contributes both paths — see the plan's Notes, Kickoff decision). The comparator fails LOUD on empty parses (0 tasks,
0 join keys) — "nothing to check" must never render as all-clear.

We will NOT: wire the check into SDD/reviewer prompts/hooks/CI, change
`plan-format.md`, make `done(<sha>)` mandatory, or touch the three
residual over-fires (accepted debt). Those are ship-arc decisions taken
on this arc's numbers.

## Alternatives Considered

Research round: skipped by explicit user approval (prior session
produced seven fresh classified instances; an industry cross-check —
harness/loop/graph practitioner synthesis, 2026-07-25 — independently
endorsed deterministic-checks-first and added no design delta).

- **Keep the prose rule only** (SDD `SKILL.md:86`): rejected — scoped to
  mechanical tasks only, and all three real instances were caught by
  accident, not by the prose rule; the repo's own record
  (`doc-string-tests-pass-while-weak-readers-misread.md`) says prose
  duties fail silently on weak tiers.
- **Make it an LLM reviewer check** (a Check 18): rejected — the
  comparison is set arithmetic with zero judgement;
  `feedback_weak_model_caveats_need_verifiable_action_not_judgment`
  says exactly this class belongs in a mechanical gate, not prose.
- **Commit-time hook** (PreToolUse on `git commit`): deferred, not
  rejected — a placement option for the ship arc; measured numbers on
  noise decide whether a blocking position is tolerable.

## What Becomes Obsolete

Nothing is removed in THIS arc (measurement-only — consciously accepted
additive change). Flagged for the ship arc: SDD `SKILL.md:86`'s prose
subset rule and the manual-diff advice in
`files-touched-misses-machinery-coupled-files.md` §How-to-apply are both
superseded the day the script is wired in; the ship arc must absorb or
delete them (cross-file §-ref debt otherwise).

## Addendum — repo-wide dogfood extension (2026-08-01, user-approved)

After the five planned tasks completed (R3: 4 hits / 0 miss / 0 false
alarms), the user asked for dogfooding on more test data. A sweep of all
170 real plans in the repo found: (a) the loud-empty contract held on
all 165 exit-2 plans (164 ledger-less, plus one whose ledger the parser
could not read — sweep §5c); (b) two parser blind spots the 10-cell corpus
could not see, both failing toward false alarms — continuation-line
(wrapped) `Files touched` values (real shape:
`docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md:48-49`)
whose continuation paths are invisible to the parser and so produce
false UNDER verdicts, and a trailing parenthetical annotation after the
final path token (real shape:
`docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md:24`) that
contaminates the token. The user approved: fix both parser gaps (TDD),
re-run the sweep, and record the results — the true wild
under-declaration rate is the load-bearing evidence for the next arc's
wire-in decision, and the pre-fix numbers are contaminated. The
weak-model consumption probe is explicitly deferred to the ship arc
(the mechanism itself is a deterministic script; tier only matters at
the consumption seam, which does not exist until wiring is decided).

## Open Questions

1. `done(<sha>)` is optional — on plans without a ledger the check is
   structurally inert (`NO_JOIN` everywhere). Whether to make the ledger
   mandatory when `Independent: true` is a ship-arc question; this arc
   only quantifies how loud the inert case reports.
2. Block vs warn at ship time: the asymmetry doctrine (a false alarm is
   loud and cheap; the hole is silent) leans warn-then-human, but the
   decision belongs to the user with the noise numbers in hand.
3. Multi-commit tasks (a task legitimately amended post-PASS): out of
   the observed convention, one commit per task held on the measured
   branch; the comparator takes one sha per task and the report notes
   the limitation.
