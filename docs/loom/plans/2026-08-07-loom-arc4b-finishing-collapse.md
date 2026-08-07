# Plan: loom arc 4b — A1: finishing's five ONCE-checklists collapse into one table

Source brief: docs/loom/specs/2026-08-07-loom-arc4-prose-slim.md
Goal: finishing-a-development-branch's five ONCE-per-branch Step-8 bullets (974 w) collapse into one table — per-check fallback wording preserved verbatim in cells, every pin keeping a carrier — saving 400-600 w, and loom-code ships 0.68.0.
Stage: finishing
Total tasks: 2
Critical-path depth: 2 (≤5)
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-08-07, round 2)

Steps:
  1. 五條 ONCE 檢查摺成一張表（pin 視窗同步遷移）
  2. 版本 bump 0.68.0＋CHANGELOG

## Task 1 — A1: five ONCE-bullets collapse into one close-out sub-checks table
- Description: In loom-code/skills/finishing-a-development-branch/SKILL.md Step 8, replace the five "orchestrator-only, ONCE per branch" bullets — Living-spec index regen (:187-194, 78 w), Archive-on-close (:195-214, 208 w), Memory-timing check (:215-225, 155 w), Memory-store integrity (:226-257, 383 w), Backlog-close check (:258-273, 150 w); 974 w total in a 4,402 w file — with ONE lead-in sentence ("Close-out sub-checks — all orchestrator-only, ONCE per branch; a parallel wave would race each check's target file") plus one markdown table, one row per check IN THE SAME ORDER, columns: Check / When it fires / Action / On failure or N/A. RULE SEMANTICS PRESERVED: every command invocation, every quoted N/A string, every fallback wording lands verbatim in a cell — the words the collapse deletes are only the per-bullet scaffolding repetitions — "orchestrator-only, ONCE per branch" ×5 (single-line at :187/:195/:215/:226/:258) plus each bullet's sibling-shape tail (":195 same shape as the living-spec index bullet immediately above"; ":226 same as its Step 8 siblings"; ":258-259 same shape as its Step 8 siblings", line-wrapped) and the per-bullet restatements of the shared concurrency rationale — which the lead-in sentence and table structure now carry once. The Attached-HEAD check bullet (:274-279) and everything after stays untouched. These cell contents are load-bearing at point of use — collapse in place, do NOT extract to a reference file. Verbatim-cell floor (checkable): these recon-listed pinned strings must appear byte-identical in the table region — "archive-on-close: N/A — no change-folder bound", "Living-spec index regen", "Backlog-close check", "SHIPPED (or CLOSED — SUPERSEDED)", "`python3 scripts/backlog_index.py --write`", "No hit, or no store → skip silently", "the same miss shipped twice", "backlog-close: index not regenerated — backlog_index.py not present", "python3 scripts/check_loom_memory_integrity.py", "from the repo root", "memory-store integrity: N/A — checker not present in this repo", "No such file", "orchestrator-only", "once per branch", "added or edited a file under `docs/loom/memory/`", "frontmatter `description`, byte-identical", (note: some floor strings are line-wrapped in the CURRENT bullets — e.g. "the same miss shipped twice" spans :256-257 — so they grep 0 in the raw file today; in the table they must land unwrapped on one line so the raw grep passes), plus the four outside-file cross-references (../writing-plans/SKILL.md §Consuming a loom-spec change-folder; ../writing-plans/references/plan-format.md join keys; docs/loom/memory/README.md §"When to record"; docs/loom/memory/README.md §Index invariant). Then migrate the pin tests' WINDOW-EXTRACTION anchors (never the pinned phrases): test_finishing_memory_store_integrity.py's `_integrity_bullet` anchor `"   - Memory-store integrity"` (:54) re-anchors to the table row; test_finishing_archive_step.py's window/proximity tests (:106, :141-143, :151) re-anchor to table rows (row adjacency satisfies the proximity pin); test_finishing_backlog_close.py's ordering test (:73 — backlog row follows memory-store row) re-anchors to row order. Each adjusted test runs RED-first against a probe copy missing its target phrase where the file's convention demands it. Finally sweep the WHOLE SKILL.md for same-file pointers to the old bullet form (Step 6's "see Step 8's Memory-timing bullet for the exact rule" and any other "…bullet" referent) and update each to point at the table row — the orphaned-referent gotcha from arc 4a, applied proactively.
- Module: finishing collapse unit (SKILL.md + the three pin-test files — an atomic move; splitting leaves red pins mid-plan)
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_archive_step.py, loom-code/scripts/test_finishing_backlog_close.py, loom-code/scripts/test_finishing_memory_store_integrity.py
- Context paths:
  - docs/loom/specs/2026-08-07-loom-arc4-prose-slim.md (§Smallest End State 2 + §Decision)
- Acceptance:
  - RED: `grep -c "orchestrator-only, ONCE per branch" loom-code/skills/finishing-a-development-branch/SKILL.md` returns 5 (the per-bullet scaffolding still present at :187/:195/:215/:226/:258).
  - GREEN: the five bullets replaced by lead-in + table; that grep returns ≤1 (the lead-in sentence's single carry); SKILL.md `wc -w` between 3,800 and 4,010 (saving ≥400 w from 4,402); every string in the Description's verbatim-cell floor greps present; `python3 -m pytest loom-code/scripts/test_finishing_archive_step.py loom-code/scripts/test_finishing_backlog_close.py loom-code/scripts/test_finishing_memory_store_integrity.py -q` green; full suite `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q` green; report lists every window anchor moved and its new carrier, and every same-file pointer updated.
- External surfaces: none — markdown + pytest.
- Dependencies: none
- Independent: false
- Brief item covered: "A1: finishing's five ONCE-bullets (974 w at arc-3-merged state) collapse into one … table — one row per check … per-check fallback wording preserved verbatim in the cells; target saving 400-600 w" + §Decision "do NOT extract A1's content to a reference (collapse in place)"
- Status: done(d26fdc33)
- Gloss: 五條收尾檢查摺成一張表——省的是重複鷹架，規則字句一字不動進格子
- Review-hint: the whole-branch review runs a HAIKU COLD-READ probe on the collapsed Step 8 (brief item 4's conditional fires: cells cite outside rules — charter §refs — so the extraction-severing duty applies; misread = wording fix, never reader-blame).

## Task 2 — loom-code 0.68.0 + CHANGELOG + version pin
- Description: Bump loom-code 0.67.0 → 0.68.0 via `python3 scripts/sync_codex_manifests.py loom-code` (--check exit 0); CHANGELOG 0.68.0 entry (house style: the A1 collapse — what the table carries, what scaffolding was deleted, pins re-anchored; names this as the arc-4 deferral landing); version-pin test rewrite in loom-code/scripts/test_docs_review_blocking_class.py `_0_67_0` → `_0_68_0` RED-first (flip pin, show missing heading, write entry, GREEN).
- Module: loom-code release unit (manifest pair + CHANGELOG + version pin, one version)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md (0.67.0 entry shape)
- Acceptance:
  - RED: version-pin test fails on missing `## [0.68.0]` heading after the flip (shown pre-entry).
  - GREEN: both manifests 0.68.0 in sync; CHANGELOG entry present naming the arc-4 deferral landing; zero 0.67.0/0_67_0 residue in the pin test; full suite green.
- External surfaces: marketplace versioning (bump-or-silent-no-op).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "loom-code minor bump (three core SKILL.md bodies change — the third lands in this split) + CHANGELOG + version-pin rewrite"
- Status: done(9fd7e448)
- Gloss: 0.68.0——瘦身弧後半場出貨，arc-4 全弧完結
- Review-hint: none.

## Notes

- Endpoint: continuous per /goal「繼續做下去吧」; PR-open terminal; never
  auto-merge. This plan is the DEFERRED HALF of arc 4 (brief §Decision's
  continuation-pressure split clause) — arc 4a shipped A2+A3 as PR #675;
  #674 (the file-overlap blocker) and #675 are both merged, so A1's
  gate is open. Recon re-anchored all line numbers and word counts to
  merged main (43712038): five bullets :187-273 = 78+208+155+383+150 =
  974 w; SKILL.md 4,402 w; manifests at 0.67.0.
- Review plan: whole-branch review carries (a) the standard code+docs arms
  and (b) a HAIKU COLD-READ probe leg on the collapsed Step 8 (Task 1's
  Review-hint; extraction-severing memory): the probe executes the
  close-out sub-checks blind on one real branch-state scenario and must
  reach each check's command and N/A wording from the table alone
  (misread = wording fix, never reader-blame).
- Kickoff briefing: zero one-way-door decisions (an in-place collapse,
  reversible from git history); no PRINCIPLES.md → nothing suppressed.
- Change-folder binding: Layer 0 explicit handoff — input is the brief;
  the non-archived investing change-folders remain unrelated, NOT bound
  (stated loudly).
- Wave discipline: sequential (T2 depends on T1); one commit per Bash
  block while agents live (parallel-wave-commit-discipline).
