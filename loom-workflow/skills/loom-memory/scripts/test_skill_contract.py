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
import subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parents[2]
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
    """REQ-21 forbids a HOST-SPECIFIC path or private API — not the portable
    `${CLAUDE_PLUGIN_ROOT}` load-time textual substitution every sibling
    skill uses (e.g. `loom-code/skills/write-plan/SKILL.md`). That token
    is permitted here precisely because it is paired with a plain-language
    restatement (see `test_no_bare_repo_root_relative_script_path` below,
    which is what actually stops the non-portable form from coming back)."""
    text = _all_skill_text()
    forbidden_substrings = [
        ".claude-plugin",
        ".codex-plugin",
        "/Users/",
    ]
    for token in forbidden_substrings:
        assert token not in text, f"skill text must not depend on host-specific token {token!r}"
    assert not re.search(r"/home/[A-Za-z0-9_.-]+", text), (
        "skill text must not depend on an absolute home-directory path"
    )


def test_no_bare_repo_root_relative_script_path() -> None:
    """A `skills/loom-memory/scripts/...` path resolves only relative to
    THIS repository's root — a project that installs the plugin (per
    `loom-workflow/README.md`'s documented layout) has no `loom-workflow/`
    directory at its root, so that path cannot resolve there. The only
    portable form is `${CLAUDE_PLUGIN_ROOT}/skills/loom-memory/scripts/loom_memory.py`
    (or its plain-language restatement); a bare repo-root-relative path must
    never reappear in the shipped skill text — every paragraph naming the
    script path must always pair it with the `${CLAUDE_PLUGIN_ROOT}`
    substitution token somewhere in that same paragraph (prose wraps the
    token and its plain-language restatement across physical lines, so the
    pairing is checked per blank-line-delimited paragraph, not per physical
    line)."""
    text = _all_skill_text()
    for paragraph in re.split(r"\n\s*\n", text):
        if "skills/loom-memory/scripts/" in paragraph:
            assert "${CLAUDE_PLUGIN_ROOT}" in paragraph, (
                f"bare repo-root-relative script path resurfaced in skill text: {paragraph!r}"
            )


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
    """The flat-folder rule governs what the skill SHIPS, so this asks Git
    what is tracked rather than what happens to sit on disk.

    Walking the filesystem instead made the test report a failure whenever
    anyone had run pytest in the skill directory without
    `PYTHONDONTWRITEBYTECODE`, because the resulting `__pycache__` is a
    nested directory. That is a fact about the runner's environment, not
    about the layout being shipped, and the generated directory is not
    tracked at all.

    A bare `git ls-files` (without `--recurse-submodules`) reports a git
    submodule mounted under the skill directory as a single depth-1 gitlink
    entry, with no visibility into the submodule's own tracked tree — which
    can nest arbitrarily deep on disk once checked out with
    `git clone --recurse-submodules`. Rather than recurse into the
    submodule (which would depend on the clone's own submodule-init state
    to be meaningful), a gitlink is flagged directly, on the principle a
    skill ships files, not submodules: `git ls-files --stage` reports each
    entry's mode, and mode `160000` is exactly a gitlink.
    """
    assert SKILL_DIR.is_dir()
    staged = subprocess.run(
        ["git", "ls-files", "--stage", "--", SKILL_DIR.as_posix()],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    assert staged, "no tracked files under the skill directory"
    skill_rel = SKILL_DIR.relative_to(REPO_ROOT)
    for line in staged:
        left, _, rel = line.partition("\t")
        mode = left.split()[0]
        assert mode != "160000", (
            f"{rel} is a git submodule mounted under the skill directory; "
            "a skill ships files, not submodules"
        )
        depth = Path(rel).relative_to(skill_rel).parts
        assert len(depth) <= 2, (
            f"{rel} nests a subfolder inside a skill subfolder; the skill "
            "folder must be SKILL.md plus single-level subfolders"
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
# Plugin manifest sanity: this skill lives under loom-workflow's default
# skills mount (no explicit `"skills"` key — loom-workflow relies on the
# host's default `./skills/` convention, unlike the retired standalone
# loom-memory plugin).
# ---------------------------------------------------------------------------


def test_skills_mount_declared_in_claude_manifest() -> None:
    manifest = json.loads(
        (REPO_ROOT / "loom-workflow" / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest.get("name") == "loom-workflow"
    assert (REPO_ROOT / "loom-workflow" / "skills" / "loom-memory").is_dir()


# ---------------------------------------------------------------------------
# Acceptance A4 — the timing and scarcity halves of the Record contract
#
# READ THIS BEFORE YOU EDIT OR DELETE ANYTHING BELOW.
#
# These assertions pin two clauses of the shipped Record contract. They are
# not style checks and they are not a snapshot of prose someone liked.
#
# History, because it has already happened once: the timing clause was
# enforced from 2026-07-08 (#515) by five lines inside the
# `finishing-a-development-branch` skill plus a test pinning them. The
# loom 1.0 cutover (#780) deleted that skill, and the instruction and its
# test went out together. Nobody noticed, because nothing was left to go
# red. The rule survived only as prose in one repository's own store
# charter, which no project installing this plugin ever reads.
#
# A phrase-presence assertion is a golden test at string granularity, and
# the documented way golden tests die is that a red one gets updated
# instead of investigated. That is exactly the failure above. So: if one
# of these goes red, the question is not "how do I make this green".
# The question is whether the clause it names is still in the shipped
# contract, and if you are removing it on purpose, that is a change to
# what this plugin promises — it needs an intent, not an edit here.
#
# The assertions pin required ELEMENTS after whitespace flattening, never
# whole sentences, so rewording that keeps both halves stays green.
# ---------------------------------------------------------------------------

_A4_WHY = (
    "This clause is part of the Record contract (timing + scarcity). It was "
    "lost once already when loom 1.0 deleted the skill carrying it along with "
    "its test. Removing it deliberately is a contract change and needs an "
    "intent; see this section's header comment."
)


def _flat(text: str) -> str:
    """Whitespace-flattened, lowercased text — prose wraps, meaning does not."""
    return " ".join(text.split()).lower()


TIMING_ELEMENTS = (
    "before the branch closes",
    "that same branch",
    "separate post-merge branch",
    "pure overhead",
    "only confirmable by observing",
    "batched",
)

SCARCITY_ELEMENTS = (
    "not a durable lesson",
    "belongs in its commit",
    "belongs in the change's evidence",
    "belongs in an intent",
    "zero to one durable lesson per change",
)


def test_record_contract_states_when_to_record() -> None:
    """Timing half: a fact known before the branch closes lands in that branch."""
    flat = _flat(_all_skill_text())
    for element in TIMING_ELEMENTS:
        assert element in flat, (
            f"the Record contract no longer states {element!r}. {_A4_WHY}"
        )


def test_record_contract_states_how_much_to_record() -> None:
    """Scarcity half: most of what a change surfaces is not a durable lesson."""
    flat = _flat(_all_skill_text())
    for element in SCARCITY_ELEMENTS:
        assert element in flat, (
            f"the Record contract no longer states {element!r}. {_A4_WHY}"
        )


def test_both_halves_live_in_the_record_section_itself() -> None:
    """Neither half may drift into an unrelated section, where a reader
    following Record would not meet it."""
    record = _flat(_section(_skill_md_text(), "Record"))
    assert "before the branch closes" in record, (
        "the timing clause left the Record section of SKILL.md. " + _A4_WHY
    )
    assert "not a durable lesson" in record, (
        "the scarcity clause left the Record section of SKILL.md. " + _A4_WHY
    )
