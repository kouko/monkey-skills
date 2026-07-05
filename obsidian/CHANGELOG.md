# Changelog

All notable changes to the `obsidian` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.19.1] — 2026-07-05 `daily-news-digest` Codex dispatch-portability fix

Following the same class of gap found and fixed in loom-code (#496) and
loom-interface-design/loom-spec (#497), `daily-news-digest`'s heavy-day
dispatch instructions named literal Claude-Code "`Agent`/`Task` calls"
and `run_in_background: true` directly in `references/heavy-day-dispatch.md`
and `SKILL.md` — a Codex reader hit terms it cannot resolve. Rewrote both
to host-neutral prose ("dispatch... in one round", "never non-blocking/
background") and added new `references/{claude-code-tools.md,codex-tools.md}`
carrying the concrete per-host call shape, including the Claude-Code-only
`name:`-triggers-mailbox-semantics pitfall and the 2026-07-02 real
`run_in_background` incident (eight consecutive blocked turns), both of
which structurally cannot recur on Codex's explicit spawn/wait/close
verb model.

## [3.15.0] — 2026-06-01 near-duplicate detection + `wiki-merge`

Adds near-duplicate awareness to the wiki layer across three surfaces:
prevent-new at ingest time, sweep-existing at lint time, and a new
human-gated skill that performs the consolidation.

### Added — `wiki-merge` skill

- New `wiki-merge` skill consolidates a confirmed near-duplicate PAIR of
  `wiki/` pages into one canonical page. The human gates **which** pair to
  merge; the skill then auto-executes a **reversible** merge.
- Merge is non-destructive: the absorbed page is **archived, not deleted**;
  the absorbed page's `User Notes` are **union-preserved** into the survivor;
  the absorbed slug is added to the survivor's `aliases` so inbound links and
  `[[wikilinks]]` keep resolving.
- Self-verifies the merge result and writes an **audit log** entry so the
  operation can be reviewed or rolled back.

### Added — `wiki-ingest` STEP 4c near-duplicate prompt (prevent-new)

- `wiki-ingest` now runs a near-duplicate check before minting a new page.
  On a **HIGH-confidence** match it prompts the user instead of silently
  creating a near-duplicate, and routes to `wiki-merge` when the user confirms.

### Added — `wiki-lint` L15 near-duplicate sweep (sweep-existing)

- `wiki-lint` gains check **L15**, a read-only sweep that flags existing
  near-duplicate page pairs across `wiki/`. Like every other lint check it
  does not auto-fix — it surfaces candidates for `wiki-merge`.

### Changed

- `wiki-lint` is now a **15-check** health audit (was 14-check) — the three
  READMEs (stale at "11") are updated accordingly.
