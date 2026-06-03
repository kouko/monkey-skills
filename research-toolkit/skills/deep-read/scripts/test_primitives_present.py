"""Presence + sentinel checks for the copied deep-research primitives.

`schemas.py`, `rank.py`, `prompts.py`, and `dedup.py` in this directory are
byte-identical functional copies of the deep-research SSOT
(research-toolkit/skills/deep-research/scripts/). They are reproduced here so
deep-read can reuse them for per-chunk extraction (EXTRACT_SCHEMA + fetch_prompt)
and claim merge (filter_novel) without importing across skill boundaries.

The copies are placed and re-synced by
research-toolkit/scripts/sync-primitives.sh and guarded against drift by the
CI MD5 sync check. Do NOT edit the copies here — edit the SSOT and re-sync.

This test asserts the four modules import (flat, same-dir) and that the three
sentinel symbols deep-read depends on are present.
"""

import importlib


def test_schemas_imports_with_extract_schema():
    schemas = importlib.import_module("schemas")
    assert hasattr(schemas, "EXTRACT_SCHEMA"), "schemas.EXTRACT_SCHEMA missing"


def test_rank_imports():
    importlib.import_module("rank")


def test_prompts_imports_with_fetch_prompt():
    prompts = importlib.import_module("prompts")
    assert hasattr(prompts, "fetch_prompt"), "prompts.fetch_prompt missing"


def test_dedup_imports_with_filter_novel():
    dedup = importlib.import_module("dedup")
    assert hasattr(dedup, "filter_novel"), "dedup.filter_novel missing"
