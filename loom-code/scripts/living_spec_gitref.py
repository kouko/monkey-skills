"""Resolve a living-spec binding's body + @req-line to git commits.

A binding (from ``living_spec_tags.locate_bindings``, enriched with a
``file`` key by the collector) names two independent 1-based line ranges
in one file: the enclosing test's body ``[body_start, body_end]`` and the
single ``@req`` line ``[binding_line, binding_line]``. The comparator
(Task 1) needs, for each range, the most-recent commit that touched it.

The importable entry point is
``resolve_binding_refs(binding, repo_root) -> dict | None``, returning
the binding ENRICHED with ``body_ref`` / ``body_ts`` (SHA + committer
epoch of the body range's last commit) and ``binding_ref`` /
``binding_ts`` (same for the ``@req`` line). The two ranges are resolved
with TWO separate ``git log -L`` calls — robust even when
``binding_line`` falls outside the body range (an inherited edge from
nearest-test attribution).

When either range has NO committed history yet (a net-new tagged test
in the working tree whose path is not in HEAD, or an uncommitted edit
pushing the range past HEAD's committed file length), ``git log -L``
exits 128 with a recognizable "no committed baseline" signature. That
is NOT a git failure — there is simply nothing to drift from yet — so
``resolve_binding_refs`` returns ``None`` (the binding is unresolvable
and the advisory WARN lane skips it). Any OTHER git failure (missing
binary, corrupt repo, unexpected exit) still raises, so a genuinely
broken setup fails loud.

Pure stdlib (``subprocess`` shelling out to the ``git`` CLI; no
third-party git library).
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

# Force git's C locale so its stderr is English regardless of the host's
# installed git.mo translations — the "no committed baseline" signatures
# below are matched as substrings, so a localized runner must NOT be able
# to translate them out from under the match (which would re-regress the
# "WARN never fails the build" invariant). Pin both LC_ALL and LANG.
_C_LOCALE_ENV = {**os.environ, "LC_ALL": "C", "LANG": "C"}


# git exit-128 stderr signatures meaning "this range has no committed
# baseline yet" — an EXPECTED, non-error condition (uncommitted tagged
# test / uncommitted edit past HEAD's file length). Distinct from a
# GENUINE git failure (e.g. "not a git repository", "unrecognized
# argument"), which we must NOT mask.
_NO_COMMITTED_HISTORY_SIGNATURES = (
    "in the commit",  # "fatal: There is no path <file> in the commit"
    "has only",  # "fatal: file <file> has only N lines"
)


def _is_no_committed_history(stderr: str) -> bool:
    """True iff git's stderr signals "range has no committed baseline".

    Matches the two ``git log -L`` exit-128 messages emitted when a
    range cannot map onto committed history (path absent from HEAD, or
    range beyond HEAD's committed file length). Any other failure stderr
    returns False so it propagates as a genuine error.
    """
    return any(sig in stderr for sig in _NO_COMMITTED_HISTORY_SIGNATURES)


def _last_commit_for_range(
    repo_root: Path, file: str, start: int, end: int
) -> tuple[str, int] | None:
    """Return (sha, committer_epoch) of the latest commit touching a range.

    Shells out to ``git -C <repo> log -L <start>,<end>:<file> -s
    --format=%H%x09%ct -n 1``. ``-L`` selects commits touching the line
    range; ``-s`` suppresses the diff; ``-n 1`` keeps only the most
    recent. The first output line is ``<sha>\\t<epoch>``.

    Returns ``None`` when the range has no committed baseline yet (git
    exits 128 with a recognizable "no path in commit" / "has only N
    lines" signature) — an uncommitted tagged test cannot drift, so the
    caller skips it. Any OTHER git failure re-raises ``CalledProcessError``
    so a broken setup fails loud.
    """
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "log",
                "-L",
                f"{start},{end}:{file}",
                "-s",
                "--format=%H%x09%ct",
                "-n",
                "1",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=_C_LOCALE_ENV,
        )
    except subprocess.CalledProcessError as exc:
        if exc.returncode == 128 and _is_no_committed_history(exc.stderr or ""):
            return None
        raise
    first_line = result.stdout.strip().splitlines()[0]
    sha, epoch = first_line.split("\t", 1)
    return sha, int(epoch)


def resolve_binding_refs(binding: dict, repo_root: Path) -> dict | None:
    """Enrich `binding` with body + @req-line commit refs and timestamps.

    Resolves ``[body_start, body_end]`` and
    ``[binding_line, binding_line]`` of ``binding["file"]`` to their most
    recent commits with two independent ``git log -L`` calls, then returns
    a new dict carrying the original keys plus ``body_ref`` / ``body_ts``
    and ``binding_ref`` / ``binding_ts``.

    Returns ``None`` when EITHER range has no committed baseline yet (an
    uncommitted tagged test or an uncommitted edit past HEAD's committed
    file length): the binding is genuinely not comparable, so the WARN
    lane skips it. Genuine git errors still raise.
    """
    file = binding["file"]
    body = _last_commit_for_range(
        repo_root, file, binding["body_start"], binding["body_end"]
    )
    binding_resolved = _last_commit_for_range(
        repo_root, file, binding["binding_line"], binding["binding_line"]
    )
    if body is None or binding_resolved is None:
        return None
    body_ref, body_ts = body
    binding_ref, binding_ts = binding_resolved
    return {
        **binding,
        "body_ref": body_ref,
        "body_ts": body_ts,
        "binding_ref": binding_ref,
        "binding_ts": binding_ts,
    }
