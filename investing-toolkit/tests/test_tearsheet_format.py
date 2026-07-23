"""RED-first tests for tearsheet_format.py's core KPI x period Markdown
table (tearsheet plan, Task 3).

Fixtures transcribe the tearsheet plan's PINNED dump payload schema verbatim
(docs/loom/plans/2026-07-23-kpi-tearsheet.md ## Notes) -- never hand-shaped.
The renderer additionally consumes an "as_of" key merged into the payload by
the CLI's required --as-of flag; that key is NOT part of the store's dump
payload -- it is a rendering-only addition documented in
tearsheet_format.py's module docstring, so fixtures here add it alongside
the verbatim pin fields rather than folding it into the pin shape.

No @req tag: this dispatch's plan (docs/loom/plans/2026-07-23-kpi-
tearsheet.md) binds tasks by "Brief item covered", not registered loom-spec
REQ-ids, so there is no id in the living-spec namespace to bind to (same
convention as test_kpi_store_read_cli.py).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_ROOT = _TESTS_DIR.parent
_SCRIPTS_DIR = _ROOT / "skills" / "report-kpi-tearsheet" / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

from tearsheet_format import render_tearsheet  # noqa: E402

# Test-only: reuse the STORE's own axis-key primitives (`_snap_month_end`/
# `_qtrs`) to compute fixture `period_axis_key` values -- so fixtures built
# with `_period()` carry the SAME key a real `kpi_store.py dump` would emit
# for identical period identity, keeping the column-alignment fixtures
# correct now that the formatter unifies columns by `period_axis_key`
# instead of the raw (period_start, period_end) tuple. This is a TEST-ONLY
# import for fixture construction -- tearsheet_format.py itself never
# imports kpi_store (pure formatter, no cross-skill runtime dependency).
_KPI_STORE_SCRIPTS_DIR = _ROOT / "skills" / "analysis-kpi" / "scripts"
sys.path.insert(0, str(_KPI_STORE_SCRIPTS_DIR))
from kpi_store import _snap_month_end, _qtrs  # noqa: E402


def _axis_key(start, end, kind):
    snapped_end = _snap_month_end(end)
    quarters = _qtrs({"period_start": start, "period_end": end, "period_kind": kind})
    if snapped_end is None or quarters is None:
        return None
    return f"{snapped_end.isoformat()}|q{quarters}"


def _period(start, end, kind, labels, canonical_value, unit=None, axis_key="__auto__"):
    """One PINNED-schema period entry (## Notes): point fields verbatim on
    `latest`/`observations`, plus `canonical_value`. `period_axis_key`
    defaults to the real store computation (`_axis_key`) so pre-existing
    fixtures keep their intended column alignment; pass an explicit value
    to simulate a real store's cross-KPI drift-tolerant key directly."""
    latest = {
        "period": labels[0],
        "value": str(canonical_value),
        "canonical_value": canonical_value,
        "as_of": "2023-02-01",
        "source_accession": "0001065280-25-000033",
    }
    if unit is not None:
        latest["unit"] = unit
    resolved_axis_key = _axis_key(start, end, kind) if axis_key == "__auto__" else axis_key
    return {
        "period_start": start,
        "period_end": end,
        "period_kind": kind,
        "period_axis_key": resolved_axis_key,
        "period_labels": labels,
        "disagreement": False,
        "latest": latest,
        "observations": [latest],
    }


def test_table_periods_as_columns_newest_left():
    dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_a",
                "periods": [
                    _period("2021-01-01", "2021-12-31", "duration", ["FY2021"], 100),
                    _period("2022-01-01", "2022-12-31", "duration", ["FY2022"], 200),
                    _period("2023-01-01", "2023-12-31", "duration", ["FY2023"], 300),
                ],
            },
            {
                "kpi_id": "kpi_b",
                "periods": [
                    _period("2021-01-01", "2021-12-31", "duration", ["FY2021"], 10),
                    # kpi_b has no FY2022 period -- that cell must render N/A.
                    _period("2023-01-01", "2023-12-31", "duration", ["FY2023"], 30),
                ],
            },
        ],
        "warnings": [],
    }

    out = render_tearsheet(dump)
    lines = out.splitlines()

    header_line = next(line for line in lines if line.startswith("|") and "FY2023" in line)
    # newest-left: FY2023 column precedes FY2022, which precedes FY2021.
    assert header_line.index("FY2023") < header_line.index("FY2022") < header_line.index("FY2021")

    row_b = next(line for line in lines if line.startswith("| kpi_b"))
    cells = [c.strip() for c in row_b.strip("|").split("|")]
    # column order mirrors header order: [kpi_id, FY2023, FY2022, FY2021]
    assert cells[0] == "kpi_b"
    assert cells[1] == "30"
    assert cells[2] == "N/A"  # FY2022 missing for kpi_b
    assert cells[3] == "10"


def test_period_sort_key_uses_period_end_not_period_start():
    """Regression for the swapped-unpack bug: `_period_sort_key` must order
    newest-left by `period_end` (the docstring's stated contract), not by
    `period_start`. A transition-stub period (long span, later end) vs a
    quarter (short span, earlier end but LATER start) makes the two axes
    disagree -- every prior fixture had start/end increasing in lockstep,
    which masked the swapped unpack."""
    dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_c",
                "periods": [
                    # period_start (2023-04-01) is LATER than the stub's,
                    # but period_end (2023-06-30) is EARLIER than the stub's.
                    _period("2023-04-01", "2023-06-30", "quarter", ["Q2 2023"], 50),
                    # period_end (2024-06-30) is the most recent of the two --
                    # this column must render newest-left (leftmost).
                    _period("2022-01-01", "2024-06-30", "transition_stub", ["Transition"], 999),
                ],
            },
        ],
        "warnings": [],
    }

    out = render_tearsheet(dump)
    header_line = next(line for line in out.splitlines() if line.startswith("|") and "Transition" in line)
    assert header_line.index("Transition") < header_line.index("Q2 2023")


def test_cell_value_thousands_separator_and_unit_suffix():
    """Cell render contract (module docstring): thousands separators, no
    B/M compaction, `unit` appended when present. Prior fixtures never
    exceeded 300 (no separator needed) nor supplied `unit`."""
    dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_revenue",
                "periods": [
                    _period(
                        "2023-01-01",
                        "2023-12-31",
                        "duration",
                        ["FY2023"],
                        93775000000,
                        unit="USD",
                    ),
                ],
            },
        ],
        "warnings": [],
    }

    out = render_tearsheet(dump)
    row = next(line for line in out.splitlines() if line.startswith("| kpi_revenue"))
    cells = [c.strip() for c in row.strip("|").split("|")]
    assert cells[1] == "93,775,000,000 USD"


def test_disagreement_cell_marker_and_revisions_block():
    """Task 4: a `disagreement: true` period cell renders the latest
    canonical value suffixed `†`; a `## Revisions` block lists every
    observation for that flagged (kpi, period) as `<canonical_value> --
    recorded <as_of> -- <source_accession>` in as_of order. A fixture with
    no flagged periods must render no `## Revisions` heading at all.

    kpi_revenue carries TWO periods here (FY2021 flagged, FY2022 not) so a
    regression stamping `†` on the whole row -- or a `## Revisions` heading
    misattributed to the unflagged period -- fails: with only one period
    column, that class of bug renders identically to the correct output."""
    dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_revenue",
                "periods": [
                    {
                        "period_start": "2021-01-01",
                        "period_end": "2021-12-31",
                        "period_kind": "duration",
                        "period_labels": ["FY2021"],
                        "disagreement": True,
                        "latest": {
                            "period": "FY2021",
                            "value": "78,700",
                            "canonical_value": 78700000000,
                            "as_of": "2022-03-01",
                            "source_accession": "0000200406-22-000123",
                        },
                        "observations": [
                            {
                                "period": "FY2021",
                                "value": "93,775",
                                "canonical_value": 93775000000,
                                "as_of": "2021-11-01",
                                "source_accession": "0000200406-21-000456",
                            },
                            {
                                "period": "FY2021",
                                "value": "78,700",
                                "canonical_value": 78700000000,
                                "as_of": "2022-03-01",
                                "source_accession": "0000200406-22-000123",
                            },
                        ],
                    },
                    _period("2022-01-01", "2022-12-31", "duration", ["FY2022"], 88000000000),
                ],
            },
        ],
        "warnings": [],
    }

    out = render_tearsheet(dump)
    row = next(line for line in out.splitlines() if line.startswith("| kpi_revenue"))
    cells = [c.strip() for c in row.strip("|").split("|")]
    # newest-left: FY2022 (period_end 2022-12-31) precedes FY2021 (2021-12-31).
    assert cells[0] == "kpi_revenue"
    # FY2022 is NOT flagged -- must render with no trailing dagger. A
    # regression that stamps the whole row would show "88,000,000,000†".
    assert cells[1] == "88,000,000,000"
    # FY2021 is flagged: latest canonical value, marked -- not the older
    # observation's value.
    assert cells[2] == "78,700,000,000†"

    assert "## Revisions" in out
    revisions_block = out[out.index("## Revisions"):]
    # Heading names the flagged period only -- a wrong-period-association
    # bug (e.g. always using axis[0]) would emit "kpi_revenue — FY2022".
    assert "### kpi_revenue — FY2021" in revisions_block
    assert "### kpi_revenue — FY2022" not in revisions_block
    assert "93,775,000,000 — recorded 2021-11-01 — 0000200406-21-000456" in revisions_block
    assert "78,700,000,000 — recorded 2022-03-01 — 0000200406-22-000123" in revisions_block
    # as_of order: the earlier observation's line precedes the later one's.
    assert revisions_block.index("2021-11-01") < revisions_block.index("2022-03-01")

    # Negative case: no flagged periods anywhere -> no Revisions heading.
    no_disagreement_dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_a",
                "periods": [
                    _period("2021-01-01", "2021-12-31", "duration", ["FY2021"], 100),
                ],
            },
        ],
        "warnings": [],
    }
    out2 = render_tearsheet(no_disagreement_dump)
    assert "## Revisions" not in out2


def test_disagreement_marker_composes_after_unit_suffix():
    """Task 4 fix: pin value -> unit -> `†` as the cell composition order.
    No prior fixture set `unit` and `disagreement: true` together, so
    "93,775,000,000 USD†" was an accident of `_fmt_cell_value` appending
    unit before `render_tearsheet` appends `†` -- nothing pinned the order.
    A regression that flips the concatenation (marker before unit, e.g.
    `_fmt_cell_value` returning "93,775,000,000†" then appending " USD")
    would produce "93,775,000,000† USD" and fail this exact-string assert."""
    dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_revenue",
                "periods": [
                    {
                        "period_start": "2021-01-01",
                        "period_end": "2021-12-31",
                        "period_kind": "duration",
                        "period_labels": ["FY2021"],
                        "disagreement": True,
                        "latest": {
                            "period": "FY2021",
                            "value": "93,775",
                            "canonical_value": 93775000000,
                            "unit": "USD",
                            "as_of": "2021-11-01",
                            "source_accession": "0000200406-21-000456",
                        },
                        "observations": [
                            {
                                "period": "FY2021",
                                "value": "93,775",
                                "canonical_value": 93775000000,
                                "as_of": "2021-11-01",
                                "source_accession": "0000200406-21-000456",
                            },
                        ],
                    },
                ],
            },
        ],
        "warnings": [],
    }

    out = render_tearsheet(dump)
    row = next(line for line in out.splitlines() if line.startswith("| kpi_revenue"))
    cells = [c.strip() for c in row.strip("|").split("|")]
    assert cells[1] == "93,775,000,000 USD†"


def test_period_axis_key_unifies_drifted_period_across_kpis():
    """Whole-branch review Fix 1(a): cross-KPI column unification is keyed
    by the store's `period_axis_key`, not the raw (period_start,
    period_end) pair. Two KPIs report the SAME real period with a
    period_end drifted within the store's snap tolerance -- kpi_a ends
    2021-12-31, kpi_b ends 2021-12-15, distinct start dates too -- both
    snap to the same December 2021 month-end and both round to q4, so the
    store emits the SAME `period_axis_key` for both even though the raw
    tuples differ. Fails on the pre-fix raw-tuple axis, which keyed
    columns by the literal (period_start, period_end) pair and would split
    these into two columns instead of one.

    (The plan's illustrative dates for this drift, 2021-12-31 vs
    2022-01-02, do NOT actually snap-match under `_snap_month_end` --
    verified directly: they fall in different calendar months, so the
    store would emit two DIFFERENT axis keys. Substituted same-month dates
    that genuinely exercise the snap-tolerance merge this fix is about.)
    """
    dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_a",
                "periods": [
                    _period("2021-01-01", "2021-12-31", "duration", ["FY2021"], 100),
                ],
            },
            {
                "kpi_id": "kpi_b",
                "periods": [
                    _period(
                        "2021-01-05", "2021-12-15", "duration",
                        ["FY2021 (early close)"], 200,
                    ),
                ],
            },
        ],
        "warnings": [],
    }
    out = render_tearsheet(dump)
    header_line = next(line for line in out.splitlines() if line.startswith("| kpi_id"))
    header_cells = [c.strip() for c in header_line.strip("|").split("|")]
    assert len(header_cells) == 2  # kpi_id + ONE shared column, not two

    row_a = next(line for line in out.splitlines() if line.startswith("| kpi_a"))
    row_b = next(line for line in out.splitlines() if line.startswith("| kpi_b"))
    assert [c.strip() for c in row_a.strip("|").split("|")][1] == "100"
    assert [c.strip() for c in row_b.strip("|").split("|")][1] == "200"


def test_degenerate_null_axis_key_periods_never_merge_across_kpis():
    """Whole-branch review Fix 1(b): two KPIs each carry a DEGENERATE
    period (missing `period_start`, so the store's `period_axis_key` is
    null) that happens to share the same raw (period_start, period_end)
    pair -- (None, "2021-12-31") for both. A null key is NOT proof they
    are the same real period, so they must render as TWO SEPARATE columns
    with BOTH values visible -- never merge/overwrite into one shared
    column keyed by the raw tuple (the pre-fix behavior)."""
    dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_a",
                "periods": [
                    _period(None, "2021-12-31", "duration", ["Stub A"], 111),
                ],
            },
            {
                "kpi_id": "kpi_b",
                "periods": [
                    _period(None, "2021-12-31", "duration", ["Stub B"], 222),
                ],
            },
        ],
        "warnings": [],
    }
    out = render_tearsheet(dump)
    header_line = next(line for line in out.splitlines() if line.startswith("| kpi_id"))
    header_cells = [c.strip() for c in header_line.strip("|").split("|")]
    assert len(header_cells) == 3  # kpi_id + TWO distinct columns
    assert "Stub A" in header_cells and "Stub B" in header_cells

    row_a = next(line for line in out.splitlines() if line.startswith("| kpi_a"))
    row_b = next(line for line in out.splitlines() if line.startswith("| kpi_b"))
    cells_a = [c.strip() for c in row_a.strip("|").split("|")]
    cells_b = [c.strip() for c in row_b.strip("|").split("|")]
    assert "111" in cells_a and "222" not in cells_a
    assert "222" in cells_b and "111" not in cells_b


def test_null_period_label_renders_unlabeled_header_no_crash():
    """Whole-branch review Fix 2: a point appended without `period` flows
    to `period_labels: [None]` -- the renderer must not TypeError
    (`_shortest_label` -> None -> `len()`/`join()` crash); a column whose
    labels are ALL null renders header `(unlabeled)`."""
    dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_a",
                "periods": [
                    _period("2021-01-01", "2021-12-31", "duration", [None], 100),
                ],
            },
        ],
        "warnings": [],
    }
    out = render_tearsheet(dump)  # must not raise
    header_line = next(line for line in out.splitlines() if line.startswith("| kpi_id"))
    assert "(unlabeled)" in header_line


def test_empty_series_card_and_warnings_footer():
    """Task 5: empty `series` renders a graceful no-records card instead of
    an empty table; the footer ALWAYS renders a provenance line (`Rendered
    <as-of> from <n> series`) regardless of whether records exist, plus a
    `--store-dir` label when that optional value is present on the payload
    (and NO such label when it is absent); non-empty `warnings` renders a
    `## Warnings` block echoing each warning verbatim. Pure-function level
    only -- CLI-level empty-series + --store-dir + --out behavior are
    covered by their own subprocess tests below."""
    empty_dump = {
        "company": "EMPTYCO",
        "as_of": "2026-07-24",
        "series": [],
        "warnings": [],
    }
    out = render_tearsheet(empty_dump)
    assert "No KPI records for EMPTYCO." in out
    assert "|" not in out  # no table markup when series is empty
    assert "Rendered 2026-07-24 from 0 series" in out
    assert "## Warnings" not in out

    warn_dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_a",
                "periods": [
                    _period("2021-01-01", "2021-12-31", "duration", ["FY2021"], 100),
                ],
            },
        ],
        "warnings": ["skipped corrupt series file: kpi_b.jsonl"],
    }
    out2 = render_tearsheet(warn_dump)
    assert "Rendered 2026-07-24 from 1 series" in out2
    assert "## Warnings" in out2
    assert "- skipped corrupt series file: kpi_b.jsonl" in out2
    # Negative case: store_dir absent from the payload -> no "(store: ...)"
    # label at all, not just a blank one.
    assert "(store:" not in out2

    store_dir_dump = dict(warn_dump, store_dir="/tmp/kpi-store")
    out3 = render_tearsheet(store_dir_dump)
    assert "/tmp/kpi-store" in out3


def test_out_flag_writes_stdout_parity(tmp_path):
    """`--out <path>` writes byte-identical Markdown to stdout mode --
    subprocess-level CLI check, split out from the pure-function footer
    assertions above (Round-2 finding: mega-test mixed levels)."""
    warn_dump = {
        "company": "TESTCO",
        "as_of": "2026-07-24",
        "series": [
            {
                "kpi_id": "kpi_a",
                "periods": [
                    _period("2021-01-01", "2021-12-31", "duration", ["FY2021"], 100),
                ],
            },
        ],
        "warnings": ["skipped corrupt series file: kpi_b.jsonl"],
    }
    script = _SCRIPTS_DIR / "tearsheet_format.py"
    dump_path = tmp_path / "dump.json"
    dump_path.write_text(json.dumps(warn_dump), encoding="utf-8")
    out_path = tmp_path / "tearsheet.md"

    stdout_result = subprocess.run(
        [sys.executable, str(script), "--in", str(dump_path), "--as-of", "2026-07-24"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert stdout_result.returncode == 0, stdout_result.stderr.decode("utf-8", errors="replace")

    file_result = subprocess.run(
        [
            sys.executable, str(script),
            "--in", str(dump_path),
            "--as-of", "2026-07-24",
            "--out", str(out_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert file_result.returncode == 0, file_result.stderr.decode("utf-8", errors="replace")
    assert out_path.exists()
    assert out_path.read_text(encoding="utf-8") == stdout_result.stdout.decode("utf-8")


def test_out_flag_nonexistent_dir_reports_clean_error(tmp_path):
    """Round-2 finding 1: the --out write path had NO exception handling --
    a nonexistent output directory dumped a raw traceback. Must match the
    --in branch's convention: clean `error:` message on stderr, exit 1, no
    traceback."""
    script = _SCRIPTS_DIR / "tearsheet_format.py"
    dump = {"company": "TESTCO", "as_of": "2026-07-24", "series": [], "warnings": []}
    dump_path = tmp_path / "dump.json"
    dump_path.write_text(json.dumps(dump), encoding="utf-8")
    bad_out_path = tmp_path / "nonexistent-dir" / "out.md"

    result = subprocess.run(
        [
            sys.executable, str(script),
            "--in", str(dump_path),
            "--as-of", "2026-07-24",
            "--out", str(bad_out_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == 1
    assert "error:" in stderr
    assert "Traceback" not in stderr


def test_in_path_is_a_directory_reports_clean_error(tmp_path):
    """Whole-branch review Fix 4: the --in read path only caught
    FileNotFoundError + JSONDecodeError -- a directory passed to --in
    raises IsADirectoryError, an OSError subtype that escaped as a raw
    traceback. Must match the --out branch's convention: clean `error:`
    message on stderr, exit 1, no traceback."""
    script = _SCRIPTS_DIR / "tearsheet_format.py"

    result = subprocess.run(
        [sys.executable, str(script), "--in", str(tmp_path), "--as-of", "2026-07-24"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == 1
    assert "error:" in stderr
    assert "Traceback" not in stderr


def test_cli_empty_series_via_store_dir_flag_exit_zero(tmp_path):
    """Round-2 finding 2: the empty-series Acceptance clause ('exit 0') was
    asserted nowhere at CLI level -- only via the pure `render_tearsheet`
    call. Also exercises `--store-dir` through the ACTUAL CLI flag (it was
    only ever set by hand-constructing the dump dict in other tests)."""
    script = _SCRIPTS_DIR / "tearsheet_format.py"
    empty_dump = {"company": "EMPTYCO", "as_of": "2026-07-24", "series": [], "warnings": []}
    dump_path = tmp_path / "dump.json"
    dump_path.write_text(json.dumps(empty_dump), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable, str(script),
            "--in", str(dump_path),
            "--as-of", "2026-07-24",
            "--store-dir", "/tmp/kpi-store",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout = result.stdout.decode("utf-8")
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert "No KPI records for EMPTYCO." in stdout
    assert "(store: /tmp/kpi-store)" in stdout


def test_main_stdin_decodes_utf8_regardless_of_locale():
    """The --in file branch opens with encoding='utf-8' explicitly; the
    stdin branch read raw sys.stdin, which decodes per the process locale --
    under a non-UTF-8 locale (e.g. LC_ALL=C), non-ASCII company names would
    mis-decode or raise. `sys.stdin.reconfigure(encoding="utf-8")` fixes it."""
    script = _SCRIPTS_DIR / "tearsheet_format.py"
    dump = {
        "company": "テスト株式会社",
        "as_of": "2026-07-24",
        "series": [],
        "warnings": [],
    }
    payload = json.dumps(dump, ensure_ascii=False).encode("utf-8")

    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    env.pop("PYTHONIOENCODING", None)
    env.pop("PYTHONUTF8", None)

    result = subprocess.run(
        [sys.executable, str(script), "--as-of", "2026-07-24"],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert "テスト株式会社".encode("utf-8") in result.stdout
