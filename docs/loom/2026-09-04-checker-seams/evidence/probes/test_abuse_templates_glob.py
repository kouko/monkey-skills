"""Adversarial probes against W0-02 (templates glob is not automatically a
user surface), written BEFORE W0-02 exists, per plan task W0-01.

Target (does not exist yet at W0-01 time): `touched_interface_surfaces()`
in `loom-code/scripts/loom_checker.py` filtering the interface-glob matches
by `artifact_types()` so only paths typed `code` count as a touched user
surface -- `docs`/`skill`/etc. under `**/templates/**` should stop tripping
`intent.needs-design-recompute` and `intent.kind-recompute`.

Attack: (1) an engineering-kind intent whose diff touches
`loom-code/contract/templates/intent.md` (a `.md` -> type `docs`) must be
let through by both `intent` and `intake write-plan` after the fix, but is
BLOCKED today -- verified live below (see docstrings), so those two cases
are `xfail(strict=True)`. (2) the same diff shape but with `.py`/`.tsx`
files under `templates/` (both type `code`), plus `src/cli/x.py`, must stay
blocked BOTH before and after -- a docs-only carve-out must not become a
directory-wide one. (3) KICKOFF-DEFAULTS `interface-surfaces:` can only ADD
a glob, never remove one, so a KICKOFF line that tries to *narrow* the
surface (e.g. `nothing/**`) leaves the manifest defaults in force -- this is
existing `interface_surfaces()` behaviour, untouched by W0-02, so both
cases assert the SAME thing today and after.

Fatal if broken: a docs-only carve-out that quietly widens (any code path
under templates/ starts passing) would let an agent smuggle a real
interface change through `needs-design: no` by putting it under a
`templates/` directory -- exactly the hole `intent.kind-recompute`'s
`kickoff_defaults... can only ADD globs, never remove one` line already
promises does not exist for the KICKOFF grammar itself.

No mutation/fuzz tool is declared for this repo (plan Boundary), so this
file is the required executable abuse/boundary cases (5 here, floor is 3).

Each fixture is a REAL git repo (mirrors `test_loom_checker_push.py`'s own
fixtures) run through the real `loom_checker.py intent` / `intake
write-plan` subcommands via subprocess -- the rule under attack recomputes
from `git diff`, so a mocked repo would test nothing.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# file: docs/loom/2026-09-04-checker-seams/evidence/probes/<this>.py
# parents: [0]=probes [1]=evidence [2]=<change-id> [3]=loom [4]=docs [5]=repo root
REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))

CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"

INTENT_TEMPLATE = """# {title}
originator: kouko
kind: {kind}
{needs_design}
status: confirmed {date}

## Problem
{problem}

## Proposed outcome
{outcome}

## Acceptance
1. it works.

## Constraints
- none

## Out of scope
- none

## Open questions
- none
"""


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_checker(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args], capture_output=True, text=True, cwd=str(cwd)
    )


def _init_work_repo(tmp_path: Path, *, kickoff_lines: list[str] | None = None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    if kickoff_lines:
        kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
        kickoff.parent.mkdir(parents=True, exist_ok=True)
        kickoff.write_text(
            "# Kickoff Defaults\n\n" + "\n".join(kickoff_lines) + "\n", encoding="utf-8"
        )
        git(repo, "add", "docs/loom/KICKOFF-DEFAULTS.md")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    return repo


def _commit_intent_and_files(
    repo: Path,
    *,
    change_id: str,
    kind: str,
    needs_design: str,
    problem: str,
    files: dict[str, str],
) -> Path:
    """Writes `docs/loom/intent/<change_id>.md` plus `files`, then commits
    them together with a message that carries the `needs-design:` line
    verbatim (`deciding_commit` reads that commit's message).

    `needs_design` is the WHOLE frontmatter line (e.g.
    `"needs-design: no — reason"`), used verbatim both in the intent's
    frontmatter and in the commit message -- not just the `no — reason`
    value."""
    intent_path = repo / "docs" / "loom" / "intent" / f"{change_id}.md"
    intent_path.parent.mkdir(parents=True, exist_ok=True)
    intent_path.write_text(
        INTENT_TEMPLATE.format(
            title=change_id,
            kind=kind,
            needs_design=needs_design,
            date=change_id[:10],
            problem=problem,
            outcome=f"{problem} fixed plainly.",
        ),
        encoding="utf-8",
    )
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git(repo, "add", "-A")
    git(
        repo,
        "commit",
        "-q",
        "-m",
        f"docs(loom): intent {change_id} confirmed\n\n{needs_design}",
    )
    return intent_path


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


# --- (1) docs-typed template path: RED until W0-02 -------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "RED until W0-02: touched_interface_surfaces() does not yet filter by "
        "artifact type, so a .md under templates/ still trips intent.kind-recompute "
        "and intent.needs-design-recompute for an engineering intent. "
        "Observed today: BLOCK intent.needs-design-recompute + BLOCK intent.kind-recompute, exit 1."
    ),
)
def test_engineering_intent_touching_templates_md_passes_intent_after_fix(
    tmp_path: Path,
) -> None:
    repo = _init_work_repo(tmp_path)
    change_id = "2099-02-01-templates-md"
    intent_path = _commit_intent_and_files(
        repo,
        change_id=change_id,
        kind="engineering",
        needs_design="needs-design: no — agent-facing template text only, no user surface",
        problem="the agent-facing template text is stale for the team.",
        files={"loom-code/contract/templates/intent.md": "# template\n"},
    )
    result = run_checker(
        "intent", str(intent_path.relative_to(repo)), cwd=repo
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.xfail(
    strict=True,
    reason=(
        "RED until W0-02: `intake write-plan` runs the same "
        "touched_interface_surfaces() recompute as `intent`, so it inherits the "
        "same false block on a docs-typed templates/ path. Observed today: "
        "BLOCK intent.kind-recompute, exit 1."
    ),
)
def test_engineering_intent_touching_templates_md_passes_intake_write_plan_after_fix(
    tmp_path: Path,
) -> None:
    repo = _init_work_repo(tmp_path)
    change_id = "2099-02-01-templates-md-intake"
    _commit_intent_and_files(
        repo,
        change_id=change_id,
        kind="engineering",
        needs_design="needs-design: no — agent-facing template text only, no user surface",
        problem="the agent-facing template text is stale for the team.",
        files={"loom-code/contract/templates/intent.md": "# template\n"},
    )
    result = run_checker("intake", "write-plan", change_id, cwd=repo)
    assert result.returncode == 0, result.stderr


# --- (2) code-typed paths under templates/, and src/cli/: must STAY blocked,
#         today and after (the docs carve-out must not widen) --------------


def test_templates_py_and_tsx_and_cli_paths_still_blocked(tmp_path: Path) -> None:
    repo = _init_work_repo(tmp_path)
    change_id = "2099-02-02-templates-code"
    intent_path = _commit_intent_and_files(
        repo,
        change_id=change_id,
        kind="engineering",
        needs_design="needs-design: no — internal script only",
        problem="the internal script is stale for the team.",
        files={
            "loom-code/contract/templates/x.py": "x = 1\n",
            "loom-code/contract/templates/x.tsx": "const x = 1\n",
            "src/cli/x.py": "x = 1\n",
        },
    )
    result = run_checker(
        "intent", str(intent_path.relative_to(repo)), cwd=repo
    )
    assert result.returncode == 1
    blocked = blocked_rules(result)
    assert "intent.needs-design-recompute" in blocked
    assert "intent.kind-recompute" in blocked
    for path in (
        "loom-code/contract/templates/x.py",
        "loom-code/contract/templates/x.tsx",
        "src/cli/x.py",
    ):
        assert path in result.stderr


# --- (3) KICKOFF interface-surfaces: adds only, never narrows --------------


def test_kickoff_interface_surfaces_can_add_a_glob(tmp_path: Path) -> None:
    repo = _init_work_repo(tmp_path, kickoff_lines=["- interface-surfaces: extra/**"])
    change_id = "2099-02-03-add-glob"
    intent_path = _commit_intent_and_files(
        repo,
        change_id=change_id,
        kind="engineering",
        needs_design="needs-design: no — internal script only",
        problem="the internal script is stale for the team.",
        files={"extra/thing.py": "x = 1\n"},
    )
    result = run_checker(
        "intent", str(intent_path.relative_to(repo)), cwd=repo
    )
    assert result.returncode == 1
    assert "intent.kind-recompute" in blocked_rules(result)
    assert "extra/thing.py" in result.stderr


def test_kickoff_interface_surfaces_cannot_narrow_away_a_default(tmp_path: Path) -> None:
    """A KICKOFF line that tries to REPLACE the defaults with a glob that
    matches nothing (`nothing/**`) must not remove `**/cli/**` from the
    surface -- `interface_surfaces()` unions, it never lets the repo's own
    file replace the manifest's. `src/cli/x.py` must still be caught."""
    repo = _init_work_repo(tmp_path, kickoff_lines=["- interface-surfaces: nothing/**"])
    change_id = "2099-02-04-narrow-attempt"
    intent_path = _commit_intent_and_files(
        repo,
        change_id=change_id,
        kind="engineering",
        needs_design="needs-design: no — internal script only",
        problem="the internal script is stale for the team.",
        files={"src/cli/x.py": "x = 1\n"},
    )
    result = run_checker(
        "intent", str(intent_path.relative_to(repo)), cwd=repo
    )
    assert result.returncode == 1
    assert "intent.kind-recompute" in blocked_rules(result)
    assert "src/cli/x.py" in result.stderr
