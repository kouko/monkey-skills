# code-reviewer sonnet default — overturn the 0.75.0 inherit carve-out

Date: 2026-08-24
Status: brief (approved direction: Option A — pin `model: sonnet` on code-reviewer)

## Design-side on-ramp

not fired — config-shaped default change to an existing agent contract; no product-shaped/user-facing/multi-state new work (Axis 0 negative guard). Backlog ready check ran: open items surfaced, none related to reviewer model tiering.

## Problem

The whole-branch review panel (`requesting-code-review` → 2× `loom-code:code-reviewer`) is the most expensive reviewer line in measured local usage, and it runs on the dispatching session's model tier by default. In Fable/Opus sessions "inherit" = most expensive tier, at ~5× sonnet price per dispatch, with no measured recall benefit.

Measured from local subagent transcripts (2026-07-23 → 2026-08-23): since 0.75.0 shipped (2026-08-12), 145 code-reviewer dispatches → 101 ran on opus/fable via inheritance, 7 on sonnet; post-#728 (portable dispatch profile) 3/3 still inherited opus. Recall evidence: G4 A/B — 2×Sonnet panel with union aggregation reproduced the correct verdict with zero false positives (`docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md`); same conclusion class as the n=1,357 audit in `docs/loom/specs/2026-08-11-review-cost-reduction.md:16`.

0.75.0 deliberately scoped this out (spec `:46` pins code-reviewer "unset (inherit)"; `:102` lists changing it as Out of Scope) — a scope-control decision, not an evidence-based objection. The user (kouko, 2026-08-24) explicitly chose to overturn it (Option A) after reviewing the dispatch data.

## Users

kouko's own loom arcs in this repo (Fable-tier sessions, where inherit = maximum price), plus any consumer repo running loom-code on an expensive session tier. Weak-model orchestrators benefit identically: a frontmatter pin is mechanical, requiring no orchestrator judgment.

## Smallest End State

1. `loom-code/agents/code-reviewer.md` frontmatter carries `model: sonnet` (matching the three checklist arms). No `effort:` key (session effort still inherited).
2. `loom-code/scripts/test_agent_model_frontmatter.py` updated: code-reviewer moves from the judgment-arm "must not carry model:" assertion to the pinned-sonnet assertion; implementer stays judgment-arm (unchanged). Test written/updated FIRST and observed RED before the frontmatter edit.
3. `docs/loom/specs/2026-08-11-review-cost-reduction.md` gets a dated appended note (never in-place rewrite): the code-reviewer half of the Out-of-Scope row is overturned 2026-08-24 with the dispatch-count + G4 evidence; implementer half remains in force.
4. `loom-code/.claude-plugin/plugin.json` version bump (skill/agent content change ships only via version bump — repo rule).

Upgrade path unchanged: an orchestrator passing an explicit `model` param at dispatch time still overrides frontmatter (dispatch-profile `frontier` route for architecture/security-sensitive branches stays available and documented in `dispatch-profile.md:11-19`).

## Current State Evidence

- **Forward**: `loom-code/skills/requesting-code-review/SKILL.md` §Process Step 2 ("Resolve the dispatch profile … dispatch TWO `code-reviewer` subagents in parallel, with byte-identical prompts") — the only dispatch site of this agent; no model param is mandated there, so frontmatter is the effective default.
- **Reverse**: `loom-code/scripts/distribute.py` (AGENT_BASELINE_TARGETS) manages only the baseline/rule-sheet blocks inside `agents/*.md`; frontmatter is NOT distributed — the frontmatter edit is made directly in `loom-code/agents/code-reviewer.md` and no sync script overwrites it (confirmed by reading distribute.py's managed-block markers).
- **Error**: `loom-code/scripts/test_agent_model_frontmatter.py` ("judgment arms … must not carry a model: key") — the assertion that currently encodes the old design and will fail first (the RED step).
- **Data**: local dispatch tally (requested→resolved model per agent type, from `~/.claude/projects/*/*.jsonl` Agent tool_use records joined to `subagents/agent-*.jsonl`): code-reviewer since 2026-08-12 n=145 — inherit→opus 75, inherit→fable 26, sonnet→sonnet 7, opus→opus 11; docs-reviewer same window shows its `model: sonnet` frontmatter working (inherit→sonnet 19, inherit→opus/fable 0).
- **Boundary**: `loom-code/skills/using-loom-code/references/dispatch-profile.md` ("rubric review → `standard`" / "`standard` | `sonnet`" mapping table; frontier must-not-downgrade clause) — the pin implements the `standard` default for this rubric-review role; frontier upgrades ride the existing dispatch-time override.

## Alternatives Considered

My take — Recommend: frontmatter pin (Option A). Why: mechanical default, no orchestrator judgment surface, proven working on docs-reviewer since 0.75.0. Conditional reversal: if branch-review recall measurably drops on sonnet (a missed 🔴 that an opus arm later catches), revert the pin and route via explicit per-dispatch model selection instead.

- **B — orchestrator resolves profile and passes `model` explicitly each dispatch**: rejected — prose judgment ("is this rubric review or architecture review?") executed by possibly-weak orchestrators; measured not to happen in practice (post-#728 3/3 still inherited). Repo memory: judgment-shaped prose rules fail where mechanical defaults hold.
- **C — keep inherit (status quo)**: rejected by user decision 2026-08-24; cost evidence above.
- (No WebSearch round: the decision space is repo-internal — an already-measured tiering choice between this repo's own two documented mechanisms; no industry-shipped third option applies.)

## What Becomes Obsolete

The "judgment arms inherit" docstring rationale in `test_agent_model_frontmatter.py` (module docstring must be updated in the same change — twin-flag rule: docstring and assertions move together). The 0.75.0 spec's Out-of-Scope row is superseded for code-reviewer only, recorded by appended note, not deletion.

## Decision

Pin `model: sonnet` in code-reviewer frontmatter with test-first coverage; amend the 0.75.0 spec by appended dated note; bump loom-code plugin version. Do NOT change implementer's inherit default (explicitly deferred — separate evidence line, per the independent review's item 4). Do NOT add any new skip/routing logic to requesting-code-review.

## Out of Scope

- implementer model default (stays inherit; revisit after cqr-transcript mining).
- Turn/tool budgets in reviewer contracts (independent review's item 2 — separate arc).
- Per-task cqr narrowing / A2 (pending transcript mining).
- dispatch-profile.md wording changes (mapping already says standard→sonnet).
- Codex-side mirror (`.codex/agents/*.toml`) — Claude Code frontmatter only; Codex tiering tracked separately.

## Queue relation

unqueued — direct user decision (2026-08-24 cost-analysis session); no related backlog entry exists.

## Open Questions

- None blocking. Post-ship telemetry: after ~2 weeks of organic dispatches, re-run the requested→resolved tally to confirm inherit→sonnet dominates and no frontier-shaped branch regressed.
