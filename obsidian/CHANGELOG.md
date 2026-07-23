# Changelog

All notable changes to the `obsidian` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.20.1] — 2026-07-24 wikilink-target-insensitive word counter

### Changed — `wiki-lint` conservation-counter semantics (words)

- `wiki_lint_check.py` words counter now normalizes every `[[...]]`
  wikilink (including `[[target|display]]` / `[[target#anchor]]`
  variants) to a single token before whitespace-splitting. A benign
  retarget — `[[Two Word Target]]` → `[[Oneword]]`, the bread and
  butter of L07 broken-link repair — no longer shifts the word count,
  while deleting a link or surrounding prose still lowers it.
  Motivation: wiki-update smoke run Finding #1
  (`docs/loom/dogfood/2026-07-23-wiki-update-loop-smoke/loop-report.md`)
  — the `[[Acme Corp]]` → `[[Acme-Corp]]` retarget shrank the count
  308→307 and tripped the ratchet fail-closed (exit 8) with zero
  content loss; on the real vault's ~873-broken-link backlog the L07
  class would have stalled on its first round. `links` / `headings`
  counters and the JSONL contract shape are unchanged.

## [3.20.0] — 2026-07-24 `wiki-update` loop + mechanical validator

Adds a self-driving update loop for the wiki layer, backed by a new
mechanical lint validator so the loop's "clean" state is machine-checked
rather than self-reported.

### Added — `wiki-lint` mechanical validator (`wiki_lint_check.py`)

- New deterministic-lane script (`scripts/wiki_lint_check.py`) covers six
  error-level checks — L01 frontmatter completeness, L02 summary length,
  L03 required body sections, L04 wikilink format, L07 broken intra-wiki
  wikilinks, L14 reference-page `## Source` wikilink — plus a `PARSE`
  error lane for unreadable/malformed pages and per-file conservation
  counters (word/link/heading) so downstream fixers can prove they didn't
  silently drop content.

### Added — `wiki-update` skill

- New thin-dispatcher skill orchestrates the existing wiki maintenance
  chain end-to-end: `wiki-ingest` → `wiki-cross-linker` → a repair loop →
  ticket triage → a final report card. It does not duplicate any member
  skill's logic — it sequences them and carries the loop state between
  stages.

### Added — repair-loop engine

- The repair loop adds: criteria freeze + safe-tier classification
  (only safe-tier fixes auto-apply; unsafe-only classes become
  work-order entries for the human lane), a fixed brake-CONSULTATION
  order (ratchet → compare → stuck → plateau → budget — safety checks
  consulted first each round; repair order itself is largest-class-
  first), a proposal-branch exit (accepted safe-tier rounds land as
  LOCAL commits on `wiki-fix/<runLabel>`, never merged or pushed), and
  a cumulative-size circuit-breaker that stops the loop once committed
  diff exceeds the cap and asks for the remaining work to be split.
- Real-execution smoke test (not a dry run) confirmed two check classes
  converge to clean within the loop, and surfaced one ratchet false-positive
  that the loop correctly re-targets as a known next-touch item rather than
  looping on it — see
  `docs/loom/dogfood/2026-07-23-wiki-update-loop-smoke/`.

## [3.19.1] — 2026-07-05 `daily-news-digest` Codex dispatch-portability fix

Following the same class of gap found and fixed in loom-code (#496) and
loom-interface-design/loom-spec (#497), `daily-news-digest`'s heavy-day
dispatch instructions named literal Claude-Code "`Agent`/`Task` calls"
and `run_in_background: true` directly in `references/heavy-day-dispatch.md`
and `SKILL.md` — a Codex reader hit terms it cannot resolve. Rewrote both
to host-neutral prose ("dispatch... in one round", "wait for every
subagent to return before proceeding") and added new
`references/{claude-code-tools.md,codex-tools.md}`
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
