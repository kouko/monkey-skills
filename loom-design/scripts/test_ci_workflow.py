"""loom-design must keep its own CI workflow, running the whole
`loom-design/scripts/` suite in one invocation, with path triggers on both
`pull_request` and `push`.

Ported from `scripts/pipeline/test_pipeline_ci_workflow.py`, which was
deleted with the pipeline station at loom 1.0. The guard it carried is not
pipeline-specific: a path trigger that stops matching what the suite reads
is fail-open, and nothing else in the repo would notice. Two of the paths
it pinned changed with the cut — the workflow renamed itself from
`loom-pipeline-ci.yml` to `loom-design-ci.yml`, and `loom-memory` moved to
loom-code long ago, replaced here by the contract package the design
stations actually read.
"""
from pathlib import Path

import yaml

WORKFLOW = (
    Path(__file__).resolve().parents[2]
    / ".github"
    / "workflows"
    / "loom-design-ci.yml"
)

# Every repo path this suite reads at test time. A file the suite reads but
# the workflow does not watch merges ungated.
REQUIRED_PATHS = (
    "loom-design/**",
    "loom-code/hooks/**",
    "loom-code/contract/**",
    ".claude-plugin/marketplace.json",
    ".github/workflows/loom-design-ci.yml",
)


def _load_workflow():
    assert WORKFLOW.exists(), f"missing {WORKFLOW}"
    text = WORKFLOW.read_text(encoding="utf-8")
    return text, yaml.safe_load(text)


def test_workflow_paths():
    text, data = _load_workflow()

    # PyYAML's SafeLoader reads the bare `on:` key as the boolean True
    # (YAML 1.1), so accept either spelling rather than pinning the quirk.
    on_block = data.get("on", data.get(True))
    assert on_block is not None, "workflow must have an `on:` block"

    for trigger_name in ("pull_request", "push"):
        trigger = on_block[trigger_name]
        assert trigger["branches"] == ["main"], (
            f"{trigger_name} must target branches: [main]"
        )
        paths = trigger["paths"]
        for expected_path in REQUIRED_PATHS:
            assert expected_path in paths, (
                f"{trigger_name}.paths missing {expected_path!r}"
            )

    assert "python3 -m pytest loom-design/scripts/ -q" in text, (
        "workflow must run the unified loom-design/scripts/ pytest suite"
    )


def test_job_display_name_is_unchanged_by_the_rename():
    """The workflow FILE was renamed at 1.0; the job's display name was not.

    Branch protection binds required checks by display name, so a rename of
    this string is a settings change, not a refactor.
    """
    _, data = _load_workflow()
    names = {job.get("name") for job in data["jobs"].values()}
    assert "loom-design pytest" in names, (
        f"job display name must stay 'loom-design pytest'; found {names}"
    )
