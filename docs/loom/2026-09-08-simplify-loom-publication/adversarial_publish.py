#!/usr/bin/env python3
"""Adversarial checks for the one-command Loom publication boundary."""

from __future__ import annotations

import inspect
import os
import subprocess
import sys
import tempfile
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = Path(__file__).resolve()
sys.path.insert(0, str(ROOT / "loom-code/scripts"))

import loom_checker  # noqa: E402


def main() -> int:
    attacks = [
        ["--confirm-authorized", "--repo", "attacker/repo"],
        ["--confirm-authorized", "--base", "attacker"],
        ["--confirm-authorized", "--head", "main"],
        ["--confirm-authorized", "--remote", "upstream"],
        ["--confirm-authorized", "--hostname", "evil.example"],
        ["--confirm-authorized", "--force"],
        ["--confirm-authorized", "--body-file", "relative.md"],
    ]
    for attack in attacks:
        assert isinstance(loom_checker._publish_args(attack), str), attack

    assert isinstance(loom_checker._publish_args([]), str)
    assert "GH_REPO" in loom_checker.PUBLISH_REDIRECT_ENV
    assert "GIT_DIR" in loom_checker.PUBLISH_REDIRECT_ENV
    assert "GIT_SSH_COMMAND" in loom_checker.PUBLISH_REDIRECT_ENV

    source = inspect.getsource(loom_checker.cmd_publish) + inspect.getsource(
        loom_checker._cmd_publish_trusted
    )
    assert "shell=True" not in source
    assert "check_probes" not in source
    assert "declared_test_command" not in source
    assert "--force" not in source
    assert "--force-with-lease" not in source
    assert '["--head", head, "--require-live-head"]' in source

    external = loom_checker.run_publish_external
    resolver = loom_checker.resolve_publish_executable
    cwd = Path.cwd()
    try:
        def forbid_network(*args, **kwargs):
            raise AssertionError("stale attestation reached a network command")

        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "config", "user.email", "probe@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "config", "user.name", "Probe"], check=True
            )
            (repo / "probe.txt").write_text("probe\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "probe.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-q", "-m", "probe"], check=True
            )
            subprocess.run(["git", "-C", str(repo), "branch", "-M", "main"], check=True)
            subprocess.run(["git", "-C", str(repo), "switch", "-q", "-c", "probe"], check=True)
            (repo / "probe.txt").write_text("probe changed\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "probe.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-q", "-m", "probe change"], check=True
            )
            subprocess.run(
                ["git", "-C", str(repo), "remote", "add", "origin",
                 "git@github.com:example/probe.git"],
                check=True,
            )
            loom_checker.run_publish_external = forbid_network
            loom_checker.resolve_publish_executable = lambda _name: "/usr/bin/git"
            os.chdir(repo)
            error = StringIO()
            rc = loom_checker.cmd_publish([
                "--confirm-authorized", "--title", "feat(loom): adversarial",
                "--body-file", str(SCRIPT),
            ], StringIO(), error)
            assert rc == 1
            assert "branch must carry exactly one generated attestation; found 0" in error.getvalue()
    finally:
        os.chdir(cwd)
        loom_checker.run_publish_external = external
        loom_checker.resolve_publish_executable = resolver
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
