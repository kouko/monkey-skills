# Plan: two-tier token-budget calibration (docs-only)

Source brief: docs/loom/specs/2026-07-15-token-budget-two-tier-calibration.md
Total tasks: 5
Critical-path depth: 3 (≤5) — 1 → {2a,2b} → {3a,3b}
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-17T09:15+08:00, round 3, 14/14; notes: header arrow-chain is illustrative — per-task Dependencies fields are authoritative)

## Notes

- **Branch**: `feat/token-budget-two-tier-calibration` from main HEAD. The
  (currently untracked) brief + this plan are committed with Task 1.
- **PINNED tier semantics** (each file phrases it in its own voice/language,
  but these FACTS must be identical everywhere): hard cap **~6,000 tokens /
  ~4,500 words** (unchanged; 🔴 rubric; the only machine-enforced tier);
  soft aim **~5,000 tokens / ~3,750 words** (aligned to official Anthropic
  Level-2 guidance, live-verified 2026-07-15); exceeding the soft aim
  requires a **one-line justification in the PR** (justified exceedance);
  the checker (`check-skill-structure.py`, `WORD_HARD_CAP = 4500`) stays
  hard-cap-only — NO code changes anywhere in this arc.
- Brief §Decision explicitly rejects a checker WARN tier (Option 2) and a
  suppression marker (Option 3) — implementers must not add either.
- Old soft-tier numbers to eradicate: "Soft target ~3,000–4,500 tokens" /
  "Warning zone ~4,500–6,000 tokens" and the "20% looser than official"
  framing (reframed, not deleted — per brief §What Becomes Obsolete).
- Grep-tests: prose assertions scope to a measured neighborhood around the
  §Token Budget anchor; RED verified against pre-change content.

## Decision Log

- Execution decision (2026-07-17, T2 review round): quality reviewer found
  residual single-tier "~6,000-token cap" framing (hard cap only, no soft
  aim — incomplete, not factually wrong) in skill-judge README×3 languages
  and the skill-creator-advance file family. Out of the brief's named
  propagation targets; skill-creator-advance is deliberately line-pinned.
  Resolution: recorded as follow-up debt (ride a future skill-dev-toolkit
  touch), NOT swept into this arc. (Two-way door, logged not briefed.)

## Task 1 — Recalibrate the skill-team SSOT + siblings

- Description: In domain-teams/skills/skill-team/, recalibrate every
  soft-tier statement to the pinned semantics (## Notes): standards/
  skill-md-structure.md §Token Budget (~:400, the SSOT), rubrics/
  skill-coherence.md (the 🟡 band numbers), protocols/new-skill-creation.md
  (its budget mention), checklists/skill-completeness-checklist.md CHK-SKL-010
  wording (~:40). Add the justified-exceedance convention sentence at the
  SSOT and point siblings at it (point-not-copy for the convention; the
  NUMBERS appear per file as today). RECONCILE the words/tokens presentation:
  every budget statement presents the pair in ONE consistent format —
  "~N tokens / ~M words", tokens first — stating the words-proxy relationship
  once at the SSOT. Old soft/warning numbers must not survive anywhere in
  domain-teams/.
- Module: domain-teams/skills/skill-team
- Files touched: domain-teams/skills/skill-team/standards/skill-md-structure.md, domain-teams/skills/skill-team/rubrics/skill-coherence.md, domain-teams/skills/skill-team/protocols/new-skill-creation.md, domain-teams/skills/skill-team/checklists/skill-completeness-checklist.md
- Context paths:
  - docs/loom/specs/2026-07-15-token-budget-two-tier-calibration.md (§Current State Evidence, §Decision)
  - domain-teams/skills/skill-team/standards/skill-md-structure.md
  - domain-teams/skills/skill-team/rubrics/skill-coherence.md
  - domain-teams/skills/skill-team/protocols/new-skill-creation.md
  - domain-teams/skills/skill-team/checklists/skill-completeness-checklist.md
- Acceptance:
  - RED: `grep -rn "5,000 tokens" domain-teams/skills/skill-team/standards/skill-md-structure.md` exits 1 (soft aim absent) AND `grep -rn "3,000–4,500" domain-teams/` hits (old numbers present).
  - GREEN: soft-aim numbers present at all four files' budget statements; `grep -rn "3,000–4,500\|4,500–6,000 tokens" domain-teams/` zero operative hits; `python3 loom-code/scripts/check-skill-structure.py` behavior untouched (no diff to any .py); `.github/workflows/skill-structure.yml`'s check script passes locally on domain-teams + loom-code plugins.
- Dependencies: none
- Independent: false
- Brief item covered: Decision "recalibrate the already-documented soft tier to the official 5k tokens ≈ 3,750 words, add a justified-exceedance prose convention, reconcile the words/tokens presentation"

## Task 2a — Consumer: CLAUDE.md house rule

- Description: Rewrite the zh house-rule line at CLAUDE.md:39 to the pinned
  tier semantics: 硬上限 ~6,000 tokens（約 4,500 words）＋軟目標 ~5,000
  tokens（約 3,750 words，對齊官方建議）＋超過軟目標需在 PR 註明一行理由。
  No other CLAUDE.md content changes (surgical).
- Module: CLAUDE.md
- Files touched: CLAUDE.md
- Context paths:
  - domain-teams/skills/skill-team/standards/skill-md-structure.md (as recalibrated by Task 1 — the pin source)
- Acceptance:
  - RED: `grep -n "5,000 tokens" CLAUDE.md` exits 1.
  - GREEN: CLAUDE.md carries the pinned numbers in the one house-rule line; `git diff CLAUDE.md` touches only that line's list item.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: Decision "propagate the aligned framing consistently to CLAUDE.md"

## Task 2b — Consumer: skill-judge token-cap reference

- Description: Update skill-dev-toolkit skill-judge's
  references/domain-team-adaptation.md token-cap mention to the pinned tier
  semantics (## Notes) — same facts, the file's own voice; point at the
  skill-team SSOT for the justified-exceedance convention.
- Module: skill-dev-toolkit/skills/skill-judge
- Files touched: skill-dev-toolkit/skills/skill-judge/references/domain-team-adaptation.md
- Context paths:
  - domain-teams/skills/skill-team/standards/skill-md-structure.md (as recalibrated by Task 1 — the pin source)
- Acceptance:
  - RED: `grep -n "5,000 tokens" skill-dev-toolkit/skills/skill-judge/references/domain-team-adaptation.md` exits 1.
  - GREEN: the reference carries the pinned numbers; repo-wide `grep -rn "3,000–4,500" --include="*.md" .` zero operative hits outside docs/ archives.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: Decision "propagate the aligned framing consistently to … skill-judge's token-cap reference"

## Task 3a — domain-teams version bump

- Description: Bump domain-teams/.claude-plugin/plugin.json `"version":
  "5.8.0"` → `"5.8.1"` (docs-only recalibration), sync the .codex-plugin
  mirror via `python3 scripts/sync_codex_manifests.py`, add a CHANGELOG
  entry per the file's convention.
- Module: domain-teams/.claude-plugin/plugin.json
- Files touched: domain-teams/.claude-plugin/plugin.json, domain-teams/.codex-plugin/plugin.json, domain-teams/CHANGELOG.md
- Context paths:
  - domain-teams/CHANGELOG.md
- Acceptance:
  - RED: `grep '"version": "5.8.0"' domain-teams/.claude-plugin/plugin.json` succeeds (pre-bump version present).
  - GREEN: 5.8.1 in claude+codex manifests; `python3 scripts/sync_codex_manifests.py --check --all` exit 0; CHANGELOG entry accurate.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: Problem "the numbers consistent across every place they appear" (release so devices pull the recalibrated docs)

## Task 3b — skill-dev-toolkit version bump

- Description: Bump skill-dev-toolkit/.claude-plugin/plugin.json `"version":
  "0.3.1"` → `"0.3.2"` (docs-only recalibration), sync the .codex-plugin
  mirror via `python3 scripts/sync_codex_manifests.py`, add a CHANGELOG
  entry per the file's convention.
- Module: skill-dev-toolkit/.claude-plugin/plugin.json
- Files touched: skill-dev-toolkit/.claude-plugin/plugin.json, skill-dev-toolkit/.codex-plugin/plugin.json, skill-dev-toolkit/CHANGELOG.md
- Context paths:
  - skill-dev-toolkit/CHANGELOG.md
- Acceptance:
  - RED: `grep '"version": "0.3.1"' skill-dev-toolkit/.claude-plugin/plugin.json` succeeds (pre-bump version present).
  - GREEN: 0.3.2 in claude+codex manifests; `python3 scripts/sync_codex_manifests.py --check --all` exit 0; CHANGELOG entry accurate.
- Dependencies: Task 2b completes first
- Independent: true
- Brief item covered: Problem "the numbers consistent across every place they appear" (release so devices pull the recalibrated docs)
