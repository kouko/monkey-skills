"""Fix-round regression (branch-end round 5, fatal): when the capability
probe's scratch object store cannot be built at all — `mktemp -d` itself
fails — extract_commits_ndjson used to treat this as INCONCLUSIVE and
fall through to the real extraction pass unguarded. On a git old enough
to echo `%(trailers:key=...)` back as literal text, that fall-through
restores the exact silent-data-loss failure this whole guard exists to
prevent: a repository full of real `Decision:` trailers reports "(none
in range)" and exits 0.

The fix must treat "the probe could not be built" as "capability
unverified", not "capability assumed fine", and exit 3 loudly — the
same class and message shape as the existing "neither placeholder
understood" exit 3 (test_probes_memory_grep_no_trailers_support.py),
naming the missing capability rather than a partial/successful-looking
digest.

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
    `--format=` argument containing `%(trailers` — simulating an old git
    that understands neither the `key=` filter nor plain
    `%(trailers:unfold)`. Every other invocation passes straight through
    to the real git unmodified. (Same fixture as
    test_probes_memory_grep_no_trailers_support.py.)
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


def _mktemp_always_fails_shim_dir(tmp_path: Path) -> Path:
    """A PATH-prepended `mktemp` shim that always fails, simulating a
    scratch-store build failure (a hostile/constrained \\$TMPDIR, a full
    disk, permissions) for the capability probe's `mktemp -d` call — the
    only `mktemp` invocation memory-grep.sh makes.
    """
    shim_dir = tmp_path / "shim-mktemp-fails"
    shim_dir.mkdir(exist_ok=True)
    shim = shim_dir / "mktemp"
    shim.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import sys
        sys.exit(1)
        """))
    shim.chmod(0o755)
    return shim_dir


def _run(repo: Path, *args: str, env: dict) -> subprocess.CompletedProcess:
    cmd = ["bash", str(SCRIPT), f"--repo={repo}"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_probe_store_build_failure_on_incapable_git_fails_loud_not_silent(tmp_path: Path) -> None:
    """The scratch object store cannot be built (mktemp fails) AND this
    git cannot expand `%(trailers:...)` at all. The old fall-through
    treated the unbuildable probe as inconclusive and ran the real
    extraction unguarded, silently reporting "(none in range)" over a
    commit that really carries a Decision: trailer. The fix must exit 3
    instead — capability unverified is not capability assumed fine.
    """
    repo = _memory_repo(tmp_path)
    no_trailers_shim = _no_trailers_support_git_shim_dir(tmp_path)
    no_mktemp_shim = _mktemp_always_fails_shim_dir(tmp_path)
    env = os.environ.copy()
    # mktemp shim first on PATH so its `mktemp` wins; the no-trailers git
    # shim's `git` wins too since both dirs are prepended.
    env["PATH"] = f"{no_mktemp_shim}:{no_trailers_shim}:{env['PATH']}"

    result = _run(repo, "--no-pr", "--since=2019-01-01", env=env)

    assert result.returncode == 3, (
        f"expected exit 3 (capability unverified) when the probe's scratch "
        f"store cannot be built at all, got {result.returncode}; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "(none in range)" not in result.stdout, (
        "a probe that could not be built must not fall through to an "
        "unguarded extraction that prints a successful-looking empty digest"
    )
    assert "Decision" not in result.stdout, (
        "a loud failure should not also print a partial/successful-looking digest"
    )
    assert "trailers" in result.stderr.lower(), (
        f"expected the error to name the missing/unverified capability, got stderr: {result.stderr!r}"
    )


def test_probe_store_build_failure_on_capable_git_still_fails_loud(tmp_path: Path) -> None:
    """Even when the real git IS fully capable, a probe that cannot be
    built at all means capability was never actually verified — the fix
    is unconditional (any failure to build the probe exits 3), not
    conditional on whether the underlying git happens to be fine. This
    pins the "exit 3 loudly instead of falling through" repair rather
    than a narrower fix that only fires when the git is also incapable.
    """
    repo = _memory_repo(tmp_path)
    no_mktemp_shim = _mktemp_always_fails_shim_dir(tmp_path)
    env = os.environ.copy()
    env["PATH"] = f"{no_mktemp_shim}:{env['PATH']}"

    result = _run(repo, "--no-pr", "--since=2019-01-01", env=env)

    assert result.returncode == 3, (
        f"expected exit 3 (capability unverified) when the probe's scratch "
        f"store cannot be built, even though the real git is capable; got "
        f"{result.returncode}; stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "trailers" in result.stderr.lower(), (
        f"expected the error to name the unverified capability, got stderr: {result.stderr!r}"
    )
