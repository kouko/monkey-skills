"""Tests pinning the removal of the Z3-based skill-consistency-check (A6).

WHY: the Z3 pipeline never worked, its adversarial probe was fake and its
attestation claimed a review that did not hold. These tests keep them from
coming back and keep live files from pointing at the removed scripts.
Checks run against `git ls-files`, so they see what is tracked, not stray
local files.
"""

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = "skill-dev-toolkit/skills/skill-consistency-check"

REMOVED_PATHS = [
    f"{SKILL}/install.sh",
    f"{SKILL}/skill-consistency-check",
    f"{SKILL}/scripts/build_dependency_graph.py",
    f"{SKILL}/scripts/check_consistency.py",
    f"{SKILL}/scripts/extract_rules.py",
    f"{SKILL}/scripts/generate_report.py",
    f"{SKILL}/scripts/pattern_engine.py",
    f"{SKILL}/scripts/smt_encode.py",
    f"{SKILL}/references/conflict-patterns.md",
    f"{SKILL}/references/rule-templates.md",
    f"{SKILL}/references/severity-rubric.md",
    "scripts/adversarial_probe.py",
    "docs/loom/2026-09-22-skill-consistency-check/attestation.json",
]

REMOVED_SCRIPT_NAMES = [
    "extract_rules.py",
    "smt_encode.py",
    "check_consistency.py",
    "pattern_engine.py",
    "build_dependency_graph.py",
    "generate_report.py",
    "adversarial_probe.py",
]

# docs/loom holds change history (including this change's plan, spec and
# intent), which legitimately names the removed scripts.
EXEMPT_PREFIXES = ("docs/loom/",)
THIS_FILE = "scripts/test_consistency_check_removal.py"


def _tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "-z"],
        check=True,
        capture_output=True,
    ).stdout
    return [p.decode("utf-8") for p in out.split(b"\0") if p]


def test_removed_paths_absent():
    """T-removed-paths-absent: no removed path is still tracked."""
    tracked = set(_tracked_files())
    still_tracked = [p for p in REMOVED_PATHS if p in tracked]
    assert still_tracked == []


def test_no_reference_to_removed_scripts():
    """T-no-reference-to-removed-scripts: no live file names a removed script."""
    offenders = []
    for rel in _tracked_files():
        if rel == THIS_FILE or rel.startswith(EXEMPT_PREFIXES):
            continue
        path = REPO / rel
        if not path.is_file():
            continue
        text = path.read_bytes().decode("utf-8", errors="ignore")
        for name in REMOVED_SCRIPT_NAMES:
            if name in text:
                offenders.append(f"{rel}: {name}")
    assert offenders == []
