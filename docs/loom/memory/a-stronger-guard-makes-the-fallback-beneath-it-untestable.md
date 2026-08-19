---
name: a-stronger-guard-makes-the-fallback-beneath-it-untestable
description: When defence-in-depth stacks a strong check in front of a weaker fallback, the fallback becomes unreachable from the front door — every test exercising that input is answered by the primary, so deleting the fallback entirely leaves the whole suite green and mutation testing reports it as dead code rather than as an unguarded path; the fallback is the ONLY guard on the machines that lack the primary's dependency, so it needs a test that disables the primary deliberately
type: practice
origin: 2026-08-19 cot-explain arc (dev-workflow 2.26.0) — two mutants survived a 12-mutant battery purely because a rebuild-and-compare check answered before the fingerprint check it superseded
---

Adding a stronger check in front of a weaker one is usually right: the
strong check catches more, the weak one remains for environments the strong
one cannot run in. The trap is what it does to the tests.

Every input that would exercise the fallback is now answered by the primary,
**and the assertions still pass**, because both guards produce the same
outcome. So the suite reports coverage it does not have. A mutation battery
makes this legible in a way a green suite never does: delete the fallback
arm entirely and nothing fails — which reads as "dead code", when the truth
is "the only guard left on a machine without the primary's dependency".

The concrete case: a verifier gained a rebuild-the-page-and-compare check in
front of an existing compare-the-recorded-fingerprint check. Two mutants —
removing the fingerprint-absent arm, and removing the fingerprint-mismatch
arm — both survived a battery that killed everything else. The fallback runs
only where the renderer cannot be imported, which is exactly the machine
that received the HTML without the toolchain.

**Why:** test-through-the-front-door is normally the right instinct — it
exercises the real path a user takes. Here there are two user populations
and only one of them can be reached that way. The population that depends
entirely on the fallback is the one whose environment the test suite does
not reproduce.

**How to apply:** whenever you add a check in front of an existing one, ask
which environment still lands on the old one, and write a test that *forces*
that landing — monkeypatch the primary to unavailable, or inject the
condition that disables it — rather than assuming an input will reach it.
Run the deletion mutant for both arms afterwards; if the lower one survives,
the test is still going through the front door. And treat a surviving mutant
in a stacked guard as a coverage report, never as evidence the code is
redundant. Related:
[[a-mutation-test-must-run-the-production-assertion]],
[[a-documented-fallback-can-legitimize-a-delivery-gap]],
[[a-control-placed-downstream-of-what-it-guards-is-not-a-control]].
