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


def _raw_text() -> str:
    return CLAUDE_TOOLS.read_text(encoding="utf-8")


def _normalized_adapter() -> str:
    return re.sub(r"\s+", " ", _raw_text()).strip()


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _window(raw: str, start_heading: str, end_heading: str) -> str:
    """Raw-text slice from `start_heading` up to (not including) `end_heading`."""
    start = raw.index(start_heading)
    end = raw.index(end_heading, start)
    return raw[start:end]


def _adapter_window() -> str:
    """The whole Review-context adapter section (both subsections)."""
    return _norm(_window(_raw_text(), "## Review-context adapter", "## Subagent dispatch"))


def _root_derivation_window() -> str:
    """Just the root-derivation steps, before post-fix confirmation."""
    return _norm(
        _window(
            _raw_text(),
            "## Review-context adapter",
            "### Claude post-fix confirmation",
        )
    )


def _post_fix_window() -> str:
    """Just the post-fix confirmation subsection."""
    return _norm(
        _window(_raw_text(), "### Claude post-fix confirmation", "## Subagent dispatch")
    )


def test_claude_adapter_resolves_and_forwards_immutable_review_context() -> None:
    """Claude resolves its installed script and forwards its packet unchanged.

    A bare `immutable` or `verbatim` is NOT a usable pin here: inside
    `_adapter_window()` this file says `immutable` three times and `verbatim`
    twice, so deleting either rule leaves a sibling occurrence satisfying the
    check. The anchors below are the shortest phrases that occur exactly once
    in that window, which is what makes deleting the rule fail the test.

    Cardinality ("once per review attempt") is pinned separately below: it is
    an invariant, not phrasing -- how many times the resolver runs decides
    whether every station shares one packet.
    """
    text = _normalized_adapter()
    window = _norm(_adapter_window())

    assert "## Review-context adapter" in text
    assert 'python3 "${derived_plugin_root}/scripts/review_context.py" --repo <target_repo>' in text
    assert "unchanged immutable context packet" in window
    assert "once per review attempt" in window
    assert "do not derive plugin paths from `target_repo`" in text.lower()

    for field in ("target_repo", "reviewed_sha", "plugin_version", "resources"):
        assert field in text

    assert "Copy the packet verbatim into every downstream station" in window


def test_claude_same_reviewer_confirmation_uses_full_packet_and_ordinary_verdict() -> None:
    """Claude's transport preserves the portable packet and agent boundary."""
    text = _normalized_adapter()
    post_fix = _post_fix_window()

    assert "SendMessage" in text
    assert "same reviewer" in text
    assert "fresh post-fix SHA" in text
    # `fresh` occurs 5x and `immutable` 2x inside _post_fix_window(), and the
    # conjunction did not require them to be adjacent -- deleting the rule
    # left the pair satisfied by unrelated occurrences. This phrase occurs once.
    assert "fresh immutable context packet" in _norm(post_fix)
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
    """A post-fix packet equal to round one cannot reach any terminal action.

    "do not create a wrapper verdict" / "do not mint a marker" are this
    repo's control vocabulary for the no-fabricated-marker rule (same terms
    used across the marker-minting contracts elsewhere in loom-code), so
    they are pinned as keywords inside the post-fix window rather than as a
    transcribed sentence.
    """
    text = _normalized_adapter()
    post_fix = _post_fix_window()

    assert "initial round `reviewed_sha`" in text
    assert "post-fix packet `reviewed_sha` equals the initial round `reviewed_sha`" in text
    assert "REFUSE confirmation" in text
    assert "wrapper verdict" in post_fix
    assert "mint a marker" in post_fix
    assert "commit the fix" in text.lower()


def test_claude_adapter_root_is_bound_to_the_loaded_reference() -> None:
    """Claude derives a root from its loaded file; the host value only checks it.

    "absolute path of the loaded reference file" and "compare the two
    canonical absolute paths" transcribed the same "canonicalize before
    comparing" invariant already pinned below via `canonical absolute path`
    -- deleted as duplicate phrasing, not a distinct check. "never a path
    source" transcribed the same env-var-is-not-authoritative invariant
    already pinned via `cross-check only` -- deleted for the same reason.
    """
    text = _normalized_adapter()
    root_window = _root_derivation_window()

    assert "walk upward until the directory named `loom-code`" in text
    assert "derived_plugin_root" in text
    assert "canonical absolute path" in text
    assert "canonicalize `claude_plugin_root` to an absolute path" in text.lower()
    assert "`CLAUDE_PLUGIN_ROOT` is missing or differs from `derived_plugin_root`" in text
    assert "REFUSE" in text
    assert "cross-check only" in text
    assert '${CLAUDE_PLUGIN_ROOT}/scripts/review_context.py' not in text
    assert "cache layout" in root_window.lower()
