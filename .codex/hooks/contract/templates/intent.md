# <title>
originator: <who>            # a person's name, "maintenance-loop", or map:<id>
kind: product | engineering
needs-design: yes | no — <reason>
map: <map-id>                # optional
evidence: [<paths>]          # optional; write-spec/review must read it
status: open                 # open | confirmed <date> | closed <date> — PR #<N> | withdrawn — <reason>; absent = open

## Problem
<the problem and who it affects, in plain language. product: no file paths, function/class identifiers, or script filenames>

## Proposed outcome
<direction and shape of the solution>

## Acceptance
1. <what I can do once this is done…; each line provable by a blind run>

## Constraints
- <…>

## Value case
<optional; product's GO/NO-GO and its reasoning>

## Out of scope
- <…>

## Open questions
- <…>                     # write `- none` when there are none: this section is required, and an empty one is blocked by intent.schema
