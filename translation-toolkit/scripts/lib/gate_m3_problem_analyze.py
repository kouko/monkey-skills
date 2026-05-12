"""M3 deterministic post-translation linter.

Inspired by the GalTransl ``problemAnalyze`` pattern — a cheap, no-LLM
structural sanity check that runs *before* S1 back-translation. M3 short-
circuits S1 when the output is structurally broken, saving the cost of a
blind back-translation that would be meaningless on a broken target.

Three subrules, aggregated into a single ``M3Verdict``:

- **M3a** Residual source-language characters — HARD. Target should not
  contain script characters that belong to the source-language locale
  (e.g. JP→EN target should be free of Hiragana / Katakana / CJK
  ideographs). Above-threshold residual = HARD FAIL.
- **M3b** Length-ratio sanity — SHOULD. Target / source approx-token
  ratio should sit in [0.5, 2.5] by default. Outside the band = WARN.
- **M3c** Punctuation convention — SHOULD. CJK targets (``zh-*`` /
  ``ja-*``) should use fullwidth ``，。？！`` per JLReq / CLReq.
  Halfwidth-dominated CJK punctuation = WARN. ASCII / other targets
  skip the check (return PASS).

Aggregation rules:

  - any HARD subrule FAIL  -> M3 FAIL
  - any SHOULD subrule WARN (with no HARD FAIL) -> M3 WARN
  - all PASS              -> M3 PASS

Empty-input handling:

  - empty source + empty target -> all subrules PASS-degenerate; aggregate
    PASS. Treats "nothing to translate, nothing translated" as a no-op.
  - non-empty source + non-empty target -> three subrules run normally.
  - non-empty source + empty (or whitespace-only) target -> a structural
    break: ``evaluate_m3`` short-circuits with a synthetic m3a FAIL
    (``"empty target — no translation produced"``) and runs m3b + m3c for
    completeness in the verdict body. M3a's bare residual-source check on
    an empty target is technically PASS (zero residual chars, by the rule
    as written), but "no translation at all" should not coast through on
    that technicality, so the aggregate-level guard escalates it.
  - empty source + non-empty target -> all three subrules PASS-degenerate
    (no source to compare against); aggregate PASS. Considered out of
    scope — translator inserting prose for an empty source is not what
    this gate guards against.

Verdict shape divergence from M1/M2: this module returns a
:class:`M3Verdict` dataclass (frozen) instead of the dict shape used in
:mod:`scripts.lib.gates`. The caller is expected to convert to the
uniform ``{verdict, diff, details}`` audit-trail entry at the integration
boundary (Layer 4 verification step in translation-doc / translation-
novel) — keeping the per-subrule structure in a typed dataclass at the
library boundary is more useful for callers than flattening early.

Locale-pair tuning hooks: :data:`_LOCALE_PAIR_THRESHOLDS` (M3a residual
ratio) and :data:`_LOCALE_PAIR_LENGTH_RATIO` (M3b length band) can
override the generic defaults for specific ``(source, target)`` pairs.
Intake-spec overrides land in v0.4 — for now the dicts are module-level
and edited by hand.

Spec: ``scripts/canonical/verification-gates.md`` §M3.

This module is independent of any skill folder (lives at plugin-level
``translation-toolkit/scripts/lib/``) and is therefore not subject to
the flat-skill-folder convention.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Callable, Literal

from lib.scene_chunker import approx_tokens

__all__ = [
    "M3SubruleVerdict",
    "M3Verdict",
    "evaluate_m3",
]


# --------------------------------------------------------------------------- #
# Locale-pair tunables                                                        #
# --------------------------------------------------------------------------- #

# M3a residual-source ratio threshold. Above this fraction of non-whitespace
# target chars belonging to the source-language script class -> FAIL.
# Generic default is 1%; specific pairs can override (e.g. JP↔ZH share CJK
# ideographs, so a strict ratio check would never apply — that pair gets
# its own treatment in v0.4).
_DEFAULT_RESIDUAL_THRESHOLD: float = 0.01
_LOCALE_PAIR_THRESHOLDS: dict[tuple[str, str], float] = {
    # (source_locale, target_locale) -> threshold ratio
    # Examples — extendable as users surface real cases.
    ("ja-JP", "en-US"): 0.01,
    ("ja-JP", "zh-TW"): 0.01,  # placeholder; CJK overlap deferred
    ("zh-CN", "en-US"): 0.01,
    ("zh-TW", "en-US"): 0.01,
}

# M3b length-ratio band. Target tokens / source tokens must lie in
# [low, high]. Generic [0.5, 2.5] catches gross under/over-translation.
_DEFAULT_LENGTH_RATIO: tuple[float, float] = (0.5, 2.5)
_LOCALE_PAIR_LENGTH_RATIO: dict[tuple[str, str], tuple[float, float]] = {
    # (source_locale, target_locale) -> (low, high)
    # JP/ZH are denser than EN; allow EN→JP/ZH to compress more.
    ("en-US", "ja-JP"): (0.4, 2.0),
    ("en-US", "zh-TW"): (0.4, 2.0),
    ("en-US", "zh-CN"): (0.4, 2.0),
    # JP/ZH→EN tends to expand.
    ("ja-JP", "en-US"): (0.6, 3.0),
    ("zh-TW", "en-US"): (0.6, 3.0),
    ("zh-CN", "en-US"): (0.6, 3.0),
}

# M3c fullwidth-punctuation pairs. Halfwidth ASCII -> CJK fullwidth.
_FULLWIDTH_PUNCT_MAP: dict[str, str] = {
    ",": "，",
    ".": "。",
    "?": "？",
    "!": "！",
}

# M3c PASS threshold: fraction of CJK punctuation that must be fullwidth.
_CJK_FULLWIDTH_RATIO_THRESHOLD: float = 0.8


# --------------------------------------------------------------------------- #
# Verdict dataclasses                                                         #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class M3SubruleVerdict:
    """One subrule's verdict.

    Attributes:
        subrule: ``"m3a"`` / ``"m3b"`` / ``"m3c"``.
        verdict: ``"PASS"`` / ``"WARN"`` / ``"FAIL"``.
        tier: ``"HARD"`` (m3a) or ``"SHOULD"`` (m3b, m3c).
        metric: scalar metric driving the verdict (e.g. residual ratio).
        threshold: the threshold that ``metric`` was compared against.
        detail: human-readable explanation suitable for an audit-trail
            ``diff`` field.
    """

    subrule: Literal["m3a", "m3b", "m3c"]
    verdict: Literal["PASS", "WARN", "FAIL"]
    tier: Literal["HARD", "SHOULD"]
    metric: float
    threshold: float
    detail: str


@dataclass(frozen=True)
class M3Verdict:
    """Aggregated M3 verdict over the three subrules.

    Aggregation:
        * any HARD subrule FAIL  -> M3 FAIL
        * any SHOULD subrule WARN (with no HARD FAIL) -> M3 WARN
        * all PASS              -> M3 PASS
    """

    verdict: Literal["PASS", "WARN", "FAIL"]
    subrules: tuple[M3SubruleVerdict, ...]  # always 3 entries: m3a, m3b, m3c


# --------------------------------------------------------------------------- #
# Source-script detection                                                     #
# --------------------------------------------------------------------------- #


def _is_jp_script_char(c: str) -> bool:
    """True if ``c`` belongs to a Japanese-script class (Hiragana / Katakana /
    CJK Unified Ideographs / CJK Symbols and Punctuation).

    Uses :func:`unicodedata.name` prefix matching. Characters with no name
    (e.g. control chars) are not script chars — return False.
    """
    try:
        name = unicodedata.name(c)
    except ValueError:
        return False
    return (
        name.startswith("HIRAGANA")
        or name.startswith("KATAKANA")
        or name.startswith("CJK UNIFIED IDEOGRAPH")
        or name.startswith("CJK SYMBOLS AND PUNCTUATION")
        or name.startswith("CJK COMPATIBILITY IDEOGRAPH")
    )


def _is_zh_script_char(c: str) -> bool:
    """True if ``c`` belongs to a Chinese-script class (CJK Unified
    Ideographs / CJK Symbols and Punctuation; no kana).
    """
    try:
        name = unicodedata.name(c)
    except ValueError:
        return False
    return (
        name.startswith("CJK UNIFIED IDEOGRAPH")
        or name.startswith("CJK SYMBOLS AND PUNCTUATION")
        or name.startswith("CJK COMPATIBILITY IDEOGRAPH")
    )


def _source_script_predicate(source_locale: str) -> Callable[[str], bool]:
    """Return a ``c -> bool`` predicate identifying source-script chars.

    Locale dispatch is by BCP-47 prefix: ``ja-*`` uses the JP predicate,
    ``zh-*`` uses the ZH predicate. Other source locales (en-*, ko-*, ...)
    return a predicate that matches nothing — M3a then trivially PASSes
    because the source script overlaps the target's expected script set.
    """
    if source_locale.startswith("ja-"):
        return _is_jp_script_char
    if source_locale.startswith("zh-"):
        return _is_zh_script_char
    return lambda _c: False


# --------------------------------------------------------------------------- #
# Subrule implementations                                                     #
# --------------------------------------------------------------------------- #


def _check_m3a_residual_source(
    *,
    target_text: str,
    source_locale: str,
    target_locale: str,
) -> M3SubruleVerdict:
    """M3a — HARD residual-source-script check.

    PASS criterion: ratio of source-script chars in target / total
    non-whitespace chars in target < threshold (default 0.01).

    Empty target -> PASS (degenerate; nothing to count).
    Source locale that does not overlap any CJK class -> PASS (predicate
    matches nothing).
    """
    threshold = _LOCALE_PAIR_THRESHOLDS.get(
        (source_locale, target_locale), _DEFAULT_RESIDUAL_THRESHOLD
    )

    non_ws = [c for c in target_text if not c.isspace()]
    if not non_ws:
        return M3SubruleVerdict(
            subrule="m3a",
            verdict="PASS",
            tier="HARD",
            metric=0.0,
            threshold=threshold,
            detail="empty target — no chars to count",
        )

    is_source_script = _source_script_predicate(source_locale)
    residual_count = sum(1 for c in non_ws if is_source_script(c))
    ratio = residual_count / len(non_ws)

    if ratio < threshold:
        return M3SubruleVerdict(
            subrule="m3a",
            verdict="PASS",
            tier="HARD",
            metric=ratio,
            threshold=threshold,
            detail=(
                f"residual source-script ratio {ratio:.4f} < threshold "
                f"{threshold:.4f} ({source_locale} -> {target_locale})"
            ),
        )
    return M3SubruleVerdict(
        subrule="m3a",
        verdict="FAIL",
        tier="HARD",
        metric=ratio,
        threshold=threshold,
        detail=(
            f"residual source-script ratio {ratio:.4f} >= threshold "
            f"{threshold:.4f} ({source_locale} -> {target_locale}); "
            f"{residual_count} of {len(non_ws)} non-whitespace target chars "
            f"belong to the source-language script — likely partial "
            f"translation"
        ),
    )


def _check_m3b_length_ratio(
    *,
    source_text: str,
    target_text: str,
    source_locale: str,
    target_locale: str,
) -> M3SubruleVerdict:
    """M3b — SHOULD length-ratio sanity check.

    Uses :func:`scripts.lib.scene_chunker.approx_tokens` for a zero-dep
    char/3 token approximation. Compares ``target_tokens / source_tokens``
    against ``[low, high]`` from :data:`_LOCALE_PAIR_LENGTH_RATIO` (or
    :data:`_DEFAULT_LENGTH_RATIO`).

    Empty source -> PASS (cannot divide by zero; degenerate input).
    """
    low, high = _LOCALE_PAIR_LENGTH_RATIO.get(
        (source_locale, target_locale), _DEFAULT_LENGTH_RATIO
    )

    src_tokens = approx_tokens(source_text)
    tgt_tokens = approx_tokens(target_text)

    if tgt_tokens == 0 and src_tokens > 0:
        return M3SubruleVerdict(
            subrule="m3b",
            verdict="WARN",
            tier="SHOULD",
            metric=0.0,
            threshold=low,
            detail=(
                f"empty target — length ratio is 0.0 (no translation "
                f"content); src_tokens={src_tokens}"
            ),
        )

    if src_tokens == 0:
        return M3SubruleVerdict(
            subrule="m3b",
            verdict="PASS",
            tier="SHOULD",
            metric=0.0,
            threshold=low,  # arbitrary; pair below renders as 0.0 in {low,high}
            detail="empty source — length ratio undefined; treated as PASS",
        )

    ratio = tgt_tokens / src_tokens

    if low <= ratio <= high:
        return M3SubruleVerdict(
            subrule="m3b",
            verdict="PASS",
            tier="SHOULD",
            metric=ratio,
            threshold=low,
            detail=(
                f"length ratio {ratio:.2f} within [{low:.2f}, {high:.2f}] "
                f"({source_locale} -> {target_locale}); src_tokens="
                f"{src_tokens}, tgt_tokens={tgt_tokens}"
            ),
        )

    # Decide which boundary was breached for the metric/threshold pair.
    if ratio < low:
        breached = low
        direction = "too short"
    else:
        breached = high
        direction = "too long"
    return M3SubruleVerdict(
        subrule="m3b",
        verdict="WARN",
        tier="SHOULD",
        metric=ratio,
        threshold=breached,
        detail=(
            f"length ratio {ratio:.2f} outside [{low:.2f}, {high:.2f}] — "
            f"{direction} ({source_locale} -> {target_locale}); "
            f"src_tokens={src_tokens}, tgt_tokens={tgt_tokens}"
        ),
    )


def _check_m3c_punctuation(
    *,
    target_text: str,
    target_locale: str,
) -> M3SubruleVerdict:
    """M3c — SHOULD punctuation convention check.

    CJK targets (``zh-*`` / ``ja-*``): compute fullwidth-vs-halfwidth
    ratio across {``,``/``，``, ``.``/``。``, ``?``/``？``, ``!``/``！``}.
    Pass if fullwidth ratio >= 0.8 (per JLReq / CLReq fullwidth-as-default
    convention).

    Non-CJK targets (``en-*``, ``ko-*``, etc.): no check; return PASS.

    No countable punctuation in target -> PASS (degenerate; nothing to
    judge against).
    """
    is_cjk_target = target_locale.startswith("zh-") or target_locale.startswith(
        "ja-"
    )
    if not is_cjk_target:
        return M3SubruleVerdict(
            subrule="m3c",
            verdict="PASS",
            tier="SHOULD",
            metric=1.0,
            threshold=_CJK_FULLWIDTH_RATIO_THRESHOLD,
            detail=(
                f"target locale {target_locale!r} is not CJK; "
                f"fullwidth punctuation check skipped (PASS by default per "
                f"JLReq/CLReq scope)"
            ),
        )

    halfwidth_count = sum(target_text.count(h) for h in _FULLWIDTH_PUNCT_MAP)
    fullwidth_count = sum(
        target_text.count(f) for f in _FULLWIDTH_PUNCT_MAP.values()
    )
    total = halfwidth_count + fullwidth_count

    if total == 0:
        return M3SubruleVerdict(
            subrule="m3c",
            verdict="PASS",
            tier="SHOULD",
            metric=1.0,
            threshold=_CJK_FULLWIDTH_RATIO_THRESHOLD,
            detail=(
                "no countable punctuation in target — fullwidth ratio "
                "undefined; treated as PASS"
            ),
        )

    fullwidth_ratio = fullwidth_count / total

    if fullwidth_ratio >= _CJK_FULLWIDTH_RATIO_THRESHOLD:
        return M3SubruleVerdict(
            subrule="m3c",
            verdict="PASS",
            tier="SHOULD",
            metric=fullwidth_ratio,
            threshold=_CJK_FULLWIDTH_RATIO_THRESHOLD,
            detail=(
                f"fullwidth punctuation ratio {fullwidth_ratio:.2f} >= "
                f"threshold {_CJK_FULLWIDTH_RATIO_THRESHOLD:.2f} "
                f"(JLReq/CLReq fullwidth convention); fullwidth="
                f"{fullwidth_count}, halfwidth={halfwidth_count}"
            ),
        )
    return M3SubruleVerdict(
        subrule="m3c",
        verdict="WARN",
        tier="SHOULD",
        metric=fullwidth_ratio,
        threshold=_CJK_FULLWIDTH_RATIO_THRESHOLD,
        detail=(
            f"fullwidth punctuation ratio {fullwidth_ratio:.2f} < threshold "
            f"{_CJK_FULLWIDTH_RATIO_THRESHOLD:.2f} (JLReq/CLReq expect "
            f"fullwidth ，。？！ in CJK prose); fullwidth="
            f"{fullwidth_count}, halfwidth={halfwidth_count}"
        ),
    )


# --------------------------------------------------------------------------- #
# Public entry point                                                          #
# --------------------------------------------------------------------------- #


def evaluate_m3(
    *,
    source_text: str,
    target_text: str,
    source_locale: str,
    target_locale: str,
) -> M3Verdict:
    """Run M3a + M3b + M3c and return the aggregated verdict.

    Aggregation:
        * any HARD subrule FAIL  -> M3 FAIL
        * any SHOULD subrule WARN (with no HARD FAIL) -> M3 WARN
        * all PASS              -> M3 PASS

    Args:
        source_text: original source text (pre-translation).
        target_text: target text (post-IMPROVE / post-restore).
        source_locale: BCP-47 source locale (e.g. ``"ja-JP"``).
        target_locale: BCP-47 target locale (e.g. ``"en-US"``).

    Returns:
        :class:`M3Verdict` with three populated subrule entries in order
        ``(m3a, m3b, m3c)``.
    """
    # Aggregate-level guard: non-empty source + empty (or whitespace-only)
    # target is a structural break ("no translation produced"). M3a's bare
    # residual-source rule would PASS here on a technicality (zero residual
    # chars) — escalate to a synthetic m3a FAIL so the aggregate verdict
    # reflects the break. M3b + M3c still run for completeness in the
    # verdict body.
    if source_text.strip() and not target_text.strip():
        m3a = M3SubruleVerdict(
            subrule="m3a",
            verdict="FAIL",
            tier="HARD",
            metric=0.0,
            threshold=_LOCALE_PAIR_THRESHOLDS.get(
                (source_locale, target_locale), _DEFAULT_RESIDUAL_THRESHOLD
            ),
            detail="empty target — no translation produced",
        )
    else:
        m3a = _check_m3a_residual_source(
            target_text=target_text,
            source_locale=source_locale,
            target_locale=target_locale,
        )
    m3b = _check_m3b_length_ratio(
        source_text=source_text,
        target_text=target_text,
        source_locale=source_locale,
        target_locale=target_locale,
    )
    m3c = _check_m3c_punctuation(
        target_text=target_text,
        target_locale=target_locale,
    )
    subrules = (m3a, m3b, m3c)

    # Aggregate: HARD FAIL dominates; otherwise WARN if any SHOULD WARN;
    # otherwise PASS.
    if any(s.tier == "HARD" and s.verdict == "FAIL" for s in subrules):
        verdict: Literal["PASS", "WARN", "FAIL"] = "FAIL"
    elif any(s.verdict == "WARN" for s in subrules):
        verdict = "WARN"
    else:
        verdict = "PASS"

    return M3Verdict(verdict=verdict, subrules=subrules)
