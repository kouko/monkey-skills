# research-toolkit triggering improvements — brainstorming brief (2026-07-06)

## Design-side on-ramp

Axis 0 negative guard: increment on an existing plugin (prompt-artifact
work, no end-user product surface) — silently skipped.

## Problem

research-toolkit's four skills almost never auto-trigger. Session
diagnosis (this session, live skill-list inspection) found three causes:

1. **Description eviction** — with ~120 skills enabled, Claude Code's
   listing budget (official: 1% of context; least-used skills' descriptions
   dropped first, confirmed at code.claude.com/docs/en/skills) drops
   3 of 4 research-toolkit descriptions to name-only entries. A name-only
   entry cannot be semantically routed to.
2. **Built-in competitor** — Claude Code ships a built-in `deep-research`
   skill whose description always survives; it out-competes
   `deep-deep-research` (which is a key-free, inspectable port of that very
   pipeline) for generic research asks.
3. **No `using-*` entry point** — the user's global CLAUDE.md Skill-Routing
   rule says "for domain tasks (code / design / research / Obsidian) load
   the corresponding `using-*` entry skill", but research-toolkit has none;
   that routing line is a dangling pointer for research. Named invocation
   via a router does NOT depend on description survival.

The job: when kouko asks a research-shaped question (中/日/英 —
fact-check a claim, audit citations, deep-read one source, multi-source
report), the right research-toolkit skill fires without a slash command.

## Users

kouko, Claude Code sessions on this machine (~120 skills enabled,
conversation language mostly 繁中), plus Codex-host portability as a
repo-wide standing constraint. Secondary consumer: the harness's own
router reasoning (description text is contract surface —
docs/loom/memory/preamble-wording-is-contract-surface.md).

## Smallest End State

1. Four rewritten `description` fields per the house standard
   (docs/skill-mining/2026-06-19-skill-description-standard.md: target
   ≤150 / cap 250 chars, what + when + positive specific triggers, at most
   ONE representative CJK trigger, positive redirects not "Do NOT use").
   deep-deep-research repositioned by positive specificity: inspectable /
   tunable / host-portable pipeline (vs the built-in's closed one).
2. One new skill `research-toolkit/skills/using-research-toolkit/SKILL.md` —
   family entry router, systems-thinking bucketed-table style
   (intent buckets → member skill), with a "trivial lookup → answer
   directly" negative guard and a note on the built-in `deep-research`
   boundary. No hooks, no SessionStart card (harness-audit just cut hook
   leakage; router card only if firing tests later prove need).
3. Metadata ripple: plugin.json + marketplace.json description sync
   (byte-identical, same PR — CI `marketplace-description-sync`);
   `.codex-plugin/plugin.json` version + stale-name fix (longDescription
   still says "deep-research fans out"); keywords rename residue; version
   0.2.1 → 0.3.0 (new skill = minor bump, commit-subject `(0.3.0)`).
4. Behavioral A/B evidence: firing corpus (research asks, 中/日/英 +
   near-miss NONE records) run via `loom-code/scripts/loom_firing_harness.py`
   Python seam (`run_corpus(claude_bin=…)`) with `--plugin-dir` wrappers —
   Arm A = main (worktree), Arm B = this branch. Clear improvement =
   B fires research-toolkit on records A misses, with zero new over-fires.

## Current State Evidence

- **Forward**: 4 skill descriptions at
  `research-toolkit/skills/*/SKILL.md:3-4` (block scalar; cite-check /
  deep-deep-research / deep-read / fact-check; only fact-check carries a
  CJK trigger 「這個說法對嗎」). No router skill exists (`ls research-toolkit/skills/`).
- **Reverse (SSOT direction)**: plugin.json description is mirrored
  byte-identical into `.claude-plugin/marketplace.json` (CI
  `.github/workflows/skill-structure.yml` job `marketplace-description-sync`);
  fact-check scripts are byte-identical functional copies of
  deep-deep-research's primitives kept by
  `research-toolkit/scripts/sync-primitives.sh` (fact-check/SKILL.md:19-21) —
  description edits do NOT touch that sync.
- **Error/guards**: `.claude/hooks/validate-skill-folder-structure.sh`
  (single-level subfolders only);
  `.github/workflows/check-plugin-description-skill-coherence.yml` (plugin
  description must not name a non-existent skill slug); conventional-commits
  type whitelist + kebab scope + no trailing period.
- **Data**: house standard doc
  `docs/skill-mining/2026-06-19-skill-description-standard.md` (PR #426;
  sweeps #428/#429) — 51-probe A/B: CJK keyword stuffing is REDUNDANT
  (identical routing with/without); keep ≤1 representative CJK trigger.
- **Boundary**: built-in `deep-research` (host-owned, not disable-able from
  the repo; user-side `skillOverrides` exists for built-ins only);
  `research-toolkit/.codex-plugin/plugin.json:24` stale "deep-research"
  name; harness interface `loom-code/scripts/loom_firing_harness.py`
  (corpus JSONL fields query/expected/notes; grade mode's EXACT/FAMILY is
  loom-specific → research A/B uses a small custom grader in the driver).

## Alternatives Considered (Axis 4 — researched EN+JA this session)

1. **SessionStart hook card** (loom-code #501 pattern) — rejected for now:
   harness-audit (#501 context) just cut hook injection; a card is paid in
   every session of every project. Revisit only if router firing fails.
2. **Raise the listing budget / trim the global surface**
   (`skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`,
   per-project plugin enablement; official) — real fix for eviction but
   machine-side settings, explicitly deferred by the user (options #1/#2);
   noted for the final report.
3. **Heavy multilingual trigger stuffing** (JA community practice, e.g.
   blog.serverworks.co.jp; unmeasured) — rejected: contradicts the house
   51-probe A/B (CJK redundancy verified in-repo, incl. bilingual probes).
4. **Chosen**: standard-compliant description rewrite + `using-*` router
   (in-house proven pattern: investing / systems-thinking / loom families) +
   behavioral A/B. Community data agrees auto-fire degrades with scale and
   named invocation is the reliable path — a router is the named-invocation
   on-ramp that CLAUDE.md already promises.

## What Becomes Obsolete

- The four current description strings (replaced in place).
- Stale `deep-research` name residue: `.codex-plugin/plugin.json:24`
  longDescription + `keywords[1]` in both plugin.json files (rename-hygiene:
  memory feedback_mine_old_names_after_rename).
- Nothing else: no README/CHANGELOG exists in this plugin; no hook exists.

## Decision

Build: 4 description rewrites (house standard; deep-deep-research
repositioned vs built-in), 1 new `using-research-toolkit` router skill
(systems-thinking style), metadata ripple (version 0.3.0, description
sync ×2 manifests + marketplace, stale-name fixes), 1 research-ask firing
corpus + driver, A/B evidence doc under `docs/loom/dogfood/`.
NOT build: hooks/SessionStart card, `when_to_use` fields (adds listing
weight against the lean-standard), README, changes to member skill bodies
beyond frontmatter, machine-side settings changes.

## Out of Scope

- Global plugin-surface slimming / listing-budget settings (options #1/#2 —
  user deferred; report will restate them).
- Disabling the built-in `deep-research` via user `skillOverrides`
  (machine-side; offered to the user at the end, not done unilaterally).
- Generalizing `loom_firing_harness.py` grade mode to non-loom families
  (driver-local grading instead; candidate BACKLOG note).
- Any change to fact-check/deep-deep-research pipeline scripts or the
  primitives sync.

## Open Questions

- None blocking. (Whether the router description itself survives eviction
  in real sessions is out of the repo's control; named routing via
  CLAUDE.md + explicit `/using-research-toolkit` works regardless, and the
  A/B measures the description-visible regime.)
