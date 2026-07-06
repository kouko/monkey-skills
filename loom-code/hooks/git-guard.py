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
   ``git -C <path> push`` and ``git --git-dir <path> push``),
   ``gh pr create``, ``gh pr merge`` — which require fresh markers
   under ``<git-dir>/loom/`` (git-dir resolved via ``git rev-parse
   --git-dir``, so linked worktrees work; an explicit ``--git-dir`` /
   ``--work-tree`` global flag — both ``--flag value`` and
   ``--flag=value`` forms — is skipped when locating the subcommand,
   and ``--git-dir`` is forwarded to the resolution so the gate reads
   the same repo the push would hit):

   - ``review-pass.json`` — verdict PASS / PASS_WITH_NOTES pinned to
     the current HEAD sha (written after
     loom-code:requesting-code-review).
   - ``verified.json`` — package-level-suite-green marker pinned to
     the current HEAD sha (written after
     loom-code:verification-before-completion).

   Both markers additionally accept a **patch-id fallback**: when a
   marker's ``head_sha`` no longer matches (message-only amend,
   content-preserving rebase) but it carries ``base_sha``/``patch_id``
   fields (written by a patch-id-aware
   ``loom_gate_markers.py``), the gate recomputes the patch-id for the
   CURRENT ``merge-base(default-branch, HEAD)..HEAD`` and accepts the
   marker if it equals the recorded one — content, not commit identity,
   is what is being re-verified. Old-format markers (no patch_id field)
   and any resolution/subprocess error fall back to strict ``head_sha``
   equality (fail-closed).

   All markers (incl. the waiver) must carry ``"schema": 1``; any
   other value makes the marker invalid — the two gate markers then
   block, and an invalid waiver is ignored (not honored, not
   consumed), the marker gates applying instead.

   A one-shot ``waiver.json`` (scope: push) bypasses both marker
   checks exactly once. The guard unlinks it BEFORE honoring it —
   consume-then-allow, never allow-then-maybe-consume — so an
   undeletable waiver (e.g. read-only dir) is treated as absent,
   loudly, and the marker gates still apply (fail-closed against both
   the permanent-bypass and the TOCTOU double-spend).

Escape hatches / fail-open behavior: ``LOOM_CODE_MODE=off`` disables
the guard; non-Bash tools, non-git/gh segments, ``git push
--dry-run`` (and its ``-n`` short form — push's ``-n`` IS dry-run,
unlike commit's), and a cwd outside any git repo are allowed — the
latter includes a bogus ``--git-dir`` (rev-parse fails → not-a-repo
path → ALLOW; safe, because the push itself fails identically against
the same bogus path, so nothing reaches a remote); malformed
stdin or any internal error fails OPEN (exit 0 with a stderr note) —
the guard must never take the session down with it.

Detection splits the command on ``&&`` / ``||`` / ``;`` / ``|`` /
single ``&`` (background) / newlines — multiline commands are routine
in Claude Code — then tokenizes each segment with shlex (naive
whitespace split on shlex errors) and matches on the first
non-env-assignment token — word-boundary, not substring, so
``echo "git push"`` does not trigger. Quoted separators inside strings
are an accepted limitation, and so are heredocs: a heredoc BODY line
beginning ``git push`` is newline-split into a segment and gated — a
false positive we accept because it fails CLOSED (an over-block the
model can rephrase around, never an under-block).

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
    """Split a ``git ...`` argv into (subcommand, sub_args, -C path,
    --git-dir path).

    Value-taking global flags (-C / -c / --git-dir / --work-tree /
    --namespace / --config-env / --attr-source, in both
    ``--flag value`` and ``--flag=value`` forms) are skipped so their
    VALUES are never mistaken for the subcommand. The ``=`` forms are
    single tokens, so all but ``--git-dir=`` (whose value we capture)
    fall through to the generic ``-``-prefix skip.
    """
    c_path = None
    git_dir = None
    i = 1
    while i < len(tokens):
        tok = tokens[i]
        if tok == "-C" and i + 1 < len(tokens):
            c_path = tokens[i + 1]
            i += 2
        elif tok == "--git-dir" and i + 1 < len(tokens):
            git_dir = tokens[i + 1]
            i += 2
        elif tok.startswith("--git-dir="):
            git_dir = tok.split("=", 1)[1]
            i += 1
        elif (
            tok in ("-c", "--work-tree", "--namespace",
                    "--config-env", "--attr-source")
            and i + 1 < len(tokens)
        ):
            i += 2
        elif tok.startswith("-"):
            i += 1
        else:
            return tok, tokens[i + 1:], c_path, git_dir
    return None, [], c_path, git_dir


def _git(args, cwd, git_globals=()):
    return subprocess.run(
        ["git", "-C", cwd, *git_globals, *args],
        capture_output=True,
        text=True,
    )


def _loom_dir(cwd, git_globals=()):
    """Path to <git-dir>/loom, or None when cwd is not inside a repo."""
    res = _git(["rev-parse", "--git-dir"], cwd, git_globals)
    if res.returncode != 0:
        return None
    git_dir = res.stdout.strip()
    if not os.path.isabs(git_dir):
        git_dir = os.path.join(cwd, git_dir)
    return os.path.join(git_dir, "loom")


def _head(cwd, git_globals=()):
    res = _git(["rev-parse", "HEAD"], cwd, git_globals)
    return res.stdout.strip() if res.returncode == 0 else None


def _default_branch_ref(cwd, git_globals=()):
    """Best-effort default-branch ref for merge-base computation, or
    None when none resolve (mirrors loom_gate_markers._default_branch_ref;
    duplicated here since this hook is stdlib-only/dependency-free)."""
    res = _git(["symbolic-ref", "-q", "refs/remotes/origin/HEAD"], cwd, git_globals)
    if res.returncode == 0:
        ref = res.stdout.strip()
        if ref.startswith("refs/remotes/"):
            ref = ref[len("refs/remotes/"):]
        if _git(["rev-parse", "--verify", "-q", ref], cwd, git_globals).returncode == 0:
            return ref
    for candidate in ("main", "master"):
        if _git(["rev-parse", "--verify", "-q", candidate],
                cwd, git_globals).returncode == 0:
            return candidate
    return None


def _current_patch_id(cwd, git_globals=()):
    """Patch-id for merge-base(default-branch, HEAD)..HEAD right now, or
    None on any resolution/subprocess/parse failure (fail-closed)."""
    ref = _default_branch_ref(cwd, git_globals)
    if ref is None:
        return None
    base_res = _git(["merge-base", ref, "HEAD"], cwd, git_globals)
    if base_res.returncode != 0:
        return None
    base_sha = base_res.stdout.strip()
    diff_res = _git(["diff", f"{base_sha}..HEAD"], cwd, git_globals)
    if diff_res.returncode != 0:
        return None
    try:
        pid_res = subprocess.run(
            ["git", "-C", cwd, *git_globals, "patch-id", "--stable"],
            input=diff_res.stdout,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if pid_res.returncode != 0 or not pid_res.stdout.strip():
        return None
    return pid_res.stdout.split()[0]


def _patch_id_matches(marker, cwd, git_globals=()):
    """True iff `marker` carries a patch_id equal to one freshly
    recomputed for the current merge-base(default-branch, HEAD)..HEAD —
    the fail-closed fallback covering message-only amends and
    content-preserving rebases. A missing/non-string field or ANY
    computation error returns False, leaving strict head_sha equality
    as the only path (backward-compatible with old-format markers)."""
    recorded = marker.get("patch_id")
    if not isinstance(recorded, str) or not recorded:
        return False
    current = _current_patch_id(cwd, git_globals)
    return current is not None and current == recorded


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


def _gate_push(cwd, git_globals=()):
    """Marker gate for one push-family segment → (exit_code, stderr_notes)."""
    notes = []
    loom = _loom_dir(cwd, git_globals)
    if loom is None:
        return 0, notes  # not a git repo — nothing to gate
    waiver_path = os.path.join(loom, "waiver.json")
    waiver = _load_json(waiver_path)
    if waiver is not None and waiver.get("schema") == 1:
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
    elif os.path.exists(waiver_path):
        notes.append(
            "loom gate: waiver.json is invalid (unparseable or wrong/"
            "missing schema) — ignored; the marker gates apply"
        )
    head = _head(cwd, git_globals)
    review = _load_json(os.path.join(loom, "review-pass.json"))
    if (
        review is None
        or review.get("schema") != 1
        or review.get("verdict") not in REVIEW_VERDICTS
        or head is None
    ):
        notes.append(MSG_REVIEW)
        return 2, notes
    if review.get("head_sha") != head and not _patch_id_matches(review, cwd, git_globals):
        notes.append(MSG_REVIEW)
        return 2, notes
    verified = _load_json(os.path.join(loom, "verified.json"))
    if verified is None or verified.get("schema") != 1:
        notes.append(MSG_VERIFIED)
        return 2, notes
    if verified.get("head_sha") != head and not _patch_id_matches(verified, cwd, git_globals):
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
        gate_globals = ()
        if toks[0] == "git":
            sub, args, c_path, git_dir = _parse_git(toks)
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
                if git_dir:
                    # Forward --git-dir so the gate resolves the same
                    # repo the push itself would hit (relative paths
                    # resolve against the effective cwd, like git's own
                    # -C-then---git-dir ordering).
                    if not os.path.isabs(git_dir):
                        git_dir = os.path.join(gate_cwd, git_dir)
                    gate_globals = ("--git-dir", git_dir)
        elif (
            toks[0] == "gh"
            and len(toks) >= 3
            and toks[1] == "pr"
            and toks[2] in {"create", "merge"}
        ):
            gate_cwd = cwd
        if gate_cwd is not None:
            code, notes = _gate_push(gate_cwd, gate_globals)
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
