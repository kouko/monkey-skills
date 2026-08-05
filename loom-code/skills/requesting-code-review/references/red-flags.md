Source: `requesting-code-review/SKILL.md` §"Red Flags — refuse these rationalizations" — serves `requesting-code-review`.

# Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"It's fine, just merge."* | Pre-merge rationalization. Branch hasn't been reviewed; skipping review = shipping without verdict. | Refuse silent skip; dispatch reviewer. If reviewer returns PASS in 30 seconds, the user lost 30 seconds; if it returns NEEDS_REVISION, the user gained a fix-before-prod. |
| *"It's a small change, doesn't need review."* | "Small" is the rationalization. 3 behavioral lines can introduce a regression. | Apply SKILL.md §When NOT to Use carefully: ONLY trivial diffs (one-line typo / mechanical doc edit / version bump / generated regen) skip review. "Small behavioral" does NOT qualify. |
| *"SDD already reviewed each task."* | True for per-task scope; not for cross-task interactions. Tasks 1-4 individually fine, combined introduce a circular dep — that's the gap this skill closes. | Run anyway; the cross-task-coherence dimension is the unique value. |
| *"I'll re-review after CI runs."* | CI is automated tests; this skill is human-judgment quality review. They're complementary, not substitutable. | Run this skill BEFORE pushing; let CI catch the orthogonal issues. |
| *"User said skip review."* | Valid only with explicit override AND §When NOT to Use exemption match. | Quote §When NOT to Use back; ask for explicit re-confirmation. |
| 「審查跳過 / レビューはスキップ」 | Same rationalization, localized. | Same refusal. |
