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
  anywhere. A scaffold write therefore proves nothing on its own.

  What this script can check alone is only half of that: ``--self-test``
  runs the copied shim directly and requires the checker's own verdict,
  ``BLOCK push.`` on stderr. That proves the copy RUNS — nothing about
  whether Codex trusts it, because Codex' trust decision is not in the loop
  of a subprocess this script spawns itself. Reading it as proof of a live
  gate is exactly what let a Codex session walk a whole station with no gate
  at all (W4-02 finding F2). The real probe belongs to the station: it
  issues a doomed ``git push`` as an ordinary tool call and reads who
  answered — the checker, or git.

  "Blocked" is a specific answer, not merely a non-zero exit. A checker that
  crashes also exits non-zero, and calling that a live safety belt is the
  other half of the same failure — so it is reported separately, as a broken
  gate rather than a dead one.

  The shim also records its own firing in ``.codex/hooks/.loom-hook-fired``,
  so ``--trusted`` can answer "has Codex ever run this hook here?" with no
  tool call at all. The marker is gitignored: it is local evidence about
  this machine's trust state, not repository content.

The copy is a package, not a file: the checker imports ``git_exec`` and reads
its contract manifest, so the scaffold ships both beside it. A copy that
cannot import its own sibling is a hook that fails on every command.

Fail-closed: any error exits 2.

Usage::

    codex_scaffold.py [--repo PATH]     # write (idempotent); prints commit subject
    codex_scaffold.py [--repo PATH] --self-test   # the copied checker runs
    codex_scaffold.py [--repo PATH] --trusted     # has the hook ever fired here?

The script never commits; the caller does.
"""
from __future__ import annotations

import argparse
import errno
import json
import os
import subprocess
import sys
from pathlib import Path

SELF_TEST_FAILED = (
    "BLOCK: the copied loom checker did not block a fake push — the scaffold "
    "is broken; re-run codex_scaffold.py --repo . and commit the result"
)
NOT_TRUSTED_MESSAGE = (
    "BLOCK: loom hooks have never fired in this repo — "
    "run /hooks in Codex once, then retry"
)
SANDBOX_MESSAGE = (
    "BLOCK: Codex' sandbox protects .codex/ — run "
    "`python3 {script} --repo .` once in a terminal outside Codex, commit, "
    "then continue"
)
GATE_BROKEN_PREFIX = "BLOCK: the loom hook ran but did not judge the push"
BLOCK_LINE_PREFIX = "BLOCK push."
STAMP_PREFIX = "# loom-checker "
SHIM_COMMAND = ".codex/hooks/loom-checker"
HOOK_DIR = ".codex/hooks"
MARKER = f"{HOOK_DIR}/.loom-hook-fired"
CHECKER_COPY = f"{HOOK_DIR}/loom_checker.py"
SIBLING_MODULES = ("git_exec.py",)
CONTRACT_COPY = f"{HOOK_DIR}/contract"

# os.path.abspath rather than Path.resolve(): module scope runs at import,
# where nothing can catch an OSError, so it must make no filesystem call.
PLUGIN_ROOT = Path(os.path.abspath(__file__)).parent.parent
PLUGIN_JSON = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
SCRIPTS_SOURCE = PLUGIN_ROOT / "scripts"
CHECKER_SOURCE = SCRIPTS_SOURCE / "loom_checker.py"
CONTRACT_SOURCE = PLUGIN_ROOT / "contract"

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
# Record that Codex' hook engine really invoked this hook. Nothing else can
# observe that: an untrusted hook is skipped in silence. Never fatal — a
# read-only checkout must still get its verdict.
{{ : > "$(dirname "$0")/.loom-hook-fired"; }} 2>/dev/null || true
exec python3 {checker} push --hook
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


def _ignore_marker(repo: Path) -> bool:
    """Append the marker to ``.gitignore`` unless it is already listed.

    The marker says what happened on THIS machine — committing it would
    carry one user's trust state into everyone else's clone."""
    gitignore = repo / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""
    if MARKER in existing.split():
        return False
    prefix = existing if not existing or existing.endswith("\n") else existing + "\n"
    gitignore.write_text(f"{prefix}{MARKER}\n", encoding="utf-8")
    return True


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

    # The checker cannot run alone: it imports its siblings and reads the
    # contract manifest and templates. Ship them next to the copy.
    for name in SIBLING_MODULES:
        source = SCRIPTS_SOURCE / name
        if source.is_file() and _write(
            repo / HOOK_DIR / name, source.read_text(encoding="utf-8")
        ):
            changed.append(f"{HOOK_DIR}/{name}")

    for source in sorted(CONTRACT_SOURCE.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(CONTRACT_SOURCE)
        if _write(repo / CONTRACT_COPY / relative, source.read_text(encoding="utf-8")):
            changed.append(f"{CONTRACT_COPY}/{relative}")

    if _ignore_marker(repo):
        changed.append(".gitignore")

    if not changed:
        print(f"unchanged — loom hooks already scaffolded at {version}")
        return 0

    for name in changed:
        print(f"wrote {name}")
    print(f"suggested commit subject: chore(loom): scaffold hooks {version}")
    print(
        "next: --self-test proves the copy runs; the station's trust probe "
        "(a doomed `git push`, issued as a normal tool call) proves Codex "
        "trusts it, and /hooks is the answer when it does not"
    )
    return 0


def trusted(repo: Path) -> int:
    """Has Codex' hook engine ever run this repo's loom hook on this machine?

    The shim writes the marker on every firing, and only a hook Codex chose
    to run can write it. No marker is not proof of an untrusted hook (a
    fresh clone has simply run no commands yet), but a marker IS proof of a
    trusted one — which is the direction the user-facing message needs."""
    if (repo / MARKER).is_file():
        print("trusted — the loom hook has fired in this repo at least once")
        return 0
    print(NOT_TRUSTED_MESSAGE, file=sys.stderr)
    return 2


def self_test(repo: Path) -> int:
    """Run the copied shim directly; a fake ``git push`` must be blocked.

    Three outcomes, and they are deliberately not one: blocked by a rule
    (the copy works), not blocked at all (the copy is broken or absent), and
    non-zero for some other reason (the gate is broken). Collapsing the last
    two would let a crashing checker read as a working checker.

    What this does NOT establish is trust: Codex is not invoking the hook
    here, this script is. The station's own probe — a doomed ``git push``
    issued as a normal tool call — is the only thing that puts Codex' hook
    engine in the loop, so the passing message says so out loud.
    """
    shim = repo / SHIM_COMMAND
    if not shim.is_file():
        print(SELF_TEST_FAILED, file=sys.stderr)
        return 2

    payload = dict(PROBE_PAYLOAD, cwd=str(repo))
    proc = subprocess.run(
        [str(shim)],
        cwd=str(repo),
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        print(SELF_TEST_FAILED, file=sys.stderr)
        return 2
    if proc.stderr.lstrip().startswith(BLOCK_LINE_PREFIX):
        print(
            "self-test passed — the copied checker blocks a fake push. This "
            "does not prove Codex trusts the hook: run the station's trust "
            "probe for that, and /hooks if it says the hook never fired."
        )
        return 0

    first = next(
        (line for line in (proc.stderr or proc.stdout).splitlines() if line.strip()),
        f"exit {proc.returncode} with no output",
    )
    print(f"{GATE_BROKEN_PREFIX}: {first.strip()}", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=os.getcwd(), help="adopting repo (default: cwd)")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="verify the COPIED checker blocks a fake git push (not that Codex trusts it)",
    )
    parser.add_argument(
        "--trusted",
        action="store_true",
        help="report whether Codex' hook engine has ever fired the loom hook here",
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
        if args.trusted:
            return trusted(repo)
        return self_test(repo) if args.self_test else scaffold(repo)
    except OSError as exc:
        # `--sandbox workspace-write` protects `.codex/` while leaving the
        # rest of the workspace writable, so the scaffold — and only the
        # scaffold — dies here (W4-02 finding F1). A bare errno left the
        # user with a dead end; name the door out instead.
        if exc.errno in (errno.EACCES, errno.EPERM):
            print(SANDBOX_MESSAGE.format(script=os.path.abspath(__file__)), file=sys.stderr)
            return 2
        print(f"loom scaffold failed: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"loom scaffold failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
