# Plan: docs/loom/memory/ — repo-native practice-memory store

Source brief: docs/loom/specs/2026-07-06-loom-memory-store.md
Total tasks: 9
Critical-path depth: 3 (T2→T3→T9)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-06, round 3, 14/14)

## Task 1 — memory store charter + index README
- Description: Create `docs/loom/memory/README.md` with three sections: (a)
  charter — the jurisdiction table from the brief §Smallest End State item 3
  (backlog→BACKLOG.md / commit-bound decision→git-memory trailers / distilled
  practice→this store / one-off event→sibling folders / harness friction→
  environment-gotchas.md stays) + the pull-not-push rule with its citation
  (git-memory SKILL.md anti-preload decision); (b) format spec — one fact per
  file, frontmatter `name/description/type(practice|gotcha|process)/origin`,
  body with `**Why:**` and `**How to apply:**` lines; (c) `## Index` heading
  with one-line-per-memory convention (initially empty).
- Module: docs/loom/memory/
- Files touched: docs/loom/memory/README.md
- Context paths:
  - docs/loom/specs/2026-07-06-loom-memory-store.md
  - docs/loom/BACKLOG.md (header charter, lines 1-11, for tone parity)
- Acceptance:
  - RED: `grep -q "## Index" docs/loom/memory/README.md` fails (file absent)
  - GREEN: file exists; grep finds the jurisdiction table (all five rows),
    the format spec fence, and the `## Index` heading
- Dependencies: none
- Independent: true
- Brief item covered: "one fact per file … `memory/README.md` = charter +
  index … pull, not push" (Smallest End State items 1-4)

## Task 2 — migration sweep → classification manifest
- Description: Read the 13 loom-relevant machine-local memory files under
  `~/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/` (list them
  via `ls | grep -i loom` plus `reference_design_md_format_and_loom_concept_layer.md`).
  For each, classify every distinct fact inside as: `practice` (distilled
  habit/process/gotcha worth keeping — candidate for the store), `backlog`
  (open item/debt with a re-trigger — candidate for BACKLOG.md), or `skip`
  (already recorded in repo — cite where — or session-only detail). Output a
  manifest at `docs/loom/memory/.migration-manifest.md` (deleted in Task 9):
  one row per fact — source file, verdict, one-line content, destination.
  Known seeds that MUST appear: corpus-`expected`-narrower-than-design →
  backlog; sibling SKILL.md frontmatter 0.3.0 vs plugin.json 0.4.0 → backlog;
  headless branch-plugin testing recipe (wrapper script + neutral dir + probe
  hook first) → practice. Process files in a single pass, one row per fact,
  no deep verification of each claim (classification only); if the sweep
  genuinely exceeds the time-box, return BLOCKED with a split-by-file-batch
  suggestion rather than truncating silently.
- Module: docs/loom/memory/
- Files touched: docs/loom/memory/.migration-manifest.md
- Context paths:
  - ~/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/ (all
    project_loom_*.md, project_ponytail_*.md, reference_design_md_*.md)
  - docs/loom/BACKLOG.md (to detect already-recorded)
- Acceptance:
  - RED: manifest file absent
  - GREEN: manifest exists; every one of the 13 source files has ≥1 row;
    the three known seeds appear with the stated verdicts
- Dependencies: none
- Independent: true
- Brief item covered: "One-time migration: sweep machine-local Claude
  memories" (Smallest End State item 5)

## Task 3 — write practice memories into the store
- Description: For each `practice`-verdict row in the manifest, write one
  memory file at `docs/loom/memory/<slug>.md` in the Task-1 format
  (frontmatter + Why + How to apply; `origin` cites the PR/session the fact
  came from). Append one index line per file to `docs/loom/memory/README.md`
  `## Index`. De-jargon: file bodies are readable standalone (no session
  shorthand). Write mechanically from manifest rows (content already
  curated there); if the practice-row count makes this exceed the time-box,
  return BLOCKED with a split-by-row-batch suggestion.
- Module: docs/loom/memory/
- Files touched: NEW: docs/loom/memory/<slug>.md per manifest practice-row; docs/loom/memory/README.md (Index section only)
- Context paths:
  - docs/loom/memory/.migration-manifest.md
  - docs/loom/memory/README.md (format spec)
- Acceptance:
  - RED: `ls docs/loom/memory/*.md | grep -v README | grep -v .migration` is empty
  - GREEN: one file per practice-verdict row; each passes a frontmatter grep
    (`name:`, `description:`, `type:`, `origin:`); README Index has one line
    per file
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "practice-shaped → new store" (Smallest End State
  item 5)

## Task 4 — write backlog entries
- Description: For each `backlog`-verdict row in the manifest, append an
  entry to `docs/loom/BACKLOG.md` in its established convention (Status /
  Start re-trigger / Origin / What). Must include the two known leaks:
  (a) goal-oriented firing-corpus `expected` narrower than design (origin:
  PR #489 residual, trap #6); (b) sibling plugin SKILL.md frontmatter 0.3.0
  vs plugin.json 0.4.0 (origin: PR #490 loom-interface-design agent flag).
- Module: docs/loom/
- Files touched: docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/memory/.migration-manifest.md
  - docs/loom/BACKLOG.md
- Acceptance:
  - RED: `grep -q "frontmatter" docs/loom/BACKLOG.md` fails
  - GREEN: both known entries present with Status/Start/Origin fields; one
    entry per backlog-verdict manifest row
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "backlog-shaped → BACKLOG.md (incl. the two known
  leaks)" (Smallest End State item 5)

## Task 5 — mirror-reminder hook script + tests (TDD)
- Description: Write `.claude/hooks/test_remind_memory_mirror.py` (pytest,
  same style as test_check_codex_manifest_drift.py: mock PostToolUse stdin
  JSON `{"tool_input": {"file_path": ...}}` piped to the script) asserting:
  (a) Write to a path matching `*/.claude/projects/*/memory/*.md` whose file
  content has frontmatter `type: project` → exit 2, stderr contains a
  mirror reminder naming `docs/loom/BACKLOG.md` and `docs/loom/memory/`;
  (b) same path with `type: user` or `type: feedback` → exit 0 silent;
  (c) MEMORY.md index writes → exit 0 silent; (d) any non-memory-dir path →
  exit 0 silent; (e) malformed/missing stdin → exit 0 (never break the
  session); (f) payload-shape tolerance — a payload whose file path arrives
  under an alternate key (e.g. `{"tool_input": {"path": ...}}`) or with no
  `tool_input` at all → exit 0 silent, never crash (dual-host tolerance RED
  test per brief item 6). Then write `.claude/hooks/remind-memory-mirror.sh`
  to make all tests pass. Test fixtures write temp files (the hook reads the
  written file's frontmatter).
- Module: .claude/hooks/
- Files touched: .claude/hooks/remind-memory-mirror.sh, .claude/hooks/test_remind_memory_mirror.py
- Context paths:
  - .claude/hooks/check-codex-manifest-drift.sh (exit-code + stderr style)
  - .claude/hooks/test_check_codex_manifest_drift.py (test harness style)
- Acceptance:
  - RED: `pytest .claude/hooks/test_remind_memory_mirror.py` fails (script
    absent)
  - GREEN: same command passes all six cases. Command surface: the test
    file is auto-collected by the repo's existing CI pytest sweep over
    `.claude/hooks/` (same lane as test_check_codex_manifest_drift.py) —
    verified by running the pytest command above.
- External surfaces: Claude Code PostToolUse stdin-JSON contract
  (`tool_input.file_path`) — grounded in the existing sibling hook test, not
  memory.
- Dependencies: none
- Independent: true
- Brief item covered: "Mirror reminder hook — dual-host … ONE host-neutral
  hook script" (Smallest End State item 6)

## Task 6 — Claude Code wiring
- Description: Add `.claude/hooks/remind-memory-mirror.sh` as a third
  command entry under the existing PostToolUse `Write|Edit` matcher group in
  `.claude/settings.json` (same shape as the two existing entries).
- Module: .claude/
- Files touched: .claude/settings.json
- Context paths:
  - .claude/settings.json
- Acceptance:
  - RED: `jq -e '.hooks.PostToolUse[0].hooks | map(.command) | any(contains("remind-memory-mirror"))' .claude/settings.json` returns false
  - GREEN: same jq check returns true; `jq . .claude/settings.json` parses
- Dependencies: Task 5 completes first
- Independent: true
- Brief item covered: "wired twice: `.claude/settings.json` (Claude Code
  PostToolUse) …" (Smallest End State item 6)

## Task 7 — Codex wiring
- Description: (a) Copy `.claude/hooks/remind-memory-mirror.sh`
  byte-identically to `.codex/hooks/remind-memory-mirror.sh` (established
  mirror convention — validate-skill-folder-structure.sh precedent); (b) add
  the entry to `.codex/hooks.json` under its PostToolUse `Write|Edit`
  matcher, pointing at the `.codex/hooks/` copy; (c) append a
  live-verify-pending note for the Codex side to
  `docs/loom/codex-verification.md` (execution=truth precedent — wiring
  shipped, real-Codex firing test outstanding).
- Module: .codex/
- Files touched: .codex/hooks.json, .codex/hooks/remind-memory-mirror.sh, docs/loom/codex-verification.md
- Context paths:
  - .codex/hooks.json
  - docs/loom/codex-verification.md
- Acceptance:
  - RED: `jq -e '.hooks.PostToolUse[0].hooks | map(.command) | any(contains("remind-memory-mirror"))' .codex/hooks.json` returns false
  - GREEN: same jq check returns true; `diff .claude/hooks/remind-memory-mirror.sh .codex/hooks/remind-memory-mirror.sh` is empty; codex-verification.md gains the pending note
- External surfaces: Codex CLI hooks engine (v0.124.0+, PostToolUse,
  `.codex/hooks.json`) — verified via developers.openai.com/codex/hooks
  (2026-07-06 search) + repo's existing `.codex/hooks.json` shipping the
  same schema.
- Dependencies: Task 5 completes first
- Independent: true
- Brief item covered: "wired twice: … and `.codex/hooks.json` (Codex
  PostToolUse …)" (Smallest End State item 6)

## Task 8 — rewrite stale docs/loom/README.md
- Description: Replace the "Frozen as historical archive (2026-05-30)"
  framing with a live directory map: BACKLOG.md (open items), memory/
  (practice store — one-line pointer to its charter), specs/ + plans/
  (briefs & plans, incl. the pre-OpenSpec 2026-05 archive note demoted to a
  history paragraph), audits/, dogfood/, research/, design/, firing-corpus/,
  INDEX.md (living-spec index), codex-verification.md. Keep the frozen-era
  explanation as a short §History, do not delete it (git-searchability
  rationale still true).
- Module: docs/loom/
- Files touched: docs/loom/README.md
- Context paths:
  - docs/loom/README.md
  - docs/loom/memory/README.md (charter, for the one-line description)
- Acceptance:
  - RED: `grep -q "memory/" docs/loom/README.md` fails
  - GREEN: README lists all nine current entries incl. memory/; "Frozen"
    appears only inside a §History section
- Dependencies: Task 1 completes first (doc-mirrors-structure: describes the
  memory/ charter)
- Independent: true
- Brief item covered: "Fix `docs/loom/README.md` staleness in the same
  change" (Smallest End State item 7)

## Task 9 — manifest cleanup + machine-local pointer stubs (ORCHESTRATOR)
- Description: Repo-diff scope: delete
  `docs/loom/memory/.migration-manifest.md` (its content is now realized in
  Tasks 3-4 output). Additionally — executed by the orchestrator as a
  machine-local side effect OUTSIDE the repo diff — rewrite each migrated
  machine-local memory file so the migrated content is replaced by a pointer
  ("→ docs/loom/memory/<slug>.md" / "→ docs/loom/BACKLOG.md §<entry>"),
  keeping any non-migrated remainder, and update the machine-local MEMORY.md
  index lines accordingly.
- Module: docs/loom/memory/
- Files touched: docs/loom/memory/.migration-manifest.md (delete)
- Context paths:
  - docs/loom/memory/.migration-manifest.md
- Acceptance:
  - RED: manifest still present after Tasks 3-4 land
  - GREEN: manifest deleted; spot-check one migrated machine-local file
    shows a pointer, not duplicated content
- Dependencies: Tasks 3, 4 complete first
- Independent: false
- Brief item covered: "Claude-side files become pointers" (Smallest End
  State item 5; BACKLOG.md:8 charter "session memory keeps only a pointer")

## Notes

- **Branching**: create `feat/loom-memory-store` from local HEAD (NOT
  origin/main — push-guard gotcha) before Task 1 dispatch. [DONE 2026-07-06]
- **Wave plan**: wave 1 = Tasks 1, 2, 5 (Independent: true, disjoint files);
  wave 2 = Tasks 4, 6, 7, 8 parallel (Independent: true, pairwise-disjoint
  Files touched; deps satisfied by wave 1: 4←2, 6←5, 7←5, 8←1) with Task 3
  running serially alongside (Independent: false — appends to the
  memory/README.md Index that Task 1 created); Task 9 last, orchestrator-run.
- Task 8's dependency rationale (doc-mirrors-structure) lives here per
  schema preference: it depends on Task 1 because it describes the memory/
  charter that Task 1 writes.
- **Commit discipline**: orchestrator-serial pathspec commits per task (no
  `git add -A` — repo hard rule); conventional-commits type whitelist +
  mandatory scope.
- **Out of scope guard** (from brief): no MCP, no CI enforcement of memory
  status, no environment-gotchas.md move, no git-memory changes, no bulk
  trailer import.
