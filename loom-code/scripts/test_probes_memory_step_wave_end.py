"""wave-end:1 adversarial probes for
2026-09-05-memory-step-before-branch-end-and-prose-pin-rule.

Six attack classes, one attempt each, against the delta at HEAD:

1. ship §3's escape-hatch sentence -- can it still be read as authorising
   ship to make a commit other than the review-only one?
2. build §5's fenced Task:-trailer loop -- a merge commit, a docs-only
   commit without a trailer, a commit touching both docs/ and code
   without a trailer, and a trailer with trailing spaces or a lowercase
   `task:` key, all fed to the loop in a throwaway sandbox repo.
3. build §4's one-commit trailer-check command against a wrong task id.
4. the two prose-pin sentences (adversary.md, engineering-baseline.md) --
   negation token present, or affirmative verb missing.
5. the six re-targeted ship pins -- do they still assert the phrases
   they asserted on origin/main, or did the re-target silently weaken
   one (compared against `git show origin/main:...`, guarded).
6. the skip guard in the two graduated language-policy probe files -- a
   `status: closed` line appearing anywhere else in the intent (inside a
   fenced code span, not the frontmatter) must not trigger the skip.

Every case is RED only on a real defect; a survived attack is recorded
GREEN, per the adversarial recipe (`kind: adversarial` probes are a
record of what ran, not only of what broke).
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import pytest

# evidence/probes/test_abuse_memory_step_wave_end.py -> parents[2] is the
# repo root (probes -> evidence -> <change-id> -> loom -> docs -> repo root).
REPO = Path(__file__).resolve().parents[2]

SHIP_SKILL = REPO / "loom-code/skills/ship/SKILL.md"
BUILD_SKILL = REPO / "loom-code/skills/build/SKILL.md"
ADVERSARY_MD = REPO / "loom-code/agents/adversary.md"
BASELINE_MD = REPO / "loom-code/references/engineering-baseline.md"
SHIP_TEST_MD = REPO / "loom-code/scripts/test_ship_station_text.py"
LANGUAGE_POLICY_TEST = REPO / "loom-code/scripts/test_probes_language_policy.py"
LANGUAGE_POLICY_BRANCH_END_TEST = (
    REPO / "loom-code/scripts/test_probes_language_policy_branch_end.py"
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_NEGATION_RE = re.compile(r"\b(?:not|never|no)\b|n't", re.IGNORECASE)
_HEADING_RE = re.compile(r"^##\s+(.*)$", re.MULTILINE)
_FENCE_RE = re.compile(r"```(?:[a-zA-Z]*)\n(.*?)```", re.DOTALL)


def _sentences(text: str) -> list[str]:
    flat = " ".join(text.split())
    return [p for p in _SENTENCE_SPLIT.split(flat) if p.strip()]


def _headings(text: str) -> list[tuple[str, int]]:
    return [(m.group(1).strip(), m.start()) for m in _HEADING_RE.finditer(text)]


def _section_body(text: str, heading_substr: str) -> str | None:
    heads = _headings(text)
    for i, (title, offset) in enumerate(heads):
        if heading_substr.lower() in title.lower():
            end = heads[i + 1][1] if i + 1 < len(heads) else len(text)
            return text[offset:end]
    return None


def _fenced_blocks(text: str) -> list[str]:
    return [m.group(1) for m in _FENCE_RE.finditer(text)]


# --- (1) ship §3 escape hatch does not authorise a post-review commit ------


def test_shipescapehatch_readasauthorisingcommit_rejected():
    """Attack: read ship's §3 escape-hatch sentence as an agent under time
    pressure looking for a loophole that lets ship commit something other
    than the review-only commit. The sentence must say the missed
    lesson/probe is a task for build, not a commit ship makes; any
    wording that instead reads "ship may commit the fix itself" would
    let a hurried agent skip the fresh branch-end checkpoint. Held: the
    section says "never a commit made here" and routes to
    `loom-code:build`."""
    text = SHIP_SKILL.read_text(encoding="utf-8")
    section = _section_body(text, "3. Memory")
    assert section is not None
    flat = " ".join(section.split())
    assert "a task for `loom-code:build`" in flat, (
        "ship §3 no longer routes a missed lesson/probe to build as a task"
    )
    assert "never a commit made here" in flat, (
        "ship §3 dropped the sentence that forbids ship from committing "
        "the fix itself -- a hurried reading could now treat the escape "
        "hatch as authorising a ship-side commit"
    )
    # The section must not carry a second sentence that contradicts the
    # escape hatch by naming a commit ship is allowed to make outside the
    # trailer-amend / nit-batch / close-intent shapes covered elsewhere.
    assert "ship may commit" not in flat.lower()
    assert "commit it here" not in flat.lower()


# --- (2) build §5's Task:-trailer loop against tricky commit shapes --------


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _trailer_check_loop() -> str:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    sec5 = _section_body(text, "5. Wave end") or ""
    for block in _fenced_blocks(sec5):
        if "git log" in block and "Task:" in block:
            return block
    pytest.skip("build §5 has no fenced git-log/Task: loop yet")


def test_trailerlooop_mergecommit_ignored():
    """Attack: a merge commit carries no Task: trailer of its own (the
    trailer lives on the commits it merges). The loop must not report it,
    because `--no-merges` is supposed to exclude it -- if that flag were
    ever dropped, every wave-end integration merge would falsely show up
    as a missing-trailer commit."""
    command = _trailer_check_loop()
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "probe@example.com")
        _git(repo, "config", "user.name", "probe")

        (repo / "genesis.txt").write_text("genesis\n")
        _git(repo, "add", "genesis.txt")
        _git(repo, "commit", "-q", "-m", "genesis")
        reviewed_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        _git(repo, "switch", "-q", "-c", "feature")
        (repo / "feature.txt").write_text("feature\n")
        _git(repo, "add", "feature.txt")
        _git(
            repo, "commit", "-q", "-m", "feature work",
            "--trailer", "Task: W9-01",
        )
        feature_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        _git(repo, "switch", "-q", "main" if _has_branch(repo, "main") else "master")
        merge_result = subprocess.run(
            ["git", "-C", str(repo), "merge", "--no-ff", "-q", "-m", "merge feature", feature_sha],
            capture_output=True, text=True,
        )
        assert merge_result.returncode == 0, merge_result.stderr
        merge_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        substituted = command.replace("<reviewed_sha>", reviewed_sha)
        result = subprocess.run(
            ["bash", "-c", substituted], cwd=repo, capture_output=True, text=True,
        )
        assert merge_sha not in result.stdout, (
            f"the trailer loop reported the merge commit itself as missing "
            f"a Task: trailer: {result.stdout!r}"
        )
        assert feature_sha not in result.stdout, (
            f"the trailered feature commit was wrongly reported: {result.stdout!r}"
        )


def _has_branch(repo: Path, name: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", name],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def test_trailerloop_docsonlycommitnotrailer_ignored():
    """Attack: a commit touching only docs/ paths and carrying no Task:
    trailer must be ignored -- build's own text says spec/intent/plan/docs
    commits owe no Task: trailer. `grep -qv '^docs/'` on an all-docs diff
    finds no non-docs line and exits non-zero, short-circuiting the `&&`,
    so the loop should stay silent."""
    command = _trailer_check_loop()
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "probe@example.com")
        _git(repo, "config", "user.name", "probe")

        (repo / "genesis.txt").write_text("genesis\n")
        _git(repo, "add", "genesis.txt")
        _git(repo, "commit", "-q", "-m", "genesis")
        reviewed_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        (repo / "docs").mkdir()
        (repo / "docs" / "note.md").write_text("a docs note\n")
        _git(repo, "add", "docs/note.md")
        _git(repo, "commit", "-q", "-m", "docs: add a note")
        docs_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        substituted = command.replace("<reviewed_sha>", reviewed_sha)
        result = subprocess.run(
            ["bash", "-c", substituted], cwd=repo, capture_output=True, text=True,
        )
        assert docs_sha not in result.stdout, (
            f"the trailer loop reported a docs-only, trailer-less commit "
            f"as missing a Task: trailer, which build's own text says it "
            f"does not owe: {result.stdout!r}"
        )


def test_trailerloop_mixeddocsandcodecommitnotrailer_reported():
    """Attack: a commit that touches both docs/ and a non-docs path, with
    no Task: trailer, must be reported -- the docs-only exemption should
    not extend to a commit that also carries code, or a task's real work
    could be smuggled in under a docs-only-looking commit."""
    command = _trailer_check_loop()
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "probe@example.com")
        _git(repo, "config", "user.name", "probe")

        (repo / "genesis.txt").write_text("genesis\n")
        _git(repo, "add", "genesis.txt")
        _git(repo, "commit", "-q", "-m", "genesis")
        reviewed_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        (repo / "docs").mkdir()
        (repo / "docs" / "note.md").write_text("a docs note\n")
        (repo / "src.py").write_text("print('hi')\n")
        _git(repo, "add", "docs/note.md", "src.py")
        _git(repo, "commit", "-q", "-m", "mixed docs and code, no trailer")
        mixed_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        substituted = command.replace("<reviewed_sha>", reviewed_sha)
        result = subprocess.run(
            ["bash", "-c", substituted], cwd=repo, capture_output=True, text=True,
        )
        assert mixed_sha in result.stdout, (
            f"the trailer loop failed to report a commit that mixes docs/ "
            f"and code with no Task: trailer: {result.stdout!r}"
        )


def test_trailerloop_trailingspacetrailer_stillmatched():
    """Attack: a `Task: W9-02 ` trailer with a trailing space after the
    task id. `grep -q '^Task: '` only anchors the start of the line, so
    trailing whitespace after the id should not cause a false "missing
    trailer" report. Recorded either way -- this is a report-what-happens
    probe, not a pass/fail gate on design taste."""
    command = _trailer_check_loop()
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "probe@example.com")
        _git(repo, "config", "user.name", "probe")

        (repo / "genesis.txt").write_text("genesis\n")
        _git(repo, "add", "genesis.txt")
        _git(repo, "commit", "-q", "-m", "genesis")
        reviewed_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        (repo / "src.py").write_text("print('hi')\n")
        _git(repo, "add", "src.py")
        _git(
            repo, "commit", "-q", "-m", "trailing-space trailer",
            "--trailer", "Task: W9-03 ",
        )
        trailing_space_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        substituted = command.replace("<reviewed_sha>", reviewed_sha)
        result = subprocess.run(
            ["bash", "-c", substituted], cwd=repo, capture_output=True, text=True,
        )
        assert trailing_space_sha not in result.stdout, (
            f"a Task: trailer with a trailing space after the id was "
            f"wrongly reported as missing: {result.stdout!r}"
        )


def test_trailerloop_lowercasetaskkeytrailer_reportedasmissing():
    """Attack: a `task: W9-04` trailer using a lowercase key, instead of
    the `Task:` capitalisation build's own dispatch text requires. `grep
    -q '^Task: '` is case-sensitive, so this commit is reported as
    missing its trailer even though a trailer-shaped line exists.
    Recorded as a report-what-happens probe: this is not a false
    positive against build's own contract (which spells the key
    capitalised), so it is not raised as a finding -- but it is left
    here as a regression pin in case the loop's case-sensitivity is ever
    relied on differently."""
    command = _trailer_check_loop()
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "probe@example.com")
        _git(repo, "config", "user.name", "probe")

        (repo / "genesis.txt").write_text("genesis\n")
        _git(repo, "add", "genesis.txt")
        _git(repo, "commit", "-q", "-m", "genesis")
        reviewed_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        (repo / "src.py").write_text("print('hi')\n")
        _git(repo, "add", "src.py")
        _git(
            repo, "commit", "-q", "-m", "lowercase key trailer",
            "--trailer", "task: W9-04",
        )
        lowercase_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        substituted = command.replace("<reviewed_sha>", reviewed_sha)
        result = subprocess.run(
            ["bash", "-c", substituted], cwd=repo, capture_output=True, text=True,
        )
        assert lowercase_sha in result.stdout, (
            f"expected the case-sensitive grep to report the lowercase-key "
            f"trailer as missing (documenting current behaviour); got "
            f"{result.stdout!r} -- if this now passes, the loop's matching "
            f"became case-insensitive and this pin should be revisited"
        )


# --- (3) build §4's one-commit trailer-check command, wrong task id -------


def _single_commit_trailer_check() -> str:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    sec4 = _section_body(text, "4. After each task returns") or ""
    for block in _fenced_blocks(sec4):
        if "git log -1" in block and "Task:" in block and "<task-id>" in block:
            return block
    pytest.skip("build §4 has no fenced single-commit Task: check yet")


def test_singlecommitcheck_wrongtaskid_reportsmissing():
    """Attack: run build §4's one-commit trailer-check command against a
    commit that carries a Task: trailer for a DIFFERENT task id than the
    one substituted into the command (the classic off-by-one dispatch
    mistake: the implementer commits under the wrong id). The command
    must print MISSING rather than silently passing, because it greps
    for the literal task id it was given."""
    command = _single_commit_trailer_check()
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "probe@example.com")
        _git(repo, "config", "user.name", "probe")

        (repo / "src.py").write_text("print('hi')\n")
        _git(repo, "add", "src.py")
        _git(
            repo, "commit", "-q", "-m", "wrong task id",
            "--trailer", "Task: W1-99",
        )
        sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

        substituted = command.replace("<sha>", sha).replace("<task-id>", "W1-01")
        result = subprocess.run(
            ["bash", "-c", substituted], cwd=repo, capture_output=True, text=True,
        )
        assert "MISSING" in result.stdout, (
            f"build §4's single-commit check did not report MISSING for a "
            f"commit whose Task: trailer names a different task id than "
            f"the one checked for: stdout={result.stdout!r} "
            f"stderr={result.stderr!r} command={substituted!r}"
        )


# --- (4) the two prose-pin sentences, independently re-implemented --------


def _independent_pin_check(sentence: str) -> bool:
    """Deliberately independent of `_sentence_pins_prose_rule` in the
    W0-01 probe file and in test_prose_pin_rule_text.py: this checks only
    (a) the sentence names all three of "affirmative", "negation", and
    "self-test"/"synthetic", and (b) the sentence contains no negation
    token anywhere. It does NOT check verb-before-keyword ordering, so it
    is a strictly weaker, independently-written oracle -- an attack that
    slips past the shared matcher but trips this one would be a real
    finding; failing here while the shared matcher passes is not."""
    low = sentence.lower()
    names_all_three = (
        "affirmative" in low
        and ("negation" in low or "negated" in low)
        and ("self-test" in low or "synthetic" in low)
    )
    if not names_all_three:
        return False
    return not bool(_NEGATION_RE.search(sentence))


@pytest.mark.parametrize("path", [ADVERSARY_MD, BASELINE_MD], ids=lambda p: p.name)
def test_prosepinsentence_independentoracle_holds(path: Path):
    """Attack: re-verify the prose-pin sentence in each file with a
    second, independently-written oracle (see `_independent_pin_check`)
    rather than trusting the shared matcher both probe files already use
    -- a shared bug in that matcher would otherwise look like two
    passing tests instead of one undetected defect."""
    text = path.read_text(encoding="utf-8")
    hits = [s for s in _sentences(text) if _independent_pin_check(s)]
    assert hits, (
        f"{path.name}: no sentence names affirmative+negation+self-test "
        f"vocabulary with no negation token, under an oracle independent "
        f"of the shared _sentence_pins_prose_rule matcher"
    )


# --- (5) the six re-targeted ship pins, checked against origin/main -------


def test_shippins_retargeted_notweakened():
    """Attack: compare each of the six re-targeted pin assertions in
    test_ship_station_text.py against the same assertions on
    origin/main -- a re-target that changes WHICH file/section a pin
    reads from is legitimate (the memory step moved to build), but a
    re-target that also drops or loosens an assertion string is a
    silent weakening. Skips if origin/main does not resolve or the file
    did not exist there."""
    base = subprocess.run(
        ["git", "show", "origin/main:loom-code/scripts/test_ship_station_text.py"],
        cwd=REPO, capture_output=True, text=True,
    )
    if base.returncode != 0:
        pytest.skip("origin/main does not resolve, or the file is new on this branch")
    base_text = base.stdout
    head_text = SHIP_TEST_MD.read_text(encoding="utf-8")

    # Phrases the base file asserted, that must still be asserted somewhere
    # in the head file (whichever section/helper now reads them) unless the
    # phrase names something the task deliberately inverted or widened --
    # those three are checked explicitly below, by consequence rather than
    # literal string survival.
    unconditional_phrases = [
        "evidence/probes/",
        "test-function name",
        "cold-read",
        "a name collision, not a duplicate",
        "rename the probe copy rather than dropping it",
    ]
    missing = [p for p in unconditional_phrases if p in base_text and p not in head_text]
    assert not missing, (
        f"phrases asserted in origin/main's test_ship_station_text.py are "
        f"absent from HEAD's version, with no documented inversion: {missing}"
    )

    # The three deliberately-changed pins: each must still constrain
    # something, not have been deleted outright.
    assert "**Store entries.**" in head_text or "**Store entries**" in head_text, (
        "the store-entries marker this pin ordered against is gone entirely"
    )
    assert re.search(r"<=\s*\d+", head_text), (
        "the word-cap assertion (<= N) is gone entirely, not just widened"
    )
    assert (
        "re-run the `branch-end` checkpoint" in head_text
        or "this step precedes the round" in head_text
    ), (
        "neither the old re-run phrase nor its documented replacement "
        "('this step precedes the round') appears anywhere in HEAD's file"
    )


# --- (6) the language-policy skip guard vs. a status: closed line in a ----
# --- fenced code span, not the frontmatter --------------------------------


def _load_guard(path: Path):
    """Exec the probe file's module body in an isolated namespace (never
    importing it, to avoid colliding module names with the sibling file
    of the same shape) and return its `_language_policy_intent_closed`
    function."""
    namespace: dict = {"__file__": str(path), "__name__": f"_probe_loaded_{path.stem}"}
    exec(
        compile(path.read_text(encoding="utf-8"), str(path), "exec"),
        namespace,
    )
    return namespace["_language_policy_intent_closed"]


@pytest.mark.parametrize(
    "path", [LANGUAGE_POLICY_TEST, LANGUAGE_POLICY_BRANCH_END_TEST], ids=lambda p: p.name
)
def test_skipguard_statusclosedinfencedcodespan_notfrontmattertriggered(path: Path):
    """Attack: feed the skip guard a synthetic intent whose frontmatter
    `status:` line says `open` and comes FIRST, but whose body later
    includes a fenced code example containing the literal line `status:
    closed` (e.g. a worked example of what a closed intent looks like).
    Held: the guard returns on the FIRST line matching `startswith
    ("status:")` and never inspects the rest of the text, so a later
    example line inside a fenced code span cannot override the real,
    earlier frontmatter line. A companion case below shows the actual
    boundary: the guard is blind to POSITION, not to code spans as
    such -- a decoy `status: closed` line placed BEFORE the real
    frontmatter line does win, which is why the guard's safety in
    practice rests on intent files always opening with frontmatter, not
    on any code-span awareness in the guard itself."""
    if not path.is_file():
        pytest.skip(f"{path} does not exist")
    guard = _load_guard(path)

    real_status_second = (
        "status: open\n"
        "\n"
        "## Worked example\n"
        "A closed intent's frontmatter looks like this:\n"
        "\n"
        "```\n"
        "status: closed 2026-01-01 -- PR #1\n"
        "```\n"
    )
    assert guard(real_status_second) is False, (
        "expected the guard to decide False from the first (frontmatter) "
        "status: line and ignore the later fenced-code-span line; a True "
        "here would mean the code-span line won even though the real "
        "frontmatter line came first -- that would be a genuine finding"
    )

    decoy_status_first = (
        "```\n"
        "status: closed 2026-01-01 -- PR #1\n"
        "```\n"
        "\n"
        "status: open\n"
    )
    assert guard(decoy_status_first) is True, (
        "documents the actual boundary: the guard has no concept of a "
        "fenced code span, so whichever status:-prefixed line comes "
        "FIRST in the text wins, decoy or not -- real intent files are "
        "safe from this only because their frontmatter is always first"
    )


def test_skipguard_realintentfile_currentlyclosed():
    """Sanity probe (not an attack): the guard's real target file,
    2026-09-03-artifact-language-policy.md, is `status: closed` as of
    this branch, so both graduated probe files should currently be
    skipping their branch-scope assertions. Confirms the guard's
    happy-path still fires on the real artifact, independent of the
    synthetic case above."""
    real_intent = REPO / "docs/loom/intent/2026-09-03-artifact-language-policy.md"
    if not real_intent.is_file():
        pytest.skip("the language-policy intent file does not exist in this tree")
    guard = _load_guard(LANGUAGE_POLICY_TEST)
    text = real_intent.read_text(encoding="utf-8")
    assert guard(text) is True, (
        "the real language-policy intent is expected to read status: "
        "closed on this branch; if it does not, the two graduated probe "
        "files are running their branch-scope assertions unexpectedly"
    )


if __name__ == "__main__":  # pragma: no cover
    import sys
    sys.exit(pytest.main([__file__, "-q"]))
