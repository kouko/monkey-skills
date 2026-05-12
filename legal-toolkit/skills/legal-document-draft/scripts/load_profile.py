#!/usr/bin/env python3
"""Load and validate legal-playbook/profile.yml against profile-schema.yml.

Public API:
    load_profile(profile_path: Path) -> LoadResult

LoadResult fields:
    valid: bool          True iff schema validation passed
    data: dict           parsed YAML; empty dict if file unreadable
    errors: list[str]    human-readable validation errors

Usage from a skill protocol:
    from load_profile import load_profile
    r = load_profile(Path("legal-playbook/profile.yml"))
    if not r.valid:
        for err in r.errors:
            print(f"profile.yml validation error: {err}")
        sys.exit(2)
    company = r.data["company_name"]
    ...
"""
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema
import yaml

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "assets" / "profile-schema.yml"


@dataclass
class LoadResult:
    valid: bool
    data: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def _load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_profile(profile_path: Path) -> LoadResult:
    if not profile_path.is_file():
        return LoadResult(valid=False, errors=[f"profile file not found: {profile_path}"])

    try:
        data = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return LoadResult(valid=False, errors=[f"YAML parse error: {e}"])

    schema = _load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in validator.iter_errors(data):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")

    return LoadResult(valid=not errors, data=data, errors=errors)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("usage: load_profile.py <path/to/profile.yml>", file=sys.stderr)
        sys.exit(2)
    result = load_profile(Path(sys.argv[1]))
    if result.valid:
        print(f"OK: profile valid; company={result.data.get('company_name')}")
        sys.exit(0)
    else:
        for err in result.errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)
