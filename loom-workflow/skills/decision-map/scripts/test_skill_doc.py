"""Doc-drift test: every script command SKILL.md cites must match the
§Command surface SSOT in references/map-format.md.

map-format.md quotes only one full invocation literally — the
`map_store.py validate <target> --repo-root <path>` example — so a
citation of that script is checked by exact (whitespace-normalized)
substring match against map-format.md. The other four scripts are
never spelled out as full invocations in map-format.md; instead it
pins their shape in prose (§Command surface's "canonical arg shape"
paragraph): a bare positional `target` plus `--repo-root <path>`,
with NO leading verb — only map_store.py carries a verb (`validate`).
So a citation of those four is checked structurally against that
pinned shape. Either check failing means SKILL.md drifted from the
SSOT; the assertion names the offending quote.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
MAP_FORMAT_MD = SKILL_DIR / "references" / "map-format.md"
PROTOTYPE_CONTRACT_MD = SKILL_DIR / "references" / "prototype-contract.md"
FAMILY_RECEPTION_MD = SKILL_DIR / "references" / "family-reception.md"
PLUGIN_ROOT = SKILL_DIR.parents[1]
CHANGELOG_MD = PLUGIN_ROOT / "CHANGELOG.md"
GOVERNANCE_MD = PLUGIN_ROOT / "docs" / "skill-governance.md"
CLAUDE_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
SCRIPTS_DIR = SKILL_DIR / "scripts"
FINISHING_SKILL_MD = (
    Path(__file__).resolve().parents[4]
    / "loom-code"
    / "skills"
    / "finishing-a-development-branch"
    / "SKILL.md"
)

SCRIPT_NAMES = (
    "map_init.py",
    "map_store.py",
    "check_map_links.py",
    "check_map_fog.py",
    "map_progress.py",
)

V2_RETIRED_WRITEBACK_PHRASES = (
    "delegate to a backlog entry",
    "task → a backlog entry",
    "filing the backlog entry IS the resolution",
    "Parts section",
    "Parts row",
    "Delivery write-back",
)

INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")

# script[.py] [verb] <target> --repo-root <path>
COMMAND_SHAPE_RE = re.compile(
    r"^(?P<script>[a-z_]+\.py)"
    r"(?:\s+(?P<verb>[a-z_]+))?"
    r"\s+(?P<target><[^>]+>)"
    r"\s+--repo-root\s+(?P<repo><[^>]+>)$"
)


def _normalize(command: str) -> str:
    """Collapse whitespace so line-wrapped or re-spaced quotes still match."""
    return " ".join(command.split())


def _script_commands(text: str) -> list[str]:
    """Every inline-code span that opens with one of the four script names."""
    commands = []
    for span in INLINE_CODE_RE.findall(text):
        stripped = span.strip()
        if stripped.startswith(SCRIPT_NAMES):
            commands.append(stripped)
    return commands


def test_skill_commands_match_command_surface():
    assert SKILL_MD.is_file(), f"missing {SKILL_MD}"
    assert MAP_FORMAT_MD.is_file(), f"missing {MAP_FORMAT_MD}"

    skill_text = SKILL_MD.read_text(encoding="utf-8")
    surface_text = MAP_FORMAT_MD.read_text(encoding="utf-8")
    normalized_surface = _normalize(surface_text)

    skill_commands = _script_commands(skill_text)
    assert skill_commands, (
        "SKILL.md cites no script commands from the pinned command surface "
        f"({', '.join(SCRIPT_NAMES)}) — expected at least one"
    )

    offenders = []
    for quote in skill_commands:
        normalized = _normalize(quote)
        match = COMMAND_SHAPE_RE.match(normalized)
        if not match:
            offenders.append((quote, "does not match canonical arg shape "
                              "'<script>.py [verb] <target> --repo-root <path>'"))
            continue
        script = match.group("script")
        verb = match.group("verb")
        if script == "map_store.py":
            # The one script with a literal full-invocation quote in the
            # SSOT — require exact (whitespace-normalized) substring match.
            if verb != "validate":
                offenders.append((quote, "map_store.py must carry the "
                                  "'validate' verb — no other verb is pinned"))
            elif normalized not in normalized_surface:
                offenders.append((quote, "not found verbatim in "
                                  "references/map-format.md §Command surface"))
        else:
            # The other four take the bare positional shape — no verb.
            if verb is not None:
                offenders.append((quote, f"{script} takes no verb "
                                  f"(§Command surface pins a bare positional "
                                  f"shape) — found verb {verb!r}"))

    assert not offenders, "SKILL.md command citation(s) drifted from " \
        "references/map-format.md §Command surface:\n" + "\n".join(
            f"  {quote!r}: {reason}" for quote, reason in offenders
        )


def test_v2_contract_rejects_relay_and_parts_language():
    """The v2 contract has no backlog relay or mutable Parts write-back."""
    contract_files = (MAP_FORMAT_MD, SKILL_MD)
    offenders = [
        f"{path}: {phrase}"
        for path in contract_files
        for phrase in V2_RETIRED_WRITEBACK_PHRASES
        if phrase.lower() in path.read_text(encoding="utf-8").lower()
    ]

    assert not offenders, "retired v2 contract wording remains:\n" + "\n".join(offenders)


def test_v3_contract_defines_multi_delivery_outcome_loop():
    # @req: REQ-75
    """A delivery closes one arc without completing or clearing its Map."""
    contract_files = (SKILL_MD, MAP_FORMAT_MD)
    for path in contract_files:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert "one persistent outcome-control loop" in text
        assert "multiple independently closed delivery arcs" in text
        assert "Closing a delivery arc must not clear the Map." in text


def test_v3_public_surface_commands_templates_and_version_are_synchronized():
    # @req: REQ-75
    skill = _normalize(SKILL_MD.read_text(encoding="utf-8"))
    map_format = _normalize(MAP_FORMAT_MD.read_text(encoding="utf-8"))
    prototype = _normalize(PROTOTYPE_CONTRACT_MD.read_text(encoding="utf-8"))
    family = _normalize(FAMILY_RECEPTION_MD.read_text(encoding="utf-8"))
    changelog = CHANGELOG_MD.read_text(encoding="utf-8")
    governance = _normalize(GOVERNANCE_MD.read_text(encoding="utf-8"))
    claude_manifest = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
    codex_manifest = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))

    assert claude_manifest["version"] == "3.0.0"
    assert codex_manifest["version"] == "3.0.0"
    for manifest in (claude_manifest, codex_manifest):
        assert "Outcome Map" in manifest["description"]
        assert "decision-map" in manifest["keywords"]
    assert "## [3.0.0]" in changelog
    assert "v3.0.0" in governance

    for public_contract in (skill, map_format):
        assert "one persistent outcome-control loop" in public_contract
        assert "multiple independently closed delivery arcs" in public_contract
        assert "exactly four closure types" in public_contract.lower()
        assert "`grilling`, `research`, `prototype`, and `delivery`" in public_contract
        assert "one outcome-advancing slice" in public_contract
        assert "source of truth" in public_contract
        assert "Map clear" in public_contract
        assert "retirement" in public_contract.lower()
        assert "schema_version: 3" in public_contract

    assert "machine-measured feasibility" in prototype
    assert "research" in prototype
    assert "human evaluates" in prototype
    assert "prototype" in prototype
    assert "multiple sessions" in family and "decision-map" in family

    operations = (
        "Start",
        "Resume",
        "Claim",
        "Update blockers",
        "Close and re-chart",
        "Migrate v2 to v3",
        "Archive",
    )
    for operation in operations:
        assert operation in skill
    assert "preview_migration(map_dir)" in skill
    assert "apply_migration(map_dir, preview)" in skill
    assert "zero-write preview" in skill

    commands = {
        "map_init.py <map-id> --repo-root <path>": "map_init.py",
        "map_store.py validate <map-dir> --repo-root <path>": "map_store.py",
        "check_map_links.py <map-dir> --repo-root <path>": "check_map_links.py",
        "check_map_fog.py <map-dir> --repo-root <path>": "check_map_fog.py",
        "map_progress.py <target> --repo-root <path>": "map_progress.py",
    }
    for command, script in commands.items():
        assert command in skill
        assert command in map_format
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / script), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr

    ticket_template = (
        "type: <grilling|research|prototype|delivery> status: open "
        "claim: null graduated-from: null"
    )
    assert ticket_template in map_format


def test_v3_contract_pins_release_boundary_and_metric_definition():
    """Current map instructions retain the v3 boundary and metric facts."""
    map_format_text = MAP_FORMAT_MD.read_text(encoding="utf-8")
    skill_text = SKILL_MD.read_text(encoding="utf-8")

    assert "schema_version: 3" in map_format_text
    assert "v1" not in map_format_text
    assert "Exactly four closure types exist" in skill_text
    assert "Dependencies are graph edges, not ticket types" in map_format_text
    assert "A closed delivery alone is never a clear transition" in map_format_text


def test_no_live_contract_or_command_surface_references_map_parts():
    """The retired Parts flipper and its tests must not remain live."""
    retired_script = SKILL_DIR / "scripts" / "map_parts.py"
    retired_test = SKILL_DIR / "scripts" / "test_map_parts.py"
    assert not retired_script.exists(), retired_script
    assert not retired_test.exists(), retired_test

    for path in (SKILL_MD, MAP_FORMAT_MD):
        text = path.read_text(encoding="utf-8").lower()
        assert "map_parts.py" not in text, f"{path} still references map_parts.py"


def test_no_live_finishing_skill_map_parts_writeback_instruction():
    """Close-out instructions must not invoke the retired Parts flipper."""
    text = FINISHING_SKILL_MD.read_text(encoding="utf-8").lower()
    assert "map delivery-progress check" in text
    assert "map-parts check" not in text
    assert "parts flipper" not in text
    assert "map_parts.py" not in text
    assert "flip that part's parts row" not in text
