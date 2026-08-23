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
DESIGN_ROOT = REPO_ROOT / "loom-design"
PIPELINE_SKILL = (
    REPO_ROOT / "loom-design" / "skills" / "using-loom-pipeline" / "SKILL.md"
)
PACKAGED_RECEPTION_TARGET = "../using-loom-design/references/family-reception.md"
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


def _assert_packaged_target(source: Path, target: str) -> Path:
    resolved = (source.parent / target).resolve()
    try:
        resolved.relative_to(DESIGN_ROOT.resolve())
    except ValueError:
        raise AssertionError(f"contract link escapes loom-design: {target}") from None
    assert resolved.is_file(), f"contract link is not a file: {target}"
    return resolved


def test_pipeline_reads_packaged_reception_contract():
    text = PIPELINE_SKILL.read_text(encoding="utf-8")

    assert (
        "[family reception](../using-loom-design/references/family-reception.md)"
        in text
    )
    assert "loom-code/hooks/family-reception.md" not in text
    assert "`loom-code:using-loom-code` for code work" in text
    assert "`using-loom-code` for code work" not in text
    _assert_packaged_target(PIPELINE_SKILL, PACKAGED_RECEPTION_TARGET)


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
    #   addition of ~18 lines (80 → 98 non-empty); budget raised 85 → 100;
    # + the sibling-optional standalone contract
    #   (plan 2026-08-23-loom-design-specialization, Task 1) — 7 load-bearing
    #   lines covering availability, artifact preservation, and local fallback
    #   (98 → 105); reviewer hardening then added 3 lines for the complete local
    #   six-block brief and the availability-gated writing-plans contract
    #   (105 → 108); budget raised 100 → 110, retaining 2 lines of headroom.
    # Further accretion must be sanctioned in the same PR.
    # Generated copies carry a five-line management header. Keep that transport
    # metadata outside the policy-body budget so growth in either remains visible.
    header, separator, body = text.partition("-->\n")
    assert separator, "family-reception.md is missing its managed-copy header"
    assert len(_non_empty_lines(header + separator)) == 5, (
        "family-reception.md managed-copy header changed; update the sync contract"
    )
    body_non_empty = _non_empty_lines(body)
    assert len(body_non_empty) <= 110, (
        f"family-reception.md policy body has {len(body_non_empty)} non-empty lines, "
        "budget is 110"
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
    assert "and its public skill is available" in lower
    assert "owning plugin's path continues" in lower
    assert "if `loom-workflow:brief-before-asking` is available" in lower
    assert "handoff-brief-format.md" not in text


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
    assert "public" in row.lower() and "available" in row.lower(), (
        "loom-init must be gated on public capability availability"
    )
    assert "otherwise skip" in row.lower(), (
        "loom-init must define the sibling-absent fallback"
    )
    assert "loom-code" not in row, (
        "loom-init must not require the loom-code sibling"
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
