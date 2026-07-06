# Plan: loom-memory — management skill for the practice-memory store

Source brief: docs/loom/specs/2026-07-06-loom-memory-skill.md
Total tasks: 3
Critical-path depth: 2 (T1→T2; T1→T3)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-06, round 1, 14/14)

## Task 1 — loom-memory SKILL.md (three verbs)
- Description: Create `loom-pipeline/skills/loom-memory/SKILL.md` — flat
  folder, SKILL.md only (no scripts per brief Decision). Frontmatter:
  name loom-memory; description per the repo SKILL.md description
  standard (what it does + when to use + triggers incl. 中/日 like
  "記住這個做法", "有沒有相關經驗", "記憶整理"). Body ≤ ~2.5k tokens:
  (a) conditional gate — N/A-loud when target repo lacks
  `docs/loom/memory/README.md` (mirror using-loom-pipeline's CONDITIONAL
  pattern); (b) SSOT rule — charter/format/jurisdiction live in the
  store README, this skill POINTS and never copies (family anti-copy
  convention); (c) verb **record**: classify the fact per the charter's
  jurisdiction table (route backlog-shaped→BACKLOG.md,
  harness-friction→environment-gotchas.md, else store), write
  `<slug>.md` per the charter format, append byte-identical index line,
  then re-verify the two invariants (filename=name, index=description);
  (d) verb **recall**: grep index first then bodies for the topic, read
  ONLY hits, surface operative rules with file citations, say "no hits"
  honestly — never fabricate; (e) verb **prune**: per-file review
  against expiry signals (origin age / superseded by a repo artifact —
  cite it / no plausible future trigger), output keep/merge/retire table
  with reasons, NEVER delete without user approval; (f) red-flags table
  (refuse: preload-everything, copy-charter-into-skill, auto-delete).
- Module: loom-pipeline/skills/loom-memory/
- Files touched: loom-pipeline/skills/loom-memory/SKILL.md
- Context paths:
  - docs/loom/memory/README.md (charter to point at)
  - loom-pipeline/skills/using-loom-pipeline/SKILL.md (CONDITIONAL + N/A-loud pattern)
  - docs/loom/specs/2026-07-06-loom-memory-skill.md
- Acceptance:
  - RED: `ls loom-pipeline/skills/loom-memory/SKILL.md` fails
  - GREEN: file exists; grep finds all three verb sections, the N/A
    condition, ≥1 中/日 trigger in description; grep does NOT find the
    charter's jurisdiction table rows copied verbatim (anti-copy: e.g.
    the row text "environment-gotchas.md — stays" must not appear)
- Dependencies: none
- Independent: true
- Brief item covered: "Smallest End State item 1 — one skill, three
  verbs, N/A-loud, points at charter"

## Task 2 — reception hook recall pointer
- Description: Add ONE short block to
  `loom-pipeline/hooks/family-reception.md` adjacent to the on-ramp SSOT
  table: before starting loom work in a repo with `docs/loom/memory/`,
  run a recall pass via the `loom-memory` skill (pointer + one-line
  what-it-buys); explicitly pointer-only, no content preloading. Match
  the file's existing register.
- Module: loom-pipeline/hooks/
- Files touched: loom-pipeline/hooks/family-reception.md
- Context paths:
  - loom-pipeline/hooks/family-reception.md
  - loom-pipeline/skills/loom-memory/SKILL.md (name/verb reference)
- Acceptance:
  - RED: `grep -q "loom-memory" loom-pipeline/hooks/family-reception.md` fails
  - GREEN: grep passes; `git diff` shows only the added block (existing
    table body untouched — anti-copy assertions elsewhere depend on it)
- Dependencies: Task 1 completes first (references the skill by name)
- Independent: true
- Brief item covered: "Smallest End State item 2 — reception hook
  pointer, pull-not-push preserved"

## Task 3 — plumbing: version bump + CHANGELOG + codex manifest sync
- Description: Bump loom-pipeline to 0.5.0 in
  `.claude-plugin/plugin.json`, run
  `python3 scripts/sync_codex_manifests.py loom-pipeline` (or the
  documented equivalent — read the script header first) so
  `.codex-plugin/plugin.json` stays in sync (drift hook enforces on
  edit); add a CHANGELOG entry (0.5.0: loom-memory skill — record /
  recall / prune verbs + reception recall pointer). If loom-pipeline
  README lists member skills, add loom-memory one-liner (check first;
  skip silently if no such list).
- Module: loom-pipeline/
- Files touched: loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, loom-pipeline/CHANGELOG.md, loom-pipeline/README.md (conditional)
- Context paths:
  - loom-pipeline/CHANGELOG.md
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: `grep -q "0.5.0" loom-pipeline/.claude-plugin/plugin.json` fails
  - GREEN: both manifests say 0.5.0 and
    `python3 scripts/sync_codex_manifests.py --check loom-pipeline`
    exits 0; CHANGELOG has the 0.5.0 entry naming all three verbs
- Dependencies: Task 1 completes first (CHANGELOG describes the shipped skill)
- Independent: true
- Brief item covered: "Smallest End State item 3 — plumbing"

## Notes

- Branch: continues feat/loom-memory-store (PR #500) — the skill depends
  on the store charter, unmerged; avoids the stacked-PR retarget race.
  Close-out re-review covers the whole enlarged branch; gate markers
  re-minted then.
- Dogfood (brief item 4) is orchestrator-run acceptance AFTER SDD, not a
  plan task: 2 consecutive clean cheap-model rounds (recall seeded-hit /
  record format / prune honesty on synthetic aged store), disk-verified.
- Tasks 2 and 3 are file-disjoint but both depend on Task 1; they may
  run as a parallel wave after Task 1.
- Commit discipline: orchestrator-serial pathspec commits (no git add -A).
