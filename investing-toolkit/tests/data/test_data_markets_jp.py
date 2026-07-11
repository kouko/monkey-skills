"""test_data_markets_jp.py — migration contract for the JP data-markets clients.

Covers plan Task 3b (docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md):
migrating skills/data-jp/scripts/{boj,ecb,edinet,estat,tdnet}_client.py + pack.py
into skills/data-markets/scripts/ as {boj,ecb,edinet,estat,tdnet}_client.py +
pack_jp.py, replacing local cache boilerplate (incl. edinet/tdnet's
import-time `CACHE_DIR.mkdir(...)`) with lazy `cache_util` usage.

Offline / fixture-fed — no network calls. Mirrors the existing
tests/data/test_pack_schemas.py fixture convention
(tests/data/fixtures/data-jp-{pack}-sample.json).
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "skills" / "data-markets" / "scripts"
OLD_PACK_PY = ROOT / "skills" / "data-jp" / "scripts" / "pack.py"
FIXTURES_DIR = ROOT / "tests" / "data" / "fixtures"

MIGRATED_CLIENTS = [
    "boj_client",
    "ecb_client",
    "edinet_client",
    "estat_client",
    "tdnet_client",
]

# Local function/constant DEFINITIONS that must NOT survive migration — the
# per-client local cache boilerplate cache_util.py (T2) now owns, including
# the underscore dialect edinet/tdnet used (`_cache_path` / `_load_cache` /
# `_save_cache`). Matched as definitions (`def foo(` / `foo =` at column 0),
# not as `cache_util.foo(...)` call sites, which are the expected replacement.
BANNED_DEFS = [
    "get_cache_path",
    "load_cache",
    "save_cache",
    "_cache_path",
    "_load_cache",
    "_save_cache",
    "_CACHE_BASE",
    "CACHE_DIR",
]

PACKS = ["snapshot", "memo-fetch", "comps-multiples", "screener-batch", "regime-pack"]


def test_jp_migration_contract(tmp_path, monkeypatch):
    # ------------------------------------------------------------------
    # (a) no local cache helpers (incl. underscore dialect) in the
    #     migrated client files; each imports the shared cache_util
    #     module instead.
    # ------------------------------------------------------------------
    for name in MIGRATED_CLIENTS:
        path = SCRIPTS_DIR / f"{name}.py"
        assert path.exists(), f"migrated client missing: {path}"
        text = path.read_text(encoding="utf-8")
        for symbol in BANNED_DEFS:
            escaped = re.escape(symbol)
            def_pattern = rf"^def {escaped}\("
            assign_pattern = rf"^{escaped}\s*="
            assert not re.search(def_pattern, text, re.MULTILINE), (
                f"{name}.py still defines banned local-cache function {symbol!r}"
            )
            assert not re.search(assign_pattern, text, re.MULTILINE), (
                f"{name}.py still assigns banned local-cache constant {symbol!r}"
            )
        assert re.search(r"^import cache_util\s*$", text, re.MULTILINE), (
            f"{name}.py does not import the shared cache_util module"
        )

    pack_jp_path = SCRIPTS_DIR / "pack_jp.py"
    assert pack_jp_path.exists(), f"pack_jp.py missing: {pack_jp_path}"

    cache_util_path = SCRIPTS_DIR / "cache_util.py"
    assert cache_util_path.exists(), "cache_util.py (T2) must already exist"

    # ------------------------------------------------------------------
    # (b) no import-time filesystem side effects — importing each client
    #     module must not create the cache directory. Reproduces the
    #     edinet_client.py:63 / tdnet_client.py:53 `CACHE_DIR.mkdir(...)`
    #     regression by pointing INVESTING_TOOLKIT_CACHE at a fresh,
    #     nonexistent-but-creatable tmp path and asserting it stays absent
    #     across a plain `import`.
    # ------------------------------------------------------------------
    cache_root = tmp_path / "import-time-cache-probe"
    assert not cache_root.exists()

    import_code = (
        f"import sys; sys.path.insert(0, {str(SCRIPTS_DIR)!r}); "
        f"import {', '.join(MIGRATED_CLIENTS)}"
    )
    env = {**os.environ, "INVESTING_TOOLKIT_CACHE": str(cache_root)}
    proc = subprocess.run(
        ["uv", "run", "--quiet", "--with", "requests==2.33.1", "python", "-c", import_code],
        capture_output=True,
        text=True,
        env=env,
        timeout=180,
    )
    assert proc.returncode == 0, (
        f"importing migrated clients failed:\nstdout={proc.stdout}\nstderr={proc.stderr}"
    )
    assert not cache_root.exists(), (
        f"cache dir {cache_root} was created merely by importing a migrated client "
        "module — an import-time filesystem side effect survived migration"
    )

    # ------------------------------------------------------------------
    # (c) pack_jp.build_pack section keys match the current data-jp
    #     pack.py output shape (fixture-fed, offline — subprocess client
    #     calls are mocked via _run_client).
    # ------------------------------------------------------------------
    monkeypatch.delenv("EDINET_API_KEY", raising=False)
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        import pack_jp  # noqa: E402  (path-dependent import, must follow sys.path insert)

        importlib.reload(pack_jp)
        monkeypatch.setattr(pack_jp, "_run_client", lambda script, args: {})

        for pack_name in PACKS:
            fixture_path = FIXTURES_DIR / f"data-jp-{pack_name}-sample.json"
            assert fixture_path.exists(), f"fixture missing: {fixture_path}"
            expected_keys = set(json.loads(fixture_path.read_text()).keys())

            if pack_name in ("comps-multiples", "screener-batch"):
                tickers = ["7203", "6758"]
            elif pack_name == "regime-pack":
                tickers = []
            else:
                tickers = ["7203"]

            result = pack_jp.build_pack(pack_name, tickers)
            assert set(result.keys()) == expected_keys, (
                f"pack_jp.build_pack({pack_name!r}, ...) top-level keys "
                f"{sorted(result.keys())} != data-jp fixture keys "
                f"{sorted(expected_keys)}"
            )
    finally:
        sys.path.remove(str(SCRIPTS_DIR))

    # ------------------------------------------------------------------
    # (d) SUPPORTED_PACKS matches data-jp pack.py's PACKS set.
    # ------------------------------------------------------------------
    assert OLD_PACK_PY.exists(), f"reference old pack.py missing: {OLD_PACK_PY}"
    spec = importlib.util.spec_from_file_location("_old_data_jp_pack", OLD_PACK_PY)
    old_pack = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old_pack)

    assert set(pack_jp.SUPPORTED_PACKS) == set(old_pack.PACKS), (
        f"pack_jp.SUPPORTED_PACKS {sorted(pack_jp.SUPPORTED_PACKS)} != "
        f"data-jp pack.py PACKS {sorted(old_pack.PACKS)}"
    )
    assert isinstance(pack_jp.SUPPORTED_PACKS, tuple), (
        "SUPPORTED_PACKS must be a tuple per the shared cross-market interface"
    )
