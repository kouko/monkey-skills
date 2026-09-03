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
  this machine's trust state, not repository content. It records firings by
  Codex only — ``--self-test`` spawns the same shim with ``LOOM_SELF_TEST``
  set, which suppresses the write, because a marker this script produced
  would make ``--trusted`` vouch for a trust decision nobody made.

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

SELF_TEST_ENV = "LOOM_SELF_TEST"
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
NOT_EXECUTABLE_MESSAGE = (
    "BLOCK: the loom hook shim is not executable — re-run the scaffold "
    "(`codex_scaffold.py --repo .`) or `chmod +x {shim}`"
)
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
# read-only checkout must still get its verdict. LOOM_SELF_TEST marks the
# one caller that is NOT Codex' hook engine — codex_scaffold.py --self-test
# spawns this shim itself, and a marker written then would let --trusted
# report a trust decision Codex never made.
if [ -z "${{LOOM_SELF_TEST:-}}" ]; then
  {{ : > "$(dirname "$0")/.loom-hook-fired"; }} 2>/dev/null || true
fi
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


def _merged_hooks_json(path: Path) -> dict:
    """Merge loom's PreToolUse Bash entry into ``path``'s existing content.

    PRINCIPLES.md non-negotiable 5: existing data is never rewritten
    without asking. An adopting repo may already have its own hooks (this
    repo's PostToolUse block was destroyed wholesale by an earlier version
    of this script, R22-O2) — every other event and matcher is left alone,
    and loom's own entry is added at most once. Unparseable content is a
    hard stop, not a silent overwrite."""
    if not path.is_file():
        return json.loads(json.dumps(HOOKS_JSON))

    text = path.read_text(encoding="utf-8")
    try:
        existing = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON — refusing to overwrite it: {exc}") from exc
    if not isinstance(existing, dict):
        raise ValueError(f"{path} has no top-level JSON object — refusing to overwrite it")

    hooks = existing.setdefault("hooks", {})
    pre_tool_use = hooks.setdefault("PreToolUse", [])
    already_present = any(
        isinstance(entry, dict)
        and entry.get("matcher") == "Bash"
        and any(
            isinstance(hook, dict) and hook.get("command") == SHIM_COMMAND
            for hook in entry.get("hooks", [])
        )
        for entry in pre_tool_use
    )
    if not already_present:
        pre_tool_use.append(
            {"matcher": "Bash", "hooks": [{"type": "command", "command": SHIM_COMMAND}]}
        )
    return existing


def _write(path: Path, content: str, executable: bool = False) -> str:
    """Install ``content`` at ``path``; return what had to be done.

    ``""`` when the file was already installed, ``"wrote"`` when the
    content changed, ``"repaired mode"`` when the content already matched
    but the executable bit was missing. The third case is not cosmetic: a
    shim that cannot be executed is a dead gate, and reporting it as
    ``unchanged`` would say the hook is installed when it cannot run."""
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        if executable and not path.stat().st_mode & 0o111:
            path.chmod(path.stat().st_mode | 0o755)
            return "repaired mode"
        return ""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | 0o755)
    return "wrote"


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
    changed: list[tuple[str, str]] = []

    def record(action: str, name: str) -> None:
        if action:
            changed.append((action, name))

    hooks_json_path = repo / ".codex" / "hooks.json"
    merged_hooks_json = _merged_hooks_json(hooks_json_path)
    record(
        _write(hooks_json_path, json.dumps(merged_hooks_json, indent=2) + "\n"),
        ".codex/hooks.json",
    )

    shim = repo / SHIM_COMMAND
    record(
        _write(
            shim,
            SHIM_TEMPLATE.format(stamp=stamp_line(version), checker=CHECKER_COPY),
            executable=True,
        ),
        SHIM_COMMAND,
    )

    copy = _checker_copy_content(version)
    if copy is not None:
        record(_write(repo / CHECKER_COPY, copy), CHECKER_COPY)

    # The checker cannot run alone: it imports its siblings and reads the
    # contract manifest and templates. Ship them next to the copy.
    for name in SIBLING_MODULES:
        source = SCRIPTS_SOURCE / name
        if source.is_file():
            record(
                _write(repo / HOOK_DIR / name, source.read_text(encoding="utf-8")),
                f"{HOOK_DIR}/{name}",
            )

    for source in sorted(CONTRACT_SOURCE.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(CONTRACT_SOURCE)
        record(
            _write(repo / CONTRACT_COPY / relative, source.read_text(encoding="utf-8")),
            f"{CONTRACT_COPY}/{relative}",
        )

    if _ignore_marker(repo):
        record("wrote", ".gitignore")

    if not changed:
        print(f"unchanged — loom hooks already scaffolded at {version}")
        return 0

    for action, name in changed:
        print(f"{action} {name}")
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

    Which is also why the run must leave no trust marker behind: the shim
    reads ``LOOM_SELF_TEST`` and skips writing it, and anything that slips
    through anyway is deleted here, because a marker this run created would
    make ``--trusted`` report a decision Codex never made.
    """
    shim = repo / SHIM_COMMAND
    if not shim.is_file():
        print(SELF_TEST_FAILED, file=sys.stderr)
        return 2

    marker = repo / MARKER
    marker_before = marker.is_file()
    payload = dict(PROBE_PAYLOAD, cwd=str(repo))
    try:
        proc = subprocess.run(
            [str(shim)],
            cwd=str(repo),
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            env=dict(os.environ, **{SELF_TEST_ENV: "1"}),
        )
    except PermissionError:
        # The shim survived a copy that dropped its mode bits — a distinct
        # dead end from the sandbox one, and it has its own door out.
        print(NOT_EXECUTABLE_MESSAGE.format(shim=SHIM_COMMAND), file=sys.stderr)
        return 2
    finally:
        if not marker_before and marker.is_file():
            marker.unlink()

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


def _scaffold_or_sandbox(repo: Path) -> int:
    """``scaffold`` with the sandbox dead end named.

    `--sandbox workspace-write` protects `.codex/` while leaving the rest of
    the workspace writable, so the scaffold's own writes — and only those —
    die on EACCES there (W4-02 finding F1). A bare errno left the user with
    a dead end; name the door out instead. Scoped this tightly on purpose:
    when the whole CLI wore this handler, a shim that had merely lost its
    executable bit was reported as a sandbox the user cannot leave."""
    try:
        return scaffold(repo)
    except OSError as exc:
        if exc.errno in (errno.EACCES, errno.EPERM):
            print(SANDBOX_MESSAGE.format(script=os.path.abspath(__file__)), file=sys.stderr)
            return 2
        raise


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
        return self_test(repo) if args.self_test else _scaffold_or_sandbox(repo)
    except OSError as exc:
        print(f"loom scaffold failed: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"loom scaffold failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
