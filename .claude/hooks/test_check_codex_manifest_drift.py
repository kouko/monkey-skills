"""Behavioral tests for the Codex-manifest drift PostToolUse hook.

The hook (``check-codex-manifest-drift.sh``) is a shift-left guard for the CI
``codex-manifest-drift`` gate. It must:

- fire for ANY plugin's ``*/.codex-plugin/plugin.json`` or
  ``*/.claude-plugin/plugin.json`` edit (not just loom-code),
- derive the plugin dir from the edited path and invoke the shared engine
  ``scripts/sync_codex_manifests.py --check <plugin>``,
- exit 0 when in sync, exit 2 on drift (blocking, with a stderr fix-hint),
- no-op (exit 0) for any non-manifest path.

Tests drive the hook the way Claude Code does: a mock PostToolUse stdin-JSON
``{"tool_input": {"file_path": ...}}`` piped to the script.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "check-codex-manifest-drift.sh"
SYNC_ENGINE = REPO_ROOT / "scripts" / "sync_codex_manifests.py"


def run_hook(file_path: str) -> subprocess.CompletedProcess[str]:
    stdin = json.dumps({"tool_input": {"file_path": file_path}})
    return subprocess.run(
        ["bash", str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
    )


def _make_repo(tmp_path: Path, *, drift: bool) -> Path:
    """Build a minimal repo: shared engine + one plugin's two manifests.

    Returns the path to the plugin's Codex manifest (what the hook is fed).
    """
    (tmp_path / "scripts").mkdir()
    shutil.copy(SYNC_ENGINE, tmp_path / "scripts" / "sync_codex_manifests.py")

    plugin = tmp_path / "myplugin"
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / ".codex-plugin").mkdir(parents=True)

    claude = {"name": "myplugin", "version": "1.2.3", "description": "d"}
    codex_desc = "DRIFTED" if drift else "d"
    codex = {
        "name": "myplugin",
        "version": "1.2.3",
        "description": codex_desc,
        "interface": {"displayName": "myplugin"},
    }
    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps(claude), encoding="utf-8")
    codex_path = plugin / ".codex-plugin" / "plugin.json"
    codex_path.write_text(json.dumps(codex), encoding="utf-8")
    return codex_path


def test_non_manifest_path_is_noop():
    result = run_hook("/somewhere/research-toolkit/SKILL.md")
    assert result.returncode == 0


def test_fires_for_arbitrary_plugin_in_sync(tmp_path):
    """A non-loom-code plugin whose manifests agree -> fires, exits 0."""
    codex_path = _make_repo(tmp_path, drift=False)
    result = run_hook(str(codex_path))
    assert result.returncode == 0, result.stderr


def test_fires_for_arbitrary_plugin_on_drift(tmp_path):
    """A non-loom-code plugin whose Codex manifest drifted -> blocks (exit 2)."""
    codex_path = _make_repo(tmp_path, drift=True)
    result = run_hook(str(codex_path))
    assert result.returncode == 2
    assert "drift" in result.stderr.lower()


def test_fires_on_claude_side_edit(tmp_path):
    """Editing the Claude SSOT side (not just Codex) also triggers the check."""
    codex_path = _make_repo(tmp_path, drift=True)
    claude_path = codex_path.parent.parent / ".claude-plugin" / "plugin.json"
    result = run_hook(str(claude_path))
    assert result.returncode == 2


def test_real_batch_a_plugin_in_sync():
    """A real in-repo Batch-A manifest path: all 21 are in sync -> exit 0."""
    real = REPO_ROOT / "research-toolkit" / ".codex-plugin" / "plugin.json"
    assert real.exists()
    result = run_hook(str(real))
    assert result.returncode == 0, result.stderr


def test_codex_less_plugin_is_noop(tmp_path):
    """A plugin with a .claude-plugin manifest but NO .codex-plugin (a
    deliberately Codex-less plugin like dev-workflow/collab/salesforce) ->
    the hook no-ops (exit 0), NOT a false drift block. Pins the load-bearing
    `[ -f .../.codex-plugin/plugin.json ] || exit 0` guard against regression:
    without it, every edit to those plugins would falsely block (exit 2)."""
    (tmp_path / "scripts").mkdir()
    shutil.copy(SYNC_ENGINE, tmp_path / "scripts" / "sync_codex_manifests.py")
    plugin = tmp_path / "codexless"
    (plugin / ".claude-plugin").mkdir(parents=True)
    claude_path = plugin / ".claude-plugin" / "plugin.json"
    claude_path.write_text(
        json.dumps({"name": "codexless", "version": "1.0.0", "description": "d"}),
        encoding="utf-8",
    )
    result = run_hook(str(claude_path))
    assert result.returncode == 0, result.stderr
