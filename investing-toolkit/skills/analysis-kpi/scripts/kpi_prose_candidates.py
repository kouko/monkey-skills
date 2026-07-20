#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
kpi_prose_candidates.py — investing-toolkit prose KPI candidate producer.

Sibling of the Route B table producer (kpi_8k_candidates.py), one layer BELOW the
LLM: it turns the canonical flattened EX-99 PROSE surface into RAW KPI candidate
points anchored to verbatim source bytes. As with the table route, the exact
printed token + source offsets never pass through an LLM; the SEMANTIC slots
(kpi_id / unit / period) are LLM-proposed and human-ratified downstream.

Landed here: the mechanical `propose` producer (crossing to data-markets
`exhibit_prose` by SUBPROCESS, mirroring the sibling ↔ exhibit_tables), the
anti-fabrication substring `passes_substring_gate` predicate, the human
confirm-all gate and the durable store append — plus the Part-2 candidate
refinements: word-scale value derivation ("3.56 billion" -> 3560000000),
date / fiscal-period label rejection ("fiscal 2026" is not a KPI value),
bounding-qualifier metadata ("up to 45,000" stays a bound), and the bounded
committed-provenance quote — the token span plus a fixed-budget context window,
which keeps PARAGRAPH-scale text (and the personal data further out in it) out of
the store. It is a width bound, not entity recognition: personal data sharing the
figure's own clause is inside any useful window, a limit declared in the Part-2
plan's deferral channel.

Anti-fabrication substring gate (the load-bearing trust rail):
  A prose candidate carries a VERBATIM matched token (the number exactly as
  printed, e.g. "1,576,000") plus a verbatim_quote snippet, alongside a NORMALIZED
  numeric `value` DERIVED from the token (comma-stripped, e.g. 1576000). The gate
  admits a candidate ONLY when its verbatim token AND its verbatim_quote are both
  literal substrings of the canonical exhibit text. It NEVER checks the normalized
  value — a printed "1,576,000" legitimately has no "1576000" anywhere in the
  source, so requiring the normalized form to appear would false-reject every
  separator-bearing number. Checking the verbatim token instead is what stops any
  layer (an LLM especially) from committing a value not present in the source.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

# The number LOCATOR is the data-markets prose surface producer
# (exhibit_prose.py). analysis-kpi reaches it by SUBPROCESS, not import — the
# analysis-* -> data-markets layer boundary is crossed by PROCESS, mirroring
# the sibling kpi_8k_candidates.run_exhibit_tables -> exhibit_tables.py
# crossing (and analysis-comps/scripts/etf_aggregator.py -> pack.py). Crossing
# by process keeps the boundary explicit, honors exhibit_prose's PEP-723
# declared env, and avoids mutating this process's global sys.path[0] (which
# would shadow stdlib — see docs/loom/memory, select.py shadowed stdlib
# select). analysis-kpi/scripts -> analysis-kpi -> skills ->
# data-markets/scripts.
_SCRIPT_DIR = Path(__file__).resolve().parent
_EXHIBIT_PROSE = (
    _SCRIPT_DIR.parent.parent / "data-markets" / "scripts" / "exhibit_prose.py"
)

# Explicit list of the SEMANTIC slots the LLM layer must fill before the human
# confirm-all gate lets a prose point commit (mirrors kpi_8k_candidates).
_SEMANTIC_FIELDS = ("kpi_id", "unit", "period")


# Word-scale multipliers, keyed by the magnitude word the LOCATOR absorbs into a
# token ("3.56 billion" arrives as ONE token, see exhibit_prose._MAGNITUDE_WORDS
# / _NUMBER_RE). The keys mirror that tuple exactly — a word the locator can
# attach but this table lacks would silently drop its multiplier, so the two
# lists must stay in lockstep.
_MAGNITUDE_MULTIPLIERS = {
    "thousand": 10 ** 3,
    "million": 10 ** 6,
    "billion": 10 ** 9,
    "trillion": 10 ** 12,
}
_MAGNITUDE_TOKEN_RE = re.compile(
    r"^(?P<number>.+?)\s+(?P<word>"
    + "|".join(_MAGNITUDE_MULTIPLIERS)
    + r")$",
    re.IGNORECASE,
)


def _normalize_value(token: str):
    """Normalize a located token into its numeric `value`: strip thousands
    separators, apply the word-scale multiplier when the token carries a
    magnitude word, and return an exact int for a whole result or a float
    otherwise ("1,576,000" -> 1576000, "3.56" -> 3.56, "3.56 billion" ->
    3560000000, "0" -> 0).

    The scaling goes through `Decimal`, NOT binary float. A decimal fraction
    like 0.1 has no exact IEEE-754 representation (`0.1 + 0.2` is famously
    0.30000000000000004), so float arithmetic is only accidentally exact — it
    happens to land on the right value for the magnitudes tested here, but the
    guarantee is absent, and an off-by-a-fraction KPI is exactly the kind of
    plausible-looking wrong number this whole feature exists to prevent. Decimal
    multiplies the printed decimal digits exactly, so a whole result comes back
    as an exact `int`; only a genuinely fractional result (e.g. "0.0015
    thousand") degrades to float. (This paragraph previously cited
    `3.56 * 1e9 == 3559999999.9999995` as proof — that claim is FALSE, it
    evaluates exactly; the reasoning is the absent guarantee, not that case.)

    A token with NO magnitude word is unchanged — the multiplier is applied only
    when a word is present, and case-insensitively, matching the locator's
    `re.IGNORECASE` token shape.

    The result is DERIVED, never required to be a source substring: the
    anti-fabrication gate verifies the VERBATIM token (which now spans the
    magnitude word), not this value.
    """
    match = _MAGNITUDE_TOKEN_RE.match(token.strip())
    if match is None:
        stripped = token.replace(",", "")
        return float(stripped) if "." in stripped else int(stripped)
    scaled = Decimal(match.group("number").replace(",", "")) * _MAGNITUDE_MULTIPLIERS[
        match.group("word").lower()
    ]
    return int(scaled) if scaled == scaled.to_integral_value() else float(scaled)


def run_exhibit_prose(canonical_text: str) -> list[dict]:
    """Subprocess data-markets `exhibit_prose.py --locate` on `canonical_text`,
    returning its located-number list (`[{"token", "start", "end"}, ...]`).

    SUBPROCESS not import: the analysis->data-markets layer boundary is crossed
    by process (mirrors kpi_8k_candidates.run_exhibit_tables -> exhibit_tables.py
    and etf_aggregator.py -> pack.py). The locator's `--locate` mode runs on the
    given text VERBATIM (no re-flatten), so every returned offset stays relative
    to `canonical_text` — the anchor the substring gate verifies against. We hand
    it the text and an `--out` temp path and read the JSON back.
    """
    with tempfile.TemporaryDirectory() as tmp:
        text_path = Path(tmp) / "canonical.txt"
        out_path = Path(tmp) / "located.json"
        text_path.write_text(canonical_text, encoding="utf-8")
        proc = subprocess.run(
            ["uv", "run", str(_EXHIBIT_PROSE),
             "--locate", "--text", str(text_path), "--out", str(out_path)],
            capture_output=True, text=True, timeout=120,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"exhibit_prose.py --locate failed: {proc.stderr[:300]}"
            )
        return json.loads(out_path.read_text(encoding="utf-8"))


# Date / fiscal-period LABEL rejection (Part 2). A bare 4-digit year in the
# 19xx/20xx range is NOT a KPI value when it functions as a date or fiscal-period
# label — "fiscal 2026", "Q1 2026", "in the year 2025". Deliberately NARROW: we
# reject such a token ONLY when it is a 4-digit year IMMEDIATELY preceded by a
# period word ("fiscal" / "quarter" / "year" / a "Q<n>" quarter tag). An ordinary
# prose figure that merely happens to be four digits ("1500 stores") is not
# preceded by a period word, so it is left untouched. This is a false-positive
# reducer BELOW the LLM/human layer, not general NLP: a bare 4-digit year with no
# temporal cue is left alone rather than guessed at.
_YEAR_RE = re.compile(r"(?:19|20)\d{2}")
_PERIOD_WORDS = frozenset({"fiscal", "quarter", "year"})
_QUARTER_RE = re.compile(r"[Qq][1-4]")
_PRECEDING_WORD_RE = re.compile(r"(\S+)\s*$")


def _is_period_label(token: str, start: int, canonical_text: str) -> bool:
    """True iff the located `token` is a 4-digit year (19xx/20xx) functioning as a
    date / fiscal-period LABEL — i.e. immediately preceded (in `canonical_text`)
    by a period word ("fiscal" / "quarter" / "year" / "Q<n>"). Such a token is a
    period label, not a KPI value, so it must not be emitted as a candidate.

    Narrow by design: a token that is not a plain 4-digit year is never a label
    here (a magnitude-bearing or separator-bearing token fails `_YEAR_RE`), and a
    4-digit year NOT preceded by a period word is left alone. `start` is the
    token's offset in `canonical_text`, so the immediately-preceding word is read
    from the source bytes — the same anchor the substring gate verifies against.
    """
    if not _YEAR_RE.fullmatch(token):
        return False
    match = _PRECEDING_WORD_RE.search(canonical_text[:start])
    if not match:
        return False
    word = match.group(1).strip(",.;:()").lower()
    return word in _PERIOD_WORDS or bool(_QUARTER_RE.fullmatch(word))


# Bounding / approximation QUALIFIERS (Part 2). SEC prose routinely states a KPI
# as a BOUND rather than an equality ("up to 45,000 deliveries", "approximately
# 931 warehouses", "more than 3 billion users"). Committing such a number as a
# bare point value silently converts a bound into a fact — a precision the source
# never claimed — so the qualifier rides along as METADATA about the candidate.
#
# Same shape as `_is_period_label`: a BOUNDED lookback at the canonical text
# immediately preceding the token (never a mutation of the verbatim token or its
# offsets, which stay the anti-fabrication anchor). Multi-word phrases are listed
# LONGEST-FIRST so "more than" wins over a bare "than"-less prefix match, and the
# alternation is anchored to the end of the lookback window with `\s*` so both a
# spaced phrase ("up to 45,000") and an abutting tilde ("~931") match.
_QUALIFIER_LOOKBACK_CHARS = 24
_QUALIFIER_PHRASES = ("approximately", "more than", "at least", "up to", "over", "~")
_QUALIFIER_RE = re.compile(
    r"(?:(?<=\s)|^)(" + "|".join(_QUALIFIER_PHRASES) + r")\s*$",
    re.IGNORECASE,
)

# "over" is the one qualifier that also ends a common business PHRASAL VERB:
# "turned over 931 units", "handed over", "took over", "carried over". None of
# those state a bound, so matching them stamps a fabricated bound onto a plain
# equality figure — the same fabrication this task closes, merely INVERTED
# (asserting imprecision the filing never stated, rather than precision). The
# word-boundary guard in _QUALIFIER_RE already rejects "leftover"/"turnover"
# (no space), but "turned over" has the space, so it needs this second guard.
_PHRASAL_HEADS_BEFORE_OVER = frozenset({
    "turned", "turn", "handed", "hand", "took", "take", "taken",
    "carried", "carry", "passed", "pass", "rolled", "roll", "spread",
})


def _detect_qualifier(start: int, canonical_text: str) -> str | None:
    """Return the lower-cased bounding/approximation qualifier immediately
    preceding the token at `start` in `canonical_text` ("up to", "approximately",
    "~", "over", "at least", "more than"), or None when the figure is stated as a
    plain equality.

    Bounded by design: only the last `_QUALIFIER_LOOKBACK_CHARS` characters before
    the token are inspected, so this reads a local cue and never scans back over a
    sentence. Case-insensitive (matching the locator's own `re.IGNORECASE` token
    shape); the returned form is normalized to lower case so a downstream reader
    compares one spelling. `None` (not `""`) marks "no bound stated" — the same
    present-but-null convention as `unit_hint`/`period_hint`.

    A bare "over" that is the tail of a phrasal verb ("turned over 931 units")
    states no bound and is rejected — see `_PHRASAL_HEADS_BEFORE_OVER`.

    The lookback is ADJACENT-only: a qualifier separated from its figure by any
    intervening word ("up to a total of 45,000") is NOT detected and the figure
    commits as a bare equality. That residual gap is declared in the plan's
    deferral channel rather than silently absorbed here.
    """
    window = canonical_text[max(0, start - _QUALIFIER_LOOKBACK_CHARS):start]
    match = _QUALIFIER_RE.search(window)
    if match is None:
        return None
    phrase = match.group(1).lower()
    if phrase == "over":
        head = _PRECEDING_WORD_RE.search(window[:match.start(1)])
        if head is not None and head.group(1).lower() in _PHRASAL_HEADS_BEFORE_OVER:
            return None
    return phrase


# Privacy bound on the COMMITTED provenance quote (Part 2). SEC prose states a
# KPI next to executive names, compensation figures, and other personal data, so a
# quote that runs to the full sentence/paragraph incidentally accumulates that
# personal data into a durable store whose purpose is operating metrics. 160 chars
# is roughly one clause's worth of context around the figure — enough for a human
# to read the number with its subject and unit — while a filing paragraph typically
# runs several hundred, so the neighboring SENTENCES are cut.
#
# What this bound does and does NOT guarantee. It guarantees no PARAGRAPH-scale
# capture: personal data more than ~one clause away from the figure cannot reach
# the store. It does NOT guarantee the window is free of personal data — a name in
# the SAME clause as the figure ("...Jane Q. Ramirez ... and 1,576,000 full-time
# employees...") sits inside any window wide enough to be useful. Excluding
# same-clause personal data needs entity recognition, which this deliberately-
# mechanical layer does not do; the residual limit is declared in the plan's
# deferral channel rather than overstated here. This is ONE budget, shared by the
# producing window and the commit-boundary clamp — never a second, parallel one.
_MAX_VERBATIM_QUOTE_CHARS = 160


def _context_window(start: int, end: int, text: str) -> str:
    """Return the bounded context window around `text[start:end]`: the token span
    plus surrounding text, at most `_MAX_VERBATIM_QUOTE_CHARS` characters.

    The result is a single CONTIGUOUS slice of `text`, never a concatenation of
    pieces around an elided middle. That is load-bearing, not cosmetic: `text` is
    the canonical source, so a contiguous slice of it is still a literal substring
    and `passes_substring_gate` keeps holding. Any truncation MARKER would break
    that same property, so none is added.

    The window is centered on the token, then RE-SLID left when centering would
    run past the end of `text`: without the re-slide a token near the right edge
    spends well under budget and discards usable left-side context for nothing.
    A token longer than the whole budget yields just the token span — still fully
    grounded, with no room for context. Offsets are never rebased: callers keep
    reporting the token's own position, not the window's.
    """
    token_length = end - start
    if token_length >= _MAX_VERBATIM_QUOTE_CHARS:
        return text[start:end]
    left = (_MAX_VERBATIM_QUOTE_CHARS - token_length) // 2
    window_start = max(0, start - left)
    window_end = min(len(text), window_start + _MAX_VERBATIM_QUOTE_CHARS)
    window_start = max(0, window_end - _MAX_VERBATIM_QUOTE_CHARS)
    return text[window_start:window_end]


def build_candidates(located_numbers: list[dict],
                     canonical_text: str | None = None) -> list[dict]:
    """Pure transform: the located-number list (already crossed the data-markets
    boundary) -> RAW candidate points. Each candidate carries ONLY mechanical
    fields — a `value` DERIVED from the verbatim token, the verbatim
    `matched_token`/`verbatim_quote`, and the `char_offset_span` anchor — with
    every SEMANTIC slot (kpi_id/unit/period) explicit null and
    `needs_semantic=True`. The value + coordinates are set here and NEVER pass
    through an LLM: that is the "values + coordinates never pass through the LLM"
    anti-fabrication contract (mirroring Route B's kpi_8k_candidates).

    Part 2 provenance window: `verbatim_quote` is the token span PLUS a bounded
    surrounding context window (`_context_window`), sliced CONTIGUOUSLY out of
    `canonical_text` so it stays a literal substring and the gate keeps holding.
    The spec asks for both halves — the minimal token span AND bounded context —
    so emitting the bare token here would satisfy "not the whole paragraph"
    trivially while leaving a human confirmer no context to judge the number by.
    `char_offset_span` keeps pointing at the TOKEN, never at the window. Without
    `canonical_text` (the pure-seam callers) there is no text to slice, so the
    quote degrades to the bare token rather than failing.

    The advisory `unit_hint`/`period_hint` remain present-but-null — sophisticated
    hint extraction is a later part and is deliberately NOT built here.

    Part 2 date/period filter: when `canonical_text` is supplied, a located number
    that is a 4-digit-year date / fiscal-period LABEL (e.g. "fiscal 2026") is
    DROPPED — a period label is not a KPI value. Reading the token's local context
    needs the surrounding text, so `canonical_text` is threaded in from `propose`;
    called WITHOUT it (the pure-seam unit tests) no context-based filtering runs
    and every located number is wrapped. The filter only DROPS labels — a
    surviving candidate keeps its mechanical value/token/offset fields unchanged.

    Part 2 bounding qualifier: also from `canonical_text`, a candidate carries
    `value_qualifier` — the bounding/approximation phrase immediately preceding
    the token ("up to" / "approximately" / "~" / "over" / "at least" / "more
    than"), or None for a plain equality (present-but-null, like the hints). It
    is METADATA derived from the surrounding text: the verbatim token, its
    offsets, and the derived `value` are untouched, so the substring gate is
    unaffected.
    """
    candidates: list[dict] = []
    for located in located_numbers:
        token = located["token"]
        if canonical_text is not None and _is_period_label(
            token, located["start"], canonical_text
        ):
            continue
        candidates.append({
            "matched_token": token,
            "verbatim_quote": (
                _context_window(located["start"], located["end"], canonical_text)
                if canonical_text is not None else token
            ),
            "value": _normalize_value(token),
            "char_offset_span": [located["start"], located["end"]],
            "value_qualifier": (
                _detect_qualifier(located["start"], canonical_text)
                if canonical_text is not None else None
            ),
            "unit_hint": None,
            "period_hint": None,
            "source_kind": "prose",
            "kpi_id": None,
            "unit": None,
            "period": None,
            "needs_semantic": True,
        })
    return candidates


def propose(canonical_text: str) -> list[dict]:
    """MECHANICAL prose-KPI producer: cross the data-markets boundary by process
    to locate the number tokens of the canonical prose surface, then wrap them
    into RAW candidate points. Thin caller over `run_exhibit_prose` (subprocess)
    + `build_candidates` (pure) — the split keeps the wrapping logic unit-
    testable without a subprocess (mirroring Route B's propose ->
    run_exhibit_tables + build_candidates).
    """
    return build_candidates(run_exhibit_prose(canonical_text), canonical_text)


def _scanned_result(candidates: list[dict]) -> dict:
    """Wrap a SCANNED candidate list into an explicit empty-aware result envelope.

    `gap=None` marks a SUCCESSFUL scan: zero candidates is empty-SUCCESS ("0 prose
    candidates"), NOT an error and NOT a gap — the anti-fabrication rail must never
    invent a KPI, and it must distinguish "scanned, found nothing" from a real gap
    (a `gap` marker). The `note` carries the count as the explicit human signal so
    a 0-found scan says so out loud rather than returning a bare empty list a caller
    could mistake for an upstream failure. Mirrors Route B's loud-gap idiom
    (sec_edgar_client `_exhibit_gap`), where an unresolved case is a NAMED slot, not
    a silent skip.
    """
    return {
        "candidates": candidates,
        "gap": None,
        "note": f"{len(candidates)} prose candidates",
    }


def _multi_exhibit_gap(exhibit_count: int) -> dict:
    """A LOUD >=2-exhibit GAP marker: extract NOTHING, never silently pick one
    exhibit. Mirrors Route B's `_exhibit_gap` vocabulary (a named gap slot for an
    8-K whose EX-99.x cannot be unambiguously sourced); here the envelope-level
    `gap="multi_exhibit"` discriminator distinguishes it from an empty-success scan.

    LOOM-SIMPLIFY: shortcut: a filing carrying >=2 EX-99 prose exhibits emits a loud
      multi_exhibit gap and extracts NOTHING, rather than scanning and arbitrating
      KPIs across the several exhibits | ceiling: a real 8-K carrying >=2 EX-99
      press-release exhibits each with recoverable prose KPIs we want extracted (not
      gapped) | upgrade: per-exhibit prose scan + table-vs-prose / prose-vs-prose
      arbitration (Part 3 dedup) once multi-exhibit RESOLUTION lands in Route B's
      sec_edgar_client `_segment_8k` | ref:
      docs/loom/plans/2026-07-19-8k-prose-kpi-intake-part-1.md T8. This inherits the
      SAME ceiling as `_segment_8k`'s >=2-exhibit LOOM-SIMPLIFY: the gap is loud +
      tested; only the multi-exhibit RESOLUTION is deferred, never the fail-loud.
    """
    return {
        "candidates": [],
        "gap": "multi_exhibit",
        "note": (
            f"{exhibit_count} EX-99 exhibits in the filing; a safe prose scan "
            f"requires exactly one (>=2-exhibit ceiling — never silently pick one)"
        ),
    }


def intake(exhibits: list[str]) -> dict:
    """Honest-gap intake entry over the mechanical prose producer.

    Takes the filing's EX-99 exhibit set (each element a canonical prose surface).
    Two negative paths are handled LOUDLY, never by fabrication or a silent pick:

      - `len(exhibits) >= 2` -> a loud `multi_exhibit` GAP and ZERO extraction
        (inherits Route B's LOOM-SIMPLIFY >=2-exhibit ceiling — see
        `_multi_exhibit_gap`). The producer does NOT scan any exhibit, so no KPI is
        attributed to an ambiguous source.
      - otherwise (the unambiguous single exhibit) -> SCAN its prose via `propose`
        and wrap the result in an empty-aware envelope (`_scanned_result`): a scan
        that finds no number token is empty-SUCCESS ("0 prose candidates"), distinct
        from the gap above. An empty set has nothing to scan and yields the same
        empty-success envelope (no exhibit -> no prose candidates).

    Returns the result envelope `{candidates, gap, note}`; the pipeline SUCCEEDS in
    both the empty-scan and the gap cases (a gap is a reported outcome, not a raised
    error) — the caller reads `gap` to branch.
    """
    if len(exhibits) >= 2:
        return _multi_exhibit_gap(len(exhibits))
    if not exhibits:
        # No exhibit to scan -> empty-SUCCESS directly, without spawning the
        # exhibit_prose subprocess on "" (keeps the empty-list case explicit,
        # hermetic, and honest — it can never surface as a subprocess error).
        return _scanned_result([])
    return _scanned_result(propose(exhibits[0]))


def passes_substring_gate(candidate: dict, canonical_text: str) -> bool:
    """Return True iff the candidate's verbatim matched token AND its
    verbatim_quote are both literal substrings of `canonical_text`.

    The gate deliberately does NOT inspect the normalized numeric `value`: that
    field is DERIVED from the token (comma-stripped), so a source that prints
    "1,576,000" has no "1576000" to match — requiring it would false-reject every
    separator-bearing figure. Grounding the verbatim token + quote is the actual
    anti-fabrication guarantee; a token absent from the source is rejected.
    """
    matched_token = candidate.get("matched_token")
    verbatim_quote = candidate.get("verbatim_quote")
    # Fail-CLOSED on the STRING grounding fields: missing / None / "" all mean
    # "no verbatim grounding" -> reject. An empty token/quote would otherwise
    # slip through (`"" in text` is always True), admitting a candidate that
    # grounds nothing — the fail-OPEN direction this anti-fabrication rail exists
    # to prevent. NOTE: this falsy guard is correct ONLY for these string fields;
    # it must NOT be applied to the numeric `value` (a legitimate 0), per
    # docs/loom/memory/falsy-guard-rejects-legitimate-zero-provenance.md.
    if not matched_token or not verbatim_quote:
        return False
    return matched_token in canonical_text and verbatim_quote in canonical_text


def commit(candidates: list[dict], confirmed: bool = False) -> list[dict]:
    """Tier-① confirm-all trust GATE: return the candidates ACCEPTED for commit.

    A prose candidate is accepted for commit ONLY after an explicit human
    confirm-all (`confirmed=True`). There is NO auto-commit: `confirmed` defaults
    False, so an omitted/False confirm accepts NOTHING (the fail-CLOSED
    direction). Moving a candidate located->committed WITHOUT the human confirm
    step is ILLEGAL and refused here — this is the three-layer trust boundary
    (mechanical produce -> LLM propose -> HUMAN confirm) that keeps unratified
    candidates out of the store. Mirrors Route B's confirm idiom
    (kpi_8k_candidates.commit gates on a falsy `confirmed`); here the confirm-all
    is a single explicit parameter covering the set.

    Interim no-taxonomy filter: a confirmed candidate is accepted REGARDLESS of
    its (LLM-labeled or merely plausible) kpi_id — there is NO fixed-taxonomy
    check gating commit. A fixed KPI taxonomy is a deferred hardening, not a
    commit precondition.

    Scope: THIS is the GATE only — it produces the accepted-for-commit set. The
    ACTUAL append into kpi_store (with the prose anchor + attribution provenance
    shape) is Task 7, which will consume this accepted set; kpi_store is NOT
    imported or appended here.
    """
    if not confirmed:
        return []
    return list(candidates)


def _bounded_quote(quote: str, matched_token: str) -> str:
    """Clamp an over-broad `quote` back down to the `_context_window` budget,
    keeping the `matched_token` inside.

    BELT-AND-BRACES, not the primary control. `build_candidates` already emits a
    bounded window, so a quote arriving here is normally within budget and is
    returned unchanged. This guard exists for the path where a DOWNSTREAM layer
    (an LLM proposal, a human editing a candidate before confirming) widens the
    quote before it reaches the store: the bound is re-enforced at the durable-
    store boundary rather than trusted from the producer alone.

    Shares `_context_window`, so the clamped result is the same CONTIGUOUS-slice
    shape with the same one budget — a slice of `quote`, which is itself a literal
    substring of the canonical text, so the anti-fabrication gate keeps holding.
    Offsets are untouched: `char_offset_span` keeps pointing at the token's true
    canonical position, never at a position within this window.

    A token longer than the whole budget yields just the token (still grounded, no
    context to spare). An over-budget quote that does not CONTAIN its own token is
    malformed — trimming it could silently drop the very number being committed,
    so it raises rather than guessing which end to cut.
    """
    if len(quote) <= _MAX_VERBATIM_QUOTE_CHARS:
        return quote
    token_at = quote.find(matched_token)
    if token_at < 0:
        raise ValueError(
            "over-long verbatim_quote does not contain its matched_token "
            f"{matched_token!r}; refusing to trim a malformed quote"
        )
    return _context_window(token_at, token_at + len(matched_token), quote)


def _prose_candidate_to_point(candidate: dict, company: str,
                              confirmer: str, confirmed_at: str) -> dict:
    """Map a confirmed prose candidate to a kpi_store-shaped point.

    Mirrors Route B's kpi_8k_candidates._candidate_to_point: values + source
    coordinates pass through VERBATIM (never re-parsed); `company` is supplied
    by the caller (one filing = one company). The prose adaptations:

    - The offset anchor is the `source_cell_ref`-analog `prose:{start}-{end}`,
      built from the candidate's `char_offset_span`. It is a TRUTHY string, so
      the store's falsy-provenance guard (`if not point.get(field)`) admits it
      cleanly — the same reason Route B renders `table:{i}` rather than a bare
      index 0. No store guard is weakened here.
    - `source_table_id` has no prose analog (prose is not tabular); it carries
      the self-describing source-kind token `"prose"` — truthy, so the store's
      provenance guard is satisfied without a table locator (the offset lives
      in `source_cell_ref`). Same source-kind-prefixed shape as Route B's
      `table:<i>` and kpi_xbrl's `xbrl:companyfacts`.
    - `as_of` is the ACCESSION-derived filing date carried on the candidate,
      DISTINCT from the wall-clock `confirmed_at`. Both are passed IN (never
      read from the clock here) so the append is deterministic; the store
      rejects a wall-clock as_of, and this one is disclosure-anchored.
    - `verbatim_quote` + filing attribution (`source_document`, `filing_date`)
      + confirmer identity (`confirmer`, `confirmed_at`) ride along so a number
      surfaced later stays citable to its source bytes and its ratifier.
    - `value_qualifier` (Part 2) rides along too, so a BOUND stated in the prose
      ("up to 45,000 deliveries") stays visible on the DURABLE point instead of
      being flattened into a bare equality at store time. It is NOT one of the
      store's required provenance fields, so a None on a plain figure cannot
      trip the falsy-provenance guard — it passes through like the optional
      `source_document`/`filing_date` above. (The truthy-token discipline is
      required only for `source_table_id`/`source_cell_ref`, which the store
      guards; inventing a truthy placeholder here would assert a bound the
      filing never stated.)
    """
    start, end = candidate["char_offset_span"]
    return {
        "company": company,
        "kpi_id": candidate["kpi_id"],
        "period": candidate["period"],
        "unit": candidate["unit"],
        "value": candidate["value"],
        "as_of": candidate["as_of"],
        "source_kind": "prose",
        "source_accession": candidate["source_accession"],
        "source_table_id": "prose",
        "source_cell_ref": f"prose:{start}-{end}",
        "verbatim_quote": _bounded_quote(
            candidate["verbatim_quote"], candidate["matched_token"]
        ),
        "value_qualifier": candidate.get("value_qualifier"),
        "source_document": candidate.get("source_document"),
        "filing_date": candidate.get("filing_date"),
        "confirmer": confirmer,
        "confirmed_at": confirmed_at,
    }


def commit_to_store(candidates: list[dict], company: str, confirmer: str,
                    confirmed_at: str, confirmed: bool = False) -> dict:
    """Append human-confirmed prose candidates into the EXISTING tier-① store.

    Closes the walking skeleton: mechanical produce (`propose`) -> LLM propose
    -> HUMAN confirm (`commit`) -> DURABLE store append (here). Composes the
    confirm-all GATE with the store append — ONLY the `commit`-accepted set
    reaches `kpi_store.append`. Fail-CLOSED: `confirmed` defaults False, so
    without an explicit human confirm-all NOTHING is appended (no bypass path
    that skips the confirm step and writes straight to the store).

    Each accepted candidate is mapped by `_prose_candidate_to_point` and handed
    to the UNMODIFIED `kpi_store.append`: the store's own provenance /
    accession-derived-as_of guards run un-weakened (a point that fails them
    raises, nothing is written). kpi_store / kpi_validate are neither imported-
    for-mutation nor reimplemented — the append reuses the existing store.
    Returns `{"committed": <n>}` (points appended this call).
    """
    accepted = commit(candidates, confirmed=confirmed)

    # Lazy sibling import (mirrors kpi_8k_candidates.commit): keep the mechanical
    # `propose`/`build_candidates` path free of the store dependency, and share
    # the same kpi_store module a caller/test resolves by name off this dir.
    if str(_SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(_SCRIPT_DIR))
    import kpi_store

    committed = 0
    for candidate in accepted:
        kpi_store.append(
            _prose_candidate_to_point(candidate, company, confirmer, confirmed_at)
        )
        committed += 1

    return {"committed": committed}
