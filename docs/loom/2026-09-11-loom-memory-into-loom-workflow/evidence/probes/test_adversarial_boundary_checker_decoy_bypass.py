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

The hardened `_sibling_plugin_exists` still hardcodes the FLAT install
shape (`<plugin>/.claude-plugin/plugin.json` directly beside `root`). This
repo's own boundary-checker suite
(`test_manifest_name_identifies_plugin_inside_versioned_install_root`)
proves a plugin is also installed one level deeper, under a version
directory: `<plugin>/<version>/`. When BOTH the scanned plugin and its real
sibling are installed in that shape, the sibling genuinely exists — with a
real manifest and a real private file — one level below where
`_sibling_plugin_exists` looks, so it returns `False`. Detection then falls
through to the bare `root/skills/<plugin>/` existence check, which a decoy
shipped at that exact path satisfies regardless of content: the exact same
class of bypass the hardening was meant to close, now gated behind the
versioned-install layout instead of the flat one.

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


def test_boundary_checker_versioned_install_decoy_still_bypasses_sibling_detection(tmp_path):
    """The surviving gap: both plugins installed in the versioned shape
    this repo's own suite proves is real (`<plugin>/<version>/`). The real
    sibling — genuine manifest, genuine private `hooks/family-relay.md` —
    sits one level below where `_sibling_plugin_exists` looks
    (`root.parent/<plugin>/.claude-plugin/plugin.json` assumes the FLAT
    shape), so it is not detected as a real sibling at all. A same-named
    decoy planted at our own `skills/loom-code/hooks/family-relay.md` then
    clears the check purely by existing there — the reference to what LOOKS
    like the real sibling's private hook is never flagged."""
    plugin_root = tmp_path / "loom-design" / "0.4.0"
    _write_manifest(plugin_root, "loom-design")

    sibling_root = tmp_path / "loom-code" / "0.9.0"
    _write_manifest(sibling_root, "loom-code")
    _write(sibling_root / "hooks" / "family-relay.md", "real sibling private hook\n")

    assert checker._sibling_plugin_exists(plugin_root, "loom-code") is False, (
        "fixture assumption broken: the versioned sibling is now detected; "
        "this probe no longer exercises the layout mismatch and must be revised"
    )

    _write(
        plugin_root / "skills" / "loom-code" / "hooks" / "family-relay.md",
        "decoy content, unrelated to the real sibling hook\n",
    )
    _write(
        plugin_root / "skills" / "router" / "SKILL.md",
        "Read `skills/loom-code/hooks/family-relay.md` before dispatch.\n",
    )

    violations = checker.find_boundary_violations(plugin_root)

    assert violations == [], (
        "expected the versioned-install decoy to defeat sibling detection "
        "(this documents the surviving bypass); if this now fails, "
        "_sibling_plugin_exists has been made layout-aware"
    )
