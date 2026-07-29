"""Tests for the planning-stage `propose_queue_entry` helper."""

import tomllib

import pytest

from queue_entry import propose_queue_entry

# A realistic slice of docs/dbt-wiki-quality-campaign.md's ## Phase 2 section —
# High/Medium sub-groups, multi-line item bodies, and a neighbouring section
# (## Phase 3) whose own B-less items must not be mistaken for Phase 2 items.
_CAMPAIGN_DOC = """\
# dbt-wiki Quality Campaign — work queue & state

## Phase 1 — loop enablers

- [x] **W1: L2 end-to-end harness** — synthetic dbt project.
- [ ] **W2: cross-doc consistency lint** — mechanically diff the copies.

## Phase 2 — backlog burn-down (from the design review)

High:
- [ ] B1: rescan ~450 lines inline pseudocode -> shipped TDD'd scripts
  (includes real `list | set` TypeError at old :203/:540)
- [ ] B2: materiality map lifecycle — cosmetic-stale pages outlive the map
Medium:
- [ ] B5: distill-spec triplication -> shared-page-rules.md reference

## Phase 3 — generalization sweep (needs W1)

- [ ] G1: fixture matrix expansion — en-language project.
"""

_PLAN_WITH_PASS = """\
# Plan: some Phase 2 item

Plan-document-reviewer verdict: PASS (2026-07-28, 14/14)

## Task 1 — do the thing
"""

_PLAN_WITHOUT_PASS = """\
# Plan: some Phase 2 item

Plan-document-reviewer verdict: PENDING

## Task 1 — do the thing
"""


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_propose_queue_entry_fails_loud_without_reviewer_pass(tmp_path):
    plan_path = _write(tmp_path, "plan.md", _PLAN_WITHOUT_PASS)
    campaign_path = _write(tmp_path, "campaign.md", _CAMPAIGN_DOC)

    with pytest.raises(ValueError) as excinfo:
        propose_queue_entry("B1", plan_path, campaign_path, 5)

    assert "Plan-document-reviewer verdict: PASS" in str(excinfo.value)


def test_propose_queue_entry_happy_path_returns_parseable_toml(tmp_path):
    plan_path = _write(tmp_path, "plan.md", _PLAN_WITH_PASS)
    campaign_path = _write(tmp_path, "campaign.md", _CAMPAIGN_DOC)

    block = propose_queue_entry("B1", plan_path, campaign_path, 5)

    assert 'id = "B1"' in block
    assert str(plan_path) in block
    assert "5" in block

    parsed = tomllib.loads(block)
    entry = parsed["change"][0]
    assert entry["id"] == "B1"
    assert entry["plan"] == str(plan_path)
    assert entry["budgets"]["run"] == 5


def test_propose_queue_entry_fails_loud_missing_reviewer_pass_names_verdict(tmp_path):
    plan_path = _write(tmp_path, "plan.md", _PLAN_WITHOUT_PASS)
    campaign_path = _write(tmp_path, "campaign.md", _CAMPAIGN_DOC)

    with pytest.raises(ValueError, match="Plan-document-reviewer verdict: PASS"):
        propose_queue_entry("B2", plan_path, campaign_path, 3)


def test_propose_queue_entry_fails_loud_item_not_in_phase2(tmp_path):
    plan_path = _write(tmp_path, "plan.md", _PLAN_WITH_PASS)
    campaign_path = _write(tmp_path, "campaign.md", _CAMPAIGN_DOC)

    with pytest.raises(ValueError) as excinfo:
        propose_queue_entry("B99", plan_path, campaign_path, 5)

    assert "B99" in str(excinfo.value)


def test_propose_queue_entry_ignores_items_outside_phase2_section(tmp_path):
    # G1 lives under ## Phase 3, not ## Phase 2 — must not be accepted.
    plan_path = _write(tmp_path, "plan.md", _PLAN_WITH_PASS)
    campaign_path = _write(tmp_path, "campaign.md", _CAMPAIGN_DOC)

    with pytest.raises(ValueError) as excinfo:
        propose_queue_entry("G1", plan_path, campaign_path, 5)

    assert "G1" in str(excinfo.value)
