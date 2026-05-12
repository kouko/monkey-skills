"""S2 register preservation gate.

LLM judge call asking: "What register is this target text? formal | neutral | warm | playful"
Compare returned register against intake-spec register. Mismatch → WARN
(or FAIL in audit mode per Decision #17).

Gate semantics:

- SHOULD in normal modes (faithful, localized, transcreation): mismatch → WARN
- HARD in audit mode: mismatch → FAIL (Decision #17 — translation-audit
  per-skill matrix promotes S2 to HARD across all modes).

Verdict shape (consistent with M1 / M2 / S1)::

    {"verdict": "PASS" | "WARN" | "FAIL" | "SKIPPED",
     "diff": str | None,
     "details": {"expected_register": str, "actual_register": str,
                 "reason": str | None}}

Spec: ``scripts/canonical/verification-gates.md`` §S2.

This module is independent of any skill folder (lives at plugin-level
``translation-toolkit/scripts/lib/``) and is therefore not subject to
the flat-skill-folder convention.
"""
from __future__ import annotations

from typing import Callable, Optional

REGISTERS = ["formal", "neutral", "warm", "playful"]


def s2_check(
    *,
    original_source: str,
    translated_v2: str,
    intake_register: str,
    llm_judge: Optional[Callable[[str], str]],
    is_audit_mode: bool = False,
) -> dict:
    """Run S2 register preservation gate.

    Args:
        original_source: source text (for context in the judge prompt; the
            current judge prompt does not include it but the parameter is
            kept for symmetry with sibling gates and future judge variants).
        translated_v2: improved target text from L3 IMPROVE step.
        intake_register: declared register from intake-spec; one of
            :data:`REGISTERS`. Unknown values trigger SKIPPED with a reason.
        llm_judge: callable that takes a structured prompt and returns one
            of :data:`REGISTERS` as a string. Pass ``None`` to SKIP
            gracefully (parallel to S1's ``subagent_dispatch=None`` path).
        is_audit_mode: ``True`` → upgrade WARN to FAIL (Decision #17).

    Verdict matrix:

        | mode    | judge result      | verdict |
        |---------|-------------------|---------|
        | normal  | matches intake    | PASS    |
        | normal  | differs           | WARN    |  (SHOULD)
        | audit   | matches intake    | PASS    |
        | audit   | differs           | FAIL    |  (HARD per #17)
        | any     | judge=None        | SKIPPED |
        | any     | unknown intake    | SKIPPED |
        | any     | judge garbage     | SKIPPED |

    Returns:
        Verdict dict per shape above.
    """
    if llm_judge is None:
        return {
            "verdict": "SKIPPED",
            "diff": None,
            "details": {"reason": "No LLM judge available"},
        }

    if intake_register not in REGISTERS:
        return {
            "verdict": "SKIPPED",
            "diff": None,
            "details": {
                "reason": (
                    f"Unknown register {intake_register!r}; "
                    f"expected one of {REGISTERS}"
                ),
            },
        }

    judge_prompt = (
        f"What register is this text? Answer with exactly ONE word from: "
        f"{' | '.join(REGISTERS)}\n\n"
        f"Text: {translated_v2}\n\n"
        f"Register:"
    )
    actual_register = llm_judge(judge_prompt).strip().lower()

    if actual_register not in REGISTERS:
        # Judge returned garbage; treat as SKIPPED so the gate never fakes
        # a verdict on an unparseable judge response.
        return {
            "verdict": "SKIPPED",
            "diff": None,
            "details": {
                "expected_register": intake_register,
                "actual_register": actual_register,
                "reason": f"Judge returned non-register value: {actual_register!r}",
            },
        }

    if actual_register == intake_register:
        return {
            "verdict": "PASS",
            "diff": None,
            "details": {
                "expected_register": intake_register,
                "actual_register": actual_register,
            },
        }

    # Mismatch — SHOULD-tier WARN, escalated to HARD FAIL in audit mode.
    verdict = "FAIL" if is_audit_mode else "WARN"
    return {
        "verdict": verdict,
        "diff": (
            f"register mismatch: expected '{intake_register}', "
            f"got '{actual_register}'"
        ),
        "details": {
            "expected_register": intake_register,
            "actual_register": actual_register,
        },
    }
