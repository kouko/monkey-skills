"""Adversarial probes against 2026-09-03-probes-graduate-to-permanent-tests
(branch-end, small lane).

Targets Acceptance 1 ("4 evidence probe files a字不差 with main; the
graduated copies collect and pass under the package command") and
Acceptance 2 ("no graduated def test_/class name collides with an
existing loom-code/scripts/test_*.py name") of
docs/loom/intent/2026-09-03-probes-graduate-to-permanent-tests.md.

Each case attacks a way the "copy = exactly the three permitted edits"
claim (docstring provenance sentence, `REPO_ROOT = ...parents[2]`,
`sys.path.insert(0, str(Path(__file__).parent))`) could be false without
the implementer noticing: a silent fourth edit that drifted behaviour, a
REPO_ROOT that resolves to the wrong directory, an import that resolves
to the wrong module on a shadowed sys.path, a name collision invisible
to `grep` because pytest namespaces by file, an evidence original edited
by mistake, or a hidden cwd dependency. All six ran green against HEAD;
none of them found a defect.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
GRADUATED = {
    "loom-code/scripts/test_probes_package_tests_command.py": (
        "docs/loom/2026-09-03-package-tests-run-in-parallel/"
        "evidence/probes/test_abuse_package_tests_command.py"
    ),
    "loom-code/scripts/test_probes_change_lane.py": (
        "docs/loom/2026-09-03-small-change-lane/"
        "evidence/probes/test_abuse_change_lane.py"
    ),
}

def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text()


# ---------------------------------------------------------------------------
# Case 1 -- Acceptance 1: the copy must differ from its evidence source in
# NOTHING but the three permitted edits. A fourth silent edit (a changed
# assertion, a reworded comment that also changes behaviour, a dropped
# line) would slip past a human "looks the same" skim but not a full
# unified diff compared against the exact expected hunks.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("graduated_rel,source_rel", GRADUATED.items())
def test_graduated_copy_diverges_from_source_only_by_the_three_permitted_edits(
    graduated_rel: str, source_rel: str
) -> None:
    graduated = _read(graduated_rel).splitlines()
    source = _read(source_rel).splitlines()

    # Isolate everything that differs, ignoring the permitted docstring
    # provenance line and the REPO_ROOT/sys.path pair. What remains after
    # stripping the permitted lines out of both sides must be byte-identical
    # -- any other change (a rewritten assertion, a deleted case, a renamed
    # fixture) surfaces here.
    provenance_start_re = re.compile(r"^Graduated from docs/loom/")
    provenance_end_re = re.compile(r"graduated 2026-09-04 \(W0-01\)\.$")
    repo_root_re = re.compile(r"^REPO_ROOT = ")
    sys_path_re = re.compile(r"^sys\.path\.insert\(0, ")
    comment_block_re = re.compile(
        r"^# (file: docs/loom/|parents: \[0\]=probes)"
    )

    def strip_permitted(lines: list[str]) -> list[str]:
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if provenance_start_re.match(line.strip()):
                # also drop the blank line the graduated docstring inserts
                # immediately before the provenance sentence
                if out and out[-1] == "":
                    out.pop()
                # the sentence may wrap across multiple physical lines --
                # consume through the one that ends it
                while i < len(lines) and not provenance_end_re.search(lines[i]):
                    i += 1
                i += 1  # consume the terminating line itself
                continue
            if repo_root_re.match(line) or sys_path_re.match(line) or comment_block_re.match(line):
                i += 1
                continue
            out.append(line)
            i += 1
        return out

    reduced_graduated = strip_permitted(graduated)
    reduced_source = strip_permitted(source)

    assert reduced_graduated == reduced_source, (
        f"{graduated_rel} differs from {source_rel} by more than the three "
        "permitted edits (docstring provenance, REPO_ROOT, sys.path). "
        "A silent fourth edit changed test behaviour on graduation."
    )


# ---------------------------------------------------------------------------
# Case 2 -- Acceptance 1: REPO_ROOT in each graduated copy (`parents[2]`
# from loom-code/scripts/) must resolve to a directory that actually is
# the repo root, not some other ancestor that happens to exist (e.g. if
# the file were ever moved one level deeper without updating the constant,
# parents[2] would silently point at `loom-code/` or the plugin cache).
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("graduated_rel", GRADUATED.keys())
def test_repo_root_constant_resolves_to_the_real_repo_root(graduated_rel: str) -> None:
    resolved = (REPO_ROOT / graduated_rel).resolve().parents[2]
    assert resolved == REPO_ROOT, (
        f"{graduated_rel}'s REPO_ROOT = Path(__file__).resolve().parents[2] "
        f"resolves to {resolved}, not the repo root {REPO_ROOT}."
    )
    assert (resolved / "loom-code" / "scripts" / "loom_checker.py").exists(), (
        f"{graduated_rel}'s REPO_ROOT does not contain loom_checker.py -- "
        "the package-tests-run-in-parallel probes import it via this path."
    )
    assert (resolved / "docs" / "loom" / "KICKOFF-DEFAULTS.md").exists(), (
        f"{graduated_rel}'s REPO_ROOT does not contain KICKOFF-DEFAULTS.md."
    )


# ---------------------------------------------------------------------------
# Case 3 -- Acceptance 1 (hostile-input class: mixed sys.path state). The
# repo carries a SECOND loom_checker.py at .codex/hooks/loom_checker.py
# (the Codex mirror). If anything ever prepended that directory onto
# sys.path ahead of loom-code/scripts, `import loom_checker` inside
# test_probes_change_lane.py would silently bind to the wrong, divergent
# module (confirmed divergent below) instead of erroring. This case pins
# that the graduated file's own sys.path.insert(0, ...) wins.
# ---------------------------------------------------------------------------
def test_loom_checker_import_binds_to_loom_code_scripts_not_the_codex_mirror() -> None:
    codex_mirror = REPO_ROOT / ".codex" / "hooks" / "loom_checker.py"
    real = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
    assert codex_mirror.exists(), "fixture assumption: repo ships a Codex mirror of loom_checker.py"
    assert codex_mirror.read_text() != real.read_text(), (
        "fixture assumption: the mirror has drifted from the real module "
        "(otherwise this case can't distinguish which one got imported)"
    )

    scripts_dir = REPO_ROOT / "loom-code" / "scripts"
    saved_path = list(sys.path)
    saved_modules = dict(sys.modules)
    try:
        sys.modules.pop("loom_checker", None)
        # Adversarial ordering: put the stale Codex mirror's directory on
        # sys.path BEFORE loom-code/scripts, exactly the ordering a future
        # conftest.py or plugin-loader change could introduce by accident.
        sys.path.insert(0, str(REPO_ROOT / ".codex" / "hooks"))
        sys.path.insert(0, str(scripts_dir))
        import loom_checker  # noqa: E402

        assert Path(loom_checker.__file__).resolve() == real.resolve(), (
            f"loom_checker imported from {loom_checker.__file__}, not the "
            "real loom-code/scripts/loom_checker.py -- graduated probes "
            "would silently test the wrong (stale) checker."
        )
    finally:
        sys.modules.clear()
        sys.modules.update(saved_modules)
        sys.path[:] = saved_path


# ---------------------------------------------------------------------------
# Case 4 -- Acceptance 2: no `def test_*` / `class` name in either
# graduated file collides with a name in any OTHER loom-code/scripts/
# test_*.py file. A textual grep for "no duplicate names" is not enough:
# pytest namespaces tests by file, so a same-named test in two different
# files silently coexists (both run) rather than erroring -- the
# collision this Acceptance line cares about (a maintainer editing the
# wrong one, an IDE "go to test" landing on the wrong file) would pass a
# naive `pytest --collect-only` check. This case enumerates every other
# test_*.py file directly and fails loudly on any overlap.
# ---------------------------------------------------------------------------
def test_graduated_test_and_class_names_do_not_collide_with_any_other_test_file() -> None:
    name_re = re.compile(r"^(def (test_\w+)|class (\w+))")
    scripts_dir = REPO_ROOT / "loom-code" / "scripts"
    graduated_paths = {scripts_dir / rel.split("/")[-1] for rel in GRADUATED}

    def names_in(path: Path) -> set[str]:
        found = set()
        for line in path.read_text().splitlines():
            m = name_re.match(line)
            if m:
                found.add(m.group(2) or m.group(3))
        return found

    other_names: dict[str, list[str]] = {}
    for path in sorted(scripts_dir.glob("test_*.py")):
        if path in graduated_paths:
            continue
        for name in names_in(path):
            other_names.setdefault(name, []).append(str(path.relative_to(REPO_ROOT)))

    collisions = []
    for gpath in sorted(graduated_paths):
        for name in names_in(gpath):
            if name in other_names:
                collisions.append(
                    f"{name} in {gpath.relative_to(REPO_ROOT)} also in {other_names[name]}"
                )

    assert not collisions, "graduated name collides with an existing test file:\n" + "\n".join(collisions)


# ---------------------------------------------------------------------------
# Case 5 -- Acceptance 1: "4 個 evidence 探針原檔的內容與 main 上一字不差"
# (the four evidence originals are byte-identical to origin/main). Attacks
# the possibility that graduation touched the source it copied FROM, not
# just the destination -- e.g. an editor auto-fix ran across both files.
# ---------------------------------------------------------------------------
def test_evidence_probe_originals_are_byte_identical_to_origin_main() -> None:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--stat",
            "origin/main",
            "--",
            "docs/loom/2026-09-03-package-tests-run-in-parallel/evidence/probes/",
            "docs/loom/2026-09-03-small-change-lane/evidence/probes/",
            "docs/loom/2026-09-03-loom-post-merge-seams/evidence/probes/",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "", (
        "an evidence probe original differs from origin/main:\n" + result.stdout
    )


# ---------------------------------------------------------------------------
# Case 6 -- Acceptance 1 (wrong-order / hostile-environment class): the
# package command (`python3 -m pytest loom-code/scripts/ scripts/
# .claude/hooks/ -q -n auto`) must collect and pass the graduated files
# regardless of the invoking cwd -- a maintainer running the suite from a
# CI working directory that is not the repo root, or from inside a
# subdirectory, must not silently skip or fail to import them.
# ---------------------------------------------------------------------------
def test_graduated_files_collect_and_pass_from_a_cwd_outside_the_repo(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(REPO_ROOT / "loom-code" / "scripts" / "test_probes_package_tests_command.py"),
            str(REPO_ROOT / "loom-code" / "scripts" / "test_probes_change_lane.py"),
            "-q",
        ],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        timeout=280,
    )
    assert result.returncode == 0, (
        f"graduated probes failed when invoked from cwd={tmp_path} "
        f"(outside the repo):\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "passed" in result.stdout
