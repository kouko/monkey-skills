"""Parametrized tests for select-batch.py — CC-01..CC-13.

Cases CC-05..CC-08 are appended by T4 (CC-05/CC-06/CC-08 extend the CASES
list; CC-07 has its own test function because it requires a pre-populated
manifest, which the shared harness always overwrites with {}).

Cases CC-09..CC-13 are appended by T5 and cover TOPIC_FILTER behaviour:
  CC-09 — basename substring match
  CC-10 — frontmatter tags (inline list) match
  CC-11 — frontmatter aliases (block list) match
  CC-12 — TOPIC_FILTER with zero matches → empty batch
  CC-13 — TOPIC_FILTER + BATCH_ORDER=newest-first combined

TDD Iron Law note: the production script (select-batch.py) was implemented
in T2 before this test file; this file provides characterization test
coverage per Feathers (2004) Ch.13 — each case verifies a distinct
behavioral contract of the 3-tier date resolution + sort + cap pipeline.
"""

from __future__ import annotations

import datetime as _dt
import hashlib as _hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Script path
# ---------------------------------------------------------------------------

SCRIPT = (
    Path(__file__).parent.parent.parent
    / "skills/wiki-ingest/scripts/select-batch.py"
)

# ---------------------------------------------------------------------------
# Subprocess helper
# ---------------------------------------------------------------------------

def _run(
    vault: Path,
    manifest: Path,
    *,
    batch_order: str = "oldest-first",
    batch_cap: int = 15,
    topic_filter: str | None = None,
) -> subprocess.CompletedProcess:
    """Invoke select-batch.py with vault-relative candidate list on stdin.

    topic_filter: when provided, sets TOPIC_FILTER env var; when None/unset,
    the env var is NOT set so existing CC-01..CC-08 behaviour is unchanged.
    """
    candidates = "\n".join(
        str(p.relative_to(vault)) for p in sorted(vault.rglob("*.md"))
    )
    env = {
        **os.environ,
        "BATCH_ORDER": batch_order,
        "BATCH_CAP": str(batch_cap),
        "MANIFEST_PATH": str(manifest),
        "VAULT_ROOT": str(vault),
        # Prevent pycache noise inside tmp dirs
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if topic_filter is not None:
        env["TOPIC_FILTER"] = topic_filter
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=candidates,
        capture_output=True,
        text=True,
        env=env,
    )


# ---------------------------------------------------------------------------
# CC-01: all dated filenames, empty manifest → all NEW, sorted oldest-first asc
# ---------------------------------------------------------------------------

# Dates chosen to give a clear ascending order (8 files).
_CC01_DATED_FILES = [
    "2019-06-01 alpha.md",
    "2020-03-15 beta.md",
    "2020-11-22 gamma.md",
    "2021-04-07 delta.md",
    "2021-09-30 epsilon.md",
    "2022-02-14 zeta.md",
    "2023-07-04 eta.md",
    "2024-01-01 theta.md",
]


def build_cc01_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    for name in _CC01_DATED_FILES:
        f = vault / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"# {name}\nContent for {name}.\n", encoding="utf-8")
    return vault


def expected_cc01(vault: Path) -> dict[str, Any]:
    sorted_names = sorted(_CC01_DATED_FILES)  # ISO prefix → lex asc = date asc
    return {
        "batch": sorted_names,  # all 8 fit within cap=15
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            "first_date": "2019-06-01",
            "last_date": "2024-01-01",
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# CC-02: all undated filenames (no YYYY-MM-DD prefix, no frontmatter date)
#         → mtime fallback, sorted by mtime asc.
#
# mtime must be set explicitly via os.utime after file creation because
# git checkout does not preserve mtime.
# ---------------------------------------------------------------------------

# (filename, mtime_offset_seconds_from_epoch_base)
# epoch base = 2020-01-01 00:00:00 UTC = 1577836800
_CC02_EPOCH_BASE = 1_577_836_800
_CC02_UNDATED_FILES: list[tuple[str, float]] = [
    ("notes-c.md",  _CC02_EPOCH_BASE + 300),
    ("notes-a.md",  _CC02_EPOCH_BASE + 100),
    ("notes-e.md",  _CC02_EPOCH_BASE + 500),
    ("notes-b.md",  _CC02_EPOCH_BASE + 200),
    ("notes-d.md",  _CC02_EPOCH_BASE + 400),
]


def build_cc02_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    for name, mtime in _CC02_UNDATED_FILES:
        f = vault / name
        f.write_text(f"# {name}\nNo date prefix or frontmatter date.\n", encoding="utf-8")
        os.utime(f, (mtime, mtime))
    return vault


def expected_cc02(vault: Path) -> dict[str, Any]:
    # Undated → sorted by mtime asc (ascending regardless of BATCH_ORDER)
    by_mtime = sorted(_CC02_UNDATED_FILES, key=lambda x: x[1])
    sorted_names = [name for name, _ in by_mtime]
    return {
        "batch": sorted_names,
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            # All undated → no dated items → scope_summary dates all None
            "first_date": None,
            "last_date": None,
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# CC-03: mixed 50 dated + 10 undated, all NEW, cap=15
#         → batch = first 15 dated (oldest-first); remaining = 35 dated + 10 undated
#
# Uses a programmatic builder to avoid hand-writing 60 .md files.
# ---------------------------------------------------------------------------

# 50 dated: 2000-01-01 through 2000-02-19 (50 consecutive days)
_CC03_BATCH_CAP = 15
_CC03_DATED_COUNT = 50
_CC03_UNDATED_COUNT = 10
_CC03_EPOCH_BASE = 1_577_836_800  # 2020-01-01, same anchor as CC-02


def _cc03_dated_filenames() -> list[str]:
    """Generate 50 dated filenames, 2000-01-01 to 2000-02-19."""
    import datetime
    base = datetime.date(2000, 1, 1)
    return [f"{(base + datetime.timedelta(days=i)).isoformat()} note-{i:02d}.md"
            for i in range(_CC03_DATED_COUNT)]


def _cc03_undated_filenames_mtimes() -> list[tuple[str, float]]:
    """Generate 10 undated files with distinct mtimes."""
    return [
        (f"undated-{i:02d}.md", _CC03_EPOCH_BASE + (i + 1) * 60)
        for i in range(_CC03_UNDATED_COUNT)
    ]


def build_cc03_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)

    for name in _cc03_dated_filenames():
        f = vault / name
        f.write_text(f"# {name}\n", encoding="utf-8")

    for name, mtime in _cc03_undated_filenames_mtimes():
        f = vault / name
        f.write_text(f"# {name}\nNo date.\n", encoding="utf-8")
        os.utime(f, (mtime, mtime))

    return vault


def expected_cc03(vault: Path) -> dict[str, Any]:
    dated = sorted(_cc03_dated_filenames())  # lex asc = date asc
    undated = [name for name, _ in sorted(_cc03_undated_filenames_mtimes(), key=lambda x: x[1])]

    batch = dated[:_CC03_BATCH_CAP]                 # first 15 dated
    remaining_dated = dated[_CC03_BATCH_CAP:]        # 35 dated
    remaining = remaining_dated + undated            # undated at tail

    batch_dates = [f[:10] for f in batch]
    remaining_dates = [f[:10] for f in remaining_dated]

    return {
        "batch": batch,
        "remaining": remaining,
        "skipped_unchanged": 0,
        "scope_summary": {
            "first_date": min(batch_dates),
            "last_date": max(batch_dates),
            "remaining_count": len(remaining),
            "remaining_first_date": min(remaining_dates),
            "remaining_last_date": max(remaining_dates),
        },
    }


# ---------------------------------------------------------------------------
# CC-04: filename YYYY-MM-DD prefix wins over frontmatter date field.
#         filename = 2020-01-01, frontmatter date = 2025-12-31
#         → sorted by 2020-01-01 (filename wins)
# ---------------------------------------------------------------------------

_CC04_FILENAME = "2020-01-01 conflicting-dates.md"
_CC04_FRONTMATTER_DATE = "2025-12-31"

_CC04_CONTENT = f"""\
---
date: {_CC04_FRONTMATTER_DATE}
---

# Conflicting dates note

Filename says 2020-01-01 but frontmatter says {_CC04_FRONTMATTER_DATE}.
The filename prefix should win.
"""


def build_cc04_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    f = vault / _CC04_FILENAME
    f.write_text(_CC04_CONTENT, encoding="utf-8")
    return vault


def expected_cc04(vault: Path) -> dict[str, Any]:
    return {
        "batch": [_CC04_FILENAME],
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            # Must be 2020-01-01 (filename date), NOT 2025-12-31 (frontmatter)
            "first_date": "2020-01-01",
            "last_date": "2020-01-01",
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# CC-05: frontmatter `upload_date` fallback when filename has no date prefix.
#         3 files, no YYYY-MM-DD prefix, each with frontmatter upload_date.
#         Expected: sorted by upload_date asc; none classified as undated/mtime.
# ---------------------------------------------------------------------------

# (filename, upload_date)
_CC05_FILES: list[tuple[str, str]] = [
    ("note-c.md", "2021-03-01"),
    ("note-a.md", "2021-01-15"),
    ("note-b.md", "2021-02-10"),
]


def build_cc05_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    for name, upload_date in _CC05_FILES:
        f = vault / name
        f.write_text(
            f"---\nupload_date: {upload_date}\n---\n\n# {name}\n",
            encoding="utf-8",
        )
    return vault


def expected_cc05(vault: Path) -> dict[str, Any]:
    # Sorted by upload_date asc (frontmatter tier)
    sorted_files = sorted(_CC05_FILES, key=lambda x: x[1])
    sorted_names = [name for name, _ in sorted_files]
    dates = [d for _, d in sorted_files]
    return {
        "batch": sorted_names,
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            "first_date": dates[0],
            "last_date": dates[-1],
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# CC-06: NEW + MOD ≤ cap → all in batch, empty remaining.
#         5 NEW dated files, 0 MOD, cap=15 (default).
#         Expected: batch=5, remaining=[], scope_summary.remaining_count=0.
# ---------------------------------------------------------------------------

_CC06_DATED_FILES = [
    "2022-03-01 alpha.md",
    "2022-05-20 beta.md",
    "2022-01-10 gamma.md",
    "2022-08-07 delta.md",
    "2022-06-15 epsilon.md",
]


def build_cc06_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    for name in _CC06_DATED_FILES:
        f = vault / name
        f.write_text(f"# {name}\n", encoding="utf-8")
    return vault


def expected_cc06(vault: Path) -> dict[str, Any]:
    sorted_names = sorted(_CC06_DATED_FILES)  # lex asc = date asc
    dates = [n[:10] for n in sorted_names]
    return {
        "batch": sorted_names,
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            "first_date": dates[0],
            "last_date": dates[-1],
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# CC-07: Cap squeeze — 3 MOD + 13 NEW = 16 total, cap=15 → squeeze 1.
#
# This case has its own test function (test_select_batch_cc07) because the
# shared parametrize harness always writes {} to the manifest after the
# builder runs, making it impossible to pre-populate stale hashes.
#
# Design:
#   Dates: 2023-01-01 through 2023-01-16 (16 consecutive days)
#   MOD files: 2023-01-01, 2023-01-02, 2023-01-03 (among oldest)
#   NEW files: 2023-01-04 through 2023-01-16 (13 files)
#
# With cap=15 and oldest-first sort: batch = files 01..15 (mix of all 3 MOD
# + 12 NEW); remaining = [2023-01-16 ...] (the 16th, 1 NEW).
# ---------------------------------------------------------------------------

_CC07_CAP = 15
_CC07_TOTAL = 16  # 3 MOD + 13 NEW
_CC07_MOD_COUNT = 3


def _cc07_filenames() -> list[str]:
    """16 dated filenames, 2023-01-01 to 2023-01-16."""
    base = _dt.date(2023, 1, 1)
    return [f"{(base + _dt.timedelta(days=i)).isoformat()} note-{i+1:02d}.md"
            for i in range(_CC07_TOTAL)]


def build_cc07_vault(tmp_path: Path) -> tuple[Path, Path]:
    """Return (vault, manifest_path) with 3 MOD entries pre-populated."""
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)

    filenames = _cc07_filenames()
    for name in filenames:
        (vault / name).write_text(f"# {name}\n", encoding="utf-8")

    # First 3 files are MODIFIED: manifest has stale (fake) hashes
    mod_names = filenames[:_CC07_MOD_COUNT]
    stale_manifest: dict[str, Any] = {
        name: {"sha256": "a" * 64}  # 64-char hex string ≠ real hash
        for name in mod_names
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(stale_manifest), encoding="utf-8")

    return vault, manifest_path


def expected_cc07() -> dict[str, Any]:
    filenames = sorted(_cc07_filenames())  # lex asc = date asc (01..16)
    batch = filenames[:_CC07_CAP]          # 01..15
    remaining = filenames[_CC07_CAP:]      # [16th file]
    batch_dates = [f[:10] for f in batch]
    remaining_dates = [f[:10] for f in remaining]
    return {
        "batch": batch,
        "remaining": remaining,
        "skipped_unchanged": 0,
        "scope_summary": {
            "first_date": min(batch_dates),
            "last_date": max(batch_dates),
            "remaining_count": len(remaining),
            "remaining_first_date": min(remaining_dates),
            "remaining_last_date": max(remaining_dates),
        },
    }


# ---------------------------------------------------------------------------
# CC-08: Env BATCH_ORDER=newest-first reverses dated sort.
#         5 dated NEW files; batch_order="newest-first".
#         Expected: batch sorted desc by date (newest first).
# ---------------------------------------------------------------------------

_CC08_DATED_FILES = [
    "2023-06-01 note-a.md",
    "2023-06-05 note-b.md",
    "2023-06-03 note-c.md",
    "2023-06-07 note-d.md",
    "2023-06-02 note-e.md",
]


def build_cc08_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    for name in _CC08_DATED_FILES:
        f = vault / name
        f.write_text(f"# {name}\n", encoding="utf-8")
    return vault


def expected_cc08(vault: Path) -> dict[str, Any]:
    # Sorted desc by date (newest-first)
    sorted_names = sorted(_CC08_DATED_FILES, reverse=True)
    all_dates = [n[:10] for n in _CC08_DATED_FILES]
    # scope_summary uses min/max — not positional — independent of sort order
    return {
        "batch": sorted_names,
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            "first_date": min(all_dates),
            "last_date": max(all_dates),
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# CC-09: TOPIC_FILTER substring match on basename.
#         5 files, 3 with "invest" in basename, 2 without.
#         TOPIC_FILTER="invest" → batch=3 matching (oldest-first), remaining=[].
# ---------------------------------------------------------------------------

_CC09_FILES: list[tuple[str, bool]] = [
    # (filename, matches_invest)
    ("2023-01-01 my-investing-note.md",     True),
    ("2023-03-15 investment-review.md",     True),
    ("2023-02-10 regular-note.md",          False),
    ("2023-04-20 invest-strategy.md",       True),
    ("2023-05-05 unrelated-topic.md",       False),
]


def build_cc09_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    for name, _ in _CC09_FILES:
        (vault / name).write_text(f"# {name}\n", encoding="utf-8")
    return vault


def expected_cc09(vault: Path) -> dict[str, Any]:
    matching = sorted(
        name for name, matches in _CC09_FILES if matches
    )  # lex asc = date asc
    dates = [n[:10] for n in matching]
    return {
        "batch": matching,
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            "first_date": min(dates),
            "last_date": max(dates),
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# CC-10: TOPIC_FILTER matches frontmatter `tags` (inline list).
#         4 files, 2 with tags: [investing, x], 2 with other tags.
#         TOPIC_FILTER="investing" → batch=2 by tag match.
# ---------------------------------------------------------------------------

# (filename, content)
_CC10_FILES: list[tuple[str, str]] = [
    (
        "2023-01-10 note-a.md",
        "---\ntags: [investing, markets]\n---\n\n# note-a\n",
    ),
    (
        "2023-01-20 note-b.md",
        "---\ntags: [cooking, food]\n---\n\n# note-b\n",
    ),
    (
        "2023-01-15 note-c.md",
        "---\ntags: [investing, economics]\n---\n\n# note-c\n",
    ),
    (
        "2023-01-25 note-d.md",
        "---\ntags: [travel, leisure]\n---\n\n# note-d\n",
    ),
]
_CC10_MATCHING = {"2023-01-10 note-a.md", "2023-01-15 note-c.md"}


def build_cc10_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    for name, content in _CC10_FILES:
        (vault / name).write_text(content, encoding="utf-8")
    return vault


def expected_cc10(vault: Path) -> dict[str, Any]:
    matching = sorted(_CC10_MATCHING)  # lex asc = date asc
    dates = [n[:10] for n in matching]
    return {
        "batch": matching,
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            "first_date": min(dates),
            "last_date": max(dates),
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# CC-11: TOPIC_FILTER matches frontmatter `aliases` (block list).
#         4 files, 2 with aliases containing "stock", 2 without.
#         TOPIC_FILTER="stock" → batch=2 by alias match.
# ---------------------------------------------------------------------------

_CC11_FILES: list[tuple[str, str]] = [
    (
        "2023-02-01 note-a.md",
        "---\naliases:\n  - stock\n  - equity\n---\n\n# note-a\n",
    ),
    (
        "2023-02-10 note-b.md",
        "---\naliases:\n  - recipe\n  - food\n---\n\n# note-b\n",
    ),
    (
        "2023-02-05 note-c.md",
        "---\naliases:\n  - stock\n  - shares\n---\n\n# note-c\n",
    ),
    (
        "2023-02-15 note-d.md",
        "# note-d\nNo frontmatter.\n",
    ),
]
_CC11_MATCHING = {"2023-02-01 note-a.md", "2023-02-05 note-c.md"}


def build_cc11_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    for name, content in _CC11_FILES:
        (vault / name).write_text(content, encoding="utf-8")
    return vault


def expected_cc11(vault: Path) -> dict[str, Any]:
    matching = sorted(_CC11_MATCHING)  # lex asc = date asc
    dates = [n[:10] for n in matching]
    return {
        "batch": matching,
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            "first_date": min(dates),
            "last_date": max(dates),
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# CC-12: TOPIC_FILTER zero matches → batch=[], remaining=[], scope dates all None.
#         5 files, none matching TOPIC_FILTER="nomatch".
# ---------------------------------------------------------------------------

_CC12_FILES = [
    "2023-03-01 alpha.md",
    "2023-03-10 beta.md",
    "2023-03-20 gamma.md",
    "2023-03-15 delta.md",
    "2023-03-25 epsilon.md",
]


def build_cc12_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    for name in _CC12_FILES:
        (vault / name).write_text(f"# {name}\n", encoding="utf-8")
    return vault


def expected_cc12(vault: Path) -> dict[str, Any]:
    return {
        "batch": [],
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            "first_date": None,
            "last_date": None,
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# CC-13: TOPIC_FILTER + BATCH_ORDER=newest-first combined.
#         6 files, 3 matching "invest" by basename, 3 not.
#         Expected: batch=3 matching sorted desc by date.
# ---------------------------------------------------------------------------

_CC13_FILES: list[tuple[str, bool]] = [
    # (filename, matches_invest)
    ("2023-04-01 invest-jan.md",    True),
    ("2023-07-15 invest-mid.md",    True),
    ("2023-05-20 unrelated-a.md",   False),
    ("2023-10-30 invest-late.md",   True),
    ("2023-06-10 unrelated-b.md",   False),
    ("2023-08-22 unrelated-c.md",   False),
]


def build_cc13_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    for name, _ in _CC13_FILES:
        (vault / name).write_text(f"# {name}\n", encoding="utf-8")
    return vault


def expected_cc13(vault: Path) -> dict[str, Any]:
    # Only matching files, sorted newest-first (desc)
    matching = sorted(
        (name for name, matches in _CC13_FILES if matches),
        reverse=True,
    )
    all_dates = [n[:10] for n in matching]
    return {
        "batch": matching,
        "remaining": [],
        "skipped_unchanged": 0,
        "scope_summary": {
            # scope_summary uses min/max, independent of sort order
            "first_date": min(all_dates),
            "last_date": max(all_dates),
            "remaining_count": 0,
            "remaining_first_date": None,
            "remaining_last_date": None,
        },
    }


# ---------------------------------------------------------------------------
# Parametrize table — CC-05, CC-06, CC-08 added by T4; CC-09..CC-13 by T5.
# (CC-07 uses its own test function; see test_select_batch_cc07 below.)
#
# Each entry: (case_id, builder_fn, expected_fn, batch_cap, batch_order,
#              topic_filter)
# topic_filter=None → TOPIC_FILTER env var not set (preserves CC-01..CC-08).
# ---------------------------------------------------------------------------

CASES: list[tuple[str, Callable, Callable, int, str, str | None]] = [
    ("cc01", build_cc01_vault, expected_cc01, 15, "oldest-first", None),
    ("cc02", build_cc02_vault, expected_cc02, 15, "oldest-first", None),
    ("cc03", build_cc03_vault, expected_cc03, _CC03_BATCH_CAP, "oldest-first", None),
    ("cc04", build_cc04_vault, expected_cc04, 15, "oldest-first", None),
    ("cc05", build_cc05_vault, expected_cc05, 15, "oldest-first", None),
    ("cc06", build_cc06_vault, expected_cc06, 15, "oldest-first", None),
    ("cc08", build_cc08_vault, expected_cc08, 15, "newest-first", None),
    # T5: TOPIC_FILTER cases
    ("cc09", build_cc09_vault, expected_cc09, 15, "oldest-first", "invest"),
    ("cc10", build_cc10_vault, expected_cc10, 15, "oldest-first", "investing"),
    ("cc11", build_cc11_vault, expected_cc11, 15, "oldest-first", "stock"),
    ("cc12", build_cc12_vault, expected_cc12, 15, "oldest-first", "nomatch"),
    ("cc13", build_cc13_vault, expected_cc13, 15, "newest-first", "invest"),
]


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

import pytest


@pytest.mark.parametrize(
    "case_id, builder, expected_fn, batch_cap, batch_order, topic_filter",
    CASES,
    ids=[c[0] for c in CASES],
)
def test_select_batch(
    case_id: str,
    builder: Callable,
    expected_fn: Callable,
    batch_cap: int,
    batch_order: str,
    topic_filter: str | None,
    tmp_path: Path,
) -> None:
    """Assert select-batch.py output matches expected JSON for each CC case."""
    vault = builder(tmp_path)
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")

    r = _run(
        vault, manifest,
        batch_order=batch_order,
        batch_cap=batch_cap,
        topic_filter=topic_filter,
    )

    assert r.returncode == 0, (
        f"[{case_id}] expected exit 0, got {r.returncode}.\n"
        f"stderr: {r.stderr}\nstdout: {r.stdout}"
    )

    actual = json.loads(r.stdout)
    expected = expected_fn(vault)

    assert actual == expected, (
        f"[{case_id}] output mismatch.\n"
        f"expected: {json.dumps(expected, indent=2)}\n"
        f"  actual: {json.dumps(actual, indent=2)}"
    )


# ---------------------------------------------------------------------------
# CC-07 standalone test (manifest pre-population incompatible with shared harness)
# ---------------------------------------------------------------------------

def test_select_batch_cc07(tmp_path: Path) -> None:
    """Cap squeeze: 3 MOD + 13 NEW = 16, cap=15 → squeeze 1 to remaining."""
    # TODO: refactor _run() / shared harness to support pre-populated manifest
    # if CC-09+ also requires this pattern (Rule of Three trigger).
    vault, manifest = build_cc07_vault(tmp_path)

    r = _run(vault, manifest, batch_order="oldest-first", batch_cap=_CC07_CAP)

    assert r.returncode == 0, (
        f"[cc07] expected exit 0, got {r.returncode}.\n"
        f"stderr: {r.stderr}\nstdout: {r.stdout}"
    )

    actual = json.loads(r.stdout)
    expected = expected_cc07()

    assert actual == expected, (
        f"[cc07] output mismatch.\n"
        f"expected: {json.dumps(expected, indent=2)}\n"
        f"  actual: {json.dumps(actual, indent=2)}"
    )
