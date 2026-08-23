"""Installation-layout proof for the two independently packaged loom plugins."""

from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from scripts.check_plugin_boundaries import find_boundary_violations


REPO_ROOT = Path(__file__).resolve().parents[1]
MANDATORY_DEPENDENCY_KEYS = {
    "dependencies",
    "pluginDependencies",
    "requiredPlugins",
    "requires",
}


def _install_plugin(source_name: str, destination: Path) -> Path:
    manifest = json.loads(
        (REPO_ROOT / source_name / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    installed_root = destination / source_name / manifest["version"]
    shutil.copytree(REPO_ROOT / source_name, installed_root)
    return installed_root


def _manifest(plugin_root: Path) -> dict[str, object]:
    return json.loads(
        (plugin_root / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )


def _mandatory_dependency_text(manifest: dict[str, object]) -> str:
    declarations = {
        key: value
        for key, value in manifest.items()
        if key in MANDATORY_DEPENDENCY_KEYS
    }
    return json.dumps(declarations, sort_keys=True)


def _resolve_local_contract(source: Path, reference: str, plugin_root: Path) -> Path:
    markdown = source.read_text(encoding="utf-8")
    links = re.findall(r"\[([^]\n]+)\]\(([^)]+)\)", markdown)
    target = next(
        (target for label, target in links if reference in {label, target}),
        None,
    )
    if target is None:
        escaped = re.escape(reference)
        instruction = re.search(
            rf"(?:follows|load|reference|criteria table|builds on)"
            rf"[^.\n]{{0,180}}`{escaped}`"
            rf"|`{escaped}`[^.\n]{{0,180}}"
            rf"(?:load|reference|on demand|pull)",
            markdown,
            flags=re.IGNORECASE,
        )
        if instruction:
            target = reference
    if target is None:
        raise FileNotFoundError(f"{source} does not resolve {reference}")
    resolved = (source.parent / target).resolve()
    resolved.relative_to(plugin_root.resolve())
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return resolved


def _assert_local_contract_graph(design_root: Path, code_root: Path) -> None:
    design_router = design_root / "skills/using-loom-design/SKILL.md"
    design_relay = _resolve_local_contract(
        design_router, "references/design-relay.md", design_root
    )
    _resolve_local_contract(design_relay, "family-relay.md", design_root)
    design_reception = _resolve_local_contract(
        design_router, "references/family-reception.md", design_root
    )
    _resolve_local_contract(design_reception, "family-relay.md", design_root)

    design_spec = design_root / "skills/spec-expansion/SKILL.md"
    _resolve_local_contract(
        design_spec, "references/design-panel-dispatch.md", design_root
    )
    _resolve_local_contract(
        design_spec, "references/requirement-identifiers.md", design_root
    )

    implementer = code_root / "agents/implementer.md"
    _resolve_local_contract(
        implementer,
        "../skills/writing-plans/references/requirement-identifiers.md",
        code_root,
    )
    plan_format = code_root / "skills/writing-plans/references/plan-format.md"
    _resolve_local_contract(
        plan_format, "requirement-identifiers.md", code_root
    )


def _assert_local_behavior_dependencies(design_root: Path, code_root: Path) -> None:
    _assert_local_contract_graph(design_root, code_root)
    for command in (
        design_root / "scripts/spec/validate_spec_output.py",
        design_root / "scripts/spec/mint_critic_verdict.py",
    ):
        if not command.is_file():
            raise FileNotFoundError(command)


def _write_valid_spec(change_folder: Path) -> None:
    (change_folder / "specs/authentication").mkdir(parents=True)
    (change_folder / "proposal.md").write_text(
        "## USM backbone\n- Log in\n\n"
        "## OOUX object model\n- User\n\n"
        "## Provenance\n- Login: seeded\n\n"
        "## Blind spots — needs human/field input\n- Policy threshold\n\n"
        "## Path × edge matrix\n| path | edge |\n| --- | --- |\n| login | retry |\n\n"
        "## Cross-object combinations\n| Stage | Objects |\n| --- | --- |\n| Login | User |\n\n"
        "## Journey navigation\n- Login → Home\n",
        encoding="utf-8",
    )
    (change_folder / "specs/authentication/spec.md").write_text(
        "## ADDED Requirements\n\n"
        "### Requirement: Login\n"
        "The system MUST authenticate valid users.\n\n"
        "#### Scenario: Valid credentials\n"
        "- GIVEN a registered user\n"
        "- WHEN valid credentials are submitted\n"
        "- THEN a session is created\n",
        encoding="utf-8",
    )


def _assert_invalid_spec_is_rejected(validator: Path, consumer_root: Path) -> None:
    invalid = consumer_root / "invalid output"
    (invalid / "specs/authentication").mkdir(parents=True)
    (invalid / "proposal.md").write_text("# Proposal\n", encoding="utf-8")
    (invalid / "specs/authentication/spec.md").write_text(
        "This deliberately has no OpenSpec requirement block.\n",
        encoding="utf-8",
    )
    rejected = subprocess.run(
        [sys.executable, str(validator), str(invalid)],
        cwd=consumer_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode == 1
    assert "INVALID:" in rejected.stderr
    assert "contains a '## ADDED Requirements'" in rejected.stderr


def _execute_installed_design_commands(
    design_root: Path,
    consumer_root: Path,
    *,
    validator: Path | None = None,
    verdict_tool: Path | None = None,
) -> None:
    change_folder = consumer_root / "docs/loom/change with a quote's name"
    _write_valid_spec(change_folder)
    validator = validator or design_root / "scripts/spec/validate_spec_output.py"
    validated = subprocess.run(
        [sys.executable, str(validator), str(change_folder)],
        cwd=consumer_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert validated.returncode == 0, validated.stderr
    _assert_invalid_spec_is_rejected(validator, consumer_root)

    (change_folder / "DESIGN.md").write_text("# Design\n", encoding="utf-8")
    (change_folder / "ui-flows.md").write_text("# Flows\n", encoding="utf-8")
    verdict_file = consumer_root / "critic verdict.md"
    verdict_file.write_text(
        "standards_version: 2026-06\nverdict: PASS_WITH_NOTES\n",
        encoding="utf-8",
    )
    verdict_tool = verdict_tool or design_root / "scripts/spec/mint_critic_verdict.py"
    common = [
        "--change-folder",
        str(change_folder),
        "--critic",
        "design-critic",
    ]
    receipt = change_folder / "design-critic-verdict.json"
    assert not receipt.exists()
    before_mint = subprocess.run(
        [
            sys.executable,
            str(verdict_tool),
            "validate",
            *common,
            "--files",
            "DESIGN.md,ui-flows.md",
        ],
        cwd=consumer_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert before_mint.returncode == 2
    assert "no verdict file at" in before_mint.stderr
    minted = subprocess.run(
        [
            sys.executable,
            str(verdict_tool),
            "mint",
            *common,
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md,ui-flows.md",
        ],
        cwd=consumer_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert minted.returncode == 0, minted.stderr
    assert receipt.is_file()
    receipt_data = json.loads(receipt.read_text(encoding="utf-8"))
    assert receipt_data["schema"] == 1
    assert receipt_data["verdict"] == "PASS_WITH_NOTES"
    assert receipt_data["files"] == ["DESIGN.md", "ui-flows.md"]
    assert len(receipt_data["sha256"]) == 64
    assert str(receipt) in minted.stdout
    checked = subprocess.run(
        [
            sys.executable,
            str(verdict_tool),
            "validate",
            *common,
            "--files",
            "DESIGN.md,ui-flows.md",
        ],
        cwd=consumer_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 0, checked.stderr


def _assert_local_behavior_executes(
    design_root: Path, code_root: Path, tmp_path: Path
) -> None:
    assert not (design_root.parent / "loom-code").exists()
    assert not (code_root.parent / "loom-design").exists()
    _assert_local_behavior_dependencies(design_root, code_root)
    _execute_installed_design_commands(
        design_root, tmp_path / "consumer project's unrelated root"
    )

    probe_dir = design_root / "reference-shape-probe"
    probe_dir.mkdir()
    (probe_dir / "local-contract.md").write_text("# Contract\n", encoding="utf-8")
    probe_source = probe_dir / "source.md"
    probe_source.write_text(
        "Example mention only: `local-contract.md`.\n", encoding="utf-8"
    )
    with pytest.raises(FileNotFoundError):
        _resolve_local_contract(probe_source, "local-contract.md", design_root)
    probe_source.write_text(
        "Load `local-contract.md` before continuing.\n", encoding="utf-8"
    )
    assert _resolve_local_contract(
        probe_source, "local-contract.md", design_root
    ).is_file()

    required_contracts = (
        design_root / "skills/using-loom-design/SKILL.md",
        design_root / "skills/using-loom-design/references/design-relay.md",
        design_root / "skills/using-loom-design/references/family-relay.md",
        design_root / "skills/using-loom-design/references/family-reception.md",
        design_root / "skills/spec-expansion/references/design-panel-dispatch.md",
        design_root / "skills/spec-expansion/references/requirement-identifiers.md",
        design_root / "scripts/spec/validate_spec_output.py",
        design_root / "scripts/spec/mint_critic_verdict.py",
        code_root / "agents/implementer.md",
        code_root / "skills/writing-plans/references/plan-format.md",
        code_root / "skills/writing-plans/references/requirement-identifiers.md",
    )
    for contract in required_contracts:
        hidden = contract.with_suffix(".md.hidden")
        contract.rename(hidden)
        try:
            with pytest.raises(FileNotFoundError):
                _assert_local_behavior_dependencies(design_root, code_root)
        finally:
            hidden.rename(contract)


def test_isolated_loom_plugins_are_standalone_and_compose_by_public_contract(
    tmp_path: Path,
) -> None:
    code_root = _install_plugin("loom-code", tmp_path / "code-cache")
    design_root = _install_plugin("loom-design", tmp_path / "design-cache")

    # The two layouts deliberately share no plugin directory or cache parent.
    assert code_root.parent.parent != design_root.parent.parent
    assert design_root not in code_root.parents
    assert code_root not in design_root.parents

    assert find_boundary_violations(code_root) == []
    assert find_boundary_violations(design_root) == []

    code_dependencies = _mandatory_dependency_text(_manifest(code_root))
    design_dependencies = _mandatory_dependency_text(_manifest(design_root))
    assert "loom-design" not in code_dependencies
    assert "loom-code" not in design_dependencies

    design_router = (
        design_root / "skills" / "using-loom-design" / "SKILL.md"
    ).read_text(encoding="utf-8")
    code_ui_verification = (
        code_root / "skills" / "ui-verification" / "SKILL.md"
    ).read_text(encoding="utf-8")
    design_spec = (
        design_root / "skills" / "spec-expansion" / "SKILL.md"
    ).read_text(encoding="utf-8")
    code_planning = (
        code_root / "skills" / "writing-plans" / "SKILL.md"
    ).read_text(encoding="utf-8")

    # Composition uses host-resolved public skill names, never sibling paths.
    assert "`loom-code:using-loom-code`" in design_router
    assert "`loom-design:interaction-flows`" in code_ui_verification

    # The shared state is project-owned loom artifacts, not plugin files.
    assert "PRINCIPLES.md" in design_router
    assert "DESIGN.md" in design_router
    assert "ui-flows.md" in design_router
    assert "ui-flows.md" in code_ui_verification
    assert "docs/loom/<change-id>/" in design_spec
    assert "docs/loom/<change-id>/" in code_planning
    assert "#### Scenario:" in design_spec
    assert "#### Scenario:" in code_planning


def test_isolated_plugins_execute_local_behavior_without_sibling(tmp_path: Path) -> None:
    design_root = _install_plugin(
        "loom-design", tmp_path / "unrelated design cache's root"
    )
    code_root = _install_plugin("loom-code", tmp_path / "unrelated code cache's root")

    _assert_local_behavior_executes(design_root, code_root, tmp_path)


def _station_argv_tools(document: str, expected_tools: tuple[str, ...]) -> list[list[str]]:
    contracts = [
        json.loads(raw)
        for raw in re.findall(r"argv: (\[[^\n`]+\])", document)
    ]
    assert contracts
    for contract in contracts:
        assert contract[0] == "python3"
        assert contract[1].startswith("${CLAUDE_PLUGIN_ROOT}/scripts/")

    normalized = document.replace(
        "${CLAUDE_PLUGIN_ROOT}", "_PLUGIN_ROOT_"
    ).replace("$CLAUDE_PLUGIN_ROOT", "_PLUGIN_ROOT_")
    assert normalized.count("_PLUGIN_ROOT_/scripts/") == len(contracts)

    tools = tuple(
        contract[1].removeprefix("${CLAUDE_PLUGIN_ROOT}/")
        for contract in contracts
    )
    assert Counter(tools) == Counter(expected_tools)
    return contracts


def test_all_interactive_station_commands_resolve_from_installed_root(
    tmp_path: Path,
) -> None:
    design_root = _install_plugin(
        "loom-design", tmp_path / "arbitrarily named design install's root"
    )
    expected_station_tools = {
        "business-value": ("scripts/discovery/validate_discovery_artifacts.py",),
        "user-insights": ("scripts/discovery/validate_discovery_artifacts.py",),
        "product-principles": (
            "scripts/principles/validate_principles_output.py",
            "scripts/principles/check_seed_traceability.py",
        ),
        "design-system": ("scripts/interface/validate_design_output.py",),
        "interaction-flows": ("scripts/interface/validate_design_output.py",),
        "design-critic": (
            "scripts/interface/validate_design_output.py",
            "scripts/interface/mint_critic_verdict.py",
        ),
        "completeness-critic": (
            "scripts/spec/validate_spec_output.py",
            "scripts/spec/mint_critic_verdict.py",
            "scripts/spec/mint_critic_verdict.py",
        ),
        "spec-expansion": (
            "scripts/spec/mint_critic_verdict.py",
            "scripts/spec/pairwise.py",
            "scripts/spec/validate_spec_output.py",
        ),
    }
    station_documents = {
        name: (design_root / "skills" / name / "SKILL.md").read_text(
            encoding="utf-8"
        )
        for name in expected_station_tools
    }
    unquoted_shell_mutation = station_documents["business-value"].replace(
        'argv: ["python3", '
        '"${CLAUDE_PLUGIN_ROOT}/scripts/discovery/validate_discovery_artifacts.py", '
        '"<discovery-folder>"]',
        "python3 $CLAUDE_PLUGIN_ROOT/scripts/discovery/"
        "validate_discovery_artifacts.py <discovery-folder>",
        1,
    )
    assert unquoted_shell_mutation != station_documents["business-value"]
    with pytest.raises(AssertionError):
        _station_argv_tools(
            unquoted_shell_mutation,
            expected_station_tools["business-value"],
        )
    consumer_root = tmp_path / "consumer project's quoted root"
    consumer_root.mkdir()
    discovery_folder = consumer_root / "discovery folder's output"
    discovery_folder.mkdir()
    (discovery_folder / "user-insights.md").write_text(
        "# Insights\n\n## Problem framing\nX\n\n## Opportunity space\nX\n\n"
        "## Value commitment\nX\n\n## Risks & open questions\nX\n",
        encoding="utf-8",
    )
    (discovery_folder / "evidence.md").write_text(
        "| Claim id | Claim | Evidence | Source | Date | Confidence |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| C1 | X | Y | Z | 2026-08-23 | high |\n",
        encoding="utf-8",
    )
    principles_file = consumer_root / "PRINCIPLES quoted's.md"
    principles_file.write_text(
        "# PRINCIPLES\n\n## Product Principles\n\n"
        "1. First — check: one\n2. Second — check: two\n"
        "3. Third — check: three\n",
        encoding="utf-8",
    )
    seed_inventory = consumer_root / "seed inventory's.md"
    seed_inventory.write_text(
        "named_anchors: none in this seed\n"
        "deferred_items: none in this seed\nnegative: none in this seed\n",
        encoding="utf-8",
    )
    design_output = consumer_root / "design output's folder"
    design_output.mkdir()
    design_sections = (
        "Overview / Brand", "Colors", "Typography", "Layout",
        "Elevation & Depth", "Shapes", "Components", "Do's & Don'ts",
    )
    (design_output / "DESIGN.md").write_text(
        "# DESIGN\n\n" + "\n".join(f"## {section}\nX" for section in design_sections),
        encoding="utf-8",
    )
    (design_output / "ui-flows.md").write_text(
        "# Flows\n\n## Inventory\nX\n## User Flows\nX\n## UI Structure\nX\n",
        encoding="utf-8",
    )
    change_folder = consumer_root / "change folder's output"
    _write_valid_spec(change_folder)
    verdict_file = consumer_root / "critic verdict's result.md"
    verdict_file.write_text(
        "standards_version: 2026-06\nverdict: PASS_WITH_NOTES\n",
        encoding="utf-8",
    )
    substitutions = {
        "<discovery-folder>": str(discovery_folder),
        "<principles-file>": str(principles_file),
        "<seed-inventory-file>": str(seed_inventory),
        "<design-output-dir>": str(design_output),
        "<design-change-folder>": str(design_output),
        "<change-folder>": str(change_folder),
        "<output-dir>": str(change_folder),
        "<verdict-file>": str(verdict_file),
    }
    seen_tools: set[str] = set()
    for station_name, document in station_documents.items():
        assert "loom-design/scripts" not in document, station_name
        assert "../../scripts" not in document, station_name
        assert "directly to process execution; never through a shell" in document
        contracts = _station_argv_tools(
            document, expected_station_tools[station_name]
        )
        for contract in contracts:
            relative_tool = contract[1].removeprefix("${CLAUDE_PLUGIN_ROOT}/")
            seen_tools.add(relative_tool)
            argv = [
                sys.executable,
                str(design_root / relative_tool),
                *(substitutions.get(arg, arg) for arg in contract[2:]),
            ]
            stdin_payload = None
            if relative_tool == "scripts/spec/pairwise.py":
                stdin_payload = json.dumps(
                    {"params": {"A": ["a1", "a2"], "B": ["b1", "b2"]}}
                )
            if "mint_critic_verdict.py" in relative_tool and "mint" in argv:
                pre_mint_argv = argv.copy()
                pre_mint_argv[2] = "validate"
                verdict_index = pre_mint_argv.index("--verdict-file")
                del pre_mint_argv[verdict_index : verdict_index + 2]
                rejected = subprocess.run(
                    pre_mint_argv,
                    cwd=consumer_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert rejected.returncode != 0, (station_name, rejected.stdout)
            executed = subprocess.run(
                argv,
                cwd=consumer_root,
                capture_output=True,
                text=True,
                input=stdin_payload,
                check=False,
            )
            assert executed.returncode == 0, (station_name, argv, executed.stderr)
            if relative_tool == "scripts/spec/pairwise.py":
                rows = json.loads(executed.stdout)
                assert {(row["A"], row["B"]) for row in rows} == {
                    ("a1", "b1"), ("a1", "b2"),
                    ("a2", "b1"), ("a2", "b2"),
                }
            if "mint_critic_verdict.py" in relative_tool and "mint" in argv:
                receipt = Path(substitutions[
                    "<design-output-dir>"
                    if station_name == "design-critic"
                    else "<change-folder>"
                ]) / f"{station_name}-verdict.json"
                assert receipt.is_file()
                validate_argv = argv.copy()
                validate_argv[2] = "validate"
                verdict_index = validate_argv.index("--verdict-file")
                del validate_argv[verdict_index : verdict_index + 2]
                validated = subprocess.run(
                    validate_argv,
                    cwd=consumer_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert validated.returncode == 0, validated.stderr

    assert seen_tools == {
        "scripts/discovery/validate_discovery_artifacts.py",
        "scripts/principles/validate_principles_output.py",
        "scripts/principles/check_seed_traceability.py",
        "scripts/interface/validate_design_output.py",
        "scripts/interface/mint_critic_verdict.py",
        "scripts/spec/validate_spec_output.py",
        "scripts/spec/mint_critic_verdict.py",
        "scripts/spec/pairwise.py",
    }

    for relative_tool in seen_tools - {
        "scripts/interface/mint_critic_verdict.py",
        "scripts/spec/mint_critic_verdict.py",
        "scripts/spec/pairwise.py",
    }:
        bad_target = consumer_root / f"invalid target for {Path(relative_tool).stem}"
        if "check_seed_traceability" in relative_tool:
            bad_target.write_text("named_anchors: missing\n", encoding="utf-8")
            bad_args = [str(principles_file), str(bad_target)]
        else:
            bad_target.mkdir()
            bad_args = [str(bad_target)]
        rejected = subprocess.run(
            [sys.executable, str(design_root / relative_tool), *bad_args],
            cwd=consumer_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert rejected.returncode != 0, relative_tool

    rejected_pairwise = subprocess.run(
        [sys.executable, str(design_root / "scripts/spec/pairwise.py")],
        cwd=consumer_root,
        input="not-json",
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected_pairwise.returncode != 0


def test_isolated_design_command_matrix_observes_every_family(tmp_path: Path) -> None:
    design_root = _install_plugin(
        "loom-design", tmp_path / "renamed plugin root's cache"
    )

    _assert_complete_design_command_matrix(design_root, tmp_path)


def _encoded_argv(argv: list[str]) -> str:
    raw = json.dumps(argv).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _run_tool(tool: Path, args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(tool), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _assert_isolated_design_install_has_no_code_sibling(design_root: Path) -> None:
    install_container = design_root.parent.parent
    assert design_root.parent.name == "loom-design"
    assert not (install_container / "loom-code").exists()
    assert "loom-code" not in {child.name for child in install_container.iterdir()}


def _documented_pipeline_tools(
    design_root: Path, pipeline_skill: str
) -> tuple[Path, Path]:
    bridge_match = re.search(
        r'python3 "\$\{CLAUDE_PLUGIN_ROOT\}/([^"\n]*argv_exec\.py)"',
        pipeline_skill,
    )
    batch_match = re.search(
        r'`batchQueueScript` to\s*`pluginRoot \+ "(/scripts/pipeline/batch_queue\.py)"`',
        pipeline_skill,
    )
    assert bridge_match, "pipeline skill must document its installed-root argv bridge"
    assert batch_match, "pipeline skill must document its installed-root batch tool"
    bridge = design_root / bridge_match.group(1)
    batch_tool = design_root / batch_match.group(1).removeprefix("/")
    bridge.resolve().relative_to(design_root.resolve())
    batch_tool.resolve().relative_to(design_root.resolve())
    return bridge, batch_tool


def _assert_spec_expansion_pairwise_commands(
    design_root: Path, tmp_path: Path
) -> None:
    document = (design_root / "skills/spec-expansion/SKILL.md").read_text(
        encoding="utf-8"
    )
    documented = set(
        re.findall(
            r'\$\{CLAUDE_PLUGIN_ROOT\}/(scripts/spec/[A-Za-z0-9_.-]+\.py)',
            document,
        )
    )
    expected = {
        "scripts/spec/validate_spec_output.py",
        "scripts/spec/mint_critic_verdict.py",
        "scripts/spec/pairwise.py",
    }
    assert documented == expected
    assert "loom-design/scripts" not in document
    validator = design_root / "scripts/spec/validate_spec_output.py"
    verdict_tool = design_root / "scripts/spec/mint_critic_verdict.py"
    _execute_installed_design_commands(
        design_root,
        tmp_path / "spec-expansion pairwise",
        validator=validator,
        verdict_tool=verdict_tool,
    )
    pairwise_tool = design_root / "scripts/spec/pairwise.py"
    _assert_pairwise_cli_behavior(pairwise_tool, tmp_path)
    for relative_tool in sorted(documented):
        mutation_root = tmp_path / "spec-expansion mutations" / Path(relative_tool).stem
        shutil.copytree(design_root, mutation_root)
        (mutation_root / relative_tool).write_text(
            "#!/usr/bin/env python3\n", encoding="utf-8"
        )
        with pytest.raises(AssertionError):
            if relative_tool.endswith("pairwise.py"):
                _assert_pairwise_cli_behavior(mutation_root / relative_tool, tmp_path)
            else:
                _execute_installed_design_commands(
                    mutation_root,
                    tmp_path / "spec-expansion no-op" / Path(relative_tool).stem,
                    validator=mutation_root / "scripts/spec/validate_spec_output.py",
                    verdict_tool=mutation_root / "scripts/spec/mint_critic_verdict.py",
                )


def _assert_pairwise_cli_behavior(tool: Path, cwd: Path) -> None:
    payload = {"params": {name: ["on", "off"] for name in "ABCD"}}
    generated = subprocess.run(
        [sys.executable, str(tool)],
        cwd=cwd,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    assert generated.returncode == 0, generated.stderr
    assert generated.stdout.strip()
    rows = json.loads(generated.stdout)
    assert rows
    assert all(set(row) == set("ABCD") for row in rows)
    rejected = subprocess.run(
        [sys.executable, str(tool)],
        cwd=cwd,
        input="{}",
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode != 0


def _assert_pipeline_bridge_changes_real_state(
    design_root: Path,
    consumer_root: Path,
    *,
    bridge: Path | None = None,
    batch_tool: Path | None = None,
) -> None:
    project = consumer_root / "pipeline project $(touch should-not-exist)'s root"
    loom_dir = project / "docs/loom"
    loom_dir.mkdir(parents=True)
    (loom_dir / "QUEUE.toml").write_text(
        '[[change]]\nid = "cold-start"\nplan = "docs/loom/plan.md"\n'
        "[change.budgets]\nrun = 1000\n",
        encoding="utf-8",
    )
    (loom_dir / "queue-state.json").write_text(
        json.dumps({"cold-start": {"status": "RUNNING"}}) + "\n",
        encoding="utf-8",
    )
    sentinel = consumer_root / "should-not-exist"
    run_id = "run $(touch should-not-exist);'quoted'"
    session_dir = consumer_root / "session $(touch should-not-exist)'s dir"
    payload = _encoded_argv(
        [
            "mark-running",
            "cold-start",
            "--run-id",
            run_id,
            "--session-dir",
            str(session_dir),
            "--project",
            str(project),
        ]
    )
    bridge = bridge or design_root / "scripts/pipeline/argv_exec.py"
    batch_tool = batch_tool or design_root / "scripts/pipeline/batch_queue.py"
    status = _run_tool(batch_tool, ["status", "--project", str(project)], consumer_root)
    assert status.returncode == 0, status.stderr
    assert "cold-start" in status.stdout
    assert "RUNNING" in status.stdout
    result = _run_tool(bridge, [payload], consumer_root)
    assert result.returncode == 0, result.stderr
    state = json.loads((loom_dir / "queue-state.json").read_text(encoding="utf-8"))
    assert state["cold-start"]["status"] == "RUNNING"
    assert state["cold-start"].get("runId") == run_id
    assert state["cold-start"].get("sessionDir") == str(session_dir)
    assert not sentinel.exists()
    rejected = _run_tool(bridge, ["not-base64!"], consumer_root)
    assert rejected.returncode == 2
    assert "URL-safe base64" in rejected.stderr


def _assert_complete_design_command_matrix(
    design_root: Path, tmp_path: Path
) -> None:
    _assert_isolated_design_install_has_no_code_sibling(design_root)
    pipeline_skill = (
        design_root / "skills/using-loom-pipeline/SKILL.md"
    ).read_text(encoding="utf-8")
    assert "loom-design/scripts" not in pipeline_skill
    assert '${CLAUDE_PLUGIN_ROOT}/scripts/pipeline/argv_exec.py' in pipeline_skill
    documented_bridge, documented_batch = _documented_pipeline_tools(
        design_root, pipeline_skill
    )
    _assert_spec_expansion_pairwise_commands(design_root, tmp_path)

    # The station probe executes every documented discovery, principles,
    # interface, and spec command with success and rejection cases.
    test_all_interactive_station_commands_resolve_from_installed_root(
        tmp_path / "station matrix"
    )
    _assert_pipeline_bridge_changes_real_state(
        design_root,
        tmp_path / "pipeline matrix",
        bridge=documented_bridge,
        batch_tool=documented_batch,
    )

    # Mutation probes ensure a copied executable cannot satisfy the contract
    # merely by existing or accepting --help. Every validator must reject bad
    # input; both critic families and the pipeline bridge must create state.
    validator_cases = {
        "scripts/discovery/validate_discovery_artifacts.py": [
            str(tmp_path / "missing discovery")
        ],
        "scripts/principles/validate_principles_output.py": [
            str(tmp_path / "missing principles")
        ],
        "scripts/principles/check_seed_traceability.py": [
            str(tmp_path / "missing principles"),
            str(tmp_path / "missing inventory"),
        ],
        "scripts/interface/validate_design_output.py": [
            str(tmp_path / "missing design")
        ],
        "scripts/spec/validate_spec_output.py": [str(tmp_path / "missing spec")],
    }
    for relative_tool, args in validator_cases.items():
        mutation_root = tmp_path / "mutations" / Path(relative_tool).stem
        shutil.copytree(design_root, mutation_root)
        mutated_tool = mutation_root / relative_tool
        mutated_tool.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        with pytest.raises(AssertionError):
            rejected = _run_tool(mutated_tool, args, tmp_path)
            assert rejected.returncode != 0

    for family in ("interface", "spec"):
        mutation_root = tmp_path / "mutations" / f"{family}-critic"
        shutil.copytree(design_root, mutation_root)
        mutated_tool = mutation_root / f"scripts/{family}/mint_critic_verdict.py"
        mutated_tool.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        change_folder = tmp_path / "mutated critic outputs" / family
        change_folder.mkdir(parents=True)
        verdict = tmp_path / "mutated critic outputs" / f"{family}.md"
        verdict.write_text(
            "standards_version: 2026-06\nverdict: PASS_WITH_NOTES\n",
            encoding="utf-8",
        )
        critic = "design-critic" if family == "interface" else "completeness-critic"
        receipt = change_folder / f"{critic}-verdict.json"
        result = _run_tool(
            mutated_tool,
            [
                "mint", "--change-folder", str(change_folder), "--critic", critic,
                "--verdict-file", str(verdict), "--files", "artifact.md",
            ],
            tmp_path,
        )
        assert result.returncode == 0
        assert not receipt.exists()

    for relative_tool in (
        "scripts/pipeline/argv_exec.py",
        "scripts/pipeline/batch_queue.py",
    ):
        mutation_root = tmp_path / "mutations" / Path(relative_tool).stem
        shutil.copytree(design_root, mutation_root)
        (mutation_root / relative_tool).write_text(
            "#!/usr/bin/env python3\n", encoding="utf-8"
        )
        with pytest.raises(AssertionError):
            _assert_pipeline_bridge_changes_real_state(
                mutation_root, tmp_path / "mutated pipeline" / Path(relative_tool).stem
            )
