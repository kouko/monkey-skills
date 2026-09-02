# Attack catalogue — the six classes an adversarial auditor works

Serves the review station's **adversarial** action on a skill or gate
artifact (`adversarial.md`): the change under review touches an
exemption, a gate or a self-check, and the six classes below are how
that touch gets probed rather than merely read.

Each class below is a question the auditor answers about the branch, plus
the evidence rule a `reproduced` verdict must meet. The rule is the same
in every class: **a `reproduced` verdict requires a command that ran and
its output in front of the auditor — never a reading of the code, the
prose, or the diff.** Reading a check and concluding "this would refuse
it" is not evidence; running the check against a crafted input and
watching it refuse (or not) is.

### Class: forge an artifact the gate trusts

- Question: can the auditor hand-craft (or edit) the artifact a gate
  reads — a review.json, a dispatch entry, a probe record — so the gate
  accepts it without the work the artifact claims having happened?
- Evidence: a `reproduced` verdict requires a command that ran against
  the forged artifact and the gate's actual accept/refuse output — never
  a reading of the gate's parser code to infer what it would do.

### Class: bypass a gate by editing its input

- Question: can the auditor change the input a gate consumes (a config
  file, a plan, a scope list) so the gate's own logic is untouched but
  now waves through what it was meant to catch?
- Evidence: a `reproduced` verdict requires a command that ran the gate
  against the edited input and captured its exit code and stderr — never
  a reading of the input format to infer the gate would still refuse it.

### Class: replay a stale artifact

- Question: can the auditor resubmit an artifact — a review verdict, a
  probe, a passing test run — that was genuine once but no longer
  reflects the current state (a later commit, a rotated key, a closed
  finding), and have the gate accept it as current?
- Evidence: a `reproduced` verdict requires a command that ran the gate
  against the stale artifact after the state moved on, with its output
  showing acceptance or refusal — never a reading of a freshness check's
  code to infer it would catch the replay.

### Class: cross a trust boundary (repo / worktree / process)

- Question: can an action taken in one repo, worktree, or process reach
  across into another and take effect there — a guard evaluated in the
  wrong cwd, a file written to a directory a different checkout reads,
  a subprocess inheriting privilege it shouldn't?
- Evidence: a `reproduced` verdict requires a command run from the other
  side of the boundary (the other worktree, the other cwd, the other
  process) with its output showing the crossing — never a reading of the
  boundary-checking code to infer it would hold.

### Class: self-exempt via a prose condition

- Question: does a prose condition — "skip if trivial", "the plan says
  Safety-bearing: no", "proceed if the diff is one line" — let the actor
  under audit grant itself an exemption that a machine-checkable gate
  would have refused?
- Evidence: a `reproduced` verdict requires a command showing the prose
  path was actually taken (the exemption invoked, the gate not run) —
  never a reading of the prose to infer it could be read that way.

### Class: race a concurrent writer

- Question: can two writers (two agents, two branches, two processes)
  interleave their reads and writes to a shared file — a ledger, a store,
  a lock — so one writer's update is lost or a partial state is read as
  final?
- Evidence: a `reproduced` verdict requires a command that ran two
  writers concurrently (or interleaved) against the shared file and
  captured the corrupted or lost-update output — never a reading of the
  locking code to infer a race is impossible.

## Verdict vocabulary

- `reproduced` — the auditor ran a command that demonstrates the attack
  actually succeeding, and is quoting that command's actual output. A
  gate's refusal is never `reproduced` — that outcome is `held`. This is
  the only verdict that counts as a hole found.
- `held` — the auditor tried to reproduce the attack on a given date and
  the gate refused it; recorded as a dated record of that one attempt,
  never as coverage. A `held` entry says "this specific probe failed to
  reproduce on this date" — it does not say the class is closed for good,
  and a later change to the gate can silently invalidate it.
- `not-applicable` — the class does not apply to this repo or this gate
  (the mechanism the class targets does not exist here), with the reason
  stated inline.

## Repo store

Each adopting repo keeps its own dated instance file at
`docs/loom/ATTACK-CATALOGUE.md` — a loom-scaffolded store path (schema,
not a citation of this repository's development records) recording that
repo's guarded paths, its `reproduced` / `held` / `not-applicable`
instances against the six classes above, and the prose temptations its
own cold reader draws from.
