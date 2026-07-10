"""Sparse-comment fixture-variant builder (G1 Task 2).

Materializes a copy of the l2-harness fixture project at `dest_dir`: every
`.sql` file under `models/` has its comments stripped via `strip_sql_comments`
(Task 1), and every other source file is copied byte-identical. Build outputs
(`target/`, `logs/`, `dbt_packages/`, `*.duckdb`/`*.wal`) are skipped so the
variant rebuilds clean, matching the fixture's own `.gitignore`. `.user.yml`
(dbt's local anonymous-usage-stats state file, also gitignored) is likewise
skipped so the variant doesn't carry environment-dependent local state.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from strip_sql_comments import strip_sql_comments

_EXCLUDED_DIRS = {"target", "logs", "dbt_packages"}
_EXCLUDED_SUFFIXES = {".duckdb", ".wal"}
_EXCLUDED_NAMES = {".user.yml"}


def build_sparse_variant(source_dir: Path, dest_dir: Path) -> None:
    source_dir = Path(source_dir)
    dest_dir = Path(dest_dir)

    for src in source_dir.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(source_dir)
        if _EXCLUDED_DIRS & set(rel.parts):
            continue
        if src.suffix in _EXCLUDED_SUFFIXES:
            continue
        if rel.name in _EXCLUDED_NAMES:
            continue

        dest = dest_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel.parts[0] == "models" and src.suffix == ".sql":
            dest.write_text(strip_sql_comments(src.read_text()))
        else:
            shutil.copyfile(src, dest)
