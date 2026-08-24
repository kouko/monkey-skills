"""Contract pins for Claude Code's portable review-context adapter."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_TOOLS = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "using-loom-code"
    / "references"
    / "claude-code-tools.md"
)


def _normalized_adapter() -> str:
    return re.sub(r"\s+", " ", CLAUDE_TOOLS.read_text(encoding="utf-8")).strip()


def test_claude_adapter_resolves_and_forwards_immutable_review_context() -> None:
    """Claude resolves its installed script once and forwards its packet unchanged."""
    text = _normalized_adapter()

    assert "## Review-context adapter" in text
    assert 'python3 "${derived_plugin_root}/scripts/review_context.py" --repo <target_repo>' in text
    assert "once per review attempt" in text
    assert "unchanged immutable context packet" in text
    assert "do not derive plugin paths from `target_repo`" in text.lower()

    for field in ("target_repo", "reviewed_sha", "plugin_version", "resources"):
        assert field in text

    assert "copy the packet verbatim" in text.lower()


def test_claude_same_reviewer_confirmation_uses_full_packet_and_ordinary_verdict() -> None:
    """Claude's transport preserves the portable packet and agent boundary."""
    text = _normalized_adapter()

    assert "SendMessage" in text
    assert "same reviewer" in text
    assert "fresh post-fix SHA" in text
    assert "fresh immutable context packet" in text
    assert "not the pre-fix `reviewed_sha`" in text
    assert "original gating findings" in text
    assert "delta evidence" in text
    assert "ordinary three-valued verdict" in text
    assert "orchestrator maps" in text
    assert "delta only" not in text
    assert "it returns `confirmed_resolved` or `still_blocking`" not in text.lower()
    assert "echoes the fresh packet `reviewed_sha`" in text
    assert "terminal evidence only" in text


def test_claude_confirmation_refuses_unchanged_reviewed_sha() -> None:
    """A post-fix packet equal to round one cannot reach any terminal action."""
    text = _normalized_adapter()

    assert "initial round `reviewed_sha`" in text
    assert "post-fix packet `reviewed_sha` equals the initial round `reviewed_sha`" in text
    assert "REFUSE confirmation" in text
    assert "do not create a wrapper verdict" in text
    assert "do not mint a marker" in text
    assert "commit the fix" in text.lower()


def test_claude_adapter_root_is_bound_to_the_loaded_reference() -> None:
    """Claude derives a root from its loaded file; the host value only checks it."""
    text = _normalized_adapter()

    assert "absolute path of the loaded reference file" in text
    assert "walk upward until the directory named `loom-code`" in text
    assert "derived_plugin_root" in text
    assert "canonical absolute path" in text
    assert "canonicalize `claude_plugin_root` to an absolute path" in text.lower()
    assert "compare the two canonical absolute paths" in text
    assert "`CLAUDE_PLUGIN_ROOT` is missing or differs from `derived_plugin_root`" in text
    assert "REFUSE" in text
    assert "cross-check only" in text
    assert "never a path source" in text
    assert '${CLAUDE_PLUGIN_ROOT}/scripts/review_context.py' not in text
    assert "do not infer it from a cache layout" in text.lower()
