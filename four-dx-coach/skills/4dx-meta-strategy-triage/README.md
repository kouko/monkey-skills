# 4dx-meta-strategy-triage (Multi-scope skill)

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Multi-scope gate for "Should X use 4DX?" — decides whether 4 Disciplines of Execution even fits the user's situation BEFORE installing D1-D4. Detects scope (solo individual vs team-leader) and loads the matching triage protocol.

## What this skill does

Detects scope (solo vs team-leader) from the user's query, then loads the matching protocol from `protocols/`. Runs a Socratic triage that ends in a single discrete verdict from the rubric — either **APPLICABLE / TEAM-APPLICABLE** (proceed to D1) or one of several redirect verdicts that route to a fitter methodology. Refusing 4DX when it doesn't fit is the skill's job, not bending the goal back into 4DX shape.

## Background — why merged

Originally 3 skills (2 atomic triages + 1 topic-router). The router was a thin disambiguation step over 2 protocols sharing the foundational stroke-of-pen / behavioral-change distinction. Merging into one multi-file scope-flex skill: kept all execution detail, deduplicated the 6-verdict rubric and Ch 1 distinction, single audit footer, single trigger-list. SKILL.md orchestrator now does scope detection + protocol routing directly.

## Indexed protocols

| Mode | Load protocol | Agent voice |
|---|---|---|
| Solo individual | [`protocols/personal-mode.md`](protocols/personal-mode.md) | personal coach |
| Team-leader (3-12 reports) | [`protocols/team-mode.md`](protocols/team-mode.md) | consultant to leader |

(Member scope intentionally absent — members inherit the WIG, do NOT triage methodology fit. Member queries route out via SKILL.md edge-case to `4dx-d1-wig-formulation`.)

## When this skill activates

- **Solo** — "Should I use 4DX for X?", "Will 4DX help me with…", "Does 4DX apply to a personal goal?"
- **Team-leader** — "Should our team adopt 4DX?", "Will 4DX work for my team?", "Is my team ready for 4DX?"
- **Ambiguous-scope fallback** — "Is 4DX a good fit?", "Is 4DX overkill?" (no explicit actor)
- Multilingual EN / JP / zh-TW per mode (see SKILL.md for full trigger list)

If the user's query is ambiguous on scope, the skill asks ONE Socratic disambiguation question covering both modes, then routes.

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Already committed to 4DX, asking "how do I start?" | D1 skills (whirlwind-triage / primary-wig-selection / wig-formulation) |
| Specific-discipline question (lead measures / scoreboard / WIG session) | Matching D-skill |
| Member receiving inherited WIG from a leader | `4dx-d1-wig-formulation` (members don't triage) |
| Enterprise multi-team rollout (cascading WIGs) | Book Ch 6-10 directly + `4dx-d1-team-wig-cascade` |
| Non-4DX methodology (OKR / agile / habit-stacking) | Plugin router `using-four-dx-coach` |

## Source citation

The 4 Disciplines of Execution (2nd ed., 2021) — McChesney / Covey / Huling / Thele / Walker. Chapter 1 (The Real Problem With Execution — stroke-of-pen vs behavioral-change distinction), Chapter 6 (Choosing Where to Focus — Strategy Map; goal-shape carve).

Industry grounding consolidated in [`references/industry-grounding.md`](references/industry-grounding.md): Kotter (urgency upstream), Heath & Heath (Path environment), March (exploration vs exploitation), Galbraith (STAR alignment), Schein (assumption-layer culture-fit).

## See also

- [`SKILL.md`](SKILL.md) — orchestrator with full scope-detection logic + routing table + cross-mode boundary
- Plugin router [`using-four-dx-coach`](../using-four-dx-coach/) for cold-start / out-of-4DX queries
