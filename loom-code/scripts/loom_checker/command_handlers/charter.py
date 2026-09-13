from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

import yaml

from git_exec import run_git

from ..helpers import UsageError, load_manifest, manifest_path_in_effect, report




CHARTER_HEADER = (
    "| artifact | answers | readers | must | must not → goes to | sign-off | edits after |\n"
)


CHARTER_SEPARATOR = "| --- | --- | --- | --- | --- | --- | --- |\n"


def _charter_join(values) -> str:
    if not isinstance(values, list) or not values:
        return ""
    return "; ".join(str(v) for v in values)


KEBAB_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _edits_after_cell(edits_after) -> str:
    """`<id>: <text>` per entry, joined by '; ' -- the dict shape (W1-02's
    charter-boundaries fix) every `edits_after` entry now carries."""
    if not isinstance(edits_after, list) or not edits_after:
        return ""
    return "; ".join(
        f"{item.get('id', '?')}: {item.get('text', '?')}"
        for item in edits_after if isinstance(item, dict)
    )


def _charter_has_forbidden_chars(value: str) -> bool:
    """A `|` or a newline inside a charter cell would render as extra
    markdown table columns or rows -- reject both."""
    return "|" in value or "\n" in value


def _check_charter_cell_chars(
    name: str, key: str, value: str, failures: list[tuple[str, str]]
) -> None:
    if isinstance(value, str) and _charter_has_forbidden_chars(value):
        failures.append((
            "contract.charter-complete",
            f"{name}.{key} contains a '|' or a newline, which would corrupt "
            f"the rendered table: {value!r}.",
        ))


def check_charter_row(
    name: str, charter: dict, all_names: list[str], stations: set[str]
) -> tuple[list[tuple[str, str]], tuple[str, str, str, str, str, str, str]]:
    """Recompute every column of one charter row against the rules the
    `contract.charter-complete` description promises: non-empty answers/
    readers/must/must_not/edits_after, every must_not item naming a kind
    and a goes_to that is ANOTHER artifact in the table, and a signoff
    naming a real station."""
    failures: list[tuple[str, str]] = []

    answers = charter.get("answers")
    if not isinstance(answers, str) or not answers.strip():
        failures.append(("contract.charter-complete", f"{name}.answers is empty."))
    else:
        _check_charter_cell_chars(name, "answers", answers, failures)

    readers = charter.get("readers")
    if not isinstance(readers, list) or not readers:
        failures.append(("contract.charter-complete", f"{name}.readers is empty."))
    else:
        for item in readers:
            if isinstance(item, str):
                _check_charter_cell_chars(name, "readers", item, failures)

    must = charter.get("must")
    if not isinstance(must, list) or not must:
        failures.append(("contract.charter-complete", f"{name}.must is empty."))
    else:
        for item in must:
            if isinstance(item, str):
                _check_charter_cell_chars(name, "must", item, failures)

    must_not = charter.get("must_not")
    if not isinstance(must_not, list) or not must_not:
        failures.append(("contract.charter-complete", f"{name}.must_not is empty."))
    else:
        for item in must_not:
            if not isinstance(item, dict) or not str(item.get("kind") or "").strip():
                failures.append(
                    ("contract.charter-complete", f"{name}.must_not has an entry with no kind.")
                )
                continue
            _check_charter_cell_chars(name, "must_not.kind", str(item.get("kind")), failures)
            goes_to = str(item.get("goes_to") or "").strip()
            if not goes_to:
                failures.append((
                    "contract.charter-complete",
                    f"{name}.must_not entry {item['kind']!r} names no goes_to.",
                ))
            elif goes_to == name:
                failures.append((
                    "contract.charter-complete",
                    f"{name}.must_not entry goes_to names itself ({name!r}); "
                    "it must name another artifact in the table.",
                ))
            elif goes_to not in all_names:
                failures.append((
                    "contract.charter-complete",
                    f"{name}.must_not entry goes_to {goes_to!r} names an artifact "
                    "absent from the table.",
                ))
            else:
                _check_charter_cell_chars(name, "must_not.goes_to", goes_to, failures)

    signoff = charter.get("signoff")
    if not isinstance(signoff, str) or not signoff.strip():
        failures.append(("contract.charter-complete", f"{name}.signoff is empty."))
    elif signoff not in stations:
        failures.append((
            "contract.charter-complete",
            f"{name}.signoff names unknown station {signoff!r}.",
        ))
    else:
        _check_charter_cell_chars(name, "signoff", signoff, failures)

    edits_after = charter.get("edits_after")
    if not isinstance(edits_after, list) or not edits_after:
        failures.append(("contract.charter-complete", f"{name}.edits_after is empty."))
    else:
        seen_ids: set[str] = set()
        for item in edits_after:
            if not isinstance(item, dict):
                failures.append((
                    "contract.charter-complete",
                    f"{name}.edits_after has a non-mapping entry {item!r}.",
                ))
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id.strip():
                failures.append(
                    ("contract.charter-complete", f"{name}.edits_after has an entry with no id.")
                )
            elif not KEBAB_ID.match(item_id):
                failures.append((
                    "contract.charter-complete",
                    f"{name}.edits_after id {item_id!r} is not kebab-case.",
                ))
            elif item_id in seen_ids:
                failures.append((
                    "contract.charter-complete",
                    f"{name}.edits_after id {item_id!r} is not unique within this artifact.",
                ))
            else:
                seen_ids.add(item_id)
            text = item.get("text")
            if not isinstance(text, str) or not text.strip():
                failures.append((
                    "contract.charter-complete",
                    f"{name}.edits_after entry {item.get('id', '?')!r} has no text.",
                ))
            elif isinstance(item_id, str):
                _check_charter_cell_chars(name, "edits_after", text, failures)

    must_not_cell = "; ".join(
        f"{item.get('kind', '?')} → {item.get('goes_to', '?')}"
        for item in must_not if isinstance(item, dict)
    ) if isinstance(must_not, list) else ""
    row = (
        name,
        str(answers) if isinstance(answers, str) and answers.strip() else "",
        _charter_join(readers),
        _charter_join(must),
        must_not_cell,
        str(signoff) if isinstance(signoff, str) and signoff.strip() else "",
        _edits_after_cell(edits_after),
    )
    return failures, row


def render_charter_table(rows: list[tuple[str, str, str, str, str, str, str]]) -> str:
    lines = [CHARTER_HEADER, CHARTER_SEPARATOR]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |\n")
    return "".join(lines)


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


__all__ = [name for name in globals() if not name.startswith("__")]
