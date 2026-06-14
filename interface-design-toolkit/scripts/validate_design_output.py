"""Validate an interface-design-toolkit DESIGN CHANGE-FOLDER.

The `design-system` + `interaction-flows` skills emit a change-folder (a
directory) holding the design-system doc plus the interaction-flows doc:

    <change-folder>/
      DESIGN.md       # design-system doc for the GUI modality (Google 8-section)
      ui-flows.md     # interaction-flows doc (inventory + nav + render variants)

This module checks the change-folder STRUCTURE (presence + well-formedness),
mirroring `spec-toolkit/scripts/validate_spec_output.py`'s structure-only
posture: extra/unknown files are tolerated, never rejected.

Task 8 implements the first check — both required files present. Later tasks
append to the registry:
  - Task 9: DESIGN.md carries the 8 canonical sections.
  - Task 10: ui-flows.md carries its required sections.

Design: each check is a function (root: Path) -> list[str] of problem
messages (empty == ok). `_CHECKS` is the registry; `validate()` runs them
all. Append new check functions to `_CHECKS` to extend coverage.

CLI: `python validate_design_output.py <change-folder>` -> exit 0 if valid,
exit 1 with agent-actionable messages on stderr if invalid.

Stdlib only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# The design-system doc filename for the GUI modality. MVP implements GUI
# fully; TUI/CLI conventions docs are phase-2 (the brief's modality posture),
# so the presence check pins the GUI name here. When TUI/CLI land, this check
# becomes modality-aware.
_DESIGN_DOC = "DESIGN.md"
_UI_FLOWS_DOC = "ui-flows.md"


# --- checks: each returns list[str] of problems (empty == ok) ---------------

def _check_design_doc_present(root: Path) -> list[str]:
    if not (root / _DESIGN_DOC).is_file():
        return [f"missing design-system doc '{_DESIGN_DOC}' at "
                f"{root / _DESIGN_DOC} (the GUI change-folder needs the "
                f"Google 8-section DESIGN.md emitted by `design-system`)"]
    return []


def _check_ui_flows_present(root: Path) -> list[str]:
    if not (root / _UI_FLOWS_DOC).is_file():
        return [f"missing interaction-flows doc '{_UI_FLOWS_DOC}' at "
                f"{root / _UI_FLOWS_DOC} (the change-folder needs the "
                f"`ui-flows.md` emitted by `interaction-flows`)"]
    return []


# --- check registry (Tasks 9/10 append section-content checks here) ---------

_CHECKS = [
    _check_design_doc_present,
    _check_ui_flows_present,
]


def validate(root: Path) -> tuple[bool, list[str]]:
    """Run all checks against the design change-folder `root`.

    Returns (ok, problems). ok is True iff problems is empty.
    """
    root = Path(root)
    if not root.is_dir():
        return False, [f"design change-folder does not exist: {root}"]
    problems: list[str] = []
    for check in _CHECKS:
        problems.extend(check(root))
    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an interface-design-toolkit design change-folder "
                    "(design-system doc + ui-flows.md present and well-formed).")
    parser.add_argument("change_folder",
                        help="path to the design change-folder directory")
    args = parser.parse_args(argv)

    ok, problems = validate(Path(args.change_folder))
    if ok:
        print(f"OK: {args.change_folder} conforms to the design change-folder "
              f"contract.")
        return 0
    print(f"INVALID: {args.change_folder} does not conform to the design "
          f"change-folder contract.", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
