"""Structural grep-window test guarding finishing-a-development-branch's
Task 4 update (`docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md`):
the flow diagram / delegation table now NAME the three-way review dispatch
(docs-only / mixed / code-only) that `requesting-code-review` Step 1 owns,
and the verdict-routing Step 3 text surfaces `requesting-docs-review`'s
2-round-cap STOP to the user instead of folding it into the existing
NEEDS_REVISION "digest silently" fix-and-re-review loop.

SKILL.md is a prompt/contract artifact, not executable code: nothing
importable observes whether the orchestrator actually treats a cap-STOP
differently from an ordinary NEEDS_REVISION loop. This file IS the
instruction the orchestrator reads at the routing moment, so its
correctness condition is the PRESENCE of the load-bearing phrases —
same convention as test_docs_review_mode.py.

Scope: assertions are window-scoped per
docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md — each
window is anchored on a unique line (`Phase 1: requesting-code-review`,
the `| 1 |` delegation row, `3. Dispatch requesting-code-review` /
`4. Before applying`) verified unique via grep before writing this file.

Polarity guard: `test_cap_stop_not_folded_into_digest_silently_loop`
proves the cap-STOP bullet and the digest-silently bullet are kept
textually distinct (the STOP sentence does not itself say "digest
silently") AND that the digest-silently bullet explicitly carves out
the cap-STOP as its one exception — inverting either half (e.g.
splicing "digest silently" into the STOP bullet, or dropping the
exception clause) must fail the same check that passes on the real
text.

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILL_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "finishing-a-development-branch"
    / "SKILL.md"
)


def _text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Whitespace-normalize so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _flow_diagram_window(text: str) -> str:
    """Phase 1 flow-diagram block: from its anchor to the Phase 2 anchor."""
    start = text.index("Phase 1: requesting-code-review")
    end = text.index("Phase 2: verification-before-completion", start)
    return text[start:end]


def _delegation_row(text: str) -> str:
    """The `| 1 | ...` delegation-table row (single line)."""
    m = re.search(r"^\|\s*1\s*\|.*$", text, re.MULTILINE)
    assert m, "delegation table row '| 1 | ...' not found"
    return m.group(0)


def _step3_window(text: str) -> str:
    """Step 3 (verdict routing) through just before Step 4."""
    start = text.index("3. Dispatch requesting-code-review")
    end = text.index("4. Before applying any review findings", start)
    return text[start:end]


def _cap_stop_bullet(step3: str) -> str:
    """The sub-bullet introducing the docs-arm cap-STOP surfacing rule."""
    m = re.search(r"-\s+If the docs arm.*?(?=\n\s+-\s|\Z)", step3, re.DOTALL)
    assert m, "docs-arm cap-STOP bullet not found inside Step 3"
    return m.group(0)


def _digest_silently_bullet(step3: str) -> str:
    """The 'Explicit contract' NEEDS_REVISION-loop bullet."""
    m = re.search(r"-\s+Explicit contract:.*?(?=\n\d+\.|\Z)", step3, re.DOTALL)
    assert m, "'Explicit contract' digest-silently bullet not found inside Step 3"
    return m.group(0)


class TestFlowDiagramNamesDocsArm:
    def test_phase1_names_three_way_dispatch(self):
        window = _norm(_flow_diagram_window(_text()))
        assert "three-way" in window, (
            "Phase 1 flow diagram must name the three-way review dispatch"
        )

    def test_phase1_names_docs_only_delegate(self):
        window = _norm(_flow_diagram_window(_text()))
        assert "requesting-docs-review" in window, (
            "Phase 1 flow diagram must name requesting-docs-review as the docs-only delegate"
        )

    def test_phase1_still_names_mixed_and_code_only(self):
        window = _norm(_flow_diagram_window(_text()))
        assert "mixed" in window.lower(), "Phase 1 must name the mixed-branch path"
        assert "code-only" in window.lower() or "code panel" in window.lower(), (
            "Phase 1 must name the code-only path"
        )


class TestDelegationTableNamesDocsArm:
    def test_row_names_three_way(self):
        row = _norm(_delegation_row(_text()))
        assert "three-way" in row.lower(), (
            "Delegation table row 1 must name the three-way dispatch"
        )
        assert "requesting-docs-review" in row, (
            "Delegation table row 1 must name requesting-docs-review"
        )

    def test_row_stays_one_line(self):
        """Pointer-style constraint: this file delegates, it does not restate
        requesting-code-review's routing logic — the row must remain a single
        table line, not a multi-line paragraph."""
        row = _delegation_row(_text())
        assert "\n" not in row


class TestVerdictRoutingSurfacesCapStop:
    def test_cap_stop_bullet_present(self):
        bullet = _norm(_cap_stop_bullet(_step3_window(_text())))
        assert "requesting-docs-review" in bullet
        assert re.search(r"2-round.cap", bullet), (
            "cap-STOP bullet must name the 2-round cap"
        )
        assert "stop" in bullet.lower()

    def test_cap_stop_bullet_surfaces_to_user_not_silent_loop(self):
        bullet = _norm(_cap_stop_bullet(_step3_window(_text())))
        assert "surface" in bullet.lower() and "user" in bullet.lower(), (
            "cap-STOP bullet must surface surviving findings to the user"
        )
        assert "explicit user authorization" in bullet.lower() or (
            "explicit" in bullet.lower() and "authoriz" in bullet.lower()
        ), "a third review round must require explicit user authorization"

    def test_cap_stop_bullet_states_needs_revision_trigger(self):
        """T4 code-quality review finding: the cap-STOP bullet must state
        its trigger explicitly as round-2 NEEDS_REVISION, and name that a
        round-2 PASS_WITH_NOTES auto-proceeds per the bullet above -- so no
        precedence question survives between the two bullets."""
        bullet = _norm(_cap_stop_bullet(_step3_window(_text()))).lower()
        assert "round 2 ended with needs_revision" in bullet, (
            "cap-STOP bullet must state the trigger explicitly: round 2 "
            "ended with NEEDS_REVISION"
        )
        assert "pass_with_notes" in bullet and "auto-proceeds" in bullet, (
            "cap-STOP bullet must state that a round-2 PASS_WITH_NOTES "
            "auto-proceeds per the bullet above, resolving the precedence "
            "question against the PASS_WITH_NOTES bullet"
        )
        assert "ended without pass" not in bullet, (
            "polarity guard: bullet must not read bare 'ended without "
            "PASS' -- ambiguous about whether PASS_WITH_NOTES counts"
        )

    def test_cap_stop_not_folded_into_digest_silently_loop(self):
        """Polarity guard: the cap-STOP bullet must NOT itself say 'digest
        silently' (that would fold it back into the very loop it exists to
        exit), and the digest-silently bullet must explicitly name the
        cap-STOP as its one exception."""
        step3 = _step3_window(_text())
        cap_bullet = _norm(_cap_stop_bullet(step3))
        digest_bullet = _norm(_digest_silently_bullet(step3))

        assert "digest silently" not in cap_bullet, (
            "regression: cap-STOP bullet must not route into the silent "
            "fix-and-re-review loop"
        )
        assert "digest silently" in digest_bullet or "digest-silently" in digest_bullet
        assert "exception" in digest_bullet and (
            "cap-stop" in digest_bullet.lower() or "docs-arm" in digest_bullet.lower()
        ), (
            "the digest-silently bullet must explicitly carve out the "
            "docs-arm cap-STOP as its exception"
        )

    def test_mutation_guard_exception_clause_required(self):
        """Simulate the regression (exception clause dropped, cap-STOP
        silently folded into the loop) and confirm the check above would
        catch it."""
        step3 = _step3_window(_text())
        digest_bullet = _norm(_digest_silently_bullet(step3))
        mutated = re.sub(
            r"the docs-arm cap-stop.*$",
            "",
            digest_bullet,
            flags=re.IGNORECASE,
        )
        with pytest.raises(AssertionError):
            assert "exception" in mutated and "cap-stop" in mutated.lower()
