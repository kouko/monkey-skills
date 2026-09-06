"""Branch-end adversarial probes for
2026-09-05-artifact-charter-boundaries-and-edit-rights — attacking the
LOOM_MANIFEST_PATH override (00cf003d), the nine graduated probe twins
(a9409281), the memory README index, the A/B evidence numbers, and the
1.6.0 release note, over the delta `git diff 39e4e20a..c782ca72`.

Every case below is independently re-runnable from the repo root:
    python3 -m pytest docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_branch_end.py -q -k <name>

No probe here writes into the tracked tree: manifest-override cases patch
scratch copies under `tmp_path` and point `LOOM_MANIFEST_PATH` at them.
"""
from __future__ import annotations

import difflib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
PLUGIN_MANIFEST = REPO / "loom-code" / "contract" / "manifest.yaml"
CHANGE_DIR = REPO / "docs" / "loom" / "2026-09-05-artifact-charter-boundaries-and-edit-rights"
EVIDENCE_PROBES = CHANGE_DIR / "evidence" / "probes"
GRADUATED_DIR = REPO / "loom-code" / "scripts"
MEMORY_DIR = REPO / "docs" / "loom" / "memory"
MEMORY_README = MEMORY_DIR / "README.md"


def _run(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = dict(os.environ)
    if env is not None:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=str(REPO), capture_output=True, text=True, env=full_env,
    )


# ---------------------------------------------------------------------------
# 1. Absent — LOOM_MANIFEST_PATH points at a file that does not exist.
# ---------------------------------------------------------------------------
def test_manifest_override_missing_file_fails_closed_not_traceback(tmp_path):
    """A LOOM_MANIFEST_PATH pointing at a non-existent file must make the
    checker fail closed (exit 2, one printed error line) — never a raw
    Python traceback leaking past main()'s bare `except Exception`, and
    never a silent fallback to the plugin manifest. `plan-edits` calls
    `load_manifest()` with no `is_file()` pre-check of its own, so this
    exercises `manifest_path_in_effect()` -> `read_text()` ->
    FileNotFoundError -> the fail-closed catch-all directly."""
    missing = tmp_path / "does-not-exist.yaml"
    result = _run(
        "plan-edits", "2026-09-05-artifact-charter-boundaries-and-edit-rights",
        env={"LOOM_MANIFEST_PATH": str(missing)},
    )
    assert result.returncode == 2, (
        f"expected exit 2 for a missing manifest override, got {result.returncode}\n"
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "Traceback" not in result.stderr and "Traceback" not in result.stdout
    assert "loom_checker internal error" in result.stderr
    assert not result.stdout.strip(), "must not have rendered any output on a fail-closed manifest read"


# ---------------------------------------------------------------------------
# 2. Hostile shape — LOOM_MANIFEST_PATH points at a directory.
# ---------------------------------------------------------------------------
def test_manifest_override_directory_fails_closed_not_traceback(tmp_path):
    """A LOOM_MANIFEST_PATH pointing at a directory (not a file) must also
    fail closed with exit 2 and no traceback — `read_text()` on a
    directory raises IsADirectoryError, and main()'s bare
    `except Exception` must catch it just like any other undecidable
    state."""
    a_dir = tmp_path / "a-directory"
    a_dir.mkdir()
    result = _run(
        "plan-edits", "2026-09-05-artifact-charter-boundaries-and-edit-rights",
        env={"LOOM_MANIFEST_PATH": str(a_dir)},
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr and "Traceback" not in result.stdout
    assert "loom_checker internal error" in result.stderr


# ---------------------------------------------------------------------------
# 3. Empty — LOOM_MANIFEST_PATH points at a zero-byte file.
# ---------------------------------------------------------------------------
def test_manifest_override_empty_file_fails_closed_not_traceback(tmp_path):
    """An empty manifest file parses via yaml.safe_load to None — the
    charter command must fail closed (never crash with an
    AttributeError leaking to a bare traceback, and never quietly render
    zero rows as if that were a legitimate empty charter)."""
    empty = tmp_path / "empty-manifest.yaml"
    empty.write_text("", encoding="utf-8")
    result = _run("charter", env={"LOOM_MANIFEST_PATH": str(empty)})
    assert result.returncode == 2
    assert "Traceback" not in result.stderr and "Traceback" not in result.stdout


# ---------------------------------------------------------------------------
# 4. Boundary — a manifest with no `artifacts:` key at all.
# ---------------------------------------------------------------------------
def test_manifest_override_no_artifacts_key_fails_closed_not_silent_fallback(tmp_path):
    """A syntactically valid YAML manifest that carries no `artifacts:`
    key must be reported as a charter-complete failure (a printed finding
    naming the missing mapping), not silently treated as `--list-rules`-
    style success and not a fallback to the plugin's real manifest."""
    scratch = tmp_path / "no-artifacts.yaml"
    scratch.write_text("stations: []\n", encoding="utf-8")
    result = _run("charter", env={"LOOM_MANIFEST_PATH": str(scratch)})
    assert result.returncode != 0, (
        "a manifest with no `artifacts:` key must not exit 0 from `charter`"
    )
    assert "no artifacts" in result.stderr.lower() or "missing" in result.stderr.lower()
    # The real plugin charter table (dozens of rows) must not have leaked in.
    real_rows = load_manifest_artifact_names()
    for name in real_rows[:3]:
        assert name not in result.stdout, (
            f"real artifact name {name!r} appeared in output for an override "
            "manifest with no artifacts — looks like a silent fallback"
        )


def load_manifest_artifact_names() -> list[str]:
    manifest = yaml.safe_load(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    return list((manifest.get("artifacts") or {}).keys())


# ---------------------------------------------------------------------------
# 5. Equivalence — override set to the REAL manifest path behaves exactly
#    like the override being unset.
# ---------------------------------------------------------------------------
def test_manifest_override_pointed_at_real_path_matches_unset_env():
    """Setting LOOM_MANIFEST_PATH to the plugin's own real manifest.yaml
    path must produce byte-identical `charter` output to leaving the
    variable unset entirely — the override is a redirect, not a second
    code path with its own behaviour."""
    env_without = dict(os.environ)
    env_without.pop("LOOM_MANIFEST_PATH", None)
    unset_result = subprocess.run(
        [sys.executable, str(CHECKER), "charter"],
        cwd=str(REPO), capture_output=True, text=True, env=env_without,
    )
    override_result = _run("charter", env={"LOOM_MANIFEST_PATH": str(PLUGIN_MANIFEST)})
    assert unset_result.returncode == override_result.returncode
    assert unset_result.stdout == override_result.stdout


# ---------------------------------------------------------------------------
# 6. Wrong order / conflicting instruction — `charter --manifest <path>`
#    disagreeing with LOOM_MANIFEST_PATH. Pin the winner.
# ---------------------------------------------------------------------------
def test_manifest_flag_wins_over_conflicting_env_override(tmp_path):
    """When `charter --manifest <path>` disagrees with LOOM_MANIFEST_PATH,
    the explicit CLI flag must win — `cmd_charter` reads the env override
    first as its default, then unconditionally reassigns `manifest_path`
    from `--manifest` when that token is present. A future refactor that
    lets the env var win silently would change which manifest a human
    invocation of `charter --manifest X` actually renders."""
    env_manifest = tmp_path / "env-manifest.yaml"
    env_manifest.write_text("artifacts: {}\n", encoding="utf-8")
    flag_manifest = tmp_path / "flag-manifest.yaml"
    flag_manifest.write_text(
        "artifacts:\n  probe_artifact:\n    charter:\n      answers: reviewer\n",
        encoding="utf-8",
    )
    result = _run(
        "charter", "--manifest", str(flag_manifest),
        env={"LOOM_MANIFEST_PATH": str(env_manifest)},
    )
    assert "probe_artifact" in result.stdout, (
        "the --manifest flag's content did not win over the conflicting "
        f"LOOM_MANIFEST_PATH env override; stdout={result.stdout!r}"
    )


# ---------------------------------------------------------------------------
# 7. Isolation — the templates/contract lookup must stay anchored to the
#    plugin's own contract dir regardless of LOOM_MANIFEST_PATH.
# ---------------------------------------------------------------------------
def test_contract_dir_stays_on_plugin_path_when_manifest_overridden(tmp_path):
    """CONTRACT_DIR (the module constant every templates/contract lookup
    resolves from) is computed once from `Path(__file__)` at import time
    and never reads LOOM_MANIFEST_PATH — so even with the override env
    var pointed at an unrelated scratch file, the checker's own
    contract/templates directory (e.g. contract/templates/review.json)
    must still resolve to the real plugin path, not vanish or redirect."""
    scratch = tmp_path / "unrelated-manifest.yaml"
    scratch.write_text("artifacts: {}\n", encoding="utf-8")
    code = (
        "import os, sys, importlib\n"
        f"os.environ['LOOM_MANIFEST_PATH'] = {str(scratch)!r}\n"
        f"sys.path.insert(0, {str(CHECKER.parent)!r})\n"
        "import loom_checker\n"
        "print(loom_checker.CONTRACT_DIR)\n"
        "print((loom_checker.CONTRACT_DIR / 'templates' / 'review.json').is_file())\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=str(REPO), capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert lines[0] == str(REPO / "loom-code" / "contract"), (
        f"CONTRACT_DIR moved under a manifest override: {lines[0]!r}"
    )
    assert lines[1] == "True", "contract/templates/review.json is unreachable from CONTRACT_DIR"


# ---------------------------------------------------------------------------
# 8. Graduated twins — every evidence/probes file promoted into
#    loom-code/scripts/ must differ from its evidence original only in an
#    allowed shape: nothing, or a path-derivation / env-threading line.
# ---------------------------------------------------------------------------
GRADUATED_PAIRS = {
    "test_abuse_charter_wave_end.py": "test_probes_charter_charter_wave_end.py",
    "test_abuse_charter.py": "test_probes_charter_charter.py",
    "test_abuse_field_caps.py": "test_probes_charter_field_caps.py",
    "test_abuse_plan_edits_after_task.py": "test_probes_charter_plan_edits_after_task.py",
    "test_abuse_plan_edits.py": "test_probes_charter_plan_edits.py",
    "test_abuse_release_1_6_0.py": "test_probes_charter_release_1_6_0.py",
    "test_abuse_review_edits.py": "test_probes_charter_review_edits.py",
    "test_abuse_wave_end_1.py": "test_probes_charter_wave_end_1.py",
    "test_abuse_wave_end_2.py": "test_probes_charter_wave_end_2.py",
}

_ALLOWED_TOKEN = re.compile(
    r"REPO_ROOT = Path\(__file__\)\.resolve\(\)\.parents\["   # path-depth line, one per location
    r"|^import os$"                                            # scratch-copy patch needs os.environ
    r"|\benv\b"                                                 # env-threading parameter/argument/kwarg
    r"|os\.environ"
    r"|cwd: Path"                                               # run_checker signature (with/without env)
    r"|manifest_path\.write_text\("                             # scratch-vs-tree manifest patch block
    r"|MANIFEST_PATH\.write_text\("
    r"|scratch = tmp_path"                                      # scratch-copy variable introduced
    r"|scratch\.write_text\("
    r"|^try:$"
    r"|^finally:$"
    r"|run_checker\("                                           # signature/call-site rewritten to thread env
    r"|run_review_edits\("
    r"|run_plan_edits\("
    r"|capture_output=True, text=True,? cwd=str\(cwd\)"
)


# A block the trunk retired from under a probe after graduation: loom-code
# 1.6.1 (#796) removed `_confirm_intent_sha` from
# test_probes_complexity_wave_end.py and its own residual-reference probe
# refuses any graduated file that still names that helper. The evidence
# original keeps the two probes that pinned it (the recorded probe commands
# select them by name; they skip, stating the retirement) and the graduated
# twin drops them. That one divergence is admitted here by stripping the
# retired block from the evidence side before the diff: from the comment
# header that opens it to the end of the file, plus the imports and the
# module-path constant only that block used.
RETIRED_BLOCKS: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    "test_abuse_charter_wave_end.py": (
        "# The W3-02 repair: `_confirm_intent_sha()` in",
        (
            "import importlib.util",
            "import shutil",
            "import tempfile",
            "import pytest",
            "from _pytest.outcomes import Skipped",
        ),
        (
            "COMPLEXITY_PROBE_MODULE = (",
            '    REPO / "loom-code" / "scripts" / "test_probes_complexity_wave_end.py"',
            ")",
        ),
    ),
}


def _strip_retired_block(original_name: str, lines: list[str]) -> list[str]:
    if original_name not in RETIRED_BLOCKS:
        return lines
    header, imports, constant = RETIRED_BLOCKS[original_name]
    try:
        start = next(i for i, line in enumerate(lines) if line.startswith(header))
    except StopIteration:
        return lines
    if start and lines[start - 1].startswith("# ----"):
        start -= 1
    kept = [line for line in lines[:start] if line not in imports]
    width = len(constant)
    for i in range(len(kept) - width + 1):
        if tuple(kept[i:i + width]) == constant:
            return kept[:i] + kept[i + width:]
    return kept


def _is_allowed_diff_line(line: str) -> bool:
    body = line[1:].strip()  # strip the leading +/- and surrounding whitespace
    return body == "" or bool(_ALLOWED_TOKEN.search(body))


def test_graduated_twins_diff_only_in_allowed_lines():
    """Every graduated probe file must differ from its evidence-original
    twin ONLY in a recognised shape: byte-identical (files that derive
    their repo root via `git rev-parse --show-toplevel` need no path
    line at all), the REPO_ROOT parents[N] depth line, or the env/os
    threading lines the scratch-manifest patch needed once promoted next
    to loom_checker.py, or a block the trunk retired after graduation
    (RETIRED_BLOCKS, stripped from the evidence side first). Any OTHER
    divergence means the promotion silently
    changed behaviour instead of only its location, and this test must
    name exactly which line broke the shape."""
    unexpected: list[str] = []
    missing_pairs: list[str] = []
    for original_name, graduated_name in GRADUATED_PAIRS.items():
        original = EVIDENCE_PROBES / original_name
        graduated = GRADUATED_DIR / graduated_name
        if not original.is_file() or not graduated.is_file():
            missing_pairs.append(f"{original_name} -> {graduated_name}")
            continue
        original_lines = _strip_retired_block(
            original_name, original.read_text(encoding="utf-8").splitlines()
        )
        graduated_lines = graduated.read_text(encoding="utf-8").splitlines()
        diff = list(difflib.unified_diff(original_lines, graduated_lines, lineterm=""))
        for line in diff:
            if line.startswith(("---", "+++", "@@")):
                continue
            if not line.startswith(("+", "-")):
                continue
            if not _is_allowed_diff_line(line):
                unexpected.append(f"{original_name}: {line}")
    assert not missing_pairs, f"graduated pairs missing from disk: {missing_pairs}"
    assert not unexpected, (
        "graduated twin diverged in a line outside the allowed shape:\n"
        + "\n".join(unexpected)
    )


# ---------------------------------------------------------------------------
# 9. Memory README index — exactly the entries present, name == filename.
# ---------------------------------------------------------------------------
_INDEX_ENTRY = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")


def test_memory_readme_index_lists_exactly_the_files_present():
    """`docs/loom/memory/README.md`'s `## Index` section must name exactly
    the `.md` files present in `docs/loom/memory/` (excluding README.md
    itself) — no listed file that is absent from disk, no file on disk
    the index never names, and every entry's link target and display
    name equal that file's own basename."""
    index_text = MEMORY_README.read_text(encoding="utf-8")
    index_section = index_text.split("## Index", 1)[1] if "## Index" in index_text else ""
    entries = [
        (name, target) for name, target in _INDEX_ENTRY.findall(index_section)
        # The index section opens with one prose line stating its own
        # `[<name>](<file>.md)` format spec -- a literal placeholder, not
        # a real entry -- which the same regex also matches.
        if "<" not in name and "<" not in target
    ]
    listed_files = {target for _, target in entries}

    actual_files = {
        p.name for p in MEMORY_DIR.glob("*.md") if p.name != "README.md"
    }

    listed_but_absent = listed_files - actual_files
    present_but_unlisted = actual_files - listed_files
    assert not listed_but_absent, f"index names files absent from disk: {sorted(listed_but_absent)[:5]}"
    assert not present_but_unlisted, (
        f"files on disk never appear in the index: {sorted(present_but_unlisted)[:5]}"
    )

    mismatched_names = [
        (name, target) for name, target in entries if name != target[:-3]
    ]
    assert not mismatched_names, (
        f"index entry display name != filename stem for: {mismatched_names[:5]}"
    )


# ---------------------------------------------------------------------------
# 10. A/B evidence — the result-table NEEDS_CONTEXT counts must equal what
#     the four saved reports actually say.
# ---------------------------------------------------------------------------
def test_ab_evidence_table_counts_match_saved_report_lines():
    """`ab-implementer-runs.md`'s result table claims NEEDS_CONTEXT counts
    2, 3, 2, 4 for runs A1/B1/A2/B2 — each of those four numbers must
    equal the `NEEDS_CONTEXT count:` line actually written in that run's
    own saved report file, not merely match what the table author typed."""
    table_path = CHANGE_DIR / "evidence" / "ab-implementer-runs.md"
    table_text = table_path.read_text(encoding="utf-8")
    row_re = re.compile(
        r"\|\s*(A1|B1|A2|B2)\s*\|[^|]*\|[^|]*\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|"
    )
    rows = row_re.findall(table_text)
    assert len(rows) == 4, f"expected 4 A/B result rows, found {len(rows)}: {rows}"

    for run_id, claimed_count, report_name in rows:
        report_path = CHANGE_DIR / "evidence" / report_name
        assert report_path.is_file(), f"{run_id}: report file {report_name} not found"
        report_text = report_path.read_text(encoding="utf-8")
        match = re.search(r"NEEDS_CONTEXT count:\s*(\d+)", report_text)
        assert match, f"{run_id}: report {report_name} carries no 'NEEDS_CONTEXT count:' line"
        actual_count = match.group(1)
        assert actual_count == claimed_count, (
            f"{run_id}: table claims NEEDS_CONTEXT count {claimed_count}, "
            f"but {report_name} says {actual_count}"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
