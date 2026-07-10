#!/usr/bin/env python3
"""Compare a loom-spec change-folder's `#### Scenario:` set against a
writing-plans plan's join keys, and name every dropped scenario.

Inputs (positional CLI args):

    check_scenario_coverage.py <change-folder> <plan-path>

- `<change-folder>` is a `docs/loom/<change-id>/` directory in the shape
  `loom-spec/scripts/validate_spec_output.py` validates: `specs/<capability>/
  spec.md` delta files, each containing `### Requirement:` blocks that each
  contain one or more `#### Scenario:` headers. The heading regexes here
  reuse that exact grammar (`^###\\s+Requirement:` / `^####\\s+Scenario:`),
  only adding capture groups for the name text — not a new variant.
- `<plan-path>` is a writing-plans plan (`docs/loom/plans/...`). Per
  `loom-code/skills/writing-plans/references/plan-format.md`, a task's
  `Brief item covered` field MAY be the stable join key
  `<change-id> / Requirement: <name> / Scenario: <name>` (referent kind (b)).

The script builds the full scenario-key set from the change-folder, the
covered-key set from the plan's join keys, and reports the difference:

    exit 0 — every change-folder scenario is covered (or the folder is
             vacuous — zero scenarios — in which case a note says so).
    exit 1 — one or more scenarios are dropped; each dropped key is printed
             on stderr, one per line, agent-actionable.

A malformed plan (no join keys found at all — e.g. all `Brief item covered`
values are prose referents, or the field is absent, or the plan file itself
is missing) is treated as zero coverage: every change-folder scenario is
reported dropped.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Same underlying heading grammar as validate_spec_output.py's
# `_REQUIREMENT_HDR` (`^###\s+Requirement:`) and the pattern
# `_first_scenario_block` matches (`^####\s+Scenario:.*$`) — these add a
# capture group for the name text, they do not change the grammar.
_REQUIREMENT_HDR = re.compile(r"^###\s+Requirement:\s*(.*)$", re.MULTILINE)
_SCENARIO_HDR = re.compile(r"^####\s+Scenario:\s*(.*)$", re.MULTILINE)

# A requirement's scope ends at the next header of level 2-3 (a sibling
# `### Requirement:`, or a higher-level `##` section heading) — `####`
# stays excluded here because that is the `#### Scenario:` level itself,
# which must stay INSIDE the requirement's scope (unlike
# validate_spec_output.py's `_ANY_HEADER = re.compile(r"^#{2,4}\s")`, used
# there to slice a single scenario's own body up to its next header).
# What we DO take from that SSOT regex: single-# is excluded, so a
# `# comment` inside an example code fence in a scenario body isn't
# mistaken for a boundary. Sharing that grammar also means sharing its
# known limitation: a `##`/`###`-prefixed line inside a fenced code block
# (e.g. a markdown example) is still mistaken for a real header, same as
# upstream.
_SECTION_BOUNDARY = re.compile(r"^#{2,3}\s", re.MULTILINE)

# writing-plans' `Brief item covered` field line (bold or not, per
# plan-format.md's canonical schema uses `**Brief item covered**:` but
# real plans in this repo write the plain `- Brief item covered:` form).
_BRIEF_ITEM_LINE = re.compile(
    r"^\s*-\s*(?:\*\*)?Brief item covered(?:\*\*)?\s*:\s*(.+)$", re.MULTILINE)

# The stable join key grammar itself: `<change-id> / Requirement: <name> /
# Scenario: <name>`, tolerant of optional surrounding quote/backtick chars.
_JOIN_KEY = re.compile(
    r"^[\"'`]?\s*(?P<change_id>.+?)\s*/\s*Requirement:\s*(?P<req>.+?)\s*/\s*"
    r"Scenario:\s*(?P<scen>.+?)\s*[\"'`]?$")


def _requirement_scenario_pairs(text: str) -> list[tuple[str, str]]:
    """(requirement name, scenario name) pairs found in one delta file's
    text, per validate_spec_output.py's heading grammar."""
    pairs: list[tuple[str, str]] = []
    for req_match in _REQUIREMENT_HDR.finditer(text):
        req_name = req_match.group(1).strip()
        start = req_match.end()
        boundary = _SECTION_BOUNDARY.search(text, start)
        end = boundary.start() if boundary else len(text)
        body = text[start:end]
        for scen_match in _SCENARIO_HDR.finditer(body):
            pairs.append((req_name, scen_match.group(1).strip()))
    return pairs


def _delta_files(change_folder: Path) -> list[Path]:
    specs = change_folder / "specs"
    if not specs.is_dir():
        return []
    return sorted(specs.rglob("*.md"))


def collect_folder_scenario_keys(change_folder: Path, change_id: str) -> set[str]:
    """Every `<change-id> / Requirement: <name> / Scenario: <name>` join key
    the change-folder's specs/ delta files define.

    Duplicate (requirement, scenario) name pairs collapse into one set
    entry — the join-key grammar is fixed (per the plan), so occurrence
    indices can't be added to disambiguate. Instead, a duplicate is
    flagged with a warning on stderr naming the key, so an uncovered
    duplicate instance is at least visible rather than silently
    undetectable.
    """
    keys: set[str] = set()
    occurrences: dict[str, int] = {}
    for delta in _delta_files(change_folder):
        text = delta.read_text(encoding="utf-8")
        for req_name, scen_name in _requirement_scenario_pairs(text):
            key = f"{change_id} / Requirement: {req_name} / Scenario: {scen_name}"
            occurrences[key] = occurrences.get(key, 0) + 1
            keys.add(key)
    for key, count in occurrences.items():
        if count > 1:
            print(f"Warning: duplicate scenario key seen {count} times "
                  f"(coverage can't distinguish instances) — {key}", file=sys.stderr)
    return keys


def collect_plan_join_keys(plan_text: str) -> set[str]:
    """Every join key referenced by a `Brief item covered` field in the
    plan. A `Brief item covered` line whose value is prose (referent kind
    (a), not the join-key grammar) contributes nothing — that is the
    malformed-plan / zero-coverage case."""
    keys: set[str] = set()
    for line_match in _BRIEF_ITEM_LINE.finditer(plan_text):
        value = line_match.group(1).strip()
        m = _JOIN_KEY.match(value)
        if m is None:
            continue
        keys.add(f"{m.group('change_id')} / Requirement: {m.group('req')} / "
                  f"Scenario: {m.group('scen')}")
    return keys


def check_coverage(
    change_folder: Path, plan_path: Path
) -> tuple[bool, list[str], str]:
    """Returns (ok, dropped_keys_sorted, note).

    `note` is a human-facing status line for the vacuous-empty-folder case
    or the missing-plan-file case; empty string when neither applies.
    """
    change_id = change_folder.name or change_folder.resolve().name
    folder_keys = collect_folder_scenario_keys(change_folder, change_id)
    if not folder_keys:
        return True, [], (
            f"No '#### Scenario:' headers found under {change_folder} — "
            f"vacuously covered (nothing to drop)."
        )

    note = ""
    if not plan_path.is_file():
        note = f"Note: plan file not found at {plan_path} — treating as zero coverage."
        plan_text = ""
    else:
        plan_text = plan_path.read_text(encoding="utf-8")

    plan_keys = collect_plan_join_keys(plan_text)
    dropped = sorted(folder_keys - plan_keys)
    return (not dropped), dropped, note


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare a loom-spec change-folder's '#### Scenario:' "
                    "set against a writing-plans plan's join keys; exit 1 "
                    "naming every dropped scenario."
    )
    parser.add_argument("change_folder", help="path to the loom-spec change-folder")
    parser.add_argument("plan_path", help="path to the writing-plans plan file")
    args = parser.parse_args(argv)

    change_folder = Path(args.change_folder)
    plan_path = Path(args.plan_path)

    ok, dropped, note = check_coverage(change_folder, plan_path)
    if note:
        print(note)

    if ok:
        if not note:
            print(f"Full coverage: every scenario under {change_folder} is "
                  f"mapped by a task in {plan_path}.")
        return 0

    print(f"Dropped scenario(s) — not covered by any task's 'Brief item "
          f"covered' field in {plan_path}:", file=sys.stderr)
    for key in dropped:
        print(f"  - {key}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
