"""Executable contract for `loom_checker.py intent` (plan W0-03).

The load-bearing case is `intent.needs-design-recompute`: an agent that
writes `needs-design: no` while its diff touches a declared interface
surface must be blocked by the RECOMPUTED diff, not believed. Every
fixture here is a real git repo under tmp_path for that reason.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).with_name("loom_checker.py")
REPO_ROOT = Path(__file__).resolve().parents[2]

INTENT_BODY = """
## Problem
{problem}

## Proposed outcome
Make the thing better for the people who use it.

## Acceptance
1. After this I can run the thing and see the result.

## Constraints
- Stay inside the existing tool.

## Out of scope
- Everything else.

## Open questions
- None yet.
"""


def write_intent(
    path: Path,
    *,
    kind: str = "engineering",
    needs_design: str = "no — nothing user-visible changes",
    status: str = "status: open",
    problem: str = "The thing is slow and the people who use it wait too long.",
    originator: str = "originator: tester",
    drop: tuple[str, ...] = (),
) -> Path:
    lines = ["# A change", originator, f"kind: {kind}"]
    if "needs-design" not in drop:
        lines.append(f"needs-design: {needs_design}")
    if status:
        lines.append(status)
    text = "\n".join(line for line in lines if line) + "\n"
    text += INTENT_BODY.format(problem=problem)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def drop_section(path: Path, heading: str) -> None:
    kept, skipping = [], False
    for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("## "):
            skipping = line.strip() == heading
        if not skipping:
            kept.append(line)
    path.write_text("".join(kept), encoding="utf-8")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def make_repo(tmp_path: Path, *, trunk: str = "main", branch: str | None = "work") -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", trunk)
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    if branch:
        git(repo, "checkout", "-q", "-b", branch)
    return repo


def seal(repo: Path, intent: Path, *, message: str | None = None) -> None:
    """Commit the intent the way the station does -- with the needs-design
    line in the commit message, which is what the rule recomputes."""
    if message is None:
        line = next(
            line for line in intent.read_text(encoding="utf-8").splitlines()
            if line.startswith("needs-design:")
        )
        message = f"docs(loom): add an intent\n\n{line}\n"
    git(repo, "add", str(intent.relative_to(repo)))
    git(repo, "commit", "-q", "-m", message)


def commit_file(repo: Path, rel: str, content: str = "x\n") -> None:
    target = repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", rel)
    git(repo, "commit", "-q", "-m", f"add {rel}")


def run_checker(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args], capture_output=True, text=True, cwd=str(cwd)
    )


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


# --- intent.schema ---------------------------------------------------------


def test_complete_intent_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/2026-09-02-a.md")
    seal(repo, intent)
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 0, result.stderr


def test_missing_frontmatter_field_blocks_schema(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/a.md", originator="")
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "intent.schema" in blocked_rules(result)
    assert "originator" in result.stderr


def test_missing_required_section_blocks_schema(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/a.md")
    drop_section(intent, "## Acceptance")
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "intent.schema" in blocked_rules(result)
    assert "Acceptance" in result.stderr


def test_unknown_kind_value_blocks_schema(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/a.md", kind="research")
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "intent.schema" in blocked_rules(result)


def test_optional_fields_are_not_required(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/a.md", status="")
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.schema" not in blocked_rules(result)


# --- intent.product-no-identifiers ----------------------------------------


def test_product_problem_with_file_path_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(
        repo / "docs/loom/intent/a.md",
        kind="product",
        problem="Users wait because src/api/handler.py is slow.",
    )
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "intent.product-no-identifiers" in blocked_rules(result)


def test_product_problem_with_code_identifier_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(
        repo / "docs/loom/intent/a.md",
        kind="product",
        problem="Users wait because run_batch() takes a minute.",
    )
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.product-no-identifiers" in blocked_rules(result)


def test_product_problem_with_script_filename_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(
        repo / "docs/loom/intent/a.md",
        kind="product",
        problem="The nightly build.sh never finishes and people give up.",
    )
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.product-no-identifiers" in blocked_rules(result)


def test_engineering_problem_may_name_identifiers(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(
        repo / "docs/loom/intent/a.md",
        kind="engineering",
        problem="src/api/handler.py duplicates run_batch() in six places.",
    )
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.product-no-identifiers" not in blocked_rules(result)


def test_product_prose_without_identifiers_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(
        repo / "docs/loom/intent/a.md",
        kind="product",
        problem="People who use the nightly report wait ten minutes and give up.",
    )
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.product-no-identifiers" not in blocked_rules(result)


def test_only_the_problem_section_is_scanned(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/a.md", kind="product")
    intent.write_text(
        intent.read_text(encoding="utf-8").replace(
            "Everything else.", "Everything in src/api/handler.py."
        ),
        encoding="utf-8",
    )
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.product-no-identifiers" not in blocked_rules(result)


# --- intent.needs-design-reason -------------------------------------------


def test_needs_design_without_reason_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="yes")
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "intent.needs-design-reason" in blocked_rules(result)


def test_needs_design_line_must_appear_in_commit_message(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(
        repo / "docs/loom/intent/a.md", needs_design="yes — many states, no spec exists"
    )
    message = tmp_path / "msg.txt"
    message.write_text("feat(loom): add an intent\n\nNo mention here.\n", encoding="utf-8")
    result = run_checker("intent", str(intent), "--commit-msg", str(message), cwd=repo)
    assert result.returncode == 1
    assert "intent.needs-design-reason" in blocked_rules(result)


def test_commit_message_carrying_the_line_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(
        repo / "docs/loom/intent/a.md", needs_design="yes — many states, no spec exists"
    )
    message = tmp_path / "msg.txt"
    message.write_text(
        "feat(loom): add an intent\n\nneeds-design: yes — many states, no spec exists\n",
        encoding="utf-8",
    )
    result = run_checker("intent", str(intent), "--commit-msg", str(message), cwd=repo)
    assert result.returncode == 0, result.stderr


# --- intent.needs-design-recompute ----------------------------------------


def test_needs_design_no_while_diff_touches_interface_surface_is_blocked(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "src/cli/main.py")
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="no — internal only")
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "intent.needs-design-recompute" in blocked_rules(result)
    assert "src/cli/main.py" in result.stderr


def test_needs_design_no_with_internal_diff_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "src/core/engine.py")
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="no — internal only")
    seal(repo, intent)
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 0, result.stderr


def test_uncommitted_interface_change_is_recomputed_too(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    target = repo / "src/api/routes.py"
    target.parent.mkdir(parents=True)
    target.write_text("x\n", encoding="utf-8")
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="no — internal only")
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.needs-design-recompute" in blocked_rules(result)


def test_needs_design_yes_skips_the_recompute(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "src/cli/main.py")
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="yes — new surface")
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.needs-design-recompute" not in blocked_rules(result)


def test_kickoff_defaults_add_interface_surfaces_and_never_narrow(tmp_path: Path) -> None:
    """A repo knows its own surfaces; it does not get to un-know the
    contract's. Pointing the key at one glob used to REPLACE the manifest
    default, which made `needs-design: no` unfalsifiable in one line
    (W1 adversary P11)."""
    repo = make_repo(tmp_path)
    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True, exist_ok=True)
    kickoff.write_text(
        "# Kickoff Defaults\n\n- interface-surfaces: **/public/** — this repo's own (2026-09-02)\n",
        encoding="utf-8",
    )
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="no — internal only")

    commit_file(repo, "src/public/thing.py")
    added = run_checker("intent", str(intent), cwd=repo)
    assert "intent.needs-design-recompute" in blocked_rules(added)

    commit_file(repo, "src/cli/main.py")
    still_default = run_checker("intent", str(intent), cwd=repo)
    assert "intent.needs-design-recompute" in blocked_rules(still_default)
    assert "src/cli/main.py" in still_default.stderr


def test_the_glob_set_in_use_is_printed(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="no — internal only")
    result = run_checker("intent", str(intent), cwd=repo)
    assert "interface-surfaces" in result.stdout
    assert "**/cli/**" in result.stdout
    assert "manifest default" in result.stdout


# --- the repo's own first v10 intent --------------------------------------


def test_the_repos_own_intent_is_accepted(tmp_path: Path) -> None:
    """Everything recomputed from the file itself passes. The only rule it
    cannot satisfy is the commit-message half of needs-design-reason: the
    commit that landed this intent predates the rule, and HEAD moves on."""
    intent = REPO_ROOT / "docs/loom/intent/2026-09-02-simple-loom-flow.md"
    result = run_checker("intent", str(intent), cwd=REPO_ROOT)
    assert blocked_rules(result) <= {"intent.needs-design-reason"}, result.stderr


# --- the base of the diff (W0-03 review fix 1) -----------------------------


def test_master_is_a_recognised_trunk(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, trunk="master")
    commit_file(repo, "src/cli/main.py")
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="no — internal only")
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "intent.needs-design-recompute" in blocked_rules(result)


def test_an_upstream_branch_is_a_recognised_base(tmp_path: Path) -> None:
    origin = tmp_path / "origin"
    origin.mkdir()
    git(origin, "init", "-q", "--bare", "-b", "trunk")
    repo = make_repo(tmp_path, trunk="trunk", branch=None)
    git(repo, "remote", "add", "origin", str(origin))
    git(repo, "checkout", "-q", "-b", "work")
    git(repo, "push", "-q", "-u", "origin", "work")
    git(repo, "branch", "-D", "-q", "trunk")
    commit_file(repo, "src/cli/main.py")
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="no — internal only")
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.needs-design-recompute" in blocked_rules(result)


def test_no_resolvable_base_fails_closed(tmp_path: Path) -> None:
    """Never "no base, therefore no changes" -- that is a fail-open."""
    repo = make_repo(tmp_path, trunk="scratch", branch=None)
    commit_file(repo, "src/cli/main.py")
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="no — internal only")
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 2
    assert result.stderr.strip()


# --- the commit message half of needs-design-reason (review fix 5) ---------


def test_heads_commit_message_is_used_when_no_flag_is_given(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="yes — new surface")
    seal(repo, intent, message="docs(loom): add an intent\n\nno mention of the line\n")
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "intent.needs-design-reason" in blocked_rules(result)


def test_the_flag_still_wins_over_head(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="yes — new surface")
    seal(repo, intent, message="docs(loom): add an intent\n\nno mention of the line\n")
    message = tmp_path / "msg.txt"
    message.write_text(
        "docs(loom): add an intent\n\nneeds-design: yes — new surface\n", encoding="utf-8"
    )
    result = run_checker("intent", str(intent), "--commit-msg", str(message), cwd=repo)
    assert result.returncode == 0, result.stderr


# --- branch_base: the trunk itself is not a base (W2 adversary P13) --------


def test_working_on_the_trunk_fails_closed(tmp_path: Path) -> None:
    """On `main` with no remote, `merge-base HEAD main` IS HEAD, so every
    diff-recomputing rule would see an empty diff and pass a claim it never
    tested. That is the one thing branch_base() exists to prevent."""
    repo = make_repo(tmp_path, branch=None)
    commit_file(repo, "src/cli/main.py")
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="no — internal only")
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 2
    assert "git switch -c" in result.stderr


def test_a_local_trunk_is_still_a_base_from_a_branch(tmp_path: Path) -> None:
    """The remote-less repo is the common case; only being ON the trunk is
    fatal. `main` alone still resolves the base from a feature branch."""
    repo = make_repo(tmp_path, branch="work")
    commit_file(repo, "src/cli/main.py")
    intent = write_intent(repo / "docs/loom/intent/a.md", needs_design="no — internal only")
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "intent.needs-design-recompute" in blocked_rules(result)


# --- intent.kind-recompute (W2 adversary P05) ------------------------------


def test_engineering_kind_over_an_interface_diff_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "src/cli/add.py")
    intent = write_intent(
        repo / "docs/loom/intent/a.md",
        kind="engineering",
        needs_design="yes — the CLI grows a flag",
    )
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "intent.kind-recompute" in blocked_rules(result)
    assert "src/cli/add.py" in result.stderr


def test_product_kind_over_an_interface_diff_is_fine(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "src/cli/add.py")
    intent = write_intent(
        repo / "docs/loom/intent/a.md",
        kind="product",
        needs_design="yes — the CLI grows a flag",
    )
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.kind-recompute" not in blocked_rules(result)


def test_engineering_kind_off_every_interface_surface_is_fine(tmp_path: Path) -> None:
    """`needs-design: yes` for reason (b) -- many states, no spec -- is a
    legitimate engineering combination (concept-model §2b, §4); only the
    diff makes it a user surface."""
    repo = make_repo(tmp_path)
    commit_file(repo, "src/store/index.py")
    intent = write_intent(
        repo / "docs/loom/intent/a.md",
        kind="engineering",
        needs_design="yes — many states, no spec exists",
    )
    seal(repo, intent)
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 0, result.stderr


# --- intent.product-no-identifiers: the F3 false positives ------------------


def test_a_consumer_product_name_is_not_an_identifier(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    for name in ("iPhone", "iPad", "iOS", "macOS", "eBay", "iCloud", "iMac", "tvOS",
                 "watchOS", "iPadOS"):
        intent = write_intent(
            repo / "docs/loom/intent/a.md",
            kind="product",
            problem=f"People on {name} cannot see what is due and miss things.",
        )
        result = run_checker("intent", str(intent), cwd=repo)
        assert "intent.product-no-identifiers" not in blocked_rules(result), name


def test_a_date_like_fraction_is_not_a_path(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    for fraction in ("9/10", "12/31", "9/10/26", "12/31/2026"):
        intent = write_intent(
            repo / "docs/loom/intent/a.md",
            kind="product",
            problem=f"On {fraction} the list still showed yesterday, so people gave up.",
        )
        result = run_checker("intent", str(intent), cwd=repo)
        assert "intent.product-no-identifiers" not in blocked_rules(result), fraction


def test_a_real_camel_case_identifier_is_still_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(
        repo / "docs/loom/intent/a.md",
        kind="product",
        problem="The saveDraft path loses what people typed.",
    )
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.product-no-identifiers" in blocked_rules(result)


def test_a_real_path_is_still_blocked_next_to_an_allowlisted_name(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    intent = write_intent(
        repo / "docs/loom/intent/a.md",
        kind="product",
        problem="On iPhone the list is empty because src/app/x.py drops the rows.",
    )
    result = run_checker("intent", str(intent), cwd=repo)
    assert "intent.product-no-identifiers" in blocked_rules(result)
    assert "src/app/x.py" in result.stderr


def test_a_none_placeholder_satisfies_a_required_section(tmp_path: Path) -> None:
    """`## Open questions` is required and checked for emptiness, so the
    template tells the author to write `- none` when there are none. That
    string has to actually pass."""
    repo = make_repo(tmp_path)
    intent = write_intent(repo / "docs/loom/intent/a.md")
    text = intent.read_text(encoding="utf-8").replace("- None yet.", "- none")
    intent.write_text(text, encoding="utf-8")
    seal(repo, intent)
    result = run_checker("intent", str(intent), cwd=repo)
    assert result.returncode == 0, result.stderr
