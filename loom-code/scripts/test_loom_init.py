"""loom_init.py scaffolds the queue layer and proves it against the live
validators.

Task 1 of docs/loom/plans/2026-08-10-loom-init-scaffold.md: 5 of 7
consuming repos run without the queue layer because adoption requires
hand-copying the charter + kickoff-defaults skeleton; the one repo that
hand-copied got drift. `loom_init.py` mints the store from templates
shipped beside it and then self-verifies the fresh store by running the
sibling `backlog_index.py --validate` — the same validator every
adopted store lives under.

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
TEMPLATE_KICKOFF_DEFAULTS = SCRIPTS / "templates" / "KICKOFF-DEFAULTS.md"
REPO_ROOT = SCRIPTS.parent.parent

# Charter sections the scaffolded README must carry (structural pins on
# the template — no validator reads the README, so this test is the guard).
REQUIRED_CHARTER_HEADINGS = (
    "## Frontmatter contract",
    "## Status word definitions",
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
    assert TEMPLATE_KICKOFF_DEFAULTS.is_file(), f"missing template {TEMPLATE_KICKOFF_DEFAULTS}"
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


def test_scaffold_creates_kickoff_defaults_not_direction(tmp_path):
    """Task 6: loom_init scaffolds docs/loom/KICKOFF-DEFAULTS.md instead of
    the old direction skeleton — a fresh scaffold target ends up with the
    former and none of the latter."""
    target = tmp_path / "repo"
    _scaffold_ok(target)

    loom = target / "docs" / "loom"
    assert (loom / "KICKOFF-DEFAULTS.md").is_file(), "KICKOFF-DEFAULTS.md not scaffolded"
    assert not (loom / ("DIREC" + "TION.md")).exists(), (
        "loom_init must no longer scaffold the old direction skeleton"
    )


def test_kickoff_defaults_scaffold_has_onramp_standing_choices_section(tmp_path):
    """Task 6: the scaffolded KICKOFF-DEFAULTS.md carries an empty
    `## On-ramp standing choices` section so a fresh repo does not need
    a manual first-touch addition before check_onramp_choice.py can
    read it."""
    target = tmp_path / "repo"
    result = _scaffold_ok(target)

    kickoff_defaults = target / "docs" / "loom" / "KICKOFF-DEFAULTS.md"
    text = kickoff_defaults.read_text(encoding="utf-8")
    assert "## On-ramp standing choices" in text, (
        f"scaffolded KICKOFF-DEFAULTS.md missing the section, got:\n{text}\n"
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
    assert not (target / "docs" / "loom" / "KICKOFF-DEFAULTS.md").exists(), (
        "refusal must write nothing at all"
    )


def test_refuses_when_kickoff_defaults_exists_without_a_store(tmp_path):
    """Half-adopted repo: KICKOFF-DEFAULTS.md present, backlog absent. The
    verb's never-overwrite posture covers the human-owned choices too."""
    target = tmp_path / "repo"
    loom = target / "docs" / "loom"
    loom.mkdir(parents=True)
    kickoff_defaults = loom / "KICKOFF-DEFAULTS.md"
    kickoff_defaults.write_text(
        "# Kickoff Defaults\n\n## On-ramp standing choices\n\nhuman choices\n",
        encoding="utf-8",
    )

    result = _run_init(target)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "KICKOFF-DEFAULTS.md" in result.stdout, result.stdout + result.stderr
    assert "human choices" in kickoff_defaults.read_text(encoding="utf-8")


def test_refuses_when_purpose_exists_and_never_overwrites_it(tmp_path):
    """Data-loss guard: a hand-authored PURPOSE.md must survive a scaffold
    run byte-identical — the refusal ladder must guard purpose.exists()
    the same way it guards direction.exists(), BEFORE _instantiate ever
    writes to it (code-quality review NEEDS_REVISION, 2026-08-20)."""
    target = tmp_path / "repo"
    loom = target / "docs" / "loom"
    loom.mkdir(parents=True)
    purpose = loom / "PURPOSE.md"
    original = "# Purpose\n\n**Why:** 我親手寫的目的，不該被蓋掉\n"
    purpose.write_text(original, encoding="utf-8")

    result = _run_init(target)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "PURPOSE.md" in result.stdout, result.stdout + result.stderr
    assert purpose.read_text(encoding="utf-8") == original, (
        "loom-init must never touch an existing hand-authored PURPOSE.md"
    )


def test_scaffold_creates_all_artifacts_with_vintage_stamps(tmp_path):
    target = tmp_path / "repo"
    result = _scaffold_ok(target)

    loom = target / "docs" / "loom"
    readme = loom / "backlog" / "README.md"
    kickoff_defaults = loom / "KICKOFF-DEFAULTS.md"
    assert readme.is_file(), "charter instance missing"
    assert kickoff_defaults.is_file(), "KICKOFF-DEFAULTS skeleton missing"
    assert (loom / "plans" / ".gitkeep").is_file(), "plans/ not git-persistable"
    assert (loom / "specs" / ".gitkeep").is_file(), "specs/ not git-persistable"

    expected_version = json.loads(
        (REPO_ROOT / "loom-code" / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )["version"]
    stamp = f"<!-- scaffolded by loom-init (loom-code {expected_version}) -->"
    for path in (readme, kickoff_defaults):
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        assert first_line == stamp, (
            f"{path.name} first line is {first_line!r}, expected {stamp!r}"
        )

    # The contract says the validator exit code is RELAYED, not swallowed
    # into a bare success line.
    assert "--validate exit 0" in result.stdout, result.stdout


def test_scaffold_creates_purpose_md_with_prompt_not_prose(tmp_path):
    target = tmp_path / "repo"
    _scaffold_ok(target)

    purpose = target / "docs" / "loom" / "PURPOSE.md"
    assert purpose.is_file(), "PURPOSE.md not scaffolded"

    text = purpose.read_text(encoding="utf-8")
    assert "**Why:**" in text, "PURPOSE.md missing the Why: field"
    assert "**Done when:**" in text, "PURPOSE.md missing the Done when: field"

    # The template body is a PROMPT to the author, never pre-filled prose —
    # a filled-in template would pass this same check while saying nothing
    # (docs/loom/specs/2026-08-20-north-star-serves-link.md ## Decision).
    # The old direction skeleton's placeholder line is the negative
    # control: it is not purpose prose, so its presence in PURPOSE.md
    # would mean the wrong template got copied, not that PURPOSE.md was
    # pre-filled.
    assert "queue empty" not in text
    assert "one sentence" in text.lower() or "one-sentence" in text.lower()


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


def test_scaffolded_readme_carries_the_charter_sections(tmp_path):
    target = tmp_path / "repo"
    _scaffold_ok(target)
    readme = (target / "docs" / "loom" / "backlog" / "README.md").read_text(
        encoding="utf-8"
    )
    for heading in REQUIRED_CHARTER_HEADINGS:
        assert heading in readme, f"charter instance lost section {heading!r}"


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
    mutated = text.replace("## Status word definitions", "## (section removed)")
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
    assert not (target / "docs" / "loom" / "KICKOFF-DEFAULTS.md").exists(), (
        "residue: KICKOFF-DEFAULTS.md was created before the refusal"
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
    assert (sub / "docs" / "loom" / "KICKOFF-DEFAULTS.md").is_file(), (
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


# Fix round on Task 5 (code-quality review NEEDS_REVISION): three residual
# false statements left over from the charter move above.


def _normalized(text: str) -> str:
    return " ".join(text.split())


BACKLOG_README = REPO_ROOT / "docs" / "loom" / "backlog" / "README.md"
TEMPLATE_BACKLOG_README = (
    REPO_ROOT / "loom-code" / "scripts" / "templates" / "backlog-README.md"
)

# The named list, not a glob — a glob that silently matched zero files
# would pass vacuously; naming all five makes a missing file a hard fail.
SIBLING_ROADMAPS = (
    REPO_ROOT / "loom-code" / "ROADMAP.md",
    REPO_ROOT / "legal-toolkit" / "ROADMAP.md",
    REPO_ROOT / "philosophers-toolkit" / "ROADMAP.md",
    REPO_ROOT / "systems-thinking-toolkit" / "ROADMAP.md",
    REPO_ROOT / "investing-toolkit" / "ROADMAP.md",
)

FALSE_SSOT_CLAIM = "charter header — the convention's SSOT."


def test_no_file_claims_direction_md_charter_header_is_the_ssot():
    # Finding 1: the charter moved out of the old direction skeleton, but
    # this claim (live doc + its scaffold template) was never updated to
    # say so.
    for path in (BACKLOG_README, TEMPLATE_BACKLOG_README):
        text = path.read_text(encoding="utf-8")
        assert FALSE_SSOT_CLAIM not in text, (
            f"{path} still claims the old direction skeleton's charter "
            "header is the SSOT, but the charter now lives in "
            "docs/loom/backlog/README.md (this file itself)"
        )


def test_all_sibling_roadmaps_retarget_the_charter_pointer():
    # Finding 2: loom-code/ROADMAP.md was already retargeted; the other
    # four sibling ROADMAP.md files still point at a charter header that
    # no longer exists. The direction layer's document-side artifacts
    # (docs/loom/DIRECTION.md and its hooks-side charter file) were later
    # dissolved entirely (commit 0c480079, Task 14 of
    # 2026-08-21-dissolve-direction-layer.md) — the charter now lives in
    # docs/loom/backlog/README.md, the sole live target for this pointer.
    for path in SIBLING_ROADMAPS:
        assert path.exists(), f"expected sibling roadmap missing: {path}"
        text = path.read_text(encoding="utf-8")
        assert "see its charter header" not in text, (
            f"{path} still points at the old direction-skeleton-resident "
            "charter header"
        )
        assert "docs/loom/backlog/README.md" in text, (
            f"{path}'s charter pointer must retarget to "
            "docs/loom/backlog/README.md"
        )


# Plan Task 2 (2026-08-20-north-star-serves-link.md) — the `serves:`
# frontmatter field (Task 1, committed 1fe7b2c1) is enforced in code but
# was never documented in either copy of the backlog frontmatter contract.


def test_backlog_readmes_document_serves_contract():
    # No registered REQ-ids in this plan's dispatch — @req tag omitted.
    for path in (BACKLOG_README, TEMPLATE_BACKLOG_README):
        text = path.read_text(encoding="utf-8")
        assert "bet" in text and "serves" in text, (
            f"{path} must document the serves: field alongside the bet status word"
        )
        assert "serves: unrelated" in text, (
            f"{path} must show the 'serves: unrelated — <reason>' canonical form"
        )
        assert "serves: <" in text, (
            f"{path} must show the 'serves: <non-empty text>' canonical form"
        )
        for bad in (
            "serves is required for every status",
            "serves is required for all statuses",
        ):
            assert bad not in text, (
                f"{path} must not claim serves is required for every status"
            )
        assert "docs/loom/PURPOSE.md" in text, (
            f"{path} must name docs/loom/PURPOSE.md in the serves contract"
        )
        assert "PRINCIPLES.md" not in text, (
            f"{path} must not name PRINCIPLES.md in the serves contract"
        )
        for exempt_phrase in ("is exempt", "stays optional here", "is exempt regardless of status"):
            assert exempt_phrase not in text, (
                f"{path} must not describe the no-PURPOSE.md case as exempt — "
                "it is prompted for one at betting instead"
            )


# Whole-branch review F2/F4 (2026-08-20): a fresh scaffold ships a pointer
# to `loom-code/hooks/family-reception.md` as if that path exists inside
# the CONSUMING repo. It does not — loom-code is a plugin, not a vendored
# directory. The scaffolded output (not just the template's raw text) is
# the thing that must read correctly outside this plugin repo.
#
# Round 2 (2026-08-21, DL-10): Task 11's charter rewrite dropped the
# hooks-side direction-layer charter pointer this test originally pinned
# (that file dies in Task 14 of
# docs/loom/plans/2026-08-21-dissolve-direction-layer.md).
# The concern — a scaffolded pointer must not name a bare repo-relative
# path that won't resolve outside this plugin repo — still applies, and
# the charter still carries exactly this shape for the archive script
# pointer: the template uses the `<loom-code plugin>` placeholder while
# this repo's own live instance (docs/loom/backlog/README.md, which is
# NOT scaffolded output) is free to name the bare path because loom-code
# really is vendored here. Re-pointed at that pointer.


def _stripped_blockquote(text: str) -> str:
    """Strip leading '> ' blockquote markers before normalizing, so a
    prose phrase that wraps across blockquote lines matches on its words
    alone, not the literal '>' the wrap left between them."""
    lines = [line[2:] if line.startswith("> ") else line for line in text.splitlines()]
    return _normalized("\n".join(lines))


def test_scaffolded_backlog_readme_pointer_does_not_name_an_unresolvable_repo_path(
    tmp_path,
):
    target = tmp_path / "repo"
    _scaffold_ok(target)

    readme = _normalized(
        (target / "docs" / "loom" / "backlog" / "README.md").read_text(
            encoding="utf-8"
        )
    )
    assert "loom-code/scripts/archive_change_folder.py" not in readme, (
        "scaffolded backlog README.md must not name a bare repo-relative "
        "path to the plugin's archive script — that path only resolves "
        "when loom-code happens to be vendored at that path, which is not "
        "true of every consuming repo"
    )
    assert "<loom-code plugin>/scripts/archive_change_folder.py" in readme, (
        "scaffolded backlog README.md must name the archive script pointer "
        "via the loom-code-plugin placeholder, not a repo-relative path"
    )


def test_loom_init_ok_message_lists_purpose_skeleton(tmp_path):
    # F4: loom_init.py writes docs/loom/PURPOSE.md but its success message's
    # parenthetical inventory omits it, so a reader trusting the message
    # would not know PURPOSE.md was scaffolded.
    target = tmp_path / "repo"
    result = _scaffold_ok(target)
    assert (target / "docs" / "loom" / "PURPOSE.md").is_file()
    assert "PURPOSE" in result.stdout, (
        f"loom-init OK message omits PURPOSE.md from its inventory:\n"
        f"{result.stdout}"
    )


def test_scaffolded_kickoff_defaults_onramp_comment_does_not_name_an_unresolvable_repo_path(
    tmp_path,
):
    # Same shape as F2: the On-ramp standing choices HTML comment must not
    # name the bare repo-relative hook path — that path does not exist in
    # a consuming repo.
    target = tmp_path / "repo"
    _scaffold_ok(target)

    kickoff_defaults = _stripped_blockquote(
        (target / "docs" / "loom" / "KICKOFF-DEFAULTS.md").read_text(
            encoding="utf-8"
        )
    )
    assert "owned by loom-code/hooks/family-reception.md" not in kickoff_defaults, (
        "scaffolded KICKOFF-DEFAULTS.md's on-ramp comment must not name a "
        "bare repo-relative path to the plugin's hook file"
    )
    assert "owned by the loom-code plugin's" in kickoff_defaults, (
        "scaffolded KICKOFF-DEFAULTS.md's on-ramp comment must name the "
        "pointer as the loom-code plugin's file, not a repo-relative path"
    )
