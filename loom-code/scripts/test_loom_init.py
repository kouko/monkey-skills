"""loom_init.py scaffolds the queue layer and proves it against the live
validators.

Task 1 of docs/loom/plans/2026-08-10-loom-init-scaffold.md: 5 of 7
consuming repos run without the queue layer because adoption requires
hand-copying the charter + DIRECTION skeleton; the one repo that
hand-copied got drift. `loom_init.py` mints the store from templates
shipped beside it and then self-verifies the fresh store by running the
sibling `backlog_index.py --validate` and `--direction-check` — the same
validators every adopted store lives under.

False-green discipline (docs/loom/memory/
subprocess-red-tests-go-false-green-before-the-script-exists.md): the
existence assert comes FIRST, and each subprocess assert pins a positive
fact only a real run produces — never a bare exit-code check.

Mutation discipline (docs/loom/memory/
a-mutation-test-must-run-the-production-assertion.md): each mutation
probe mutates the INPUT (a scratch copy of the templates) and drives it
through the PRODUCTION path — the real loom_init.py run, and for the
charter probe the production test function itself (`ACTIVE_SCRIPTS` is
monkeypatched so the green test re-executes against the mutated
scaffold) — never a re-implemented predicate beside the production one.

External-surface grounding (source a — live verification): the one git
flag the script depends on (`git -C <target> rev-parse --show-toplevel`,
the nested-cwd advisory) is exercised LIVE by
`test_nested_cwd_run_warns_but_proceeds` against a throwaway `git init`
repo — the asserted stderr line must carry the real toplevel path the
installed git printed, so a flag regression surfaces here, not via
belief.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent
LOOM_INIT = SCRIPTS / "loom_init.py"
BACKLOG_INDEX = SCRIPTS / "backlog_index.py"
TEMPLATE_README = SCRIPTS / "templates" / "backlog-README.md"
TEMPLATE_DIRECTION = SCRIPTS / "templates" / "DIRECTION.md"
REPO_ROOT = SCRIPTS.parent.parent

# The exact line backlog_index.py's --direction-write renders into `## Now`
# for an EMPTY queue (backlog_index.py DIRECTION_EMPTY_QUEUE_LINE). The
# template must carry it verbatim: --direction-check diffs the whole
# section body against regenerated output, so any drift is exit 1.
DIRECTION_PLACEHOLDER = "_(queue empty — bet at the next close-out)_"

# Charter sections the scaffolded README must carry (structural pins on
# the template — no validator reads the README, so this test is the guard).
REQUIRED_CHARTER_HEADINGS = (
    "## Frontmatter contract",
    "## Closed status vocabulary",
    "## Verbs",
    "## Filename rule",
    "is generated — never hand-edit it",  # ## `docs/loom/BACKLOG.md` heading
    "## Archive rule",
)

# Mutation probes repoint this at a scratch scripts dir via monkeypatch;
# every helper resolves it at CALL time so the production test functions
# themselves re-execute against the mutated copy.
ACTIVE_SCRIPTS = SCRIPTS


def _run_init(target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ACTIVE_SCRIPTS / "loom_init.py"), str(target)],
        capture_output=True,
        text=True,
    )


def _scaffold_ok(target: Path) -> subprocess.CompletedProcess:
    target.mkdir(parents=True, exist_ok=True)
    result = _run_init(target)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "loom-init: OK" in result.stdout, result.stdout + result.stderr
    return result


def _scratch_scripts(tmp_path: Path) -> Path:
    """A scratch copy of the production scripts + templates, so a mutation
    probe can rewrite a template and still run the REAL loom_init.py
    (which resolves templates and the sibling validator __file__-relative)."""
    scratch = tmp_path / "scratch-scripts"
    scratch.mkdir()
    shutil.copy(LOOM_INIT, scratch / "loom_init.py")
    shutil.copy(BACKLOG_INDEX, scratch / "backlog_index.py")
    shutil.copytree(SCRIPTS / "templates", scratch / "templates")
    return scratch


def test_loom_init_ships_with_its_templates_and_runs(tmp_path):
    assert LOOM_INIT.is_file(), f"loom_init.py does not exist at {LOOM_INIT}"
    assert TEMPLATE_README.is_file(), f"missing template {TEMPLATE_README}"
    assert TEMPLATE_DIRECTION.is_file(), f"missing template {TEMPLATE_DIRECTION}"
    # Run probe against a tmp fixture with a pre-made store: the refusal
    # branch is a positive fact only a real run produces — and probing a
    # fixture keeps the suite decoupled from the live repo's adoption state.
    (tmp_path / "docs" / "loom" / "backlog").mkdir(parents=True)
    result = subprocess.run(
        [sys.executable, str(LOOM_INIT), str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert "already exists" in result.stdout, result.stdout + result.stderr
    assert result.returncode == 1, result.stdout + result.stderr


def test_agents_md_declares_loom_init():
    """Command-surface accretion obligation: AGENTS.md's managed
    command-surface block must declare loom_init.py so the bootstrap
    verb shipped in #683 has a declared entry point (pin convention:
    test_writing_plans_change_binding.py::test_agents_md_declares_coverage_script)."""
    agents_md = REPO_ROOT / "AGENTS.md"
    assert agents_md.is_file(), f"AGENTS.md is absent at {agents_md}"
    text = agents_md.read_text(encoding="utf-8")
    start = text.index("BEGIN command-surface (managed)")
    end = text.index("END command-surface (managed)")
    managed_block = text[start:end]
    assert "loom_init.py" in managed_block, \
        "AGENTS.md managed command-surface block must declare loom_init.py"


def test_direction_template_carries_the_placeholder_line_verbatim():
    text = TEMPLATE_DIRECTION.read_text(encoding="utf-8")
    assert f"\n{DIRECTION_PLACEHOLDER}\n" in text, (
        "the DIRECTION template's ## Now body must carry the generator's "
        f"empty-queue placeholder verbatim, got:\n{text}"
    )


def test_direction_scaffold_has_onramp_standing_choices_section(tmp_path):
    """Task 6: the scaffolded DIRECTION.md carries an empty
    `## On-ramp standing choices` section so a fresh repo does not need
    a manual first-touch addition before check_onramp_choice.py can
    read it."""
    target = tmp_path / "repo"
    result = _scaffold_ok(target)

    direction = target / "docs" / "loom" / "DIRECTION.md"
    text = direction.read_text(encoding="utf-8")
    assert "## On-ramp standing choices" in text, (
        f"scaffolded DIRECTION.md missing the section, got:\n{text}\n"
        f"{result.stdout}{result.stderr}"
    )


def test_refuses_when_the_store_already_exists(tmp_path):
    target = tmp_path / "repo"
    store = target / "docs" / "loom" / "backlog"
    store.mkdir(parents=True)
    sentinel = store / "README.md"
    sentinel.write_text("SENTINEL — must never be overwritten\n", encoding="utf-8")

    result = _run_init(target)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "already exists" in result.stdout, result.stdout + result.stderr
    assert sentinel.read_text(encoding="utf-8").startswith("SENTINEL"), (
        "loom-init must never touch an existing store"
    )
    assert not (target / "docs" / "loom" / "DIRECTION.md").exists(), (
        "refusal must write nothing at all"
    )


def test_refuses_when_direction_exists_without_a_store(tmp_path):
    """Half-adopted repo: DIRECTION.md present, backlog absent. The verb's
    never-overwrite posture covers the human-owned DIRECTION themes too."""
    target = tmp_path / "repo"
    loom = target / "docs" / "loom"
    loom.mkdir(parents=True)
    direction = loom / "DIRECTION.md"
    direction.write_text("# Direction\n\n## Now\n\nhuman themes\n", encoding="utf-8")

    result = _run_init(target)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "DIRECTION.md" in result.stdout, result.stdout + result.stderr
    assert "human themes" in direction.read_text(encoding="utf-8")


def test_scaffold_creates_all_artifacts_with_vintage_stamps(tmp_path):
    target = tmp_path / "repo"
    result = _scaffold_ok(target)

    loom = target / "docs" / "loom"
    readme = loom / "backlog" / "README.md"
    direction = loom / "DIRECTION.md"
    assert readme.is_file(), "charter instance missing"
    assert direction.is_file(), "DIRECTION skeleton missing"
    assert (loom / "plans" / ".gitkeep").is_file(), "plans/ not git-persistable"
    assert (loom / "specs" / ".gitkeep").is_file(), "specs/ not git-persistable"

    expected_version = json.loads(
        (REPO_ROOT / "loom-code" / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )["version"]
    stamp = f"<!-- scaffolded by loom-init (loom-code {expected_version}) -->"
    for path in (readme, direction):
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        assert first_line == stamp, (
            f"{path.name} first line is {first_line!r}, expected {stamp!r}"
        )

    # The contract says the two validator exit codes are RELAYED, not
    # swallowed into a bare success line.
    assert "--validate exit 0" in result.stdout, result.stdout
    assert "--direction-check exit 0" in result.stdout, result.stdout


def test_fresh_store_passes_the_real_validators(tmp_path):
    """Independent of loom_init's own relay: this test runs the production
    validators itself against the scaffolded store."""
    target = tmp_path / "repo"
    _scaffold_ok(target)

    validate = subprocess.run(
        [sys.executable, str(BACKLOG_INDEX), "--validate"],
        capture_output=True,
        text=True,
        cwd=target,
    )
    assert "backlog_index --validate: OK" in validate.stdout, (
        validate.stdout + validate.stderr
    )
    assert validate.returncode == 0, validate.stdout + validate.stderr

    direction_check = subprocess.run(
        [
            sys.executable,
            str(BACKLOG_INDEX),
            "--direction-check",
            "docs/loom/DIRECTION.md",
        ],
        capture_output=True,
        text=True,
        cwd=target,
    )
    assert "backlog_index --direction-check: OK" in direction_check.stdout, (
        direction_check.stdout + direction_check.stderr
    )
    assert direction_check.returncode == 0, (
        direction_check.stdout + direction_check.stderr
    )


def test_scaffolded_readme_carries_the_charter_sections(tmp_path):
    target = tmp_path / "repo"
    _scaffold_ok(target)
    readme = (target / "docs" / "loom" / "backlog" / "README.md").read_text(
        encoding="utf-8"
    )
    for heading in REQUIRED_CHARTER_HEADINGS:
        assert heading in readme, f"charter instance lost section {heading!r}"


def test_mutation_stripped_placeholder_turns_init_self_verify_red(tmp_path):
    """Mutate the INPUT (DIRECTION template loses the placeholder line) and
    run the whole PRODUCTION pipeline: init's self-verify must go red and
    init itself must exit 1."""
    scratch = _scratch_scripts(tmp_path)
    template = scratch / "templates" / "DIRECTION.md"
    text = template.read_text(encoding="utf-8")
    mutated = text.replace(f"{DIRECTION_PLACEHOLDER}\n", "")
    assert DIRECTION_PLACEHOLDER not in mutated, "mutation did not apply"
    template.write_text(mutated, encoding="utf-8")

    target = tmp_path / "repo"
    target.mkdir()
    result = subprocess.run(
        [sys.executable, str(scratch / "loom_init.py"), str(target)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "loom-init: FAIL" in result.stdout, result.stdout + result.stderr
    assert "loom-init: OK" not in result.stdout, result.stdout


def test_mutation_stripped_charter_section_fails_the_production_assertion(
    tmp_path, monkeypatch
):
    """Mutate the INPUT (charter template loses a required section) and
    invoke the PRODUCTION test function itself — never a re-implemented
    predicate (docs/loom/memory/
    a-mutation-test-must-run-the-production-assertion.md)."""
    scratch = _scratch_scripts(tmp_path)
    template = scratch / "templates" / "backlog-README.md"
    text = template.read_text(encoding="utf-8")
    mutated = text.replace("## Closed status vocabulary", "## (section removed)")
    assert mutated != text, "mutation did not apply"
    template.write_text(mutated, encoding="utf-8")

    monkeypatch.setattr(sys.modules[__name__], "ACTIVE_SCRIPTS", scratch)
    with pytest.raises(AssertionError):
        test_scaffolded_readme_carries_the_charter_sections(tmp_path / "mut")


def test_refuses_before_any_write_when_a_file_blocks_a_scaffold_path(tmp_path):
    """(10) Whole-branch review 🟡: a stray FILE at any scaffold path
    (probed: docs/loom/plans) used to crash MID-scaffold with residue
    left behind — later runs then misdescribed the crash husk as
    adoption. All collision points now precheck BEFORE the first
    write: loud refusal naming the path, exit 1, ZERO residue."""
    assert LOOM_INIT.is_file(), f"missing script at {LOOM_INIT}"
    target = tmp_path / "repo"
    (target / "docs" / "loom").mkdir(parents=True)
    (target / "docs" / "loom" / "plans").write_text("stray file")

    result = _run_init(target)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "plans" in result.stdout, result.stdout
    assert "not a directory" in result.stdout, result.stdout
    assert not (target / "docs" / "loom" / "backlog").exists(), (
        "residue: backlog/ was created before the refusal"
    )
    assert not (target / "docs" / "loom" / "DIRECTION.md").exists(), (
        "residue: DIRECTION.md was created before the refusal"
    )


def test_nested_cwd_run_warns_but_proceeds(tmp_path):
    """Task 3 (plan 2026-08-10-cheap-hardening-batch.md): a target nested
    inside a git repo gets ONE advisory line on stderr naming the repo
    root — and the scaffold still proceeds with exit 0, because monorepo
    subdirs adopting their own queue layer are legitimate (advisory,
    never refusal; PR #683 debt)."""
    init = subprocess.run(
        ["git", "init", str(tmp_path)], capture_output=True, text=True
    )
    assert init.returncode == 0, init.stdout + init.stderr
    sub = tmp_path / "sub"
    sub.mkdir()

    result = _run_init(sub)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "loom-init: OK" in result.stdout, result.stdout + result.stderr
    assert (sub / "docs" / "loom" / "backlog" / "README.md").is_file(), (
        "advisory must never block the scaffold"
    )
    assert (sub / "docs" / "loom" / "DIRECTION.md").is_file(), (
        "advisory must never block the scaffold"
    )
    assert "not the git repo root" in result.stderr, result.stderr
    assert str(tmp_path.resolve()) in result.stderr, (
        "the advisory must name the repo root, got: " + result.stderr
    )


def test_non_git_target_stays_silent_on_stderr(tmp_path):
    """Companion pin: the plain success run (target not inside any git
    repo) emits NOTHING on stderr — the nested-cwd advisory is the only
    stderr speaker and it stays quiet outside a repo."""
    result = _scaffold_ok(tmp_path / "repo")
    assert result.stderr == "", result.stderr


def test_stray_file_at_store_path_is_not_called_adoption(tmp_path):
    """(11) Companion 🟢: a stray FILE at docs/loom/backlog gets the
    inspect-and-remove message, never the 'has adopted the queue
    layer' claim (which is reserved for a real store directory)."""
    assert LOOM_INIT.is_file(), f"missing script at {LOOM_INIT}"
    target = tmp_path / "repo"
    (target / "docs" / "loom").mkdir(parents=True)
    (target / "docs" / "loom" / "backlog").write_text("stray file")

    result = _run_init(target)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "not a directory" in result.stdout, result.stdout
    assert "adopted the queue layer" not in result.stdout, result.stdout
