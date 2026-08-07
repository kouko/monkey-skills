"""Tests for the queue-entry helpers (planning-stage authoring + the
execution stage's campaign-doc description lookup)."""

import tomllib

import pytest

from queue_entry import lookup_backlog_description, propose_queue_entry
from safety_gates import requires_real_agent_surface

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


# --- lookup_backlog_description (execution-stage scope-guard input) ---------
#
# ROUTINE.md Step 4 calls `requires_real_agent_surface` on the picked entry's
# description. No description exists in batch_queue.py's dispatch payload, in
# `load_queue`'s accepted fields, or in `propose_queue_entry`'s emitted block —
# the campaign doc's own Phase 2 checklist line IS the description of record,
# and this is the only supported way to obtain it.

# B7's real-agent signal ("e2e run") sits on the WRAPPED continuation line, not
# the head line — the case a head-line-only lookup would silently pass through.
_CAMPAIGN_DOC_WRAPPED_SIGNAL = """\
# dbt-wiki Quality Campaign — work queue & state

## Phase 2 — backlog burn-down

- [ ] B6: init SKILL.md pseudocode duplicating build_evidence_pages.py
- [ ] B7: log.md template dual-spec — needs a real e2e run against the
  headless harness to confirm the dialect line
- [ ] B8: stale in-file version headers

## Phase 3 — generalization sweep
"""


def test_lookup_backlog_description_includes_wrapped_continuation_lines(tmp_path):
    campaign_path = _write(tmp_path, "campaign.md", _CAMPAIGN_DOC)

    description = lookup_backlog_description("B1", campaign_path)

    assert "rescan ~450 lines inline pseudocode" in description
    # The wrapped second line belongs to B1 and must be part of its description.
    assert "TypeError" in description
    # ...and the NEXT item's text must not bleed in.
    assert "materiality map" not in description


def test_lookup_backlog_description_feeds_scope_guard_on_wrapped_signal(tmp_path):
    # The safety-critical composition: a signal on the continuation line must
    # still trip the fail-closed guard.
    campaign_path = _write(tmp_path, "campaign.md", _CAMPAIGN_DOC_WRAPPED_SIGNAL)

    assert requires_real_agent_surface(
        lookup_backlog_description("B7", campaign_path)
    ) is True
    assert requires_real_agent_surface(
        lookup_backlog_description("B8", campaign_path)
    ) is False


# B9's signal sits in a continuation paragraph separated by a BLANK line —
# still one list item under CommonMark, and one ordinary markdown edit away in
# a hand-maintained doc. Round-2 review found the blank line ended the item,
# dropping the paragraph and failing the guard OPEN.
_CAMPAIGN_DOC_BLANK_LINE_CONTINUATION = """\
# dbt-wiki Quality Campaign — work queue & state

## Phase 2 — backlog burn-down

- [ ] B9: redistill-vs-review stale-clearing convention mismatch

  Confirming this needs a real e2e run against the headless harness before
  the convention can be pinned.

- [ ] B10: sync couples to sibling skills by step number

## Phase 3 — generalization sweep
"""


def test_lookup_backlog_description_keeps_blank_line_separated_continuation(tmp_path):
    campaign_path = _write(
        tmp_path, "campaign.md", _CAMPAIGN_DOC_BLANK_LINE_CONTINUATION
    )

    description = lookup_backlog_description("B9", campaign_path)

    assert "real e2e run" in description, (
        "a blank line does not end a list item — dropping the continuation "
        "hands the fail-closed guard a truncated description, which fails OPEN"
    )
    assert "sync couples" not in description, "next item must not bleed in"
    assert requires_real_agent_surface(description) is True


def test_lookup_backlog_description_fails_loud_for_unknown_item(tmp_path):
    campaign_path = _write(tmp_path, "campaign.md", _CAMPAIGN_DOC)

    with pytest.raises(ValueError) as excinfo:
        lookup_backlog_description("B99", campaign_path)

    assert "B99" in str(excinfo.value)


def test_lookup_backlog_description_scoped_to_phase2_section(tmp_path):
    # G1 lives under ## Phase 3 — the execution stage must not scope-guard
    # against a description from another section.
    campaign_path = _write(tmp_path, "campaign.md", _CAMPAIGN_DOC)

    with pytest.raises(ValueError) as excinfo:
        lookup_backlog_description("G1", campaign_path)

    assert "G1" in str(excinfo.value)
