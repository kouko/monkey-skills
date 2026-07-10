"""Mechanical marker-grep tests for the family relay-discipline SSOT.

Task 4 (this file) writes ALL SIX assertion targets. Only
test_relay_section is expected GREEN after Task 4 — the other five stay
RED by design until Tasks 5-11 add their one-line pointers / catalog
edits to files this task must NOT touch. Each test's docstring is the
contract: the exact marker string(s) a later implementer must add,
verbatim, to flip that test green.

Canonical pointer phrase (reused by tests 2-5): every seam that relays
to the family relay SSOT must contain this exact substring somewhere in
its file — never a copy of the section body. The SSOT body lives in its
own sibling file (loom-pipeline/hooks/family-relay.md) because
family-reception.md is injected verbatim every SessionStart and is
test-pinned to ≤60 non-empty lines; reception carries only a pointer.

Task 3 (2026-07-10 ascii-graph-trigger-fix plan) adds
test_reception_includes_visual_defaults: session-start additionally
extracts family-relay.md §(b) Visual defaults AT RUNTIME and appends it
to the injected reception context.
"""

import json
import os
import re
import shutil
import subprocess
import tempfile

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

POINTER_PHRASE = "family-relay.md §Family relay discipline"

FAMILY_RECEPTION = REPO_ROOT / "loom-pipeline/hooks/family-reception.md"
FAMILY_RELAY = REPO_ROOT / "loom-pipeline/hooks/family-relay.md"
HOOKS_DIR = REPO_ROOT / "loom-pipeline/hooks"
SESSION_START = HOOKS_DIR / "session-start"
SDD_SKILL = REPO_ROOT / "loom-code/skills/subagent-driven-development/SKILL.md"
REVIEW_SKILL = REPO_ROOT / "loom-code/skills/requesting-code-review/SKILL.md"
BRAINSTORM_VISUAL_COMPANION = REPO_ROOT / "loom-code/skills/brainstorming/references/visual-companion.md"
BRAINSTORM_HANDOFF_BRIEF = REPO_ROOT / "loom-code/skills/brainstorming/references/handoff-brief-format.md"
BRAINSTORM_SKILL = REPO_ROOT / "loom-code/skills/brainstorming/SKILL.md"
BRIEF_BEFORE_ASKING_SKILL = REPO_ROOT / "dev-workflow/skills/brief-before-asking/SKILL.md"

DESIGN_SIDE_FILES = {
    "spec": REPO_ROOT / "loom-spec/skills/using-loom-spec/SKILL.md",
    "interface-design": REPO_ROOT / "loom-interface-design/skills/using-loom-interface-design/SKILL.md",
    "product-principles": REPO_ROOT / "loom-product-principles/skills/using-loom-product-principles/SKILL.md",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_relay_section():
    """
    Markers required in loom-pipeline/hooks/family-relay.md
    (this task writes them):
      1. "## Family relay discipline"        — section heading
      2. rollup-card slot names, all five, verbatim:
         "task restated", "current state", "what changed",
         "impact on you", "next + decision"
      3. "ascii-graph-toolkit"                — visual default (flow/state)
      4. "markdown comparison table"          — visual default (>=2 options)
      5. "never bury a briefing and an AskUserQuestion" — turn-ordering rule

    Discovery path: family-reception.md (the SessionStart-injected file)
    must contain a pointer naming "family-relay.md" so readers can find
    the SSOT — the body itself stays out of reception (line budget).

    Anti-copy: the distinctive ③ rule-body phrase "Outcome, not
    mechanism." (requesting-code-review/SKILL.md ③, rule 1) must NOT
    appear in family-relay.md — this section points at the loom-code
    gate, it never copies the rule text.
    """
    text = _read(FAMILY_RELAY)
    assert "## Family relay discipline" in text

    for slot in (
        "task restated",
        "current state",
        "what changed",
        "impact on you",
        "next + decision",
    ):
        assert slot in text, f"missing rollup-card slot: {slot!r}"

    assert "ascii-graph-toolkit" in text
    assert "markdown comparison table" in text
    assert "never bury a briefing and an AskUserQuestion" in text

    assert "Outcome, not mechanism." not in text, (
        "family-relay.md must POINT at requesting-code-review's ③ "
        "gate, never copy its rule bodies"
    )

    reception = _read(FAMILY_RECEPTION)
    assert "family-relay.md" in reception, (
        "family-reception.md must point readers to family-relay.md "
        "(discovery path for the pull-on-demand SSOT)"
    )


def test_sdd_pointer():
    """
    Task 5 adds the canonical pointer phrase to BOTH narration seams in
    loom-code/skills/subagent-driven-development/SKILL.md:
      - near '### ③ How to phrase' (Asking the user seam)
      - near '## Status handling' (checkpoint sign-off seam)
    Marker: POINTER_PHRASE ("family-relay.md §Family relay
    discipline") must occur at least twice in the file — no template
    body copied in either seam.
    """
    text = _read(SDD_SKILL)
    assert text.count(POINTER_PHRASE) >= 2, (
        "expected the pointer phrase in both the ③ seam and the "
        "Status handling seam"
    )


def test_review_pointer():
    """
    Task 6 adds the canonical pointer phrase to
    loom-code/skills/requesting-code-review/SKILL.md ③ (lines ~34-56),
    signalling the verdict-relay + remediation-option seam now defers
    to the shared family relay section instead of a locally-copied rule.
    Marker: POINTER_PHRASE present at least once.
    """
    text = _read(REVIEW_SKILL)
    assert POINTER_PHRASE in text


def test_brainstorming_visuals():
    """
    Task 7 edits three files under loom-code/skills/brainstorming/:
      - references/visual-companion.md: adds "ascii-graph-toolkit" (the
        named tool for flow/state shapes) AND "channel-aware
        degradation" (the catalog's new channel-table heading/phrase)
      - references/handoff-brief-format.md: adds "channel-aware
        degradation" to its `## Diagrams` section
      - SKILL.md: adds POINTER_PHRASE near its plain-language summary
        rule (~line 181)
    """
    visual_companion = _read(BRAINSTORM_VISUAL_COMPANION)
    handoff_brief = _read(BRAINSTORM_HANDOFF_BRIEF)
    skill = _read(BRAINSTORM_SKILL)

    assert "ascii-graph-toolkit" in visual_companion
    assert "channel-aware degradation" in visual_companion
    assert "channel-aware degradation" in handoff_brief
    assert POINTER_PHRASE in skill


def test_brainstorming_fork_table_default():
    """
    Dogfood F1 fix: the fork-guidance region in brainstorming/SKILL.md
    (the "lead with the stakes" rule, ~line 58) must carry the
    "markdown comparison table" default marker at the FORK moment
    itself — not only at the summary seam (~line 181, already covered
    by test_brainstorming_visuals). A weak-model actor rendering a
    2-option fork as bullet lists is the failure this closes.
    """
    skill = _read(BRAINSTORM_SKILL)
    assert "markdown comparison table" in skill


@pytest.mark.parametrize("skill_id", ["spec", "interface-design", "product-principles"])
def test_design_side_pointers(skill_id):
    """
    Tasks 8/9/10 each add ONE line containing POINTER_PHRASE to the
    named using-loom-* SKILL.md's §Intake section:
      spec             -> loom-spec/skills/using-loom-spec/SKILL.md
      interface-design -> loom-interface-design/skills/using-loom-interface-design/SKILL.md
      product-principles -> loom-product-principles/skills/using-loom-product-principles/SKILL.md
    """
    text = _read(DESIGN_SIDE_FILES[skill_id])
    assert POINTER_PHRASE in text


def test_brief_before_asking_ordering():
    """
    Task 11 edits dev-workflow/skills/brief-before-asking/SKILL.md:
      - turn-ordering marker: "never bury a briefing and an
        AskUserQuestion" (same phrase as the relay section, ~line 20-22)
      - anti-diagram carve-out marker: "explicit user request for a
        visual is always honored" (rescoped wording, ~lines 73/185)
    """
    text = _read(BRIEF_BEFORE_ASKING_SKILL)
    assert "never bury a briefing and an AskUserQuestion" in text
    assert "explicit user request for a visual is always honored" in text


def test_reception_includes_visual_defaults():
    """
    session-start must extract the "### (b) Visual defaults" section of
    family-relay.md at RUNTIME and append it to the injected reception
    context — never duplicate the rule text into session-start itself
    (pointer-not-copy stays intact; family-relay.md remains SSOT).

    (a) Running the real session-start emits additionalContext containing
        both "ascii-graph-toolkit" and "markdown comparison table" (the
        two canonical §(b) markers already pinned in family-relay.md by
        test_relay_section above).
    (b) Runtime-extraction proof: copy hooks/ to a temp plugin root,
        mutate the COPIED family-relay.md's §(b) body with a unique
        sentinel, run the byte-identical, unmodified session-start
        script from that temp root, and assert the sentinel shows up in
        its output. session-start's own code is untouched in this
        step — only the data file changed — so a passing assertion
        proves the section is read from family-relay.md at runtime, not
        hard-coded into the script.
    """
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = str(HOOKS_DIR.parent)
    result = subprocess.run(
        [str(SESSION_START)],
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    assert result.returncode == 0, f"session-start exited {result.returncode}: {result.stderr}"
    payload = json.loads(result.stdout)
    nested = payload["hookSpecificOutput"]["additionalContext"]
    assert "ascii-graph-toolkit" in nested
    assert "markdown comparison table" in nested

    with tempfile.TemporaryDirectory() as tmp:
        tmp_hooks = Path(tmp) / "hooks"
        shutil.copytree(HOOKS_DIR, tmp_hooks)

        relay_path = tmp_hooks / "family-relay.md"
        original = relay_path.read_text(encoding="utf-8")
        sentinel = "SENTINEL-RUNTIME-EXTRACTION-9f3a"
        mutated = original.replace(
            "markdown comparison table", f"markdown comparison table {sentinel}"
        )
        assert mutated != original, "expected to find the marker text to mutate"
        relay_path.write_text(mutated, encoding="utf-8")

        tmp_session_start = tmp_hooks / "session-start"
        result2 = subprocess.run(
            [str(tmp_session_start)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result2.returncode == 0, f"session-start exited {result2.returncode}: {result2.stderr}"
        payload2 = json.loads(result2.stdout)
        nested2 = payload2["hookSpecificOutput"]["additionalContext"]
        assert sentinel in nested2, (
            "session-start did not reflect the mutated family-relay.md content — "
            "extraction is not happening at runtime"
        )


def test_brainstorming_visual_operative_line():
    """
    Task 4 (2026-07-10 ascii-graph-trigger-fix plan) adds an operative
    one-liner to brainstorming/SKILL.md's "## Visual companion" section:
    flow/state diagrams in briefs and user-facing summaries are
    GENERATED via ascii-graph-toolkit (or Mermaid where the channel
    renders it), never hand-drawn box art — pointing at
    family-relay.md §(b) Visual defaults as SSOT for the channel rule.
    Markers required WITHIN that section specifically (not just
    anywhere in the file):
      - "ascii-graph-toolkit"
      - "never hand-drawn" (operative not-hand-drawn phrase)
    """
    text = _read(BRAINSTORM_SKILL)
    match = re.search(r"## Visual companion\n(.*?)(?=\n## )", text, re.DOTALL)
    assert match, "expected a '## Visual companion' section in brainstorming/SKILL.md"
    section = match.group(1)
    assert "ascii-graph-toolkit" in section
    assert "never hand-drawn" in section
