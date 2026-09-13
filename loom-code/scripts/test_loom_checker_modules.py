"""Architecture contract for the modular Loom checker."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


SCRIPTS = Path(__file__).parent
ENTRY = SCRIPTS / "loom_checker.py"


def test_executable_rules_import_without_command_handlers() -> None:
    script = """
import sys
from loom_checker.rule_checks.intent import check_intent_schema, check_product_no_identifiers, check_needs_design_reason, check_needs_design_recompute, check_kind_recompute
from loom_checker.rule_checks.intake import check_confirmed, check_confirmed_behavior, check_spec_ready, check_test_case_pairs, check_req_grammar, check_ui_flows_recompute, check_plan_field_caps
from loom_checker.rule_checks.standing import check_standing_warn, check_standing_silence, check_product_principles, check_second_vendor
from loom_checker.rule_checks.contract import check_contract_requires
from loom_checker.rule_checks.charter import check_charter_row
from loom_checker.rule_checks.publish import validate_contextual_pr_body
from loom_checker.attestation import validate_attestation
assert check_kind_recompute([]) == []
assert not any(name.startswith('loom_checker.command_handlers.') for name in sys.modules)
"""
    subprocess.run([sys.executable, "-c", script], cwd=SCRIPTS, check=True, capture_output=True, text=True)


def test_each_subcommand_has_its_own_module() -> None:
    script = """
import runpy
commands = runpy.run_path('loom_checker.py')['COMMANDS']
expected = {'intent': 'intent', 'intents': 'intents', 'intake': 'intake', 'push': 'push', 'publish': 'publish', 'standing': 'standing', 'contract': 'contract', 'charter': 'charter', 'plan': 'plan', 'reviewer-count': 'reviewer_count', 'finalize-review': 'finalize'}
assert {name: fn.__module__ for name, fn in commands.items()} == {name: 'loom_checker.command_handlers.' + module for name, module in expected.items()}
"""
    subprocess.run([sys.executable, "-c", script], cwd=SCRIPTS, check=True, capture_output=True, text=True)


def test_rules_are_importable_without_command_modules() -> None:
    script = """
import sys
from loom_checker.rules import RULES
assert len(RULES) == 20
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
    assert len(rule_ids) == 20
    assert "push.attestation" in rule_ids
    assert "push.contextual-body" in rule_ids
    assert "standing.second-vendor-valid" in rule_ids
