"""Adversary-first probes for 2026-09-06-memory-grep-single-pass, written
BEFORE W1-02/W1-03 (docs/loom/2026-09-06-memory-grep-single-pass/plan.md)
touch memory-grep.sh. Every case builds its own fixture repo under
tmp_path with subprocess + git, using fixed author/committer identity and
explicit --since= bounds so nothing depends on today's date.

Most cases here PASS today: they pin behaviour of the current
(three-loop, ~3,000-subprocess) script that the rewrite must reproduce
byte-for-byte per the intent's "output and exit codes byte-identical to
today" promise (docs/loom/intent/2026-09-06-memory-grep-single-pass.md).
Two cases are marked "EXPECTED RED until W1-02/W1-03 lands" — they pin
the not-yet-written subprocess-count and wall-clock speed contract from
plan.md's W1-02/W1-03 Risk bullets; they are left plainly red (no
xfail), and the implementer's job is to turn them green without
disturbing the byte-identical cases above.

None of these duplicate loom-workflow/tests/test-memory-grep-*.sh or
test-memory-grep-equivalence.sh — this file is a separate adversarial
attack surface (case sensitivity, path/supersession interaction, hostile
byte sequences, empty states, exact suppression/verify wording,
pre-flight ordering, and the speed contract itself), not a re-run of the
existing suites.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

# .../docs/loom/2026-09-06-memory-grep-single-pass/evidence/probes/this_file.py
# parents[4] is the repo root from here (scripts -> git-memory -> skills -> loom-workflow -> root); the evidence original under docs/loom/.../evidence/probes/ uses parents[5]
REPO = Path(__file__).resolve().parents[4]
SCRIPT = REPO / "loom-workflow" / "skills" / "git-memory" / "scripts" / "memory-grep.sh"

assert SCRIPT.is_file(), f"expected memory-grep.sh at {SCRIPT}"

ENV_IDENTITY = {
    "GIT_AUTHOR_NAME": "Fixture Bot",
    "GIT_AUTHOR_EMAIL": "fixture@example.com",
    "GIT_COMMITTER_NAME": "Fixture Bot",
    "GIT_COMMITTER_EMAIL": "fixture@example.com",
}


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "symbolic-ref", "HEAD", "refs/heads/main"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Fixture Bot"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=path, check=True)
    subprocess.run(["git", "config", "core.abbrev", "7"], cwd=path, check=True)


def _commit(
    path: Path,
    date: str,
    subject: str,
    body: bytes | None = None,
    files: dict[str, str] | None = None,
) -> str:
    """Create one commit at an ISO date (YYYY-MM-DD), returning its full sha.

    `subject` is str (ASCII-safe control text); `body` is raw bytes so a
    probe can embed hostile byte sequences the shell would mangle if it
    went through -m/-m string args.
    """
    env = os.environ.copy()
    env.update(ENV_IDENTITY)
    env["GIT_AUTHOR_DATE"] = f"{date}T00:00:00+0000"
    env["GIT_COMMITTER_DATE"] = f"{date}T00:00:00+0000"
    if files:
        for fname, content in files.items():
            fpath = path / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content)
            subprocess.run(["git", "add", fname], cwd=path, check=True)
    msg = subject.encode()
    if body:
        msg += b"\n\n" + body
    subprocess.run(
        ["git", "commit", "-q", "--allow-empty", "-F", "-"],
        cwd=path, input=msg, env=env, check=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True, check=True,
    ).stdout.strip()


def _run(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    cmd = ["bash", str(SCRIPT), f"--repo={repo}"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


# ─── 1. case-sensitivity ────────────────────────────────────────────

def test_extract_commits_mixed_case_trailer_key_excluded(tmp_path):
    """A `DECISION:` (all-caps) and a `decision:` (lowercase) trailer key
    must both stay excluded from output; only the exact-case `Decision:`
    is picked up. `%(trailers:key=)` in the rewrite matches keys
    case-insensitively, so this pins the exclusion the jq re-filter
    (plan.md W1-02 Risk 4) must reproduce.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)")
    _commit(repo, "2026-01-03", "feat: upper case key (#2)", b"DECISION: should not match uppercase")
    _commit(repo, "2026-01-04", "feat: lower case key (#3)", b"decision: should not match lowercase")
    _commit(repo, "2026-01-05", "feat: proper case key (#4)", b"Decision: should match proper case")

    r = _run(repo, "--no-pr", "--since=2020-01-01")
    assert r.returncode == 0
    assert "should not match uppercase" not in r.stdout
    assert "should not match lowercase" not in r.stdout
    assert "should match proper case" in r.stdout
    assert r.stdout.count("### ") == 1


# ─── 2. --path scoping + out-of-path Supersedes ────────────────────

def test_extract_commits_path_scope_external_supersession_retires_record(tmp_path):
    """A `Supersedes:` commit that touches a file OUTSIDE the pathspec
    must still retire a shown record INSIDE it (plan.md :372-374); the
    superseded record is hidden by default and shown with --history.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)", files={"src/target.txt": "base\n"})
    _commit(
        repo, "2026-01-03", "feat: target decision in src (#2)",
        b"Decision: decision inside src path", files={"src/target.txt": "v2\n"},
    )
    target_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    _commit(
        repo, "2026-01-04", "fix: supersede from outside src (#3)",
        f"Gotcha: retiring the src decision\nSupersedes: {target_sha}".encode(),
        files={"outside.txt": "changed\n"},
    )

    default_run = _run(repo, "--no-pr", "--since=2020-01-01", "--path=src")
    assert default_run.returncode == 0
    assert '(no memory touched "src")' in default_run.stdout
    assert "decision inside src path" not in default_run.stdout

    history_run = _run(repo, "--no-pr", "--since=2020-01-01", "--path=src", "--history")
    assert history_run.returncode == 0
    assert "decision inside src path" in history_run.stdout
    assert "[SUPERSEDED by" in history_run.stdout


# ─── 3. hostile separator bytes in a trailer value ─────────────────

def test_extract_commits_hostile_separator_value_stays_structurally_valid(tmp_path):
    """wave-end:1-03: a trailer value containing the script's own
    internal separators (`\\x1F`, `\\x1E`), a literal tab, the literal
    text "%x1F", and a double quote + backslash must not corrupt the
    record: --format=json must stay parseable and the raw value must
    survive VERBATIM (exact equality, not a substring check — deleting
    both separator bytes would have still passed the old substring-only
    assertions), and plain output must render the value byte-for-byte
    too. This is a structural invariant (not a byte-for-byte pin
    against the pre-change script) because the pre-change script's own
    behaviour on this input IS the baseline being pinned — the
    subject-side counterpart of this same encoding is pinned against
    the pre-change script directly by
    test_extract_commits_subject_with_hostile_separator_byte_round_trips
    above.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)")
    hostile_val = (
        "bad seps " + chr(0x1F) + chr(0x1E) + '\t %x1F literal "quoted\\backslash"'
    )
    _commit(
        repo, "2026-01-03", "feat: hostile separator trailer (#2)",
        ("Decision: " + hostile_val).encode(),
    )

    plain_run = _run(repo, "--no-pr", "--since=2020-01-01")
    assert plain_run.returncode == 0
    assert ("  Decision: " + hostile_val + "\n") in plain_run.stdout

    json_run = _run(repo, "--no-pr", "--since=2020-01-01", "--format=json")
    assert json_run.returncode == 0
    obj = json.loads(json_run.stdout)  # must not raise
    commits = [c for c in obj["commits"] if "hostile separator" in c["subject"]]
    assert len(commits) == 1
    assert commits[0]["decision"] == [hostile_val]


def test_extract_commits_subject_with_hostile_separator_byte_round_trips(tmp_path):
    """wave-end:1-01: a commit SUBJECT containing a raw 0x1F byte must
    round-trip exactly as the PRE-CHANGE script rendered it — the
    single-pass rewrite's field encoding must be injective for every
    non-NUL byte, not just trailer values. The pre-change script (a
    committed byte copy of the version at 4e45d6de, the last pre-rewrite
    commit — a fixture file rather than a `git show <sha>` lookup, so the
    oracle works in a depth-1 CI checkout that carries no history) is
    run against the identical fixture and its output is the expectation,
    not an invented string.
    Before the wave-end:1-01 fix, the new script silently dropped this
    record (printed "(none in range)", exit 0) because its `%x1F`
    field-separator encoding mis-split on the embedded 0x1F byte.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    hostile_subject = "feat: subject with " + chr(0x1F) + " inside (#1)"
    _commit(repo, "2026-01-03", hostile_subject, b"Decision: hostile subject decision")

    old_script = SCRIPT.parent / "fixture_memory_grep_pre_change.sh"
    assert old_script.is_file(), f"expected pre-change fixture at {old_script}"

    old_run = subprocess.run(
        ["bash", str(old_script), f"--repo={repo}", "--no-pr", "--since=2020-01-01"],
        capture_output=True, text=True,
    )
    new_run = _run(repo, "--no-pr", "--since=2020-01-01")

    assert old_run.returncode == 0
    assert new_run.returncode == old_run.returncode
    assert new_run.stdout == old_run.stdout
    assert "hostile subject decision" in new_run.stdout


# ─── 4. trailer block followed by a non-trailer line (#575) ───────

def test_extract_commits_trailer_followed_by_stray_line_excluded(tmp_path):
    """A commit whose apparent trailer block is followed by a
    non-trailer line parses to nothing under `git interpret-trailers
    --parse` (the #575 case, :123-128 of memory-grep-fixture.sh already
    covers this via the golden oracle; this is an independent,
    self-contained repro so it survives even if that fixture changes).
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)")
    _commit(
        repo, "2026-01-03", "fix: weird trailer parse (#2)",
        b"Decision: this looks like a trailer\nbut a non-trailer line follows immediately",
    )

    r = _run(repo, "--no-pr", "--since=2020-01-01")
    assert r.returncode == 0
    assert "this looks like a trailer" not in r.stdout
    assert "(none in range)" in r.stdout


# ─── 5. folded continuation line, --unfold semantics ───────────────

def test_extract_commits_folded_continuation_joined_single_space(tmp_path):
    """A folded continuation line (an indented line right after a
    trailer line) is joined into the trailer's value with exactly one
    space by `git interpret-trailers --parse --unfold` — pin the exact
    rendered text.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)")
    _commit(
        repo, "2026-01-03", "feat: folded continuation (#2)",
        b"Decision: folded value here\n continuation appended",
    )

    r = _run(repo, "--no-pr", "--since=2020-01-01")
    assert r.returncode == 0
    assert "  Decision: folded value here continuation appended\n" in r.stdout


# ─── 6. subprocess count contract (EXPECTED RED today) ─────────────

# The perf fixture's contracted shape. These are the numbers the probes
# below were written against, so the shape self-assertion in
# `_build_perf_repo` compares the built history against THESE rather than
# against the builder's own arguments — an argument-relative assertion holds
# for every argument and therefore binds nothing. `perf_repo` passes them
# explicitly and the builder takes no defaults, so a caller that perturbs
# the shape fails the read-back instead of silently building something else.
PERF_COMMITS = 200
PERF_MEMORY_WORTHY = 40
PERF_SUPERSEDED = 5


def _build_perf_repo(repo: Path, bulk, n_commits: int, memory_count: int) -> None:
    """200 commits, 40 memory-worthy (Decision:), 5 of those also carry
    Supersedes: pointing at an earlier memory commit. Every commit
    touches the same tracked file so a --path pathspec matches all of
    them (exercising the path-scoped git-call count too).

    Built by `bulk.build` (conftest.py's `git fast-import` wrapper, taken
    as the `bulk_history` fixture) rather than one `git commit` per
    commit: the per-commit version cost ~9s, which was a third of this
    whole test directory's runtime. The history it produces is
    byte-identical — every commit sha matches what `_commit` above
    produced for the same index, which is why `_commit` is left in place
    and still used by every small fixture in this file.

    The supersession targets are what forces fast-import into more than
    one pass: commit 38 cites commit 36's sha and commit 39 cites 38's,
    and a sha only exists once written, so the stream is cut into waves
    (see conftest.py). `2 * i - memory_count` reproduces the original
    negative-index arithmetic — commits 35..39 supersede 30, 32, 34, 36,
    38 respectively.
    """
    _init_repo(repo)

    def _superseding_body(i: int):
        return lambda sha: f"Gotcha: superseding decision {i}\nSupersedes: {sha}".encode()

    specs = []
    for i in range(n_commits):
        date = f"2020-{(i // 28) % 12 + 1:02d}-{(i % 28) + 1:02d}"
        common = {
            "date": date,
            "subject": f"chore: commit {i} (#{i + 100})",
            "files": {"content.txt": f"content at commit {i}\n"},
        }
        if i >= memory_count:
            specs.append(bulk.spec(**common))
        elif i >= memory_count - 5:
            specs.append(bulk.spec(
                **common,
                supersedes_index=2 * i - memory_count,
                body_from_sha=_superseding_body(i),
            ))
        else:
            specs.append(bulk.spec(
                **common,
                body=f"Decision: memory decision number {i}".encode(),
            ))
    bulk.build(repo, specs)

    # Shape self-assertion. The probes below bind git-call COUNTS, which a
    # fixture with the wrong record shape would still satisfy — verified:
    # dropping memory_count to 39 left both of them green. So the fixture
    # asserts its own observable shape here against the PERF_* literals
    # above, and a rewrite (or a caller) that quietly stopped producing
    # 200/40/5 fails loudly at build time.
    records = bulk.read_shape(repo)
    shas_so_far: set[str] = set()
    memory_worthy = superseded = 0
    for sha, message in records:
        if "Decision:" in message or "Gotcha:" in message:
            memory_worthy += 1
        for line in message.splitlines():
            if line.startswith("Supersedes: "):
                superseded += 1
                target = line.removeprefix("Supersedes: ").strip()
                assert target in shas_so_far, (
                    f"Supersedes: in {sha} cites {target}, which is not an earlier commit"
                )
        shas_so_far.add(sha)
    assert len(records) == PERF_COMMITS, (
        f"expected {PERF_COMMITS} commits, got {len(records)}"
    )
    assert memory_worthy == PERF_MEMORY_WORTHY, (
        f"expected {PERF_MEMORY_WORTHY} memory-worthy commits, got {memory_worthy}"
    )
    assert superseded == PERF_SUPERSEDED, (
        f"expected {PERF_SUPERSEDED} Supersedes: commits, got {superseded}"
    )
    touching = subprocess.run(
        ["git", "-C", str(repo), "log", "--format=%H", "--", "content.txt"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    assert len(touching) == PERF_COMMITS, (
        f"expected all {PERF_COMMITS} commits to touch content.txt, got {len(touching)}"
    )


def _count_shim_dir(tmp_path: Path, tool: str, log_path: Path) -> Path:
    """A PATH-prepended directory containing one shim for `tool` that
    appends its args to `log_path` (one line per invocation) then execs
    the real binary.
    """
    real = shutil.which(tool)
    assert real, f"{tool} not found on PATH"
    shim_dir = tmp_path / f"shim-{tool}"
    shim_dir.mkdir(exist_ok=True)
    shim = shim_dir / tool
    shim.write_text(f'#!/bin/sh\necho "$@" >> "{log_path}"\nexec "{real}" "$@"\n')
    shim.chmod(0o755)
    return shim_dir


@pytest.fixture(scope="module")
def perf_repo(tmp_path_factory, bulk_history):
    repo = tmp_path_factory.mktemp("perf-repo") / "repo"
    repo.mkdir()
    _build_perf_repo(repo, bulk_history, PERF_COMMITS, PERF_MEMORY_WORTHY)
    return repo


def test_extract_commits_subprocess_count_bounded(perf_repo, tmp_path):
    """EXPECTED RED until W1-02 lands. A 200-commit repo (40
    memory-worthy, 5 with Supersedes:) must produce a SMALL CONSTANT
    number of `git` invocations for `--no-pr` (plan.md W1-02 Risk: <=4)
    and for `--no-pr --path=<file>` (<=6) — today's per-commit loops
    spawn on the order of a thousand. This is the deterministic half of
    the speed contract (the wall-clock probe below is the secondary,
    load-sensitive half).
    """
    log = tmp_path / "git-calls.log"
    log.write_text("")
    shim_dir = _count_shim_dir(tmp_path, "git", log)
    env = os.environ.copy()
    env["PATH"] = f"{shim_dir}:{env['PATH']}"

    r1 = _run(perf_repo, "--no-pr", "--since=2019-01-01", env=env)
    assert r1.returncode == 0
    count_no_path = sum(1 for _ in log.read_text().splitlines())

    log.write_text("")
    r2 = _run(perf_repo, "--no-pr", "--since=2019-01-01", "--path=content.txt", env=env)
    assert r2.returncode == 0
    count_path = sum(1 for _ in log.read_text().splitlines())

    assert count_no_path <= 4, f"expected <=4 git invocations, got {count_no_path}"
    assert count_path <= 6, f"expected <=6 git invocations with --path, got {count_path}"


def test_extract_commits_wall_clock_bounded(perf_repo):
    """EXPECTED RED until W1-02/W1-03 land. The 200-commit repo's
    `--no-pr` run must complete within 3 seconds wall-clock (plan.md
    Acceptance 1's spirit, loosened here because this is a subprocess
    contention environment, not the CI runner the plan bounds at 2s on
    a 2,000-commit repo). Today this takes on the order of ten seconds.
    The subprocess-count probe above is the deterministic assertion; a
    red run here on an otherwise-passing count probe should be read as
    machine load, per plan.md Risk 1.
    """
    start = time.monotonic()
    r = _run(perf_repo, "--no-pr", "--since=2019-01-01")
    elapsed = time.monotonic() - start
    assert r.returncode == 0
    assert elapsed <= 3.0, f"expected <=3s wall-clock, took {elapsed:.2f}s"


# ─── 8. empty repo / zero memory-worthy commits / no matches ───────

def test_render_plain_brand_new_repo_crashes_with_undocumented_exit(tmp_path):
    """A brand-new repo with ZERO commits ever crashes today with exit
    128 and a raw git fatal message ("your current branch 'main' does
    not have any commits yet") instead of one of the five documented
    exit codes (0/1/2/3/4, script header :38-56). This pins TODAY's
    behaviour (the intent requires byte-identical exit codes across the
    rewrite) and is also reported as a finding: it is a real, reachable
    state (git-memory run against a freshly `git init`-ed repo before
    the first commit) that the script's own contract does not document.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    r = _run(repo, "--no-pr", "--since=2020-01-01")
    assert r.returncode == 128
    assert "does not have any commits yet" in r.stderr


def test_render_plain_zero_memory_commits_shows_none_in_range(tmp_path):
    """Commits exist but none carry a memory trailer (or the only one
    that does is dated before --since) -> exact line "(none in range)".
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2019-01-01", "feat: memory outside window (#1)", b"Decision: too old to show")
    _commit(repo, "2026-01-02", "chore: no memory here (#2)")

    r = _run(repo, "--no-pr", "--since=2020-01-01")
    assert r.returncode == 0
    assert "(none in range)\n" in r.stdout
    assert "too old to show" not in r.stdout


def test_render_plain_match_no_hit_shows_no_memory_matches_line(tmp_path):
    """--match with zero hits prints the exact line
    '(no memory matches "<term>")'.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "feat: something (#1)", b"Decision: unrelated topic")

    r = _run(repo, "--no-pr", "--since=2020-01-01", "--match=zzz")
    assert r.returncode == 0
    assert '(no memory matches "zzz")\n' in r.stdout


def test_render_plain_path_no_hit_shows_no_memory_touched_line(tmp_path):
    """--path with zero hits prints the exact line
    '(no memory touched "<pathspec>")'.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "feat: something (#1)", b"Decision: unrelated topic")

    r = _run(repo, "--no-pr", "--since=2020-01-01", "--path=zzz")
    assert r.returncode == 0
    assert '(no memory touched "zzz")\n' in r.stdout


# ─── 9. --top suppression line, exact text ─────────────────────────

def test_render_plain_top_cap_shows_exact_suppression_line(tmp_path):
    """--top caps displayed commits and prints the exact suppression
    line '(… N more matches suppressed; raise --top or narrow
    --match/--path)' with the correctly-computed N.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    for i in range(5):
        _commit(repo, f"2026-01-{i + 2:02d}", f"feat: decision {i} (#{i + 1})", f"Decision: decision number {i}".encode())

    r = _run(repo, "--no-pr", "--since=2020-01-01", "--top=2")
    assert r.returncode == 0
    assert r.stdout.count("### ") == 2
    assert "(… 3 more matches suppressed; raise --top or narrow --match/--path)\n" in r.stdout


# ─── 10. exit codes and pre-flight ordering ─────────────────────────

def test_verify_mode_non_memory_commit_exits_four(tmp_path):
    """--verify on a commit with no Decision:/Learning:/Gotcha: trailer
    exits 4.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: no memory here (#1)")
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()

    r = _run(repo, "--verify", sha)
    assert r.returncode == 4
    assert "No memory trailer found" in r.stderr


def test_verify_mode_unresolvable_ref_exits_two(tmp_path):
    """--verify with a ref that does not resolve to a commit exits 2."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)")

    r = _run(repo, "--verify", "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
    assert r.returncode == 2
    assert "Unresolvable ref" in r.stderr


def _shim_path_without_jq(tmp_path: Path) -> str:
    """Build a minimal PATH that has every tool memory-grep.sh needs
    EXCEPT jq (symlinked from wherever they really live), so `command -v
    jq` genuinely fails without also breaking git/grep/sed/awk/etc. by
    naively filtering PATH entries (a directory holding jq typically
    also holds several of those).
    """
    shim_dir = tmp_path / "shim-no-jq"
    shim_dir.mkdir(exist_ok=True)
    for tool in ("git", "grep", "sed", "awk", "tr", "wc", "cat", "head", "printf", "bash", "sh"):
        real = shutil.which(tool)
        if real and not (shim_dir / tool).exists():
            (shim_dir / tool).symlink_to(real)
    return str(shim_dir)


def test_preflight_git_repo_check_precedes_jq_check(tmp_path):
    """Pre-flight ordering: with jq entirely absent from PATH, a
    NOT-a-git-repo target still exits 2 (the git-repo check at
    memory-grep.sh:344-347 runs BEFORE the jq-required check at :351),
    while a VALID repo with jq absent exits 3. A rewrite that reorders
    these checks (e.g. checking jq first, "for speed") would flip the
    exit code on the first case.
    """
    not_a_repo = tmp_path / "not-a-repo"
    not_a_repo.mkdir()
    valid_repo = tmp_path / "valid-repo"
    valid_repo.mkdir()
    _init_repo(valid_repo)

    env = os.environ.copy()
    env["PATH"] = _shim_path_without_jq(tmp_path)

    r1 = _run(not_a_repo, "--no-pr", "--since=2020-01-01", env=env)
    assert r1.returncode == 2
    assert "Not a git repository" in r1.stderr

    r2 = _run(valid_repo, "--no-pr", "--since=2020-01-01", env=env)
    assert r2.returncode == 3
    assert "requires jq" in r2.stderr


# ─── synthetic self-tests for the pinned-prose contract ────────────
# (No prose sentence is pinned verbatim in this file's own assertions
# beyond exact CLI output strings the script itself emits, so there is
# no separate affirmative/negated pair to self-test here; the exact-text
# assertions above (empty-state lines, suppression line, exit-code
# stderr substrings) are themselves the affirmative pins, each checked
# against the script's actual current output captured earlier in this
# session, not invented.)
