"""Tests for check_scenario_coverage.py — the coverage script that compares
a loom-design change-folder's `#### Scenario:` set (per
`loom-design/scripts/spec/validate_spec_output.py`'s heading grammar: `### Requirement:`
/ `#### Scenario:`) against a writing-plans plan's join keys (`<change-id> /
Requirement: <name> / Scenario: <name>`, from each task's `Brief item covered`
field — see `loom-code/skills/writing-plans/references/plan-format.md`).

Exercised as a CLI subprocess (the actual interface: two positional args,
exit 0 / exit 1) rather than importing internals, since the contract this
script must honor is the process boundary.

Brief mode (`--brief <brief> <plan>`, no change-folder) is exercised the
same way, as a subprocess.

The brief-item collector is the one exception, tested by direct import:
its per-identifier results (which ids, at which line numbers) are not
visible at the process boundary, which reports only the resolution
outcome.

Stdlib only (subprocess + pathlib), plus a direct import of the module
under test for the collector tests.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

from check_scenario_coverage import collect_brief_item_ids

SCRIPT = Path(__file__).parent / "check_scenario_coverage.py"

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run(change_folder: Path, plan_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(change_folder), str(plan_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


def _write_spec(change_folder: Path, body: str) -> None:
    spec_dir = change_folder / "specs" / "widgets"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(body, encoding="utf-8")


_TWO_SCENARIO_SPEC = """\
## ADDED Requirements

### Requirement: Users can filter by date
The system MUST allow filtering.

#### Scenario: Empty result set
- GIVEN no records match
- WHEN filter applied
- THEN empty list returned

#### Scenario: Single match
- GIVEN one record matches
- WHEN filter applied
- THEN one item returned
"""


def test_full_coverage_exit_0(tmp_path):
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Empty result set\n\n"
        "## Task 2 — bar\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Single match\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


def test_dropped_scenario_named_on_stderr_exit_1(tmp_path):
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Empty result set\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 1
    assert "Single match" in result.stderr
    assert "2026-07-10-my-change" in result.stderr
    assert "Users can filter by date" in result.stderr
    # the covered scenario must NOT be reported as dropped
    assert "Empty result set" not in result.stderr


_LEGACY_BRACKET_SPEC = """\
## ADDED Requirements

### Requirement: Legacy thing [deferred]
The system MUST allow something legacy.

#### Scenario: S1
- GIVEN a precondition
- WHEN an action
- THEN an outcome
"""


def test_legacy_header_with_bracket_suffix_keys_by_full_header_text(tmp_path):
    """A legacy (non-id-form) `### Requirement:` header keeps its trailing
    `[status]` bracket suffix AS PART OF the key's requirement segment —
    the legacy path must stay byte-identical to the pre-id-aware grammar
    (`^###\\s+Requirement:\\s*(.*)$`), which captured the whole header text
    including any bracket. A plan citing the key with the bracket included
    must resolve (exit 0)."""
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _LEGACY_BRACKET_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Legacy thing [deferred] / Scenario: S1\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


_ID_ONLY_NO_NAME_SPEC = """\
## ADDED Requirements

### Requirement: REQ-3
The system MUST allow something with an id but no display name.

#### Scenario: S1
- GIVEN a precondition
- WHEN an action
- THEN an outcome
"""


def test_id_only_header_without_name_does_not_flip_file_to_id_mode(tmp_path):
    """A header whose `id` group matched but whose `name` group did NOT
    (`### Requirement: REQ-3`, no `— <name>` suffix) must not flip the
    whole file into id-mode — aligned with validate_spec_output.py's own
    `is_id_form = bool(m.group("id")) and bool(m.group("name"))`
    predicate. The file stays legacy-keyed: the key's requirement segment
    is `Requirement: REQ-3` (legacy form), not the bare `REQ-3` id-mode
    form."""
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _ID_ONLY_NO_NAME_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: REQ-3 / Scenario: S1\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


def test_malformed_plan_prose_only_zero_coverage_exit_1(tmp_path):
    """A plan whose 'Brief item covered' fields are all prose referents
    (kind (a) — no join-key grammar) has zero join keys — treat as zero
    coverage: every scenario is reported dropped."""
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: \"some unrelated brief prose, not a join key\"\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 1
    assert "Empty result set" in result.stderr
    assert "Single match" in result.stderr


def test_malformed_plan_no_brief_item_field_at_all_zero_coverage_exit_1(tmp_path):
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan: x\n\n## Task 1 — foo\n- Description: does stuff\n",
                     encoding="utf-8")
    result = _run(change_folder, plan)
    assert result.returncode == 1
    assert "Empty result set" in result.stderr
    assert "Single match" in result.stderr


def test_empty_change_folder_vacuous_exit_0(tmp_path):
    change_folder = tmp_path / "2026-07-10-empty-change"
    change_folder.mkdir(parents=True)
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan: x\n", encoding="utf-8")
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
    assert "vacuous" in result.stdout.lower() or "no" in result.stdout.lower()


def test_missing_plan_file_treated_as_zero_coverage_exit_1(tmp_path):
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "does-not-exist.md"
    result = _run(change_folder, plan)
    assert result.returncode == 1
    assert "Empty result set" in result.stderr
    assert "Single match" in result.stderr


_HASH_IN_BODY_SPEC = """\
## ADDED Requirements

### Requirement: Users can filter by date
The system MUST allow filtering.

#### Scenario: Empty result set
- GIVEN no records match
- WHEN filter applied
- THEN empty list returned

```python
# a comment inside an example code fence
x = 1
```

#### Scenario: Single match
- GIVEN one record matches
- WHEN filter applied
- THEN one item returned
"""


def test_single_hash_comment_in_scenario_body_does_not_truncate(tmp_path):
    """A `# comment` line inside a scenario body's example code fence must
    NOT be treated as a section boundary — parity with
    validate_spec_output.py's `_ANY_HEADER = re.compile(r"^#{2,4}\\s")`,
    which deliberately excludes single-#. If the boundary wrongly matches
    the `# comment` line, the requirement's scope truncates before the
    second `#### Scenario:` header, and that scenario silently vanishes
    from the folder scan — undetectable as 'dropped' since the script never
    knew it existed. Here the plan does NOT cover 'Single match', so a
    correct scanner must report it dropped (exit 1)."""
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _HASH_IN_BODY_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Empty result set\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 1
    assert "Single match" in result.stderr


_DUPLICATE_SCENARIO_SPEC = """\
## ADDED Requirements

### Requirement: Users can filter by date
The system MUST allow filtering.

#### Scenario: Empty result set
- GIVEN no records match
- WHEN filter applied
- THEN empty list returned

#### Scenario: Empty result set
- GIVEN no records match again
- WHEN filter applied
- THEN empty list returned
"""


def test_duplicate_scenario_key_warns_on_stderr(tmp_path):
    """Duplicate (requirement, scenario) name pairs collapse into one set
    entry — an uncovered duplicate instance would otherwise be
    undetectable. The script must warn on stderr naming the duplicated
    key (without changing the join-key format) and still proceed.

    The warning is located by its line-initial `Warning: duplicate scenario
    key` prefix, and the duplicated key is then sought in THAT LINE — not in
    the whole stderr blob. Searching the blob for the bare word would make
    the assertion self-satisfying the day the message grows a path for
    context: `tmp_path` names its directory after this function, so
    `duplicate` would arrive through the fixture path and the check would
    still pass with the implementation's word deleted. Today's message
    interpolates only `change_folder.name`, but nothing enforces that, so
    the pin does not rely on it.
    """
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _DUPLICATE_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Empty result set\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
    warnings = [line for line in result.stderr.splitlines()
                if line.startswith("Warning: duplicate scenario key")]
    assert warnings, (
        "a duplicate key must be announced by a line opening "
        f"'Warning: duplicate scenario key' — got:\n{result.stderr}"
    )
    assert "Empty result set" in warnings[0], \
        "the announcement must name the duplicated key"


_ID_MODE_SPEC = """\
## ADDED Requirements

### Requirement: REQ-3 — Foo
The system MUST allow filtering.

#### Scenario: S1
- GIVEN one record matches
- WHEN filter applied
- THEN one item returned

### Requirement: REQ-4 — Foo
The system MUST allow something else, same name as REQ-3 on purpose.

#### Scenario: S1
- GIVEN a different record matches
- WHEN filter applied
- THEN one item returned
"""


def test_id_mode_folder_keys_use_req_id_and_plan_key_resolves(tmp_path):
    """An id-mode requirement header (`### Requirement: REQ-3 — Foo`) keys
    its scenario as `<change-id> / REQ-3 / Scenario: <name>` — bare id, no
    `Requirement:` prefix — so a plan citing that same bare-id join key
    resolves and the folder is fully covered (exit 0).

    A second id-mode requirement (`REQ-4 — Foo`) shares REQ-3's exact NAME
    and also declares a `Scenario: S1`. Under the legacy name-keyed grammar
    this would collide into one set entry and trip the duplicate-key
    warning; keyed by id instead, `REQ-3 / Scenario: S1` and `REQ-4 /
    Scenario: S1` are two distinct keys, so no collision and no warning —
    that is the whole point of moving the key off the (unstable,
    coincidentally shared) name and onto the (stable, always-distinct) id.
    """
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _ID_MODE_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / REQ-3 / Scenario: S1\n\n"
        "## Task 2 — bar\n"
        "- Brief item covered: 2026-07-10-my-change / REQ-4 / Scenario: S1\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
    assert "duplicate scenario key" not in result.stderr


_ID_MODE_TWO_SCENARIO_SPEC = """\
## ADDED Requirements

### Requirement: REQ-3 — Foo
The system MUST allow filtering.

#### Scenario: S1
- GIVEN one record matches
- WHEN filter applied
- THEN one item returned

#### Scenario: S2
- GIVEN a second record matches
- WHEN filter applied
- THEN a second item returned
"""


def test_bare_req_id_citation_covers_all_scenarios_of_that_requirement(tmp_path):
    """A `Brief item covered` value that is exactly a bare `REQ-<n>` token
    (referent kind (d), OQ-3 option A) covers EVERY scenario under that
    requirement in the bound change-folder — one task citing `REQ-3` is
    enough to discharge both `S1` and `S2`.

    A bare id naming a requirement the folder never declares (`REQ-9`) is
    unambiguous, unlike prose: it is an ERROR (exit 1) naming the task and
    quoting the value, mirroring the brief-mode unresolvable-citation
    diagnostic shape.
    """
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _ID_MODE_TWO_SCENARIO_SPEC)

    covered_plan = tmp_path / "plan.md"
    covered_plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: REQ-3\n",
        encoding="utf-8",
    )
    result = _run(change_folder, covered_plan)
    assert result.returncode == 0, (
        f"a bare REQ-3 citation must cover both of REQ-3's scenarios\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    undeclared_plan = tmp_path / "plan_bad.md"
    undeclared_plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — bogus\n"
        "- Brief item covered: REQ-9\n",
        encoding="utf-8",
    )
    bad_result = _run(change_folder, undeclared_plan)
    assert bad_result.returncode == 1, (
        "a bare REQ-<n> matching no id-form header in the folder must fail "
        f"the run\nstdout:\n{bad_result.stdout}\nstderr:\n{bad_result.stderr}"
    )
    assert "REQ-9" in bad_result.stderr, \
        "the undeclared value must be quoted so the author can find it"
    assert "Task 1 — bogus" in bad_result.stderr, \
        "the offending task must be named"


def test_citation_error_alone_exits_1_without_dropped_header(tmp_path):
    """Pins main()'s two exit-1 guards: a run with full scenario coverage
    (no dropped keys) but ONE citation error must still exit 1 — the
    citation error alone is enough (`if ok and not citation_errors:` must
    not short-circuit to a success message) — and must NOT print the
    "Dropped scenario(s)" header (the `if dropped:` guard must stay gated
    on an actually non-empty `dropped` list, not fire just because the run
    is non-zero).

    Folder REQ-3 (id-mode) has S1+S2. Task 1 cites the bare `REQ-3` id,
    fully covering both scenarios (`dropped` ends up empty). Task 2 cites
    the undeclared `REQ-9`, which is a citation error. The run must fail
    on the citation error alone, with no dropped-scenario header at all.
    """
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _ID_MODE_TWO_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: REQ-3\n\n"
        "## Task 2 — bogus\n"
        "- Brief item covered: REQ-9\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 1, (
        f"a citation error alone (no dropped scenarios) must still fail "
        f"the run\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "Task 2 — bogus" in result.stderr
    assert "REQ-9" in result.stderr
    assert "Dropped scenario(s)" not in result.stderr, (
        "no scenario was actually dropped — the citation error is the "
        "only failure — so the dropped-scenario header must not print\n"
        f"stderr:\n{result.stderr}"
    )


def test_unparsed_change_folder_referent_is_named_not_dropped(tmp_path):
    """A `Brief item covered` value that does not match the join-key
    grammar must be reported with its task and its verbatim text, not
    silently skipped. Otherwise a typo among otherwise-valid keys reads as
    'this scenario has no task' — a different repair from 'this citation
    did not parse', reported today with the same message.

    It stays a report, never an error: on this path a prose quote is a
    legal referent kind (`plan-format.md` referent kind (a)), so an
    unparsed value is genuinely ambiguous between a legitimate quote and a
    typo. Exit code therefore still reflects coverage alone — here exit 1,
    because the typo'd task covers nothing.
    """
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    typo_value = ("2026-07-10-my-change / Requirment: Users can filter by date "
                  "/ Scenario: Single match")
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Empty result set\n\n"
        "## Task 2 — typo'd join key\n"
        f"- Brief item covered: {typo_value}\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 1
    # the unparsed value, verbatim, and the task it sits under
    assert typo_value in result.stderr
    assert "Task 2 — typo'd join key" in result.stderr


def test_unparsed_value_is_attributed_to_the_nearest_preceding_heading(tmp_path):
    """The task named for an unparsed value must be the NEAREST PRECEDING
    heading, not merely *some* heading in the document.

    A two-heading fixture cannot pin this: with the unparsed value under the
    last heading, an implementation that ignores position and returns the
    last (or the first, or any fixed) heading still satisfies it. Here the
    plan has five headings and the typo sits under the SECOND task, so
    returning the document's last heading ('Task 4'), its first ('Plan:
    nearest-heading fixture'), or any other names the wrong task and fails.

    Coverage is complete (Task 1 and Task 3 between them cite both
    scenarios), so exit stays 0: the unparsed-value report is a diagnostic,
    never an error. It rides the per-item stderr channel word 'Warning: ',
    the same word the duplicate-key per-item report uses, so grepping
    stderr for 'Warning: ' enumerates every per-item diagnostic.
    """
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    typo_value = ("2026-07-10-my-change / Requirment: Users can filter by date "
                  "/ Scenario: Single match")
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: nearest-heading fixture\n\n"
        "## Task 1 — the first task\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Empty result set\n\n"
        "## Task 2 — the typo'd task\n"
        f"- Brief item covered: {typo_value}\n\n"
        "## Task 3 — a later task\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Single match\n\n"
        "## Task 4 — the last task\n"
        "- Description: no brief item field at all\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
    assert "Warning: " in result.stderr, \
        "per-item stderr diagnostics use the 'Warning: ' channel word"
    assert typo_value in result.stderr
    # the nearest preceding heading, and ONLY it
    assert "Task 2 — the typo'd task" in result.stderr
    assert "Task 1 — the first task" not in result.stderr
    assert "Task 3 — a later task" not in result.stderr
    assert "Task 4 — the last task" not in result.stderr
    assert "Plan: nearest-heading fixture" not in result.stderr


# A realistic brief: three declared identifiers across TWO sections, plus
# every near-miss the shipped convention rules out —
# `handoff-brief-format.md` §Brief item identifiers names `BI1`, `bi-1` and
# `B-1` as explicitly not the form, and demonstrates the form itself inside
# a ```markdown fence, which makes a fence the documented carrier for
# illustrative (non-declaring) identifiers. Without these near-misses the
# collector's precision is untested: a bare `BI-\\d+` substring scan passes
# a fixture that only holds well-formed declarations.
_BRIEF_WITH_THREE_IDS = """\
# widget rework — brief

## Problem

When a plan cites a brief item, I want the citation to survive a reword.

## Smallest End State

The brief carries stable identifiers. Note that BI-42 is discussed in this
sentence but never declared, so a scan that reads prose as declarations
would invent it.

- BI-1 — Brief items carry an identifier that survives rewording.
- BI-2 — The coverage checker resolves a cited identifier to a declared item.

## Out of Scope

- Renumbering existing items. See BI-2 above for what we do instead.
- BI1 — the prefix without its hyphen is not the form.
- bi-1 — lowercase is not the form.
- B-1 — a single-letter prefix is not the form.

## Decision

We ship the identifier convention and the checker's brief mode together.

- BI-3 — The umbrella outcome this decision commits to.

## Template

```markdown
- BI-9 — (example identifier inside a fenced skeleton, never a declaration)
```
"""


def _lineno_of(text: str, line: str) -> int:
    """1-based line number of the one line equal to `line`."""
    hits = [i for i, candidate in enumerate(text.splitlines(), start=1)
            if candidate == line]
    assert len(hits) == 1, f"fixture must hold exactly one {line!r}: {hits}"
    return hits[0]


def test_collects_declared_brief_item_ids():
    """The collector returns every declared `BI-<n>` with its 1-based line
    number, and nothing else.

    Three properties are pinned together because each one alone is passed
    by a wrong collector that the others catch:

    - **Form.** `handoff-brief-format.md` §Brief item identifiers rules out
      `BI1`, `bi-1` and `B-1` by name. A regex loosened to accept `BI<n>`
      would collect the `BI1` bullet.
    - **Position.** A declaration is the identifier FIRST on its line, then
      the item text. `BI-42` and `BI-2` also appear mid-sentence in prose
      here; a scan that matches anywhere on the line invents `BI-42` and
      mis-locates `BI-2` to the prose line.
    - **Line number.** Pinned to the exact declaring line, so an off-by-one
      (0-based, or the line after) fails. The numbers are looked up from
      the fixture by exact line text rather than hardcoded, so editing the
      fixture cannot silently desync the expectation from the pin.

    Sections are not enumerated: `BI-3` sits in `## Decision` and `BI-1` /
    `BI-2` in `## Smallest End State`, and the convention's extension clause
    lets a fourth section declare outcomes too — so the collector must scan
    the whole file, and a three-section allowlist is not a legal shortcut.
    """
    text = _BRIEF_WITH_THREE_IDS
    assert collect_brief_item_ids(text) == {
        "BI-1": _lineno_of(
            text,
            "- BI-1 — Brief items carry an identifier that survives rewording."),
        "BI-2": _lineno_of(
            text,
            "- BI-2 — The coverage checker resolves a cited identifier to a "
            "declared item."),
        "BI-3": _lineno_of(
            text, "- BI-3 — The umbrella outcome this decision commits to."),
    }


def test_fenced_example_identifier_is_not_a_declaration():
    """`BI-9` sits inside the fixture's ```markdown fence and must not be
    collected.

    The shipped convention demonstrates the form inside a fence
    (`handoff-brief-format.md` §Brief item identifiers), and its
    `## Template` nests a whole brief skeleton carrying `BI-1` / `BI-2` /
    `BI-3` example lines. A brief that pastes such a skeleton would
    otherwise gain phantom identifiers that no task can ever deliver — and,
    worse, would resolve a downstream citation against an example instead
    of failing it.
    """
    assert "BI-9" not in collect_brief_item_ids(_BRIEF_WITH_THREE_IDS)


def test_legacy_brief_declaring_no_ids_returns_empty_without_raising():
    """A brief predating the convention declares zero identifiers. That is
    a legal legacy brief, not an error: the collector returns an empty
    mapping rather than raising, which is what lets the caller enter legacy
    mode instead of failing every brief written before the convention
    landed."""
    legacy = (
        "# older brief\n\n"
        "## Smallest End State\n\n"
        "The thing works end to end.\n\n"
        "## Decision\n\n"
        "We build the thing.\n"
    )
    assert collect_brief_item_ids(legacy) == {}


# A brief that declares `BI-2` twice — the authoring error the never-reused
# rule forbids. The two declarations carry different item text so each line
# can be located by its exact text rather than a hardcoded number.
_BRIEF_WITH_DUPLICATE_ID = """\
# duplicated-identifier brief

## Smallest End State

- BI-1 — An outcome declared exactly once.
- BI-2 — The second outcome, declared here first.

## Decision

- BI-2 — The same identifier reused by mistake, further down the file.
"""


def test_duplicate_brief_item_declaration_warns_and_first_line_wins(capsys):
    """A `BI-<n>` declared twice is an authoring error the never-reused rule
    forbids, so the collector must not resolve it in silence.

    Two properties are pinned together, because the silence had two halves
    and closing either one alone leaves the other open:

    - **The warning.** It rides the `Warning: ` per-item stderr channel word
      the sibling collector already uses (`collect_folder_scenario_keys`,
      pinned by `test_duplicate_scenario_key_warns_on_stderr`), and names the
      identifier plus BOTH declaring lines — one line number alone tells an
      author a duplicate exists without telling them where the other half is.
    - **The resolution.** First-declaration-wins was previously an untested
      choice of `setdefault`. Pinned here so flipping it to last-wins fails,
      rather than being caught only by whichever downstream caller happened
      to depend on the line number.
    """
    text = _BRIEF_WITH_DUPLICATE_ID
    first = _lineno_of(text, "- BI-2 — The second outcome, declared here first.")
    later = _lineno_of(
        text,
        "- BI-2 — The same identifier reused by mistake, further down the file.")
    assert first < later, "fixture must declare the duplicate after the original"

    declared = collect_brief_item_ids(text)

    # the resolution: first declaration wins, unchanged by the warning
    assert declared["BI-2"] == first
    assert declared == {
        "BI-1": _lineno_of(text, "- BI-1 — An outcome declared exactly once."),
        "BI-2": first,
    }

    err = capsys.readouterr().err
    assert "Warning: " in err, \
        "per-item stderr diagnostics use the 'Warning: ' channel word"
    assert "BI-2" in err
    assert f"line {first}" in err, "the warning must name the first declaration"
    assert f"line {later}" in err, "the warning must name the later declaration"


# --- brief mode: resolving citations against the brief's declared ids ---


def _run_brief(brief_path: Path, plan_path: Path) -> subprocess.CompletedProcess:
    """Brief mode's process boundary: `--brief <brief> <plan>`, no
    change-folder positional — a brief-only plan has none to pass."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--brief", str(brief_path), str(plan_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


_BRIEF_TWO_IDS = """\
# widget rework — brief

## Smallest End State

- BI-1 — Brief items carry an identifier that survives rewording.
- BI-2 — The coverage checker resolves a cited identifier to a declared item.
"""


def test_unresolvable_citation_errors_when_brief_declares_ids(tmp_path):
    """A citation naming an id the brief never declared is an ERROR that
    names the task and quotes the value verbatim.

    Three properties are pinned together, each one alone passed by a wrong
    implementation the others catch:

    - **It is an error, not a warning.** Before this check existed, an
      unknown `BI-99` contributed nothing and the run exited 0 — the
      fail-open this arc closes. A version that prints the same sentence
      on stderr and still exits 0 leaves the plan shippable, so the exit
      code is asserted, not the message alone.
    - **The offending value is quoted.** A message reading only "a citation
      did not resolve" sends the author to read all ten tasks. `BI-99` must
      appear so the value is findable by search.
    - **The task is named.** Same reason, other axis: the value alone does
      not say where it sits.

    The grammar is unambiguous here — the brief declares ids, so the quote
    referent is no longer legal — which is why this path errors while the
    change-folder path only reports (see
    `test_unparsed_change_folder_referent_is_named_not_dropped`).
    """
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_TWO_IDS, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: BI-1\n\n"
        "## Task 2 — bar\n"
        "- Brief item covered: BI-99 — an item no brief ever declared\n",
        encoding="utf-8",
    )
    result = _run_brief(brief, plan)
    assert result.returncode != 0, \
        f"an unresolvable citation must fail the run, got 0\n{result.stdout}"
    assert "BI-99" in result.stderr, \
        "the unresolvable value must be quoted so the author can find it"
    assert "Task 2 — bar" in result.stderr, \
        "the offending task must be named"
    # the resolvable citation is not collateral damage
    assert "Task 1 — foo" not in result.stderr


def test_value_with_no_identifier_at_all_errors_when_brief_declares_ids(tmp_path):
    """A value that is plain prose — carrying no `BI-` substring anywhere —
    is an ERROR once the brief declares identifiers.

    This is the sibling of the typo'd-id pin above, and the likelier of the
    two in practice: an author reaching this state has simply written the
    old quote form (or a bare description) and never added an identifier,
    which is what every plan written before this convention looks like. The
    typo pin exercises the `unknown` branch; only this one exercises the
    empty-`cited` branch, and the two fail for different reasons — an
    implementation that errors only on ids it does not recognise passes the
    typo pin while letting every un-identified value through, which is the
    fail-open this arc exists to close.

    The distinct diagnostic is asserted, not just the exit code: "cites
    BI-99, which the brief does not declare" would misdescribe a value that
    cites nothing, and sends the author looking for an id that was never
    written.
    """
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_TWO_IDS, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: BI-1\n\n"
        "## Task 2 — ship\n"
        "- Brief item covered: the widget rework ships end to end\n",
        encoding="utf-8",
    )
    result = _run_brief(brief, plan)
    assert result.returncode != 0, (
        "a value naming no identifier under a brief that declares them must "
        f"fail the run, got 0\n{result.stdout}"
    )
    assert "Task 2 — ship" in result.stderr, "the offending task must be named"
    assert "the widget rework ships end to end" in result.stderr, \
        "the un-identified value must be quoted so the author can find it"
    assert "cites no BI-" in result.stderr, (
        "the diagnostic must say the value cites NOTHING — reusing the "
        "unknown-id wording sends the author hunting for an absent id"
    )
    # the resolvable citation is not collateral damage
    assert "Task 1 — foo" not in result.stderr


# A plan carrying BOTH referent kinds at once: two tasks citing `BI-<n>`
# identifiers (kind (c)) and one citing the change-folder join key
# `<change-id> / Requirement: … / Scenario: …` (kind (b)). `plan-format.md`
# declares both legal for the same field, and `writing-plans/SKILL.md` fires
# brief mode on any brief declaring `BI-` ids — change-folder or not — so
# this plan is what a change with both a brief and a change-folder actually
# looks like when brief mode runs over it.
_PLAN_MIXING_JOIN_KEY_AND_IDS = (
    "# Plan: x\n\n"
    "## Task 1 — identifier referent\n"
    "- Brief item covered: BI-1\n\n"
    "## Task 2 — join-key referent\n"
    "- Brief item covered: widget-rework / Requirement: Users can filter by "
    "date / Scenario: Empty result set\n\n"
    "## Task 3 — the other identifier\n"
    "- Brief item covered: BI-2\n"
)


def _stderr_lines_naming(task: str, stderr: str) -> list[str]:
    """Every stderr line that names `task` — the register (`Error:` /
    `Warning:`) is the line's own prefix, so a caller can assert which one
    a task was reported under rather than merely that it appeared."""
    return [line for line in stderr.splitlines() if task in line]


def test_wellformed_join_key_is_a_warning_not_an_error_in_brief_mode(tmp_path):
    """A task citing a well-formed change-folder join key does not fail
    brief mode; it is reported as contributing no coverage HERE.

    Both referent kinds are legal for `Brief item covered` per
    `plan-format.md`, and brief mode fires on any brief declaring `BI-` ids,
    so a plan mixing the two reaches this check as a matter of course. Before
    this tolerance existed it exited 1 at a gate with no bypass — the
    `Notes`-approval escape covers coverage drops, not citation errors — which
    made a legal plan unshippable.

    The fail-closed instinct does not apply: fail-closed protects against
    AMBIGUITY, and a value matching the join-key grammar is not ambiguous.
    It is the mirror of the tolerance the change-folder path already extends
    to prose referents, and it is a warning rather than silence for the same
    reason that one is — a value that contributes nothing must say so, or a
    mistyped key reads as an item no task delivers.

    Two properties are pinned, and the register is the load-bearing one: an
    implementation that keeps the sentence but leaves the exit code at 1
    still blocks the gate, and one that drops the line entirely restores the
    silence.
    """
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_TWO_IDS, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(_PLAN_MIXING_JOIN_KEY_AND_IDS, encoding="utf-8")

    result = _run_brief(brief, plan)
    assert result.returncode == 0, (
        "a well-formed join key is a legal referent kind, so brief mode must "
        f"not fail on it\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    reported = _stderr_lines_naming("Task 2 — join-key referent", result.stderr)
    assert reported, (
        "the join-key task must still be named — silence is what makes a "
        "mistyped key read as an uncovered item"
    )
    assert all(line.lstrip().startswith("Warning:") for line in reported), (
        "the join-key task must be reported in the warning register, not the "
        f"error one; got:\n" + "\n".join(reported)
    )


def test_bare_req_id_is_a_warning_not_an_error_in_brief_mode(tmp_path):
    """A task citing a bare `REQ-<n>` token does not fail brief mode — same
    treatment as a well-formed change-folder join key
    (`test_wellformed_join_key_is_a_warning_not_an_error_in_brief_mode`):
    it is a legal `Brief item covered` value that simply answers a
    different question here, so it is warned about, not errored."""
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_TWO_IDS, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — identifier referent\n"
        "- Brief item covered: BI-1\n\n"
        "## Task 2 — bare req-id referent\n"
        "- Brief item covered: REQ-3\n",
        encoding="utf-8",
    )

    result = _run_brief(brief, plan)
    assert result.returncode == 0, (
        "a bare REQ-<n> is a legal referent kind, so brief mode must not "
        f"fail on it\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    reported = _stderr_lines_naming("Task 2 — bare req-id referent", result.stderr)
    assert reported, "the bare-REQ-id task must still be named"
    assert all(line.lstrip().startswith("Warning:") for line in reported), (
        "the bare-REQ-id task must be reported in the warning register, not "
        f"the error one; got:\n" + "\n".join(reported)
    )


def test_near_miss_identifiers_still_error_in_brief_mode(tmp_path):
    """The join-key tolerance is not a hole: every value that is neither a
    resolvable identifier nor a well-formed join key still fails the run.

    Five shapes, each a different way of missing. `BI-2x` and `BI2` are the
    typos `handoff-brief-format.md` §Brief item identifiers rules out by the
    trailing `\\b` and the mandatory hyphen; `bi-1` is the case error the
    same section names; the bare prose quote is the pre-convention form. None
    of those four contains the `/ Requirement: … / Scenario: …` grammar, so
    none may reach the tolerance — and each is asserted by task, not by a
    single exit code, because one surviving shape among five would otherwise
    hide behind the others.

    The fifth is the one that pins WHERE the tolerance sits. `_JOIN_KEY`
    reads its change-id slot as `.+?`, so an undeclared `BI-99` wearing the
    join-key shape matches the grammar perfectly — testing it ahead of the
    cites-nothing branch would route that typo into the warning register and
    silence it. The shipped order tests it inside `if not cited:`, which
    confines the tolerance to values citing no `BI-` at all; this row is what
    fails if that order is ever inverted.
    """
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_TWO_IDS, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — trailing character\n"
        "- Brief item covered: BI-2x\n\n"
        "## Task 2 — missing hyphen\n"
        "- Brief item covered: BI2\n\n"
        "## Task 3 — wrong case\n"
        "- Brief item covered: bi-1\n\n"
        "## Task 4 — bare prose\n"
        "- Brief item covered: the widget rework ships end to end\n\n"
        "## Task 5 — undeclared id wearing the join-key shape\n"
        "- Brief item covered: BI-99 / Requirement: Users can filter by date "
        "/ Scenario: Empty result set\n",
        encoding="utf-8",
    )

    result = _run_brief(brief, plan)
    assert result.returncode != 0, (
        "a mistyped identifier must still fail loudly\n" + result.stdout
    )
    for task in (
        "Task 1 — trailing character",
        "Task 2 — missing hyphen",
        "Task 3 — wrong case",
        "Task 4 — bare prose",
        "Task 5 — undeclared id wearing the join-key shape",
    ):
        reported = _stderr_lines_naming(task, result.stderr)
        assert reported, f"{task} must be reported"
        assert all(line.lstrip().startswith("Error:") for line in reported), (
            f"{task} must stay in the error register; got:\n"
            + "\n".join(reported)
        )


def test_join_key_still_counts_as_coverage_in_change_folder_mode(tmp_path):
    """The tolerance is scoped to brief mode: on the change-folder path the
    same join key still CONTRIBUTES coverage rather than being warned away.

    The two modes read the same field and now treat the same value
    differently, which is exactly the shape a fix leaks across. Running the
    identical plan through the change-folder path is what proves it did not:
    the key covers its scenario, and only the genuinely uncovered sibling is
    reported dropped.
    """
    change_folder = tmp_path / "widget-rework"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(_PLAN_MIXING_JOIN_KEY_AND_IDS, encoding="utf-8")

    result = _run(change_folder, plan)
    assert result.returncode != 0, (
        "the second scenario is covered by nobody, so the run must fail"
    )
    assert "Scenario: Single match" in result.stderr, \
        "the genuinely uncovered scenario must be named"
    assert "Scenario: Empty result set" not in result.stderr, (
        "the join key must still count as coverage on the change-folder "
        "path — a tolerance scoped to brief mode must not reach here"
    )


def test_legacy_brief_declaring_no_ids_announces_legacy_mode(tmp_path):
    """A brief predating the convention puts the run in legacy mode: the
    quote referent stays legal, no resolution is attempted — and the run
    SAYS so.

    The announcement is the point. A silent exit 0 here is indistinguishable
    from a checked exit 0, so a brief that simply forgot to declare ids
    would read as fully covered. Legacy must never be mistakable for
    checked.

    The announcement is located by its line-initial `Legacy mode:` prefix,
    and the brief is then sought in THAT LINE — not in the whole output.
    Searching the concatenated output for the bare word made the assertion
    self-satisfying: `tmp_path` names its directory after this function, so
    the substring `legacy` arrived through the brief's own path, and the
    check still passed with the implementation's word deleted. An assertion
    over output that embeds a fixture path can only be trusted against
    words the test's own name does not contain.
    """
    brief = tmp_path / "brief.md"
    brief.write_text(
        "# older brief\n\n## Smallest End State\n\nThe thing works.\n",
        encoding="utf-8",
    )
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: \"the thing works end to end\"\n",
        encoding="utf-8",
    )
    result = _run_brief(brief, plan)
    assert result.returncode == 0, result.stderr
    combined = result.stdout + result.stderr
    announcements = [line for line in combined.splitlines()
                     if line.startswith("Legacy mode:")]
    assert announcements, (
        "legacy mode must be announced by a line opening 'Legacy mode:', "
        f"never passed silently — got:\n{combined}"
    )
    assert str(brief) in announcements[0], \
        "the announcement must name the brief that declared no ids"


def test_resolvable_citations_exit_zero(tmp_path):
    """The positive control for the error above: an implementation that
    errors on every value would pass the unresolvable pin. Two tasks citing
    two declared ids must exit 0."""
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_TWO_IDS, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: BI-1 — Brief items carry an identifier\n\n"
        "## Task 2 — bar\n"
        "- Brief item covered: `BI-2`\n",
        encoding="utf-8",
    )
    result = _run_brief(brief, plan)
    assert result.returncode == 0, result.stderr


def test_none_with_reason_is_not_treated_as_unresolvable(tmp_path):
    """`none — <reason>` is the legal no-requirement value, so brief-mode
    resolution passes it through rather than calling it unresolvable.

    This pins only the direction the two tasks agree on: the form with a
    reason is never an error. Whether a BARE `none` (or an empty reason) is
    rejected is the next task's subject; that check lands on top of this
    pass-through without changing it.
    """
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_TWO_IDS, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: BI-1\n\n"
        "## Task 9 — ship\n"
        "- Brief item covered: none — release administration only\n",
        encoding="utf-8",
    )
    result = _run_brief(brief, plan)
    assert result.returncode == 0, result.stderr


# The reason-less rejection, machine-readable so the pin can compare the SET
# of offending tasks rather than hunt for a phrase that happens to co-occur.
# Line-initial and literal-prefixed by construction, so no fixture path can
# reach it: `tmp_path` names its directory after the test function, and this
# test's name carries the words `none` and `rejected`.
_NO_REASON_ERROR = re.compile(
    r"^Error: 'Brief item covered' under '(?P<task>.+?)' is the "
    r"no-requirement value with no reason\b")

# The pre-existing "this value resolves to nothing" error, parsed the same
# way — a value that only LOOKS like the no-requirement value lands here.
_CITES_NOTHING_ERROR = re.compile(
    r"^Error: 'Brief item covered' under '(?P<task>.+?)' cites no BI-")


def _tasks_reported_by(pattern: "re.Pattern[str]", stderr: str) -> set[str]:
    """The set of task headings `pattern` names, one per stderr line."""
    return {match.group("task")
            for match in (pattern.match(line) for line in stderr.splitlines())
            if match}


# Every shape of the no-requirement value in one plan, so one run decides the
# whole boundary. Task 5's reason is absent rather than a trailing space: the
# reader strips the field value, so `none — ` and `none —` are the same input.
# Task 6 is quoted for exactly that reason — the quotes are what keep a
# whitespace-only reason reachable at all past the strip.
_PLAN_EVERY_NONE_SHAPE = """\
# Plan: x

## Task 1 — cites a real item
- Brief item covered: BI-1

## Task 2 — release administration
- Brief item covered: none — release administration only

## Task 3 — spaced hyphen separator
- Brief item covered: none - a plain hyphen still separates a reason

## Task 4 — bare escape
- Brief item covered: none

## Task 5 — separator but nothing after it
- Brief item covered: none —

## Task 6 — separator and only spaces after it
- Brief item covered: "none —   "
"""


def test_bare_none_is_rejected_and_none_with_reason_is_accepted(tmp_path):
    """`none — <reason>` is legal; the reason is what makes it legal.

    A task delivering no brief outcome must not be forced into a false
    citation, so the value exists — but a bare `none` is that escape with
    the justification deleted, which is a silent opt-out wearing the legal
    value's clothes (`plan-format.md`: "a bare `none`, an empty reason, or a
    whitespace-only reason is invalid"). The reason is the whole mechanism.

    Three shapes of the boundary are settled here, each pinned in the run
    where it is decidable:

    - **The reason-less shapes fail, and the offending task is named.** The
      exit code is asserted, not the message alone: a version that prints
      the same sentence and still exits 0 leaves the plan shippable. Task
      names are compared as a parsed SET, so an implementation that rejects
      only the bare form (and lets `none —` through) fails on the narrowing,
      and one that rejects the legal Tasks 2 and 3 fails on the widening —
      containment could see neither.
    - **The separator is a separator, not a glyph.** An em-dash, an en-dash,
      and a SPACED plain hyphen all separate a reason; the reason carries
      the safety and the glyph carries none of it, so rejecting a value
      whose intent is unmistakable would punish typography.
    - **A word-initial `none` is not the escape value.** `none of the brief
      items apply` is prose and `none-of-a-kind` is a hyphen joining a word,
      not introducing a reason. Reading either as the escape would let an
      author opt a task out by accident, which is the failure this value's
      mandatory reason exists to prevent. Both stay ordinary unresolvable
      citations — they fail, by the pre-existing route, naming the task.
      The joined word stays joined when a stray space lands in FRONT of the
      hyphen (`none -of-a-kind`): one accidental keystroke away from the
      glued form, materially the same prose, so it cannot be a different
      answer — which is why a plain hyphen is a separator only with
      whitespace on BOTH sides.
    - **Only the three named glyphs separate a reason.** Em-dash, en-dash
      and a spaced plain hyphen are the separator set; a dash-alike the
      format does not name (U+2212 MINUS SIGN, U+FF0D FULLWIDTH HYPHEN-MINUS
      — the one a CJK IME emits) is NOT the escape. That is fail-closed by
      choice: an unrecognised glyph fails loudly as an unresolvable citation
      with the value quoted, so the author retypes it, whereas widening the
      set to every dash-alike widens the surface on which an opt-out can be
      granted by accident. Rejecting typography a reader would forgive is
      the cost, and it is paid in a visible error, never in silence.

    Assertions are parsed from line-initial `Error:` prefixes, never sought
    in the output blob: this test's own name contains `none` and `rejected`,
    and `tmp_path` puts the truncated name into every path the run prints.
    """
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_TWO_IDS, encoding="utf-8")

    plan = tmp_path / "plan.md"
    plan.write_text(_PLAN_EVERY_NONE_SHAPE, encoding="utf-8")
    result = _run_brief(brief, plan)
    assert result.returncode != 0, (
        "a no-requirement value with no reason must fail the run, got 0\n"
        f"{result.stdout}"
    )
    assert _tasks_reported_by(_NO_REASON_ERROR, result.stderr) == {
        "Task 4 — bare escape",
        "Task 5 — separator but nothing after it",
        "Task 6 — separator and only spaces after it",
    }, (
        "exactly the three reason-less tasks must be reported as such — the "
        "two carrying a reason are legal and must not appear\n"
        f"{result.stderr}"
    )

    # The positive control: an implementation rejecting every `none` passes
    # the run above. Both separator glyphs must survive to exit 0.
    legal = tmp_path / "legal.md"
    legal.write_text(
        "# Plan: x\n\n"
        "## Task 1 — cites a real item\n"
        "- Brief item covered: BI-1\n\n"
        "## Task 2 — release administration\n"
        "- Brief item covered: none — release administration only\n\n"
        "## Task 3 — spaced hyphen separator\n"
        "- Brief item covered: none - a plain hyphen still separates a reason\n\n"
        "## Task 4 — en-dash, tight\n"
        "- Brief item covered: none–an en-dash is never a word-joiner\n\n"
        "## Task 5 — en-dash, spaced\n"
        "- Brief item covered: none – release administration only\n",
        encoding="utf-8",
    )
    accepted = _run_brief(brief, legal)
    assert accepted.returncode == 0, accepted.stderr

    # The look-alikes: `none` opening a word or a sentence is not the value,
    # and neither is a dash-alike glyph the format does not name.
    lookalike = tmp_path / "lookalike.md"
    lookalike.write_text(
        "# Plan: x\n\n"
        "## Task 1 — prose opening with the word\n"
        "- Brief item covered: none of the brief items apply to this task\n\n"
        "## Task 2 — hyphen joining a word\n"
        "- Brief item covered: none-of-a-kind rendering work\n\n"
        "## Task 3 — a stray space in front of the joining hyphen\n"
        "- Brief item covered: none -of-a-kind rendering work\n\n"
        "## Task 4 — the same stray space, value ending at the joined word\n"
        "- Brief item covered: none -of-a-kind\n\n"
        "## Task 5 — U+2212 minus sign, a glyph the format does not name\n"
        "- Brief item covered: none − release administration only\n\n"
        "## Task 6 — U+FF0D fullwidth hyphen-minus, as a CJK IME emits it\n"
        "- Brief item covered: none － release administration only\n",
        encoding="utf-8",
    )
    looks = _run_brief(brief, lookalike)
    assert looks.returncode != 0, (
        "a value that is not the no-requirement value and cites nothing must "
        f"fail the run, got 0\n{looks.stdout}"
    )
    assert _tasks_reported_by(_NO_REASON_ERROR, looks.stderr) == set(), (
        "no look-alike is the no-requirement value, so none may be "
        f"reported as one whose reason is missing\n{looks.stderr}"
    )
    assert _tasks_reported_by(_CITES_NOTHING_ERROR, looks.stderr) == {
        "Task 1 — prose opening with the word",
        "Task 2 — hyphen joining a word",
        "Task 3 — a stray space in front of the joining hyphen",
        "Task 4 — the same stray space, value ending at the joined word",
        "Task 5 — U+2212 minus sign, a glyph the format does not name",
        "Task 6 — U+FF0D fullwidth hyphen-minus, as a CJK IME emits it",
    }, (
        "every look-alike must fail as an ordinary unresolvable citation, "
        f"each naming its own task\n{looks.stderr}"
    )


# --- per-item coverage: the union of every task citing an identifier ---


# Two tasks, one shared identifier: the shape the experiment found in the
# wild (`--lang` on **both** scripts, delivered half by one task and half by
# another). BI-1 and BI-3 are declared by the same brief and cited by
# nobody, which is the other direction of the same question.
_PLAN_TWO_TASKS_BOTH_CITING_BI2 = """\
# Plan: x

## Task 1 — first half
- Brief item covered: BI-2 — the checker resolves a cited identifier

## Task 2 — second half
- Brief item covered: `BI-2`
"""

# The per-item tally, machine-readable so a test can assert the NUMBER of
# covered items rather than a phrase that happens to appear when it is right.
_TALLY = re.compile(r"^Brief item coverage: (\d+) of (\d+)\b")

# One uncovered-item report line: which identifier, and the brief line that
# declared it.
_UNCOVERED = re.compile(
    r"^Warning: uncovered brief item (BI-\d+) — declared at line (\d+)\b")


def _coverage_tally(output: str) -> tuple[int, int]:
    """(covered, declared) read off the run's tally line."""
    hits = [match for match in (_TALLY.match(line)
                                for line in output.splitlines()) if match]
    assert len(hits) == 1, (
        "the run must print exactly one 'Brief item coverage: <n> of <n>' "
        f"tally line — got {len(hits)} in:\n{output}"
    )
    return int(hits[0].group(1)), int(hits[0].group(2))


def _uncovered_reports(stderr: str) -> set[tuple[str, int]]:
    """Every (identifier, declaring line number) pair the run reports as
    covered by no task."""
    return {(match.group(1), int(match.group(2)))
            for match in (_UNCOVERED.match(line)
                          for line in stderr.splitlines()) if match}


def test_item_cited_by_two_tasks_is_covered_once(tmp_path):
    """An identifier cited by two tasks is ONE covered item, not two.

    Coverage is per declared identifier, computed as the union of the tasks
    citing it — so the tally counts items, never citations. The distinction
    is invisible until an item is shared: the experiment found `--lang on
    both scripts` delivered half by one task and half by another, and a
    checker that counts citations reports 2-of-3 covered for a brief where
    only 1 of 3 items is cited at all. That inflated number is worse than no
    number, because it reads as progress against items nobody touched.

    The tally is parsed and compared as a pair of integers rather than
    matched as a phrase: the test's own name says "covered once", so a
    substring assertion that merely finds the word `covered` would be
    satisfied by the double-counting implementation this pin exists to
    reject — and by the `tmp_path` directory name, which pytest builds from
    this function's own name.
    """
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_WITH_THREE_IDS, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(_PLAN_TWO_TASKS_BOTH_CITING_BI2, encoding="utf-8")

    result = _run_brief(brief, plan)

    assert result.returncode == 0, (
        "both citations resolve, so the run must not fail\n"
        f"{result.stdout}\n{result.stderr}"
    )
    assert _coverage_tally(result.stdout + result.stderr) == (1, 3), (
        "the brief declares 3 identifiers and exactly 1 of them is cited; "
        "counting citations instead of items would report 2 covered"
    )


# Two tasks citing two DIFFERENT identifiers, with a third declared and
# cited by neither. The complement of the shared-item fixture above: that
# one proves two citations of one id count once, this one proves one
# citation each of two ids both count.
_PLAN_TWO_TASKS_CITING_DIFFERENT_IDS = """\
# Plan: x

## Task 1 — first item
- Brief item covered: BI-1 — Brief items carry an identifier

## Task 2 — second item
- Brief item covered: BI-2 — the checker resolves a cited identifier
"""


def test_coverage_accumulates_across_tasks(tmp_path):
    """An identifier stays covered once some task cites it, even when later
    tasks cite other identifiers.

    This is the property a mutation test found unpinned. Coverage is built
    by scanning every `Brief item covered` value in document order and
    accumulating; an implementation that ASSIGNS per value instead of
    accumulating — last citation wins — passes every other pin in this file,
    including the shared-item one above, because those fixtures happen to
    cite the same id in their final value. It reports the last task's items
    as the whole plan's coverage, so a 10-task plan reads as covering one
    or two items no matter how complete it is.

    The tally is asserted as a pair AND the uncovered set as a set: under
    last-write-wins the tally alone drops to 1-of-3, but a plan whose final
    task cited every id would keep the tally right while the uncovered
    report went wrong, and only the set sees that.
    """
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_WITH_THREE_IDS, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(_PLAN_TWO_TASKS_CITING_DIFFERENT_IDS, encoding="utf-8")

    result = _run_brief(brief, plan)

    assert result.returncode == 0, (
        "both citations resolve, so the run must not fail\n"
        f"{result.stdout}\n{result.stderr}"
    )
    assert _coverage_tally(result.stdout + result.stderr) == (2, 3), (
        "two tasks citing two distinct identifiers cover two items; an "
        "implementation that keeps only the last value's citations reports 1"
    )
    assert _uncovered_reports(result.stderr) == {
        ("BI-3", _lineno_of(
            _BRIEF_WITH_THREE_IDS,
            "- BI-3 — The umbrella outcome this decision commits to.")),
    }, (
        "only the genuinely uncited identifier may be reported uncovered\n"
        f"{result.stderr}"
    )


def test_declared_id_cited_by_no_task_is_reported_with_its_declaring_line(
    tmp_path,
):
    """Every declared identifier no task cites is named, each with the brief
    line that declared it.

    This is the reverse direction of the citation check: that one asks
    whether each task's value resolves, this one asks whether each item
    found a task. Both are needed — a plan citing one item three times
    resolves perfectly and still leaves two items unbuilt.

    The reported pairs are compared as a SET, not searched for: a report
    narrowed to the first uncovered item still contains `BI-1`, so a
    containment assertion cannot see the narrowing. The declaring line
    number is half of each pair because that is the coordinate the collector
    exists to supply — without it the author is told an id is missing and
    left to find where it was declared. The identifiers and line numbers are
    read out of the fixture, so a fixture edit cannot silently desync them
    from the expectation.
    """
    brief = tmp_path / "brief.md"
    brief.write_text(_BRIEF_WITH_THREE_IDS, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(_PLAN_TWO_TASKS_BOTH_CITING_BI2, encoding="utf-8")

    result = _run_brief(brief, plan)

    expected = {
        ("BI-1", _lineno_of(
            _BRIEF_WITH_THREE_IDS,
            "- BI-1 — Brief items carry an identifier that survives rewording.")),
        ("BI-3", _lineno_of(
            _BRIEF_WITH_THREE_IDS,
            "- BI-3 — The umbrella outcome this decision commits to.")),
    }
    assert _uncovered_reports(result.stderr) == expected, (
        "every uncovered identifier must be reported with its declaring "
        f"line, and the cited BI-2 must not be — got:\n{result.stderr}"
    )


def test_multiple_requirements_and_scenarios_all_paired_correctly(tmp_path):
    change_folder = tmp_path / "2026-07-10-my-change"
    spec = """\
## ADDED Requirements

### Requirement: First requirement
The system MUST do A.

#### Scenario: First scenario of first requirement
- GIVEN a
- WHEN b
- THEN c

### Requirement: Second requirement
The system MUST do B.

#### Scenario: Only scenario of second requirement
- GIVEN a
- WHEN b
- THEN c
"""
    _write_spec(change_folder, spec)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: First requirement / Scenario: First scenario of first requirement\n\n"
        "## Task 2\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Second requirement / Scenario: Only scenario of second requirement\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr


# --- argv binding at the CLI boundary ---


def _run_argv(*argv: str) -> subprocess.CompletedProcess:
    """The script under an arbitrary argv. These shapes never reach a file:
    argparse rejects them while binding, so the arguments are deliberately
    literal strings — no `tmp_path` reaches the output, and no assertion
    below can be satisfied by a fixture directory's name."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *argv],
        capture_output=True,
        text=True,
        env=_ENV,
    )


def test_positional_binding_at_the_four_argv_boundaries():
    """Which slot absorbs which positional, pinned at all four boundary
    shapes — every one of them a refusal, none of them silent.

    Brief mode made `change_folder` optional, and an optional positional
    ahead of a required one moves the binding: a lone positional now fills
    `plan_path`, where it previously filled `change_folder`. Nothing pinned
    that, so the move was invisible. What the four shapes are worth
    asserting is not the binding as an end in itself but that each one
    exits 2 with a diagnostic naming the argument the caller actually
    still owes:

    - **No arguments.** Only `plan_path` is unconditionally required, so
      argparse names it alone and leaves `[change_folder]` bracketed in the
      usage line. That reading is correct for a two-mode CLI and is pinned
      as-is rather than reworded: an error naming both would be wrong in
      brief mode, where the change-folder is forbidden.
    - **One bare positional.** The value binds to `plan_path`, and the
      diagnostic therefore asks for the change-folder. This is the shape
      that changed, and the assertion below is what would have caught the
      move. Also pinned as-is: the message is accurate either way the value
      was meant, and both documented invocation forms pass two arguments.
    - **`--brief` with a change-folder.** The two modes read different
      inputs, so combining them is refused explicitly instead of one check
      silently winning.
    - **`--brief` with no plan.** The plan is required in both modes;
      brief mode drops the change-folder, not the plan.
    """
    bare = _run_argv()
    assert bare.returncode == 2, f"no arguments must be refused: {bare!r}"
    assert "plan_path" in bare.stderr, \
        "the refusal must name the argument that is always required"

    lone = _run_argv("only_one_arg")
    assert lone.returncode == 2, f"one positional must be refused: {lone!r}"
    assert "<change-folder> is required" in lone.stderr, (
        "a lone positional binds to plan_path, so the diagnostic must ask "
        "for the change-folder — if it asks for plan_path instead, the "
        "optional-positional binding has moved back"
    )

    both_positionals = _run_argv(
        "--brief", "brief.md", "change-folder", "plan.md")
    assert both_positionals.returncode == 2, \
        f"--brief plus a change-folder must be refused: {both_positionals!r}"
    assert "takes no <change-folder>" in both_positionals.stderr, \
        "the refusal must say which of the two modes was contradicted"

    no_plan = _run_argv("--brief", "brief.md")
    assert no_plan.returncode == 2, \
        f"--brief with no plan must be refused: {no_plan!r}"
    assert "plan_path" in no_plan.stderr, \
        "brief mode drops the change-folder, not the plan"
