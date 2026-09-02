#!/usr/bin/env python3
"""Scaffold loom's deterministic layer into a repo for Codex CLI (concept-model §7a).

Claude Code gets the layer from plugin hooks with zero user action. Codex has
no plugin-level equivalent that a repo can rely on, so the hook definition and
a checker copy live inside the adopting repo, and the user trusts them once
with ``/hooks``.

Two live-tested facts shape this script
(docs/loom/2026-09-02-simple-loom-flow/evidence/q4-codex-hooks-live-test.md):

* run E — Codex binds trust to the hook DEFINITION, not to the script bytes.
  So ``.codex/hooks.json`` carries a fixed relative, version-free command
  (``.codex/hooks/loom-checker``) and the version stamp lives INSIDE the
  copied files. An upgrade rewrites only the copies, and the user is never
  asked to re-trust. (The flip side, also run E: an agent on a working branch
  can rewrite the copied checker and it still runs as trusted — this layer
  stops slips, not a determined agent (§0). Repos that need more compare the
  checker digest against main in CI.)
* run C — an untrusted hook is skipped SILENTLY in ``codex exec``: no warning
  anywhere. A scaffold write therefore proves nothing on its own, so
  ``--probe`` fires a command that MUST be blocked. Not blocked means the
  safety belt is absent, and the answer is a BLOCK naming ``/hooks`` — never
  a warning the session can walk past.

Fail-closed: any error exits 2.

Usage::

    codex_scaffold.py [--repo PATH]     # write (idempotent); prints commit subject
    codex_scaffold.py [--repo PATH] --probe   # verify the belt is live

The script never commits; the caller does.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

BLOCK_MESSAGE = (
    "BLOCK: loom hooks are not trusted in this repo yet — "
    "run /hooks in Codex once, then retry"
)
STAMP_PREFIX = "# loom-checker "
SHIM_COMMAND = ".codex/hooks/loom-checker"
CHECKER_COPY = ".codex/hooks/loom_checker.py"

# os.path.abspath rather than Path.resolve(): module scope runs at import,
# where nothing can catch an OSError, so it must make no filesystem call.
PLUGIN_ROOT = Path(os.path.abspath(__file__)).parent.parent
PLUGIN_JSON = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CHECKER_SOURCE = PLUGIN_ROOT / "scripts" / "loom_checker.py"

HOOKS_JSON = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [{"type": "command", "command": SHIM_COMMAND}],
            }
        ]
    }
}

SHIM_TEMPLATE = """#!/usr/bin/env bash
{stamp}
# Written by loom-code/scripts/codex_scaffold.py — do not edit by hand.
# The version stamp lives here, never in .codex/hooks.json: Codex binds hook
# trust to the definition, so the command string must never change.
set -euo pipefail
exec python3 {checker} push
"""

PROBE_PAYLOAD = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "git push origin HEAD"},
    "cwd": "",
    "permission_mode": "default",
}


def plugin_version() -> str:
    return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]


def stamp_line(version: str) -> str:
    return f"{STAMP_PREFIX}{version}"


def _write(path: Path, content: str, executable: bool = False) -> bool:
    """Write ``content`` if it differs; return True when the file changed."""
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | 0o755)
    return True


def _checker_copy_content(version: str) -> str | None:
    """The checker source with a version stamp inserted, or None if absent."""
    if not CHECKER_SOURCE.is_file():
        return None
    lines = CHECKER_SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)
    at = 1 if lines and lines[0].startswith("#!") else 0
    lines.insert(at, stamp_line(version) + "\n")
    return "".join(lines)


def scaffold(repo: Path) -> int:
    version = plugin_version()
    changed: list[str] = []

    if _write(repo / ".codex" / "hooks.json", json.dumps(HOOKS_JSON, indent=2) + "\n"):
        changed.append(".codex/hooks.json")

    shim = repo / SHIM_COMMAND
    if _write(
        shim,
        SHIM_TEMPLATE.format(stamp=stamp_line(version), checker=CHECKER_COPY),
        executable=True,
    ):
        changed.append(SHIM_COMMAND)

    copy = _checker_copy_content(version)
    if copy is not None and _write(repo / CHECKER_COPY, copy):
        changed.append(CHECKER_COPY)

    if not changed:
        print(f"unchanged — loom hooks already scaffolded at {version}")
        return 0

    for name in changed:
        print(f"wrote {name}")
    print(f"suggested commit subject: chore(loom): scaffold hooks {version}")
    print("run /hooks in Codex once to trust the hook, then re-run with --probe")
    return 0


def probe(repo: Path) -> int:
    """Run the shim the way Codex would; a fake ``git push`` must be blocked."""
    shim = repo / SHIM_COMMAND
    if not shim.is_file():
        print(BLOCK_MESSAGE, file=sys.stderr)
        return 2

    payload = dict(PROBE_PAYLOAD, cwd=str(repo))
    proc = subprocess.run(
        [str(shim)],
        cwd=str(repo),
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 2:
        print(BLOCK_MESSAGE, file=sys.stderr)
        return 2
    print("probe blocked the fake push — the loom gate is live")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=os.getcwd(), help="adopting repo (default: cwd)")
    parser.add_argument(
        "--probe",
        action="store_true",
        help="verify a fake git push is blocked; exit 2 with a BLOCK message if not",
    )
    args = parser.parse_args(argv)

    # Fail-closed at the CLI boundary: an unreadable path, a malformed
    # plugin.json or any other OSError leaves the caller with one actionable
    # line and exit 2 — never a traceback and never an exit 0.
    try:
        repo = Path(args.repo).resolve()
        if not repo.is_dir():
            print(f"loom scaffold: no such repo: {repo}", file=sys.stderr)
            return 2
        return probe(repo) if args.probe else scaffold(repo)
    except Exception as exc:
        print(f"loom scaffold failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
