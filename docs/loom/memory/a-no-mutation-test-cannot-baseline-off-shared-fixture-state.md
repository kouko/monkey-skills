---
name: a-no-mutation-test-cannot-baseline-off-shared-fixture-state
description: A "does not mutate its input" test that snapshots a SHARED fixture as its baseline is vacuous against an IDEMPOTENT write-back — earlier tests already ran the code over that state, so the mutation is in the baseline and the assertion compares it to itself; the tell is passing in-file and failing alone, the fix is a pristine read, and a deep copy of the polluted state inherits the blindness
type: gotcha
sources:
  - resource: feat-us-quarterly-statement-series Task E (US quarterly series arc, 2026-07-30)
---

A test named `test_derivation_does_not_mutate_the_statements_it_is_given` guarded
the load-bearing invariant of a whole arc: that a derivation must not write its
results back over its inputs. Its body was the obvious one —

```python
before = copy.deepcopy(fixture_doc["statements"])
derive(fixture_doc["statements"])
assert fixture_doc["statements"] == before
```

`fixture_doc` was **module-scoped**, and **seven earlier tests in the same file had
already called `derive` on it**. So a mutant that wrote each derived value back into
the caller's own rows **passed the entire file** and failed only when that one test
was selected alone. The write-back was already present when the baseline was taken;
the assertion compared the mutation to itself.

The mutation has to be **idempotent** for this to hide — writing the same value to
the same key on every call. A write that grows or changes with each call is still
caught, which is why the test looks alive. It is alive for the easy case and blind
to the exact shape the arc existed to remove.

**The trap inside the trap.** The obvious fix — baseline off the file's own
function-scoped copy fixture — does not work, and this was measured rather than
argued: that fixture `deepcopy`s the same polluted module-scoped dict, so it
inherits the blindness and reproduces the failure mode byte for byte. An
orchestrator proposed exactly that fix; the implementer rejected it and measured
why. **Only a read that never passed through the shared object is a trustworthy
baseline** — here, re-reading the fixture file from disk.

**A second mechanism makes the pollution wider than it looks.** The suite's test
double returned the fixture's own substructure **by reference**:

```python
return full["statement_data"]          # not a copy
```

so tests that reached the data through the production API — rather than touching the
fixture directly — were *also* not insulated. Counting the polluting tests by hand
gave "about a dozen" from two different reviewers; counting them programmatically
gave **seven**. Instrument the mutation and run each node id paired with a pollution
probe; do not estimate.

**Why:** a no-mutation assertion is the one test whose correctness depends on the
provenance of its baseline rather than on the values in it. Every other assertion
compares against something the test states; this one compares against something the
test *captured*, and capture order is invisible in the test body. Shared fixtures
are otherwise good practice — they are fast and they keep tests short — so nothing
in the test looks wrong, and the defect is one word (`fixture_doc`) in a line that
reads as boilerplate.

**How to apply:**

1. **Baseline a no-mutation test from a pristine read** — re-read the file, rebuild
   the object, or use a fixture scoped so nothing has touched it. Never from state
   the code under test may already have visited, and never from a copy of it.
2. **The detection is mechanical: run the test alone and in-file.** A no-mutation
   test that passes in-file and fails alone under a mutant is order-dependent, and
   the ordering is doing the work its assertion claims to do. Add "every node id
   passes alone as well as together" to the suite's own checks — it is one command
   and it catches this whole class.
3. **Check what your test doubles hand back.** A double returning a slice, a view,
   or a nested object by reference silently widens shared state to every test that
   goes near it. Copy on the way out, or know exactly who is aliased.
4. **Mutate idempotently when probing this class.** A growing or varying mutation
   is the easy case and will make the test look sound.

Relates to [[a-test-can-be-correct-and-still-unable-to-fail]] (the same class by a
different route — there the inputs made the mutation arithmetically inert, here the
baseline already contained it) and to
[[construction-guaranteed-invariant-proves-nothing]] (an assertion whose subject is
guaranteed by how the test was built rather than by the code).
