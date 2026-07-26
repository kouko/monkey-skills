#!/usr/bin/env python3
"""kpi_us_statement_cells.py — say which KIND of empty a statement cell is
(plan Task 5), docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md.

THE PROBLEM THIS EXISTS FOR. Three different facts render identically as a
blank today, and a reader cannot tell a pipeline defect from an accounting
fact (brief §"Every empty cell must say which kind of empty it is"):

  not_presented   the filer's statement has NO such line. IBM's FY2025 income
                  statement declares no operating income at all — it runs gross
                  profit -> expenses -> income before taxes. That is the filer's
                  own presentation, not a gap in ours.
  not_tagged      the line EXISTS, but that period carries no undimensioned
                  value. KO's FY2017 balance sheet presents
                  `us-gaap_MinorityInterest` and tags it for two of the three
                  instants its equity block spans.
  derived         not separately tagged, but computable from the filer's OWN
                  arithmetic — and it carries the arithmetic with it.

`value` is the fourth state and the uninteresting one: the filer tagged a
number for that period.

THE ONE DERIVATION, AND ITS ONE TRAP. Total liabilities from
`LiabilitiesAndStockholdersEquity` minus WHOLE equity (measured: 21 of 21
filers who omit `Liabilities` tag both terms, so it is always derivable).
Subtracting PARENT-ONLY `StockholdersEquity` instead pushes the minority
interest — and the mezzanine — into "liabilities": a wrong number wearing a
correct-looking label, which nothing downstream can detect. On the OBSERVED KO
FY2017 balance sheet the two answers differ by 1,905M.

THE WHOLE-EQUITY RULES ARE REUSED, NEVER RE-DERIVED (brief §"the existing
`_equity_kind` / mezzanine machinery … must be reused rather than
re-derived"). They live in `kpi_equity_terms`, a LEAF module that imports
neither this one nor `kpi_spine_view`:

  `EQUITY_CHAIN`                         the chain, PARENT-ONLY FIRST, which is
                                         also the order this resolves in
  `_equity_kind`                         which chain member a filing supplied
  `_minority_interest_term`              what to ADD on the parent-only branch,
                                         including the measured rule that an
                                         untagged interest reads as ZERO and the
                                         one exception where it does not
  `MEZZANINE_CHAIN`, `MINORITY_INTEREST_CHAIN`, `EQUITY_INCL_NCI_CONCEPT`
  `_identity_value`                      what counts as a usable figure

THEY USED TO BE READ OFF `kpi_spine_view` DIRECTLY, and the import moved for a
measured reason rather than a stylistic one: plan Task 7 makes `kpi_spine_view`
consume the reconstruction, and with that import in place `import
kpi_spine_view` raises `AttributeError: partially initialized module` while
`import kpi_us_statement_cells` still succeeds — an order-dependent breakage,
which is the kind that does not announce itself. `kpi_equity_terms`'s own
header records the mutation that reproduced it. The COUPLING is unchanged and
still deliberate: the alternative is a SECOND copy of the whole-equity branch,
which is precisely the thing the brief says must not exist twice.
`kpi_spine_view.py`'s header section "THE EQUITY TERM IS WHOLE EQUITY" explains
why the parent-only branch is the MAJORITY case (17 of 32 checkable filers)
rather than an edge case, and ITS import-time `_assert_equity_chain` is what
keeps its own `SPINE_FIELD_CHAINS["total_equity"]` equal to the `EQUITY_CHAIN`
read here.

WHAT THE REUSE DOES **NOT** CARRY OVER. `kpi_spine_view` resolves across a
BITEMPORAL store, where the same period is covered by several filings and
"absent" has to mean absent from the period rather than from one filing. Here
there is exactly ONE filing — the statement being reconstructed — so that
split collapses and the period/observation distinction in
`_minority_interest_term`'s signature is satisfied from the one statement. The
rule it encodes is what is reused; its cross-vintage motivation does not apply
and is not claimed to.

ARITHMETIC IN `Decimal`, NEVER BINARY FLOAT
(docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md). Every
figure crosses into `Decimal` via `str()` — never `Decimal(float)`, which would
bake in the binary expansion this is avoiding. Every captured filing reports
whole dollars, where float happens to be exact, so the test that can actually
FAIL on this uses constructed float-hostile values and says so at its own site.

`cell_state` IS A PURE FUNCTION of (statements, kind, concept, period). It
reads no file, makes no network call, and mutates nothing it is handed.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Sequence

# Sibling import, mirroring `kpi_us_statement_shape.py`'s shim so the module
# resolves both under `uv run --script` and under importlib test loading.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import kpi_equity_terms as equity_terms  # noqa: E402

# The three kinds `kpi_us_statement_shape.statements_for` can produce. A kind
# outside them is a CALLER BUG (a typo'd `"balance-sheet"`), and answering it
# with `not_presented` would render as exactly the undifferentiated blank this
# module exists to abolish — so it raises instead (Rule 12, fail loud).
_STATEMENT_KINDS = ("income", "balance_sheet", "cash_flow")

# Read from the shared module, never re-transcribed: the chain's ORDER is
# load-bearing (parent-only first) and a second copy of it is the drift this
# module exists to avoid. It used to be sliced out of
# `kpi_spine_view.SPINE_FIELD_CHAINS`; that chain is still the spine's, and
# `kpi_spine_view._assert_equity_chain` fails loud at import if it ever stops
# being this pair.
_EQUITY_CHAIN: tuple[str, ...] = equity_terms.EQUITY_CHAIN

# The concept the derivation starts from. Not a member of any spine chain --
# it is the balance sheet's footing, which no spine field carries.
_LIABILITIES_AND_EQUITY = "LiabilitiesAndStockholdersEquity"

# The one cell this module can derive: (statement kind, concept) -> the rule.
_DERIVABLE = ("balance_sheet", "Liabilities")


@dataclass(frozen=True)
class Derivation:
    """The arithmetic behind a `derived` cell, in the filer's own concepts.

    `formula` is BUILT from `terms`, so the two cannot disagree — which makes
    that agreement a BOOKKEEPING property, not evidence the arithmetic is
    right (docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md:
    an invariant both sides of which come from one operation answers "did I
    record what I did", never "was it the right thing to do"). What makes it
    useful is that `terms` names every figure that entered the subtraction,
    INCLUDING the ones read as zero because the filer tagged nothing — those
    are the assumptions a reader most needs to be able to challenge.

    Concepts are spelled the store's way (`us-gaap:MinorityInterest`), which is
    the same spelling `cell_state` accepts as its `concept` argument and the
    same one `_equity_kind` branches on. A statement ROW spells it
    `us-gaap_MinorityInterest`; the two are the same concept and `cell_state`
    accepts either.
    """

    formula: str
    terms: tuple[tuple[str, Decimal], ...]


@dataclass(frozen=True)
class Cell:
    """One statement cell, typed.

    `state` is exactly one of `"value"`, `"not_presented"`, `"not_tagged"`,
    `"derived"` — the four the plan's Task 5 names.

    RETURNING AN OBJECT RATHER THAN THE BARE STRING is a deliberate departure
    from the plan's `cell_state(...) -> "value" | "not_presented" |
    "not_tagged" | "derived"` shorthand, and it is what the SAME Task 5 text
    requires two lines later: "`derived` = computed from the filer's own
    arithmetic, CARRYING ITS PROVENANCE", and its GREEN, "every `derived` cell
    names the arithmetic that produced it". A bare string structurally cannot
    carry either. The arrow names the four STATES, and `state` is where they
    live.

    `value` is a `Decimal` for both `value` and `derived`, and `None` for the
    two empties. `derivation` is non-`None` for `derived` and `None` for every
    other state — a consumer can therefore branch on `state` alone and never
    has to ask whether a blank was our fault.
    """

    state: str
    value: Decimal | None
    derivation: Derivation | None


def cell_state(statements, kind: str, concept: str, period: str) -> Cell:
    """Which kind of cell this is — see the module docstring for the four.

    `statements` need only answer `.by_kind` (Task 3's `Statements`); that one
    attribute is the whole input contract, which is what lets the suite run
    offline. A kind ABSENT from `by_kind` is a filing that files no such
    statement, and that is `not_presented`, never an error.

    `concept` may be spelled either way — `us-gaap:Liabilities` (the store's)
    or `us-gaap_Liabilities` (a statement row's). `period` is a key of a
    `Line.values` dict, e.g. `"instant_2017-12-31"`.

    ORDER OF THE FOUR, and it decides real cases: a tagged value wins; a
    derivation wins over BOTH empties; only then does the line's presence
    decide between `not_tagged` and `not_presented`. Derivation ranking above
    `not_presented` is the case the plan's acceptance is built on — KO
    presents no total-liabilities line at all, yet the figure is computable
    from its own footing, and "computable" is strictly more informative than
    "absent".
    """
    if kind not in _STATEMENT_KINDS:
        raise ValueError(
            f"kpi_us_statement_cells: {kind!r} is not a statement kind; "
            f"expected one of {_STATEMENT_KINDS}"
        )
    lines = statements.by_kind.get(kind) or []
    line = _find(lines, concept)
    if line is not None:
        value = _figure(line.values.get(period))
        if value is not None:
            return Cell(state="value", value=value, derivation=None)

    derived = _derive(kind, concept, lines, period)
    if derived is not None:
        return derived

    return Cell(
        state="not_tagged" if line is not None else "not_presented",
        value=None,
        derivation=None,
    )


def _derive(kind: str, concept: str, lines: Sequence[Any], period: str) -> Cell | None:
    """The derived cell for this (kind, concept, period), or `None` when there
    is no rule for it or the rule cannot run on this filing.

    ONE RULE, not a framework. A second derivation earns a registry when it
    exists; today a dict of one would be indirection with nothing to
    indirect."""
    if (kind, _local_name(concept)) != _DERIVABLE:
        return None
    return _derive_total_liabilities(lines, period)


def _derive_total_liabilities(lines: Sequence[Any], period: str) -> Cell | None:
    """`LiabilitiesAndStockholdersEquity` - mezzanine - WHOLE equity.

    THE MEZZANINE IS SUBTRACTED TOO, and dropping it is the same defect as
    dropping the minority interest: temporary equity is presented BETWEEN
    liabilities and equity, so a `Liabilities` subtotal excludes it, and
    leaving it in the subtraction's remainder relabels it as debt. This is the
    identity `kpi_spine_view._annotate_balance_identity` already checks
    (`assets = liabilities + mezzanine + whole equity`), solved for
    liabilities — not a new accounting claim.

    UNCHECKABLE IS NOT ZERO. Every `None` return below is "this filing does not
    let me compute it", and the caller turns that into `not_tagged` /
    `not_presented` — an honest empty. Substituting a zero for any missing term
    would emit a number that is wrong by exactly that term, which is the
    failure mode `kpi_spine_view`'s header records being burned by repeatedly.

    THE TWO TERMS THAT DO READ AS ZERO WHEN ABSENT are the mezzanine and (on
    the parent-only branch) the minority interest, and that asymmetry is
    MEASURED, not assumed — 30 of 32 checkable filers in the committed probe
    balance EXACTLY under an identity that reads both as zero when untagged,
    which can only hold if absence means none. `_minority_interest_term`
    carries that measurement, and the one exception to it: a filer tagging BOTH
    equity totals is asserting a non-controlling interest EXISTS, so an absent
    amount there is missing, not zero, and this returns `None`.
    """
    footing = _amount(lines, (_LIABILITIES_AND_EQUITY,), period)
    if footing is None:
        return None

    equity_line, equity = _amount_with_line(lines, _EQUITY_CHAIN, period)
    if equity is None:
        return None
    equity_kind = equity_terms._equity_kind({"kpi_id": _store_qname(equity_line.concept)})
    if equity_kind is None:
        # Unreachable while `kpi_spine_view._assert_equity_chain` holds -- it
        # refuses at import any `total_equity` chain that is not exactly the
        # two concepts `_equity_kind` can name, and `equity_line` came from
        # that chain. Kept as a fail-closed branch rather than an assumption:
        # it costs two lines and it is the direction that emits a wrong number.
        return None

    minority_name, minority = _minority_interest(lines, period, equity_kind)
    if minority is None:
        return None
    mezzanine_name, mezzanine = _mezzanine(lines, period)
    if mezzanine is None:
        return None

    subtracted: list[tuple[str, Decimal]] = [
        (_store_qname(equity_line.concept), equity),
        (mezzanine_name, mezzanine),
    ]
    if equity_kind == "parent_only":
        # On the incl_NCI branch the interest is ALREADY inside `equity` and is
        # not a term at all; listing it as 0 there would read as "the filer
        # tagged none", which is a different and false claim.
        subtracted.append((minority_name, minority))

    footing_term = (equity_terms._US_GAAP + _LIABILITIES_AND_EQUITY, footing)
    return Cell(
        state="derived",
        value=footing - equity - minority - mezzanine,
        derivation=Derivation(
            formula=" - ".join(
                [f"{equity_terms._US_GAAP}{_DERIVABLE[1]} = {footing_term[0]}"]
                + [name for name, _ in subtracted]
            ),
            terms=(footing_term,) + tuple(subtracted),
        ),
    )


def _minority_interest(
    lines: Sequence[Any], period: str, equity_kind: str,
) -> tuple[str, Decimal | None]:
    """The amount to ADD to this period's equity figure to make it WHOLE
    equity, WITH the concept it came from — `kpi_equity_terms.
    _minority_interest_term`'s rule, called rather than restated.

    The two store-shaped arguments that rule takes collapse here: it separates
    "the PERIOD carries this term (per any filing)" from "the CHECKED FILING
    supplies the amount" because the store is bitemporal, and a statement is
    one filing, so this statement's own row answers both. `nci_is_asserted`
    survives the collapse intact — a filer tagging BOTH equity totals is
    asserting a non-controlling interest exists whether or not it tagged the
    amount.
    """
    line, raw = _raw(lines, equity_terms.MINORITY_INTEREST_CHAIN, period)
    observation = {"canonical_value": raw}
    _, nci_raw = _raw(lines, (equity_terms.EQUITY_INCL_NCI_CONCEPT,), period)
    term = equity_terms._minority_interest_term(
        equity_kind,
        observation if raw is not None else None,
        observation,
        nci_is_asserted=nci_raw is not None,
    )
    return (
        _term_name(line, equity_terms.MINORITY_INTEREST_CHAIN),
        None if term is None else _decimal(term),
    )


def _mezzanine(lines: Sequence[Any], period: str) -> tuple[str, Decimal | None]:
    """The temporary-equity term, ZERO when the statement presents none, WITH
    the concept it came from.

    Mirrors `kpi_spine_view._annotate_balance_identity`'s three-line rule
    ("absent from the period is the balance sheet asserting zero; tagged but
    unreadable stays uncheckable") for the one-filing case. Mirrored rather
    than called: there it is an inline expression inside a 90-line annotator,
    with no function to import.

    UNOBSERVED IN THIS CAPTURE — none of the five captured filings tags either
    mezzanine concept, so the non-zero branch is pinned by a constructed
    fixture and labelled as such at its site. It is kept, not dropped as
    unpinned, because `kpi_spine_view`'s header records TSLA's entire
    balance-sheet residual being exactly its redeemable non-controlling
    interest, to the dollar.
    """
    line, raw = _raw(lines, equity_terms.MEZZANINE_CHAIN, period)
    name = _term_name(line, equity_terms.MEZZANINE_CHAIN)
    return name, _decimal(0) if raw is None else _figure(raw)


def _term_name(line: Any | None, chain: Sequence[str]) -> str:
    """What to CALL a term in a derivation's provenance: the concept the filer
    actually tagged, or the chain's first concept when it tagged none.

    The fallback is only ever reached by a term read as ZERO, where there is no
    tagged concept to name and the chain's head is the conventional name for
    the thing that is absent. Naming the head UNCONDITIONALLY is the defect
    this exists to prevent: a filer tagging `RedeemableNoncontrolling
    InterestEquityCarryingAmount` would have had its derivation cite a
    `TemporaryEquity...` line its balance sheet does not contain — a wrong
    provenance on a right number, on the one cell whose entire purpose is to
    let a reader audit the arithmetic.
    """
    return _store_qname(line.concept) if line is not None else (
        equity_terms._US_GAAP + chain[0]
    )


def _raw(
    lines: Sequence[Any], chain: Iterable[str], period: str,
) -> tuple[Any | None, Any]:
    """The first chain concept this statement presents WITH a cell for
    `period`, as (line, the cell's raw value).

    First-present over the chain in chain order — the same resolution rule
    `kpi_spine_view._resolve_field` applies per period, on a statement instead
    of a store dump. Raw, not converted: whether the value is USABLE is
    `_figure`'s question, and a caller that must tell "tagged but unreadable"
    from "not tagged at all" needs to see the difference.
    """
    for name in chain:
        line = _find(lines, equity_terms._US_GAAP + name)
        if line is None:
            continue
        raw = line.values.get(period)
        if raw is not None:
            return line, raw
    return None, None


def _amount_with_line(
    lines: Sequence[Any], chain: Iterable[str], period: str,
) -> tuple[Any | None, Decimal | None]:
    """`_raw` narrowed to a usable figure, with the line that supplied it."""
    line, raw = _raw(lines, chain, period)
    return line, _figure(raw)


def _amount(lines: Sequence[Any], chain: Iterable[str], period: str) -> Decimal | None:
    return _amount_with_line(lines, chain, period)[1]


def _find(lines: Sequence[Any], concept: str) -> Any | None:
    """The first line declaring this concept, or `None`.

    FIRST, not "the only one": a statement may present one concept twice (a
    line repeated under two sections). Taking the first keeps the answer
    deterministic and matches presentation order, which is the order a reader
    meets the number in.
    """
    wanted = _store_qname(concept)
    return next(
        (line for line in lines if _store_qname(line.concept or "") == wanted),
        None,
    )


def _store_qname(concept: str) -> str:
    """A concept in the store's spelling: `us-gaap_Assets` -> `us-gaap:Assets`.

    Statement rows spell the namespace separator `_`, the store's `kpi_id`
    spells it `:`, and `_equity_kind` branches on the store's spelling. Folding
    on the FIRST separator only is what keeps a filer's own concept intact
    (`ko_UnusualOrInfrequentItemOperating` -> `ko:UnusualOrInfrequent...`) and
    distinct from a us-gaap one of the same local name — a custom
    `ko_Liabilities` is NOT `us-gaap:Liabilities` and must never match it.

    ALREADY-FOLDED CONCEPTS ARE RETURNED UNTOUCHED, and that guard is not
    cosmetic: this function is applied to BOTH sides of every comparison, so it
    must be idempotent or the two sides fold differently. Without it a caller
    asking for `ibm:Segment_Revenue_Adjustment` — store spelling, underscores
    inside the LOCAL name — folded again to `ibm:Segment:Revenue_Adjustment`
    and matched nothing, reporting a line the filer does present as
    `not_presented`. That is the taxonomy's worst answer: it blames the filer
    for our own name handling. A `:` can only be a namespace separator here
    (XBRL local names are NCNames, which admit `_` but never `:`), so its
    presence is proof the concept is already in store spelling.
    """
    if ":" in concept:
        return concept
    prefix, separator, local = concept.partition("_")
    return f"{prefix}:{local}" if separator else concept


def _local_name(concept: str) -> str:
    """The concept without its namespace, in either spelling."""
    return _store_qname(concept).rpartition(":")[2]


def _figure(raw: Any) -> Decimal | None:
    """A cell's raw value as a `Decimal`, or `None` when it is not a usable
    figure.

    "Usable" is asked of `kpi_equity_terms._identity_value` rather than
    re-decided here, so this module and the balance-sheet identity can never
    disagree about whether a cell holds a number (it rejects `None`, strings
    and — deliberately — `bool`, which is an `int` in Python and would
    otherwise arrive as 0 or 1).
    """
    value = equity_terms._identity_value({"canonical_value": raw})
    return None if value is None else _decimal(value)


def _decimal(value: int | float) -> Decimal:
    """Via `str`, NEVER `Decimal(float)`: `Decimal(1.005)` is the binary
    expansion `1.00499999999999989...`, which is the exact class of defect
    docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md
    records manufacturing a false restatement in this module family.
    `Decimal(str(1.005))` is `Decimal("1.005")`.
    """
    return Decimal(str(value))
