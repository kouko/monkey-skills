"""Adversarial probe (surface 1): `check_plugin_boundaries._is_internal_path`.

`_is_internal_path` (scripts/check_plugin_boundaries.py) exempts a
`loom-*`-shaped reference from the sibling-boundary check when it names
this plugin's OWN skill folder rather than a real sibling plugin's private
tree — added so `loom-workflow` can ship a same-named `loom-memory` skill
without the generic sibling-name regex mistaking it for the retired
`loom-memory` plugin.

An earlier version of this function decided "internal" purely by whether
*something* existed at the matched relative path inside the scanned
plugin's own root — no check that it was really that plugin's own skill
folder. This probe's first case (`test_...flat_layout_decoy_is_now_rejected`)
reproduced that decoy exactly and confirmed the bypass; mid-session the
function was hardened, in the same working tree, to require the target
resolve under `root/skills/<plugin>/` AND to refuse the exemption outright
whenever a real sibling plugin of that name exists on disk
(`_sibling_plugin_exists`), checked at `root.parent/<plugin>/.claude-
plugin/plugin.json`. That first case is now a passing control, kept to
prove the flat-layout decoy is genuinely closed.

`_sibling_plugin_exists` used to hardcode the FLAT install shape
(`<plugin>/.claude-plugin/plugin.json` directly beside `root`). This repo's
own boundary-checker suite
(`test_manifest_name_identifies_plugin_inside_versioned_install_root`)
proves a plugin is also installed one level deeper, under a version
directory: `<plugin>/<version>/`. When BOTH the scanned plugin and its real
sibling were installed in that shape, the sibling genuinely existed — with a
real manifest and a real private file — one level below where
`_sibling_plugin_exists` looked, so it returned `False`, and a same-named
decoy at the bare `root/skills/<plugin>/` path slipped through undetected —
the exact same class of bypass the flat-layout hardening was meant to
close, gated behind the versioned-install layout instead. `_sibling_plugin_
exists` now also checks one level below the sibling's base directory for a
`.claude-plugin/plugin.json`, so the versioned-install sibling is found and
the decoy is flagged like any other.

Run:
    PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
        docs/loom/2026-09-11-loom-memory-into-loom-workflow/evidence/probes/test_adversarial_boundary_checker_decoy_bypass.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_plugin_boundaries as checker  # noqa: E402


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _write_manifest(root: Path, name: str) -> None:
    _write(root / ".claude-plugin" / "plugin.json", json.dumps({"name": name}))


def test_boundary_checker_flat_layout_decoy_is_now_rejected(tmp_path):
    """Control: the flat-layout decoy — a plugin shipping an unrelated file
    at the exact relative path of a real sibling's genuinely private
    script — no longer clears the check now that a real sibling with a
    manifest is checked first. Confirms the mid-session hardening actually
    holds for the layout it targeted."""
    plugin = tmp_path / "loom-workflow"
    sibling = tmp_path / "loom-code"
    _write_manifest(sibling, "loom-code")
    _write(sibling / "scripts" / "private_check.py", "# real sibling private script\n")

    # Decoy: unrelated content at the identical relative path, inside our
    # own root.
    _write(plugin / "loom-code" / "scripts" / "private_check.py", "# decoy\n")
    source = _write(
        plugin / "skills" / "loom-memory" / "SKILL.md",
        "Run `loom-code/scripts/private_check.py` to cross-check a citation.\n",
    )

    violations = checker.find_boundary_violations(plugin)

    assert violations == [
        f"{source}:1: sibling internal path: loom-code/scripts/private_check.py",
    ], "expected the flat-layout decoy fix to hold; if this fails, the fix regressed"


def test_boundary_checker_versioned_install_decoy_no_longer_bypasses_sibling_detection(tmp_path):
    """The closed gap: both plugins installed in the versioned shape this
    repo's own suite proves is real (`<plugin>/<version>/`). The real
    sibling — genuine manifest, genuine private `hooks/family-relay.md` —
    sits one level below the sibling's base directory
    (`root.parent/<plugin>/<version>/.claude-plugin/plugin.json`), and
    `_sibling_plugin_exists` now checks that depth too, so it is detected as
    a real sibling. A same-named decoy planted at our own
    `skills/loom-code/hooks/family-relay.md` therefore no longer clears the
    check by merely existing there — the reference is flagged like any
    other sibling-internal path."""
    plugin_root = tmp_path / "loom-design" / "0.4.0"
    _write_manifest(plugin_root, "loom-design")

    sibling_root = tmp_path / "loom-code" / "0.9.0"
    _write_manifest(sibling_root, "loom-code")
    _write(sibling_root / "hooks" / "family-relay.md", "real sibling private hook\n")

    assert checker._sibling_plugin_exists(plugin_root, "loom-code") is True, (
        "fixture assumption broken: the versioned sibling is no longer "
        "detected; this probe no longer exercises the fixed layout and "
        "must be revised"
    )

    decoy = _write(
        plugin_root / "skills" / "loom-code" / "hooks" / "family-relay.md",
        "decoy content, unrelated to the real sibling hook\n",
    )
    source = _write(
        plugin_root / "skills" / "router" / "SKILL.md",
        "Read `skills/loom-code/hooks/family-relay.md` before dispatch.\n",
    )

    violations = checker.find_boundary_violations(plugin_root)

    assert violations == [
        f"{source}:1: sibling internal path: skills/loom-code/hooks/family-relay.md",
    ], violations
    assert decoy.is_file()
