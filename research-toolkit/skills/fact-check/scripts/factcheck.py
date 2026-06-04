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


def classify_verdict(
    verdicts: list[dict[str, Any] | None],
    *,
    no_referent: bool = False,
    independent_fanout: bool = True,
) -> dict[str, Any]:
    """Map voter verdicts to {verdict, reason, confidence, valid_count, refuted_count}.

    - `supported` when quorum_survives is True (>=2 valid, <2 refute).
    - `refuted` when >=REFUTATIONS_REQUIRED valid votes have refuted=True.
    - `inconclusive` otherwise (all-abstain / <2 valid / empty input).

    `reason` discriminates the verdict so the caller can phrase the user-facing
    answer (the verdict label alone is too coarse — an `inconclusive` from a
    fabricated entity reads very differently from one on a real-but-thin topic):

    - `quorum-survived` / `quorum-refuted` — drove `supported` / `refuted`.
    - `no-quorum` — `independent_fanout=False` AND votes were cast: the quorum's
      integrity rests on INDEPENDENT voters (parallel subagents, or sequential
      FRESH contexts). When the host could only reason in a single shared
      context, the three "votes" are not independent, so they cannot drive
      `supported`/`refuted` — a non-independent quorum is not a quorum (F-004).
      The verdict is forced to `inconclusive`; the caller should say so plainly.
    - `no-referent` — `no_referent=True` AND the quorum could not decide: Stage
      A found the claim's named entity/event has ZERO footprint, so absence is
      itself disconfirming (F-003). The verdict stays `inconclusive` (0 valid
      votes is math-true), but the caller should surface "no trace found —
      likely fabricated", NOT a neutral "undecided".
    - `insufficient-evidence` — inconclusive on a real topic (thin / all-abstain
      / <2 valid votes): genuine epistemic suspension.

    Neither flag can manufacture a verdict: `no_referent` only labels the
    empty-evidence bucket; `independent_fanout=False` only INVALIDATES a quorum,
    never creates one. The solo gate fires only when >=2 valid votes WOULD have
    formed a quorum; with fewer it is moot (a sub-quorum was never a quorum), so
    those cases fall through to the evidence-sufficiency reasons.

    confidence is DIRECTION-AWARE: for `supported` it is the best non-refuting
    valid confidence; for `refuted` it is the best confidence among the
    refuting votes that drove the verdict; for `inconclusive` it is "low".
    """
    valid = [v for v in (verdicts or []) if v is not None]
    refuted_count = sum(1 for v in valid if v["refuted"])

    if not independent_fanout and len(valid) >= REFUTATIONS_REQUIRED:
        # A quorum WOULD have formed (>=2 valid votes) but they came from a
        # single shared context, so its independence precondition fails and it
        # cannot conclude. Fewer than 2 valid votes were never a quorum, so the
        # solo flag has nothing to invalidate — those fall through to the
        # evidence-sufficiency reasons below.
        verdict = "inconclusive"
        reason = "no-quorum"
        confidence = "low"
    elif quorum_survives(verdicts or []):
        verdict = "supported"
        reason = "quorum-survived"
        confidence = _best_confidence(valid, refuting=False)
    elif refuted_count >= REFUTATIONS_REQUIRED:
        verdict = "refuted"
        reason = "quorum-refuted"
        confidence = _best_confidence(valid, refuting=True)
    else:
        verdict = "inconclusive"
        reason = "no-referent" if no_referent else "insufficient-evidence"
        confidence = "low"

    return {
        "verdict": verdict,
        "reason": reason,
        "confidence": confidence,
        "valid_count": len(valid),
        "refuted_count": refuted_count,
    }


def main(argv: list[str] | None = None) -> int:
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] != "verdict":
        name = args[0] if args else "(none)"
        print(f"unknown subcommand {name!r}; expected 'verdict'", file=sys.stderr)
        return 1
    rest = args[1:]
    no_referent = "--no-referent" in rest
    solo = "--solo" in rest
    extra = [a for a in rest if a not in ("--no-referent", "--solo")]
    if extra:
        print(f"unexpected argument(s): {' '.join(extra)}", file=sys.stderr)
        return 1

    data = json.load(sys.stdin)
    print(json.dumps(
        classify_verdict(data, no_referent=no_referent, independent_fanout=not solo)
    ))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
