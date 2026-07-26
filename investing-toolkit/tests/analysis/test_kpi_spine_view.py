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
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SKILLS = _ROOT / "skills"
KPI_STORE_SCRIPT = _SKILLS / "analysis-kpi" / "scripts" / "kpi_store.py"
KPI_SPINE_VIEW_SCRIPT = _SKILLS / "analysis-kpi" / "scripts" / "kpi_spine_view.py"
KPI_XBRL_SCRIPT = _SKILLS / "analysis-kpi" / "scripts" / "kpi_xbrl.py"
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
