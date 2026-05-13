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

REPO = SCRIPTS.parent.parent


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


# ---------------------------------------------------------- T-V-4: missing canonical
def test_verify_drift_returns_one_when_canonical_missing(fake_plugin, capsys):
    verify_drift = _load_verify_drift()

    # Build a functional copy without a matching canonical source.
    dst = fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(b"orphan")

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }

    rc = verify_drift.verify_drift(route=route, root=fake_plugin)
    out = capsys.readouterr().out

    assert rc == 1
    assert "MISSING-CANONICAL" in out


# ---------------------------------------------------------- T-V-5: CLI + diff
def test_verify_drift_cli_emits_unified_diff_on_drift(fake_plugin):
    import distribute

    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(b'{"original": true}\n')

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }
    distribute.distribute(route=route, root=fake_plugin)
    dst = fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json"
    dst.write_bytes(b'{"mutated": true}\n')

    wrapper = fake_plugin / "run-verify.py"
    wrapper.write_text(
        f"""
import sys, importlib.util
sys.path.insert(0, {str(SCRIPTS)!r})
import distribute
distribute.ROOT = __import__('pathlib').Path({str(fake_plugin)!r})
distribute.CANONICAL_DIR = distribute.ROOT / 'scripts' / 'canonical'
distribute.ROUTE = {{
    'legal-sources.json': ['skills/legal-contract-review/assets/legal-sources.json'],
}}
spec = importlib.util.spec_from_file_location('verify_drift', {str(SCRIPTS / 'verify-drift.py')!r})
vd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vd)
sys.exit(vd.main())
"""
    )
    result = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

    assert result.returncode == 1
    assert "DRIFT" in result.stdout
    # Unified-diff lines from `diff -u` start with --- / +++ / @@
    assert "---" in result.stdout
    assert "+++" in result.stdout
    assert "@@" in result.stdout


# ---------------------------------------------------------- T-V-6: real SP3b destination drift
def test_verify_drift_catches_sp3b_destination_modification():
    """Modifying SP3b's functional copy should be caught by verify-drift.py
    (exit 1) against the REAL repository ROUTE table."""
    sp3b_copy = (
        REPO
        / "legal-toolkit"
        / "skills"
        / "legal-incident-response"
        / "scripts"
        / "load_profile.py"
    )
    assert sp3b_copy.is_file(), (
        f"SP3b functional copy missing — run distribute.py first: {sp3b_copy}"
    )
    original = sp3b_copy.read_bytes()
    try:
        sp3b_copy.write_text(
            original.decode() + "\n# drift marker\n", encoding="utf-8"
        )
        result = subprocess.run(
            ["python3", "legal-toolkit/scripts/verify-drift.py"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        assert result.returncode == 1, (
            f"verify-drift should fail on drift; got rc={result.returncode}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "DRIFT" in result.stdout
        assert "legal-incident-response" in result.stdout
    finally:
        sp3b_copy.write_bytes(original)
