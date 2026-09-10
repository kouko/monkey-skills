"""Installation-layout proof for the independently packaged loom plugins.

Each plugin must be usable installed alone, under an arbitrary cache path,
composing with its siblings only through host-resolved skill names, the
loom-code contract package and the consumer project's own `docs/loom/`
artifacts — never through a sibling plugin's private files.

Loom 1.0 changed what there is to prove on the loom-design side. Its skills
used to declare `argv:` contracts running validators and verdict-minters out
of `${CLAUDE_PLUGIN_ROOT}/scripts/`, and most of this file drove each of
those commands from an isolated install. Those skills and scripts are gone:
loom-design 1.0 declares no in-plugin station command at all, and its four
SKILL.md files say in prose that no `${CLAUDE_PLUGIN_ROOT}` path reaches
loom-code. So the command-matrix tests are replaced by one that pins that
state — an empty command surface, asserted rather than assumed — plus the
one executable the plugin still ships, exercised from the isolated install.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
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
# loom 1.0 merged proposal-critique + complexity-critique into `critique` and
# deleted brief-before-asking (its judgement-fork definition moved into
# loom-code's one-way-door action).
REQUIRED_LOOM_WORKFLOW_SKILLS = {
    "critique",
    "decision-map",
    "git-memory",
}

# loom-design 1.0's whole skill surface: two stations and two tools.
DESIGN_SKILLS = {
    "capture-intent",
    "write-spec",
    "product-principles",
    "design-system",
}

# The one executable loom-design still ships. No SKILL.md declares an `argv:`
# contract for it — `test_design_declares_no_in_plugin_station_command` pins
# that — but it must be present and runnable from an isolated install,
# because the product-principles tool names it as its format contract.
DESIGN_EXECUTABLE = "scripts/principles/validate_principles_output.py"


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
        # The mount verbs a skill actually uses to send a reader to a
        # reference. Widened at loom 1.0 with `check`, `read`, `follow` and
        # the locative `are in` / `lives in`: the four surviving loom-design
        # skills mount their references with those words, and a heuristic
        # that misses a real mount reports a resolvable file as missing.
        #
        # The gap is `[^.]`, not `[^.\n]`: prose wraps, and a mount sentence
        # whose verb and filename land on different lines is the same
        # sentence. A period still bounds it, so the window stays inside one
        # sentence rather than reaching across a paragraph.
        instruction = re.search(
            rf"(?:follows?|following|load|read|check|reference"
            rf"|criteria table|builds on|(?:are|is|live|lives) in)"
            rf"[^.]{{0,180}}`{escaped}`"
            rf"|`{escaped}`[^.]{{0,180}}"
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
    """Every reference a skill loads must resolve INSIDE its own plugin."""
    capture_intent = design_root / "skills/capture-intent/SKILL.md"
    _resolve_local_contract(capture_intent, "references/interview.md", design_root)

    write_spec = design_root / "skills/write-spec/SKILL.md"
    _resolve_local_contract(write_spec, "references/spec-forms.md", design_root)
    _resolve_local_contract(write_spec, "references/ui-flows.md", design_root)

    design_system = design_root / "skills/design-system/SKILL.md"
    _resolve_local_contract(
        design_system, "references/design-md-schema.md", design_root
    )
    _resolve_local_contract(
        design_system, "references/knowledge-triage.md", design_root
    )

    implementer = code_root / "agents/implementer.md"
    _resolve_local_contract(
        implementer,
        "../references/engineering-baseline.md",
        code_root,
    )
    write_plan = code_root / "skills/write-plan/SKILL.md"
    _resolve_local_contract(write_plan, "references/one-way-door.md", code_root)


def _assert_local_behavior_dependencies(design_root: Path, code_root: Path) -> None:
    _assert_local_contract_graph(design_root, code_root)
    command = design_root / DESIGN_EXECUTABLE
    if not command.is_file():
        raise FileNotFoundError(command)


def _write_valid_principles(path: Path) -> None:
    path.write_text(
        "# PRINCIPLES\n\n"
        "## Who\nSolo maintainers.\n\n"
        "## Non-negotiables\n"
        "- Every claim ships with the command that proves it\n"
        "- One maintainer can run the whole thing alone\n"
        "- A deleted mechanism never comes back silently\n\n"
        "## Won't do\n- Multi-tenant billing\n\n"
        "## Failure we must avoid\n- Silent data loss\n\n"
        "## Fixed choices\n- Python\n\n"
        "ratified-by: kouko 2026-09-02\n",
        encoding="utf-8",
    )


def _execute_installed_design_command(design_root: Path, consumer_root: Path) -> None:
    """Run loom-design's one executable from an isolated install.

    The consumer paths carry an apostrophe deliberately: a command documented
    for a shell rather than for direct process execution breaks on exactly
    that, and the install layout is where it would break.
    """
    validator = design_root / DESIGN_EXECUTABLE
    consumer_root.mkdir(parents=True, exist_ok=True)

    accepted_file = consumer_root / "the project's PRINCIPLES.md"
    _write_valid_principles(accepted_file)
    accepted = subprocess.run(
        [sys.executable, str(validator), str(accepted_file)],
        cwd=consumer_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert accepted.returncode == 0, accepted.stderr

    # A run that accepts everything proves nothing, so drive a rejection too.
    rejected_file = consumer_root / "the project's thin PRINCIPLES.md"
    rejected_file.write_text(
        "# PRINCIPLES\n\n"
        "## Who\nSolo maintainers.\n\n"
        "## Non-negotiables\n- Only one\n\n"
        "## Won't do\n- Nothing\n\n"
        "## Failure we must avoid\n- Nothing\n\n"
        "## Fixed choices\n- Python\n",
        encoding="utf-8",
    )
    rejected = subprocess.run(
        [sys.executable, str(validator), str(rejected_file)],
        cwd=consumer_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode != 0, (
        "the validator accepted a PRINCIPLES.md carrying fewer than three "
        "non-negotiables, so running it proves nothing"
    )


def _assert_local_behavior_executes(
    design_root: Path, code_root: Path, tmp_path: Path
) -> None:
    assert not (design_root.parent / "loom-code").exists()
    assert not (code_root.parent / "loom-design").exists()
    _assert_local_behavior_dependencies(design_root, code_root)
    _execute_installed_design_command(
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

    # Hiding any one of these must make the dependency check fail — otherwise
    # that check is vacuous and would stay green on a broken install.
    required_contracts = (
        design_root / "skills/capture-intent/references/interview.md",
        design_root / "skills/write-spec/references/spec-forms.md",
        design_root / "skills/write-spec/references/ui-flows.md",
        design_root / "skills/design-system/references/design-md-schema.md",
        design_root / "skills/design-system/references/knowledge-triage.md",
        design_root / DESIGN_EXECUTABLE,
        code_root / "agents/implementer.md",
        code_root / "references/engineering-baseline.md",
        code_root / "skills/write-plan/references/one-way-door.md",
    )
    for contract in required_contracts:
        hidden = contract.with_suffix(contract.suffix + ".hidden")
        contract.rename(hidden)
        try:
            with pytest.raises(FileNotFoundError):
                _assert_local_behavior_dependencies(design_root, code_root)
        finally:
            hidden.rename(contract)


def _assert_isolated_design_install_has_no_code_sibling(design_root: Path) -> None:
    install_container = design_root.parent.parent
    assert design_root.parent.name == "loom-design"
    assert not (install_container / "loom-code").exists()
    assert "loom-code" not in {child.name for child in install_container.iterdir()}


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

    design_entry = (
        design_root / "skills" / "capture-intent" / "SKILL.md"
    ).read_text(encoding="utf-8")
    design_spec = (
        design_root / "skills" / "write-spec" / "SKILL.md"
    ).read_text(encoding="utf-8")
    design_system = (
        design_root / "skills" / "design-system" / "SKILL.md"
    ).read_text(encoding="utf-8")
    code_planning = (
        code_root / "skills" / "write-plan" / "SKILL.md"
    ).read_text(encoding="utf-8")

    # Composition uses host-resolved public skill names, never sibling paths.
    assert "loom-code" in design_entry

    # The shared state is project-owned loom artifacts, not plugin files.
    assert "docs/loom/intent/<change-id>.md" in design_entry
    assert "PRINCIPLES.md" in design_entry
    assert "DESIGN.md" in design_system
    assert "docs/loom/<change-id>/" in design_spec
    assert "docs/loom/<change-id>/" in code_planning
    assert "positive" in code_planning and "negative or boundary" in code_planning
    assert "review station once at branch end" in " ".join(code_planning.split())


def test_isolated_plugins_execute_local_behavior_without_sibling(tmp_path: Path) -> None:
    design_root = _install_plugin(
        "loom-design", tmp_path / "unrelated design cache's root"
    )
    code_root = _install_plugin("loom-code", tmp_path / "unrelated code cache's root")

    _assert_local_behavior_executes(design_root, code_root, tmp_path)


def test_isolated_codex_install_selects_only_its_native_hook_manifest(
    tmp_path: Path,
) -> None:
    code_root = _install_plugin("loom-code", tmp_path / "renamed codex cache")
    manifest = json.loads(
        (code_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )
    assert manifest["hooks"] == "./hooks/hooks-codex.json"
    selected = (code_root / manifest["hooks"]).resolve()
    selected.relative_to(code_root.resolve())
    hooks = json.loads(selected.read_text(encoding="utf-8"))["hooks"]
    assert set(hooks) == {"PreToolUse"}
    assert "${PLUGIN_ROOT}" in hooks["PreToolUse"][0]["hooks"][0]["command"]

    claude = json.loads(
        (code_root / "hooks/hooks.json").read_text(encoding="utf-8")
    )["hooks"]
    assert {"SessionStart", "PreToolUse", "PostToolUse"} <= set(claude)
    assert "${CLAUDE_PLUGIN_ROOT}" in json.dumps(claude)


def test_isolated_codex_hook_uses_copied_root_and_survives_its_removal(
    tmp_path: Path,
) -> None:
    code_root = _install_plugin("loom-code", tmp_path / "arbitrary codex root")
    manifest = json.loads(
        (code_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )
    hook_data = json.loads(
        (code_root / manifest["hooks"]).read_text(encoding="utf-8")
    )["hooks"]
    command = hook_data["PreToolUse"][0]["hooks"][0]["command"]
    payload = json.dumps(
        {
            "cwd": str(tmp_path),
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "git status --short"},
        }
    )
    env = dict(os.environ, PLUGIN_ROOT=str(code_root))
    present = subprocess.run(
        command, shell=True, input=payload, text=True, capture_output=True, env=env
    )
    assert present.returncode == 0, present.stderr

    shutil.rmtree(code_root)
    stale = subprocess.run(
        command, shell=True, input=payload, text=True, capture_output=True, env=env
    )
    assert stale.returncode == 0, stale.stderr


def test_isolated_host_hook_lifecycle_matrix(tmp_path: Path) -> None:
    code_root = _install_plugin("loom-code", tmp_path / "installed-v1")
    codex_manifest = json.loads(
        (code_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )
    codex_hooks = json.loads(
        (code_root / codex_manifest["hooks"]).read_text(encoding="utf-8")
    )["hooks"]
    claude_hooks = json.loads(
        (code_root / "hooks/hooks.json").read_text(encoding="utf-8")
    )["hooks"]
    codex_command = codex_hooks["PreToolUse"][0]["hooks"][0]["command"]
    claude_command = claude_hooks["PreToolUse"][0]["hooks"][0]["command"]

    def invoke(command: str, root_var: str, root: Path, body: str) -> subprocess.CompletedProcess[str]:
        payload = json.dumps(
            {
                "cwd": str(REPO_ROOT),
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": body},
            }
        )
        return subprocess.run(
            command, shell=True, input=payload, text=True, capture_output=True,
            env=dict(os.environ, **{root_var: str(root)}),
        )

    for body, expected in (("git status --short", 0), ("git push origin HEAD", 2)):
        codex = invoke(codex_command, "PLUGIN_ROOT", code_root, body)
        claude = invoke(claude_command, "CLAUDE_PLUGIN_ROOT", code_root, body)
        assert codex.returncode == claude.returncode == expected

    for command, root_var in (
        (codex_command, "PLUGIN_ROOT"),
        (claude_command, "CLAUDE_PLUGIN_ROOT"),
    ):
        malformed = subprocess.run(
            command, shell=True, input="not-json", text=True,
            capture_output=True, env=dict(os.environ, **{root_var: str(code_root)}),
        )
        assert malformed.returncode == 2

    shutil.rmtree(code_root)
    assert invoke(codex_command, "PLUGIN_ROOT", code_root, "git status").returncode == 0
    assert invoke(codex_command, "PLUGIN_ROOT", code_root, "git push origin HEAD").returncode == 2

    reloaded_root = _install_plugin("loom-code", tmp_path / "installed-v2")
    reloaded_manifest = json.loads(
        (reloaded_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )
    reloaded_command = json.loads(
        (reloaded_root / reloaded_manifest["hooks"]).read_text(encoding="utf-8")
    )["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    assert invoke(reloaded_command, "PLUGIN_ROOT", reloaded_root, "git status").returncode == 0


def test_design_declares_no_in_plugin_station_command(tmp_path: Path) -> None:
    """loom-design 1.0's command surface is empty, and that is load-bearing.

    Until 1.0 every design skill ran validators and verdict-minters out of
    `${CLAUDE_PLUGIN_ROOT}/scripts/`, and this file drove each one from an
    isolated install to prove those paths resolved there. The 1.0 stations
    call loom-code's checker instead, which they cannot reach by path — so
    the property to pin flipped: no skill may declare an in-plugin `argv:`
    command, and none may name a sibling plugin's private directory or its
    own plugin by repo path (which does not exist in an install). If a
    station command comes back, this fails, and the driving coverage it
    replaced has to come back with it.
    """
    design_root = _install_plugin(
        "loom-design", tmp_path / "arbitrarily named design install's root"
    )
    _assert_isolated_design_install_has_no_code_sibling(design_root)

    skills = sorted((design_root / "skills").iterdir())
    assert {skill.name for skill in skills} == DESIGN_SKILLS

    for skill in skills:
        for document in sorted(skill.rglob("*.md")):
            text = document.read_text(encoding="utf-8")
            rel = document.relative_to(design_root)
            assert "argv: [" not in text, (
                f"{rel} declares an in-plugin station command again"
            )
            assert "${CLAUDE_PLUGIN_ROOT}/scripts/" not in text, (
                f"{rel} reaches a script by plugin-root path again"
            )
            for sibling in (
                "loom-code/skills",
                "loom-code/scripts",
                "loom-code/hooks",
            ):
                assert sibling not in text, (
                    f"{rel} names the sibling plugin's private path {sibling!r}"
                )
            assert "loom-design/scripts" not in text, (
                f"{rel} names its own plugin by repo path, which does not "
                "exist in an install"
            )


def test_isolated_loom_workflow_bundle_contains_required_skills_and_executes(
    tmp_path: Path,
) -> None:
    """A renamed workflow install remains usable without the source checkout."""

    workflow_root = _install_plugin(
        "loom-workflow", tmp_path / "unrelated workflow cache's root"
    )
    assert not (workflow_root.parent / "dev-workflow").exists()
    assert find_boundary_violations(workflow_root) == []
    for skill_name in REQUIRED_LOOM_WORKFLOW_SKILLS:
        assert (workflow_root / "skills" / skill_name / "SKILL.md").is_file()

    consumer_root = tmp_path / "consumer repository"
    consumer_root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=consumer_root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "loom@example.test"],
        cwd=consumer_root,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Loom Test"],
        cwd=consumer_root,
        check=True,
    )
    (consumer_root / "README.md").write_text("# Consumer\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=consumer_root, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-qm",
            "test: seed consumer\n\nDecision: prove copied workflow scripts run locally",
        ],
        cwd=consumer_root,
        check=True,
    )

    memory_grep = workflow_root / "skills/git-memory/scripts/memory-grep.sh"
    verified = subprocess.run(
        ["bash", str(memory_grep), "--verify", "HEAD", f"--repo={consumer_root}"],
        cwd=consumer_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert verified.returncode == 0, verified.stderr


def test_memory_plugin_installs_alone(tmp_path: Path) -> None:
    """loom-memory copies into a clean isolated install root standalone.

    Its manifests must declare none of the mandatory-dependency keys and no
    `requires-contract` — loom-memory does not require loom-code's contract
    package, unlike loom-design.
    """
    memory_root = _install_plugin(
        "loom-memory", tmp_path / "unrelated memory cache's root"
    )
    assert not (memory_root.parent / "loom-code").exists()
    assert not (memory_root.parent / "loom-design").exists()

    manifest = _manifest(memory_root)
    dependency_text = _mandatory_dependency_text(manifest)
    assert dependency_text == "{}", dependency_text
    assert "requires-contract" not in manifest

    assert find_boundary_violations(memory_root) == []


def test_code_design_manifests_have_no_memory_dependency(tmp_path: Path) -> None:
    """loom-code and loom-design manifests must not gain a loom-memory dependency."""
    code_root = _install_plugin("loom-code", tmp_path / "code-cache-for-memory-check")
    design_root = _install_plugin(
        "loom-design", tmp_path / "design-cache-for-memory-check"
    )

    code_dependencies = _mandatory_dependency_text(_manifest(code_root))
    design_dependencies = _mandatory_dependency_text(_manifest(design_root))
    assert "loom-memory" not in code_dependencies
    assert "loom-memory" not in design_dependencies

    code_manifest_text = (code_root / ".claude-plugin" / "plugin.json").read_text(
        encoding="utf-8"
    )
    design_manifest_text = (design_root / ".claude-plugin" / "plugin.json").read_text(
        encoding="utf-8"
    )
    assert "loom-memory" not in code_manifest_text
    assert "loom-memory" not in design_manifest_text


# --- W4-01: the complete optional integration (REQ-3, REQ-22) --------------
#
# The tests above prove loom-memory installs alone and declares no mandatory
# dependency. What follows proves the two-way property the whole change
# exists for: loom-memory validates a real store using ONLY its own copied
# files (no repo-root path, no sibling plugin path), and loom-code /
# loom-design genuinely keep working — not just "declare no dependency" —
# with no loom-memory sibling installed at all.

MEMORY_FIXTURE = REPO_ROOT / "scripts" / "fixtures" / "loom-memory" / "okf-v0.2"


def test_isolated_loom_memory_validates_the_committed_fixture_using_only_installed_files(
    tmp_path: Path,
) -> None:
    """A1 positive / A6 positive.

    The fixture is copied to a location unrelated to both the plugin cache
    and the repository root, and the validator invoked is the one copied
    into the isolated install — never `REPO_ROOT`-relative and never a
    sibling plugin's script.
    """
    memory_root = _install_plugin(
        "loom-memory", tmp_path / "unrelated memory cache for fixture validation"
    )
    fixture_copy = tmp_path / "consumer project's memory store"
    shutil.copytree(MEMORY_FIXTURE, fixture_copy)

    validator = memory_root / "scripts" / "loom_memory.py"
    result = subprocess.run(
        [sys.executable, str(validator), "validate", str(fixture_copy)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_isolated_loom_memory_rejects_a_corrupted_fixture_copy_using_only_installed_files(
    tmp_path: Path,
) -> None:
    """A1 negative / A6 negative — the positive proof above is not vacuous:
    the same isolated install rejects a deliberately corrupted copy of the
    reserved `index.md` (clause 6 permits only `okf_version`)."""
    memory_root = _install_plugin(
        "loom-memory", tmp_path / "unrelated memory cache for corrupt fixture"
    )
    fixture_copy = tmp_path / "consumer project's corrupted memory store"
    shutil.copytree(MEMORY_FIXTURE, fixture_copy)
    index = fixture_copy / "index.md"
    index.write_text(
        index.read_text(encoding="utf-8").replace(
            'okf_version: "0.2"', 'okf_version: "0.2"\nextra_key: not allowed'
        ),
        encoding="utf-8",
    )

    validator = memory_root / "scripts" / "loom_memory.py"
    result = subprocess.run(
        [sys.executable, str(validator), "validate", str(fixture_copy)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "a corrupted index.md must fail validation"
    assert "reserved-index" in result.stdout


def _write_intake_fixture_repo(repo: Path, change_id: str) -> None:
    """A minimal git repo carrying a confirmed intent, ready for `intake
    write-plan`. Mirrors loom-code/scripts/test_loom_checker_intake.py's
    `make_repo()`: the checker's delivery-state rule reads the local
    remote-default ref, so this fixture needs one even though nothing is
    delivered on it."""

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
        ).stdout.strip()

    repo.mkdir(parents=True, exist_ok=True)
    git("init", "-q", "-b", "main")
    git("config", "user.email", "loom-memory-absence@example.test")
    git("config", "user.name", "Isolated Install Fixture")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git("add", "seed.txt")
    git("commit", "-q", "-m", "seed")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    git("checkout", "-q", "-b", "work")

    intent_path = repo / "docs/loom/intent" / f"{change_id}.md"
    intent_path.parent.mkdir(parents=True, exist_ok=True)
    intent_path.write_text(
        f"""# Fixture change
originator: tester
kind: engineering
needs-design: no — internal only
status: confirmed 2026-09-10

## Problem
The isolated install proof needs a confirmed intent.

## Proposed outcome
Prove `intake write-plan` completes with no loom-memory sibling installed.

## Acceptance
1. `intake write-plan {change_id}` exits 0.

## Constraints
- None.

## Out of scope
- Everything else.

## Open questions
- None yet.
""",
        encoding="utf-8",
    )


def test_isolated_loom_code_completes_write_plan_intake_without_loom_memory_sibling(
    tmp_path: Path,
) -> None:
    """REQ-3 / Acceptance #4 positive `consumers-work` and boundary
    `absent-plugin`.

    Installs ONLY loom-code (no loom-design, no loom-memory) into an
    unrelated cache root, runs the installed `loom_checker.py intake
    write-plan` from a fixture repository, and asserts a clean exit — and
    that nothing in the installed skill surface names loom-memory as a
    missing requirement.
    """
    code_root = _install_plugin(
        "loom-code", tmp_path / "isolated code cache without memory's root"
    )
    assert not (code_root.parent / "loom-memory").exists()
    assert not (code_root.parent / "loom-design").exists()

    change_id = "2026-09-10-fixture-absence-proof"
    fixture_repo = tmp_path / "consumer project without loom-memory"
    _write_intake_fixture_repo(fixture_repo, change_id)

    checker = code_root / "scripts" / "loom_checker.py"
    result = subprocess.run(
        [sys.executable, str(checker), "intake", "write-plan", change_id],
        cwd=fixture_repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    combined_output = result.stdout + result.stderr
    assert "loom-memory" not in combined_output

    for document in sorted(code_root.rglob("*.md")):
        if document.name.startswith("CHANGELOG"):
            continue
        text = document.read_text(encoding="utf-8")
        assert "loom-memory" not in text, (
            f"{document.relative_to(code_root)} still names loom-memory; an "
            "isolated install must not describe it as missing"
        )


def test_isolated_loom_design_keeps_complete_surface_without_loom_memory_sibling(
    tmp_path: Path,
) -> None:
    """REQ-3 / Acceptance #4 boundary `absent-plugin`: loom-design's skill
    and executable surface is complete with no loom-memory sibling
    installed, and no skill text names loom-memory as a missing
    requirement."""
    design_root = _install_plugin(
        "loom-design", tmp_path / "isolated design cache without memory's root"
    )
    assert not (design_root.parent / "loom-memory").exists()
    assert not (design_root.parent / "loom-code").exists()

    skills = sorted((design_root / "skills").iterdir())
    assert {skill.name for skill in skills} == DESIGN_SKILLS
    assert (design_root / DESIGN_EXECUTABLE).is_file()

    _execute_installed_design_command(
        design_root, tmp_path / "consumer project's unrelated root for design"
    )

    for document in sorted(design_root.rglob("*.md")):
        if document.name.startswith("CHANGELOG"):
            continue
        text = document.read_text(encoding="utf-8")
        assert "loom-memory" not in text, (
            f"{document.relative_to(design_root)} still names loom-memory; an "
            "isolated install must not describe it as missing"
        )


def test_isolated_loom_memory_boundary_check_rejects_sibling_paths(tmp_path: Path) -> None:
    """Bullet 1's closing clause, exercised through the real installed
    plugin rather than a synthetic fixture: `check_plugin_boundaries.py`
    rejects a sibling-private path even when the plugin under test is
    loom-memory itself."""
    memory_root = _install_plugin(
        "loom-memory", tmp_path / "memory cache for a boundary violation probe"
    )
    probe = memory_root / "skills" / "loom-memory" / "reference-probe.md"
    probe.write_text(
        "Read `loom-code/scripts/loom_checker.py` before recording a lesson.\n",
        encoding="utf-8",
    )
    try:
        violations = find_boundary_violations(memory_root)
        assert any("sibling internal path" in v for v in violations)
    finally:
        probe.unlink()
