# Brief: Stage-update owner for review rounds + blocked:user-decision enum value

Date: 2026-08-07
Endpoint named: yes → continuous (user: 「先做 PR A 吧」— PR is the endpoint; scope fixed by the user-approved evaluation table in-session)

## Problem

The plan's `Stage:` header is the progress surface's coarse state, and the
schema comment says "orchestrator updates it at each transition"
(`loom-code/skills/writing-plans/SKILL.md:147-148`) — but the skill that
drives review rounds carries no such duty: `requesting-code-review/SKILL.md`
never mentions updating Stage (its only "Stage" hit is the router label,
line 202). The transition into `review:round-2..N` therefore has no owner in
the skill actually running when it happens. Live defect: kumiko-zaiku-app-icons
plan sat at `Stage: review:round-1` through three real review rounds
(device on loom-code 0.64.0 — not version lag).

Second gap, same surface: the enum (`planning | sdd:wave-N | review:round-N |
finishing`) has no value for "halted awaiting a user decision", so a branch
blocked on the user is indistinguishable from one mid-flight. Live defect:
finacial-analytics-r2's sparse-Q4 OPEN finding waited 7+ hours invisibly —
the plan recorded the deferral, but no surface carried the state.

## Users

kouko + any future orchestrator session (any repo on loom-code ≥0.60.0
progress cards) reading plan headers, progress cards, or resuming after
interruption.

## Smallest End State

1. `requesting-code-review/SKILL.md` gains ONE self-contained duty sentence:
   at the start of each whole-branch review round, the orchestrator flips the
   plan's `Stage:` to `review:round-N` (hand-edit; `plan_card.py` treats Stage
   as free text — scripts/plan_card.py:318-320 — no script change needed).
   Own sentence, not spliced into an existing pinned sentence
   (docs/loom/memory/splicing-into-a-pinned-sentence-creates-false-readings.md).
   Budget: rcr word cap 3900, current 3832 → 68-word margin.
2. `writing-plans/SKILL.md:147` enum line gains `| blocked:user-decision`
   (+2 words against an 8-word margin: cap 4047, current 4039).
3. `writing-plans/references/plan-format.md:36` enum copy gains the same value
   PLUS the when-to-set duty text (set when the arc halts awaiting a user
   decision; flip back to the resumed stage when the user rules). plan-format.md
   has pin tests but no word cap — duty prose lands here, not in SKILL.md.
4. Pin test `loom-code/scripts/test_plan_format_progress_fields.py:49-53`
   (STAGE_ENUM_LINE, verbatim) updated RED-first alongside.
5. Rider (mechanical criterion, no user ask): the same one-sentence round-flip
   duty in `requesting-docs-review/SKILL.md` IF its word cap allows (docs arm
   runs rounds too; current 4428 words, cap to be checked at plan time).
   Cap blown → skip the rider, note it in the PR body.
6. `loom-code` version bump + CHANGELOG entry (skill-content PR ⇒ bump is
   mandatory; marketplace sync per repo convention).

## Current State Evidence

- Forward: `loom-code/skills/writing-plans/SKILL.md:147-148` — enum definition
  + "orchestrator updates it at each transition" comment (the only statement
  of the duty; lives where review-running orchestrators never re-read).
- Reverse: enum copies swept full-plugin (grep `review:round|sdd:wave`):
  exactly three statements — `writing-plans/SKILL.md:147`,
  `writing-plans/references/plan-format.md:36`,
  `scripts/test_plan_format_progress_fields.py:50` (pin). CHANGELOG mentions
  are historical, not contract. No other skill states the enum.
- Error: `scripts/plan_card.py:318-320` — Stage line must exist, value is
  free text (no enum validation); adding a value breaks no parser.
- Data: kumiko plan `Stage: review:round-1` unchanged across 3 rounds
  (their docs/loom/plans/2026-08-06-marukiwa-third-role.md:5);
  finacial-analytics plan OPEN finding lines 406-461 awaiting user, no
  visible state.
- Boundary: `requesting-code-review/SKILL.md` — zero Stage duty (line 202
  router label only); `subagent-driven-development/SKILL.md:112` owns per-task
  `Status` flips only; `finishing-a-development-branch/SKILL.md:102` renders
  the card on entry only. Word caps: rcr 3900/3832, wp 4047/4039,
  plan-format.md uncapped.

## Alternatives Considered

Explored in-session (evaluation table, user-approved): script-enforced Stage
validation in plan_card.py (rejected: heavier, Stage free-text is deliberate),
duty in SDD (rejected: SDD exits before review rounds), surfacing layer in
briefing-toolkit (deferred as separate arc — the #3-surface half + open-PR
scan). Narrow problem space; no external research needed (internal contract
wording, no tech-stack choice).

## Decision

Add the round-flip duty sentence to requesting-code-review (owner where the
transition happens), extend the Stage enum with `blocked:user-decision` in
both prose copies + the pin test, put the when-to-set prose in plan-format.md
(the uncapped schema SSOT), take the requesting-docs-review rider only if its
cap allows. Bump + CHANGELOG. Nothing else.

## Out of Scope

- Proactive surfacing of blocked:user-decision (briefing-toolkit / daily-brief
  integration) — separate backlog arc, per the evaluation split.
- Open-PR staleness scanning (komado #43 class) — same separate arc.
- Cross-repo memory propagation (reviewer-agent pattern promotion) — separate
  backlog decision.
- plan_card.py enum validation or `--set-stage` flag — Stage stays free text.
- Backlog items whose start conditions this PR lights
  (2026-07-06-anti-copy-acceptance-greps…: "next touch of writing-plans
  SKILL.md"; 2026-07-10-change-binding-chain…: "next loom-code touch") —
  surfaced here, not folded in; they remain OPEN.

## Open Questions

None blocking. Rider (item 5) resolves mechanically at plan time by cap check.
