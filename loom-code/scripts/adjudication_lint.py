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
      cannot / must not / without) requires ≥1 negation marker in
      `rendition`, per the resolved profile's negation model — a
      character set for zh-Hant (不 / 未 / 無 / 非 / 沒 / 勿), a regex
      for a suffix-negating language like ja. Whether a shortfall is
      hard or warning-only is the profile's `negation_tier`, so this
      check is a HARD one only for profiles that say so (zh-Hant does;
      ja does not)

Warning-only check (does not affect exit code):
    - modality mapping per the resolved profile's `modality_map` (the
      protocol carries one fixed table per supported language; zh-Hant
      is must→必須 / should→應 / may→可 / must not→不得 / should not→不應)
      — none of a modal's accepted target-language forms present, or one
      present only in negated form (polarity inversion), emits a
      `WARNING ...` line on stdout. A
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
    python3 adjudication_lint.py <units-json-file> [--lang <tag>]

Exit 0 and no output on a clean run; exit 1 with one violation line
per finding (stdout) otherwise. WARNING-prefixed lines print but
never flip the exit code.
"""

import argparse
import functools
import json
import re
import sys
import unicodedata
from pathlib import Path

from adjudication_profiles import get_profile


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
_BACKTICK_SPAN_PATTERN = re.compile(r"`[^`]*`")
_DEFAULT_PROFILE = get_profile("zh-Hant")


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


def _normalized(rendition):
    """NFC-normalize a rendition before any codepoint-exact match.

    Both language checks compare untrusted rendition text against
    NFC-composed literals (the profile's negation pattern and modality
    forms), so a canonically-equivalent NFD rendition — dakuten carried
    as a combining mark, which macOS filesystems and some IMEs emit —
    silently stopped matching every form containing ば/が/ざ. Measured:
    「実行しなければならない」 and 「実行することが望ましい」 both flipped
    from quiet to WARNING purely by re-encoding. Canonicalize once,
    then compare (CHK-SEC-005)."""
    return unicodedata.normalize("NFC", rendition)


@functools.lru_cache(maxsize=None)
def _negation_pattern_regex(pattern):
    """Compile+cache a profile's `negation_pattern` regex string (Task
    2) — mirrors `_modality_pattern`'s cache-by-hashable-input shape."""
    return re.compile(pattern)


def _count_negation_markers(rendition, profile):
    """Count negation marker occurrences. Prefers `profile.negation_
    pattern` (a regex, non-overlapping match count) when the profile
    carries one — Japanese negation is an inflectional kana suffix, not
    a standalone character, so a char-set scan cannot express it (Task
    2). Falls back to `profile.negation_markers` (single-char markers
    only — `不得` contains `不` and is counted via that marker, per the
    protocol note that marker-occurrence counting suffices) otherwise."""
    if profile.negation_pattern:
        return len(_negation_pattern_regex(profile.negation_pattern).findall(rendition))
    return sum(1 for ch in rendition if ch in profile.negation_markers)


def check_negation_preserved(unit, profile=None):
    """Two-tier count design (round-1 finding 1): N = EN negation
    token count in `source_text` (after `_count_en_negations`'
    exclusions), M = negation marker count in `rendition` per
    `profile.negation_markers`.
      - N >= 1 and M == 0 -> violation at `profile.negation_tier`
        ("hard" fails the lint, unchanged for zh-Hant; a "warning"
        tier reports without affecting the exit code): total
        negation absence.
      - N >= 2 and 1 <= M < N -> WARNING (does not affect exit code)
        regardless of tier: a multi-negation unit dropped some but
        not all negations — the whole-unit `any()` check alone
        cannot see this."""
    profile = profile or _DEFAULT_PROFILE
    n = _count_en_negations(unit["source_text"])
    if n == 0:
        return []
    m = _count_negation_markers(_normalized(unit["rendition"]), profile)
    if m == 0:
        line = f"{unit['id']}: negation dropped in rendition"
        return [line if profile.negation_tier == "hard" else f"WARNING {line}"]
    if n >= 2 and m < n:
        return [
            f"WARNING {unit['id']}: negation count shortfall (source {n}, rendition {m})"
        ]
    return []


@functools.lru_cache(maxsize=None)
def _modality_pattern(modality_map):
    """Build the modality-scan regex from a profile's `modality_map`
    (a hashable tuple of `(term, forms)` pairs — see
    adjudication_profiles.LanguageProfile). Term order matters: a
    profile lists two-word phrases ("must not" / "should not") before
    their single-word prefixes so alternation consumes the phrase
    whole and never also counts it as the bare "must" / "should"."""
    terms = [term for term, _forms in modality_map]
    return re.compile(
        r"\b(?:" + "|".join(re.escape(term) for term in terms) + r")\b",
        re.IGNORECASE,
    )


def _all_occurrences_negated(expected, rendition, negation_prefix):
    """True if `expected` occurs in `rendition` at least once, and
    EVERY occurrence is immediately preceded by one of the
    `negation_prefix` STRINGS — the polarity-inversion signal (round-1
    finding u3(b)): source says e.g. "should" (affirmative), but the
    rendition only ever has the negated form (不應), never a standalone
    應. A rendition with both a negated and a standalone occurrence is
    fine (some occurrence is not preceded by a negation marker).

    `negation_prefix` is a tuple of strings, not a character set
    (whole-branch review F5): zh-Hant's prefixes are single characters,
    but Japanese negation morphemes that can sit between the verb and a
    modality suffix are multi-character (「なく」/「ない」), so a
    per-character test could not express them. `str.endswith` takes the
    tuple directly and also handles an empty tuple (never negated) and
    a match at position 0 (empty prefix slice)."""
    positions = [m.start() for m in re.finditer(re.escape(expected), rendition)]
    if not positions:
        return False
    return all(rendition[:pos].endswith(negation_prefix) for pos in positions)


def check_modality_mapping(unit, profile=None):
    """WARNING-only: for each distinct modal verb in `source_text`,
    flag (does not fail lint) when NONE of its `profile.modality_map`
    accepted forms are present in `rendition`, or when every present
    form appears ONLY in negated form (polarity inversion — see
    `_all_occurrences_negated`). Returned lines are prefixed
    `WARNING ` — see `main()`'s exit-code filter.

    Two scan exclusions (round-1 finding u3, live dogfood finding):
    a modal token inside a backticked span is stripped before the scan
    (parity with `_count_en_negations`), and a modal token immediately
    followed by `-` (a hyphen-compound like "should-fix" — a severity
    label, not a modality claim) is skipped."""
    profile = profile or _DEFAULT_PROFILE
    expected_by_term = dict(profile.modality_map)
    source_text = _BACKTICK_SPAN_PATTERN.sub("", unit["source_text"])
    rendition = _normalized(unit["rendition"])
    warnings = []
    seen = set()
    for match in _modality_pattern(profile.modality_map).finditer(source_text):
        end = match.end()
        if end < len(source_text) and source_text[end] == "-":
            continue
        token = match.group(0).lower()
        if token in seen:
            continue
        seen.add(token)
        forms = expected_by_term[token]
        present = [form for form in forms if form in rendition]
        label = "／".join(forms)
        if not present:
            warnings.append(
                f"WARNING {unit['id']}: expected 「{label}」 for '{token}'"
            )
        elif all(
            _all_occurrences_negated(form, rendition, profile.negation_prefix)
            for form in present
        ):
            warnings.append(
                f"WARNING {unit['id']}: expected 「{label}」 for '{token}' appears only negated"
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
    parser.add_argument(
        "--lang",
        default="zh-Hant",
        help="language profile tag for negation/modality checks (default: zh-Hant)",
    )
    args = parser.parse_args(argv)

    profile = get_profile(args.lang)
    checks = [
        check_nonempty_rendition,
        check_anchor_echo,
        functools.partial(check_negation_preserved, profile=profile),
        functools.partial(check_modality_mapping, profile=profile),
    ]

    units = json.loads(Path(args.path).read_text(encoding="utf-8"))
    violations = run_checks(units, checks=checks)
    for line in violations:
        print(line)
    return exit_code_for(violations)


if __name__ == "__main__":
    sys.exit(main())
