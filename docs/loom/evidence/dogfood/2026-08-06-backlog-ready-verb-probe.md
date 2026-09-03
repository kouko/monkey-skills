# Dogfood: backlog ready verb + close loop — three-leg haiku cold-read probe

Date: 2026-08-06
Branch: feat-backlog-ready-verb-and-close-loop (probes ran by-path
against the edited working tree at the T6 commit, 7970cc3a; leg (a)
consumed the REAL post-sweep `--ready` output)
Probe tier: haiku (weak-reader acceptance instrument), one fresh
context per leg, written exercises (no command execution)
Verdict: **3/3 CLEAN**

| Leg | Surface | Scenario | Verdict |
|---|---|---|---|
| a | `--ready` output + charter §Verbs | empty queue + seed-related OPEN entry | CLEAN |
| b | finishing Step 8 + Step 13 | branch ships an entry's subject | CLEAN |
| c | brainstorming Axis 0 | repo without a store; store + unrelated queue | CLEAN |

## Leg a — ready-output comprehension

Given the real output (0 committed / 69 open / 21 excluded) and a seed
idea touching TECH-SPEC.md: correctly read the missing COMMITTED-NEXT
section as an empty "now" queue; picked the related OPEN entry AND
articulated unprompted that the user's seed idea IS the entry's
`start:` trigger ("the user's seed idea IS that next touch — editing
stale descriptions in that file triggers the entry"); refused to let
the entry override the seed, citing the informs-never-hijacks
principle.

## Leg b — finishing close duty

Recited the full flip sequence in order from the shipped bullet: flip
`status:` → append the evidence line → `backlog_index.py --write` →
stage both "in the same close-out commit", anchored to Step 8 timing
(before the close-out commit). No-hit case: "skip silently (auditable
from the diff, like the memory-store bullet)" — no invented report
noise. Step 13: quoted the queue-tail line format ("backlog next:
<name>" / "backlog queue empty") and its producing command.

## Leg c — kickoff read moment

Storeless repo: "(no store → skip silently, N/A)" — no invented
check, nothing surfaced to the user. With a store: command runs
"before settling the arc's scope" (quoted). Unrelated COMMITTED-NEXT
item vs the user's export-feature seed: "the user's seed idea stays
the default subject" — quoted verbatim.

## Reading

The three failure directions the plan feared — inventing a backlog
check where no store exists, skipping the status flip at close-out,
and the queue hijacking the user's seed — all came back correctly
refused at the haiku tier, each answer anchored to a shipped sentence.
Leg (a) additionally demonstrated the start-condition semantics
working as designed on real store data: prose conditions are judgeable
by a weak reader at read time, supporting the brief's decision to
defer the machine-readable dependency field.
