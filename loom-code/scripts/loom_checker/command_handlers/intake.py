from __future__ import annotations

from loom_checker.helpers import UsageError
from loom_checker.helpers import artifact_path
from loom_checker.helpers import load_manifest
from loom_checker.helpers import read_text
from loom_checker.helpers import repo_root
from loom_checker.helpers import report
from loom_checker.intent_state import CHANGE_ID
from loom_checker.intent_state import INTAKE_STATIONS
from loom_checker.parsing import parse_document
from loom_checker.rule_checks.intake import check_confirmed
from loom_checker.rule_checks.intake import check_confirmed_behavior
from loom_checker.rule_checks.intake import check_plan_field_caps_at
from loom_checker.rule_checks.intake import check_req_grammar
from loom_checker.rule_checks.intake import check_spec_ready
from loom_checker.rule_checks.intake import check_test_case_pairs
from loom_checker.rule_checks.intake import check_ui_flows_recompute
from loom_checker.rule_checks.intent import check_kind_recompute
from loom_checker.rule_checks.intent import touched_interface_surfaces
from pathlib import Path
import sys


def cmd_intake(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    if len(args) < 2:
        raise UsageError("intake needs a station and a change-id.")
    station, change_id = args[0], args[1]
    if not CHANGE_ID.fullmatch(change_id):
        raise UsageError(
            f"{change_id!r} is not a change-id; expected [A-Za-z0-9._-]+ "
            "(the id is spliced into a path, so nothing else is accepted)."
        )
    if len(args) > 2:
        raise UsageError(f"unexpected argument {args[2]!r}.")
    if station not in INTAKE_STATIONS:
        raise UsageError(
            f"unknown station {station!r}; intake covers {' and '.join(INTAKE_STATIONS)}."
        )

    manifest = load_manifest()
    repo = repo_root(Path.cwd())
    failures = check_confirmed(manifest, repo, change_id, station)
    if failures:
        return report(failures, err)
    intent_path = artifact_path(manifest, "intent", change_id, repo)
    front, sections = parse_document(read_text(intent_path))

    failures: list[tuple[str, str]] = []
    if station == "write-plan":
        failures += check_test_case_pairs(manifest, repo, change_id, sections)
        failures += check_plan_field_caps_at(manifest, repo, change_id)

    kind = front.get("kind", "").strip()
    needs_design = front.get("needs-design", "").strip().split()[:1]
    yes_at_write_plan = station == "write-plan" and needs_design == ["yes"]

    touched: list[str] = []
    if kind == "engineering" or yes_at_write_plan:
        touched = touched_interface_surfaces(repo, manifest, out)
    if kind == "engineering":
        failures += check_kind_recompute(touched)

    failures += check_req_grammar(manifest, repo, change_id, sections)

    if yes_at_write_plan:
        failures += check_spec_ready(manifest, repo, change_id)
        failures += check_ui_flows_recompute(manifest, repo, change_id, touched)
        if kind == "product":
            failures += check_confirmed_behavior(manifest, repo, change_id, err)
    return report(failures, err)
