# loom-workflow

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Loom workflow plugin for Claude Code and Codex — decision briefs, deletion-first critique gates, git-native project memory, recap, handoff, and session distill.

**Version**: 1.0.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## Background

Building skills for Claude Code is iterative. You draft a skill, ship it, find that it's too long or that the output is off-tone, and want to improve it — but *how* you improve it depends on the kind of change. **Token / structure refactor** is mechanically verifiable (output should be the same after). **Output quality tuning** is taste-sensitive (only a human can say which variant is better). Mixing the two into one rubric, as `darwin-skill`-style approaches do, lets an LLM-as-judge hill-climb away from human preference (Goodhart drift).

`loom-workflow` grew from two architectural moves, one of which has since relocated:

1. **Two Hats split for skills** (Fowler refactor-vs-feature, applied to skill authoring) — `skill-refactor` (Phase A: behavior-preserving, auto-evaluable) separate from `skill-tuning` (Phase B: taste-sensitive, human-judged). Both skills, plus `skill-creator-advance` and `skill-judge`, have since moved to `skill-dev-toolkit`; see "Skill-evolution architecture (relocated)" below.
2. **A critique-gate line** that intercepts proposals before they become commits — `proposal-critique` (multi-item triage) → `complexity-critique` (single-change deletion-first gate) → simplify (post-implementation review, lives in Anthropic's own toolkit). This move still lives in `loom-workflow`.

The plugin also carries `git-memory` (portable project memory written into commit trailers and PR bodies, recoverable by any tool that can read git).

Operational governance: [`docs/skill-governance.md`](docs/skill-governance.md). Quarterly health checks: [`docs/quarterly-audit-runbook.md`](docs/quarterly-audit-runbook.md).

## Admission rule

A skill belongs in `loom-workflow` when it does **cross-station, multi-session coordination** — not merely because it happens to be "used by several plugins." Being widely used is not the test; coordinating work *across* stations, or carrying state *across* sessions, is. `decision-map` is the rule's first instance: it persists a decision map (`MAP.md` + tickets) that multiple stations read and write over the life of a project, which is exactly the cross-station, multi-session shape this plugin exists to hold. This rule gates *new* admissions only — existing utility skills already in the plugin are grandfathered in and will be re-evaluated together in the deferred family-relocation arc.

## Skills

| Skill | Role |
|---|---|
| [`brief-before-asking`](skills/brief-before-asking/) | Deliver a Mental-Model-first briefing before asking the user to decide a non-trivial engineering fork — the default, not optional. Also fires reactively when they're lost on the question, the explanation, or the stakes. |
| [`complexity-critique`](skills/complexity-critique/) | Evaluate one proposed change (refactor / feature / tech-debt) via a deletion-first lens: before/after LOC, what it obsoletes. Multi-item proposal → `proposal-critique`. |
| [`cot-explain`](skills/cot-explain/) | Explain how something was reasoned — a named file, or the work just done — as a standalone page built around a chain-of-thought diagram, every arrow labeled with why that step follows. |
| [`dbt-model-style`](skills/dbt-model-style/) | Enforce a dbt + Redshift model style & structure contract — CTE roles, zero-logic final CTE, naming, YAML header, comments, syntax. |
| [`decision-map`](skills/decision-map/) | Chart and work through a persistent decision map at `docs/loom/maps/<map-id>/` — a destination, a growing Decisions-so-far log, and a Not-yet-specified (fog) list that graduates into tickets over many sessions instead of a one-shot plan. |
| [`distill-sessions`](skills/distill-sessions/) | Mine past Claude Code and Codex session transcripts + `/insights` for friction patterns into a per-skill improvement-proposals doc. |
| [`git-memory`](skills/git-memory/) | Capture decision context (the **why**, not the diff) into commit trailers and PR bodies so any future session — Claude Code, Cursor, Codex, aider, or a human — can reconstruct project knowledge from `git log` alone. |
| [`goal-create`](skills/goal-create/) | Draft a goal condition — SESSION mode's four-field stopping condition (Outcome / Constraints / Verification / Stop-when) for a long-running agent run, or ARC mode's repository purpose artifact (`Why` / `Done when`). |
| [`handoff`](skills/handoff/) | Save session state to a structured HANDOFF file so a future agent resumes cleanly, or load/verify a prior HANDOFF. |
| [`independent-advisor`](skills/independent-advisor/) | Get a second opinion on the current plan or decision from a **different executor** — a stronger model, higher effort, or another vendor. The executor changes, not the critique lens. |
| [`proposal-critique`](skills/proposal-critique/) | Triage a proposal (list, plan, or prose recommendation) into KEEP / DEFER / DROP using evidence grounding and YAGNI. |
| [`recap-state`](skills/recap-state/) | In-session re-orientation — a structured recap ending with a Synthesis-check when the user loses the thread. |

All twelve skills are **Active**. Lifecycle states and ownership: [`docs/skill-governance.md`](docs/skill-governance.md).

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

## Skill-evolution architecture (relocated)

`skill-creator-advance`, `skill-refactor`, `skill-tuning`, and `skill-judge` — the size × evaluation-mode lifecycle model this section used to describe — have moved to `skill-dev-toolkit`, alongside `dogfood-skill-testing`. `loom-workflow` no longer bundles them. The original design rationale (Two Hats split, the evaluation-cost argument for why mechanical changes tolerate auto-evaluation but taste-sensitive changes need a human) is archived at [`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md); current ownership and ongoing design now live in `skill-dev-toolkit`'s own README.

## git-memory pillars

`git-memory` rests on three claims:

1. **Carrier — git artifacts themselves.** Commit messages and PR bodies are the substrate. Any tool that can read git can read the memory. `git clone` brings it with you. No server, no embedding store, no vendor lock-in.
2. **Structure — commit trailers.** Structured facts ride in git trailers — same mechanism as `Co-Authored-By:` and `Signed-off-by:`. Three trailers cover ~80% of value: `Decision:` (why this approach), `Learning:` (what was discovered), `Gotcha:` (a trap for future you).
3. **Content — decision context, not code.** The diff already shows *what* changed. Memory records *why*. Aim for entries still valuable six months later when the original context is gone — not entries redundant with the code itself.

`git-memory` complements (does not replace) Claude Code's native `~/.claude/.../MEMORY.md`. Native memory holds user-level preferences across projects; `git-memory` holds project decisions inside the repo.

## Upstream chain

One of the twelve skills derives from an MIT-licensed upstream. Full attribution lives in the skill's `NOTICE` file. (`skill-creator-advance`'s and `skill-judge`'s upstream attributions moved with them to `skill-dev-toolkit`.)

| Skill | Upstream chain |
|---|---|
| `complexity-critique` | joshuadavidthomas [`reducing-entropy`](https://github.com/joshuadavidthomas/agent-skills/tree/main/skills/reducing-entropy) → softaworks fork → monkey-skills (renamed `reducing-entropy` → `complexity-critique`) |

The remaining eleven skills are original designs with no external upstream to attribute. Details in each skill's `NOTICE` file where one exists.

## Repository structure

```
loom-workflow/
├── .claude-plugin/
│   └── plugin.json
├── docs/
│   ├── skill-evolution-architecture.md
│   ├── skill-governance.md
│   ├── quarterly-audit-runbook.md
│   └── telemetry-setup.md
├── skills/
│   ├── brief-before-asking/
│   ├── complexity-critique/
│   ├── cot-explain/
│   ├── dbt-model-style/
│   ├── decision-map/
│   ├── distill-sessions/
│   ├── git-memory/
│   ├── goal-create/
│   ├── handoff/
│   ├── independent-advisor/
│   ├── proposal-critique/
│   └── recap-state/
├── CHANGELOG.md
├── README.md          (this file)
├── README.ja.md
└── README.zh-TW.md
```

## Install

`loom-workflow` is distributed as part of the [monkey-skills](https://github.com/kouko/monkey-skills) marketplace. This hard-cut rename replaces `dev-workflow`; update any custom skill references to `loom-workflow:<skill>`. Add the marketplace and install the plugin:

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install loom-workflow@monkey-skills
```

## Usage

`loom-workflow` ships no slash commands — all twelve skills auto-trigger from natural language. For example:

```
"Critique this 12-item plan"                              → proposal-critique
"Worth the lines?" / "should we build this?"               → complexity-critique
"I'm about to commit — help me write the trailer"          → git-memory
"看不懂" / "跟不上" / agent-about-to-ask-complex-fork      → brief-before-asking
"開一張決策地圖" / "chart a decision map"                  → decision-map
"wrap up" / "save state"                                   → handoff
"where were we" / "我跟丟了"                                → recap-state
"second opinion" / "換一個模型看看"                         → independent-advisor
```

For the (relocated) Two-Hats split behind `skill-refactor` vs `skill-tuning`, see "Skill-evolution architecture (relocated)" above.

## Contributing

Contributions follow the repo-wide convention in [`CLAUDE.md`](https://github.com/kouko/monkey-skills/blob/main/AGENTS.md) at the repo root.

- **Questions**: open a GitHub Discussion or an issue on [kouko/monkey-skills](https://github.com/kouko/monkey-skills/issues).
- **PRs**: branch from `main`, follow Conventional Commits, run the convention-drift CI script (`scripts/check-shared-conventions-drift.py`) locally before pushing.
- **Skill-internal READMEs** are authored directly by the skill owner against a lighter rule set (see [`docs/skill-governance.md`](docs/skill-governance.md) §README Authoring Discipline). Plugin-level READMEs (this file and its translations) go through `domain-teams:docs-team`.
- **New shared conventions** must update the SSOT registry in [`docs/skill-governance.md`](docs/skill-governance.md) and add a pair to the drift CI manifest in the same PR.

## License

MIT. `complexity-critique`, the plugin's one skill with an MIT-licensed upstream, preserves its full copyright chain in its `LICENSE` and `NOTICE` files. (`skill-creator-advance` and `skill-judge` carry their own copyright chains now that they live in `skill-dev-toolkit`.)

See [LICENSE](https://github.com/kouko/monkey-skills/blob/main/LICENSE) at the repo root for the umbrella license.
