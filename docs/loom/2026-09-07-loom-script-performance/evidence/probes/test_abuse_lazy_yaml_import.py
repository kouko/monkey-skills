"""Adversarial probes for W1-01 — lazy `yaml` import on the checker hook path.

These pin behaviour that must survive moving `import yaml` from module
scope into `load_manifest`: the non-push hook fast path must never touch
`yaml`, the push path must still reach `load_manifest`, non-hook
sub-commands that need the manifest must keep working, the Codex mirror
must keep behaving identically, and hostile/malformed hook payloads must
keep today's exact exit code and message unchanged by the refactor.

Run directly: `python3 -m pytest <this file> -v`.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
MIRROR = REPO_ROOT / ".codex" / "hooks" / "loom_checker.py"


def _init_git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "a@b.c"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "a"], cwd=repo, check=True)
    (repo / "f.txt").write_text("x\n")
    subprocess.run(["git", "add", "f.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
    return repo


def _run_hook_with_importtime(checker: Path, payload: dict, cwd: Path):
    return subprocess.run(
        [sys.executable, "-X", "importtime", str(checker), "push", "--hook"],
        input=json.dumps(payload),
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_hook_nonpush_command_does_not_import_yaml():
    """A1 positive: a non-push Bash command through `push --hook` must not
    load the `yaml` module at all — today it does, because `import yaml`
    sits at module scope and runs before the push/non-push branch."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        repo = _init_git_repo(Path(td))
        payload = {"tool_name": "Bash", "tool_input": {"command": "echo hi"}, "cwd": str(repo)}
        result = _run_hook_with_importtime(CHECKER, payload, repo)
        assert result.returncode == 0, result.stderr
        # importtime prints one line per module with the dotted module name
        # at the end of the line, e.g. "import time:       123 |    123 | yaml".
        yaml_import_lines = [ln for ln in result.stderr.splitlines() if ln.strip().split(" ")[-1] in ("yaml", "yaml.cyaml", "yaml.error", "yaml.tokens", "yaml.events", "yaml.nodes", "yaml.loader", "yaml.dumper", "yaml.resolver", "yaml.representer", "yaml.constructor", "yaml.composer", "yaml.parser", "yaml.scanner", "yaml.emitter", "yaml.serializer", "yaml.reader", "_yaml")]
        assert not yaml_import_lines, (
            "expected no `yaml` import on the non-push hook fast path, found:\n"
            + "\n".join(yaml_import_lines)
        )


def test_load_manifest_is_the_only_module_level_use_of_yaml():
    """AST check of the plan's stated fact: `yaml` must be referenced only
    inside `load_manifest`'s body, never at module scope. Today this is
    RED because of the top-level `import yaml` statement (a Import node at
    module scope, not inside any FunctionDef)."""
    tree = ast.parse(CHECKER.read_text(encoding="utf-8"))

    def function_bodies():
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                yield node

    load_manifest_nodes = [f for f in function_bodies() if f.name == "load_manifest"]
    assert load_manifest_nodes, "load_manifest must exist"
    load_manifest_node = load_manifest_nodes[0]
    inside_load_manifest = set(ast.walk(load_manifest_node))

    offending = []
    for node in ast.walk(tree):
        if node in inside_load_manifest:
            continue
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "yaml":
                    offending.append(("Import", node.lineno))
        if isinstance(node, ast.Name) and node.id == "yaml":
            offending.append(("Name", node.lineno))
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "yaml":
            offending.append(("Attribute", node.lineno))

    assert not offending, (
        "yaml must be referenced only inside load_manifest; found outside it: "
        f"{offending}"
    )


def test_push_command_still_reaches_manifest_via_block():
    """Negative: a push-shaped command in a repo with no review.json must
    still be judged (BLOCK from a push rule), not crash with ImportError
    or NameError from a mis-scoped `yaml` reference."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        repo = _init_git_repo(Path(td))
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "git push origin HEAD"},
            "cwd": str(repo),
        }
        result = subprocess.run(
            [sys.executable, str(CHECKER), "push", "--hook"],
            input=json.dumps(payload),
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "ImportError" not in result.stderr
        assert "NameError" not in result.stderr
        assert result.returncode in (0, 1, 2), result.stderr
        # It must have reached a real BLOCK/PASS decision, not an internal error.
        assert "loom_checker internal error" not in result.stderr, result.stderr


def test_contract_subcommand_without_hook_still_loads_manifest():
    """A non-hook sub-command that needs the manifest (`contract --require`)
    must keep working after yaml becomes a local import inside
    load_manifest — it doesn't go through cmd_push at all."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        repo = _init_git_repo(Path(td))
        result = subprocess.run(
            [sys.executable, str(CHECKER), "contract", "--require", "0.0"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Whatever the verdict, it must not die on missing/undefined `yaml`.
        assert "NameError" not in result.stderr
        assert "ImportError" not in result.stderr
        assert result.returncode != 2 or "loom_checker internal error" not in result.stderr


def test_codex_mirror_nonpush_hook_also_skips_yaml_import():
    """The committed Codex mirror must exhibit the same lazy-import
    behaviour as the source on the identical non-push hook path (it is
    the file Codex actually executes)."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        repo = _init_git_repo(Path(td))
        payload = {"tool_name": "Bash", "tool_input": {"command": "echo hi"}, "cwd": str(repo)}
        result = _run_hook_with_importtime(MIRROR, payload, repo)
        assert result.returncode == 0, result.stderr
        yaml_import_lines = [ln for ln in result.stderr.splitlines() if ln.strip().split(" ")[-1] in ("yaml",)]
        assert not yaml_import_lines, (
            "mirror still imports yaml on the non-push hook path:\n" + "\n".join(yaml_import_lines)
        )


def test_hook_missing_tool_input_exits_usage_error_before_and_after():
    """Hostile: a payload with no `tool_input` at all must keep behaving
    exactly as it does today (command defaults to ''), i.e. treated as a
    non-push command and exit 0 with no output — this must not regress
    when yaml import moves, and it must not silently start requiring
    tool_input."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        repo = _init_git_repo(Path(td))
        payload = {"tool_name": "Bash", "cwd": str(repo)}
        result = subprocess.run(
            [sys.executable, str(CHECKER), "push", "--hook"],
            input=json.dumps(payload),
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""


def test_hook_empty_stdin_raises_usage_error_exit_2():
    """Hostile: empty stdin on `push --hook` must keep raising the
    documented UsageError (exit 2) with the exact message, unchanged by
    where `yaml` gets imported."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        repo = _init_git_repo(Path(td))
        result = subprocess.run(
            [sys.executable, str(CHECKER), "push", "--hook"],
            input="",
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 2
        assert "push --hook expects a PreToolUse JSON payload on stdin." in result.stderr


def test_hook_malformed_json_raises_usage_error_exit_2():
    """Hostile: malformed JSON on stdin must keep failing closed at exit 2
    with a `hook payload is not JSON` message, not crash with an
    unrelated traceback caused by import reordering."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        repo = _init_git_repo(Path(td))
        result = subprocess.run(
            [sys.executable, str(CHECKER), "push", "--hook"],
            input="{not json",
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 2
        assert "hook payload is not JSON" in result.stderr
