"""Pre-flight safety gates for the nightly Phase 2 loop.

Three deterministic, side-effect-free checks the unattended routine runs
BEFORE it touches anything:

- ``is_nightly_paused``            — kill switch (read-only sentinel file)
- ``requires_real_agent_surface`` — scope guard (fail-closed keyword check)
- ``assert_safe_target_branch``   — branch guard (owned-namespace allowlist)

See docs/loom/specs/2026-07-11-u1-nightly-phase2-loop.md.
"""

import re
from pathlib import Path

# Signals that a backlog item needs the metered real-headless-agent eval
# surface (W1/G1/G2/G3), which this loop must refuse. Matched as case-folded
# substrings; over-matching is the SAFE direction — a false positive means a
# human scopes the item, a false negative means an unattended run silently
# burns quota. Fail closed: refuse rather than guess.
_REAL_AGENT_SIGNALS = (
    "claude -p",
    "headless",
    "real agent",
    "real-headless-agent",
    "e2e run",
    "e2e-run",
    "quota",
    "metered",
    "live model",
    "live api",
    "live-api",
    "llm call",
    "llm-judge",
    "invoke claude",
)

# Bare single words too generic for plain substring matching — "eval" is a
# substring of the in-domain term "retrieval" (e.g. query's tiered-retrieval
# design), and "agent" appears constantly in descriptive prose ("blind
# agent") unrelated to invoking one. Word-boundary regex keeps the fail-closed
# intent (still catches standalone "agent"/"eval"/"eval loop") without
# false-positiving on words that merely contain them.
_REAL_AGENT_WORD_SIGNALS = re.compile(r"\b(?:agent|eval)\b")

# The routine may commit ONLY inside its own branch namespace. An allowlist
# (not a denylist of human prefixes) is the strongest guarantee it never
# collides with a human-owned branch, whatever that branch happens to be named.
_OWNED_BRANCH_PREFIX = "nightly/"
_BASE_BRANCHES = frozenset({"main", "master"})


def is_nightly_paused(sentinel_path: Path) -> bool:
    """Return True iff the kill-switch sentinel file exists.

    The routine only ever READS this file — kouko toggles the pause by
    committing/removing it, so its git history is the audit log. This check
    must never create the file.
    """
    return Path(sentinel_path).exists()


def requires_real_agent_surface(item_description: str) -> bool:
    """Return True if a backlog item looks like it needs the real-agent surface.

    Deterministic, case-insensitive substring match. Fail closed: anything
    gesturing at agent/eval invocation is refused rather than guessed.
    """
    text = item_description.casefold()
    if any(signal in text for signal in _REAL_AGENT_SIGNALS):
        return True
    return _REAL_AGENT_WORD_SIGNALS.search(text) is not None


def assert_safe_target_branch(branch_name: str) -> None:
    """Raise ValueError unless ``branch_name`` is inside the loop's own namespace.

    Guards against the routine ever committing onto ``main``/``master`` or a
    human-owned feature branch (e.g. ``feat/dbt-wiki-w1-l2-e2e-harness``). The
    routine owns the ``nightly/`` namespace exclusively; everything else is
    rejected.
    """
    name = branch_name.strip()
    if name in _BASE_BRANCHES:
        raise ValueError(
            f"refusing to target base branch {name!r}: the nightly routine "
            f"commits only inside its own {_OWNED_BRANCH_PREFIX!r} namespace"
        )
    if not name.startswith(_OWNED_BRANCH_PREFIX):
        raise ValueError(
            f"refusing to target {name!r}: the nightly routine may only commit "
            f"to branches under {_OWNED_BRANCH_PREFIX!r} (never a human-owned branch)"
        )
