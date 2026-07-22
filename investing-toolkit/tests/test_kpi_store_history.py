"""RED-first tests for the history read (Slice C, Task 6).

`kpi_store.history(company, kpi_id, period_match)` returns every stored
observation of ONE fiscal period across filings, ordered by `as_of`, with a
computed `disagreement` flag. The point of the read (brief §Problem, the J&J
shape): J&J's FY2021 revenue was 93,775,000,000 in the FY2021/FY2022 10-Ks then
re-presented as 78,740,000,000 in the FY2023 10-K — a -16% revision to a
two-year-old figure. A user who recorded the old value has no way to know it
changed. `history` surfaces ALL vintages (none dropped as "wrong") and flags
when they disagree.

Contract exercised here:
  - matching is by T3's `same_period` over the raw `(period_start, period_end)`
    identity, NOT exact string equality on the old `period` label — the two J&J
    vintages carry DIFFERENT `period` labels but the SAME date pair and must
    still group (this is the whole point of the slice).
  - observations ordered by `as_of` (ISO string, consistent with query_latest).
  - `disagreement=True` iff >=2 returned observations differ in `value` after
    unit normalization; same value -> False; a single observation -> False.
  - a superseded value is RETAINED and returned, never marked "wrong".
  - a stored `value` is NOT always base-scale: the 8-K TABLE lane stores a RAW,
    unscaled cell value paired with a scale-word `unit` (kpi_8k_candidates
    commits value="301.63", unit="millions"), so `history` scales each value by
    its unit's scale-word multiplier before comparing.
  - units that differ across observations are surfaced as `unit_mismatch=True`
    (an INDEPENDENT informational flag) but NEVER suppress a genuine value
    disagreement — a differing unit LABEL neither invents nor hides a conflict.

No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-22-kpi-observation-
history.md) binds tasks by "Brief item covered", not registered loom-spec
REQ-ids, so there is no id in the living-spec namespace to bind to (same
convention as test_kpi_store_period_identity.py / test_kpi_store_enumerate.py).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPT = (
    _TESTS_DIR.parent
    / "skills"
    / "analysis-kpi"
    / "scripts"
    / "kpi_store.py"
)

# A representative probe carrying only the period-identity fields `same_period`
# reads — history matches stored points against THIS via same_period, not by
# the old `period` label string.
_PROBE = {
    "period_start": "2021-01-01",
    "period_end": "2021-12-31",
    "period_kind": "duration",
}


def _load_module():
    spec = importlib.util.spec_from_file_location("kpi_store_history", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_store_history"] = module
    spec.loader.exec_module(module)
    return module


def _point(
    company,
    kpi_id,
    *,
    value,
    as_of,
    accession,
    period_label,
    period_start="2021-01-01",
    period_end="2021-12-31",
    period_kind="duration",
    unit=None,
):
    """A minimal store-valid point: full provenance + a non-wall-clock as_of so
    `append` accepts it, plus the raw period-identity fields T2/T3 read. Two
    observations of one period MUST differ in `as_of` AND `source_accession` so
    the dedup key does not silently drop the second (that is exactly why the
    J&J restatement is visible at all).
    """
    return {
        "company": company,
        "kpi_id": kpi_id,
        "period": period_label,
        "period_start": period_start,
        "period_end": period_end,
        "period_kind": period_kind,
        "unit": unit,
        "as_of": as_of,
        "value": value,
        "source_accession": accession,
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
    }


def test_history_flags_disagreement_across_filings(tmp_path, monkeypatch):
    """The J&J shape, three cases of one contract:
      (a) two observations of ONE period (93,775,000,000 then 78,740,000,000)
          from different accessions/as_of -> BOTH returned, ordered by as_of,
          disagreement=True. Both retained; neither marked "wrong". The two
          vintages carry DIFFERENT `period` labels but the same date pair, so
          grouping is by same_period, never by the label string.
      (b) two observations with the SAME value -> disagreement=False.
      (c) a SINGLE observation -> disagreement=False.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    # (a) J&J FY2021 revenue: as-first-reported vs re-presented, different
    # filings, DIFFERENT period labels but the same real (start, end) period.
    module.append(
        _point(
            "JNJ", "revenue",
            value=93775000000, as_of="2022-02-16",
            accession="0000200406-22-000006", period_label="FY2021",
        )
    )
    module.append(
        _point(
            "JNJ", "revenue",
            value=78740000000, as_of="2024-02-15",
            accession="0000200406-24-000010", period_label="2021 (comparative)",
        )
    )

    result = module.history("JNJ", "revenue", _PROBE)

    obs = result["observations"]
    assert len(obs) == 2, "both vintages retained, none dropped as wrong"
    # Ordered by as_of ascending: the 2022 first-report before the 2024 recast.
    assert [o["value"] for o in obs] == [93775000000, 78740000000]
    assert [o["as_of"] for o in obs] == ["2022-02-16", "2024-02-15"]
    assert [o["source_accession"] for o in obs] == [
        "0000200406-22-000006",
        "0000200406-24-000010",
    ]
    assert result["disagreement"] is True
    assert result["unit_mismatch"] is False

    # (b) SAME value across two filings -> not a disagreement.
    module.append(
        _point(
            "JNJ", "employees",
            value=141700, as_of="2022-02-16",
            accession="0000200406-22-000006", period_label="FY2021",
        )
    )
    module.append(
        _point(
            "JNJ", "employees",
            value=141700, as_of="2023-02-15",
            accession="0000200406-23-000008", period_label="FY2021",
        )
    )
    agree = module.history("JNJ", "employees", _PROBE)
    assert len(agree["observations"]) == 2
    assert agree["disagreement"] is False

    # (c) a SINGLE observation -> not a disagreement.
    module.append(
        _point(
            "JNJ", "segments",
            value=3, as_of="2022-02-16",
            accession="0000200406-22-000006", period_label="FY2021",
        )
    )
    single = module.history("JNJ", "segments", _PROBE)
    assert len(single["observations"]) == 1
    assert single["disagreement"] is False


def test_history_scale_equal_across_units_is_not_a_disagreement(
    tmp_path, monkeypatch
):
    """Scale-equal-so-not-a-disagreement: value=12345 (unit="millions") vs
    value=12345000 (unit="thousands") are THE SAME figure at two scales —
    12345e6 == 12345000e3 == 1.2345e10 — so `disagreement=False`.

    This is real because the 8-K TABLE lane stores a RAW, unscaled cell value
    paired with a scale-word `unit`: kpi_8k_candidates commits value="301.63"
    with unit="millions" (test_kpi_8k_candidates_commit line 53-65,
    `_confirmed_complete_candidate`), the SKILL contract forbids altering
    `value`, and the `(in millions)` caption is surfaced only as an advisory
    `unit_hint`. So a stored value is NOT always base-scale, and `history` must
    apply the unit's scale-word multiplier before comparing. Comparing the raw
    values without scaling would manufacture a false conflict on exactly this
    two-scales-of-one-figure case.

    The differing raw unit LABELS still surface as `unit_mismatch=True` (an
    independent caveat) — a label difference neither invents a disagreement (this
    test) nor suppresses one (`..._does_not_mask_real_disagreement`).
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    module.append(
        _point(
            "ACME", "revenue",
            value=12345, as_of="2022-02-16",
            accession="0000000000-22-000001", period_label="FY2021",
            unit="millions",
        )
    )
    module.append(
        _point(
            "ACME", "revenue",
            value=12345000, as_of="2023-02-15",
            accession="0000000000-23-000002", period_label="FY2021",
            unit="thousands",
        )
    )

    result = module.history("ACME", "revenue", _PROBE)
    assert len(result["observations"]) == 2, "both retained even under mismatch"
    assert result["unit_mismatch"] is True
    # 12345e6 == 12345000e3 — the same figure, so NOT a disagreement.
    assert result["disagreement"] is False


def test_scale_multiplier_matches_scale_word_as_whole_word(tmp_path, monkeypatch):
    """`_scale_multiplier` derives the multiplier from the unit's scale WORD,
    matched with word boundaries so a magnitude word that is only a SUBSTRING of a
    larger word never scales.

    The word-boundary guard is a documented Part-2 lesson (docs/loom/memory):
    "billionaire" must NOT match "billion", "millionaire households" must NOT be
    scaled. A dimensional prefix around the scale word ("USD millions",
    "$ in millions") still scales off the scale word. A plain dimensional label
    (USD) or None carries no scale word -> multiplier 1.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    assert module._scale_multiplier("thousands") == 1e3
    assert module._scale_multiplier("million") == 1e6
    assert module._scale_multiplier("millions") == 1e6
    assert module._scale_multiplier("billion") == 1e9
    assert module._scale_multiplier("trillion") == 1e12
    # Dimensional part around the scale word: multiplier comes from the word.
    assert module._scale_multiplier("USD millions") == 1e6
    assert module._scale_multiplier("$ in millions") == 1e6
    # Whole-word guard: substring occurrences must NOT scale.
    assert module._scale_multiplier("billionaire") == 1
    assert module._scale_multiplier("millionaire households") == 1
    # No scale word / absent unit -> multiplier 1.
    assert module._scale_multiplier("USD") == 1
    assert module._scale_multiplier(None) == 1


def test_history_word_boundary_unit_is_not_scaled(tmp_path, monkeypatch):
    """A KPI `unit` that merely CONTAINS a magnitude word as a substring
    ("millionaire households") must NOT be scaled — so a substring-match
    regression is caught here, not only in the helper's unit test.

    value=5 (unit="millionaire households") vs value=5000000 (unit=None): with
    the correct whole-word guard these scale to 5 and 5000000 (multiplier 1 each)
    -> genuinely DIFFERENT -> disagreement=True. A buggy substring match would
    scale the first by 1e6 to 5,000,000, falsely equating them to
    disagreement=False — which this asserts against.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    module.append(
        _point(
            "WEALTH", "millionaire_households",
            value=5, as_of="2022-02-16",
            accession="0000000000-22-000001", period_label="FY2021",
            unit="millionaire households",
        )
    )
    module.append(
        _point(
            "WEALTH", "millionaire_households",
            value=5000000, as_of="2023-02-15",
            accession="0000000000-23-000002", period_label="FY2021",
            unit=None,
        )
    )

    result = module.history("WEALTH", "millionaire_households", _PROBE)
    assert len(result["observations"]) == 2
    # "millionaire households" is NOT scaled -> 5 vs 5,000,000 -> a real diff.
    assert result["disagreement"] is True


def test_history_precision_normalization_same_value_same_unit(tmp_path, monkeypatch):
    """Precision/format normalization (the reason `_normalized_value` exists,
    previously untested — reviewer Finding 2): an int and a comma-formatted
    string of the SAME figure, same unit, are equal after normalization, so two
    such observations are NOT a disagreement.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    module.append(
        _point(
            "FMT", "revenue",
            value=93775, as_of="2022-02-16",
            accession="0000000000-22-000001", period_label="FY2021",
            unit="USD",
        )
    )
    module.append(
        _point(
            "FMT", "revenue",
            value="93,775", as_of="2023-02-15",
            accession="0000000000-23-000002", period_label="FY2021",
            unit="USD",
        )
    )

    result = module.history("FMT", "revenue", _PROBE)
    assert len(result["observations"]) == 2
    assert result["unit_mismatch"] is False
    assert result["disagreement"] is False


def test_history_precision_normalization_different_value_same_unit(
    tmp_path, monkeypatch
):
    """The counterpart: an int and a comma-string of DIFFERENT figures, same unit,
    are a genuine disagreement after normalization (comma-stripping does not hide
    a real difference).
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    module.append(
        _point(
            "FMT2", "revenue",
            value=93775, as_of="2022-02-16",
            accession="0000000000-22-000001", period_label="FY2021",
            unit="USD",
        )
    )
    module.append(
        _point(
            "FMT2", "revenue",
            value="78,740", as_of="2023-02-15",
            accession="0000000000-23-000002", period_label="FY2021",
            unit="USD",
        )
    )

    result = module.history("FMT2", "revenue", _PROBE)
    assert len(result["observations"]) == 2
    assert result["unit_mismatch"] is False
    assert result["disagreement"] is True


def test_history_corrupt_series_file_degrades_to_no_observations(
    tmp_path, monkeypatch
):
    """A corrupt/unreadable series file returns no observations rather than
    taking down the read — history's load is wrapped in the same
    (json.JSONDecodeError, OSError) skip as list_series (T1's degrade-loud
    posture), not left to raise out.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    module.append(
        _point(
            "CORRUPT", "revenue",
            value=100, as_of="2022-02-16",
            accession="0000000000-22-000001", period_label="FY2021",
        )
    )
    # Corrupt the just-written series file (only one exists in this store).
    (series_file,) = list(store_dir.glob("*.json"))
    series_file.write_text("{not valid json", encoding="utf-8")

    result = module.history("CORRUPT", "revenue", _PROBE)
    assert result["observations"] == []
    assert result["disagreement"] is False
    assert result["unit_mismatch"] is False


def test_history_unit_mismatch_does_not_mask_real_disagreement(tmp_path, monkeypatch):
    """THE regression: a genuine value conflict must NOT be silenced just because
    the observations' `unit` labels differ. Two observations of one period,
    93,775 (unit="millions") and 11,111 (unit=None) — an 8.4x gap, a real
    restatement — with a `unit` mismatch. The old code forced `disagreement=False`
    on ANY unit mismatch, so a caller reading only `disagreement` (its literal
    name/purpose) saw "no problem" for an obvious conflict. The fix: `disagreement`
    is the pure value diff (True here), and `unit_mismatch=True` is surfaced as an
    independent caveat, never a mask.

    Even AFTER scale-normalization the conflict stands: 93775 (unit="millions")
    scales to 9.3775e10 and 11111 (unit=None) to 11111 — an 8.4e6x gap. The
    scale multiplier removes false conflicts (two scales of one figure), it does
    NOT remove this real one. So `disagreement=True` and `unit_mismatch=True`
    (the labels "millions" vs None differ) coexist honestly.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    module.append(
        _point(
            "RESTATE", "revenue",
            value=93775, as_of="2022-02-16",
            accession="0000000000-22-000001", period_label="FY2021",
            unit="millions",
        )
    )
    module.append(
        _point(
            "RESTATE", "revenue",
            value=11111, as_of="2024-02-15",
            accession="0000000000-24-000002", period_label="FY2021",
            unit=None,
        )
    )

    result = module.history("RESTATE", "revenue", _PROBE)
    assert len(result["observations"]) == 2
    assert result["unit_mismatch"] is True
    # The load-bearing assertion: a real conflict is NOT reported as "no problem".
    assert result["disagreement"] is not False
    assert result["disagreement"] is True


def test_history_absent_series_returns_no_observations(tmp_path, monkeypatch):
    """`history` on a company/kpi with no stored series returns an empty
    observation list, disagreement=False, and never raises — the store's
    never-raise-on-read posture (matching list_series/query_latest).
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    result = module.history("NOBODY", "nothing", _PROBE)
    assert result["observations"] == []
    assert result["disagreement"] is False
    assert result["unit_mismatch"] is False
