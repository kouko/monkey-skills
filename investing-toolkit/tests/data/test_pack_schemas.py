"""test_pack_schemas.py — validate pack sample fixtures against per-pack JSON Schemas.

Each `data-{country}/references/schema-{pack}.json` defines the contract;
each `tests/data/fixtures/data-{country}-{pack}-sample.json` is the example output;
this test ensures example matches schema (drift guard).

Plus an opt-in @pytest.mark.network variant that fetches LIVE pack output and
validates against schema (catches contract drift between schema and pack.py).

Dependencies:
    pytest, jsonschema (install via `uv run --with pytest --with jsonschema pytest ...`).

Sequence note:
    The 5 country schemas + 25 sample fixtures are produced by sibling agents
    S1-S5 in parallel. This test gracefully skips per (country, pack) cell when
    its schema or fixture is not yet committed, so it can run before S1-S5 land.
    Once schemas/fixtures are committed, the skip→pass transition is automatic.

Run:
    uv run --with pytest --with jsonschema pytest tests/data/test_pack_schemas.py -v
    uv run --with pytest --with jsonschema pytest tests/data/test_pack_schemas.py -v -m network  # live
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"
FIXTURES = ROOT / "tests" / "data" / "fixtures"

COUNTRIES = ["us", "jp", "tw", "kr", "cn"]
PACKS = ["snapshot", "memo-fetch", "comps-multiples", "screener-batch", "regime-pack"]

# 5 countries × 5 packs = 25 static-fixture cases (no network).
PARAMS = [(c, p) for c in COUNTRIES for p in PACKS]


def _build_validator(schema_path: Path):
    """Build a jsonschema validator with a registry of sibling schemas.

    Schemas in `data-{country}/references/` may use relative `$ref` like
    `schema-error-envelope.json` to share definitions. We pre-load every
    `*.json` file in the schema's directory into a `referencing.Registry`
    so those refs resolve without network lookups.

    We register each sibling under three keys to handle both draft-07 (no
    `$id`, refs by bare filename) and draft-2020-12 (refs are resolved
    against the parent schema's `$id` as a base URI):

      1. bare filename (e.g. `schema-error-envelope.json`)
      2. `$id` of the sibling (if present)
      3. `<base-of-current-$id>/<filename>` so a draft-2020-12 ref like
         `schema-error-envelope.json` from a schema whose `$id` is
         `https://monkey-skills/.../snapshot.json` resolves to
         `https://monkey-skills/.../schema-error-envelope.json`.
    """
    import jsonschema
    from referencing import Registry, Resource

    schema = json.loads(schema_path.read_text())
    refs_dir = schema_path.parent

    # Determine base URI from current schema's $id (if any) — used to
    # build the third registration key for relative refs.
    base_uri = ""
    if isinstance(schema, dict) and isinstance(schema.get("$id"), str):
        sid = schema["$id"]
        if "/" in sid:
            base_uri = sid.rsplit("/", 1)[0] + "/"

    resources = []
    for sibling in sorted(refs_dir.glob("*.json")):
        try:
            content = json.loads(sibling.read_text())
        except json.JSONDecodeError:
            continue
        res = Resource.from_contents(content)
        # 1. bare filename
        resources.append((sibling.name, res))
        # 2. $id
        if isinstance(content, dict) and isinstance(content.get("$id"), str):
            resources.append((content["$id"], res))
        # 3. base_uri + filename (for draft-2020-12 relative-ref resolution)
        if base_uri:
            resources.append((base_uri + sibling.name, res))

    registry = Registry().with_resources(resources)
    # Pick the right validator class for the schema's $schema declaration.
    validator_cls = jsonschema.validators.validator_for(schema)
    return validator_cls(schema, registry=registry)


@pytest.mark.parametrize(
    "country,pack",
    PARAMS,
    ids=[f"{c}-{p}" for c, p in PARAMS],
)
def test_pack_sample_validates_against_schema(country, pack):
    """Pre-committed sample fixture must validate against pack's JSON Schema.

    Skipped if schema or sample is not yet committed (pre-S1-S5 state).
    """
    schema_path = SKILLS / f"data-{country}" / "references" / f"schema-{pack}.json"
    sample_path = FIXTURES / f"data-{country}-{pack}-sample.json"

    if not schema_path.exists():
        pytest.skip(f"schema not yet committed: {schema_path.relative_to(ROOT)}")
    if not sample_path.exists():
        pytest.skip(f"sample not yet committed: {sample_path.relative_to(ROOT)}")

    try:
        import jsonschema  # noqa: F401
    except ImportError:
        pytest.skip("jsonschema not installed; run with `uv run --with jsonschema pytest ...`")

    sample = json.loads(sample_path.read_text())
    validator = _build_validator(schema_path)
    validator.validate(sample)


# ---------------------------------------------------------------------------
# Live pack output validation — opt-in via `-m network`
# ---------------------------------------------------------------------------

LIVE_CASES = [
    # (country, pack, ticker)  — ticker ignored for regime-pack
    ("us", "snapshot", "AAPL"),
    ("us", "comps-multiples", "AAPL"),
    ("us", "regime-pack", None),
    ("jp", "snapshot", "7203"),
    ("tw", "snapshot", "2330.TW"),
    ("kr", "snapshot", "005930.KS"),
    ("cn", "snapshot", "600519.SS"),
]


@pytest.mark.network
@pytest.mark.parametrize(
    "country,pack,ticker",
    LIVE_CASES,
    ids=[f"{c}-{p}" for c, p, _ in LIVE_CASES],
)
def test_pack_live_output_matches_schema(country, pack, ticker):
    """Live pack run must validate against committed schema (catches drift).

    Skipped if the country's schema is not yet committed.
    """
    schema_path = SKILLS / f"data-{country}" / "references" / f"schema-{pack}.json"
    if not schema_path.exists():
        pytest.skip(f"schema not yet committed: {schema_path.relative_to(ROOT)}")

    try:
        import jsonschema  # noqa: F401
    except ImportError:
        pytest.skip("jsonschema not installed; run with `uv run --with jsonschema pytest ...`")

    pack_script = SKILLS / f"data-{country}" / "scripts" / "pack.py"
    if not pack_script.exists():
        pytest.skip(f"pack.py not found: {pack_script.relative_to(ROOT)}")

    args = [str(pack_script), "--pack", pack]
    if pack != "regime-pack" and ticker is not None:
        args.extend(["--ticker", ticker])

    proc = subprocess.run(
        ["uv", "run", *args],
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert proc.returncode == 0, (
        f"pack.py failed (exit {proc.returncode}): {proc.stderr[-500:]}"
    )

    output = json.loads(proc.stdout)
    validator = _build_validator(schema_path)
    validator.validate(output)
