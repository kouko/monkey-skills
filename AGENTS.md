# Monkey Skills

Personal agent skills organized into two plugins: domain teams and Obsidian workflows.

## Architecture: Checkpoint-Based Quality Gates + Open Domain Knowledge

```
Team Skill (checkpoint orchestrator)
  ├── worker (sonnet)    ← execute with protocols/ + standards/
  └── evaluator (opus)   ← judge with checklists/ + rubrics/ + standards/

Domain knowledge (open access, colocated in each team skill directory):
  protocols/   → Step-by-step SOPs (execution guidance)
  checklists/  → Binary pass/fail criteria (gate evaluation)
  rubrics/     → Qualitative flag criteria (gate evaluation)
  standards/   → Baseline rules (shared SSOT)

Role boundaries enforced by behavior, not reading restrictions:
  worker      → produces artifacts, does NOT produce gate verdicts
  evaluator   → produces verdicts, does NOT modify artifacts
```

### Four-Level Quality Gates

| Level | Behavior | Executor |
|-------|----------|----------|
| SELF | Agent self-generates check items | main agent |
| MUST | Auto-trigger, non-skippable | evaluator |
| SHOULD | Auto-trigger, skippable with reason | evaluator |
| MAY | User-requested only | evaluator |

## Commands

<!-- BEGIN command-surface (managed) -->
- **Living-spec structural gate** (every push):
  `python3 loom-code/scripts/check-living-spec-index.py [<repo-root>]` —
  fails rc=1 on any dangling `@req` / malformed tag; runs the advisory
  drift WARN lane alongside.
- **Regenerate the living-spec index**:
  `python3 loom-code/scripts/check-living-spec-index.py --write-index docs/loom/INDEX.md`
  — regenerates `docs/loom/INDEX.md` from the source tree (the
  finishing-step / once-per-branch regen path).
- **Verify the committed index is current** (merge-boundary gate):
  `python3 loom-code/scripts/check-living-spec-index.py --verify-index docs/loom/INDEX.md`
  — byte-identity check vs a fresh regeneration; rc=1 if stale.
- **Check active-req coverage** (merge-boundary gate):
  `python3 loom-code/scripts/check-living-spec-index.py --check-coverage [<repo-root>]`
  — fails rc=1 on any ACTIVE `### Requirement:` with 0 linked tests
  (named on stderr); a `[deferred]` req with 0 tests is surfaced on
  stdout (informational, rc=0). Sound because CI runs it after the green
  pytest gate, so a linked test ≡ a passing test.
- **Check writing-plans scenario coverage** (writing-plans self-check,
  change-folder input only):
  `python3 loom-code/scripts/check_scenario_coverage.py <change-folder> <plan-path>`
  — compares the change-folder's `#### Scenario:` set against the
  plan's `Brief item covered` join keys; rc=1 names every dropped
  scenario on stderr, rc=0 on full coverage (or a vacuous zero-scenario
  folder).
- **Archive a shipped change-folder** (finishing-a-development-branch
  archive-on-close step, orchestrator-only, once per branch):
  `python3 loom-code/scripts/archive_change_folder.py <change-id> [root] [--date YYYY-MM-DD]`
  — moves `docs/loom/<change-id>/` to
  `docs/loom/archive/<date>-<change-id>/` and stamps `status: archived`
  into the moved `proposal.md`'s frontmatter; rc=1 with actionable
  stderr on any refusal (missing source, already-archived, destination
  collision, unsafe change-id/date), zero filesystem mutation on
  refusal.
- **Sync a plugin's Codex manifest from its Claude SSOT**:
  `python3 scripts/sync_codex_manifests.py <plugin>` — copies the 8
  shared fields (name/version/description/author/homepage/repository/
  license/keywords) from `<plugin>/.claude-plugin/plugin.json` into
  `<plugin>/.codex-plugin/plugin.json`, preserving the Codex-only
  `interface` block verbatim.
- **Check Codex-manifest drift** (CI gate):
  `python3 scripts/sync_codex_manifests.py --check <plugin>` — pure
  read; rc=0 when the Codex manifest's shared fields match the Claude
  SSOT, rc=1 on divergence.
- **Rebuild the loom-pipeline driver asset**:
  `python3 loom-pipeline/scripts/build_driver.py` — concatenates
  `loom-pipeline/scripts/driver_NN_*.js` sources in filename order into
  `loom-pipeline/skills/using-loom-pipeline/assets/loom-pipeline.js`;
  `--out <path>` builds to an alternate path instead.
- **Drive loom-pipeline batch mode's queue bookkeeping**:
  `python3 loom-pipeline/scripts/batch_queue.py {next|mark|mark-running|reconcile|reset|force-fail|status}` —
  deterministic dispatcher-loop CLI over `docs/loom/QUEUE.toml` (human
  intent) and `docs/loom/queue-state.json` (machine state); `next` emits
  ready-to-use `Workflow` args, `mark` records done/failed, `status`
  prints a one-screen queue overview; `mark-running` records runId +
  session-dir right after `Workflow()` returns; `reconcile` (also run at
  the top of `next`, never in `status`) checks RUNNING entries against
  wf-record evidence, auto-FAILing on definitive failed/killed evidence
  and flagging `SUSPECT`/`SUSPECT-COMPLETE` for a human operator; `reset`
  and `force-fail` are the human-operator recovery verbs for stuck or
  confirmed-dead entries.
- **Check the loom-memory store's §Index invariants**:
  `python3 scripts/check_loom_memory_integrity.py [--store docs/loom/memory]`
  — validate-only, stdlib-only; fails rc=1 and names every offender when a
  body file has no index line, an index line points to a missing file, a
  filename diverges from its frontmatter `name`, or an index description
  isn't byte-identical to its frontmatter `description`; rc=0 when clean.
<!-- END command-surface (managed) -->

## Plugin: domain-teams

### Entry Point
- `using-domain-teams` — Route to the right domain team

### Teams
- `planning-team` — Cross-domain project planning (企画) with Completeness + Consistency gates
- `code-team` — Code development with Security + Architecture + Quality + Spec gates
- `docs-team` — Documentation and codebase assessment (MAY gates only)
- `qa-team` — Test strategy and planning with Test Plan Completeness + Strategy Quality gates
- `devops-team` — Deployment and infrastructure with Deployment Safety + IaC Quality gates
- `design-team` — Design with Accessibility + UX/UI gates
- `research-team` — Research with Citation + Quality gates

### Agents (shared across domain teams)

| Agent | Role | Model |
|-------|------|-------|
| `worker` | Generic task executor (protocols + standards) | sonnet |
| `evaluator` | Generic quality evaluator (checklists + rubrics + standards) | opus |

## Plugin: obsidian

### Skills
- `using-obsidian` — Entry point and routing guide
- `obsidian-daily` — Start the day with vault context
- `obsidian-vault-setup` — Interactive vault configurator
- `obsidian-tldr` — Save conversation summary to vault
- `obsidian-file-intel` — Extract content from files into Obsidian notes
- `obsidian-mermaid-visualizer` — Create Mermaid diagrams
- `obsidian-excalidraw-diagram` — Generate Excalidraw diagrams
- `obsidian-canvas-creator` — Create Canvas files
- `dashboard-design` — Dashboard design workflow

### Agents

| Agent | Role | Model |
|-------|------|-------|
| `obsidian-vault-organizer` | Vault maintenance (standalone) | haiku |

## Plugin: philosophers-toolkit (v0.1.0 — roadmap only)

Philosophical thinking frameworks for problem clarification and deeper reasoning.
See `philosophers-toolkit/ROADMAP.md` for planned skills.

## Installation

See `.codex/INSTALL.md` for Codex, `gemini-extension.json` for Gemini CLI.
