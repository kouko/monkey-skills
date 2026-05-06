"""I1 untranslatability flagging gate.

Heuristic detection of how each Layer-2-source-analysis-flagged untranslatable
phrase was handled in the target. Decisions:

- ``borrow`` — phrase appears verbatim in target.
- ``explain`` — phrase appears verbatim WITH a parenthetical / footnote
  nearby (heuristic: ``(`` or ``（`` within ~50 chars after the phrase).
- ``approximate`` — phrase NOT in target, but at least one candidate
  alternative from source-analysis appears in target.
- ``unknown`` — phrase not in target and no candidate matched.

Per spec line 405-407: I1 is **INFO-only** and **non-interactive**. It
records decisions in the audit trail; it does NOT block output and does
NOT prompt the user. This contrasts with M1/M2 (HARD) and S1/S2 (SHOULD
escalating in audit).

Verdict shape (consistent with M1 / M2 / S1 / S2)::

    {"verdict": "INFO" | "PASS" | "SKIPPED",
     "diff": None,
     "details": {"flags": [{"phrase", "decision", "target_excerpt",
                            "alternatives"}, ...]}}

Where verdict:

- ``INFO`` — at least one untranslatable was flagged; ``details.flags``
  lists each handling decision for audit-trail review.
- ``PASS`` — source-analysis returned no untranslatables to evaluate
  (nothing to flag, nothing to record).
- ``SKIPPED`` — source-analysis structure unavailable (caller must record
  the skip in the audit trail).

Spec: ``scripts/canonical/verification-gates.md`` §I1.

This module is independent of any skill folder (lives at plugin-level
``translation-toolkit/scripts/lib/``) and is therefore not subject to
the flat-skill-folder convention.
"""
from __future__ import annotations


def i1_check(
    *,
    source_analysis: dict | None,
    target: str,
) -> dict:
    """Run I1 untranslatability flagging gate.

    Args:
        source_analysis: dict from Layer 2 source-analysis with key
            ``untranslatables`` (list of ``{phrase, category, candidates}``).
            Pass ``None`` if source-analysis is unavailable for this run.
        target: the v2 translated text.

    Returns:
        Verdict dict per shape above.
    """
    if source_analysis is None:
        return {
            "verdict": "SKIPPED",
            "diff": None,
            "details": {"reason": "No source-analysis available"},
        }

    untranslatables = source_analysis.get("untranslatables") or []
    if not untranslatables:
        return {"verdict": "PASS", "diff": None, "details": {"flags": []}}

    flags = []
    for entry in untranslatables:
        phrase = entry.get("phrase", "")
        if not phrase:
            # Defensive: skip degenerate entries rather than emit a flag
            # with empty phrase that downstream consumers can't display.
            continue
        candidates = entry.get("candidates", []) or []
        decision = _detect_handling(phrase, target, candidates)
        flags.append({
            "phrase": phrase,
            "decision": decision,
            "target_excerpt": _extract_target_excerpt(phrase, target),
            "alternatives": candidates,
        })

    return {
        "verdict": "INFO",
        "diff": None,
        "details": {"flags": flags},
    }


def _detect_handling(phrase: str, target: str, candidates: list[str]) -> str:
    """Heuristic: how was the phrase handled in target?

    Returns one of: ``borrow`` / ``explain`` / ``approximate`` / ``unknown``.

    The ``explain`` heuristic checks for either an ASCII ``(`` or fullwidth
    ``（`` within 50 characters after the phrase — a reasonable approximation
    of a translator's parenthetical gloss without requiring NLP. Both
    parens are checked because Japanese / Chinese targets predominantly
    use the fullwidth form.
    """
    if not target:
        return "unknown"
    if phrase in target:
        # Borrow vs explain: check for parenthetical gloss within 50 chars.
        idx = target.find(phrase)
        suffix = target[idx + len(phrase): idx + len(phrase) + 50]
        if "(" in suffix or "（" in suffix:
            return "explain"
        return "borrow"
    for cand in candidates:
        if cand and cand in target:
            return "approximate"
    return "unknown"


def _extract_target_excerpt(phrase: str, target: str, ctx: int = 30) -> str:
    """Pull a short window around the first phrase occurrence.

    Returns empty string if the phrase is not present in the target
    (the ``approximate`` / ``unknown`` cases). Window is symmetric:
    ``ctx`` chars before + phrase + ``ctx`` chars after.
    """
    idx = target.find(phrase)
    if idx < 0:
        return ""
    start = max(0, idx - ctx)
    end = min(len(target), idx + len(phrase) + ctx)
    return target[start:end]
