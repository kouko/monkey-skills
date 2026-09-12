"""Adversary probes for the RENDERER rewrite (W1-03,
docs/loom/2026-09-06-memory-grep-single-pass/plan.md), dispatched BEFORE
W1-03 touches `render_group`, the `plain)` / `json)` arms, and any
per-record `jq` left in `memory-grep.sh`. W1-02 (the extraction/
supersession-index single pass) already landed at 1653c67d; this file
targets what a renderer rewrite specifically breaks silently: exact
whitespace layout, hostile trailer values that look like jq/shell syntax,
a value that looks like a record header, empty trailer groups, the
--top/--history/--match interaction, JSON shape, and the not-yet-written
jq-invocation-count contract.

Every case except the jq-count probe PASSES today against the
pre-W1-03 script — they pin the CURRENT byte-exact rendering the rewrite
must reproduce, per the intent's "output byte-identical to today" promise
(docs/loom/intent/2026-09-06-memory-grep-single-pass.md). One case is
marked "EXPECTED RED until W1-03 lands": it pins the not-yet-written
jq-invocation-count bound from plan.md's W1-03 Test bullet (<=6 jq calls,
constant across record count) and is left plainly red, no xfail.

This file does not duplicate
docs/loom/2026-09-06-memory-grep-single-pass/evidence/probes/test_abuse_memory_grep_single_pass.py
(case-sensitivity, path/supersession, #575, folded continuation,
subprocess *count* for git, empty-repo crash, verify pre-flight ordering)
or loom-workflow/tests/test-memory-grep-equivalence.sh (the golden-output
oracle) or test-memory-grep-perf.sh (the git-call-count + wall-clock
contract for W1-02). Every fixture here is self-contained under
tmp_path/tmp_path_factory; no case depends on today's date or on any
other probe's ordering.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

# .../docs/loom/2026-09-06-memory-grep-single-pass/evidence/probes/this_file.py
# parents[4] is the repo root from here (scripts -> git-memory -> skills -> loom-workflow -> root); the evidence original under docs/loom/.../evidence/probes/ uses parents[5]
REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "loom-workflow" / "skills" / "git-memory" / "scripts" / "memory-grep.sh"

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
    # Pins short-sha width to exactly 7 so an expected string built from a
    # `git rev-parse --short=7` capture matches the script's own `%h`.
    subprocess.run(["git", "config", "core.abbrev", "7"], cwd=path, check=True)


def _commit(path: Path, date: str, subject: str, body: bytes | None = None) -> str:
    """Create one commit at an ISO date, returning its full sha. `body`
    is raw bytes so a hostile byte sequence never round-trips through a
    shell -m argument.
    """
    env = os.environ.copy()
    env.update(ENV_IDENTITY)
    env["GIT_AUTHOR_DATE"] = f"{date}T00:00:00+0000"
    env["GIT_COMMITTER_DATE"] = f"{date}T00:00:00+0000"
    msg = subject.encode()
    if body:
        # A blank line is REQUIRED between subject and body: without it
        # git folds the "trailer" lines into the subject paragraph and
        # %s (subject) becomes the whole first paragraph space-joined —
        # this is not a hypothetical, it is how the fixture in this very
        # file was first built wrong while preparing these probes.
        msg += b"\n\n" + body
    subprocess.run(
        ["git", "commit", "-q", "--allow-empty", "-F", "-"],
        cwd=path, input=msg, env=env, check=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True, check=True,
    ).stdout.strip()


def _short(path: Path, full_sha: str) -> str:
    """The 7-char short sha git's own `%h` would print for this commit,
    captured directly via `git rev-parse` — never by running memory-grep.sh.
    """
    return subprocess.run(
        ["git", "rev-parse", "--short=7", full_sha],
        cwd=path, capture_output=True, text=True, check=True,
    ).stdout.strip()


def _run(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    cmd = ["bash", str(SCRIPT), f"--repo={repo}"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


# ─── 1. jq invocation count (EXPECTED RED until W1-03 lands) ──────────

# The two contracted sizes of the records fixture. The shape self-assertion
# in `_build_records_repo` checks the built history against THIS set, not
# against the builder's own `n_records` argument — an argument-relative
# read-back holds for any argument and so binds nothing.
RECORD_COUNTS = (20, 200)


def _build_records_repo(repo: Path, n_records: int, bulk) -> None:
    """`n_records` commits, every one memory-worthy with a single
    Decision: trailer, no supersession — the minimal shape that still
    forces the plain renderer's per-record loop (and, pre-W1-03,
    per-record jq calls) to run `n_records` times.

    Built by `bulk.build` (conftest.py's `git fast-import` wrapper, taken
    as the `bulk_history` fixture) rather than one `git commit` per
    commit: at 20 + 200 records the per-commit version cost ~7s, the
    second largest entry in this test directory's runtime. The history is
    byte-identical — every commit sha matches what `_commit` above
    produced for the same index, which is why `_commit` stays in place
    and is still used by every other fixture in this file. No commit here
    cites another's sha, so this import is a single pass.
    """
    _init_repo(repo)
    bulk.build(repo, [
        bulk.spec(
            date=f"2020-{(i // 28) % 12 + 1:02d}-{(i % 28) + 1:02d}",
            subject=f"chore: record {i} (#{i + 1})",
            body=f"Decision: decision number {i}".encode(),
        )
        for i in range(n_records)
    ])

    # Shape self-assertion. The probe below binds jq CALL COUNTS, which a
    # fixture with the wrong record shape would still satisfy, so the
    # fixture asserts its own observable shape here instead of trusting
    # the builder — see the same guard in
    # test_probes_memory_grep_single_pass.py::_build_perf_repo.
    records = bulk.read_shape(repo)
    assert len(records) in RECORD_COUNTS, (
        f"expected one of {RECORD_COUNTS} commits, got {len(records)}"
    )
    assert len(records) == n_records, f"expected {n_records} commits, got {len(records)}"
    for sha, message in records:
        decisions = [ln for ln in message.splitlines() if ln.startswith("Decision: ")]
        assert len(decisions) == 1, (
            f"expected exactly one Decision: trailer in {sha}, got {len(decisions)}"
        )
        assert "Supersedes:" not in message, f"{sha} must carry no supersession"


def _jq_call_count(repo: Path, tmp_path: Path, *args: str) -> int:
    """A PATH-prepended `jq` shim that logs exactly ONE fixed marker
    line per invocation (never the args themselves — wave-end:1-06: a
    jq FILTER PROGRAM is typically a multi-line string, so `echo "$@"
    >> log` logs several newlines per single invocation and overcounts,
    which is what forced production jq programs in memory-grep.sh onto
    single physical lines to dodge this shim's own miscounting instead
    of fixing the shim. Matches loom-workflow/tests/test-memory-grep-perf.sh's
    `make_jq_shim`, which already used the correct one-marker-per-call
    shape.
    """
    real_jq = shutil.which("jq")
    assert real_jq, "jq not found on PATH"
    shim_dir = tmp_path / f"shim-jq-{'-'.join(a.lstrip('-') for a in args) or 'plain'}"
    shim_dir.mkdir(exist_ok=True)
    log = shim_dir / "jq-calls.log"
    log.write_text("")
    shim = shim_dir / "jq"
    shim.write_text(f'#!/bin/sh\necho call >> "{log}"\nexec "{real_jq}" "$@"\n')
    shim.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{shim_dir}:{env['PATH']}"
    r = _run(repo, "--no-pr", "--since=2019-01-01", *args, env=env)
    assert r.returncode == 0
    return sum(1 for _ in log.read_text().splitlines())


def test_render_plain_and_json_jq_invocation_count_bounded_and_constant(tmp_path, bulk_history):
    """EXPECTED RED until W1-03 lands. A 20-record repo and a 200-record
    repo must each need <=6 jq invocations for `--no-pr` plain and <=6
    for `--no-pr --format=json` — AND the count must be the SAME for
    both repo sizes (plan.md W1-03 Test bullet: "a small constant number
    of jq invocations"). Today's per-record `render_group`/plain loop and
    per-record `jq -s` in the json arm both scale linearly with the
    record count, so this is red on both the bound and the constancy.
    """
    small = tmp_path / "small-repo"
    small.mkdir()
    _build_records_repo(small, RECORD_COUNTS[0], bulk_history)
    large = tmp_path / "large-repo"
    large.mkdir()
    _build_records_repo(large, RECORD_COUNTS[1], bulk_history)

    plain_small = _jq_call_count(small, tmp_path)
    plain_large = _jq_call_count(large, tmp_path)
    json_small = _jq_call_count(small, tmp_path, "--format=json")
    json_large = _jq_call_count(large, tmp_path, "--format=json")

    assert plain_small <= 6, f"expected <=6 jq calls (plain, 20 records), got {plain_small}"
    assert plain_large <= 6, f"expected <=6 jq calls (plain, 200 records), got {plain_large}"
    assert json_small <= 6, f"expected <=6 jq calls (json, 20 records), got {json_small}"
    assert json_large <= 6, f"expected <=6 jq calls (json, 200 records), got {json_large}"
    assert plain_small == plain_large, (
        f"jq call count must not grow with record count (plain): "
        f"{plain_small} @20 vs {plain_large} @200"
    )
    assert json_small == json_large, (
        f"jq call count must not grow with record count (json): "
        f"{json_small} @20 vs {json_large} @200"
    )


# ─── 2. exact byte layout of plain output, built from fixture facts ──

def test_render_plain_exact_byte_layout_matches_fixture_built_expectation(tmp_path):
    """Pins the plain renderer's exact bytes for a small, hand-computed
    fixture: the `### <sha>  <date>  <subject>` header's TWO spaces
    between fields, the `  [SUPERSEDED by ...]` suffix, `render_group`'s
    single-entry vs multi-entry ("(i/N)") layout, and the blank-line
    spacing between records and after the last one. The expected string
    is assembled here from facts the test itself controls (dates,
    subjects, and shas captured via `git rev-parse`) — it is NOT produced
    by running memory-grep.sh and diffing against itself.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)")
    sha_alpha = _commit(
        repo, "2026-01-03", "feat: alpha (#2)",
        b"Decision: alpha one\nDecision: alpha two\nRelated: rel one",
    )
    sha_retire = _commit(
        repo, "2026-01-04", "fix: supersede alpha (#3)",
        f"Gotcha: bye alpha\nSupersedes: {sha_alpha}".encode(),
    )
    short_alpha = _short(repo, sha_alpha)
    short_retire = _short(repo, sha_retire)

    r = _run(repo, "--no-pr", "--since=2020-01-01", "--history")
    assert r.returncode == 0

    expected = (
        f'# git-memory digest — repo={repo} since="2020-01-01"\n'
        "\n"
        "## Commit trailers\n"
        "\n"
        f"### {short_retire}  2026-01-04  fix: supersede alpha (#3)\n"
        "  Gotcha: bye alpha\n"
        "\n"
        f"### {short_alpha}  2026-01-03  feat: alpha (#2)  [SUPERSEDED by {short_retire} (PR #3)]\n"
        "  Decision (1/2): alpha one\n"
        "  Decision (2/2): alpha two\n"
        "  Related: rel one\n"
        "\n"
    )
    assert r.stdout == expected


# ─── 3. trailer values that look like jq/shell syntax ─────────────────

def test_render_hostile_jq_syntax_trailer_value_survives_verbatim(tmp_path):
    """A Decision: value containing `%(trailers)`, `\\(.x)`, `$__loc__`,
    `@text`, a lone backslash and a trailing backslash must appear
    VERBATIM in plain output and round-trip byte-for-byte through
    --format=json (parsed back to the identical Python string) — none of
    these are interpreted as jq template syntax, git format directives,
    or shell substitution.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)")
    hostile = 'jq syntax %(trailers) \\(.x) $__loc__ @text \\ trailing-backslash-> \\'
    _commit(repo, "2026-01-03", "feat: hostile jq syntax (#2)", ("Decision: " + hostile).encode())

    plain_run = _run(repo, "--no-pr", "--since=2020-01-01")
    assert plain_run.returncode == 0
    assert f"  Decision: {hostile}\n" in plain_run.stdout

    json_run = _run(repo, "--no-pr", "--since=2020-01-01", "--format=json")
    assert json_run.returncode == 0
    obj = json.loads(json_run.stdout)  # must not raise
    commits = [c for c in obj["commits"] if "hostile jq syntax" in c["subject"]]
    assert len(commits) == 1
    assert commits[0]["decision"] == [hostile]


# ─── 4. trailer value that looks like a record header line ───────────

def test_render_trailer_value_resembling_record_header_does_not_split_layout(tmp_path):
    """A trailer value folded onto a continuation line that itself reads
    like a `### <sha> <date> <subject>` record header must stay part of
    the ONE Learning: line it belongs to — it must never start its own
    line (which would look like a second record boundary to a line-based
    reader) and the record count (lines starting with "### " at
    column 0) must still be exactly the number of real records.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)")
    fake_header = "### deadbeef 2026-01-01 fake"
    _commit(
        repo, "2026-01-03", "feat: fake header trailer (#2)",
        f"Learning: line one\n {fake_header}".encode(),  # leading space = folded continuation
    )
    _commit(repo, "2026-01-04", "feat: second real record (#3)", b"Decision: unrelated")

    r = _run(repo, "--no-pr", "--since=2020-01-01")
    assert r.returncode == 0
    assert f"  Learning: line one {fake_header}\n" in r.stdout
    header_lines = [ln for ln in r.stdout.splitlines() if ln.startswith("### ")]
    assert len(header_lines) == 2, f"expected exactly 2 real record headers, got {header_lines}"
    assert not any(ln == fake_header for ln in header_lines)


# ─── 5. empty trailer-group keys ───────────────────────────────────────

def test_render_plain_empty_groups_omitted_json_arrays_present(tmp_path):
    """A record carrying only Learning: must render NO Decision:/
    Gotcha:/Related: group line in plain output, while --format=json
    still carries all four keys with the unused ones as empty arrays
    (today's shape — the rewrite must reproduce it, not merely "some
    reasonable shape").
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)")
    _commit(repo, "2026-01-03", "feat: learning only (#2)", b"Learning: only a learning here")

    plain_run = _run(repo, "--no-pr", "--since=2020-01-01")
    assert plain_run.returncode == 0
    assert "  Learning: only a learning here\n" in plain_run.stdout
    for absent_label in ("Decision:", "Gotcha:", "Related:"):
        assert absent_label not in plain_run.stdout

    json_run = _run(repo, "--no-pr", "--since=2020-01-01", "--format=json")
    assert json_run.returncode == 0
    obj = json.loads(json_run.stdout)
    commits = [c for c in obj["commits"] if "learning only" in c["subject"]]
    assert len(commits) == 1
    rec = commits[0]
    assert rec["learning"] == ["only a learning here"]
    assert rec["decision"] == []
    assert rec["gotcha"] == []
    assert rec["related"] == []


# ─── 6. --top + --history + --match combined ──────────────────────────

def test_render_top_history_match_combined_counts_superseded_toward_cap(tmp_path):
    """With --history, a superseded record that matches --match still
    counts toward the --top cap and its suppressed-count arithmetic —
    the same way a live record does — even when the record itself does
    not survive into the capped display window.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    widget_shas = []
    for i in range(4):
        sha = _commit(
            repo, f"2026-01-{i + 2:02d}", f"feat: widget {i} (#{i + 1})",
            f"Decision: widget decision {i}".encode(),
        )
        widget_shas.append(sha)
    _commit(
        repo, "2026-01-06", "fix: retire widget 0 (#5)",
        f"Gotcha: retiring widget 0\nSupersedes: {widget_shas[0]}".encode(),
    )
    # Unrelated commits --match must filter out.
    for i in range(2):
        _commit(repo, f"2026-01-{i + 7:02d}", f"feat: gadget {i} (#{i + 6})", f"Decision: gadget decision {i}".encode())

    r = _run(repo, "--no-pr", "--since=2020-01-01", "--match=widget", "--history", "--top=2")
    assert r.returncode == 0
    # 5 records match "widget" (widget 0-3 + the retire commit, whose
    # subject/Gotcha text both say "widget"); --top=2 keeps the newest 2
    # (retire, widget 3) and suppresses 3 — including widget 0, which is
    # superseded (hidden by default) but still counted because --history
    # is on. If superseded records were dropped from the match set before
    # the cap arithmetic, this would read "(… 2 more … )" instead of 3.
    assert r.stdout.count("### ") == 2
    assert "(… 3 more matches suppressed; raise --top or narrow --match/--path)\n" in r.stdout
    assert "gadget" not in r.stdout


# ─── 7. json top-level shape, key order, null vs string ───────────────

def test_render_json_top_level_shape_key_order_and_null_vs_string(tmp_path):
    """--format=json's top-level object has the same keys in the same
    ORDER every time (repo, since, match, path, commits_suppressed,
    commits, prs), `superseded_by` is JSON `null` for a live record and a
    non-empty string for a superseded one, and zero memory-worthy commits
    still produces a valid JSON document with `commits: []` (not absent,
    not `null`, not a parse error).
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2026-01-02", "chore: base (#1)")

    empty_run = _run(repo, "--no-pr", "--since=2020-01-01", "--format=json")
    assert empty_run.returncode == 0
    empty_obj = json.loads(empty_run.stdout)  # must not raise
    assert empty_obj["commits"] == []
    assert list(empty_obj.keys()) == [
        "repo", "since", "match", "path", "commits_suppressed", "commits", "prs",
    ]

    sha_alpha = _commit(repo, "2026-01-03", "feat: alpha (#2)", b"Decision: alpha")
    _commit(repo, "2026-01-04", "fix: retire alpha (#3)", f"Gotcha: bye\nSupersedes: {sha_alpha}".encode())

    live_run = _run(repo, "--no-pr", "--since=2020-01-01", "--format=json")
    assert live_run.returncode == 0
    live_obj = json.loads(live_run.stdout)
    assert list(live_obj.keys()) == [
        "repo", "since", "match", "path", "commits_suppressed", "commits", "prs",
    ]
    live_records = {c["subject"]: c for c in live_obj["commits"]}
    assert live_records["fix: retire alpha (#3)"]["superseded_by"] is None

    history_run = _run(repo, "--no-pr", "--since=2020-01-01", "--format=json", "--history")
    assert history_run.returncode == 0
    history_obj = json.loads(history_run.stdout)
    history_records = {c["subject"]: c for c in history_obj["commits"]}
    superseded_by = history_records["feat: alpha (#2)"]["superseded_by"]
    assert isinstance(superseded_by, str) and superseded_by, (
        f"expected a non-empty string superseded_by, got {superseded_by!r}"
    )


# ─── synthetic self-tests for the pinned-prose contract ────────────────
# No sentence of prose is pinned verbatim by these probes — every
# assertion above targets exact CLI output bytes or JSON structure the
# script itself emits (each captured from the script's actual current
# behaviour while building this file, never invented), so there is no
# separate affirmative/negated prose pair to self-test here.
