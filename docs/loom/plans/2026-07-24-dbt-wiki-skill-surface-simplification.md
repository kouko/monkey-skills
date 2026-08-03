# Plan: dbt-wiki skill-surface simplification — router + sync→update rename

Source brief: docs/loom/specs/2026-07-24-dbt-wiki-skill-surface-simplification.md
Total tasks: 5
Critical-path depth: 3 (≤5) — T1→{T2|T3}→T5; T4 independent
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-24, round 1, 14/14 checks)

Notes:
- Change-folder binding: N/A, loudly — no `docs/loom/<change-id>/` bound;
  input is the brainstorming brief only (non-archived change-folders present
  belong to unrelated shipped investing arcs).
- SKILL.md tasks (T2/T3) are prose-contract authoring, not code. Their
  "RED/GREEN" uses the repo's SKILL pattern: grep-marker for structural
  presence + a fresh-context cold-read dogfood for behavioral correctness +
  the folder-structure hook + token-cap check. Same technique as the
  obsidian wiki-update arc.
- No new runnable verb: the phantom-column gate reuses the EXISTING
  `lint_identifier_fidelity.py` (drop-in JSON+exit-code); T2 wires it as
  a prose step in update's contract, no new script/aggregator.
- Repo memory honored: git mv preserves history (rename); mine OLD names
  after a rename (zero operative `sync`-as-skill survivors); never
  `git add -A`; version bump + codex manifest sync required for skill
  content changes.
- Kickoff decision RESOLVED (user 2026-07-24): minor bump 3.2.1 → 3.3.0
  + loud CHANGELOG BREAKING note (not major).
- T4 spec correction (2026-07-24, post-PASS, additive/schema-safe —
  re-review skipped): dbt-wiki test files are self-executing smoke
  scripts (`if __name__=="__main__": sys.exit(main())`), NOT pytest
  modules — `python3 -m pytest` collects zero / crashes on import.
  T4's CI invokes each directly (`python3 <file>` in a glob loop,
  fail on non-zero exit); all three verified green run directly
  (8/8+7/7+11/11). Same task/module/deps — only the invocation
  mechanism corrected.

## Task 1 — Rename skills/sync → skills/update (git mv + zero-survivor sweep)
- Description: `git mv dbt-wiki/skills/sync dbt-wiki/skills/update`
  (preserve history); update the skill's own `name:` frontmatter
  sync→update and its self-references; sweep the whole `dbt-wiki/` plugin
  for operative old-name references (cross-skill `→ sync` hints, prose
  "the sync skill", `skills/sync/` paths, codex-mirror manifest) and
  retarget them to `update`. A CHANGELOG history line naming the old
  `sync` is the ONLY sanctioned survivor.
- Module: dbt-wiki/skills/update (the rename operation)
- Files touched: dbt-wiki/skills/update/SKILL.md (mv'd from sync/),
  dbt-wiki/skills/rescan/SKILL.md, dbt-wiki/skills/redistill/SKILL.md,
  dbt-wiki/skills/init/SKILL.md, dbt-wiki/skills/query/SKILL.md,
  dbt-wiki/skills/review/SKILL.md, dbt-wiki/skills/ingest/SKILL.md,
  dbt-wiki/skills/pack/SKILL.md, dbt-wiki/README.md
  (+ any other `dbt-wiki/**` file the sweep finds referencing sync)
- Context paths:
  - dbt-wiki/skills/sync/SKILL.md (rename source)
  - dbt-wiki/skills/rescan/SKILL.md (has `→sync` hint, rescan/SKILL.md:4)
- Acceptance:
  - RED: `test -d dbt-wiki/skills/sync` still passes (dir not yet moved)
    AND `grep -rn 'dbt-wiki:sync\|skills/sync\|→ *sync\|the sync skill' dbt-wiki/`
    finds operative survivors
  - GREEN: `dbt-wiki/skills/update/` exists (git-mv history preserved,
    `git log --follow` traces it), `dbt-wiki/skills/sync/` gone,
    the operative-survivor grep returns ZERO hits (CHANGELOG history
    mention exempt), update/SKILL.md `name:` == `update`
- External surfaces: none (git mv + text edits)
- Dependencies: none
- Independent: false
- Brief item covered: "hard-rename `sync`→`update` … plugin-wide
  grep-sweep must leave zero operative survivors of the old `sync` name"
  (Decision / Open Q1 RESOLVED)

## Task 2 — Enrich update SKILL.md into the full maintenance pass
- Description: Author update/SKILL.md as the one maintenance verb — the
  pipeline: (optional) ingest-front → rescan → redistill →
  phantom-column lint gate (run existing `lint_identifier_fidelity.py`,
  surface phantom-columns as a mechanical pre-review gate) →
  review-handoff (present the review queue; do NOT auto-run interactive
  review) → structural scorecard (regenerated pages / phantom count /
  pages awaiting review), in the conversation language. Keep the
  one-way dbt→wiki discipline (never touch dbt/target). Position it in
  the description as THE maintenance verb; rescan/redistill remain
  callable for cost-conscious iteration.
- Module: dbt-wiki/skills/update
- Files touched: dbt-wiki/skills/update/SKILL.md
- Context paths:
  - dbt-wiki/skills/update/SKILL.md (T1 output — renamed sync body)
  - dbt-wiki/skills/rescan/SKILL.md, dbt-wiki/skills/redistill/SKILL.md
    (the steps it orchestrates)
  - dbt-wiki/skills/init/assets/lint_identifier_fidelity.py
    (the phantom-column gate; CLI `[WIKI_DIR] --json`, exit 0/1/2)
- Acceptance:
  - RED: update/SKILL.md lacks the enriched pipeline — grep for the
    lint-gate step + review-handoff + scorecard fails
  - GREEN: contains the full pipeline (ingest→rescan→redistill→
    phantom-lint gate→review-handoff→scorecard); folder-structure hook
    clean; SKILL.md ≤4,500 words; a fresh-context cold-read dogfood has
    an agent correctly execute the maintenance flow on a described
    scenario (sequences the steps, runs the lint gate, hands off to
    review rather than auto-certifying)
- External surfaces: none (prose contract; reuses existing lint script)
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "`dbt-wiki:update` = the renamed+enriched
  orchestrator: ingest-front → rescan → redistill → phantom-column lint
  gate → review-handoff → scorecard" (Decision)

## Task 3 — using-dbt-wiki router skill
- Description: Author `dbt-wiki/skills/using-dbt-wiki/SKILL.md` — an
  obsidian-style lightweight routing table (no orchestration): a
  "when to use which" table grouping skills as Setup (init) / Input
  (ingest) / Maintain (**update** as the primary verb; rescan/redistill
  demoted to "advanced — update runs these for you") / Read (query) /
  Certify (review) / Export (pack), plus a Quick Start sequence
  (`init → (ingest) → update → query → review`). Description carries
  zh/ja trigger keywords per family convention. Reference `update` by
  its final name (not sync).
- Module: dbt-wiki/skills/using-dbt-wiki
- Files touched: dbt-wiki/skills/using-dbt-wiki/SKILL.md
- Context paths:
  - obsidian/skills/using-obsidian/SKILL.md (router pattern to mirror)
  - docs/loom/specs/2026-07-24-dbt-wiki-skill-surface-simplification.md
- Acceptance:
  - RED: `dbt-wiki/skills/using-dbt-wiki/SKILL.md` absent
  - GREEN: router present with the grouped routing table (update as
    primary maintain verb, rescan/redistill demoted), Quick Start
    sequence, zh/ja trigger keywords; folder-hook clean; a fresh-context
    cold-read has a first-time user correctly pick `update` for
    "bring my wiki up to date" and `init` for first-time setup
- External surfaces: none (prose contract)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "add `using-dbt-wiki` router (obsidian-style …
  routing table … primary-vs-advanced grouping)" (Decision Committed 1)

## Task 4 — dbt-wiki CI wire-up
- Description: Add a dbt-wiki CI job/step to `.github/workflows/` that
  runs the plugin's pytest suites (the 3 lint tests +
  `reconcile_test.py` in init/assets) — mirroring loom-code-ci's pytest
  step shape. First verify the existing tests pass locally; if any
  bit-rotted, surface as NEEDS_CONTEXT rather than wiring a red suite.
  Ensure `dbt-wiki/**` path triggers the workflow.
- Module: .github/workflows
- Files touched: .github/workflows/test-dbt-wiki.yml (new; or a step in
  an existing appropriate workflow — implementer picks per repo pattern)
- Context paths:
  - .github/workflows/loom-code-ci.yml (pytest step shape prior art)
  - dbt-wiki/skills/init/assets/lint_identifier_fidelity_test.py,
    lint_schema_divergence_test.py, reconcile_test.py
- Acceptance:
  - RED: `grep -rl dbt-wiki .github/workflows/` returns nothing
  - GREEN: a workflow runs `python3 -m pytest` over dbt-wiki's script
    tests; yml parses (`python3 -c "import yaml; yaml.safe_load(...)"`);
    local `pytest` over those test files is green (or bit-rot surfaced)
- External surfaces: GitHub Actions yml (mirror existing pytest step)
- Dependencies: none
- Independent: true
- Brief item covered: "wire dbt-wiki into CI … the 3 lint scripts have
  tests that never run" (Decision prerequisite; Open Q2 RESOLVED
  folded-in)

## Task 5 — Version bump + CHANGELOG (breaking rename) + codex sync
- Description: Bump dbt-wiki plugin version; add a CHANGELOG entry
  covering the three surfaces (BREAKING: `sync` renamed to `update`;
  new `using-dbt-wiki` router; CI wire-up) with the breaking rename
  called out prominently; run `python3 scripts/sync_codex_manifests.py
  dbt-wiki`; update the marketplace/plugin description if the skill
  roster line changed.
- Module: dbt-wiki (ship surface)
- Files touched: dbt-wiki/.claude-plugin/plugin.json,
  dbt-wiki/.codex-plugin/plugin.json, dbt-wiki/CHANGELOG.md
  (+ .claude-plugin/marketplace.json only if the plugin description line changed)
- Context paths:
  - dbt-wiki/CHANGELOG.md (entry format; current 3.2.1)
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: plugin.json version unchanged from 3.2.1 (diff empty)
  - GREEN: version bumped; CHANGELOG entry names the BREAKING sync→update
    rename + router + CI; both manifests synced (`sync_codex_manifests.py
    --check dbt-wiki` exits 0)
- External surfaces: none
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: "hard rename … CHANGELOG marks the breaking
  rename" (Open Q1 RESOLVED) + ship surface for Committed 1 (router)
