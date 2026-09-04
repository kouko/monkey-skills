"""Branch-end adversarial probes for 2026-09-03-artifact-language-policy.

Six attack classes against the wave-2 delta (origin/main..HEAD), one
attempt each, per the branch-end dispatch packet:

1. station sentences self-contradict — can a station's new language
   sentence be satisfied while naming the wrong artifact for that
   station (capture-intent must keep the intent user-language, ship must
   keep the blind-run report and PR body user-language)?
2. .codex/hooks/contract/templates/*.md mirrors diverge from the
   loom-code source, or carry CJK the source doesn't.
3. version stamps disagree across plugin.json x4 / README table /
   CHANGELOG top heading / the Codex checker's stamp line, or the sync
   script disagrees with the checked-in mirrors.
4. KICKOFF-DEFAULTS.md no longer parses for the checker, or the rule
   count drifted.
5. this branch's diff touches docs/loom/ paths outside its own
   change-id and outside docs/loom/intent/.
6. every changed SKILL.md exceeds the 4,500-word cap.

Every probe is GREEN at HEAD unless a real defect surfaced; a RED probe
is reported as a finding, not silently weakened to pass.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

# evidence/probes/test_abuse_language_policy_branch_end.py -> parents[5]
# is the repo root (probes -> evidence -> <change-id> -> loom -> docs ->
# repo root).
REPO = Path(__file__).resolve().parents[5]

CJK_RE = re.compile(r"[一-鿿　-〿＀-￯]")

STATION_SENTENCES = {
    "loom-code/skills/build/SKILL.md": {
        "must_say_english_for": ["commit messages", "probe docstrings"],
    },
    "loom-code/skills/review/SKILL.md": {
        "must_say_english_for": ["finding", "review.json"],
    },
    "loom-code/skills/ship/SKILL.md": {
        "must_say_english_for": ["memory trailers"],
        "must_keep_user_language_for": ["blind-run report", "pull-request body"],
    },
    "loom-code/skills/write-plan/SKILL.md": {
        "must_say_english_for": ["plan.md", "Current State Evidence"],
    },
    "loom-design/skills/capture-intent/SKILL.md": {
        "must_keep_user_language_for": ["intent"],
    },
    "loom-design/skills/write-spec/SKILL.md": {
        "must_say_english_for": ["spec"],
    },
}


def _resolve_base_ref() -> str:
    for ref in ("origin/main", "main"):
        result = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "--verify", ref],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return ref
    return ""


def test_ShipSentence_bothCarriersCited_userLanguageKept() -> None:
    """Attack: satisfy the ship sentence's letter while dropping one of
    the two carriers it must keep in the user's language — a reader
    under time pressure could quote only 'blind-run report' and silently
    drop 'pull-request body' from the exemption, letting a later pass
    translate the PR body unnoticed. The sentence must name both."""
    text = (REPO / "loom-code/skills/ship/SKILL.md").read_text(encoding="utf-8")
    marker = "The memory trailers and any store entry"
    idx = text.index(marker)
    window = text[idx : idx + 600]
    assert "blind-run report" in window
    assert "pull-request body" in window
    assert "user's language" in window
    # The attack: a sentence that says "stay in the user's language" but
    # only lists the PR body while the memory trailers stay English is
    # the wanted reading -- confirm the trailers/store clause is present
    # and separate from the two user-facing carriers.
    assert "memory trailers" in window
    assert "docs/loom/memory/" in window


def test_CaptureIntentSentence_translationAttempt_forbidden() -> None:
    """Attack: read the capture-intent sentence as permitting the intent
    to be translated to English later 'because everything downstream is
    English' -- the sentence must explicitly except the intent itself,
    naming it as staying in the user's language, unlike the plan/spec."""
    text = (REPO / "loom-design/skills/capture-intent/SKILL.md").read_text(encoding="utf-8")
    marker = "The intent file is the user's own words"
    idx = text.index(marker)
    window = text[idx : idx + 400]
    assert "nothing in it is" in window and "translated" in window
    assert "English being the language of the plan" in window


def test_WritePlanSentence_evidenceSection_staysEnglish() -> None:
    """Attack: exploit the plan.md sentence's carve-out for the Questions
    asked section (quoted verbatim) to also exempt the Current State
    Evidence section from English -- the sentence must scope the
    exemption to quoted user words only."""
    text = (REPO / "loom-code/skills/write-plan/SKILL.md").read_text(encoding="utf-8")
    marker = "The plan itself"
    idx = text.index(marker)
    window = text[idx : idx + 500]
    assert "Current State Evidence" in window
    assert "written in English" in window
    assert "Questions asked" in window and "copies the user's own words verbatim" in window


def test_CodexMirrors_comparedToSource_identicalAndCjkFree() -> None:
    """Attack: bypass the English-templates gate by editing only the
    loom-code source and leaving the .codex/hooks mirror stale (or
    stale-but-still-CJK) -- Codex agents read the mirror, so a diverging
    or CJK-laden mirror defeats the whole policy for that host."""
    names = ["PRINCIPLES-interview.md", "intent.md", "plan.md", "spec-minimal.md"]
    for name in names:
        src = (REPO / "loom-code/contract/templates" / name).read_bytes()
        mirror = (REPO / ".codex/hooks/contract/templates" / name).read_bytes()
        assert src == mirror, f"{name}: mirror diverges from source"
        assert not CJK_RE.search(mirror.decode("utf-8")), f"{name}: mirror carries CJK"


def test_VersionStamps_acrossAllFiles_agree() -> None:
    """Attack: bump one plugin.json's version without touching the
    README table, the CHANGELOG heading, or the Codex-side mirror --
    any single stamp left behind would silently desync the release."""
    loom_code_version = json.loads(
        (REPO / "loom-code/.claude-plugin/plugin.json").read_text(encoding="utf-8")
    )["version"]
    loom_code_codex_version = json.loads(
        (REPO / "loom-code/.codex-plugin/plugin.json").read_text(encoding="utf-8")
    )["version"]
    loom_design_version = json.loads(
        (REPO / "loom-design/.claude-plugin/plugin.json").read_text(encoding="utf-8")
    )["version"]
    loom_design_codex_version = json.loads(
        (REPO / "loom-design/.codex-plugin/plugin.json").read_text(encoding="utf-8")
    )["version"]
    assert loom_code_version == loom_code_codex_version == "1.3.0"
    assert loom_design_version == loom_design_codex_version == "1.0.4"

    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert re.search(r"\[`loom-code`\]\(loom-code/\)\s*\|\s*1\.3\.0\s*\|", readme)
    assert re.search(r"\[`loom-design`\]\(loom-design/\)\s*\|\s*1\.0\.4\s*\|", readme)

    loom_code_changelog = (REPO / "loom-code/CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [1.3.0]" in loom_code_changelog
    loom_design_changelog = (REPO / "loom-design/CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [1.0.4]" in loom_design_changelog

    checker_stamp = (REPO / ".codex/hooks/loom-checker").read_text(encoding="utf-8")
    assert "# loom-checker 1.3.0" in checker_stamp

    for plugin in ("loom-code", "loom-design"):
        result = subprocess.run(
            ["python3", str(REPO / "scripts/sync_codex_manifests.py"), "--check", plugin],
            capture_output=True,
            text=True,
            cwd=str(REPO),
        )
        assert result.returncode == 0, (
            f"{plugin}: sync_codex_manifests.py --check failed: "
            f"{result.stdout}{result.stderr}"
        )


def test_KickoffDefaults_checkerParse_ruleCountStable() -> None:
    """Attack: rewrite the docs-lint line's prose in a way that still
    reads as English but breaks the checker's frontmatter/marker parse
    of KICKOFF-DEFAULTS.md, or silently changes the rule roster size."""
    result = subprocess.run(
        [
            "python3",
            str(REPO / "loom-code/scripts/loom_checker.py"),
            "--list-rules",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert result.returncode == 0, result.stderr
    rule_lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(rule_lines) == 27

    intake_result = subprocess.run(
        [
            "python3",
            str(REPO / "loom-code/scripts/loom_checker.py"),
            "intake",
            "write-plan",
            "2026-09-03-artifact-language-policy",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert intake_result.returncode == 0, intake_result.stderr


def test_BranchDiff_docsLoomPaths_scopedToChangeId() -> None:
    """Attack: smuggle an edit to another change's docs/loom/<id>/ tree
    (or to a different change's intent file) inside this branch, hoping
    the branch-end review only samples the six SKILL.md files."""
    base_ref = _resolve_base_ref()
    if not base_ref:
        import pytest

        pytest.skip("neither origin/main nor main resolves in this tree")

    result = subprocess.run(
        ["git", "-C", str(REPO), "diff", "--name-only", f"{base_ref}..HEAD"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    touched = [line for line in result.stdout.splitlines() if line.strip()]
    docs_loom_touched = [p for p in touched if p.startswith("docs/loom/")]

    allowed_prefix = "docs/loom/2026-09-03-artifact-language-policy/"
    allowed_exact = {"docs/loom/KICKOFF-DEFAULTS.md"}
    violations = [
        p
        for p in docs_loom_touched
        if not (
            p.startswith(allowed_prefix)
            or p in allowed_exact
            or p == "docs/loom/intent/2026-09-03-artifact-language-policy.md"
        )
    ]
    assert violations == [], f"branch touches foreign docs/loom paths: {violations}"


def test_ChangedSkillFiles_wordCount_withinCap() -> None:
    """Attack: let one of the six edited SKILL.md files creep past the
    4,500-word soft cap under cover of the new language-policy sentence
    being 'just a few lines'."""
    files = [
        "loom-code/skills/build/SKILL.md",
        "loom-code/skills/review/SKILL.md",
        "loom-code/skills/ship/SKILL.md",
        "loom-code/skills/write-plan/SKILL.md",
        "loom-design/skills/capture-intent/SKILL.md",
        "loom-design/skills/write-spec/SKILL.md",
    ]
    for rel in files:
        text = (REPO / rel).read_text(encoding="utf-8")
        word_count = len(text.split())
        assert word_count <= 4500, f"{rel}: {word_count} words exceeds cap"
