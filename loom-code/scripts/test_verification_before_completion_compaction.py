"""Static contract for verification-before-completion compaction."""

import json
from pathlib import Path
import sys


SKILL = Path(__file__).resolve().parents[1] / "skills/verification-before-completion/SKILL.md"
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import skill_compaction_preflight as preflight


def test_entrypoint_preserves_package_evidence_failure_routing_and_marker():
    text = SKILL.read_text(encoding="utf-8")

    required = (
        "<SUBAGENT-STOP>",
        'NO "DONE" WITHOUT PACKAGE-LEVEL TEST INVOCATION',
        "Evidence predating current HEAD is invalid. A focused test is never package verification. Until the current package suite passes, do not enter finishing or close-out: run the current package suite first.",
        "Single-file",
        "Test interaction bugs",
        "Orphan tests",
        "Lint passes ≠ tests pass",
        "## When NOT to use",
        "No tests exist yet",
        "Pure doc / config / generated regen",
        "Test infrastructure broken",
        "Explicit user override + scoped",
        "## Red Flags",
        "## Process",
        "declared-first consult",
        "AGENTS.md",
        "package.json",
        "falling back to detection",
        "Run it from project root",
        "Read the exit code AND the output",
        "total test count > 0",
        "Exit 0 with 0 tests ran",
        "If failures",
        "Do NOT mark \"done.\"",
        "tdd-iron-law",
        "systematic-debugging",
        "If pass",
        "the command run, the test count, the summary line",
        "loom_gate_markers.py verified --run",
        ".git/loom/verified.json",
        "current HEAD sha",
        "AFTER the final commit",
        "plain-relay",
        "## Boundaries",
        "requesting-code-review",
        "ui-verification",
        "ui-flows.md",
        "finishing-a-development-branch",
        "On **PASS**",
        "On **FAIL**",
    )
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f"missing verification-before-completion essence: {missing}"

    frozen = json.loads(
        (REPO_ROOT / "docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json")
        .read_text(encoding="utf-8")
    )["skills"]["verification-before-completion"]
    current = preflight.snapshot_skill(SKILL.parent)
    assert current["frontmatter"] == frozen["frontmatter"]
    assert current["declared_dependencies"] == frozen["declared_dependencies"]


def test_readmes_do_not_readvertise_the_revoked_exemptions():
    """Guard the re-addition direction, which presence assertions cannot see.

    The #740 follow-up revoked two exemptions in SKILL.md and re-aligned all
    three READMEs. A presence pin cannot detect a rule coming back, so the
    revoked phrasings are asserted absent instead. Mutation-checked: re-adding
    either phrase to any of the three READMEs turns this red.
    """
    revoked = {
        "README.md": ("Pure doc / config / generated regen (no runtime behavior change)",
                      "Explicit user override AND change matches exempt category"),
        "README.ja.md": ("- 純 doc / config / 生成コード再生成（ランタイム挙動変更なし）",
                         "- ユーザの明示的 override AND 変更が exempt カテゴリ該当"),
        "README.zh-TW.md": ("- 純 doc / config / 重新生成的 code（無 runtime 行為改變）",
                            "- 使用者明確 override AND 變更屬於 exempt 類別"),
    }
    for name, phrases in revoked.items():
        text = (SKILL.parent / name).read_text(encoding="utf-8")
        for phrase in phrases:
            assert phrase not in text, (
                f"{name} re-advertises a revoked exemption: {phrase!r}"
            )
