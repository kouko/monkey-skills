---
name: 2026-08-19-cjk-space-indented-bullet-vanishes-from-both-parsers
description: a nested bullet indented with NBSP or an ideographic space is dropped by BOTH the field-microstructure checker and plan_card, so the gate exits 0 and the rendered card silently loses the bullet — no checker/renderer divergence exists to detect it, and a CJK IME produces these characters without the author seeing anything unusual
status: OPEN
origin: whole-branch review of the field-value-microstructure arc (2026-08-19, round 2) — found by a differential probe over 1152 indent/marker/separator shapes; recorded as pre-existing and out of that arc's scope
start: next touch of `_bullet_lines` in loom-code/scripts/plan_card.py, or the first real report of a bullet missing from a rendered plan card
---

`plan_card._bullet_lines` collects a field's continuation lines only while the
line's first character is exactly `" "` or `"\t"`, and BREAKS out of the field
otherwise. A nested bullet indented with a no-break space (`\xa0`) or an
ideographic space (`　`) therefore ends the field early: the bullet, and
everything under it, is never seen.

Both parsers share that entry point, so they agree — `check_field_microstructure.py`
exits 0 and `plan_card.py --detail` renders the `Description` with the bullet
simply absent. The 2026-08-19 arc hardened the checker/renderer pair against
*divergence*, and this defect produces none. It is a shared blind spot, which
is why that arc's differential probe found it only as a by-product.

**Why it is worth fixing rather than ignoring.** This repo's plans are written
in mixed Chinese/Japanese/English, and a CJK IME emits `　` for the space
key in full-width mode. The author sees indentation that looks correct in every
editor. Nothing in the toolchain reports anything: the gate passes, the card
renders, and the only symptom is that a bullet the author wrote is not on the
card. Silent content loss with a green gate is precisely the class the
field-value-microstructure arc exists to close — this instance survived because
it sits one layer below where that arc looked.

**Fix shape (not decided).** Either widen `_bullet_lines`' continuation test to
any Unicode whitespace — which aligns it with `_NESTED_BULLET_LINE`'s `\s`, the
same alignment the 2026-08-19 arc applied one line further down for tabs — or
reject such lines loudly rather than dropping them. The first is the smaller
change and matches the direction already taken; the second surfaces the typo to
the author instead of normalising it, which may be the better service. Whoever
opens this should decide deliberately and record why.

Pin with a fixture using literal `　` and `\xa0` indents, and make the pin
fail on the REVERSAL of the fix, not merely on its deletion — see
`docs/loom/memory/assertion-must-encode-the-property-it-claims.md`.

Related: `docs/loom/backlog/2026-08-06-plan-card-cjk-aware-gloss-line-join.md`
(the sibling CJK defect in the same renderer, also still open — a fix touching
`plan_card.py` should look at both).
