# Engineering baselines — 12-rule canonical list

This document is the human-readable catalog of the 12-rule engineering
baseline that code-toolkit's plugin-level agents carry in their system
prompts. It is **NOT the SSOT for agent injection** — that is
`code-toolkit/agents/_baseline.md`, kept in sync by
`code-toolkit/scripts/distribute.py`.

Read this file when:

- You want a single page describing the discipline floor for any
  code-toolkit agent dispatch.
- You are about to copy the 12 rules into your own project's
  `CLAUDE.md` (you can; the rules are designed as cross-cutting
  baselines that apply to every coding task).
- You want to know which rule a given skill / agent / dispatch is
  amplifying.

## The 12 rules

The full text lives in [`code-toolkit/agents/_baseline.md`](../../../agents/_baseline.md).
Below: one-line summary + cross-reference table.

| # | Rule | Where it lives in the workflow |
|---|---|---|
| 1 | **Think before coding** — state assumptions; ask if uncertain; stop when confused | Fully enforced by [`brainstorming`](../../brainstorming/SKILL.md) 5-axis HARD-GATE; also baked into every plugin-level agent via `_baseline.md` |
| 2 | **Simplicity first** — minimum code; no speculation; senior-engineer simplification test | Delegated to `dev-workflow:complexity-critique` + [`brainstorming`](../../brainstorming/SKILL.md) Axis 3 (Smallest End State); also baked into every plugin-level agent |
| 3 | **Surgical changes** — touch only what you must; don't refactor adjacent code | Baked into every plugin-level agent; not explicitly enforced by a skill HARD-GATE (this is the closest thing to a "previously unaddressed gap" the 12 rules surface for the toolkit) |
| 4 | **Goal-driven execution** — define success criteria; loop until verified | [`writing-plans`](../../writing-plans/SKILL.md) structures success criteria; [`verification-before-completion`](../../verification-before-completion/SKILL.md) gates on them; also baked into every plugin-level agent |
| 5 | **Use the model only for judgment calls** — code answers what code can answer | Meta — out of scope for skill-level enforcement. Baked into agents as guidance for code-emitting tasks that involve LLM calls (the rule binds the code you author, not just the caller). |
| 6 | **Token budgets are not advisory** — surface breaches, don't silently overrun | Meta — out of scope for skill-level enforcement. Baked into agents as guidance on response length. |
| 7 | **Surface conflicts, don't average** — pick one pattern, explain why, flag the other | Touched by [`requesting-code-review`](../../requesting-code-review/SKILL.md) cross-task-coherence dimension; also baked into every plugin-level agent |
| 8 | **Read before you write** — read exports, callers, shared utilities first | Implicit in SDD implementer worker contract; explicit in baseline baked into every plugin-level agent |
| 9 | **Tests verify intent, not just behavior** — encode WHY, not just WHAT | Implicit in [`tdd-iron-law`](../../tdd-iron-law/SKILL.md) (Beck preface); explicit in baseline baked into every plugin-level agent |
| 10 | **Checkpoint after every significant step** — summarize done / verified / left | Implicit in [`writing-plans`](../../writing-plans/SKILL.md) structure + SDD atomic units; explicit in baseline baked into every plugin-level agent |
| 11 | **Match codebase conventions, even if you disagree** — surface harmful conventions, don't fork silently | CLAUDE.md base guidance covers it; also baked into every plugin-level agent |
| 12 | **Fail loud** — "completed" wrong if skipped silently; surface uncertainty | Fully enforced by [`verification-before-completion`](../../verification-before-completion/SKILL.md) HARD-GATE + router rule #4 (push-without-review = silent skip); also baked into every plugin-level agent |

## How the integration works

```
code-toolkit/
  agents/
    _baseline.md           ← SSOT — the canonical 12-rule text
    implementer.md         ← plugin-level agent — role contract + injected baseline block
    (Phase 2 will add: spec-reviewer.md / code-quality-reviewer.md / reviewer.md / debugger.md)
  scripts/
    distribute.py          ← injects _baseline.md content between BEGIN/END markers in each agent
    verify-drift.py        ← CI gate: rejects any agent file whose baseline block diverges from SSOT
```

Each plugin-level agent embeds the baseline verbatim between
`<!-- BEGIN baseline-v1 ... -->` and `<!-- END baseline-v1 -->`
markers. Drift is impossible without `verify-drift.py` failing.

When `_baseline.md` is updated, run `distribute.py` and the change
propagates to every routed agent file.

## Why the rules are baked into agents, not just listed here

A reference doc is **passive** — it only fires when an agent reads it.
An agent system prompt is **active** — it fires on every dispatch
without the agent having to discover it.

The 12 rules are baseline discipline that should apply to every
dispatch. Putting them in the agent's system prompt is the only way
to guarantee they apply. This reference doc is for human readers who
want to understand what the agents carry.

## Origin

The 12 rules are a CLAUDE.md template pattern that surfaced in user
practice across multiple sessions. They were integrated into
code-toolkit in v0.5.2 (P15-12) as part of a broader move to
plugin-level agent definitions. The rules themselves are not
canon-grounded in primary sources (unlike the rest of the toolkit,
which roots in Beck / Martin / Fowler / Feathers / ASVS / 徳丸本) —
they are prompt-engineering shorthand for behaviors that the
canon-grounded skills enforce structurally.

The relationship is complementary, not redundant:

- **Canon-grounded skills** = "here is the discipline rule and why
  Beck / Martin / Fowler grounds it."
- **12-rule baseline** = "here is the discipline as a prompt-loadable
  short statement that primes the agent for every task."

## Out-of-scope rules (5 and 6)

Rules 5 (LLM judgment only) and 6 (token budgets) are about
meta-AI-orchestration, not coding discipline per se. They are baked
into agent prompts with **agent-application** notes that translate
them to in-dispatch behaviors:

- **Rule 5** binds the code the agent *authors* when that code uses
  LLMs (prefer deterministic paths).
- **Rule 6** binds the agent's own output length (keep responses
  concise; one well-scoped response beats sprawling).

But neither is enforced by a skill HARD-GATE because skills don't
have hooks into token accounting or downstream LLM-using code
behavior. The agent-baked version is the only enforcement surface
the toolkit owns.

## See also

- [`code-toolkit/agents/_baseline.md`](../../../agents/_baseline.md)
  — the SSOT.
- [`code-toolkit/agents/implementer.md`](../../../agents/implementer.md)
  — the v0.5.2 first plugin-level agent carrying the baseline.
- [`../../subagent-driven-development/SKILL.md`](../../subagent-driven-development/SKILL.md)
  — SDD orchestration, now dispatches implementer via
  `Agent({subagent_type: "code-toolkit:implementer"})`.
- [`../../../CHANGELOG.md`](../../../CHANGELOG.md) v0.5.2 entry — full
  ship notes for P15-12.
