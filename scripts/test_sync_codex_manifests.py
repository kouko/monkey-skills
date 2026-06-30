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


# --- --scaffold seeds a missing Codex manifest with mechanical + TODO fields ---

def _build_claude_only(plugin_dir: Path, claude: dict) -> Path:
    """Create only <plugin_dir>/.claude-plugin/plugin.json (no Codex manifest)."""
    (plugin_dir / ".claude-plugin").mkdir(parents=True)
    (plugin_dir / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(claude, indent=2) + "\n", encoding="utf-8"
    )
    return plugin_dir


def test_scaffold_seeds_mechanical_fields_and_todo_placeholders(tmp_path):
    import sync_codex_manifests as m

    plugin = _build_claude_only(tmp_path / "demo-plugin", _claude_ssot())
    assert not _codex_path(plugin).exists()

    m.scaffold_plugin(plugin)

    written = json.loads(_codex_path(plugin).read_text(encoding="utf-8"))
    # shared fields seeded from the Claude SSOT
    for field in SHARED_FIELDS:
        assert written[field] == _claude_ssot()[field], f"{field} not seeded from SSOT"

    iface = written["interface"]
    # mechanically-derivable fields come from the Claude manifest
    assert iface["displayName"] == "demo-plugin"  # == name
    assert iface["developerName"] == "kouko"  # == author.name
    # websiteURL == repository + "/tree/main/" + name (canonical GitHub subdir form)
    assert iface["websiteURL"] == "https://example.com/repo/tree/main/demo-plugin"
    # judgment fields are literal "TODO" placeholders for Phase 2 to fill
    for todo in ("longDescription", "category", "capabilities", "defaultPrompt", "brandColor"):
        assert iface[todo] == "TODO", f"{todo} must be a TODO placeholder"


def test_website_url_falls_back_to_homepage_when_no_repository(tmp_path):
    """A plugin with `homepage` but NO `repository` must get a real URL.

    The Claude SSOT's `homepage` is the canonical GitHub tree URL; when
    `repository` is absent the websiteURL fallback must use it, not degrade to
    the bare plugin name (which is not a URL).
    """
    import sync_codex_manifests as m

    claude = _claude_ssot()
    del claude["repository"]
    claude["homepage"] = "https://github.com/kouko/monkey-skills/tree/main/demo-plugin"

    plugin = _build_claude_only(tmp_path / "demo-plugin", claude)
    m.scaffold_plugin(plugin)

    iface = json.loads(_codex_path(plugin).read_text(encoding="utf-8"))["interface"]
    assert iface["websiteURL"] == claude["homepage"]
    assert iface["websiteURL"] != "demo-plugin"  # must not degrade to bare name


def test_check_all_reports_missing_manifest_cleanly(tmp_path):
    """`--all --check` on an eligible plugin with no Codex manifest must fail
    with a clean MISSING message, not a raw FileNotFoundError traceback."""
    dirs = _build_all_eligible(tmp_path)
    assert _run_all([], tmp_path).returncode == 0  # bring all into sync first

    # remove one eligible plugin's Codex manifest entirely
    _codex_path(dirs["dbt-wiki"]).unlink()

    proc = _run_all(["--check"], tmp_path)
    assert proc.returncode != 0, "missing manifest must fail --all --check"
    assert "MISSING" in proc.stderr, proc.stderr
    assert "Traceback" not in proc.stderr, "must be a clean message, not a traceback"


def test_scaffold_does_not_clobber_existing_codex(tmp_path):
    import sync_codex_manifests as m

    plugin = _build_plugin(tmp_path / "demo-plugin", _claude_ssot(), _stale_codex())
    iface_before = json.loads(_codex_path(plugin).read_text())["interface"]

    created = m.scaffold_plugin(plugin)
    assert created is False  # already exists -> not created

    after = json.loads(_codex_path(plugin).read_text(encoding="utf-8"))
    # human-authored interface preserved verbatim (not overwritten with TODOs)
    assert after["interface"] == iface_before
    # but shared fields are still brought into sync from the SSOT
    assert after["version"] == _claude_ssot()["version"]


# --- CODEX_ELIGIBLE: 21 Batch-A + loom-code; excludes hook/mcp-only plugins ----

def test_eligible_list_excludes_hook_and_mcp_plugins():
    import sync_codex_manifests as m

    batch_a = {
        "ascii-graph-toolkit", "briefing-toolkit", "copywriting-toolkit",
        "dbt-wiki", "deconstruct-toolkit", "domain-teams", "four-dx-coach",
        "gws-toolkit", "investing-toolkit", "legal-toolkit",
        "loom-interface-design", "loom-product-principles", "loom-spec",
        "obsidian", "philosophers-toolkit", "repo-wiki", "research-toolkit",
        "skill-dev-toolkit", "systems-thinking-toolkit", "translation-toolkit",
        "tsundoku",
    }
    assert len(batch_a) == 21

    eligible = set(m.CODEX_ELIGIBLE)
    assert batch_a <= eligible, batch_a - eligible
    assert "loom-code" in eligible
    assert len(eligible) == 22  # 21 Batch-A + loom-code, no duplicates

    for excluded in ("dev-workflow", "collab-toolkit", "salesforce-toolkit"):
        assert excluded not in eligible, f"{excluded} must be excluded"


# --- CLI: --scaffold creates a manifest; --all iterates; --all --check read-only

def test_cli_scaffold_creates_manifest(tmp_path):
    """`--scaffold <plugin>` over a claude-only dir creates the Codex manifest."""
    plugin = _build_claude_only(tmp_path / "demo-plugin", _claude_ssot())
    assert not _codex_path(plugin).exists()

    proc = _run(["--scaffold"], plugin)
    assert proc.returncode == 0, proc.stderr
    assert _codex_path(plugin).exists()
    written = json.loads(_codex_path(plugin).read_text(encoding="utf-8"))
    assert written["interface"]["displayName"] == "demo-plugin"


def _build_all_eligible(repo_root: Path) -> dict:
    """Build every CODEX_ELIGIBLE plugin under ``repo_root`` (stale Codex copy)."""
    import sync_codex_manifests as m

    dirs = {}
    for name in m.CODEX_ELIGIBLE:
        claude = _claude_ssot()
        claude["name"] = name
        dirs[name] = _build_plugin(repo_root / name, claude, _stale_codex())
    return dirs


def _run_all(argv, repo_root: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--all", *argv, "--repo-root", str(repo_root)],
        capture_output=True,
        text=True,
    )


def test_cli_all_iterates_and_syncs(tmp_path):
    """`--all` walks every eligible plugin under --repo-root and syncs each."""
    dirs = _build_all_eligible(tmp_path)

    proc = _run_all([], tmp_path)
    assert proc.returncode == 0, proc.stderr
    for name, plugin in dirs.items():
        written = json.loads(_codex_path(plugin).read_text(encoding="utf-8"))
        assert written["version"] == _claude_ssot()["version"], f"{name} not synced"


def test_cli_all_check_is_read_only_and_fails_on_drift(tmp_path):
    """`--all --check` is a pure read: exits non-zero on drift, mutates nothing."""
    dirs = _build_all_eligible(tmp_path)
    assert _run_all([], tmp_path).returncode == 0  # bring all into sync first

    # drift exactly one plugin's Codex shared field
    victim = dirs["dbt-wiki"]
    codex = json.loads(_codex_path(victim).read_text(encoding="utf-8"))
    codex["version"] = "9.9.9"
    _codex_path(victim).write_text(
        json.dumps(codex, indent=2) + "\n", encoding="utf-8"
    )

    before = {n: _codex_path(p).read_text(encoding="utf-8") for n, p in dirs.items()}
    proc = _run_all(["--check"], tmp_path)
    after = {n: _codex_path(p).read_text(encoding="utf-8") for n, p in dirs.items()}

    assert proc.returncode != 0, "drift in one plugin must fail --all --check"
    assert "DRIFT" in proc.stderr, proc.stderr
    assert after == before, "--all --check must be pure read (no mutation)"


# --- repo-level regression guard: the REAL committed manifests must be in sync --
# Third drift-defense layer, independent of the git hook (shift-left) and the CI
# gate. Runs against the actual committed manifests (not a tmp fixture) so the
# pytest suite alone catches any plugin whose .codex-plugin/plugin.json has
# drifted from its .claude-plugin/plugin.json SSOT.

REPO_ROOT = SCRIPT.resolve().parent.parent


def test_all_eligible_codex_manifests_in_sync():
    import sync_codex_manifests as m

    # Sanity sub-check: the eligible set is the expected 21 Batch-A + loom-code.
    assert len(m.CODEX_ELIGIBLE) == 22, f"expected 22 eligible, got {len(m.CODEX_ELIGIBLE)}"

    # Fold MISSING (no .codex-plugin manifest yet) into the offender list so a
    # future eligible plugin added before it is scaffolded fails CLEANLY (named),
    # not with a raw FileNotFoundError from sync_plugin's _load.
    offenders = []
    for name in m.CODEX_ELIGIBLE:
        plugin_dir = REPO_ROOT / name
        if not m.codex_manifest_path(plugin_dir).exists():
            offenders.append(f"{name} (MISSING .codex-plugin/plugin.json)")
        elif not m.sync_plugin(plugin_dir, check=True):
            offenders.append(name)
    assert not offenders, (
        "committed Codex manifests drifted or missing vs their Claude SSOT: "
        f"{offenders}. Run: python3 scripts/sync_codex_manifests.py --scaffold --all"
    )
