# Plan: investing analysis memory layer (Obsidian-carried frontmatter) — pilot on report-equity-memo

Source brief: docs/loom/specs/2026-07-11-investing-obsidian-memory-layer.md
Total tasks: 3
Critical-path depth: 3 (T1 → T2 → T3, all touch the same SKILL.md)
Execution order: sequential
Plan-document-reviewer verdict: PASS (round 2, 14/14, 2026-07-11)

## Task 1 — frontmatter schema SSOT + Phase 4 always-on emission
- Description: Create the toolkit-owned frontmatter schema reference and make Phase 4 emit it unconditionally at the top of `/tmp/${TICKER_SAFE}-memo.md`.
- Module: investing-toolkit/skills/report-equity-memo
- Files touched: investing-toolkit/skills/report-equity-memo/references/vault-frontmatter.md (new), investing-toolkit/skills/report-equity-memo/SKILL.md
- Context paths:
  - docs/loom/specs/2026-07-11-investing-obsidian-memory-layer.md (schema fields + casing decision + Bases date gotcha)
  - investing-toolkit/skills/report-equity-memo/SKILL.md:264-274 (Phase 4 persist + artifact gate — emission instruction lands here)
- Acceptance:
  - RED (diagnostic): grep shows Phase 4 section has no frontmatter emission instruction; references/vault-frontmatter.md absent
  - GREEN: references/vault-frontmatter.md exists with the 8-field schema (type/ticker/market/date/verdict/confidence/priceAtAnalysis/intrinsicMid), field types + Bases date-typing note + a sample `.base` table snippet; SKILL.md Phase 4 instructs emitting the block (values sourced from the run: verdict/confidence from §一, priceAtAnalysis from fetch, intrinsicMid from DCF) BEFORE the body, and the Phase 4 artifact gate additionally verifies the file starts with `---` (e.g. `head -1`); flat-folder convention intact (references/ one level deep)
- External surfaces: Obsidian frontmatter/Bases property semantics — grounded via brief's Alternatives §4 research; best-effort casing check against the live vault via obsidian-cli if reachable, else keep camelCase and record the check as pending in the schema doc
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State item 1 "Toolkit-owned frontmatter schema, always emitted by Phase 4"

## Task 2 — recall step (prior-verdict lookup before analysis)
- Description: Add a recall step early in the workflow (before Phase 1 data fetch): search prior memos' frontmatter for the same ticker; surface last verdict/date/priceAtAnalysis and feed them into the memo context; silent-skip when nothing found, disclosed in Limitations.
- Module: investing-toolkit/skills/report-equity-memo
- Files touched: investing-toolkit/skills/report-equity-memo/SKILL.md
- Context paths:
  - docs/loom/specs/2026-07-11-investing-obsidian-memory-layer.md (Smallest End State item 2; Error sub-bullet — mirror Phase 5b's graceful-skip shape at SKILL.md:296-297)
  - investing-toolkit/skills/report-equity-memo/references/vault-frontmatter.md (from T1 — grep key is the `ticker:` field)
- Acceptance:
  - RED (diagnostic): grep shows no recall/prior-verdict step before Phase 1
  - GREEN: a recall step exists with (a) concrete search command shape (grep for `ticker: <T>` across the vault when cwd/user-named, else prior memo dirs), (b) what to surface (last verdict/date/price + delta vs current price), (c) explicit silent-skip + Limitations disclosure rule; weak-model-safe (pure grep, no judgment call required to execute)
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State item 2 "Recall step at memo start"

## Task 3 — Phase 5b field-ownership wording alignment
- Description: Rewrite Phase 5b (:283-297) so obsidian-markdown applies placement/wikilinks/vault conventions but MUST respect the toolkit frontmatter fields (no re-inventing/overwriting); name the default vault folder `investing/memos/` as a reversible proposal. (Needs T1's schema file to reference; runs after T2 because all three tasks edit the same SKILL.md.)
- Module: investing-toolkit/skills/report-equity-memo
- Files touched: investing-toolkit/skills/report-equity-memo/SKILL.md
- Context paths:
  - docs/loom/specs/2026-07-11-investing-obsidian-memory-layer.md (What Becomes Obsolete — the :287 "apply frontmatter" wording)
- Acceptance:
  - RED (diagnostic): SKILL.md:287 still says obsidian-markdown applies frontmatter (field invention implied)
  - GREEN: Phase 5b text says fields come from the toolkit schema (reference the T1 file), obsidian side owns placement/linking/conventions only; `investing/memos/` named as default-unless-user-says-otherwise; artifact-gate paragraph unchanged in force
- External surfaces: none
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: Smallest End State item 3 "Phase 5b wording update" + What Becomes Obsolete item 1

## Notes
- All three tasks edit the same SKILL.md → strictly sequential; no parallel wave.
- Doc-only plan: RED/GREEN are grep diagnostics per house convention (same pattern as the merged #539 Task 7); package pytest suite must stay green as a no-regression check after each task (no code is touched, so any suite change is a red flag).
- Post-plan verification (review stage, not a task): fresh-context cold-read of the edited SKILL.md — "which fields does Phase 4 emit, and when may Phase 5b rewrite them?" must be answerable from the doc alone.
- SKILL.md size guard: file was 19,422 bytes after #539 (word count ~2.6k, budget ~4.5k words); T1+T2+T3 additions must keep it under budget — implementers report before/after `wc -c`.
