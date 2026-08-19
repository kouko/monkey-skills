---
name: a-cap-raised-at-every-touch-is-not-a-cap
description: A numeric ceiling that gets raised each time it binds has stopped being a constraint and become a running total; writing-plans' SKILL.md word cap had been raised 17 times and sat one word under its own limit, and the correct move at the 18th was extracting a section to a reference file, not a raise — the tell is the raise-count in the file's own history, not the current number
type: practice
origin: branch plan-field-microstructure (2026-08-19) — the 18th raise would have crossed the repo's hard ceiling, forcing the extraction that should have happened many raises earlier
---

A cap exists to force a decision when content stops fitting: cut, extract, or
argue that this content is worth the room. Raising the number answers the
question by dissolving it. Done once with a reason, that is judgment; done
every time the limit binds, the number is no longer a ceiling — it is a
record of how large the file has grown, updated by whoever last found it in
the way.

`writing-plans/SKILL.md` carried a word cap that had been raised 17 times. The
file sat at 4419 words against its own 4420. Each individual raise had a
plausible local reason, and no single one was the mistake; what was missing was
anyone reading the *sequence*. The 18th raise would have crossed the repo-wide
hard ceiling — an external limit that could not be edited — which is the only
reason the extraction happened at all.

**Why:** the raise is always locally cheaper than the alternative. Extracting a
section means deciding what is load-bearing, finding it a home, and re-pointing
every reference; editing one digit takes seconds and passes review, because a
reviewer sees a one-line diff with a reason attached and not the seventeen that
came before. The constraint therefore decays silently and specifically under
review, not in spite of it. The current value carries no information about this
— 4420 looks exactly as principled as 2000 did.

**How to apply:** when a cap blocks you, read its history first
(`git log -L` on the line, or grep the changelog for the number) and count the
prior raises. Two or more means the cap is not the problem being solved: the
options are extraction to a reference file, deletion, or an explicit decision —
recorded where the next person will read it — that the cap was set wrong and
this is the last raise. A raise with no such record is the eighteenth raise
waiting to happen. Related: [[verified-gate-pytest-suite-misses-skill-structure-word-cap]]
(the same cap, measured rather than enforced).
