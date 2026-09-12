# <title>
originator: <who>            # a person's name, "maintenance-loop", or map:<id>
kind: product | engineering
needs-design: yes | no — <reason>
map: <map-id>                # optional
evidence: [<paths>]          # optional; write-spec/review must read it
status: open                 # open | confirmed <date> | closed <date> — PR #<N> | withdrawn — <reason>; absent = open
publication: automatic — authorized <YYYY-MM-DD> by <name> # optional; only after the user explicitly authorizes automatic publication
lane: express | gate-only    # optional; absent = repo default (KICKOFF-DEFAULTS.md default-lane); a bare name is never legal — declared form: `lane: <name> — declared <YYYY-MM-DD> by <name>`; switch form: `lane: <name> — switched <YYYY-MM-DD> by <name>, from <wave <n>|round <n>>`; last line wins; only the user writes it

## Problem
<present pain, who it affects, and consequence; no diagnosis or fix. product: no file paths, function/class identifiers, or script filenames>

## Proposed outcome
<wanted capability or state; no scenario, UI reaction, state transition, or implementation>

## Acceptance
1. <observable delivery outcomes, not scenarios or implementation; each line externally provable>

## Constraints
- <already-fixed boundaries, not agent preferences>

## Value case
<optional; product beneficiary, urgency, and GO/NO-GO; omit obvious engineering value>

## Out of scope
- <excluded capabilities, actors, systems, or data; not deferred implementation tasks>

## Open questions
- <unresolved outcome or scope choice; delegate spec and engineering questions> # write `- none` when there are none
