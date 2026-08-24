"""Regression coverage for the standalone review-context resolver."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _consumer_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "consumer"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "review@example.test")
    _git(repo, "config", "user.name", "Review Context Test")
    (repo / "README.md").write_text("# Consumer\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "initial")
    return repo


def _make_review_scope_escape(plugin_root: Path, outside: Path) -> None:
    review_scope = plugin_root / "scripts" / "review_scope.py"
    review_scope.unlink()
    review_scope.symlink_to(outside)


def test_context_uses_script_parent_not_consumer_repo(tmp_path: Path) -> None:
    """A copied standalone plugin must not look for consumer/loom-code."""
    installed_root = tmp_path / "plugin-cache" / "loom-code" / "0.98.0"
    installed_root.parent.mkdir(parents=True)
    shutil.copytree(PLUGIN_ROOT, installed_root)
    consumer = _consumer_repo(tmp_path)
    assert not (consumer / "loom-code").exists()

    result = subprocess.run(
        [
            sys.executable,
            str(installed_root / "scripts" / "review_context.py"),
            "--repo",
            str(consumer),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    context = json.loads(result.stdout)

    assert context["target_repo"] == str(consumer.resolve())
    assert context["reviewed_sha"] == _git(consumer, "rev-parse", "HEAD")
    assert context["plugin_version"] == "0.98.0"
    assert context["resources"]
    for resource in context["resources"].values():
        resource_path = Path(resource)
        assert resource_path.is_absolute()
        assert resource_path.is_file()
        assert resource_path.is_relative_to(installed_root)


def test_context_refuses_damaged_or_escaping_installed_resources(
    tmp_path: Path,
) -> None:
    """A review packet must not approve missing or out-of-plugin resources."""
    consumer = _consumer_repo(tmp_path)
    for name, damage in (
        ("missing", lambda root: (root / "agents" / "code-reviewer.md").unlink()),
        (
            "escaping",
            lambda root: _make_review_scope_escape(
                root, tmp_path / "outside-plugin.py"
            ),
        ),
    ):
        installed_root = tmp_path / name / "loom-code" / "0.98.0"
        installed_root.parent.mkdir(parents=True)
        shutil.copytree(PLUGIN_ROOT, installed_root)
        (tmp_path / "outside-plugin.py").write_text("# outside\n", encoding="utf-8")
        damage(installed_root)

        result = subprocess.run(
            [
                sys.executable,
                str(installed_root / "scripts" / "review_context.py"),
                "--repo",
                str(consumer),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Traceback" not in result.stderr
        assert "review-context: refused" in result.stderr
