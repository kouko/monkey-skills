"""Stage-C verdict mapper for the fact-check skill.

Maps a list of voter verdicts (each a VERDICT_SCHEMA dict, or None = abstain)
to the 3-way taxonomy used by the fact-check report:

    supported     — the claim survives the adversarial quorum
                    (rank.quorum_survives: >=2 valid votes, <2 refute).
    refuted       — >=REFUTATIONS_REQUIRED valid votes carry refuted=True.
    inconclusive  — anything else: all-abstain, <2 valid votes, empty input
                    (no evidence found). Guards the false-survive bug.

Pure logic; stdlib only. Reuses deep-research's quorum rule + constants via
flat imports of the copied primitives (no synthesis import — self-contained).

CLI (consumed by SKILL.md over stdin/stdout JSON):
    python factcheck.py verdict   # stdin: verdicts JSON array -> stdout: verdict object JSON
"""

from __future__ import annotations

from typing import Any

from rank import quorum_survives
from schemas import REFUTATIONS_REQUIRED, VOTES_PER_CLAIM  # noqa: F401 (VOTES_PER_CLAIM re-exported for callers)

# Confidence ranking: lower index = stronger. Mirrors the deep-research
# synthesis ordering, kept self-contained here on purpose.
_CONFIDENCE_ORDER = ["high", "medium", "low"]


def _best_confidence(verdicts: list[dict[str, Any]], *, refuting: bool) -> str:
    """Best (strongest) confidence among the verdicts that drove the result.

    `refuting=False` → look at non-refuting valid votes (supports the
    `supported` verdict). `refuting=True` → look at the refuting valid votes
    (the votes that drove a `refuted` verdict). This makes confidence
    DIRECTION-AWARE: a unanimous strong refutation reports high confidence,
    not the "low" fallback.

    Returns "low" when there are no votes in the requested direction.
    """
    candidates = [
        v.get("confidence", "low")
        for v in verdicts
        if v is not None and bool(v["refuted"]) == refuting
    ]
    if not candidates:
        return "low"
    return min(candidates, key=lambda c: _CONFIDENCE_ORDER.index(c)
               if c in _CONFIDENCE_ORDER else len(_CONFIDENCE_ORDER))


def classify_verdict(verdicts: list[dict[str, Any] | None]) -> dict[str, Any]:
    """Map voter verdicts to {verdict, confidence, valid_count, refuted_count}.

    - `supported` when quorum_survives is True (>=2 valid, <2 refute).
    - `refuted` when >=REFUTATIONS_REQUIRED valid votes have refuted=True.
    - `inconclusive` otherwise (all-abstain / <2 valid / empty input).

    confidence is DIRECTION-AWARE: for `supported` it is the best non-refuting
    valid confidence; for `refuted` it is the best confidence among the
    refuting votes that drove the verdict; for `inconclusive` it is "low".
    """
    valid = [v for v in (verdicts or []) if v is not None]
    refuted_count = sum(1 for v in valid if v["refuted"])

    if quorum_survives(verdicts or []):
        verdict = "supported"
        confidence = _best_confidence(valid, refuting=False)
    elif refuted_count >= REFUTATIONS_REQUIRED:
        verdict = "refuted"
        confidence = _best_confidence(valid, refuting=True)
    else:
        verdict = "inconclusive"
        confidence = "low"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "valid_count": len(valid),
        "refuted_count": refuted_count,
    }


def main(argv: list[str] | None = None) -> int:
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or args[0] != "verdict":
        name = args[0] if args else "(none)"
        print(f"unknown subcommand {name!r}; expected 'verdict'", file=sys.stderr)
        return 1

    data = json.load(sys.stdin)
    print(json.dumps(classify_verdict(data)))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
