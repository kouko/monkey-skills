"""Mechanical contract tests over the shipped `loom-memory` skill text.

These tests assert against the actual prose the skill ships (`SKILL.md` and
its `references/*.md`), never against a claim about it — per
`loom-code:implementer`'s baseline, prose is tested the same way code is:
observe the assertion fail against the not-yet-written files, then write the
files to make it pass.

Structural note: everything here is a text/filesystem check. No LLM
judgement is involved — the skill's actual triggering and step-following
behavior is a `skill-dev-toolkit:dogfood-skill-testing` concern, out of
scope for this task.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "loom-memory" / "skills" / "loom-memory"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES_DIR = SKILL_DIR / "references"
OKF_PROFILE = REFERENCES_DIR / "okf-profile.md"
OPERATIONS = REFERENCES_DIR / "operations.md"

OPERATIONS_NAMES = ["Recall", "Record", "Reconcile", "Retire"]

DESCRIPTION_BUDGET_CHARS = 1536
WORD_HARD_CAP = 4500  # ~6,000 tokens, matching scripts/check-skill-structure.py's proxy


def _read(path: Path) -> str:
    assert path.is_file(), f"expected file at {path}"
    return path.read_text(encoding="utf-8")


def _skill_md_text() -> str:
    return _read(SKILL_MD)


def _all_skill_text() -> str:
    parts = [_read(SKILL_MD)]
    if REFERENCES_DIR.is_dir():
        for md in sorted(REFERENCES_DIR.glob("*.md")):
            parts.append(_read(md))
    return "\n".join(parts)


def _frontmatter_description(text: str) -> str:
    """Extract the YAML-ish `description:` block value from SKILL.md frontmatter."""
    lines = text.splitlines()
    assert lines and lines[0].strip() == "---", "SKILL.md must open with a frontmatter block"
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    block = lines[1:end]
    # description may be a scalar `description: text` or a block scalar `description: |`
    for idx, line in enumerate(block):
        if line.startswith("description:"):
            rest = line[len("description:") :].strip()
            if rest and rest != "|" and rest != ">":
                return rest
            # block scalar — collect following indented lines
            collected: list[str] = []
            for cont in block[idx + 1 :]:
                if cont.startswith((" ", "\t")) and cont.strip():
                    collected.append(cont.strip())
                elif not cont.strip():
                    continue
                else:
                    break
            return " ".join(collected)
    raise AssertionError("no 'description:' key found in SKILL.md frontmatter")


def _section(text: str, heading_name: str) -> str:
    """Return the body of a `##`/`###` heading matching `heading_name` up to
    the next heading of the same or shallower level."""
    pattern = re.compile(
        rf"^(#{{2,3}})\s+{re.escape(heading_name)}\s*$", re.MULTILINE
    )
    match = pattern.search(text)
    assert match, f"no heading named {heading_name!r} found"
    level = len(match.group(1))
    start = match.end()
    next_heading = re.compile(rf"^#{{1,{level}}}\s+\S", re.MULTILINE)
    later = next_heading.search(text, pos=start)
    end = later.start() if later else len(text)
    return text[start:end]


# ---------------------------------------------------------------------------
# Acceptance A3 positive: four-operations-contract
# ---------------------------------------------------------------------------


def test_four_operations_contract() -> None:
    text = _skill_md_text()
    for name in OPERATIONS_NAMES:
        section = _section(text, name)
        assert "Trigger" in section, f"{name} section must state its trigger"
        assert "Steps" in section, f"{name} section must state its steps"
        assert re.search(r"^\d+\.\s", section, re.MULTILINE), (
            f"{name} section must enumerate concrete steps"
        )


# ---------------------------------------------------------------------------
# Acceptance A3 boundary: absent-store-empty-recall-and-retire-approval
# ---------------------------------------------------------------------------


def test_absent_store_and_empty_recall_are_normal_no_memory_results() -> None:
    text = _all_skill_text()
    assert "normal no-memory result" in text


def test_retire_requires_explicit_user_approval_before_deleting() -> None:
    text = _all_skill_text()
    assert "explicit user approval before deleting" in text


# ---------------------------------------------------------------------------
# REQ-4: passive activation only, no fixed-station mandatory invocation
# ---------------------------------------------------------------------------


def test_no_fixed_station_mandatory_invocation() -> None:
    text = _skill_md_text()
    lowered = text.lower()
    assert "mandatory" not in lowered, "no station coupling may be phrased as mandatory"
    forbidden_station_names = {
        "loom-code:write-plan",
        "loom-code:build",
        "loom-code:review",
        "loom-code:ship",
        "loom-code:maintain",
        "loom-design:capture-intent",
        "loom-design:write-spec",
        "loom-design:design-system",
        "loom-design:product-principles",
    }
    for name in forbidden_station_names:
        assert name not in lowered, f"skill text must not couple to station {name!r}"


def test_activation_states_only_explicit_request_or_agent_judgement() -> None:
    text = _skill_md_text()
    lowered = text.lower()
    assert "explicit" in lowered
    assert "judgement" in lowered or "judgment" in lowered


# ---------------------------------------------------------------------------
# REQ-20: git-memory stays a separate, non-dependent sibling
# ---------------------------------------------------------------------------


def test_git_memory_boundary_is_stated() -> None:
    text = _skill_md_text()
    assert "git-memory" in text
    assert "commit- and pull-request-bound" in text
    assert "outlive a change" in text
    assert "runtime dependency of the other" in text.lower()


# ---------------------------------------------------------------------------
# REQ-21: no host-specific path or private API
# ---------------------------------------------------------------------------


def test_no_host_specific_path_or_private_api() -> None:
    text = _all_skill_text()
    forbidden_substrings = [
        "${CLAUDE_PLUGIN_ROOT}",
        ".claude-plugin",
        ".codex-plugin",
        "/Users/",
        "CLAUDE_PLUGIN_ROOT",
    ]
    for token in forbidden_substrings:
        assert token not in text, f"skill text must not depend on host-specific token {token!r}"


# ---------------------------------------------------------------------------
# REQ-23: migration is not implicit, and this skill is never a legacy reader
# ---------------------------------------------------------------------------


def test_legacy_store_reported_needing_explicit_migration_without_modification() -> None:
    text = _all_skill_text()
    assert "explicit migration" in text
    assert "without modifying any file" in text
    assert "never reads or writes that legacy format itself" in text


# ---------------------------------------------------------------------------
# Structure: flat folder, token cap, description budget
# ---------------------------------------------------------------------------


def test_skill_folder_is_flat_no_nested_subfolder() -> None:
    assert SKILL_DIR.is_dir()
    for entry in SKILL_DIR.iterdir():
        if entry.is_dir():
            for nested in entry.iterdir():
                assert not nested.is_dir(), (
                    f"{entry} must not contain a nested subfolder ({nested})"
                )


def test_skill_md_under_token_budget() -> None:
    text = _skill_md_text()
    word_count = len(text.split())
    assert word_count <= WORD_HARD_CAP, (
        f"SKILL.md is {word_count} words (hard cap: {WORD_HARD_CAP} words / ~6,000 tokens)"
    )


def test_description_under_listing_budget() -> None:
    text = _skill_md_text()
    description = _frontmatter_description(text)
    assert len(description) <= DESCRIPTION_BUDGET_CHARS, (
        f"frontmatter description is {len(description)} chars "
        f"(budget: {DESCRIPTION_BUDGET_CHARS})"
    )
    assert len(description) > 0


def test_references_exist_and_are_referenced() -> None:
    assert OKF_PROFILE.is_file()
    assert OPERATIONS.is_file()
    text = _skill_md_text()
    assert "references/okf-profile.md" in text
    assert "references/operations.md" in text


# ---------------------------------------------------------------------------
# Plugin manifest sanity: skills mount point exists, matching the plugin.json
# `"skills": "./skills/"` declaration this task builds under.
# ---------------------------------------------------------------------------


def test_skills_mount_declared_in_claude_manifest() -> None:
    manifest = json.loads(
        (REPO_ROOT / "loom-memory" / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest.get("skills") == "./skills/"
    assert (REPO_ROOT / "loom-memory" / "skills").is_dir()
