"""RED test for Task 7 — think-orbit CI workflow.

@req: BI-8
"""
from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "think-orbit-ci.yml"


def _all_run_lines(workflow: dict) -> str:
    lines = []
    for job in workflow["jobs"].values():
        for step in job["steps"]:
            if "run" in step:
                lines.append(step["run"])
    return "\n".join(lines)


def test_workflow_runs_pytest_structure_hook_and_codex_check():
    # @req: BI-8
    assert WORKFLOW_PATH.exists(), f"missing {WORKFLOW_PATH}"
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))

    # PyYAML parses the bare `on:` key as the boolean True, not the
    # string "on" — trigger block lives at workflow[True].
    triggers = workflow.get("on", workflow.get(True))
    assert triggers is not None, "workflow has no trigger block"

    paths_filters = []
    for trigger in ("push", "pull_request"):
        assert trigger in triggers, f"missing {trigger!r} trigger"
        paths_filters.extend(triggers[trigger].get("paths", []))
    assert "think-orbit/**" in paths_filters

    run_lines = _all_run_lines(workflow)
    assert "python3 -m pytest think-orbit/skills/think-orbit/scripts/" in run_lines
    assert (
        "bash .claude/hooks/validate-skill-folder-structure.sh "
        "think-orbit/skills/think-orbit/SKILL.md"
    ) in run_lines
    assert "python3 scripts/sync_codex_manifests.py --check think-orbit" in run_lines
