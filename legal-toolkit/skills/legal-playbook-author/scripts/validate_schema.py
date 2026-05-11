#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.20", "pyyaml>=6.0"]
# ///
"""validate_schema — JSON Schema validation of playbook .md frontmatter.

Reads one or more playbook .md files, parses the YAML frontmatter
between the leading `---` delimiters, validates against the schema
at `assets/schema.json` (oneOf flat / variant-file / _clause).

Best-effort + verbose error reporting: prints every validation
failure inline, exits 0 only when every input file validates.

Usage:
    validate_schema.py <path>...
    validate_schema.py legal-playbook/             # all .md under dir
    validate_schema.py --format json <path>...     # machine-readable
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "assets" / "schema.json"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def _normalise(value):
    """Recursively coerce YAML-parsed date/datetime values to ISO strings.

    PyYAML's safe_load auto-converts `YYYY-MM-DD` scalars to `datetime.date`
    objects, which the JSON-Schema pattern (a string regex) would otherwise
    reject. Re-stringify before validation so frontmatter authored in
    natural YAML date syntax still validates.
    """
    if isinstance(value, _dt.datetime):
        return value.isoformat()
    if isinstance(value, _dt.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _normalise(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    return value


def extract_frontmatter(text: str) -> dict | None:
    """Return parsed YAML dict from leading frontmatter, or None when absent."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    parsed = yaml.safe_load(m.group(1)) or {}
    return _normalise(parsed)


def _gather_files(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_dir():
            for entry in sorted(p.rglob("*.md")):
                # Skip seed README and dot-files
                if entry.name == "README.md" or entry.name.startswith("."):
                    continue
                out.append(entry)
        elif p.is_file():
            out.append(p)
    return out


def validate_one(path: Path, validator: jsonschema.Draft202012Validator) -> dict:
    """Return { path, ok, errors[], frontmatter? } for one .md file."""
    record: dict = {"path": str(path), "ok": False, "errors": []}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        record["errors"].append(f"read failed: {exc}")
        return record
    fm = extract_frontmatter(text)
    if fm is None:
        record["errors"].append("missing or unparseable frontmatter (--- block at top)")
        return record
    record["frontmatter"] = fm
    errs = list(validator.iter_errors(fm))
    if errs:
        for e in errs:
            location = "/".join(str(p) for p in e.absolute_path) or "<root>"
            record["errors"].append(f"{location}: {e.message}")
        return record
    record["ok"] = True
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", help=".md files or directories to validate")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )
    args = parser.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text())
    validator = jsonschema.Draft202012Validator(schema)

    files = _gather_files([Path(p) for p in args.paths])
    if not files:
        print("validate_schema: no .md files to validate", file=sys.stderr)
        return 2

    results = [validate_one(p, validator) for p in files]
    failures = [r for r in results if not r["ok"]]

    if args.format == "json":
        json.dump(
            {
                "checked": len(results),
                "passed": len(results) - len(failures),
                "failed": len(failures),
                "results": results,
            },
            sys.stdout,
            indent=2,
            ensure_ascii=False,
        )
        sys.stdout.write("\n")
    else:
        for r in results:
            status = "PASS" if r["ok"] else "FAIL"
            print(f"[{status}] {r['path']}")
            for e in r["errors"]:
                print(f"        {e}")
        print(
            f"\n{len(results)} checked, "
            f"{len(results) - len(failures)} passed, {len(failures)} failed"
        )

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
