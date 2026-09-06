"""Branch-end adversarial probes for 2026-09-06-memory-grep-single-pass.

Written at the branch-end checkpoint (HEAD df6f4b07), attacking what only a
whole-branch view exposes and that no probe already committed under this
directory or under loom-workflow/skills/git-memory/scripts/ covers:

1. The two probe files graduated as byte copies in af5060b8 — pin the
   RELATIONSHIP between each evidence original and its graduated copy (only
   the `parents[N]` path-climbing line and its adjacent comment may differ),
   not any fact of the moment.
2. The version-carrier set a222d110 actually touched (plugin.json, its
   codex-plugin mirror, and the root README row) versus the narrower set
   test_memory_grep_version.py pins (CHANGELOG + plugin.json + header
   text) — recomputed from the filesystem, no version number hardcoded.
3. The header's honestly-labelled minimum-git-version assumption: what
   actually happens when `%(trailers:key=...)` is unavailable, simulated
   with a `git` shim on PATH (no real old git needed, no network).
4. The memory store's own invariants after af5060b8: the two new entries
   are indexed and wikilink each other in both directions.
5. The PR-body path shares the jq stage but is out of scope for this
   change (confirmed byte-identical against main by a clean diff below) —
   probed once with a malformed `gh` shim to confirm it stays a bystander.

No network. No mutation of memory-grep.sh, any existing test, any golden,
review.json, or the blind-run report. Every fixture is self-contained
under tmp_path with fixed identity and explicit --since= bounds.
"""
from __future__ import annotations

import difflib
import json
import os
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

# .../docs/loom/2026-09-06-memory-grep-single-pass/evidence/probes/this_file.py
# parents[4] is the repo root (probes -> evidence -> <change-id> -> loom -> docs -> root)
REPO = Path(__file__).resolve().parents[5]
SCRIPT = REPO / "loom-workflow" / "skills" / "git-memory" / "scripts" / "memory-grep.sh"
LOOM_WORKFLOW_ROOT = REPO / "loom-workflow"
MEMORY_STORE = REPO / "docs" / "loom" / "memory"

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


def _commit(path: Path, date: str, subject: str, body: bytes | None = None) -> str:
    env = os.environ.copy()
    env.update(ENV_IDENTITY)
    env["GIT_AUTHOR_DATE"] = f"{date}T00:00:00+0000"
    env["GIT_COMMITTER_DATE"] = f"{date}T00:00:00+0000"
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


# ─── 1. graduated copies: pin the relationship, not the content ────

_PARENTS_LINE_RE = re.compile(r"parents\[\d+\]")


def _changed_lines(original: Path, copy: Path) -> list[str]:
    """Every line that differs between `original` and `copy`, from either
    side of the diff (added or removed), via a real diff — not a byte
    length or hash comparison, so the assertion below can inspect exactly
    which lines changed.
    """
    a = original.read_text(encoding="utf-8").splitlines()
    b = copy.read_text(encoding="utf-8").splitlines()
    changed: list[str] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b).get_opcodes():
        if tag != "equal":
            changed.extend(a[i1:i2])
            changed.extend(b[j1:j2])
    return changed


def _assert_diff_isolated_to_parents_line(original: Path, copy: Path) -> None:
    assert original.is_file(), f"missing evidence original: {original}"
    assert copy.is_file(), f"missing graduated copy: {copy}"
    changed = _changed_lines(original, copy)
    assert changed, (
        f"{original} and {copy} are byte-identical — the graduation is "
        f"supposed to differ on the repo-root path-climb, so this pins "
        f"nothing; if a future edit makes them truly identical, delete "
        f"this expectation deliberately instead of leaving it vacuous"
    )
    offenders = [line for line in changed if not _PARENTS_LINE_RE.search(line)]
    assert not offenders, (
        f"{original.name} vs {copy.name}: lines changed that do not "
        f"mention a parents[N] path-climb — the graduation is supposed "
        f"to be a byte copy apart from the repo-root path line and its "
        f"adjacent comment: {offenders!r}"
    )


def test_graduated_copy_single_pass_diff_pinned_to_parents_line() -> None:
    """af5060b8 graduated test_abuse_memory_grep_single_pass.py into
    loom-workflow/skills/git-memory/scripts/test_probes_memory_grep_single_pass.py
    as a byte copy apart from the parents[N] repo-root line. This
    recomputes the diff between the two files on disk and asserts every
    changed line mentions `parents[`, so a future edit that silently
    drifts real test logic between the two copies (not just the path
    line) goes red — without pinning the current N value, which will
    legitimately change if either file ever moves.
    """
    original = REPO / "docs/loom/2026-09-06-memory-grep-single-pass/evidence/probes/test_abuse_memory_grep_single_pass.py"
    copy = LOOM_WORKFLOW_ROOT / "skills/git-memory/scripts/test_probes_memory_grep_single_pass.py"
    _assert_diff_isolated_to_parents_line(original, copy)


def test_graduated_copy_render_diff_pinned_to_parents_line() -> None:
    """Same relationship as the single_pass pair above, for the render
    probe file af5060b8 also graduated.
    """
    original = REPO / "docs/loom/2026-09-06-memory-grep-single-pass/evidence/probes/test_abuse_memory_grep_render.py"
    copy = LOOM_WORKFLOW_ROOT / "skills/git-memory/scripts/test_probes_memory_grep_render.py"
    _assert_diff_isolated_to_parents_line(original, copy)


# ─── 2. the version-carrier set test_memory_grep_version.py does NOT pin ──

_README_ROW_RE = re.compile(
    r"\[`loom-workflow`\]\(loom-workflow/\)\s*\|\s*(?P<version>\d+\.\d+\.\d+)"
)


def _plugin_manifest_version(path: Path) -> str:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    version = manifest.get("version")
    assert version, f"{path} has no top-level \"version\" field"
    return version


def _readme_row_version() -> str:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    m = _README_ROW_RE.search(text)
    assert m, "README.md has no loom-workflow row matching the plugin-table shape"
    return m.group("version")


def test_version_carriers_full_set_agree() -> None:
    """a222d110 (W2-01) touched THREE version carriers: plugin.json, its
    .codex-plugin mirror, and the root README's loom-workflow row — but
    test_memory_grep_version.py only pins plugin.json against the
    CHANGELOG and the header text. It never reads .codex-plugin/plugin.json
    or README.md, so either one could drift from plugin.json and every
    existing test would still stay green. This recomputes all three from
    the filesystem and asserts they agree with each other, with no version
    number hardcoded here, so it survives the next bump unmodified — and
    goes red the moment codex or README stops tracking a bump like this one.
    """
    plugin_version = _plugin_manifest_version(LOOM_WORKFLOW_ROOT / ".claude-plugin" / "plugin.json")
    codex_version = _plugin_manifest_version(LOOM_WORKFLOW_ROOT / ".codex-plugin" / "plugin.json")
    readme_version = _readme_row_version()

    assert codex_version == plugin_version, (
        f".codex-plugin/plugin.json ({codex_version}) != .claude-plugin/plugin.json "
        f"({plugin_version})"
    )
    assert readme_version == plugin_version, (
        f"README.md loom-workflow row ({readme_version}) != .claude-plugin/plugin.json "
        f"({plugin_version})"
    )


# ─── 3. the honestly-assumed minimum git version: what actually happens ──

_TRAILERS_FORMAT_NEEDLE = "%(trailers:key="


def _incompatible_git_shim_dir(tmp_path: Path, mode: str) -> Path:
    """A PATH-prepended `git` shim that intercepts only the ONE `--format=`
    argument carrying `%(trailers:key=...)` (the extraction pass's
    single-git-log call) and either:
      - mode="reject": rejects it the way a git that never learned the
        `key=` filter argument does — fatal, non-zero exit, no stdout —
        without needing an actual pre-2.22 git binary; or
      - mode="literal": leaves that ONE placeholder un-expanded by
        escaping its leading `%` to `%%`, so real git prints the
        placeholder text itself as literal output — simulating a git
        that does not recognise the `%(trailers:...)` syntax at all and
        falls back to printing it verbatim instead of erroring.
    Every other git invocation (init, commit, rev-parse, config, the
    plain `--format='%h'` path-scoping call) passes straight through to
    the real git unmodified.
    """
    real_git = shutil.which("git")
    assert real_git, "git not found on PATH"
    shim_dir = tmp_path / f"shim-git-{mode}"
    shim_dir.mkdir(exist_ok=True)
    shim = shim_dir / "git"
    shim.write_text(textwrap.dedent(f"""\
        #!/usr/bin/env python3
        import sys, os
        REAL_GIT = {real_git!r}
        NEEDLE = {_TRAILERS_FORMAT_NEEDLE!r}
        MODE = {mode!r}
        args = sys.argv[1:]
        for i, a in enumerate(args):
            if a.startswith("--format=") and NEEDLE in a:
                if MODE == "reject":
                    sys.stderr.write(
                        "fatal: unknown --pretty format placeholder "
                        "%(trailers:key=...) (git-too-old shim)\\n"
                    )
                    sys.exit(128)
                else:
                    args[i] = a.replace(NEEDLE, "%%(trailers:key=")
        os.execv(REAL_GIT, [REAL_GIT] + args)
        """))
    shim.chmod(0o755)
    return shim_dir


def _memory_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _commit(repo, "2024-01-01", "do the thing", body=b"Decision: use X because Y")
    return repo


def test_extract_commits_incompatible_git_rejects_loudly(tmp_path: Path) -> None:
    """When the git on PATH rejects `%(trailers:key=...)` outright (the
    reject half of the header's assumption — an older git that never
    learned the `key=` filter), the script's own PIPESTATUS re-exit
    (memory-grep.sh:454-458) is exercised: it must exit non-zero and must
    NOT print a digest claiming zero memories, because the real failure
    was git's, not an empty repo's.
    """
    repo = _memory_repo(tmp_path)
    shim_dir = _incompatible_git_shim_dir(tmp_path, "reject")
    env = os.environ.copy()
    env["PATH"] = f"{shim_dir}:{env['PATH']}"

    result = _run(repo, "--no-pr", "--since=2019-01-01", env=env)

    assert result.returncode != 0, (
        "an older git that rejects %(trailers:key=...) must fail loudly, "
        f"got exit 0 with stdout: {result.stdout!r}"
    )
    assert "Decision" not in result.stdout, (
        "a loud failure should not also print a partial/successful-looking digest"
    )


def test_extract_commits_incompatible_git_literal_placeholder_not_silently_dropped(
    tmp_path: Path,
) -> None:
    """When the git on PATH does not error on `%(trailers:key=...)` but
    instead treats it as literal, unexpanded text (the OTHER half of the
    header's honestly-labelled assumption — plausible for a git that
    predates the `key=` filter argument but still accepts arbitrary
    `%(...)` placeholder syntax), the extraction jq stage receives that
    literal string as the fourth NUL-delimited field instead of real
    trailer lines. None of `^Decision: ` / `^Learning: ` / `^Gotcha: ` /
    `^Related: ` match literal placeholder text, so the memory-worthy
    filter (memory-grep.sh's `select((.decision|length)>0 or ...)`) drops
    the record — even though the underlying commit DOES carry a real
    `Decision:` trailer. The script exits 0 and renders "(none in
    range)": a repo with real memory silently reports having none. This
    is the worst possible failure mode named in the adversary brief, and
    it is exactly what happens today — this probe is expected to fail
    (RED) and is reported as a finding, not softened.
    """
    repo = _memory_repo(tmp_path)
    shim_dir = _incompatible_git_shim_dir(tmp_path, "literal")
    env = os.environ.copy()
    env["PATH"] = f"{shim_dir}:{env['PATH']}"

    result = _run(repo, "--no-pr", "--since=2019-01-01", env=env)

    assert result.returncode == 0, f"expected the literal-placeholder git to still exit 0, got {result.returncode}"
    assert "(none in range)" not in result.stdout, (
        "the digest silently reports zero memories while a real Decision: "
        "trailer exists in range — the tool gave no signal that its git "
        "trailer-placeholder assumption was not met"
    )
    assert "Decision: use X because Y" in result.stdout, (
        f"expected the real Decision: trailer to survive even against an "
        f"incompatible git, got stdout: {result.stdout!r}"
    )


# ─── 4. the memory store's own invariants after af5060b8 ──────────

_ENTRY_A = "a-rewrite-that-promises-byte-identical-output-needs-an-oracle-built-from-the-old-code-first"
_ENTRY_B = "two-readers-disagreeing-is-the-finding-not-a-tie-to-break"

_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def test_memory_store_new_entries_resolve_and_wikilink_each_other() -> None:
    """af5060b8 added two docs/loom/memory/ entries and regenerated the
    index. Check, from the files on disk, that: (a) both files exist,
    (b) the index (README.md) links to both by a working relative path,
    (c) each entry's own wikilink resolves to a file that actually exists
    in the store, and (d) the two entries wikilink each other — in BOTH
    directions, not just one, since a one-way pointer between two
    entries written about the same incident is itself a defect a lint
    pass would flag.
    """
    entry_a = MEMORY_STORE / f"{_ENTRY_A}.md"
    entry_b = MEMORY_STORE / f"{_ENTRY_B}.md"
    assert entry_a.is_file(), f"missing memory entry: {entry_a}"
    assert entry_b.is_file(), f"missing memory entry: {entry_b}"

    index_text = (MEMORY_STORE / "README.md").read_text(encoding="utf-8")
    assert f"[{_ENTRY_A}]({_ENTRY_A}.md)" in index_text, (
        f"README.md index does not link {_ENTRY_A}.md by its expected relative path"
    )
    assert f"[{_ENTRY_B}]({_ENTRY_B}.md)" in index_text, (
        f"README.md index does not link {_ENTRY_B}.md by its expected relative path"
    )

    def _wikilink_targets(entry: Path) -> set[str]:
        return {m.group(1).strip() for m in _WIKILINK_RE.finditer(entry.read_text(encoding="utf-8"))}

    targets_a = _wikilink_targets(entry_a)
    targets_b = _wikilink_targets(entry_b)

    assert _ENTRY_B in targets_a, f"{entry_a.name} does not wikilink {_ENTRY_B}"
    assert _ENTRY_A in targets_b, f"{entry_b.name} does not wikilink {_ENTRY_A}"

    # every wikilink target named by either new entry must resolve to a
    # real file in the store — a dangling link to a name that doesn't exist.
    for target in targets_a | targets_b:
        target_path = MEMORY_STORE / f"{target}.md"
        assert target_path.is_file(), (
            f"wikilink target [[{target}]] does not resolve to a file "
            f"under {MEMORY_STORE}"
        )


# ─── 5. the PR-body path shares the jq stage but is out of scope ──

def test_pr_extraction_malformed_gh_json_does_not_corrupt_commit_digest(tmp_path: Path) -> None:
    """The PR-body path (`gh pr list` -> jq) is explicitly out of scope
    for this change (docs/loom/intent/2026-09-06-memory-grep-single-pass.md
    Out of scope: "PR body 的那條路"), and `git diff` between this branch
    and its merge-base main confirms memory-grep.sh's PR extraction and
    render code is byte-for-byte untouched. This probe still exercises
    it once with a `gh` shim that emits truncated/malformed JSON (no
    network) to confirm the shared jq stage does not let a hostile PR
    payload corrupt or crash the commit-trailers section, which the
    single-pass rewrite DID touch. An attempt recorded as failing to
    break anything is still evidence, per the adversary contract.
    """
    repo = _memory_repo(tmp_path)
    shim_dir = tmp_path / "shim-gh"
    shim_dir.mkdir()
    gh_shim = shim_dir / "gh"
    gh_shim.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import sys
        args = sys.argv[1:]
        if args[:2] == ["auth", "status"]:
            sys.exit(0)
        if args[:2] == ["pr", "list"]:
            sys.stdout.write('[{"number": 1, "title": "broken')
            sys.exit(0)
        sys.exit(1)
        """))
    gh_shim.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{shim_dir}:{env['PATH']}"

    plain = _run(repo, "--since=2019-01-01", env=env)
    as_json = _run(repo, "--since=2019-01-01", "--format=json", env=env)

    assert plain.returncode == 0, f"plain run crashed against malformed gh JSON: {plain.stderr!r}"
    assert "Decision: use X because Y" in plain.stdout, (
        "the commit-trailers section must survive a malformed PR payload"
    )
    assert as_json.returncode == 0, f"json run crashed against malformed gh JSON: {as_json.stderr!r}"
    parsed = json.loads(as_json.stdout)
    assert parsed["commits"], "json commits array must survive a malformed PR payload"
    assert parsed["prs"] == [], "malformed PR JSON must not fabricate a PR entry"
