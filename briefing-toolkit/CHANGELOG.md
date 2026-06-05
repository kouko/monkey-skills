# Changelog — briefing-toolkit

All notable changes to this plugin are documented here.

## [0.2.0] — 2026-06-05

Continuity & zero-omission hardening; regression-verified via `dev-workflow:dogfood-skill-testing` (see `docs/skill-dogfood/2026-06-05-daily-brief/report.md`) — gate: no new Critical/High vs the 2026-06-04 baseline.

### Added
- **G1 — 5th continuity state**: distinguishes `🆕 真新發生` (item date ≥ prior-brief generation time) from `⚠️ 昨日未涵蓋` (item date < prior-brief time — missed-yesterday / suspected under-collection), rendered distinctly in the 📈 brief section. Prevents a collection-method change (e.g. Asana 1→42 between days) from mislabeling old backlog as new events.
- **G4 — collection-volume visibility**: per-platform returned counts in the coverage statement; a `計數對照` step flags material count swings, feeding the G1 discrimination.
- **Per-platform Worked Examples + a shared generative Sanity-check** — one tight example per platform sub-agent; the Sanity-check ("an active source returning 0 → suspect the query, retry; don't report empty") replaces the prior reactive "enumerate every landmine" approach.
- **"Live discovery wins" principle** — live `ToolSearch` results override the playbook's dated negative-capability notes (treated as "as of YYYY-MM" snapshots, not capability ceilings), so the skill auto-adapts to MCP changes instead of silently suppressing newly-added tools.
- **Supplementary "waiting-on-me" signals** — Gmail `is:unread` (weak proxy), Slack `is:saved` / `has:pin` as personal-marker signals; Drive `viewedByMeTime` browse-history.
- **Window-edge (窗緣) inclusion** — items 1–3 days past the future-N window still surface, flagged "(窗緣)", instead of being dropped at the boundary.

### Changed
- **G3 — strict zero-fold complete table**: the complete action table is now one-row-per-item in BOTH MD and CSV (never grouped / footnote-summarized; every JOIN key preserved), with a named anti-pattern against consolidating stale backlog. Clarifies the dual-product split (curated brief vs zero-omission table).
- **G2 — stale/cached re-verify degradation**: if a continuity re-verify returns an `as-of`/cached snapshot earlier than today, the item's confidence drops to `推論` with a "重驗資料非即時 (as-of X)" caveat (mirrors the §3 thread-read-failure rule); Notion `notion-fetch` playbook bullet added to check the returned timestamp.
- **Per-platform fan-out hardening**: Notion ranks by owner/teamspace/last-edited (`created_by=0` means rarely-authors, not an API bug); Slack drops the unreliable `after:`/`before:` operators (filter timestamps client-side) and mandates DM / private-channel coverage; GitHub uses global `--author=@me` / `--review-requested=@me` / `--assignee=@me` search (avoids the non-repo-cwd failure).
- **5-cell per-platform template** (identity / tools / strategy + Worked Example + Pitfalls & Sanity-check), replacing the heavier 7-cell form — context-engineering evidence shows extra cells bloat agent context and degrade output.
- **✅-rarity expectation + thread-read degradation**: documents that a cross-platform `✅` (2+ independent sources) is inherently rare in this ecosystem; an unreadable/truncated thread degrades confidence rather than asserting "they're waiting on you".

### Fixed
- **H1**: dispatch phrasing now "全部 ✅就緒平台（最多 7）" — no longer contradicts the readiness Gate.
- **M1**: a returned link that is not an `http(s)` URL (placeholder / unresolved token) is marked `⚠️無直連`, not rendered clickable.
- **M2**: "PDB" expanded to "PDB（President's Daily Brief）" on first use in `SKILL.md` and `brief-templates.md`.
- **L2**: defined 高槓桿決策 with an example; purged dev-internal jargon (`source skill` / `source_book`) from user-facing prose across all four reference files.
- Continuity state-count + label consistency: every reference now reflects the 4-base-states + 第五狀態 structure; canonicalized `🆕 真新發生` across `SKILL.md` and all reference files.

## [0.1.0] — 2026-06-03

Initial release.

### Added
- **`daily-brief` skill** — cross-platform daily morning brief over 7 platforms (Gmail / Slack / Notion / Asana / Google Drive / Google Calendar / GitHub), self-contained raw-MCP fan-out (loads tools at runtime via ToolSearch; consumes whatever the user has connected, degrades gracefully).
  - **Dual artifacts**: curated PDB-style `<date>_晨報.md` + zero-omission, link-rich `<date>_完整事項.md` + machine-readable `<date>_完整事項.csv` (unique-id column = next-day join key).
  - **Cross-day continuity**: dated-ledger accumulation; each run diffs against the most-recent prior CSV (🆕 new / ⏳ still-waiting-N-days / ✅ resolved / 🔄 changed). Grounded by live-platform re-verification of each ID — never trusts yesterday's text.
  - **0-A readiness Gate** (connection / identity / read smoke-test per platform, GitHub included) guards against "false completeness".
  - **Dynamic focus** (threshold-driven, floor 0, soft cap ~5 with no silent truncation), confidence marks (✅ 2+ platforms / ⚠️ single / 推論), per-row clickable deep links, word-ceiling discipline.
  - **read-only + draft-only** safety lines; on-demand (scheduling layered via `/schedule` / cron / Cowork).
  - Bundled references: `platform-search-playbook.md`, `prioritization-framework.md`, `brief-templates.md`.
- **`/daily-brief` slash command.**

### Notes
- Mechanism mirrors (does not fork) the `performance-evidence-audit` skill — same cross-platform access discipline, but forward-facing (today + next N days + last 48h) and triage-oriented rather than evidence/retrospective.
- GitHub is a **core** platform here (it is optional in the source skill) — engineering evidence (PRs awaiting review, assigned issues) is first-class.
