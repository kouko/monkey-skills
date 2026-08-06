# Brief: deterministic ledger writer + plan-tooling hardening (4 items)

Date: 2026-08-06
Status: FROZEN (user: 「可以直接做 1 2 4 5 嗎」 — the 0.62.0
retrospective's items 1/2/4/5; item 3 deliberately excluded, stays a
memory-tier lesson. Endpoint = PR per the session's standing
arc pattern, continuous)
Consumer: writing-plans → SDD; ships as loom-code 0.63.0 (repo-root
script changes ride the same PR; the script itself is host-neutral and
unversioned)

## Problem

Four evidence-backed friction points from the 0.62.0 arc:

1. Ledger flips are bare string edits: one arc produced a duplicate
   Status field AND a silent str.replace no-op whose commit message
   claimed a flip that never landed (erratum commit 6ca4ea41's body
   records it). State=LLM / projection=script is only half-mechanized —
   the WRITE side has no tool.
2. `plan_card.py` silently drops a `Steps:` declaration written inline
   ("Steps: a / b / c" — content on the same line): `_parse_steps`
   only recognizes a bare `Steps:` line, so the malformed form renders
   titleless steps at exit 0 (plan reviewer empirically confirmed).
   Fail-loud is the repo's contract; this is a silent degradation.
3. Every new arc re-derives the branch-start workaround: `git merge
   --ff-only origin/main` and `checkout -b <name> origin/main` both
   trip the push-guard's string matching; the working recipe
   (`git checkout -b <name> <main-tip-sha>`) lives only in session
   memory.
4. `Independent: true` + `Dependencies:` interplay is stated nowhere:
   a dispatcher reading plan-format's §`Files touched` and
   `Independent` alone could pair a task with the dependency it
   declares (the 0.62.0 plan reviewer flagged exactly this and
   recommended one sentence).

## Smallest End State

1. **`scripts/plan_card.py --set-status "T<N>=<status>"`** — the
   deterministic ledger writer. Grammar: status is exactly one of
   `pending` | `claimed(@<agent>)` | `done(<sha>)` | `blocked` (the
   schema's four kinds; parenthetical REQUIRED for claimed/done,
   FORBIDDEN for pending/blocked). Behavior: locate the task block by
   `## Task <N>` heading, rewrite its existing `- Status:` line in
   place wherever it sits in the block. Loud exit 1 on: task not
   found, malformed status, zero `- Status:` lines in the block, more
   than one `- Status:` line in the block (the 0.62.0 duplicate-field
   incident becomes detectable instead of survivable). Exit 0 prints
   the old→new line. Tests RED-first (happy path per kind; each error
   path; a Status line positioned after Gloss AND one directly after
   the heading both rewrite correctly; file byte-identical outside
   the one line).
2. **Loud Steps guard**: a `Steps:` line with content after the colon
   → exit 1 with a message naming the bare-line + indented-titles
   format. Test RED-first (the 0.62.0 plan's original inline form as
   fixture).
3. **Duty + docs wiring (prose)**: (a) SDD SKILL.md's Progress-ledger
   paragraph gains one sentence — perform ledger flips via
   `python3 scripts/plan_card.py --set-status` when the script is
   present, hand-edit only when absent (degradation stated);
   (b) plan-format.md gains one sentence in the Dependencies/
   Independent area: `Dependencies` is the ordering authority;
   `Independent: true` governs concurrency only among tasks at the
   same dependency level — never against a declared dependency;
   (c) plan-format.md's Steps schema notes the inline form is
   rejected loudly; (d) environment-gotchas.md gains the branch-start
   recipe line (new arc branch = `git checkout -b <name>
   <main-tip-sha>`; both `merge --ff-only origin/main` and
   `checkout -b <name> origin/main` trip the guard's string match).
   Ceiling check at plan time: SDD SKILL.md is pinned — if the
   sentence exceeds headroom, deliberate raise (changelog-noted).
4. loom-code → 0.63.0 (both manifests + CHANGELOG + shipping-version
   pin rewrite).
5. One haiku probe: given SDD's new ledger-flip sentence + a
   "T2 finished, flip it to done(abc1234)" scenario, does a cold
   reader use the command instead of hand-editing? Mini dogfood note
   in the same report file as the probe verdict.

## Out of scope

- Item 3 of the retrospective (exemption-premise verification) — one
  occurrence, memory-tier, not legislated.
- Any change to the Status schema's four kinds or to plan_card's
  rendering.
- Auto-flipping from git state (the writer takes explicit input; the
  orchestrator still decides).

## Decisions

- The writer validates but never invents: task number, status kind,
  and parenthetical all come from the caller verbatim; the script's
  value is the loud failure modes and the in-place single-line edit.
- Duplicate `- Status:` lines are an error, not a repair: the writer
  refuses and the caller fixes the plan (repair-in-tool would mask
  the authoring defect).
- Counting convention len(text.split()); verified at plan time: SDD
  SKILL.md current count vs its pin (task must measure), plan-format
  and environment-gotchas uncapped references.
