"""Shared fixture for the W1 adversary probes.

Every probe file creates its OWN throwaway git repo under the system temp
directory (nothing is ever written into the repo under audit, and nothing
is ever written next to this file) and runs the real
`loom-code/scripts/loom_checker.py` from the repo being audited.

Convention for every probe: exit 0 == the gate CAUGHT the attack,
exit 1 == the attack ESCAPED. `EXPECTED: escaped-by-design` probes are the
exception -- they record an accepted cheap bypass (concept-model §0) and
exit 0 regardless of catch/escape.
"""
from __future__ import annotations

import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _find_repo_under_audit() -> Path:
    """Walk up from this file to the repo that owns
    loom-code/scripts/loom_checker.py -- no absolute paths baked in, so the
    probes work no matter where this evidence directory is checked out."""
    override = os.environ.get("LOOM_REPO")
    if override:
        return Path(override).resolve()
    for candidate in (HERE, *HERE.parents):
        if (candidate / "loom-code" / "scripts" / "loom_checker.py").is_file():
            return candidate
    raise RuntimeError(
        "could not find loom-code/scripts/loom_checker.py above "
        f"{HERE} (set LOOM_REPO to override)"
    )


REPO_UNDER_AUDIT = _find_repo_under_audit()
CHECKER = REPO_UNDER_AUDIT / "loom-code" / "scripts" / "loom_checker.py"

_CREATED_REPOS: list[Path] = []


def _cleanup_created_repos() -> None:
    for repo in _CREATED_REPOS:
        shutil.rmtree(repo, ignore_errors=True)


atexit.register(_cleanup_created_repos)


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout.strip()


def new_repo(name: str) -> Path:
    # Under the system temp dir, never next to this file -- a probe run
    # leaves this evidence directory clean.
    root = Path(tempfile.mkdtemp(prefix=f"loomprobe-{name}-"))
    _CREATED_REPOS.append(root)
    git(root, "init", "-b", "main", "-q")
    git(root, "config", "user.email", "probe@example.com")
    git(root, "config", "user.name", "probe")
    (root / "README.md").write_text("seed\n", encoding="utf-8")
    # Every fixture repo declares its own test command and carries a trivial
    # suite, so `push.probes-package-tests` has something real to recompute
    # and a probe about another rule is not caught by this one first.
    (root / "docs" / "loom").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "loom" / "KICKOFF-DEFAULTS.md").write_text(
        "# Kickoff Defaults\n\n- package-tests: python3 -m pytest -q — the "
        "fixture's whole suite (2026-09-02)\n",
        encoding="utf-8",
    )
    (root / "tests").mkdir(exist_ok=True)
    (root / "tests" / "test_seed.py").write_text(
        "def test_seed():\n    assert True\n", encoding="utf-8"
    )
    # The adversarial cases `adversarial_probes` records; the checker runs
    # these files directly, so they have to exist and be runnable.
    for index in range(3):
        (root / f"probe{index}.py").write_text(
            "raise SystemExit(0)\n", encoding="utf-8"
        )
    git(root, "add", "-A")
    git(root, "commit", "-qm", "seed")
    git(root, "checkout", "-qb", "feat")
    return root


def write(repo: Path, rel: str, text: str) -> Path:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def checker(repo: Path, *args: str, env_extra: dict | None = None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=str(repo), capture_output=True, text=True, env=env,
    )


def review_doc(reviewed_sha: str, **overrides) -> dict:
    """A review.json that passes every push rule, as the baseline an attack
    then bends one field of."""
    doc = {
        "reviewed_sha": reviewed_sha,
        "scope": "wave-end:1",
        "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "verdict": "PASS", "dimension_scores": {}, "findings": [], "round": 1},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "docs",
             "verdict": "PASS", "dimension_scores": {}, "findings": [], "round": 1},
        ],
        "probes": [
            {"kind": "package-tests", "command": "python3 -m pytest -q",
             "sha": reviewed_sha, "result": "pass", "artifact": ""},
        ],
        "open_findings": [],
        "dispatch": [
            {"task": "W1-01", "role": "implementer", "agent_id": "imp-1",
             "model": "m", "started": "2026-09-02T00:00:00Z", "fresh_context": True},
            {"task": "W1-01", "role": "reviewer", "agent_id": "rev-a",
             "model": "m", "started": "2026-09-02T00:00:00Z", "fresh_context": True},
            {"task": "W1-01", "role": "reviewer", "agent_id": "rev-b",
             "model": "m", "started": "2026-09-02T00:00:00Z", "fresh_context": True},
        ],
    }
    doc.update(overrides)
    return doc


def adversarial_probes(sha: str, n: int = 3) -> list[dict]:
    return [
        {"kind": "adversarial", "command": f"python3 probe{i}.py",
         "sha": sha, "result": "pass", "artifact": f"probe{i}.py"}
        for i in range(n)
    ]


def push_case(repo: Path, review: dict, change_id: str = "w1") -> subprocess.CompletedProcess:
    """Commit `review` as a review-only HEAD and run the push gate."""
    write(repo, f"docs/loom/{change_id}/review.json", json.dumps(review, indent=2) + "\n")
    git(repo, "add", f"docs/loom/{change_id}/review.json")
    git(repo, "commit", "-qm", "chore(loom): review checkpoint")
    return checker(repo, "push")


def verdict(caught: bool, note: str) -> int:
    print(("CAUGHT: " if caught else "ESCAPED: ") + note)
    return 0 if caught else 1


def code_repo_with_attacks(name: str, trailer: str = "\n\nTask: W1-01") -> tuple[Path, str]:
    """A repo with a real (green) package-test suite plus three attackN.py
    files that each exit 1 -- shared setup for the X1/X2 reviewer-authored
    probes, which attack how the recorded probe *command* is re-run."""
    repo = new_repo(name)
    write(repo, "docs/loom/KICKOFF-DEFAULTS.md",
          "# Kickoff\n\n- package-tests: python3 -m pytest -q\n")
    write(repo, "src/thing.py", "x = 1\n")
    write(repo, "tests/test_thing.py", "def test_ok():\n    assert True\n")
    for i in range(3):
        write(repo, f"attack{i}.py", "import sys; sys.exit(1)\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "feat: thing" + trailer)
    return repo, git(repo, "rev-parse", "HEAD")


def review_with_adversarial_commands(sha: str, commands: list[str]) -> dict:
    """A review.json with a real package-tests probe plus one adversarial
    probe per given command, each pointed at attack<i>.py."""
    rev = review_doc(sha)
    rev["probes"] = [
        {"kind": "package-tests", "command": "python3 -m pytest -q",
         "sha": sha, "result": "pass", "artifact": ""},
    ]
    for i, command in enumerate(commands):
        rev["probes"].append({
            "kind": "adversarial", "command": command, "sha": sha,
            "result": "pass", "artifact": f"attack{i}.py",
        })
    return rev


def expected_escape(note: str) -> int:
    """For probes marked EXPECTED: escaped-by-design (concept-model §0
    accepted cheap bypasses) -- a record, not a gate. Always exits 0."""
    print("EXPECTED: escaped-by-design — " + note)
    return 0
