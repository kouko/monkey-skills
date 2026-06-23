"""Resolve a living-spec binding's body + @req-line to git commits.

A binding (from ``living_spec_tags.locate_bindings``, enriched with a
``file`` key by the collector) names two independent 1-based line ranges
in one file: the enclosing test's body ``[body_start, body_end]`` and the
single ``@req`` line ``[binding_line, binding_line]``. The comparator
(Task 1) needs, for each range, the most-recent commit that touched it.

The importable entry point is
``resolve_binding_refs(binding, repo_root) -> dict``, returning the
binding ENRICHED with ``body_ref`` / ``body_ts`` (SHA + committer epoch
of the body range's last commit) and ``binding_ref`` / ``binding_ts``
(same for the ``@req`` line). The two ranges are resolved with TWO
separate ``git log -L`` calls — robust even when ``binding_line`` falls
outside the body range (an inherited edge from nearest-test attribution).

Pure stdlib (``subprocess`` shelling out to the ``git`` CLI; no
third-party git library).
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def _last_commit_for_range(
    repo_root: Path, file: str, start: int, end: int
) -> tuple[str, int]:
    """Return (sha, committer_epoch) of the latest commit touching a range.

    Shells out to ``git -C <repo> log -L <start>,<end>:<file> -s
    --format=%H%x09%ct -n 1``. ``-L`` selects commits touching the line
    range; ``-s`` suppresses the diff; ``-n 1`` keeps only the most
    recent. The first output line is ``<sha>\\t<epoch>``; fail loud if
    git emits nothing (the range resolved to no commit).
    """
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
    )
    first_line = result.stdout.strip().splitlines()[0]
    sha, epoch = first_line.split("\t", 1)
    return sha, int(epoch)


def resolve_binding_refs(binding: dict, repo_root: Path) -> dict:
    """Enrich `binding` with body + @req-line commit refs and timestamps.

    Resolves ``[body_start, body_end]`` and
    ``[binding_line, binding_line]`` of ``binding["file"]`` to their most
    recent commits with two independent ``git log -L`` calls, then returns
    a new dict carrying the original keys plus ``body_ref`` / ``body_ts``
    and ``binding_ref`` / ``binding_ts``.
    """
    file = binding["file"]
    body_ref, body_ts = _last_commit_for_range(
        repo_root, file, binding["body_start"], binding["body_end"]
    )
    binding_ref, binding_ts = _last_commit_for_range(
        repo_root, file, binding["binding_line"], binding["binding_line"]
    )
    return {
        **binding,
        "body_ref": body_ref,
        "body_ts": body_ts,
        "binding_ref": binding_ref,
        "binding_ts": binding_ts,
    }
