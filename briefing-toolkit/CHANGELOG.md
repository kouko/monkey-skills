# Changelog — briefing-toolkit

All notable changes to this plugin are documented here.

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
