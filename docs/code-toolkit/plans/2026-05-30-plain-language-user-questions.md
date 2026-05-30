# Plan: code-toolkit plain-language user-questions

**Source brief**: docs/code-toolkit/specs/2026-05-30-plain-language-user-questions-brief.md
**Total tasks**: 4 (≤5)
**Execution order**: sequential (T1 → T2 → T3 → T4; T2 reuses T1's canonical rule wording to prevent drift)
**Plan-document-reviewer verdict**: PASS (2026-05-30 11:19 CST, round 2)

Scope note: pure SKILL.md prose + ship hygiene. No Python, no agent files, no tool changes. Dogfood is POST-ship (per [[project-code-toolkit-question-plain-language-investigation]] rollout plan) — NOT a task here. The other 6 question-emitting skills are v0.2 — NOT here.

Acceptance model: these are prose edits; the RED→GREEN diagnostic is a **content assertion** (grep the SKILL.md for the required section + rule markers), which is how this repo verifies SKILL.md changes (no pytest asserts SKILL.md prose; `validate-skill-folder-structure.sh` covers structure). Each GREEN condition is a concrete, checkable grep.

---

## Task 1 — Add `## Asking the user` 7-rule block to subagent-driven-development

- Description: Author a new `## Asking the user` section in SDD's SKILL.md containing the 7 rules (outcome-not-mechanism / translate-jargon-except-user-terms / numbers-carry-meaning / state-anchor-opener / research-first re-pointer / ≤4-options-no-explicit-Other / topic-coherent-compound), tuned to SDD's worst surface = the「下一步?」hand-off + NEEDS_CONTEXT/BLOCKED surfacing. Add a one-line cross-reference from each existing "surface to user" point to this section.
- Module: code-toolkit/skills/subagent-driven-development/SKILL.md
- Files touched: code-toolkit/skills/subagent-driven-development/SKILL.md
- Context paths:
  - docs/code-toolkit/specs/2026-05-30-plain-language-user-questions-brief.md (the 7-rule table + grounding)
  - dev-workflow/skills/recap-state/SKILL.md (lines ~141-148 — house style for a plain-language principle block + Block-1 "Situation" state-anchor wording to reuse)
  - code-toolkit/skills/subagent-driven-development/SKILL.md (existing surface-to-user points: lines 7-14 §Continuous execution, 51, 65, 83-85)
- Acceptance:
  - RED: `grep -c "## Asking the user" code-toolkit/skills/subagent-driven-development/SKILL.md` → 0 (section absent today)
  - GREEN: section present AND all 7 rules identifiable (7 distinct rule lines/markers) AND ≥1 cross-reference added at a surface-to-user point (e.g. line 84 `NEEDS_CONTEXT → surface...` now points to §Asking the user) AND state-anchor rule explicitly names the「state anchor / 一句話現況」concept
- Brief item covered: §Smallest End State — "Add one `asking-the-user` principle block (the 7 rules below) to the two highest-friction skills first — `subagent-driven-development` and `requesting-code-review`" (SDD half); §Decision §What-we-will-build.
- External surfaces: none (internal prose)
- Dependencies: none
- Independent: false

## Task 2 — Add audience-tailored block to requesting-code-review (verdict-relay flavor + boundary)

- Description: Add the same `## Asking the user` section to requesting-code-review's SKILL.md, tailored to its surface = relaying the reviewer **verdict** to the user. Emphasize translating `🔴🟡🟢` + Beck/OWASP citations into plain language and leading with a state anchor. Include an explicit BOUNDARY note: these rules govern the orchestrator's relay TO the user only — the `code-reviewer` agent's structured verdict MUST stay machine-precise + citation-bearing (do not loosen its evidence-citation contract). Reuse Task 1's canonical wording for the 5 shared rules to prevent cross-skill drift; tailor only rules 1/3/4 to the verdict context. Cross-reference from the existing surface points.
- Module: code-toolkit/skills/requesting-code-review/SKILL.md
- Files touched: code-toolkit/skills/requesting-code-review/SKILL.md
- Context paths:
  - code-toolkit/skills/subagent-driven-development/SKILL.md (Task 1's just-written §Asking the user block — wording template)
  - docs/code-toolkit/specs/2026-05-30-plain-language-user-questions-brief.md
  - code-toolkit/skills/requesting-code-review/SKILL.md (existing surface points: lines 77, 78, 89)
  - code-toolkit/agents/code-reviewer.md (lines 59-78 R2 evidence-citation + 289-315 verdict schema — the boundary that must NOT change; read to phrase the boundary note correctly)
- Acceptance:
  - RED: `grep -c "## Asking the user" code-toolkit/skills/requesting-code-review/SKILL.md` → 0
  - GREEN: section present with all 7 rules AND an explicit boundary sentence naming that the reviewer-agent verdict stays technically precise (not loosened) AND a verdict-relay rule mentioning translating 🔴/🟡/🟢 into plain language AND ≥1 cross-reference at a surface point (line 89 "Print the verdict + findings" → points to §Asking the user) AND the 5 shared-rule wordings match Task 1's (drift check)
- Brief item covered: §Smallest End State (requesting-code-review half); §Users — "the rules apply to the orchestrator → user surface, NOT to the code-reviewer agent's verdict"; §Decision §What-we-will-NOT-build — "no reviewer-agent change".
- External surfaces: none
- Dependencies: Task 1 completes first (wording template)
- Independent: false

## Task 3 — Bump versions (plugin manifest + skill frontmatter)

- Description: Bump code-toolkit plugin version 0.9.1 → 0.10.0 (minor — new user-facing behavior across 2 skills) in plugin.json; bump each touched skill's frontmatter `version` IF it carries one, to keep version strings in sync. This task is a single logical change = "sync all version strings for the 0.10.0 release."
- Module: code-toolkit/.claude-plugin/plugin.json
- Files touched: code-toolkit/.claude-plugin/plugin.json (+ subagent-driven-development/SKILL.md and requesting-code-review/SKILL.md frontmatter `version` IF present — version-string edits only, same logical change)
- Context paths:
  - code-toolkit/.claude-plugin/plugin.json (current "version": "0.9.1")
  - code-toolkit/skills/subagent-driven-development/SKILL.md + requesting-code-review/SKILL.md (check frontmatter for a version field)
- Acceptance:
  - RED: `grep '"version": "0.9.1"' code-toolkit/.claude-plugin/plugin.json` matches (still old)
  - GREEN: plugin.json version = `0.10.0` AND any skill frontmatter version fields bumped consistently (no `0.9.1` version string remains in the touched manifests/frontmatter)
- Brief item covered: ship necessity — NOT in brief scope; required to release the T1/T2 SKILL.md changes (standard release hygiene, flagged explicitly rather than fabricating brief traceability).
- External surfaces: none
- Dependencies: Tasks 1, 2 complete first
- Independent: false

## Task 4 — Add CHANGELOG entry

- Description: Add a `## [0.10.0]` entry to code-toolkit/CHANGELOG.md (Keep-a-Changelog format) summarizing the plain-language `## Asking the user` block added to SDD + requesting-code-review, citing the 6-mode AskUserQuestion investigation evidence and the per-skill placement decision.
- Module: code-toolkit/CHANGELOG.md
- Files touched: code-toolkit/CHANGELOG.md
- Context paths:
  - code-toolkit/CHANGELOG.md (Keep-a-Changelog format; head for entry style)
  - docs/code-toolkit/specs/2026-05-30-plain-language-user-questions-brief.md (evidence to cite in the entry)
- Acceptance:
  - RED: `grep -c "\[0.10.0\]" code-toolkit/CHANGELOG.md` → 0 (no entry yet)
  - GREEN: a `## [0.10.0]` entry present naming the new `## Asking the user` block + both skills (SDD + requesting-code-review) + the 6-mode investigation grounding
- Brief item covered: ship necessity — NOT in brief scope; release-notes hygiene for the T1/T2 changes (flagged explicitly, same as T3).
- External surfaces: none
- Dependencies: Task 3 completes first (entry names the 0.10.0 version T3 sets)
- Independent: false

---

## Brief-coverage map (every Smallest-End-State item → ≥1 task)
- 7-rule block in SDD → Task 1
- 7-rule block in requesting-code-review (audience-tailored + boundary) → Task 2
- Reuse recap-state wording / state-anchor → Tasks 1 + 2
- Cross-reference existing surface points → Tasks 1 + 2
- Per-skill duplication (not shared file) → Tasks 1 + 2 (separate files, full copy each)
- Ship hygiene (versions + CHANGELOG) → Tasks 3 + 4 (release necessity, not brief-scoped — flagged)
- Dogfood / other-6-skill rollout / XML-tag enforcer → OUT OF SCOPE (brief §Out of scope; post-ship + v0.2)

## OQ resolution (from brief, non-blocking)
- OQ1 → resolved: dedicated `## Asking the user` section + cross-reference (matches recap-state house style).
- OQ2 → resolved: rule 5 is a one-line re-pointer to router rule #5, NOT a copy of the Axis-4 protocol (avoids drift with brainstorming).
