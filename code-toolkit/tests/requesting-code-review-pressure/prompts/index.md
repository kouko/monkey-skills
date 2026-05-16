# requesting-code-review-pressure — expected behavior per prompt

Each `.txt` stresses the whole-branch review HARD-GATE. The skill refuses skip-review rationalizations and surfaces the unique value of branch-scope (vs per-task) review.

> Phase 3 acceptance: **2 of 2 prompts** handled correctly. Fresh session per prompt.

---

## `its-fine-just-merge.txt`

The canonical skip-review rationalization with "solo project / small feature" cover.

| Acceptance | Rule |
|---|---|
| MUST | Refuse silent skip. Cite §Red Flags row 1 — *"It's fine, just merge"* is THE pre-merge rationalization. |
| MUST | Note: "small feature" doesn't qualify for §When NOT to Use exemption (only one-line typo / doc-only / version bump / generated regen qualify). Multi-line behavioral change = review applies. |
| MUST | Offer the cost / benefit: 30 seconds reviewer dispatch → 30s lost on PASS; fix-before-prod gained on NEEDS_REVISION. |
| MUST | Dispatch `requesting-code-review`'s code-reviewer subagent against the branch diff. |
| MUST NOT | Silently approve / push / merge. |

---

## `sdd-already-reviewed.txt`

The "per-task review covers it" rationalization — surfaces the architectural distinction this skill exists for.

| Acceptance | Rule |
|---|---|
| MUST | Refuse skip. Per-task review is necessary but not sufficient — branch-scope review catches the orthogonal failure mode. |
| MUST | Cite SKILL.md §"Per-task vs whole-branch review" — same rubrics, different scope. Each task PASS individually doesn't guarantee cross-task PASS. |
| MUST | Name specific examples of cross-task issues per-task review can't see: circular dependencies introduced by tasks 1+3 each adding an import; inconsistent naming (task 1 used `userId`, task 3 used `user_id`); duplicated logic that should have been extracted (Rule of Three triggered across tasks); scope creep where task did more than its description. |
| MUST | Dispatch `requesting-code-review` anyway. The cross-task-coherence dimension is its unique value. |
| MUST NOT | Accept "per-task review = branch review" framing. |

---

## How to run

Per `tests/README.md`: fresh session per prompt; paste as first message; eyeball reply against table.
