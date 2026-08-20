---
name: 2026-08-10-foreign-repo-cold-start-probe-for-plugin-shipped-mechanisms
description: No gate ever runs a loom skill's own commands from a repo that is not monkey-skills, so delivery defects (a mandated tool that ships in no plugin, a path that only resolves here) are structurally invisible to every existing check — candidate mechanism is a cold-start probe that installs the plugins in a scratch foreign repo and follows the skill text literally
status: open
origin: 2026-08-10 ship-progress-tooling arc — the plan_card.py/backlog_index.py delivery gap survived plan gates, SDD triads, and whole-branch reviews for the mechanism's whole life because every check ran inside monkey-skills, the one repo where the defect cannot manifest; the arc's whole-branch code arm B then demonstrated the probe shape works (ran the plugin copies from a scratch cwd with a fake docs/loom store and exercised render/--set-status/--validate/--write/--ready/--direction-write)
start: next time a loom-code/loom-pipeline arc changes what the plugins DELIVER (new script, new hook, renamed path — not prose-only edits), or the first recurrence of an external-repo-only failure
---

- Start: next time a loom-code/loom-pipeline arc changes what the plugins DELIVER (new script, new hook, renamed path — not prose-only edits), or the first recurrence of an external-repo-only failure
- Origin: 2026-08-10 ship-progress-tooling arc — the plan_card.py/backlog_index.py delivery gap survived plan gates, SDD triads, and whole-branch reviews for the mechanism's whole life because every check ran inside monkey-skills, the one repo where the defect cannot manifest; the arc's whole-branch code arm B then demonstrated the probe shape works (ran the plugin copies from a scratch cwd with a fake docs/loom store and exercised render/--set-status/--validate/--write/--ready/--direction-write)

- What: every existing gate — plan-document-reviewer, SDD triads,
  whole-branch panels, CI, dogfood — executes inside monkey-skills,
  where repo-root scripts exist and repo-relative paths resolve. A
  defect of the class "the skill mandates a tool that never arrives
  where the skill runs" is therefore invisible by construction; the
  progress-tooling gap lived its whole life ungated and was found only
  by a consumer repo's drift pain (see
  `docs/loom/memory/a-documented-fallback-can-legitimize-a-delivery-gap.md`).

  Candidate mechanism, demonstrated manually by this arc's review arm:
  a **cold-start probe** that (a) builds a scratch repo containing only
  a minimal `docs/loom/` skeleton (a plan with Status lines, a tiny
  backlog store), (b) resolves every skill-mandated command against the
  plugin CACHE paths (`~/.claude/plugins/cache/...` — what an external
  repo actually has), (c) runs each command from the scratch cwd and
  asserts the mechanism's own success criteria (card renders, ledger
  flips, index regenerates). Cheap version: a pytest module in
  loom-code/scripts/ that simulates the foreign cwd against the
  WORKING-TREE plugin dirs (no install step, catches path-resolution
  defects); expensive version: the full `plugin update` → cache →
  probe loop on a real second machine (catches packaging/manifest
  defects too — overlaps `headless-branch-plugin-testing-recipe`).

  Open design questions: which tier runs where (per-PR CI vs
  release-time), and whether the probe list is maintained by hand or
  derived by grepping skill bodies for mandated commands (the same
  extraction the cascade duty test already does — reuse candidate).

  Related: `docs/loom/backlog/2026-08-10-loom-lacks-a-milestone-layer-between-plan-stage-and-direction.md`
  (the other half of the same incident), memory entry
  `headless-branch-plugin-testing-recipe` (existing recipe the
  expensive tier would build on).
