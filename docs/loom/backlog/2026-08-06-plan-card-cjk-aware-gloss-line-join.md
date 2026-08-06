---
name: 2026-08-06-plan-card-cjk-aware-gloss-line-join
description: plan_card.py joins wrapped bullet lines with a space, which is correct for Latin text but inserts a stray mid-word space in CJK glosses (e.g. 大聲報錯教 你正確寫法) — the join should be width-aware (no space between CJK codepoints)
status: OPEN
origin: 0.63.0 plan review round-2 note 3 (plan-document-reviewer, 2026-08-06) — pre-existing renderer behavior affecting every plan with zh-TW Gloss lines
start: next scripts/plan_card.py touch
---

# plan_card CJK-aware gloss line join

`_bullet_lines` / the gloss renderer joins a wrapped plan bullet's
continuation lines with `" ".join(...)`. Latin text needs the space;
CJK text does not, so every zh-TW `Gloss:` that wraps in the plan file
renders with a stray space mid-word in the card.

Fix shape: join adjacent lines without a space when the boundary
codepoints are both CJK (East Asian Width W/F), keep the space
otherwise. Pin with a wrapped-CJK fixture asserting the exact joined
output.
