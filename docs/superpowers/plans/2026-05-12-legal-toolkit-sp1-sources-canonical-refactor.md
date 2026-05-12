# legal-toolkit SP1 — `legal-sources.json` SSOT-and-functional-copy refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json` to a plugin-level canonical source-of-truth at `legal-toolkit/scripts/canonical/legal-sources.json`, plus deterministic `distribute.py` + `verify-drift.py` (mirrors translation-toolkit precedent), so Phase 2 sibling skills can carry byte-identical functional copies under their own `assets/` without violating the self-contained-skill convention. Zero runtime behavior change.

**Architecture:** Plugin-level `scripts/canonical/` is the only editable surface. `scripts/distribute.py` deploys byte-identical copies to each routed destination (current: 1 consumer; Phase 2: 3 consumers). `scripts/verify-drift.py` is the CI gate that fails on any mismatch or missing destination. Tests use `pytest tmp_path` to simulate the plugin tree in isolation, so the real `legal-sources.json` is touched only in Task 10 (migration).

**Tech Stack:** Python 3.11 stdlib (`shutil`, `pathlib`, `filecmp`, `hashlib`, `subprocess`, `sys`). pytest for tests. GitHub Actions for CI.

**Branch:** `feat/legal-toolkit-v0.3.6-sources-canonical` (already created; spec committed at `2ac626d` + `aa1be43`).

**Spec:** [docs/superpowers/specs/2026-05-12-legal-toolkit-sp1-sources-canonical-refactor-design.md](../specs/2026-05-12-legal-toolkit-sp1-sources-canonical-refactor-design.md)

---

## File Structure

**Created**:
- `legal-toolkit/scripts/__init__.py` (empty marker for pytest import)
- `legal-toolkit/scripts/canonical/legal-sources.json` (via `git mv` from existing location in Task 10)
- `legal-toolkit/scripts/canonical/README.md` (forcing-function doc — Task 11)
- `legal-toolkit/scripts/distribute.py` (Tasks 1–4)
- `legal-toolkit/scripts/verify-drift.py` (Tasks 5–9)
- `legal-toolkit/scripts/tests/__init__.py` (empty marker)
- `legal-toolkit/scripts/tests/conftest.py` (shared fixtures)
- `legal-toolkit/scripts/tests/test_distribute.py` (Tasks 1–4 incremental)
- `legal-toolkit/scripts/tests/test_verify_drift.py` (Tasks 5–9 incremental)
- `.github/workflows/legal-toolkit-ci.yml` (Task 12)

**Modified**:
- `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json` (removed by `git mv` in Task 10, then immediately recreated byte-identical by `distribute.py` — net diff at HEAD = unchanged content, file presence preserved so `build_citation_url.py` runtime stays green)
- `legal-toolkit/.claude-plugin/plugin.json` (version 0.3.5 → 0.3.6 + append Phase 1.10 sentence to description — Task 13)
- `.claude-plugin/marketplace.json` (description sync per CI rule — Task 13)
- `legal-toolkit/ROADMAP.md` (add `## Phase 1.10 — SoT canonical refactor (v0.3.6, ...)` section — Task 13)

**NOT touched** (out of scope per spec §9):
- `legal-toolkit/baseline-source/` (different pattern class, 1→1 tarball)
- `legal-toolkit/skills/legal-contract-review/scripts/build_baseline.py` / `build_citation_url.py` / `cache_check.py`
- `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json` content (SP2 will update; SP1 is plumbing)
- Phase 2 skill directories (don't exist yet)

---

## Task 1: Scaffold `scripts/` + import-test sentinel

**Files:**
- Create: `legal-toolkit/scripts/__init__.py`
- Create: `legal-toolkit/scripts/distribute.py`
- Create: `legal-toolkit/scripts/tests/__init__.py`
- Create: `legal-toolkit/scripts/tests/conftest.py`
- Create: `legal-toolkit/scripts/tests/test_distribute.py`

- [ ] **Step 1: Create `scripts/__init__.py` and `scripts/tests/__init__.py` (both empty)**

```bash
mkdir -p legal-toolkit/scripts/canonical legal-toolkit/scripts/tests
touch legal-toolkit/scripts/__init__.py legal-toolkit/scripts/tests/__init__.py
```

- [ ] **Step 2: Write `scripts/tests/conftest.py` — shared fixture for synthetic plugin tree**

`legal-toolkit/scripts/tests/conftest.py`:

```python
"""Shared pytest fixtures for distribute / verify-drift tests.

Each test builds an isolated synthetic plugin tree under pytest's
tmp_path so we never touch the real legal-toolkit/ skills/ tree.
"""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fake_plugin(tmp_path: Path) -> Path:
    """Return a tmp_path that looks like a plugin root: scripts/canonical/
    pre-created, skills/ empty.

    Tests put canonical files under <fake_plugin>/scripts/canonical/, and
    assert distribute() / verify_drift() behavior against the synthetic tree.
    """
    (tmp_path / "scripts" / "canonical").mkdir(parents=True)
    (tmp_path / "skills").mkdir()
    return tmp_path
```

- [ ] **Step 3: Write `scripts/tests/test_distribute.py` — Task-1 import test**

`legal-toolkit/scripts/tests/test_distribute.py`:

```python
"""Tests for legal-toolkit/scripts/distribute.py.

distribute.py exposes ROUTE / ROOT / CANONICAL_DIR / iter_canonical_files /
distribute(); these are the surface that verify-drift.py imports.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


# ---------------------------------------------------------- T-D-1: surface
def test_distribute_module_exposes_constants():
    import distribute

    assert hasattr(distribute, "ROUTE"), "distribute.ROUTE missing"
    assert hasattr(distribute, "ROOT"), "distribute.ROOT missing"
    assert hasattr(distribute, "CANONICAL_DIR"), "distribute.CANONICAL_DIR missing"
    assert isinstance(distribute.ROUTE, dict)
    assert isinstance(distribute.ROOT, Path)
    assert isinstance(distribute.CANONICAL_DIR, Path)


def test_route_table_well_formed():
    import distribute

    assert distribute.ROUTE, "ROUTE must declare at least one canonical file"
    for canonical_name, destinations in distribute.ROUTE.items():
        assert isinstance(canonical_name, str)
        assert isinstance(destinations, list)
        assert destinations, f"ROUTE['{canonical_name}'] has no destinations"
        for dst in destinations:
            assert isinstance(dst, str)
            assert dst.startswith("skills/"), (
                f"ROUTE destination must be skills-relative: {dst!r}"
            )
```

- [ ] **Step 4: Write minimal `scripts/distribute.py` — constants only**

`legal-toolkit/scripts/distribute.py`:

```python
#!/usr/bin/env python3
"""Distribute scripts/canonical/* to each routed skill assets/ as byte-identical
functional copies.

SSOT-and-functional-copy pattern (mirror of translation-toolkit/scripts/):
  scripts/canonical/<file>          -> single source of truth (only editable
                                       location)
  skills/<skill>/<subfolder>/<file> -> byte-identical functional copy
                                       (Edit forbidden; CI verifies)

Workflow:
  1. Edit a file under scripts/canonical/.
  2. Run `python3 legal-toolkit/scripts/distribute.py` from the repo root.
  3. Commit canonical edit + functional-copy updates in the same commit.

CI runs verify-drift.py to enforce byte-identical copies.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_DIR = ROOT / "scripts" / "canonical"

# Routing table — reflects CURRENT state. Update in the same commit that
# creates the new consuming skill. No auto-skip.
ROUTE: dict[str, list[str]] = {
    "legal-sources.json": [
        "skills/legal-contract-review/assets/legal-sources.json",
    ],
}
```

- [ ] **Step 5: Run T-D-1 surface tests to verify they pass**

Run from repo root:

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_distribute.py -v
```

Expected: 2 tests PASS (`test_distribute_module_exposes_constants`, `test_route_table_well_formed`).

- [ ] **Step 6: Commit**

```bash
git add legal-toolkit/scripts/
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): scaffold scripts/canonical + distribute.py constants

Mirror of translation-toolkit/scripts/ scaffolding: scripts/canonical/
SoT dir + scripts/distribute.py constants (ROUTE, ROOT, CANONICAL_DIR)
+ pytest tests/ with conftest.py fake_plugin fixture. ROUTE declares
1 consumer (legal-contract-review/assets/legal-sources.json) at SP1
ship — Phase 2 PR will append the two sibling skills.

No real legal-sources.json motion yet (Task 10); distribute.py is
constants-only at this commit.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: `distribute.py` — `iter_canonical_files`

**Files:**
- Modify: `legal-toolkit/scripts/distribute.py`
- Modify: `legal-toolkit/scripts/tests/test_distribute.py`

- [ ] **Step 1: Write failing tests for iter_canonical_files**

Append to `legal-toolkit/scripts/tests/test_distribute.py`:

```python
# ---------------------------------------------------------- T-D-2: scanner
def test_iter_canonical_files_yields_relative_names(fake_plugin):
    import distribute

    (fake_plugin / "scripts" / "canonical" / "a.json").write_text("a")
    (fake_plugin / "scripts" / "canonical" / "b.json").write_text("b")

    result = distribute.iter_canonical_files(fake_plugin / "scripts" / "canonical")

    names = sorted(rel for rel, _ in result)
    assert names == ["a.json", "b.json"]


def test_iter_canonical_files_skips_filesystem_noise(fake_plugin):
    import distribute

    canonical = fake_plugin / "scripts" / "canonical"
    (canonical / "real.json").write_text("real")
    (canonical / ".DS_Store").write_text("mac droppings")
    (canonical / ".gitkeep").write_text("")
    (canonical / "._real.json").write_text("appledouble")

    names = sorted(rel for rel, _ in distribute.iter_canonical_files(canonical))
    assert names == ["real.json"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_distribute.py -v
```

Expected: 2 prior tests PASS, 2 new tests FAIL with `AttributeError: module 'distribute' has no attribute 'iter_canonical_files'`.

- [ ] **Step 3: Implement `iter_canonical_files`**

Append to `legal-toolkit/scripts/distribute.py`:

```python
# Filesystem noise to skip — never authored files.
IGNORED_NAMES = {".DS_Store", ".gitkeep"}


def iter_canonical_files(canonical_dir: Path = CANONICAL_DIR) -> list[tuple[str, Path]]:
    """Yield (relative_posix_name, absolute_path) for every file under
    canonical_dir, sorted for deterministic output.

    Filters out macOS Finder droppings, empty-dir markers, AppleDouble files,
    and Python bytecode caches.
    """
    out: list[tuple[str, Path]] = []
    for p in sorted(canonical_dir.rglob("*")):
        if not p.is_file():
            continue
        if p.name in IGNORED_NAMES or p.name.startswith("._"):
            continue
        if "__pycache__" in p.parts:
            continue
        rel = p.relative_to(canonical_dir).as_posix()
        out.append((rel, p))
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_distribute.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add legal-toolkit/scripts/
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): distribute.py iter_canonical_files scanner

Walks scripts/canonical/ recursively, returns sorted (relative_name,
abs_path) tuples. Skips macOS Finder droppings (.DS_Store, ._* AppleDouble),
empty-dir markers (.gitkeep), and __pycache__ trees.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: `distribute.py` — `distribute()` core copy logic

**Files:**
- Modify: `legal-toolkit/scripts/distribute.py`
- Modify: `legal-toolkit/scripts/tests/test_distribute.py`

- [ ] **Step 1: Write failing tests for distribute() byte-identical + idempotent + parent-dir creation**

Append to `legal-toolkit/scripts/tests/test_distribute.py`:

```python
# ---------------------------------------------------------- T-D-3: distribute()
def test_distribute_creates_byte_identical_copies(fake_plugin):
    import distribute

    payload = b'{"key": "value", "n": 42}\n'
    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(payload)

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }
    distribute.distribute(route=route, root=fake_plugin)

    dst = fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json"
    assert dst.exists()
    assert dst.read_bytes() == payload


def test_distribute_creates_parent_dirs(fake_plugin):
    import distribute

    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(b"x")

    # skills/legal-contract-review/assets/ does NOT exist beforehand.
    assert not (fake_plugin / "skills" / "legal-contract-review").exists()

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }
    distribute.distribute(route=route, root=fake_plugin)

    assert (fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json").exists()


def test_distribute_is_idempotent(fake_plugin):
    import distribute

    payload = b'{"version": 1}'
    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(payload)

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }
    distribute.distribute(route=route, root=fake_plugin)
    distribute.distribute(route=route, root=fake_plugin)  # second call

    dst = fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json"
    assert dst.read_bytes() == payload
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_distribute.py -v
```

Expected: 4 prior tests PASS, 3 new tests FAIL with `AttributeError: module 'distribute' has no attribute 'distribute'`.

- [ ] **Step 3: Implement `distribute()`**

Append to `legal-toolkit/scripts/distribute.py`:

```python
import shutil


def distribute(
    route: dict[str, list[str]] | None = None,
    root: Path | None = None,
) -> int:
    """Copy each canonical file to its routed destinations.

    Args:
      route: routing table; defaults to module-level ROUTE.
      root:  plugin root path; defaults to module-level ROOT.

    Returns:
      Number of byte-identical copies written. Creates parent dirs as needed.
      Raises FileNotFoundError if a canonical file declared in ROUTE is absent.
    """
    if route is None:
        route = ROUTE
    if root is None:
        root = ROOT
    canonical_dir = root / "scripts" / "canonical"

    written = 0
    for canonical_name, destinations in route.items():
        src = canonical_dir / canonical_name
        if not src.is_file():
            raise FileNotFoundError(
                f"canonical source missing: {src.relative_to(root)}"
            )
        for rel_dst in destinations:
            dst = root / rel_dst
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            written += 1
            print(f"[deploy] canonical/{canonical_name} -> {rel_dst}")
    return written
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_distribute.py -v
```

Expected: 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add legal-toolkit/scripts/
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): distribute.py distribute() core copy

Copy each ROUTE canonical_name to its declared destinations using
shutil.copyfile (data-only copy; no metadata bleed). Creates parent
dirs as needed; idempotent. Raises FileNotFoundError if a declared
canonical source is missing. Prints [deploy] line per copy.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: `distribute.py` — CLI `main()`

**Files:**
- Modify: `legal-toolkit/scripts/distribute.py`
- Modify: `legal-toolkit/scripts/tests/test_distribute.py`

- [ ] **Step 1: Write failing test for CLI invocation**

Append to `legal-toolkit/scripts/tests/test_distribute.py`:

```python
# ---------------------------------------------------------- T-D-4: CLI
import subprocess


def test_distribute_cli_writes_copy_and_summary(fake_plugin, monkeypatch):
    """Invoke distribute.py as a script, with ROOT pointing at the fake plugin
    via a tiny wrapper script.
    """
    import distribute

    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(b'{"a": 1}')

    wrapper = fake_plugin / "run.py"
    wrapper.write_text(
        f"""
import sys
sys.path.insert(0, {str(SCRIPTS)!r})
import distribute
distribute.ROOT = __import__('pathlib').Path({str(fake_plugin)!r})
distribute.CANONICAL_DIR = distribute.ROOT / 'scripts' / 'canonical'
distribute.ROUTE = {{
    'legal-sources.json': ['skills/legal-contract-review/assets/legal-sources.json'],
}}
sys.exit(distribute.main())
"""
    )
    result = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )

    assert result.returncode == 0, result.stderr
    assert "[deploy]" in result.stdout
    assert "1 copies" in result.stdout or "1 file" in result.stdout
    dst = fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json"
    assert dst.read_bytes() == b'{"a": 1}'
```

- [ ] **Step 2: Run test to verify it fails**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_distribute.py::test_distribute_cli_writes_copy_and_summary -v
```

Expected: FAIL — `main` not defined.

- [ ] **Step 3: Implement `main()` + `__main__` guard**

Append to `legal-toolkit/scripts/distribute.py`:

```python
import sys


def main() -> int:
    if not CANONICAL_DIR.is_dir():
        print(f"ERROR: canonical directory not found: {CANONICAL_DIR}", file=sys.stderr)
        return 2
    try:
        n = distribute()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print(f"\nOK: deployed {n} copies from canonical/ to skill assets/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify all pass**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_distribute.py -v
```

Expected: 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add legal-toolkit/scripts/
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): distribute.py CLI main() + __main__ guard

Exit 0 on success; exit 2 on missing canonical dir or declared
canonical source. Prints per-file [deploy] line then summary count.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: `verify-drift.py` — pass case (byte-identical match)

**Files:**
- Create: `legal-toolkit/scripts/verify-drift.py`
- Create: `legal-toolkit/scripts/tests/test_verify_drift.py`

- [ ] **Step 1: Write failing test for the pass case**

`legal-toolkit/scripts/tests/test_verify_drift.py`:

```python
"""Tests for legal-toolkit/scripts/verify-drift.py.

verify-drift checks that each ROUTE destination is byte-identical
to its canonical source. No auto-skip — every declared route is
mandatory.
"""
from __future__ import annotations

import importlib.util
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_verify_drift.py -v
```

Expected: FAIL — `verify-drift.py` does not exist.

- [ ] **Step 3: Write minimal `verify-drift.py` — happy path only**

`legal-toolkit/scripts/verify-drift.py`:

```python
#!/usr/bin/env python3
"""Verify each ROUTE destination is byte-identical to its canonical source.

Exit 0 -> every routed destination exists and matches canonical.
Exit 1 -> at least one drift (mismatch, missing file, or missing canonical).

No auto-skip — every entry in ROUTE is mandatory. Update ROUTE in the same
commit that creates (or removes) a consuming skill.

CI gate: runs after every PR / push that touches legal-toolkit/.
"""
from __future__ import annotations

import filecmp
import sys
from pathlib import Path

# Reuse routing from distribute.py for consistency.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from distribute import (  # type: ignore  # noqa: E402
    CANONICAL_DIR,
    ROOT,
    ROUTE,
)


def verify_drift(
    route: dict[str, list[str]] | None = None,
    root: Path | None = None,
) -> int:
    """Return 0 if every routed destination matches its canonical source; 1
    otherwise. Pure function — does not touch the real filesystem unless
    `root` defaults to ROOT.
    """
    if route is None:
        route = ROUTE
    if root is None:
        root = ROOT
    canonical_dir = root / "scripts" / "canonical"

    drifts: list[str] = []
    checked = 0
    for canonical_name, destinations in route.items():
        src = canonical_dir / canonical_name
        if not src.is_file():
            drifts.append(f"MISSING-CANONICAL  scripts/canonical/{canonical_name}")
            continue
        for rel_dst in destinations:
            dst = root / rel_dst
            if not dst.is_file():
                drifts.append(f"MISSING  {rel_dst}")
                continue
            if not filecmp.cmp(src, dst, shallow=False):
                drifts.append(
                    f"DRIFT    {rel_dst} differs from scripts/canonical/{canonical_name}"
                )
            checked += 1
    if drifts:
        for d in drifts:
            print(d)
        return 1
    print(f"OK: all {checked} functional copies byte-identical to canonical.")
    return 0
```

- [ ] **Step 4: Run test to verify it passes**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_verify_drift.py -v
```

Expected: 1 test PASSES.

- [ ] **Step 5: Commit**

```bash
git add legal-toolkit/scripts/verify-drift.py legal-toolkit/scripts/tests/test_verify_drift.py
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): verify-drift.py byte-compare happy path

Reuse ROUTE / ROOT / CANONICAL_DIR from distribute.py. Iterate the
routing table; assert each destination exists and is byte-identical
to its canonical source. Print summary line on PASS.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: `verify-drift.py` — mutation detection + DRIFT message

**Files:**
- Modify: `legal-toolkit/scripts/tests/test_verify_drift.py`

(No code change to `verify-drift.py` — Task 5's loop already detects mismatch via filecmp; this task locks the behavior with a regression test.)

- [ ] **Step 1: Write failing test for mutation case**

Append to `legal-toolkit/scripts/tests/test_verify_drift.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it passes (already covered by Task 5 impl)**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_verify_drift.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 3: Commit (regression-lock only — no impl change)**

```bash
git add legal-toolkit/scripts/tests/test_verify_drift.py
git commit -m "$(cat <<'EOF'
test(legal-toolkit): verify-drift detects mutated functional copy

Regression test for T-V-2: mutating a functional copy by 1 byte
must produce exit 1 + stdout containing "DRIFT" and the destination
path. Locks Task 5's filecmp-based detection behavior.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: `verify-drift.py` — missing-copy detection

**Files:**
- Modify: `legal-toolkit/scripts/tests/test_verify_drift.py`

(Behavior covered by Task 5 impl; this task locks it with a test.)

- [ ] **Step 1: Write test for missing-copy case**

Append to `legal-toolkit/scripts/tests/test_verify_drift.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it passes**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_verify_drift.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add legal-toolkit/scripts/tests/test_verify_drift.py
git commit -m "$(cat <<'EOF'
test(legal-toolkit): verify-drift detects missing functional copy

Regression test for T-V-3: every declared ROUTE destination is
mandatory — absence produces exit 1 + stdout containing "MISSING"
and the destination path. No auto-skip rule (matches spec §4.2 +
translation-toolkit precedent).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: `verify-drift.py` — missing-canonical detection

**Files:**
- Modify: `legal-toolkit/scripts/tests/test_verify_drift.py`

- [ ] **Step 1: Write test for missing-canonical case**

Append to `legal-toolkit/scripts/tests/test_verify_drift.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it passes**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_verify_drift.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add legal-toolkit/scripts/tests/test_verify_drift.py
git commit -m "$(cat <<'EOF'
test(legal-toolkit): verify-drift detects missing canonical source

Regression test for T-V-4: if a ROUTE entry references a canonical
file that does not exist under scripts/canonical/, exit 1 with
"MISSING-CANONICAL" — a broken pipe is a bug.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: `verify-drift.py` — CLI main + unified diff on DRIFT

**Files:**
- Modify: `legal-toolkit/scripts/verify-drift.py`
- Modify: `legal-toolkit/scripts/tests/test_verify_drift.py`

- [ ] **Step 1: Write failing test for CLI behavior + unified-diff output on mutation**

Append to `legal-toolkit/scripts/tests/test_verify_drift.py`:

```python
# ---------------------------------------------------------- T-V-5: CLI + diff
import subprocess


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
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )

    assert result.returncode == 1
    assert "DRIFT" in result.stdout
    # Unified-diff lines from `diff -u` start with --- / +++ / @@
    assert "---" in result.stdout
    assert "+++" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/test_verify_drift.py::test_verify_drift_cli_emits_unified_diff_on_drift -v
```

Expected: FAIL — `main` not defined OR no unified diff.

- [ ] **Step 3: Implement `main()` with unified-diff output**

Append to `legal-toolkit/scripts/verify-drift.py`:

```python
import hashlib
import subprocess


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _print_unified_diff(reference: Path, drift_path: Path, max_lines: int = 50) -> None:
    """Print up to max_lines of `diff -u` output so reviewers see WHAT differs,
    not just THAT it differs. Also print md5 for both files.
    """
    print(f"    md5(canonical) = {_md5(reference)}")
    print(f"    md5(copy)      = {_md5(drift_path)}")
    try:
        out = subprocess.run(
            ["diff", "-u", str(reference), str(drift_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        text = out.stdout or out.stderr or ""
        lines = text.splitlines()
        for line in lines[:max_lines]:
            print(f"    {line}")
        if len(lines) > max_lines:
            print(f"    ... ({len(lines) - max_lines} more lines truncated)")
    except FileNotFoundError:
        print("    (diff binary unavailable)")


def main() -> int:
    if not CANONICAL_DIR.is_dir():
        print(f"ERROR: canonical directory not found: {CANONICAL_DIR}", file=sys.stderr)
        return 2

    drifts: list[tuple[str, Path | None, Path | None]] = []
    checked = 0
    for canonical_name, destinations in ROUTE.items():
        src = CANONICAL_DIR / canonical_name
        if not src.is_file():
            drifts.append(
                (f"MISSING-CANONICAL  scripts/canonical/{canonical_name}", None, None)
            )
            continue
        for rel_dst in destinations:
            dst = ROOT / rel_dst
            if not dst.is_file():
                drifts.append((f"MISSING  {rel_dst}", None, None))
                continue
            if not filecmp.cmp(src, dst, shallow=False):
                drifts.append(
                    (
                        f"DRIFT    {rel_dst} differs from scripts/canonical/{canonical_name}",
                        src,
                        dst,
                    )
                )
            checked += 1

    if drifts:
        for label, ref, drift_path in drifts:
            print(label)
            if ref is not None and drift_path is not None:
                _print_unified_diff(ref, drift_path)
        print(f"\nFAIL: {len(drifts)} drift(s) detected (checked {checked} pairs).")
        print("\nFix locally: python3 legal-toolkit/scripts/distribute.py")
        return 1

    print(f"OK: all {checked} functional copies byte-identical to canonical.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run all verify-drift tests to confirm green**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/ -v
```

Expected: 13 tests PASS (8 distribute + 5 verify-drift).

- [ ] **Step 5: Commit**

```bash
git add legal-toolkit/scripts/
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): verify-drift CLI + unified diff on DRIFT

main() classifies drifts (MISSING-CANONICAL / MISSING / DRIFT),
prints md5 + truncated diff -u for true content mismatches so PR
reviewers see WHAT differs not just THAT it differs. Hint at the
fix command at the bottom of the FAIL summary.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Migration — promote `legal-sources.json` to canonical

**Files:**
- `git mv`: `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json` → `legal-toolkit/scripts/canonical/legal-sources.json`
- Regenerated: `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json` (byte-identical, materialized by distribute.py)

- [ ] **Step 1: Stage the move + run distribute.py to materialize the functional copy**

Run from repo root:

```bash
git mv legal-toolkit/skills/legal-contract-review/assets/legal-sources.json \
       legal-toolkit/scripts/canonical/legal-sources.json
python3 legal-toolkit/scripts/distribute.py
```

Expected stdout from distribute.py:
```
[deploy] canonical/legal-sources.json -> skills/legal-contract-review/assets/legal-sources.json

OK: deployed 1 copies from canonical/ to skill assets/.
```

- [ ] **Step 2: Confirm byte-identical at both locations**

```bash
diff -q legal-toolkit/scripts/canonical/legal-sources.json \
        legal-toolkit/skills/legal-contract-review/assets/legal-sources.json
```

Expected: no output (files identical). If diff prints anything, abort and investigate.

- [ ] **Step 3: Run verify-drift.py against the live working tree → must exit 0**

```bash
python3 legal-toolkit/scripts/verify-drift.py
```

Expected:
```
OK: all 1 functional copies byte-identical to canonical.
```

- [ ] **Step 4: Manual drift smoke — mutate copy + re-verify → must exit 1, then restore**

```bash
# Mutate
echo "X" >> legal-toolkit/skills/legal-contract-review/assets/legal-sources.json
python3 legal-toolkit/scripts/verify-drift.py; echo "exit=$?"
# Expected: stdout has DRIFT + unified diff; exit=1

# Restore via distribute.py
python3 legal-toolkit/scripts/distribute.py
python3 legal-toolkit/scripts/verify-drift.py; echo "exit=$?"
# Expected: OK; exit=0
```

- [ ] **Step 5: Run full existing legal-toolkit test suite — must remain green (171 tests)**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/tests/ -v
```

Expected: 171 tests PASS (or whatever count v0.3.5 ships).

Per memory `feedback_pycache_hook_blocks_edits.md`: `PYTHONDONTWRITEBYTECODE=1` is required to avoid the validate-skill-folder-structure hook blocking later edits on `__pycache__/` artifacts.

If any test fails, the most likely cause is `build_citation_url.py` not finding the JSON at its expected location — verify the path with `ls legal-toolkit/skills/legal-contract-review/assets/legal-sources.json` and re-run distribute.py if missing.

- [ ] **Step 6: Run new scripts test suite — must be green (13 tests)**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/scripts/tests/ -v
```

Expected: 13 tests PASS.

- [ ] **Step 7: Stage the recreated functional copy + commit**

```bash
git add legal-toolkit/skills/legal-contract-review/assets/legal-sources.json
git status --short
# Expected:
#  R  legal-toolkit/skills/legal-contract-review/assets/legal-sources.json -> legal-toolkit/scripts/canonical/legal-sources.json
#  A  legal-toolkit/skills/legal-contract-review/assets/legal-sources.json
# (git may detect this as rename + new-file pair, or as 2 untracked + 1 deleted — either is OK as long as both paths end up at HEAD with identical bytes)

git commit -m "$(cat <<'EOF'
refactor(legal-toolkit): promote legal-sources.json to canonical SoT

git mv the runtime registry from legal-contract-review/assets/ to the
new plugin-level scripts/canonical/, then re-materialize the functional
copy at its original skill-side location via distribute.py. End-state:
canonical SoT is the only hand-edited surface; legal-contract-review's
assets/legal-sources.json is now a byte-identical functional copy that
build_citation_url.py + L7-evaluate.md continue to read unchanged.

Zero runtime behavior change. Validated by:
  - 171/171 legal-toolkit/tests/ green
  - 13/13 legal-toolkit/scripts/tests/ green
  - verify-drift.py exit 0
  - mutate-then-verify smoke returns exit 1

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: `scripts/canonical/README.md` — forcing-function doc

**Files:**
- Create: `legal-toolkit/scripts/canonical/README.md`

- [ ] **Step 1: Write README**

`legal-toolkit/scripts/canonical/README.md`:

```markdown
# Canonical sources (SoT)

This directory is the **single source of truth** for cross-skill data files
in `legal-toolkit`. Editing rules:

- **Only edit files here.** Never edit `skills/<skill>/assets/<file>` directly —
  those are byte-identical functional copies materialized by `distribute.py`.
- **After editing**, run from the repo root:
  ```
  python3 legal-toolkit/scripts/distribute.py
  ```
  This deploys the byte-identical copy to every skill listed in `distribute.py`'s
  `ROUTE` table.
- **Commit canonical edit + functional-copy updates in the same commit.**
  CI runs `verify-drift.py` and will fail the PR if any functional copy
  drifts from canonical.

## Current consumers

See `legal-toolkit/scripts/distribute.py:ROUTE` for the authoritative list.
As of v0.3.6, `legal-sources.json` deploys to:

- `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json`

Phase 2 (v0.4.0) extends the ROUTE with `legal-document-draft` and
`legal-incident-response`.

## Why this pattern

Anthropic skill convention: each skill is self-contained — its SKILL.md and
runtime-loaded protocols may not reach into another skill's directory tree.
But Phase 2 sibling skills need the same statute / case / 函釋 URL registry.
We resolve this by **storing the SoT outside `skills/`** and **deploying
byte-identical copies INTO each consuming skill**, with CI enforcing that
the copies never drift. Mirrors `translation-toolkit/scripts/canonical/`
precedent.

Background: `docs/superpowers/specs/2026-05-12-legal-toolkit-sp1-sources-canonical-refactor-design.md`.
```

- [ ] **Step 2: Commit**

```bash
git add legal-toolkit/scripts/canonical/README.md
git commit -m "$(cat <<'EOF'
docs(legal-toolkit): canonical/ README explaining SoT editing rule

Tells future editors: only edit canonical/, run distribute.py, commit
both in same PR; verify-drift will catch any drift. Mirrors the
translation-toolkit canonical/ workflow.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: GitHub Actions workflow

**Files:**
- Create: `.github/workflows/legal-toolkit-ci.yml`

- [ ] **Step 1: Write the workflow**

`.github/workflows/legal-toolkit-ci.yml`:

```yaml
name: legal-toolkit CI

# Runs the legal-toolkit pytest suite (171 tests under tests/ + 13 tests
# under scripts/tests/) and the SSOT-vs-functional-copy drift verifier
# on every PR that touches the plugin (or the workflow itself), and on
# every push to main that changes the plugin.

on:
  pull_request:
    paths:
      - 'legal-toolkit/**'
      - '.github/workflows/legal-toolkit-ci.yml'
  push:
    branches: [main]
    paths:
      - 'legal-toolkit/**'

permissions:
  contents: read

jobs:
  test:
    name: pytest + drift + skill-folder-structure
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install test deps
        run: python3 -m pip install --quiet pytest

      - name: Run legal-toolkit scripts/ pytest suite
        env:
          PYTHONDONTWRITEBYTECODE: "1"
        run: python3 -m pytest legal-toolkit/scripts/tests/ -v

      - name: Run legal-toolkit existing pytest suite
        env:
          PYTHONDONTWRITEBYTECODE: "1"
        run: python3 -m pytest legal-toolkit/tests/ -v

      - name: Verify SSOT-vs-functional-copy drift
        # canonical/ is the single source of truth; each skill carries
        # functional copies under assets/. Any byte-level divergence fails
        # the build.
        run: python3 legal-toolkit/scripts/verify-drift.py

      - name: Validate skill folder structure
        # Anthropic skill convention: SKILL.md + flat single-level subfolders.
        # Hook script enforces no nested-subfolder violations per skill.
        run: |
          for skill in using-legal-toolkit legal-playbook-author legal-contract-review; do
            bash .claude/hooks/validate-skill-folder-structure.sh "legal-toolkit/skills/$skill/SKILL.md"
          done
```

- [ ] **Step 2: Sanity-check the workflow file locally**

```bash
# Confirm YAML parses
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/legal-toolkit-ci.yml'))"
```

Expected: no output (clean parse).

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/legal-toolkit-ci.yml
git commit -m "$(cat <<'EOF'
chore(legal-toolkit): add CI workflow — pytest + verify-drift + skill-struct

Mirrors translation-toolkit-ci.yml; trigger paths constrained to
legal-toolkit/** + workflow file. Runs both pytest suites (scripts/tests
+ legacy tests/) and the new verify-drift.py SoT gate. Validates folder
structure for all 3 skills via .claude/hooks/.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 13: Version bump + ROADMAP entry + marketplace.json sync

**Files:**
- Modify: `legal-toolkit/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `legal-toolkit/ROADMAP.md`

- [ ] **Step 1: Bump plugin.json version + append v0.3.6 description sentence**

`legal-toolkit/.claude-plugin/plugin.json`:

1. Change `"version": "0.3.5"` to `"version": "0.3.6"`.
2. Append this sentence to the existing description string (immediately before the final `Phase 2-5 adds ...` sentence):

   ```
   v0.3.6 Phase 1.10 cross-skill plumbing refactor: legal-sources.json promoted to plugin-level scripts/canonical/ SoT (mirror of translation-toolkit pattern); scripts/distribute.py deploys byte-identical functional copies to each consuming skill's assets/; scripts/verify-drift.py CI gate fails PRs on any drift. Unblocks Phase 2 (legal-document-draft + legal-incident-response) sibling-skill access without violating self-contained-skill convention.
   ```

- [ ] **Step 2: Sync marketplace.json description**

`.claude-plugin/marketplace.json`: find the entry whose `"source"` is `"./legal-toolkit/"` and update its `"description"` field to match plugin.json byte-identical.

Easier mechanical alternative:

```bash
python3 - <<'PY'
import json
from pathlib import Path

plugin_json = json.loads(Path("legal-toolkit/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
new_desc = plugin_json["description"]

market_path = Path(".claude-plugin/marketplace.json")
market = json.loads(market_path.read_text(encoding="utf-8"))
for p in market["plugins"]:
    if p.get("source") == "./legal-toolkit/":
        p["description"] = new_desc
        break
else:
    raise SystemExit("legal-toolkit entry not found in marketplace.json")

market_path.write_text(
    json.dumps(market, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print("OK: marketplace.json description synced to plugin.json")
PY
```

- [ ] **Step 3: Run the sync checker — must exit 0**

```bash
python3 scripts/check-marketplace-description-sync.py
```

Expected: exit 0 with success message. If exit 1, the descriptions don't match; copy plugin.json description verbatim into marketplace.json's `description` field and retry.

- [ ] **Step 4: Append Phase 1.10 section to ROADMAP.md**

Add this section after the `## Phase 1.9 — Audit-driven polish + NDA-native fallback` block in `legal-toolkit/ROADMAP.md` (search for `## Phase 2 — Template + Runbook` and insert ABOVE it):

```markdown
## Phase 1.10 — `legal-sources.json` SSOT-and-functional-copy refactor（v0.3.6，半天） ✅ **DONE 2026-05-12**

**Scope**：純 plumbing PR；零 runtime 行為改變。Phase 2 sibling skills 需要存取相同 statute / case / 函釋 URL registry，但 monkey-skills CLAUDE.md `Skill Structure` 規範要求每個 skill 自包含、SKILL.md 不可跨 skill reach。

### 完成狀態

- `legal-toolkit/scripts/canonical/legal-sources.json` — plugin-level SoT（唯一可手動編輯位置）
- `legal-toolkit/scripts/distribute.py` — byte-identical deploy 到 `ROUTE` 內每個 consumer skill
- `legal-toolkit/scripts/verify-drift.py` — CI gate；任何漂移 / missing 都 exit 1
- `legal-toolkit/scripts/tests/` — 13 tests（T-D-1..5 + T-V-1..5）
- `.github/workflows/legal-toolkit-ci.yml` — CI workflow（pytest + verify-drift + skill-folder-structure）
- `legal-contract-review/assets/legal-sources.json` 透過 `git mv` → canonical/，再由 distribute.py 重新生成回原位（byte-identical），`build_citation_url.py` 無需修改

### Quality gate

- 既有 171 tests 全綠（zero runtime behavior change）
- 新增 13 tests 全綠
- verify-drift.py 在 HEAD state 為 exit 0；mutation smoke 確認 exit 1
- CI workflow 第一次跑綠

### 為什麼

Phase 2 增加兩個 sibling skill（`legal-document-draft` + `legal-incident-response`），都要存取相同的 URL registry。三種選項：
- ❌ Skills reach into `legal-contract-review/assets/`（違反 self-contained 規範）
- ❌ Per-skill 獨立 narrow registry（三處漂移）
- ✅ Plugin-level SoT + byte-identical functional copies + CI drift gate（translation-toolkit 已驗證模式）

完整 design：`docs/superpowers/specs/2026-05-12-legal-toolkit-sp1-sources-canonical-refactor-design.md`
完整 plan：`docs/superpowers/plans/2026-05-12-legal-toolkit-sp1-sources-canonical-refactor.md`

### Deferred 到 SP2+

- `legal-sources.json` 內容更新（PDPA 2025/11 條文 verify）→ SP2 verify run
- `build_citation_url.py` / `cache_check.py` 是否也走 canonical/ pattern → Phase 2 設計階段決定（取決於 Phase 2 skills 是否做 runtime fetch；很可能不需要）

---
```

- [ ] **Step 5: Run final smoke — full pytest + verify-drift + sync checker**

```bash
python3 scripts/check-marketplace-description-sync.py
echo "---"
python3 legal-toolkit/scripts/verify-drift.py
echo "---"
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/tests/ legal-toolkit/scripts/tests/ -v
```

Expected:
- check-marketplace-description-sync.py exit 0
- verify-drift.py exit 0 with `OK: all 1 functional copies byte-identical to canonical.`
- pytest: 171 + 13 = 184 tests PASS

- [ ] **Step 6: Commit**

```bash
git add legal-toolkit/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json \
        legal-toolkit/ROADMAP.md
git commit -m "$(cat <<'EOF'
chore(legal-toolkit): bump to v0.3.6 + Phase 1.10 ROADMAP section

Phase 1.10 = SSOT-and-functional-copy refactor for legal-sources.json
(plugin-level scripts/canonical/ + distribute.py + verify-drift.py +
CI workflow). Zero runtime behavior change. Unblocks Phase 2 sibling
skills (legal-document-draft + legal-incident-response) without
violating self-contained-skill convention.

plugin.json + marketplace.json descriptions synced per repo CI rule
(scripts/check-marketplace-description-sync.py).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 14: PR readiness — final cross-checks

**Files:** none modified

- [ ] **Step 1: Confirm branch state is clean**

```bash
git status --short
git log --oneline feat/legal-toolkit-v0.3.6-sources-canonical ^main
```

Expected:
- `git status --short` shows no uncommitted changes (pre-existing untracked files from outside legal-toolkit/ are OK)
- Log shows ~14-15 commits (2 spec commits + 13 implementation commits + maybe minor fix-ups)

- [ ] **Step 2: Final triple-smoke**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/ -v
python3 legal-toolkit/scripts/verify-drift.py
python3 scripts/check-marketplace-description-sync.py
bash .claude/hooks/validate-skill-folder-structure.sh legal-toolkit/skills/legal-contract-review/SKILL.md
bash .claude/hooks/validate-skill-folder-structure.sh legal-toolkit/skills/legal-playbook-author/SKILL.md
bash .claude/hooks/validate-skill-folder-structure.sh legal-toolkit/skills/using-legal-toolkit/SKILL.md
```

All four must succeed (exit 0, all green).

- [ ] **Step 3: Ready to push + open PR**

Pause here for user confirmation. Don't push or open PR autonomously per user red-line rules (CLAUDE.md global instructions: outbound actions require approval).

When user gives the go signal, push the branch and open a PR:

```bash
git push -u origin feat/legal-toolkit-v0.3.6-sources-canonical
gh pr create --title "feat(legal-toolkit): v0.3.6 — legal-sources.json SSOT-and-functional-copy refactor" --body "$(cat <<'EOF'
## Summary

SP1 of legal-toolkit Phase 2 program. Promotes `legal-sources.json` to a plugin-level canonical SoT at `legal-toolkit/scripts/canonical/` + `distribute.py` deploy script + `verify-drift.py` CI gate. Mirrors `translation-toolkit/scripts/` precedent.

**Zero runtime behavior change.** Unblocks SP2 (PDPA 2025/11 verify run) and SP3 (Phase 2 `v0.4.0` ship of `legal-document-draft` + `legal-incident-response`) without violating the monkey-skills self-contained-skill convention.

## What changed

- **NEW** `legal-toolkit/scripts/canonical/legal-sources.json` — promoted via `git mv` from `legal-contract-review/assets/`; now the only editable surface.
- **NEW** `legal-toolkit/scripts/distribute.py` — deploys byte-identical functional copies per `ROUTE` table. SP1 ROUTE has 1 consumer; Phase 2 PR extends to 3.
- **NEW** `legal-toolkit/scripts/verify-drift.py` — CI gate; exits 1 on any divergence, missing copy, or missing canonical.
- **NEW** `legal-toolkit/scripts/tests/` — 13 tests (T-D-1..5 + T-V-1..5).
- **NEW** `.github/workflows/legal-toolkit-ci.yml` — pytest + verify-drift + skill-folder-structure validator.
- **NEW** `legal-toolkit/scripts/canonical/README.md` — workflow doc for future editors.
- **REGEN** `legal-contract-review/assets/legal-sources.json` — byte-identical, materialized by `distribute.py`; `build_citation_url.py` reads it unchanged.
- **BUMP** plugin.json `0.3.5 → 0.3.6`, marketplace.json description synced.
- **DOCS** `ROADMAP.md` `## Phase 1.10` section added.

## Test plan

- [ ] CI green (pytest 171 + 13 = 184 tests, verify-drift exit 0, skill-folder-structure validator green)
- [ ] `python3 legal-toolkit/scripts/verify-drift.py` returns exit 0 locally
- [ ] Manual smoke: mutate `legal-contract-review/assets/legal-sources.json` by 1 byte, run verify-drift → exit 1 with unified diff; revert with distribute.py → exit 0
- [ ] `python3 scripts/check-marketplace-description-sync.py` exit 0
- [ ] Add `legal-toolkit CI` to `main` branch protection's required checks list after first green run

## Design / plan

- Spec: `docs/superpowers/specs/2026-05-12-legal-toolkit-sp1-sources-canonical-refactor-design.md`
- Plan: `docs/superpowers/plans/2026-05-12-legal-toolkit-sp1-sources-canonical-refactor.md`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Completion checklist

After Task 14 passes the final triple-smoke:

- [ ] 13 implementation commits + 2 spec commits + (optional) fix-up commits
- [ ] All commits use Conventional Commits with kebab-case scope (per repo CI lint)
- [ ] Branch `feat/legal-toolkit-v0.3.6-sources-canonical` ready for push
- [ ] User confirms before push + PR open

---

## Estimate

~半天 工程 + 半天 CI iteration / review polish (per spec §12). 13–15 commits expected. Subagent-driven NOT recommended for this PR — the work is mechanical, well-bounded, and short enough that fresh-subagent-per-task overhead exceeds the parallelism gain. Inline execution via `superpowers:executing-plans` is the expected path.
