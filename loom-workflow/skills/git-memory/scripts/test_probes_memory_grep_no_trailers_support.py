"""Probe for the third capability band of the W1-02 branch-end fix, plus
(second round) a regression pin for the fatal substring-vs-exact defect
the closing reviewer found in that same guard.

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

Second round (fix round, finding 1): the guard used to decide capability
by `grep -qF` — a SUBSTRING test of the probe output against the
placeholder text — which a real trailer VALUE that happens to quote the
placeholder syntax verbatim can satisfy even on a fully capable git. The
two cases below pin the fix (a synthetic, content-free probe object) so
repository content can never again reach the capability decision:
(a) a fully capable real git whose HEAD trailer value contains
`%(trailers:unfold)` still takes the fast (key=) path, and (b) a git
that is unfold-capable but not key=-capable, with that SAME hostile
HEAD value, still recovers via the fallback (exit 0) instead of the old
code's false exit 3.

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


# ─── fix-round regression: substring vs exact capability decision ─────

_HOSTILE_TRAILER_VALUE = "%(trailers:unfold)"


def _memory_repo_with_hostile_trailer(tmp_path: Path) -> Path:
    """HEAD's own `Decision:` trailer VALUE is, verbatim, the exact text
    of the fallback probe's placeholder — plausible real content for a
    repo (like this one) whose commits discuss the placeholder syntax
    itself. This must never be mistaken for an unexpanded echo of that
    placeholder.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(
        repo, "2024-01-01", "quote the placeholder syntax in a trailer",
        body=f"Decision: {_HOSTILE_TRAILER_VALUE}".encode(),
    )
    return repo


def _call_logging_git_shim_dir(tmp_path: Path, name: str, *, reject_key: bool) -> tuple[Path, Path]:
    """A PATH-prepended `git` shim that appends one line per `git log`
    invocation carrying a `%(trailers...)` --format argument to a log
    file (so the test can observe which capability probe actually ran,
    independent of stdout content), then either passes the call straight
    through to the real git (reject_key=False) or, when reject_key=True,
    leaves ONLY the `%(trailers:key=...)` variant unexpanded (literal
    echo) — simulating a git that understands `%(trailers:unfold)` but
    not the `key=` filter — while the plain `%(trailers:unfold)` variant
    and every other invocation pass through unmodified.
    """
    real_git = shutil.which("git")
    assert real_git, "git not found on PATH"
    shim_dir = tmp_path / f"shim-git-{name}"
    shim_dir.mkdir(exist_ok=True)
    log_path = tmp_path / f"calls-{name}.log"
    shim = shim_dir / "git"
    shim.write_text(textwrap.dedent(f"""\
        #!/usr/bin/env python3
        import sys, os
        REAL_GIT = {real_git!r}
        LOG_PATH = {str(log_path)!r}
        REJECT_KEY = {reject_key!r}
        KEY_NEEDLE = "%(trailers:key="
        UNFOLD_NEEDLE = "%(trailers:unfold)"
        args = sys.argv[1:]
        for i, a in enumerate(args):
            if a.startswith("--format=") and KEY_NEEDLE in a:
                with open(LOG_PATH, "a") as f:
                    f.write("key\\n")
                if REJECT_KEY:
                    args[i] = a.replace(KEY_NEEDLE, "%%(trailers:key=")
            elif a.startswith("--format=") and UNFOLD_NEEDLE in a:
                with open(LOG_PATH, "a") as f:
                    f.write("unfold\\n")
        os.execv(REAL_GIT, [REAL_GIT] + args)
        """))
    shim.chmod(0o755)
    return shim_dir, log_path


def _probe_calls(log_path: Path) -> list[str]:
    if not log_path.is_file():
        return []
    return [line for line in log_path.read_text(encoding="utf-8").splitlines() if line]


def test_extract_commits_capable_git_hostile_trailer_stays_on_fast_path(tmp_path: Path) -> None:
    """A fully capable real git (understands `key=`) whose HEAD trailer
    VALUE is, verbatim, `%(trailers:unfold)` — the fallback probe's own
    placeholder text — must still take the fast (key=) path: the key=
    probe's own rendered output never contains the key= probe's OWN
    placeholder text as a substring here, so even the old substring
    check stayed correct in this specific shape; this pins that the fix
    does not regress it, and that the fallback's needle is never even
    checked (probe call count stays at exactly one: the key= probe).
    """
    repo = _memory_repo_with_hostile_trailer(tmp_path)
    shim_dir, log_path = _call_logging_git_shim_dir(tmp_path, "capable", reject_key=False)
    env = os.environ.copy()
    env["PATH"] = f"{shim_dir}:{env['PATH']}"

    result = _run(repo, "--no-pr", "--since=2019-01-01", env=env)

    assert result.returncode == 0, (
        f"a fully capable git must not be misdiagnosed as incapable, got "
        f"exit {result.returncode}; stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "(none in range)" not in result.stdout
    assert f"Decision: {_HOSTILE_TRAILER_VALUE}" in result.stdout, (
        f"expected the real hostile Decision: trailer to survive, got stdout: {result.stdout!r}"
    )
    calls = _probe_calls(log_path)
    assert calls == ["key", "key"], (
        f"expected exactly two key= --format calls (the capability probe, "
        f"then the real extraction pass reusing the fast path) with no "
        f"fallback probe ever run, got: {calls!r}"
    )


def test_extract_commits_unfold_only_git_hostile_trailer_recovers_via_fallback(tmp_path: Path) -> None:
    """A git that understands `%(trailers:unfold)` but not `key=` (the
    middle capability band), with that SAME hostile HEAD trailer value,
    must still recover via the fallback and exit 0 with a complete
    digest — NOT the old code's false exit 3. Under the old substring
    check: the key= probe (rejected, literal echo) trivially matches its
    own needle and selects the fallback; the fallback probe then renders
    HEAD's real trailers via `%(trailers:unfold)`, and that real,
    fully-expanded output contains `%(trailers:unfold)` as a substring
    because the trailer VALUE itself is that exact text — so the old
    code wrongly concluded this capable-enough git supports neither
    placeholder and exited 3. The fix must tell the two apart.
    """
    repo = _memory_repo_with_hostile_trailer(tmp_path)
    shim_dir, log_path = _call_logging_git_shim_dir(tmp_path, "unfold-only", reject_key=True)
    env = os.environ.copy()
    env["PATH"] = f"{shim_dir}:{env['PATH']}"

    result = _run(repo, "--no-pr", "--since=2019-01-01", env=env)

    assert result.returncode == 0, (
        f"a git that supports the unfold fallback must recover, not exit 3; "
        f"got exit {result.returncode}; stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "(none in range)" not in result.stdout
    assert f"Decision: {_HOSTILE_TRAILER_VALUE}" in result.stdout, (
        f"expected the real hostile Decision: trailer to survive via the fallback, got stdout: {result.stdout!r}"
    )
    calls = _probe_calls(log_path)
    assert calls == ["key", "unfold", "unfold"], (
        f"expected the key= probe to fail, the unfold fallback probe to then "
        f"run and succeed, and the real extraction pass to reuse that "
        f"fallback format, got: {calls!r}"
    )
