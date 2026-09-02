# Engineering baseline

Advisory reference, not a gate. It is what every `loom-code:implementer`
works under, and what a reviewer reads the work against. Two disciplines
live here: how new behaviour is written (TDD) and how a failure is chased
(four-phase debugging). Nothing here blocks a push; the checker does that,
and it never reads this file.

## 1. The iron law

> **No production code without a failing test first.**

One consequence when it is violated: **delete the code, write the test,
start over.** Not "add a test afterwards", not "a test next round". The
deletion restores the feedback loop the violation switched off.

Grounding, unchanged from the skill this reference replaces:

- Beck (2002), *Test-Driven Development: By Example*, Preface and Ch.1 —
  "Write the test you wish you had. Make it fail. Make it pass. Make it
  clean." Part II supplies the ordered patterns.
- Martin (2008), *Clean Code* Ch.9 — write only enough test to fail, then
  only enough production code to pass.
- 和田卓人 訳『テスト駆動開発』(2017) — the Japanese primary reference:
  tests concretise the specification and supply design feedback.

Together these define TDD as design feedback, not coverage added later.

## 2. Red → green → refactor

- **RED** — write the smallest test that expresses the next increment of
  behaviour. Run it. It **must** fail. A test that passes on its first run
  either describes behaviour that already exists (no new test needed) or
  tests nothing.
- **GREEN** — write the simplest code that makes it pass. *Simplest* is not
  *sloppy*: no speculative generality, no premature abstraction. Duplication
  at GREEN is fine; it goes in the next step.
- **REFACTOR** — with every test green, improve the internal structure
  without changing behaviour. If a test goes red during a refactor, revert
  and take a smaller step. Stopping before this step is "tests-first", which
  is not TDD (Beck 2002, Preface).

**False-green diagnostic.** A test that passed on its first run: comment out
the production change it covers, re-run — it must fail. If it still passes,
the test is not testing what you think; rewrite it until it can fail.
Restore the code, re-run, confirm green.

**Narrow exemptions.** Throwaway code deleted within the same session and
never committed; pure generator output regenerated from a specification;
one-line getters, setters, and pure delegations; configuration files with no
executable behaviour; and an explicit user override that also falls in one
of those categories. Everything else is on the critical path. Do not invent
new exemptions — "I'll clean it up later" and "just this once, it is small"
are the rationalisations the law exists for.

**Legacy backfill is not a violation** (Feathers 2004, *Working Effectively
with Legacy Code*): code inherited without tests is characterised first —
pin its current behaviour, bugs included — and new behaviour then follows
the iron law. The deciding question is whether the test-first opportunity
existed when the code was written. If it did and was skipped, it is a
violation whatever the code's age.

## 3. Debugging: four phases, in order

> **No fixing without reproducing.**

Skip this whole discipline only when a failing test already points at the
wrong line and the fix is one obvious edit, or the defect is a literal typo
or a wrong configuration value with no behaviour chain behind it. If you
cannot prove a change fixed the failure, you did not reproduce it.

**Phase 1 — REPRODUCE.** Produce a reliable trigger: a failing test, or a
recorded command + input + observation. Reliable → continue. Intermittent →
bound the conditions (timing, environment, ordering) and record them before
continuing. Cannot reproduce → the failure is not actionable yet; instrument
the code to capture it next time and say so. Never fix anyway.

**Phase 2 — ISOLATE.** Narrow the surface until you can point at one
component, input field, dependency version, or line. Bisect on whichever
axis is available: commits (`git bisect`) when a known-good version exists,
input (which field or byte matters), dependency version, or pipeline stage
(observation points at module boundaries). For non-code causes — process,
data, a human step — trace with five whys.

**Phase 3 — ROOT CAUSE.** State a falsifiable hypothesis: it must predict an
observation you have not yet made. "I think it is X" is a guess; "if it is
X, then doing Z yields Y, and W yields not-Y" is a hypothesis. Change one
variable per experiment and log each: hypothesis, variable, command,
observed result, confirmed or falsified. The line that throws is rarely the
line that broke. Kernighan & Pike (1999) Ch.5: *"Debugging requires
thinking, not changing."*

**Phase 4 — FIX + REGRESSION TEST.** Apply the fix only against a confirmed
hypothesis, then turn the Phase 1 reproduction into a permanent test — the
reproduction *is* the RED of §2, so the fix is written under the iron law
like any other code. A fix with no regression test leaves the same failure
free to return silently.

If a hypothesis is falsified once, that is the experiment working: revert
whatever speculative change you made and go back to Phase 2 with the new
information. If two hypotheses in a row are falsified, your framing is the
bias — search outside your own head (the framework plus the symptom, in
English and Japanese, including issue trackers) before forming a third, and
say which known pattern it rests on or why none apply.

## 4. Wrong-direction signals

Any one of these means stop iterating and change approach — or report:

- **The same error class survives a fix that should have killed it.** The
  cause is upstream of where you are patching; go find the producer.
- **The fix needs to touch systems unrelated to the symptom.** Either the
  isolation is wrong, or the change is a redesign wearing a fix's clothes.
  Re-isolate, or say so and stop.
- **Each iteration adds a special case instead of removing one.** You are
  encoding the symptom, not the cause. Revert the special cases and return
  to Phase 2.
- **You are about to weaken a test, delete one, or loosen an assertion to
  get green.** That destroys the evidence the whole discipline runs on.
  Never do it: the test is the report, and a passing suite bought this way
  is a false statement about the code. Report the failure instead.
- **A guard or hook blocks the same command twice.** The plan is wrong, not
  the guard. Stop, report the block message verbatim.

The correct response to every one of them is the same: stop, write down what
was tried and what was observed, and either re-enter Phase 2 with that
evidence or hand the failure back with it attached. Repetition is not
progress.

## 5. Working discipline

Terse rules the reviewer reads work against:

1. **Think before coding.** State assumptions; name what is unclear instead
   of guessing; push back when something simpler would do.
2. **Simplicity first.** The minimum code that solves the problem. Nothing
   speculative, no abstraction for a single use.
3. **Surgical changes.** Touch only what the task requires. Clean up only
   your own leftovers. Match the surrounding style.
4. **Read before you write.** Read the exports, the immediate callers, and
   the shared utilities first. "Looks orthogonal" is where regressions live.
5. **Surface conflicts, do not average them.** When two patterns contradict,
   pick one, say why, flag the other.
6. **Tests verify intent.** A test that cannot fail when the logic changes
   is not a test.
7. **Fail loud.** "Done" is wrong if anything was skipped silently; "tests
   pass" is wrong if you did not run them. A claim resting on belief is
   downgraded, never asserted — say "will verify by: `<command>`" instead.
