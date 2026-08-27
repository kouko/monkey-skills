"""Static contract for the requesting-docs-review entrypoint compaction."""

import json
from pathlib import Path
import sys


SKILL = Path(__file__).resolve().parents[1] / "skills/requesting-docs-review/SKILL.md"
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import skill_compaction_preflight as preflight


def test_entrypoint_preserves_scope_panel_dimensions_and_bounded_confirmation():
    text = SKILL.read_text(encoding="utf-8")

    required = (
        "<SUBAGENT-STOP>",
        "## Live-gate receipt (DOCS only)",
        'python3 "$LOOM_LIVE_GATE_PLUGIN_ROOT/scripts/live_gate_station_receipt.py" --packet "$LOOM_LIVE_GATE_PACKET" --plugin-root "$LOOM_LIVE_GATE_PLUGIN_ROOT" --marker-dir "$LOOM_LIVE_GATE_MARKER_DIR" --repo "$LOOM_LIVE_GATE_REPO" --station DOCS --nonce "$LOOM_LIVE_GATE_NONCE"',
        "Otherwise do nothing.",
        "Never re-run `review_context.py` in a live-gate station",
        "## When to use",
        "## When NOT to use",
        "round 1 whole-artifact is the only full review",
        "CONFIRMED_RESOLVED",
        "STILL_BLOCKING",
        "quality stop, not a new permission boundary",
        "Session death before confirmation",
        "target_repo",
        "reviewed_sha",
        "plugin_version",
        "resources",
        "python3 <installed-plugin-root>/scripts/review_context.py --repo <target_repo>",
        "python3 <installed-plugin-root>/scripts/review_context.py --validate <packet-file>",
        "resolved-scope",
        "The delegate resolves scope itself ONLY when no `resolved-scope` was supplied.",
        "A stale base, or any failure to establish freshness, REFUSES.",
        "non-empty AND every file in it ends in `.md`",
        "python3 <resources.doc_citation_checker>",
        "Exit 2",
        "do not dispatch",
        "do not mint",
        "Dispatch TWO `docs-reviewer` subagents in parallel, with byte-identical prompts",
        '"You ARE the reviewer"',
        "omission",
        "ambiguity",
        "inconsistency",
        "incorrect-fact",
        "missing-population",
        "class: instruction | evidence",
        "Unclear class is `instruction`",
        "Wait for BOTH verdicts",
        "same path + anchor + dimension",
        "Re-run §Aggregation rule on the union",
        "return the verdict to that orchestrator and do NOT mint",
        "python3 <resources.gate_markers> review-pass",
        "verdict: MALFORMED_PACKET",
        "Review-only request",
        "Authorized change task",
        "SendMessage",
        "labelled fresh whole-artifact review",
        "If upstream supplies one, adopt it verbatim and ask the active host adapter for `<installed-plugin-root>` as root lookup only; otherwise ask the adapter for that root",
        "Then validate either packet with `python3 <installed-plugin-root>/scripts/review_context.py --validate <packet-file>`",
        "nonzero REFUSES confirmation and marker minting",
        "must not mint CONFIRMED_RESOLVED directly",
        "schema-valid terminal wrapper",
        "must not upgrade",
        "## Aggregation rule",
        "instruction-class findings only",
        "superseded by an appended correction",
        "## Verdict structure",
        "dimension_scores:",
        "## Red Flags",
    )
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f"missing requesting-docs-review essence: {missing}"

    frozen = json.loads(
        (REPO_ROOT / "docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json")
        .read_text(encoding="utf-8")
    )["skills"]["requesting-docs-review"]
    current = preflight.snapshot_skill(SKILL.parent)
    assert current["frontmatter"] == frozen["frontmatter"]
    assert current["declared_dependencies"] == frozen["declared_dependencies"]
