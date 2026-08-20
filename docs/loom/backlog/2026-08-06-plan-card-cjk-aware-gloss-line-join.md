---
name: 2026-08-06-plan-card-cjk-aware-gloss-line-join
description: plan_card.py joins wrapped bullet lines with a space, which is correct for Latin text but inserts a stray mid-word space in CJK glosses (e.g. 大聲報錯教 你正確寫法) — the join should be width-aware (no space between CJK codepoints); reproduced again 2026-08-19 by the field-value-microstructure plan's own Goal line (而 審查者的判斷), still unfixed
status: open
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

2026-08-10 note: since PR #680 the canonical code lives at
`loom-code/scripts/plan_card.py` (the repo-root `scripts/plan_card.py` is an
exec shim); the code references in this entry refer to the canonical file.

## Trigger met, defect reproduced again (2026-08-19)

This entry's start condition — "next `scripts/plan_card.py` touch" — is
met by Task 5/Task 6 of
`docs/loom/plans/2026-08-19-field-value-microstructure.md` (both edit
`loom-code/scripts/plan_card.py`). Neither task touches the join
function this entry is about, so the defect is not fixed by that arc —
it is out of that brief's scope and stays open here.

The same plan's own rendered card reproduces the defect, this time in a
`Goal:` header value rather than a `Gloss:` bullet (same join path:
`_header_value` folds continuation lines with `" ".join(...)` exactly
like `_bullet_value` does):

```
$ python3 loom-code/scripts/plan_card.py docs/loom/plans/2026-08-19-field-value-microstructure.md
goal: ...而判定這件事的是機械檢查而非 審查者的判斷。
```

— a stray space between `非` and `審`, both CJK codepoints, at the
line-wrap boundary. Recorded here as a second worked instance; **not
fixed by this arc**, which is out of scope for
`docs/loom/plans/2026-08-19-field-value-microstructure.md`. Status stays
`OPEN`.
