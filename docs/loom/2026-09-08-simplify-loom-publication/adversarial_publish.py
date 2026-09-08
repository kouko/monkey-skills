#!/usr/bin/env python3
"""Adversarial checks for the one-command Loom publication boundary."""

from __future__ import annotations

import inspect
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
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

    source = inspect.getsource(loom_checker.cmd_publish)
    assert "shell=True" not in source
    assert "check_probes" not in source
    assert "declared_test_command" not in source
    assert "--force" not in source
    assert "--force-with-lease" not in source
    assert '["--head", head, "--require-live-head"]' in source
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
