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

PLUGIN_ROOT = Path(__file__).parents[1]
HOOKS_DIR = PLUGIN_ROOT / "hooks"
RECEPTION_MD = HOOKS_DIR / "family-reception.md"
HOOKS_JSON = HOOKS_DIR / "hooks.json"
SESSION_START = HOOKS_DIR / "session-start"

FAMILY_ENTRIES = [
    "using-loom-product-principles",
    "using-loom-interface-design",
    "using-loom-spec",
    "using-loom-code",
    "using-loom-pipeline",
]


def _non_empty_lines(text: str) -> list:
    return [line for line in text.splitlines() if line.strip()]


def test_reception_content_contract():
    assert RECEPTION_MD.exists(), f"missing {RECEPTION_MD}"
    text = RECEPTION_MD.read_text()
    lower = text.lower()

    # Line budget (brief §Open Q1): ≤60 non-empty lines.
    non_empty = _non_empty_lines(text)
    assert len(non_empty) <= 60, (
        f"family-reception.md has {len(non_empty)} non-empty lines, budget is 60"
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
    assert "principles.md" in lower and "using-loom-product-principles first" in lower, (
        "missing row 1 (no PRINCIPLES.md + product-shaped -> product-principles first)"
    )
    assert (
        "design.md" in lower or "ui-flows" in lower
    ) and "using-loom-interface-design first" in lower, (
        "missing row 2 (user-facing surface + no DESIGN.md/ui-flows -> interface-design first)"
    )
    assert "using-loom-spec first" in lower, (
        "missing row 3 (multi-state/multi-object + no spec/change-folder -> spec first)"
    )
    assert "do not interrupt" in lower, "missing the negative-guard phrase"
    assert (
        "bug fix" in lower and "refactor" in lower and "test-covered" in lower
    ), "missing the negative guard's three named cases"

    # Recommend-once + record-choice rule.
    assert "recommend" in lower and "once" in lower, "missing the recommend-once rule"
    assert "record" in lower and "choice" in lower, "missing the record-the-choice rule"


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
