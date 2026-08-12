---
name: removing-over-specificity-removes-guarding-you-did-not-know-it-did
description: A pattern that is too specific produces false alarms, and the obvious fix is to strip the over-specific part — but that part may have been incidentally excluding something, so the fix trades a loud false-positive for a silent false-negative; before loosening any matcher, enumerate what the removed characters were keeping OUT, and check whether a guard elsewhere in the system is a no-op that only stayed safe because of the over-specificity
type: practice
origin: adjudication-view Japanese-support arc (2026-08-12) — stripping the サ変 stem 「し」 from the ja modality forms fixed a real false-warning and opened two silent polarity inversions; caught by a whole-branch reviewer's delta confirmation, not by the fix's own tests
---

The Japanese modality check matched forms like `してはならない`
("must not"). That was over-specific: Japanese modality is a suffix on
whatever verb precedes it, so a *correct* rendition of a non-サ変 verb —
「書き換えてはならない」 — did not match and warned. The fix was obvious
and correct on its own terms: strip the leading 「し」 so the stored form
is a verb-independent suffix.

The 「し」 had also been doing work nobody had named. It sat exactly
where a negation morpheme can be inserted:

| source modal | rendition | what it actually means | before | after |
|---|---|---|---|---|
| must not | 書き換え**なくて**はならない | *must* rewrite | WARNS | silent |
| should | 書き換え**ない**ことが望ましい | desirable *not* to | WARNS | silent |

`なくてはならない` ends in `てはならない`; `ないことが望ましい` ends in
`ことが望ましい`. With the stem present, the inserted negation broke the
match and the check complained. With it stripped, the inverted rendition
matches the affirmative form and the check goes quiet — trading a loud,
harmless false alarm for a silent, meaning-inverting false pass, which is
the direction that defeats the guarantee the check exists for.

There was no second line of defence, and the reason is the sharpest part:
the profile carried a polarity guard (`negation_prefix`) that was set
EMPTY for Japanese, making it a no-op. A comment called that deliberate,
and it *was* safe — but only because the forms carried 「し」. Loosening
the matcher silently promoted a dead field to load-bearing.

**Why:** an over-specific matcher's extra characters are doing two jobs
at once — identifying the thing you meant, and excluding things you never
enumerated. Only the first job is written down, so removing them reads as
a pure win. The false-positive the loosening fixes is visible (someone
complained); the false-negative it opens is silent by definition.

**How to apply:** when loosening any matcher — stripping an affix,
widening a regex, dropping an alternative, replacing exact match with
`startswith`/`endswith`/`in` — write down what the removed part was
keeping out, and construct one input that the old pattern rejected and
the new one accepts. If you cannot construct one, you have not understood
the change. Then audit whether any guard downstream is currently a no-op
or a trivially-satisfied default: loosening upstream is how a dead guard
becomes the only thing standing between you and a silent wrong answer.
The fix, when it comes, should reactivate the structural guard rather
than add another literal to the list — this arc edited the form list
three times (each edit buying a new collision class) before the fourth
fix made the check ask a structural question ("is the matched ending
preceded by a negation?") and both directions finally held at once.

**Contradiction check:** this does not argue against loosening
over-specific patterns — the false warning it fixed was real, and the
non-サ変 case had to be served. It argues that a loosening is a
*behaviour change in two directions* and only one of them shows up in the
bug report you are answering. Related but distinct from
[[a-narrowing-that-leaves-a-substring-passes-every-containment-pin]],
which is about the same edit being invisible to pins elsewhere; this
entry is about the edit's own semantics.
