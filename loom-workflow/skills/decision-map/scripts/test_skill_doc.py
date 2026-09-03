"""Public-contract drift tests for the decision-map skill."""

import ast
import json
import re
import shlex
import subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
MAP_FORMAT_MD = SKILL_DIR / "references" / "map-format.md"
PROTOTYPE_CONTRACT_MD = SKILL_DIR / "references" / "prototype-contract.md"
PLUGIN_ROOT = SKILL_DIR.parents[1]
CHANGELOG_MD = PLUGIN_ROOT / "CHANGELOG.md"
GOVERNANCE_MD = PLUGIN_ROOT / "docs" / "skill-governance.md"
CLAUDE_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
SCRIPTS_DIR = SKILL_DIR / "scripts"
SCRIPT_NAMES = (
    "map_init.py",
    "start_delivery.py",
    "map_store.py",
    "check_map_links.py",
    "check_map_fog.py",
    "map_progress.py",
)

V2_RETIRED_WRITEBACK_PHRASES = (
    "delegate to a backlog entry",
    "task → a backlog entry",
    "filing the backlog entry IS the resolution",
    "Parts section",
    "Parts row",
    "Delivery write-back",
)

INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")

# script[.py] [verb] <target> --repo-root <path>
DOCUMENTED_COMMANDS = (
    'python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/map_init.py" "<map-id>" --repo-root "<path>"',
    'python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/map_store.py" validate "<map-dir>" --repo-root "<path>"',
    'python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/check_map_links.py" "<map-dir>" --repo-root "<path>"',
    'python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/check_map_fog.py" "<map-dir>" --repo-root "<path>"',
    'python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/map_progress.py" "<target>" --repo-root "<path>"',
    'python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/start_delivery.py" "<map-dir>" "<DA-id>" "<change-id>" --repo-root "<path>"',
)

# start_delivery.py is a writer that requires an active Map with an open
# criterion, so the doc-runner cannot drive it from the bare scaffold above;
# test_start_delivery.py owns its behaviour.
RUNNABLE_FROM_SCAFFOLD = tuple(
    command for command in DOCUMENTED_COMMANDS if "start_delivery.py" not in command
)


def _normalize(command: str) -> str:
    """Collapse whitespace so line-wrapped or re-spaced quotes still match."""
    return " ".join(command.split())


def _script_commands(text: str) -> list[str]:
    """Return installed-plugin decision-map command spans."""
    commands = []
    for span in INLINE_CODE_RE.findall(text):
        stripped = span.strip()
        if stripped.startswith(
            'python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/'
        ):
            commands.append(stripped)
    return commands


def _implemented_reentry_states() -> set[str]:
    tree = ast.parse((SCRIPTS_DIR / "map_progress.py").read_text(encoding="utf-8"))
    states: set[str] = set()

    def state_literals(expression: ast.expr) -> set[str]:
        if isinstance(expression, ast.Constant) and isinstance(expression.value, str):
            return {expression.value}
        if isinstance(expression, ast.IfExp):
            return state_literals(expression.body) | state_literals(expression.orelse)
        return set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "ReentryReport":
            continue
        states.update(state_literals(node.args[0]))
    return states


def _implemented_delivery_phases() -> set[str]:
    tree = ast.parse((SCRIPTS_DIR / "map_progress.py").read_text(encoding="utf-8"))
    phases: set[str] = set()
    for function in (
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name in {"_plan_phase", "resolve_progress"}
    ):
        for returned in (
            node for node in ast.walk(function) if isinstance(node, ast.Return)
        ):
            value = returned.value
            if function.name == "_plan_phase" and isinstance(value, ast.Constant):
                if isinstance(value.value, str):
                    phases.add(value.value)
            elif isinstance(value, ast.Tuple) and value.elts:
                phase = value.elts[-1]
                if isinstance(phase, ast.Constant) and isinstance(phase.value, str):
                    phases.add(phase.value)
    return phases


def _run_documented_commands(tmp_path: Path, commands: list[str]) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Doc Test", "-c", "user.email=doc@example.invalid",
         "commit", "--allow-empty", "-qm", "base"],
        cwd=tmp_path,
        check=True,
    )
    map_dir = tmp_path / "docs" / "loom" / "maps" / "public-contract"
    substitutions = {
        "${CLAUDE_PLUGIN_ROOT}": str(PLUGIN_ROOT),
        "<map-id>": "public-contract",
        "<map-dir>": str(map_dir),
        "<target>": str(tmp_path),
        "<path>": str(tmp_path),
    }
    for documented in commands:
        rendered = documented
        for placeholder, value in substitutions.items():
            rendered = rendered.replace(placeholder, value)
        result = subprocess.run(
            shlex.split(rendered), cwd=tmp_path, capture_output=True, text=True
        )
        assert result.returncode == 0, (
            f"documented command failed: {documented}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def test_skill_commands_match_command_surface():
    assert SKILL_MD.is_file(), f"missing {SKILL_MD}"
    assert MAP_FORMAT_MD.is_file(), f"missing {MAP_FORMAT_MD}"

    skill_text = SKILL_MD.read_text(encoding="utf-8")
    surface_text = MAP_FORMAT_MD.read_text(encoding="utf-8")
    skill_commands = _script_commands(skill_text)
    surface_commands = _script_commands(surface_text)
    assert set(skill_commands) == set(DOCUMENTED_COMMANDS)
    assert set(surface_commands) == set(DOCUMENTED_COMMANDS)
    for text in (skill_text, surface_text):
        for script in SCRIPT_NAMES:
            assert re.search(rf"`{re.escape(script)}\s+<", text) is None


def test_v2_contract_rejects_relay_and_parts_language():
    """The v2 contract has no backlog relay or mutable Parts write-back."""
    contract_files = (MAP_FORMAT_MD, SKILL_MD)
    offenders = [
        f"{path}: {phrase}"
        for path in contract_files
        for phrase in V2_RETIRED_WRITEBACK_PHRASES
        if phrase.lower() in path.read_text(encoding="utf-8").lower()
    ]

    assert not offenders, "retired v2 contract wording remains:\n" + "\n".join(offenders)


def test_v3_contract_defines_multi_delivery_outcome_loop():
    # @req: REQ-75
    """A delivery closes one arc without completing or clearing its Map."""
    contract_files = (SKILL_MD, MAP_FORMAT_MD)
    for path in contract_files:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert "one persistent outcome-control loop" in text
        assert "multiple independently closed delivery arcs" in text
        assert "Closing a delivery arc must not clear the Map." in text


def test_v3_public_surface_commands_templates_and_version_are_synchronized(
    tmp_path: Path,
):
    # @req: REQ-75
    skill_source = SKILL_MD.read_text(encoding="utf-8")
    map_format_source = MAP_FORMAT_MD.read_text(encoding="utf-8")
    skill = _normalize(skill_source)
    map_format = _normalize(map_format_source)
    prototype = _normalize(PROTOTYPE_CONTRACT_MD.read_text(encoding="utf-8"))
    changelog = CHANGELOG_MD.read_text(encoding="utf-8")
    governance = _normalize(GOVERNANCE_MD.read_text(encoding="utf-8"))
    claude_manifest = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
    codex_manifest = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))

    assert claude_manifest["version"] == codex_manifest["version"]
    for manifest in (claude_manifest, codex_manifest):
        assert "Outcome Map" in manifest["description"]
        assert "decision-map" in manifest["keywords"]
    codex_interface = codex_manifest["interface"]
    assert "Outcome Map" in codex_interface["longDescription"]
    assert "decision-map" in codex_interface["longDescription"]
    assert "v3" in codex_interface["longDescription"]
    assert (
        "Use decision-map to start or resume an Outcome Map v3 for this repo."
        in codex_interface["defaultPrompt"]
    )
    assert f"## [{claude_manifest['version']}]" in changelog
    assert "v3.0.0" in governance

    for public_contract in (skill, map_format):
        assert "one persistent outcome-control loop" in public_contract
        assert "multiple independently closed delivery arcs" in public_contract
        assert "exactly three ticket closure types" in public_contract.lower()
        assert "`grilling`, `research`, and `prototype`" in public_contract
        assert "one outcome-advancing slice" in public_contract
        assert "source of truth" in public_contract
        assert "Map clear" in public_contract
        assert "retirement" in public_contract.lower()
        assert "schema_version: 3" in public_contract

    assert "machine-measured feasibility" in prototype
    assert "research" in prototype
    assert "human evaluates" in prototype
    assert "prototype" in prototype

    operations = (
        "Start",
        "Resume",
        "Claim",
        "Update blockers",
        "Close and re-chart",
        "Migrate v2 to v3",
        "Archive",
    )
    for operation in operations:
        assert operation in skill
    assert "preview_migration(map_dir)" in skill
    assert "apply_migration(map_dir, preview)" in skill
    assert "zero-write preview" in skill

    for command in DOCUMENTED_COMMANDS:
        assert command in skill
        assert command in map_format
    extracted_commands = list(dict.fromkeys(_script_commands(skill_source)))
    assert set(extracted_commands) == set(DOCUMENTED_COMMANDS)
    _run_documented_commands(
        tmp_path,
        [c for c in extracted_commands if c in RUNNABLE_FROM_SCAFFOLD],
    )

    expected_reentry_states = {
        "absent", "broken", "ambiguous-live", "live", "blocked", "claimed", "da-gap"
    }
    expected_delivery_phases = {
        "unbriefed", "briefed", "planning", "implementing", "reviewing",
        "finishing", "repair-required", "delivered",
    }
    assert _implemented_reentry_states() == expected_reentry_states
    assert _implemented_delivery_phases() == expected_delivery_phases
    state_sentence = (
        "Top-level re-entry states are exactly `absent`, `broken`, "
        "`ambiguous-live`, `live`, `blocked`, `claimed`, and `da-gap`."
    )
    phase_sentence = (
        "Legacy delivery phase values are separate and resolve only for "
        "pre-1.0 delivery tickets: `unbriefed`, `briefed`, `planning`, "
        "`implementing`, `reviewing`, `finishing`, `repair-required`, and "
        "`delivered`."
    )
    for public_contract in (skill, map_format):
        assert state_sentence in public_contract
        assert phase_sentence in public_contract

    assert "map_transaction.UnknownRoute" in skill
    assert "map_transaction.UnknownRoute" in map_format
    assert "`destination` is exactly `fog`, `ticket`, or `out-of-scope`" in map_format
    assert "`text` is non-empty after trimming" in map_format
    assert "ticket_slug" in map_format and "ticket_type" in map_format
    assert "only a `ticket` route may carry" in map_format.lower()
    assert "[a-z0-9]+(?:-[a-z0-9]+)*" in map_format
    assert "`grilling`, `research`, or `prototype`" in map_format
    assert "`(destination, text, ticket_slug)` is unique" in map_format
    assert "unique `ticket_slug`" in map_format

    risk_step = "Before every close-time gate, run the risk-front-loading pass"
    assert risk_step in skill
    assert risk_step in map_format
    close_checks = skill_source.split("## Close-time checks", 1)[1]
    assert close_checks.index(risk_step) < close_checks.index(DOCUMENTED_COMMANDS[1])

    ticket_template = (
        "type: <grilling|research|prototype> status: open "
        "claim: null graduated-from: null"
    )
    assert ticket_template in map_format


def test_v3_contract_pins_release_boundary_and_metric_definition():
    """Current map instructions retain the v3 boundary and metric facts."""
    map_format_text = MAP_FORMAT_MD.read_text(encoding="utf-8")
    skill_text = SKILL_MD.read_text(encoding="utf-8")

    assert "schema_version: 3" in map_format_text
    assert "v1" not in map_format_text
    assert "Exactly three ticket closure types exist" in skill_text
    assert "Dependencies are graph edges, not ticket types" in map_format_text
    assert "A closed delivery alone is never a clear transition" in map_format_text


def test_no_live_contract_or_command_surface_references_map_parts():
    """The retired Parts flipper and its tests must not remain live."""
    retired_script = SKILL_DIR / "scripts" / "map_parts.py"
    retired_test = SKILL_DIR / "scripts" / "test_map_parts.py"
    assert not retired_script.exists(), retired_script
    assert not retired_test.exists(), retired_test

    for path in (SKILL_MD, MAP_FORMAT_MD):
        text = path.read_text(encoding="utf-8").lower()
        assert "map_parts.py" not in text, f"{path} still references map_parts.py"
