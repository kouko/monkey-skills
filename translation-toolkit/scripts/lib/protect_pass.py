"""Protect-pass: regex-extract placeholders → mask as ⟦P:NN⟧ tokens; restore inverse.

Runtime library used by translation-toolkit skills (translation-i18n,
translation-doc, translation-creative, translation-audit) to wrap LLM
translation calls so that placeholders survive the round-trip unchanged.

Why mask?
    LLMs left to themselves will localise / translate / reflow any token-like
    span — ``{name}`` becomes ``{名前}``, ``%s`` becomes ``％ｓ``, ``</a>``
    becomes ``</リンク>``. For i18n strings, code samples, URLs, and HTML this
    breaks downstream behaviour. The protect-pass replaces every such span
    with an opaque sentinel (``⟦P:NN⟧``) before the LLM sees the source, then
    restores the originals after translation.

Patterns protected (priority order — longer / more specific FIRST so containment
is resolved correctly):

    P-class 1: ICU plurals       {count, plural, one {…} other {…}}
    P-class 2: Curly braces      {name}  {0}  {{var}}
    P-class 3: printf-style      %s  %d  %1$s  %f  %x
    P-class 4: Fenced code       ```…```
    P-class 5: Inline code       `…`
    P-class 6: HTML tags         <foo>  </foo>  <a href="…">
    P-class 7: URLs              https?://…
    P-class 8: Email addresses   user@example.com
    P-class 9: File paths        /usr/…  C:\…   (DEFERRED to v0.2 — too risky
                                  to regex without false positives. Document
                                  the gap; do not implement.)

Token format
    ``⟦P:NN⟧`` where ``NN`` is a zero-padded 2-digit counter (auto-widens past
    99). The ``⟦P:`` prefix and ``⟧`` suffix use mathematical white square
    brackets (U+27E6 / U+27E7) that LLMs are extremely unlikely to invent
    spontaneously, making accidental token collisions astronomically rare.

Algorithm (overlap-resolving single pass)
    Naive iterative ``re.sub`` per pattern is fragile: a later pattern can
    match a span the earlier pattern *would* have owned, or worse, partially
    overlap an already-replaced region. This module instead:

        1. Collects all matches across all patterns into ``(start, end,
           pattern_priority, original)`` records.
        2. Sorts records by ``(start, pattern_priority)`` so that on a tie at
           the same start offset, the earlier pattern wins.
        3. Walks the sorted list and drops any record whose start lies inside
           the previously accepted record's span (containment / overlap →
           outer / earlier wins).
        4. Walks accepted spans left-to-right with a cursor, building output
           via ``out_parts.append(text[cursor:start])`` then the token, then
           advancing the cursor past the span end. Tokens are numbered in
           document order as ``⟦P:NN⟧``.

    This handles "URL inside HTML tag" cleanly: HTML pattern (priority 6)
    matches the whole tag including the ``href`` attribute; URL pattern
    (priority 7) matches the href value alone, but its span lies inside the
    HTML span and is discarded.

This module is independent of any skill folder (lives at plugin-level
``translation-toolkit/scripts/lib/``) and is therefore not subject to the
flat-skill-folder convention.
"""
from __future__ import annotations

import re

# --------------------------------------------------------------------------- #
# Pattern table — order is priority (lower index = higher priority).          #
# --------------------------------------------------------------------------- #

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # ICU plurals BEFORE generic curly braces (containment).
    # Matches: {count, plural, one {1 item} other {# items}}
    # The inner-brace pass `(?:\{[^{}]*\}[^{}]*)*` allows the nested option
    # blocks; outer must close the whole construct.
    ("icu", re.compile(r"\{[^{}]*,\s*plural\s*,\s*[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")),
    # Generic curly: {name}, {0}, {1}, {42}, {{var}} (allow optional doubled
    # braces). Numeric-only positional args (Java MessageFormat / Python
    # str.format() / Android string resources) are first-class — leading char
    # may be alpha/digit/underscore (\w == [A-Za-z0-9_]).
    ("var", re.compile(r"\{\{?\w+\}?\}")),
    # printf-style: %s %d %i %f %o %x %X %c %% with optional positional %N$.
    ("printf", re.compile(r"%(?:\d+\$)?[sdifoxXc%]")),
    # Fenced code blocks BEFORE inline code (containment).
    ("fenced", re.compile(r"```[\s\S]*?```")),
    # Inline code — single backticks. Triple-backtick spans already consumed
    # by the fenced pattern above so won't double-match here.
    ("inline_code", re.compile(r"`[^`]+`")),
    # HTML tags: <foo>, </foo>, <foo bar="baz">.
    # First char after `<` must NOT be `>` or whitespace (rules out lone `<`).
    ("html", re.compile(r"<[^>\s][^>]*>")),
    # URLs (http/https only — file paths deferred to v0.2).
    # Stops at whitespace, `)`, `]` to avoid swallowing markdown closer.
    ("url", re.compile(r"https?://[^\s)\]]+")),
    # Emails — conservative; deliberately does not allow + sign in domain etc.
    ("email", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")),
]


# --------------------------------------------------------------------------- #
# Token format                                                                 #
# --------------------------------------------------------------------------- #


_TOKEN_PREFIX = "⟦P:"   # ⟦P:
_TOKEN_SUFFIX = "⟧"     # ⟧


def _format_token(index: int, width: int) -> str:
    """Format a token. ``width`` is the zero-pad width (>= 2)."""
    return f"{_TOKEN_PREFIX}{index:0{width}d}{_TOKEN_SUFFIX}"


# Regex used by ``verify_count`` — matches any well-formed token regardless of
# digit width so future re-tokenisation runs interoperate.
_TOKEN_RE = re.compile(r"⟦P:\d+⟧")


# --------------------------------------------------------------------------- #
# Public API                                                                  #
# --------------------------------------------------------------------------- #


def protect(text: str) -> tuple[str, dict[str, str]]:
    """Mask placeholders in ``text``; return ``(masked_text, token_map)``.

    ``token_map`` maps each ``⟦P:NN⟧`` token (in the order it appears in the
    masked output) to the original substring it replaced. Restoration is
    performed by :func:`restore`.

    Behaviour:
        * Patterns are applied in priority order (see module docstring).
        * Overlapping / nested matches are resolved earliest-pattern-wins.
        * If no placeholders are found, the masked text is identical to the
          input and ``token_map`` is empty.
    """
    if not text:
        return text, {}

    # 1. Collect every candidate match across all patterns.
    candidates: list[tuple[int, int, int, str]] = []
    for priority, (_name, pat) in enumerate(PATTERNS):
        for m in pat.finditer(text):
            # Skip zero-width matches (defensive — none of our patterns can
            # produce them, but a future addition might).
            if m.end() == m.start():
                continue
            candidates.append((m.start(), priority, m.end(), m.group(0)))

    if not candidates:
        return text, {}

    # 2. Sort by (start, priority). On a tie at the same start, the earlier
    #    pattern wins because lower priority sorts first.
    candidates.sort(key=lambda r: (r[0], r[1]))

    # 3. Resolve overlaps / containment: walk left-to-right, accept a match
    #    only if it does not start inside the most recently accepted span. If
    #    a candidate starts at the same offset as an accepted one, it loses
    #    (sort order ensured the higher-priority match was accepted first).
    accepted: list[tuple[int, int, str]] = []
    last_end = -1
    for start, _priority, end, original in candidates:
        if start < last_end:
            # Inside or overlapping an already-accepted span → drop.
            continue
        accepted.append((start, end, original))
        last_end = end

    # 4. Determine token width (>= 2 digits, widens for >= 100 placeholders).
    width = max(2, len(str(len(accepted))))

    # 5. Build token list in document order; walk left-to-right with a cursor
    #    that advances past each accepted span's end, emitting (pre-text,
    #    token) chunks then a final tail.
    token_map: dict[str, str] = {}
    tokens_in_order: list[tuple[int, int, str]] = []
    for i, (start, end, original) in enumerate(accepted, start=1):
        token = _format_token(i, width)
        token_map[token] = original
        tokens_in_order.append((start, end, token))

    out_parts: list[str] = []
    cursor = 0
    for start, end, token in tokens_in_order:
        out_parts.append(text[cursor:start])
        out_parts.append(token)
        cursor = end
    out_parts.append(text[cursor:])
    return "".join(out_parts), token_map


def restore(masked: str, token_map: dict[str, str]) -> str:
    """Inverse of :func:`protect`: replace ``⟦P:NN⟧`` tokens with originals.

    Tokens absent from ``masked`` are silently ignored (the LLM may have
    dropped them — surface that via :func:`verify_count`, not here). Tokens
    in ``masked`` that are not in ``token_map`` are likewise left untouched
    so the caller can spot LLM-invented tokens.
    """
    if not token_map or not masked:
        return masked
    # Replace longest tokens first to be safe under future width changes
    # (currently all tokens in a single map share the same width, but this
    # makes the function robust to mixed-width maps).
    for token in sorted(token_map.keys(), key=len, reverse=True):
        masked = masked.replace(token, token_map[token])
    return masked


def verify_count(translated: str, token_map: dict[str, str]) -> bool:
    """M1 gate primitive: target placeholder count == source placeholder count.

    Counts ``⟦P:NN⟧`` tokens in ``translated`` and compares to ``len(token_map)``.
    Equal → True (no drops, no inventions); unequal → False.

    This is the cheapest possible structural check — it does NOT verify that
    the *same* tokens appear (an LLM that drops ⟦P:01⟧ and invents ⟦P:99⟧
    would still pass count parity). Stronger checks live in higher gates.
    """
    expected = len(token_map)
    actual = len(_TOKEN_RE.findall(translated))
    return expected == actual
