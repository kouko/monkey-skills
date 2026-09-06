"""Adversarial probes against W0-01 (artifact charter rows in the contract
manifest, rendered by `loom_checker.py charter`), written BEFORE W0-01
exists per the adversary-first dispatch order.

Targets (not yet implemented at commit time -- W0-01 is the RED->GREEN task):
* `artifacts.<name>.charter` keys (`answers`, `readers`, `must`, `must_not`,
  `signoff`, `edits_after`) in `loom-code/contract/manifest.yaml`.
* the four new artifact entries `blind-run-report`, `memory`,
  `kickoff-defaults`, `dispatch`.
* a `charter` sub-command on `loom_checker.py` that renders the markdown
  table and exits non-zero with one `BLOCK contract.charter-complete: ...`
  line per incomplete row.
* rule id `contract.charter-complete` appearing in `--list-rules`.
* `.codex/hooks/contract/manifest.yaml` staying a byte-for-byte mirror of
  `loom-code/contract/manifest.yaml` after the charter keys land.

No mutation/fuzz tool is declared for this repo (loom-code has none in its
KICKOFF-DEFAULTS or pyproject config), so this file is the required >=3
executable abuse/boundary cases -- it has more. Every scenario except the
mirror-equality check builds its own tmp_path copy of the manifest; the
real committed manifest is never edited by this file.

Each test's docstring records `Attack:` / `Expected (after W0-01):` /
`Observed (before W0-01, at this commit)`, the last filled in from an
actual run, per the adversary contract's ban on cases that only ran in
the adversary's head.
"""
from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
REAL_MANIFEST = REPO_ROOT / "loom-code" / "contract" / "manifest.yaml"
CODEX_MIRROR_MANIFEST = REPO_ROOT / ".codex" / "hooks" / "contract" / "manifest.yaml"

NEW_ARTIFACTS = {
    "blind-run-report": {"path": "docs/loom/<change-id>/blind-run-report.md"},
    "memory": {"path": "docs/loom/memory/<slug>.md"},
    "kickoff-defaults": {"path": "docs/loom/KICKOFF-DEFAULTS.md"},
    "dispatch": {"path": "docs/loom/<change-id>/review.json#dispatch"},
}

ALL_ROWS = [
    "intent", "spec", "plan", "review",
    "blind-run-report", "memory", "kickoff-defaults", "dispatch",
]


def _valid_row(name: str, goes_to: str) -> dict:
    return {
        "answers": f"who reads the {name} artifact and why",
        "readers": ["reviewer"],
        "must": ["decision"],
        "must_not": [{"kind": "code", "goes_to": goes_to}],
        "signoff": "review",
        "edits_after": [{"id": f"{name}-fix-round-lands", "text": "a fix round lands"}],
    }


def _load_real_manifest() -> dict:
    return yaml.safe_load(REAL_MANIFEST.read_text(encoding="utf-8"))


def _manifest_with_charter(tmp_path: Path, mutate=None, omit_row: str | None = None) -> Path:
    """A tmp copy of the real manifest with the four new artifact entries
    added and a valid `charter:` block stamped on all eight rows, then
    `mutate(data)` applied (in place) if given. `omit_row` drops the
    `charter:` key from that one row entirely (empty-charter probe)."""
    data = copy.deepcopy(_load_real_manifest())
    for name, extra in NEW_ARTIFACTS.items():
        data["artifacts"][name] = dict(extra)
    for name in ALL_ROWS:
        goes_to = "plan" if name == "review" else "review"
        data["artifacts"][name]["charter"] = _valid_row(name, goes_to)
    if omit_row:
        del data["artifacts"][omit_row]["charter"]
    if mutate:
        mutate(data)
    out = tmp_path / "manifest.yaml"
    out.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return out


def run_charter(manifest_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "charter", "--manifest", str(manifest_path)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


# --- 1. empty `must` -----------------------------------------------------

def test_charter_row_with_empty_must_blocked(tmp_path):
    """Attack: a row's `must` list is emptied ([]).
    Expected (after W0-01): exit non-zero, one BLOCK contract.charter-complete
    line naming `spec.must`.
    Observed (before W0-01, at this commit): `charter` is not a known
    sub-command yet -- `main` raises UsageError and exits 2 with
    "unknown sub-command 'charter'." on stderr, never a BLOCK line."""
    def mutate(data):
        data["artifacts"]["spec"]["charter"]["must"] = []

    manifest = _manifest_with_charter(tmp_path, mutate=mutate)
    result = run_charter(manifest)
    assert result.returncode != 0
    assert "contract.charter-complete" in blocked_rules(result)
    assert "spec.must" in result.stderr


# --- 2. must_not entry lacking goes_to ------------------------------------

def test_charter_row_must_not_missing_goes_to_blocked(tmp_path):
    """Attack: a `must_not` entry carries `kind` but no `goes_to`.
    Expected (after W0-01): BLOCK contract.charter-complete naming
    `plan.must_not`.
    Observed (before W0-01): unknown sub-command, exit 2, no BLOCK line."""
    def mutate(data):
        data["artifacts"]["plan"]["charter"]["must_not"] = [{"kind": "code"}]

    manifest = _manifest_with_charter(tmp_path, mutate=mutate)
    result = run_charter(manifest)
    assert result.returncode != 0
    assert "contract.charter-complete" in blocked_rules(result)
    assert "plan.must_not" in result.stderr


# --- 3. goes_to naming an artifact absent from the table -------------------

def test_charter_row_goes_to_unknown_artifact_blocked(tmp_path):
    """Attack: `goes_to: nonexistent-artifact`, a name absent from the
    eight-row table.
    Expected (after W0-01): BLOCK contract.charter-complete naming
    `memory.must_not` (or the offending goes_to value).
    Observed (before W0-01): unknown sub-command, exit 2, no BLOCK line."""
    def mutate(data):
        data["artifacts"]["memory"]["charter"]["must_not"] = [
            {"kind": "code", "goes_to": "nonexistent-artifact"}
        ]

    manifest = _manifest_with_charter(tmp_path, mutate=mutate)
    result = run_charter(manifest)
    assert result.returncode != 0
    assert "contract.charter-complete" in blocked_rules(result)


# --- 3b. goes_to naming itself ---------------------------------------------

def test_charter_row_goes_to_self_blocked(tmp_path):
    """Attack: `goes_to` names the row's own artifact -- a self-loop that
    passes a naive 'names another artifact in the table' membership check
    but violates 'goes to ANOTHER artifact'.
    Expected (after W0-01): BLOCK contract.charter-complete naming
    `dispatch.must_not` (self-reference rejected).
    Observed (before W0-01): unknown sub-command, exit 2, no BLOCK line."""
    def mutate(data):
        data["artifacts"]["dispatch"]["charter"]["must_not"] = [
            {"kind": "code", "goes_to": "dispatch"}
        ]

    manifest = _manifest_with_charter(tmp_path, mutate=mutate)
    result = run_charter(manifest)
    assert result.returncode != 0
    assert "contract.charter-complete" in blocked_rules(result)


# --- 4. signoff naming an unknown station ----------------------------------

def test_charter_row_signoff_unknown_station_blocked(tmp_path):
    """Attack: `signoff: not-a-real-station`, absent from `stations:`.
    Expected (after W0-01): BLOCK contract.charter-complete naming
    `kickoff-defaults.signoff`.
    Observed (before W0-01): unknown sub-command, exit 2, no BLOCK line."""
    def mutate(data):
        data["artifacts"]["kickoff-defaults"]["charter"]["signoff"] = "not-a-real-station"

    manifest = _manifest_with_charter(tmp_path, mutate=mutate)
    result = run_charter(manifest)
    assert result.returncode != 0
    assert "contract.charter-complete" in blocked_rules(result)
    assert "kickoff-defaults.signoff" in result.stderr


# --- 5. an artifact with no charter key at all -----------------------------

def test_charter_row_missing_entirely_blocked(tmp_path):
    """Attack: `intent` gets no `charter:` key at all (as if W0-01 forgot
    a row, or an older manifest is fed in unmigrated).
    Expected (after W0-01): BLOCK contract.charter-complete naming `intent`
    (whole row missing, not one column).
    Observed (before W0-01): unknown sub-command, exit 2, no BLOCK line."""
    manifest = _manifest_with_charter(tmp_path, omit_row="intent")
    result = run_charter(manifest)
    assert result.returncode != 0
    assert "contract.charter-complete" in blocked_rules(result)
    assert "intent" in result.stderr


# --- 6. --manifest pointing at a missing file ------------------------------

def test_charter_command_manifest_path_missing_fails_closed(tmp_path):
    """Attack: `--manifest` points at a file that does not exist.
    Expected: exit 2 (usage/internal error), never exit 0 -- a checker
    that cannot read its input never says 'fine' (module docstring:
    'Any unexpected exception fails closed as exit 2').
    Observed (before W0-01): exit 2 already, but for the wrong reason
    (unknown sub-command 'charter'), not a missing-manifest message --
    this probe will need re-pointing once `charter` exists, since a
    missing --manifest should be caught before 'unknown sub-command' can
    even be reached only when the command IS recognised."""
    missing = tmp_path / "does-not-exist.yaml"
    result = run_charter(missing)
    assert result.returncode == 2
    assert result.returncode != 0


# --- 7. duplicated artifact name --------------------------------------------

def test_manifest_duplicate_artifact_key_collapses_silently():
    """Attack: hand-write a manifest whose `artifacts:` mapping repeats the
    same key (`spec:`) twice with different `charter:` blocks, simulating
    a bad hand-edit or merge conflict resolved wrong.
    Expected/Observed (true today, independent of W0-01): YAML mappings
    cannot carry duplicate keys -- `yaml.safe_load` silently keeps only the
    LAST occurrence and raises no error, so a duplicated artifact name is
    structurally impossible to detect from the parsed data alone; any
    'duplicate name' rule the implementer might consider must scan the raw
    text (e.g. a key-count regex) rather than trust the parsed mapping.
    This is recorded as a finding, not a fatal probe failure, since the
    W0-01 interface never promises duplicate-key detection."""
    raw = (
        "artifacts:\n"
        "  spec:\n"
        "    path: docs/loom/<change-id>/spec.md\n"
        "    charter: {answers: first, readers: [r], must: [a], "
        "must_not: [{kind: c, goes_to: plan}], signoff: review, edits_after: [x]}\n"
        "  spec:\n"
        "    path: docs/loom/<change-id>/spec.md\n"
        "    charter: {answers: second, readers: [r], must: [a], "
        "must_not: [{kind: c, goes_to: plan}], signoff: review, edits_after: [x]}\n"
    )
    data = yaml.safe_load(raw)
    assert list(data["artifacts"].keys()).count("spec") == 1
    assert data["artifacts"]["spec"]["charter"]["answers"] == "second"


# --- 8. non-ASCII / very long strings in `answers` -------------------------

def test_charter_row_non_ascii_and_huge_answers_does_not_crash(tmp_path):
    """Attack: `answers` carries CJK text, an emoji, and a 5000-character
    string in the same field.
    Expected (after W0-01): the command either renders the row (possibly
    truncated) or blocks it for a length reason -- but never raises an
    unhandled exception (module docstring: 'fail closed as exit 2', never
    an uncaught traceback with exit 1 nonsense).
    Observed (before W0-01): unknown sub-command, exit 2, clean stderr
    message, no traceback -- this already holds, since main() never
    reaches the mutated data at all yet."""
    def mutate(data):
        long_answer = ("配置與稽核 🔥 " * 400)[:5000] + "非ASCII結尾"
        data["artifacts"]["plan"]["charter"]["answers"] = long_answer

    manifest = _manifest_with_charter(tmp_path, mutate=mutate)
    result = run_charter(manifest)
    assert "Traceback" not in result.stderr
    assert result.returncode in (0, 1, 2)


# --- 9. exactly eight rows, every row's four columns non-empty ------------

def test_charter_command_renders_eight_complete_rows_on_valid_manifest(tmp_path):
    """Attack/floor case: feed a manifest where every one of the eight rows
    carries a fully valid charter -- the happy path the interface promises.
    Expected (after W0-01): exit 0, markdown table with exactly 8 data rows
    (one per artifact: intent, spec, plan, review, blind-run-report,
    memory, kickoff-defaults, dispatch), and each row's must / must-not+
    goes-to / sign-off / edits-after columns non-empty.
    Observed (before W0-01): unknown sub-command, exit 2, no table at all."""
    manifest = _manifest_with_charter(tmp_path)
    result = run_charter(manifest)
    assert result.returncode == 0
    lines = [ln for ln in result.stdout.splitlines() if ln.strip().startswith("|")]
    data_rows = [ln for ln in lines if not set(ln.replace("|", "").strip()) <= {"-", " "}]
    data_rows = [ln for ln in data_rows if "artifact" not in ln.split("|")[1].lower()]
    assert len(data_rows) == 8, f"expected 8 data rows, got {len(data_rows)}: {data_rows}"
    for row in data_rows:
        cols = [c.strip() for c in row.strip().strip("|").split("|")]
        assert len(cols) >= 5
        assert all(cols), f"an empty column in row: {row!r}"


# --- 10. --list-rules carries contract.charter-complete --------------------

def test_list_rules_carries_charter_complete_rule_id():
    """Attack: check the rule registry, the SSOT `--list-rules` claims to
    be, for the new rule id.
    Expected (after W0-01): `contract.charter-complete` is one of the
    tab-separated rule ids on stdout.
    Observed (before W0-01, at this commit): absent -- `RULES` in
    loom_checker.py has no `contract.charter-complete` entry yet."""
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--list-rules"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0
    rule_ids = {line.split("\t", 1)[0] for line in result.stdout.splitlines()}
    assert "contract.charter-complete" in rule_ids


# --- 11. codex mirror equals plugin manifest byte for byte -----------------

def test_codex_mirror_manifest_matches_plugin_manifest_byte_for_byte():
    """Regression guard, not a W0-01-only probe: `.codex/hooks/contract/
    manifest.yaml` (concept-model §7a Codex scaffold copy) must stay a
    byte-for-byte copy of `loom-code/contract/manifest.yaml`. This already
    passes today -- it is recorded so the next round catches the
    implementer forgetting to re-run `codex_scaffold.py` after adding the
    charter keys and the four new artifact rows.
    Expected/Observed (true today, before W0-01 touches either file):
    the two files are identical."""
    source = REAL_MANIFEST.read_text(encoding="utf-8")
    mirror = CODEX_MIRROR_MANIFEST.read_text(encoding="utf-8")
    assert source == mirror, (
        "loom-code/contract/manifest.yaml and .codex/hooks/contract/manifest.yaml "
        "have already diverged before W0-01 even started"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
