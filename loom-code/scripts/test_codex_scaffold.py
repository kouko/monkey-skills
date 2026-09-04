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
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCAFFOLD = REPO / "loom-code" / "scripts" / "codex_scaffold.py"
PLUGIN_JSON = REPO / "loom-code" / ".claude-plugin" / "plugin.json"

SELF_TEST_FAILED = (
    "BLOCK: the copied loom checker did not block a fake push — the scaffold "
    "is broken; re-run codex_scaffold.py --repo . and commit the result"
)
SANDBOX_PREFIX = "BLOCK: Codex' sandbox protects .codex/"
GATE_BROKEN_PREFIX = "BLOCK: the loom hook ran but did not judge the push"
SHIM_COMMAND = ".codex/hooks/loom-checker"


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
    # branch-end-02: the checker target is resolved from the shim's own
    # location ($HERE), not a cwd-relative literal path.
    assert 'TARGET="$HERE/loom_checker.py"' in shim
    assert 'exec python3 "$TARGET" push --hook' in shim


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


# --- self-test -----------------------------------------------------------


def test_self_test_passes_when_the_fake_push_is_blocked(repo):
    scaffold(repo)
    stub_checker(repo, 2)
    proc = run("--repo", str(repo), "--self-test")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert SELF_TEST_FAILED not in proc.stdout + proc.stderr


def test_self_test_reports_a_broken_gate_apart_from_a_dead_one(repo):
    """A checker that crashes exits non-zero too; reading that as a live
    safety belt is the exact failure the probe exists to catch."""
    scaffold(repo)
    stub_checker(repo, 1, stderr="Traceback: ModuleNotFoundError: git_exec")
    proc = run("--repo", str(repo), "--self-test")
    assert proc.returncode == 2
    assert GATE_BROKEN_PREFIX in proc.stderr
    assert "git_exec" in proc.stderr
    assert SELF_TEST_FAILED not in proc.stdout + proc.stderr


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
    assert run("--repo", str(repo), "--self-test").returncode == 0


def test_self_test_blocks_when_the_fake_push_is_not_blocked(repo):
    scaffold(repo)
    stub_checker(repo, 0)
    proc = run("--repo", str(repo), "--self-test")
    assert proc.returncode == 2
    assert SELF_TEST_FAILED in proc.stdout + proc.stderr


def test_self_test_feeds_a_pre_tool_use_bash_payload_on_stdin(repo):
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
    proc = run("--repo", str(repo), "--self-test")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads((repo / "payload.json").read_text(encoding="utf-8"))
    assert payload["hook_event_name"] == "PreToolUse"
    assert payload["tool_name"] == "Bash"
    assert "git push" in payload["tool_input"]["command"]


def test_self_test_fails_closed_when_the_shim_is_missing(repo):
    proc = run("--repo", str(repo), "--self-test")
    assert proc.returncode == 2


def test_fails_closed_when_the_repo_path_does_not_exist(tmp_path):
    proc = run("--repo", str(tmp_path / "nope"))
    assert proc.returncode == 2


# --- the trust marker (W4-02 finding F2) ----------------------------------


MARKER = Path(".codex") / "hooks" / ".loom-hook-fired"


def test_self_test_says_it_does_not_prove_trust(repo):
    """The old `--probe` invoked the shim itself, so Codex' trust decision
    was never in the loop, and it printed "the loom gate is live" while the
    gate was dead (W4-02 finding F2). What it really proves is that the
    copied checker runs, and it must say so."""
    scaffold(repo)
    stub_checker(repo, 2)
    proc = run("--repo", str(repo), "--self-test")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "does not prove" in proc.stdout.lower()
    assert "/hooks" in proc.stdout


def test_the_shim_leaves_a_marker_when_it_actually_runs(repo):
    """Only Codex' own hook engine can prove the hook is trusted, and it
    reports nothing when it skips one. So the shim records its own firing:
    the ledger carries a line for the loom definition if and only if the
    hook has really run here."""
    git_repo(repo)
    assert scaffold(repo).returncode == 0
    assert not (repo / MARKER).exists(), "no hook has fired yet"
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
    assert (repo / MARKER).is_file(), "the shim must record that it fired"
    lines = [line for line in (repo / MARKER).read_text(encoding="utf-8").splitlines() if line]
    assert lines[-1] == "PreToolUse\t.codex/hooks/loom-checker\tBash"


def test_shim_fired_from_a_subdirectory_still_blocks_and_records_once(repo):
    """branch-end-02 regression: both halves of the shim resolve their
    target relative to cwd. From a subdirectory, `INPUT=$(cat)` still
    works, but `python3 .codex/hooks/loom_checker.py` cannot find the
    checker and the shim used to crash there without ever recording -- or
    (the fatal half) record BEFORE that crash, so `--trusted` reports
    `fired` for a definition that never delivered a verdict. Firing from a
    subdirectory of the adopting repo must still deliver `BLOCK push.` and
    append exactly one genuine ledger line."""
    git_repo(repo)
    assert scaffold(repo).returncode == 0
    subdir = repo / "sub"
    subdir.mkdir()
    shim = repo / ".codex" / "hooks" / "loom-checker"
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git push origin HEAD"},
        "cwd": str(repo),
        "permission_mode": "default",
    }
    proc = subprocess.run(
        [str(shim)], cwd=str(subdir), input=json.dumps(payload),
        capture_output=True, text=True, timeout=60,
    )
    assert proc.stderr.lstrip().startswith("BLOCK push."), (
        f"a non-root cwd must still reach a real verdict: {proc.stdout + proc.stderr}"
    )
    assert proc.returncode == 2
    assert (repo / MARKER).is_file(), "a real verdict must record its own firing"
    lines = [line for line in (repo / MARKER).read_text(encoding="utf-8").splitlines() if line]
    assert len(lines) == 1, f"expected exactly one ledger line, got {lines!r}"
    assert lines[0] == "PreToolUse\t.codex/hooks/loom-checker\tBash"


def test_shim_records_nothing_and_blocks_when_its_checker_copy_is_missing(repo):
    """branch-end-02 regression, the other half: when the delegated target
    genuinely cannot be found (a corrupted clone, a checker copy someone
    deleted), the shim must exit non-zero WITHOUT writing a ledger line —
    recording success for a target that does not exist is the exact false
    'safe to continue' signal the finding named."""
    git_repo(repo)
    assert scaffold(repo).returncode == 0
    (repo / ".codex" / "hooks" / "loom_checker.py").unlink()
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
    assert proc.returncode != 0
    assert "cannot find its target" in proc.stderr
    assert not (repo / MARKER).exists(), "a missing target must never be recorded as fired"


def test_trusted_reports_whether_the_hook_ever_fired(repo):
    """A pre-existing zero-byte marker is the legacy ledger format: it
    credits only the loom PreToolUse Bash definition. This repo's scaffold
    defines nothing else, so crediting that one definition is enough to
    flip the whole repo trusted."""
    scaffold(repo)
    before = run("--repo", str(repo), "--trusted")
    assert before.returncode == 2
    assert f"{SHIM_COMMAND}: never" in before.stdout
    assert "/hooks" in before.stdout + before.stderr
    (repo / MARKER).write_text("", encoding="utf-8")
    after = run("--repo", str(repo), "--trusted")
    assert after.returncode == 0, after.stdout + after.stderr
    assert "fired (legacy)" in after.stdout


def test_the_marker_is_gitignored_idempotently(repo):
    scaffold(repo)
    gitignore = repo / ".gitignore"
    assert ".codex/hooks/.loom-hook-fired" in gitignore.read_text(encoding="utf-8")
    before = gitignore.read_bytes()
    assert scaffold(repo).returncode == 0
    assert gitignore.read_bytes() == before


def test_an_existing_gitignore_keeps_its_content(repo):
    gitignore = repo / ".gitignore"
    gitignore.write_text("*.pyc\n", encoding="utf-8")
    scaffold(repo)
    text = gitignore.read_text(encoding="utf-8")
    assert text.startswith("*.pyc\n")
    assert ".codex/hooks/.loom-hook-fired" in text


# --- Codex' sandbox protects .codex/ (W4-02 finding F1) -------------------


def test_a_write_protected_codex_directory_is_named_not_a_traceback(repo):
    """`--sandbox workspace-write` forbids writing `.codex/` while the rest
    of the workspace stays writable; the scaffold used to die with a bare
    errno and leave the user nowhere."""
    (repo / ".codex").mkdir()
    (repo / ".codex").chmod(0o500)
    try:
        proc = scaffold(repo)
    finally:
        (repo / ".codex").chmod(0o700)
    assert proc.returncode == 2
    assert SANDBOX_PREFIX in proc.stderr
    assert "outside Codex" in proc.stderr
    assert "Traceback" not in proc.stderr


# --- the self-test must not forge the trust marker (branch-end F2) ---------


def shim_fires(repo: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """Invoke the shim the way Codex' hook engine would: a payload on stdin
    and no self-test flag in the environment."""
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git push origin HEAD"},
        "cwd": str(repo),
        "permission_mode": "default",
    }
    return subprocess.run(
        [str(repo / ".codex" / "hooks" / "loom-checker")],
        cwd=str(repo), input=json.dumps(payload),
        capture_output=True, text=True, timeout=60, env=env,
    )


def test_self_test_leaves_no_trust_marker(repo):
    """`--self-test` spawns the shim itself, so a marker written during it
    says nothing about Codex' trust decision -- yet `--trusted` would read
    it as proof and tell the user the gate is live while it is dead."""
    scaffold(repo)
    stub_checker(repo, 2)
    assert run("--repo", str(repo), "--self-test").returncode == 0
    assert not (repo / MARKER).exists(), "the self-test must not forge the marker"
    assert run("--repo", str(repo), "--trusted").returncode == 2


def test_self_test_keeps_a_marker_it_did_not_create(repo):
    """Belt and braces cuts one way only: a marker from a real firing is
    evidence, and the self-test must not destroy it."""
    scaffold(repo)
    stub_checker(repo, 2)
    (repo / MARKER).write_text("", encoding="utf-8")
    assert run("--repo", str(repo), "--self-test").returncode == 0
    assert (repo / MARKER).is_file()


def test_a_real_firing_still_marks_the_repo_trusted(repo):
    """The other side of the same fence: without the self-test flag the
    shim records its firing, which is the only trust evidence there is."""
    git_repo(repo)
    assert scaffold(repo).returncode == 0
    assert shim_fires(repo).returncode == 2
    assert run("--repo", str(repo), "--trusted").returncode == 0


# --- a non-executable shim is its own dead end (branch-end F4) -------------


NOT_EXECUTABLE_PREFIX = "BLOCK: the loom hook shim is not executable"


def test_a_non_executable_shim_is_named_not_read_as_the_sandbox(repo):
    """Spawning a shim without +x raises EACCES, which the CLI's sandbox
    branch used to translate into "Codex' sandbox protects .codex/" -- a
    door that is not the one the user is standing in front of."""
    scaffold(repo)
    (repo / ".codex" / "hooks" / "loom-checker").chmod(0o644)
    proc = run("--repo", str(repo), "--self-test")
    assert proc.returncode == 2
    assert NOT_EXECUTABLE_PREFIX in proc.stderr
    assert "chmod +x" in proc.stderr
    assert SANDBOX_PREFIX not in proc.stderr
    assert "Traceback" not in proc.stderr


def test_a_shim_that_lost_its_executable_bit_is_repaired(repo):
    """Content-identical is not the same as installed: a shim that cannot
    be executed is a dead gate, so `unchanged` would be a lie."""
    scaffold(repo)
    shim = repo / ".codex" / "hooks" / "loom-checker"
    shim.chmod(0o644)
    proc = scaffold(repo)
    assert proc.returncode == 0, proc.stderr
    assert "repaired mode" in proc.stdout
    assert "unchanged" not in proc.stdout
    assert shim.stat().st_mode & 0o111
    assert "unchanged" in scaffold(repo).stdout


# --- hooks.json merge (R22-O2) --------------------------------------------


def test_an_existing_hooks_json_block_survives_a_scaffold_run(repo):
    """PRINCIPLES.md non-negotiable 5: existing data is never rewritten
    without asking. A repo's own PostToolUse hooks must survive, with
    loom's PreToolUse Bash entry added alongside them."""
    hooks_dir = repo / ".codex"
    hooks_dir.mkdir(parents=True)
    existing = {
        "hooks": {
            "PostToolUse": [
                {"matcher": "Write", "hooks": [{"type": "command", "command": "echo hi"}]}
            ]
        }
    }
    (hooks_dir / "hooks.json").write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    proc = scaffold(repo)
    assert proc.returncode == 0, proc.stderr
    config = json.loads((hooks_dir / "hooks.json").read_text(encoding="utf-8"))
    assert config["hooks"]["PostToolUse"] == existing["hooks"]["PostToolUse"]
    pre = config["hooks"]["PreToolUse"]
    commands = [hook["command"] for entry in pre for hook in entry["hooks"]]
    assert commands.count(".codex/hooks/loom-checker") == 1


def test_rerunning_scaffold_on_a_merged_hooks_json_is_idempotent(repo):
    hooks_dir = repo / ".codex"
    hooks_dir.mkdir(parents=True)
    existing = {
        "hooks": {
            "PostToolUse": [
                {"matcher": "Write", "hooks": [{"type": "command", "command": "echo hi"}]}
            ]
        }
    }
    (hooks_dir / "hooks.json").write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    scaffold(repo)
    proc = scaffold(repo)
    assert proc.returncode == 0, proc.stderr
    assert "unchanged" in proc.stdout


def test_unparseable_hooks_json_stops_the_scaffold_untouched(repo):
    hooks_dir = repo / ".codex"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "hooks.json").write_text("{not json", encoding="utf-8")
    proc = scaffold(repo)
    assert proc.returncode == 2
    assert "hooks.json" in proc.stderr
    assert "Traceback" not in proc.stderr
    assert (hooks_dir / "hooks.json").read_text(encoding="utf-8") == "{not json"


# --- per-definition trust ledger (W1-01) -----------------------------------


def test_trusted_reports_one_line_per_hooks_json_definition(repo):
    scaffold(repo)
    proc = run("--repo", str(repo), "--trusted")
    assert f"PreToolUse Bash {SHIM_COMMAND}: never" in proc.stdout


def test_trusted_marks_a_command_shared_by_two_matchers_ambiguous(repo):
    """Two matchers pointing at the same (event, command) pair cannot be
    told apart by a ledger line, so neither counts as fired — the ledger
    would have no way to say which matcher's firing it was evidence of."""
    scaffold(repo)
    hooks_json = repo / ".codex" / "hooks.json"
    config = json.loads(hooks_json.read_text(encoding="utf-8"))
    config["hooks"]["PreToolUse"].append(
        {"matcher": "Write", "hooks": [{"type": "command", "command": SHIM_COMMAND}]}
    )
    hooks_json.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    proc = run("--repo", str(repo), "--trusted")
    combined = proc.stdout + proc.stderr
    assert f"PreToolUse Bash {SHIM_COMMAND}: ambiguous" in combined
    assert f"PreToolUse Write {SHIM_COMMAND}: ambiguous" in combined
    assert proc.returncode != 0


def test_recorder_ignores_malformed_stdin_without_raising(repo):
    scaffold(repo)
    recorder = repo / ".codex" / "hooks" / "loom_record_fire.py"
    assert recorder.is_file()
    proc = subprocess.run(
        [sys.executable, str(recorder), str(repo / SHIM_COMMAND)],
        cwd=str(repo), input="not json", capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr
    assert not (repo / MARKER).exists()


def test_recorder_ignores_a_missing_hook_path_argument(repo):
    scaffold(repo)
    recorder = repo / ".codex" / "hooks" / "loom_record_fire.py"
    proc = subprocess.run(
        [sys.executable, str(recorder)],
        cwd=str(repo),
        input=json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash"}),
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr
    assert not (repo / MARKER).exists()


def test_recorder_writes_nothing_under_loom_self_test(repo):
    scaffold(repo)
    recorder = repo / ".codex" / "hooks" / "loom_record_fire.py"
    payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash"})
    proc = subprocess.run(
        [sys.executable, str(recorder), str(repo / SHIM_COMMAND)],
        cwd=str(repo), input=payload, capture_output=True, text=True, timeout=30,
        env=dict(os.environ, LOOM_SELF_TEST="1"),
    )
    assert proc.returncode == 0
    assert not (repo / MARKER).exists()
