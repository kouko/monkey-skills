"""Branch-end adversarial probes (adv-be-9c4e, round 3) against the delta
`88162f4d..HEAD` of 2026-09-05-graduated-probes-independent-of-local-history.

Targets, one probe group each:

1. The new build/SKILL.md §6.5 rehearsal paragraph and the prose pin that
   guards it (`loom-code/scripts/test_build_station_text.py::
   test_graduation_paragraph_names_rehearsal_and_red_blocks_graduation`).
   Attack classes worked from `loom-code/skills/review/references/
   attack-catalogue.md`: "bypass a gate by editing its input" (rewrite the
   paragraph the pin reads) and "self-exempt via a prose condition"
   (add a get-out clause the pin cannot see). The pin is *imported*, not
   copied, so a later change to the pin is exercised by these probes too.
2. The recursion guard `REHEARSE_PROBES_NESTED` in
   `loom-code/scripts/rehearse_probes.py` and in the clone-and-run probe.
3. The 1.6.1 version stamps and the CHANGELOG entry's claims about the
   script it describes.
4. The four graduated copies against their evidence originals.
5. The `docs/loom/memory/` entries added by this delta.

Independently re-runnable from the repo root:
`python3 -m pytest docs/loom/2026-09-05-graduated-probes-independent-of-local-history/evidence/probes/test_abuse_branch_end.py -q -p no:cacheprovider`
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)
SCRIPTS = REPO / "loom-code" / "scripts"
CID = "2026-09-05-graduated-probes-independent-of-local-history"
EVIDENCE = REPO / "docs" / "loom" / CID / "evidence" / "probes"
MEMORY = REPO / "docs" / "loom" / "memory"
BASE_SHA = "88162f4d7fb7fb8365ce47fdfe513ed2f63555cc"


def _load(name: str, path: Path):
    # the shipped test modules import siblings (`prose_pin`) with no package
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, path
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# 1. the prose pin on build/SKILL.md §6.5
# ---------------------------------------------------------------------------

PIN = _load("_adv_build_station_text", SCRIPTS / "test_build_station_text.py")
PIN_CASE = PIN.test_graduation_paragraph_names_rehearsal_and_red_blocks_graduation

SKILL_TEXT = (REPO / "loom-code" / "skills" / "build" / "SKILL.md").read_text("utf-8")

GRADUATION_HEAD = "**Probe graduation.**"
STORE_HEAD = "**Store entries.**"
REHEARSAL_PARAGRAPH = (
    "`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rehearse_probes.py <test paths>`\n"
    "clones the repo the way CI checks it out — full history, `origin/main`,\n"
    "no local trunk branch — and runs the copies there (on Codex, the script\n"
    "ships with the loom-code checkout). A red rehearsal blocks graduation\n"
    "until the probe reads `origin/main` first and skips when nothing\n"
    "resolves, and reading every skip it lists matters, since a skip naming a\n"
    "commit or a branch only this tree has verifies nothing on CI.\n"
)


def _skill_with(paragraph: str) -> str:
    """Return the whole SKILL.md with the rehearsal paragraph replaced."""
    assert REHEARSAL_PARAGRAPH in SKILL_TEXT, (
        "the shipped rehearsal paragraph moved; this probe's target is stale"
    )
    return SKILL_TEXT.replace(REHEARSAL_PARAGRAPH, paragraph)


def _pin_accepts(skill_text: str, tmp_path: Path) -> bool:
    """Run the SHIPPED pin against `skill_text`. True = the pin passes it."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    target = tmp_path / "SKILL.md"
    target.write_text(skill_text, encoding="utf-8")
    original = PIN.BUILD_SKILL
    PIN.BUILD_SKILL = target
    try:
        PIN_CASE()
        return True
    except (AssertionError, IndexError):
        return False
    finally:
        PIN.BUILD_SKILL = original


# Each variant keeps the command literal the pin demands. The comment says
# what a reader of the hostile text would actually do.
HOSTILE_VARIANTS: dict[str, str] = {
    # Verb inflection: the pin only inspects sentences containing the exact
    # string "blocks graduation", so an inverting sentence that says
    # "does not block graduation" is never examined for its negation token.
    "verb-inflection-inverts-the-rule": (
        "`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rehearse_probes.py <test paths>`\n"
        "clones the repo the way CI checks it out. A red rehearsal blocks\n"
        "graduation in principle. In practice a red rehearsal does not block\n"
        "graduation when the failure comes from this tree's own history, so\n"
        "graduate the copies and move on.\n"
    ),
    # Self-exempt via a prose condition: the pinned sentence survives intact
    # and a separate sentence hands the actor the exemption.
    "prose-escape-hatch": (
        "`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rehearse_probes.py <test paths>`\n"
        "clones the repo the way CI checks it out. A red rehearsal blocks\n"
        "graduation until the probe reads `origin/main` first. Graduate anyway\n"
        "when the rehearsal is red only for reasons local to this tree, and\n"
        "skip the rehearsal entirely when the diff is one line.\n"
    ),
}

HELD_VARIANTS: dict[str, str] = {
    # The command is gone: the rehearsal becomes unrunnable prose.
    "command-dropped": (
        "Rehearse the graduated copies in a CI-shaped clone before you keep\n"
        "them. A red rehearsal blocks graduation until the probe reads\n"
        "`origin/main` first and skips when nothing resolves.\n"
    ),
    # Straight negation of the pinned claim in the pinned sentence itself.
    "pinned-sentence-negated": (
        "`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rehearse_probes.py <test paths>`\n"
        "clones the repo the way CI checks it out. A red rehearsal never\n"
        "blocks graduation; it is advisory only.\n"
    ),
    # The rule is deleted outright.
    "rule-deleted": (
        "`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rehearse_probes.py <test paths>`\n"
        "clones the repo the way CI checks it out and runs the copies there.\n"
    ),
}


def test_graduationPin_hostileRewritesThatInvertTheRule_areRefused(
    tmp_path: Path,
) -> None:
    """A rewrite of §6.5 that keeps every token the pin demands but tells the
    reader to graduate a red rehearsal must not pass the pin. Both variants
    below are edits a hurried author could plausibly make, and both leave the
    pinned literal intact."""
    survivors = [
        name
        for name, paragraph in HOSTILE_VARIANTS.items()
        if _pin_accepts(_skill_with(paragraph), tmp_path / name)
    ]
    assert survivors == [], (
        "REPRODUCED: the shipped prose pin accepts hostile rewrites of "
        "build/SKILL.md §6.5 that invert the graduation rule while keeping "
        f"every pinned literal: {survivors}"
    )


def test_graduationPin_rewritesThatDropOrNegateTheRule_areRefused(
    tmp_path: Path,
) -> None:
    """Held-record: the pin does catch the blunt evasions -- dropping the
    command, negating the pinned sentence, deleting the rule."""
    survivors = [
        name
        for name, paragraph in HELD_VARIANTS.items()
        if _pin_accepts(_skill_with(paragraph), tmp_path / name)
    ]
    assert survivors == [], (
        f"the prose pin accepted a blunt evasion it should refuse: {survivors}"
    )


def test_graduationPin_sectionEndMarkerRenamed_stillBoundsTheSearch(
    tmp_path: Path,
) -> None:
    """The pin bounds its search with `text.split("**Store entries.**")[0]`.
    Drop the trailing period from that bold run-in and the "paragraph" the pin
    reads runs to the end of the file, so the pinned sentence can live
    anywhere below §6.5 while §6.5 itself says the opposite.

    Held, but by luck rather than by design: with the end marker gone the
    sentence splitter fuses the file's tail (markdown tables carry no
    sentence-ending punctuation) into one enormous "sentence" that happens to
    contain a negation token, so the pin refuses. Nothing in the pin notices
    that its end marker vanished."""
    hostile = _skill_with(
        "`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rehearse_probes.py <test paths>`\n"
        "clones the repo the way CI checks it out. Graduate the copies\n"
        "whatever the rehearsal reports.\n"
    ).replace(STORE_HEAD, "**Store entries**")
    hostile += (
        "\n<!-- historical note -->\n"
        "A red rehearsal blocks graduation, in the 1.6.1 sense of that phrase.\n"
    )
    assert not _pin_accepts(hostile, tmp_path / "boundary"), (
        "REPRODUCED: renaming the `**Store entries.**` run-in unbounds the "
        "pin's paragraph search to the end of the file, so a sentence far "
        "below §6.5 satisfies a pin that is meant to read §6.5"
    )


# ---------------------------------------------------------------------------
# 2. the recursion guard
# ---------------------------------------------------------------------------

REHEARSE = SCRIPTS / "rehearse_probes.py"
NESTED_ENV = "REHEARSE_PROBES_NESTED"

# A probe that rehearses the very repository it lives in: without the guard
# each rehearsal spawns another one, without end.
RECURSIVE_PROBE = '''\
import os
import subprocess
import sys

import pytest

SCRIPT = {script!r}
REPO = {repo!r}


def test_marker_is_visible_and_the_nested_run_stops():
    """Inside a rehearsal the marker is set and this probe stops; outside it,
    it rehearses the same repository once."""
    if os.environ.get("REHEARSE_PROBES_NESTED"):
        pytest.skip("nested marker set; rehearsing again here would recurse")
    result = subprocess.run(
        [sys.executable, SCRIPT, "tests/test_recursive.py", "--repo", REPO],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
'''


# The same probe with the guard removed, plus its own hard depth bound so
# this negative control can never fork-bomb the machine: each level appends
# its depth to LEDGER and stops at depth 2.
UNGUARDED_PROBE = '''\
import os
import subprocess
import sys

SCRIPT = {script!r}
REPO = {repo!r}
LEDGER = {ledger!r}
DEPTH = int(os.environ.get("ADV_DEPTH", "0"))


def test_no_guard_reenters_the_rehearsal():
    """No marker check here -- only a self-imposed depth bound."""
    with open(LEDGER, "a", encoding="utf-8") as handle:
        handle.write(str(DEPTH) + "\\n")
    if DEPTH >= 2:
        return
    subprocess.run(
        [sys.executable, SCRIPT, "tests/test_recursive.py", "--repo", REPO],
        capture_output=True, text=True, timeout=120,
        env={{**os.environ, "ADV_DEPTH": str(DEPTH + 1)}},
    )
'''


def _make_repo(root: Path, body: str | None = None) -> Path:
    repo = root / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_recursive.py").write_text(
        body or RECURSIVE_PROBE.format(script=str(REHEARSE), repo=str(repo)),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.email", "adv@example.com"), ("user.name", "adv")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "tests/test_recursive.py"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "-m", "recursive probe"], check=True
    )
    return repo


def test_rehearseProbes_probeThatRehearsesItsOwnRepo_terminatesWithTheMarkerSet(
    tmp_path: Path,
) -> None:
    """Wrong-order / re-entrancy: a probe whose body invokes the rehearsal
    script on the same repository. The clone's pytest must carry the marker so
    the copy inside the clone stops instead of cloning again, and the whole
    outer run must finish well inside the tool timeout."""
    repo = _make_repo(tmp_path)
    started = time.monotonic()
    result = subprocess.run(
        [sys.executable, str(REHEARSE), "tests/test_recursive.py", "--repo", str(repo)],
        capture_output=True, text=True, timeout=240,
    )
    elapsed = time.monotonic() - started

    assert result.returncode == 0, result.stdout + result.stderr
    assert elapsed < 180, f"the guarded rehearsal took {elapsed:.0f}s"
    assert "FAILED (0)" in result.stdout, result.stdout
    # exactly one level of nesting happened, and the inner level stopped
    assert "SKIPPED (1)" in result.stdout, result.stdout
    assert "nested marker set" in result.stdout, result.stdout
    # and the marker never leaks back into this process
    assert NESTED_ENV not in os.environ


def test_rehearseProbes_probeWithoutTheGuard_reentersTheRehearsalOnceMore(
    tmp_path: Path,
) -> None:
    """Negative control for the probe above: without the marker check the same
    probe re-enters the rehearsal from inside the clone. If this control does
    not re-enter, the guarded probe's termination proves nothing.

    A self-imposed depth bound (stop at 2) keeps this from becoming the
    forty-process runaway the store entry describes."""
    ledger = tmp_path / "depths.txt"
    repo_path = tmp_path / "repo"
    repo = _make_repo(
        tmp_path,
        UNGUARDED_PROBE.format(
            script=str(REHEARSE), repo=str(repo_path), ledger=str(ledger)
        ),
    )
    result = subprocess.run(
        [sys.executable, str(REHEARSE), "tests/test_recursive.py", "--repo", str(repo)],
        capture_output=True, text=True, timeout=240,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    depths = ledger.read_text("utf-8").split()
    assert depths == ["0", "1", "2"], (
        "the unguarded probe did not re-enter the rehearsal, so the guarded "
        f"probe's termination is not evidence the guard works: {depths}"
    )


def test_rehearseProbes_keepWithTheGuard_leavesTheCloneAndNoMarkerBehind(
    tmp_path: Path,
) -> None:
    """`--keep` plus the guard: the clone stays on disk for inspection and
    nothing else leaks -- no marker in the parent environment, and the kept
    clone is a real directory the report names."""
    repo = _make_repo(tmp_path)
    result = subprocess.run(
        [
            sys.executable, str(REHEARSE),
            "tests/test_recursive.py", "--repo", str(repo), "--keep",
        ],
        capture_output=True, text=True, timeout=240,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    kept = re.search(r"kept the rehearsal clone at: (.+)$", result.stdout, re.MULTILINE)
    assert kept, result.stdout
    clone_dir = Path(kept.group(1).strip())
    assert clone_dir.is_dir(), clone_dir
    assert NESTED_ENV not in os.environ


CLONE_AND_RUN_COPY = SCRIPTS / "test_probes_rehearsal_no_history_class_skips_on_main.py"


def test_cloneAndRunProbe_markerPresetOutsideAnyRehearsal_skipsWithTheReasonNamed(
    tmp_path: Path,
) -> None:
    """False-green boundary: the guard is a bare boolean, so an environment
    that carries `REHEARSE_PROBES_NESTED` for any other reason (an exported
    shell variable, a CI job that inherits it) makes the graduated
    clone-and-run probe skip although no rehearsal is in progress. This probe
    records the observed behaviour and asserts the skip is at least loud --
    the reason must name the marker so a reader of `-rs` can see why."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", str(CLONE_AND_RUN_COPY),
            "-q", "-rs", "-p", "no:cacheprovider",
        ],
        cwd=str(REPO), capture_output=True, text=True, timeout=240,
        env={**os.environ, NESTED_ENV: "1"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 skipped" in result.stdout, result.stdout
    assert NESTED_ENV in result.stdout, (
        "the guard skipped without naming the marker in its reason: "
        + result.stdout
    )


# ---------------------------------------------------------------------------
# 3. version stamps and the CHANGELOG's claims
# ---------------------------------------------------------------------------

CHANGELOG = REPO / "loom-code" / "CHANGELOG.md"
TARGET_VERSION = "1.6.1"
PREVIOUS_VERSION = "1.5.1"


def _changelog_entry(version: str) -> str:
    text = CHANGELOG.read_text(encoding="utf-8")
    start = text.index(f"## [{version}]")
    nxt = text.index("\n## [", start + 1)
    return text[start:nxt]


def test_versionStamps_afterTheBump_allReadTheNewVersionAndNoneTheOld() -> None:
    """The six stamps the shipped enumeration checks must AGREE (its own
    assertion) and must agree ON 1.6.1 -- agreement alone would be satisfied
    by a uniform revert to 1.5.1."""
    module = _load(
        "_adv_positioning_branch_end", SCRIPTS / "test_probes_positioning_branch_end.py"
    )
    versions = module._versions()
    assert len(versions) == 6, versions
    wrong = {where: ver for where, ver in versions.items() if ver != TARGET_VERSION}
    assert wrong == {}, f"stamps not at {TARGET_VERSION}: {wrong}"
    assert PREVIOUS_VERSION not in set(versions.values())


def test_changelogEntry_forTheNewVersion_describesTheScriptThatShipped() -> None:
    """A CHANGELOG is a claim about the code. Two claims in the 1.6.1 entry
    are checked here against `rehearse_probes.py` at HEAD: which temporary
    directory API it uses, and whether it ever passes `-n auto`."""
    entry = _changelog_entry(TARGET_VERSION)
    script = REHEARSE.read_text(encoding="utf-8")
    uses_tempdir_object = "tempfile.TemporaryDirectory(" in script
    passes_xdist = '"-n"' in script or "'-n'" in script

    lies: list[str] = []
    if "tempfile.TemporaryDirectory" in entry and not uses_tempdir_object:
        lies.append(
            "the entry credits `tempfile.TemporaryDirectory`, but the script "
            "uses `tempfile.mkdtemp` and its own docstring says "
            "'Not `TemporaryDirectory`'"
        )
    if "`-n auto` added only when" in entry and not passes_xdist:
        lies.append(
            "the entry says `-n auto` is added when xdist imports, but the "
            "script's docstring says `-n auto` 'is deliberately never added' "
            "and no branch adds it"
        )
    assert lies == [], "REPRODUCED: " + "; ".join(lies)


def test_changelogEntry_deletionCount_matchesTheDeletionCommit() -> None:
    """The entry claims nine tests removed, broken down 2 / 2 / 3 / 2. Recount
    the `def test_` lines on both sides of the deletion commit."""
    entry = _changelog_entry(TARGET_VERSION)
    assert "Nine graduated probes deleted" in entry, entry[:400]
    commit = subprocess.run(
        ["git", "log", "--format=%H", "--all", "-1", "--grep",
         "delete graduated probes that can only run on their own branch history"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert commit, "the deletion commit named by the entry is not in this repository"

    removed = 0
    for name in (
        "test_probes_complexity_wave_end",
        "test_probes_language_policy",
        "test_probes_language_policy_branch_end",
        "test_probes_memory_step_wave_end",
    ):
        path = f"loom-code/scripts/{name}.py"
        before = subprocess.run(
            ["git", "show", f"{commit}^:{path}"], cwd=str(REPO),
            capture_output=True, text=True, check=True,
        ).stdout
        after = subprocess.run(
            ["git", "show", f"{commit}:{path}"], cwd=str(REPO),
            capture_output=True, text=True, check=True,
        ).stdout
        removed += len(re.findall(r"^def test_", before, re.MULTILINE)) - len(
            re.findall(r"^def test_", after, re.MULTILINE)
        )
    assert removed == 9, f"the entry claims nine tests removed; recount is {removed}"


# ---------------------------------------------------------------------------
# 4. graduated copies against their evidence originals
# ---------------------------------------------------------------------------

GRADUATED_PAIRS = {
    f"test_probes_rehearsal_{stem}.py": f"test_{stem}.py"
    for stem in (
        "abuse_rehearse_probes",
        "abuse_rehearse_probes_wave_end",
        "changelog_carries_1_6_1",
        "no_history_class_skips_on_main",
    )
}


@pytest.mark.parametrize("copy_name", sorted(GRADUATED_PAIRS))
def test_graduatedCopy_againstItsEvidenceOriginal_differsOnlyOnTheRepoRootLine(
    copy_name: str,
) -> None:
    """A graduated probe is a byte copy with its path line adjusted. Any other
    difference is a silently divergent second implementation."""
    copy_path = SCRIPTS / copy_name
    original = EVIDENCE / GRADUATED_PAIRS[copy_name]
    assert copy_path.is_file(), copy_path
    assert original.is_file(), original

    copy_lines = copy_path.read_text("utf-8").splitlines()
    orig_lines = original.read_text("utf-8").splitlines()
    assert len(copy_lines) == len(orig_lines), (
        f"{copy_name} has {len(copy_lines)} lines, its original {len(orig_lines)}"
    )
    differing = [
        (n, o, c)
        for n, (o, c) in enumerate(zip(orig_lines, copy_lines), start=1)
        if o != c
    ]
    for _, old, new in differing:
        assert "parents[" in old and "parents[" in new, (
            f"{copy_name} differs from its original outside the path line: "
            f"{old!r} -> {new!r}"
        )
        assert new.replace("parents[2]", "parents[5]") == old, (
            f"{copy_name} path line is not the expected parents[5]->parents[2] "
            f"adjustment: {old!r} -> {new!r}"
        )
    assert len(differing) <= 1, f"{copy_name} differs on {len(differing)} lines"


# ---------------------------------------------------------------------------
# 5. the memory entries this delta adds
# ---------------------------------------------------------------------------


def _new_memory_entries() -> list[Path]:
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{BASE_SHA}..HEAD", "--", "docs/loom/memory/"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout.split()
    return [
        REPO / p for p in out if p.endswith(".md") and not p.endswith("README.md")
    ]


def test_memoryEntries_addedByThisDelta_haveFrontmatterNameMatchingTheirStem() -> None:
    entries = _new_memory_entries()
    assert entries, "this delta touched no memory body files"
    wrong = []
    for path in entries:
        match = re.search(r"^name:\s*(\S+)\s*$", path.read_text("utf-8"), re.MULTILINE)
        if not match or match.group(1) != path.stem:
            wrong.append((path.name, match.group(1) if match else None))
    assert wrong == [], f"frontmatter `name` does not match the filename stem: {wrong}"


def test_memoryEntries_addedByThisDelta_areIndexedAndPassTheIntegrityCheck() -> None:
    readme = (MEMORY / "README.md").read_text("utf-8")
    missing = [p.name for p in _new_memory_entries() if p.stem not in readme]
    assert missing == [], f"not listed in docs/loom/memory/README.md: {missing}"
    result = subprocess.run(
        [sys.executable, "scripts/check_loom_memory_integrity.py", "--check"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


PATH_RE = re.compile(r"`([A-Za-z0-9_.][A-Za-z0-9_./-]*\.(?:py|md|yml|yaml|txt|json))`")


def test_memoryEntries_addedByThisDelta_citeOnlyPathsThatExistInTheTree() -> None:
    """A store entry that names a file the repository does not have sends its
    next reader nowhere. Two exclusions, both principled rather than
    convenient: a bare filename with no `/` is prose, and a line that shows a
    transformation (`a` -> `b`) is illustrating a rule with an invented
    example, not citing a file (the junit entry does exactly this with
    `loom_code.scripts.test_x`)."""
    dangling: list[tuple[str, str]] = []
    for path in _new_memory_entries():
        for line in path.read_text("utf-8").splitlines():
            if "→" in line or "->" in line:
                continue
            for cited in set(PATH_RE.findall(line)):
                if "/" not in cited or cited.startswith("<"):
                    continue
                if not (REPO / cited).exists():
                    dangling.append((path.name, cited))
    assert dangling == [], f"memory entries cite paths absent from the tree: {dangling}"


def test_memoryEntries_addedByThisDelta_haveResolvableWikilinks() -> None:
    dangling: list[tuple[str, str]] = []
    for path in _new_memory_entries():
        for link in re.findall(r"\[\[([^\]]+)\]\]", path.read_text("utf-8")):
            if not (MEMORY / f"{link}.md").is_file():
                dangling.append((path.name, link))
    assert dangling == [], f"wikilinks with no target entry: {dangling}"


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-q"]))
