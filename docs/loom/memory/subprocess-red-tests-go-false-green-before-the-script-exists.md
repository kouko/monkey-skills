---
name: subprocess-red-tests-go-false-green-before-the-script-exists
description: In a subprocess-driven RED phase, two common assertion shapes pass while the script under test does not exist yet — an absence assertion ("X not in stdout") is trivially true against empty output, and a bare exit-code check for 2 matches the interpreter's own exit 2 for a missing file — so every such test must also assert something only a real run produces
type: gotcha
origin: 2026-08-03, TDD RED phase for `scripts/claim_copy_sweep.py` — 5 of 22 tests passed before a single line of the script was written
---

Writing the failing tests for a CLI before writing the CLI, the first run
reported failures **and five passes**. The script did not exist. Both passing
shapes were structurally incapable of failing:

- **Absence assertions.** `assert "thing.py" not in result.stdout` is
  trivially true when `stdout` is empty — which is exactly what a missing
  script produces. The test asserted nothing about the behaviour it named.
- **Bare exit-code checks.** `assert result.returncode == 2` for a usage error
  passes because the Python interpreter *also* exits 2 when it cannot open the
  script file. The intended cause and the accident share a code.

Both are the false-green class `tdd-iron-law` warns about, but they arrive
through a door the skill's standard diagnostic does not open: the usual advice
is "comment out the production code and confirm the test fails", and here there
was no production code to comment out. The RED run itself is the diagnostic,
and it silently reported five greens.

**Why:** a RED phase is the only moment a test's ability to fail is free to
verify. A test that passes at RED never earns the right to be trusted at GREEN
— it will keep passing through any regression, and nothing later in the cycle
re-checks it. Five such tests would have shipped as coverage that measured
nothing.

**How to apply:** in any subprocess-driven test, pair every absence assertion
and every exit-code assertion with a positive fact only a real run can produce
— a sentinel hit the sweep must report, a substring of the tool's own usage
message on stderr, a summary header. Concretely: `assert "sentinel.md:1" in
result.stdout` alongside the absence check, and `assert "usage" in
result.stderr.lower()` alongside `returncode == 2`. Then **read the RED run's
pass count**: at RED it must be zero, and any green is a defective test, not a
head start. Related: [[grep-tests-scope-to-measured-neighborhood]] is the same
false-green family on prose substring guards.
