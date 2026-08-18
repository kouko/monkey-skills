"""Structural test: the loom family reception (hooks/family-reception.md +
hooks/hooks.json + hooks/session-start) — the SSOT on-ramp criteria table,
the family map, the three-doors framing, and the SessionStart hook mechanism
mirroring loom-code's.

"""
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
# The family reception hooks ship from the loom-code plugin.
PLUGIN_ROOT = REPO_ROOT / "loom-code"
HOOKS_DIR = PLUGIN_ROOT / "hooks"
RECEPTION_MD = HOOKS_DIR / "family-reception.md"
HOOKS_JSON = HOOKS_DIR / "hooks.json"
SESSION_START = HOOKS_DIR / "session-start"

# Part-1 merged the four design-side routers (product-principles /
# interface-design / spec / discovery) into one `using-loom-design` entry.
FAMILY_ENTRIES = [
    "using-loom-design",
    "using-loom-code",
    "using-loom-pipeline",
]


def _non_empty_lines(text: str) -> list:
    return [line for line in text.splitlines() if line.strip()]


def test_reception_content_contract():
    assert RECEPTION_MD.exists(), f"missing {RECEPTION_MD}"
    text = RECEPTION_MD.read_text()
    lower = text.lower()

    # Line budget (brief §Open Q1): base ≤60 non-empty lines, +1 for the
    # sanctioned row-5 loom-init addition (plan 2026-08-10-loom-init-scaffold §Task 3),
    # + sanctioned plain-relay additions (plan 2026-08-15-plain-relay-contract):
    #   the imperative <PLAIN-RELAY> trigger card (Task 2) and the
    #   §Brief before a complex fork SSOT section (Task 5) — both load-bearing
    #   per the frozen brief, so the reception budget grows to accommodate them;
    # + the on-ramp explicit-choice gate (plan 2026-08-18-onramp-explicit-choice-gate,
    #   PR #704: the detour choice is the user's, recorded mechanically) — sanctioned
    #   addition of ~18 lines (80 → 98 non-empty); budget raised 85 → 100 — 2 lines
    #   of headroom on purpose: further accretion must be sanctioned in the same PR.
    non_empty = _non_empty_lines(text)
    assert len(non_empty) <= 100, (
        f"family-reception.md has {len(non_empty)} non-empty lines, budget is 100"
    )

    # Family map: all five using-loom-* entries present.
    for name in FAMILY_ENTRIES:
        assert name in text, f"missing family entry {name}"

    # The "要用 loom-X, 就從 using-loom-X 開始" rule.
    assert "using-loom-x" in lower.replace(" ", ""), (
        "missing the 「要用 loom-X 就從 using-loom-X 開始」 rule"
    )

    # Three doors, with the Workflow door pinned as described-never-auto-opened.
    assert "workflow" in lower, "missing the Workflow door"
    assert "never auto-opened" in lower, (
        "missing the pinned 'never auto-opened' phrase for the Workflow door"
    )
    assert "explicit" in lower, "missing explicit-invocation framing for the Workflow door"

    # On-ramp criteria table (SSOT) — three rows + negative guard.
    # Post-merge every row suggests `using-loom-design first`; the station
    # parenthetical is what keeps the three rows distinguishable.
    assert "using-loom-design first" in lower, "missing the design-side on-ramp suggestion"
    assert "principles.md" in lower and "routes to the product-principles station" in lower, (
        "missing row 1 (no PRINCIPLES.md + product-shaped -> product-principles station)"
    )
    assert (
        "design.md" in lower or "ui-flows" in lower
    ) and "routes to the interface-design station" in lower, (
        "missing row 2 (user-facing surface + no DESIGN.md/ui-flows -> interface-design station)"
    )
    assert "routes to the spec station" in lower, (
        "missing row 3 (multi-state/multi-object + no spec/change-folder -> spec station)"
    )
    assert "do not interrupt" in lower, "missing the negative-guard phrase"
    assert (
        "bug fix" in lower and "refactor" in lower and "test-covered" in lower
    ), "missing the negative guard's three named cases"

    # Recommend-once + record-choice rule.
    assert "recommend" in lower and "once" in lower, "missing the recommend-once rule"
    assert "record" in lower and "choice" in lower, "missing the record-the-choice rule"

    # Batch-the-intake rule (2026-07-06 /insights adoption): one ask, never
    # serial; PRINCIPLES.md stays a recommendation, not a prerequisite.
    assert "batch the intake" in lower, "missing the batch-the-intake rule"
    assert "one ask" in lower and "never serially" in lower, (
        "missing the one-ask / never-serially phrasing"
    )
    # PR #704 reworded the reconciliation: the docs are never a prerequisite to
    # RUN loom-design, but the on-ramp CHOICE itself is gated (explicit user choice).
    assert (
        "never a prerequisite to *run* loom-design" in lower
        and "*choice* is gated" in lower
    ), (
        "missing the recommendations-are-not-prerequisites / choice-is-gated reconciliation"
    )


def test_reception_onramp_row_suggests_loom_init_once():
    text = RECEPTION_MD.read_text()

    # Row 5: repo lacks the queue layer -> suggest running loom-init once.
    rows = [line for line in text.splitlines() if "loom-init" in line]
    assert rows, "missing the loom-init on-ramp row"
    row = rows[0]
    assert row.lstrip().startswith("|"), "loom-init must appear as a table row"
    assert "docs/loom/backlog/" in row, (
        "loom-init row must condition on the missing queue layer (docs/loom/backlog/)"
    )
    assert "once" in row.lower(), "loom-init row must carry the once wording"
    assert "loom-code" in row, (
        "loom-init row must name loom-code as where the scaffold verb ships"
    )

    # Negative pin: this hook file is read raw — no placeholder literal.
    assert "${CLAUDE_PLUGIN_ROOT}" not in text, (
        "family-reception.md is read raw; ${CLAUDE_PLUGIN_ROOT} must not appear"
    )


def test_hooks_json_shape_matches_loom_code():
    assert HOOKS_JSON.exists(), f"missing {HOOKS_JSON}"
    data = json.loads(HOOKS_JSON.read_text())

    session_start_hooks = data["hooks"]["SessionStart"]
    assert len(session_start_hooks) == 1
    entry = session_start_hooks[0]
    assert entry["matcher"] == "startup|clear|compact"

    inner_hooks = entry["hooks"]
    assert len(inner_hooks) == 1
    hook = inner_hooks[0]
    assert hook["type"] == "command"
    assert hook["command"] == '"${CLAUDE_PLUGIN_ROOT}/hooks/session-start"'
    assert hook["async"] is False


def test_session_start_is_executable():
    assert SESSION_START.exists(), f"missing {SESSION_START}"
    mode = SESSION_START.stat().st_mode
    assert mode & stat.S_IXUSR, "session-start is not executable (owner)"


def test_session_start_emits_three_keys_with_reception_text():
    assert SESSION_START.exists(), f"missing {SESSION_START}"
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    result = subprocess.run(
        [str(SESSION_START)],
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    assert result.returncode == 0, f"session-start exited {result.returncode}: {result.stderr}"

    payload = json.loads(result.stdout)

    # Canonical key.
    nested = payload["hookSpecificOutput"]["additionalContext"]
    assert nested, "hookSpecificOutput.additionalContext is empty"

    # Two defensive keys.
    assert payload["additional_context"], "additional_context is empty"
    assert payload["additionalContext"], "additionalContext is empty"

    # Reception content actually landed in the injected text.
    for name in FAMILY_ENTRIES:
        assert name in nested, f"reception text missing {name} in injected context"
