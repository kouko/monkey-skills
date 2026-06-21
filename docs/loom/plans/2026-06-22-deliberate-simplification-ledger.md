# Plan: deliberate-simplification ledger (LOOM-SIMPLIFY marker + harvest)

**Source brief**: docs/loom/specs/2026-06-22-deliberate-simplification-ledger.md
**Total tasks**: 6
**Critical-path depth**: 4 (≤5 ✓) — Task 1 → Task 2 → {3,4,5 parallel} → Task 6
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-22)

## Task 1 — Author canonical deliberate-simplification standard

- **Description**: Write the canonical standard at `domain-teams/skills/code-team/standards/deliberate-simplification.md` defining: the `LOOM-SIMPLIFY:` marker with **4 fields** (`shortcut` | `ceiling` | `upgrade` | `ref`); the rule that `ceiling:` MUST be a **checkable condition** (not "later") and `ref:` ties the marker to its brief/task; an explicit **"the marker is NOT a TDD-iron-law waiver — the shortcut's current behavior is still tested"** clause; the **harvest-at-the-introducing-branch's-review-gate scope boundary** (in-code markers are SSOT, harvest is grep-on-demand, no persisted ledger file — rationale: the 58%-fake-removal SATD finding makes lifetime grep-tracking unreliable, so we scope to the merge gate). Include Primary Sources grounding (PEP 350 codetags; Fowler 2009 deliberate-prudent debt quadrant; Maldonado ICSME 2017 58%-fake-removal; Maipradit "Wait For It" on-hold SATD = the ceiling concept; PromptDebt arXiv 2509.20497 AI-generated debt). Match the prose style + section shape of the sibling `external-surface-grounding.md` (Primary Sources / The Rule / categories / examples). Do NOT prepend the FUNCTIONAL-COPY header — this is the canonical SSOT, not a copy.
- **Module**: `domain-teams/skills/code-team/standards/deliberate-simplification.md`
- **Files touched**: `domain-teams/skills/code-team/standards/deliberate-simplification.md`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/domain-teams/skills/code-team/standards/external-surface-grounding.md`
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/docs/loom/specs/2026-06-22-deliberate-simplification-ledger.md`
- **Acceptance**:
  - **RED**: `grep -l "LOOM-SIMPLIFY" domain-teams/skills/code-team/standards/deliberate-simplification.md` fails (file absent / lacks the marker spec).
  - **GREEN**: file exists; contains the 4 field names (`shortcut`/`ceiling`/`upgrade`/`ref`), the literal "not a" + TDD-waiver disclaimer, the checkable-ceiling rule, the harvest-scope-boundary paragraph, and a Primary Sources section with ≥4 citations; no FUNCTIONAL-COPY header present.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State item 1 ("A marker convention … defined as a new SDD standard, modeled on external-surface-grounding.md").

## Task 2 — Route the standard through distribute.py + generate the loom-code functional copy

- **Description**: Add a routing entry to `loom-code/scripts/distribute.py`'s routing table — `"standards/deliberate-simplification.md": [f"{_SDD_STANDARDS_DIR}/deliberate-simplification.md"]` — then run `python3 loom-code/scripts/distribute.py` to generate the functional copy (canonical bytes + SSOT header) at `loom-code/skills/subagent-driven-development/standards/deliberate-simplification.md`. The copy is generated, not hand-authored.
- **Module**: `loom-code/scripts/distribute.py`
- **Files touched**: `loom-code/scripts/distribute.py`, `loom-code/skills/subagent-driven-development/standards/deliberate-simplification.md`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/loom-code/scripts/distribute.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/loom-code/scripts/verify-drift.py`
- **Acceptance**:
  - **RED**: `python3 loom-code/scripts/verify-drift.py` fails (routed copy missing or byte-divergent) — equivalently `grep deliberate-simplification loom-code/scripts/distribute.py` returns nothing.
  - **GREEN**: routing entry present; functional copy exists with the `FUNCTIONAL COPY … SSOT: domain-teams/…/deliberate-simplification.md` header followed by canonical bytes; `python3 loom-code/scripts/verify-drift.py` exits 0.
- **External surfaces**: CLI: `python3 loom-code/scripts/distribute.py` + `verify-drift.py` — grounding: in-repo scripts (read in Context paths).
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: Smallest End State item 1 (the standard is "referenced by multiple skills, not duplicated" — the distribute/verify-drift mechanism is how loom-code gets the copy).

## Task 3 — Wire implementer.md to leave the marker

- **Description**: Add a rule section to `loom-code/agents/implementer.md` (OUTSIDE the distribute.py-injected baseline block — place it as ordinary agent prose): when the implementer takes a **deliberate, scope-bounded** shortcut because the proper solution is Out-of-Scope per the brief, it MUST leave a `LOOM-SIMPLIFY:` marker per `standards/deliberate-simplification.md`. State explicitly this is **not** a TDD waiver (current behavior still tested). Reference the standard by its loom-code path.
- **Module**: `loom-code/agents/implementer.md`
- **Files touched**: `loom-code/agents/implementer.md`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/loom-code/agents/implementer.md`
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/loom-code/skills/subagent-driven-development/standards/deliberate-simplification.md`
- **Acceptance**:
  - **RED**: `grep "LOOM-SIMPLIFY" loom-code/agents/implementer.md` returns nothing.
  - **GREEN**: a rule referencing `deliberate-simplification.md` is present, names the not-a-TDD-waiver constraint, and sits outside the managed injection block (`grep -n "injection\|P15-12\|baseline"` boundaries unchanged).
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State item 2 ("Implementer leaves it … explicitly NOT a TDD bypass").

## Task 4 — Wire code-reviewer.md to harvest + completeness-check markers

- **Description**: Add to `loom-code/agents/code-reviewer.md` (outside the injected reviewer-discipline block) a whole-branch step: grep `LOOM-SIMPLIFY:` across the branch diff, surface the collected markers as a ledger view in the review output, and flag any marker missing `ceiling:` / `upgrade:` / `ref:` or whose `ceiling:` is vague ("later") as a finding.
- **Module**: `loom-code/agents/code-reviewer.md`
- **Files touched**: `loom-code/agents/code-reviewer.md`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/loom-code/agents/code-reviewer.md`
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/loom-code/skills/subagent-driven-development/standards/deliberate-simplification.md`
- **Acceptance**:
  - **RED**: `grep "LOOM-SIMPLIFY" loom-code/agents/code-reviewer.md` returns nothing.
  - **GREEN**: a harvest + completeness check is present that names the grep, the ledger surfacing, and the missing-field / vague-ceiling flag; references the standard.
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State item 3 ("whole-branch code-reviewer flags any marker missing ceiling or upgrade").

## Task 5 — Wire requesting-code-review SKILL.md to surface the harvested ledger

- **Description**: Add a step to `loom-code/skills/requesting-code-review/SKILL.md` review workflow: before producing the review summary, harvest `LOOM-SIMPLIFY:` markers from the whole-branch diff and present the ledger view in the summary, so deliberate shortcuts are visible at the merge gate. Bump the skill `version:`.
- **Module**: `loom-code/skills/requesting-code-review/SKILL.md`
- **Files touched**: `loom-code/skills/requesting-code-review/SKILL.md`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/loom-code/skills/requesting-code-review/SKILL.md`
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/loom-code/skills/subagent-driven-development/standards/deliberate-simplification.md`
- **Acceptance**:
  - **RED**: `grep "LOOM-SIMPLIFY" loom-code/skills/requesting-code-review/SKILL.md` returns nothing.
  - **GREEN**: a harvest-and-surface step is present in the review workflow; `version:` bumped; references the harvest as a review-summary element.
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State item 3 ("requesting-code-review greps LOOM-SIMPLIFY … and surfaces a ledger view in the review summary").

## Task 6 — Version bumps + CHANGELOG for the convention

- **Description**: Bump `version:` in `subagent-driven-development/SKILL.md` (new bundled standard) and add a `loom-code/CHANGELOG.md` entry describing the deliberate-simplification ledger (LOOM-SIMPLIFY marker + review-gate harvest). Verify no plugin/marketplace description coherence gate breaks.
- **Module**: `loom-code/CHANGELOG.md`
- **Files touched**: `loom-code/CHANGELOG.md`, `loom-code/skills/subagent-driven-development/SKILL.md`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/loom-code/CHANGELOG.md`
  - `/Users/kouko/.supacode/repos/monkey-skills/ponytail-research/loom-code/skills/subagent-driven-development/SKILL.md`
- **Acceptance**:
  - **RED**: `grep -i "deliberate-simplification\|LOOM-SIMPLIFY" loom-code/CHANGELOG.md` returns nothing.
  - **GREEN**: CHANGELOG entry present; SDD SKILL.md version bumped; `python3 scripts/check-plugin-description-skill-coherence.py` and `python3 scripts/check-skill-structure.py` exit 0.
- **External surfaces**: CLI: `python3 scripts/check-plugin-description-skill-coherence.py`, `python3 scripts/check-skill-structure.py` — grounding: in-repo scripts.
- **Dependencies**: Tasks 3, 4, 5 complete first
- **Independent**: false
- **Brief item covered**: Decision ("housed as a new SDD standard wired into three touch points") — release-hygiene closure of the wiring.

## Notes

- **SSOT placement (surfaced architectural constraint).** Planning-time recon found all 8 SDD standards are **synced functional copies** from `domain-teams/skills/code-team/standards/` via `loom-code/scripts/distribute.py`, gated by `verify-drift.py`. So the new standard is authored canonical-in-code-team (Task 1) and distributed (Task 2) — NOT hand-written into loom-code. Side effect: the convention also becomes available to the shared `domain-teams:code-team`, which is architecturally correct (standards are code-team-owned) and consistent with the user's "house additions in new module, not synced SSOT" discipline.
- **Agent injection blocks.** `loom-code/agents/*.md` are local-editable but `distribute.py` injects managed blocks (12-rule baseline / reviewer-discipline). Tasks 3 & 4 add prose OUTSIDE those blocks to avoid clobbering on next distribute run.
- **Parallelism.** Tasks 3, 4, 5 touch disjoint files, all depend only on Task 2, and share no symbol → `Independent: true` leaves at one dependency level (count as one level; critical-path depth stays 4).
- **Dropped as YAGNI.** A `writing-plans` one-line cross-reference (brief's "at most a one-line cross-reference") was considered and dropped: the convention is discovered via the standard + implementer agent; a writing-plans pointer earns no reliability and the topic itself is about not adding unrequested scope.
- **Acceptance model.** These are prose/convention edits; RED/GREEN are grep/structure assertions + the repo's existing CI gates (`verify-drift.py`, `check-skill-structure.py`, `check-plugin-description-skill-coherence.py`) — the same model used for prior prose-only loom-code changes. A behavioral dogfood (does the implementer actually leave a marker; does review surface it) rides the requesting-code-review stage at branch finish, not a per-task pressure test.
