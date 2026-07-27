"""test_cli_exit_codes.py — a failing CLI must not report success.

Every analysis-kpi CLI ends `sys.exit(main())`, and **`sys.exit(None)` exits
0**. So a `main()` whose error path stops returning its documented non-zero
code does not merely lose a diagnostic — it tells the shell the command
SUCCEEDED. A pipeline reading `$?`, a `&&` chain, or CI then proceeds on a
failure.

These paths already return the right codes, and each module's own docstring
states the contract ("Every fail-loud guard is a ValueError -> exit 1",
kpi_break.py:498-502; "invalid --binding JSON: ... return 2",
kpi_xbrl.py:1851-1854). What was missing is anything that HOLDS it: a sampled
mutation pass over the US lanes (2026-07-27, 180 mutants) found four failure
paths whose `return 1` / `return 2` could be replaced by `return None` with
all 1363 tests still green.

The discriminator for these tests is therefore the mutant, not a red bar —
they pass on first run because the behaviour is already correct. Asserting the
EXACT documented code rather than merely "non-zero" is deliberate: `1` and `2`
mean different things to a caller (a fail-loud guard vs malformed input), and
"non-zero" would let them drift into each other.

The store is redirected to tmp_path per case: these subcommands write to the
durable, append-only KPI store, and a test must never deposit history there.
"""
from __future__ import annotations

import importlib.util
import json
import sys

import pytest
from conftest import KPI_BREAK_SCRIPT, KPI_SERIES_SCRIPT, KPI_XBRL_SCRIPT


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def kpi_break_cli():
    return _load(KPI_BREAK_SCRIPT, "kpi_break_exitcode_test")


@pytest.fixture(scope="module")
def kpi_series_cli():
    return _load(KPI_SERIES_SCRIPT, "kpi_series_exitcode_test")


@pytest.fixture(scope="module")
def kpi_xbrl_cli():
    return _load(KPI_XBRL_SCRIPT, "kpi_xbrl_exitcode_test")


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path / "store"))


def _run(module, monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", argv)
    return module.main()


def test_break_dismiss_unknown_id_exits_1(kpi_break_cli, monkeypatch):
    """`dismiss` on a break-id that is not in the store raises ValueError.
    Documented as exit 1 (kpi_break.py:498-502)."""
    rc = _run(kpi_break_cli, monkeypatch, [
        "kpi_break.py", "dismiss", "--company", "NOSUCH",
        "--break-id", "brk-does-not-exist", "--by", "tester",
    ])
    assert rc == 1, f"a failed dismiss returned {rc!r}; sys.exit({rc!r}) exits 0"


def test_break_confirm_invalid_json_exits_2(kpi_break_cli, monkeypatch, tmp_path):
    """`confirm` with a malformed mapping file is a JSONDecodeError.
    Documented as exit 2 — distinct from the ValueError guards' 1."""
    bad = tmp_path / "bad-mapping.json"
    bad.write_text("{not valid json", encoding="utf-8")
    rc = _run(kpi_break_cli, monkeypatch, [
        "kpi_break.py", "confirm", "--company", "NOSUCH",
        "--break-id", "brk-1", "--by", "tester", "--file", str(bad),
    ])
    assert rc == 2, f"malformed input returned {rc!r}; sys.exit({rc!r}) exits 0"


def test_series_apply_unknown_break_exits_1(kpi_series_cli, monkeypatch):
    """`apply` on a break-id absent from the store raises ValueError -> 1."""
    rc = _run(kpi_series_cli, monkeypatch, [
        "kpi_series.py", "apply", "--company", "NOSUCH",
        "--break-id", "brk-does-not-exist", "--break-period", "2024-Q1",
    ])
    assert rc == 1, f"a failed apply returned {rc!r}; sys.exit({rc!r}) exits 0"


def test_xbrl_build_non_object_binding_exits_2(kpi_xbrl_cli, monkeypatch, tmp_path):
    """`build` given a --binding whose JSON is valid but not an object stops
    with "nothing computed" -> 2 (kpi_xbrl.py:1856-1862)."""
    binding = tmp_path / "binding.json"
    binding.write_text('["not", "an", "object"]', encoding="utf-8")
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps({"facts": []}), encoding="utf-8")
    rc = _run(kpi_xbrl_cli, monkeypatch, [
        "kpi_xbrl.py", "build", "--company", "NOSUCH",
        "--binding", str(binding), "--file", str(pack),
    ])
    assert rc == 2, f"a non-object binding returned {rc!r}; sys.exit({rc!r}) exits 0"


def test_sys_exit_none_really_is_zero():
    """The premise the four tests above rest on, pinned so it cannot be
    dismissed as folklore: returning None from main() is a SUCCESS exit."""
    with pytest.raises(SystemExit) as caught:
        sys.exit(None)
    assert caught.value.code is None
    # SystemExit(None) is what the interpreter turns into status 0.
    assert not caught.value.code
