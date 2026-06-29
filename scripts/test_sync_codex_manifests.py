"""Tests for sync_codex_manifests.py — the REPO-LEVEL Codex manifest sync engine.

Unlike loom-code/scripts/sync_codex_manifest.py (self-locating to its own parent
plugin), this engine is repo-level: it takes a plugin (dir name or path) as input
and syncs that plugin's `.codex-plugin/plugin.json` shared fields from its
`.claude-plugin/plugin.json` SSOT, preserving the Codex-only `interface` block.

These tests build self-contained fixture plugin dirs under tmp_path so they never
touch any committed manifest. Stdlib only (json + subprocess to exercise the CLI).
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "sync_codex_manifests.py"

SHARED_FIELDS = (
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
)


def _claude_ssot() -> dict:
    return {
        "name": "demo-plugin",
        "version": "1.4.0",
        "description": "new description",
        "author": {"name": "kouko", "url": "https://github.com/kouko"},
        "homepage": "https://example.com/home",
        "repository": "https://example.com/repo",
        "license": "MIT",
        "keywords": ["a", "b", "c"],
        "skills": "./skills/",
    }


def _interface() -> dict:
    return {
        "displayName": "demo-plugin",
        "shortDescription": "short",
        "capabilities": ["Interactive", "Read", "Write"],
        "brandColor": "#2563EB",
    }


def _stale_codex() -> dict:
    return {
        "name": "demo-plugin",
        "version": "0.9.0",
        "description": "old description",
        "author": {"name": "kouko", "url": "https://github.com/kouko"},
        "homepage": "https://old.example.com",
        "repository": "https://example.com/repo",
        "license": "MIT",
        "keywords": ["a"],
        "skills": "./skills/",
        "interface": _interface(),
    }


def _build_plugin(plugin_dir: Path, claude: dict, codex: dict) -> Path:
    """Create <plugin_dir>/.claude-plugin/plugin.json + .codex-plugin/plugin.json."""
    (plugin_dir / ".claude-plugin").mkdir(parents=True)
    (plugin_dir / ".codex-plugin").mkdir(parents=True)
    (plugin_dir / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(claude, indent=2) + "\n", encoding="utf-8"
    )
    (plugin_dir / ".codex-plugin" / "plugin.json").write_text(
        json.dumps(codex, indent=2) + "\n", encoding="utf-8"
    )
    return plugin_dir


def _codex_path(plugin_dir: Path) -> Path:
    return plugin_dir / ".codex-plugin" / "plugin.json"


# --- the cohesive engine unit: sync copies shared fields, preserves interface --

def test_sync_copies_shared_fields_preserving_interface(tmp_path):
    import sync_codex_manifests as m

    plugin = _build_plugin(tmp_path / "demo-plugin", _claude_ssot(), _stale_codex())
    interface_before = json.loads(_codex_path(plugin).read_text())["interface"]

    m.sync_plugin(plugin)

    written = json.loads(_codex_path(plugin).read_text(encoding="utf-8"))
    for field in SHARED_FIELDS:
        assert written[field] == _claude_ssot()[field], f"{field} not synced from SSOT"
    # interface block byte-identical (preserved verbatim, not merged with SSOT)
    assert written["interface"] == interface_before
    assert written["interface"] == _interface()


def test_sync_accepts_plugin_dir_as_string_path(tmp_path):
    """Public surface takes a plugin dir name/path, not a hardcoded parent."""
    import sync_codex_manifests as m

    plugin = _build_plugin(tmp_path / "demo-plugin", _claude_ssot(), _stale_codex())
    m.sync_plugin(str(plugin))

    written = json.loads(_codex_path(plugin).read_text(encoding="utf-8"))
    assert written["version"] == _claude_ssot()["version"]


# --- --check is a pure read; in-sync exits 0, divergence exits non-zero --------

def _run(argv, plugin_dir: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *argv, str(plugin_dir)],
        capture_output=True,
        text=True,
    )


def test_check_exits_zero_when_synced(tmp_path):
    import sync_codex_manifests as m

    plugin = _build_plugin(tmp_path / "demo-plugin", _claude_ssot(), _stale_codex())
    m.sync_plugin(plugin)  # bring into sync first

    before = _codex_path(plugin).read_text(encoding="utf-8")
    proc = _run(["--check"], plugin)
    assert proc.returncode == 0, proc.stderr
    # --check must not mutate
    assert _codex_path(plugin).read_text(encoding="utf-8") == before


def test_check_exits_nonzero_after_mutating_one_shared_field(tmp_path):
    import sync_codex_manifests as m

    plugin = _build_plugin(tmp_path / "demo-plugin", _claude_ssot(), _stale_codex())
    m.sync_plugin(plugin)

    # mutate exactly one shared field on the Codex manifest -> divergence
    codex = json.loads(_codex_path(plugin).read_text(encoding="utf-8"))
    codex["version"] = "9.9.9"
    _codex_path(plugin).write_text(json.dumps(codex, indent=2) + "\n", encoding="utf-8")

    proc = _run(["--check"], plugin)
    assert proc.returncode != 0, "divergent shared field must fail --check"


def test_sync_plugin_check_mode_returns_bool_without_mutating(tmp_path):
    import sync_codex_manifests as m

    plugin = _build_plugin(tmp_path / "demo-plugin", _claude_ssot(), _stale_codex())
    before = _codex_path(plugin).read_text(encoding="utf-8")

    in_sync = m.sync_plugin(plugin, check=True)
    assert in_sync is False  # stale codex diverges
    assert _codex_path(plugin).read_text(encoding="utf-8") == before  # no mutation


def test_cli_sync_then_check_is_clean(tmp_path):
    plugin = _build_plugin(tmp_path / "demo-plugin", _claude_ssot(), _stale_codex())

    assert _run([], plugin).returncode == 0
    assert _run(["--check"], plugin).returncode == 0
