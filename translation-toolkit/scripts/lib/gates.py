"""Verification gates M1 (placeholder integrity) and M2 (project glossary compliance).

Runtime library used by translation-toolkit skills (translation-i18n,
translation-doc, translation-creative, translation-audit) to score a
chunk's IMPROVE-pass output against the M1 + M2 hard gates.

Spec: ``scripts/canonical/verification-gates.md`` §M1 / §M2.

M1 wraps the regex-counted placeholder-set check (the primitive
``protect_pass.verify_count`` only does count parity; M1 here checks the
*set* of token IDs so it can name missing/extra tokens in its diff).

M2 is a fresh implementation: scan source for known glossary terms in
the active domain; verify each appears in target with its prescribed
translation; entries flagged ``context-dependent`` in notes downgrade
to ``PASS_ADVISORY`` instead of ``FAIL``.

Verdict shape (uniform across all gates per spec §Audit-trail entry format)::

    {
        "verdict": "PASS" | "FAIL" | "PASS_ADVISORY" | "WARN" | "SKIPPED",
        "diff": str | None,           # human-readable failure summary; None on PASS
        "details": dict | None,       # optional structured details
    }

This module is independent of any skill folder (lives at plugin-level
``translation-toolkit/scripts/lib/``) and is therefore not subject to
the flat-skill-folder convention.
"""
from __future__ import annotations

import re

# Match any well-formed placeholder token regardless of digit width
# (current protect-pass output uses zero-padded 2-digit, but auto-widens
# past 99 — keep this pattern width-agnostic for forward compatibility).
_TOKEN_RE = re.compile(r"⟦P:\d+⟧")

# Cache of compiled word-boundary patterns for ASCII glossary terms.
# Glossaries are small and process-lived, so unbounded growth is fine.
_WORD_BOUND_CACHE: dict[str, re.Pattern[str]] = {}


def _term_in_source(term: str, src_lower: str) -> bool:
    """Detect whether ``term`` appears in already-lowercased ``src_lower``.

    ASCII terms (e.g. ``cancel``) use word-boundary regex to avoid false
    positives from substrings (``cancellation``, ``cancelled``).
    CJK terms (e.g. ``取消``) use plain substring matching — CJK scripts
    have no whitespace word boundaries, so ``\\b`` would never match.

    Branching on ``isascii()`` is the cheapest reliable proxy for "this
    script has Latin-style word-boundary semantics" without dragging
    Unicode-aware tokenisation into the runtime.
    """
    t = term.lower()
    if t.isascii():
        pat = _WORD_BOUND_CACHE.get(t)
        if pat is None:
            pat = re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)
            _WORD_BOUND_CACHE[t] = pat
        return bool(pat.search(src_lower))
    return t in src_lower


# --------------------------------------------------------------------------- #
# M1 — Placeholder integrity                                                  #
# --------------------------------------------------------------------------- #


def m1_check(target: str, source_token_map: dict[str, str]) -> dict:
    """M1 — placeholder integrity. HARD gate.

    Compare the set of ``⟦P:NN⟧`` tokens in ``target`` against the keys of
    ``source_token_map`` (which is the masked-token map produced by
    :func:`scripts.lib.protect_pass.protect`).

    Returns:
        Verdict dict::

            {"verdict": "PASS", "diff": None, "details": None}

        on a clean match, or::

            {"verdict": "FAIL",
             "diff": "missing: [...]; extra: [...]",
             "details": {"missing": [...], "extra": [...]}}

        when at least one token is missing or extra.

    Why HARD: a missing placeholder = broken software (lost variable
    substitution at runtime, broken inline link, lost code reference).
    """
    expected = set(source_token_map.keys())
    actual = set(_TOKEN_RE.findall(target))
    if actual == expected:
        return {"verdict": "PASS", "diff": None, "details": None}

    missing = expected - actual
    extra = actual - expected
    parts = []
    if missing:
        parts.append(f"missing: {sorted(missing)}")
    if extra:
        parts.append(f"extra: {sorted(extra)}")
    return {
        "verdict": "FAIL",
        "diff": "; ".join(parts),
        "details": {"missing": sorted(missing), "extra": sorted(extra)},
    }


# --------------------------------------------------------------------------- #
# M2 — Project glossary compliance                                             #
# --------------------------------------------------------------------------- #


def m2_check(
    source: str,
    target: str,
    project_glossary: dict[tuple[str, str], str],
    domain: str,
    notes: dict[tuple[str, str], str] | None = None,
) -> dict:
    """M2 — project glossary compliance. HARD gate (with advisory escape).

    For each entry ``(term, term_domain) -> expected_translation`` in
    ``project_glossary`` where ``term_domain == domain``:

      * If ``term`` does not appear in ``source``, skip — the glossary rule
        is not in scope for this chunk. ASCII terms use word-boundary
        matching (so ``cancel`` does NOT match ``cancellation``); CJK terms
        use substring matching (no word boundaries in CJK scripts).
      * If ``expected_translation`` appears in ``target``, the entry is
        compliant.
      * Otherwise, record a violation. If ``notes[(term, term_domain)]``
        contains the substring ``"context-dependent"`` (case-insensitive),
        the violation is downgraded to advisory; otherwise it is strict.

    Known limitation (v0.1): ``expected_translation in target`` is a literal
    substring check — a target containing ``未確認`` ("not confirmed") would
    falsely PASS for an expected ``確認`` because the literal characters are
    present even though the meaning is reversed. Negation detection (``未``
    / ``非`` / ``不`` / ``無`` ...) requires NLP beyond simple string match
    and is deferred to v0.2. Documented in
    ``scripts/canonical/verification-gates.md`` §M2.

    Verdicts:
        * **PASS** — no violations and no advisories.
        * **PASS_ADVISORY** — only context-dependent advisory hits;
          caller should surface the deviation in the audit trail but
          allow output.
        * **FAIL** — at least one strict violation; ``diff`` lists the
          offending terms and their expected translations.

    Args:
        source: original source text (pre-translation).
        target: target text (post-IMPROVE).
        project_glossary: mapping ``(term, domain) -> expected_translation``.
            Both ``term`` and ``domain`` are matched as supplied; ``term``
            matching against source is case-insensitive.
        domain: active domain (e.g. ``"ui"``); only entries whose
            ``term_domain`` equals this value are checked. Domain matching
            is exact — ``"tech.crypto"`` does NOT fall back to
            ``"tech.software"``.
        notes: optional ``(term, domain) -> note_string`` map. The
            substring ``"context-dependent"`` (case-insensitive) flips the
            entry from strict to advisory.

    Returns:
        Verdict dict in the uniform ``{verdict, diff, details}`` shape.
    """
    notes = notes or {}
    violations: list[str] = []
    advisory: list[str] = []
    src_lower = source.lower()

    for (term, term_domain), expected_translation in project_glossary.items():
        if term_domain != domain:
            continue
        if not _term_in_source(term, src_lower):
            # Term is not in scope for this chunk — skip silently.
            continue
        if expected_translation in target:
            # Compliant.
            continue
        note = notes.get((term, term_domain), "")
        msg = f"'{term}' should translate to '{expected_translation}'"
        if "context-dependent" in note.lower():
            advisory.append(msg)
        else:
            violations.append(msg)

    if violations:
        return {
            "verdict": "FAIL",
            "diff": "; ".join(violations),
            "details": {"violations": violations, "advisory": advisory},
        }
    if advisory:
        return {
            "verdict": "PASS_ADVISORY",
            "diff": "; ".join(advisory),
            "details": {"violations": [], "advisory": advisory},
        }
    return {"verdict": "PASS", "diff": None, "details": None}
