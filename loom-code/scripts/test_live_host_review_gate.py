"""Contract tests for the real Claude Code + Codex release gate.

The live probes are intentionally not run in unit tests.  These tests exercise
the deterministic safety boundary with a fake host runner so that a future
CLI/auth failure cannot weaken the release gate into a best-effort report.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import live_host_review_gate as gate
import pytest

@pytest.fixture(autouse=True)
def _named_claude_test_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    """Give every unit test the one supported, private Claude profile."""

    home = tmp_path / "home"
    profile = home / ".claude-test"
    profile.mkdir(parents=True, mode=0o700)
    monkeypatch.setattr(gate.Path, "home", classmethod(lambda _cls: home))
    return profile


def _candidate(tmp_path: Path) -> Path:
    root = tmp_path / "source" / "loom-code"
    source_root = Path(__file__).resolve().parents[1]
    for relative in {"scripts/review_context.py", *gate.RESOURCE_RELATIVE_PATHS.values()}:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_root / relative, target)
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "plugin.json").write_text(
        '{"name": "loom-code", "version": "test"}\n'
    )
    return root


def _packet(workspace: gate.Workspace, host: str) -> dict[str, object]:
    root = workspace.expected_root(host)
    return {
        "target_repo": str(workspace.consumer_root),
        "reviewed_sha": workspace.reviewed_sha,
        "plugin_version": "test",
        "resources": {
            name: str((root / relative).resolve())
            for name, relative in gate.RESOURCE_RELATIVE_PATHS.items()
        },
    }


def _auth(tmp_path: Path) -> Path:
    auth = tmp_path / "caller-supplied-auth.json"
    auth.write_text('{"tokens": {"access_token": "do-not-report"}}\n')
    auth.chmod(0o600)
    return auth


def _claude_config(tmp_path: Path) -> Path:
    """Return the test's stand-in for the fixed ~/.claude-test profile."""

    del tmp_path
    return Path.home() / ".claude-test"


def _main_args(
    candidate: Path, auth: Path, config: Path, report: Path
) -> list[str]:
    del config
    return [
        "--candidate", str(candidate),
        "--codex-auth-source", str(auth),
        "--report", str(report),
    ]


def test_live_gate_uses_only_named_claude_test_profile_without_home_rewrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = _candidate(tmp_path)
    auth = _auth(tmp_path)
    profile = _claude_config(tmp_path)
    profile_marker = profile / "plugin-state"
    profile_marker.write_text("before", encoding="utf-8")
    monkeypatch.setenv("HOME", "daily-home-must-not-be-rewritten")

    workspace = gate.create_workspace(candidate, auth)
    captured: list[dict[str, str]] = []

    def capture(_command, *, cwd, env):
        del cwd
        captured.append(dict(env))
        return 0, ""

    monkeypatch.setattr(gate, "_run", capture)
    try:
        assert workspace.claude_config_dir == profile
        assert workspace.claude_config_source == profile
        assert gate.check_claude_auth(command_runner=capture) is None
        gate._real_host_runner(workspace, "claude", "invalid-reference")
        assert all(env["CLAUDE_CONFIG_DIR"] == str(profile) for env in captured)
        assert all(env["HOME"] == "daily-home-must-not-be-rewritten" for env in captured)
        assert profile_marker.read_text(encoding="utf-8") == "before"
    finally:
        gate.cleanup_workspace(workspace)


def test_part4_runner_contract_has_no_removed_claude_sandbox_flags() -> None:
    """Active Part 4 records describe the fixed test profile, not removed flags."""

    repo_root = Path(__file__).resolve().parents[2]
    records = (
        repo_root / "docs/loom/specs/2026-08-24-cross-host-review-gate-hardening-part-4.md",
        repo_root / "docs/loom/plans/2026-08-24-cross-host-review-gate-hardening-part-4.md",
    )
    removed_runner_contract = (
        "--allow-mutable-claude-sandbox",
        "--claude-config-dir",
        "user-provided Claude-config mutation",
    )
    assert "protected daily-state mutation" in records[1].read_text(encoding="utf-8")
    for record in records:
        text = record.read_text(encoding="utf-8")
        assert "~/.claude-test" in text
        assert "--permission-mode bypassPermissions" in text
        assert not any(stale_text in text for stale_text in removed_runner_contract)


def _transcript(workspace: gate.Workspace, host: str, case: str) -> str:
    root = workspace.expected_root(host)
    station = (
        case.removeprefix("valid-").upper()
        if case.startswith("valid-")
        else ("CODE" if case == "invalid-reference" else "DOCS")
    )
    skill = gate.STATION_SKILLS[station]
    skill_path = root / "skills" / skill / "SKILL.md"
    read_event = (
        json.dumps({
            "type": "assistant",
            "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": str(skill_path)}}]},
        })
        if host == "claude"
        else json.dumps({
            "type": "item.completed",
            "item": {"type": "command_execution", "command": f"cat {skill_path}"},
        })
    )
    if case.startswith("valid-"):
        receipt_event = (
            json.dumps({
                "type": "assistant",
                "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": gate.receipt_command(station)}}]},
            })
            if host == "claude"
            else json.dumps({
                "type": "item.completed",
                "item": {"type": "command_execution", "command": gate.receipt_command(station)},
            })
        )
        return "\n".join(
            (
                read_event,
                receipt_event,
                f"CANDIDATE_ROOT: {root}",
                f"REVIEWED_SHA: {workspace.reviewed_sha}",
                "PACKET_SOURCE: scripts/review_context.py",
                f"HOST_SKILL_INVOKED: {station}",
                f"{station}_STATION_PACKET: {root} {workspace.reviewed_sha}",
            )
        )
    probe_command = gate.adapter_probe_command(workspace, host, case)
    typed_refusal = json.dumps(gate.ADAPTER_REFUSALS[case], sort_keys=True)
    if host == "claude":
        probe_event = json.dumps({
            "type": "assistant",
            "message": {"content": [{
                "type": "tool_use",
                "id": "adapter-probe-1",
                "name": "Bash",
                "input": {"command": probe_command},
            }]},
        })
        result_event = json.dumps({
            "type": "user",
            "message": {"content": [{
                "type": "tool_result",
                "tool_use_id": "adapter-probe-1",
                "content": typed_refusal,
            }]},
        })
        return f"{read_event}\n{probe_event}\n{result_event}\nREFUSE: {host} {case}\n"
    probe_event = json.dumps({
        "type": "item.completed",
        "item": {
            "type": "command_execution",
            "command": probe_command,
            "aggregated_output": typed_refusal + "\n",
            "exit_code": 3,
        },
    })
    return f"{read_event}\n{probe_event}\nREFUSE: {host} {case}\n"


def _fake_result(
    workspace: gate.Workspace,
    host: str,
    case: str,
    *,
    output: str | None = None,
) -> gate.HostResult:
    before = tuple(sorted(path.name for path in workspace.marker_directory.iterdir()))
    if case.startswith("valid-") and host in workspace.host_packets:
        station = case.removeprefix("valid-").upper()
        command = [
            sys.executable,
            str(workspace.expected_root(host) / "scripts/live_gate_station_receipt.py"),
            "--packet", str(workspace.host_packet_paths[host]),
            "--plugin-root", str(workspace.expected_root(host)),
            "--marker-dir", str(workspace.marker_directory),
            "--repo", str(workspace.consumer_root),
            "--station", station,
            "--nonce", workspace.host_nonces[(host, case)],
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
    after = tuple(sorted(path.name for path in workspace.marker_directory.iterdir()))
    return gate.HostResult(
        host,
        case,
        gate.host_argv_for_case(workspace, host, case),
        _transcript(workspace, host, case) if output is None else output,
        0,
        before,
        after,
    )


def test_gate_requires_both_caller_supplied_auth_bootstraps(tmp_path: Path) -> None:
    missing = tmp_path / "missing-auth.json"
    candidate = _candidate(tmp_path)
    config = _claude_config(tmp_path)
    result = gate.main(_main_args(candidate, missing, config, tmp_path / "report.md"))

    assert result != 0
    assert not (tmp_path / "report.md").exists()

    assert gate.main(
        _main_args(candidate, _auth(tmp_path), config, tmp_path / "valid.md"),
        host_runner=_fake_result,
    ) == 0


def test_gate_fails_closed_when_any_required_host_case_fails(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    auth = _auth(tmp_path)
    config = _claude_config(tmp_path)
    report = tmp_path / "report.md"

    def fake_host(workspace: gate.Workspace, host: str, case: str) -> gate.HostResult:
        output = _transcript(workspace, host, case)
        if (host, case) == ("codex", "valid-sdd"):
            output = "unexpected success\n"
        return _fake_result(workspace, host, case, output=output)

    result = gate.main(
        _main_args(candidate, auth, config, report), host_runner=fake_host
    )

    assert result != 0
    rendered = report.read_text(encoding="utf-8")
    assert "FAIL" in rendered
    assert "do-not-report" not in rendered
    assert "caller-supplied-auth" not in rendered


def test_gate_uses_read_only_copies_and_cleans_temporary_auth(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    auth = _auth(tmp_path)
    claude_config = _claude_config(tmp_path)
    report = tmp_path / "report.md"
    captured: list[gate.Workspace] = []

    def fake_host(workspace: gate.Workspace, host: str, case: str) -> gate.HostResult:
        captured.append(workspace)
        assert workspace.candidate_root != candidate
        assert os.stat(workspace.candidate_root).st_mode & 0o222 == 0
        assert os.stat(workspace.consumer_root).st_mode & 0o222 == 0
        assert workspace.marker_directory.is_dir()
        assert os.stat(workspace.marker_directory).st_mode & 0o200
        assert workspace.claude_config_source == claude_config.absolute()
        assert workspace.claude_config_dir == claude_config.absolute()
        assert workspace.codex_auth_target.is_file()
        assert os.stat(workspace.codex_auth_target).st_mode & 0o077 == 0
        return _fake_result(workspace, host, case)

    result = gate.main(
        _main_args(candidate, auth, claude_config, report), host_runner=fake_host
    )

    assert result == 0
    assert captured
    workspace = captured[0]
    assert not workspace.temporary_root.exists()
    assert claude_config.is_dir()
    rendered = report.read_text(encoding="utf-8")
    assert "PASS" in rendered
    assert "finally cleanup: PASS" in rendered
    assert "protected daily state: unchanged" in rendered
    assert "cli versions: Claude Code=not-probed; Codex=not-probed" in rendered
    assert str(candidate) not in rendered
    assert str(auth) not in rendered
    assert str(claude_config) not in rendered


def test_codex_prepares_a_legacy_install_then_replaces_it_with_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The release gate proves the installed root changes across an upgrade."""

    workspace = gate.create_workspace(
        _candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path)
    )
    commands: list[tuple[str, ...]] = []
    legacy_root = workspace.codex_home / "plugins" / "legacy" / "loom-code"
    candidate_root = workspace.codex_home / "plugins" / "candidate" / "loom-code"

    def fake_run(command, **_kwargs):
        commands.append(tuple(command))
        if command[:3] == ("codex", "plugin", "add") and command[3] == "loom-code@legacy-live-host-gate":
            (legacy_root / ".codex-plugin").mkdir(parents=True)
            (legacy_root / ".codex-plugin" / "plugin.json").write_text(
                '{"name": "loom-code", "version": "legacy"}\n', encoding="utf-8"
            )
        elif command[:3] == ("codex", "plugin", "remove"):
            shutil.rmtree(legacy_root)
        elif command[:3] == ("codex", "plugin", "add"):
            shutil.copytree(workspace.candidate_root, candidate_root)
            candidate_root.chmod(0o755)
            (candidate_root / ".codex-plugin").mkdir(exist_ok=True)
            (candidate_root / ".codex-plugin" / "plugin.json").write_text(
                '{"name": "loom-code", "version": "candidate"}\n', encoding="utf-8"
            )
        return 0, "ok"

    monkeypatch.setattr(gate, "_run", fake_run)
    try:
        assert gate._prepare_codex(workspace) == (True, "")
        assert workspace.expected_root("codex") == candidate_root.resolve()
        assert (workspace.expected_root("codex") / "scripts/review_context.py").is_file()
        assert not legacy_root.exists()
        assert commands == [
            ("codex", "plugin", "marketplace", "add", str(workspace.temporary_root / "legacy-marketplace")),
            ("codex", "plugin", "add", "loom-code@legacy-live-host-gate"),
            ("codex", "plugin", "remove", "loom-code@legacy-live-host-gate"),
            ("codex", "plugin", "marketplace", "add", str(workspace.temporary_root / "marketplace")),
            ("codex", "plugin", "add", "loom-code@live-host-gate"),
        ]
    finally:
        gate.cleanup_workspace(workspace)


def test_claude_config_is_fixed_to_the_named_test_profile(tmp_path: Path) -> None:
    non_temporary = tmp_path / "not-disposable"
    non_temporary.mkdir(mode=0o700)
    with pytest.raises(ValueError, match="named"):
        gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), non_temporary)


def test_named_claude_test_profile_accepts_dotfiles_standard_mode(
    tmp_path: Path, _named_claude_test_profile: Path
) -> None:
    """The established dotfiles profiles are directories with mode 0755."""

    _named_claude_test_profile.chmod(0o755)
    calls: list[tuple[str, ...]] = []

    def authenticated(command, **_kwargs):
        calls.append(tuple(command))
        return 0, "logged in"

    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path))
    try:
        assert workspace.claude_config_source == _named_claude_test_profile
        assert gate.check_claude_auth(command_runner=authenticated) is None
        assert calls == [("claude", "auth", "status", "--text")]
    finally:
        gate.cleanup_workspace(workspace)


@pytest.mark.parametrize("profile_kind", ("symlink", "regular-file"))
def test_named_claude_test_profile_still_rejects_non_directory_or_symlink(
    tmp_path: Path,
    _named_claude_test_profile: Path,
    profile_kind: str,
) -> None:
    _named_claude_test_profile.rmdir()
    if profile_kind == "symlink":
        target = tmp_path / "profile-target"
        target.mkdir()
        _named_claude_test_profile.symlink_to(target, target_is_directory=True)
    else:
        _named_claude_test_profile.write_text("not a directory", encoding="utf-8")

    with pytest.raises(ValueError):
        gate.create_workspace(_candidate(tmp_path), _auth(tmp_path))


def test_claude_auth_exports_only_the_named_test_profile(tmp_path: Path) -> None:
    seen_env: dict[str, str] = {}

    def allowed(_command, **kwargs):
        seen_env.update(kwargs["env"])
        return 0, "logged in"

    assert gate.check_claude_auth(command_runner=allowed) is None
    assert seen_env["CLAUDE_CONFIG_DIR"] == str(_claude_config(tmp_path))
    assert "HOME" in seen_env


def test_cli_rejects_arbitrary_claude_profile_flags(
    tmp_path: Path,
) -> None:
    candidate = _candidate(tmp_path)
    auth = _auth(tmp_path)
    config = _claude_config(tmp_path)
    common = [
        "--candidate", str(candidate),
        "--codex-auth-source", str(auth),
        "--claude-config-dir", str(config),
        "--report", str(tmp_path / "report.md"),
    ]

    with pytest.raises(SystemExit):
        gate.main(
            common,
            host_runner=lambda *_args: pytest.fail("runner must not start"),
        )

    with pytest.raises(SystemExit):
        gate.main(
            [*common, "--allow-mutable-claude-sandbox", str(tmp_path / "wrong")],
            host_runner=lambda *_args: pytest.fail("runner must not start"),
        )


def test_each_valid_station_session_must_bind_to_the_one_candidate_packet(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        assert gate._canonical_packet(workspace, "claude") is None
        valid = _fake_result(workspace, "claude", "valid-code")
        assert gate.validate_host_result(workspace, valid) == []

        wrong_sha = gate.HostResult(
            host="claude",
            case="valid-code",
            command=gate.host_argv_for_case(workspace, "claude", "valid-code"),
            output=_transcript(workspace, "claude", "valid-code").replace(
                workspace.reviewed_sha, "0" * 40, 1
            ),
            returncode=0,
            marker_files_before=valid.marker_files_before,
            marker_files_after=valid.marker_files_after,
        )
        assert gate.validate_host_result(workspace, wrong_sha)
    finally:
        gate.cleanup_workspace(workspace)


def test_gate_requires_real_sessions_for_all_four_stations_per_host(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    auth = _auth(tmp_path)
    claude_config = _claude_config(tmp_path)
    report = tmp_path / "report.md"
    observed: list[tuple[str, str]] = []

    def fake_host(workspace: gate.Workspace, host: str, case: str) -> gate.HostResult:
        observed.append((host, case))
        return _fake_result(workspace, host, case)

    assert gate.main(
        _main_args(candidate, auth, claude_config, report), host_runner=fake_host
    ) == 0
    assert set(observed) == {
        *( (host, f"valid-{station.lower()}") for host in gate.HOSTS for station in gate.STATIONS ),
        *((host, "invalid-reference") for host in gate.HOSTS),
        *((host, "unchanged-post-fix") for host in gate.HOSTS),
    }


def test_refusal_cases_may_not_run_scope_marker_or_wrapper(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        refused = _fake_result(workspace, "codex", "invalid-reference")
        assert gate.validate_host_result(workspace, refused) == []
        leaked = _fake_result(
            workspace,
            "codex",
            "invalid-reference",
            output=_transcript(workspace, "codex", "invalid-reference")
            + json.dumps({
                "type": "item.completed",
                "item": {"type": "command_execution", "command": "python3 review_scope.py"},
            })
            + "\n",
        )
        assert gate.validate_host_result(workspace, leaked)
    finally:
        gate.cleanup_workspace(workspace)


def test_codex_refusal_ignores_forbidden_words_in_skill_command_output(
    tmp_path: Path,
) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        transcript = _transcript(workspace, "codex", "invalid-reference")
        events = transcript.splitlines()
        read_event = json.loads(events[0])
        read_event["item"]["aggregated_output"] = (
            "Skill prose mentions review_context.py, markers, receipts, and wrappers."
        )
        events[0] = json.dumps(read_event)
        result = _fake_result(
            workspace,
            "codex",
            "invalid-reference",
            output="\n".join(events) + "\n",
        )

        assert gate.validate_host_result(workspace, result) == []
    finally:
        gate.cleanup_workspace(workspace)


def test_negative_marker_check_uses_each_cases_existing_receipt_baseline(
    tmp_path: Path,
) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        existing = workspace.marker_directory / "CODE-existing.json"
        existing.write_text("{}\n", encoding="utf-8")
        result = _fake_result(workspace, "codex", "invalid-reference")

        assert result.marker_files_before == (existing.name,)
        assert result.marker_files_after == (existing.name,)
        assert gate.validate_host_result(workspace, result) == []
    finally:
        gate.cleanup_workspace(workspace)


def test_refusal_requires_exact_candidate_probe_event_and_typed_result(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        for host, case in (("claude", "invalid-reference"), ("codex", "unchanged-post-fix")):
            transcript = _transcript(workspace, host, case)
            prose_only = _fake_result(
                workspace,
                host,
                case,
                output="\n".join((transcript.splitlines()[0], f"REFUSE: {host} {case}")),
            )
            errors = gate.validate_host_result(workspace, prose_only)
            assert any("missing exact adapter probe command event" in error for error in errors)
            assert any("missing typed adapter refusal event" in error for error in errors)
    finally:
        gate.cleanup_workspace(workspace)


def test_refusal_requires_the_exact_native_station_slash_command(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        valid_shape = _fake_result(workspace, "claude", "invalid-reference")
        wrong_command = (
            *valid_shape.command[:-1],
            valid_shape.command[-1].replace(
                "/loom-code:requesting-code-review\n",
                "/loom-code:requesting-docs-review\n",
                1,
            ),
        )
        wrong = gate.HostResult(
            valid_shape.host,
            valid_shape.case,
            wrong_command,
            valid_shape.output,
            valid_shape.returncode,
            valid_shape.marker_files_before,
            valid_shape.marker_files_after,
        )
        assert any(
            "missing native refusal slash invocation" in error
            for error in gate.validate_host_result(workspace, wrong)
        )
    finally:
        gate.cleanup_workspace(workspace)


def test_valid_echo_without_actual_candidate_tool_event_is_rejected(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        echoed = gate.HostResult(
            host="claude",
            case="valid-code",
            command=gate.host_argv_for_case(workspace, "claude", "valid-code"),
            output="\n".join(_transcript(workspace, "claude", "valid-code").splitlines()[2:]),
            returncode=0,
        )
        assert gate.validate_host_result(workspace, echoed)
    finally:
        gate.cleanup_workspace(workspace)


def test_forged_receipt_file_without_exact_receipt_event_is_rejected(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        assert gate._canonical_packet(workspace, "claude") is None
        valid = _fake_result(workspace, "claude", "valid-code")
        output_without_receipt_event = "\n".join(
            line
            for line in valid.output.splitlines()
            if "live_gate_station_receipt.py" not in line
        )
        forged = gate.HostResult(
            valid.host,
            valid.case,
            valid.command,
            output_without_receipt_event,
            0,
            valid.marker_files_before,
            valid.marker_files_after,
        )
        assert any(
            "missing exact station receipt command event" in error
            for error in gate.validate_host_result(workspace, forged)
        )
    finally:
        gate.cleanup_workspace(workspace)


def test_valid_session_that_reruns_review_context_is_rejected(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        assert gate._canonical_packet(workspace, "claude") is None
        valid = _fake_result(workspace, "claude", "valid-code")
        rerun_event = json.dumps({
            "type": "assistant",
            "message": {"content": [{
                "type": "tool_use",
                "name": "Bash",
                "input": {"command": f"python3 {workspace.expected_root('claude')}/scripts/review_context.py --repo {workspace.consumer_root}"},
            }]},
        })
        rerun = gate.HostResult(
            valid.host,
            valid.case,
            valid.command,
            valid.output + "\n" + rerun_event,
            0,
            valid.marker_files_before,
            valid.marker_files_after,
        )
        assert any(
            "re-ran handed packet resolver" in error
            for error in gate.validate_host_result(workspace, rerun)
        )
    finally:
        gate.cleanup_workspace(workspace)


def test_canonical_packet_is_resolved_once_per_host_and_records_subprocess_event(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    calls: list[tuple[str, ...]] = []

    def fake_run(command, **_kwargs):
        calls.append(tuple(command))
        return 0, json.dumps({
            "target_repo": str(workspace.consumer_root),
            "reviewed_sha": workspace.reviewed_sha,
            "plugin_version": "test",
            "resources": {
                name: str((workspace.candidate_root / relative).resolve())
                for name, relative in gate.RESOURCE_RELATIVE_PATHS.items()
            },
        })

    try:
        monkeypatch.setattr(gate, "_run", fake_run)
        assert gate._canonical_packet(workspace, "claude") is None
        assert gate._canonical_packet(workspace, "claude") is None
        assert len(calls) == 1
        assert gate._event_commands(workspace.host_packet_events["claude"])
    finally:
        gate.cleanup_workspace(workspace)


def test_canonical_packet_rejects_any_incomplete_resource_schema(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    packet = _packet(workspace, "claude")
    packet["resources"].pop("docs_review_skill")
    monkeypatch.setattr(gate, "_run", lambda *_args, **_kwargs: (0, json.dumps(packet)))
    try:
        assert gate._canonical_packet(workspace, "claude") == (
            "claude: canonical packet resource schema mismatch"
        )
        assert "claude" not in workspace.host_packets
    finally:
        gate.cleanup_workspace(workspace)


def test_real_host_argv_is_read_only_and_uses_native_station_slash_command(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        claude = gate.host_argv_for_case(workspace, "claude", "valid-code")
        codex = gate.host_argv_for_case(workspace, "codex", "valid-code")
        assert "Write" not in claude and "Edit" not in claude
        assert "bypassPermissions" in claude
        assert "dontAsk" not in claude
        assert "workspace-write" in codex
        assert any(value.startswith("/loom-code:requesting-code-review") for value in claude)
        assert any(value.startswith("/loom-code:requesting-code-review") for value in codex)
    finally:
        gate.cleanup_workspace(workspace)


@pytest.mark.parametrize(
    ("case", "station"),
    [
        ("valid-code", "CODE"),
        ("invalid-reference", "CODE"),
        ("unchanged-post-fix", "DOCS"),
    ],
)
def test_claude_allows_only_the_exact_two_gate_tool_calls(
    tmp_path: Path, case: str, station: str
) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        argv = gate.host_argv_for_case(workspace, "claude", case)
        allowed_index = argv.index("--allowedTools")
        permission_index = argv.index("--permission-mode")
        skill_path = gate._station_skill_path(workspace.expected_root("claude"), station)
        command = (
            gate.receipt_command(station)
            if case.startswith("valid-")
            else gate.adapter_probe_command(workspace, "claude", case)
        )

        assert argv[allowed_index + 1:permission_index] == (
            f"Read({skill_path})",
            f"Bash({command})",
        )
        assert "Read" not in argv[allowed_index + 1:permission_index]
        assert "Bash" not in argv[allowed_index + 1:permission_index]
    finally:
        gate.cleanup_workspace(workspace)


def test_real_host_runner_purges_inherited_live_gate_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    captured: list[tuple[str, str, dict[str, str]]] = []

    def capture(_command, *, cwd, env):
        captured.append((str(cwd), env.get("LOOM_LIVE_GATE_UNTRUSTED", ""), dict(env)))
        return 0, ""

    monkeypatch.setenv("LOOM_LIVE_GATE_UNTRUSTED", "parent-sentinel")
    monkeypatch.setattr(gate, "_run", capture)
    try:
        for host in gate.HOSTS:
            gate._real_host_runner(workspace, host, "invalid-reference")
            workspace.host_packet_paths[host] = workspace.packet_directory / f"{host}.json"
            workspace.host_nonces[(host, "valid-code")] = "a" * 32
            gate._real_host_runner(workspace, host, "valid-code")

        expected_valid = {
            "LOOM_LIVE_GATE_PACKET",
            "LOOM_LIVE_GATE_MARKER_DIR",
            "LOOM_LIVE_GATE_NONCE",
            "LOOM_LIVE_GATE_PLUGIN_ROOT",
            "LOOM_LIVE_GATE_REPO",
        }
        assert len(captured) == 4
        for index, (_cwd, sentinel, env) in enumerate(captured):
            assert sentinel == ""
            present = {key for key in env if key.startswith("LOOM_LIVE_GATE_")}
            assert present == (set() if index % 2 == 0 else expected_valid)
            if index < 2:
                assert env["HOME"] == os.environ["HOME"]
    finally:
        gate.cleanup_workspace(workspace)


def test_parent_directories_are_locked_while_marker_directory_stays_writable(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        gate._lock_fixture_parents(workspace)
        for path in (
            workspace.temporary_root,
            workspace.candidate_root.parent,
            workspace.consumer_root,
            workspace.consumer_root / ".git",
            workspace.packet_directory,
        ):
            assert os.stat(path).st_mode & 0o222 == 0
        assert os.stat(workspace.marker_directory).st_mode & 0o200
    finally:
        gate.cleanup_workspace(workspace)


def test_report_redacts_paths_and_raw_prompt_even_on_error(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    auth = _auth(tmp_path)
    claude_config = _claude_config(tmp_path)
    workspace = gate.create_workspace(candidate, auth, claude_config)
    try:
        report = gate._render_report(
            workspace=workspace,
            results=[gate.HostResult("claude", "valid-code", ("claude", "raw prompt " + str(workspace.consumer_root)), "raw prompt " + str(workspace.candidate_root), 1)],
            errors=[f"failure at {workspace.temporary_root} using {claude_config}"],
            user_state_unchanged=False,
            cleanup_ok=False,
        )
        for private_path in (str(candidate), str(auth), str(claude_config), str(workspace.temporary_root), str(workspace.consumer_root)):
            assert private_path not in report
        assert "raw prompt" not in report
        assert "[CANDIDATE_PLUGIN]" in report
        assert "[RUNNER_TEMP]" not in report
        assert "internal gate failure (details withheld)" in report
    finally:
        gate.cleanup_workspace(workspace)


def test_report_withholds_unrecognized_error_text_and_unsafe_cli_version(tmp_path: Path) -> None:
    auth = _auth(tmp_path)
    workspace = gate.create_workspace(_candidate(tmp_path), auth, _claude_config(tmp_path))
    workspace.host_versions["claude"] = "Claude 1.2 TOP_SECRET/path"
    try:
        report = gate._render_report(
            workspace=workspace,
            results=[],
            errors=["TOP_SECRET raw host failure"],
            user_state_unchanged=True,
            cleanup_ok=True,
        )
        assert "TOP_SECRET" not in report
        assert "internal gate failure (details withheld)" in report
        assert "Claude Code=unavailable" in report
    finally:
        gate.cleanup_workspace(workspace)


def test_run_timeout_preserves_only_a_safe_overload_category(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    private_path = str(tmp_path / "private-consumer")
    partial = "\n".join((
        json.dumps({
            "type": "system",
            "subtype": "api_retry",
            "error_status": 529,
            "error": "overloaded",
            "cwd": private_path,
        }),
        private_path,
    ))

    def timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(
            cmd=["claude", private_path], timeout=180, output=partial
        )

    monkeypatch.setattr(gate.subprocess, "run", timeout)
    code, output = gate._run(("claude", "private-prompt"), cwd=tmp_path)

    assert code == 124
    assert json.loads(output) == {
        "type": "runner.error",
        "category": "api-overloaded",
    }
    assert private_path not in output


@pytest.mark.parametrize(
    ("error", "category"),
    [
        (FileNotFoundError("/private/tool/path"), "spawn-not-found"),
        (PermissionError("/private/cwd/path"), "spawn-permission-denied"),
        (OSError("/private/other/path"), "spawn-os-error"),
    ],
)
def test_run_os_error_preserves_only_a_safe_spawn_category(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error: OSError,
    category: str,
) -> None:
    def fail(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(gate.subprocess, "run", fail)
    code, output = gate._run(("claude", "private-prompt"), cwd=tmp_path)

    assert code == 127
    assert json.loads(output) == {"type": "runner.error", "category": category}
    assert "/private/" not in output


def test_report_renders_only_allowlisted_runner_error_category(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        output = json.dumps({
            "type": "runner.error",
            "category": "api-overloaded",
            "private": str(workspace.consumer_root),
        })
        evidence = gate._redacted_evidence(output, workspace)

        assert evidence == "HOST_ERROR: API_OVERLOADED"
        assert str(workspace.consumer_root) not in evidence
    finally:
        gate.cleanup_workspace(workspace)


def test_committed_live_report_is_not_release_evidence_without_all_case_evidence() -> None:
    report = (
        Path(__file__).resolve().parents[2]
        / "docs/loom/dogfood/2026-08-24-cross-host-review-gate-live-host.md"
    ).read_text(encoding="utf-8")

    if "status: PASS" not in report:
        assert any(status in report for status in ("status: NOT_RUN", "status: FAIL"))
        return

    assert report.count("### claude /") == len(gate.CASES)
    assert report.count("### codex /") == len(gate.CASES)
    for host in gate.HOSTS:
        for case in gate.CASES:
            assert f"### {host} / {case}" in report


def test_report_drops_prose_that_only_quotes_an_evidence_key(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    auth = _auth(tmp_path)
    workspace = gate.create_workspace(candidate, auth, _claude_config(tmp_path))
    try:
        output = "I will not emit PACKET_SOURCE: scripts/review_context.py because raw prompt text must stay private."
        evidence = gate._redacted_evidence(output, workspace)
        assert "I will not emit" not in evidence
        assert "raw prompt text" not in evidence
    finally:
        gate.cleanup_workspace(workspace)


def test_claude_auth_status_failure_is_a_release_blocker(tmp_path: Path) -> None:
    config = _claude_config(tmp_path)

    def denied(*_args, **_kwargs):
        return 1, "not logged in"

    assert gate.check_claude_auth(config, command_runner=denied) == "Claude auth status failed"


def test_claude_auth_check_uses_the_noninteractive_text_status_form(tmp_path: Path) -> None:
    seen: list[tuple[str, ...]] = []

    def allowed(command, **_kwargs):
        seen.append(tuple(command))
        return 0, "logged in"

    assert gate.check_claude_auth(_claude_config(tmp_path), command_runner=allowed) is None
    assert seen == [("claude", "auth", "status", "--text")]


def test_claude_auth_check_rejects_any_non_profile_path_before_running_the_cli(
    tmp_path: Path,
) -> None:
    caller_path = tmp_path / "caller-spelling"
    caller_path.mkdir()
    called = False

    def allowed(_command, **_kwargs):
        nonlocal called
        called = True
        return 0, "logged in"

    assert gate.check_claude_auth(caller_path, command_runner=allowed) == (
        "Claude live gate uses only the named ~/.claude-test profile"
    )
    assert not called


def test_caller_claude_config_mutation_fails_closed_and_redacts_its_path(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    auth = _auth(tmp_path)
    config = _claude_config(tmp_path)
    report = tmp_path / "report.md"

    def mutating_host(workspace: gate.Workspace, host: str, case: str) -> gate.HostResult:
        (config / "unexpected-session-state").write_text("changed", encoding="utf-8")
        return _fake_result(workspace, host, case)

    assert gate.main(
        _main_args(candidate, auth, config, report), host_runner=mutating_host
    ) == 0
    rendered = report.read_text(encoding="utf-8")
    assert "Claude test-profile metadata: CHANGED (expected dedicated profile)" in rendered
    assert "protected daily state: unchanged" in rendered
    assert str(config) not in rendered


@pytest.mark.parametrize(
    "daily_path",
    (".claude/settings.local.json", ".codex/config.toml"),
)
def test_daily_configuration_mutation_fails_closed(
    tmp_path: Path, daily_path: str,
) -> None:
    candidate = _candidate(tmp_path)
    auth = _auth(tmp_path)
    report = tmp_path / "report.md"
    daily_metadata = Path.home() / daily_path

    def mutating_host(workspace: gate.Workspace, host: str, case: str) -> gate.HostResult:
        daily_metadata.parent.mkdir(parents=True, exist_ok=True)
        daily_metadata.write_text("changed", encoding="utf-8")
        return _fake_result(workspace, host, case)

    assert gate.main(
        _main_args(candidate, auth, _claude_config(tmp_path), report),
        host_runner=mutating_host,
    ) == 1
    rendered = report.read_text(encoding="utf-8")
    assert "status: FAIL" in rendered
    assert "protected daily state: CHANGED" in rendered
    assert "- protected daily state changed during live probe" in rendered
    assert str(daily_metadata) not in rendered


def test_user_state_snapshot_covers_configuration_and_plugins(tmp_path: Path) -> None:
    for relative_path in (
        ".claude/settings.json",
        ".claude/plugins/installed_plugins.json",
        ".codex/config.toml",
        ".codex/auth.json",
        ".codex/plugins/cache/example/.codex-plugin/plugin.json",
    ):
        metadata = Path.home() / relative_path
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text("same metadata shape", encoding="utf-8")

    snapshot = gate._snapshot_user_state()

    names = {entry[0] for entry in snapshot}
    assert ".claude/settings.json" in names
    assert ".claude/plugins/installed_plugins.json" in names
    assert ".codex/config.toml" in names
    assert ".codex/auth.json" in names
    assert ".codex/plugins/cache/example/.codex-plugin/plugin.json" in names


def test_user_state_snapshot_ignores_runtime_sessions(tmp_path: Path) -> None:
    for relative_path in (
        ".claude/projects/session-state.json",
        ".codex/plugins/cache/example/runtime.log",
    ):
        runtime_metadata = Path.home() / relative_path
        runtime_metadata.parent.mkdir(parents=True, exist_ok=True)
        runtime_metadata.write_text("runtime only", encoding="utf-8")

    names = {entry[0] for entry in gate._snapshot_user_state()}

    assert ".claude/projects/session-state.json" not in names
    assert ".codex/plugins/cache/example/runtime.log" not in names


def test_user_state_snapshot_follows_daily_settings_symlink(tmp_path: Path) -> None:
    target = tmp_path / "managed-settings.json"
    target.write_text('{"mode":"before"}', encoding="utf-8")
    settings = Path.home() / ".claude/settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.symlink_to(target)

    before = gate._snapshot_user_state()
    target.write_text('{"mode":"after"}', encoding="utf-8")

    assert before != gate._snapshot_user_state()


def test_structured_skill_read_parser_rejects_cross_field_substring_spoof(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    expected = workspace.candidate_root / "skills/requesting-code-review/SKILL.md"
    exact_claude = json.dumps({
        "type": "assistant",
        "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": str(expected)}}]},
    })
    spoofed_claude = json.dumps({
        "type": "assistant",
        "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/wrong/SKILL.md", "note": str(expected)}}]},
    })
    exact_codex = json.dumps({
        "type": "item.completed",
        "item": {"type": "command_execution", "command": f"cat {expected}"},
    })
    spoofed_codex = json.dumps({
        "type": "item.completed",
        "item": {"type": "command_execution", "command": f"printf read {expected}"},
    })
    try:
        assert gate._event_loaded_candidate_skill(exact_claude, "claude", expected)
        assert not gate._event_loaded_candidate_skill(spoofed_claude, "claude", expected)
        assert gate._event_loaded_candidate_skill(exact_codex, "codex", expected)
        assert not gate._event_loaded_candidate_skill(spoofed_codex, "codex", expected)
    finally:
        gate.cleanup_workspace(workspace)


def test_receipt_event_parser_requires_the_exact_station_argv() -> None:
    exact = gate.expected_receipt_argv("DOCS")
    claude = json.dumps({
        "type": "assistant",
        "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": gate.receipt_command("DOCS")}}]},
    })
    codex = json.dumps({
        "type": "item.completed",
        "item": {"type": "command_execution", "command": gate.receipt_command("DOCS")},
    })
    wrong_station = claude.replace("--station DOCS", "--station CODE")
    extra_shell = claude.replace("--nonce", "&& touch /tmp/nope --nonce")

    assert gate._event_command_argvs(claude, "claude") == (exact,)
    assert gate._event_command_argvs(codex, "codex") == (exact,)
    assert exact not in gate._event_command_argvs(wrong_station, "claude")
    assert exact not in gate._event_command_argvs(extra_shell, "claude")
    wrapped_codex = json.dumps({
        "type": "item.completed",
        "item": {
            "type": "command_execution",
            "command": f"/bin/zsh -lc {json.dumps(gate.receipt_command('DOCS'))}",
        },
    })
    assert gate._event_command_argvs(wrapped_codex, "codex") == (exact,)
    assert gate._event_command_argvs(wrapped_codex, "claude") == ()

    wrong_wrapper = wrapped_codex.replace("/bin/zsh", "/bin/bash")
    assert gate._event_command_argvs(wrong_wrapper, "codex") == ()


def _extra_tool_event(host: str) -> str:
    if host == "claude":
        return json.dumps({
            "type": "assistant",
            "message": {"content": [{
                "type": "tool_use",
                "name": "Bash",
                "input": {"command": "pwd"},
            }]},
        })
    return json.dumps({
        "type": "item.completed",
        "item": {"type": "command_execution", "command": "pwd"},
    })


def test_valid_station_rejects_an_extra_tool_before_the_exact_pair(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        assert gate._canonical_packet(workspace, "claude") is None
        assert gate._canonical_packet(workspace, "codex") is None
        for host in gate.HOSTS:
            output = _extra_tool_event(host) + "\n" + _transcript(workspace, host, "valid-code")
            result = _fake_result(workspace, host, "valid-code", output=output)
            assert any(
                "exact gate tool sequence mismatch" in error
                for error in gate.validate_host_result(workspace, result)
            )
    finally:
        gate.cleanup_workspace(workspace)


def test_valid_station_rejects_reordered_read_and_receipt_events(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        assert gate._canonical_packet(workspace, "claude") is None
        assert gate._canonical_packet(workspace, "codex") is None
        for host in gate.HOSTS:
            lines = _transcript(workspace, host, "valid-code").splitlines()
            lines[0], lines[1] = lines[1], lines[0]
            result = _fake_result(
                workspace, host, "valid-code", output="\n".join(lines) + "\n"
            )
            assert any(
                "exact gate tool sequence mismatch" in error
                for error in gate.validate_host_result(workspace, result)
            )
    finally:
        gate.cleanup_workspace(workspace)


def test_valid_station_rejects_a_duplicate_skill_read_event(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        assert gate._canonical_packet(workspace, "claude") is None
        assert gate._canonical_packet(workspace, "codex") is None
        for host in gate.HOSTS:
            lines = _transcript(workspace, host, "valid-code").splitlines()
            lines.insert(1, lines[0])
            result = _fake_result(
                workspace, host, "valid-code", output="\n".join(lines) + "\n"
            )
            assert any(
                "exact gate tool sequence mismatch" in error
                for error in gate.validate_host_result(workspace, result)
            )
    finally:
        gate.cleanup_workspace(workspace)


def test_codex_sandbox_exposes_only_marker_directory_as_writable_workspace(tmp_path: Path) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        argv = gate.host_argv_for_case(workspace, "codex", "valid-code")
        assert argv[argv.index("--sandbox") + 1] == "workspace-write"
        assert argv[argv.index("-C") + 1] == str(workspace.marker_directory)
        assert "--skip-git-repo-check" in argv
        assert "--add-dir" not in argv
        assert str(workspace.consumer_root) not in (argv[argv.index("-C") + 1],)
    finally:
        gate.cleanup_workspace(workspace)


def test_report_evidence_is_a_fixed_allowlist_not_host_text(tmp_path: Path) -> None:
    auth = _auth(tmp_path)
    workspace = gate.create_workspace(_candidate(tmp_path), auth, _claude_config(tmp_path))
    try:
        output = "\n".join((
            f"CANDIDATE_ROOT: {workspace.candidate_root} TOP_SECRET",
            "REFUSE: TOP_SECRET",
            json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "PACKET_SOURCE: scripts/review_context.py TOP_SECRET"}]}}),
        ))
        evidence = gate._redacted_evidence(output, workspace)
        assert "TOP_SECRET" not in evidence
        assert evidence.splitlines() == ["REFUSE: recorded"]
    finally:
        gate.cleanup_workspace(workspace)


def test_each_station_skill_pins_one_explicit_receipt_argv() -> None:
    plugin_root = Path(__file__).resolve().parents[1]
    expected_file = {
        "CODE": plugin_root / "skills/requesting-code-review/SKILL.md",
        "MIXED": plugin_root / "skills/requesting-code-review/SKILL.md",
        "DOCS": plugin_root / "skills/requesting-docs-review/SKILL.md",
        "SDD": plugin_root / "skills/subagent-driven-development/SKILL.md",
    }
    for station, path in expected_file.items():
        text = path.read_text(encoding="utf-8")
        assert f"`{gate.receipt_command(station)}`" in text
    assert "<CODE|MIXED>" not in expected_file["CODE"].read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("station", "slash_skill"),
    [
        ("CODE", "requesting-code-review"),
        ("MIXED", "requesting-code-review"),
        ("DOCS", "requesting-docs-review"),
        ("SDD", "subagent-driven-development"),
    ],
)
def test_valid_case_argv_starts_with_the_exact_station_skill(
    tmp_path: Path, station: str, slash_skill: str
) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        for host in gate.HOSTS:
            argv = gate.host_argv_for_case(workspace, host, f"valid-{station.lower()}")
            assert argv[-1].startswith(f"/loom-code:{slash_skill}\n")
            assert gate.receipt_command(station) in argv[-1]
    finally:
        gate.cleanup_workspace(workspace)


@pytest.mark.parametrize(
    ("case", "station", "loaded_input"),
    [
        ("invalid-reference", "CODE", "relative/codex-tools.md"),
        ("unchanged-post-fix", "DOCS", "initial SHA equals post-fix SHA"),
    ],
)
def test_refusal_prompts_inject_the_bad_input_and_exact_candidate_skill_read(
    tmp_path: Path, case: str, station: str, loaded_input: str
) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        for host in gate.HOSTS:
            prompt = gate.host_argv_for_case(workspace, host, case)[-1]
            expected_skill = workspace.expected_root(host) / "skills" / gate.STATION_SKILLS[station] / "SKILL.md"
            assert str(expected_skill) in prompt
            if case == "invalid-reference":
                reference_name = "claude-code-tools.md" if host == "claude" else "codex-tools.md"
                assert f"relative/{reference_name}" in prompt
            else:
                assert loaded_input in prompt
            assert str(workspace.expected_root(host) / "scripts/live_gate_adapter_probe.py") in prompt
            assert "execute this adapter probe command exactly once" in prompt.lower()
            if host == "claude":
                assert "use one Read tool call" in prompt
            else:
                assert f"execute exactly `cat {expected_skill}`" in prompt
    finally:
        gate.cleanup_workspace(workspace)


@pytest.mark.parametrize("case", ("valid-code", "invalid-reference"))
def test_claude_prompt_makes_exact_read_and_gate_command_the_first_two_tools(
    tmp_path: Path, case: str
) -> None:
    workspace = gate.create_workspace(_candidate(tmp_path), _auth(tmp_path), _claude_config(tmp_path))
    try:
        prompt = gate.host_argv_for_case(workspace, "claude", case)[-1]
        assert "Your first tool call must be the exact candidate SKILL Read" in prompt
        assert "Your second tool call must be the exact gate command" in prompt
        assert "Do not run exploratory" in prompt
        assert "Do not dispatch reviewers" in prompt
    finally:
        gate.cleanup_workspace(workspace)
