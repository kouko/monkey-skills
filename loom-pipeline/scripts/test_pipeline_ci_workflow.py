"""RED-first test: loom-pipeline must have its own CI workflow file that
runs its pytest suite as a separate invocation (same-basename collision
rule per loom-siblings-ci.yml) with path triggers on both pull_request
and push, covering loom-pipeline/**, the marketplace.json fail-open
guard, and the workflow file itself."""
from pathlib import Path

import yaml


def _load_workflow():
    repo_root = Path(__file__).parents[2]
    workflow_path = repo_root / ".github" / "workflows" / "loom-pipeline-ci.yml"
    assert workflow_path.exists(), f"missing {workflow_path}"
    # yaml.safe_load chokes on the bare `on:` key (YAML 1.1 parses it as
    # boolean True) unless we use the full_load/safe_load with a custom
    # resolver workaround; PyYAML's SafeLoader maps `on` -> True by
    # default. Guard against that by reading raw text for path assertions
    # and also parsing structurally for the run command.
    text = workflow_path.read_text()
    data = yaml.safe_load(text)
    return text, data


def test_workflow_paths():
    text, data = _load_workflow()

    # PyYAML's SafeLoader interprets the bare `on:` key as boolean True.
    on_block = data.get("on", data.get(True))
    assert on_block is not None, "workflow must have an `on:` block"

    for trigger_name in ("pull_request", "push"):
        trigger = on_block[trigger_name]
        assert trigger["branches"] == ["main"], (
            f"{trigger_name} must target branches: [main]"
        )
        paths = trigger["paths"]
        for expected_path in (
            "loom-pipeline/**",
            ".claude-plugin/marketplace.json",
            ".github/workflows/loom-pipeline-ci.yml",
        ):
            assert expected_path in paths, (
                f"{trigger_name}.paths missing {expected_path!r}"
            )

    assert "python3 -m pytest loom-pipeline/scripts/" in text, (
        "workflow must run the loom-pipeline/scripts/ pytest suite"
    )
