"""branch-end-02: write-plan's Shape task-id sentence names the one
exception to the numeric task-id form.

docs/loom/2026-09-05-memory-step-before-branch-end-and-prose-pin-rule/
review.json, rev-be-ms-codex round-1 finding: the Shape contract says
all task ids are `W<n>-<nn>`, then reserves the incompatible `W<n>-memory`
form a few bullets later with no exception stated -- following the id
rule literally forbids the very id the plan's last-wave bullet requires.
This test pins that the id sentence in loom-code/skills/write-plan/
SKILL.md's Shape section names `W<n>-memory` as the one named exception.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WRITE_PLAN_SKILL = REPO / "loom-code" / "skills" / "write-plan" / "SKILL.md"

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _sentences(text: str) -> list[str]:
    flat = " ".join(text.split())
    return [p for p in _SENTENCE_SPLIT.split(flat) if p.strip()]


def _shape_section() -> str:
    text = WRITE_PLAN_SKILL.read_text(encoding="utf-8")
    section = text.split("**Shape.**", 1)[1]
    section = section.split("**Sections.**", 1)[0]
    return section


def _task_id_sentence() -> str:
    section = _shape_section()
    for sentence in _sentences(section):
        if "W<n>-<nn>" in sentence.replace("`", "") or "W<n>-<nn>" in sentence:
            return sentence
    raise AssertionError("no sentence in write-plan's Shape section names W<n>-<nn>")


def test_taskidsentence_names_wnnn_form() -> None:
    sentence = _task_id_sentence()
    assert "W<n>-<nn>" in sentence.replace("`", "")


def test_taskidsentence_names_wnmemory_as_named_exception() -> None:
    """The id sentence must name `W<n>-memory` as an EXCEPTION to the
    numeric form -- not merely mention it elsewhere in the section,
    since a bare co-occurrence would pass even if the two bullets stayed
    contradictory."""
    sentence = _task_id_sentence()
    flat = sentence.replace("`", "")
    assert "W<n>-memory" in flat, (
        "the task-id sentence does not name the reserved W<n>-memory id"
    )
    assert "exception" in flat.lower(), (
        "the task-id sentence does not call W<n>-memory an exception to "
        "the numeric form"
    )


def test_synthetic_mentionwithoutexception_rejected() -> None:
    """Self-test: a sentence that merely mentions W<n>-memory alongside
    W<n>-<nn>, without calling it an exception, must be rejected by the
    same substring check used above -- guards against a fix that restates
    both ids side by side without resolving the contradiction."""
    synthetic = "Task ids are W<n>-<nn> and the last wave also has W<n>-memory."
    assert "exception" not in synthetic.lower()
