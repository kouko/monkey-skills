"""S1 back-translation gate.

REQUIRES subagent dispatch for blindness (correctness, not optimization).
The main context has already seen both source and v2; it cannot blindly
re-translate v2 → source. The dispatched subagent gets only v2 + the
target→source language pair, NO reference to the original source.

Per Decision #16 (spec): runtime without subagent capability gracefully
skips with audit-trail flag ``S1: SKIPPED (no isolation capability)``.

Per Decision #4 (spec): S1 is HARD (MUST) in transcreation mode, SHOULD
in faithful / literal / localized modes. ``translation-audit`` upgrades
S1 to HARD across all modes via ``is_audit_mode=True``.

Verdict shape (consistent with M1 / M2 gates in :mod:`scripts.lib.gates`)::

    {"verdict": "PASS" | "WARN" | "FAIL" | "SKIPPED",
     "diff": str | None,
     "details": {"similarity": float, "threshold": float,
                 "back_translation": str, "reason": str | None}}

Spec: ``scripts/canonical/verification-gates.md`` §S1.

This module is independent of any skill folder (lives at plugin-level
``translation-toolkit/scripts/lib/``) and is therefore not subject to
the flat-skill-folder convention.
"""
from __future__ import annotations

from typing import Callable, Optional


def make_blind_prompt(translated_v2: str, source_lang: str) -> str:
    """Build the back-translation prompt.

    Exported for subagents that construct prompts independently (e.g. when
    the dispatch wrapper handles its own prompt assembly). The prompt is
    deliberately spartan: the subagent must NOT receive the original
    source text — that would defeat the blindness guarantee.
    """
    return (
        f"Translate the following text to {source_lang}. "
        f"Output ONLY the translation, no commentary, no explanation.\n\n"
        f"{translated_v2}"
    )


def compute_semantic_similarity(a: str, b: str) -> float:
    """Embedding cosine similarity. STUB for v0.1 — returns a constant placeholder.

    TODO v0.2: integrate sentence-transformers (multilingual model) or an
    LLM-judge call asking for a 0–1 similarity score. Real embedding
    integration requires a model-dep decision (sentence-transformers
    ~500MB on disk) and is deferred to v0.2.

    For v0.1 this returns a deterministic stub:

    - ``0.0`` if either input is empty (forces WARN/FAIL on degenerate
      inputs so the gate's mode-conditional behavior is testable);
    - ``0.9`` otherwise (above the 0.85 default threshold so non-empty
      inputs trivially PASS).

    Callers should treat S1 PASS at v0.1 as advisory only until real
    similarity ships.
    """
    if not a or not b:
        return 0.0
    return 0.9  # stub — see TODO above


def s1_check(
    *,
    original_source: str,
    translated_v2: str,
    source_lang: str,
    subagent_dispatch: Optional[Callable[[str], str]],
    threshold: float = 0.85,
    transcreation_threshold: float = 0.70,
    is_transcreation: bool = False,
    is_audit_mode: bool = False,
) -> dict:
    """Run S1 back-translation gate.

    Args:
        original_source: source text. Used for similarity comparison only —
            **NOT** passed to ``subagent_dispatch``. Keeping this argument
            out of the subagent prompt is the entire point of the gate.
        translated_v2: improved target text from L3 IMPROVE step.
        source_lang: BCP-47 source language tag (back-translation target).
        subagent_dispatch: callable that takes a prompt string and returns
            the subagent's string output, blind to ``original_source``.
            Pass ``None`` if the runtime lacks isolation capability; the
            gate will SKIP gracefully per Decision #16.
        threshold: PASS cutoff for faithful / literal / localized modes
            (default ``0.85`` cosine similarity).
        transcreation_threshold: PASS cutoff for transcreation mode
            (default ``0.70`` — surface deviation expected, semantic
            anchor still required).
        is_transcreation: ``True`` → use ``transcreation_threshold`` AND
            promote the gate from SHOULD to MUST (Decision #4): a
            below-threshold similarity in transcreation is HARD FAIL, not
            WARN, because S1 is the primary semantic-fidelity anchor when
            surface deviation is expected.
        is_audit_mode: ``True`` → upgrade WARN to FAIL semantics across
            all modes (Decision #17): ``translation-audit`` treats every
            below-threshold S1 result as HARD per the per-skill matrix in
            ``verification-gates.md``.

    Verdict matrix (Decision #4 + #17 + verification-gates.md §S1):

        | mode          | similarity        | verdict |
        |---------------|-------------------|---------|
        | faithful      | ≥ 0.85            | PASS    |
        | faithful      | < 0.85            | WARN    |  (SHOULD)
        | transcreation | ≥ 0.70            | PASS    |
        | transcreation | < 0.70            | FAIL    |  (MUST per #4)
        | audit         | ≥ effective thr.  | PASS    |
        | audit         | < effective thr.  | FAIL    |  (HARD per #17)

    Returns:
        Verdict dict per shape above. ``details.similarity`` and
        ``details.threshold`` are always present when the gate ran;
        ``details.reason`` is set on SKIPPED.
    """
    if subagent_dispatch is None:
        return {
            "verdict": "SKIPPED",
            "diff": None,
            "details": {"reason": "No isolation capability available"},
        }

    # Construct blind prompt — no reference to original_source. The
    # subagent only sees v2 + the target language tag.
    backtrans_prompt = make_blind_prompt(translated_v2, source_lang)
    backtrans = subagent_dispatch(backtrans_prompt)

    similarity = compute_semantic_similarity(original_source, backtrans)
    effective_threshold = (
        transcreation_threshold if is_transcreation else threshold
    )

    passed = similarity >= effective_threshold
    if passed:
        verdict = "PASS"
    elif is_audit_mode or is_transcreation:
        # MUST-tier: HARD failure.
        # - is_audit_mode → translation-audit per-skill matrix
        #   (Decision #17): S1 escalated across all modes.
        # - is_transcreation → tier-flip per Decision #4 +
        #   verification-gates.md §S1: a back-translation that drops
        #   below 0.70 in transcreation indicates v2 has drifted
        #   off-topic, not just been re-styled.
        verdict = "FAIL"
    else:
        # SHOULD-tier in faithful / literal / localized modes — surface
        # the gap as WARN; output proceeds.
        verdict = "WARN"

    diff = None if passed else (
        f"similarity {similarity:.2f} < threshold {effective_threshold:.2f}"
    )

    return {
        "verdict": verdict,
        "diff": diff,
        "details": {
            "similarity": similarity,
            "threshold": effective_threshold,
            "back_translation": backtrans,
        },
    }
