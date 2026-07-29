"""Planning-stage helper: draft a batch-mode `[[change]]` queue entry.

`propose_queue_entry` is the PLANNING-stage tool (the execution routine in
ROUTINE.md never calls it). It validates that a Phase 2 backlog item's plan
is actually frozen — the plan file carries a
``Plan-document-reviewer verdict: PASS`` line — and that the item id really
exists as an unfinished checklist line under the campaign doc's
``## Phase 2`` section, then emits the TOML block a human pastes into
``docs/loom/QUEUE.toml`` for ``loom-pipeline/scripts/batch_queue.py`` to
consume.

Fail-loud, no improvised defaults — mirrors ``batch_queue.py``'s
``load_queue`` stance: a missing verdict or a bogus item id RAISES rather
than guessing. See docs/loom/specs/2026-07-28-phase2-loop-execution-only.md.
"""

import re
from pathlib import Path

# The plan header's reviewer-verdict line — mirrors batch_queue.py's own
# _PLAN_REVIEWER_PASS_PATTERN: anchored to line start (a header FIELD, not a
# whole-body substring), tolerant of the markdown bold-marker variants
# (`**Plan-document-reviewer verdict**: PASS`) and the plain form. PENDING
# never matches.
_PLAN_REVIEWER_PASS_PATTERN = re.compile(
    r"^\*{0,2}Plan-document-reviewer verdict\*{0,2}\s*:\s*\*{0,2}\s*PASS\b",
    re.MULTILINE,
)

# Phase 2 section scanning — same spirit as the retired backlog_parser.py:
# scan only within the `## Phase 2` heading up to the next `## ` heading, so a
# similarly-numbered item in another section is never mistaken for a Phase 2
# item.
_PHASE2_HEADING = re.compile(r"^##\s+Phase 2\b")
_SECTION_HEADING = re.compile(r"^##\s+")
_ITEM = re.compile(r"^- \[[ xX]\] (?P<id>B\d+):")


def _phase2_item_ids(campaign_text: str) -> set[str]:
    """Return every ``B<n>`` id that appears as a checklist line under
    ``## Phase 2`` (checked or unchecked), scoped to that section only."""
    lines = campaign_text.splitlines()
    start = next(
        (i + 1 for i, line in enumerate(lines) if _PHASE2_HEADING.match(line)),
        None,
    )
    if start is None:
        return set()
    end = next(
        (j for j in range(start, len(lines)) if _SECTION_HEADING.match(lines[j])),
        len(lines),
    )
    return {
        m.group("id")
        for line in lines[start:end]
        if (m := _ITEM.match(line))
    }


def _toml_escape(value: str) -> str:
    """Escape a string for a TOML basic (double-quoted) string."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def propose_queue_entry(
    item_id: str,
    plan_path: Path,
    campaign_doc_path: Path,
    budget_run: int,
) -> str:
    """Draft the ``[[change]]`` TOML block for a frozen Phase 2 item.

    ``plan_path`` must carry a ``Plan-document-reviewer verdict: PASS`` line
    (the freeze gate) and ``item_id`` (e.g. ``"B1"``) must appear as a
    ``- [ ] B<n>: ...`` / ``- [x] B<n>: ...`` line under
    ``campaign_doc_path``'s ``## Phase 2`` section specifically. Either
    check failing RAISES ``ValueError`` naming the missing thing — no
    improvised default, no silent skip.

    ``plan_path`` is emitted verbatim as the entry's ``plan`` field; callers
    pass a project-relative path (the value ``batch_queue.py``'s
    ``check_frozen`` resolves against the project root). Returns valid TOML
    (``tomllib``-parseable) carrying ``id``, ``plan``, and ``budgets.run``.
    """
    plan_text = Path(plan_path).read_text(encoding="utf-8")
    if not _PLAN_REVIEWER_PASS_PATTERN.search(plan_text):
        raise ValueError(
            f'propose_queue_entry: plan "{plan_path}" carries no '
            '"Plan-document-reviewer verdict: PASS" line — refusing to queue '
            "an unfrozen item (fail-loud: no defaults, no silent skip)."
        )

    campaign_text = Path(campaign_doc_path).read_text(encoding="utf-8")
    if item_id not in _phase2_item_ids(campaign_text):
        raise ValueError(
            f'propose_queue_entry: item "{item_id}" is not a Phase 2 '
            f'checklist item in "{campaign_doc_path}" — refusing to queue an '
            "id that does not exist under ## Phase 2 (fail-loud)."
        )

    return (
        "[[change]]\n"
        f'id = "{_toml_escape(item_id)}"\n'
        f'plan = "{_toml_escape(str(plan_path))}"\n'
        f"budgets.run = {int(budget_run)}\n"
    )
