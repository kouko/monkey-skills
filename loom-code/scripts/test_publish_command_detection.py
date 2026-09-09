"""Regression coverage for publication command classification."""
from __future__ import annotations

import loom_checker


def test_quoted_rg_pattern_is_not_a_publisher() -> None:
    command = (
        'rg -n "SEGMENT_SPLIT|publisher&&gh pr create|gh pr merge" '
        "loom-code -g '*.py'"
    )

    assert not loom_checker.is_push_command(command)
    assert not loom_checker.is_pr_create_command(command)
    assert not loom_checker.is_pr_merge_command(command)


def test_real_publishers_remain_detected() -> None:
    commands = [
        "git push origin HEAD",
        "gh pr create --fill",
        "gh pr merge 123 --squash",
        "zsh -c 'git push origin HEAD'",
        "eval 'gh pr create --fill'",
    ]

    assert all(loom_checker.is_push_command(command) for command in commands)


def test_unbalanced_quote_keeps_conservative_detection() -> None:
    assert loom_checker.is_push_command("rg -n 'needle|gh pr create")


def test_dynamic_command_substitution_keeps_conservative_detection() -> None:
    assert loom_checker.is_push_command('echo "$(true | gh pr create --fill)"')
    assert loom_checker.is_push_command('echo "`true | git push origin HEAD`"')
    assert loom_checker.is_push_command('echo "`true | gh pr create --fill`"')


def test_single_quoted_backticks_remain_literal() -> None:
    command = "rg -n '`true | gh pr create --fill`' docs"

    assert not loom_checker.is_push_command(command)
    assert not loom_checker.is_pr_create_command(command)
