# Plan: brainstorming greenfield UI-coverage nudge (Tier 1)

Source brief: docs/code-toolkit/specs/2026-06-11-brainstorming-greenfield-ui-coverage-nudge.md
Total tasks: 1
Critical-path depth: 1 (≤5)
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-06-11; 11/14, checks 12-14 N/A)

## Design notes
- The whole brief is one atomic prose change to a single SKILL.md, guarded by one grep-test → 1 task (RED grep-test → GREEN prose).
- Test location: `code-toolkit/scripts/test_brainstorming_greenfield_nudge.py` — mirrors the shipped spec-toolkit convention (`spec-toolkit/scripts/test_*skill*.py`); code-toolkit/scripts/ exists.
- Insertion points (recon): nudge subsection right after `## Current State Evidence` (SKILL.md:145, where the `N/A — greenfield` determination is made = the gate signal); forward-pointer line in/near `## Cross-skill delegation` (SKILL.md:176).
- Token budget: SKILL.md ~3,900 tokens; +~20 lines stays well under ~6,000.
- The behavioral A/B (greenfield with-nudge vs without, same eyedropper/collections/side-by-side seeds) is the REAL proof but is a **verification step**, not a code task — see Notes.

## Task 1 — add greenfield UI-coverage nudge + forward-pointer to brainstorming SKILL.md
- Description: Add to `code-toolkit/skills/brainstorming/SKILL.md` (a) a short nudge subsection after `## Current State Evidence`: when Current-State-Evidence is `N/A — greenfield`/thin **AND** the feature has a UI/interaction/stateful surface, enumerate UI states across the six categories — **empty / error / loading / state-transition / permission / boundary** — before finalizing the brief; (b) a one-line DRY guardrail: this is a category reminder only, the full method/matrix lives in `spec-toolkit:spec-expansion` (do not reproduce it here); (c) a forward-pointer in/near `## Cross-skill delegation`: for high-coverage/high-risk greenfield, `spec-toolkit:spec-expansion` runs the full lens — noted as Tier 2 / active once writing-plans reads OpenSpec change-folders (deferred). Must NOT fire in brownfield or for non-UI features (gate explicit).
- Module: code-toolkit:brainstorming nudge
- Files touched: code-toolkit/skills/brainstorming/SKILL.md, code-toolkit/scripts/test_brainstorming_greenfield_nudge.py
- Context paths:
  - code-toolkit/skills/brainstorming/SKILL.md (insertion points :145 and :176)
  - spec-toolkit/skills/spec-expansion/SKILL.md (the SSOT the forward-pointer references — read to phrase it; do NOT copy content)
  - docs/code-toolkit/specs/2026-06-11-brainstorming-greenfield-ui-coverage-nudge.md (the brief)
- Acceptance:
  - RED: `code-toolkit/scripts/test_brainstorming_greenfield_nudge.py` (run `PYTHONDONTWRITEBYTECODE=1 python -m pytest code-toolkit/scripts/test_brainstorming_greenfield_nudge.py -q -p no:cacheprovider`) fails against the current SKILL.md. It asserts the SKILL.md contains: all six category names (empty/error/loading/state-transition/permission/boundary); a greenfield-AND-UI gate (assert "greenfield" co-occurs with a UI/interaction/state-surface phrase AND a not-brownfield / only-when guard); the forward-pointer naming `spec-toolkit:spec-expansion` + a Tier-2/deferred marker; and a DRY-guardrail phrase (reminder-only / full method lives in spec-toolkit / do-not-reproduce). Resolve SKILL.md via `Path(__file__).parents[1] / "skills" / "brainstorming" / "SKILL.md"`.
  - GREEN: prose added; the grep-test passes; the folder-structure hook passes; SKILL.md stays under the ~6,000-token budget (report word count).
- Dependencies: none
- Independent: false
- Brief item covered: "a few prose lines added to `code-toolkit:brainstorming` that fire only when both: (a) Current-State-Evidence is `N/A — greenfield`/thin, AND (b) the feature has a UI/interaction/stateful surface — reminding the agent to enumerate states across the standard categories … Plus a forward-pointer … to `spec-toolkit:spec-expansion`" (Smallest End State)

## Notes
- Worktree: `.worktrees/feat-brainstorming-greenfield-ui-nudge` on branch `feat/brainstorming-greenfield-ui-nudge` (off origin/main ffd82717).
- **Post-build verification (not a task):** run the greenfield A/B — brainstorming WITH the nudge vs WITHOUT, on the same 3 seeds (eyedropper/collections/side-by-side) — and score coverage. If the nudge does not lift coverage above the no-nudge baseline (8/17, 6/12, 3/13), it's dead text → surface to user before shipping (per the A/B-baseline lesson, memory `feedback_ab_baseline_reveals_marginal_behavioral_delta`).
- Tier 2 (judge→delegate to spec-toolkit via OpenSpec change-folder) is OUT — depends on the unbuilt OpenSpec DECLARE wiring (2026-05-30 brief Q6=A).
- **Verification result (A/B, 2026-06-11): NUDGE VALIDATED — not dead text.** Ran greenfield brainstorming WITH the nudge vs the recorded no-nudge baseline on the same 3 seeds, scoring intrinsic UI-state coverage: eyedropper **8/17 → ~16/17**, collections **6/12 → ~12/12**, side-by-side **3/13 → ~11/13**. The nudge fired correctly (greenfield+UI gate) and made brainstorming enumerate the six categories it previously skipped — closing nearly the whole gap to spec-toolkit's full lens, for ~20 lines of prose. Safe to ship. (Implication: the nudge nearly matches the full lens, so Tier-2's marginal value is even smaller than thought — input to the future DECLARE-wiring decision.)
- **Close-out:** code-toolkit plugin 0.15.0 → 0.16.0; brainstorming skill 0.10.1 → 0.11.0; CHANGELOG [0.16.0] entry added (review 🟡 — version bump on behavior change).
