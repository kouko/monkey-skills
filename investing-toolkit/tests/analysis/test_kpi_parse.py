"""Tests for analysis-kpi/scripts/kpi_parse.py — deterministic cell parser
(operational-kpi capability, slice 9, Task 1: numeric parse forms).

kpi_parse.py is PURE-COMPUTE (stdlib only) — it does NOT import `_store_fs`,
resolve a store dir, lock, or persist anything, and does NOT touch the
network or an LLM. No `KPI_STORE_DIR` fixture is needed.

The library function is exercised by loading `kpi_parse.py` via importlib
(same convention as test_kpi_validate.py's `kpi_validate_module` fixture).
The Task 3 CLI (`parse` subcommand) is exercised via subprocess, mirroring
test_kpi_validate.py::test_cli_validate_roundtrip.

No `@req` tags: this dispatch's plan/spec trace work by named change-folder
Requirements (operational-kpi / "Locate-then-parse parser-emits-number
invariant"), NOT by registered loom-spec REQ-ids — so `@req` is omitted per
the implementer contract.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys

from conftest import KPI_PARSE_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_parse_module():
    """Load kpi_parse.py as an importable module for unit tests of its
    library surface (parse_cell). No CLI yet — that lands in Task 3.
    """
    spec = importlib.util.spec_from_file_location("kpi_parse_test", KPI_PARSE_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_parse_test"] = module
    spec.loader.exec_module(module)
    return module


def test_parse_cell_numeric_forms(kpi_parse_module):
    """Task 1: parse_cell handles the numeric happy path — leading currency
    `$`, thousands `,`, decimal point, leading sign, the accounting
    parenthesized-negative convention, and a true `0` → 0.0 (not missing).
    """
    assert kpi_parse_module.parse_cell("$1,234") == pytest.approx(1234.0)
    assert kpi_parse_module.parse_cell("1,234.56") == pytest.approx(1234.56)
    assert kpi_parse_module.parse_cell("1234") == pytest.approx(1234.0)
    assert kpi_parse_module.parse_cell("0") == pytest.approx(0.0)
    assert kpi_parse_module.parse_cell("(123)") == pytest.approx(-123.0)
    assert kpi_parse_module.parse_cell("-45") == pytest.approx(-45.0)


def test_parse_cell_fails_loud_on_unparseable_tokens(kpi_parse_module):
    """Task 2: parse_cell RAISES (never returns 0) for not-a-number tokens —
    NM, n/a, dash-as-NA, and blank/whitespace-only. A missing cell must
    become the caller's review-item, never a fabricated zero. A true `"0"`
    still parses to 0.0 (a real value, not missing), and `-45` still parses
    as a negative number (not a dash-token) — the dash-vs-negative-sign
    distinction is the crux of this taxonomy.
    """
    unparseable_tokens = [
        "NM",
        "nm",
        "n/a",
        "N/A",
        "na",
        "—",  # em dash
        "–",  # en dash
        "‒",  # figure dash
        "-",  # bare hyphen alone = not-applicable, NOT a negative number
        "",
        "   ",
        "foo",
    ]
    for token in unparseable_tokens:
        with pytest.raises(kpi_parse_module.UnparseableCell):
            kpi_parse_module.parse_cell(token)

    # true zero is a real value, NOT missing
    assert kpi_parse_module.parse_cell("0") == pytest.approx(0.0)
    # a negative number is NOT a dash-token
    assert kpi_parse_module.parse_cell("-45") == pytest.approx(-45.0)


def test_cli_parse_roundtrip():
    """Task 3: the `parse` subcommand reads the cell text from stdin (or
    --cell), prints the parsed number, and exits 0 on success. An
    UnparseableCell (a genuinely-unparseable cell) is a normal fail-loud
    outcome — clean stderr, no raw traceback, exit 1. A malformed
    invocation (no subcommand) is an argparse-level error, exit 2.
    `--help` must list the `parse` subcommand.
    """

    def run_parse(stdin_text):
        return subprocess.run(
            ["uv", "run", "--script", str(KPI_PARSE_SCRIPT), "parse"],
            input=stdin_text, capture_output=True, text=True, timeout=60,
        )

    # (1) a numeric cell via stdin → stdout the parsed number, exit 0
    numeric = run_parse("$1,234")
    assert numeric.returncode == 0, numeric.stderr
    assert numeric.stdout.strip() == "1234.0"

    # (2) an unparseable cell via stdin → exit 1, non-empty clean stderr,
    # no raw traceback
    unparseable = run_parse("NM")
    assert unparseable.returncode == 1, unparseable.stdout
    assert unparseable.stderr.strip() != ""
    assert "Traceback" not in unparseable.stderr

    # (3) --cell flag also works (no stdin needed)
    via_flag = subprocess.run(
        ["uv", "run", "--script", str(KPI_PARSE_SCRIPT), "parse", "--cell", "(123)"],
        capture_output=True, text=True, timeout=60,
    )
    assert via_flag.returncode == 0, via_flag.stderr
    assert via_flag.stdout.strip() == "-123.0"

    # (4) malformed invocation (no subcommand) → argparse exit 2
    no_subcommand = subprocess.run(
        ["uv", "run", "--script", str(KPI_PARSE_SCRIPT)],
        capture_output=True, text=True, timeout=60,
    )
    assert no_subcommand.returncode == 2, no_subcommand.stdout

    # (5) --help lists the parse subcommand
    help_result = subprocess.run(
        ["uv", "run", "--script", str(KPI_PARSE_SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert help_result.returncode == 0, help_result.stderr
    assert "parse" in help_result.stdout
