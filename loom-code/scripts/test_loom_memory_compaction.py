"""Behavior pins for the loom-memory entrypoint compaction."""

from pathlib import Path
import re
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = REPO_ROOT / "loom-code" / "skills" / "loom-memory" / "SKILL.md"


def test_entrypoint_preserves_conditional_record_recall_prune_contract_within_word_range():
    text = SKILL.read_text(encoding="utf-8")
    flat = re.sub(r"\s+", " ", text)
    words = int(
        subprocess.run(
            ("wc", "-w", str(SKILL)),
            check=True,
            capture_output=True,
            text=True,
        ).stdout.split()[0]
    )
    violations = []

    if not 741 <= words <= 846:
        violations.append(f"word count {words} is outside 741..846")

    # Immutable package surface and verb structure.
    for marker in (
        "name: loom-memory",
        "version: 0.2.1",
        "## record",
        "## recall",
        "## prune",
        "docs/loom/memory/README.md",
        "docs/loom/backlog/README.md",
        "docs/loom/memory/<file>.md",
        "<slug>.md",
    ):
        if marker not in flat:
            violations.append(f"missing invariant marker: {marker}")

    # Conditional activation must stop loudly and must not bootstrap a store.
    for marker in (
        "Fire only when the target repo has the store charter",
        "The target repo is the user's current project repository, never the plugin installation or skill directory",
        "loom-memory: N/A (no docs/loom/memory/README.md in this repo)",
        "stop",
        "never scaffold",
    ):
        if marker not in flat:
            violations.append(f"missing conditional-gate marker: {marker}")

    # The charter remains the live SSOT rather than copied instructions.
    for marker in (
        "reads the charter at execution time",
        "charter wins",
        "Do not reproduce",
        "jurisdiction table",
        "format block",
        "pull-not-push",
    ):
        if marker not in flat:
            violations.append(f"missing charter marker: {marker}")

    # Record: classify, replace contradictions, generate and certify the index.
    for marker in (
        "backlog-shaped open item/debt/re-trigger",
        "plugin-shipped gotchas reference",
        "Classify everything else by the charter",
        "Tell the user the chosen route and why",
        "Check the store for contradictions",
        "First grep both index and bodies",
        "update or replace",
        "never add a contradicting sibling",
        "frontmatter `description`",
        "python3 scripts/check_loom_memory_integrity.py --write",
        "generates `## Index` from entry frontmatter",
        "never append a line manually",
        "python3 scripts/check_loom_memory_integrity.py",
        "Also run `--check`",
        "must exit 0",
    ):
        if marker not in flat:
            violations.append(f"missing record marker: {marker}")

    # Recall is pull-only, cites hits, verifies freshness, and reports misses.
    for marker in (
        "Grep the index first",
        "Read ONLY the hit files",
        "file citation per rule",
        "verify any file/flag/skill it names still exists",
        'No hits → say "no hits" honestly',
    ):
        if marker not in flat:
            violations.append(f"missing recall marker: {marker}")

    # Prune is explicit, exhaustive, evidence-based, and never auto-deletes.
    for marker in (
        "Invoked explicitly, never ambient",
        "For **each** file",
        "origin age",
        "superseded by a repo artifact",
        "no plausible future trigger",
        "keep / merge / retire",
        "every file gets a row",
        "NEVER delete without explicit user approval",
        "After approval, execute and regenerate the index in the same pass",
        "then run `--check` for merged files",
    ):
        if marker not in flat:
            violations.append(f"missing prune marker: {marker}")

    # No companion reference extraction may absorb removed prose.
    reference_files = list((SKILL.parent / "references").glob("**/*")) \
        if (SKILL.parent / "references").exists() else []
    if any(path.is_file() for path in reference_files):
        violations.append("loom-memory gained reference files")

    assert violations == [], "\n".join(violations)
