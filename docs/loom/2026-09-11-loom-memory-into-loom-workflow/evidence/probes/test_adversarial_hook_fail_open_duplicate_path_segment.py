"""Adversarial probe (surface 4): the memory-integrity hook's fail-open path.

`.claude/hooks/check-memory-store-integrity.sh` used to derive the repo
root with a single bash SHORTEST-suffix strip:

    REPO_ROOT="${FILE_PATH%/docs/loom/memory/*}"

`%pattern` removes the SHORTEST matching suffix. When the edited file's
absolute path contained the literal substring `/docs/loom/memory/` more
than once — which happens exactly when someone nests a duplicate `docs/
loom/memory` subtree INSIDE the real store (the very `nested-document`
abuse the hook's own docstring says `validate` exists to catch) — the
shortest-suffix match anchored on the LAST occurrence, so `REPO_ROOT`
resolved to a subdirectory of the true repository root (the store
directory itself, not its ancestor).

The hook then built `VALIDATOR="$REPO_ROOT/loom-workflow/skills/loom-
memory/scripts/loom_memory.py"` from that wrong root. The path didn't
exist there, so `[ -f "$VALIDATOR" ] || exit 0` took the "validator
absent, portable store, harmless no-op" branch documented for a repo that
never shipped `loom-workflow` at all — except the real validator DID
exist, one level up, and the real store WAS invalid (proven directly
against `loom_memory.py validate`). The hook silently reported success on
a genuinely broken store.

The fix swaps the strip to `%%` (LONGEST-suffix removal), which anchors on
the FIRST occurrence of `/docs/loom/memory/` instead — always the true repo
boundary, however many times the rest of the path repeats the store's own
marker segment.

Run:
    PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
        docs/loom/2026-09-11-loom-memory-into-loom-workflow/evidence/probes/test_adversarial_hook_fail_open_duplicate_path_segment.py -v -s
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
REAL_VALIDATOR = REPO_ROOT / "loom-workflow" / "skills" / "loom-memory" / "scripts" / "loom_memory.py"
REAL_HOOK = REPO_ROOT / ".claude" / "hooks" / "check-memory-store-integrity.sh"


def _build_repo_with_broken_store_and_duplicate_path(root: Path) -> tuple[Path, Path]:
    """Build a synthetic repo carrying the real validator at its correct,
    canonical relative location, a genuinely broken top-level store entry,
    and a nested duplicate `docs/loom/memory` subtree inside the store —
    the exact abuse the hook's docstring calls out as `validate`'s job to
    catch. Returns (repo_root, nested_duplicate_file)."""
    scripts_dir = root / "loom-workflow" / "skills" / "loom-memory" / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy2(REAL_VALIDATOR, scripts_dir / "loom_memory.py")

    store = root / "docs" / "loom" / "memory"
    store.mkdir(parents=True)
    # A genuinely broken concept: missing description/type/sources.
    (store / "bad.md").write_text(
        "---\nname: bad\n---\nMissing required frontmatter fields.\n",
        encoding="utf-8",
    )
    (store / "README.md").write_text(
        "---\n"
        "name: README\n"
        "description: test store guide\n"
        "type: Memory Store Guide\n"
        "sources:\n"
        "  - resource: introducing commit "
        + "0" * 40
        + "\n---\nCharter text.\n",
        encoding="utf-8",
    )

    nested = store / "docs" / "loom" / "memory"
    nested.mkdir(parents=True)
    nested_file = nested / "evil.md"
    nested_file.write_text(
        "---\n"
        "name: evil\n"
        "description: nested duplicate path abuse\n"
        "type: Memory\n"
        "sources:\n"
        "  - resource: introducing commit "
        + "0" * 40
        + "\n---\nNested body.\n",
        encoding="utf-8",
    )
    return root, nested_file


def test_validate_directly_confirms_the_store_is_genuinely_broken(tmp_path):
    """Control: run the real validator directly against the real store
    path, bypassing the hook entirely, to prove the store built above is
    an actual invariant violation — not an artifact of this probe."""
    root, _nested_file = _build_repo_with_broken_store_and_duplicate_path(tmp_path)
    store = root / "docs" / "loom" / "memory"
    validator = root / "loom-workflow" / "skills" / "loom-memory" / "scripts" / "loom_memory.py"

    result = subprocess.run(
        ["python3", str(validator), "validate", str(store)],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode != 0
    assert "description" in result.stdout
    assert "nested-document" in result.stdout


def test_hook_exits_two_on_a_broken_store_when_edited_path_repeats_the_store_marker(tmp_path):
    """The former attack, now closed: invoke the real hook script,
    unmodified, as the host harness would — JSON on stdin naming the
    nested duplicate file as the just-edited `file_path` — and show it now
    reaches the real validator and reports the violation (exit 2, naming
    the offenders), instead of silently no-opping."""
    root, nested_file = _build_repo_with_broken_store_and_duplicate_path(tmp_path)

    payload = json.dumps({"tool_input": {"file_path": str(nested_file)}})
    result = subprocess.run(
        ["bash", str(REAL_HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 2, (
        f"expected the fixed longest-suffix strip to reach the real "
        f"validator (exit 2); got {result.returncode}, stderr={result.stderr!r}"
    )
    assert "loom memory-store integrity violated" in result.stderr
    assert "nested-document" in result.stderr
    assert "bad.md" in result.stderr


def test_hook_exits_two_on_the_same_broken_store_via_the_top_level_file(tmp_path):
    """Control: the SAME broken repo, but the edited path is the ordinary
    top-level `bad.md` (no duplicated store-marker segment). REPO_ROOT
    resolves correctly, the real validator is found, and the hook reports
    the violation as designed — isolating the (now-fixed) defect to the
    duplicate-path-segment computation, not to the store or validator."""
    root, _nested_file = _build_repo_with_broken_store_and_duplicate_path(tmp_path)
    ordinary_file = root / "docs" / "loom" / "memory" / "bad.md"

    payload = json.dumps({"tool_input": {"file_path": str(ordinary_file)}})
    result = subprocess.run(
        ["bash", str(REAL_HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stderr
    assert "loom memory-store integrity violated" in result.stderr
