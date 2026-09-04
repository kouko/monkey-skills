"""W0-01 adversary-first probes for
2026-09-04-codex-hook-trust-covers-every-definition-and-worktree, written
before W1-01/W1-02/W1-03 exist. Every case is RED now unless its docstring
says otherwise; each names the task that should turn it green.

Attack surface, per plan.md `## 設計決定` (the ledger line format
``<hook_event_name>\\t<command>\\t<tool_name>``, the per-definition
``--trusted`` line ``<event> <matcher> <command>: fired|never|ambiguous``,
the legacy zero-byte-marker rule, and the BLOCK message naming the
absolute repo path and ``/hooks``): today's ``codex_scaffold.py`` only
knows about ONE hook definition (the loom PreToolUse Bash entry) and
answers ``--trusted`` with a single global yes/no keyed off whether
``.codex/hooks/.loom-hook-fired`` exists at all — regardless of its
content and regardless of how many OTHER definitions live in
``.codex/hooks.json``. Every case below drives a scratch repo that has
that single loom definition PLUS two PostToolUse definitions (mirroring
this repo's own hooks.json), and asks whether trust is reported per
definition or laundered through one file's mere existence.

These probes build their own hooks.json and payloads (the shape of
``codex_scaffold.PROBE_PAYLOAD``) and never invoke the real Codex binary.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# evidence/probes/test_abuse_hook_trust.py -> parents[5] is the repo root
# (probes -> evidence -> <change-id> -> loom -> docs -> repo root).
REPO = Path(__file__).resolve().parents[5]
SCAFFOLD = REPO / "loom-code" / "scripts" / "codex_scaffold.py"
PLUGIN_JSON = REPO / "loom-code" / ".claude-plugin" / "plugin.json"
CHANGELOG = REPO / "loom-code" / "CHANGELOG.md"
LOOM_CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"

CODEX_HOOKS_JSON = REPO / ".codex" / "hooks.json"
CODEX_VALIDATE_SH = REPO / ".codex" / "hooks" / "validate-skill-folder-structure.sh"
CODEX_MIRROR_SH = REPO / ".codex" / "hooks" / "remind-memory-mirror.sh"
CLAUDE_VALIDATE_SH = REPO / ".claude" / "hooks" / "validate-skill-folder-structure.sh"
CLAUDE_MIRROR_SH = REPO / ".claude" / "hooks" / "remind-memory-mirror.sh"

WRITE_PLAN_CODEX_FIRST_CONTACT = (
    REPO / "loom-code" / "skills" / "write-plan" / "references" / "codex-first-contact.md"
)
WRITE_PLAN_SKILL = REPO / "loom-code" / "skills" / "write-plan" / "SKILL.md"
BUILD_SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"

SHIM_COMMAND = ".codex/hooks/loom-checker"
VALIDATE_COMMAND = ".codex/hooks/validate-skill-folder-structure.sh"
MIRROR_COMMAND = ".codex/hooks/remind-memory-mirror.sh"
MARKER_REL = Path(".codex/hooks/.loom-hook-fired")

# Pinned in this probe as a guard (Acceptance case 7's "simpler" option) —
# re-verify with `python3 loom-code/scripts/loom_checker.py --list-rules |
# wc -l` if a later change legitimately adds/removes a rule.
LIST_RULES_LINE_COUNT = 27


def run(*args: str, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCAFFOLD), *args],
        cwd=str(cwd or REPO),
        capture_output=True,
        text=True,
        env=env,
    )


def scaffold(repo: Path) -> subprocess.CompletedProcess:
    return run("--repo", str(repo))


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "adopting-repo"
    target.mkdir()
    return target


def git_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "seed.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "seed"], check=True)


def add_posttooluse_definitions(repo: Path) -> None:
    """Add this repo's own PostToolUse Write|Edit block (two commands) to a
    scaffolded ``hooks.json``, mirroring ``.codex/hooks.json`` — the second
    and third hook definitions the whole file exists to cover."""
    hooks_json = repo / ".codex" / "hooks.json"
    config = json.loads(hooks_json.read_text(encoding="utf-8"))
    config["hooks"]["PostToolUse"] = [
        {
            "matcher": "Write|Edit",
            "hooks": [
                {"type": "command", "command": VALIDATE_COMMAND},
                {"type": "command", "command": MIRROR_COMMAND},
            ],
        }
    ]
    hooks_json.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def write_recording_stub(repo: Path, command: str) -> None:
    """A stub for one of this repo's OWN PostToolUse hooks, written the way
    W1-02's thin shim is designed to work: read stdin once, hand it to the
    future recorder, exit 0. ``loom_record_fire.py`` does not exist yet
    (that is W1-01), so today this call is a no-op that fails silently —
    which is exactly why the ledger stays empty for these two definitions
    until the implementation lands."""
    path = repo / command
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "#!/bin/bash\n"
        "set -uo pipefail\n"
        "INPUT=$(cat)\n"
        'printf \'%s\' "$INPUT" | python3 "$(dirname "$0")/loom_record_fire.py" "$0" '
        ">/dev/null 2>&1 || true\n"
        "exit 0\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def pre_tool_use_bash_payload(repo: Path) -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git push origin HEAD"},
        "cwd": str(repo),
        "permission_mode": "default",
    }


def post_tool_use_write_payload(repo: Path, file_path: str) -> dict:
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path},
        "cwd": str(repo),
        "permission_mode": "default",
    }


def fire(command_path: Path, payload: dict, cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    return subprocess.run(
        [str(command_path)],
        cwd=str(cwd),
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=full_env,
        timeout=60,
    )


# --- (1) three definitions, per-line --trusted, all-never, abs path, /hooks ---


def test_trusted_reports_every_definition_not_one_global_yes_no(repo):
    """RED until W1-01. ``.codex/hooks.json`` in this scratch repo carries
    three hook definitions (loom's PreToolUse Bash + this repo's own two
    PostToolUse Write|Edit commands). Nothing has ever fired. Today's
    ``trusted()`` only checks whether one marker FILE exists and prints a
    single global message; it has no idea the other two definitions exist
    at all. The fixed shape (plan.md `## 設計決定`) is one line per
    definition, all ``never``, a non-zero exit, and a stderr message
    carrying both ``/hooks`` and this scratch repo's own absolute path
    (never a path from some other worktree)."""
    scaffold(repo)
    add_posttooluse_definitions(repo)
    proc = run("--repo", str(repo), "--trusted")
    combined = proc.stdout + proc.stderr

    assert proc.returncode != 0, "no definition has fired — must not report trusted"
    abs_repo = str(repo.resolve())
    assert abs_repo in combined, "BLOCK message must name THIS repo's absolute path"
    assert "/hooks" in combined

    expected_lines = [
        f"PreToolUse Bash {SHIM_COMMAND}: never",
        f"PostToolUse Write|Edit {VALIDATE_COMMAND}: never",
        f"PostToolUse Write|Edit {MIRROR_COMMAND}: never",
    ]
    missing = [line for line in expected_lines if line not in combined]
    assert not missing, f"missing per-definition never lines: {missing}\n---\n{combined}"


# --- (2) scripts exist, ledger empty -> still all never (guard: existence != ran) ---


def test_scripts_existing_does_not_count_as_having_fired(repo):
    """Guard — must hold both before and after W1-01/W1-02: the hook
    scripts referenced by hooks.json are real, executable files on disk,
    but nothing has invoked them through Codex' hook engine. Existence is
    not evidence of a firing."""
    scaffold(repo)
    add_posttooluse_definitions(repo)
    write_recording_stub(repo, VALIDATE_COMMAND)
    write_recording_stub(repo, MIRROR_COMMAND)
    assert (repo / VALIDATE_COMMAND).is_file()
    assert (repo / MIRROR_COMMAND).is_file()
    assert (repo / VALIDATE_COMMAND).stat().st_mode & 0o111
    proc = run("--repo", str(repo), "--trusted")
    assert proc.returncode != 0, "scripts existing must not read as trusted"


# --- (3) firing exactly one definition flips only that one to fired ---


def test_firing_one_definition_leaves_the_others_never(repo):
    """RED until W1-01. Piping a PostToolUse payload straight into one of
    this repo's own hook commands (bypassing Codex entirely, exactly the
    way an attacker or a stray script could) must flip ONLY that
    (event, command) pair to ``fired`` — never the other two, and never a
    blanket "something fired so everything is trusted" reading. Today's
    single boolean marker cannot distinguish which of the three ran."""
    git_repo(repo)
    scaffold(repo)
    add_posttooluse_definitions(repo)
    write_recording_stub(repo, VALIDATE_COMMAND)
    write_recording_stub(repo, MIRROR_COMMAND)

    skill_file = repo / "skills" / "foo" / "SKILL.md"
    skill_file.parent.mkdir(parents=True)
    skill_file.write_text("---\nname: foo\n---\n", encoding="utf-8")
    payload = post_tool_use_write_payload(repo, str(skill_file))
    fired = fire(repo / VALIDATE_COMMAND, payload, cwd=repo)
    assert fired.returncode == 0, fired.stdout + fired.stderr

    proc = run("--repo", str(repo), "--trusted")
    combined = proc.stdout + proc.stderr
    assert f"PostToolUse Write|Edit {VALIDATE_COMMAND}: fired" in combined
    assert f"PostToolUse Write|Edit {MIRROR_COMMAND}: never" in combined
    assert f"PreToolUse Bash {SHIM_COMMAND}: never" in combined
    assert proc.returncode != 0, "one fired definition out of three is still not fully trusted"


# --- (4) LOOM_SELF_TEST=1 must never move the ledger ---


def test_self_test_env_does_not_extend_the_ledger(repo):
    """A prior real firing left one ledger line. Spawning the shim again
    with ``LOOM_SELF_TEST=1`` (the escape hatch ``--self-test`` sets, but
    which nothing stops a hostile caller from setting directly) must add
    no second line — that env var is the one thing that must make
    ``--trusted`` blind to a run, by design. Today's ledger IS the
    zero-byte marker (no line format to preserve), so this only becomes a
    meaningful assertion once W1-01 lands the line-based ledger; run now
    against today's code it exercises the marker's current
    truncate-unless-self-test behaviour, which happens to already hold —
    recorded as a guard against regressing it, not a new requirement."""
    git_repo(repo)
    scaffold(repo)
    marker = repo / MARKER_REL
    marker.parent.mkdir(parents=True, exist_ok=True)
    seeded = "PreToolUse\t.codex/hooks/loom-checker\tBash\n"
    marker.write_text(seeded, encoding="utf-8")

    shim = repo / SHIM_COMMAND
    fired = fire(shim, pre_tool_use_bash_payload(repo), cwd=repo, env={"LOOM_SELF_TEST": "1"})
    assert fired.returncode != 0  # the checker still blocks a fake push

    assert marker.read_text(encoding="utf-8") == seeded, (
        "LOOM_SELF_TEST must leave the ledger byte-for-byte unchanged"
    )


# --- (5) zero-byte legacy marker: only loom-checker counts, and only as legacy ---


def test_legacy_zero_byte_marker_only_credits_the_loom_definition(repo):
    """RED until W1-01. A pre-existing clone may carry the OLD zero-byte
    marker format from before the ledger existed. Per plan.md `## 設計決
    定` that must read as "PreToolUse Bash loom-checker fired (legacy)"
    and nothing else — the two PostToolUse definitions this repo also
    carries get no benefit of the doubt from a marker that predates them.
    Today's code reads ANY existing marker file as fully-globally-trusted
    (exit 0), which would silently vouch for hooks that have never once
    run."""
    scaffold(repo)
    add_posttooluse_definitions(repo)
    marker = repo / MARKER_REL
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_bytes(b"")  # legacy: zero bytes, no line format

    proc = run("--repo", str(repo), "--trusted")
    combined = proc.stdout + proc.stderr
    assert proc.returncode != 0, "two of three definitions have no evidence — must not be trusted"
    assert f"PostToolUse Write|Edit {VALIDATE_COMMAND}: never" in combined
    assert f"PostToolUse Write|Edit {MIRROR_COMMAND}: never" in combined
    assert "legacy" in combined.lower()
    assert f"PreToolUse Bash {SHIM_COMMAND}" in combined and "never" not in combined.split(
        f"PreToolUse Bash {SHIM_COMMAND}"
    )[1].split("\n")[0]


# --- (6) .codex/hooks.json command strings are byte-identical to main (guard) ---


def test_codex_hooks_json_commands_unchanged_from_main():
    """Guard, must stay GREEN: changing any ``command`` string in
    ``.codex/hooks.json`` invalidates every user's existing Codex trust —
    this whole change is not allowed to touch it."""
    main_text = subprocess.run(
        ["git", "show", "main:.codex/hooks.json"], cwd=str(REPO),
        capture_output=True, text=True, check=True,
    ).stdout
    main_commands = [
        hook["command"]
        for entry in json.loads(main_text)["hooks"].values()
        for block in entry
        for hook in block["hooks"]
    ]
    current = json.loads(CODEX_HOOKS_JSON.read_text(encoding="utf-8"))
    current_commands = [
        hook["command"]
        for entry in current["hooks"].values()
        for block in entry
        for hook in block["hooks"]
    ]
    assert current_commands == main_commands


# --- (7) --list-rules line count unchanged from main (guard) ---


def test_list_rules_line_count_matches_main_pin():
    """Guard, must stay GREEN: this change must not add or remove a
    checker rule. Pinned to a constant (Acceptance's "simpler" option)
    rather than shelling out to a temp copy of main's script."""
    proc = subprocess.run(
        [sys.executable, str(LOOM_CHECKER), "--list-rules"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    )
    line_count = len([line for line in proc.stdout.splitlines() if line.strip()])
    assert line_count == LIST_RULES_LINE_COUNT


# --- (8) all three station texts name per-definition / never / /hooks / stop ---


@pytest.mark.parametrize(
    "path",
    [WRITE_PLAN_CODEX_FIRST_CONTACT, WRITE_PLAN_SKILL, BUILD_SKILL],
    ids=["codex-first-contact", "write-plan-SKILL", "build-SKILL"],
)
def test_station_text_names_per_definition_never_hooks_and_stop(path):
    """RED until W1-03. Each of the three station texts must, after this
    change, describe the per-definition trust check: today none of them
    mention "definition" at all (they describe a single trust probe), so
    this is a reliable RED signal even though "/hooks" and "stop" already
    appear for the old single-probe design."""
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    assert "definition" in lower, f"{path}: no per-definition language yet"
    assert "never" in lower
    assert "/hooks" in text
    assert "stop" in lower


# --- (9) the repo's two .codex/*.sh thin shims match .claude/*.sh on real payloads ---


def test_codex_and_claude_skill_validator_agree_on_a_violation_payload(tmp_path):
    """Guard-ish, currently GREEN by luck: the comment-only drift between
    the two copies does not change behaviour for this payload. Once W1-02
    turns the .codex copy into a thin shim that also writes a ledger line,
    the extra ledger write is the only allowed difference — this case does
    not touch the ledger, so it stays a straight equality check."""
    skill_dir = tmp_path / "skills" / "foo"
    nested = skill_dir / "assets" / "scripts"
    nested.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: foo\n---\n", encoding="utf-8")
    (nested / "bad.py").write_text("# nested\n", encoding="utf-8")
    payload = post_tool_use_write_payload(tmp_path, str(skill_dir / "assets" / "SKILL.md"))

    codex_proc = fire(CODEX_VALIDATE_SH, payload, cwd=REPO)
    claude_proc = fire(CLAUDE_VALIDATE_SH, payload, cwd=REPO)
    assert codex_proc.returncode == claude_proc.returncode
    assert codex_proc.stdout == claude_proc.stdout
    assert codex_proc.stderr == claude_proc.stderr


def test_codex_and_claude_memory_mirror_reminder_agree(tmp_path):
    """RED until W1-02. This is the concrete instance of plan.md's
    documented drift: the two remind-memory-mirror.sh copies are
    byte-different today (the .codex copy still says
    ``docs/loom/backlog/``; the .claude original says
    ``docs/loom/intent/<change-id>.md``). Firing both with a payload that
    actually triggers the reminder shows that drift live in stderr, not
    just in a diff of comments — asserting equality here is what must
    hold once W1-02 turns the .codex copy into a thin shim delegating to
    the .claude original (apart from an extra ledger write, which this
    payload/env combination does not exercise either copy's stdout on)."""
    memory_dir = tmp_path / ".claude" / "projects" / "proj" / "memory"
    memory_dir.mkdir(parents=True)
    note = memory_dir / "project_thing.md"
    note.write_text("---\ntype: project\n---\nsome note\n", encoding="utf-8")
    payload = post_tool_use_write_payload(tmp_path, str(note))

    codex_proc = fire(CODEX_MIRROR_SH, payload, cwd=REPO)
    claude_proc = fire(CLAUDE_MIRROR_SH, payload, cwd=REPO)
    assert codex_proc.returncode == claude_proc.returncode == 2
    assert codex_proc.stderr == claude_proc.stderr, (
        "the two copies' reminder text has drifted — this is the RED this "
        "case exists to catch"
    )


# --- (10) ledger line format: tab-separated, relative command, no crash on bad JSON ---


def test_ledger_line_is_tab_separated_with_a_relative_command(repo):
    """RED until W1-01. plan.md `## 設計決定` fixes the line shape as
    ``<hook_event_name>\\t<command>\\t<tool_name>`` with ``command``
    computed as a path relative to the repo — never an absolute path that
    would make the ledger unshareable/non-comparable across machines.
    Today a real firing writes a zero-byte marker, not a line at all."""
    git_repo(repo)
    scaffold(repo)
    shim = repo / SHIM_COMMAND
    fired = fire(shim, pre_tool_use_bash_payload(repo), cwd=repo)
    assert fired.returncode == 2, fired.stdout + fired.stderr

    marker = repo / MARKER_REL
    assert marker.is_file()
    content = marker.read_text(encoding="utf-8")
    lines = [line for line in content.splitlines() if line]
    assert lines, "a real firing must append a ledger line, not leave the file empty"
    fields = lines[-1].split("\t")
    assert len(fields) == 3, f"expected 3 tab-separated fields, got {fields!r}"
    event, command, tool_name = fields
    assert event == "PreToolUse"
    assert command == SHIM_COMMAND, "command must be relative to the repo, not absolute"
    assert not command.startswith("/")
    assert tool_name == "Bash"


def test_ledger_write_survives_malformed_json_on_stdin(repo):
    """RED until W1-01. A hook must never crash the whole tool call just
    because the JSON on stdin was truncated or malformed (a hostile or
    buggy Codex build, a pipe that got cut) — the ledger write, if it
    cannot parse the event, must degrade to a no-op, never fatal. This
    probe feeds garbage directly at the shim and asserts the process does
    not blow up with an unhandled traceback."""
    git_repo(repo)
    scaffold(repo)
    shim = repo / SHIM_COMMAND
    proc = subprocess.run(
        [str(shim)], cwd=str(repo), input="{not json at all",
        capture_output=True, text=True, timeout=60,
    )
    assert "Traceback" not in proc.stderr
    assert "Traceback" not in proc.stdout


# --- (11) plugin.json version bumped past 1.2.3 and CHANGELOG carries it ---


def test_plugin_version_bumped_and_changelogged():
    """RED until W1-04. This whole change touches skill content
    (codex-first-contact.md, SKILL.md files) and code
    (codex_scaffold.py), which this repo's own convention requires a
    version bump and a CHANGELOG entry for."""
    version = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]
    parts = tuple(int(p) for p in version.split("."))
    assert parts > (1, 2, 3), f"plugin.json version is still {version}"
    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert f"[{version}]" in changelog, f"CHANGELOG.md has no entry for {version}"
