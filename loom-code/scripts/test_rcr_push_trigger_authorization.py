"""Prose-pin test for Task 3 (rcr push-trigger request-derived authorization).

Pins the rewritten Push-as-trigger steps 4/6 in
requesting-code-review/SKILL.md (after PASS the push executes — the
request already authorized it; after PASS_WITH_NOTES the push carries
findings verbatim), the ask-vs-resolve SSOT pointer appended after
step 6, and the request-derived closing clause in
references/relay-phrasing.md.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RCR_DIR = REPO_ROOT / "loom-code" / "skills" / "requesting-code-review"
SKILL_MD = RCR_DIR / "SKILL.md"
RELAY_MD = RCR_DIR / "references" / "relay-phrasing.md"


def _normalized(path: Path) -> str:
    """Whitespace-normalized file text (collapses hard wraps so a
    contiguous-phrase match doesn't depend on line breaks)."""
    return " ".join(path.read_text(encoding="utf-8").split())


# --- positive-fact controls --------------------------------------------------


def test_skill_push_as_trigger_heading_present():
    """Positive-fact control (SKILL.md): the pre-existing §Push-as-trigger
    heading is present — proves the assertions below are not vacuous."""
    assert "## Push-as-trigger" in _normalized(SKILL_MD)


def test_relay_phrasing_gate_one_heading_present():
    """Positive-fact control (relay-phrasing.md): the pre-existing gate ①
    heading is present — proves the file is actually read/matched."""
    assert "## ① Whether to ask — tier by reversibility × cost" in _normalized(
        RELAY_MD
    )


# --- step 4: the push WAS the request ---------------------------------------


def test_step4_push_was_the_request_lead_present():
    """After PASS the push executes — the request already authorized it."""
    assert (
        "**After PASS**: the push WAS the request — execute it "
        "(branch-qualified form) and report loudly what was pushed. "
        "Do not re-ask."
        in _normalized(SKILL_MD)
    )
    # Paired absence pin: the retired post-PASS re-ask is an INSTRUCTION whose
    # literal return (copy-paste from history) would make the agent stop and
    # re-request authorization the request already granted. Deliberately
    # unnarrowed — an absence check is only weakened by a window.
    assert "want me to push now" not in _normalized(SKILL_MD), (
        "the retired post-PASS re-ask must not reappear anywhere in SKILL.md"
    )


# --- step 6: carry findings, no push-anyway ask ------------------------------


def test_step6_carry_findings_wording_present():
    """After PASS_WITH_NOTES the push carries every finding verbatim."""
    assert (
        "**After PASS_WITH_NOTES**: push, carrying every finding verbatim "
        "into the report (and the PR body if one follows) — consistent with "
        "`finishing-a-development-branch` Step 3's auto-proceed. Do NOT fix "
        "findings inline silently." in _normalized(SKILL_MD)
    )
    # Paired absence pin: the retired "push anyway" ask is an authorization
    # escape hatch — its literal return would re-open pushing past findings
    # on the agent's own say-so. Deliberately unnarrowed.
    assert "push anyway (acceptable for non-🔴 findings)" not in _normalized(
        SKILL_MD
    ), "the retired PASS_WITH_NOTES push-anyway ask must not reappear"


# --- SSOT pointer after step 6 ----------------------------------------------


def test_ssot_triage_pointer_present():
    """The ask-vs-resolve SSOT pointer paragraph follows step 6."""
    assert (
        "Any further question this flow surfaces runs the ask-vs-resolve "
        "triage at `subagent-driven-development` §Asking the user, gate ① "
        "(the cross-skill SSOT) before it reaches the user."
        in _normalized(SKILL_MD)
    )


# --- relay-phrasing.md closing clause ----------------------------------------


def test_relay_phrasing_request_derived_clause_present():
    """relay-phrasing.md gate ① closes with the request-derived clause:
    merge always confirms; push/PR-create confirm once, at the request
    that names them."""
    assert (
        "The push-as-trigger actions publish to teammates / CI / production — "
        "`gh pr merge` always confirms first and is never auto-run; "
        "`git push` / `gh pr create` confirm ONCE, at the request that names "
        "them (request-derived authorization) — a naming request executes "
        "with a loud report, an unnamed one still asks."
        in _normalized(RELAY_MD)
    )
