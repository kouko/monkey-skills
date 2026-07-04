#!/usr/bin/env python3
"""PreToolUse guard enforcing loom-code's mechanical git gates.

Claude Code pipes the hook-event JSON (`tool_name`, `tool_input`,
`cwd`) to stdin before every tool call. For Bash commands this guard
blocks two families of gate bypass:

1. ``git commit --no-verify`` (or the ``-n`` short form, incl. inside
   bundled short-option clusters like ``-anm``; commit subcommand
   only) — pre-commit hooks are load-bearing; the flag is refused
   outright.
2. Push-family commands — ``git push`` (any argv shape, incl.
   ``git -C <path> push``), ``gh pr create``, ``gh pr merge`` — which
   require fresh markers under ``<git-dir>/loom/`` (git-dir resolved
   via ``git rev-parse --git-dir``, so linked worktrees work):

   - ``review-pass.json`` — verdict PASS / PASS_WITH_NOTES pinned to
     the current HEAD sha (written after
     loom-code:requesting-code-review).
   - ``verified.json`` — package-level-suite-green marker pinned to
     the current HEAD sha (written after
     loom-code:verification-before-completion).

   A one-shot ``waiver.json`` (scope: push) bypasses both marker
   checks exactly once. The guard unlinks it BEFORE honoring it —
   consume-then-allow, never allow-then-maybe-consume — so an
   undeletable waiver (e.g. read-only dir) is treated as absent,
   loudly, and the marker gates still apply (fail-closed against both
   the permanent-bypass and the TOCTOU double-spend).

Escape hatches / fail-open behavior: ``LOOM_CODE_MODE=off`` disables
the guard; non-Bash tools, non-git/gh segments, ``git push
--dry-run`` (and its ``-n`` short form — push's ``-n`` IS dry-run,
unlike commit's), and a cwd outside any git repo are allowed; malformed
stdin or any internal error fails OPEN (exit 0 with a stderr note) —
the guard must never take the session down with it.

Detection splits the command on ``&&`` / ``||`` / ``;`` / ``|`` /
single ``&`` (background) / newlines — multiline commands are routine
in Claude Code — then tokenizes each segment with shlex (naive
whitespace split on shlex errors) and matches on the first
non-env-assignment token — word-boundary, not substring, so
``echo "git push"`` does not trigger. Quoted separators inside strings
are an accepted limitation.

Exit codes follow the PreToolUse contract: 0 = allow, 2 = block
(stderr shown to the model). Stdlib only.
"""

import json
import os
import re
import shlex
import subprocess
import sys

# Segment separators: ||, &&, ;, |, single & (background — a safe
# superset of &&), and newlines (multiline Bash commands are routine).
SEGMENT_SPLIT = re.compile(r"\|\||&&|;|\||&|\n")
ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
REVIEW_VERDICTS = {"PASS", "PASS_WITH_NOTES"}

MSG_NO_VERIFY = (
    "loom gate: `git commit --no-verify` / `-n` is blocked — pre-commit "
    "hooks are load-bearing in this repo. Drop the flag and let the hooks "
    "run (loom-code gate)."
)
MSG_REVIEW = (
    "loom gate: no fresh review-PASS marker for the current HEAD. Run "
    "loom-code:requesting-code-review to a PASS / PASS_WITH_NOTES verdict "
    "first, or ask the user to waive this push (the orchestrator then "
    "writes the waiver via loom-code/scripts/loom_gate_markers.py)."
)
MSG_VERIFIED = (
    "loom gate: no fresh verification marker for the current HEAD. Run the "
    "package-level test suite green, then write the marker via "
    "loom-code/scripts/loom_gate_markers.py verified."
)


def _tokens(segment):
    """Shell-word tokens of one command segment, leading FOO=bar dropped."""
    try:
        toks = shlex.split(segment)
    except ValueError:
        toks = segment.split()
    while toks and ENV_ASSIGN.match(toks[0]):
        toks.pop(0)
    return toks


def _parse_git(tokens):
    """Split a ``git ...`` argv into (subcommand, sub_args, -C path)."""
    c_path = None
    i = 1
    while i < len(tokens):
        tok = tokens[i]
        if tok == "-C" and i + 1 < len(tokens):
            c_path = tokens[i + 1]
            i += 2
        elif tok == "-c" and i + 1 < len(tokens):
            i += 2
        elif tok.startswith("-"):
            i += 1
        else:
            return tok, tokens[i + 1:], c_path
    return None, [], c_path


def _git(args, cwd):
    return subprocess.run(
        ["git", "-C", cwd, *args], capture_output=True, text=True
    )


def _loom_dir(cwd):
    """Path to <git-dir>/loom, or None when cwd is not inside a repo."""
    res = _git(["rev-parse", "--git-dir"], cwd)
    if res.returncode != 0:
        return None
    git_dir = res.stdout.strip()
    if not os.path.isabs(git_dir):
        git_dir = os.path.join(cwd, git_dir)
    return os.path.join(git_dir, "loom")


def _head(cwd):
    res = _git(["rev-parse", "HEAD"], cwd)
    return res.stdout.strip() if res.returncode == 0 else None


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def _has_no_verify(args):
    """True when commit args carry --no-verify or -n (incl. bundled -anm)."""
    for tok in args:
        if tok == "--no-verify":
            return True
        if re.fullmatch(r"-[a-zA-Z]+", tok) and "n" in tok:
            return True
    return False


def _gate_push(cwd):
    """Marker gate for one push-family segment → (exit_code, stderr_notes)."""
    notes = []
    loom = _loom_dir(cwd)
    if loom is None:
        return 0, notes  # not a git repo — nothing to gate
    waiver_path = os.path.join(loom, "waiver.json")
    if os.path.exists(waiver_path):
        waiver = _load_json(waiver_path) or {}
        reason = str(waiver.get("reason", "no reason recorded"))
        # Unlink FIRST: a waiver only counts once it is provably consumed.
        try:
            os.unlink(waiver_path)
        except FileNotFoundError:
            pass  # raced away — no waiver to honor; fall through to markers
        except OSError:
            notes.append(
                "loom gate: waiver could NOT be deleted — treating it as "
                "absent and applying the marker gates (fail-closed)"
            )
        else:
            return 0, [f"loom gate: waiver consumed ({reason})"]
    head = _head(cwd)
    review = _load_json(os.path.join(loom, "review-pass.json"))
    if (
        review is None
        or review.get("verdict") not in REVIEW_VERDICTS
        or head is None
        or review.get("head_sha") != head
    ):
        notes.append(MSG_REVIEW)
        return 2, notes
    verified = _load_json(os.path.join(loom, "verified.json"))
    if verified is None or verified.get("head_sha") != head:
        notes.append(MSG_VERIFIED)
        return 2, notes
    return 0, notes


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except ValueError:
        print("loom git-guard: malformed hook input; fail-open", file=sys.stderr)
        return 0
    if not isinstance(payload, dict):
        print("loom git-guard: malformed hook input; fail-open", file=sys.stderr)
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    if os.environ.get("LOOM_CODE_MODE") == "off":
        return 0
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not command.strip():
        return 0
    cwd = payload.get("cwd") or os.getcwd()

    for segment in SEGMENT_SPLIT.split(command):
        toks = _tokens(segment)
        if not toks:
            continue
        gate_cwd = None
        if toks[0] == "git":
            sub, args, c_path = _parse_git(toks)
            if sub == "commit" and _has_no_verify(args):
                print(MSG_NO_VERIFY, file=sys.stderr)
                return 2
            # push's -n means --dry-run (unlike commit's -n = --no-verify)
            if sub == "push" and "--dry-run" not in args and "-n" not in args:
                gate_cwd = cwd
                if c_path:
                    gate_cwd = (
                        c_path
                        if os.path.isabs(c_path)
                        else os.path.join(cwd, c_path)
                    )
        elif (
            toks[0] == "gh"
            and len(toks) >= 3
            and toks[1] == "pr"
            and toks[2] in {"create", "merge"}
        ):
            gate_cwd = cwd
        if gate_cwd is not None:
            code, notes = _gate_push(gate_cwd)
            for note in notes:
                print(note, file=sys.stderr)
            if code != 0:
                return code
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # never crash the session — fail open
        print(f"loom git-guard: internal error ({exc}); fail-open", file=sys.stderr)
        sys.exit(0)
