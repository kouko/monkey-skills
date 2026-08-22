"""RED/GREEN gate: finishing-a-development-branch/SKILL.md must declare the
purpose-linked betting duty as its own paragraph (not spliced into the
Backlog-close row's sentences, which carry pins other tests depend on),
naming `check_north_star_link.py`, binding each of its three exits to its
meaning in its own clause, and stating the print-before-listing duty, the
absent-file prompt duty, and the exit-2 stop/relay/wait/record/re-run duty.
"""

import pathlib
import re

SKILL_MD = (
    pathlib.Path(__file__).resolve().parents[1]
    / "skills"
    / "finishing-a-development-branch"
    / "SKILL.md"
)


def _purpose_paragraph() -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    match = re.search(r"\*\*Purpose-linked betting\.\*\*.*?(?=\n   - )", text, re.DOTALL)
    assert match, "Purpose-linked betting paragraph not found in finishing-a-development-branch/SKILL.md"
    return match.group(0)


def test_skill_md_declares_the_purpose_row():
    # No @req tag: this task's dispatch carries no registered REQ-ids.
    para = _purpose_paragraph()

    assert "check_north_star_link.py" in para

    # A substring assertion on the positive word alone would still pass if
    # the exit-0 clause said the opposite ("is NOT linked", "unresolved").
    # Assert the positive word AND the absence of its negation, in the same
    # clause, per test_writing_plans_queue_gate.py's negation-guard technique.
    # `.` after a period-space, not a bare `[^.]*` — a bare version stops
    # early at the `.` inside `PURPOSE.md`, splitting the clause and
    # dropping the very content the negation-guard needs to see.
    exit_0_clause = re.search(r"[Ee]xit 0[\s\S]*?\.(?=\s|$)", para)
    assert exit_0_clause, "exit 0 not stated as its own clause"
    assert "linked" in exit_0_clause.group(0), "exit 0 not bound to 'linked' in one clause"
    assert "unresolved" not in exit_0_clause.group(0), "exit 0's clause says 'unresolved' — the meanings are swapped"
    assert "not linked" not in exit_0_clause.group(0), "exit 0's clause negates 'linked' — the meanings are swapped"

    exit_1_clause = re.search(r"[Ee]xit 1[\s\S]*?\.(?=\s|$)", para)
    assert exit_1_clause, "exit 1 not stated as its own clause"
    assert "unreadable" in exit_1_clause.group(0), "exit 1 not bound to 'unreadable' in one clause"

    # exit 1 has TWO causes since the retired-vocabulary guard landed: an
    # unreadable store path, and an entry whose status: falls outside the
    # closed vocabulary. Their remedies differ — the first is treated as
    # store-absent, the second is that entry's frontmatter to fix — so the
    # text must name both. The exit-2 clause shipped this exact defect
    # (a cause count drifting out from under the prose) and no assertion
    # here noticed; pinning the second cause is what closes that gap.
    assert "vocabulary" in exit_1_clause.group(0), "exit 1 clause omits the out-of-vocabulary-status cause"
    assert "frontmatter" in exit_1_clause.group(0), "exit 1 clause omits the remedy for the out-of-vocabulary cause"

    exit_2_clause = re.search(r"[Ee]xit 2[\s\S]*?\.(?=\s|$)", para)
    assert exit_2_clause, "exit 2 not stated as its own clause"
    assert "unresolved" in exit_2_clause.group(0), "exit 2 not bound to 'unresolved' in one clause"

    # check_north_star_link.py has THREE distinct exit-2 causes, each with its
    # own question builder: PURPOSE.md absent (build_purpose_missing_question),
    # PURPOSE.md present but still unanswered — template placeholder or a bare
    # "not yet" (build_purpose_template_question), and a bet entry lacking a
    # well-formed serves: line (build_serves_question). The text must name all
    # three, not collapse them. An earlier revision of this test asserted TWO
    # and so pinned the undercount it was meant to catch; the whole-branch
    # review found the SKILL.md sentence still wrong underneath it.
    assert "PURPOSE.md` is absent" in exit_2_clause.group(0), "exit 2 clause does not name the absent-PURPOSE.md cause"
    assert "unanswered" in exit_2_clause.group(0), "exit 2 clause does not name the unanswered-PURPOSE.md cause"
    assert "serves" in exit_2_clause.group(0), "exit 2 clause does not name the malformed-serves cause"

    assert (
        "Only AFTER the user explicitly requests choosing or promoting a bet, "
        "and before listing betting candidates, print `docs/loom/PURPOSE.md`"
        in para
    ), "explicit-request print-before-listing duty missing"

    assert "absent" in para and "offer to write one" in para, "absent-file prompt duty missing"
    assert "never silently skip the print" in para, "absent-file prompt duty missing its loud-not-silent clause"

    for duty_phrase in (
        "STOP-and-ask",
        "relay the printed question",
        "wait",
        # The remedy is cause-dependent: the serves: line answers only the
        # third cause; the first two are answered in PURPOSE.md itself. An
        # earlier revision pinned a single unconditional destination, which
        # was wrong for two of the three causes.
        "record it where that question asks",
        "`PURPOSE.md` itself",
        "re-run",
    ):
        assert duty_phrase in para, f"missing exit-2 duty phrase: {duty_phrase!r}"


def test_check_north_star_link_invocation_uses_plugin_root_form():
    # No @req tag: this task's dispatch carries no registered REQ-ids.
    #
    # check_north_star_link.py ships ONLY inside the loom-code plugin —
    # unlike backlog_index.py / plan_card.py it has no repo-root shim in
    # any consuming repo. A bare `loom-code/scripts/...` path resolves
    # only inside monkey-skills (the plugin's own source repo); every
    # consuming repo (e.g. kumiko) gets the plugin from a cache with no
    # `loom-code/` directory at all, so that form fails at the one place
    # this duty exists to run.
    para = _purpose_paragraph()

    assert '${CLAUDE_PLUGIN_ROOT}/scripts/check_north_star_link.py' in para, (
        "check_north_star_link.py invocation must use the plugin-root form"
    )
    assert "load-time substitution, not a run-time shell variable" in para, (
        "missing the load-time-substitution warning parenthetical"
    )

    # Guard against a bare repo-relative path anywhere in the paragraph —
    # this is the exact defect being fixed: it only resolves inside
    # monkey-skills, the plugin's own source repo.
    assert not re.search(r"(?<!\$\{CLAUDE_PLUGIN_ROOT\}/)loom-code/scripts/check_north_star_link\.py", para), (
        "bare repo-relative loom-code/scripts/ path found — only resolves inside monkey-skills"
    )
