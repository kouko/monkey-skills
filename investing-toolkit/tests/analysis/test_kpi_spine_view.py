"""RED-first tests for analysis-kpi/scripts/kpi_spine_view.py — the pure
read-time view that resolves the 14 canonical spine fields out of the
store's AS-REPORTED concept series (plan
docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md, Task 4) and
flags a balance-sheet identity residual per period (same plan, Task 7).

Every fixture here is built by the REAL producer: points are appended
through `kpi_store.append` into a tmp store (`KPI_STORE_DIR`) and the input
payload is whatever `kpi_store.dump_company` actually emits — never a
hand-shaped guess at the pinned schema. The repo has been burned by
fixtures that encoded the consumer's assumption instead of the producer's
shape, and this module's whole contract is "consume the producer's payload,
emit the same shape".

The script paths are resolved locally (not via tests/analysis/conftest.py)
because this task's Files-touched list does not include conftest.py.

No `@req` tag: this dispatch's plan binds tasks by "Brief item covered", not
by registered loom-spec REQ-ids, so there is no id in the living-spec
namespace to bind these tests to (same convention as
test_kpi_store_read_cli.py).
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SKILLS = _ROOT / "skills"
KPI_STORE_SCRIPT = _SKILLS / "analysis-kpi" / "scripts" / "kpi_store.py"
KPI_SPINE_VIEW_SCRIPT = _SKILLS / "analysis-kpi" / "scripts" / "kpi_spine_view.py"
KPI_XBRL_SCRIPT = _SKILLS / "analysis-kpi" / "scripts" / "kpi_xbrl.py"
KPI_US_STATEMENT_CHECK_SCRIPT = (
    _SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_check.py"
)
TEARSHEET_FORMAT_SCRIPT = (
    _SKILLS / "report-kpi-tearsheet" / "scripts" / "tearsheet_format.py"
)

# A real accession shape, so the store's accession-derived `as_of` guard
# accepts every fixture point (a wall-clock or absent as_of is rejected).
_ACCESSION = "0000789019-25-000010"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    return _load("kpi_store_for_spine_view", KPI_STORE_SCRIPT)


@pytest.fixture
def statement_check():
    """`kpi_us_statement_check`, which owns the revenue-total rule this view
    reads through. Loaded here so the binding test at the bottom of this module
    can ask BOTH surfaces the same question."""
    return _load("kpi_us_statement_check_for_spine_view", KPI_US_STATEMENT_CHECK_SCRIPT)


@pytest.fixture
def spine_view():
    return _load("kpi_spine_view_under_test", KPI_SPINE_VIEW_SCRIPT)


def _point(
    company: str,
    concept: str,
    label: str,
    start: str | None,
    end: str,
    value,
    as_of: str,
    kind: str = "duration",
    accession: str = _ACCESSION,
) -> dict:
    """One store-valid as-reported point: the filer's own qname verbatim as
    `kpi_id` (Task 3's pin), full provenance, accession-derived as_of.

    `accession` is a parameter (not the module constant everywhere) so a test
    can tell WHICH filing a flag's `accessions` list actually came from — a
    single shared accession cannot distinguish "listed because it contributed"
    from "listed because it was passed in".
    """
    return {
        "company": company,
        "kpi_id": concept,
        "period": label,
        "period_start": start,
        "period_end": end,
        "period_kind": kind,
        "as_of": as_of,
        "value": value,
        "unit": "USD",
        "scale": 1,
        "source_accession": accession,
        "source_table_id": "xbrl:companyfacts-statement",
        "source_cell_ref": concept,
    }


def _dump_of(store, company: str, points: list[dict]) -> dict:
    for point in points:
        store.append(point)
    return store.dump_company(company)


def _series_ids(payload: dict) -> list[str]:
    return [entry["kpi_id"] for entry in payload["series"]]


def _series(payload: dict, kpi_id: str) -> dict:
    matches = [e for e in payload["series"] if e["kpi_id"] == kpi_id]
    assert len(matches) == 1, f"expected exactly one {kpi_id!r} series, got {matches}"
    return matches[0]


def _values_by_end(entry: dict) -> dict[str, object]:
    return {
        period["period_end"]: period["latest"]["canonical_value"]
        for period in entry["periods"]
    }


# --- Task 7: balance-sheet identity ---------------------------------------
#
# Every identity component is an INSTANT (a balance-sheet date), so the
# store sizes each one to `qtrs` 0 and mints a non-null `period_axis_key`
# ("<month-end>|q0") — the identity is matched across concepts on that key,
# exactly like the tearsheet's column alignment.

_ASSETS = "us-gaap:Assets"
_LIABILITIES = "us-gaap:Liabilities"
_EQUITY = "us-gaap:StockholdersEquity"
_EQUITY_INCL_NCI = (
    "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
)
_MINORITY_INTEREST = "us-gaap:MinorityInterest"
_TEMPORARY_EQUITY = (
    "us-gaap:TemporaryEquityCarryingAmountIncludingPortionAttributable"
    "ToNoncontrollingInterests"
)
_REDEEMABLE_NCI = "us-gaap:RedeemableNoncontrollingInterestEquityCarryingAmount"

# A SECOND real-shaped accession, so a test can prove a component's filing is
# absent from `accessions` rather than merely indistinguishable from the rest.
_OTHER_ACCESSION = "0000789019-25-000099"
# A THIRD one, for the vintage-alignment fixtures below: a restated period can
# carry three filings of one component, and a test must be able to name which.
_THIRD_ACCESSION = "0000789019-25-000177"


def _balance(
    company: str,
    concept: str,
    label: str,
    end: str,
    value,
    as_of: str,
    accession: str = _ACCESSION,
) -> dict:
    """One balance-sheet point: an instant, no period_start."""
    return _point(
        company, concept, label, None, end, value, as_of,
        kind="instant", accession=accession,
    )


def _identity_flag(payload: dict, period_end: str):
    """The balance-identity flag attached to `total_assets` for one period,
    or None when that period was not flagged. `total_assets` is the flag's
    carrier because it is the identity's subject AND its denominator.
    """
    matches = [
        period
        for period in _series(payload, "total_assets")["periods"]
        if period["period_end"] == period_end
    ]
    assert len(matches) == 1, f"expected one total_assets period ending {period_end}"
    return matches[0].get("balance_identity")


def test_mezzanine_is_required_for_the_identity(store, spine_view):
    """The mezzanine term is REQUIRED, not optional: a filer whose assets
    exceed liabilities+equity by EXACTLY its temporary equity balances, and
    the same filer without that term reads as "does not balance".

    Measured on the 47-filer probe (brief §Probe evidence): TSLA's entire
    residual was exactly its redeemable non-controlling interest, to the
    dollar; with the term, 30 of 32 checkable filers balance EXACTLY. Drop
    the term and this filer is falsely accused.
    """
    with_mezzanine = "TSLA-SHAPED"
    balanced = _dump_of(
        store,
        with_mezzanine,
        [
            _balance(with_mezzanine, _ASSETS, "FY2019", "2019-12-31", 34_309_000_000, "2020-02-01"),
            _balance(with_mezzanine, _LIABILITIES, "FY2019", "2019-12-31", 26_199_000_000, "2020-02-01"),
            _balance(with_mezzanine, _EQUITY_INCL_NCI, "FY2019", "2019-12-31", 8_052_000_000, "2020-02-01"),
            _balance(with_mezzanine, _TEMPORARY_EQUITY, "FY2019", "2019-12-31", 58_000_000, "2020-02-01"),
        ],
    )
    without_mezzanine = "TSLA-SHAPED-NO-MEZZANINE"
    unbalanced = _dump_of(
        store,
        without_mezzanine,
        [
            _balance(without_mezzanine, _ASSETS, "FY2019", "2019-12-31", 34_309_000_000, "2020-02-01"),
            _balance(without_mezzanine, _LIABILITIES, "FY2019", "2019-12-31", 26_199_000_000, "2020-02-01"),
            _balance(without_mezzanine, _EQUITY_INCL_NCI, "FY2019", "2019-12-31", 8_052_000_000, "2020-02-01"),
        ],
    )

    assert _identity_flag(spine_view.derive_spine(balanced), "2019-12-31") is None

    flag = _identity_flag(spine_view.derive_spine(unbalanced), "2019-12-31")
    assert flag is not None, "without the mezzanine term the same filer must not balance"
    assert flag["type"] == spine_view.BALANCE_IDENTITY_FLAG_TYPE
    assert flag["residual"] == 58_000_000
    # The mezzanine term IS the whole residual — that is why it is required.
    assert flag["components"]["mezzanine"] == 0


def test_rounding_residual_passes_but_a_real_break_is_flagged(store, spine_view):
    """The 1e-5 relative tolerance, bracketed on ONE filer's two periods.

    `companyfacts` carries no `decimals` attribute, so a precision-derived
    tolerance is not constructible; 1e-5 was pinned at kickoff against the
    two measured non-exact filers (IBM and P&G each miss by exactly
    1,000,000 against figures reported in millions — 7.99e-06 relative).
    Here 1,000,000 (7.99e-06) passes and 2,000,000 (1.60e-05) is flagged,
    so the constant cannot drift by an order of magnitude unnoticed.

    Also pins mezzanine-absent = 0: this filer tags no temporary equity at
    all (the common case), and its periods are still CHECKED. Absence of a
    redeemable instrument is the balance sheet asserting zero, unlike an
    untagged `Liabilities` subtotal (next test), which is a missing TOTAL.
    """
    company = "ROUNDING-VS-BREAK"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2022", "2022-12-31", 125_155_000_000, "2023-02-01"),
            _balance(company, _LIABILITIES, "FY2022", "2022-12-31", 105_222_000_000, "2023-02-01"),
            _balance(company, _EQUITY, "FY2022", "2022-12-31", 19_932_000_000, "2023-02-01"),
            _balance(company, _ASSETS, "FY2023", "2023-12-31", 125_155_000_000, "2024-02-01"),
            _balance(company, _LIABILITIES, "FY2023", "2023-12-31", 105_222_000_000, "2024-02-01"),
            _balance(company, _EQUITY, "FY2023", "2023-12-31", 19_931_000_000, "2024-02-01"),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert spine_view.BALANCE_IDENTITY_TOLERANCE == 1e-5
    assert _identity_flag(derived, "2022-12-31") is None  # residual 1e6 -> 7.99e-06

    flag = _identity_flag(derived, "2023-12-31")  # residual 2e6 -> 1.60e-05
    assert flag is not None
    assert flag["residual"] == 2_000_000
    assert flag["relative_residual"] > spine_view.BALANCE_IDENTITY_TOLERANCE
    # Never a suppression: the flagged period keeps every as-reported value.
    assert _values_by_end(_series(derived, "total_assets")) == {
        "2022-12-31": 125_155_000_000,
        "2023-12-31": 125_155_000_000,
    }
    assert _values_by_end(_series(derived, "total_equity")) == {
        "2022-12-31": 19_932_000_000,
        "2023-12-31": 19_931_000_000,
    }


def test_a_period_missing_a_component_is_neither_flagged_nor_dropped(store, spine_view):
    """Uncheckable is NOT the same as wrong. 13 of 46 probed filers never
    tag a total `Liabilities`; silence there is correct, and a flag would be
    a false accusation about figures the filer reported honestly.
    """
    company = "NO-TOTAL-LIABILITIES"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2020", "2020-12-31", 44_000, "2021-02-01"),
            _balance(company, _EQUITY, "FY2020", "2020-12-31", 30_000, "2021-02-01"),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert _series_ids(derived) == ["total_assets", "total_equity"]
    assert _identity_flag(derived, "2020-12-31") is None
    # Not dropped either — both as-reported values survive intact.
    assert _values_by_end(_series(derived, "total_assets")) == {"2020-12-31": 44_000}
    assert _values_by_end(_series(derived, "total_equity")) == {"2020-12-31": 30_000}


def test_mezzanine_falls_back_to_the_redeemable_nci_concept(store, spine_view):
    """A filer tagging only `RedeemableNoncontrollingInterestEquityCarrying
    Amount` (the chain's fallback) balances just as one tagging the primary
    `TemporaryEquityCarryingAmount...` concept does.
    """
    company = "REDEEMABLE-NCI-ONLY"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2019", "2019-12-31", 34_309_000_000, "2020-02-01"),
            _balance(company, _LIABILITIES, "FY2019", "2019-12-31", 26_199_000_000, "2020-02-01"),
            _balance(company, _EQUITY_INCL_NCI, "FY2019", "2019-12-31", 8_052_000_000, "2020-02-01"),
            _balance(company, _REDEEMABLE_NCI, "FY2019", "2019-12-31", 58_000_000, "2020-02-01"),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert _identity_flag(derived, "2019-12-31") is None
    # The mezzanine concept is identity-only: it never becomes a spine row.
    assert _series_ids(derived) == ["total_assets", "total_liabilities", "total_equity"]


def test_the_equity_chain_drift_guard_trips_on_reorder_and_on_extension(spine_view):
    """The guard that stops the `total_equity` chain and the two concepts the
    identity branches on from drifting apart silently.

    Two properties are pinned SEPARATELY because they are what a later
    "simplification" would take away: the comparison is ORDER-sensitive (a
    reordered chain flips which concept the majority of periods resolve to,
    which is exactly the defect this round fixed) and LENGTH-sensitive (a third
    member is a concept `_equity_kind` cannot name, so every period carrying it
    would fall through to "uncheckable" — a check that quietly stops checking).
    Loosening tuple equality to a set or a subset test would keep the shipped
    chain passing while silently admitting both; these two assertions are what
    breaks if someone does.
    """
    reordered = (
        spine_view.EQUITY_INCL_NCI_CONCEPT,
        spine_view.EQUITY_PARENT_ONLY_CONCEPT,
    )
    extended = (
        spine_view.EQUITY_PARENT_ONLY_CONCEPT,
        spine_view.EQUITY_INCL_NCI_CONCEPT,
        "StockholdersEquityOther",
    )

    with pytest.raises(RuntimeError, match="total_equity chain"):
        spine_view._assert_equity_chain(reordered)
    with pytest.raises(RuntimeError, match="total_equity chain"):
        spine_view._assert_equity_chain(extended)

    # ...and the chain this module actually ships passes it — the guard is
    # asserted to be satisfied at import, not merely to be raisable.
    shipped = dict(spine_view.SPINE_FIELD_CHAINS)["total_equity"]
    assert spine_view._assert_equity_chain(shipped) is None


def test_parent_only_equity_takes_the_minority_interest_term(store, spine_view):
    """THE CHAIN-ORDER INTERACTION. The `total_equity` chain puts PARENT-ONLY
    `StockholdersEquity` FIRST, so for a filer tagging BOTH equity totals at
    one instant the view resolves the parent-only figure — and the identity's
    equity term must then be completed with `MinorityInterest`, or the
    residual IS the non-controlling interest and the period is falsely
    flagged.

    Not an edge case: cross-tabbing the committed 47-filer probe fixture
    (`us_statement_shapes_probe_2026-07-26.json`), 17 of the 32 checkable
    filers used the incl-NCI concept in the probe's own four-term identity
    while this view's chain resolves parent-only — BA, C, COST, CVX, F, GE,
    GM, IBM, JNJ, MS, PEP, PFE, PSX, QCOM, TSLA, UNH, WFC.

    The FIX IS THE IDENTITY, NOT THE CHAIN: `total_equity` still reports the
    parent-only figure the filer tagged (asserted below), because what the
    spine's `total_equity` field should MEAN is a separate product question.
    """
    company = "PARENT-ONLY-WITH-NCI"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000, "2024-02-01"),
            _balance(company, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(company, _EQUITY, "FY2023", "2023-12-31", 44_000_000_000, "2024-02-01"),
            _balance(company, _EQUITY_INCL_NCI, "FY2023", "2023-12-31", 50_000_000_000, "2024-02-01"),
            _balance(company, _MINORITY_INTEREST, "FY2023", "2023-12-31", 6_000_000_000, "2024-02-01"),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert _identity_flag(derived, "2023-12-31") is None, (
        "assets equal liabilities + WHOLE equity, so this filer balances; "
        "flagging it accuses the filer of our own chain-order choice"
    )
    # The chain is untouched: the reported field is still the parent-only
    # figure, and `MinorityInterest` is identity-only — never a spine row.
    assert _values_by_end(_series(derived, "total_equity")) == {
        "2023-12-31": 44_000_000_000
    }
    assert _series_ids(derived) == ["total_assets", "total_liabilities", "total_equity"]


def test_incl_nci_equity_never_double_counts_the_minority_interest(store, spine_view):
    """The other branch. When the period's `total_equity` resolves to
    `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest`
    the NCI is ALREADY inside it, so adding `MinorityInterest` on top would
    double-count it and flag a filer that balances.

    This branch is reached only when the filer tags no parent-only
    `StockholdersEquity` for the period (chain order), which is exactly the
    shape below.
    """
    company = "INCL-NCI-ONLY"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000, "2024-02-01"),
            _balance(company, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(company, _EQUITY_INCL_NCI, "FY2023", "2023-12-31", 50_000_000_000, "2024-02-01"),
            _balance(company, _MINORITY_INTEREST, "FY2023", "2023-12-31", 6_000_000_000, "2024-02-01"),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert _identity_flag(derived, "2023-12-31") is None
    assert _values_by_end(_series(derived, "total_equity")) == {
        "2023-12-31": 50_000_000_000
    }


def test_accessions_omit_a_filing_that_contributed_nothing_to_the_arithmetic(
    store, spine_view
):
    """`accessions` is the provenance BEHIND THE COMPONENTS — the filings the
    residual was actually computed from — so a component whose term is 0 by
    construction must not put its filing there.

    On the `incl_NCI` branch `MinorityInterest` is exactly that: the resolved
    equity concept already contains the interest, so the term is 0 no matter
    what the filer tagged. Listing its accession would send a reader to a
    filing that moved no number in the residual, which is the opposite of what
    the list is for.
    """
    company = "INCL-NCI-BROKEN-WITH-MI"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000, "2024-02-01"),
            _balance(company, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(company, _EQUITY_INCL_NCI, "FY2023", "2023-12-31", 44_000_000_000, "2024-02-01"),
            # Tagged, from its OWN filing, and irrelevant to the arithmetic.
            _balance(
                company, _MINORITY_INTEREST, "FY2023", "2023-12-31", 6_000_000_000,
                "2024-02-01", accession=_OTHER_ACCESSION,
            ),
        ],
    )

    flag = _identity_flag(spine_view.derive_spine(dump), "2023-12-31")

    assert flag is not None
    assert flag["equity_kind"] == "incl_NCI"
    assert flag["components"]["minority_interest"] == 0
    assert flag["accessions"] == [_ACCESSION], (
        "the minority-interest filing contributed a term of 0 by construction, "
        "so it is not one of the accessions the residual came from"
    )


def test_an_untagged_minority_interest_reads_as_zero_when_nothing_asserts_one(
    store, spine_view
):
    """MEASURED, not assumed. A filer that tags ONLY the parent-only equity
    total and no `MinorityInterest` has no non-controlling interest, so the
    absent term reads as 0 and the period stays CHECKED — the same rule, and
    the same kind of evidence, as the mezzanine's.

    Evidence: of the committed probe's 32 checkable filers, 13 resolved
    parent-only with no `MinorityInterest` at that instant (the probe's
    `parent_plus_MI` branch fired ZERO times in-sample), and all 13 balance
    EXACTLY. Making absence uncheckable instead would silence the identity
    for the single-entity majority — the common case, not an edge case.
    """
    balanced = "SINGLE-ENTITY-BALANCED"
    balanced_dump = _dump_of(
        store,
        balanced,
        [
            _balance(balanced, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000, "2024-02-01"),
            _balance(balanced, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(balanced, _EQUITY, "FY2023", "2023-12-31", 50_000_000_000, "2024-02-01"),
        ],
    )
    broken = "SINGLE-ENTITY-BROKEN"
    broken_dump = _dump_of(
        store,
        broken,
        [
            _balance(broken, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000, "2024-02-01"),
            _balance(broken, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(broken, _EQUITY, "FY2023", "2023-12-31", 44_000_000_000, "2024-02-01"),
        ],
    )

    assert _identity_flag(spine_view.derive_spine(balanced_dump), "2023-12-31") is None

    flag = _identity_flag(spine_view.derive_spine(broken_dump), "2023-12-31")
    assert flag is not None, "absence must read as 0, NOT make the period uncheckable"
    assert flag["components"]["minority_interest"] == 0
    assert flag["equity_kind"] == "parent_only"


def test_a_parent_only_period_whose_asserted_nci_has_no_amount_is_uncheckable(
    store, spine_view
):
    """The one place absence does NOT read as 0. A filer tagging BOTH equity
    totals is asserting a non-controlling interest EXISTS (that is the line
    between the two subtotals); if it never tags `MinorityInterest`, the term
    we need has no amount and the period is UNCHECKABLE.

    Reading 0 here would reproduce the exact defect this round fixes — the
    residual would be the NCI and the filer falsely accused — while
    substituting the incl-NCI figure would make the flag's own
    `components.total_equity` disagree with the `total_equity` the view
    EMITS for that period, which no reader could reconcile. Uncheckable is
    the honest third answer.
    """
    company = "NCI-ASSERTED-BUT-UNTAGGED"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000, "2024-02-01"),
            _balance(company, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(company, _EQUITY, "FY2023", "2023-12-31", 44_000_000_000, "2024-02-01"),
            _balance(company, _EQUITY_INCL_NCI, "FY2023", "2023-12-31", 50_000_000_000, "2024-02-01"),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert _identity_flag(derived, "2023-12-31") is None
    # Not dropped either — every as-reported figure survives.
    assert _values_by_end(_series(derived, "total_assets")) == {
        "2023-12-31": 200_000_000_000
    }
    assert _values_by_end(_series(derived, "total_equity")) == {
        "2023-12-31": 44_000_000_000
    }


def test_the_flag_conforms_to_the_one_dqc_schema(store, spine_view):
    """The repo pins ONE flag schema — `{type, old, new, accessions,
    reason}` with locating extras allowed (`kpi_xbrl.assert_dqc_schema`,
    plan kickoff decision "no per-class schema variants"). This flag is not
    a variant of it.
    """
    company = "SCHEMA-CHECK"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2023", "2023-12-31", 125_155_000_000, "2024-02-01"),
            _balance(company, _LIABILITIES, "FY2023", "2023-12-31", 105_222_000_000, "2024-02-01"),
            _balance(company, _EQUITY, "FY2023", "2023-12-31", 19_931_000_000, "2024-02-01"),
        ],
    )
    kpi_xbrl = _load("kpi_xbrl_for_spine_view", KPI_XBRL_SCRIPT)

    flag = _identity_flag(spine_view.derive_spine(dump), "2023-12-31")

    assert kpi_xbrl.assert_dqc_schema(flag) is flag
    assert flag["accessions"] == [_ACCESSION]
    assert flag["reason"]
    assert flag["period_axis_key"] == "2023-12-31|q0"
    assert flag["equity_kind"] == "parent_only"
    assert flag["components"] == {
        "total_assets": 125_155_000_000,
        "total_liabilities": 105_222_000_000,
        "mezzanine": 0,
        "total_equity": 19_931_000_000,
        "minority_interest": 0,
    }


def test_the_flag_annotates_only_the_top_level_of_the_view_copy(store, spine_view):
    """Derived period entries are SHALLOW copies of the caller's dump
    entries: annotating a top level key is safe, but the nested `latest` /
    `observations` / `period_labels` objects are STILL the caller's, so
    writing into one would silently rewrite the store's payload.

    The load-bearing assertion is the whole-payload DEEP-EQUALITY snapshot:
    object identity alone would still pass if a nested write landed inside
    `observations` or `period_labels`, and comparing the entire input dump
    before/after covers every nested container at once rather than the two
    this module happens to name.
    """
    company = "NO-WRITE-BACK"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2023", "2023-12-31", 125_155_000_000, "2024-02-01"),
            _balance(company, _LIABILITIES, "FY2023", "2023-12-31", 105_222_000_000, "2024-02-01"),
            _balance(company, _EQUITY, "FY2023", "2023-12-31", 19_931_000_000, "2024-02-01"),
        ],
    )
    stored_assets = _series(dump, _ASSETS)["periods"][0]
    before = copy.deepcopy(dump)

    derived = spine_view.derive_spine(dump)

    assert _identity_flag(derived, "2023-12-31") is not None
    # Nothing anywhere in the caller's payload moved — top level or nested.
    assert dump == before
    # ...and the nested objects are still SHARED, so the deep-equality check
    # above really did have the chance to catch a nested write.
    derived_assets = _series(derived, "total_assets")["periods"][0]
    assert derived_assets is not stored_assets
    assert derived_assets["latest"] is stored_assets["latest"]
    assert derived_assets["observations"] is stored_assets["observations"]
    assert derived_assets["period_labels"] is stored_assets["period_labels"]


# --- Task 7, vintage alignment --------------------------------------------
#
# The store is BITEMPORAL: a restatement APPENDS a new vintage of a period
# rather than overwriting the old one, and different components of one period
# can end up with different numbers of vintages. Reading each component's own
# `latest` therefore compares figures from DIFFERENT filings, which is not an
# accounting identity at all. Measured on the live six-filer dogfood: four
# filers flagged (MSFT 5.73e-02, AAPL 1.29e-01, JPM 3.36e-04, TSLA 9.98e-03)
# and every one was this shape — the store working exactly as designed,
# reported as a defect.


def test_a_restated_period_is_checked_within_one_filing_not_across_vintages(
    store, spine_view
):
    """THE REAL MSFT SHAPE, at period end 2016-06-30 (live dogfood dump
    `MSFT.dump.json`): assets and liabilities each carry two vintages, equity
    carries a THIRD that the other two lack.

    Taking each component's own `latest` mixes a 2017-filed assets figure with
    a 2018-filed equity figure — 193,468 − (121,471 + 83,090) = −11,093 M,
    5.73e-02 relative, flagged. But the 2017 filing balances to the dollar:
    193,468 = 121,471 + 71,997. The residual was an artifact of the mixture,
    and the filer was falsely accused of a restatement the store recorded
    correctly.

    The view still REPORTS each component's own latest (asserted below) — this
    changes only which vintage feeds the CHECK, never a displayed figure.
    """
    company = "MSFT-SHAPED-RESTATED"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2016", "2016-06-30", 193_694_000_000, "2016-07-28"),
            _balance(company, _LIABILITIES, "FY2016", "2016-06-30", 121_697_000_000, "2016-07-28"),
            _balance(company, _EQUITY, "FY2016", "2016-06-30", 71_997_000_000, "2016-07-28"),
            _balance(
                company, _ASSETS, "FY2016", "2016-06-30", 193_468_000_000,
                "2017-08-02", accession=_OTHER_ACCESSION,
            ),
            _balance(
                company, _LIABILITIES, "FY2016", "2016-06-30", 121_471_000_000,
                "2017-08-02", accession=_OTHER_ACCESSION,
            ),
            _balance(
                company, _EQUITY, "FY2016", "2016-06-30", 71_997_000_000,
                "2017-08-02", accession=_OTHER_ACCESSION,
            ),
            # The third vintage only equity has — the whole defect.
            _balance(
                company, _EQUITY, "FY2016", "2016-06-30", 83_090_000_000,
                "2018-08-03", accession=_THIRD_ACCESSION,
            ),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert _identity_flag(derived, "2016-06-30") is None, (
        "the newest filing carrying all three totals balances EXACTLY; the "
        "residual exists only in a mixture of two filings"
    )
    assert _values_by_end(_series(derived, "total_assets")) == {
        "2016-06-30": 193_468_000_000
    }
    assert _values_by_end(_series(derived, "total_equity")) == {
        "2016-06-30": 83_090_000_000
    }


def test_the_newest_complete_vintage_is_the_one_checked(store, spine_view):
    """WHICH vintage, stated rather than left implicit: the newest filing
    carrying every required total, because that is what a reader sees as this
    period's current figures. A superseded filing's residual is not news.

    Both directions are pinned, because either one alone is satisfiable by a
    wrong rule: checking the OLDEST vintage would pass the first company and
    fail the second, and checking ANY vintage that balances would pass both
    while never flagging anything.
    """
    fixed = "RESTATEMENT-FIXED"
    fixed_dump = _dump_of(
        store,
        fixed,
        [
            _balance(fixed, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000, "2024-02-01"),
            _balance(fixed, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(fixed, _EQUITY, "FY2023", "2023-12-31", 44_000_000_000, "2024-02-01"),
            _balance(
                fixed, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
            _balance(
                fixed, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
            _balance(
                fixed, _EQUITY, "FY2023", "2023-12-31", 50_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
        ],
    )
    broke = "RESTATEMENT-BROKE-IT"
    broke_dump = _dump_of(
        store,
        broke,
        [
            _balance(broke, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000, "2024-02-01"),
            _balance(broke, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(broke, _EQUITY, "FY2023", "2023-12-31", 50_000_000_000, "2024-02-01"),
            _balance(
                broke, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
            _balance(
                broke, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
            _balance(
                broke, _EQUITY, "FY2023", "2023-12-31", 44_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
        ],
    )

    assert _identity_flag(spine_view.derive_spine(fixed_dump), "2023-12-31") is None, (
        "the restatement balances; the superseded filing's break is not news"
    )

    flag = _identity_flag(spine_view.derive_spine(broke_dump), "2023-12-31")
    assert flag is not None, "the CURRENT filing does not balance — that is news"
    assert flag["residual"] == 6_000_000_000
    # The flag names the ONE vintage it checked, so the residual is
    # reproducible from the flag alone rather than from a list of filings
    # the reader would have to re-combine.
    assert flag["accessions"] == [_OTHER_ACCESSION]
    assert flag["checked_vintage"] == {
        "as_of": "2025-02-01",
        "source_accession": _OTHER_ACCESSION,
    }
    assert flag["components"]["total_equity"] == 44_000_000_000


def test_a_period_no_single_filing_covers_is_uncheckable_not_flagged(
    store, spine_view
):
    """UNCHECKABLE ≠ WRONG, extended to the vintage axis. When no ONE filing
    carries all three totals for a period, there is no identity to evaluate —
    the same honest silence this check already keeps for the 13 of 46 probed
    filers that never tag a total `Liabilities`.

    The mixture here is off by 30,000 M (1.5e-01 relative), so a `latest`-per-
    component reading would flag it loudly; no filing ever asserted those
    three figures together.
    """
    company = "NO-COMPLETE-VINTAGE"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000, "2024-02-01"),
            _balance(company, _EQUITY, "FY2023", "2023-12-31", 50_000_000_000, "2024-02-01"),
            _balance(
                company, _LIABILITIES, "FY2023", "2023-12-31", 120_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
            _balance(
                company, _EQUITY, "FY2023", "2023-12-31", 50_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert _identity_flag(derived, "2023-12-31") is None
    # Not dropped either — every as-reported figure still rides through.
    assert _values_by_end(_series(derived, "total_assets")) == {
        "2023-12-31": 200_000_000_000
    }
    assert _values_by_end(_series(derived, "total_liabilities")) == {
        "2023-12-31": 120_000_000_000
    }


def test_the_equity_completing_terms_come_from_the_checked_filing_too(
    store, spine_view
):
    """The mezzanine and `MinorityInterest` are read from the CHECKED vintage,
    not from their own latest — otherwise the fix would leave two of the five
    components still crossing filings.

    Here a later filing tags only those two identity-only concepts for the
    instant (it restates neither total), so their `latest` is one vintage newer
    than the newest filing carrying the three totals. The checked filing
    balances exactly; reading their latest instead yields a 6,000 M residual.
    """
    company = "TERMS-FROM-CHECKED-VINTAGE"
    dump = _dump_of(
        store,
        company,
        [
            _balance(company, _ASSETS, "FY2023", "2023-12-31", 201_000_000_000, "2024-02-01"),
            _balance(company, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(company, _EQUITY, "FY2023", "2023-12-31", 44_000_000_000, "2024-02-01"),
            _balance(company, _TEMPORARY_EQUITY, "FY2023", "2023-12-31", 1_000_000_000, "2024-02-01"),
            _balance(company, _MINORITY_INTEREST, "FY2023", "2023-12-31", 6_000_000_000, "2024-02-01"),
            _balance(
                company, _TEMPORARY_EQUITY, "FY2023", "2023-12-31", 4_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
            _balance(
                company, _MINORITY_INTEREST, "FY2023", "2023-12-31", 9_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert _identity_flag(derived, "2023-12-31") is None, (
        "201,000 = 150,000 + 1,000 + 44,000 + 6,000 in the checked filing"
    )


def test_a_term_the_checked_filing_omits_is_a_missing_amount_not_a_zero(
    store, spine_view
):
    """The one rule that keeps "absent reads as 0" honest once values are
    vintage-scoped.

    Absence reads as 0 because an untagged mezzanine / `MinorityInterest` is
    the balance sheet asserting there is none (measured — see the two tests
    above). But when ANOTHER filing of the SAME instant tagged the concept,
    that instant demonstrably HAD one, and the checked filing simply does not
    give us its amount. Reading 0 there would manufacture a residual equal to
    the omitted term and falsely accuse the filer — the exact failure mode
    this whole check keeps being burned by. So the PERIOD (across all its
    filings) says which terms exist; the CHECKED filing supplies every amount.

    Each filer below shrank in the restatement, so the omitted term cannot be
    mistaken for a rounding difference either way: read as 0 the residual is
    the whole term (1,000 M and 6,000 M), and read from the older filing it is
    the shrinkage on top of it.
    """
    mezzanine_dropped = "RESTATEMENT-OMITS-MEZZANINE"
    mezzanine_dump = _dump_of(
        store,
        mezzanine_dropped,
        [
            _balance(mezzanine_dropped, _ASSETS, "FY2023", "2023-12-31", 300_000_000_000, "2024-02-01"),
            _balance(mezzanine_dropped, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(mezzanine_dropped, _EQUITY, "FY2023", "2023-12-31", 50_000_000_000, "2024-02-01"),
            _balance(mezzanine_dropped, _TEMPORARY_EQUITY, "FY2023", "2023-12-31", 100_000_000_000, "2024-02-01"),
            _balance(
                mezzanine_dropped, _ASSETS, "FY2023", "2023-12-31", 201_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
            _balance(
                mezzanine_dropped, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
            _balance(
                mezzanine_dropped, _EQUITY, "FY2023", "2023-12-31", 50_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
        ],
    )
    minority_dropped = "RESTATEMENT-OMITS-MINORITY-INTEREST"
    minority_dump = _dump_of(
        store,
        minority_dropped,
        [
            _balance(minority_dropped, _ASSETS, "FY2023", "2023-12-31", 250_000_000_000, "2024-02-01"),
            _balance(minority_dropped, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000, "2024-02-01"),
            _balance(minority_dropped, _EQUITY, "FY2023", "2023-12-31", 44_000_000_000, "2024-02-01"),
            _balance(minority_dropped, _MINORITY_INTEREST, "FY2023", "2023-12-31", 56_000_000_000, "2024-02-01"),
            _balance(
                minority_dropped, _ASSETS, "FY2023", "2023-12-31", 200_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
            _balance(
                minority_dropped, _LIABILITIES, "FY2023", "2023-12-31", 150_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
            _balance(
                minority_dropped, _EQUITY, "FY2023", "2023-12-31", 44_000_000_000,
                "2025-02-01", accession=_OTHER_ACCESSION,
            ),
        ],
    )

    assert _identity_flag(
        spine_view.derive_spine(mezzanine_dump), "2023-12-31"
    ) is None, "the omitted mezzanine is a missing amount, not a zero"
    assert _identity_flag(
        spine_view.derive_spine(minority_dump), "2023-12-31"
    ) is None, "the omitted non-controlling interest is a missing amount, not a zero"


def test_resolves_a_different_concept_per_period(store, spine_view):
    """A filer that switched revenue tags mid-history yields ONE continuous
    `revenue` series spanning both eras.

    This is the reason the store holds as-reported concepts instead of
    pre-resolved canonical values: resolution is per PERIOD, not per company.
    A per-company winner (the shipped top-line lane's `break`-on-first-hit)
    would keep only the pre-switch years and silently truncate the history.
    """
    company = "SWITCHER"
    dump = _dump_of(
        store,
        company,
        [
            _point(company, "us-gaap:Revenues", "FY2016", "2016-01-01", "2016-12-31", 85320000000, "2017-02-01"),
            _point(company, "us-gaap:Revenues", "FY2017", "2017-01-01", "2017-12-31", 89950000000, "2018-02-01"),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2018", "2018-01-01", "2018-12-31", 110360000000, "2019-02-01",
            ),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2019", "2019-01-01", "2019-12-31", 125843000000, "2020-02-01",
            ),
        ],
    )

    derived = spine_view.derive_spine(dump)

    revenue = _series(derived, "revenue")
    assert _values_by_end(revenue) == {
        "2016-12-31": 85320000000,
        "2017-12-31": 89950000000,
        "2018-12-31": 110360000000,
        "2019-12-31": 125843000000,
    }
    # Provenance survives: each period still names the concept it came from,
    # so a reader can tell WHICH tag carried the field in that period.
    concepts = [p["latest"]["kpi_id"] for p in revenue["periods"]]
    assert concepts == [
        "us-gaap:Revenues",
        "us-gaap:Revenues",
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
    ]
    assert derived["company"] == company


def test_a_field_no_concept_ever_tagged_yields_no_row(store, spine_view):
    """Honest absence: a spine field whose chain concepts appear nowhere in
    the store produces NO series entry at all — never a 0, never a derived
    guess, never an empty placeholder row.

    Measured on the 46-filer probe: 22 filers report no gross profit and 13
    never tag a total `Liabilities`. A hole is the truth about the filing,
    not a defect in the view.
    """
    company = "NO-GROSS-PROFIT"
    dump = _dump_of(
        store,
        company,
        [
            _point(company, "us-gaap:Revenues", "FY2020", "2020-01-01", "2020-12-31", 12000, "2021-02-01"),
            _point(company, "us-gaap:Assets", "FY2020", None, "2020-12-31", 44000, "2021-02-01", kind="instant"),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert _series_ids(derived) == ["revenue", "total_assets"]
    assert "gross_profit" not in _series_ids(derived)
    assert derived["warnings"] == dump["warnings"]


def test_chain_order_resolves_a_same_period_overlap(store, spine_view):
    """When two chain concepts BOTH carry the same period, the chain's order
    is the tiebreak — first present wins, deterministically.

    Order is a same-period tiebreak only; it is never a per-company winner
    (the previous test proves the loser still supplies the periods the
    winner does not cover).
    """
    company = "OVERLAP"
    dump = _dump_of(
        store,
        company,
        [
            _point(company, "us-gaap:Revenues", "FY2021", "2021-01-01", "2021-12-31", 700, "2022-02-01"),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2021", "2021-01-01", "2021-12-31", 690, "2022-02-01",
            ),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2022", "2022-01-01", "2022-12-31", 810, "2023-02-01",
            ),
        ],
    )

    derived = spine_view.derive_spine(dump)

    revenue = _series(derived, "revenue")
    assert _values_by_end(revenue) == {"2021-12-31": 700, "2022-12-31": 810}
    assert revenue["periods"][0]["latest"]["kpi_id"] == "us-gaap:Revenues"


def test_null_axis_key_periods_are_never_merged_across_concepts(store, spine_view):
    """A `period_axis_key` of null means "not proven to be the same period",
    NOT "no period" — so two null-key entries from two concepts must never
    collapse into one resolved period.

    A 15-month transition FY is the real shape: the store refuses to size it
    to 1..4 quarters, so its axis key is null. Keying resolution on the raw
    null would silently drop one filer-reported figure.
    """
    company = "TRANSITION-FY"
    dump = _dump_of(
        store,
        company,
        [
            _point(company, "us-gaap:Revenues", "FY2014T", "2013-10-01", "2014-12-31", 51, "2015-02-01"),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2014T", "2013-10-01", "2014-12-31", 52, "2015-02-01",
            ),
        ],
    )
    stored_keys = {
        period["period_axis_key"]
        for entry in dump["series"]
        for period in entry["periods"]
    }
    assert stored_keys == {None}, "fixture precondition: the store cannot size this span"

    derived = spine_view.derive_spine(dump)

    revenue = _series(derived, "revenue")
    assert len(revenue["periods"]) == 2
    assert sorted(p["latest"]["canonical_value"] for p in revenue["periods"]) == [51, 52]


def test_derived_payload_renders_through_the_tearsheet_formatter(store, spine_view):
    """The emitted payload is the SAME pinned schema the shipped formatter
    already consumes — so `kpi_store dump | kpi_spine_view derive |
    tearsheet_format` composes with tearsheet_format.py untouched.
    """
    company = "RENDERABLE"
    dump = _dump_of(
        store,
        company,
        [
            _point(company, "us-gaap:Revenues", "FY2016", "2016-01-01", "2016-12-31", 85320000000, "2017-02-01"),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2018", "2018-01-01", "2018-12-31", 110360000000, "2019-02-01",
            ),
            _point(company, "us-gaap:NetIncomeLoss", "FY2018", "2018-01-01", "2018-12-31", 16571000000, "2019-02-01"),
        ],
    )
    formatter = _load("tearsheet_format_for_spine_view", TEARSHEET_FORMAT_SCRIPT)

    derived = spine_view.derive_spine(dump)
    derived["as_of"] = "2026-07-26"
    rendered = formatter.render_tearsheet(derived)

    assert "| revenue |" in rendered
    assert "| net_income |" in rendered
    assert "85,320,000,000 USD" in rendered
    assert "110,360,000,000 USD" in rendered
    assert "us-gaap:" not in rendered


def test_cli_derive_reads_a_dump_from_stdin_or_path(store, spine_view, tmp_path):
    """`kpi_spine_view.py derive --dump <path>` (stdin when omitted) — the
    pinned invocation shape, so the render pipeline is a plain pipe.
    """
    company = "CLI"
    dump = _dump_of(
        store,
        company,
        [_point(company, "us-gaap:Assets", "FY2020", None, "2020-12-31", 44000, "2021-02-01", kind="instant")],
    )
    expected = spine_view.derive_spine(dump)
    raw = json.dumps(dump)

    piped = subprocess.run(
        ["uv", "run", "--script", str(KPI_SPINE_VIEW_SCRIPT), "derive"],
        input=raw, capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert piped.returncode == 0, piped.stderr
    assert json.loads(piped.stdout) == expected

    dump_path = tmp_path / "dump.json"
    dump_path.write_text(raw, encoding="utf-8")
    from_path = subprocess.run(
        ["uv", "run", "--script", str(KPI_SPINE_VIEW_SCRIPT), "derive", "--dump", str(dump_path)],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert from_path.returncode == 0, from_path.stderr
    assert json.loads(from_path.stdout) == expected


def _hand_fed_balance_period(concept: str, value) -> dict:
    """One pinned-schema period entry with NO `source_accession` — a shape
    `kpi_store.append`'s provenance guard cannot produce, reachable only by
    hand-feeding the CLI.
    """
    return {
        "period_start": None,
        "period_end": "2023-12-31",
        "period_kind": "instant",
        "period_axis_key": "2023-12-31|q0",
        "period_labels": ["FY2023"],
        "disagreement": False,
        "latest": {"kpi_id": concept, "canonical_value": value},
        "observations": [{"kpi_id": concept, "canonical_value": value}],
    }


def test_cli_derive_reports_a_malformed_dump_as_an_error_not_a_traceback():
    """The CLI is the HAND-FED surface, so every malformed input leaves by
    the same door: `error: ...` on stderr and exit 1.

    A flagged period whose components carry no `source_accession` is the one
    input that makes `derive_spine` raise (`assert_dqc_schema` rejects an
    empty `accessions` list — deliberate, since the alternatives are
    fabricating provenance or dropping a real residual). The raise is right;
    letting it reach the terminal as a raw traceback is not.
    """
    dump = {
        "company": "HAND-FED",
        "series": [
            {"kpi_id": "us-gaap:Assets",
             "periods": [_hand_fed_balance_period("us-gaap:Assets", 200_000_000_000)]},
            {"kpi_id": "us-gaap:Liabilities",
             "periods": [_hand_fed_balance_period("us-gaap:Liabilities", 150_000_000_000)]},
            {"kpi_id": "us-gaap:StockholdersEquity",
             "periods": [_hand_fed_balance_period("us-gaap:StockholdersEquity", 44_000_000_000)]},
        ],
        "warnings": [],
    }

    result = subprocess.run(
        ["uv", "run", "--script", str(KPI_SPINE_VIEW_SCRIPT), "derive"],
        input=json.dumps(dump), capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

    assert result.returncode == 1
    assert result.stderr.startswith("error: ")
    assert "Traceback" not in result.stderr
    assert result.stdout == ""


# =====================================================================
# THE AS-FILED VIEW (plan Task 7) — the 14 fields over the RECONSTRUCTION
# =====================================================================
#
# A SECOND ENTRY POINT, not a replacement, and the reason is structural: a
# store dump carries no calculation linkbase, so the reconstruction is not
# computable from `derive_spine`'s input at all. Its input is Task 9's
# `reconstruct` pack payload (pack_us.py `_reconstruction_payload`), which is
# plain JSON — which is what lets every test below run offline.
#
# FIXTURE PROVENANCE, per fixture and never in bulk:
#
#   OBSERVED — rows read verbatim from the committed live capture
#              tests/data/fixtures/us_statement_reconstruction_2026-07-26.json.
#              Only KO FY2017 and IBM FY2025 were captured WITH rows (the other
#              three filings are census-only), so those two are the whole
#              observed surface here.
#   CONSTRUCTED-CONVENTIONAL — written by hand to exercise a branch no captured
#              filing reaches, labelled at its own site.
#
# WHAT IS NOT OBSERVABLE OFFLINE, recorded so the coverage limit is visible
# rather than implied. The plan's RED named three filers by their measured
# revenue concepts — DUK (`RegulatedAndUnregulatedOperatingRevenue`), PLD
# (`RealEstateRevenueNet`) and PSX (its own declared total
# `RevenuesAndOtherIncome`, 104,622M, against the chain's 2.2%-low
# `SalesRevenueNet`, 102,354M). None of the three has rows in the committed
# capture, so none can ground a test here. KO FY2017 pins the SAME claim on
# OBSERVED rows: it tags `SalesRevenueGoodsNet`, which is not in
# `SPINE_FIELD_CHAINS["revenue"]` either, so the chain resolves nothing for it
# while the filing declares the total plainly. The claim is the structure, not
# the filer — the same re-grounding Task 5 applied when the plan named an oil
# major and only IBM was observable.

RECONSTRUCTION_CAPTURE = (
    _ROOT / "tests" / "data" / "fixtures"
    / "us_statement_reconstruction_2026-07-26.json"
)

# The 14 field names as this module has always emitted them. Written out
# rather than read from `SPINE_FIELD_CHAINS`, deliberately: read from the
# chain, this assertion would agree with any edit to the chain and could never
# fail — the plan's GREEN asks whether the names are the SAME ones, which only
# an independent transcription can answer.
_FOURTEEN_FIELDS = (
    "revenue", "gross_profit", "operating_income", "pretax_income",
    "net_income", "eps_basic", "total_assets", "total_liabilities",
    "total_equity", "cash", "operating_cash_flow", "investing_cash_flow",
    "financing_cash_flow", "capex",
)


def _captured_filing(ticker: str) -> dict:
    """One captured filing's rows, projected into Task 9's `reconstruct`
    payload shape — the same projection `pack_us._reconstruction_payload`
    performs on a live `Statements`, run here on captured rows so no network
    call is made.

    Assembly (`kpi_us_statement_shape.statements_for`) is not called HERE:
    Tasks 8 and 10 were editing that module in parallel when this helper was
    written, and it must not couple to a file in flight. The rows are filtered
    by the SAME published predicate assembly uses (`is_statement_line` + not
    abstract), so what reaches the view is what assembly would have produced.

    THAT LAST SENTENCE IS A CLAIM, AND IT IS NO LONGER UNCHECKED — which is
    the one exception to the paragraph above. `_really_produced_filing` at the
    bottom of this module DOES run assembly and the real
    `pack_us._reconstruction_payload`, and
    `test_the_real_reconstruct_producer_feeds_this_view` asserts the two
    routes give the same view. Drift in this mirror fails there.
    """
    capture = json.loads(RECONSTRUCTION_CAPTURE.read_text(encoding="utf-8"))
    filing = next(
        f for f in capture["filings"] if f["ticker"] == ticker and f["rows_captured"]
    )
    lines_module = _load(
        "kpi_us_statement_lines_for_spine_test",
        _SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_lines.py",
    )
    statements: dict[str, list[dict]] = {}
    for role in filing["roles_captured"]:
        kind = _kind_of_role(role["role"])
        if kind is None:
            continue
        statements[kind] = [
            {
                "label": row.get("label"), "concept": row.get("concept"),
                "level": row.get("level"), "weight": row.get("weight"),
                "calculation_parent": row.get("calculation_parent"),
                # The taxonomy's own debit/credit classification, which Task 8
                # added to `Line` and `asdict` therefore carries. Projected
                # from the SAME captured row as every other field — this helper
                # mirrors `pack_us._reconstruction_payload`, so a field missing
                # here is a field the view would never see in production.
                "balance": row.get("balance"),
                "values": dict(row.get("values") or {}),
            }
            for row in role["rows"]
            if lines_module.is_statement_line(row) and not row.get("is_abstract")
        ]
    return {
        "accession": filing["accession"],
        "form": filing["form"],
        "filingDate": filing["filing_date"],
        "statements": statements,
        "roles": {},
        "unrecognised_dimension_keys": [],
    }


def _kind_of_role(role: str) -> str | None:
    """Which statement a captured role is, decided here from the three role
    URIs this capture actually carries rather than by importing
    `kpi_us_statement_shape.statement_kind` — that module is being edited by
    two parallel tasks. Narrow on purpose: it answers for THIS fixture, and
    the real classifier is pinned by its own suite."""
    folded = role.rsplit("/", 1)[-1].lower()
    if "cashflow" in folded.replace("_", ""):
        return "cash_flow"
    if "balancesheet" in folded:
        return "balance_sheet"
    if "income" in folded or "operations" in folded:
        return "income"
    return None


def _payload(
    *filings: dict,
    company: str = "TEST CO",
    verification: dict | None = None,
    status: str | None = "ok",
) -> dict:
    """Task 9's `reconstruct` envelope around the given filings.

    `verification` and `status` are OPTIONAL AND OMITTED WHEN `None`, which is
    not laziness: the section the real pack emits always carries both, and a
    payload that carries neither is what a hand-fed or older caller pipes in.
    Both cases are exercised — see
    `test_a_refused_verification_stays_visible_through_the_view` — and the
    field-resolution tests above pass neither, because nothing they assert
    reads them.
    """
    reconstruction: dict = {
        "filings": list(filings), "failed_items": [],
        "requested": len(filings), "succeeded": len(filings),
        "failed": 0,
    }
    if status is not None:
        reconstruction["_status"] = status
    if verification is not None:
        reconstruction["verification"] = verification
    return {
        "pack": "reconstruct", "ticker": "TEST", "company": company,
        "reconstruction": reconstruction,
    }


def _field(view: dict, accession: str, name: str) -> dict:
    filings = [f for f in view["filings"] if f["accession"] == accession]
    assert len(filings) == 1, f"expected one filing {accession}, got {filings}"
    matches = [f for f in filings[0]["fields"] if f["field"] == name]
    assert len(matches) == 1, f"expected exactly one {name!r} field, got {matches}"
    return matches[0]


def test_sector_revenue_no_longer_blank(spine_view):
    """OBSERVED (KO FY2017, accession 0000021344-18-000008).

    THE PLAN'S RED, re-grounded on a filer whose rows this repo actually has.
    KO tags `SalesRevenueGoodsNet` — the beverage/pharma dialect the brief
    names alongside the utility (DUK), REIT (PLD) and refiner (PSX) dialects —
    and it is NOT in `SPINE_FIELD_CHAINS["revenue"]`. So the chain resolves
    NOTHING while the filing declares its total plainly, at 35,410M, labelled
    "NET OPERATING REVENUES". That premise is asserted first: without it this
    test would pass for the wrong reason the day someone widens the chain,
    which is the fix the brief rejected.

    IBM FY2025 rides along as the second OBSERVED filer: its income statement
    carries `CostOfRevenue`, whose local name matches the same revenue wording
    as `Revenues`, and something must tell the two apart.

    WHAT IBM DOES *NOT* EVIDENCE, corrected here after this test shipped for
    two rounds with the wrong reason attached. It said the calculation weight
    was "what makes the sign filter load-bearing". IBM carries BOTH signals on
    that row — weight -1.0 AND `balance='debit'` — so EITHER filter alone
    passes here and this filing cannot discriminate between them. The sign
    looked sufficient only because IBM subtracts its cost DIRECTLY from
    revenue; a filer whose cost block sums positively into its own subtotal
    (the oil-major layout, PSX's shape) defeats the sign entirely. Both signals
    are asserted below so the claim matches what the fixture can actually
    prove, and `test_a_cost_block_that_sums_positively_does_not_rival_the_total`
    is where the two are told apart.
    """
    chain = dict(spine_view.SPINE_FIELD_CHAINS)["revenue"]
    assert "SalesRevenueGoodsNet" not in chain, (
        "the premise of this test is that the chain CANNOT resolve KO's "
        "revenue concept; widening the chain is the fix the brief rejected"
    )

    ko, ibm = _captured_filing("KO"), _captured_filing("IBM")
    view = spine_view.derive_spine_as_filed(_payload(ko, ibm))

    revenue = _field(view, ko["accession"], "revenue")
    assert revenue["concept"] == "us-gaap_SalesRevenueGoodsNet"
    assert revenue["periods"]["duration_2017-01-01_2017-12-31"] == {
        "state": "value", "value": 35_410_000_000.0,
    }

    ibm_revenue = _field(view, ibm["accession"], "revenue")
    assert ibm_revenue["concept"] == "us-gaap_Revenues"
    assert ibm_revenue["periods"]["duration_2025-01-01_2025-12-31"]["value"] == (
        67_535_000_000.0
    )

    # The reason this filing cannot arbitrate between the two filters, asserted
    # rather than asserted-about: read the captured row and show it carries
    # both. A prose claim here would be the same untested claim this docstring
    # just retracted.
    cost = next(
        line for line in ibm["statements"]["income"]
        if line["concept"] == "us-gaap_CostOfRevenue"
    )
    assert cost["weight"] == -1.0 and cost["balance"] == "debit"


def test_a_filer_presenting_no_operating_income_renders_not_presented(spine_view):
    """OBSERVED (IBM FY2025). The plan's GREEN: `not_presented` reaches the
    reader as its own thing, DISTINCT from empty.

    IBM's income statement runs gross profit -> total expense and other
    (income) -> income from continuing operations before taxes. There is no
    operating-income line at all, which is the filer's own presentation and not
    a gap in ours. KO, which does present one, is asserted in the same test:
    the claim is that the two render DIFFERENTLY, and a test that only looked
    at IBM would pass if every field rendered `not_presented`.
    """
    ko, ibm = _captured_filing("KO"), _captured_filing("IBM")
    view = spine_view.derive_spine_as_filed(_payload(ko, ibm))

    ibm_operating = _field(view, ibm["accession"], "operating_income")
    assert ibm_operating["periods"]["duration_2025-01-01_2025-12-31"] == {
        "state": "not_presented", "value": None,
    }

    ko_operating = _field(view, ko["accession"], "operating_income")
    assert ko_operating["periods"]["duration_2017-01-01_2017-12-31"] == {
        # OBSERVED: the capture's `us-gaap_OperatingIncomeLoss` row, labelled
        # "OPERATING INCOME", FY2017. Read off the fixture rather than recalled
        # — this literal was first written from memory as 7,599M and the
        # captured filing refuted it.
        "state": "value", "value": 7_501_000_000.0,
    }


def test_the_as_filed_view_emits_the_same_fourteen_field_names(spine_view):
    """The plan's GREEN: the field names are byte-identical to today's.

    Asserted as an ORDERED tuple against an independent transcription, so both
    halves of "the same fields" are covered — that none was added, renamed or
    dropped, and that the statement reading order (income -> balance sheet ->
    cash flow) the module deliberately departs from an alphabetical sort for is
    the order this view emits too.
    """
    ko = _captured_filing("KO")
    view = spine_view.derive_spine_as_filed(_payload(ko))

    names = tuple(f["field"] for f in view["filings"][0]["fields"])
    assert names == _FOURTEEN_FIELDS
    assert tuple(f for f, _ in spine_view.SPINE_FIELD_CHAINS) == _FOURTEEN_FIELDS


def test_several_candidate_totals_stay_an_honest_gap(spine_view):
    """CONSTRUCTED-CONVENTIONAL — two sibling revenue totals under no common
    parent. Not observable offline: the measured instance is DUK's 2013-2017
    FILED range, which yields 2-3 candidate totals, and no DUK rows were
    captured.

    Kickoff decision 甲 (plan ## Notes): where the filing declares no single
    total, emit a VISIBLE TYPED GAP — never fall back to `SPINE_FIELD_CHAINS`,
    because a silently-low year reads as a downturn on a 10-year trend. The
    gap must therefore NOT be a value, and must not be `not_presented` either:
    the filer presents revenue lines, we simply cannot tell which is the total.
    Both halves are asserted, because picking one candidate and reporting
    `not_presented` are two different wrong answers.
    """
    filing = {
        "accession": "0000000000-00-000000", "form": "10-K",
        "filingDate": "2018-02-23",
        "statements": {"income": [
            {"label": "Regulated revenues", "concept": "us-gaap_RegulatedOperatingRevenue",
             "level": 3, "weight": 1.0, "calculation_parent": "us-gaap_OperatingIncomeLoss",
             "values": {"duration_2017-01-01_2017-12-31": 20_000_000_000.0}},
            {"label": "Nonregulated revenues",
             "concept": "us-gaap_UnregulatedOperatingRevenue",
             "level": 3, "weight": 1.0, "calculation_parent": "us-gaap_OperatingIncomeLoss",
             "values": {"duration_2017-01-01_2017-12-31": 3_000_000_000.0}},
        ]},
        "roles": {}, "unrecognised_dimension_keys": [],
    }

    view = spine_view.derive_spine_as_filed(_payload(filing))
    revenue = _field(view, filing["accession"], "revenue")

    assert revenue["concept"] is None
    assert revenue["periods"] == {}
    assert revenue["unresolved"] == (
        "us-gaap_RegulatedOperatingRevenue", "us-gaap_UnregulatedOperatingRevenue",
    )
    assert "20000000000" not in json.dumps(revenue), (
        "an unresolvable total must not leak a candidate's figure"
    )


# =====================================================================
# THE DISPOSITION OF `SPINE_FIELD_CHAINS` (plan Task 11)
# =====================================================================
#
# The plan drafted this task expecting the symbol to be DEAD after Task 7, so
# its RED offers two passing shapes: the symbol is gone, or its prose names
# what it is still for. Task 7 shipped the second world and the test is built
# for the world that shipped — `derive_spine_as_filed` binds exactly ONE field
# structurally (`revenue`) and resolves the other thirteen through this very
# chain, so deleting it would delete the resolution rule of both entry points.
#
# WHY THE EXCEPTION IS MEASURED RATHER THAN TRANSCRIBED. A test that hard-coded
# "revenue is the exception" would agree with any future change that made a
# second field structural, and the prose would quietly become false again —
# which is the exact defect this task exists to close, one round later. So the
# exception set is measured by RUNNING the view and the prose is checked
# against the measurement.
#
# WHAT THIS TEST CANNOT PROVE: that the prose is well written. It can prove
# that the prose names both readers, names every field that left, and states a
# count that matches what the code does. Prose quality is a reviewer's job.


def _chain_prose(spine_view) -> str:
    """The `#` comment block immediately preceding the `SPINE_FIELD_CHAINS`
    declaration — the symbol's only prose.

    Read from module SOURCE, never from an attribute: `SPINE_FIELD_CHAINS` is
    a module-level tuple, so `SPINE_FIELD_CHAINS.__doc__` returns `tuple`'s own
    docstring and asserting on it would test CPython rather than this module.
    """
    source = Path(spine_view.__file__).read_text(encoding="utf-8").splitlines()
    declaration = next(
        i for i, line in enumerate(source) if line.startswith("SPINE_FIELD_CHAINS")
    )
    block: list[str] = []
    index = declaration - 1
    while index >= 0 and source[index].startswith("#"):
        block.append(source[index])
        index -= 1
    assert block, "the declaration carries no comment block at all"
    return "\n".join(reversed(block))


def _fields_resolved_without_the_chain(spine_view) -> set[str]:
    """Which of the 14 fields the as-filed view resolves WITHOUT consulting
    `SPINE_FIELD_CHAINS`, measured by running the view over a real captured
    filing and recording which chains `_chain_concept` was actually asked for.

    Measured, not read off a list, so the answer follows the code: a field
    bound structurally tomorrow lands in this set on its own and forces the
    prose to say so.
    """
    field_of_chain = {chain: field for field, chain in spine_view.SPINE_FIELD_CHAINS}
    assert len(field_of_chain) == len(spine_view.SPINE_FIELD_CHAINS), (
        "two fields share a chain; this measurement cannot attribute the call"
    )
    consulted: set[str] = set()
    real = spine_view._chain_concept

    def recording(lines, chain):
        consulted.add(field_of_chain[chain])
        return real(lines, chain)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(spine_view, "_chain_concept", recording)
        spine_view.derive_spine_as_filed(_payload(_captured_filing("KO")))
    return set(_FOURTEEN_FIELDS) - consulted


def test_spine_field_chains_has_a_stated_disposition(spine_view):
    """The plan's RED. `SPINE_FIELD_CHAINS` survives Task 7, so its prose must
    say what it is STILL for — the claim that it resolves the spine's fields is
    now only partly true, and a half-true description of a money-path constant
    is the dead-but-live config the brief refuses to leave behind.

    Three checks, each of which a stale description fails:
      1. it names BOTH readers, since the chain now serves two entry points
         over two different inputs (`derive_spine` over the store dump,
         `derive_spine_as_filed` over the reconstruction) and a reader who
         edits it must know both are downstream;
      2. it names every field that no longer resolves through it — the
         universal claim and its exception in the same place, never one
         without the other;
      3. the count it claims equals the measured count, so the prose cannot
         drift away from the code silently — in EITHER direction, which the
         count is matched WITH ITS DENOMINATOR to buy. A bare `\\b{n}\\b`
         search passed on the case that matters most: the block already
         contains "14" (inside "13 of those 14"), so if `revenue` ever
         rejoined the chain, `still_served` would become 14 and a stale
         paragraph would satisfy the search. Binding "N of the M" is what
         makes the count a claim about the split rather than a number
         appearing somewhere.
    """
    left_the_chain = _fields_resolved_without_the_chain(spine_view)
    still_served = len(_FOURTEEN_FIELDS) - len(left_the_chain)
    prose = _chain_prose(spine_view)

    for reader in ("`derive_spine`", "`derive_spine_as_filed`"):
        assert reader in prose, (
            f"the chain's prose does not name {reader}, which reads it"
        )
    for field in left_the_chain:
        assert field in prose, (
            f"{field!r} no longer resolves through the chain and the chain's "
            "own prose does not say so"
        )
    assert re.search(
        rf"\b{still_served} of (the |those )?{len(_FOURTEEN_FIELDS)}\b", prose
    ), (
        f"the chain still resolves {still_served} of the {len(_FOURTEEN_FIELDS)} "
        "fields and its prose does not state that count"
    )


def test_a_filing_with_no_revenue_line_at_all_is_not_presented(spine_view):
    """CONSTRUCTED-CONVENTIONAL — a bank-shaped income statement, whose lines
    are interest and fee income and carry no revenue wording at all. Not
    observable offline: all five captured filings are operating filers, and 9
    of the brief's 79-filer universe are financials with no rows captured.

    THE OTHER ZERO OF `_revenue_total`, and it must not be confused with the
    ambiguous one. Two candidate totals is "the filing declares revenue and we
    cannot tell which line is the total" — a typed `unresolved` gap naming
    them. NO candidate is a different fact: this filer has no single revenue
    origin by construction (brief §Open Questions, financial-sector filers), so
    the honest answer is `not_presented`, with no candidate list, exactly as if
    the line were absent — which it is.

    `net_income` is asserted on the same filing on purpose: without it, a
    statement that failed to parse at all would satisfy every assertion above
    and this test would pass for the wrong reason.
    """
    filing = {
        "accession": "0000000000-00-000001", "form": "10-K",
        "filingDate": "2018-02-23",
        "statements": {"income": [
            {"label": "Interest and dividend income",
             "concept": "us-gaap_InterestAndDividendIncomeOperating",
             "level": 3, "weight": 1.0,
             "calculation_parent": "us-gaap_InterestIncomeExpenseNet",
             "values": {"duration_2017-01-01_2017-12-31": 40_000_000_000.0}},
            {"label": "Interest expense", "concept": "us-gaap_InterestExpense",
             "level": 3, "weight": -1.0,
             "calculation_parent": "us-gaap_InterestIncomeExpenseNet",
             "values": {"duration_2017-01-01_2017-12-31": 9_000_000_000.0}},
            {"label": "Net interest income",
             "concept": "us-gaap_InterestIncomeExpenseNet",
             "level": 2, "weight": 1.0, "calculation_parent": None,
             "values": {"duration_2017-01-01_2017-12-31": 31_000_000_000.0}},
            {"label": "Net income", "concept": "us-gaap_NetIncomeLoss",
             "level": 2, "weight": 1.0, "calculation_parent": None,
             "values": {"duration_2017-01-01_2017-12-31": 24_000_000_000.0}},
        ]},
        "roles": {}, "unrecognised_dimension_keys": [],
    }

    view = spine_view.derive_spine_as_filed(_payload(filing))

    revenue = _field(view, filing["accession"], "revenue")
    assert revenue["concept"] is None
    assert "unresolved" not in revenue, (
        "no candidate is not an ambiguous total; naming candidates here would "
        "invite a reader to adjudicate a choice that was never offered"
    )
    assert revenue["periods"]["duration_2017-01-01_2017-12-31"] == {
        "state": "not_presented", "value": None,
    }

    net_income = _field(view, filing["accession"], "net_income")
    assert net_income["periods"]["duration_2017-01-01_2017-12-31"] == {
        "state": "value", "value": 24_000_000_000.0,
    }


def test_a_derivable_total_liabilities_is_derived_not_blanked(spine_view):
    """OBSERVED (KO FY2017). The arc's headline derivation must survive the
    trip through this view.

    KO tags `LiabilitiesAndStockholdersEquity` and NO `Liabilities` line, which
    is precisely when `cell_state`'s derivation applies — its own ranking puts
    `derived` ABOVE `not_presented` because "computable from the filer's own
    footing" is strictly more informative than "absent". A view that answers
    `not_presented` as soon as the chain binds nothing prints a blank where the
    filing's own arithmetic gives 68,919M, which is the failure this whole arc
    exists to remove, reproduced in the arc's own output.

    THE FORMULA IS ASSERTED, not just the number. A future short-circuit that
    emitted a bare figure would satisfy a value-only assertion while dropping
    the provenance that lets a reader audit it — and the mezzanine and minority
    terms in that formula are exactly the two the brief says must not be folded
    into "liabilities".

    The 2014/2015 instants are asserted `not_presented` in the same test: this
    is a claim that the view DISTINGUISHES the two, not that it derives
    everywhere. KO's earlier instants carry no footing to derive from.
    """
    ko = _captured_filing("KO")
    view = spine_view.derive_spine_as_filed(_payload(ko))
    liabilities = _field(view, ko["accession"], "total_liabilities")

    assert liabilities["periods"]["instant_2017-12-31"] == {
        "state": "derived",
        "value": 68_919_000_000.0,
        "derivation": (
            "us-gaap:Liabilities = us-gaap:LiabilitiesAndStockholdersEquity"
            " - us-gaap:StockholdersEquity"
            " - us-gaap:TemporaryEquityCarryingAmountIncluding"
            "PortionAttributableToNoncontrollingInterests"
            " - us-gaap:MinorityInterest"
        ),
    }
    assert liabilities["periods"]["instant_2014-12-31"] == {
        "state": "not_presented", "value": None,
    }


def test_a_negative_parent_does_not_orphan_its_children_into_totals(spine_view):
    """CONSTRUCTED-CONVENTIONAL — an IBM-shaped cost block broken into
    revenue-worded components. Not observable offline: IBM's captured statement
    presents `CostOfRevenue` as a single line with no children, so nothing in
    the capture reaches this branch.

    THE BUG THIS PINS. The sign filter drops a negative-weight revenue-worded
    line (`CostOfRevenue`). If the parent set is built from the SURVIVORS, that
    line stops existing as a parent, and its own revenue-worded children look
    parentless — so they join the totals set, the count exceeds one, and the
    filer's revenue collapses to a false `unresolved` gap. Building the parent
    set from ALL wording matches BEFORE the sign filter is what keeps a
    component recognisable as a component regardless of which side of the sign
    its parent sits on.
    """
    filing = {
        "accession": "0000000000-00-000002", "form": "10-K",
        "filingDate": "2026-02-24",
        "statements": {"income": [
            {"label": "Revenue", "concept": "us-gaap_Revenues", "level": 4,
             "weight": 1.0, "calculation_parent": "us-gaap_GrossProfit",
             "values": {"duration_2025-01-01_2025-12-31": 67_535_000_000.0}},
            {"label": "Cost", "concept": "us-gaap_CostOfRevenue", "level": 4,
             "weight": -1.0, "calculation_parent": "us-gaap_GrossProfit",
             "values": {"duration_2025-01-01_2025-12-31": 30_000_000_000.0}},
            {"label": "Cost of services revenue",
             "concept": "ibm_CostOfServicesRevenue", "level": 5, "weight": 1.0,
             "calculation_parent": "us-gaap_CostOfRevenue",
             "values": {"duration_2025-01-01_2025-12-31": 20_000_000_000.0}},
            {"label": "Cost of sales", "concept": "ibm_CostOfSalesRevenue",
             "level": 5, "weight": 1.0,
             "calculation_parent": "us-gaap_CostOfRevenue",
             "values": {"duration_2025-01-01_2025-12-31": 10_000_000_000.0}},
        ]},
        "roles": {}, "unrecognised_dimension_keys": [],
    }

    revenue = _field(
        spine_view.derive_spine_as_filed(_payload(filing)),
        filing["accession"], "revenue",
    )
    assert "unresolved" not in revenue, (
        "the cost block's components are components, not rival totals"
    )
    assert revenue["concept"] == "us-gaap_Revenues"
    assert revenue["periods"]["duration_2025-01-01_2025-12-31"]["value"] == (
        67_535_000_000.0
    )


def test_every_bound_concept_carries_the_filers_own_row_spelling(spine_view):
    """OBSERVED (KO FY2017). One payload, one spelling.

    A statement row spells the namespace separator `_`
    (`us-gaap_SalesRevenueGoodsNet`); the store's `kpi_id` spells it `:`. This
    view is over statement rows, and its own docstring defers the multi-year
    join to `kpi_us_statement_series.series_for`, which keys series identity on
    the filer's own concept — so two spellings under one key would split one
    series in two. The structural revenue rule reports the row's own concept;
    the chain path must not re-qualify its answer into the other spelling.
    """
    ko = _captured_filing("KO")
    view = spine_view.derive_spine_as_filed(_payload(ko))

    bound = {f["field"]: f["concept"] for f in view["filings"][0]["fields"]
             if f["concept"] is not None}
    assert bound["revenue"] == "us-gaap_SalesRevenueGoodsNet"
    assert bound["gross_profit"] == "us-gaap_GrossProfit"
    assert not [c for c in bound.values() if ":" in c], bound


def test_a_cost_block_that_sums_positively_does_not_rival_the_total(spine_view):
    """CONSTRUCTED-CONVENTIONAL row shape, OBSERVED figures — a PSX-shaped
    refiner: a revenue block and a cost block, EACH summing POSITIVELY into its
    own subtotal, both subtotals meeting at income before taxes.

    Provenance, split because the two halves have different standing. The
    LAYOUT and concepts are the oil-major shape the brief names (PSX declares
    `RevenuesAndOtherIncome` as its total while the chain reaches only the
    component `SalesRevenueNet`); the FIGURES — 104,622M and 102,354M, the
    2.2% understatement — are the measurement recorded in the plan's Task 7
    acceptance. The ROWS are written here because PSX has no rows in the
    committed capture; no captured filing has this layout at all.

    WHY THE SIGN FILTER IS NOT ENOUGH, which is the whole point of this test.
    `CostOfRevenue` here carries weight +1.0 — it is ADDED into `CostsAndExpenses`,
    and it is that subtotal which is subtracted later. So the filer's own sign
    admits it as a candidate, it survives elimination (its parent is a cost
    concept, not a revenue-worded one), and the rule reports two rival totals
    and blanks the revenue of every filer with this layout. The taxonomy's
    `balance` attribute is what separates them: `RevenuesAndOtherIncome` is
    `credit`, `CostOfRevenue` is `debit`.

    This test replaces the claim `test_sector_revenue_no_longer_blank` used to
    make. IBM carries both signals, so it proved neither.
    """
    period = "duration_2017-01-01_2017-12-31"
    filing = {
        "accession": "0000000000-00-000003", "form": "10-K",
        "filingDate": "2018-02-23",
        "statements": {"income": [
            {"label": "Sales and other operating revenues",
             "concept": "us-gaap_SalesRevenueNet", "level": 4, "weight": 1.0,
             "balance": "credit",
             "calculation_parent": "us-gaap_RevenuesAndOtherIncome",
             "values": {period: 102_354_000_000.0}},
            {"label": "Equity in earnings of affiliates",
             "concept": "us-gaap_IncomeLossFromEquityMethodInvestments",
             "level": 4, "weight": 1.0, "balance": "credit",
             "calculation_parent": "us-gaap_RevenuesAndOtherIncome",
             "values": {period: 2_268_000_000.0}},
            {"label": "Total Revenues and Other Income",
             "concept": "us-gaap_RevenuesAndOtherIncome", "level": 3,
             "weight": 1.0, "balance": "credit",
             "calculation_parent": (
                 "us-gaap_IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
                 "ExtraordinaryItemsNoncontrollingInterest"
             ),
             "values": {period: 104_622_000_000.0}},
            {"label": "Purchased crude oil and products",
             "concept": "us-gaap_CostOfRevenue", "level": 4, "weight": 1.0,
             "balance": "debit", "calculation_parent": "us-gaap_CostsAndExpenses",
             "values": {period: 90_000_000_000.0}},
            {"label": "Total Costs and Expenses",
             "concept": "us-gaap_CostsAndExpenses", "level": 3, "weight": -1.0,
             "balance": "debit",
             "calculation_parent": (
                 "us-gaap_IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
                 "ExtraordinaryItemsNoncontrollingInterest"
             ),
             "values": {period: 99_000_000_000.0}},
        ]},
        "roles": {}, "unrecognised_dimension_keys": [],
    }

    revenue = _field(
        spine_view.derive_spine_as_filed(_payload(filing)),
        filing["accession"], "revenue",
    )

    assert "unresolved" not in revenue, (
        "the cost block sums positively into its own subtotal, so the sign "
        "cannot exclude it — a debit-balance line is not a revenue total"
    )
    assert revenue["concept"] == "us-gaap_RevenuesAndOtherIncome"
    assert revenue["periods"][period] == {
        "state": "value", "value": 104_622_000_000.0,
    }, "the filer's own declared total, not the chain's 2.2%-low component"


def test_a_revenue_concept_with_no_balance_is_still_admitted(spine_view):
    """CONSTRUCTED-CONVENTIONAL — a filer's OWN revenue concept, carrying no
    taxonomy balance at all.

    THE BALANCE FILTER MUST FAIL OPEN, and this is the test that stops it being
    tightened. Measured on the committed capture: 349 of 455 rows carry NO
    balance, against 55 credit and 51 debit. Requiring `credit` would therefore
    discard the filer's own custom concepts — the exact class this arc exists
    to keep, and the one no fixed chain could ever contain
    (`ko_UnusualOrInfrequentItemOperating` is the brief's example). Only a
    positively-identified `debit` may exclude a line.
    """
    period = "duration_2017-01-01_2017-12-31"
    filing = {
        "accession": "0000000000-00-000004", "form": "10-K",
        "filingDate": "2018-02-23",
        "statements": {"income": [
            {"label": "Refining revenues", "concept": "psx_RefiningRevenue",
             "level": 3, "weight": 1.0, "balance": None,
             "calculation_parent": "us-gaap_OperatingIncomeLoss",
             "values": {period: 104_622_000_000.0}},
            {"label": "Operating expenses",
             "concept": "us-gaap_OperatingExpenses", "level": 3, "weight": -1.0,
             "balance": "debit",
             "calculation_parent": "us-gaap_OperatingIncomeLoss",
             "values": {period: 97_000_000_000.0}},
        ]},
        "roles": {}, "unrecognised_dimension_keys": [],
    }

    revenue = _field(
        spine_view.derive_spine_as_filed(_payload(filing)),
        filing["accession"], "revenue",
    )
    assert revenue["concept"] == "psx_RefiningRevenue"
    assert revenue["periods"][period]["value"] == 104_622_000_000.0


# =====================================================================
# ONE REVENUE-TOTAL RULE, TWO CALLERS — the binding test
# =====================================================================
#
# This view and `kpi_us_statement_check` both need "which concept is this
# filing's revenue TOTAL", and for two rounds each carried its OWN answer. They
# were never verified against each other, and the branch's whole-branch review
# measured them diverged in three ways at once — wording, the parent test, and
# de-duplication. The rule now lives in `kpi_us_statement_check.revenue_totals`
# and this view reads it; the test below is what keeps that true, by asking the
# SAME question of both surfaces on fixtures built to hit each divergence.
#
# WHY IT ASSERTS THE ANSWER TOO, not only the agreement: two copies agreeing is
# not evidence that either is right
# (docs/loom/memory/convergence-is-not-evidence-when-the-sample-is-shared.md).
# Agreement alone would still pass the day both are wrong together, which is
# exactly the regime a single shared implementation creates.

# Every case CONSTRUCTED-CONVENTIONAL: each is a shape neither captured filing
# (KO FY2017, IBM FY2025) presents, which is why the divergence survived two
# rounds of tests grounded on those two. Each is labelled with the measured
# behaviour of the pre-fix spine, so a reader can tell what it cost.
_ONE_RULE_PERIOD = "duration_2017-01-01_2017-12-31"

_REVENUE_RULE_DIVERGENCES = (
    (
        # PRE-FIX SPINE: three rival totals, revenue blanked. The filer's
        # disaggregated lines roll into a revenue-named parent it does not
        # PRESENT, so a parent test keyed on the presented lines cannot see the
        # roll-up and reads two components as rival totals.
        "a revenue parent the filer does not present",
        [
            {"label": "Net revenues", "concept": "us-gaap_Revenues", "level": 3,
             "weight": 1.0, "balance": "credit", "calculation_parent": None,
             "values": {_ONE_RULE_PERIOD: 100_000_000.0}},
            {"label": "Products", "concept": "acme_ProductRevenue", "level": 4,
             "weight": 1.0, "balance": "credit",
             "calculation_parent": "acme_DisaggregatedRevenue",
             "values": {_ONE_RULE_PERIOD: 60_000_000.0}},
            {"label": "Services", "concept": "acme_ServiceRevenue", "level": 4,
             "weight": 1.0, "balance": "credit",
             "calculation_parent": "acme_DisaggregatedRevenue",
             "values": {_ONE_RULE_PERIOD: 40_000_000.0}},
        ],
        ("us-gaap_Revenues",),
    ),
    (
        # PRE-FIX SPINE: revenue blanked AND the one concept printed TWICE in
        # the rival list. The presentation rendering one fact on two rows is
        # observed (KO repeats `CashAndCashEquivalentsAtCarryingValue` on its
        # cash-flow statement); a filing cannot be ambiguous between its total
        # and itself.
        "a revenue row the presentation repeats",
        [
            {"label": "Net revenues", "concept": "us-gaap_Revenues", "level": 3,
             "weight": 1.0, "balance": "credit", "calculation_parent": None,
             "values": {_ONE_RULE_PERIOD: 100_000_000.0}},
            {"label": "Net revenues", "concept": "us-gaap_Revenues", "level": 4,
             "weight": 1.0, "balance": "credit", "calculation_parent": None,
             "values": {_ONE_RULE_PERIOD: 100_000_000.0}},
        ],
        ("us-gaap_Revenues",),
    ),
    (
        # PRE-FIX SPINE: revenue blanked. THE LIVE MONEY PATH. The spine matched
        # the wording "sales" as well as "revenue", so a custom cost-of-SALES
        # line was revenue-worded. It carries +1.0 into its own costs subtotal,
        # so the sign admits it, and it carries NO taxonomy balance — the
        # majority case, 349 of the 455 captured rows — so the balance filter
        # fails open and admits it too. It then stood as a second candidate.
        # The `sales` wording is what opened that hole and it bought nothing:
        # every revenue dialect the brief measured (`SalesRevenueGoodsNet`,
        # `SalesRevenueServicesNet`, `RealEstateRevenueNet`, `RevenueMineralSales`,
        # `RegulatedAndUnregulatedOperatingRevenue`, `RevenuesAndOtherIncome`)
        # carries `revenue` too.
        "a custom cost-of-sales line rolled into a costs subtotal",
        [
            {"label": "Net revenues", "concept": "us-gaap_Revenues", "level": 3,
             "weight": 1.0, "balance": "credit", "calculation_parent": None,
             "values": {_ONE_RULE_PERIOD: 100_000_000.0}},
            {"label": "Cost of sales", "concept": "acme_CostOfSales", "level": 4,
             "weight": 1.0, "balance": None,
             "calculation_parent": "us-gaap_CostsAndExpenses",
             "values": {_ONE_RULE_PERIOD: 70_000_000.0}},
            {"label": "Total costs and expenses",
             "concept": "us-gaap_CostsAndExpenses", "level": 3, "weight": -1.0,
             "balance": "debit", "calculation_parent": None,
             "values": {_ONE_RULE_PERIOD: 70_000_000.0}},
        ],
        ("us-gaap_Revenues",),
    ),
)


@pytest.mark.parametrize(
    "case_name,rows,expected_totals",
    _REVENUE_RULE_DIVERGENCES,
    ids=[case[0] for case in _REVENUE_RULE_DIVERGENCES],
)
def test_the_spine_reads_the_checks_revenue_total_rule(
    spine_view, statement_check, case_name, rows, expected_totals,
):
    """One rule, one implementation: what `kpi_us_statement_check.revenue_totals`
    answers is what this view's `revenue` field binds.

    Each case is a shape on which the two implementations gave DIFFERENT answers
    before the rule was unified, measured on this branch: the check resolved the
    filer's total and the spine reported a false `unresolved`, blanking the
    revenue of every filer with that layout.
    """
    filing = {
        "accession": "0000000000-00-000009", "form": "10-K",
        "filingDate": "2018-02-23",
        "statements": {"income": rows},
        "roles": {}, "unrecognised_dimension_keys": [],
    }

    # What the single implementation says, asked of it directly.
    totals = statement_check.revenue_totals(
        [spine_view._ReconstructedLine(row) for row in rows]
    )
    assert totals == expected_totals, (
        f"{case_name}: the shared rule's own answer changed"
    )

    # And what this view binds, asked through its public surface.
    revenue = _field(
        spine_view.derive_spine_as_filed(_payload(filing)),
        filing["accession"], "revenue",
    )
    assert "unresolved" not in revenue, (
        f"{case_name}: the check resolves this filing to {totals}; the spine "
        f"reports rivals {revenue.get('unresolved')} and blanks the revenue"
    )
    assert revenue["concept"] == expected_totals[0], case_name
    assert revenue["periods"][_ONE_RULE_PERIOD] == {
        "state": "value", "value": 100_000_000.0,
    }, case_name


# =====================================================================
# THE AS-FILED VIEW ON THE COMMAND SURFACE
# =====================================================================
#
# `derive_spine_as_filed` shipped wired to NO CLI, so the four-state cell
# taxonomy — the part that answers the user's actual question, "is this cell
# empty because the company has no such line, or because my pipeline lost
# it?" — was reachable only in-process. `derive-as-filed` is that second
# entry point on the module's existing CLI: it takes Task 9's `reconstruct`
# pack payload, where `derive` takes a `kpi_store dump --company` payload.
# Two entry points, two inputs, both shipped — `derive` is untouched.

def test_cli_derive_as_filed_types_every_cell_for_a_reader(tmp_path):
    """OBSERVED (KO FY2017 `0000021344-18-000008`, IBM FY2025
    `0000051143-26-000010`). `kpi_spine_view.py derive-as-filed --payload
    <path>` (stdin when omitted) — the same invocation shape as `derive`.

    WHAT A READER MUST BE ABLE TO SEE WITHOUT READING ANY CODE, which is why
    both filers ride in one payload rather than one test each: the two cells
    below render DIFFERENTLY. A subcommand that emitted the same blank for
    both would satisfy either assertion alone.

      * KO's `total_liabilities` is `derived` 68,919,000,000 — KO tags
        `LiabilitiesAndStockholdersEquity` and no `Liabilities` line, and the
        formula rides along so the reader can audit it. The two subtracted
        terms the brief says must never be folded into "liabilities" (the
        mezzanine and the minority interest) are named IN the formula, so a
        future short-circuit emitting a bare figure fails here.
      * IBM's `operating_income` is `not_presented` — IBM's income statement
        runs gross profit -> total expense -> income before taxes and
        declares no operating-income line at all. That is the filer's own
        presentation, not a hole in ours, and it must not read as blank.

    MONEY CROSSES THE JSON BOUNDARY AS EXACT TEXT, and that is asserted as a
    TYPE, not just a value: `"68919000000.0"`, a JSON string, is `str(Decimal)`
    — digit-for-digit lossless, keeping the scale the arithmetic produced. A
    JSON *number* here would mean the subcommand routed an exact decimal back
    through the binary representation this module family bans on money
    (docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md,
    which records that mode manufacturing a false restatement signal here
    once). The same projection `pack_us._decimal_text` makes, at the same kind
    of boundary, pinned the same way.
    """
    ko, ibm = _captured_filing("KO"), _captured_filing("IBM")
    raw = json.dumps(_payload(ko, ibm))

    piped = subprocess.run(
        ["uv", "run", "--script", str(KPI_SPINE_VIEW_SCRIPT), "derive-as-filed"],
        input=raw, capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert piped.returncode == 0, piped.stderr
    view = json.loads(piped.stdout)

    liabilities = _field(view, ko["accession"], "total_liabilities")
    assert liabilities["periods"]["instant_2017-12-31"] == {
        "state": "derived",
        "value": "68919000000.0",
        "derivation": (
            "us-gaap:Liabilities = us-gaap:LiabilitiesAndStockholdersEquity"
            " - us-gaap:StockholdersEquity"
            " - us-gaap:TemporaryEquityCarryingAmountIncluding"
            "PortionAttributableToNoncontrollingInterests"
            " - us-gaap:MinorityInterest"
        ),
    }
    assert isinstance(liabilities["periods"]["instant_2017-12-31"]["value"], str), (
        "money must cross as exact text; a JSON number means it went through "
        "the binary float representation this module family bans on money"
    )

    operating = _field(view, ibm["accession"], "operating_income")
    assert operating["periods"]["duration_2025-01-01_2025-12-31"] == {
        "state": "not_presented", "value": None,
    }

    payload_path = tmp_path / "reconstruct.json"
    payload_path.write_text(raw, encoding="utf-8")
    from_path = subprocess.run(
        ["uv", "run", "--script", str(KPI_SPINE_VIEW_SCRIPT),
         "derive-as-filed", "--payload", str(payload_path)],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert from_path.returncode == 0, from_path.stderr
    assert from_path.stdout == piped.stdout


# Two DIFFERENT malformed shapes, because they are caught by two different
# guards and a single case leaves one of them unpinned. Measured: with only
# the array case, deleting the whole not-an-object check still passed — the
# array fell through to `.get` on a list, which the shape door then reported,
# so the test could not tell the two doors apart. Each case therefore asserts
# the MESSAGE its own guard produces.
_MALFORMED_AS_FILED_PAYLOADS = (
    # The not-an-object door. Piping the wrong thing is how a caller reaches
    # it, so the message must name the shape that WAS expected — that is what
    # `_read_json_object`'s `noun` argument is for, and it is the only part of
    # this that tells a caller which subcommand they wanted.
    ("a JSON array", [{"pack": "reconstruct"}], "reconstruct payload"),
    # The wrong-shape-inside door: a genuine object whose `reconstruction` is
    # a string. It reaches `derive_spine_as_filed` and raises `AttributeError`
    # there, NOT the `ValueError` `derive`'s narrower catch handles.
    (
        "a payload whose reconstruction is not an object",
        {"pack": "reconstruct", "ticker": "KO", "reconstruction": "nope"},
        "cannot derive the as-filed spine",
    ),
)


@pytest.mark.parametrize(
    "case_name,payload,expected_in_stderr",
    _MALFORMED_AS_FILED_PAYLOADS,
    ids=[case[0] for case in _MALFORMED_AS_FILED_PAYLOADS],
)
def test_cli_derive_as_filed_reports_a_malformed_payload_as_an_error(
    case_name, payload, expected_in_stderr,
):
    """The as-filed subcommand is a HAND-FED surface too, so it leaves by the
    SAME door `derive` does: `error: ...` on stderr, exit 1, nothing on stdout.
    A traceback in a terminal is the failure this pins.
    """
    result = subprocess.run(
        ["uv", "run", "--script", str(KPI_SPINE_VIEW_SCRIPT), "derive-as-filed"],
        input=json.dumps(payload),
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

    assert result.returncode == 1, case_name
    assert result.stderr.startswith("error: "), case_name
    assert expected_in_stderr in result.stderr, case_name
    assert "Traceback" not in result.stderr, case_name
    assert result.stdout == "", case_name


# =====================================================================
# WHAT SURVIVES THE PIPE — the run's own degradation markers
# =====================================================================
#
# `references/cli-reference.md` recommends one composition:
#
#     pack.py --market us --pack reconstruct --ticker KO
#       | kpi_spine_view.py derive-as-filed
#
# so whatever the PACK says about its own health has to be readable on the
# far side of that pipe, or the recommended composition silently launders it.

def test_a_refused_verification_stays_visible_through_the_view(spine_view):
    """CONSTRUCTED-CONVENTIONAL, and the construction is a transcription: the
    two keys asserted here are the marker `pack_us.pack_reconstruct` writes
    when its verification layer refuses (`except Exception` ->
    `{"error": "as-filed verification refused this run: ...",
    "error_class": "verification"}`), together with the fold that then drops
    the section's own `_status` to `"partial"`.

    WHY THIS IS THIS ARC'S FAILURE MODE ONE LAYER UP. `kpi_us_statement_check`
    refuses rather than guesses, and the pack contains that refusal instead of
    letting it take an ~85s run down — loudly, in two places. A view that
    carried the filings and dropped the markers would hand its reader a
    payload BYTE-IDENTICAL to a clean run's: a blank that cannot be read,
    which is the exact defect the four cell states exist to remove.

    So the markers ride through for the reason already written above
    `failed_items`, and the SAME absence doctrine governs them as governs
    `Statements.by_kind`: a marker the payload does not carry is ABSENT here,
    never a fabricated empty. `{}` would say "verification ran and found
    nothing to say", which is a different and untrue claim.

    NOT FOLDED INTO ONE FLAG. `status` is the run's, `verification` is the
    arithmetic's, and a run can be `partial` for an acquisition failure with
    its verification perfectly clean — collapsing them would make a reader
    unable to tell which half degraded.
    """
    ko = _captured_filing("KO")
    clean_verification = {
        "by_era": [], "statements": [],
        "sum_checks": {"by_status": {}, "disagreements": []},
    }

    refused = spine_view.derive_spine_as_filed(_payload(
        ko,
        verification={
            "error": (
                "as-filed verification refused this run: "
                "no readable year in filing date 'n/a'"
            ),
            "error_class": "verification",
        },
        status="partial",
    ))
    clean = spine_view.derive_spine_as_filed(_payload(
        ko, verification=clean_verification, status="ok",
    ))

    assert refused != clean, (
        "a run whose verification refused must not be indistinguishable from "
        "a clean one on the far side of the documented pipe"
    )
    assert refused["verification"]["error_class"] == "verification"
    assert "refused this run" in refused["verification"]["error"]
    assert refused["status"] == "partial"

    assert "error" not in clean["verification"], clean["verification"]
    assert clean["status"] == "ok"
    # The degradation is carried BESIDE the fields, never instead of them:
    # the filings themselves reconstructed fine in both runs.
    assert refused["filings"] == clean["filings"]

    hand_fed = spine_view.derive_spine_as_filed(
        _payload(ko, verification=None, status=None)
    )
    assert "verification" not in hand_fed and "status" not in hand_fed, (
        "a payload carrying no marker must leave the key ABSENT -- an empty "
        "dict here would claim a verification that never ran"
    )


# =====================================================================
# THE PRODUCER -> CONSUMER SEAM, run for real
# =====================================================================
#
# `_captured_filing` above MIRRORS `pack_us._reconstruction_payload`'s
# projection by hand (it says so at its own site), and a mirror binds nothing:
# the day the producer renames a key, every test in this file keeps passing
# against a projection production no longer emits. That is structurally the
# same defect as two implementations of one rule with no test between them —
# the defect this branch already paid to close once, at the layer below.
#
# So this seam runs the REAL producer chain offline, end to end:
#
#   captured rows -> kpi_us_statement_shape.statements_for
#                 -> pack_us._reconstruction_payload
#                 -> kpi_spine_view.derive_spine_as_filed
#
# Nothing is stubbed but edgartools itself, whose two-call surface
# (`presentation_roles` + `get_statement`) is `statements_for`'s whole
# documented input contract.


class _CapturedXBRL:
    """The two attributes assembly reads off `edgar.xbrl.XBRL`, served from
    the committed capture. Anything else raises `AttributeError`, which is the
    point: the double fails loudly rather than drifting from the live surface.
    (`test_kpi_us_statement_shape.py` carries the same double for the same
    reason; duplicated rather than imported because that suite is a test
    module, not a published surface, and importing across suites couples two
    files' fixtures for one class.)"""

    def __init__(self, entry: dict):
        self._rows_by_role = {
            role["role"]: role["rows"]
            for role in entry["roles_captured"]
            if role.get("rows") is not None
        }
        self.presentation_roles = list(entry["presentation_roles"])

    def get_statement(self, role: str) -> list[dict]:
        return self._rows_by_role[role]


class _CapturedFiling:
    def __init__(self, entry: dict):
        self.accession_no = entry["accession"]
        self._xbrl = _CapturedXBRL(entry)

    def xbrl(self):
        return self._xbrl


def _really_produced_filing(ticker: str) -> dict:
    """One captured filing projected by the REAL producer, in the exact three
    lines `pack_us.pack_reconstruct` writes around it (`accession` / `form` /
    `filingDate` + the projection). `pack_reconstruct` itself cannot run here
    — it acquires over the network — so those three keys are the only
    hand-written part, and they are the part no test could have got wrong
    silently: the view reads them by name in its own assertions above.
    """
    capture = json.loads(RECONSTRUCTION_CAPTURE.read_text(encoding="utf-8"))
    entry = next(
        f for f in capture["filings"]
        if f["ticker"] == ticker and f["rows_captured"]
    )
    shape = _load(
        "kpi_us_statement_shape_for_spine_seam",
        _SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_shape.py",
    )
    pack_us = _load(
        "pack_us_for_spine_seam",
        _SKILLS / "data-markets" / "scripts" / "pack_us.py",
    )
    assembled = shape.statements_for(_CapturedFiling(entry))
    return {
        "accession": entry["accession"],
        "form": entry["form"],
        "filingDate": entry["filing_date"],
        **pack_us._reconstruction_payload(assembled),
    }


def test_the_real_reconstruct_producer_feeds_this_view(spine_view):
    """OBSERVED (KO FY2017 `0000021344-18-000008`), through the real producer.

    TWO CLAIMS, and the second is why this test exists at all:

      1. The view reads what production actually emits — KO's
         `total_liabilities` still derives to 68,919,000,000 carrying its
         formula when the payload comes from `pack_us._reconstruction_payload`
         rather than from this suite's hand-written mirror.
      2. The mirror and the producer AGREE. `_captured_filing` writes out
         seven line keys by hand; the producer emits `asdict(Line)`. Any key
         the producer renames, drops or starts populating differently now
         fails HERE, where before it would have failed nowhere.

    WHAT THIS DOES NOT CLAIM: not that the two projections are IDENTICAL.
    `asdict(Line)` also carries `decimals`, which the mirror omits and which
    this view never reads — the equality asserted is of the VIEWS, so a
    divergence in a field the consumer ignores rightly does not fail. A
    divergence in one it reads does.
    """
    produced = _really_produced_filing("KO")
    mirrored = _captured_filing("KO")

    view = spine_view.derive_spine_as_filed(_payload(produced))

    liabilities = _field(view, produced["accession"], "total_liabilities")
    cell = liabilities["periods"]["instant_2017-12-31"]
    assert cell["state"] == "derived"
    assert str(cell["value"]) == "68919000000.0"
    assert cell["derivation"].startswith("us-gaap:Liabilities = ")

    assert view == spine_view.derive_spine_as_filed(_payload(mirrored)), (
        "the hand-written mirror in `_captured_filing` has drifted from "
        "`pack_us._reconstruction_payload`; the mirror is the copy, so the "
        "producer is right and the mirror is what must move"
    )


def test_the_skill_index_names_every_subcommand_this_cli_exposes():
    """The skill that OWNS this script is where a reader looks up what it can
    be asked to do, so a subcommand missing from that index is a subcommand
    that effectively does not exist (`derive-as-filed` shipped with a CLI, a
    reference page and a data-markets cross-link, and was absent HERE).

    THE EXPECTED LIST IS ASKED OF THE CLI, never transcribed: `--help` is the
    live surface, so a third subcommand added later fails this test until it
    is declared too. That is the whole point — the transcription is what went
    stale the first time.
    """
    listed = subprocess.run(
        ["uv", "run", "--script", str(KPI_SPINE_VIEW_SCRIPT), "--help"],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert listed.returncode == 0, listed.stderr
    choices = re.search(r"\{([a-z0-9,\-]+)\}", listed.stdout)
    assert choices is not None, listed.stdout
    subcommands = choices.group(1).split(",")
    assert "derive-as-filed" in subcommands, subcommands

    skill_doc = (_SKILLS / "analysis-kpi" / "SKILL.md").read_text(encoding="utf-8")
    entry = next(
        # ITS OWN BULLET, cut at the blank line that ends it. Searching the
        # whole file would pass on a mention anywhere else in it — the CLI
        # index is what a reader scans, and that is what must carry the name.
        block.split("\n\n")[0]
        for block in skill_doc.split("\n- ")
        if block.startswith("**`kpi_spine_view`**")
    )
    for subcommand in subcommands:
        assert f"`{subcommand}`" in entry, (
            f"{subcommand!r} is on this script's command surface but the "
            f"analysis-kpi skill index does not name it: {entry!r}"
        )
