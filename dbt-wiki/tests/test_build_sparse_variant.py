"""Task 2 acceptance test — sparse-comment fixture-variant builder.

`build_sparse_variant` materializes a copy of the l2-harness fixture where
every `models/**.sql` file has had its comments stripped (via
`strip_sql_comments`) while every other source file is copied byte-identical.
The resulting variant must still `dbt build` against DuckDB with the same
10-model shape (5 traps + 5 fillers) and the same queryability as the
original.
"""
from __future__ import annotations

import filecmp
import json
import subprocess
from pathlib import Path

import duckdb

from build_sparse_variant import build_sparse_variant
from strip_sql_comments import strip_sql_comments

SOURCE_DIR = Path(__file__).parent / "fixtures" / "l2-harness"

EXPECTED_MODELS = {
    "fct_amortization_trap",
    "fct_avg_ratio_trap",
    "fct_categorical_trap",
    "fct_fanout_trap",
    "fct_regional_twins_trap",
    "fct_filler_c",
    "fct_filler_d",
    "fct_filler_e",
    "stg_filler_a",
    "stg_filler_b",
}


def _sql_models(root: Path) -> list[Path]:
    return sorted((root / "models").rglob("*.sql"))


def _byte_identical_sources() -> list[Path]:
    """Source files the acceptance requires to be copied verbatim: schema
    YAMLs, seed CSVs, and the three project-root config files.
    """
    return (
        sorted((SOURCE_DIR / "models").rglob("*.yml"))
        + sorted((SOURCE_DIR / "seeds").glob("*.csv"))
        + [
            SOURCE_DIR / "dbt_project.yml",
            SOURCE_DIR / "profiles.yml",
            SOURCE_DIR / ".gitignore",
        ]
    )


def test_sparse_variant_builds_with_zero_sql_comments(tmp_path):
    dest = tmp_path / "sparse"
    build_sparse_variant(SOURCE_DIR, dest)

    # Precondition: the source really carries SQL comments, so a zero-comment
    # result proves a real strip rather than a vacuous pass.
    src_models = _sql_models(SOURCE_DIR)
    assert src_models, "source fixture has no SQL models"
    assert any(
        "--" in p.read_text() or "/*" in p.read_text() for p in src_models
    ), "source SQL models carry no comments — the strip would be a no-op"

    # 1. Every copied SQL model has zero comments left.
    dest_models = _sql_models(dest)
    assert len(dest_models) == len(src_models), (
        f"model count changed: {len(src_models)} source vs {len(dest_models)} copy"
    )
    for p in dest_models:
        text = p.read_text()
        assert "--" not in text and "/*" not in text, f"{p} still has comments"
        assert strip_sql_comments(text) == text, f"{p} is not fully stripped"

    # 2. Every non-model-SQL source file is byte-identical in the copy.
    for src in _byte_identical_sources():
        rel = src.relative_to(SOURCE_DIR)
        copied = dest / rel
        assert copied.is_file(), f"{rel} missing from copy"
        assert filecmp.cmp(src, copied, shallow=False), f"{rel} is not byte-identical"

    # 3. The stripped copy still builds against DuckDB.
    result = subprocess.run(
        [
            "dbt", "build",
            "--project-dir", str(dest),
            "--profiles-dir", str(dest),
        ],
        cwd=dest,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"dbt build failed against the sparse copy:\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )

    # 4. Same model count as the original (10 models).
    run_results = json.loads((dest / "target" / "run_results.json").read_text())
    built_models = {
        r["unique_id"]
        for r in run_results["results"]
        if r["unique_id"].startswith("model.")
    }
    assert len(built_models) == 10, f"expected 10 models, built {len(built_models)}"

    # 5. Same DuckDB queryability: all 10 model tables exist and a trap table
    #    returns a sane row.
    conn = duckdb.connect(str(dest / "target" / "l2_harness.duckdb"))
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "select table_name from information_schema.tables "
                "where table_schema = 'main'"
            ).fetchall()
        }
        assert EXPECTED_MODELS <= tables, (
            f"missing model tables: {EXPECTED_MODELS - tables}"
        )
        row = conn.execute(
            "select book_value from fct_amortization_trap"
        ).fetchone()
        assert row is not None, "fct_amortization_trap returned no rows"
        (book_value,) = row
        assert book_value is not None and float(book_value) > 0
    finally:
        conn.close()
