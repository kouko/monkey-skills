---
name: pytest-skip-reasons-with-nodeids-come-from-junit-xml-not-from-rs
description: A script that must report each skipped or failed test with both its nodeid and its reason reads them from `--junit-xml`, because `-rs` prints `SKIPPED [n] <file>:<line>: <reason>` with no nodeid, `-v` truncates the reason at the terminal width, and `-n auto` changes the per-test line shape again; the junit `classname` has no `file` attribute on this pytest, so the nodeid is rebuilt by splitting `classname` at the last segment whose `.py` exists (the rest are `::Class` segments)
type: gotcha
origin: 2026-09-05-graduated-probes-independent-of-local-history — build-phase adversary finding on the plan (2026-09-05) and wave-end:1 adversary probe on the class-name splice (2026-09-06)
---

The plan for the rehearsal script said "`-q -rs` and list every skip as
`SKIPPED <nodeid>: <reason>`". The adversary measured before the script
existed: `-rs` emits `SKIPPED [1] path.py:42: reason` — file and line,
never a nodeid a reader can paste back into pytest — while `-v` prints
the nodeid and either drops the reason or cuts it to `ad…` depending on
the terminal width. Neither is a parseable contract.

The width-independent source is `--junit-xml <file>`: one `<testcase>`
per test with `classname`, `name`, and a `<skipped message=…>` or
`<failure>` child. Two traps inside it:

- This pytest writes no `file` attribute, so the path must be rebuilt
  from `classname` (`loom_code.scripts.test_x` → `loom-code/scripts/test_x.py`).
  A test inside a class makes `classname` `…test_x.TestThing`; splitting
  naively yields `…/test_x/TestThing.py`, a nodeid pytest cannot select.
  Split at the last dotted segment whose `.py` exists in the tree and
  emit the remainder as `::TestThing`.
- An xfail is `<skipped type="pytest.xfail">`; filtering by element name
  alone lists expected failures under SKIPPED and inflates the list a
  reader is told to audit.

Keep `-q -rs` as the human-readable tail of the output; never parse it.

Related: [[a-graduated-probe-that-clones-the-repo-asserts-the-subprocess-exit-code]].
