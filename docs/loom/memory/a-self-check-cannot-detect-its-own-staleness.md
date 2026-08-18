---
name: a-self-check-cannot-detect-its-own-staleness
description: A guard written INSIDE the artifact it protects cannot catch the case where an old copy of that artifact is what ran, because the old copy does not contain the guard either — only a mark the CURRENT code emits, and an old copy therefore cannot emit, discriminates the two; absence of the mark is the signal
type: practice
origin: 2026-08-18 stale-render arc (loom-code 0.88.0) — five HTML views were delivered unconverted because a pre-conversion copy of the renderer ran and exited 0; the first fix proposed was a self-check inside that same renderer
---

A tool that can be deployed in several copies — a plugin cache holding
every released version, an un-rebased worktree, a checkout mid-fix — has a
failure mode where the WRONG COPY ran and its output looks like success. The
intuitive fix is to make the tool verify its own output before writing.

That fix cannot work, and the reason is not subtle once stated: **the stale
copy does not contain the self-check.** Adding a postcondition to today's
code protects against tomorrow's regression in today's code. It says nothing
about the copy from three versions ago that is still sitting on disk and is
still what an executor may run.

What discriminates is the opposite direction — a mark the current code
EMITS into its output, which an older copy cannot emit because it predates
the mark. A version stamp is the cheap form. The signal is then read
inversely: a page with no stamp came from a pre-stamp copy, and a stamp
naming an older version came from that older copy. **Absence is the
evidence.**

**Why:** the two designs feel equivalent when described ("make the tool
catch the bad output") and are not. One is a regression guard for the code
you are editing; the other is an identity claim about which code ran. A team
that ships only the first believes it has covered a failure class it has not
touched, which is worse than shipping nothing — the belief suppresses the
next investigation.

**How to apply:** when a bug's root cause is "an old copy of X ran", ask
which artifact can carry evidence that only the NEW X can produce, and make
the delivery path refuse output lacking it. Add a self-check too if it earns
its place, but state in the same breath what it does not reach — this arc's
first draft of that test's own docstring claimed the fixture "simulates what
a pre-markdown-it copy produces", which was false, and the claim survived
review until someone opened the old copy and compared its output markup.
Related: [[a-mechanical-check-can-go-green-by-skipping]].
