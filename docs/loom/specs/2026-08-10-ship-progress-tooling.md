# Brief: ship the progress tooling inside the loom-code plugin

Date: 2026-08-10
Origin: live observation in an external repo (kumiko-zaiku-app-icons,
session 63262433, 2026-08-10) — the repo hand-maintains a `progress.md`
that drifted from reality four times, because the machinery loom-code
prescribes for progress state never arrives on any repo but this one.

## Problem

loom-code's progress machinery is two scripts: `plan_card.py` (renders
and flips the plan's per-task `Status:` ledger, machine-validated) and
`backlog_index.py` (regenerates `BACKLOG.md` / `DIRECTION.md`, the
cross-plan queue). Five shipped skills — `subagent-driven-development`,
`writing-plans`, `requesting-code-review`, `brainstorming`,
`finishing-a-development-branch` — mandate them at 10 call sites, all as
`python3 scripts/<name>.py`: a path relative to the TARGET repo's root.
The scripts themselves live at monkey-skills' repo root and ship in no
plugin (`find ~/.claude/plugins/cache -name plan_card.py` → empty).

So in every repo except monkey-skills, the mandated call falls through
to its documented fallback ("hand-edit / render the four fields inline")
**permanently and silently** — the degradation is designed to be loud
once, but it fires on every plan of every external repo forever. Live
consequence: kumiko's hand-kept progress table drifted 4 times, each
drift surviving every gate because no gate recognizes a hand-copy.

## Users

kouko + any agent running loom-code skills in a repo other than
monkey-skills. (monkey-skills itself is unaffected — the repo-root
scripts are present here.)

## Smallest End State

1. `plan_card.py` and `backlog_index.py` (with their test files) live in
   `loom-code/scripts/` — inside the plugin, so every `plugin update`
   delivers them. Single copy; no sync duty.
2. Repo-root `scripts/plan_card.py` / `scripts/backlog_index.py` become
   small exec shims, so every documented invocation in this repo's
   plans, memory entries, and muscle memory keeps working unchanged.
3. The skill-body call sites gain a two-step resolution cascade:
   repo-root `scripts/<name>.py` when present, else
   `"${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py"` (load-time textual
   substitution — precedent: investing-toolkit / tsundoku SKILL.md
   bodies, loom-pipeline hooks.json). Reference files (`plan-format.md`,
   `family-relay.md`) state the cascade in prose only — `${...}` does
   not expand in files read raw via the Read tool.
4. The one claim this falsifies — finishing SKILL.md:196
   "`backlog_index.py` absent (ships in no plugin)" — is rewritten.
   Census run via `claim_copy_sweep.py`: exactly one live copy; the
   `:195` neighbor is about `check_loom_memory_integrity.py` (stays
   repo-only, stays true); one hit in a shipped plan is a frozen
   historical record, not edited.
5. loom-code 0.70.0 → 0.71.0, loom-pipeline 0.15.0 → 0.16.0 (its
   `family-relay.md` names the script), codex manifests synced,
   version-pin test (`test_docs_review_blocking_class.py`) migrated.

## Current State Evidence

- Forward: SDD SKILL.md:55,124; writing-plans SKILL.md:130; rcr
  SKILL.md:85; brainstorming SKILL.md:73,76; finishing SKILL.md:102,
  196, 294-295 — all `python3 scripts/<name>.py` (target-repo-relative).
- Reverse: no `.py` file imports either script (grep: 0 hits) — both
  pure stdlib, all paths via argv (`plan_card` takes the plan path;
  `backlog_index` takes `--store`, default cwd-relative). Portable as-is.
- Error: the designed fallbacks ("hand-edit only when the script is
  absent" / "backlog-close: index not regenerated") make absence
  survivable but permanent in external repos.
- Data: CI runs `pytest loom-code/scripts/ scripts/ .claude/hooks/`
  (loom-code-ci.yml:115) — tests remain in-lane after the move
  (memory: test-must-land-in-the-ci-lane-its-plugin-runs).
- Boundary: `${CLAUDE_PLUGIN_ROOT}` expands in rendered SKILL.md bodies
  and hooks.json, NOT in reference files read raw (memory:
  claude-skill-dir textual substitution) — hence the prose-only rule for
  reference files.

## Alternatives Considered

1. **Move SSOT into the plugin + repo-root shims** (chosen) — one real
   copy, ships automatically, zero sync duty. Repo precedent: "house
   additions in the owning module".
2. Keep repo-root SSOT + sync a functional copy into the plugin with a
   drift checker (distribute.py pattern) — works, but adds a permanent
   sync duty and drift surface for a tool that belongs to loom-code
   anyway; the distribute.py pattern exists for *cross-plugin* knowledge
   ownership, which this is not.
3. Symlink repo-root → plugin dir — fragile across hosts (Codex mirror,
   Windows), and the plugin cache is a deploy target, not a source.
4. Status quo (skills teach, repos hand-copy) — the defect itself.

Grounding is repo-internal precedent (verified live this session);
external search adds nothing to a plugin-packaging mechanism question.

## Decision

Move the two scripts + their tests into `loom-code/scripts/`, leave
exec shims at the old paths, teach the 10 skill-body call sites the
two-step cascade, prose-update the 2 reference files, fix the one
falsified claim, bump both plugins.

We will NOT: ship `check_loom_memory_integrity.py` or any other
repo-root script (out of this defect's scope — that checker guards this
repo's own memory store); redesign the milestone layer kumiko also
lacks (separate backlog entry); fix the two OPEN script-internal defects
(CJK gloss join, duplicate frontmatter keys — they ride along unchanged).

## Out of Scope

- Milestone/roadmap layer between plan-level `Stage:` and
  `DIRECTION.md` (the second, deeper gap the kumiko session surfaced) —
  design question, goes to backlog.
- `check_loom_memory_integrity.py`, `claim_copy_sweep.py`,
  `sync_codex_manifests.py` — stay repo-only by design.
- Backfilling `docs/loom/backlog/` / `DIRECTION.md` into external repos
  (opt-in per repo, unchanged).
- The two OPEN backlog entries on these scripts' internals.

## Design-side on-ramp

Negative guard: mechanism fix to existing tooling (bug-fix shaped) —
upstream-artifact walk skipped silently. Backlog ready check: ran
`--ready` context via store grep; the two OPEN entries touching these
scripts noted above; no COMMITTED-NEXT conflict.

## Open Questions

None blocking. (Whether external repos should get the shims too is moot
— the cascade's plugin leg covers them.)
