"""Structural grep-window test guarding finishing-a-development-branch's
Task 4 update (`docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md`):
the flow diagram / delegation table now NAME the three-way review dispatch
(docs-only / mixed / code-only) that `requesting-code-review` Step 1 owns,
and the verdict-routing Step 3 text surfaces `requesting-docs-review`'s
bounded-cap STOP to the user instead of folding it into the existing
NEEDS_REVISION "digest silently" fix-and-re-review loop.

T2 of the bounded-auto-third-round plan
(`docs/loom/plans/2026-08-06-bounded-auto-third-round-and-dispatch-hardening.md`)
extends this file's population: the cap-STOP bullet now routes on
requesting-docs-review's NEW bounded contract (2 rounds + at most one
mechanically-conditioned auto-delta round) by POINTER — never restating
the auto-round's three conditions (anti-copy convention: Directive 1
owns them); Step 4 carries the prose-contract placement guard (repo
memory: splicing-into-a-pinned-sentence-creates-false-readings); the
conductor paragraph carries the entry read duty (Read the CURRENT
SKILL.md before executing — never run the flow from a compacted
summary).

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


def _step4_window(text: str) -> str:
    """Step 4 (fix-application preconditions) through just before Step 5.

    Anchors verified unique via grep: `4. Before applying any review
    findings` (also the Step-3 window's end anchor) and
    `5. Dispatch verification-before-completion`."""
    start = text.index("4. Before applying any review findings")
    end = text.index("5. Dispatch verification-before-completion", start)
    return text[start:end]


def _conductor_paragraph(text: str) -> str:
    """The '## What this skill does' conductor paragraph: from its unique
    opening sentence to the phase-diagram code fence that follows it."""
    start = text.index("Orchestrates the close-branch sequence")
    end = text.index("```", start)
    return text[start:end]


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
        assert re.search(r"bounded[- ]cap", bullet, re.IGNORECASE), (
            "cap-STOP bullet must name the bounded cap (2 rounds + one "
            "conditional auto-delta round), not the old 2-round cap"
        )
        assert "stop" in bullet.lower()

    def test_cap_stop_bullet_surfaces_to_user_not_silent_loop(self):
        bullet = _norm(_cap_stop_bullet(_step3_window(_text())))
        assert "surface" in bullet.lower() and "user" in bullet.lower(), (
            "cap-STOP bullet must surface surviving findings to the user"
        )
        assert "explicit user authorization" in bullet.lower() or (
            "explicit" in bullet.lower() and "authoriz" in bullet.lower()
        ), (
            "rounds beyond the bounded cap must require explicit user "
            "authorization"
        )

    def test_cap_stop_bullet_states_needs_revision_trigger(self):
        """T4 code-quality review finding, re-pinned to the bounded
        contract: the cap-STOP bullet must state its round-2 trigger
        explicitly (a NEEDS_REVISION shape failing the auto-round
        conditions), and name that a round-2 PASS_WITH_NOTES
        auto-proceeds per the bullet above -- so no precedence question
        survives between the two bullets."""
        bullet = _norm(_cap_stop_bullet(_step3_window(_text()))).lower()
        assert (
            "round-2 needs_revision shape failing the auto-round conditions"
            in bullet
        ), (
            "cap-STOP bullet must state the round-2 trigger explicitly: a "
            "NEEDS_REVISION shape failing the auto-round conditions"
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


# --- T2: bounded-cap pointer + placement guard + entry read duty ---------


def test_cap_stop_routes_on_bounded_contract():
    """The cap-STOP bullet routes on requesting-docs-review's bounded
    contract by POINTER: it names the auto-delta round existing and
    REPORTED, names the two shapes rdr still stops on, keeps beyond-cap
    rounds behind explicit user authorization — and does NOT restate the
    three mechanical conditions (anti-copy convention: Directive 1 owns
    them; a copy here would drift)."""
    bullet = _norm(_cap_stop_bullet(_step3_window(_text())))
    low = bullet.lower()
    assert "mechanically-conditioned" in low and "auto-delta round" in low, (
        "bullet must name rdr's mechanically-conditioned auto-delta round"
    )
    assert "report" in low, (
        "bullet must state the auto-round is REPORTED by rdr, never silent"
    )
    assert "directive 1" in low, (
        "bullet must point at requesting-docs-review's Directive 1 for the "
        "auto-round conditions"
    )
    assert "failing the auto-round conditions" in low, (
        "bullet must name the first surfaced shape: a round-2 "
        "NEEDS_REVISION shape failing the auto-round conditions"
    )
    assert "round-3 verdict other than pass or pass_with_notes" in low, (
        "bullet must name the second surfaced shape: a round-3 verdict "
        "other than PASS or PASS_WITH_NOTES"
    )
    assert "beyond the bounded cap" in low, (
        "bullet must keep rounds beyond the bounded cap behind explicit "
        "user authorization"
    )
    for copied in ("fix-verified", "at most 2", "once per branch"):
        assert copied not in low, (
            f"anti-copy violation: condition wording {copied!r} restated "
            "here — the conditions live in rdr's Directive 1 only"
        )


def test_fix_application_placement_guard():
    """Step 4 warns fix appliers about prose-contract placement: new
    material goes in its OWN sentence or inside the placeholder it
    governs, never spliced into a pinned sentence — and names the memory
    entry slug as the incident source."""
    window = _step4_window(_text())
    low = _norm(window).lower()
    assert "own sentence" in low, (
        "Step 4 must state that new prose-contract material goes in its "
        "OWN sentence"
    )
    assert "placeholder" in low, (
        "Step 4 must allow the schema-template alternative: inside the "
        "placeholder the material governs"
    )
    assert "never spliced" in low, (
        "Step 4 must forbid splicing into an existing pinned sentence"
    )
    assert "splicing-into-a-pinned-sentence-creates-false-readings" in window, (
        "Step 4 must name the memory entry slug as the incident source"
    )


def test_entry_reads_current_skill():
    """The conductor paragraph carries the entry read duty: before
    executing, Read the CURRENT SKILL.md from the installed plugin —
    never run the flow from memory or a compacted summary (the
    post-compaction stale-cached-skill-text incident)."""
    para = _norm(_conductor_paragraph(_text())).lower()
    assert "read the current skill.md" in para, (
        "conductor paragraph must require Reading the CURRENT SKILL.md "
        "before executing"
    )
    assert "installed plugin" in para, (
        "the read duty must target the installed plugin's file, not any "
        "cached copy"
    )
    assert "never run the flow from memory or a compacted summary" in para, (
        "conductor paragraph must forbid running the flow from memory or "
        "a compacted summary"
    )
