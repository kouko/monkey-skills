"""W1-03 — the committed Codex mirror of the checker matches the source.

``.codex/hooks/loom_checker.py`` is the checker Codex actually runs (via the
scaffolded shim); ``loom-code/scripts/loom_checker.py`` is the Claude Code
source of truth. ``codex_scaffold.py`` is the only legal way to write the
mirror (docs/loom/2026-09-04-checker-seams/intent.md #6) — it inserts exactly
one version-stamp line (``# loom-checker <version>``) right after the
checker's shebang line and otherwise copies the source byte for byte
(``codex_scaffold.py::_checker_copy_content``). A committed mirror that
diverges anywhere else means someone hand-edited it, or it was never
refreshed after the source changed — either way Codex is running stale or
tampered logic.

This test reads the two committed files directly (no scaffold invocation,
no temp repo): it is a drift gate on what is actually checked in, not a
behavioural test of the scaffold script (that lives in
test_codex_scaffold.py).
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER_SOURCE = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
CHECKER_MIRROR = REPO_ROOT / ".codex" / "hooks" / "loom_checker.py"
STAMP_PREFIX = "# loom-checker "


def test_mirror_is_the_source_with_exactly_one_stamp_line_inserted():
    source_lines = CHECKER_SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)
    mirror_lines = CHECKER_MIRROR.read_text(encoding="utf-8").splitlines(keepends=True)

    assert len(mirror_lines) == len(source_lines) + 1, (
        "the mirror must be the source plus exactly one inserted stamp line — "
        f"source has {len(source_lines)} lines, mirror has {len(mirror_lines)}"
    )

    at = 1 if source_lines and source_lines[0].startswith("#!") else 0
    stamped_line = mirror_lines[at]
    assert stamped_line.startswith(STAMP_PREFIX), (
        f"expected the inserted line at index {at} to start with {STAMP_PREFIX!r}, "
        f"got {stamped_line!r}"
    )

    rebuilt = mirror_lines[:at] + mirror_lines[at + 1 :]
    assert rebuilt == source_lines, (
        "removing the stamp line from the mirror must reproduce the source "
        "byte for byte — the mirror has drifted from loom_checker.py and "
        "needs `python3 loom-code/scripts/codex_scaffold.py --repo .`"
    )


def test_mirror_stamp_version_matches_plugin_manifest():
    import json

    plugin_manifest = REPO_ROOT / "loom-code" / ".claude-plugin" / "plugin.json"
    manifest_version = json.loads(plugin_manifest.read_text(encoding="utf-8"))["version"]

    mirror_lines = CHECKER_MIRROR.read_text(encoding="utf-8").splitlines()
    at = 1 if mirror_lines and mirror_lines[0].startswith("#!") else 0
    stamped_line = mirror_lines[at]
    assert stamped_line == f"{STAMP_PREFIX}{manifest_version}", (
        f"mirror stamp is {stamped_line!r}, expected {STAMP_PREFIX}{manifest_version!r} — "
        "re-run `python3 loom-code/scripts/codex_scaffold.py --repo .`"
    )
