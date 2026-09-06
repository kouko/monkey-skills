"""Controlled replay of the real versioned Ship-to-local-gate boundary.

The harness builds one accepted checkpoint, copies it for every arm, and
stops when the hook returns. It never executes the intercepted network push.
Each revision's checker, hook declaration, and contract package are extracted
from Git, so the current checkout's imported checker cannot stand in for them.
"""
from __future__ import annotations

import io
import json
import os
import shlex
import shutil
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "loom-code" / "skills" / "ship" / "SKILL.md").exists()
)
BASELINE = "9d009c49e02a52c4838dba30a88501e0bbe79ab0"
CANDIDATE = "b197c123fb1c0cc513fc56b3262f15aefd845b82"
SAMPLES = 7
WORK_SECONDS = "0.080"
CHANGE = "2026-09-02-a"
REVIEW = f"docs/loom/{CHANGE}/review.json"
PACKAGE_COMMAND = "python3 evidence/package_suite.py"
ARCHIVE_PATHS = (
    "loom-code/scripts/loom_checker.py",
    "loom-code/scripts/git_exec.py",
    "loom-code/scripts/codex_scaffold.py",
    "loom-code/scripts/loom_record_fire.py",
    "loom-code/hooks/hooks.json",
    "loom-code/contract",
)


@dataclass(frozen=True)
class PackageInvocation:
    elapsed_seconds: float


@dataclass(frozen=True)
class Observation:
    revision: str
    fixture_head: str
    entrypoints: tuple[str, ...]
    returncodes: tuple[int, ...]
    calls: int
    invocation_seconds: tuple[float, ...]
    elapsed_seconds: float
    verdict: str
    refspec: str
    push_command: str


def run(*args: str, cwd: Path, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, **kwargs)


def git(repo: Path, *args: str) -> str:
    return run("git", *args, cwd=repo, check=True).stdout.strip()


def extract_versioned_bundle(revision: str, destination: Path) -> Path:
    """Materialize only the checker runtime declared by ``revision``."""
    archive = subprocess.run(
        ["git", "archive", "--format=tar", revision, *ARCHIVE_PATHS],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
        bundle.extractall(destination, filter="data")
    plugin = destination / "loom-code"
    assert (plugin / "scripts/loom_checker.py").is_file()
    assert (plugin / "scripts/git_exec.py").is_file()
    assert (plugin / "scripts/codex_scaffold.py").is_file()
    assert (plugin / "scripts/loom_record_fire.py").is_file()
    assert (plugin / "hooks/hooks.json").is_file()
    assert (plugin / "contract/manifest.yaml").is_file()
    return plugin


def review_body(reviewed_sha: str) -> dict:
    adversarial = [
        {
            "kind": "adversarial",
            "command": f"python3 evidence/abuse_{name}.py",
            "sha": reviewed_sha,
            "result": "pass",
            "artifact": f"evidence/abuse_{name}.py",
        }
        for name in ("empty", "boundary", "hostile")
    ]
    return {
        "reviewed_sha": reviewed_sha,
        "scope": "wave 1 code delta",
        "vendors": ["anthropic"],
        "verdicts": [
            {
                "reviewer": "agent-rev", "vendor": "anthropic", "model": "m",
                "lens": "code", "verdict": "PASS", "dimension_scores": {},
                "findings": [], "sha": reviewed_sha,
            },
            {
                "reviewer": "agent-blind", "vendor": "anthropic", "model": "m",
                "lens": "code", "verdict": "PASS_WITH_NOTES", "dimension_scores": {},
                "findings": [], "sha": reviewed_sha,
            },
        ],
        "probes": [
            {
                "kind": "package-tests", "command": PACKAGE_COMMAND,
                "sha": reviewed_sha, "result": "pass", "artifact": "evidence/tests.txt",
            },
            *adversarial,
        ],
        "open_findings": [
            {
                "id": "F-1", "anchor": "a.py:1", "origin_sha": "deadbee",
                "raised_by": "agent-rev", "resolved": "fixed in HEAD^",
            }
        ],
        "dispatch": [
            {
                "task": "T1", "role": role, "agent_id": agent, "model": "m",
                "started": started, "fresh_context": True,
            }
            for role, agent, started in (
                ("implementer", "agent-imp", "2026-09-02T09:00:00Z"),
                ("reviewer", "agent-rev", "2026-09-02T10:00:00Z"),
                ("blind-runner", "agent-blind", "2026-09-02T11:00:00Z"),
            )
        ],
    }


def build_accepted_checkpoint(repo: Path) -> str:
    """Create the one accepted checkpoint copied unchanged into both arms."""
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")

    evidence = repo / "evidence"
    evidence.mkdir()
    (repo / "a.py").write_text("value = 1\n", encoding="utf-8")
    (evidence / "tests.txt").write_text("controlled complete suite\n", encoding="utf-8")
    (evidence / "package_suite.py").write_text(
        "import json, os, time\n"
        "from pathlib import Path\n"
        "started = time.monotonic_ns()\n"
        "time.sleep(float(os.environ['W1_WORK_SECONDS']))\n"
        "elapsed = time.monotonic_ns() - started\n"
        "with Path(os.environ['W1_CALL_LOG']).open('a', encoding='utf-8') as stream:\n"
        "    stream.write(json.dumps({'elapsed_ns': elapsed}) + '\\n')\n",
        encoding="utf-8",
    )
    for name in ("empty", "boundary", "hostile"):
        (evidence / f"abuse_{name}.py").write_text("raise SystemExit(0)\n", encoding="utf-8")

    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True)
    kickoff.write_text(
        f"# Kickoff Defaults\n\n- package-tests: {PACKAGE_COMMAND}"
        " — controlled complete fixture suite (2026-09-07)\n",
        encoding="utf-8",
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: accepted fixture\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    review = repo / REVIEW
    review.parent.mkdir(parents=True)
    review.write_text(json.dumps(review_body(reviewed_sha), indent=1), encoding="utf-8")
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    assert not git(repo, "status", "--porcelain")
    return git(repo, "rev-parse", "HEAD")


def hook_argv(plugin: Path) -> list[str]:
    hooks = json.loads((plugin / "hooks/hooks.json").read_text(encoding="utf-8"))
    command = hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    expanded = command.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin))
    argv = shlex.split(expanded)
    assert Path(argv[1]).resolve() == (plugin / "scripts/loom_checker.py").resolve()
    assert argv[2:] == ["push", "--hook"]
    return [sys.executable, *argv[1:]]


def package_invocations(log: Path) -> tuple[PackageInvocation, ...]:
    if not log.exists():
        return ()
    return tuple(
        PackageInvocation(json.loads(line)["elapsed_ns"] / 1_000_000_000)
        for line in log.read_text(encoding="utf-8").splitlines()
    )


def quote_all_shell_token(token: str) -> str:
    """Render one observed argv token with no shell expansion position."""
    return "'" + token.replace("'", "'\"'\"'") + "'"


def canonical_push_command(repo: Path, refspec: str) -> str:
    trusted = shutil.which("git")
    assert trusted is not None
    tokens = [
        str(Path(trusted).resolve()),
        "-C",
        str(repo.resolve()),
        "push",
        "--no-follow-tags",
        "--recurse-submodules=no",
        "-u",
        "origin",
        refspec,
    ]
    return " ".join(quote_all_shell_token(token) for token in tokens)


def replay(revision: str, fixture: Path, template: Path, plugin: Path) -> Observation:
    """Run the specified real entrypoints and stop before network transfer."""
    fixture.mkdir(parents=True)
    repo = fixture / "repo"
    shutil.copytree(template, repo)
    call_log = fixture / "calls.jsonl"
    env = os.environ.copy()
    env.update(
        {
            "PYTHONHASHSEED": "0",
            "W1_CALL_LOG": str(call_log),
            "W1_WORK_SECONDS": WORK_SECONDS,
        }
    )
    head = git(repo, "rev-parse", "HEAD")
    branch = git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    refspec = f"{head}:refs/heads/{branch}"
    push_command = canonical_push_command(repo, refspec)
    payload = json.dumps(
        {
            "tool_name": "Bash", "cwd": str(repo),
            "tool_input": {"command": push_command},
        }
    )

    entrypoints = ["versioned-hook"]
    commands: list[tuple[list[str], str | None]] = [(hook_argv(plugin), payload)]
    if revision == BASELINE:
        entrypoints.insert(0, "explicit-checker")
        commands.insert(
            0,
            ([sys.executable, str(plugin / "scripts/loom_checker.py"), "push"], None),
        )

    results: list[subprocess.CompletedProcess] = []
    started = time.monotonic_ns()
    for command, stdin in commands:
        results.append(
            subprocess.run(
                command, cwd=repo, env=env, input=stdin,
                capture_output=True, text=True, check=False,
            )
        )
    elapsed = (time.monotonic_ns() - started) / 1_000_000_000
    returncodes = tuple(result.returncode for result in results)
    invocations = package_invocations(call_log)
    verdict = "release" if returncodes and all(code == 0 for code in returncodes) else "block"
    if verdict == "block":
        detail = "\n".join(f"stdout={r.stdout}\nstderr={r.stderr}" for r in results)
        raise AssertionError(f"{revision} gate blocked unexpectedly: {returncodes}\n{detail}")
    return Observation(
        revision=revision,
        fixture_head=head,
        entrypoints=tuple(entrypoints),
        returncodes=returncodes,
        calls=len(invocations),
        invocation_seconds=tuple(item.elapsed_seconds for item in invocations),
        elapsed_seconds=elapsed,
        verdict=verdict,
        refspec=refspec,
        push_command=push_command,
    )


def prepare_replay(tmp_path: Path) -> tuple[Path, dict[str, Path]]:
    template = tmp_path / "accepted-checkpoint"
    build_accepted_checkpoint(template)
    bundles = {
        revision: extract_versioned_bundle(revision, tmp_path / f"bundle-{revision[:8]}")
        for revision in (BASELINE, CANDIDATE)
    }
    return template, bundles


def measured_samples(tmp_path: Path) -> tuple[list[Observation], list[Observation]]:
    template, bundles = prepare_replay(tmp_path)
    baseline: list[Observation] = []
    candidate: list[Observation] = []
    for index in range(SAMPLES):
        order = ((BASELINE, baseline), (CANDIDATE, candidate))
        if index % 2:
            order = tuple(reversed(order))
        for revision, results in order:
            results.append(
                replay(
                    revision, tmp_path / f"sample-{index}-{revision[:8]}",
                    template, bundles[revision],
                )
            )
    return baseline, candidate


def test_revisions_execute_versioned_real_gate_entrypoints(tmp_path: Path) -> None:
    """Both arms report the real versioned checker entrypoints they ran."""
    template, bundles = prepare_replay(tmp_path)
    baseline = replay(BASELINE, tmp_path / "baseline", template, bundles[BASELINE])
    candidate = replay(CANDIDATE, tmp_path / "candidate", template, bundles[CANDIDATE])
    assert baseline.entrypoints == ("explicit-checker", "versioned-hook")
    assert candidate.entrypoints == ("versioned-hook",)
    assert baseline.returncodes == (0, 0)
    assert candidate.returncodes == (0,)
    assert baseline.fixture_head == candidate.fixture_head
    assert baseline.refspec == f"{baseline.fixture_head}:refs/heads/work"
    assert candidate.refspec == f"{candidate.fixture_head}:refs/heads/work"
    candidate_tokens = shlex.split(candidate.push_command)
    assert candidate.push_command == " ".join(
        quote_all_shell_token(token) for token in candidate_tokens
    )
    assert candidate_tokens == [
        str(Path(shutil.which("git")).resolve()),
        "-C",
        str((tmp_path / "candidate/repo").resolve()),
        "push",
        "--no-follow-tags",
        "--recurse-submodules=no",
        "-u",
        "origin",
        candidate.refspec,
    ]


def test_candidate_one_call_faster_same_verdict(tmp_path: Path) -> None:
    baseline, candidate = measured_samples(tmp_path)
    assert [sample.calls for sample in baseline] == [2] * SAMPLES
    assert [sample.calls for sample in candidate] == [1] * SAMPLES
    assert all(len(sample.invocation_seconds) == sample.calls for sample in baseline + candidate)
    assert all(seconds > 0 for sample in baseline + candidate for seconds in sample.invocation_seconds)
    assert sum(sample.calls for sample in candidate) < sum(sample.calls for sample in baseline)
    assert {sample.verdict for sample in baseline} == {"release"}
    assert {sample.verdict for sample in candidate} == {"release"}
    assert {sample.returncodes for sample in baseline} == {(0, 0)}
    assert {sample.returncodes for sample in candidate} == {(0,)}
    assert len({sample.fixture_head for sample in baseline + candidate}) == 1
    assert statistics.median(sample.elapsed_seconds for sample in candidate) < statistics.median(
        sample.elapsed_seconds for sample in baseline
    )


def observation_payload(tmp_path: Path) -> dict:
    baseline, candidate = measured_samples(tmp_path)
    return {
        "baseline": [asdict(sample) for sample in baseline],
        "candidate": [asdict(sample) for sample in candidate],
        "baseline_median_seconds": statistics.median(x.elapsed_seconds for x in baseline),
        "candidate_median_seconds": statistics.median(x.elapsed_seconds for x in candidate),
    }


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        print(json.dumps(observation_payload(Path(directory)), indent=2))
