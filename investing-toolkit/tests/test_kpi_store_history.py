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
  - `disagreement=True` iff >=2 returned observations differ in their CANONICAL
    value; same canonical -> False; a single observation -> False.
  - a superseded value is RETAINED and returned, never marked "wrong".
  - every stored point carries an EXPLICIT per-point `scale` set once at its
    producer (Slice C, Task 9), so the canonical compared here is
    `_normalized_value(value) * scale` — a trivial value diff with NO read-time
    parsing of a magnitude word out of the free-text `unit`. The 8-K TABLE lane
    stores the verbatim cell (value="301.63") with `scale=1e6`; the prose lane
    stores an already-base value with `scale` HARDCODED 1; so a cross-lane pair
    of the same figure canonicalizes equal without the `unit` driving anything.
    A point missing `scale` defaults to 1.

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
    scale=None,
):
    """A minimal store-valid point: full provenance + a non-wall-clock as_of so
    `append` accepts it, plus the raw period-identity fields T2/T3 read. Two
    observations of one period MUST differ in `as_of` AND `source_accession` so
    the dedup key does not silently drop the second (that is exactly why the
    J&J restatement is visible at all).

    `scale` is the EXPLICIT per-point multiplier from `value` to the base-scale
    figure (Task 9). It is added ONLY when supplied, so a point without it keeps
    exercising history's `scale`-missing default of 1.
    """
    point = {
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
    if scale is not None:
        point["scale"] = scale
    return point


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


def test_history_compares_base_via_explicit_scale(tmp_path, monkeypatch):
    """Slice C, Task 9 — every lane stores an EXPLICIT per-point `scale`, so the
    canonical history compares is `_normalized_value(value) * scale`, with NO
    read-time parsing of a magnitude word out of the free-text `unit`.

      (a) an 8-K-shaped point (value="301.63", scale=1e6) and a prose-shaped
          point (value=301630000, scale=1) for the SAME period read
          disagreement=False — both canonicalize to base 301,630,000. The 8-K
          point's `unit` is the DIMENSIONAL "USD" (not "millions"): the explicit
          `scale` field drives the magnitude, proving the read no longer parses
          the unit label.
      (b) a genuine restatement (both scale=1, 93,775,000,000 vs
          78,740,000,000 — the J&J payoff) reads disagreement=True.
      (c) a prose point tagged unit="billion" (scale HARDCODED 1 by the producer,
          value already the base 3,560,000,000) is NOT double-scaled: its
          canonical stays 3,560,000,000, so it AGREES with a plain 3,560,000,000
          point rather than exploding to 3.56e18. This is the trap the retired
          read-time inference (and its T8 write-guard) existed to prevent;
          hardcoding prose scale=1 makes it structurally impossible.

    No `@req` tag: same convention as the sibling tests (plan binds by "Brief
    item covered", not a registered loom-spec REQ-id).
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    # (a) 8-K raw cell (301.63 x 1e6) vs prose base (301,630,000 x 1) -> same base.
    # The 8-K `unit` is dimensional "USD"; the explicit scale, NOT the label,
    # carries the 1e6 — so an old read-time unit parser would have compared 301.63
    # (unit "USD" -> x1) against 301,630,000 and manufactured a false conflict.
    module.append(
        _point(
            "SAME", "revenue",
            value="301.63", as_of="2025-01-30",
            accession="0001065280-25-000033", period_label="Q4-2024",
            unit="USD", scale=1e6,
        )
    )
    module.append(
        _point(
            "SAME", "revenue",
            value=301630000, as_of="2025-04-30",
            accession="0001065280-25-000099", period_label="Q4-2024",
            unit="USD", scale=1,
        )
    )
    same = module.history("SAME", "revenue", _PROBE)
    assert len(same["observations"]) == 2
    assert same["disagreement"] is False, "301.63x1e6 == 301,630,000x1 — same base"

    # (b) genuine restatement, both already base -> a real disagreement.
    module.append(
        _point(
            "JNJ", "revenue",
            value=93775000000, as_of="2022-02-16",
            accession="0000200406-22-000006", period_label="FY2021", scale=1,
        )
    )
    module.append(
        _point(
            "JNJ", "revenue",
            value=78740000000, as_of="2024-02-15",
            accession="0000200406-24-000010",
            period_label="2021 (comparative)", scale=1,
        )
    )
    restated = module.history("JNJ", "revenue", _PROBE)
    assert restated["disagreement"] is True

    # (c) prose unit="billion" is NOT double-scaled: the producer hardcodes
    # scale=1 and the value is already folded to base 3,560,000,000 by the prose
    # _normalize_value. An old read-time parser seeing unit="billion" would have
    # multiplied it AGAIN to 3.56e18, forging a disagreement with the plain point.
    module.append(
        _point(
            "META", "dap",
            value=3560000000, as_of="2025-01-29",
            accession="0001326801-25-000004", period_label="Q4-2024",
            unit="billion", scale=1,
        )
    )
    module.append(
        _point(
            "META", "dap",
            value=3560000000, as_of="2025-04-30",
            accession="0001326801-25-000050", period_label="Q4-2024",
            unit="people", scale=1,
        )
    )
    not_double = module.history("META", "dap", _PROBE)
    assert len(not_double["observations"]) == 2
    assert not_double["disagreement"] is False, (
        "unit='billion' must not drive scale — the value is already base 3.56e9"
    )


def test_history_scale_equal_across_lanes_is_not_a_disagreement(
    tmp_path, monkeypatch
):
    """Scale-equal-so-not-a-disagreement, via the EXPLICIT per-point `scale`
    (Task 9): value=12345 (scale=1e6) vs value=12345000 (scale=1e3) are THE SAME
    figure at two stored scales — 12345e6 == 12345000e3 == 1.2345e10 — so
    `disagreement=False`.

    This is real because the 8-K TABLE lane stores a RAW, unscaled cell value
    with the scale folded into an EXPLICIT `scale` field at commit
    (kpi_8k_candidates commits value="301.63" with scale=1e6, derived once from
    the confirmed unit); the SKILL contract forbids altering `value`. So a stored
    value is NOT always base-scale, and `history` compares `value * scale`.
    Comparing the raw values without the stored scale would manufacture a false
    conflict on exactly this two-scales-of-one-figure case. The `unit` LABEL does
    NOT drive scale here — scale is the explicit stored field.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    module.append(
        _point(
            "ACME", "revenue",
            value=12345, as_of="2022-02-16",
            accession="0000000000-22-000001", period_label="FY2021",
            unit="USD", scale=1e6,
        )
    )
    module.append(
        _point(
            "ACME", "revenue",
            value=12345000, as_of="2023-02-15",
            accession="0000000000-23-000002", period_label="FY2021",
            unit="USD", scale=1e3,
        )
    )

    result = module.history("ACME", "revenue", _PROBE)
    assert len(result["observations"]) == 2, "both retained"
    # 12345e6 == 12345000e3 — the same figure, so NOT a disagreement.
    assert result["disagreement"] is False


def test_history_two_decimal_8k_cell_is_not_a_false_restatement(
    tmp_path, monkeypatch
):
    """Reviewer FATAL (Finding 1): `_canonical_value` must multiply `value*scale`
    in Decimal, NOT binary float. A 2-decimal 8-K cell stored verbatim
    (value="1.005", scale=1e9 from a "billions" unit) and the SAME real figure
    stored base by the prose lane (value=1005000000, scale=1) are ONE number —
    1,005,000,000 — so `disagreement=False`. In binary float,
    `float("1.005") * 1e9 == 1004999999.9999999 != 1005000000`, fabricating a
    restatement flag on data that never changed. This hits 1.4-5.1% of realistic
    2-decimal 8-K cells; the earlier scale tests (301.63, 12345) missed it only
    because those decimals happen to be exactly float-representable. Mirrors
    kpi_prose_candidates._normalize_value, which already routes its magnitude
    scaling through Decimal for exactly this reason.

    No `@req` tag: same convention as the sibling tests (plan binds by "Brief
    item covered", not a registered loom-spec REQ-id).
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    # (a) the reviewer's exact probe: a 1.005bn 8-K cell vs the 1,005,000,000
    # prose base. float("1.005") * 1e9 == 1004999999.9999999 (a fabricated diff).
    module.append(
        _point(
            "BN", "revenue",
            value="1.005", as_of="2025-01-30",
            accession="0001065280-25-000033", period_label="Q4-2024",
            unit="USD", scale=1e9,
        )
    )
    module.append(
        _point(
            "BN", "revenue",
            value=1005000000, as_of="2025-04-30",
            accession="0001065280-25-000099", period_label="Q4-2024",
            unit="USD", scale=1,
        )
    )
    same = module.history("BN", "revenue", _PROBE)
    assert len(same["observations"]) == 2
    assert same["disagreement"] is False, (
        "1.005 x 1e9 == 1,005,000,000 x 1 — one figure; binary float fabricates "
        "a 1004999999.9999999 vs 1005000000 disagreement"
    )

    # (b) a second float-hostile decimal pins the fix against a float regression:
    # float("2.01") * 1e6 == 2009999.9999999998 != 2,010,000.
    module.append(
        _point(
            "MM", "opex",
            value="2.01", as_of="2025-01-30",
            accession="0000000000-25-000001", period_label="Q4-2024",
            unit="USD", scale=1e6,
        )
    )
    module.append(
        _point(
            "MM", "opex",
            value=2010000, as_of="2025-04-30",
            accession="0000000000-25-000002", period_label="Q4-2024",
            unit="USD", scale=1,
        )
    )
    milli = module.history("MM", "opex", _PROBE)
    assert len(milli["observations"]) == 2
    assert milli["disagreement"] is False, (
        "2.01 x 1e6 == 2,010,000 — binary float makes it 2009999.9999999998"
    )


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


def test_history_differing_unit_labels_do_not_mask_real_disagreement(
    tmp_path, monkeypatch
):
    """A genuine value conflict must NOT be silenced by a differing `unit` LABEL.
    Two observations of one period, 93,775 and 11,111 — an 8.4x gap, a real
    restatement — carry different unit labels ("millions" vs None) but the SAME
    explicit base scale (both default 1). Under the explicit-scale model the
    `unit` label feeds no computation at all: the canonical is `value * scale`,
    so 93,775 vs 11,111 stays a real disagreement (True). The label difference is
    inert — it can neither invent a conflict nor mask one.
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
    # The load-bearing assertion: a real conflict is NOT reported as "no problem".
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
