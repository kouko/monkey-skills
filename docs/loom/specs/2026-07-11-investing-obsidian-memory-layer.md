# Brief: investing analysis memory layer (Obsidian-carried frontmatter)

## Design-side on-ramp
Not fired — increment to an existing report pipeline (negative guard: test-covered increment, no new interactive surface).

## Problem
Every analysis run is memoryless: a 2330.TW memo concluding HOLD @2415 leaves no queryable trace, so (a) the next analysis of the same ticker cannot recall the prior verdict, and (b) the user has no way to see the tool's track record ("were the verdicts right?"). Job story: 當我重複分析同一標的時，我要自動看到過去的結論與其事後對錯，好讓判斷可以累積而不是每次歸零。Industry grounding: memory/reflection loops are one of only two ablation-proven wins in the finance-agent literature (FinCon CVRF — removing it collapses returns; session survey 2026-07-11).

## Users
kouko, consuming via the report layer (report-equity-memo primarily), in two session shapes: terminal Claude Code AND Claudian (Claude Code embedded in the Obsidian vault, cwd = vault — first-class scenario, no bridge needed). Weak-to-mid model sessions must not break: the mechanism must be file/grep-based, not judgment-based.

## Smallest End State
Three deltas, pilot scope = report-equity-memo ONLY:
1. **Toolkit-owned frontmatter schema**, always emitted by Phase 4 into `/tmp/${TICKER_SAFE}-memo.md` regardless of destination: flat camelCase — `type: equity-memo`, `ticker`, `market`, `date` (ISO, must be typed Date in Obsidian properties — Bases date-comparison gotcha), `verdict` (HOLD/BUY/SELL/…), `confidence`, `priceAtAnalysis`, `intrinsicMid`. Schema documented in the SKILL.md (or a references/ file) as the SSOT.
2. **Recall step** at memo start: grep the vault (when resolvable — cwd is vault or user names it) or prior memo files for `ticker: <T>` frontmatter; if hits, surface last verdict/date/price in the conversation and cite them in the new memo's context. No hits / no vault → silent skip (loud in memo Limitations only).
3. **Phase 5b wording update**: obsidian-markdown applies placement + wikilinks + vault conventions but MUST respect (not re-invent) the toolkit frontmatter fields.
Track-record table = Obsidian Bases view over these properties — user-side, no code; a sample `.base` snippet MAY ship in docs as convenience, not a gate.

## Current State Evidence
- **Forward**: report-equity-memo/SKILL.md:264-272 — Phase 4 persists `/tmp/${TICKER_SAFE}-memo.md` with artifact gate; :276-281 Phase 5a docs-team format (optional); **:283-297 Phase 5b Obsidian vault delivery ALREADY EXISTS** (optional, delegates `obsidian:obsidian-markdown`, paths-not-content, artifact gate) — placement delegation needs no new construction.
- **Reverse**: vault-syntax ownership sits with the obsidian plugin (`obsidian:obsidian-markdown` per :286-287 "apply frontmatter / wikilinks / callouts") — today the FIELDS are improvised by the obsidian side; this change moves field ownership to the toolkit (investment domain knowledge), leaving syntax/placement ownership where it is.
- **Error**: Phase 5b skip path documented (:296-297 — /tmp memo is final artifact when skipped); recall step must mirror this graceful-skip shape.
- **Data**: memo body carries verdict/price/intrinsic values in prose (§一 執行摘要, §四 DCF) — no structured fields anywhere; `grep -rn frontmatter investing-toolkit/skills/*/SKILL.md` → only the :287 Phase 5b mention.
- **Boundary**: report-stock-snapshot has no vault/frontmatter phase (SKILL.md:85 renders to stdout; hands off to equity-memo) — out of pilot scope.
- Evidence paths: investing-toolkit/skills/report-equity-memo/SKILL.md; investing-toolkit/skills/report-stock-snapshot/SKILL.md.

## Alternatives Considered
1. **Plain file-dump into vault (A)** — rejected: no structured fields ⇒ no Bases queries, no machine recall (session discussion 2026-07-11).
2. **Merge investing into the obsidian plugin (C)** — rejected: jurisdiction mixing, kills host portability (Codex/no-vault), violates repo plugin-boundary precedent.
3. **Toolkit-side JSON verdict ledger** — superseded: frontmatter IS the ledger; one substrate serves human (Bases) and machine (grep) reads.
4. **Schema casing**: no community standard exists (research 2026-07-11: three shipped examples, three casings — kebab-nested / camelCase / PascalCase; JA ecosystem 見つからず). Chose flat camelCase per Bases `note.propertyName` ergonomics (EN forum evidence). **Conditional reversal**: at implementation, check the user's existing vault property casing via obsidian-cli — if the vault already standardizes differently, follow the vault.

## What Becomes Obsolete
- Phase 5b's "apply frontmatter" wording (:287) — obsidian side no longer invents investment fields; rewrite in the same change.
- The interim "verdict ledger JSON" idea from session discussion — superseded before construction; no code to delete.

## Decision
Build: schema definition + Phase 4 always-on frontmatter emission + recall step + Phase 5b wording alignment, in report-equity-memo only. NOT build: other 4 report skills (rollout after pilot proves), wikilinks/callouts in toolkit output (vault-side only), backtest engine, any new bridge for Claudian (native), merging plugins. Why: smallest change that makes analyses accumulate; every structural piece (Phase 5b delegation, artifact gates, cross-plugin contract) already exists.

## Open Questions
1. Vault folder default: propose `investing/memos/` (mirrors news/ structure); reversible — confirm or rename at review.
2. Final casing check against the live vault's existing properties (implementation-time, via obsidian-cli).
3. Snapshot/screener rollout timing — after pilot feedback.
