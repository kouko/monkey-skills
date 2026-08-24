# Brief: cross-host review-gate hardening

Date: 2026-08-24
Origin: high-priority findings from the independent whole-prompt audit.

## Design-side on-ramp

Negative guard: this is a hardening refactor of an existing agent workflow, not
a new user-facing product or interaction surface. Backlog ready check ran;
related entries are open or closed, not live bets.

## Problem

Loom's review gate can claim a portable, current-HEAD review when the evidence
does not support that claim. A standalone consumer repository has no
`<repo>/loom-code` directory, while reviewer Rule R1 and several review calls
derive plugin resources from that repository. Separately, a pass marker reads
HEAD only when it is minted, so a verdict can review commit A and mint on B.

The docs confirmation route can resolve findings without creating a terminal
pass artifact. Plan Check 17 can declare itself N/A before checking whether a
task required reuse evidence. An unconfirmed R3 caveat and a simplification
finding can also disappear before the pass marker is written.

## Users

- Kouko, who needs one review outcome to mean the same thing in Claude Code
  and Codex.
- Maintainers using loom-code from a consumer repository, where the plugin is
  installed outside that repository.
- Reviewer subagents, which need an explicit immutable input instead of
  reconstructing host-dependent state.

## Smallest End State

- BI-1 — Every review station receives one host-neutral review context carrying
  the target-repo path, reviewed SHA, plugin version, and absolute paths to the
  plugin resources it may read. A reviewer never derives a plugin path from the
  target repository.
- BI-2 — `review-pass` accepts an expected reviewed SHA and refuses to mint if
  the target repository's current HEAD differs. Code and docs terminal verdicts
  name that SHA.
- BI-3 — After a docs fix, Claude Code may use its same-reviewer confirmation
  route; Codex uses one explicitly labelled fresh whole-artifact review. Either
  route produces a terminal verdict for the current SHA before a marker can be
  minted. A mixed code/docs branch re-runs every required arm at that SHA.
- BI-4 — Plan Check 17 reads the cited repository source for reuse claims and
  fails a task that says to reuse a helper without a `Reuse-adequacy` block.
- BI-5 — An R3 unverified-evidence caveat remains visible as a non-clean review
  outcome, and simplification findings enter the aggregate before marker mint.
- BI-6 — Claude Code and Codex have tested, documented host adapters around the
  same context contract; neither adapter depends on a relative plugin path in a
  consumer repository.

## Current State Evidence

- `loom-code/agents/_reviewer-discipline.md` Rule R1 derives the consumer repo
  root then reads `loom-code/.claude-plugin/plugin.json`; that path is absent in
  an isolated consumer install.
- `loom-code/skills/requesting-code-review/SKILL.md` calls
  `python3 loom-code/scripts/review_scope.py`, another target-repo-relative
  plugin path.
- `loom-code/scripts/loom_gate_markers.py` resolves `HEAD` inside
  `_cmd_review_pass` after it has read the verdict; its CLI has no expected-HEAD
  argument.
- `loom-code/skills/requesting-docs-review/SKILL.md` asks for confirmation
  after a fix but does not describe a terminal marker-minting artifact.
- `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`
  limits Check 17 to plan/brief/schema even though its cross-read requires the
  cited repository source; its mapping makes Check 17 N/A when no block exists.
- `loom-code/skills/requesting-code-review/SKILL.md` aggregates and mints before
  its simplification-harvest step; `_reviewer-discipline.md` makes R3 a note
  rather than a severity finding.

## Decision

Use a shared, read-only review-context contract. A plugin-shipped resolver
locates its own installation from its script path and emits absolute resource
paths plus an immutable reviewed SHA. Claude Code and Codex adapt only the
host-specific handoff of that context; reviewer prompts consume the same data.

The marker command independently enforces the reviewed SHA. Docs confirmation
is host-specific in execution but identical in its terminal requirement:
current-SHA verdict first, marker second. This retains Claude Code's
same-reviewer continuity without pretending Codex has a mailbox.

## Alternatives Considered

1. **Shared context contract plus thin host adapters** (chosen) — keeps policy,
   evidence paths, and marker semantics common while isolating real platform
   differences.
2. Use only `${CLAUDE_PLUGIN_ROOT}` or a Codex cache path — rejected: each is a
   host-specific locator and leaks into reviewer logic, which is exactly the
   standalone failure.
3. Copy or mount plugin files into every consumer repository — rejected: it
   mutates the review target, risks collisions, and creates a second version
   source.
4. Always run a fresh full docs panel after every fix — rejected: it discards a
   valid Claude Code continuity capability and costs more; Codex retains this
   as its explicit, bounded fallback.

Claude Code documents plugin-defined subagents and their working-directory
model, so reviewer resources must not be inferred from that directory. Codex
plugins likewise package skills separately from the target repository. See
[Claude Code custom subagents](https://code.claude.com/docs/ja/sub-agents) and
[Codex plugins](https://help.openai.com/en/articles/20001256-plugins-in-codex/).

## Out of Scope

- Durable ledger revival, new telemetry, or changing reviewer model defaults.
- Server-side GitHub enforcement and unrelated finishing-flow contradictions.
- Rewriting all reviewer prompts beyond the contracts needed for these six
findings.

## Queue relation

unqueued — direct user-authorized remediation from the 2026-08-24 prompt audit;
related backlog entries are not live bets.

## Open Questions

None blocking. The implementation chooses the exact JSON field names only after
the RED tests identify the smallest compatible contract.

## What Becomes Obsolete

- Target-repository-relative `loom-code/...` resource resolution in review
  stations.
- Marker minting that silently substitutes the current HEAD for the reviewed
  commit.
- The Check 17 assumption that no block means no reuse obligation.
