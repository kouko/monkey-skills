"""The live plan contract has one ordinary task-id form."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WRITE_PLAN = ROOT / "loom-code/skills/write-plan/SKILL.md"


def test_task_ids_use_one_numeric_form_without_reserved_process_tasks() -> None:
    text = WRITE_PLAN.read_text(encoding="utf-8")
    shape = text.split("**Shape.**", 1)[1].split("**Sections.**", 1)[0]
    assert "Task ids are `W<n>-<nn>`" in shape
    assert "W<n>-memory" not in shape
