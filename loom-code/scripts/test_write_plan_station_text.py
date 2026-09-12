"""W2-01 -- write-plan's station text and the plan template cite the plan
row of the artifact charter (`contract/manifest.yaml`, `artifacts.plan.charter`)
instead of restating its caps or its edits-after policy list.

Three literals are load-bearing and pinned here: the SKILL.md sentence
naming `artifacts.plan.charter`, the `loom_checker.py plan
docs/loom/<change-id>/plan.md` command line the station runs before the
plan commit, and the template's one-sentence spec-change-path comment.
"""
from __future__ import annotations

import re
from pathlib import Path

from prose_pin import NEGATION_RE

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "loom-code" / "skills" / "write-plan" / "SKILL.md"
TEMPLATE = REPO / "loom-code" / "contract" / "templates" / "plan.md"
SECOND_VENDOR_REFERENCE = (
    REPO
    / "loom-code"
    / "skills"
    / "write-plan"
    / "references"
    / "second-vendor-ask-and-docs-lint.md"
)


def _has_negation(sentence: str) -> bool:
    return bool(NEGATION_RE.search(sentence))


def _flat_sentences(text: str) -> list[str]:
    flat = " ".join(text.split())
    return [p for p in re.split(r"(?<=[.!?])\s+", flat) if p.strip()]


def test_skill_names_the_plan_charter_row() -> None:
    text = SKILL.read_text(encoding="utf-8")
    hits = [
        s for s in _flat_sentences(text)
        if "artifacts.plan.charter" in s and not _has_negation(s)
    ]
    assert hits, (
        "SKILL.md has no affirmative sentence naming artifacts.plan.charter "
        "-- the task fields' content kinds and caps must cite the charter "
        "row instead of restating it"
    )


def test_skill_runs_the_plan_checker_before_commit() -> None:
    text = SKILL.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "loom_checker.py plan docs/loom/<change-id>/plan.md" in flat, (
        "SKILL.md no longer names the `plan docs/loom/<change-id>/plan.md` "
        "checker command run before the plan commit"
    )


def test_template_states_the_spec_change_path() -> None:
    text = TEMPLATE.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    sentence = (
        "When a spec requirement changes after this commit, the un-landed "
        "tasks it touches are replaced and the reason is named in the "
        "commit message."
    )
    assert sentence in flat, (
        "contract/templates/plan.md no longer carries the spec-change-path "
        "sentence under its Task DAG heading"
    )
    assert not _has_negation(sentence), (
        "the spec-change-path sentence carries a negation token"
    )


def test_template_spec_change_comment_under_task_dag_heading() -> None:
    text = TEMPLATE.read_text(encoding="utf-8")
    dag_idx = text.index("## Task DAG")
    comment_idx = text.index(
        "When a spec requirement changes after this commit", dag_idx
    )
    next_heading = text.find("## ", dag_idx + len("## Task DAG"))
    assert dag_idx < comment_idx, (
        "the spec-change sentence must sit at or after the Task DAG heading"
    )
    if next_heading != -1:
        assert comment_idx < next_heading, (
            "the spec-change sentence has drifted past the Task DAG section"
        )


def test_matcher_spec_change_sentence_negated_rejected() -> None:
    sentence = (
        "When a spec requirement changes after this commit, the un-landed "
        "tasks it touches are never replaced and the reason is not named "
        "in the commit message."
    )
    assert _has_negation(sentence)


# --- W0-01/W2-01 fix round: an engineering spec has a home other than the
# ninth artifact the branch-end finding warned against --------------------


def test_skill_names_the_engineering_spec_path() -> None:
    text = SKILL.read_text(encoding="utf-8")
    sentence = (
        "When a task's rationale outgrows its Risk line, write "
        "`docs/loom/<change-id>/spec.md` from "
        "`contract/templates/spec-minimal.md` — Requirements one per "
        "Acceptance line, Design decision one line per agent-decided fork, "
        "Alternatives considered, Current state evidence, UI flows N/A — carrying the template's five sections and leaving the `confirmed-behavior:` line to product changes."
    )
    flat = " ".join(text.split())
    assert sentence in flat, (
        "SKILL.md no longer carries the engineering-spec-for-oversized-"
        "Risk-line sentence in step 4's `no` branch"
    )
    assert not _has_negation(sentence), (
        "the engineering-spec sentence carries a negation token"
    )


def test_matcher_engineering_spec_sentence_negated_rejected() -> None:
    sentence = (
        "When a task's rationale will not fit its Risk line, write "
        "`docs/loom/<change-id>/spec.md` from "
        "`contract/templates/spec-minimal.md` with no `confirmed-behavior:` "
        "line."
    )
    assert _has_negation(sentence)


# --- W1-02 -- suggest is visible after risk evidence, without becoming a
# fourth decision point ----------------------------------------------------


def test_suggest_runs_policy_after_plan_risk_evidence_exists() -> None:
    text = SKILL.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "second_vendor_policy.py" in flat
    assert "after the plan's Risk lines exist" in flat
    assert "recommendation_reasons" in flat
    assert "notice_kind" in flat


def test_suggest_is_non_blocking_and_has_no_background_listener() -> None:
    text = SECOND_VENDOR_REFERENCE.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "continue without waiting" in flat
    assert "no background listener" in flat
    assert "do not reclassify risk" in flat


def test_ask_still_asks_once_per_full_lane_change() -> None:
    text = SECOND_VENDOR_REFERENCE.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "second-vendor: ask" in flat
    assert "every full-lane change" in flat
    assert "這次要不要用" in text


def test_small_lane_suggest_is_information_only() -> None:
    text = SECOND_VENDOR_REFERENCE.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "small lane" in flat
    assert "informational only" in flat
    assert "next-change-only" in flat


def test_reference_has_no_none_mode_or_per_change_none_answer() -> None:
    text = SECOND_VENDOR_REFERENCE.read_text(encoding="utf-8")
    assert "second-vendor: <cli> | none" not in text
    assert "`<cli>` / `none`" not in text
