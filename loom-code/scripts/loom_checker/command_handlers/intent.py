from __future__ import annotations

from loom_checker.helpers import UsageError
from loom_checker.helpers import load_manifest
from loom_checker.helpers import read_text
from loom_checker.helpers import repo_root
from loom_checker.helpers import report
from loom_checker.parsing import parse_document
from loom_checker.rule_checks.intent import check_intent_schema
from loom_checker.rule_checks.intent import check_kind_recompute
from loom_checker.rule_checks.intent import check_lane_reason
from loom_checker.rule_checks.intent import check_lane_schema
from loom_checker.rule_checks.intent import check_map_exists
from loom_checker.rule_checks.intent import check_needs_design_reason
from loom_checker.rule_checks.intent import check_needs_design_recompute
from loom_checker.rule_checks.intent import check_product_no_identifiers
from loom_checker.rule_checks.intent import touched_interface_surfaces
from pathlib import Path
import sys


def cmd_intent(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    path, commit_msg = None, None
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token == "--commit-msg":
            if not rest:
                raise UsageError("--commit-msg needs a file path.")
            commit_msg = Path(rest.pop(0))
        elif path is None:
            path = Path(token)
        else:
            raise UsageError(f"unexpected argument {token!r}.")
    if path is None:
        raise UsageError("intent needs a path to the intent file.")
    if not path.is_file():
        raise UsageError(f"no intent file at {path}")

    manifest = load_manifest()
    repo = repo_root(path)
    front, sections = parse_document(read_text(path))
    failures: list[tuple[str, str]] = []

    failures += check_intent_schema(manifest, front, sections)
    failures += check_map_exists(repo, front)
    failures += check_product_no_identifiers(front, sections)
    failures += check_lane_schema(front)
    failures += check_lane_reason(front, commit_msg, repo, path, out)

    reason_failures, needs_design = check_needs_design_reason(
        front, commit_msg, repo, path, out
    )
    failures += reason_failures

    kind = front.get("kind", "").strip()
    if needs_design == "no" or kind == "engineering":
        touched = touched_interface_surfaces(repo, manifest, out)
        if needs_design == "no":
            failures += check_needs_design_recompute(touched)
        if kind == "engineering":
            failures += check_kind_recompute(touched)

    return report(failures, err)
