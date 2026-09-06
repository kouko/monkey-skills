"""Measured W1-01 replay of the accepted Ship-to-local-push-gate boundary.

The fixture never contacts a remote. It observes each revision's Ship station,
then executes the same local package command at every package-suite execution
site from the start of Ship's Push step until the hook releases the would-be
network push. Invocation counts come from the workload's append-only log.
"""
from __future__ import annotations

import os
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "loom-code" / "skills" / "ship" / "SKILL.md").exists()
)
BASELINE = "9d009c49"
CANDIDATE = "998ba231"
SHIP = "loom-code/skills/ship/SKILL.md"
SAMPLES = 7
WORK_SECONDS = "0.080"
EXPLICIT_PREFLIGHT = "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py push"


@dataclass(frozen=True)
class Observation:
    calls: int
    elapsed_seconds: float
    verdict: str


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def ship_text(revision: str) -> str:
    return git("show", f"{revision}:{SHIP}")


def replay(revision: str, fixture: Path) -> Observation:
    """Execute observed owners; the hook is always the final local gate."""
    fixture.mkdir(parents=True)
    counter = fixture / "calls.log"
    workload = fixture / "package_suite.py"
    workload.write_text(
        "import os, time\n"
        "from pathlib import Path\n"
        "Path(os.environ['W1_CALL_LOG']).open('a').write('package-suite\\n')\n"
        "time.sleep(float(os.environ['W1_WORK_SECONDS']))\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env.update(
        {
            "PYTHONHASHSEED": "0",
            "W1_CALL_LOG": str(counter),
            "W1_WORK_SECONDS": WORK_SECONDS,
        }
    )
    command = [sys.executable, str(workload)]
    returncodes: list[int] = []
    started = time.monotonic_ns()

    if EXPLICIT_PREFLIGHT in ship_text(revision):
        returncodes.append(subprocess.run(command, env=env, check=False).returncode)
    returncodes.append(subprocess.run(command, env=env, check=False).returncode)

    elapsed = (time.monotonic_ns() - started) / 1_000_000_000
    calls = counter.read_text(encoding="utf-8").splitlines()
    verdict = "release" if returncodes and all(code == 0 for code in returncodes) else "block"
    return Observation(len(calls), elapsed, verdict)


def measured_samples(tmp_path: Path) -> tuple[list[Observation], list[Observation]]:
    baseline: list[Observation] = []
    candidate: list[Observation] = []
    for index in range(SAMPLES):
        order = ((BASELINE, baseline), (CANDIDATE, candidate))
        if index % 2:
            order = tuple(reversed(order))
        for revision, results in order:
            results.append(replay(revision, tmp_path / f"{index}-{revision}"))
    return baseline, candidate


def test_revisions_observe_different_execution_owners() -> None:
    """Invocation multiplicity is observed from versioned station code."""
    assert git("rev-parse", BASELINE) == "9d009c49e02a52c4838dba30a88501e0bbe79ab0"
    assert git("rev-parse", CANDIDATE) == "998ba231327580c2262f650e54661dc1cb1d6d17"
    assert EXPLICIT_PREFLIGHT in ship_text(BASELINE)
    assert EXPLICIT_PREFLIGHT not in ship_text(CANDIDATE)


def test_candidate_one_call_faster_same_verdict(tmp_path: Path) -> None:
    baseline, candidate = measured_samples(tmp_path)
    assert [sample.calls for sample in baseline] == [2] * SAMPLES
    assert [sample.calls for sample in candidate] == [1] * SAMPLES
    assert sum(sample.calls for sample in candidate) < sum(sample.calls for sample in baseline)
    assert {sample.verdict for sample in baseline} == {"release"}
    assert {sample.verdict for sample in candidate} == {"release"}
    assert statistics.median(sample.elapsed_seconds for sample in candidate) < statistics.median(
        sample.elapsed_seconds for sample in baseline
    )
