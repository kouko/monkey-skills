"""Integration proof: propose_queue_entry output round-trips through batch_queue.

Proves the planning-stage helper's TOML is genuinely consumable by
loom-pipeline's batch_queue.py: load_queue parses the drafted entry and
check_frozen returns eligible via the Form B (brief+plan) path — no
docs/loom/<id>/ change folder exists for the synthetic fixture, so the
plan's own ``Plan-document-reviewer verdict: PASS`` line is the freeze gate.
"""

import importlib.util
from pathlib import Path

from queue_entry import propose_queue_entry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BATCH_QUEUE_PATH = _REPO_ROOT / "loom-pipeline" / "scripts" / "batch_queue.py"


def _load_batch_queue():
    """Import loom-pipeline's batch_queue.py by file path — a cross-plugin
    sibling module in the same repo — without touching sys.path or any
    shared conftest (scoped to this test module only)."""
    spec = importlib.util.spec_from_file_location(
        "loom_pipeline_batch_queue", _BATCH_QUEUE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_PLAN_WITH_PASS = """\
# Plan: synthetic Phase 2 item

Plan-document-reviewer verdict: PASS (2026-07-28, 14/14)

## Task 1 — do the thing
"""

_CAMPAIGN_DOC = """\
# dbt-wiki Quality Campaign

## Phase 2 — backlog burn-down

- [ ] B1: rescan inline pseudocode -> shipped TDD'd scripts
"""


def test_proposed_entry_passes_batch_queue_freeze_check(tmp_path, monkeypatch):
    batch_queue = _load_batch_queue()
    project_path = tmp_path

    # Plan fixture lives inside the temp project root. propose_queue_entry
    # emits `plan` verbatim as str(plan_path), and check_frozen resolves it
    # as (project_path / entry["plan"]).resolve() — so pass a PROJECT-RELATIVE
    # path (matching how a real caller queues an entry) and chdir into the
    # project root so propose_queue_entry can read it during the call.
    plan_rel = Path("docs/loom/plans/synthetic-plan.md")
    plan_abs = project_path / plan_rel
    plan_abs.parent.mkdir(parents=True)
    plan_abs.write_text(_PLAN_WITH_PASS, encoding="utf-8")

    campaign_path = project_path / "campaign.md"
    campaign_path.write_text(_CAMPAIGN_DOC, encoding="utf-8")

    monkeypatch.chdir(project_path)
    block = propose_queue_entry("B1", plan_rel, campaign_path, 5)
    assert block.count("[[change]]") == 1
    assert 'plan = "docs/loom/plans/synthetic-plan.md"' in block

    # (1)+(2): write the drafted block into a temp QUEUE.toml under [[change]].
    queue_path = project_path / "docs" / "loom" / "QUEUE.toml"
    queue_path.write_text(block, encoding="utf-8")

    # (3): load_queue parses it without raising and yields the one drafted entry.
    entries = batch_queue.load_queue(queue_path)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["id"] == "B1"
    assert entry["plan"] == "docs/loom/plans/synthetic-plan.md"
    assert entry["budgets"]["run"] == 5

    # (4): Form B fires — no docs/loom/B1/ change folder exists, so the plan's
    # own PASS line is the gate; check_frozen returns (True, ...brief+plan...).
    assert not (project_path / "docs" / "loom" / "B1").exists()
    eligible, reason = batch_queue.check_frozen(entry, project_path, _REPO_ROOT)
    assert eligible is True
    assert "brief+plan form" in reason
