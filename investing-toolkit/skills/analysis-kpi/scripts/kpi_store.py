#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Append-only bitemporal KPI store (operational-kpi capability, slice 1).

Layer 2 (Analysis) internal persistence — NOT external I/O. Persists a
validated operational-KPI series-point to a **file-per-series JSON** (one
file per company+kpi_id, holding a list of point records) under a durable
DATA dir, so a later restatement/re-extraction APPENDS a superseding record
instead of overwriting history, and a point-in-time query "as of" an earlier
date sees only what was known then (no look-ahead bias).

This slice ships the store scaffold + `append(point)` ONLY. Provenance/
as_of rejection, idempotent dedup, point-in-time/latest queries,
concurrency-safe locking, and the CLI land in later tasks (plan
docs/loom/plans/2026-07-14-operational-kpi-bitemporal-store.md, Tasks 2-8).

Persistence PATTERN mirrors data-markets/scripts/cache_util.py (key
sanitization `:170`, atomic tmp+rename write `:225`) but does NOT import it
and does NOT reuse its TTL envelope — a bitemporal series is durable,
immutable, append-only, so it roots under the DATA dir (~/.local/share),
not the evictable cache dir, and never expires. The small sanitize +
atomic-write duplication is a deliberate, flagged Rule-of-Three candidate
(extract a shared module only when a THIRD durable store appears).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

# Distinct from cache_util's CACHE_SCHEMA_VERSION / `_cache_meta` — a
# record-shape change here is a detectable migration, not a silent misread
# (brief Open Question 2: version the envelope).
STORE_SCHEMA_VERSION = "1.0"

# Mirrors cache_util._UNSAFE_KEY_CHARS: any char outside [A-Za-z0-9_-] is
# replaced with `_`, so a company/kpi_id can never escape the store dir via
# `../` or a path separator.
_UNSAFE_KEY_CHARS = re.compile(r"[^A-Za-z0-9_-]+")


def resolve_store_dir() -> Path:
    """Resolve the durable DATA dir for the KPI store.

    Precedence ladder (highest to lowest):
      1. KPI_STORE_DIR env var (stripped; empty after strip = unset) — test
         override + explicit operator control.
      2. $XDG_DATA_HOME/investing-toolkit/kpi-store (only if XDG_DATA_HOME
         set + non-empty).
      3. ~/.local/share/investing-toolkit/kpi-store (default).

    A DATA dir, NOT cache_util's cache dir: a bitemporal series is
    irreplaceable history that must survive cache eviction.
    """
    override = os.environ.get("KPI_STORE_DIR", "").strip()
    if override:
        return Path(override)

    xdg_data_home = os.environ.get("XDG_DATA_HOME", "").strip()
    if xdg_data_home:
        return Path(xdg_data_home) / "investing-toolkit" / "kpi-store"

    return Path.home() / ".local" / "share" / "investing-toolkit" / "kpi-store"


def _series_key(company: str, kpi_id: str) -> str:
    """Collision-proof `<company>__<kpi_id>__<digest>` filename stem — one
    file per series, for arbitrary input.

    Both components are sanitized independently for PATH SAFETY (every char
    outside `[A-Za-z0-9_-]` → `_`), so a malicious/malformed company or
    kpi_id can never escape the store dir via `../` or a separator. But
    sanitization alone is NOT collision-proof: `_` is in the allowed set, so
    input underscores survive and a shared separator cannot disambiguate —
    e.g. (company="AAPL_", kpi_id="X") and (company="AAPL", kpi_id="_X") both
    sanitize to `AAPL___X`. A 12-hex-char digest of the EXACT raw
    (company, kpi_id) pair, NUL-separated, is appended so distinct raw pairs
    always map to distinct files — preserving the file-per-series invariant
    the later dedup/query/lock slices rely on, while keeping the sanitized
    prefix human-readable.
    """
    company_key = _UNSAFE_KEY_CHARS.sub("_", str(company)) or "_"
    kpi_key = _UNSAFE_KEY_CHARS.sub("_", str(kpi_id)) or "_"
    digest = hashlib.sha1(
        f"{company}\x00{kpi_id}".encode("utf-8")
    ).hexdigest()[:12]
    return f"{company_key}__{kpi_key}__{digest}"


def _series_path(company: str, kpi_id: str) -> Path:
    return resolve_store_dir() / f"{_series_key(company, kpi_id)}.json"


def _load_series(path: Path) -> dict:
    """Read an existing series envelope, or return a fresh empty one.

    Append-only: an existing file's `points` list is preserved and never
    overwritten. A fresh series starts with a versioned `_kpi_store_meta`
    envelope and an empty `points` list.
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope.setdefault("points", [])
        return envelope
    return {
        "_kpi_store_meta": {"version": STORE_SCHEMA_VERSION},
        "points": [],
    }


def _atomic_write(path: Path, envelope: dict) -> None:
    """Write the series envelope atomically (tmp + rename), mirroring
    cache_util.save_cache's write pattern (:225).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=str(path.parent),
        prefix=f".{path.name}.", suffix=".tmp", delete=False,
    ) as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2)
        tmp = Path(f.name)
    tmp.rename(path)


def append(point: dict) -> None:
    """Append one series-point to its file-per-series JSON, verbatim.

    A point is a dict keyed by `(company, kpi_id, period, as_of)` carrying
    `value` + provenance (`source_accession`, `source_table_id`,
    `source_cell_ref`) and optional `lineage`/`restates` (persisted as-is,
    NOT interpreted this slice). This slice does no validation, dedup, or
    query — those guards land in Tasks 2-7. The point is stored unchanged so
    a later point-in-time query reads back exactly what was written.
    """
    path = _series_path(point["company"], point["kpi_id"])
    envelope = _load_series(path)
    envelope["points"].append(point)
    _atomic_write(path, envelope)
