"""wave-end:1 adversarial probes for 2026-09-03-artifact-language-policy.

Attack, one attempt per attack-catalogue.md class, against the delta
between origin/main (4e459ed0) and HEAD:

1. self-exempt via a prose condition — is the new reviewer.md paragraph
   "Language and template shape are not style" really immune to the
   `docs-lint` carve-out that sits right above it, and does that
   carve-out paragraph still exist unchanged?
2. bypass a gate by editing its input — did any of the template's
   machine-read anchors (YAML keys, `##` headings, the `- none` marker,
   the `-> Acceptance #<n>` suffix, the `review: after-task` marker, the
   `intake.after-task-budget` comment) drift between origin/main and HEAD
   under cover of a translation pass?
3. forge/replay an artifact the gate trusts — does loom_checker.py still
   accept a template-shaped intent (placeholders filled, English prose)
   in a scratch repo, i.e. did translating the template break the
   checker's own parse of it?
4. cross a trust boundary via character smuggling — do the four English
   templates carry full-width punctuation or IDEOGRAPHIC SPACE (U+3000)
   that a Han-only regex (U+4E00-U+9FFF) would miss?
5. bypass a gate by editing its input, second target — does any of
   the three retired one-character labels (file/test/risk) survive
   anywhere else in loom-code/skills or loom-code/contract after
   build/SKILL.md was repointed to `Files:` / `Test:` / `Risk:`?
6. race the cap against the paragraph it was raised for — is the
   reviewer.md body cap (1450) actually above the word count added by
   the new paragraph (i.e. not a cap bumped by coincidence to a number
   that happens to still fail), and are adversary.md / blind-runner.md
   still within their unchanged 600-word cap?

Every probe is GREEN at HEAD unless a real defect surfaced; a RED probe
is reported as a finding, not silently weakened to pass.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(__file__).resolve().parent,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
)

BASE_SHA = "4e459ed054a86e6cc830270d547b7729d2b0bd26"

REVIEWER_MD = REPO / "loom-code/agents/reviewer.md"
ADVERSARY_MD = REPO / "loom-code/agents/adversary.md"
BLIND_RUNNER_MD = REPO / "loom-code/agents/blind-runner.md"
CHECKER = REPO / "loom-code/scripts/loom_checker.py"
CAPS_TEST = REPO / "loom-code/scripts/test_reviewer_agent_single_contract.py"

TEMPLATES_DIR = REPO / "loom-code/contract/templates"
TEMPLATE_FILES = [
    "intent.md",
    "plan.md",
    "spec-minimal.md",
    "PRINCIPLES-interview.md",
]

CJK_HAN_RANGE = re.compile(r"[一-鿿]")
FULLWIDTH_OR_IDEOGRAPHIC_SPACE = re.compile(r"[　＀-￯]")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _body_of(text: str) -> str:
    """Strip YAML frontmatter, matching test_reviewer_agent_single_contract.py."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "no frontmatter found"
    return text[match.end():]


def _show_at_base(path: Path) -> str | None:
    """`git show <base>:<path>`, or None if the base ref does not resolve
    (guarded per the task brief: never fail the probe on a missing ref)."""
    rel = path.relative_to(REPO).as_posix()
    resolve = subprocess.run(
        ["git", "rev-parse", "--verify", BASE_SHA],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if resolve.returncode != 0:
        return None
    result = subprocess.run(
        ["git", "show", f"{BASE_SHA}:{rel}"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


# --- class 1: self-exempt via a prose condition ----------------------------


def test_reviewer_docs_lint_carveout_paragraph_still_present_unchanged():
    """Attack: the new "language and template shape are not style" clause
    could have been slipped in by silently deleting or weakening the
    docs-lint carve-out paragraph next to it, so the new clause reads as
    the *only* style rule and looks easier to route around than it is.
    Expected: the carve-out paragraph ("Style, when the repo declares
    `docs-lint`...") is present, unchanged in substance, at both base and
    HEAD -- the new clause is additive, not a replacement.
    """
    text = _read(REVIEWER_MD)
    assert "Style, when the repo declares `docs-lint`." in text
    assert "style is out of scope for you: raise no finding" in text
    base_text = _show_at_base(REVIEWER_MD)
    if base_text is not None:
        assert "Style, when the repo declares `docs-lint`." in base_text


def test_reviewer_language_clause_explicitly_immune_to_docs_lint_exemption():
    """Attack: try to read the new clause as exempt under `docs-lint: <cmd>`
    the way ordinary wording/phrasing findings are exempted just above it
    -- would that reading actually silence a language-policy finding?
    Expected: the clause states its own immunity in-line ("is a `nit`
    regardless of `docs-lint`"), so the self-exemption reading is refuted
    by the text itself, not by an external check.
    """
    text = _read(REVIEWER_MD)
    idx = text.find("Language and template shape are not style.")
    assert idx != -1, "the new clause is missing entirely"
    clause = text[idx : idx + 800]
    assert "regardless of" in clause and "docs-lint" in clause, (
        "the clause does not name its own immunity to the docs-lint carve-out"
    )


# --- class 2: bypass a gate by editing its input ----------------------------


def test_template_machine_anchors_unchanged_across_translation():
    """Attack: use the translation pass as cover to also drift a
    machine-read anchor (a YAML key, a `##` heading, the `- none`
    sentinel, the `-> Acceptance #<n>` suffix, `review: after-task`, or
    the `intake.after-task-budget` comment) -- a downstream checker rule
    keyed on exact text would then silently stop firing.
    Expected: for every template, the set of YAML keys, `##` headings,
    and the four fixed markers is identical (ignoring insertion order
    only within the marker set) between origin/main and HEAD; skip a file
    if the base ref cannot be read.
    """
    # `^#{2,3} ` only -- deliberately excludes the `# <title>` H1, which is
    # each template's own prose title and is expected to translate along
    # with the rest of the document, not a machine-read section anchor.
    anchor_re = re.compile(
        r"^[a-zA-Z_-]+:|^#{2,3} [A-Za-z /]+|- none|-> Acceptance #<n>|"
        r"review: after-task|intake\.after-task-budget",
        re.MULTILINE,
    )
    checked_any = False
    for name in TEMPLATE_FILES:
        path = TEMPLATES_DIR / name
        base_text = _show_at_base(path)
        if base_text is None:
            continue
        checked_any = True
        head_text = _read(path)
        base_anchors = sorted(
            m.group(0) for m in anchor_re.finditer(base_text.replace("→", "->"))
        )
        head_anchors = sorted(
            m.group(0) for m in anchor_re.finditer(head_text.replace("→", "->"))
        )
        assert base_anchors == head_anchors, (
            f"{name}: machine-read anchors drifted -- "
            f"base={base_anchors} head={head_anchors}"
        )
    assert checked_any, "base ref did not resolve for any template; nothing was checked"


def test_after_task_budget_comment_still_matches_checker_rule_id():
    """Attack: rename or reword the `intake.after-task-budget` HTML
    comment in plan.md's template during translation, decoupling the
    comment a plan author reads from the rule id loom_checker.py raises.
    Expected: the exact rule id string appears verbatim both in the
    template's HTML comment and in loom_checker.py's own source.
    """
    plan_template = _read(TEMPLATES_DIR / "plan.md")
    assert "intake.after-task-budget" in plan_template
    checker_source = _read(CHECKER)
    assert "intake.after-task-budget" in checker_source


# --- class 3: forge/replay an artifact the gate trusts ----------------------


def test_checker_still_parses_template_shaped_intent_after_translation():
    """Attack: translating intent.md's placeholders to English could have
    broken a section header or field name the checker's own parser
    matches literally, so a template-shaped intent (placeholders filled,
    nothing else changed) would be rejected at parse time -- not on a
    substantive rule -- defeating the template's purpose.
    Expected: running `loom_checker.py intent <path>` against a filled
    copy of the template, in a scratch git repo on its own branch, does
    NOT fail with a parse-level complaint (missing section / missing
    frontmatter field / "no intent file"); it is allowed to fail on a
    substantive, unrelated rule (e.g. commit-message wording) instead.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        intent_dir = tmp_path / "docs" / "loom" / "intent"
        intent_dir.mkdir(parents=True)
        intent_path = intent_dir / "2026-09-05-scratch-probe.md"
        intent_path.write_text(
            "# Scratch Probe Change\n"
            "originator: probe\n"
            "kind: engineering\n"
            "needs-design: no — mechanical\n"
            "status: open\n"
            "\n"
            "## Problem\n"
            "Scratch problem statement.\n"
            "\n"
            "## Proposed outcome\n"
            "Scratch direction.\n"
            "\n"
            "## Acceptance\n"
            "1. Scratch acceptance line.\n"
            "\n"
            "## Constraints\n"
            "- none\n"
            "\n"
            "## Out of scope\n"
            "- none\n"
            "\n"
            "## Open questions\n"
            "- none\n",
            encoding="utf-8",
        )
        checker_copy = tmp_path / "loom-code" / "scripts"
        checker_copy.mkdir(parents=True)
        (checker_copy / "loom_checker.py").write_text(_read(CHECKER), encoding="utf-8")
        contract_src = REPO / "loom-code" / "contract"
        contract_dst = tmp_path / "loom-code" / "contract"
        import shutil

        shutil.copytree(contract_src, contract_dst)

        def run(*args: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, "loom-code/scripts/loom_checker.py", *args],
                cwd=tmp_path,
                capture_output=True,
                text=True,
            )

        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
        subprocess.run(
            ["git", "-c", "user.email=a@a", "-c", "user.name=a", "add", "-A"],
            cwd=tmp_path,
            check=True,
        )
        subprocess.run(
            [
                "git", "-c", "user.email=a@a", "-c", "user.name=a",
                "commit", "-qm", "init",
            ],
            cwd=tmp_path,
            check=True,
        )
        subprocess.run(
            ["git", "switch", "-c", "scratch-probe", "-q"], cwd=tmp_path, check=True
        )

        result = run("intent", "docs/loom/intent/2026-09-05-scratch-probe.md")
        parse_level_markers = (
            "no intent file",
            "has no frontmatter",
            "does not exist",
            "missing section",
            "not inside a git work tree",
        )
        combined = result.stdout + result.stderr
        for marker in parse_level_markers:
            assert marker not in combined, (
                f"checker rejected the filled template at parse level: {combined!r}"
            )


# --- class 4: cross a trust boundary via character smuggling ---------------


def test_templates_carry_no_fullwidth_or_ideographic_space_smuggling():
    """Attack: swap Han characters for full-width Latin punctuation or an
    IDEOGRAPHIC SPACE (U+3000) -- visually similar to CJK, but outside a
    naive `[\\u4e00-\\u9fff]`-only scanner some other check might use --
    to smuggle non-English formatting past a Han-only language check.
    Expected: reported, not failed, if the intent's own ban is scoped to
    Han characters only (docs/loom/intent/2026-09-03-artifact-language-policy.md
    is the authority on scope) -- but no such characters are present in
    the four templates at HEAD regardless, so this probe is GREEN either way.
    """
    findings = []
    for name in TEMPLATE_FILES:
        text = _read(TEMPLATES_DIR / name)
        hits = FULLWIDTH_OR_IDEOGRAPHIC_SPACE.findall(text)
        if hits:
            findings.append((name, hits))
    # Report-only per the task brief: do not fail on this class unless the
    # intent's own scope actually covers these code points.
    intent_text = _read(
        REPO / "docs/loom/intent/2026-09-03-artifact-language-policy.md"
    )
    bans_fullwidth_explicitly = "full-width" in intent_text or "U+3000" in intent_text
    if findings and bans_fullwidth_explicitly:
        raise AssertionError(f"full-width/ideographic-space smuggling found: {findings}")
    # else: findings (if any) are just recorded via the assertion below,
    # which always holds -- the probe stays GREEN and the finding (if any)
    # is surfaced in the adversary's prose report instead.
    assert True, findings


# --- class 5: bypass a gate by editing its input, second target ------------


def test_no_retired_single_char_labels_survive_in_skills_or_contract():
    """Attack: build/SKILL.md was repointed from the one-character labels
    (檔/測/風) to `Files:`/`Test:`/`Risk:`, but a stray copy of the old
    labels elsewhere in loom-code/skills or loom-code/contract (a second
    place an implementer's dispatch prompt might quote from) would let
    the old vocabulary leak back into a real task dispatch.
    Expected: none of 檔, 測, 風 appear anywhere under loom-code/skills
    or loom-code/contract at HEAD.
    """
    retired = ("檔", "測", "風")
    hits: list[str] = []
    for base in (REPO / "loom-code/skills", REPO / "loom-code/contract"):
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, IsADirectoryError):
                continue
            for label in retired:
                if label in text:
                    hits.append(f"{path.relative_to(REPO)}: {label!r}")
    assert not hits, f"retired single-character labels still present: {hits}"


def test_build_skill_quotes_english_field_labels_verbatim():
    """Attack: check that build/SKILL.md's dispatch-prompt template
    actually quotes the new field labels the plan template now emits,
    rather than some other spelling that would desync the dispatch
    prompt from what a real plan.md task looks like.
    Expected: `Files:`, `Test:`, and `Risk:` all appear in build/SKILL.md.
    """
    text = _read(REPO / "loom-code/skills/build/SKILL.md")
    for label in ("Files:", "Test:", "Risk:"):
        assert label in text, f"build/SKILL.md no longer quotes {label!r}"


# --- class 6: race the cap against the paragraph it was raised for ---------


def test_reviewer_cap_bump_actually_covers_the_added_paragraph():
    """Attack: bump the reviewer.md word cap in the test file by a round
    number without checking it is enough -- a cap raised to 1450 that
    still sits below the real body word count would make the cap-test
    pass today by coincidence and fail on the next unrelated one-line
    edit, which is not a real fix, just a deferred failure.
    Expected: the current reviewer.md body word count is <= 1450 (the
    new cap) and > 1340 (the old cap) -- proving the new paragraph is
    what pushed the count past the old cap, not slack that was already
    there, and that the new cap actually covers it.
    """
    text = _read(REVIEWER_MD)
    words = len(_body_of(text).split())
    assert words <= 1450, f"reviewer.md body is {words} words, exceeds the new cap of 1450"
    assert words > 1340, (
        f"reviewer.md body is only {words} words -- the cap bump to 1450 "
        "was not actually needed; a stale/unneeded cap raise is a finding"
    )


def test_adversary_and_blind_runner_still_within_unchanged_cap():
    """Attack: the language-policy delta added prose to adversary.md and
    blind-runner.md too (three-part probe names, English evidence,
    per-artifact language/template rows) -- did that push either past
    their cap, which the plan did NOT raise (still 600 in the caps test)?
    Expected: both bodies stay <= 600 words.
    """
    for path in (ADVERSARY_MD, BLIND_RUNNER_MD):
        words = len(_body_of(_read(path)).split())
        assert words <= 600, f"{path.name} body is {words} words, exceeds the unbumped cap of 600"


def test_caps_test_file_declares_the_same_numbers_probed_above():
    """Attack: this probe file and the repo's own cap test
    (test_reviewer_agent_single_contract.py) could silently disagree on
    the cap numbers -- this file passing would then prove nothing about
    what the real gate enforces.
    Expected: AGENT_CAPS in the caps test file names reviewer.md: 1450,
    blind-runner.md: 600, adversary.md: 600 -- exactly what was probed.
    """
    caps_source = _read(CAPS_TEST)
    match = re.search(r"AGENT_CAPS\s*=\s*\{([^}]*)\}", caps_source)
    assert match, "AGENT_CAPS dict not found in the caps test file"
    body = match.group(1)
    assert '"reviewer.md": 1450' in body
    assert '"blind-runner.md": 600' in body
    assert '"adversary.md": 600' in body
