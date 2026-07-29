"""Pre-flight safety gates for the Phase 2 loop.

Two deterministic, side-effect-free checks the unattended routine runs
BEFORE it touches anything:

- ``is_nightly_paused``            — kill switch (read-only sentinel file)
- ``requires_real_agent_surface`` — scope guard (fail-closed keyword check)

See docs/loom/specs/2026-07-28-phase2-loop-execution-only.md.
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
