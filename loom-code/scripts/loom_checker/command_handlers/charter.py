from __future__ import annotations

from loom_checker.helpers import UsageError
from loom_checker.helpers import load_manifest
from loom_checker.helpers import manifest_path_in_effect
from loom_checker.helpers import report
from loom_checker.rule_checks.charter import check_charter_row
from loom_checker.rule_checks.charter import render_charter_table
from pathlib import Path
import sys


def cmd_charter(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """`loom_checker.py charter [--manifest PATH]` -- the human view of
    `artifacts.<name>.charter` (manifest.yaml is the checker-read SSOT;
    this renders it). Prints one markdown row per artifact in manifest
    order and recomputes `contract.charter-complete` over every row."""
    manifest_path = manifest_path_in_effect()
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token == "--manifest":
            if not rest:
                raise UsageError("--manifest needs a path.")
            manifest_path = Path(rest.pop(0))
        else:
            raise UsageError(f"unexpected argument {token!r}.")
    if not manifest_path.is_file():
        raise UsageError(f"no contract manifest at {manifest_path}")

    manifest = load_manifest(manifest_path)
    artifacts = manifest.get("artifacts")
    if not artifacts:
        out.write(render_charter_table([]))
        return report(
            [(
                "contract.charter-complete",
                "manifest carries no artifacts: mapping (absent or empty) -- "
                "every charter row is missing.",
            )],
            err,
        )
    stations = {
        s["name"] for s in manifest.get("stations", []) if isinstance(s, dict) and s.get("name")
    }
    all_names = list(artifacts.keys())

    failures: list[tuple[str, str]] = []
    rows: list[tuple[str, str, str, str, str, str, str]] = []
    for name in all_names:
        entry = artifacts.get(name) or {}
        charter = entry.get("charter")
        if not isinstance(charter, dict):
            failures.append((
                "contract.charter-complete",
                f"{name} has no charter block (`charter:` is missing entirely).",
            ))
            rows.append((name, "", "", "", "", "", ""))
            continue
        row_failures, row = check_charter_row(name, charter, all_names, stations)
        failures.extend(row_failures)
        rows.append(row)

    out.write(render_charter_table(rows))
    return report(failures, err)
