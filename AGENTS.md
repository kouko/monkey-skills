# Monkey Skills

Personal agent skills organized into multiple plugins — domain teams, Obsidian workflows, the loom family, investing/research toolkits, and more.

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
- **Check an intent's Open questions gate** (write-spec / write-plan
  intake self-check):
  `python3 loom-code/scripts/check_open_questions.py <intent-path>` —
  scopes the scan to the intent's `## Open questions` section only
  (a token outside that section — prose, a fenced code-block example —
  is never inspected; heading detection and the entry scan are both
  fence-aware); rc=1 on any `[OPEN]` entry (its `OQ-<n>` named on
  stderr), on an absent or duplicated `## Open questions` heading, on a
  present-but-bare or prose-only section, on a line that ATTEMPTS an
  entry — an `OQ-<n>` id followed by an opening `[` — but fails the
  strict `- OQ-<n> [OPEN|RESOLVED] — <text>` grammar, or on the pinned
  `N/A — no unresolved question: <reason>` line missing its reason;
  rc=0 when every well-formed entry is `[RESOLVED]` or the N/A line is
  well-formed. Grammar SSOT: the `intent` artifact schema in
  `loom-code/contract/manifest.yaml` + `loom-code/contract/templates/intent.md`
  — not restated here.
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
- **Check standalone plugin filesystem boundaries** (CI gate):
  `python3 scripts/check_plugin_boundaries.py loom-code` and
  `python3 scripts/check_plugin_boundaries.py loom-design` — scan each
  installable root independently; fail on relative Markdown links that escape
  that root or references to another loom plugin's private hooks, skills, or
  scripts. Changelogs, research notes, and `TECH-SPEC.md` are historical
  records and are outside the install-runtime scan.
- **Verify isolated loom installs**:
  `python3 -m pytest scripts/test_loom_plugin_install_layout.py -q` — copies
  each plugin into an unrelated install root and verifies standalone
  behavior; manifest tests separately forbid a mandatory sibling dependency.
- **Run the dbt-wiki test suite**:
  `python3 -m pip install -r dbt-wiki/tests/requirements.txt && python3 -m pytest dbt-wiki/tests/ -v -m "not e2e"`
  — covers the L2 end-to-end harness (`dbt-wiki/tests/fixtures/l2-harness/`,
  a synthetic dbt-duckdb project) and its shared `dbt_build` pytest fixture
  (`dbt-wiki/tests/conftest.py`). `-m "not e2e"` excludes BOTH real headless
  `claude -p` validation runs — `test_e2e_validation.py` (W1 L2-harness plan
  Task 11) and `test_e2e_sparse_comment_validation.py` (G1 sparse-comment
  plan Task 3); each spends real quota. The suite shells out to `dbt`, so the
  venv's `bin` must be on `PATH`, not just its interpreter. Run manually; the
  `test-dbt-wiki.yml` workflow does NOT cover this directory (it globs
  `dbt-wiki/skills/*/assets/*_test.py` only) — wiring it in is Phase 4
  (U1/U2) of the dbt-wiki quality campaign, not yet built.
- **Check the loom-memory store's §Index invariants**:
  `python3 scripts/check_loom_memory_integrity.py [--store docs/loom/memory]`
  — validate-only (default), stdlib-only; fails rc=1 and names every offender
  when a body file has no index line, an index line points to a missing
  file, a filename diverges from its frontmatter `name`, an index
  description isn't byte-identical to its frontmatter `description`, or
  two index lines point at the same body file; rc=0 when clean.
  `python3 scripts/check_loom_memory_integrity.py --write`
  regenerates the `## Index` section from every entry's frontmatter and
  writes it back in place. `--check` diffs the committed `## Index` against
  a freshly rebuilt one and fails rc=1 on any drift without writing —
  the CI-safe form.
- **Run the skill-refactor package gate**:
  `python3 skill-dev-toolkit/skills/skill-refactor/scripts/package_gate.py {export|verify|account|reduce} [arguments]`
  — JSON CLI over the tested immutable-baseline, verification, whole-package
  accounting, and layered-evidence APIs. `reduce` reads evidence JSON from
  stdin and emits only `PASS`, `FAIL`, or `UNGRADABLE`; see the bundled
  package-resource protocol for each subcommand's required arguments.

- **Run the loom checker** (the one deterministic gate; host hooks call it):
  `python3 loom-code/scripts/loom_checker.py --list-rules` prints every rule
  id as `<area>.<name>` and is the SSOT for what the checker enforces — the
  rule list is deliberately not restated anywhere else, in this file least of
  all. Each rule is a RECOMPUTE against the working tree or the git history,
  never a claim read out of a document.
- **Recompute the mechanism population** (CI gate, concept-model §11's
  admission rule):
  `python3 loom-code/scripts/check_mechanisms.py --baseline <ref>` — recomputes
  the five mechanism classes (skill directories, checker rule ids, hooks.json
  entries, contract-manifest declarations, `<!-- gate: … -->` prose gates) and
  diffs them against `docs/loom/evidence/mechanisms.yaml`. rc=1 on an
  unregistered mechanism, a registered mechanism the recompute cannot find, a
  mechanism with no working `eval:`, or a net-count rise whose CHANGELOG entry
  carries no `budget-exception: <mechanism-id> — <reason>` line.
  `--measure` instead prints the skill count, the artifact-type count and the
  session-start injection word count, and exits 1 when the word count exceeds
  the `session-start-baseline:` recorded in `docs/loom/KICKOFF-DEFAULTS.md`.
- **Scaffold the Codex hook package into an adopting repo** (one-time, done
  by the station itself):
  `python3 loom-code/scripts/codex_scaffold.py <repo-root>` — writes
  `.codex/hooks.json` plus the checker copy it needs (`loom-checker` shim,
  `loom_checker.py`, `git_exec.py`, `contract/`). The command string in
  `hooks.json` is a fixed relative path carrying no version, so a checker
  upgrade does not re-trigger Codex's trust prompt; the version stamp lives
  inside the copied files.
- **Check runtime prose contracts cite nothing repo-local** (CI gate):
  `python3 loom-code/scripts/check_contract_citations.py` — a runtime prose
  contract under the loom skill/agent trees must not cite this repository's
  own development records under `docs/`; the script owns the full rule and
  the shrinking `DEBT_LIST` of files that already violated it when the rule
  landed.
- **Check doc citations resolve** (CI gate):
  `python3 loom-code/scripts/check_doc_citations.py <file.md> [more.md …]` —
  every backtick `path:line` citation, and every backtick `path` paired with
  a same-line quoted anchor, must resolve against the repo root. CI runs it
  over the operative loom prose only; the frozen stores under
  `docs/loom/{plans,specs,backlog,design,archive}/` and `docs/loom/evidence/`
  are historical records and are deliberately out of scope.
- **Check skill cross-references resolve** (CI gate):
  `python3 loom-code/scripts/check-skill-crossrefs.py` — every relative
  markdown link in a SKILL.md must point at a file that exists.

<!-- END command-surface (managed) -->

## The loom family (loom-code / loom-design / loom-workflow) — 1.0 flow

One change moves through seven stations. Each station is a skill; each
station's SKILL.md opens with a station-summary table naming its inputs,
its artifact, who decides, and when the checker and the checkpoint fire.

```
capture-intent ─► write-spec ─┐            (loom-design; only when needs-design: yes)
                              ▼
                        write-plan ─► build ─► review ─► ship   (loom-code)
                              ▲                   │
                        maintain ◄────────────────┘  (an incident becomes a new intent)
```

- **Artifacts** (five, plus git): `docs/loom/intent/<change-id>.md`,
  and inside `docs/loom/<change-id>/`: `spec.md`, `plan.md`, `review.json`,
  `evidence/`. Nothing else is a per-change artifact. Store layout and the
  frozen pre-1.0 stores: `docs/loom/README.md`.
- **Three human decision points, and no others**: ① restate-and-confirm the
  intent (one-way-door questions folded in), ② for a product change, confirm
  the user-visible behaviour in the spec, ③ accept the blind-run report.
  Everything else the agent decides and records as `agent-decided`.
- **Quality comes from three verification actions only** — read (≥2
  fresh-context reviewers), blind run, adversarial probes — run at a
  checkpoint review, never as a per-task three-arm ceremony. Verdicts land in
  `review.json`.
- **One deterministic gate**: `loom_checker.py`, invoked by host hooks
  (Claude Code plugin hooks; on Codex, a scaffolded `.codex/hooks.json` plus a
  checker copy). Every rule is a recompute. `--list-rules` is the rule SSOT.
- **Prose is advisory**: only a paragraph marked `<!-- gate: <id> -->` counts
  as a gate, and unmarked prose may not be used as one.
- Concept model (the design this shape came from):
  `docs/loom/2026-09-02-simple-loom-flow/concept-model.md`.

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

## Plugin: philosophers-toolkit (v1.0.4 — 12 skills)

Philosophical thinking frameworks for problem clarification and deeper
reasoning — 12 shipped skills (11 frameworks + 1 router).
`philosophers-toolkit/ROADMAP.md` is a historical design record that
holds the original planned-frameworks list; future planned work, when
it exists, starts as an intent in `docs/loom/intent/` (the backlog store is frozen).

## Installation

See `.codex/INSTALL.md` for Codex, `gemini-extension.json` for Gemini CLI.
