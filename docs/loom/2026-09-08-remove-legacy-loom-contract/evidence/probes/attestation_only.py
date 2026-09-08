"""Adversarially prove that no legacy publication contract remains live."""

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[5]
CHECKER = ROOT / "loom-code/scripts/loom_checker.py"


result = subprocess.run(
    ["python3", str(CHECKER), "--list-rules"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
)
push_rules = {
    line.split("\t", 1)[0]
    for line in result.stdout.splitlines()
    if line.startswith("push.")
}
assert push_rules == {"push.attestation"}, push_rules

live_text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in [
        CHECKER,
        ROOT / "loom-code/contract/manifest.yaml",
        ROOT / "loom-code/skills/review/SKILL.md",
        ROOT / "loom-code/skills/ship/SKILL.md",
    ]
)
for retired in ("review.json", "--skip-package-tests", "Task:"):
    assert retired not in live_text, retired
