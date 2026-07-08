"""Task 7 acceptance test — filler models with mixed inline-comment density.

The L2 harness's trap models (Tasks 2-6) exercise dbt-wiki's ability to
CATCH analytics mistakes. This task rounds the fixture out with plain,
non-trap "filler" models whose only distinguishing feature is deliberately
varied inline-comment density — some densely commented column-by-column,
some with zero inline SQL comments — so the fixture also exercises
dbt-wiki's comments-as-source-of-truth assumption on ordinary models, not
just its trap-catching behavior.

This test asserts:
  1. all five filler models build (queried through the shared dbt_build
     fixture, so a successful build is proven end-to-end), and
  2. the comment-density spread is real — read straight from the .sql
     source files: at least one filler model has zero inline SQL comments
     and at least one is commented column-by-column, and
  3. the fixture as a whole (traps + filler) has grown to a plausible
     model count (>= 6). An exact ~10 is deliberately avoided because
     sibling trap tasks (2-6) may still be landing concurrently.
"""
from __future__ import annotations

from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "l2-harness"
MODELS_DIR = FIXTURE_DIR / "models"

FILLER_MODELS = {
    "stg_filler_a": MODELS_DIR / "staging" / "stg_filler_a.sql",
    "stg_filler_b": MODELS_DIR / "staging" / "stg_filler_b.sql",
    "fct_filler_c": MODELS_DIR / "marts" / "fct_filler_c.sql",
    "fct_filler_d": MODELS_DIR / "marts" / "fct_filler_d.sql",
    "fct_filler_e": MODELS_DIR / "marts" / "fct_filler_e.sql",
}


def _inline_after_code_comment_count(sql: str) -> int:
    """Number of lines carrying a trailing (column-level) `--` comment —
    real SQL code precedes the `--` on the same line. This is what
    distinguishes column-by-column commenting from a leading header block."""
    n = 0
    for line in sql.splitlines():
        idx = line.find("--")
        if idx > 0 and line[:idx].strip():
            n += 1
    return n


def _has_any_sql_comment(sql: str) -> bool:
    return any("--" in line for line in sql.splitlines())


def test_filler_models_build_with_varied_comment_density(dbt_build):
    # 1. All five filler models exist as source files and built successfully
    #    (querying through dbt_build proves the build reached each one).
    for name, path in FILLER_MODELS.items():
        assert path.exists(), f"filler model source missing: {path}"
        (row_count,) = dbt_build.execute(
            f"select count(*) from {name}"
        ).fetchone()
        assert row_count > 0, f"filler model {name} built but produced no rows"

    sources = {name: path.read_text() for name, path in FILLER_MODELS.items()}

    # 2. Comment-density spread is real and read from source.
    zero_comment_models = [
        name for name, sql in sources.items() if not _has_any_sql_comment(sql)
    ]
    assert zero_comment_models, (
        "expected at least one filler model with zero inline SQL comments, "
        "found none — the comment-density spread is not exercised"
    )

    column_by_column_models = [
        name
        for name, sql in sources.items()
        if _inline_after_code_comment_count(sql) >= 2
    ]
    assert column_by_column_models, (
        "expected at least one filler model commented column-by-column "
        "(>= 2 trailing inline comments), found none"
    )

    # 3. Fixture model count has grown (traps + filler). Lower-bound rather
    #    than exact ~10 because sibling trap tasks may still be landing.
    all_models = list(MODELS_DIR.glob("**/*.sql"))
    assert len(all_models) >= 6, (
        f"expected >= 6 total models (traps + 5 filler), found "
        f"{len(all_models)}: {sorted(p.name for p in all_models)}"
    )
