"""Architecture contract for the modular Loom checker."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


SCRIPTS = Path(__file__).parent
ENTRY = SCRIPTS / "loom_checker.py"


def test_rules_are_importable_without_command_modules() -> None:
    script = """
import sys
from loom_checker.rules import RULES
assert len(RULES) == 19
assert not any(name.startswith('loom_checker.command_handlers.') for name in sys.modules)
"""
    subprocess.run(
        [sys.executable, "-c", script],
        cwd=SCRIPTS,
        check=True,
        capture_output=True,
        text=True,
    )


def test_entry_point_owns_only_cli_dispatch() -> None:
    tree = ast.parse(ENTRY.read_text(encoding="utf-8"))
    definitions = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
    assert definitions == {"main"}

    assignments = {
        target.id
        for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (
            node.targets if isinstance(node, ast.Assign) else [node.target]
        )
        if isinstance(target, ast.Name)
    }
    assert "COMMANDS" in assignments


def test_list_rules_still_reports_the_complete_public_set() -> None:
    result = subprocess.run(
        [sys.executable, str(ENTRY), "--list-rules"],
        cwd=SCRIPTS.parent.parent,
        check=True,
        capture_output=True,
        text=True,
    )
    rule_ids = {line.split("\t", 1)[0] for line in result.stdout.splitlines()}
    assert len(rule_ids) == 19
    assert "push.attestation" in rule_ids
    assert "push.contextual-body" in rule_ids
