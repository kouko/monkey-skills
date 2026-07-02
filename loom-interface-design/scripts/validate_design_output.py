"""Validate an loom-interface-design DESIGN CHANGE-FOLDER.

The `design-system` + `interaction-flows` skills emit a change-folder (a
directory) holding the interaction-flows doc, governed by the product-level
design-system doc. Two layouts are accepted:

    per-change (canonical):            legacy (side-by-side):
    docs/loom/
      DESIGN.md    # product-level         <change-folder>/
      <change-id>/                           DESIGN.md
        ui-flows.md                          ui-flows.md

`ui-flows.md` MUST sit in the change-folder handed to this validator;
`DESIGN.md` (Google 8-section, GUI modality) is resolved most-specific-first —
the change-folder itself, then its parent (the product level). A fixed
product-level ui-flows.md is NOT a layout: per-feature flows at a fixed path
would overwrite each other, which is why the change-id folder exists.

This module checks the change-folder STRUCTURE (presence + well-formedness),
mirroring `loom-spec/scripts/validate_spec_output.py`'s structure-only
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

# The 8 canonical `##` sections DESIGN.md MUST carry, in order, per
# design-system/references/design-md-schema.md ("The 8 canonical sections").
_DESIGN_SECTIONS = (
    "Overview / Brand",
    "Colors",
    "Typography",
    "Layout",
    "Elevation & Depth",
    "Shapes",
    "Components",
    "Do's & Don'ts",
)

# The required `##` sections ui-flows.md MUST carry, per
# interaction-flows/references/ux-flow-checklist.md. Lenient/minimal subset of
# the 7 generation dimensions — the structural backbone a generator following
# the checklist must emit: dimension 1 (inventory), 2 (user flows), 3 (UI
# structure). The remaining dimensions (transitions / entry / exit / density)
# enrich a surface but are not gated here.
_UI_FLOWS_SECTIONS = (
    "Inventory",
    "User Flows",
    "UI Structure",
)


# --- checks: each returns list[str] of problems (empty == ok) ---------------

def _resolve_design_doc(root: Path) -> Path | None:
    """Resolve the governing DESIGN.md, most-specific-first.

    The change-folder's own DESIGN.md (legacy side-by-side layout) wins over
    the parent's product-level one (per-change layout). None when neither
    exists.
    """
    local = root / _DESIGN_DOC
    if local.is_file():
        return local
    parent = root.parent / _DESIGN_DOC
    if parent.is_file():
        return parent
    return None


def _check_design_doc_present(root: Path) -> list[str]:
    if _resolve_design_doc(root) is None:
        return [f"missing design-system doc '{_DESIGN_DOC}': not at "
                f"{root / _DESIGN_DOC} (side-by-side layout) nor at "
                f"{root.parent / _DESIGN_DOC} (product level) — the "
                f"change-folder needs the Google 8-section DESIGN.md emitted "
                f"by `design-system`"]
    return []


def _check_ui_flows_present(root: Path) -> list[str]:
    if not (root / _UI_FLOWS_DOC).is_file():
        return [f"missing interaction-flows doc '{_UI_FLOWS_DOC}' at "
                f"{root / _UI_FLOWS_DOC} (the change-folder needs the "
                f"`ui-flows.md` emitted by `interaction-flows`)"]
    return []


def _heading_titles(text: str) -> list[str]:
    """Collect the `## <title>` heading titles in `text`, lower-cased, in order.

    Whole-line matching: a heading is a line whose stripped form starts with
    `## ` (exactly two hashes then a space), excluding `#`/`###` and any
    section name buried in prose. Returned lower-cased for case-insensitive
    comparison. Shared by the DESIGN.md (exact-membership) and ui-flows.md
    (substring) section checks.
    """
    titles: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            titles.append(stripped[len("## "):].strip().lower())
    return titles


def _check_design_sections(root: Path) -> list[str]:
    design = _resolve_design_doc(root)
    if design is None:
        # presence is _check_design_doc_present's job; don't double-report.
        return []
    present = set(_heading_titles(design.read_text(encoding="utf-8")))
    missing = [s for s in _DESIGN_SECTIONS if s.lower() not in present]
    if missing:
        return [f"DESIGN.md is missing canonical `## ` section(s): "
                f"{', '.join(missing)} (the GUI DESIGN.md MUST carry all 8 "
                f"sections per design-md-schema.md: "
                f"{', '.join(_DESIGN_SECTIONS)})"]
    return []


def _check_ui_flows_sections(root: Path) -> list[str]:
    flows = root / _UI_FLOWS_DOC
    if not flows.is_file():
        # presence is _check_ui_flows_present's job; don't double-report.
        return []
    # Lenient match: each required section name must appear (as a substring,
    # case-insensitive) within SOME `## ` heading title. This tolerates the
    # verbose headings a generator following ux-flow-checklist.md would emit
    # (e.g. "Screen / panel / command inventory" satisfies "Inventory") while
    # still requiring a whole-line `## ` heading — a name buried only in prose
    # does not count.
    titles = _heading_titles(flows.read_text(encoding="utf-8"))
    missing = [
        s for s in _UI_FLOWS_SECTIONS
        if not any(s.lower() in title for title in titles)
    ]
    if missing:
        return [f"ui-flows.md is missing required `## ` section(s): "
                f"{', '.join(missing)} (the GUI ui-flows.md MUST carry an "
                f"inventory, user flows, and UI structure per "
                f"ux-flow-checklist.md; expected: "
                f"{', '.join(_UI_FLOWS_SECTIONS)})"]
    return []


# --- check registry (Task 10 appends ui-flows section checks here) ----------

_CHECKS = [
    _check_design_doc_present,
    _check_ui_flows_present,
    _check_design_sections,
    _check_ui_flows_sections,
]


def validate(root: Path) -> tuple[bool, list[str]]:
    """Run all checks against the design change-folder `root`.

    Returns (ok, problems). ok is True iff problems is empty.
    """
    # Resolve to an absolute path: with a relative root like "." invoked from
    # inside the change folder, Path(".").parent is Path(".") — the parent
    # (product-level) DESIGN.md lookup would silently check the same dir.
    root = Path(root).resolve()
    if not root.is_dir():
        return False, [f"design change-folder does not exist: {root}"]
    problems: list[str] = []
    for check in _CHECKS:
        problems.extend(check(root))
    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an loom-interface-design design change-folder "
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
