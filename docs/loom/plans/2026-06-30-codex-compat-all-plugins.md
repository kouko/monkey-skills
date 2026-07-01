# Plan: Codex compatibility repo-wide (all eligible plugins)

Source brief: docs/loom/specs/2026-06-30-codex-compat-all-plugins.md
Total tasks: 11 (T4 is a per-plugin wide wave over the 21 Batch-A plugins)
Critical-path depth: 5 (T1 → T2 → T3 → T4 → T5) ≤5
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-30, round 2 — depth 5 verified, all Independent:true pairs disjoint)

## Eligible-plugin data (Batch A — 21 plugins)
ascii-graph-toolkit, briefing-toolkit, copywriting-toolkit, dbt-wiki,
deconstruct-toolkit, domain-teams, four-dx-coach, gws-toolkit, investing-toolkit,
legal-toolkit, loom-interface-design, loom-product-principles, loom-spec, obsidian,
philosophers-toolkit, repo-wiki, research-toolkit, skill-dev-toolkit,
systems-thinking-toolkit, translation-toolkit, tsundoku
(loom-code = already Codex; consolidated in T8. dev-workflow = Batch B / T10–T11.
collab-toolkit + salesforce-toolkit = Batch C / out of scope.)

## Task 1 — port the sync engine to a repo-level module (sync + --check)
- Description: Create `scripts/sync_codex_manifests.py` — copy the 8 SHARED_FIELDS from `<plugin>/.claude-plugin/plugin.json` (SSOT) into `<plugin>/.codex-plugin/plugin.json`, preserving the Codex-only `interface` block verbatim; with a `--check` pure-read drift mode. Port the proven logic from `loom-code/scripts/sync_codex_manifest.py` (same field set, stdlib only).
- Module: scripts/sync_codex_manifests.py
- Files touched: scripts/sync_codex_manifests.py, scripts/test_sync_codex_manifests.py
- Context paths:
  - loom-code/scripts/sync_codex_manifest.py
  - loom-code/scripts/test_sync_codex_manifest.py
- Acceptance:
  - RED: scripts/test_sync_codex_manifests.py::test_sync_copies_shared_fields_preserving_interface fails (undefined) — on a fixture plugin (tmp_path) with a Claude manifest + a Codex manifest carrying an `interface` block.
  - GREEN: post-sync the Codex manifest's 8 shared fields equal the Claude SSOT, `interface` is byte-identical; `--check` exits 0 in-sync, non-zero after mutating a shared field.
- External surfaces: none (stdlib json/pathlib/argparse only — match loom-code's no-third-party constraint).
- Dependencies: none
- Independent: false
- Brief item covered: "ONE shared repo-level script ... copied from .claude-plugin (SSOT) → .codex-plugin, preserving the interface block"

## Task 2 — add --scaffold mode + the eligible-plugin list to the engine
- Description: Extend the engine with `--scaffold` (when a plugin lacks `.codex-plugin/plugin.json`, create one = 8 shared fields + mechanically-derivable interface fields [displayName=name, developerName=author, websiteURL=repository+"/tree/main/"+name (canonical GitHub subdir form — NOT bare repository+/name, which 404s)] + judgment fields [longDescription, category, capabilities, defaultPrompt, brandColor] set to literal `"TODO"`), and a `CODEX_ELIGIBLE` constant (21 Batch-A names + loom-code; excludes dev-workflow / collab-toolkit / salesforce-toolkit) so `--all` iterates exactly that set.
- Module: scripts/sync_codex_manifests.py
- Files touched: scripts/sync_codex_manifests.py, scripts/test_sync_codex_manifests.py
- Context paths:
  - scripts/sync_codex_manifests.py
  - loom-code/.codex-plugin/plugin.json   # interface-block schema template
- Acceptance:
  - RED: scripts/test_sync_codex_manifests.py::test_scaffold_seeds_mechanical_fields_and_todo_placeholders AND ::test_eligible_list_excludes_hook_and_mcp_plugins fail.
  - GREEN: `--scaffold` seeds mechanical fields + "TODO" judgment placeholders; `CODEX_ELIGIBLE` contains the 21 + loom-code and excludes dev-workflow/collab/salesforce.
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "the 8 mechanical shared fields + mechanically-derivable interface fields + placeholders for the judgment ones"

## Task 3 — generate Batch-A Codex manifests via the engine
- Description: Run `python3 scripts/sync_codex_manifests.py --scaffold --all` to create `.codex-plugin/plugin.json` for the 21 Batch-A plugins (judgment fields = TODO for now), then `--check --all` to prove sync. Commit the 21 generated manifests.
- Module: (generated artifacts) Batch-A */.codex-plugin/plugin.json
- Files touched: ascii-graph-toolkit/.codex-plugin/plugin.json, briefing-toolkit/.codex-plugin/plugin.json, … (all 21 Batch-A plugins)
- Context paths:
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: `python3 scripts/sync_codex_manifests.py --check --all` exits non-zero (manifests absent).
  - GREEN: all 21 `.codex-plugin/plugin.json` exist with shared fields synced; `--check --all` exits 0.
- External surfaces: none
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "creates/syncs each eligible plugin's .codex-plugin/plugin.json"

## Task 4 — (WIDE WAVE, one task per Batch-A plugin) author the interface judgment fields
- Description: For EACH of the 21 Batch-A plugins, replace the TODO placeholders (longDescription, category, capabilities, defaultPrompt, brandColor) with authored values derived from that plugin's `description` + its skills (LLM-draft, human-reviewed). One implementer task per plugin; all `Independent: true` — each touches only its own `.codex-plugin/plugin.json` (mutually disjoint).
- Module: <plugin>/.codex-plugin/plugin.json  (one plugin per task)
- Files touched: <plugin>/.codex-plugin/plugin.json  (single file per task; disjoint across the wave)
- Context paths:
  - <plugin>/.claude-plugin/plugin.json
  - <plugin>/skills/*/SKILL.md
  - loom-code/.codex-plugin/plugin.json   # exemplar interface block
- Acceptance:
  - RED: grep finds literal "TODO" in `<plugin>/.codex-plugin/plugin.json`.
  - GREEN: no "TODO" placeholders remain; description ≤1024; `python3 scripts/sync_codex_manifests.py --check <plugin>` exits 0 (interface preserved, shared fields synced).
- External surfaces: none
- Dependencies: Task 3 completes first
- Independent: true   # per-plugin wave; tasks mutually disjoint (single own-manifest file each)
- Brief item covered: "Author each plugin's interface block (judgment fields)"

## Task 5 — live-verify Batch A on Codex 0.139.0 + record + INSTALL note
- Description: Install the repo into Codex 0.139.0 (`codex plugin marketplace add .` → `codex plugin add <plugin>@monkey-skills`) for a representative sample (≥5 across different plugin shapes), confirm skill discovery, and **append** results to a fresh `docs/loom/codex-verification.md` (verified plugins + the working install command surface + any per-plugin fix); then update `.codex/INSTALL.md` to point at it + note the Batch-C MCP deferral. Resolves the brief's local-marketplace-install Open Q.
- Module: docs/loom/codex-verification.md
- Files touched: docs/loom/codex-verification.md, .codex/INSTALL.md
- Context paths:
  - docs/loom/specs/2026-06-14-codex-compat-completion.md   # the loom-code ritual precedent
  - .codex/INSTALL.md
- Acceptance:
  - RED: docs/loom/codex-verification.md absent.
  - GREEN: the doc records ≥5 Batch-A plugins installed on Codex 0.139.0 with skills discovered + the exact install commands; .codex/INSTALL.md links it + states the Batch-C caveat.
- External surfaces: Codex CLI 0.139.0 (manual ritual — not CI-automatable).
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: "live-verified to load + skills discoverable on Codex 0.139.0"

## Task 6 — generalize the drift hook to all .codex-plugin manifests
- Description: Generalize `.claude/hooks/check-codex-manifest-drift.sh` to fire on ANY `*/.codex-plugin/plugin.json` or `*/.claude-plugin/plugin.json` edit and run `scripts/sync_codex_manifests.py --check <plugin>` (was loom-code-only path match).
- Module: .claude/hooks/check-codex-manifest-drift.sh
- Files touched: .claude/hooks/check-codex-manifest-drift.sh
- Context paths:
  - .claude/hooks/check-codex-manifest-drift.sh
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: editing a Batch-A `.codex-plugin/plugin.json` does not trigger the drift check (hook case-matches only loom-code paths).
  - GREEN: the hook's case-match covers all `*/.codex-plugin/plugin.json` paths and invokes `--check <plugin>`.
- External surfaces: none
- Dependencies: Task 3 completes first
- Independent: true   # disjoint files from T7 (CI yaml), T4 (manifests), T9 (test)
- Brief item covered: "Extend the drift hook ... repo-wide"

## Task 7 — extend the CI drift-gate to --check --all
- Description: Update the CI workflow that runs the Codex-manifest drift gate to call `python3 scripts/sync_codex_manifests.py --check --all` (was loom-code-only).
- Module: .github/workflows/<codex-drift-gate>.yml
- Files touched: .github/workflows/<codex-drift-gate>.yml
- Context paths:
  - .github/workflows/   # locate the existing drift-gate workflow
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: the CI drift gate runs loom-code-only `--check`; a drifted Batch-A manifest would pass CI.
  - GREEN: the CI step runs `--check --all`; a drifted Batch-A manifest fails the gate.
- External surfaces: GitHub Actions (CI workflow YAML — declared, not run locally).
- Dependencies: Task 3 completes first
- Independent: true   # disjoint from T6 (hook .sh) and T9 (test)
- Brief item covered: "Extend the drift hook + CI gate repo-wide"

## Task 8 — consolidate loom-code onto the shared engine (delete self-local copy)
- Description: Delete `loom-code/scripts/sync_codex_manifest.py`; retarget `loom-code/scripts/test_sync_codex_manifest.py` IN PLACE to import/exercise the shared `scripts/sync_codex_manifests.py` (keep loom-code's test self-local — do NOT fold into the shared test file, to preserve disjoint Files touched). Verify loom-code's Codex manifest output is byte-unchanged.
- Module: loom-code/scripts/
- Files touched: loom-code/scripts/sync_codex_manifest.py (delete), loom-code/scripts/test_sync_codex_manifest.py (retarget)
- Context paths:
  - loom-code/scripts/sync_codex_manifest.py
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: `git ls-files` shows loom-code/scripts/sync_codex_manifest.py (two sync impls coexist).
  - GREEN: the self-local script is deleted, `scripts/sync_codex_manifests.py --check loom-code` exits 0 (byte-unchanged output), loom-code's retargeted test + the full suite stay green.
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: true   # Files touched are loom-code/scripts/* only — disjoint from all others
- Brief item covered: "Consolidate loom-code onto the shared script (delete its self-local copy — SSOT)"

## Task 9 — repo-level sync regression test (--check --all in CI even off the hook path)
- Description: Add `scripts/test_sync_codex_manifests.py::test_all_eligible_codex_manifests_in_sync` — enumerate `CODEX_ELIGIBLE`, assert `--check <plugin>` exit 0 for each, so any future drift fails the test suite independently of the git hook.
- Module: scripts/test_sync_codex_manifests.py
- Files touched: scripts/test_sync_codex_manifests.py
- Context paths:
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: scripts/test_sync_codex_manifests.py::test_all_eligible_codex_manifests_in_sync fails (no such test).
  - GREEN: the test enumerates eligible plugins and asserts `--check` exit 0 for each; fails on any drift.
- External surfaces: none
- Dependencies: Task 3 completes first
- Independent: false   # appends to scripts/test_sync_codex_manifests.py, the same file T1/T2 build — sequential after them
- Brief item covered: "drift-guarded ... repo-wide drift hook + CI gate"

## Task 10 — Batch B: dev-workflow Codex manifest + interface
- Description: Add dev-workflow to a generation run (`--scaffold dev-workflow`) and author its interface judgment fields. (Hook-key verification is T11.) dev-workflow is not in `CODEX_ELIGIBLE` Batch-A; generate it explicitly here.
- Module: dev-workflow/.codex-plugin/plugin.json
- Files touched: dev-workflow/.codex-plugin/plugin.json
- Context paths:
  - dev-workflow/.claude-plugin/plugin.json
  - dev-workflow/skills/*/SKILL.md
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: dev-workflow has no `.codex-plugin/plugin.json`.
  - GREEN: manifest generated, interface authored (no TODO), `--check dev-workflow` exits 0.
- External surfaces: none
- Dependencies: Task 2 completes first
- Independent: true   # disjoint file from Batch-A waves and loom-code
- Brief item covered: "Batch B — dev-workflow (1): has hooks → needs the loom-code hook-contract treatment"

## Task 11 — Batch B: dev-workflow hook-key verification + Codex live-verify
- Description: Verify dev-workflow's bundled `hooks/hooks.json` emits `hookSpecificOutput.additionalContext` (the host-agnostic key loom-code uses) so the hook works on Codex; align it if drifted (do NOT fork a Codex-only path). Live-verify on Codex 0.139.0 and append to codex-verification.md.
- Module: dev-workflow/hooks/hooks.json
- Files touched: dev-workflow/hooks/hooks.json (only if key-alignment needed), docs/loom/codex-verification.md
- Context paths:
  - loom-code/hooks/hooks.json
  - dev-workflow/hooks/
- Acceptance:
  - RED: dev-workflow's hook key is unverified for Codex.
  - GREEN: the hook emits `hookSpecificOutput.additionalContext`; dev-workflow live-verified on Codex 0.139.0 (appended to codex-verification.md).
- External surfaces: Codex CLI 0.139.0 (manual ritual).
- Dependencies: Task 10 completes first
- Independent: false
- Brief item covered: "Batch B ... needs the loom-code hook-contract treatment (hookSpecificOutput.additionalContext)"

## Notes
- Critical path: T1 → T2 → T3 → T4 → T5 (depth 5). Off-path leaves: T6/T7/T9 (dep T3, level 4), T8 (dep T1, level 2), T10 (dep T2, level 3) → T11 (level 4). Longest chain = 5.
- T4 is a data-driven WIDE wave (21 per-plugin tasks, all Independent:true, single own-manifest disjoint touches) = ONE dependency level. dispatching-parallel-agents expands it over the eligible list.
- `docs/loom/codex-verification.md` is written by T5 (creates) then T11 (appends) — at different DAG depths, never two Independent:true writers at once. Convention: **append-don't-overwrite** (each task adds a section, never rewrites the file).
- Non-TDD-shaped tasks (T4 content authoring; T5/T11 live Codex ritual) carry mechanical GREENs (no-"TODO" + `--check` exit 0; a recorded ≥5-entry verification doc) — each has an observable, falsifiable acceptance.
- Batch C (collab-toolkit + salesforce-toolkit) is OUT OF SCOPE per the brief — a separable follow-on plan gated on the plugin-MCP-auto-registration live test.
