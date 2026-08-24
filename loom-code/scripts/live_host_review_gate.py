#!/usr/bin/env python3
"""Fail-closed, disposable real-host release gate for loom-code.

The normal test suite calls this module with a fake host runner.  ``main``
uses the real Claude Code and Codex CLIs, but only after building a temporary
plugin copy, a temporary consumer git fixture, and a temporary CODEX_HOME.
No auth is discovered implicitly: callers supply a private Codex auth file,
while Claude uses the named, preauthenticated ``~/.claude-test`` profile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence

from review_context import RESOURCE_RELATIVE_PATHS


HOSTS = ("claude", "codex")
STATIONS = ("CODE", "DOCS", "MIXED", "SDD")
VALID_CASES = tuple(f"valid-{station.lower()}" for station in STATIONS)
CASES = (*VALID_CASES, "invalid-reference", "unchanged-post-fix")
FORBIDDEN_REFUSAL_OUTPUT = (
    "review_context.py",
    "check_doc_citations.py",
    "review_scope.py",
    "loom_gate_markers.py",
    "live_gate_station_receipt.py",
    "wrapper",
    "marker",
)
STATION_SKILLS = {
    "CODE": "requesting-code-review",
    "DOCS": "requesting-docs-review",
    "MIXED": "requesting-code-review",
    "SDD": "subagent-driven-development",
}
ADAPTER_REFUSALS = {
    "invalid-reference": {
        "type": "loom.live-gate.adapter-refusal",
        "case": "invalid-reference",
        "reason": "loaded-reference-path-not-absolute",
    },
    "unchanged-post-fix": {
        "type": "loom.live-gate.adapter-refusal",
        "case": "unchanged-post-fix",
        "reason": "post-fix-sha-unchanged",
    },
}
RECEIPT_ARGUMENTS = (
    "python3",
    "$LOOM_LIVE_GATE_PLUGIN_ROOT/scripts/live_gate_station_receipt.py",
    "--packet",
    "$LOOM_LIVE_GATE_PACKET",
    "--plugin-root",
    "$LOOM_LIVE_GATE_PLUGIN_ROOT",
    "--marker-dir",
    "$LOOM_LIVE_GATE_MARKER_DIR",
    "--repo",
    "$LOOM_LIVE_GATE_REPO",
    "--station",
    "{station}",
    "--nonce",
    "$LOOM_LIVE_GATE_NONCE",
)


@dataclass(frozen=True)
class HostResult:
    host: str
    case: str
    command: tuple[str, ...]
    output: str
    returncode: int
    marker_files_before: tuple[str, ...] = ()
    marker_files_after: tuple[str, ...] = ()


@dataclass
class Workspace:
    temporary_root: Path
    candidate_root: Path
    consumer_root: Path
    marker_directory: Path
    packet_directory: Path
    claude_config_source: Path
    claude_config_dir: Path
    codex_home: Path
    codex_auth_target: Path
    reviewed_sha: str
    host_roots: dict[str, Path] = field(default_factory=dict)
    host_versions: dict[str, str] = field(default_factory=dict)
    host_packets: dict[str, dict[str, object]] = field(default_factory=dict)
    # JSONL-shaped audit events emitted by this runner for the one resolver
    # subprocess per host.  They are joined with host JSON events at validation
    # time; this avoids asking every station session to rebuild the packet.
    host_packet_events: dict[str, str] = field(default_factory=dict)
    host_packet_paths: dict[str, Path] = field(default_factory=dict)
    host_nonces: dict[tuple[str, str], str] = field(default_factory=dict)

    def expected_root(self, host: str) -> Path:
        return self.host_roots.get(host, self.candidate_root)


HostRunner = Callable[[Workspace, str, str], HostResult]


def _path_has_symlink_component(path: Path) -> bool:
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        if current.is_symlink():
            return True
    return False


def _canonical_claude_config_path(path: Path) -> Path:
    """Canonicalize only macOS's root-owned ``/tmp`` system alias."""

    lexical = path.absolute()
    system_tmp = Path("/tmp")
    canonical_tmp = Path("/private/tmp")
    try:
        system_alias = (
            lexical.parent == system_tmp
            and not lexical.is_symlink()
            and system_tmp.is_symlink()
            and system_tmp.lstat().st_uid == 0
            and system_tmp.resolve(strict=True) == canonical_tmp
        )
        if system_alias:
            canonical = lexical.resolve(strict=True)
            if canonical.parent == canonical_tmp and canonical.name == lexical.name:
                return canonical
        if _path_has_symlink_component(lexical):
            raise ValueError("claude config path and ancestors must not be symlinks")
    except OSError as error:
        raise ValueError("claude config path could not be validated") from error
    return lexical


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return completed.stdout.strip()


def _make_consumer(root: Path) -> tuple[Path, str]:
    upstream = root / "upstream"
    upstream.mkdir()
    _git(upstream, "init", "-q", "-b", "main")
    _git(upstream, "config", "user.email", "gate@example.test")
    _git(upstream, "config", "user.name", "Live Host Gate")
    (upstream / "README.md").write_text("# Gate fixture\n", encoding="utf-8")
    _git(upstream, "add", "README.md")
    _git(upstream, "commit", "-qm", "base")

    consumer = root / "consumer"
    subprocess.run(["git", "clone", "-q", str(upstream), str(consumer)], check=True, timeout=20)
    _git(consumer, "config", "user.email", "gate@example.test")
    _git(consumer, "config", "user.name", "Live Host Gate")
    _git(consumer, "checkout", "-qb", "review-gate")
    (consumer / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    (consumer / "review.md").write_text("# Review artifact\n", encoding="utf-8")
    _git(consumer, "add", "feature.py", "review.md")
    _git(consumer, "commit", "-qm", "reviewable mixed change")
    return consumer, _git(consumer, "rev-parse", "HEAD")


def _make_read_only(path: Path, writable: Path | None = None) -> None:
    """Remove write bits from a tree, then restore one explicit exception."""

    for descendant in sorted(path.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if descendant.is_symlink():
            continue
        mode = descendant.stat().st_mode
        descendant.chmod(mode & ~0o222)
    mode = path.stat().st_mode
    path.chmod(mode & ~0o222)
    if writable is not None:
        writable.mkdir(parents=True, exist_ok=True)
        writable.chmod(0o700)


def _claude_test_profile() -> Path:
    """Return the one Claude profile this release gate is permitted to use."""

    return Path.home() / ".claude-test"


def create_workspace(
    candidate: Path, auth_source: Path, claude_config_dir: Path | None = None
) -> Workspace:
    candidate = candidate.resolve()
    auth_source = auth_source.resolve()
    expected_claude_config = _claude_test_profile().absolute()
    if claude_config_dir is not None and claude_config_dir.absolute() != expected_claude_config:
        raise ValueError("Claude live gate uses only the named ~/.claude-test profile")
    claude_config_lexical = expected_claude_config
    claude_config_source = _canonical_claude_config_path(claude_config_lexical)
    if not candidate.is_dir() or not (candidate / "scripts/review_context.py").is_file():
        raise ValueError("candidate must be a loom-code root containing scripts/review_context.py")
    if not auth_source.is_file() or auth_source.stat().st_mode & 0o077:
        raise ValueError("codex auth source must be an existing private regular file")
    if not claude_config_source.is_dir():
        raise ValueError("claude config dir must be an existing directory")

    temporary_root = Path(tempfile.mkdtemp(prefix="loom-live-host-")).resolve()
    copied_root = temporary_root / "candidate" / "loom-code"
    copied_root.parent.mkdir(parents=True)
    shutil.copytree(candidate, copied_root, symlinks=True)
    consumer, reviewed_sha = _make_consumer(temporary_root)
    marker = consumer / ".git" / "loom"
    marker.mkdir(parents=True)
    packet_directory = temporary_root / "packets"
    packet_directory.mkdir(mode=0o700)
    codex_home = temporary_root / "codex-home"
    codex_home.mkdir(mode=0o700)
    auth_target = codex_home / "auth.json"
    # This copies bytes only into a private disposable root.  Never inspect,
    # hash, serialize, or report the authentication material.
    shutil.copyfile(auth_source, auth_target)
    auth_target.chmod(0o600)
    # The named profile is intentionally persistent: it owns the Claude Max
    # login and its own mutable cache, while daily ~/.claude remains watched.
    claude_config_dir = claude_config_lexical
    _make_read_only(copied_root)
    _make_read_only(consumer, marker)
    return Workspace(
        temporary_root=temporary_root,
        candidate_root=copied_root,
        consumer_root=consumer,
        marker_directory=marker,
        packet_directory=packet_directory,
        claude_config_source=claude_config_source,
        claude_config_dir=claude_config_dir,
        codex_home=codex_home,
        codex_auth_target=auth_target,
        reviewed_sha=reviewed_sha,
    )


def cleanup_workspace(workspace: Workspace) -> None:
    # The temporary root is owned by this runner.  Make it writable first so
    # readonly fixture permissions cannot prevent the finally cleanup.
    for path in sorted(workspace.temporary_root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if not path.is_symlink():
            try:
                path.chmod(path.stat().st_mode | stat.S_IWUSR)
            except FileNotFoundError:
                pass
    workspace.temporary_root.chmod(workspace.temporary_root.stat().st_mode | stat.S_IWUSR)
    shutil.rmtree(workspace.temporary_root, ignore_errors=False)


def _lock_fixture_parents(workspace: Workspace) -> None:
    """Close parent-directory rename/delete paths after setup is complete."""

    locked = {
        workspace.temporary_root,
        workspace.candidate_root.parent,
        workspace.consumer_root,
        workspace.consumer_root / ".git",
        workspace.packet_directory,
        *(workspace.expected_root(host).parent for host in workspace.host_roots),
    }
    for path in locked:
        path.chmod(path.stat().st_mode & ~0o222)
    workspace.marker_directory.chmod(0o700)


def _redacted_evidence(output: str, workspace: Workspace) -> str:
    """Render only fixed, value-checked evidence labels from untrusted host text."""

    candidate_lines = {
        f"CANDIDATE_ROOT: {workspace.expected_root(host)}": "CANDIDATE_ROOT: [CANDIDATE_PLUGIN]"
        for host in HOSTS
    }
    candidate_lines[f"REVIEWED_SHA: {workspace.reviewed_sha}"] = (
        f"REVIEWED_SHA: {workspace.reviewed_sha}"
    )
    candidate_lines["PACKET_SOURCE: scripts/review_context.py"] = (
        "PACKET_SOURCE: scripts/review_context.py"
    )
    for station in STATIONS:
        candidate_lines[f"HOST_SKILL_INVOKED: {station}"] = f"HOST_SKILL_INVOKED: {station}"
        for host in HOSTS:
            candidate_lines[
                f"{station}_STATION_PACKET: {workspace.expected_root(host)} {workspace.reviewed_sha}"
            ] = f"{station}_STATION_PACKET: [CANDIDATE_PLUGIN] {workspace.reviewed_sha}"

    strings: list[str] = list(output.splitlines())
    for event in _json_events(output):
        def walk(value: object) -> None:
            if isinstance(value, str):
                strings.extend(value.splitlines())
            elif isinstance(value, dict):
                for nested in value.values():
                    walk(nested)
            elif isinstance(value, list):
                for nested in value:
                    walk(nested)
        walk(event)

    evidence: list[str] = []
    runner_categories = {
        "api-overloaded": "HOST_ERROR: API_OVERLOADED",
        "timeout": "HOST_ERROR: TIMEOUT",
        "spawn-not-found": "HOST_ERROR: SPAWN_NOT_FOUND",
        "spawn-permission-denied": "HOST_ERROR: SPAWN_PERMISSION_DENIED",
        "spawn-os-error": "HOST_ERROR: SPAWN_OS_ERROR",
    }
    for event in _json_events(output):
        if event.get("type") == "runner.error":
            category = event.get("category")
            if isinstance(category, str) and category in runner_categories:
                evidence.append(runner_categories[category])
    for raw in strings:
        cleaned = raw.strip()
        if cleaned in candidate_lines:
            evidence.append(candidate_lines[cleaned])
        elif cleaned.startswith("REFUSE:"):
            evidence.append("REFUSE: recorded")
    if not evidence:
        evidence.append("[no redacted host evidence emitted]")
    return "\n".join(dict.fromkeys(evidence))


def _state_fingerprint(path: Path, label: str) -> tuple[object, ...]:
    """Return a non-reportable integrity record for one protected path."""

    try:
        link_data = path.lstat()
    except FileNotFoundError:
        return (label, "missing")
    record: list[object] = [
        label, "link", link_data.st_mode, link_data.st_ino, link_data.st_dev,
        link_data.st_ctime_ns, link_data.st_mtime_ns, link_data.st_size,
    ]
    try:
        data = path.stat()
    except OSError as error:
        return (*record, "target-error", type(error).__name__)
    record.extend((
        "target", data.st_mode, data.st_ino, data.st_dev, data.st_ctime_ns,
        data.st_mtime_ns, data.st_size,
    ))
    if stat.S_ISREG(data.st_mode):
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(64 * 1024), b""):
                digest.update(block)
        record.extend(("sha256", digest.digest()))
    return tuple(record)


def _protected_plugin_metadata(root: Path) -> tuple[Path, ...]:
    """Return plugin state files and manifests, never runtime cache payloads."""

    candidates = {
        root / name
        for name in ("installed_plugins.json", "known_marketplaces.json", "blocklist.json")
    }
    if not root.exists():
        return tuple(sorted(candidates))
    for path in root.rglob("plugin.json"):
        if ".claude-plugin" in path.parts or ".codex-plugin" in path.parts:
            candidates.add(path)
    return tuple(sorted(candidates))


def _snapshot_user_state() -> tuple[tuple[object, ...], ...]:
    """Inventory daily configuration and plugin metadata without contents.

    A SHA-256 digest is retained only in process memory for protected regular
    files and is never written to the report. It protects the durable release
    boundary (configuration, Codex auth, and plugin installations) while
    excluding ordinary session, log, and cache activity that desktop hosts
    update independently. The named ``.claude-test`` profile is outside this
    inventory.
    """

    home = Path.home()
    monitored_paths = [
        home / ".claude" / "settings.json",
        home / ".claude" / "settings.local.json",
        home / ".codex" / "config.toml",
        home / ".codex" / "auth.json",
    ]
    monitored_paths.extend(_protected_plugin_metadata(home / ".claude" / "plugins"))
    monitored_paths.extend(_protected_plugin_metadata(home / ".codex" / "plugins"))
    snapshot: list[tuple[object, ...]] = []
    for path in sorted(set(monitored_paths)):
        snapshot.append(_state_fingerprint(path, str(path.relative_to(home))))
    return tuple(snapshot)


def _snapshot_metadata(root: Path) -> tuple[tuple[str, int, int], ...]:
    """Content-blind snapshot for a caller-owned disposable auth directory."""

    entries: list[tuple[str, int, int]] = []
    for path in sorted(root.rglob("*")):
        data = path.lstat()
        entries.append((str(path.relative_to(root)), data.st_mtime_ns, data.st_size))
    return tuple(entries)


def receipt_command(station: str) -> str:
    """Return the one shell command station prose and live validation share."""

    if station not in STATIONS:
        raise ValueError(f"unknown station: {station}")
    arguments = tuple(value.format(station=station) for value in RECEIPT_ARGUMENTS)
    return " ".join(
        f'"{value}"' if value.startswith("$") else value for value in arguments
    )


def expected_receipt_argv(station: str) -> tuple[str, ...]:
    return tuple(shlex.split(receipt_command(station)))


def expected_adapter_probe_argv(
    workspace: Workspace, host: str, case: str
) -> tuple[str, ...]:
    script = str(workspace.expected_root(host) / "scripts/live_gate_adapter_probe.py")
    if case == "invalid-reference":
        reference_name = (
            "claude-code-tools.md" if host == "claude" else "codex-tools.md"
        )
        return (
            "python3",
            script,
            "loaded-reference",
            "--host",
            host,
            "--loaded-reference-path",
            f"relative/{reference_name}",
        )
    if case == "unchanged-post-fix":
        return (
            "python3",
            script,
            "post-fix-sha",
            "--initial-sha",
            workspace.reviewed_sha,
            "--post-fix-sha",
            workspace.reviewed_sha,
        )
    raise ValueError(f"case has no adapter probe: {case}")


def adapter_probe_command(workspace: Workspace, host: str, case: str) -> str:
    return shlex.join(expected_adapter_probe_argv(workspace, host, case))


def _skill_read_instruction(host: str, skill_path: Path) -> str:
    if host == "claude":
        return f"Claude: use one Read tool call whose file_path is exactly {skill_path}."
    return f"Codex: execute exactly `cat {shlex.quote(str(skill_path))}` once to read the skill."


def _prompt(workspace: Workspace, host: str, case: str, root: Path) -> str:
    packet = workspace.host_packets.get(host)
    if case.startswith("valid-"):
        station = case.removeprefix("valid-").upper()
        skill = STATION_SKILLS[station]
        command = f"/loom-code:{skill}"
        read_instruction = _skill_read_instruction(
            host, root / "skills" / skill / "SKILL.md"
        )
        return f"""{command}
Run the installed loom-code live release probe.
The candidate plugin itself must not be edited. Fixture-only artifacts are allowed.
The opening slash command above is mandatory: invoke that loaded candidate station, do not merely read or quote its SKILL.md.
This is a gate-only route probe, not a downstream whole review. Do not dispatch reviewers. Do not run exploratory commands.
Your first tool call must be the exact candidate SKILL Read described below. Your second tool call must be the exact gate command shown below. Make no other tool calls.
This is the {station} station case. The loaded {host} reference root is: {root}
The target consumer repo is: {workspace.consumer_root}
The runner already resolved this canonical packet once; consume it verbatim and do not run another resolver:
{json.dumps(packet, sort_keys=True) if packet else '[MISSING_CANONICAL_PACKET]'}
{read_instruction}
After consuming that exact packet, execute this receipt command exactly once, with no agent-added wrapper, redirection, prefix, suffix, or substitution. Codex may record its fixed `/bin/zsh -lc` transport; the validator accepts only that host-emitted wrapper:
`{receipt_command(station)}`
Do not run review_context.py in this session. Return ONLY these evidence lines,
with actual values from the executed packet and station:
CANDIDATE_ROOT: <absolute root used>
REVIEWED_SHA: <packet reviewed_sha>
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: {station}
{station}_STATION_PACKET: <root> <sha>
"""
    if case == "invalid-reference":
        skill_path = root / "skills" / STATION_SKILLS["CODE"] / "SKILL.md"
        return f"""/loom-code:requesting-code-review
{_skill_read_instruction(host, skill_path)}
This is a gate-only route probe. Do not dispatch reviewers. Do not run exploratory commands.
Your first tool call must be the exact candidate SKILL Read described above. Your second tool call must be the exact gate command shown below. Make no other tool calls.
Execute this adapter probe command exactly once, with no agent-added wrapper, redirection, prefix, suffix, or substitution. Codex may record its fixed `/bin/zsh -lc` transport; the validator accepts only that host-emitted wrapper:
`{adapter_probe_command(workspace, host, case)}`
Its deliberately relative loaded-reference input must produce the typed candidate refusal. REFUSE before any review_context, citation, scope, marker, receipt, or downstream wrapper command. Return exactly one line starting `REFUSE:` and no other text."""
    skill_path = root / "skills" / STATION_SKILLS["DOCS"] / "SKILL.md"
    return f"""/loom-code:requesting-docs-review
{_skill_read_instruction(host, skill_path)}
This is a gate-only route probe. Do not dispatch reviewers. Do not run exploratory commands.
Your first tool call must be the exact candidate SKILL Read described above. Your second tool call must be the exact gate command shown below. Make no other tool calls.
Execute this adapter probe command exactly once, with no agent-added wrapper, redirection, prefix, suffix, or substitution. Codex may record its fixed `/bin/zsh -lc` transport; the validator accepts only that host-emitted wrapper:
`{adapter_probe_command(workspace, host, case)}`
Its initial SHA equals post-fix SHA ({workspace.reviewed_sha}) and must produce the typed candidate refusal. REFUSE before any review_context, citation, scope, marker, receipt, or downstream wrapper command. Return exactly one line starting `REFUSE:` and no other text."""


def _run(command: Sequence[str], *, cwd: Path, env: dict[str, str] | None = None) -> tuple[int, str]:
    try:
        result = subprocess.run(
            list(command), cwd=cwd, env=env, capture_output=True, text=True, timeout=180
        )
    except subprocess.TimeoutExpired as error:
        fragments: list[str] = []
        for value in (error.stdout, error.stderr):
            if isinstance(value, bytes):
                fragments.append(value.decode("utf-8", errors="replace"))
            elif isinstance(value, str):
                fragments.append(value)
        partial = "\n".join(fragments)
        overloaded = any(
            event.get("type") == "system"
            and event.get("subtype") == "api_retry"
            and event.get("error_status") == 529
            and event.get("error") == "overloaded"
            for event in _json_events(partial)
        )
        category = "api-overloaded" if overloaded else "timeout"
        return 124, json.dumps({"type": "runner.error", "category": category})
    except OSError as error:
        if isinstance(error, FileNotFoundError):
            category = "spawn-not-found"
        elif isinstance(error, PermissionError):
            category = "spawn-permission-denied"
        else:
            category = "spawn-os-error"
        return 127, json.dumps({"type": "runner.error", "category": category})
    return result.returncode, (result.stdout + result.stderr)


def host_argv_for_case(workspace: Workspace, host: str, case: str) -> tuple[str, ...]:
    """The exact real-host argv, kept separately so tests lock the safety flags."""

    root = workspace.expected_root(host)
    prompt = _prompt(workspace, host, case, root)
    if host == "claude":
        if case.startswith("valid-"):
            station = case.removeprefix("valid-").upper()
            gate_command = receipt_command(station)
        else:
            station = "CODE" if case == "invalid-reference" else "DOCS"
            gate_command = adapter_probe_command(workspace, host, case)
        skill_path = _station_skill_path(root, station)
        return (
            "claude", "-p", "--verbose", "--no-session-persistence", "--plugin-dir", str(root),
            "--tools", "Read,Bash",
            "--allowedTools", f"Read({skill_path})", f"Bash({gate_command})",
            "--permission-mode", "bypassPermissions", "--output-format", "stream-json", prompt,
        )
    return (
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
        "--sandbox", "workspace-write", "--skip-git-repo-check",
        "-C", str(workspace.marker_directory), "--json", prompt,
    )


def _json_events(output: str) -> tuple[dict[str, object], ...]:
    events: list[dict[str, object]] = []
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return tuple(events)


def _event_command_strings(output: str, host: str) -> tuple[str, ...]:
    """Extract only actual host command tool events, never arbitrary JSON keys."""

    commands: list[str] = []
    for event in _json_events(output):
        if host == "claude" and event.get("type") == "assistant":
            message = event.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_use" or item.get("name") != "Bash":
                    continue
                inputs = item.get("input")
                command = inputs.get("command") if isinstance(inputs, dict) else None
                if isinstance(command, str):
                    commands.append(command)
        elif host == "codex" and event.get("type") == "item.completed":
            item = event.get("item")
            if not isinstance(item, dict) or item.get("type") != "command_execution":
                continue
            command = item.get("command")
            if isinstance(command, str):
                commands.append(command)
    return tuple(commands)


def _parse_host_command_argv(command: str, host: str) -> tuple[str, ...] | None:
    """Parse one structured command event under the host's exact contract."""

    try:
        argv = tuple(shlex.split(command))
    except ValueError:
        return None
    if len(argv) == 3 and argv[1] == "-lc" and argv[0].startswith("/bin/"):
        if host != "codex" or argv[0] != "/bin/zsh":
            return None
        try:
            argv = tuple(shlex.split(argv[2]))
        except ValueError:
            return None
    # Shell operators are not argv.  Reject their presence so a matching
    # prefix plus an injected suffix cannot count as the exact command.
    if any(token in {"&&", "||", ";", "|", ">", ">>", "<"} for token in argv):
        return None
    return argv


def _event_command_argvs(output: str, host: str) -> tuple[tuple[str, ...], ...]:
    parsed: list[tuple[str, ...]] = []
    for command in _event_command_strings(output, host):
        argv = _parse_host_command_argv(command, host)
        if argv is not None:
            parsed.append(argv)
    return tuple(parsed)


def _event_tool_sequence(
    output: str, host: str
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return every ordered host tool invocation, including invalid extras."""

    sequence: list[tuple[str, tuple[str, ...]]] = []
    for event in _json_events(output):
        if host == "claude" and event.get("type") == "assistant":
            message = event.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_use":
                    continue
                name = item.get("name")
                inputs = item.get("input")
                if name == "Read" and isinstance(inputs, dict):
                    path = inputs.get("file_path")
                    if isinstance(path, str):
                        sequence.append(("read", (path,)))
                        continue
                if name == "Bash" and isinstance(inputs, dict):
                    command = inputs.get("command")
                    argv = (
                        _parse_host_command_argv(command, host)
                        if isinstance(command, str)
                        else None
                    )
                    if argv is not None:
                        sequence.append(("command", argv))
                        continue
                label = name if isinstance(name, str) else "malformed"
                sequence.append(("other", (label,)))
        elif host == "codex" and event.get("type") == "item.completed":
            item = event.get("item")
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            if item_type == "command_execution":
                command = item.get("command")
                argv = (
                    _parse_host_command_argv(command, host)
                    if isinstance(command, str)
                    else None
                )
                if argv is not None:
                    sequence.append(("command", argv))
                else:
                    sequence.append(("other", ("command_execution",)))
            elif item_type not in {"agent_message", "reasoning", "todo_list"}:
                label = item_type if isinstance(item_type, str) else "malformed"
                sequence.append(("other", (label,)))
    return tuple(sequence)


def _event_commands(output: str) -> tuple[str, ...]:
    """Compatibility view used only for the runner's own resolver audit event."""

    commands: list[str] = []
    for event in _json_events(output):
        if event.get("type") != "runner.command_execution":
            continue
        argv = event.get("argv")
        if isinstance(argv, list) and all(isinstance(value, str) for value in argv):
            commands.append(" ".join(argv))
    return tuple(commands)


def _event_has_typed_adapter_refusal(
    output: str,
    host: str,
    expected_argv: tuple[str, ...],
    expected: dict[str, str],
) -> bool:
    """Accept an exact typed refusal only from a real command-result field."""

    candidates: list[str] = []
    claude_probe_ids: set[str] = set()
    events = _json_events(output)
    if host == "claude":
        for event in events:
            if event.get("type") != "assistant":
                continue
            message = event.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_use" or item.get("name") != "Bash":
                    continue
                inputs = item.get("input")
                command = inputs.get("command") if isinstance(inputs, dict) else None
                identifier = item.get("id")
                if not isinstance(command, str) or not isinstance(identifier, str):
                    continue
                if _event_command_argvs(json.dumps(event), host) == (expected_argv,):
                    claude_probe_ids.add(identifier)
    for event in events:
        if host == "claude" and event.get("type") == "user":
            message = event.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_result":
                    continue
                if item.get("tool_use_id") not in claude_probe_ids:
                    continue
                value = item.get("content")
                if isinstance(value, str):
                    candidates.extend(value.splitlines())
        elif host == "codex" and event.get("type") == "item.completed":
            item = event.get("item")
            if not isinstance(item, dict) or item.get("type") != "command_execution":
                continue
            if _event_command_argvs(json.dumps(event), host) != (expected_argv,):
                continue
            value = item.get("aggregated_output")
            if isinstance(value, str):
                candidates.extend(value.splitlines())
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if parsed == expected:
            return True
    return False


def _event_loaded_candidate_skill(output: str, host: str, expected_path: Path) -> bool:
    """Require host JSON evidence that a candidate station skill was actually read."""

    expected = str(expected_path)
    for event in _json_events(output):
        if host == "claude" and event.get("type") == "assistant":
            message = event.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_use" or item.get("name") != "Read":
                    continue
                inputs = item.get("input")
                if isinstance(inputs, dict) and inputs.get("file_path") == expected:
                    return True
        elif host == "codex":
            if ("cat", expected) in _event_command_argvs(json.dumps(event), "codex"):
                return True
    return False


def _station_skill_path(root: Path, station: str) -> Path:
    return root / "skills" / STATION_SKILLS[station] / "SKILL.md"


def _canonical_packet(workspace: Workspace, host: str) -> str | None:
    if host in workspace.host_packets:
        return None
    root = workspace.expected_root(host)
    command = (sys.executable, str(root / "scripts/review_context.py"), "--repo", str(workspace.consumer_root))
    code, output = _run(command, cwd=workspace.consumer_root)
    if code:
        return f"{host}: canonical packet resolver failed"
    try:
        packet = json.loads(output)
    except json.JSONDecodeError:
        return f"{host}: canonical packet was not JSON"
    if not isinstance(packet, dict) or set(packet) != {
        "target_repo", "reviewed_sha", "plugin_version", "resources"
    }:
        return f"{host}: canonical packet schema mismatch"
    if packet.get("target_repo") != str(workspace.consumer_root) or packet.get("reviewed_sha") != workspace.reviewed_sha:
        return f"{host}: canonical packet target or SHA mismatch"
    try:
        manifest_version = json.loads(
            (root / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )["version"]
    except (OSError, json.JSONDecodeError, KeyError):
        return f"{host}: candidate manifest unavailable"
    if packet.get("plugin_version") != manifest_version:
        return f"{host}: canonical packet version mismatch"
    resources = packet.get("resources")
    if not isinstance(resources, dict) or set(resources) != set(RESOURCE_RELATIVE_PATHS):
        return f"{host}: canonical packet resource schema mismatch"
    for name, relative in RESOURCE_RELATIVE_PATHS.items():
        expected = (root / relative).resolve()
        resource = resources.get(name)
        if not isinstance(resource, str) or Path(resource) != expected or not expected.is_file():
            return f"{host}: canonical packet resource mismatch: {name}"
    workspace.host_packets[host] = packet
    packet_path = workspace.packet_directory / f"{host}-packet.json"
    packet_path.write_text(json.dumps(packet, sort_keys=True), encoding="utf-8")
    packet_path.chmod(0o400)
    workspace.host_packet_paths[host] = packet_path
    for case in VALID_CASES:
        workspace.host_nonces[(host, case)] = secrets.token_hex(16)
    # Preserve the executed command as structured evidence, not as prose
    # supplied by a station response.  This is deliberately one event per
    # host: all four station sessions consume this already validated packet.
    workspace.host_packet_events[host] = json.dumps(
        {"type": "runner.command_execution", "argv": list(command), "exit_code": 0}
    )
    return None


def check_claude_auth(
    config_dir: Path | None = None,
    *,
    command_runner: Callable[..., tuple[int, str]] = _run,
) -> str | None:
    """Check the named Claude test profile without reading its contents."""

    expected = _claude_test_profile().absolute()
    if config_dir is not None and config_dir.absolute() != expected:
        return "Claude live gate uses only the named ~/.claude-test profile"
    lexical_config_dir = expected
    try:
        canonical_config_dir = _canonical_claude_config_path(lexical_config_dir)
    except ValueError as error:
        if "symlink" in str(error):
            return "Claude config path contains symlink"
        return "Claude config path could not be validated"
    if not canonical_config_dir.is_dir():
        return "Claude config directory is unavailable"
    env = os.environ.copy()
    env["CLAUDE_CONFIG_DIR"] = str(lexical_config_dir)
    code, _ = command_runner(("claude", "auth", "status", "--text"), cwd=Path.cwd(), env=env)
    return None if code == 0 else "Claude auth status failed"


def _cli_version(command: tuple[str, ...], *, env: dict[str, str] | None = None) -> str:
    code, output = _run(command, cwd=Path.cwd(), env=env)
    if code:
        return "unavailable"
    first_line = output.strip().splitlines()
    return _safe_version(first_line[0]) if first_line else "unavailable"


def _safe_version(value: str) -> str:
    """Permit only ordinary one-line version text in a committed report."""

    return value if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._()+-]{0,95}", value) else "unavailable"


def _safe_report_error(error: str) -> str:
    """Map internal failures to a closed report vocabulary."""

    match = re.fullmatch(r"(claude|codex)/([^:]+): (.+)", error)
    if match:
        host, case, detail = match.groups()
        reasons = (
            ("cli exited ", "CLI exit"),
            ("missing ", "missing evidence"),
            ("receipt content mismatch", "receipt mismatch"),
            ("station re-ran handed packet resolver", "resolver rerun"),
            ("marker directory changed outside one receipt", "marker side effect"),
            ("refusal ", "refusal side effect"),
            ("did not refuse", "missing refusal"),
        )
        for prefix, label in reasons:
            if detail.startswith(prefix):
                return f"{host}/{case}: {label}"
        return f"{host}/{case}: validation failed"
    if re.fullmatch(r"(claude|codex): canonical packet .+", error):
        return error.split(":", 1)[0] + ": canonical packet validation failed"
    fixed = {
        "Claude auth status failed",
        "protected daily state changed during live probe",
        "codex/install: failed",
    }
    if error in fixed:
        return error
    if error.startswith("temporary cleanup failed:"):
        return "temporary cleanup failed"
    return "internal gate failure (details withheld)"


def _marketplace_for(workspace: Workspace) -> Path:
    marketplace = workspace.temporary_root / "marketplace"
    shutil.copytree(workspace.candidate_root, marketplace / "loom-code", symlinks=True)
    manifest_dir = marketplace / ".claude-plugin"
    manifest_dir.mkdir()
    (manifest_dir / "marketplace.json").write_text(
        json.dumps({"name": "live-host-gate", "owner": {"name": "fixture"}, "plugins": [{"name": "loom-code", "source": "./loom-code/"}]}),
        encoding="utf-8",
    )
    return marketplace


def _legacy_marketplace_for(workspace: Workspace) -> Path:
    """Build a disposable pre-resolver marketplace for the upgrade probe."""

    marketplace = workspace.temporary_root / "legacy-marketplace"
    legacy_root = marketplace / "loom-code"
    shutil.copytree(workspace.candidate_root, legacy_root, symlinks=True)
    legacy_root.chmod(0o755)
    scripts = legacy_root / "scripts"
    scripts.chmod(0o755)
    (scripts / "review_context.py").unlink()
    manifest_dir = marketplace / ".claude-plugin"
    manifest_dir.mkdir()
    (manifest_dir / "marketplace.json").write_text(
        json.dumps({"name": "legacy-live-host-gate", "owner": {"name": "fixture"}, "plugins": [{"name": "loom-code", "source": "./loom-code/"}]}),
        encoding="utf-8",
    )
    return marketplace


def _find_codex_plugin_root(workspace: Workspace) -> Path | None:
    candidates = []
    for manifest in workspace.codex_home.rglob("plugin.json"):
        if manifest.parent.name != ".codex-plugin":
            continue
        try:
            if json.loads(manifest.read_text(encoding="utf-8")).get("name") == "loom-code":
                candidates.append(manifest.parent.parent.resolve())
        except (OSError, json.JSONDecodeError):
            continue
    return candidates[0] if len(candidates) == 1 else None


def _prepare_codex(workspace: Workspace) -> tuple[bool, str]:
    marketplace = _marketplace_for(workspace)
    legacy_marketplace = _legacy_marketplace_for(workspace)
    env = os.environ.copy()
    env["CODEX_HOME"] = str(workspace.codex_home)
    legacy_commands = (
        ("codex", "plugin", "marketplace", "add", str(legacy_marketplace)),
        ("codex", "plugin", "add", "loom-code@legacy-live-host-gate"),
    )
    for command in legacy_commands:
        code, output = _run(command, cwd=workspace.consumer_root, env=env)
        if code:
            return False, output
    legacy_root = _find_codex_plugin_root(workspace)
    if legacy_root is None or (legacy_root / "scripts/review_context.py").exists():
        return False, "Codex legacy install was not the expected pre-resolver version"
    code, output = _run(
        ("codex", "plugin", "remove", "loom-code@legacy-live-host-gate"),
        cwd=workspace.consumer_root,
        env=env,
    )
    if code:
        return False, output
    candidate_commands = (
        ("codex", "plugin", "marketplace", "add", str(marketplace)),
        ("codex", "plugin", "add", "loom-code@live-host-gate"),
    )
    for command in candidate_commands:
        code, output = _run(command, cwd=workspace.consumer_root, env=env)
        if code:
            return False, output
    installed_root = _find_codex_plugin_root(workspace)
    if installed_root is None or not (installed_root / "scripts/review_context.py").is_file():
        return False, "Codex installed candidate root could not be resolved"
    workspace.host_roots["codex"] = installed_root
    _make_read_only(installed_root)
    return True, ""


def _real_host_runner(workspace: Workspace, host: str, case: str) -> HostResult:
    command = host_argv_for_case(workspace, host, case)
    before = tuple(sorted(path.name for path in workspace.marker_directory.iterdir()))
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("LOOM_LIVE_GATE_")
    }
    if host == "claude":
        # This is the sole Claude override. HOME must remain untouched because
        # the named profile's account credentials are stored by the host user.
        env["CLAUDE_CONFIG_DIR"] = str(workspace.claude_config_dir)
        if case.startswith("valid-"):
            env.update({"LOOM_LIVE_GATE_PACKET": str(workspace.host_packet_paths[host]), "LOOM_LIVE_GATE_MARKER_DIR": str(workspace.marker_directory), "LOOM_LIVE_GATE_NONCE": workspace.host_nonces[(host, case)], "LOOM_LIVE_GATE_PLUGIN_ROOT": str(workspace.expected_root(host)), "LOOM_LIVE_GATE_REPO": str(workspace.consumer_root)})
        code, output = _run(command, cwd=workspace.consumer_root, env=env)
        after = tuple(sorted(path.name for path in workspace.marker_directory.iterdir()))
        return HostResult(host, case, command, output, code, before, after)

    env["CODEX_HOME"] = str(workspace.codex_home)
    if case.startswith("valid-"):
        env.update({"LOOM_LIVE_GATE_PACKET": str(workspace.host_packet_paths[host]), "LOOM_LIVE_GATE_MARKER_DIR": str(workspace.marker_directory), "LOOM_LIVE_GATE_NONCE": workspace.host_nonces[(host, case)], "LOOM_LIVE_GATE_PLUGIN_ROOT": str(workspace.expected_root(host)), "LOOM_LIVE_GATE_REPO": str(workspace.consumer_root)})
    code, output = _run(command, cwd=workspace.consumer_root, env=env)
    after = tuple(sorted(path.name for path in workspace.marker_directory.iterdir()))
    return HostResult(host, case, command, output, code, before, after)


def _validate_valid_host_result(workspace: Workspace, result: HostResult) -> list[str]:
    errors: list[str] = []
    if not result.case.startswith("valid-"):
        return errors
    output = result.output
    station = result.case.removeprefix("valid-").upper()
    root = str(workspace.expected_root(result.host))
    required = (
        f"CANDIDATE_ROOT: {root}", f"REVIEWED_SHA: {workspace.reviewed_sha}",
        "PACKET_SOURCE: scripts/review_context.py", f"HOST_SKILL_INVOKED: {station}",
        f"{station}_STATION_PACKET: {root} {workspace.reviewed_sha}",
    )
    for item in required:
        if item not in output:
            errors.append(f"{result.host}/valid: missing {item}")
    resolver = str(workspace.expected_root(result.host) / "scripts/review_context.py")
    event_commands = _event_command_strings(output, result.host)
    event_argvs = _event_command_argvs(output, result.host)
    resolver_events = _event_commands(workspace.host_packet_events.get(result.host, ""))
    if not event_commands:
        errors.append(f"{result.host}/{result.case}: missing host JSON tool event")
    expected_skill = _station_skill_path(workspace.expected_root(result.host), station)
    if not _event_loaded_candidate_skill(output, result.host, expected_skill):
        errors.append(f"{result.host}/{result.case}: missing candidate station skill tool event")
    expected_sequence = (("read", (str(expected_skill),)), ("command", expected_receipt_argv(station))) if result.host == "claude" else (("command", ("cat", str(expected_skill))), ("command", expected_receipt_argv(station)))
    if _event_tool_sequence(output, result.host) != expected_sequence:
        errors.append(f"{result.host}/{result.case}: exact gate tool sequence mismatch")
    if result.host in workspace.host_packets:
        nonce = workspace.host_nonces[(result.host, result.case)]
        receipt = workspace.marker_directory / f"{station}-{nonce}.json"
        try:
            data = json.loads(receipt.read_text(encoding="utf-8"))
            packet = workspace.host_packets[result.host]
            packet_digest = hashlib.sha256((json.dumps(packet, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")).hexdigest()
            if data != {"station": station, "nonce": nonce, "reviewed_sha": workspace.reviewed_sha, "plugin_root": root, "target_repo": str(workspace.consumer_root), "packet_sha256": packet_digest}:
                errors.append(f"{result.host}/{result.case}: receipt content mismatch")
        except (OSError, json.JSONDecodeError):
            errors.append(f"{result.host}/{result.case}: missing station receipt")
        expected_files = tuple(sorted((*result.marker_files_before, receipt.name)))
        if result.marker_files_after and result.marker_files_after != expected_files:
            errors.append(f"{result.host}/{result.case}: marker directory changed outside one receipt")
    if result.host in workspace.host_packets and not any(resolver in command for command in resolver_events):
        errors.append(f"{result.host}/{result.case}: missing candidate resolver tool event")
    if any("review_context.py" in token for argv in event_argvs for token in argv):
        errors.append(f"{result.host}/{result.case}: station re-ran handed packet resolver")
    receipt_argvs = tuple(argv for argv in event_argvs if any("live_gate_station_receipt.py" in token for token in argv))
    if receipt_argvs != (expected_receipt_argv(station),):
        errors.append(f"{result.host}/{result.case}: missing exact station receipt command event")
    expected_slash = f"/loom-code:{STATION_SKILLS[station]}\n"
    if not result.command or not result.command[-1].startswith(expected_slash):
        errors.append(f"{result.host}/{result.case}: missing native station slash invocation")
    return errors


def _validate_refusal_host_result(workspace: Workspace, result: HostResult) -> list[str]:
    errors: list[str] = []
    output = result.output
    if "REFUSE:" not in output:
        errors.append(f"{result.host}/{result.case}: did not refuse")
    refusal_station = "CODE" if result.case == "invalid-reference" else "DOCS"
    refusal_skill = _station_skill_path(workspace.expected_root(result.host), refusal_station)
    if not _event_loaded_candidate_skill(output, result.host, refusal_skill):
        errors.append(f"{result.host}/{result.case}: missing candidate refusal skill tool event")
    expected_probe = expected_adapter_probe_argv(workspace, result.host, result.case)
    probe_argvs = tuple(argv for argv in _event_command_argvs(output, result.host) if any("live_gate_adapter_probe.py" in token for token in argv))
    if probe_argvs != (expected_probe,):
        errors.append(f"{result.host}/{result.case}: missing exact adapter probe command event")
    if not _event_has_typed_adapter_refusal(output, result.host, expected_probe, ADAPTER_REFUSALS[result.case]):
        errors.append(f"{result.host}/{result.case}: missing typed adapter refusal event")
    expected_slash = f"/loom-code:{STATION_SKILLS[refusal_station]}\n"
    if not result.command or not result.command[-1].startswith(expected_slash):
        errors.append(f"{result.host}/{result.case}: missing native refusal slash invocation")
    if any(any(token in command.lower() for token in FORBIDDEN_REFUSAL_OUTPUT) for command in _event_command_strings(output, result.host)):
        errors.append(f"{result.host}/{result.case}: refusal performed forbidden downstream work")
    if result.marker_files_after != result.marker_files_before:
        errors.append(f"{result.host}/{result.case}: refusal changed marker directory")
    return errors


def validate_host_result(workspace: Workspace, result: HostResult) -> list[str]:
    if result.returncode != 0:
        return [f"{result.host}/{result.case}: cli exited {result.returncode}"]
    if result.case.startswith("valid-"):
        return _validate_valid_host_result(workspace, result)
    return _validate_refusal_host_result(workspace, result)


def _render_report(
    *, workspace: Workspace, results: Sequence[HostResult], errors: Sequence[str],
    user_state_unchanged: bool, cleanup_ok: bool,
    claude_sandbox_changed: bool = False,
) -> str:
    status = "PASS" if not errors and user_state_unchanged and cleanup_ok else "FAIL"
    lines = [
        "# Cross-host review-gate live-host run",
        "",
        f"status: {status}",
        "candidate root: [CANDIDATE_PLUGIN]",
        f"consumer SHA: {workspace.reviewed_sha}",
        "cli versions: Claude Code=" + _safe_version(workspace.host_versions.get("claude", "not-probed"))
        + "; Codex=" + _safe_version(workspace.host_versions.get("codex", "not-probed")),
        "authentication: caller-supplied private Codex file is copied only into disposable CODEX_HOME; Claude uses only the named ~/.claude-test profile.",
        f"protected daily state: {'unchanged' if user_state_unchanged else 'CHANGED'}",
        "Claude test-profile metadata: " + ("CHANGED (expected dedicated profile)" if claude_sandbox_changed else "unchanged"),
        f"finally cleanup: {'PASS' if cleanup_ok else 'FAIL'}",
        "",
        "## Cases",
    ]
    for result in results:
        lines += [
            f"### {result.host} / {result.case}",
            f"command: {result.host} session invocation [REDACTED_ARGUMENTS]",
            f"exit: {result.returncode}",
            "output:",
            "```text",
            _redacted_evidence(result.output, workspace).rstrip(),
            "```",
        ]
    if errors:
        safe_errors = tuple(dict.fromkeys(_safe_report_error(error) for error in errors))
        lines += ["", "## Failures", *[f"- {error}" for error in safe_errors]]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, host_runner: HostRunner | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--codex-auth-source", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        workspace = create_workspace(args.candidate, args.codex_auth_source)
    except ValueError as error:
        print(f"live-host gate: refused: {error}", file=sys.stderr)
        return 2
    results: list[HostResult] = []
    errors: list[str] = []
    cleanup_ok = False
    before_state: tuple[tuple[object, ...], ...] = ()
    before_state_ok = True
    try:
        before_state = _snapshot_user_state()
    except OSError:
        before_state_ok = False
        errors.append("protected daily state snapshot failed")
    before_claude_config = _snapshot_metadata(workspace.claude_config_source)
    try:
        runner = host_runner or _real_host_runner
        if host_runner is None:
            auth_failure = check_claude_auth(workspace.claude_config_dir)
            if auth_failure:
                errors.append(auth_failure)
            else:
                claude_env = os.environ.copy()
                claude_env["CLAUDE_CONFIG_DIR"] = str(workspace.claude_config_dir)
                workspace.host_versions["claude"] = _cli_version(("claude", "--version"), env=claude_env)
                workspace.host_versions["codex"] = _cli_version(("codex", "--version"))
                prepared, _detail = _prepare_codex(workspace)
                if not prepared:
                    errors.append("codex/install: failed")
                else:
                    for host in HOSTS:
                        packet_error = _canonical_packet(workspace, host)
                        if packet_error:
                            errors.append(packet_error)
                    if not errors:
                        _lock_fixture_parents(workspace)
        else:
            # Deterministic test runners use the same copied candidate for both
            # adapters, but still consume the real resolver packet and receipt
            # path.  A fake host transcript therefore cannot bypass the gate.
            workspace.host_roots.update({host: workspace.candidate_root for host in HOSTS})
            for host in HOSTS:
                packet_error = _canonical_packet(workspace, host)
                if packet_error:
                    errors.append(packet_error)
            if not errors:
                _lock_fixture_parents(workspace)
        if not errors:
            for host in HOSTS:
                for case in CASES:
                    result = runner(workspace, host, case)
                    results.append(result)
                    errors.extend(validate_host_result(workspace, result))
    finally:
        try:
            after_state = _snapshot_user_state()
        except OSError:
            after_state = ()
            errors.append("protected daily state snapshot failed")
        after_claude_config = _snapshot_metadata(workspace.claude_config_source)
        user_state_unchanged = before_state_ok and before_state == after_state
        if not user_state_unchanged:
            errors.append("protected daily state changed during live probe")
        claude_sandbox_changed = before_claude_config != after_claude_config
        try:
            cleanup_workspace(workspace)
            cleanup_ok = not workspace.temporary_root.exists()
        except OSError as error:
            errors.append(f"temporary cleanup failed: {error}")
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            _render_report(
                workspace=workspace, results=results, errors=errors,
                user_state_unchanged=user_state_unchanged, cleanup_ok=cleanup_ok,
                claude_sandbox_changed=claude_sandbox_changed,
            ), encoding="utf-8",
        )
    return 0 if not errors and cleanup_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
