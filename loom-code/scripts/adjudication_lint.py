#!/usr/bin/env python3
"""Zero-token lint over adjudication-view units-JSON (hard checks —
Task 3; language checks — Task 4), per
loom-code/skills/using-loom-code/protocols/adjudication-view.md
"Lint-failure rule".

Hard checks:
    - every unit has a non-empty `rendition`
    - every anchor in a unit's `anchors` list appears verbatim in
      that unit's `rendition`
    - every EN negation token in `source_text` (not / no / never /
      cannot / must not / without) requires ≥1 ZH negation marker
      (不 / 未 / 無 / 非 / 沒 / 勿 / 不得) in `rendition`

Warning-only check (does not affect exit code):
    - modality mapping per the protocol's fixed table (must→必須 /
      should→應 / may→可 / must not→不得 / should not→不應) — a
      missing expected ZH form, or one present only in negated form
      (polarity inversion), emits a `WARNING ...` line on stdout. A
      modal token inside a backticked span, or immediately followed by
      `-` (a hyphen-compound like "should-fix"), is not a modality
      claim and is excluded from the scan.
    - negation count shortfall: a unit with ≥2 EN negation tokens
      whose rendition preserves some but not all of them (whole-unit
      `any()` presence alone cannot see a partial drop) emits a
      `WARNING ...` line; total absence (0 preserved) stays a HARD
      violation, unchanged.

Each check is a callable `unit -> list[str]` (violation lines for
that unit, empty if clean). Hard checks return plain lines; the
warning check prefixes its lines with `WARNING ` — that prefix is
how `main()` excludes them from the exit-code decision without
`run_checks()` needing to know which checks are hard vs. advisory.

CLI:
    python3 adjudication_lint.py <units-json-file>

Exit 0 and no output on a clean run; exit 1 with one violation line
per finding (stdout) otherwise. WARNING-prefixed lines print but
never flip the exit code.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def check_nonempty_rendition(unit):
    """Flag a unit whose `rendition` is empty (or whitespace-only)."""
    if not unit["rendition"].strip():
        return [f"{unit['id']}: empty rendition"]
    return []


def _anchor_echoed(anchor, rendition):
    """True if `anchor` appears verbatim in `rendition`. Purely-digit
    anchors require non-digit boundaries (`re.search` with lookaround)
    so e.g. anchor "1" does not false-match inside "10"; anchors with
    any non-digit character (backticked terms, identifiers, dotted
    versions like "0.77") keep plain substring matching — they may
    legitimately sit flush against CJK text or other digits."""
    if anchor.isdigit():
        pattern = r"(?<!\d)" + re.escape(anchor) + r"(?!\d)"
        return re.search(pattern, rendition) is not None
    return anchor in rendition


def check_anchor_echo(unit):
    """Flag each anchor from `unit['anchors']` that does not appear
    verbatim in `unit['rendition']`."""
    rendition = unit["rendition"]
    return [
        f"{unit['id']}: missing anchor {anchor!r}"
        for anchor in unit["anchors"]
        if not _anchor_echoed(anchor, rendition)
    ]


# EN negation tokens, per the protocol's negation-presence check —
# word-boundary matched so "not" inside "note:"/"nothing" never
# triggers (no boundary exists between "t" and the following letter
# in either word).
_NEGATION_PATTERN = re.compile(
    r"\b(?:not|no|never|cannot|must not|without)\b", re.IGNORECASE
)
_ZH_NEGATION_MARKERS = "不未無非沒勿"
_BACKTICK_SPAN_PATTERN = re.compile(r"`[^`]*`")


def _count_en_negations(source_text):
    """Count EN negation token occurrences, excluding two false-
    positive sources (round-1 finding 2): tokens inside backticked
    spans (code/flag references) are stripped before the scan, and
    any remaining match immediately preceded by `-` (flag-name
    context, e.g. `--no-verify`) is dropped."""
    stripped = _BACKTICK_SPAN_PATTERN.sub("", source_text)
    count = 0
    for match in _NEGATION_PATTERN.finditer(stripped):
        if match.start() > 0 and stripped[match.start() - 1] == "-":
            continue
        count += 1
    return count


def _count_zh_negation_markers(rendition):
    """Count ZH negation marker occurrences (single-char markers only
    — `不得` contains `不` and is counted via that marker, per the
    protocol note that marker-occurrence counting suffices)."""
    return sum(1 for ch in rendition if ch in _ZH_NEGATION_MARKERS)


def check_negation_preserved(unit):
    """Two-tier count design (round-1 finding 1): N = EN negation
    token count in `source_text` (after `_count_en_negations`'
    exclusions), M = ZH negation marker count in `rendition`.
      - N >= 1 and M == 0 -> HARD violation (existing exit-affecting
        behavior, unchanged): total negation absence.
      - N >= 2 and 1 <= M < N -> WARNING (does not affect exit code):
        a multi-negation unit dropped some but not all negations —
        the whole-unit `any()` check alone cannot see this."""
    n = _count_en_negations(unit["source_text"])
    if n == 0:
        return []
    m = _count_zh_negation_markers(unit["rendition"])
    if m == 0:
        return [f"{unit['id']}: negation dropped in rendition"]
    if n >= 2 and m < n:
        return [
            f"WARNING {unit['id']}: negation count shortfall (source {n}, rendition {m})"
        ]
    return []


# Fixed modality mapping (protocol "Fixed modality mapping" table).
# "must not" / "should not" listed before their single-word prefixes
# so alternation prefers the two-word phrase at a matching position —
# a "must not" occurrence is consumed whole and never also counted as
# a bare "must".
_MODALITY_MAP = [
    ("must not", "不得"),
    ("should not", "不應"),
    ("must", "必須"),
    ("should", "應"),
    ("may", "可"),
]
_MODALITY_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(term) for term, _ in _MODALITY_MAP) + r")\b",
    re.IGNORECASE,
)
_MODALITY_EXPECTED = {term: zh for term, zh in _MODALITY_MAP}
_ZH_NEGATION_PREFIX = "不未非"


def _all_occurrences_negated(expected, rendition):
    """True if `expected` occurs in `rendition` at least once, and
    EVERY occurrence is immediately preceded by a ZH negation marker
    (不/未/非) — the polarity-inversion signal (round-1 finding u3(b)):
    source says e.g. "should" (affirmative), but the rendition only
    ever has the negated form (不應), never a standalone 應. A
    rendition with both a negated and a standalone occurrence is fine
    (some occurrence is not preceded by a negation marker)."""
    positions = [m.start() for m in re.finditer(re.escape(expected), rendition)]
    if not positions:
        return False
    return all(
        pos > 0 and rendition[pos - 1] in _ZH_NEGATION_PREFIX for pos in positions
    )


def check_modality_mapping(unit):
    """WARNING-only: for each distinct modal verb in `source_text`,
    flag (does not fail lint) when its fixed ZH mapping is absent from
    `rendition`, or present ONLY in negated form (polarity inversion —
    see `_all_occurrences_negated`). Returned lines are prefixed
    `WARNING ` — see `main()`'s exit-code filter.

    Two scan exclusions (round-1 finding u3, live dogfood finding):
    a modal token inside a backticked span is stripped before the scan
    (parity with `_count_en_negations`), and a modal token immediately
    followed by `-` (a hyphen-compound like "should-fix" — a severity
    label, not a modality claim) is skipped."""
    source_text = _BACKTICK_SPAN_PATTERN.sub("", unit["source_text"])
    rendition = unit["rendition"]
    warnings = []
    seen = set()
    for match in _MODALITY_PATTERN.finditer(source_text):
        end = match.end()
        if end < len(source_text) and source_text[end] == "-":
            continue
        token = match.group(0).lower()
        if token in seen:
            continue
        seen.add(token)
        expected = _MODALITY_EXPECTED[token]
        if expected not in rendition:
            warnings.append(
                f"WARNING {unit['id']}: expected 「{expected}」 for '{token}'"
            )
        elif _all_occurrences_negated(expected, rendition):
            warnings.append(
                f"WARNING {unit['id']}: expected 「{expected}」 for '{token}' appears only negated"
            )
    return warnings


CHECKS = [
    check_nonempty_rendition,
    check_anchor_echo,
    check_negation_preserved,
    check_modality_mapping,
]


def run_checks(units, checks=CHECKS):
    """Run `checks` over every unit; return the flattened list of
    violation lines, in unit order then check order."""
    violations = []
    for unit in units:
        for check in checks:
            violations.extend(check(unit))
    return violations


def exit_code_for(lines):
    """Exit code from `run_checks()` output: `WARNING `-prefixed lines
    are advisory (modality mapping) and never flip the exit code —
    only hard-check lines do."""
    return 1 if any(not line.startswith("WARNING ") for line in lines) else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="path to a units-JSON file")
    args = parser.parse_args(argv)

    units = json.loads(Path(args.path).read_text(encoding="utf-8"))
    violations = run_checks(units)
    for line in violations:
        print(line)
    return exit_code_for(violations)


if __name__ == "__main__":
    sys.exit(main())
