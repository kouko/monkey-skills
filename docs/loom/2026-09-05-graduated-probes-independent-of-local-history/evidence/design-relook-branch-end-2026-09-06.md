# Design re-look — branch-end, third round (2026-09-06)

Dispatched under fix-rounds.md "Third round: stop fixing, look at the
design" for open finding branch-end-01 (rev-be-codex-47d0, rounds 3–4):
the graduation sentence in build/SKILL.md §6.5 is a blocking rule in
prose, and PRINCIPLES.md:17 forbids prose-only gates. Agent
`design-relook-be-opus` (opus, fresh context). Verbatim conclusion:

decision: c — accept as-is; the dismissal belongs to the raising reviewer.

- PRINCIPLES.md carries no definition of "prose-only"; the repo's own
  definition is mechanisms.yaml `counting:` (prose-gate = a `<!-- gate: <id> -->`
  marked paragraph; an unmarked paragraph is not a gate and may not be used
  as one) and CLAUDE.md "Quality Gates". "Prose-only" = unmarked,
  unregistered, no machine recomputing its fact. A marked, registered,
  budget-declared paragraph is the admitted class, not the forbidden one.
- The reading "a blocking rule must live in the checker, full stop" would
  condemn the ten registered prose gates on main, including two in the same
  file: build.no-dispatch-without-a-record (SKILL.md:180-201) and
  build.after-task-review-before-next-task (:242-252), both at
  mechanisms.yaml:269-274.
- The fact the sentence turns on — red vs green — is recomputed by
  rehearse_probes.py (non-zero exit on a clone-red). What is unenforced is
  the operator's obedience, exactly as for the two gates above. The sentence
  names no push rule and over-promises nothing.
- Moving the block into the checker is barred by the user's decision at ①
  (intent Constraints and Out of scope). A reword would soften a rule the
  intent deliberately states as blocking station text.
- The fix exceeds the class floor: budget exception declared
  (CHANGELOG [1.6.1]; written as [1.5.2] before the rebase onto 1.6.0), cold-read eval plus an executable twin
  (test_build_station_text.py) recomputing marker presence and scope.
- The disagreement is definitional, not a defect; no smaller correct shape
  keeps the intent's constraint. Per fix-rounds.md the dismissal is
  recorded only by the raising reviewing role, never by an implementer.

replacement: none.
