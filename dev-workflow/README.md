# dev-workflow

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Developer workflow plugin for Claude Code — skill creation, scoring, refactor, tuning, deletion-first critique gates, and git-native project memory.

**Version**: 2.0.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## Background

Building skills for Claude Code is iterative. You draft a skill, ship it, find that it's too long or that the output is off-tone, and want to improve it — but *how* you improve it depends on the kind of change. **Token / structure refactor** is mechanically verifiable (output should be the same after). **Output quality tuning** is taste-sensitive (only a human can say which variant is better). Mixing the two into one rubric, as `darwin-skill`-style approaches do, lets an LLM-as-judge hill-climb away from human preference (Goodhart drift).

`dev-workflow` ships a family of skills built around two architectural moves:

1. **Two Hats split for skills** (Fowler refactor-vs-feature, applied to skill authoring) — `skill-refactor` (Phase A: behavior-preserving, auto-evaluable) is separate from `skill-tuning` (Phase B: taste-sensitive, human-judged).
2. **A critique-gate line** that intercepts proposals before they become commits — `proposal-critique` (multi-item triage) → `complexity-critique` (single-change deletion-first gate) → simplify (post-implementation review, lives in Anthropic's own toolkit).

The plugin also bundles `skill-creator-advance` (creation + major redesign), `skill-judge` (advisory 8-dimension quality rubric, never modifies), and `git-memory` (portable project memory written into commit trailers and PR bodies, recoverable by any tool that can read git).

Full design rationale: [`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md). Operational governance: [`docs/skill-governance.md`](docs/skill-governance.md). Quarterly health checks: [`docs/quarterly-audit-runbook.md`](docs/quarterly-audit-runbook.md).

## Skills

| Skill | Role |
|---|---|
| [`skill-creator-advance`](skills/skill-creator-advance/) | Create new skills or do major redesigns (add / split / merge phases, change agent decomposition, change input/output contract). Iterative eval-driven development with description optimization. |
| [`skill-refactor`](skills/skill-refactor/) | Token / structure refactor for an existing skill, **preserving output behavior**. Three-question gate: equivalence (multi-judge ensemble) + token reduction (≥10%) + invariant preservation. PROCEED / RESHAPE / REJECT verdict with git ratchet (auto-revert on failure). |
| [`skill-tuning`](skills/skill-tuning/) | Output quality A/B for an existing skill — generate variants, run them blind, capture human preference (A / B / both / neither). Constitution is the floor; taste is the ceiling. Preference log accumulates as RLHF-lite dataset. |
| [`skill-judge`](skills/skill-judge/) | Advisory 8-dimension design rubric (Knowledge Delta · Mindset+Procedures · Anti-Pattern · Spec Compliance · Progressive Disclosure · Freedom Calibration · Pattern Recognition · Practical Usability), 0–120 score + A–F grade. Never modifies. |
| [`proposal-critique`](skills/proposal-critique/) | Triage a multi-item proposal — list, plan, prose recommendation — into KEEP / DEFER / DROP using evidence grounding and YAGNI. |
| [`complexity-critique`](skills/complexity-critique/) | Gate one specific proposed change through three deletion-first questions: smallest possible end state, before/after LOC, what becomes obsolete. PROCEED / PROCEED-WITH-CAVEAT / RESHAPE / REJECT. |
| [`git-memory`](skills/git-memory/) | Capture decision context (the **why**, not the diff) into commit trailers and PR bodies so any future session — Claude Code, Cursor, Codex, aider, or a human — can reconstruct project knowledge from `git log` alone. |

All seven skills are **Active**. Lifecycle states and ownership: [`docs/skill-governance.md`](docs/skill-governance.md).

## The critique line

Three skills form a deletion-first review pipeline, each tuned to a different proposal shape:

```
proposal-critique           complexity-critique           Anthropic simplify
─────────────────           ─────────────────────         ──────────────────
Multi-item proposal         One specific proposed         Post-implementation
(list / plan / prose)       change (refactor, feature     diff review
                            add, debt cleanup, or
                            "should we build this")

Triage: each item gets      Gate: three deletion-first    Review what shipped:
  KEEP / DEFER / DROP         questions                     reuse, quality,
based on evidence + YAGNI     • smallest end state          efficiency
                              • before/after LOC
                              • what becomes obsolete

Verdict: KEEP / DEFER       Verdict: PROCEED /            (lives outside this
         / DROP                      PROCEED-WITH-CAVEAT  plugin)
                                   / RESHAPE / REJECT
```

Use `proposal-critique` when handed a backlog or numbered plan. Use `complexity-critique` when one specific change is on the table. Use Anthropic's `simplify` after the change has shipped.

## Skill-evolution architecture

`skill-creator-advance`, `skill-refactor`, `skill-tuning`, and `skill-judge` cover the full lifecycle of a skill, split by **size of change × evaluation mode**:

```
size →    small                medium                large                new
       ┌────────────────┐  ┌────────────────┐  ┌──────────────────────────────┐
       │ skill-tuning   │  │ skill-refactor │  │ skill-creator-advance        │
       │                │  │                │  │ (creation + major redesign)  │
       │ output quality │  │ token / struct │  │                              │
       │ A/B variants   │  │ same behavior  │  │ spec-first redesign / new    │
       │                │  │                │  │                              │
       │ HUMAN judge    │  │ LLM equiv.     │  │ user-led iteration loop +    │
       │ each iteration │  │ + git ratchet  │  │ optional AI A/B comparator   │
       └────────────────┘  └────────────────┘  └──────────────────────────────┘

       skill-judge: advisory 0–120 score, doesn't modify, runs at any time
```

The split is forced by the cost of evaluation: mechanical changes (refactor) tolerate auto-evaluation because LLM-as-judge can reliably check binary equivalence; taste-sensitive changes (tuning) require a human because LLM-as-judge is unreliable on style, voice, persuasive force, and design feel. Picking the right skill is a question of *what kind of change* you're making, not *how much automation* you want.

## git-memory pillars

`git-memory` rests on three claims:

1. **Carrier — git artifacts themselves.** Commit messages and PR bodies are the substrate. Any tool that can read git can read the memory. `git clone` brings it with you. No server, no embedding store, no vendor lock-in.
2. **Structure — commit trailers.** Structured facts ride in git trailers — same mechanism as `Co-Authored-By:` and `Signed-off-by:`. Three trailers cover ~80% of value: `Decision:` (why this approach), `Learning:` (what was discovered), `Gotcha:` (a trap for future you).
3. **Content — decision context, not code.** The diff already shows *what* changed. Memory records *why*. Aim for entries still valuable six months later when the original context is gone — not entries redundant with the code itself.

`git-memory` complements (does not replace) Claude Code's native `~/.claude/.../MEMORY.md`. Native memory holds user-level preferences across projects; `git-memory` holds project decisions inside the repo.

## Upstream chain

Three of the seven skills derive from MIT-licensed upstreams. Full attribution lives in each skill's `NOTICE` file.

| Skill | Upstream chain |
|---|---|
| `skill-creator-advance` | Anthropic [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) → AllanYiin (尹相志) [`skill-creator-advanced`](https://github.com/AllanYiin/Amon) → monkey-skills |
| `skill-judge` | Leonardo Flores [`skill-judge`](https://github.com/softaworks/agent-toolkit) → monkey-skills |
| `complexity-critique` | joshuadavidthomas [`reducing-entropy`](https://github.com/joshuadavidthomas/agent-skills/tree/main/skills/reducing-entropy) → softaworks fork → monkey-skills (renamed `reducing-entropy` → `complexity-critique`) |

`skill-refactor`, `skill-tuning`, `proposal-critique`, and `git-memory` are original designs. `skill-refactor` and `skill-tuning` acknowledge `alchaincyf/darwin-skill` (MIT) and Andrej Karpathy's `autoresearch` (MIT) as conceptual inspirations for the autonomous-loop + git-ratchet pattern, but the architecture, gate functions, and evaluation rubrics are independent. Details in each skill's `NOTICE`.

## Repository structure

```
dev-workflow/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── complexity-critique.md
│   ├── skill-creator-advance.md
│   ├── skill-refactor.md
│   └── skill-tuning.md
├── docs/
│   ├── skill-evolution-architecture.md
│   ├── skill-governance.md
│   ├── quarterly-audit-runbook.md
│   └── telemetry-setup.md
├── skills/
│   ├── complexity-critique/
│   ├── git-memory/
│   ├── proposal-critique/
│   ├── skill-creator-advance/
│   ├── skill-judge/
│   ├── skill-refactor/
│   └── skill-tuning/
├── CHANGELOG.md
├── README.md          (this file)
├── README.ja.md
└── README.zh-TW.md
```

## Install

`dev-workflow` is distributed as part of the [monkey-skills](https://github.com/kouko/monkey-skills) marketplace. Add the marketplace and install the plugin:

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install dev-workflow@monkey-skills
```

## Usage

Four slash commands ship with the plugin:

```
/skill-creator-advance      # create new or major-redesign existing
/skill-refactor             # token / structure refactor, equivalence-preserving
/skill-tuning               # human-judged output A/B
/complexity-critique        # deletion-first gate on a specific change
```

The remaining three skills (`skill-judge`, `proposal-critique`, `git-memory`) auto-trigger from natural language — for example:

```
"Score this skill against the 8-dimension rubric"     → skill-judge
"Critique this 12-item plan"                          → proposal-critique
"I'm about to commit — help me write the trailer"     → git-memory
```

For a worked walk-through of the Two-Hats split (refactor vs tuning), see [`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md) §2.

## Contributing

Contributions follow the repo-wide convention in [`CLAUDE.md`](../CLAUDE.md) at the repo root.

- **Questions**: open a GitHub Discussion or an issue on [kouko/monkey-skills](https://github.com/kouko/monkey-skills/issues).
- **PRs**: branch from `main`, follow Conventional Commits, run the convention-drift CI script (`scripts/check-shared-conventions-drift.py`) locally before pushing.
- **Skill-internal READMEs** are authored directly by the skill owner against a lighter rule set (see [`docs/skill-governance.md`](docs/skill-governance.md) §README Authoring Discipline). Plugin-level READMEs (this file and its translations) go through `domain-teams:docs-team`.
- **New shared conventions** must update the SSOT registry in [`docs/skill-governance.md`](docs/skill-governance.md) and add a pair to the drift CI manifest in the same PR.

## License

MIT. Skills with MIT-licensed upstreams (`skill-creator-advance`, `skill-judge`, `complexity-critique`) preserve their full copyright chain in their per-skill `LICENSE` and `NOTICE` files.

See [LICENSE](../LICENSE) at the repo root for the umbrella license.
