"""Tests for check_scenario_coverage.py — the coverage script that compares
a loom-spec change-folder's `#### Scenario:` set (per
`loom-spec/scripts/validate_spec_output.py`'s heading grammar: `### Requirement:`
/ `#### Scenario:`) against a writing-plans plan's join keys (`<change-id> /
Requirement: <name> / Scenario: <name>`, from each task's `Brief item covered`
field — see `loom-code/skills/writing-plans/references/plan-format.md`).

Exercised as a CLI subprocess (the actual interface: two positional args,
exit 0 / exit 1) rather than importing internals, since the contract this
script must honor is the process boundary.

The brief-item collector is the one exception, tested by direct import.
It has no process boundary yet — nothing on the CLI path calls it until
the brief-mode check is wired to the gate — so a subprocess test could
only assert the collector's absence from output it does not yet reach.

Stdlib only (subprocess + pathlib), plus a direct import of the module
under test for the collector tests.
"""

import os
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
    key (without changing the join-key format) and still proceed."""
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
    assert "duplicate" in result.stderr.lower()
    assert "Empty result set" in result.stderr


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


def test_legacy_brief_declaring_no_ids_announces_legacy_mode(tmp_path):
    """A brief predating the convention puts the run in legacy mode: the
    quote referent stays legal, no resolution is attempted — and the run
    SAYS so.

    The announcement is the point. A silent exit 0 here is indistinguishable
    from a checked exit 0, so a brief that simply forgot to declare ids
    would read as fully covered. Legacy must never be mistakable for
    checked.
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
    assert "legacy" in combined.lower(), \
        "legacy mode must be announced, never passed silently"
    assert str(brief) in combined, \
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
