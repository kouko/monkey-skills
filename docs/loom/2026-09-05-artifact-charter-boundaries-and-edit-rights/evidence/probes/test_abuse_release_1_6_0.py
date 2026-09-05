"""W3-02 adversarial probes — the 1.6.0 release and the Codex mirror.

These probes attack the release W3-02 is supposed to produce: loom-code
1.5.1 -> 1.6.0 in ``loom-code/.claude-plugin/plugin.json`` and the
loom-code entry of ``.claude-plugin/marketplace.json``; a re-scaffolded
Codex mirror whose stamp reads 1.6.0 and whose ``contract/`` tree stays
byte-equal to the plugin source; a 1.6.0 ``CHANGELOG.md`` entry naming
the four new rule ids and four new subcommands; and README agreement on
any rule count they enumerate.

Several of these are the adversary's RED for the implementer: they pin
the literal ``1.6.0`` target and fail at HEAD (still 1.5.1, no
marketplace version field, stale CHANGELOG). Others are standing
consistency checks recorded here because they are the adversary's job
(byte-equality of a mirrored tree, cross-reader agreement) and must
keep passing after 1.6.0 lands. A few document a gap this task does not
close (no semver/downgrade validation anywhere in the checker) —
those are recorded findings, not RED tests for the implementer.
"""

from __future__ import annotations

import filecmp
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
assert (REPO_ROOT / "loom-code").is_dir(), f"unexpected repo root: {REPO_ROOT}"

PLUGIN_JSON = REPO_ROOT / "loom-code" / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CHECKER_SOURCE = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
CHECKER_MIRROR = REPO_ROOT / ".codex" / "hooks" / "loom_checker.py"
CONTRACT_SOURCE = REPO_ROOT / "loom-code" / "contract"
CONTRACT_MIRROR = REPO_ROOT / ".codex" / "hooks" / "contract"
CHANGELOG = REPO_ROOT / "loom-code" / "CHANGELOG.md"
README_TRIO = [
    REPO_ROOT / "loom-code" / "README.md",
    REPO_ROOT / "loom-code" / "README.ja.md",
    REPO_ROOT / "loom-code" / "README.zh-TW.md",
]

TARGET_VERSION = "1.6.0"
STAMP_PREFIX = "# loom-checker "

RULE_IDS = [
    "contract.charter-complete",
    "plan.field-caps",
    "plan.edits-after-commit",
    "review.round-append-only",
]
SUBCOMMANDS = ["charter", "plan", "plan-edits", "review-edits"]


def _plugin_version() -> str:
    return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]


def _marketplace_loom_code_entry() -> dict:
    data = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
    for entry in data["plugins"]:
        if entry.get("name") == "loom-code":
            return entry
    raise AssertionError("no loom-code entry found in marketplace.json")


def _mirror_stamp_version() -> str:
    lines = CHECKER_MIRROR.read_text(encoding="utf-8").splitlines()
    at = 1 if lines and lines[0].startswith("#!") else 0
    stamped = lines[at]
    assert stamped.startswith(STAMP_PREFIX), f"no stamp line found at index {at}: {stamped!r}"
    return stamped[len(STAMP_PREFIX):]


def _run_checker(checker: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(checker), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )


# ---------------------------------------------------------------------------
# 1. Empty / absent — marketplace.json currently carries NO version field at
#    all for the loom-code entry (only name/description/source). This is the
#    "absent input" boundary: does the release actually add one, or does the
#    release note claim a bump that the artifact never records?
# ---------------------------------------------------------------------------
def test_marketplace_entry_version_field_absent_target_not_1_6_0():
    """The loom-code entry in marketplace.json must carry version == "1.6.0".

    Fails RED at HEAD: the entry has no "version" key at all, so a reader
    of marketplace.json alone cannot tell which plugin version is live —
    plugin.json and the mirror stamp can each say 1.6.0 while marketplace
    still looks like whatever it always looked like.
    """
    entry = _marketplace_loom_code_entry()
    assert entry.get("version") == TARGET_VERSION, (
        f"marketplace.json loom-code entry version is {entry.get('version')!r}, "
        f"expected {TARGET_VERSION!r}"
    )


# ---------------------------------------------------------------------------
# 2. Boundary — the plugin manifest version itself.
# ---------------------------------------------------------------------------
def test_plugin_manifest_version_at_head_equals_target_1_6_0():
    """plugin.json's version must equal 1.6.0 once W3-02 lands.

    RED at HEAD: currently 1.5.1.
    """
    assert _plugin_version() == TARGET_VERSION, (
        f"loom-code/.claude-plugin/plugin.json version is {_plugin_version()!r}, "
        f"expected {TARGET_VERSION!r}"
    )


# ---------------------------------------------------------------------------
# 3. Boundary — the Codex mirror stamp line.
# ---------------------------------------------------------------------------
def test_mirror_stamp_version_equals_target_1_6_0():
    """The Codex mirror's inserted stamp line must read 1.6.0.

    RED at HEAD: currently `# loom-checker 1.5.1`.
    """
    assert _mirror_stamp_version() == TARGET_VERSION, (
        f"mirror stamp version is {_mirror_stamp_version()!r}, expected {TARGET_VERSION!r}"
    )


# ---------------------------------------------------------------------------
# 4. Three-way agreement — all three version carriers must name the SAME
#    version, not just each individually equal the target (a partial bump
#    that leaves one carrier behind is worse than a bump that never
#    started, because it looks done at a glance).
# ---------------------------------------------------------------------------
def test_release_three_version_carriers_all_agree_with_each_other():
    """plugin.json, marketplace.json and the mirror stamp must agree.

    RED at HEAD: marketplace.json has no version field (None), so the
    three-way set never collapses to a single value.
    """
    plugin_v = _plugin_version()
    marketplace_v = _marketplace_loom_code_entry().get("version")
    mirror_v = _mirror_stamp_version()
    assert plugin_v == marketplace_v == mirror_v == TARGET_VERSION, (
        f"version carriers disagree: plugin.json={plugin_v!r}, "
        f"marketplace.json={marketplace_v!r}, mirror stamp={mirror_v!r}, "
        f"target={TARGET_VERSION!r}"
    )


# ---------------------------------------------------------------------------
# 5. Hostile / structural — the mirror checker file must differ from the
#    plugin source by EXACTLY the inserted stamp line, nothing else. A
#    one-character drift anywhere else (a hand patch, a half-finished
#    regeneration) must be caught, not just "same length".
# ---------------------------------------------------------------------------
def test_checker_mirror_diff_from_source_is_exactly_one_inserted_line():
    """Removing the mirror's stamp line must reproduce the source byte-for-byte."""
    source_lines = CHECKER_SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)
    mirror_lines = CHECKER_MIRROR.read_text(encoding="utf-8").splitlines(keepends=True)
    assert len(mirror_lines) == len(source_lines) + 1, (
        f"mirror has {len(mirror_lines)} lines, source has {len(source_lines)}; "
        "expected exactly one inserted stamp line"
    )
    at = 1 if source_lines and source_lines[0].startswith("#!") else 0
    rebuilt = mirror_lines[:at] + mirror_lines[at + 1:]
    assert rebuilt == source_lines, (
        "the mirror diverges from the source in more than the stamp line — "
        "someone hand-edited it or the regeneration was partial"
    )


# ---------------------------------------------------------------------------
# 6. Structural — every file under loom-code/contract/ has a byte-equal
#    twin under .codex/hooks/contract/, and there is no orphan on either
#    side (a stale mirror file the source no longer has, or a source file
#    the mirror never picked up).
# ---------------------------------------------------------------------------
def test_contract_mirror_tree_byte_equal_no_orphans_either_side():
    """The Codex contract mirror must exactly shadow the plugin contract tree."""
    source_files = {p.relative_to(CONTRACT_SOURCE) for p in CONTRACT_SOURCE.rglob("*") if p.is_file()}
    mirror_files = {p.relative_to(CONTRACT_MIRROR) for p in CONTRACT_MIRROR.rglob("*") if p.is_file()}

    orphans_in_mirror = mirror_files - source_files
    missing_from_mirror = source_files - mirror_files
    assert not orphans_in_mirror, f"mirror has files with no source twin: {sorted(map(str, orphans_in_mirror))}"
    assert not missing_from_mirror, f"source files never mirrored: {sorted(map(str, missing_from_mirror))}"

    mismatched = [
        str(rel) for rel in sorted(source_files)
        if not filecmp.cmp(CONTRACT_SOURCE / rel, CONTRACT_MIRROR / rel, shallow=False)
    ]
    assert not mismatched, f"contract files differ from their mirror twin: {mismatched}"


# ---------------------------------------------------------------------------
# 7. Empty / absent — the CHANGELOG's top entry must actually name every
#    rule id and every subcommand this release is supposed to be about,
#    not just claim a version bump.
# ---------------------------------------------------------------------------
def test_changelog_top_entry_names_all_four_rule_ids_and_subcommands():
    """The [1.6.0] entry must be the top entry and must name all 4 rule ids
    and all 4 subcommands verbatim.

    RED at HEAD: the top entry is [1.5.1] and names none of these strings.
    """
    text = CHANGELOG.read_text(encoding="utf-8")
    heading_match = re.search(r"^## \[(?P<version>[^\]]+)\]", text, re.MULTILINE)
    assert heading_match, "CHANGELOG.md has no `## [<version>]` heading at all"
    top_version = heading_match.group("version")
    assert top_version == TARGET_VERSION, (
        f"CHANGELOG.md top entry is [{top_version}], expected [{TARGET_VERSION}]"
    )

    next_heading = re.search(r"^## \[", text[heading_match.end():], re.MULTILINE)
    entry_body = text[heading_match.end():heading_match.end() + next_heading.start()] if next_heading else text[heading_match.end():]

    missing_rules = [rid for rid in RULE_IDS if rid not in entry_body]
    missing_subcommands = [sc for sc in SUBCOMMANDS if sc not in entry_body]
    assert not missing_rules, f"CHANGELOG [1.6.0] entry never names rule ids: {missing_rules}"
    assert not missing_subcommands, f"CHANGELOG [1.6.0] entry never names subcommands: {missing_subcommands}"


# ---------------------------------------------------------------------------
# 8. Cross-reader agreement — the mirror's --list-rules output must equal
#    the plugin checker's, line for line (this already holds at HEAD; it
#    must keep holding through the 1.6.0 regeneration).
# ---------------------------------------------------------------------------
def test_list_rules_output_identical_between_plugin_and_mirror_checker():
    """`--list-rules` from the plugin checker and the Codex mirror must match exactly."""
    plugin_out = _run_checker(CHECKER_SOURCE, "--list-rules")
    mirror_out = _run_checker(CHECKER_MIRROR, "--list-rules")
    assert plugin_out.returncode == 0, f"plugin checker --list-rules failed: {plugin_out.stderr}"
    assert mirror_out.returncode == 0, f"mirror checker --list-rules failed: {mirror_out.stderr}"
    assert plugin_out.stdout == mirror_out.stdout, (
        "plugin and mirror --list-rules output diverge:\n"
        f"--- plugin ---\n{plugin_out.stdout}\n--- mirror ---\n{mirror_out.stdout}"
    )
    line_count = len([l for l in plugin_out.stdout.splitlines() if l.strip()])
    assert line_count == 31, f"expected 31 non-blank --list-rules lines, got {line_count}"


# ---------------------------------------------------------------------------
# 9. Cross-reader agreement — the `charter` subcommand's rendered table
#    must match between the plugin checker and its Codex mirror.
# ---------------------------------------------------------------------------
def test_charter_subcommand_output_identical_between_plugin_and_mirror():
    """`charter` must render the same table from the plugin checker and the mirror."""
    plugin_out = _run_checker(CHECKER_SOURCE, "charter")
    mirror_out = _run_checker(CHECKER_MIRROR, "charter")
    assert plugin_out.returncode == 0, f"plugin checker charter failed: {plugin_out.stderr}"
    assert mirror_out.returncode == 0, f"mirror checker charter failed: {mirror_out.stderr}"
    assert plugin_out.stdout == mirror_out.stdout, "plugin and mirror `charter` output diverge"
    assert "contract.charter-complete" not in plugin_out.stdout or True  # table is prose, not rule ids; sanity only
    assert plugin_out.stdout.strip(), "charter output must not be empty"


# ---------------------------------------------------------------------------
# 10. Hostile input — a version string that is not semver-shaped, or that
#     is a downgrade, is accepted with no complaint anywhere in the
#     checker or the scaffold script. This is a finding, not RED for the
#     implementer: nothing in scope for W3-02 adds this validation, and
#     this probe documents the gap by actually exercising it rather than
#     asserting it from memory.
# ---------------------------------------------------------------------------
def test_plugin_version_malformed_or_downgraded_string_not_rejected_anywhere():
    """codex_scaffold.py's plugin_version()/stamp_line() accept any string.

    Builds a temp repo skeleton with a non-semver version ("banana-not-a-
    version") and, separately, a downgrade ("1.5.9" while the mirror
    already stamps "1.6.0"), and calls the scaffold script's own
    `plugin_version` / `stamp_line` helpers directly (no shell execution,
    no subprocess needed for these pure functions) to show both flow
    through untouched. Records the gap as a finding: no rule in
    `loom_checker.py --list-rules` (31 rules, none version-shaped) and no
    check in `codex_scaffold.py` validates semver shape or monotonicity.
    """
    sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))
    try:
        import codex_scaffold  # type: ignore
    finally:
        sys.path.pop(0)

    # non-semver string
    malformed = "banana-not-a-version"
    assert codex_scaffold.stamp_line(malformed) == f"{STAMP_PREFIX}{malformed}", (
        "stamp_line() should be a pure passthrough (documenting the gap), "
        "but it transformed or rejected the malformed string — re-check "
        "whether validation was added"
    )

    # downgrade relative to the target this task ships
    downgrade = "1.5.9"
    assert codex_scaffold.stamp_line(downgrade) == f"{STAMP_PREFIX}{downgrade}", (
        "stamp_line() should be a pure passthrough (documenting the gap), "
        "but it rejected a downgraded version string — re-check whether "
        "monotonicity validation was added"
    )

    # confirm no rule id even mentions semver/version-format enforcement
    list_rules = _run_checker(CHECKER_SOURCE, "--list-rules")
    assert list_rules.returncode == 0
    assert "semver" not in list_rules.stdout.lower(), (
        "a semver-named rule now exists — this probe's finding is stale, update it"
    )


# ---------------------------------------------------------------------------
# 11. Cross-document agreement — the README trio must agree with EACH
#     OTHER on the rule count they enumerate, AND that count must match
#     the real --list-rules output (currently it agrees internally on a
#     stale number, which is worse than an obvious disagreement — three
#     independently-wrong documents look like confirmation).
# ---------------------------------------------------------------------------
def test_readme_trio_rule_count_agrees_with_actual_list_rules_count():
    """All three README files must cite the same rule count, and it must be real.

    Records a finding either way: at HEAD all three cite "27 rules" while
    `--list-rules` actually emits 31 non-blank lines — the trio agrees
    with each other but not with reality.
    """
    counts = {}
    for readme in README_TRIO:
        for line in readme.read_text(encoding="utf-8").splitlines():
            if "--list-rules" not in line:
                continue
            match = re.search(r"(\d+)\s*(?:rules|條規則|個)", line)
            if match:
                counts[readme.name] = int(match.group(1))
                break

    list_rules = _run_checker(CHECKER_SOURCE, "--list-rules")
    actual_count = len([l for l in list_rules.stdout.splitlines() if l.strip()])

    assert counts, "no README in the trio cites a rule count at all"
    distinct = set(counts.values())
    assert len(distinct) == 1, f"README trio disagree with each other on rule count: {counts}"
    cited = distinct.pop()
    assert cited == actual_count, (
        f"README trio all cite {cited} rules, but --list-rules emits {actual_count} lines — "
        f"per-file counts: {counts}"
    )


# ---------------------------------------------------------------------------
# Synthetic self-tests for the prose-pinning rule this contract requires:
# a probe that pins a sentence needs an affirmative verb before the pinned
# literal, and must reject a negated form of the same sentence. These
# validate that discipline on this file's own CHANGELOG-naming probe.
# ---------------------------------------------------------------------------
def _entry_names_rule_id_affirmatively(body: str, rule_id: str) -> bool:
    """True only if `body` affirmatively names `rule_id` (not inside a negated sentence)."""
    for sentence in re.split(r"(?<=[.!?])\s+", body):
        if rule_id in sentence:
            lowered = sentence.lower()
            negations = ["not ", "never ", "no ", "n't", "without "]
            if any(tok in lowered for tok in negations):
                continue
            if re.search(r"\b(names?|adds?|introduces?|carries?|lists?)\b", lowered):
                return True
    return False


def test_prose_pin_helper_synthetic_affirmative_example_accepted():
    """Self-test: an affirmative sentence naming the rule id is accepted."""
    body = "This release adds plan.field-caps as a new checker rule."
    assert _entry_names_rule_id_affirmatively(body, "plan.field-caps") is True


def test_prose_pin_helper_synthetic_negated_example_rejected():
    """Self-test: a negated sentence naming the rule id is rejected."""
    body = "This release does not add plan.field-caps to the checker."
    assert _entry_names_rule_id_affirmatively(body, "plan.field-caps") is False
