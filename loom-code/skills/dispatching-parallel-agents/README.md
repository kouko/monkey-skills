# dispatching-parallel-agents

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> **One agent per independent problem domain — let them work concurrently.** Default is sequential; parallel dispatch is the exception you justify with an honest independence check (disjoint files, disjoint symbols, no data dependency). Original pattern: superpowers v5.1.0 `dispatching-parallel-agents`, adapted for loom-code's TDD iron-law + verdict aggregation.

Part of the [loom-code](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## What this skill does

When the work is **2+ independent problem domains** — fixes in unrelated test files, audits across unrelated modules, data fetches for disjoint inputs — sequential dispatch wastes wall-clock time. This skill is the **across-domain dispatch layer**: identify truly independent domains, compose a self-contained prompt per domain, dispatch all `Agent` calls **in one assistant message** (the harness only runs them concurrently when they share a message), then aggregate verdicts without dropping any.

## When to use

- 3+ test files failing for **unrelated** reasons — one implementer per file.
- Security audit across multiple modules — one reviewer per module.
- Data fetch for N tickers / regions / feeds — one data agent per input.
- Plan tasks marked `independent: true` by `writing-plans` **and** whose `files touched` sets are disjoint — both conditions must hold; the marker is the plan author's claim, not a guarantee.

A domain is independent only when all hold: no shared file (or shared file is read-only everywhere), no shared symbol any branch will rename/remove/re-export, no sequential data dependency. If you cannot state the independence in one sentence per domain, the work is not independent.

## When NOT to use

See [`SKILL.md`](SKILL.md) §When to use vs. when NOT to:

- Tasks share a file or symbol — merge conflicts + non-deterministic state; sequence, or split the file first.
- Sequential data dependency (B needs A's output) — by definition not parallel.
- Failures might share a root cause / root cause unknown — one agent investigates first; fragmenting hides the shared cause.
- Single domain, complex but cohesive — one focused subagent, not N fragmented ones.
- Two reviewers on one artifact — `subagent-driven-development` already does this per-task; don't double-wrap.

## Relationship to subagent-driven-development

SDD's implementer/reviewer triad is **per-task within one domain**; this skill is the **across-task / across-domain** complement. Parallel dispatch waives nothing: every branch still follows `tdd-iron-law` (failing test first — "small + parallel" is the rationalization combo, refused), and `verification-before-completion` runs the package suite **once at the integration point**, not per branch — per-branch suites pass in isolation while the combined diff can still fail.

## Two modes

- **Mode (a)** — one orchestrator fans out subagents in a single message; they share one checkout, results aggregate in that orchestrator. This is the skill's main body.
- **Mode (b)** — several independent sessions work the same repo at once. The harness does not coordinate across sessions, so the convention is: worktree-per-agent (see [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md)) + static up-front partition of disjoint plan tasks + the plan's `Status` field as shared ledger + PR-per-agent. **Load-bearing pitfall:** the worktree isolates files but does NOT prevent overlapping-edit collisions — the `files touched` disjointness partition is the real collision defense. Practical ceiling: ~3–5 concurrent agents.

## What this skill does NOT do

- Does **not** replace `subagent-driven-development` — SDD stays the per-task engine inside each domain.
- Does **not** license implementers writing to the same files in parallel — file conflicts are forbidden, "git will sort it out" is refused.
- Does **not** exempt any branch from `tdd-iron-law`.
- Has **no** Skill Priority stage in the router — auxiliary, on-demand.

## See also

- [`SKILL.md`](SKILL.md) — operational spec (independence criteria + dispatch pattern + aggregation rules + mode (b) + red flags).
- [`../writing-plans/SKILL.md`](../writing-plans/SKILL.md) — upstream; produces the `independent: true` atomic tasks this skill consumes.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — lateral; per-task triad inside one domain.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — downstream; runs once at integration.
- [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) — required for mode (b) concurrent sessions.
