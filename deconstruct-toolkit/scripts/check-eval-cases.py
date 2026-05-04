#!/usr/bin/env python3
"""check-eval-cases.py — structural validator for deconstruct-toolkit eval suite.

Verifies eval case YAMLs are well-formed, fixture files referenced
in cases exist on disk, fixtures contain the "Annotations for evaluator"
block, lens references contain primary-source citation blocks, and
skill folders follow the deconstruct-toolkit single-level subfolder
convention.

This is NOT an LLM-eval runner. Running the actual deconstruction
through Claude Code (manually or via SDK) and comparing output to
must_find criteria happens locally / on-demand. This script catches
*structural* problems pre-merge so the LLM eval is sound when run.

Usage:
    python3 deconstruct-toolkit/scripts/check-eval-cases.py
    python3 deconstruct-toolkit/scripts/check-eval-cases.py --verbose

Exit codes:
    0  — all checks pass
    1  — at least one check failed (FATAL); CI should block merge
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# Resolve plugin root regardless of where script is invoked from.
SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent

EVAL_CASES_DIR = PLUGIN_ROOT / "eval" / "cases"
SKILLS_DIR = PLUGIN_ROOT / "skills"

ALLOWED_SUBDIRS = {"protocols", "references", "assets", "checklists"}
REQUIRED_TOP_LEVEL = {"SKILL.md"}

ANNOTATIONS_HEADER_RE = re.compile(
    r"^##\s+Annotations\s+for\s+evaluator\s*$",
    re.MULTILINE | re.IGNORECASE,
)
PRIMARY_SOURCE_RE = re.compile(
    r"^>\s*\*\*Sources?\*\*:",
    re.MULTILINE,
)


class CheckResult:
    def __init__(self) -> None:
        self.failures: list[tuple[str, str]] = []
        self.passes: list[str] = []

    def fail(self, check: str, detail: str) -> None:
        self.failures.append((check, detail))

    def passed(self, check: str) -> None:
        self.passes.append(check)

    @property
    def ok(self) -> bool:
        return not self.failures


def parse_yaml(path: Path) -> dict[str, Any]:
    """Minimal YAML parser for our case files. Avoids PyYAML dependency.

    Supports the subset we use:
    - top-level scalars: `key: value`
    - top-level lists of scalars: `key:` followed by `- item` lines
    - top-level lists of dicts: `key:` followed by `- subkey: subvalue` blocks
    - dict continuation across list items (2-space indented `subkey:` lines
      attach to the current list-item dict)
    NOT a general YAML parser.
    """
    text = path.read_text(encoding="utf-8")
    result: dict[str, Any] = {}

    current_list_key: str | None = None       # key whose value is a list
    current_list: list[Any] | None = None     # the list we're appending to
    list_item_indent: int = -1                # indent of `- ` lines for current list
    list_item_attr_indent: int = -1           # indent of subkeys inside a list-dict-item
    current_item_dict: dict[str, Any] | None = None  # dict currently receiving subkeys

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # List item line: `- ...`
        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            list_item_indent = indent
            list_item_attr_indent = indent + 2
            if current_list is None:
                continue
            if ":" in item_text:
                # list of dicts; first key on the dash line
                item_dict: dict[str, Any] = {}
                k, _, v = item_text.partition(":")
                v = v.strip()
                if v:
                    item_dict[k.strip()] = _coerce_scalar(v)
                else:
                    item_dict[k.strip()] = ""
                current_list.append(item_dict)
                current_item_dict = item_dict
            else:
                current_list.append(_coerce_scalar(item_text))
                current_item_dict = None
            continue

        # Continuation of list-item dict: indent matches subkey indent
        if (
            current_item_dict is not None
            and indent == list_item_attr_indent
            and ":" in stripped
        ):
            key, _, value = stripped.partition(":")
            current_item_dict[key.strip()] = _coerce_scalar(value.strip()) if value.strip() else ""
            continue

        # Top-level key
        if indent == 0 and ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if value:
                result[key] = _coerce_scalar(value)
                current_list = None
                current_list_key = None
                current_item_dict = None
            else:
                # Start of a list (or nested dict) under this key
                new_list: list[Any] = []
                result[key] = new_list
                current_list = new_list
                current_list_key = key
                current_item_dict = None
            continue

        # Anything else we treat as a list-item attribute even if indent doesn't match the
        # exact +2 we expect (some authors use +4 or tabs). Fallback only triggers if we
        # already have a current_item_dict and the line has a `:`.
        if current_item_dict is not None and ":" in stripped:
            key, _, value = stripped.partition(":")
            current_item_dict[key.strip()] = _coerce_scalar(value.strip()) if value.strip() else ""
            continue

    return result


def _coerce_scalar(value: str) -> Any:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def check_eval_cases(result: CheckResult, verbose: bool) -> None:
    if not EVAL_CASES_DIR.exists():
        result.fail("eval-cases-dir", f"Missing: {EVAL_CASES_DIR}")
        return

    case_files = sorted(EVAL_CASES_DIR.glob("*.yaml"))
    if not case_files:
        result.fail("eval-cases-empty", f"No .yaml files in {EVAL_CASES_DIR}")
        return

    for case_path in case_files:
        try:
            data = parse_yaml(case_path)
        except Exception as exc:
            result.fail(f"yaml-parse:{case_path.name}", str(exc))
            continue

        # Required keys
        for key in ("name", "skill", "fixture", "input_query", "must_find"):
            if key not in data:
                result.fail(
                    f"missing-key:{case_path.name}",
                    f"Required key '{key}' absent",
                )

        if "fixture" in data:
            fixture_path = PLUGIN_ROOT / data["fixture"]
            if not fixture_path.exists():
                result.fail(
                    f"fixture-missing:{case_path.name}",
                    f"Fixture not found: {fixture_path}",
                )
            else:
                fixture_text = fixture_path.read_text(encoding="utf-8")
                if not ANNOTATIONS_HEADER_RE.search(fixture_text):
                    result.fail(
                        f"fixture-annotation-missing:{case_path.name}",
                        f"Fixture {fixture_path.name} missing '## Annotations for evaluator' block",
                    )
                else:
                    if verbose:
                        result.passed(f"fixture-annotation-ok:{case_path.name}")

        if "must_find" in data:
            mf = data["must_find"]
            if not isinstance(mf, list) or not mf:
                result.fail(
                    f"must-find-empty:{case_path.name}",
                    "must_find must be a non-empty list",
                )
            else:
                for i, item in enumerate(mf):
                    if not isinstance(item, dict):
                        result.fail(
                            f"must-find-bad-item:{case_path.name}#{i}",
                            f"must_find[{i}] must be a dict with id+description",
                        )
                        continue
                    for k in ("id", "description"):
                        if k not in item:
                            result.fail(
                                f"must-find-missing-{k}:{case_path.name}#{i}",
                                f"must_find[{i}] missing '{k}'",
                            )
        if verbose:
            result.passed(f"yaml-ok:{case_path.name}")


def check_lens_references(result: CheckResult, verbose: bool) -> None:
    """Each lens reference file must open with a primary-source citation."""
    if not SKILLS_DIR.exists():
        result.fail("skills-dir-missing", str(SKILLS_DIR))
        return

    lens_files = sorted(SKILLS_DIR.glob("*/references/lens-*.md"))
    if not lens_files:
        result.fail("no-lens-files", f"No lens-*.md found under {SKILLS_DIR}/*/references/")
        return

    for lens_path in lens_files:
        text = lens_path.read_text(encoding="utf-8")
        first_500 = text[:1000]
        if not PRIMARY_SOURCE_RE.search(first_500):
            result.fail(
                f"primary-source-missing:{lens_path.relative_to(PLUGIN_ROOT)}",
                f"Lens reference {lens_path.name} missing '> **Source(s)**:' anchor in first 1000 chars",
            )
        elif verbose:
            result.passed(f"primary-source-ok:{lens_path.relative_to(PLUGIN_ROOT)}")


def check_skill_folders(result: CheckResult, verbose: bool) -> None:
    """Each skill folder must have flat single-level subfolders only."""
    if not SKILLS_DIR.exists():
        result.fail("skills-dir-missing", str(SKILLS_DIR))
        return

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_name = skill_dir.name

        # Required: SKILL.md
        if not (skill_dir / "SKILL.md").exists():
            result.fail(
                f"skill-md-missing:{skill_name}",
                f"{skill_dir}/SKILL.md not found",
            )
            continue

        # Subfolders must be single-level
        for entry in skill_dir.iterdir():
            if entry.is_dir():
                # Check no nested subfolders inside this subfolder
                for sub_entry in entry.iterdir():
                    if sub_entry.is_dir() and sub_entry.name != "__pycache__":
                        result.fail(
                            f"nested-subfolder:{skill_name}",
                            f"Nested subfolder forbidden: {sub_entry.relative_to(PLUGIN_ROOT)}",
                        )

        if verbose:
            result.passed(f"skill-layout-ok:{skill_name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--verbose", "-v", action="store_true", help="Print passes too")
    args = parser.parse_args()

    result = CheckResult()
    check_eval_cases(result, args.verbose)
    check_lens_references(result, args.verbose)
    check_skill_folders(result, args.verbose)

    if args.verbose:
        for p in result.passes:
            print(f"  PASS  {p}")

    if result.ok:
        n_cases = len(list(EVAL_CASES_DIR.glob("*.yaml"))) if EVAL_CASES_DIR.exists() else 0
        n_lenses = len(list(SKILLS_DIR.glob("*/references/lens-*.md"))) if SKILLS_DIR.exists() else 0
        n_skills = sum(1 for d in SKILLS_DIR.iterdir() if d.is_dir()) if SKILLS_DIR.exists() else 0
        print(
            f"OK — {n_cases} eval cases, {n_lenses} lens references, "
            f"{n_skills} skills all valid."
        )
        return 0

    print(f"FAIL — {len(result.failures)} check(s) failed:")
    for check, detail in result.failures:
        print(f"  FAIL  {check}")
        print(f"        {detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
