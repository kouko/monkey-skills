"""Static contract for the requesting-code-review entrypoint compaction."""

from pathlib import Path
import json
import subprocess
import sys


SKILL = Path(__file__).resolve().parents[1] / "skills/requesting-code-review/SKILL.md"
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import skill_compaction_preflight as preflight


def test_entrypoint_preserves_receipt_scope_routing_panel_and_publish_gate_within_word_range():
    text = SKILL.read_text()
    words = int(subprocess.run(
        ["wc", "-w", str(SKILL)], capture_output=True, check=True, text=True
    ).stdout.split()[0])
    assert 3148 <= words <= 3596

    required = (
        "## Live-gate receipt (CODE / MIXED only)",
        "LOOM_LIVE_GATE_PACKET",
        "LOOM_LIVE_GATE_MARKER_DIR",
        "LOOM_LIVE_GATE_NONCE",
        "LOOM_LIVE_GATE_PLUGIN_ROOT",
        "LOOM_LIVE_GATE_REPO",
        "exactly one matching command",
        "runner-owned packet is the sole packet source",
        "Otherwise do nothing.",
        'CODE: `python3 "$LOOM_LIVE_GATE_PLUGIN_ROOT/scripts/live_gate_station_receipt.py" --packet "$LOOM_LIVE_GATE_PACKET" --plugin-root "$LOOM_LIVE_GATE_PLUGIN_ROOT" --marker-dir "$LOOM_LIVE_GATE_MARKER_DIR" --repo "$LOOM_LIVE_GATE_REPO" --station CODE --nonce "$LOOM_LIVE_GATE_NONCE"`',
        'MIXED: `python3 "$LOOM_LIVE_GATE_PLUGIN_ROOT/scripts/live_gate_station_receipt.py" --packet "$LOOM_LIVE_GATE_PACKET" --plugin-root "$LOOM_LIVE_GATE_PLUGIN_ROOT" --marker-dir "$LOOM_LIVE_GATE_MARKER_DIR" --repo "$LOOM_LIVE_GATE_REPO" --station MIXED --nonce "$LOOM_LIVE_GATE_NONCE"`',
        "Never re-run `review_context.py` in a live-gate station",
        "## When to use",
        "## When NOT to use",
        "## Classification: contract-class vs record-class",
        "## Push-as-trigger",
        "Do NOT execute the push",
        "A refusal STOPS before dispatch",
        "After NEEDS_REVISION",
        "After PASS_WITH_NOTES",
        "finishing-a-development-branch",
        "on PASS the push executes — no re-ask",
        "review_context.py --validate <packet-file>",
        "Preserve its packet unchanged",
        "endpoint equals `reviewed_sha`",
        "§Pinned refusal contract",
        "A stale base, or any failure to establish freshness, REFUSES",
        "**Record-only branch**",
        "review-na-record-only",
        "**Docs-only branch**",
        "ONLY the contract-class subset",
        "**Mixed branch**",
        "read-context",
        "WORSE of the two arm verdicts",
        "**Code-only branch**",
        "**M3 — mechanical upgrade rule (docs arm only).**",
        "dispatch TWO `code-reviewer` subagents in parallel, with byte-identical prompts",
        '"You ARE the reviewer"',
        "full immutable context packet",
        "principles-conformance: N/A",
        "Wait for BOTH verdicts, union the findings, and re-aggregate",
        "same path + anchor AND dimension",
        "Dead-arm rule",
        "verdict: MALFORMED_PACKET",
        "One packet-fix re-dispatch",
        "## Verdict structure",
        "**Aggregation rule**",
        "**Panel union**",
        'set-stage "review:round-N"',
        "If the repo copy is missing, run `python3 <installed-plugin-root>/scripts/plan_card.py <plan-path> --set-stage \"review:round-N\"`; hand-edit only when neither copy is present.",
        "python3 <installed-plugin-root>/scripts/review_context.py --repo <path>",
        "python3 <installed-plugin-root>/scripts/review_context.py --validate <packet-file>",
        "LOOM-" + "SIMPLIFY:",
        "snapshot_read: verified",
        "marker_valid: true",
        "review-pass --repo <target_repo>",
        "Do NOT auto-fix",
        "Re-dispatch if user fixed and wants re-review",
        "## Asking the user",
        "state-anchor-first",
        "family-relay.md §Family relay discipline",
        "adjudication-view",
    )
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f"missing requesting-code-review essence: {missing}"

    frozen = json.loads(
        (REPO_ROOT / "docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json")
        .read_text(encoding="utf-8")
    )["skills"]["requesting-code-review"]
    current = preflight.snapshot_skill(SKILL.parent)
    assert current["frontmatter"] == frozen["frontmatter"]
    assert current["declared_dependencies"] == frozen["declared_dependencies"]
