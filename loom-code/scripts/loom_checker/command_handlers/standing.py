from __future__ import annotations

from loom_checker.helpers import UsageError
from loom_checker.helpers import read_text
from loom_checker.helpers import repo_root
from loom_checker.helpers import report
from loom_checker.parsing import parse_document
from loom_checker.rule_checks.standing import check_standing_silence, check_standing_warn, check_second_vendor, check_product_principles
from loom_checker.rule_checks.standing import find_standing_doc
from pathlib import Path
import sys


def cmd_standing(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    if not args:
        raise UsageError("standing needs a path to the intent file.")
    if len(args) > 1:
        raise UsageError(f"unexpected argument {args[1]!r}.")
    intent_path = Path(args[0])
    if not intent_path.is_file():
        raise UsageError(f"no intent file at {intent_path}")

    repo = repo_root(intent_path)
    front, _ = parse_document(read_text(intent_path))
    principles = find_standing_doc(repo, "PRINCIPLES.md")
    design = find_standing_doc(repo, "DESIGN.md")
    waived = check_standing_silence(repo)
    check_standing_warn(principles, design, waived, err)
    failures = check_second_vendor(repo)
    failures += check_product_principles(repo, front, principles)
    return report(failures, err)
