#!/usr/bin/env python3
"""kpi_us_statement_lines.py — is this presentation row a real statement line,
or dimensional noise? (pure-compute, plan Task 1,
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md).

A filer's income/balance/cash-flow presentation role does NOT contain only the
statement. KO's FY2017 income role returns 80 rows of which 26 are the
statement; the rest are segment breakdowns and axis scaffolding interleaved in
the same role. This module owns the one predicate that separates them, and it
is isolated in its own module because it is the reconstruction's single largest
correctness risk: a leaked dimensional row does not crash, it renders as a
plausible line with a plausible label and silently corrupts every arithmetic
check downstream.

TWO ERAS, TWO SIGNALS — why one signal is not enough. Rows disclosing a segment
slice carry a dimension label (`full_dimension_label`, e.g.
`"us-gaap:StatementBusinessSegmentsAxis: Asia Pacific"`), and that is the whole
story for pre-2018 filings. From ~2019 filers disaggregate revenue via
`srt:ProductOrServiceAxis`, and that axis's DOMAIN MEMBERS appear as
presentation rows carrying NO dimension label at all — their only signal is the
concept name itself. Filtering on the dimension label alone was MEASURED to read
`TechnologyServiceMember` as IBM's first income-statement line and
`NaturalGasReservesMember` as Duke Energy's, on every filing 2019-2026.

ALLOWLIST POLARITY (docs/loom/memory/shared-classifier-over-open-dialects-needs-
allowlist.md). This predicate states POSITIVELY what a statement line is —
a row PROVEN undimensioned whose concept is a non-placeholder element — and
rejects everything else, including everything it does not recognize. It is not
a denylist of observed member/axis names, and it must never become one: the set
of member names across all filers and all future filings is OPEN, so a name
list fails toward admitting the unsampled row, which here is the dangerous
direction (a leak, not a gap). `_STRUCTURAL_SUFFIXES` below is a CLOSED set
drawn from XBRL's own naming convention rather than from observation — it does
not grow with the filer count, and a filer inventing `NeverBeforeSampledMember`
is excluded without anyone listing it.

The predicate is deliberately blind to labels. A label is prose the filer
chooses; a concept and a dimension are structure the taxonomy imposes.

stdlib only, and a pure function of the row (plan ## Notes kickoff decision:
the reconstruction is recomputed, never persisted).
"""
from __future__ import annotations

from typing import Any

# XBRL reserves these element-name suffixes for taxonomy STRUCTURE — an axis, a
# domain, a member of that domain, a hypercube table, or the abstract
# line-items header a table hangs off. None of them is a reportable fact, so
# none can be a statement line. This set is closed and comes from the naming
# convention, NOT from a sample of filings (see ALLOWLIST POLARITY above).
_STRUCTURAL_SUFFIXES = ("Axis", "Domain", "LineItems", "Member", "Table")

# Matched against the row's KEYS, not its values. A key naming a dimension does
# NOT on its own mean "this row is a slice": the presentation surface spells
# BOTH sides of the slice relationship with the same three letters, and reading
# them alike deleted the top line of every statement that discloses segments
# (MEASURED: KO FY2017 income kept 17 of its 26 lines, losing `NET OPERATING
# REVENUES`; Realty Income FY2025 lost `Total assets` / `Total liabilities` /
# `Total equity`). That is silent DELETION, the mirror of the leak this module
# exists to prevent, so the distinction below is semantic and not a substring.
#
# FOUR such keys are observed live on a `get_statement` row (KO accession
# 0000021344-18-000008, captured 2026-07-26), in two groups meaning OPPOSITE
# things:
#
#   THIS ROW IS A SLICE     `is_dimension`, `full_dimension_label`,
#                           `dimension_metadata` — 49 of KO's 80 income rows.
#   THIS ROW HAS SLICES     `has_dimension_children` — 10 rows, ordinary
#   BENEATH IT              consolidated lines whose segment detail follows
#                           them in document order.
#
# A fifth spelling is recorded on the neighbouring FACT-row surface: the
# per-axis columns `dim_<namespace>_<AxisLocalName>`, e.g.
# `dim_srt_ProductOrServiceAxis` (data-markets/scripts/sec_edgar_client.py
# :2277-2288), whose truthy value names the member the row is sliced by. It is
# named here because applying evidence measured on THAT surface to THIS one is
# how the deletion above was introduced.
#
# SCOPE OF THIS RULE, stated because the claim "every dimension key is handled"
# would be false (docs/loom/memory/unifying-a-normalization-has-a-scope.md):
# only the four keys above are observed, and the rule is written by EXEMPTION
# rather than enumeration. A truthy key whose name contains "dim" rejects the
# row UNLESS it is one of the known child descriptors. So an UNOBSERVED sixth
# spelling — a rename, a new convenience column, an axis column appearing on the
# presentation surface — REJECTS the row: deliberately a gap, not a leak, the
# direction this module chooses everywhere. The price of that polarity is that a
# newly-introduced "has children"-style descriptor drops consolidated lines
# until it is added below, which IS the defect this constant was written to fix
# — so the exemption set is the first place a live re-capture must check.
_DIMENSION_KEY_MARKER = "dim"
_CHILD_DIMENSION_DESCRIPTOR_KEYS = frozenset({"has_dimension_children"})


def local_name(concept: str) -> str:
    """The element name with its namespace prefix stripped.

    Both spellings occur in edgartools output: `us-gaap:Revenues` and the
    underscore form `ko_UnusualOrInfrequentItemOperating` (KO's own custom
    concept, observed live). Element local names are camelCase alphanumerics,
    so the FIRST underscore is the prefix separator; a colon, when present,
    wins outright.
    """
    if ":" in concept:
        return concept.rsplit(":", 1)[-1]
    if "_" in concept:
        return concept.split("_", 1)[-1]
    return concept


def _has_structural_suffix(name: str) -> bool:
    """True if `name` ends with one of `_STRUCTURAL_SUFFIXES`, CASE-INSENSITIVELY.

    The trailing slice is compared under `.casefold()` rather than by a raw
    `.endswith()`. SCOPE OF THAT AGREEMENT, stated narrowly on purpose: this
    shares only the CASE REGIME with
    `kpi_xbrl_ingest._strip_axis_member_suffix` — the two do NOT answer "is
    this an XBRL structural suffix?" the same way, and must not be described
    as if they did. They differ in two ways:

      * SUFFIX SET — five here (`Axis, Domain, LineItems, Member, Table`),
        two there (`Axis, Member`). The two modules give OPPOSITE answers for
        `IncomeStatementTable`, by design: that helper strips a dimensional
        token off a KPI id, while this one decides whether a presentation row
        is a statement line at all.
      * EMPTY-NAME BOUNDARY — it requires the name be strictly longer than the
        suffix (stripping the whole token would leave an empty slug); here a
        name that IS the bare suffix is itself a placeholder and is rejected
        (`>=`, the fail-closed direction).

    Why the case regime is shared: a raw `.endswith()` was MEASURED to miss the
    all-caps 10-Q variant there (`DataCenterMEMBER`). The same defect here does
    not split an id — it ADMITS the placeholder as a statement line, the leak
    this module exists to prevent.

    The narrowness above is the point, not pedantry:
    docs/loom/memory/unifying-a-normalization-has-a-scope.md is this exact
    defect class (its instance 2 IS the case-sensitive suffix match), and its
    rule is that a shared-normalization claim must carry its scope — "decides
    the CASE regime in one place", never "the two can never disagree". This
    docstring shipped over-scoped once and was narrowed in review; commit
    a4681718 on this same branch line was the same correction one arc ago.
    """
    return any(
        len(name) >= len(suffix)
        and name[-len(suffix):].casefold() == suffix.casefold()
        for suffix in _STRUCTURAL_SUFFIXES
    )


def is_row_level_dimension_signal(key: Any) -> bool:
    """True if a TRUTHY value under `key` would prove the row IS a slice.

    False only for the child descriptors — keys describing rows BENEATH this
    one, which say nothing about this row and must never reject it. Both the
    observed membership of each group and what an unobserved key does are stated
    at `_CHILD_DIMENSION_DESCRIPTOR_KEYS` above; the exemption is scoped to the
    four keys measured on the presentation surface, not to dimension keys in
    general.

    PUBLIC ON PURPOSE. `kpi_us_statement_shape.statements_for` reports the
    dimension-ish keys this predicate did NOT recognise — the "count visibly"
    half of the exclusion doctrine — and that report is only trustworthy if it
    asks THIS function rather than re-deriving the test. It first re-implemented
    the comparison and compared exact-case, so a key spelled
    `Has_Dimension_Children` was exempted here and reported as unrecognised
    there: a false "the row shape has moved" alarm on a channel whose entire
    value is being silent when nothing is wrong. One shared predicate, not two
    that agree today.
    """
    name = str(key).casefold()
    return (
        _DIMENSION_KEY_MARKER in name
        and name not in _CHILD_DIMENSION_DESCRIPTOR_KEYS
    )


def is_statement_line(row: dict[str, Any]) -> bool:
    """True only for a row PROVEN to be an undimensioned, non-placeholder line.

    Every other row — dimensioned, placeholder-concept, concept missing or
    unusable — is False. That default is the point: an unrecognized row is
    excluded, never admitted (fail-closed).

    "Undimensioned" means the ROW is not itself a slice. A consolidated line
    that HAS dimensioned children is undimensioned and is kept; see
    `is_row_level_dimension_signal`.
    """
    concept = row.get("concept")
    if not isinstance(concept, str) or not concept:
        return False

    if any(
        is_row_level_dimension_signal(key) and value
        for key, value in row.items()
    ):
        return False

    name = local_name(concept)
    if not name or _has_structural_suffix(name):
        return False

    return True
