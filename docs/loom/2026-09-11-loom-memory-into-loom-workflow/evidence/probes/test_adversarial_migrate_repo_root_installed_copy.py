"""Adversarial probe (surface 2): `migrate_legacy_store.py`'s repo-root default
after the relocation added a directory level.

`migrate_legacy_store.py` used to compute its own repo root as
`Path(__file__).resolve().parent.parents[3]` (via `SCRIPTS_DIR.parents[3]`),
which was only correct when the script's own containing directories were
exactly `.../<repo-root>/loom-workflow/skills/loom-memory/scripts/`. That is
true in this git checkout, but this repo's OWN test suite
(`scripts/test_check_plugin_boundaries.py::
test_manifest_name_identifies_plugin_inside_versioned_install_root`) proves
plugins are also installed one level deeper, under a version directory
(`.../loom-workflow/<version>/skills/loom-memory/scripts/`). Run from that
shape without an explicit `--repo-root`, the old default silently resolved
to the WRONG ancestor (the plugin's own install directory, not the project
repo that owns the `docs/loom/memory` store being migrated), and `migrate()`
reached `store.relative_to(repo_root)` unconditionally once
`is_legacy_store(store)` was true, raising an uncaught `ValueError` — main()
only caught `MigrationError`. A one-shot, explicitly-invoked migration
command that is supposed to fail with a clear `FAIL — ...` message instead
exited via a raw Python traceback.

The fix replaces the fixed hop count with `_discover_repo_root`, which walks
upward from the STORE path (not the script's own location) for the nearest
`.git` — correct in any install layout, because the store always lives in
the caller's project repo, never inside the plugin's own tree. `migrate()`
also now turns a residual `store.relative_to(repo_root)` mismatch (e.g. an
explicit `--repo-root` that does not actually contain the store) into a
`MigrationError` naming both paths instead of crashing.

Run:
    PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
        docs/loom/2026-09-11-loom-memory-into-loom-workflow/evidence/probes/test_adversarial_migrate_repo_root_installed_copy.py -v
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
REAL_SCRIPTS_DIR = REPO_ROOT / "loom-workflow" / "skills" / "loom-memory" / "scripts"


def _install_layout_copy(dest_scripts_dir: Path) -> Path:
    """Reproduce the versioned-install layout this repo's own boundary-checker
    suite asserts is real: `<plugin>/<version>/skills/loom-memory/scripts/`."""
    dest_scripts_dir.mkdir(parents=True, exist_ok=True)
    for name in ("migrate_legacy_store.py", "loom_memory.py"):
        shutil.copy2(REAL_SCRIPTS_DIR / name, dest_scripts_dir / name)
    return dest_scripts_dir


def _legacy_store(store_dir: Path) -> Path:
    store_dir.mkdir(parents=True, exist_ok=True)
    (store_dir / "README.md").write_text(
        "---\n"
        "name: README\n"
        "description: legacy store guide\n"
        "type: Memory Store Guide\n"
        "---\n"
        "## Index\n"
        "- [foo](foo.md) — a lesson\n",
        encoding="utf-8",
    )
    (store_dir / "foo.md").write_text(
        "---\n"
        "name: foo\n"
        "description: a legacy lesson\n"
        "type: Memory\n"
        "origin: some origin\n"
        "---\n"
        "Body text here.\n",
        encoding="utf-8",
    )
    return store_dir


def test_migrate_legacy_store_installed_layout_without_repo_root_flag_fails_cleanly_instead_of_crashing(
    tmp_path,
):
    """Reproduces the plugin's own documented installed shape
    (`<plugin>/<version>/skills/...`) with a genuinely legacy store that
    lives OUTSIDE that install tree (as any real project's `docs/loom/
    memory/` would, relative to a plugin cache) AND outside any git
    repository at all. No `--repo-root` is passed — the documented CLI
    usage in the script's own docstring
    (`migrate_legacy_store.py <store> [--repo-root PATH]`) treats it as
    optional.

    `_discover_repo_root` walks upward from the STORE path (not the
    script's install depth) looking for `.git`; when none exists anywhere
    above the store, it raises `MigrationError` naming the store path,
    which `main()` already catches and reports as a clean
    `migrate_legacy_store: FAIL — ...` line — never a raw traceback."""
    scripts_dir = _install_layout_copy(
        tmp_path / "plugins" / "loom-workflow" / "9.9.9" / "skills" / "loom-memory" / "scripts"
    )
    store = _legacy_store(tmp_path / "project" / "docs" / "loom" / "memory")

    result = subprocess.run(
        [sys.executable, str(scripts_dir / "migrate_legacy_store.py"), str(store)],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"},
    )

    # The fix: exit 1 with a "migrate_legacy_store: FAIL — ..." message on
    # stdout naming the store, and no traceback on stderr at all.
    assert result.returncode != 0
    assert "migrate_legacy_store: FAIL —" in result.stdout, result.stdout
    assert str(store) in result.stdout
    assert "Traceback (most recent call last)" not in result.stderr, result.stderr
    assert "ValueError" not in result.stderr


def test_migrate_legacy_store_installed_layout_without_repo_root_flag_still_migrates_when_the_project_has_git(
    tmp_path,
):
    """The realistic success case the old fixed-hop-count default could
    never reach correctly: the script installed in the versioned layout,
    the store in a SEPARATE real project repo (with its own `.git`), and
    no `--repo-root` passed. `_discover_repo_root` finds the project's
    `.git` by walking up from the store path itself, so migration succeeds
    without ever needing to know how deep the script itself is installed."""
    scripts_dir = _install_layout_copy(
        tmp_path / "plugins" / "loom-workflow" / "9.9.9" / "skills" / "loom-memory" / "scripts"
    )
    project_root = tmp_path / "project"
    store = _legacy_store(project_root / "docs" / "loom" / "memory")
    subprocess.run(["git", "init", "-q"], cwd=project_root, check=True)
    subprocess.run(["git", "config", "user.email", "a@b.c"], cwd=project_root, check=True)
    subprocess.run(["git", "config", "user.name", "tester"], cwd=project_root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=project_root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=project_root, check=True)

    result = subprocess.run(
        [sys.executable, str(scripts_dir / "migrate_legacy_store.py"), str(store)],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 0, result.stderr
    assert "migrated 1 lesson concept" in result.stdout


def test_migrate_legacy_store_installed_layout_with_explicit_repo_root_still_works(tmp_path):
    """Control: the same installed-layout script, given the correct
    `--repo-root` explicitly, still migrates cleanly — proving the fixed
    default computation above did not regress the explicit-flag path."""
    scripts_dir = _install_layout_copy(
        tmp_path / "plugins" / "loom-workflow" / "9.9.9" / "skills" / "loom-memory" / "scripts"
    )
    project_root = tmp_path / "project"
    store = _legacy_store(project_root / "docs" / "loom" / "memory")
    # introducing_commit() shells out to `git log` in repo_root; give it a
    # real (trivial) git repo so that call succeeds rather than masking the
    # result with an unrelated git failure.
    subprocess.run(["git", "init", "-q"], cwd=project_root, check=True)
    subprocess.run(["git", "config", "user.email", "a@b.c"], cwd=project_root, check=True)
    subprocess.run(["git", "config", "user.name", "tester"], cwd=project_root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=project_root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=project_root, check=True)

    result = subprocess.run(
        [
            sys.executable,
            str(scripts_dir / "migrate_legacy_store.py"),
            str(store),
            "--repo-root",
            str(project_root),
        ],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 0, result.stderr
    assert "migrated 1 lesson concept" in result.stdout
