# Plan: skill-dev-toolkit extraction

Source brief: docs/code-toolkit/specs/2026-06-20-skill-dev-toolkit-extraction.md
Total tasks: 13   (uncapped; wave 3 is wide/parallel-eligible)
Critical-path depth: 4 (T1 → T2 → wave-3 → T13) — ≤5 ✓
Execution order: parallel-where-possible by file-disjointness, BUT commits are
  sequential (orchestrator commits) — parallel implementers in one worktree race
  the git index (known incident this session). Work class = structural migration
  (git mv + YAML/markdown/py ref edits + repath 1 gate script); verification is
  invariant-checks (moved gate passes, live-scoped grep-clean, plugins valid), not
  new unit tests — tdd-iron-law §When-NOT-to-use (structural/config). Each task's
  RED/GREEN is a diagnostic, not a TDD test.
Plan-document-reviewer verdict: PASS (2026-06-20). r1+r2 NEEDS_REVISION resolved; r2's sole residual = a one-token grep-anchor fix (`/docs/`→`(^|/)docs/`), applied + oracle-verified (16 referrers pre-move → 0 post-repoint). Round-3 review skipped per "amending toward a PASS" — the change is the reviewer-specified fix only; all other checks (file list, DAG, depth, coverage, drift-sync) PASSed in r2.

## Conventions used by several tasks
- **FROZEN (never rewrite)**: dated historical records keep their old `dev-workflow:` IDs
  as a record of past state — `docs/**` (plans/specs/audits/dogfood/research),
  `CHANGELOG*`, `*-SPEC.md`, `ROADMAP*`, `ATTRIBUTION*`, `/adr/`, `.claude/`, worktrees.
  The ONE exception is `docs/skill-mining/2026-06-19-skill-description-standard.md`
  (the operative standard, not a frozen run-record) — updated in T12.
- **LIVE-SCOPED GREP** (used by T9 RED/GREEN and T13): 
  `grep -rlE 'dev-workflow:(skill-creator-advance|skill-judge|skill-refactor|skill-tuning|dogfood-skill-testing)' . --include='*.md' --include='*.py' | grep -vE '/\.git/|\.claude/|worktrees|(^|/)docs/|CHANGELOG|-SPEC\.md|ROADMAP|ATTRIBUTION|/adr/|skill-dev-toolkit/'`
  (anchored `(^|/)docs/` — a leading-slash `/docs/` misses the top-level docs/ tree since `grep -rl` emits unprefixed paths; verified: returns the 16 referrers pre-move, 0 post-repoint.)
- **Per-skill repoint scope** (T3–T7): edits cover the WHOLE moved skill dir —
  `SKILL.md`, `README.md/.ja.md/.zh-TW.md`, `NOTICE`, and `references/**` — not just SKILL.md.

## Task 1 — scaffold skill-dev-toolkit plugin skeleton
- Description: create `.claude-plugin/plugin.json` (name skill-dev-toolkit, 0.1.0, author/repo/license mirroring a sibling), README.md + README.ja.md + README.zh-TW.md (purpose + the 5 skills + self-contained note), CHANGELOG.md ([0.1.0] — extracted from dev-workflow).
- Module: skill-dev-toolkit/.claude-plugin + plugin root
- Files touched: skill-dev-toolkit/.claude-plugin/plugin.json, skill-dev-toolkit/README.md, README.ja.md, README.zh-TW.md, skill-dev-toolkit/CHANGELOG.md
- Context paths: dbt-wiki/.claude-plugin/plugin.json
- Acceptance:
  - RED: `python3 -c "import json;json.load(open('skill-dev-toolkit/.claude-plugin/plugin.json'))"` fails (absent)
  - GREEN: valid JSON, name=skill-dev-toolkit, 0.1.0; 3 READMEs + CHANGELOG present
- Dependencies: none
- Independent: true
- Brief item covered: "A new plugin skill-dev-toolkit … new plugin 0.1.0"

## Task 2 — git mv the 5 skill dirs into skill-dev-toolkit/skills/
- Description: `git mv dev-workflow/skills/{skill-creator-advance,skill-judge,skill-refactor,skill-tuning,dogfood-skill-testing} skill-dev-toolkit/skills/` — relocate the 5 self-contained dirs intact.
- Module: skill-dev-toolkit/skills (move)
- Files touched: dev-workflow/skills/{the 5}/** → skill-dev-toolkit/skills/**
- Context paths: CLAUDE.md (flat-skill convention)
- Acceptance:
  - RED: `ls skill-dev-toolkit/skills/skill-creator-advance/SKILL.md` fails
  - GREEN: all 5 SKILL.md under skill-dev-toolkit/skills/; none remain under dev-workflow/skills/; flat-skill hook clean
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "the 5 skill-authoring skills … self-contained dirs … git mv is safe"

## Task 3 — sever skill-creator-advance deps (inline worth-it) + self-rename
- Description: in the moved skill-creator-advance dir, replace Gate-1/Gate-2 refs to `dev-workflow:proposal-critique`/`complexity-critique` with an inlined 2–3-question worth-it/smallest-skill check; repoint intra-family `dev-workflow:skill-*`→`skill-dev-toolkit:skill-*` across SKILL.md + README*.md + NOTICE + references/** (incl. references/plugin-conventions.md).
- Module: skill-dev-toolkit/skills/skill-creator-advance
- Files touched: skill-dev-toolkit/skills/skill-creator-advance/** (SKILL.md, README*.md, references/**)
- Acceptance:
  - RED: `grep -rE 'dev-workflow:' skill-dev-toolkit/skills/skill-creator-advance/` matches
  - GREEN: zero `dev-workflow:` refs in the dir; inlined worth-it block present
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "creator-advance → complexity-critique,proposal-critique (inline check)"

## Task 4 — sever skill-refactor deps + fix skill-tasting typo + self-rename
- Description: in moved skill-refactor dir, drop `dev-workflow:complexity-critique`/`proposal-critique` redirects (inline worth-it intent), drop the `domain-teams:code-team/standards/refactoring-standard.md` SSOT pointer (keep bundled content), fix typo `skill-tasting`→`skill-dev-toolkit:skill-tuning`, repoint intra-family `dev-workflow:skill-*`→`skill-dev-toolkit:` across SKILL.md + NOTICE + README*.md + references/**. **Drift-sync**: references/{golden-anchor-protocol,test-prompts-schema,constitution-schema}.md are drift-gated SoT vs skill-tuning copies — apply the SAME id-repoint here and in Task 5 so check-shared-conventions-drift stays green.
- Module: skill-dev-toolkit/skills/skill-refactor
- Files touched: skill-dev-toolkit/skills/skill-refactor/** (SKILL.md, NOTICE, README*.md, references/**)
- Acceptance:
  - RED: `grep -rE 'dev-workflow:|domain-teams:code-team|skill-tasting' skill-dev-toolkit/skills/skill-refactor/` matches
  - GREEN: zero `dev-workflow:`/`domain-teams:`/`skill-tasting`; bundled content intact
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "skill-refactor → complexity/proposal-critique, code-team SSOT pointer + fix skill-tasting typo"

## Task 5 — sever skill-tuning dep + self-rename (drift-mirror with T4)
- Description: in moved skill-tuning dir, drop/inline the `dev-workflow:proposal-critique` redirect; repoint intra-family `dev-workflow:skill-*`→`skill-dev-toolkit:` across SKILL.md + README*.md + references/** (incl. constitution-schema, golden-anchor-protocol, test-prompts-schema, constitutional-judging). **Drift-sync**: mirror T4's id-repoint in the shared convention files exactly.
- Module: skill-dev-toolkit/skills/skill-tuning
- Files touched: skill-dev-toolkit/skills/skill-tuning/** (SKILL.md, README*.md, references/**)
- Acceptance:
  - RED: `grep -rE 'dev-workflow:' skill-dev-toolkit/skills/skill-tuning/` matches
  - GREEN: zero `dev-workflow:` refs in the dir
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "skill-tuning → proposal-critique (inline/drop)"

## Task 6 — genericize skill-judge → domain-teams:skill-team (13×) + self-rename
- Description: in moved skill-judge dir, replace `domain-teams:skill-team` boundary/comparison prose with generic phrasing ("structural / convention gates are a separate concern outside this design-quality rubric") — no `plugin:skill` ID; repoint intra-family `dev-workflow:skill-*`→`skill-dev-toolkit:` across SKILL.md + NOTICE + README*.md. No behavior change.
- Module: skill-dev-toolkit/skills/skill-judge
- Files touched: skill-dev-toolkit/skills/skill-judge/** (SKILL.md, NOTICE, README.md, README.ja.md, README.zh-TW.md)
- Acceptance:
  - RED: `grep -rE 'domain-teams:skill-team|dev-workflow:' skill-dev-toolkit/skills/skill-judge/` matches
  - GREEN: zero `domain-teams:` / `dev-workflow:` refs in the dir
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "skill-judge → domain-teams:skill-team (13×, genericize)"

## Task 7 — drop dogfood-skill-testing → distill-sessions redirect + self-rename
- Description: in moved dogfood-skill-testing dir, drop the `dev-workflow:distill-sessions` redirect; repoint any intra-family `dev-workflow:skill-*`→`skill-dev-toolkit:`.
- Module: skill-dev-toolkit/skills/dogfood-skill-testing
- Files touched: skill-dev-toolkit/skills/dogfood-skill-testing/** (SKILL.md + any README/refs)
- Acceptance:
  - RED: `grep -rE 'dev-workflow:' skill-dev-toolkit/skills/dogfood-skill-testing/` matches
  - GREEN: zero `dev-workflow:` refs
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "dogfood-skill-testing → dev-workflow:distill-sessions (drop)"

## Task 8 — move + repath the 2 intra-set CI gate files
- Description: move `dev-workflow/.claude-plugin/test_skill_description_standard.py` → `skill-dev-toolkit/.claude-plugin/` and repath its CREATOR/JUDGE constants to skill-dev-toolkit; repath `scripts/check-shared-conventions-drift.py`'s skill-refactor/skill-tuning paths to skill-dev-toolkit. Update `.github/workflows/skill-structure.yml` ONLY for the `shared-conventions-drift` job (the description-standard pytest is not wired into any workflow — it moves+repaths but has no workflow line; if a dev-workflow pytest job globs `.claude-plugin/`, confirm it still finds it or add the new path).
- Module: CI gates (.claude-plugin + scripts + workflow)
- Files touched: skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py (moved), scripts/check-shared-conventions-drift.py, .github/workflows/skill-structure.yml
- Context paths: dev-workflow/.claude-plugin/test_skill_description_standard.py
- Acceptance:
  - RED: `python -m pytest skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py` fails (absent/wrong paths)
  - GREEN: that pytest passes (11) at new path; `python3 scripts/check-shared-conventions-drift.py` passes against skill-dev-toolkit; shared-conventions-drift workflow job references the new paths
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "two intra-set CI gates … become plugin-internal … scripts + workflow must be repathed"

## Task 9 — repoint LIVE inbound external refs (~16 files)
- Description: replace `dev-workflow:<moved-skill>` → `skill-dev-toolkit:<moved-skill>` ONLY in live (non-frozen) external files:
  code-toolkit/skills/using-code-toolkit/README.md + .ja.md + .zh-TW.md;
  dev-workflow/skills/brief-before-asking/README.md + .ja.md + .zh-TW.md + SKILL.md + references/IMPLEMENTATION-CHECKLIST.md;
  dev-workflow/skills/distill-sessions/SKILL.md + scripts/test_aggregate.py;
  dev-workflow/skills/proposal-critique/README.md + .ja.md + .zh-TW.md;
  four-dx-coach/optimization-workspace/README.md;
  tsundoku/skills/book-distill/SKILL.md + tsundoku/skills/book-extract/SKILL.md.
  Do NOT touch frozen docs/** / CHANGELOG / specs / adr (historical record).
- Module: cross-repo live inbound refs
- Files touched: (the ~16 listed above)
- Acceptance:
  - RED: the LIVE-SCOPED GREP (see Conventions) — excluding the 5 moved dirs (now under skill-dev-toolkit) — returns external referrers
  - GREEN: the LIVE-SCOPED GREP returns nothing
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "inbound dev-workflow:<moved-skill> IDs … → repoint"

## Task 10 — update dev-workflow plugin.json + CHANGELOG + version
- Description: in dev-workflow, if `.claude-plugin/plugin.json` enumerates skills, remove the 5 moved (it currently has no `skills` key → vacuous); bump version; add CHANGELOG entry ("extracted 5 skill-authoring skills to skill-dev-toolkit").
- Module: dev-workflow plugin metadata
- Files touched: dev-workflow/.claude-plugin/plugin.json, dev-workflow/CHANGELOG.md
- Acceptance:
  - RED: dev-workflow CHANGELOG has no extraction entry
  - GREEN: version bumped, CHANGELOG entry present, plugin.json valid
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "dev-workflow plugin.json (drop 5 skills, version bump, CHANGELOG)"

## Task 11 — add skill-dev-toolkit to marketplace.json
- Description: add a marketplace entry mirroring sibling entries (source/name/description); 24 → 25 sources.
- Module: root marketplace
- Files touched: .claude-plugin/marketplace.json
- Acceptance:
  - RED: `grep -c skill-dev-toolkit .claude-plugin/marketplace.json` = 0
  - GREEN: valid JSON; skill-dev-toolkit entry present; 25 sources
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "marketplace.json (+1 entry → 25 plugins)"

## Task 12 — update the operative standard doc refs
- Description: in `docs/skill-mining/2026-06-19-skill-description-standard.md` (the operative standard, not a frozen run-record), repoint `dev-workflow:skill-creator-advance`/`skill-judge` → `skill-dev-toolkit:` where they name the enforcing skills' homes. (The auto-memory file is out-of-repo; updated separately post-merge.) Leave all other frozen docs/** unchanged.
- Module: docs (operative standard only)
- Files touched: docs/skill-mining/2026-06-19-skill-description-standard.md
- Acceptance:
  - RED: `grep 'dev-workflow:skill-creator-advance\|dev-workflow:skill-judge' docs/skill-mining/2026-06-19-skill-description-standard.md` matches
  - GREEN: those refs now read skill-dev-toolkit:
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "standard doc string refs"

## Task 13 — whole-extraction verification
- Description: run all invariants: pytest the moved grep-guard at new path (11 passed); `check-shared-conventions-drift.py` green (T4/T5 mirror held); the LIVE-SCOPED GREP returns 0; both plugin.json valid JSON; marketplace 25 sources valid; flat-skill hook clean; repo-wide over-250 description count still 0; new plugin loads (5 skills discoverable).
- Module: verification (read-only)
- Files touched: (none)
- Acceptance:
  - RED: any invariant fails
  - GREEN: all green
- Dependencies: Tasks 3,4,5,6,7,8,9,10,11,12 complete first
- Independent: false
- Brief item covered: "self-sufficient (zero plugin:skill references to other plugins)"

## Notes
- Wave structure: T1 → T2 → {T3..T12 parallel-eligible, disjoint files} → T13. Depth 4.
- Execution: orchestrator commits sequentially (no parallel-commit — index-race incident this session). Edits done by orchestrator directly given mechanical/structural nature (tdd-iron-law §When-NOT-to-use).
- r1 reviewer fixes applied: (1)+(2) T9/T13 grep is now LIVE-SCOPED (was unsatisfiable — caught 63 frozen records); (3) T9 file list corrected to the 16 live referrers incl. .ja/.zh-TW + IMPLEMENTATION-CHECKLIST.md + test_aggregate.py, dropped the 0-live-ID files (dev-workflow/README.md, root README.md, deconstruct-toolkit/README.md); (4) T8 reworded (description-standard pytest not in any workflow). Added: T3–T7 cover whole skill dir (references/** carry IDs); T4/T5 drift-sync note for the 3 shared convention files.
