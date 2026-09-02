"""W0-05 — Codex host hooks scaffold (concept-model §7a).

Codex binds hook trust to the hook DEFINITION, not to the script content
(evidence/q4-codex-hooks-live-test.md run E). So the command string in
``.codex/hooks.json`` must be relative and version-free — otherwise every
loom upgrade rewrites the definition and costs the user another ``/hooks``
trust round. The version stamp therefore lives INSIDE the copied files.

Untrusted hooks are skipped SILENTLY in ``codex exec`` (run C), so a
scaffold write is worthless without a probe: fire a command that must be
blocked; if it is not blocked, the safety belt is absent and the scaffold
BLOCKs with a fixed message naming ``/hooks``. Fail-closed throughout.

Most cases stub the checker, because what they assert is the scaffold's own
behaviour. One case deliberately does not: the copied checker must actually
RUN inside the adopting repo -- it imports a sibling module and reads a
contract manifest, and a copy that ships neither is a hook that raises on
every command while looking, to a probe that only counts exit codes, exactly
like a working gate.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCAFFOLD = REPO / "loom-code" / "scripts" / "codex_scaffold.py"
PLUGIN_JSON = REPO / "loom-code" / ".claude-plugin" / "plugin.json"

BLOCK_MESSAGE = (
    "BLOCK: loom hooks are not trusted in this repo yet — "
    "run /hooks in Codex once, then retry"
)
GATE_BROKEN_PREFIX = "BLOCK: the loom hook ran but did not judge the push"


def version() -> str:
    return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCAFFOLD), *args],
        cwd=str(cwd or REPO),
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "adopting-repo"
    target.mkdir()
    return target


def scaffold(repo: Path) -> subprocess.CompletedProcess:
    return run("--repo", str(repo))


def stub_checker(repo: Path, exit_code: int, stderr: str = "BLOCK push.stub: no.") -> None:
    """Replace the checker copy with a stub exiting ``exit_code``, writing
    ``stderr`` first -- the probe reads the verdict, not just the code."""
    checker = repo / ".codex" / "hooks" / "loom_checker.py"
    checker.write_text(
        f"# loom-checker {version()}\nimport sys\n"
        f"sys.stderr.write({stderr!r} + chr(10))\nsys.exit({exit_code})\n",
        encoding="utf-8",
    )


def git_repo(repo: Path) -> None:
    """A one-commit git repo: the checker's push rules need a HEAD."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "seed.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "seed"], check=True)


# --- write ---------------------------------------------------------------


def test_scaffold_writes_hooks_json_and_shim(repo):
    proc = scaffold(repo)
    assert proc.returncode == 0, proc.stderr
    assert (repo / ".codex" / "hooks.json").is_file()
    shim = repo / ".codex" / "hooks" / "loom-checker"
    assert shim.is_file()
    assert shim.stat().st_mode & 0o111, "shim must be executable"


def test_command_string_is_relative_and_version_free(repo):
    scaffold(repo)
    config = json.loads((repo / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    commands = [
        hook["command"]
        for entry in config["hooks"]["PreToolUse"]
        for hook in entry["hooks"]
    ]
    assert commands == [".codex/hooks/loom-checker"]
    text = (repo / ".codex" / "hooks.json").read_text(encoding="utf-8")
    assert version() not in text
    assert "/Users/" not in text and not text.count("${")


def test_pre_tool_use_matcher_is_bash(repo):
    scaffold(repo)
    config = json.loads((repo / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    assert [e["matcher"] for e in config["hooks"]["PreToolUse"]] == ["Bash"]


def test_version_stamp_lives_inside_the_shim(repo):
    scaffold(repo)
    shim = (repo / ".codex" / "hooks" / "loom-checker").read_text(encoding="utf-8")
    assert f"# loom-checker {version()}" in shim
    assert "python3 .codex/hooks/loom_checker.py push --hook" in shim


def test_the_checker_copy_ships_its_dependencies(repo):
    """The checker imports ``git_exec`` and reads its contract manifest, so
    a lone .py copy cannot run at all."""
    scaffold(repo)
    hooks = repo / ".codex" / "hooks"
    assert (hooks / "loom_checker.py").is_file()
    assert (hooks / "git_exec.py").is_file()
    assert (hooks / "contract" / "manifest.yaml").is_file()
    assert (hooks / "contract" / "templates" / "review.json").is_file()


def test_prints_suggested_commit_subject_and_does_not_commit(repo):
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    proc = scaffold(repo)
    assert f"chore(loom): scaffold hooks {version()}" in proc.stdout
    log = subprocess.run(
        ["git", "-C", str(repo), "log", "--oneline"], capture_output=True, text=True
    )
    assert log.stdout.strip() == ""


# --- idempotence ---------------------------------------------------------


def test_rerun_at_same_version_changes_nothing(repo):
    scaffold(repo)
    before = {
        p: p.read_bytes()
        for p in sorted((repo / ".codex").rglob("*"))
        if p.is_file()
    }
    proc = scaffold(repo)
    assert proc.returncode == 0
    assert "unchanged" in proc.stdout
    after = {p: p.read_bytes() for p in sorted((repo / ".codex").rglob("*")) if p.is_file()}
    assert after == before


def test_newer_version_replaces_only_the_copies(repo):
    scaffold(repo)
    hooks_json_before = (repo / ".codex" / "hooks.json").read_bytes()
    shim = repo / ".codex" / "hooks" / "loom-checker"
    shim.write_text(
        shim.read_text(encoding="utf-8").replace(
            f"# loom-checker {version()}", "# loom-checker 0.0.1"
        ),
        encoding="utf-8",
    )
    proc = scaffold(repo)
    assert proc.returncode == 0
    assert "unchanged" not in proc.stdout
    assert f"# loom-checker {version()}" in shim.read_text(encoding="utf-8")
    assert (repo / ".codex" / "hooks.json").read_bytes() == hooks_json_before


# --- probe ---------------------------------------------------------------


def test_probe_passes_when_the_fake_push_is_blocked(repo):
    scaffold(repo)
    stub_checker(repo, 2)
    proc = run("--repo", str(repo), "--probe")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert BLOCK_MESSAGE not in proc.stdout + proc.stderr


def test_probe_reports_a_broken_gate_apart_from_an_untrusted_one(repo):
    """A checker that crashes exits non-zero too; reading that as a live
    safety belt is the exact failure the probe exists to catch."""
    scaffold(repo)
    stub_checker(repo, 1, stderr="Traceback: ModuleNotFoundError: git_exec")
    proc = run("--repo", str(repo), "--probe")
    assert proc.returncode == 2
    assert GATE_BROKEN_PREFIX in proc.stderr
    assert "git_exec" in proc.stderr
    assert BLOCK_MESSAGE not in proc.stdout + proc.stderr


def test_the_scaffolded_checker_really_blocks_a_push_end_to_end(repo):
    """No stub: the copied checker, its sibling module and its contract are
    exercised exactly as Codex would exercise them."""
    git_repo(repo)
    assert scaffold(repo).returncode == 0
    shim = repo / ".codex" / "hooks" / "loom-checker"
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git push origin HEAD"},
        "cwd": str(repo),
        "permission_mode": "default",
    }
    proc = subprocess.run(
        [str(shim)], cwd=str(repo), input=json.dumps(payload),
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert proc.stderr.lstrip().startswith("BLOCK push."), proc.stderr
    assert run("--repo", str(repo), "--probe").returncode == 0


def test_probe_blocks_when_the_fake_push_is_not_blocked(repo):
    scaffold(repo)
    stub_checker(repo, 0)
    proc = run("--repo", str(repo), "--probe")
    assert proc.returncode == 2
    assert BLOCK_MESSAGE in proc.stdout + proc.stderr


def test_probe_feeds_a_pre_tool_use_bash_payload_on_stdin(repo):
    scaffold(repo)
    checker = repo / ".codex" / "hooks" / "loom_checker.py"
    checker.write_text(
        "import json, sys\n"
        "payload = json.load(sys.stdin)\n"
        "open('payload.json', 'w').write(json.dumps(payload))\n"
        "sys.stderr.write('BLOCK push.stub: no.\\n')\n"
        "sys.exit(2)\n",
        encoding="utf-8",
    )
    proc = run("--repo", str(repo), "--probe")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads((repo / "payload.json").read_text(encoding="utf-8"))
    assert payload["hook_event_name"] == "PreToolUse"
    assert payload["tool_name"] == "Bash"
    assert "git push" in payload["tool_input"]["command"]


def test_probe_fails_closed_when_the_shim_is_missing(repo):
    proc = run("--repo", str(repo), "--probe")
    assert proc.returncode == 2


def test_fails_closed_when_the_repo_path_does_not_exist(tmp_path):
    proc = run("--repo", str(tmp_path / "nope"))
    assert proc.returncode == 2
