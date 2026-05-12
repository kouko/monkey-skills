"""Tests for legal-toolkit/scripts/verify-drift.py.

verify-drift checks that each ROUTE destination is byte-identical
to its canonical source. No auto-skip — every declared route is
mandatory.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def _load_verify_drift():
    """Importlib helper — script filename has a hyphen, so we can't `import
    verify-drift`. Load it as a module spec.
    """
    spec = importlib.util.spec_from_file_location(
        "verify_drift", SCRIPTS / "verify-drift.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------- T-V-1: pass case
def test_verify_drift_returns_zero_after_distribute(fake_plugin):
    import distribute

    verify_drift = _load_verify_drift()

    payload = b'{"k": "v"}'
    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(payload)

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }
    distribute.distribute(route=route, root=fake_plugin)

    rc = verify_drift.verify_drift(route=route, root=fake_plugin)
    assert rc == 0


# ---------------------------------------------------------- T-V-2: mutation
def test_verify_drift_returns_one_when_copy_mutated(fake_plugin, capsys):
    import distribute

    verify_drift = _load_verify_drift()

    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(b'{"original": true}')

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }
    distribute.distribute(route=route, root=fake_plugin)

    dst = fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json"
    dst.write_bytes(b'{"mutated": true}')  # tamper with the functional copy

    rc = verify_drift.verify_drift(route=route, root=fake_plugin)
    out = capsys.readouterr().out

    assert rc == 1
    assert "DRIFT" in out
    assert "legal-sources.json" in out


# ---------------------------------------------------------- T-V-3: missing copy
def test_verify_drift_returns_one_when_copy_missing(fake_plugin, capsys):
    verify_drift = _load_verify_drift()

    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(b"x")

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }
    # distribute() NOT called — destination is intentionally missing.

    rc = verify_drift.verify_drift(route=route, root=fake_plugin)
    out = capsys.readouterr().out

    assert rc == 1
    assert "MISSING" in out
    assert "legal-sources.json" in out
