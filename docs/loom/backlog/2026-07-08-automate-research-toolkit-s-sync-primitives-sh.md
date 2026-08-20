---
name: 2026-07-08-automate-research-toolkit-s-sync-primitives-sh
description: Automate research-toolkit's sync-primitives.sh
status: open
blocked: waiting on a second real SSOT-drift incident reaching main
origin: raised during review of `docs/loom/specs/2026-07-08-deep-deep-research-fact-opinion-classification.md` (2026-07-08) — an external critique suggested moving `research-toolkit/scripts/sync-primitives.sh` from a manual step (backstopped only by a CI-side MD5 drift gate) to a git pre-commit hook or build-pipeline dependency, for local "fail loud" instead of async CI-only catch. Valid idea, evaluated and deliberately deferred from that brief because it targets the *pre-existing, repo-wide* SSOT-sync convention shared by every synced primitive in `research-toolkit` (not something that brief's `claimType` change introduced) — out of scope for a single-feature brief.
start: a second real drift incident (a synced primitive shipped out of sync with its SSOT and reached `main` before CI's MD5 drift gate caught it — not just failed a PR check, actually merged wrong). One incident (PR #519) was caught by the existing CI gate before merge, which is the gate working as designed, not a failure of it.
---

- Start: a second real drift incident (a synced primitive shipped out of
  sync with its SSOT and reached `main` before CI's MD5 drift gate
  caught it — not just failed a PR check, actually merged wrong). One
  incident (PR #519) was caught by the existing CI gate before merge,
  which is the gate working as designed, not a failure of it.
- Origin: raised during review of
  `docs/loom/specs/2026-07-08-deep-deep-research-fact-opinion-classification.md`
  (2026-07-08) — an external critique suggested moving
  `research-toolkit/scripts/sync-primitives.sh` from a manual step
  (backstopped only by a CI-side MD5 drift gate) to a git pre-commit
  hook or build-pipeline dependency, for local "fail loud" instead of
  async CI-only catch. Valid idea, evaluated and deliberately deferred
  from that brief because it targets the *pre-existing, repo-wide*
  SSOT-sync convention shared by every synced primitive in
  `research-toolkit` (not something that brief's `claimType` change
  introduced) — out of scope for a single-feature brief.
- What: if triggered, add a local pre-commit hook (or equivalent) that
  detects an edit to a declared SSOT primitive
  (`research-toolkit/skills/deep-deep-research/scripts/{schemas,rank,prompts,dedup}.py`)
  and either auto-runs `sync-primitives.sh` for the known sibling skills
  or blocks the commit until it's run manually. Keep the existing CI MD5
  gate regardless — this is a local speed-up, not a replacement for the
  CI backstop.
