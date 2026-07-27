"""test_fact_validation_guards.py — the fail-loud guards, held loudly.

Third batch from the 2026-07-27 sampled mutation pass. Each guard below exists
to REJECT an input rather than guess at it, and each says so in its own
docstring ("rejected, never fabricated", "surfaced rather than resolved by
guessing"). Weakening the `or` in a two-part guard admits exactly the inputs
the guard was written for, and nothing downstream raises — the fact simply
enters the store with a fabricated label.

The store is redirected per test: these modules resolve a durable,
append-only path, and a test must never write history into a real one.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from conftest import KPI_XBRL_SCRIPT

STORE_FS_SCRIPT = KPI_XBRL_SCRIPT.parent / "_store_fs.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def kpi_xbrl_guards():
    return _load(KPI_XBRL_SCRIPT, "kpi_xbrl_guard_test")


@pytest.fixture(scope="module")
def store_fs():
    return _load(STORE_FS_SCRIPT, "store_fs_guard_test")


# ---------------------------------------------------------------------------
# Mutant: kpi_xbrl.py:461  `not isinstance(pe, str) or not pe` -> `and`
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_period_end", [None, "", 20231231, [], {}])
def test_a_fact_without_a_usable_period_end_is_rejected(
    kpi_xbrl_guards, bad_period_end
):
    """`period_end` is the raw window every derived label is grounded in, and
    the guard commits to rejecting rather than fabricating `period "None"`.

    Every case here must be reported as MISSING, not merely rejected. The
    distinction is what makes the parametrisation hold the `or` -> `and`
    mutation instead of just documenting it: under the weakened guard `''`
    passes the type half, falls through to `date.fromisoformat('')`, and is
    reported as MALFORMED — an assertion of "is a ValueError mentioning
    period_end" is satisfied by both messages and catches nothing. An earlier
    revision of this test asserted exactly that, and its docstring claimed
    `''` was the discriminating case when it was the only one that was not.
    """
    fact = {"concept": "us-gaap:Revenues", "period_end": bad_period_end}

    with pytest.raises(ValueError) as caught:
        kpi_xbrl_guards._require_period(fact)

    assert "missing required 'period_end'" in str(caught.value), (
        f"{bad_period_end!r} must be reported as missing, not "
        f"reclassified: {caught.value}"
    )


def test_the_rejection_message_distinguishes_missing_from_malformed(
    kpi_xbrl_guards
):
    """The two failure modes have different messages, and the empty string is
    MISSING, not malformed. Under the weakened guard `''` falls through to the
    `date.fromisoformat` check and is reported as malformed instead — the fact
    is still rejected, so only the message reveals it."""
    with pytest.raises(ValueError) as missing:
        kpi_xbrl_guards._require_period(
            {"concept": "c", "period_end": ""}
        )
    with pytest.raises(ValueError) as malformed:
        kpi_xbrl_guards._require_period(
            {"concept": "c", "period_end": "not-a-date"}
        )

    assert "missing required 'period_end'" in str(missing.value)
    assert "malformed" in str(malformed.value)


# ---------------------------------------------------------------------------
# Mutant: kpi_xbrl.py:347  `not isinstance(fy, int) or isinstance(fy, bool)`
# ---------------------------------------------------------------------------

def _classifiable(**over):
    fact = {
        "concept": "us-gaap:Revenues", "period_end": "2024-12-31",
        "fiscal_year": 2024, "fiscal_quarter": "FY", "duration_months": 12,
    }
    fact.update(over)
    return fact


def test_a_boolean_fiscal_year_is_rejected_not_used_as_a_year(kpi_xbrl_guards):
    """Python calls `True` an `int`, so the type half of this guard passes it.
    The `or isinstance(fy, bool)` half is the whole defence; weakened to `and`,
    `True` classifies as fiscal year 1 and the fact enters the series under a
    year that does not exist."""
    with pytest.raises(Exception) as caught:
        kpi_xbrl_guards.classify_fact_period(_classifiable(fiscal_year=True))

    assert "fiscal_year" in str(caught.value)


@pytest.mark.parametrize("bad_year", [None, "2024", 2024.0])
def test_a_non_integer_fiscal_year_is_rejected(kpi_xbrl_guards, bad_year):
    """The other half of the same guard, so the bool test above is not the
    only thing holding it."""
    with pytest.raises(Exception) as caught:
        kpi_xbrl_guards.classify_fact_period(_classifiable(fiscal_year=bad_year))

    assert "fiscal_year" in str(caught.value)


def test_a_well_formed_fact_still_classifies(kpi_xbrl_guards):
    """The discriminator for all four rejections above: a valid fact must NOT
    raise, or the tests would pass against a guard that rejects everything."""
    out = kpi_xbrl_guards.classify_fact_period(_classifiable())

    assert out == {
        "period_type": "FY", "cumulative": False, "duration_class": "12mo-FY",
    }


# ---------------------------------------------------------------------------
# Mutant: _store_fs.py:62  `return Path(XDG_DATA_HOME)/...` -> `return None`
# ---------------------------------------------------------------------------

def test_xdg_data_home_selects_the_store_directory(store_fs, monkeypatch, tmp_path):
    """Rung 2 of the documented precedence ladder. Returning None here does
    not raise at resolution — it raises later, wherever the path is joined, on
    a machine that happens to set XDG_DATA_HOME. The store is irreplaceable
    history, so its location must be resolvable on every documented rung."""
    monkeypatch.delenv("KPI_STORE_DIR", raising=False)
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))

    resolved = store_fs.resolve_store_dir()

    assert resolved == tmp_path / "xdg" / "investing-toolkit" / "kpi-store"


def test_the_store_precedence_ladder_holds_all_three_rungs(
    store_fs, monkeypatch, tmp_path
):
    """Rung 1 outranks rung 2, and rung 3 is the fallback — pinned together so
    a change to one rung cannot silently reorder the others."""
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path / "explicit"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    assert store_fs.resolve_store_dir() == tmp_path / "explicit"

    monkeypatch.delenv("KPI_STORE_DIR")
    monkeypatch.delenv("XDG_DATA_HOME")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))
    assert store_fs.resolve_store_dir() == (
        tmp_path / "home" / ".local" / "share" / "investing-toolkit" / "kpi-store"
    )


def test_an_empty_env_var_is_treated_as_unset(store_fs, monkeypatch, tmp_path):
    """The ladder's documented "empty after strip = unset" rule, which is what
    stops a blank CI variable from resolving the store to the process CWD."""
    monkeypatch.setenv("KPI_STORE_DIR", "   ")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))

    assert store_fs.resolve_store_dir() == (
        tmp_path / "xdg" / "investing-toolkit" / "kpi-store"
    )
