"""Probe for the third capability band of the W1-02 branch-end fix.

docs/loom/2026-09-06-memory-grep-single-pass/evidence/probes/
test_abuse_memory_grep_branch_end.py pins the first two bands: a git
that understands `%(trailers:key=...)` (the fast path), and a git that
echoes that placeholder back as literal text but still understands the
key-less `%(trailers:unfold)` fallback (recovered transparently, exit
0). Neither probe covers a THIRD git: one old enough to understand
NEITHER placeholder — `%(trailers)`/`unfold` predate `key=`, but a git
predating both would echo the fallback back as literal text too, one
band further down the same silent-empty-digest failure mode. This file
is a separate, non-adversary suite (this repo's own, not the finding's
pin) that exercises exactly that terminal case: extract_commits_ndjson's
second capability probe must catch it and exit 3 with a message naming
the missing capability, rather than silently reporting "(none in
range)" over a commit that actually carries a real Decision: trailer.

Self-contained: builds its own tmp_path fixture repo, no network, no
mutation of memory-grep.sh, any golden, or any probe file under
docs/loom/.../evidence/probes/.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

# .../loom-workflow/skills/git-memory/scripts/this_file.py
# parents[4] is the repo root from here (scripts -> git-memory -> skills -> loom-workflow -> root)
REPO = Path(__file__).resolve().parents[4]
SCRIPT = REPO / "loom-workflow" / "skills" / "git-memory" / "scripts" / "memory-grep.sh"

assert SCRIPT.is_file(), f"expected memory-grep.sh at {SCRIPT}"

ENV_IDENTITY = {
    "GIT_AUTHOR_NAME": "Fixture Bot",
    "GIT_AUTHOR_EMAIL": "fixture@example.com",
    "GIT_COMMITTER_NAME": "Fixture Bot",
    "GIT_COMMITTER_EMAIL": "fixture@example.com",
}

_TRAILERS_NEEDLE = "%(trailers"


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "symbolic-ref", "HEAD", "refs/heads/main"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Fixture Bot"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=path, check=True)
    subprocess.run(["git", "config", "core.abbrev", "7"], cwd=path, check=True)


def _commit(path: Path, date: str, subject: str, body: bytes | None = None) -> str:
    env = os.environ.copy()
    env.update(ENV_IDENTITY)
    env["GIT_AUTHOR_DATE"] = f"{date}T00:00:00+0000"
    env["GIT_COMMITTER_DATE"] = f"{date}T00:00:00+0000"
    msg = subject.encode()
    if body:
        msg += b"\n\n" + body
    subprocess.run(
        ["git", "commit", "-q", "--allow-empty", "-F", "-"],
        cwd=path, input=msg, env=env, check=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True, check=True,
    ).stdout.strip()


def _memory_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2024-01-01", "do the thing", body=b"Decision: use X because Y")
    return repo


def _no_trailers_support_git_shim_dir(tmp_path: Path) -> Path:
    """A PATH-prepended `git` shim that echoes back as LITERAL text ANY
    `--format=` argument containing `%(trailers` — simulating a git old
    enough to understand neither the `key=` filter nor plain
    `%(trailers:unfold)`. Every other invocation passes straight through
    to the real git unmodified.
    """
    real_git = shutil.which("git")
    assert real_git, "git not found on PATH"
    shim_dir = tmp_path / "shim-git-no-trailers-support"
    shim_dir.mkdir(exist_ok=True)
    shim = shim_dir / "git"
    shim.write_text(textwrap.dedent(f"""\
        #!/usr/bin/env python3
        import sys, os
        REAL_GIT = {real_git!r}
        NEEDLE = {_TRAILERS_NEEDLE!r}
        args = sys.argv[1:]
        for i, a in enumerate(args):
            if a.startswith("--format=") and NEEDLE in a:
                args[i] = a.replace("%(trailers", "%%(trailers")
        os.execv(REAL_GIT, [REAL_GIT] + args)
        """))
    shim.chmod(0o755)
    return shim_dir


def _run(repo: Path, *args: str, env: dict) -> subprocess.CompletedProcess:
    cmd = ["bash", str(SCRIPT), f"--repo={repo}"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_extract_commits_no_trailers_support_at_all_fails_loudly(tmp_path: Path) -> None:
    """Neither `%(trailers:key=...)` nor the key-less `%(trailers:unfold)`
    fallback is understood by this git (both come back as literal,
    unexpanded placeholder text). extract_commits_ndjson's first probe
    detects the key= failure and selects the fallback format; its SECOND
    probe must then detect that the fallback ALSO comes back literal,
    and exit 3 (external dependency missing — the same class as the
    missing-jq check) with a message naming the missing capability,
    rather than silently reporting zero memories over a commit that
    really does carry a Decision: trailer.
    """
    repo = _memory_repo(tmp_path)
    shim_dir = _no_trailers_support_git_shim_dir(tmp_path)
    env = os.environ.copy()
    env["PATH"] = f"{shim_dir}:{env['PATH']}"

    result = _run(repo, "--no-pr", "--since=2019-01-01", env=env)

    assert result.returncode == 3, (
        f"expected exit 3 (external dependency missing) when neither "
        f"trailers placeholder is supported, got {result.returncode}; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "(none in range)" not in result.stdout, (
        "a git with no working trailers placeholder must not print a "
        "digest claiming zero memories"
    )
    assert "Decision" not in result.stdout, (
        "a loud failure should not also print a partial/successful-looking digest"
    )
    assert "trailers" in result.stderr.lower(), (
        f"expected the error to name the missing capability, got stderr: {result.stderr!r}"
    )
    assert "upgrade" in result.stderr.lower() or "git" in result.stderr.lower(), (
        f"expected the error to tell the user what to do, got stderr: {result.stderr!r}"
    )
