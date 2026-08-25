"""Contract tests for repository command-surface declarations."""

from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
DUAL_HOST_COMMAND = (
    "python3 loom-code/scripts/loom_firing_harness.py compare "
    "--corpus <corpus.json> --baseline <baseline-root> "
    "--candidate <candidate-root> --raw-dir <raw-dir> "
    "--out <comparison.json> --replicates 2"
)


def test_dual_host_firing_comparison_is_declared() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert DUAL_HOST_COMMAND in " ".join(agents.split())

    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "loom-code/scripts/loom_firing_harness.py"),
            "compare",
            "--help",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    for required_flag in (
        "--corpus",
        "--baseline",
        "--candidate",
        "--raw-dir",
        "--out",
        "--replicates",
    ):
        assert required_flag in completed.stdout
