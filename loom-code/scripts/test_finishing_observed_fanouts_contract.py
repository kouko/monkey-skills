"""RED/GREEN gate: finishing-a-development-branch/SKILL.md must carry an
"Observed fan-outs" close-out sub-check row that relays the branch's
observed reviewer fan-outs from the dispatch log and stamps the line into
the plan's `## Notes` — and its invocation string must be the argv
`task_batch_replay.py observe --summary` actually accepts.
"""

import pathlib
import re
import shlex
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parent
SKILL_MD = SCRIPTS.parent / "skills" / "finishing-a-development-branch" / "SKILL.md"
NO_LOG_LINE = "observed reviewer fan-outs: N/A — no dispatch log"
SUMMARY_CMD = re.compile(
    r"`(python3 loom-code/scripts/task_batch_replay\.py observe [^`]*--summary)`"
)


def _fanouts_row() -> str:
    lines = [
        line
        for line in SKILL_MD.read_text(encoding="utf-8").splitlines()
        if line.lstrip().startswith("|") and "review-dispatches.jsonl" in line
    ]
    assert len(lines) == 1, (
        "expected exactly one close-out sub-check row naming "
        f"review-dispatches.jsonl, got {len(lines)}"
    )
    return lines[0]


def test_finishing_documents_observed_fanouts_row(tmp_path):
    # No @req tag: this task's dispatch carries no registered REQ-ids.
    row = _fanouts_row()

    cmd = SUMMARY_CMD.search(row)
    assert cmd, "row does not carry the repo-root `observe ... --summary` invocation"
    assert "--log <git-dir>/loom/review-dispatches.jsonl" in cmd.group(1)
    assert "--branch <branch>" in cmd.group(1)
    assert "## Notes" in row, "row does not stamp the line into the plan's `## Notes`"
    assert NO_LOG_LINE in row, "row does not name the absent-log N/A line"
    assert "silently" in row and "never" in row, "absent log must be loud, never silent"

    # GREEN pin: the prose's argv is what Task 5's parser accepts. Run it
    # with an empty temp dir as <git-dir> (no log there) — the N/A line
    # proves the invocation parsed and took the absent-log path.
    argv = shlex.split(
        cmd.group(1)
        .replace("<git-dir>", str(tmp_path))
        .replace("<branch>", "any-branch")
    )
    argv[0] = sys.executable
    argv[1] = str(SCRIPTS / "task_batch_replay.py")
    proc = subprocess.run(argv, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == NO_LOG_LINE
