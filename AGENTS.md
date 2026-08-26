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
- **Look up the next free requirement id**:
  `python3 loom-code/scripts/check-living-spec-index.py --next-req-id [<repo-root>]`
  — prints `REQ-<max+1>` where max is the highest `\d+` among ALL
  id-form `### Requirement:` headers found across live change-folders +
  archive + the living-spec root (`REQ-1` when none exist), exit 0
  always. LIMIT: scans headers PRESENT, not every id ever minted — a
  retired number is free to be re-minted; this matches the "next
  unused = highest ever seen + 1" minting convention only while no
  declaration is ever deleted.
- **Check writing-plans scenario coverage** (writing-plans self-check;
  two modes, selected by the input you pass — passing both is refused):
  `python3 loom-code/scripts/check_scenario_coverage.py <change-folder> <plan-path>`
  — compares the change-folder's `#### Scenario:` set against the
  plan's `Brief item covered` join keys; rc=1 names every dropped
  scenario on stderr, rc=0 on full coverage (or a vacuous zero-scenario
  folder).
  `python3 loom-code/scripts/check_scenario_coverage.py --brief <brief-path> <plan-path>`
  — brief mode: resolves every task's `Brief item covered` value against
  the `BI-<n>` identifiers the brief declares; rc=1 names each
  unresolvable citation on stderr, rc=0 otherwise, with every declared
  identifier no task cites warned and a coverage count printed. A brief
  declaring no identifiers is announced as legacy mode — that run
  resolved nothing, and says so rather than exiting 0 silently.
- **Check a plan's Open Questions gate** (writing-plans self-check):
  `python3 loom-code/scripts/check_open_questions.py <plan-path>` —
  scopes the scan to the plan's `## Open Questions` section only
  (a token outside that section, e.g. in prose, a Decision Log entry,
  or a fenced code-block example, is never inspected — heading
  detection and the entry scan are both fence-aware); rc=1 on any
  `[OPEN]` entry (its `OQ-<n>` named on stderr), on an absent
  `## Open Questions` heading, on more than one such heading (a
  malformed plan — exactly one is required), on a present-but-bare
  section (heading present, body empty), on a section whose body is
  prose only (no recognizable entry and no N/A line), on a line that
  ATTEMPTS an entry — an `OQ-<n>` id followed by an opening `[`, under
  any bullet (`-`, `*`, `+`, `>`, blockquoted, or none at all) — that
  fails the strict entry grammar (a malformed entry, e.g. wrong/
  lowercase token or a non-`-` bullet, named on stderr), or on the
  pinned `N/A — no unresolved question: <reason>` line missing its
  reason; rc=0 when every well-formed entry is `[RESOLVED]` or the N/A
  line is well-formed (a bare `OQ-<n>` id mentioned in prose, with no
  bracketed-token attempt following it, is not scanned as an entry). A
  reused `OQ-<n>` identifier (the never-renumbered/never-reused rule) is
  warned on stderr, first-wins — a warning only, it never changes rc.
- **Check a plan's `Description`/`RED`/`GREEN` field microstructure**
  (writing-plans self-check):
  `python3 loom-code/scripts/check_field_microstructure.py <plan-path>`
  — walks every `## Task <N> —` block; in a `Description`, `RED` or
  `GREEN`, no prose unit may exceed 300 characters — a unit being the
  field's own first line, or one nested bullet's text folded across
  however many physical lines it wraps to. One cap, the same for all
  three fields and both unit kinds, with no sentence counting and no
  per-field branch. An indented continuation line that is none of
  (nested bullet / markdown table row / a wrapped continuation of the
  nested bullet above it) also violates; a table row ends the preceding
  bullet's wrap window. Plan mode also runs a `Goal:` check: a
  continuation line under the header `Goal:` field shaped as a nested
  bullet or a markdown table row violates (`Goal:` must fold to one
  line, unlike `Description`/`RED`/`GREEN` it carries no length cap).
  rc=1 with every violation (field-microstructure or `Goal:`) named on
  stderr, rc=2 when the plan has no `## Task` headings at all —
  structurally not a plan, distinct from "nothing violated" — rc=0
  when the plan is clean.
  Sentence counting was tried twice and abandoned: counting occurrences
  of `.`/`?`/`!` false-positives on `0.89.0`, `e.g.`, `i.e.` and
  ellipsis, and the boundary heuristic that replaced it false-negatives
  on a lowercase-initial sentence. A character cap has no punctuation
  edge cases to enumerate.
  `--brief <path>` runs a separate check instead: every blank-line-
  delimited prose paragraph (none of whose lines is a heading, list
  item, table row, or blockquote, and none of it inside a fenced code
  block) over 600 characters violates unless a `<!-- narrative:
  <reason> -->` declaration line (non-blank reason) sits directly
  beneath it; `## Current State Evidence` and `## Alternatives
  Considered` are exempt. No checker classifies a paragraph as
  narrative — only the declaration string's presence is checked.
  rc=1 with each violation naming its `## ` section on stderr, rc=2
  when the brief has no `## ` sections at all — structurally not a
  brief, distinct from "nothing violated" — rc=0 when the brief is
  clean.
- **Check a plan's Seam coverage** (writing-plans self-check):
  `python3 loom-code/scripts/check_seam_coverage.py <plan-path>` —
  every task whose `Dependencies` is not "none" must carry a `Seam`
  field with one bullet per incoming edge, matched by `from Task <N>`
  identity; payload-bearing bullets must name `owner:` + `probe:`, and
  the `probe:` value must appear verbatim inside that task's
  `Acceptance` block (substring containment). rc=1 with one
  agent-actionable violation per stderr line; rc=0 when every edge is
  covered or the plan has no dependent tasks (vacuous). Grammar SSOT:
  `loom-code/skills/writing-plans/references/plan-format.md` `#### Seam`.
- **Archive a shipped change-folder, or a single backlog entry file**
  (finishing-a-development-branch archive-on-close step, orchestrator-only,
  once per branch; the file unit is also used to close a
  `docs/loom/backlog/` entry per that store's README.md Archive rule):
  `python3 loom-code/scripts/archive_change_folder.py <identifier> [root] [--date YYYY-MM-DD] [--unit folder|file]`
  — `--unit` defaults to `folder` (`docs/loom/<identifier>/` moves to
  `docs/loom/archive/<date>-<identifier>/`, stamping `status: closed`
  into the moved `proposal.md`'s frontmatter); `--unit file` moves
  `docs/loom/backlog/<identifier>` to `docs/loom/backlog/archive/<identifier>`
  unrenamed, stamping `status: closed` into the moved file itself and
  stripping any `blocked:` field from it (`archived` is retired
  vocabulary and no `archived: <date>` field is written any more). rc=1 with actionable stderr on any refusal
  (missing source, already-archived, destination collision, unsafe
  identifier/date, unrecognized `--unit`), zero filesystem mutation on
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
- **Check standalone plugin filesystem boundaries** (CI gate):
  `python3 scripts/check_plugin_boundaries.py loom-code` and
  `python3 scripts/check_plugin_boundaries.py loom-design` — scan each
  installable root independently; fail on relative Markdown links that escape
  that root or references to another loom plugin's private hooks, skills, or
  scripts. Changelogs, research notes, and `TECH-SPEC.md` are historical
  records and are outside the install-runtime scan.
- **Sync the loom-family policy copies**:
  `python3 scripts/sync_loom_family_contracts.py` — regenerates the packaged
  `family-reception`, `family-relay`, and `plain-relay` contracts for both
  independently installable plugins from `scripts/canonical/loom-family/`.
  `python3 scripts/sync_loom_family_contracts.py --check` is the read-only CI
  drift gate.
- **Verify isolated loom installs and public composition**:
  `python3 -m pytest scripts/test_loom_plugin_install_layout.py
  scripts/test_loom_plugin_composition.py -q` — copies each plugin into an
  unrelated install root, verifies standalone behavior, then proves their
  optional handoff resolves only through plugin-qualified skills and
  project-owned `docs/loom/` artifacts. The composition probe also verifies
  that removing the exported target makes the public skill name stop
  resolving; manifest tests separately forbid a mandatory sibling dependency.
- **Rebuild the loom-pipeline driver asset**:
  `python3 loom-design/scripts/pipeline/build_driver.py` — concatenates
  `loom-design/scripts/pipeline/driver_NN_*.js` sources in filename order into
  `loom-design/skills/using-loom-pipeline/assets/loom-pipeline.js`;
  `--out <path>` builds to an alternate path instead.
- **Drive loom-pipeline batch mode's queue bookkeeping**:
  `python3 loom-design/scripts/pipeline/batch_queue.py {next|mark|mark-running|reconcile|reset|force-fail|status}` —
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
- **Resolve review scope** (the scope input a review station dispatches
  from): `python3 loom-code/scripts/review_scope.py [--repo <path>]`
  (default cwd) — fetches the default branch narrowly, verifies the
  branch's merge-base is still the remote's current tip, and only then
  prints the changed-file list, one path per line, byte-identical to
  `git diff <default-branch>...HEAD --name-only` (three-dot, unchanged);
  rc=0 with the list on stdout. Any way freshness cannot be established
  REFUSES instead of printing a list it cannot vouch for — the shapes are
  enumerated once, in `review_scope.py`'s own module docstring, and are
  deliberately not re-listed here: three separate restatements of that
  population each drifted to a different count before this entry stopped
  restating it. rc=1, the reason on stderr, and — for the stale-base shape,
  where both shas resolved — the concrete
  `git rebase --onto <remote_sha> <old_base> HEAD` remedy also on stderr
  (`<old_base>` = the branch's reflog creation sha when usable, else the
  merge-base plus a recovery caveat line).
  A third rc=1 source exists past the freshness verdict: a fresh base
  whose changed-file diff itself fails — a hardcoded stderr message,
  not a `FreshnessResult.reason`, and no rebase remedy either.
- **Run the Phase 2 loop test suite**:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest scripts/phase2-loop/ -v`
  — covers the execution-stage loop's three pure-logic modules
  (`safety_gates.py` kill switch + scope guard, `journal_writer.py`,
  `queue_entry.py` entry authoring + backlog-description lookup), the
  cross-plugin integration proof against
  `loom-design/scripts/pipeline/batch_queue.py`, and the structural-completeness
  test for `ROUTINE.md` (the only doc in the directory — there is no
  schedule doc). Pure stdlib plus pytest, so no dedicated venv is required;
  this directory IS already covered by CI, since `loom-code-ci.yml` runs
  `pytest … scripts/ …` over the whole tree.
- **Wait for post-PR checks**:
  `python3 loom-code/scripts/post_pr_ci.py --pr <number-or-url> --expected-head <sha>`
  — polls checks bound to that exact PR head and prints one JSON result;
  exit codes distinguish pass, failed/cancelled checks, timeout, no-check
  grace expiry, GitHub operational errors, head drift, and malformed CLI
  arguments (exit 7).
- **Print/update a plan-ledger progress card**:
  `python3 scripts/plan_card.py <plan-path> [--set-status "T<N>=<status>"] [--set-stage "<text>"]`
  — reads (or flips, with a `--set-*` flag) a plan's ledger fields and
  prints the progress card. Resolution is two-tier: the repo-root
  `scripts/plan_card.py` when it exists, otherwise the loom-code
  plugin-shipped copy
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py" …` — where
  `${CLAUDE_PLUGIN_ROOT}` is a load-time substitution performed when
  skill text is rendered, not a run-time shell variable.
- **Validate/regenerate the backlog index**:
  `python3 scripts/backlog_index.py {--ready | --validate | --write | --check}`
  — the backlog store's generator/validator (charter:
  `docs/loom/backlog/README.md`). Same two-tier resolution: repo-root
  `scripts/backlog_index.py` first, else the loom-code plugin-shipped
  copy via `"${CLAUDE_PLUGIN_ROOT}/scripts/backlog_index.py"`
  (load-time substitution, as above).
- **Scaffold the queue layer into a repo (one-time)**:
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/loom_init.py" [repo-root]`
  — creates the backlog charter + KICKOFF-DEFAULTS skeleton + PURPOSE
  skeleton + plans/ + specs/, self-verifies the fresh store via
  `backlog_index.py`, and refuses — writing nothing — when the store,
  the KICKOFF-DEFAULTS skeleton, or the PURPOSE skeleton already
  exists, when the store path exists but is not a directory, or when
  a `plans/`/`specs/` path clashes with a non-directory. Plugin-shipped ONLY —
  a bootstrap verb has no repo-root tier (its precondition is the
  repo lacking the layer). `${CLAUDE_PLUGIN_ROOT}` is a load-time
  substitution, as above.
- **Check a brief's queue relation** (arc-entry gate):
  `python3 loom-code/scripts/check_queue_relation.py <brief-path> [--repo-root <path>]`
  — resolves the brief's `## Queue relation` line against the closed
  grammar — the three canonical forms are enumerated once, in
  `handoff-brief-format.md`'s own `## Queue relation` section (and
  the script's module docstring points there too), and are
  deliberately not re-listed here: `review_scope.py`'s entry above
  already records what happens when a population gets restated in a
  second place — it drifted to a different count three times before
  the entry stopped restating it. Blocks on anything outside that
  grammar, and also blocks a well-formed `in-queue:`/`displaces:` line
  that names an entry absent from the live `status: bet` entries
  under `docs/loom/backlog/` — the existence requirement is the
  SSOT's, not restated here. A repo with no `docs/loom/backlog/`
  directory reports a loud `N/A` on stdout and exits 0, rather than
  gating a repo that never adopted the queue layer. Exit 0 when the
  queue relation resolves (or the repo has no queue layer); exit 1
  for any of four causes its stderr distinguishes — `<brief-path>` is
  missing or is not a regular file (a directory path takes this exit
  too), the brief exists but is unreadable, the backlog store exists
  but is unreadable (NOT the store-absent case above, which exits 0),
  or a store entry's `status:` falls outside the closed status
  vocabulary; exit 2 when the queue relation
  is missing or malformed, or names an absent entry (the question to
  relay verbatim is printed to stderr).
- **Compare loom skill behavior across Claude Code and Codex**:
  `python3 loom-code/scripts/loom_firing_harness.py compare --corpus <corpus.json> --baseline <baseline-root> --candidate <candidate-root> --raw-dir <raw-dir> --out <comparison.json> --replicates 2`
  — runs both plugin roots through both hosts, retains raw JSONL under
  `<raw-dir>`, and writes normalized behavioral comparisons to
  `<comparison.json>`. Use at least two replicates for A/B evidence.
- **Run the skill-refactor package gate**:
  `python3 skill-dev-toolkit/skills/skill-refactor/scripts/package_gate.py {export|verify|account|reduce} [arguments]`
  — JSON CLI over the tested immutable-baseline, verification, whole-package
  accounting, and layered-evidence APIs. `reduce` reads evidence JSON from
  stdin and emits only `PASS`, `FAIL`, or `UNGRADABLE`; see the bundled
  package-resource protocol for each subcommand's required arguments.
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

## Plugin: philosophers-toolkit (v1.0.4 — 12 skills)

Philosophical thinking frameworks for problem clarification and deeper
reasoning — 12 shipped skills (11 frameworks + 1 router).
`philosophers-toolkit/ROADMAP.md` is a historical design record that
holds the original planned-frameworks list; future planned work, when
it exists, lives in `docs/loom/backlog/` entries.

## Installation

See `.codex/INSTALL.md` for Codex, `gemini-extension.json` for Gemini CLI.
