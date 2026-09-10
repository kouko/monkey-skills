"""Adversarial probe (surface 2): `migrate_legacy_store.py`'s `REPO_ROOT_DEFAULT`
after the relocation added a directory level.

`migrate_legacy_store.py` computes its own repo root as
`Path(__file__).resolve().parent.parents[3]` (via `SCRIPTS_DIR.parents[3]`),
which is only correct when the script's own containing directories are
exactly `.../<repo-root>/loom-workflow/skills/loom-memory/scripts/`. That is
true in this git checkout, but this repo's OWN test suite
(`scripts/test_check_plugin_boundaries.py::
test_manifest_name_identifies_plugin_inside_versioned_install_root`) proves
plugins are also installed one level deeper, under a version directory
(`.../loom-workflow/<version>/skills/loom-memory/scripts/`). Run from that
shape without an explicit `--repo-root`, the default silently resolves to
the WRONG ancestor (the plugin's own install directory, not the project
repo that owns the `docs/loom/memory` store being migrated), and the code
path has no guard for it: `migrate()` reaches `store.relative_to(repo_root)`
unconditionally once `is_legacy_store(store)` is true, and that raises an
uncaught `ValueError` — main() only catches `MigrationError`. A one-shot,
explicitly-invoked migration command that is supposed to fail with a clear
`FAIL — ...` message instead exits via a raw Python traceback.

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


def test_migrate_legacy_store_installed_layout_without_repo_root_flag_crashes_instead_of_failing_cleanly(
    tmp_path,
):
    """Reproduces the plugin's own documented installed shape
    (`<plugin>/<version>/skills/...`) with a genuinely legacy store that
    lives OUTSIDE that install tree (as any real project's `docs/loom/
    memory/` would, relative to a plugin cache). No `--repo-root` is
    passed — the documented CLI usage in the script's own docstring
    (`migrate_legacy_store.py <store> [--repo-root PATH]`) treats it as
    optional."""
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

    # The documented, graceful failure mode is exit 1 with a
    # "migrate_legacy_store: FAIL — ..." message on stdout (see
    # `main()`'s `except MigrationError` branch). What actually happens is
    # an unhandled `ValueError` traceback on stderr — a defect this probe
    # pins so a fix (catching it, or computing repo_root correctly) is
    # provable.
    assert result.returncode != 0
    assert "FAIL" not in result.stdout, (
        "expected the documented clean-failure message to be ABSENT, "
        "proving the crash bypasses it entirely"
    )
    assert "Traceback (most recent call last)" in result.stderr
    assert "ValueError" in result.stderr
    assert "relative_to" in result.stderr


def test_migrate_legacy_store_installed_layout_with_explicit_repo_root_still_works(tmp_path):
    """Control: the same installed-layout script, given the correct
    `--repo-root` explicitly, migrates cleanly — proving the defect above
    is specifically the *default* computation, not the script generally."""
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
