"""Validate a spec-toolkit OUTPUT DIRECTORY against the OpenSpec change-folder
skeleton.

Spec-toolkit emits a directory in OpenSpec change-folder *shape* (plain
markdown, no OpenSpec CLI dependency):

    <output-dir>/
      proposal.md
      specs/<capability>/spec.md   # delta with ## ADDED Requirements ...

This module checks the SKELETON only (structure, not content quality),
mirroring `openspec validate`'s structure-only behavior: extra/unknown
sections are tolerated, never rejected.

Design: each check is a function (root: Path) -> list[str] of problem
messages (empty == ok). `_SKELETON_CHECKS` is the ordered registry. Task 3
adds an `_ADDITIVE_CHECKS` group of the same shape and appends it to the
checks `validate()` runs — no edits to existing check functions required.

CLI: `python validate_spec_output.py <output-dir>` -> exit 0 if valid,
exit 1 with agent-actionable messages on stderr if invalid.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# RFC-2119 keyword on a requirement body line (word-boundary, case-sensitive
# per OpenSpec convention that the normative keyword is uppercase).
_RFC2119 = re.compile(r"\b(MUST|SHALL|SHOULD|MAY)\b")

_ADDED_REQ_HDR = re.compile(r"^##\s+ADDED\s+Requirements\s*$", re.MULTILINE)
_REQUIREMENT_HDR = re.compile(r"^###\s+Requirement:", re.MULTILINE)
_SCENARIO_HDR = re.compile(r"^####\s+Scenario:")


def _delta_files(root: Path) -> list[Path]:
    specs = root / "specs"
    if not specs.is_dir():
        return []
    return sorted(specs.rglob("*.md"))


# --- skeleton checks: each returns list[str] of problems (empty == ok) ------

def _check_proposal(root: Path) -> list[str]:
    if not (root / "proposal.md").is_file():
        return [f"missing proposal.md at {root / 'proposal.md'} "
                f"(every change folder needs a proposal.md)"]
    return []


def _check_specs_dir(root: Path) -> list[str]:
    specs = root / "specs"
    if not specs.is_dir():
        return [f"missing specs/ subdirectory at {specs} "
                f"(put delta spec files under specs/<capability>/spec.md)"]
    if not _delta_files(root):
        return [f"specs/ at {specs} contains no *.md delta files "
                f"(add at least one delta, e.g. specs/<capability>/spec.md)"]
    return []


def _check_added_requirements(root: Path) -> list[str]:
    deltas = _delta_files(root)
    if not deltas:
        return []  # already reported by _check_specs_dir
    if any(_ADDED_REQ_HDR.search(d.read_text(encoding="utf-8")) for d in deltas):
        return []
    return [f"no delta under {root / 'specs'} contains a "
            f"'## ADDED Requirements' header "
            f"(this header opens the block OpenSpec parses)"]


def _check_requirement_with_rfc2119(root: Path) -> list[str]:
    deltas = _delta_files(root)
    if not deltas:
        return []
    for d in deltas:
        text = d.read_text(encoding="utf-8")
        for m in _REQUIREMENT_HDR.finditer(text):
            # Inspect the requirement's body: lines after the header up to the
            # next header (### or ####) or the next blank-line block.
            body = _slice_until_next_header(text, m.end())
            if _RFC2119.search(body):
                return []
    return [f"no '### Requirement:' under {root / 'specs'} carries an "
            f"RFC-2119 keyword (MUST / SHALL / SHOULD / MAY) on its body line "
            f"(state the normative obligation, e.g. 'The system MUST ...')"]


def _check_scenario_given_when_then(root: Path) -> list[str]:
    deltas = _delta_files(root)
    if not deltas:
        return []
    saw_scenario = False
    for d in deltas:
        for line_no, line in enumerate(d.read_text(encoding="utf-8").splitlines()):
            if _SCENARIO_HDR.match(line):
                saw_scenario = True
        block = _first_scenario_block(d.read_text(encoding="utf-8"))
        if block is not None:
            upper = block.upper()
            missing = [kw for kw in ("GIVEN", "WHEN", "THEN") if kw not in upper]
            if not missing:
                return []
            return [f"'#### Scenario:' in {d} is missing "
                    f"{', '.join(missing)} line(s) "
                    f"(each scenario needs GIVEN / WHEN / THEN)"]
    if not saw_scenario:
        return [f"no '#### Scenario:' header found under {root / 'specs'} "
                f"(each requirement needs >=1 scenario with GIVEN/WHEN/THEN)"]
    return []


# --- text helpers -----------------------------------------------------------

_ANY_HEADER = re.compile(r"^#{2,4}\s", re.MULTILINE)


def _slice_until_next_header(text: str, start: int) -> str:
    """Body from `start` up to the next ##/###/#### header (or end)."""
    nxt = _ANY_HEADER.search(text, start)
    return text[start:nxt.start()] if nxt else text[start:]


def _first_scenario_block(text: str) -> str | None:
    """Return the body of the first `#### Scenario:` header up to the next
    header, or None if there is no scenario."""
    for m in re.finditer(r"^####\s+Scenario:.*$", text, re.MULTILINE):
        return _slice_until_next_header(text, m.end())
    return None


# --- check registry (Task 3 appends an additive group here) -----------------

_SKELETON_CHECKS = [
    _check_proposal,
    _check_specs_dir,
    _check_added_requirements,
    _check_requirement_with_rfc2119,
    _check_scenario_given_when_then,
]


def validate(root: Path) -> tuple[bool, list[str]]:
    """Run all checks against the output directory `root`.

    Returns (ok, problems). ok is True iff problems is empty.
    """
    root = Path(root)
    problems: list[str] = []
    if not root.is_dir():
        return False, [f"output directory does not exist: {root}"]
    for check in _SKELETON_CHECKS:
        problems.extend(check(root))
    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a spec-toolkit output directory against the "
                    "OpenSpec change-folder skeleton.")
    parser.add_argument("output_dir", help="path to the spec-toolkit output directory")
    args = parser.parse_args(argv)

    ok, problems = validate(Path(args.output_dir))
    if ok:
        print(f"OK: {args.output_dir} conforms to the OpenSpec skeleton.")
        return 0
    print(f"INVALID: {args.output_dir} does not conform to the OpenSpec skeleton.",
          file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
