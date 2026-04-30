# 4dx-d4-cadence (Multi-scope skill)

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Multi-scope coach for the D4 weekly Cadence of Accountability — the WIG Session — across all four roles the user might occupy: solo participant / team-leader facilitator / team-member before the session / team-member after.

## What this skill does

Detects scope (role + timing) from the user's query, then loads the matching protocol from `protocols/`. Same Account → Review → Plan grammar across all 4 modes; different agent voice per mode (peer-witness for solo, consultant-to-leader for facilitator, personal-coach for member). All 4 protocols share the same standards (`account-review-plan-agenda`, `commitment-shape`, `whirlwind-exclusion`, `sacred-cadence`).

## Background — why merged

Originally 5 skills (4 atomic D4 + 1 topic-router). The router was a thin disambiguation step over 4 nearly-symmetric protocols sharing 80%+ of their R/I/E/B content. Merging into one multi-file scope-flex skill: kept all execution detail, deduplicated standards, single audit footer, single trigger-list. SKILL.md orchestrator now does scope detection + protocol routing directly, without a separate router skill.

## Indexed protocols

| Mode | Load protocol | Agent voice |
|---|---|---|
| Solo, during session | [`protocols/solo-session.md`](protocols/solo-session.md) | peer-witness |
| Team-leader, during session | [`protocols/team-leader-session.md`](protocols/team-leader-session.md) | consultant-to-leader |
| Team-member, before session | [`protocols/member-prep.md`](protocols/member-prep.md) | personal coach to member |
| Team-member, after session | [`protocols/member-debrief.md`](protocols/member-debrief.md) | personal coach to member |

## When this skill activates

- **Solo** — "Run my weekly WIG Session", "I want a weekly review for my goal", "Help me stay on track each week"
- **Team-leader** — "Facilitate our team WIG meeting", "Walk me through how to lead this week's session", "A member missed a commitment — what do I do?"
- **Member-prep** — "Help me prepare my commitment for next WIG Session", "What should I commit to this week?"
- **Member-debrief** — "I missed my commitment last week — how do I show up at the session?", "I half-did it — kept or miss?"
- Multilingual EN / JP / zh-TW per mode (see SKILL.md for full trigger list)

If the user's query is ambiguous on (role, timing), the skill asks ONE Socratic disambiguation question covering all 4 modes, then routes.

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Cadence already broken (multiple skipped weeks) | `4dx-sustain-personal-momentum-rescue` (rescue precedes restart) |
| No WIG / lead measure / scoreboard yet | D1 / D2 / D3 first; D4 has nothing to operate on |
| Sprint review / PI planning / OKR check-in / 1-on-1 / status report | Out of 4DX — `using-four-dx-coach` |
| Daily stand-up / scrum daily | Wrong cadence (daily ≠ weekly), wrong format |
| Annual / quarterly retrospective | Wrong cadence scope |
| Member doesn't know team's WIG / lead measure | `4dx-d1-wig-formulation` first |
| 3+ misses in a row (member) | Commitment-design problem; redesign via member-prep mode (not debrief) |

## Source citation

The 4 Disciplines of Execution (2nd ed., 2021) — McChesney / Covey / Huling / Thele / Walker. Chapter 5 (Discipline 4: Create a Cadence of Accountability), Chapter 10 (Sustaining 4DX — Susan/Marcus dialogue), Chapter 15 (Applying Discipline 4).

Industry grounding consolidated in [`references/industry-grounding.md`](references/industry-grounding.md): Rogelberg, Lencioni, Reinertsen, Edmondson (×2), Pfeffer, Drucker, Cialdini, Eurich, Wiseman.

## See also

- [`SKILL.md`](SKILL.md) — orchestrator with full scope-detection logic + routing table + cross-mode boundary
- Plugin router [`using-four-dx-coach`](../using-four-dx-coach/) for cold-start / out-of-4DX queries
