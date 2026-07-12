"""Tests for check_version_bump.py — the skill-content version-bump gate.

WHY this gate exists: the marketplace publishes plugins BY VERSION. A PR that
changes skill content without bumping `<plugin>/.claude-plugin/plugin.json`
`version` ships nothing — `plugin update` is a silent no-op and users keep
running the stale skill. This repo missed the bump three times (PR#539→#540,
PR#545→#546, PR#552). These tests pin the mechanical enforcement.

Fixtures build a REAL temporary git repo (init → base commit → head commit) so
the script's actual `git diff` / `git show` behavior is exercised, not a mock of
it. Plugin names are drawn from the real CODEX_ELIGIBLE tuple because that tuple
is the script's plugin registry (a naive `**/plugin.json` glob would also pick up
the root `.cursor-plugin/plugin.json`, which is not a plugin).
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check_version_bump.py"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _manifest(repo: Path, plugin: str, version: str) -> None:
    _write(
        repo,
        f"{plugin}/.claude-plugin/plugin.json",
        json.dumps({"name": plugin, "version": version}, indent=2) + "\n",
    )


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD").strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "test")
    return repo


def _run(repo: Path, base: str, head: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--base",
            base,
            "--head",
            head,
        ],
        capture_output=True,
        text=True,
    )


def test_skill_content_without_version_bump_is_a_violation(tmp_path):
    """The #552 shape: skill script changed, version left alone → must fail."""
    repo = _init_repo(tmp_path)
    _manifest(repo, "investing-toolkit", "2.5.0")
    _write(repo, "investing-toolkit/skills/data-markets/scripts/pack.py", "v1\n")
    base = _commit(repo, "base")

    _write(repo, "investing-toolkit/skills/data-markets/scripts/pack.py", "v2\n")
    head = _commit(repo, "skill change, no bump")

    result = _run(repo, base, head)

    assert result.returncode != 0
    assert "investing-toolkit" in result.stdout
    # The failure must be actionable: it names the exact fix.
    assert "investing-toolkit/.claude-plugin/plugin.json" in result.stdout
    assert "sync_codex_manifests.py investing-toolkit" in result.stdout


def test_skill_content_with_version_bump_passes(tmp_path):
    repo = _init_repo(tmp_path)
    _manifest(repo, "investing-toolkit", "2.5.0")
    _write(repo, "investing-toolkit/skills/data-markets/scripts/pack.py", "v1\n")
    base = _commit(repo, "base")

    _manifest(repo, "investing-toolkit", "2.6.0")
    _write(repo, "investing-toolkit/skills/data-markets/scripts/pack.py", "v2\n")
    head = _commit(repo, "skill change + bump")

    result = _run(repo, base, head)

    assert result.returncode == 0, result.stdout + result.stderr


def test_touching_plugin_json_without_changing_version_is_still_a_violation(tmp_path):
    """The gate checks the VERSION FIELD, not merely that plugin.json was touched."""
    repo = _init_repo(tmp_path)
    _write(
        repo,
        "obsidian/.claude-plugin/plugin.json",
        json.dumps({"name": "obsidian", "version": "1.0.0"}, indent=2) + "\n",
    )
    _write(repo, "obsidian/skills/wiki-lint/SKILL.md", "v1\n")
    base = _commit(repo, "base")

    _write(
        repo,
        "obsidian/.claude-plugin/plugin.json",
        json.dumps(
            {"name": "obsidian", "version": "1.0.0", "description": "new"}, indent=2
        )
        + "\n",
    )
    _write(repo, "obsidian/skills/wiki-lint/SKILL.md", "v2\n")
    head = _commit(repo, "skill change + plugin.json touched but version same")

    result = _run(repo, base, head)

    assert result.returncode != 0
    assert "obsidian" in result.stdout


def test_non_skill_content_change_inside_a_plugin_needs_no_bump(tmp_path):
    """CHANGELOG / tests are not skill content — they ship nothing to the marketplace."""
    repo = _init_repo(tmp_path)
    _manifest(repo, "dbt-wiki", "1.0.0")
    _write(repo, "dbt-wiki/CHANGELOG.md", "v1\n")
    _write(repo, "dbt-wiki/tests/test_thing.py", "v1\n")
    base = _commit(repo, "base")

    _write(repo, "dbt-wiki/CHANGELOG.md", "v2\n")
    _write(repo, "dbt-wiki/tests/test_thing.py", "v2\n")
    head = _commit(repo, "docs + tests only")

    result = _run(repo, base, head)

    assert result.returncode == 0, result.stdout + result.stderr


def test_hooks_agents_references_count_as_skill_content(tmp_path):
    """The gate is wider than skills/ — hooks/, agents/, references/ ship too."""
    repo = _init_repo(tmp_path)
    _manifest(repo, "loom-code", "1.0.0")
    _write(repo, "loom-code/agents/implementer.md", "v1\n")
    base = _commit(repo, "base")

    _write(repo, "loom-code/agents/implementer.md", "v2\n")
    head = _commit(repo, "agent change, no bump")

    result = _run(repo, base, head)

    assert result.returncode != 0
    assert "loom-code" in result.stdout


def test_changes_outside_any_plugin_are_a_no_op(tmp_path):
    """Root scripts/, .github/, docs/ are not plugins."""
    repo = _init_repo(tmp_path)
    _write(repo, "scripts/thing.py", "v1\n")
    _write(repo, "docs/loom/BACKLOG.md", "v1\n")
    base = _commit(repo, "base")

    _write(repo, "scripts/thing.py", "v2\n")
    _write(repo, "docs/loom/BACKLOG.md", "v2\n")
    head = _commit(repo, "repo-level only")

    result = _run(repo, base, head)

    assert result.returncode == 0, result.stdout + result.stderr


def test_multi_plugin_names_only_the_violator(tmp_path):
    repo = _init_repo(tmp_path)
    _manifest(repo, "obsidian", "1.0.0")
    _write(repo, "obsidian/skills/wiki-lint/SKILL.md", "v1\n")
    _manifest(repo, "dbt-wiki", "1.0.0")
    _write(repo, "dbt-wiki/skills/ingest/SKILL.md", "v1\n")
    base = _commit(repo, "base")

    _manifest(repo, "obsidian", "1.1.0")
    _write(repo, "obsidian/skills/wiki-lint/SKILL.md", "v2\n")
    _write(repo, "dbt-wiki/skills/ingest/SKILL.md", "v2\n")  # no bump
    head = _commit(repo, "one compliant, one violating")

    result = _run(repo, base, head)

    assert result.returncode != 0
    assert "dbt-wiki" in result.stdout
    assert "obsidian" not in result.stdout


def test_new_plugin_absent_at_base_is_not_a_violation(tmp_path):
    """A plugin's first commit has no base version to bump from."""
    repo = _init_repo(tmp_path)
    _write(repo, "README.md", "v1\n")
    base = _commit(repo, "base")

    _manifest(repo, "tsundoku", "0.1.0")
    _write(repo, "tsundoku/skills/book-extract/SKILL.md", "v1\n")
    head = _commit(repo, "brand-new plugin")

    result = _run(repo, base, head)

    assert result.returncode == 0, result.stdout + result.stderr


def test_deleted_plugin_is_not_a_violation(tmp_path):
    repo = _init_repo(tmp_path)
    _manifest(repo, "four-dx-coach", "1.0.0")
    _write(repo, "four-dx-coach/skills/coach/SKILL.md", "v1\n")
    base = _commit(repo, "base")

    _git(repo, "rm", "-r", "-q", "four-dx-coach")
    head = _commit(repo, "remove plugin")

    result = _run(repo, base, head)

    assert result.returncode == 0, result.stdout + result.stderr
