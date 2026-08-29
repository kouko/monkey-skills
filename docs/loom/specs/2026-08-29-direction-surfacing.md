# direction surfacing — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-08-29
> **Author**: kouko + agent (Fable session; scope ratified in-conversation 2026-08-29 after a two-arm research round — repo contract recon + EN/JA external prior-art)

## Design-side on-ramp

not fired — contract-text increment on existing skills; no product-shaped, UI, or spec-station surface.

## Queue relation

unqueued — user-directed mechanism revision arising from this session's direction-surfacing evaluation; no backlog entry covers it (the batch-3 "summary-surface visibility" candidate remains deliberately unfiled and is a different, wider cut).

## Problem

When a long arc reaches a decision point, I want the remote goal (PURPOSE / governing map Destination) and the near goal (this arc's plan Goal) in front of me at that moment, so I can decide without reconstructing direction from memory. Today direction is written down and partially gated (bet promotion requires a `serves:` link; map tickets must serve their Destination) but is only ever *displayed* at rare gate moments: PURPOSE.md prints only during bet promotion, and nothing re-surfaces direction when an agent stops mid-arc to ask the user a question.

## Users

- kouko, mid-arc, interrupted by an `AskUserQuestion` or a complex-fork brief — needs the far/near goals restated in the question itself, not in a file they must go open.
- Cold agent sessions (any tier, Claude Code and Codex mirror) — each session starts with no memory of direction; a kickoff banner is re-read fresh every time, so agent-side habituation does not apply.
- Adopting repos post-relocation — the same skill text must work there: rules may reference loom-scaffolded store paths (`docs/loom/PURPOSE.md`, `docs/loom/maps/`) but nothing monkey-skills-specific.

## Smallest End State

Three prose additions ship in one loom-code release; no new scripts, no new checkers, no state kept anywhere.

- BI-1 — **Kickoff direction banner**: at brainstorming Axis 0, alongside the existing backlog-ready and live-map checks, the session prints one line quoting `docs/loom/PURPOSE.md`'s `**Why:**` line verbatim, plus one line per live map pairing map-id with its Destination first line (the liveness contract already supplies exactly this pair). PURPOSE.md absent → one loud line `direction banner: PURPOSE.md absent`, never a silent skip. Always-on, single-line-per-item, no change-detection state.
- BI-2 — **Decision-point direction anchor**: the existing state-and-stakes anchor duty on mid-arc user-facing questions (SDD gate ③ asks, kickoff-briefing escalations, complex-fork briefs) is extended: the anchor also names the remote goal (PURPOSE Why, or the governing map's Destination when the arc carries a `Map part:` key), the near goal (the plan's `Goal:` line), and this decision's relation to them, in one sentence. Discovery-phase (brainstorming) questions are exempt — direction is itself the topic there.
- BI-3 — **Goal-line direction relation**: the plan's `Goal:` line, written once at plan birth and frozen, ends with a direction-relation clause — `— serves <PURPOSE | map <map-id>>: <short relation>` or the honest escape `— off-direction: <reason>`. The progress card prints `Goal:` verbatim already, so every card inherits remote-goal visibility with zero script or card changes.

Success = a cold-reader dogfood on the revised text produces, on one real case: the banner at kickoff, an anchored question at a decision point, and a plan Goal line carrying the relation clause. `loom-workflow` is untouched; loom-code bumps once (both manifests + root README row).

## Current State Evidence

- **Forward**: kickoff surfacing is owned solely by `loom-code/skills/brainstorming/SKILL.md` Axis 0 — "**Backlog ready check**" (line 63) and "**Live-map check**" (line 73); neither prints PURPOSE content. PURPOSE.md is printed only at bet promotion (`loom-code/skills/finishing-a-development-branch/SKILL.md` §Purpose-linked betting).
- **Reverse**: the anchor duty exists in three places — `loom-code/skills/subagent-driven-development/SKILL.md:65` ("Keep the state-and-stakes anchor in the rendered question"), its validity condition `loom-code/skills/subagent-driven-development/references/conditional-operations.md:30`, and brainstorming's own copy `loom-code/skills/brainstorming/SKILL.md:49`; `loom-code/hooks/family-reception.md:38` §Brief before a complex fork owns the fork-brief trigger. Confirmed by reading all four — SDD delegates rendering to conditional-operations; brainstorming does not.
- **Error**: `check_north_star_link.py` treats PURPOSE.md as opaque prose and only evaluates it at bet promotion (exit 2 on absence/unanswered); no other consumer parses it — BI-1 must define absence behavior itself (the loud N/A line above).
- **Data**: the `**Why:**` bold prefix is a stable anchor in both `loom-code/scripts/templates/PURPOSE.md` and the live `docs/loom/PURPOSE.md`; the map-id + Destination-first-line pair is already the return shape of `loom-workflow/skills/decision-map/SKILL.md:145` §Liveness assessment — BI-1 needs no new parsing.
- **Boundary**: `Goal:` admits no nested body but carries no length ceiling (`loom-code/skills/writing-plans/references/plan-format.md:193`), so BI-3's appended clause stays legal; the Goal template line is duplicated at `plan-format.md:33` and `writing-plans/SKILL.md:172` — both copies must change together. `check_queue_relation.py:43-51` reads only its own field's first non-empty line — untouched by every BI.

## Alternatives Considered

- **Per-turn injection** (mission text on every request, like a hook) — rejected: token cost compounds linearly and long-context dilution erodes it anyway (AWS agentic-lens AGENTCOST02-BP02; mindstudio token-reduction write-up). Event-driven surfacing at kickoff + decision points matches the aviation-briefing "recap at critical moments" pattern (flightsafety.org "Rethinking the Briefing").
- **Change-aware banner** (highlight only when PURPOSE/Destination changed) — deferred, not chosen: habituation research (banner blindness, Frontiers in Psychology 2022) predicts a static always-on banner gets filtered by the *human*; but the mitigation needs "what was shown last" state, violating this arc's no-state constraint, and the agent side re-reads cold each session regardless. **Conditional reversal**: if kouko reports the banner has become noise, upgrade BI-1 to change-aware then.
- **Mandatory work-item→objective linkage** (every backlog entry / brief forced into a map) — rejected on evidence: rigid OKR cascading is a documented driver of alignment theater (Goodhart; EN/JA sources agree, 形骸化). BI-3 binds the *plan* (agent-written, with an honest off-direction escape), not human-filed work items.

## Decision

Build exactly BI-1..BI-3 as prose-only additions to loom-code skill/hook text, shipping in one version bump. Do NOT build: new scripts or checkers, plan_card.py changes, any cross-file parser for PURPOSE.md, change-detection state, or mandatory direction fields on backlog entries/briefs. The earlier idea of an optional direction line under the brief's `Queue relation` field is superseded by BI-3 (the Goal line covers unqueued arcs too, and rides existing machinery).

## Out of Scope

- Change-aware banner highlighting (reversal condition recorded above).
- Per-turn injection of direction text.
- Mandatory direction linkage on backlog entries or briefs; any new checker.
- Progress-card (`plan_card.py`) or any script changes.
- The batch-3 "summary-surface visibility" candidate (cross-store overview) — wider cut, stays unfiled with its re-trigger.
- Codex-side behavior differences (the edited files ship to both hosts via the existing mirror; no host-specific text).

## What Becomes Obsolete

Nothing is deleted; the additions are three sentences-scale duties on existing contract surfaces. The un-shipped "Queue relation optional direction line" concept is retired before birth (superseded by BI-3). Honest additive-YAGNI check: each BI traces to a stated user pain from this session (banner → "隨時清楚方向"; anchor → "決策時要被提醒遠程＋近程"; Goal clause → "進度卡也想看到方向" answered with the zero-cost fold-in).

## Open Questions

N/A — no unresolved question: the always-on vs change-aware fork and the mandatory-vs-optional linkage fork were both closed by the research round (see Alternatives Considered).

## Diagrams

Declared not needed — three independent one-sentence duties on known surfaces; the Evidence section's file:line anchors carry the structure.
