"""Tests for the read-only decision-map delivery-progress query."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import map_progress  # noqa: E402


SCRIPT = Path(__file__).parent / "map_progress.py"
SKILL_DIR = Path(__file__).parent.parent
MAP_FORMAT_MD = SKILL_DIR / "references" / "map-format.md"
SKILL_MD = SKILL_DIR / "SKILL.md"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _arc(tmp_path: Path, *, status: str = "claimed", with_plan: bool = True) -> tuple[Path, Path, Path]:
    ticket = tmp_path / "docs/loom/maps/wayfinder/tickets/deliver.md"
    brief = tmp_path / "docs/loom/specs/deliver.md"
    plan = tmp_path / "docs/loom/plans/deliver.md"
    ticket_relative = ticket.relative_to(tmp_path).as_posix()
    brief_relative = brief.relative_to(tmp_path).as_posix()
    _write(ticket, f"---\ntype: delivery\nstatus: {status}\nbrief: {brief_relative}\n---\n")
    _write(brief, f"Outcome Map ticket: {ticket_relative}\n")
    if with_plan:
        _write(plan, """# Plan: deliver

**Source brief**: docs/loom/specs/deliver.md
Goal: Ship.
Stage: sdd:wave-1

## Task 1 — ship

- Status: pending
""")
    return ticket, brief, plan


def test_progress_resolves_ticket_brief_plan_without_writes(
    tmp_path: Path,
) -> None:
    # @req: REQ-81
    map_md = tmp_path / "docs" / "loom" / "maps" / "wayfinder" / "MAP.md"
    _write(map_md, "original map bytes\n")
    ticket = map_md.parent / "tickets" / "deliver-search.md"
    brief = tmp_path / "docs" / "loom" / "specs" / "deliver-search.md"
    plan = tmp_path / "docs" / "loom" / "plans" / "delivery.md"
    ticket_relative = ticket.relative_to(tmp_path).as_posix()
    brief_relative = brief.relative_to(tmp_path).as_posix()
    _write(
        ticket,
        f"---\ntype: delivery\nstatus: claimed\nbrief: {brief_relative}\n---\n",
    )
    _write(brief, f"# Deliver search\n\nOutcome Map ticket: {ticket_relative}\n")
    _write(
        plan,
        """# Plan: delivery

**Source brief**: docs/loom/specs/deliver-search.md

Goal: Ship the delivery.
Stage: sdd:wave-1

## Task 1 — finish it

- Status: done(abc1234)

## Task 2 — review it

- Status: claimed(@worker)

""",
    )
    sources = (map_md, ticket, brief, plan)
    before = {path: path.read_bytes() for path in sources}

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(ticket), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert f"ticket: {ticket_relative}" in result.stdout
    assert f"brief: {brief_relative}" in result.stdout
    assert "plan: docs/loom/plans/delivery.md" in result.stdout
    assert "phase: implementing" in result.stdout
    assert {path: path.read_bytes() for path in sources} == before
    assert "map_progress.py" in MAP_FORMAT_MD.read_text(encoding="utf-8")
    assert "map_progress.py <plan-path> --repo-root <path>" in SKILL_MD.read_text(
        encoding="utf-8"
    )


def test_map_progress_preserves_legacy_plan_query_output(tmp_path: Path) -> None:
    plan = tmp_path / "docs" / "loom" / "plans" / "delivery.md"
    _write(
        plan,
        """# Plan: delivery

Goal: Ship the delivery.
Stage: sdd:wave-1

## Task 1 — finish it

- Status: done(abc1234)

## Task 2 — review it

- Status: blocked(needs human decision)

## Notes

Map part: wayfinder / Part: delivery
""",
    )
    before = plan.read_bytes()

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "map delivery-progress: wayfinder / delivery" in result.stdout
    assert "plan: delivery.md" in result.stdout
    assert "state: blocked" in result.stdout
    assert plan.read_bytes() == before
    assert map_progress.derive_progress(plan.read_text(encoding="utf-8")) == (
        "wayfinder",
        "delivery",
        "blocked",
    )


def test_progress_reports_closed_delivery_as_delivered_with_its_arc(
    tmp_path: Path,
) -> None:
    # @req: REQ-81
    ticket = tmp_path / "docs/loom/maps/wayfinder/tickets/deliver.md"
    brief = tmp_path / "docs/loom/specs/deliver.md"
    plan = tmp_path / "docs/loom/plans/deliver.md"
    ticket_relative = ticket.relative_to(tmp_path).as_posix()
    brief_relative = brief.relative_to(tmp_path).as_posix()
    _write(ticket, f"---\ntype: delivery\nstatus: closed\nbrief: {brief_relative}\n---\n")
    _write(brief, f"Outcome Map ticket: {ticket_relative}\n")
    _write(
        plan,
        """# Plan: deliver

**Source brief**: docs/loom/specs/deliver.md
Goal: Ship.
Stage: finishing

## Task 1 — ship

- Status: done(abc1234)
""",
    )
    sources = (ticket, brief, plan)
    before = {path: path.read_bytes() for path in sources}

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(ticket), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert f"brief: {brief_relative}" in result.stdout
    assert "plan: docs/loom/plans/deliver.md" in result.stdout
    assert "phase: delivered" in result.stdout
    assert {path: path.read_bytes() for path in sources} == before


def test_progress_reports_unbriefed_and_briefed_without_writes(tmp_path: Path) -> None:
    # @req: REQ-81
    unbriefed = tmp_path / "docs/loom/maps/wayfinder/tickets/unbriefed.md"
    _write(unbriefed, "---\ntype: delivery\nstatus: claimed\n---\n")
    before = unbriefed.read_bytes()
    unbriefed_result = subprocess.run([sys.executable, str(SCRIPT), str(unbriefed), "--repo-root", str(tmp_path)], capture_output=True, text=True)
    assert unbriefed_result.returncode == 0, unbriefed_result.stderr
    assert "phase: unbriefed" in unbriefed_result.stdout
    assert unbriefed.read_bytes() == before

    ticket, brief, plan = _arc(tmp_path, with_plan=False)
    before = {path: path.read_bytes() for path in (ticket, brief)}
    briefed_result = subprocess.run([sys.executable, str(SCRIPT), str(ticket), "--repo-root", str(tmp_path)], capture_output=True, text=True)
    assert briefed_result.returncode == 0, briefed_result.stderr
    assert "phase: briefed" in briefed_result.stdout
    assert {path: path.read_bytes() for path in (ticket, brief)} == before


@pytest.mark.parametrize(
    ("stage", "status", "phase"),
    [("planning", "pending", "planning"), ("sdd:wave-1", "pending", "implementing"), ("review:round-1", "claimed(@reviewer)", "reviewing"), ("finishing", "done(abc1234)", "finishing"), ("sdd:wave-1", "blocked", "repair-required")],
)
def test_progress_derives_plan_phases_without_writes(tmp_path: Path, stage: str, status: str, phase: str) -> None:
    # @req: REQ-81
    ticket, brief, plan = _arc(tmp_path)
    _write(plan, plan.read_text(encoding="utf-8").replace("Stage: sdd:wave-1", f"Stage: {stage}").replace("- Status: pending", f"- Status: {status}"))
    sources = (ticket, brief, plan)
    before = {path: path.read_bytes() for path in sources}
    result = subprocess.run([sys.executable, str(SCRIPT), str(ticket), "--repo-root", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert f"phase: {phase}" in result.stdout
    assert {path: path.read_bytes() for path in sources} == before


@pytest.mark.parametrize("fault", ["malformed", "multiple", "binding", "unreadable"])
def test_progress_refuses_broken_delivery_arc_without_writes(tmp_path: Path, fault: str) -> None:
    # @req: REQ-81
    ticket, brief, plan = _arc(tmp_path)
    if fault == "malformed":
        _write(plan, plan.read_text(encoding="utf-8").replace("Stage: sdd:wave-1", "Stage: unknown"))
    elif fault == "multiple":
        _write(tmp_path / "docs/loom/plans/another.md", plan.read_text(encoding="utf-8"))
    elif fault == "unreadable":
        plan.unlink()
        plan.mkdir()
    else:
        _write(brief, "# broken reciprocal binding\n")
    sources = tuple(path for path in (ticket, brief, plan, tmp_path / "docs/loom/plans/another.md") if path.is_file())
    before = {path: path.read_bytes() for path in sources}
    result = subprocess.run([sys.executable, str(SCRIPT), str(ticket), "--repo-root", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == (1 if fault == "unreadable" else 2)
    assert result.stderr.startswith("Error: ")
    assert {path: path.read_bytes() for path in sources} == before
    if fault == "unreadable":
        assert plan.is_dir()


def test_progress_refuses_duplicate_source_brief_without_writes(tmp_path: Path) -> None:
    # @req: REQ-81
    ticket, brief, plan = _arc(tmp_path)
    _write(
        plan,
        plan.read_text(encoding="utf-8").replace(
            "Goal: Ship.", "**Source brief**: docs/loom/specs/deliver.md\nGoal: Ship."
        ),
    )
    sources = (ticket, brief, plan)
    before = {path: path.read_bytes() for path in sources}
    result = subprocess.run([sys.executable, str(SCRIPT), str(ticket), "--repo-root", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 2
    assert "Source brief" in result.stderr
    assert {path: path.read_bytes() for path in sources} == before


def test_progress_refuses_symlinked_plans_directory_without_writes(tmp_path: Path) -> None:
    # @req: REQ-81
    ticket, brief, plan = _arc(tmp_path, with_plan=False)
    plans_dir = plan.parent
    external = tmp_path.parent / "external-plans"
    _write(external / "delivery.md", "external plan bytes\n")
    plans_dir.symlink_to(external, target_is_directory=True)
    before = {path: path.read_bytes() for path in (ticket, brief, external / "delivery.md")}
    result = subprocess.run([sys.executable, str(SCRIPT), str(ticket), "--repo-root", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 2
    assert "symlink" in result.stderr
    assert {path: path.read_bytes() for path in before} == before


def test_progress_refuses_missing_and_symlink_targets_without_writes(tmp_path: Path) -> None:
    # @req: REQ-81
    missing = tmp_path / "docs/loom/maps/wayfinder/tickets/missing.md"
    missing_result = subprocess.run([sys.executable, str(SCRIPT), str(missing), "--repo-root", str(tmp_path)], capture_output=True, text=True)
    assert missing_result.returncode == 1

    ticket, brief, plan = _arc(tmp_path)
    ticket_link = ticket.with_name("ticket-link.md")
    ticket_link.symlink_to(ticket)
    plan_link = plan.with_name("plan-link.md")
    plan_link.symlink_to(plan)
    sources = (ticket, brief, plan)
    before = {path: path.read_bytes() for path in sources}
    ticket_result = subprocess.run([sys.executable, str(SCRIPT), str(ticket_link), "--repo-root", str(tmp_path)], capture_output=True, text=True)
    assert ticket_result.returncode == 2
    plan_result = subprocess.run([sys.executable, str(SCRIPT), str(plan_link), "--repo-root", str(tmp_path)], capture_output=True, text=True)
    assert plan_result.returncode == 2
    assert {path: path.read_bytes() for path in sources} == before
