"""Regression coverage for Codex Desktop worktree-aware direct merges."""

from __future__ import annotations

import io
from pathlib import Path

import loom_checker


SHIP = Path(__file__).resolve().parents[1] / "skills" / "ship" / "SKILL.md"


def test_ship_authorized_merge_renders_absolute_repository_in_command() -> None:
    text = SHIP.read_text(encoding="utf-8")

    assert "cd '<absolute-repository-root>' && gh pr merge" in text
    assert "never rely on the Bash tool's workdir" in text


def test_cmd_push_observed_codex_payload_explicit_cd_selects_worktree(
    tmp_path: Path, monkeypatch,
) -> None:
    main = tmp_path / "main"
    feature = tmp_path / "feature"
    main.mkdir()
    feature.mkdir()
    observed: list[Path] = []
    payload = {
        "cwd": str(main),
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {
            "command": f"cd '{feature}' && gh pr merge 808 --squash",
        },
    }

    monkeypatch.setattr(loom_checker, "read_hook_payload", lambda: payload)
    monkeypatch.setattr(
        loom_checker,
        "_cmd_push",
        lambda _args, _out, _err: observed.append(Path.cwd()) or 0,
    )
    monkeypatch.chdir(tmp_path)

    assert loom_checker.cmd_push(["--hook"], io.StringIO(), io.StringIO()) == 0
    assert observed == [feature.resolve()]


def test_cmd_push_relative_cd_remains_fail_closed(tmp_path: Path, monkeypatch) -> None:
    main = tmp_path / "main"
    main.mkdir()
    payload = {
        "cwd": str(main),
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "cd feature && gh pr merge 808 --squash"},
    }
    err = io.StringIO()

    monkeypatch.setattr(loom_checker, "read_hook_payload", lambda: payload)

    assert loom_checker.cmd_push(["--hook"], io.StringIO(), err) == 2
    assert "ambiguous repository selection" in err.getvalue()


def test_cmd_push_bare_merge_does_not_trust_top_level_cwd(
    tmp_path: Path, monkeypatch,
) -> None:
    main = tmp_path / "main"
    main.mkdir()
    payload = {
        "cwd": str(main),
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "gh pr merge 808 --squash"},
    }
    err = io.StringIO()

    monkeypatch.setattr(loom_checker, "read_hook_payload", lambda: payload)

    assert loom_checker.cmd_push(["--hook"], io.StringIO(), err) == 2
    assert "absolute" in err.getvalue()


def test_cmd_push_non_publication_command_still_passes(monkeypatch) -> None:
    payload = {
        "cwd": "/does/not/matter",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la"},
    }
    called = False

    def unexpected(*_args):
        nonlocal called
        called = True
        return 0

    monkeypatch.setattr(loom_checker, "read_hook_payload", lambda: payload)
    monkeypatch.setattr(loom_checker, "_cmd_push", unexpected)

    assert loom_checker.cmd_push(["--hook"], io.StringIO(), io.StringIO()) == 0
    assert called is False


def test_cmd_push_noncanonical_git_push_remains_blocked(
    tmp_path: Path, monkeypatch,
) -> None:
    feature = tmp_path / "feature"
    feature.mkdir()
    payload = {
        "cwd": str(feature),
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": f"cd '{feature}' && git push --force origin main"},
    }
    err = io.StringIO()

    monkeypatch.setattr(loom_checker, "read_hook_payload", lambda: payload)

    assert loom_checker.cmd_push(["--hook"], io.StringIO(), err) == 2
    assert "canonical quote-all rendering" in err.getvalue()
