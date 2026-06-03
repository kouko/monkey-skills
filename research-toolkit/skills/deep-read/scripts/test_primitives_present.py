"""Presence + sentinel checks for the copied deep-research primitives.

`schemas.py` and `prompts.py` in this directory are byte-identical functional
copies of the deep-research SSOT (research-toolkit/skills/deep-research/scripts/).
deep-read invokes them via CLI for per-chunk extraction — `schemas.py extract`
(EXTRACT_SCHEMA) and `prompts.py fetch` (fetch_prompt). deep-read does NOT carry
`rank.py` / `dedup.py`: it has no quorum step and `deepread.merge_chunks` rolls
its own claim-text dedup, so copying them would be dead code.

The copies are placed and re-synced by
research-toolkit/scripts/sync-primitives.sh and guarded against drift by the
CI MD5 sync check. Do NOT edit the copies here — edit the SSOT and re-sync.
"""

import importlib


def test_schemas_imports_with_extract_schema():
    schemas = importlib.import_module("schemas")
    assert hasattr(schemas, "EXTRACT_SCHEMA"), "schemas.EXTRACT_SCHEMA missing"


def test_prompts_imports_with_fetch_prompt():
    prompts = importlib.import_module("prompts")
    assert hasattr(prompts, "fetch_prompt"), "prompts.fetch_prompt missing"
