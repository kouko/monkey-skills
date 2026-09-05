"""W0-01 adversary-first probes for 2026-09-03-artifact-language-policy,
written before W1-01/W1-02/W1-03/W2-01 exist. Every case is RED today
unless its docstring says GREEN; each names the task that should turn it
green (plan.md, section "Wave 1"/"Wave 2").

Policy under test (plan.md / intent.md): machine-read artifacts (spec,
plan, review records, evidence, probe comments, commits, station prose,
template comments) become English from this change forward; user-facing
artifacts (intent, the three decision-point conversations, the blind-run
report, the PR body) stay in the user's language. A violation is a `nit`,
never a blocker.

These probes pin FACTS, not verbatim wording (plan.md Risk: "probes that
grep for exact sentences over-fit the implementer's wording") — a CJK
count of zero, a sentence naming both "English" and the station's own
artifact noun, an EARS keyword at the head of the REQ example body line,
a compound clause in reviewer.md that is outside the docs-lint carve-out.

Word counts, if ever needed, always use `len(str.split())` — never `wc`
(BSD/GNU disagree; documented gotcha from a prior change in this repo).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

# evidence/probes/test_abuse_language_policy.py -> parents[2] is the repo
# root (scripts -> loom-code -> repo root). Graduated byte copy; only the path lines differ.
REPO = Path(__file__).resolve().parents[2]

TEMPLATES_DIR = REPO / "loom-code/contract/templates"

STATION_FILES = {
    "write-plan": (REPO / "loom-code/skills/write-plan/SKILL.md", {"plan"}),
    "build": (REPO / "loom-code/skills/build/SKILL.md", {"plan", "probe", "commit", "spec"}),
    "review": (REPO / "loom-code/skills/review/SKILL.md", {"review.json", "findings", "evidence", "probe"}),
    "ship": (REPO / "loom-code/skills/ship/SKILL.md", {"pr body", "commit", "report"}),
    "capture-intent": (REPO / "loom-design/skills/capture-intent/SKILL.md", {"intent"}),
    "write-spec": (REPO / "loom-design/skills/write-spec/SKILL.md", {"spec"}),
}

REVIEWER_MD = REPO / "loom-code/agents/reviewer.md"
ADVERSARY_MD = REPO / "loom-code/agents/adversary.md"
BLIND_RUNNER_MD = REPO / "loom-code/agents/blind-runner.md"
SPEC_MINIMAL_MD = TEMPLATES_DIR / "spec-minimal.md"
LOOM_CHECKER = REPO / "loom-code/scripts/loom_checker.py"

CJK_RANGE = re.compile(r"[一-鿿]")

EARS_HEAD = re.compile(
    r"^\s*(WHEN\b|WHILE\b|WHERE\b|IF\b.*\bTHEN\b|The\s+\S+.*\bshall\b)",
    re.IGNORECASE,
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _sentences(text: str) -> list[str]:
    """Loose sentence splitter — good enough to locate one sentence that
    names both a keyword and a noun; not the sentence-cap oracle from the
    positioning-cap change (no cap arithmetic is asserted here)."""
    flat = " ".join(text.split())
    return [p for p in _SENTENCE_SPLIT.split(flat) if p.strip()]


# --- (a) templates carry zero CJK characters --------------------------------


def _template_files():
    files = sorted(TEMPLATES_DIR.glob("*.md")) + sorted(TEMPLATES_DIR.glob("*.json"))
    assert len(files) == 8, f"expected 8 template files, found {len(files)}: {files}"
    return files


import pytest  # noqa: E402  (after helper defs, matches worked-example order)


@pytest.mark.parametrize("path", _template_files(), ids=lambda p: p.name)
def test_templates_cjk_absent(path: Path):
    """Attack: every file directly under loom-code/contract/templates/ must
    have zero CJK (U+4E00-U+9FFF) characters once the policy lands. RED
    today (at W0-01) on intent.md (76 CJK chars), plan.md (112),
    spec-minimal.md (141), PRINCIPLES-interview.md (200) — each carries CJK
    field comments; already GREEN today on KICKOFF-DEFAULTS.md,
    memory-README.md, PURPOSE.md, review.json (already English/JSON-only).
    Turns fully GREEN at W1-01, which translates the four RED files — this
    test asserts only the desired end state, so it turns GREEN on its own
    once W1-01 lands, with no change needed here."""
    text = path.read_text(encoding="utf-8")
    hits = CJK_RANGE.findall(text)
    assert not hits, (
        f"{path.name} still has {len(hits)} CJK character(s): "
        f"{''.join(hits[:10])!r}"
    )


# --- (b) each station names English + its own artifact in one sentence -----


@pytest.mark.parametrize("station", sorted(STATION_FILES), ids=sorted(STATION_FILES))
def test_stations_english_absent(station: str):
    """Attack: each of the six station SKILL.md files must contain a
    sentence naming "English" together with at least one internal artifact
    noun that station owns. RED today for all six — none of them mention
    "English" at all (grep confirmed empty across all six files). Turns
    GREEN at W2-01."""
    path, nouns = STATION_FILES[station]
    text = path.read_text(encoding="utf-8")
    sentences = _sentences(text)
    hits = [
        s for s in sentences
        if "english" in s.lower() and any(n.lower() in s.lower() for n in nouns)
    ]
    assert hits, (
        f"{path.name} has no sentence naming English together with one of "
        f"{sorted(nouns)} — 'English' does not appear in the file at all"
    )


# --- (c) reviewer.md's language/shape nit clause, outside docs-lint --------


def test_reviewer_nitclause_absent():
    """Attack: reviewer.md must carry one clause that (i) mentions
    English, (ii) mentions EARS or SHALL, (iii) mentions "Conventional
    Comments" or a label list, (iv) says nit, and (v) sits outside the
    docs-lint carve-out (stating the rule holds "regardless" of docs-lint).
    Also assert the carve-out paragraph itself still exists, so the clause
    is provably a *second*, separate paragraph, not folded into the
    carve-out's own scope. RED today — reviewer.md contains none of
    "English", "EARS", "shall", or "Conventional Comments" anywhere (grep
    confirmed). GREEN target: W1-02."""
    text = REVIEWER_MD.read_text(encoding="utf-8")

    assert "docs-lint" in text, "docs-lint carve-out heading text is missing"
    assert "style is out of scope" in text, (
        "docs-lint carve-out paragraph (style out of scope) is missing or reworded"
    )

    blocks = [b for b in text.split("\n\n") if b.strip()]
    lower_blocks = [b.lower() for b in blocks]

    facts = {
        "english": any("english" in b for b in lower_blocks),
        "ears_or_shall": any("ears" in b or "shall" in b for b in lower_blocks),
        "conventional_or_label": any(
            "conventional comments" in b or "label" in b for b in lower_blocks
        ),
        "nit": any("nit" in b for b in lower_blocks),
        "regardless": any("regardless" in b for b in lower_blocks),
    }
    missing = [k for k, present in facts.items() if not present]
    assert not missing, (
        f"reviewer.md is missing these required facts anywhere in the "
        f"document: {missing}"
    )

    compound_hits = [
        b for b in lower_blocks
        if "english" in b
        and ("ears" in b or "shall" in b)
        and ("conventional comments" in b or "label" in b)
        and "nit" in b
        and "regardless" in b
    ]
    assert compound_hits, (
        "no single paragraph in reviewer.md combines English + EARS/shall + "
        "Conventional-Comments/label + nit + 'regardless' (the docs-lint- "
        "independence marker) — each fact was checked in isolation above "
        "and at least the compound co-location is missing"
    )


# --- (d) spec-minimal.md REQ example body line is in EARS form -------------


def test_specminimal_ears_absent():
    """Attack: the REQ-1 example body line (the line right after
    `REQ-1 — <name>`) must open with one of the five EARS keyword forms
    (WHEN / WHILE / WHERE / IF...THEN / "The <system> shall") and keep the
    `→ Acceptance #<n>` suffix. RED today — the body line is
    `<一句可驗的義務> → Acceptance #<n>` (Chinese placeholder, no EARS
    keyword). GREEN target: W1-01."""
    text = SPEC_MINIMAL_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    label_idx = next(
        (i for i, l in enumerate(lines) if l.strip().startswith("REQ-1")), None
    )
    assert label_idx is not None, "REQ-1 — <name> label line not found in spec-minimal.md"
    assert label_idx + 1 < len(lines), "no body line follows the REQ-1 label"
    body = lines[label_idx + 1]

    assert "→ Acceptance #" in body, (
        f"REQ example body line lost the '→ Acceptance #<n>' suffix: {body!r}"
    )
    assert EARS_HEAD.match(body.strip()), (
        f"REQ example body line does not open with an EARS keyword "
        f"(WHEN/WHILE/WHERE/IF...THEN/shall): {body!r}"
    )


# --- (e) adversary.md / blind-runner.md name the probe-name shape ----------

_SHAPE_LITERAL = "test_<unit>_<state>_<expected>"

# Round-2 finding (rev-we1-codex, wave-end:1-03): a paragraph that merely
# co-locates the literal shape string with the word "English" is not
# discriminating — it would also accept a paragraph that FORBIDS the shape
# ("probes are never named `test_<unit>_<state>_<expected>`") as long as
# "English" appears somewhere else in it. The fix moves the check from
# paragraph-level substring co-location to sentence-level semantics: the
# sentence naming the shape must affirmatively name it (a naming verb
# BEFORE the literal, no negation anywhere in that sentence), and some
# sentence in the same paragraph must affirmatively require English (an
# "in English" form, no negation anywhere in that sentence) — the two
# checks may land on the same sentence (adversary.md) or different
# sentences of the same paragraph.
_NAMING_VERB_PHRASES = ("must be named", "is named", "name is", "named")
_ENGLISH_AFFIRM_PHRASES = ("is in english", "are in english", "in english")
# Word-boundary regex, not naive substring: "not"/"no" as plain substrings
# false-positive inside ordinary words (e.g. "note" contains "not",
# "know" contains "no") — verified against adversary.md's real sentence,
# which says "evidence note" and must NOT be flagged as negated.
_NEGATION_RE = re.compile(r"\b(?:not|never|no)\b|n't", re.IGNORECASE)


def _has_negation(sentence: str) -> bool:
    return bool(_NEGATION_RE.search(sentence))


def _sentence_affirmatively_names_shape(sentence: str) -> bool:
    """True iff `sentence` contains the literal shape string, a naming-verb
    phrase strictly BEFORE that literal, and no negation token anywhere in
    the sentence."""
    idx = sentence.find(_SHAPE_LITERAL)
    if idx == -1:
        return False
    prefix = sentence[:idx].lower()
    if not any(phrase in prefix for phrase in _NAMING_VERB_PHRASES):
        return False
    return not _has_negation(sentence)


def _sentence_affirmatively_requires_english(sentence: str) -> bool:
    lowered = sentence.lower()
    if not any(phrase in lowered for phrase in _ENGLISH_AFFIRM_PHRASES):
        return False
    return not _has_negation(sentence)


def _paragraph_names_shape_and_requires_english(paragraph: str) -> bool:
    sentences = _sentences(paragraph)
    if not any(_sentence_affirmatively_names_shape(s) for s in sentences):
        return False
    return any(_sentence_affirmatively_requires_english(s) for s in sentences)


@pytest.mark.parametrize("agent_path", [ADVERSARY_MD, BLIND_RUNNER_MD], ids=lambda p: p.name)
def test_agents_probename_absent(agent_path: Path):
    """Attack: both adversary.md and blind-runner.md must carry a paragraph
    in which one sentence affirmatively NAMES the probe shape (a naming
    verb — named/is named/must be named/name is — before the literal
    `test_<unit>_<state>_<expected>`, with no negation anywhere in that
    sentence), and some sentence in the same paragraph affirmatively
    requires English for docstrings/evidence (an "in English" form, no
    negation). This rejects a paragraph that merely co-locates the literal
    with the word "English" regardless of polarity (round-2 finding,
    rev-we1-codex: such a paragraph could say the shape is FORBIDDEN and
    still pass the looser check). RED today unless both files already
    satisfy the affirmative, un-negated form. GREEN target: W1-03."""
    text = agent_path.read_text(encoding="utf-8")
    assert _SHAPE_LITERAL in text, (
        f"{agent_path.name} does not contain the literal string {_SHAPE_LITERAL!r}"
    )

    blocks = [b for b in text.split("\n\n") if b.strip()]
    shape_paragraphs = [b for b in blocks if _SHAPE_LITERAL in b]
    assert shape_paragraphs, (
        f"{agent_path.name} has the literal shape string but it is not "
        "inside any paragraph (blank-line-delimited block)"
    )

    qualifying = [b for b in shape_paragraphs if _paragraph_names_shape_and_requires_english(b)]
    assert qualifying, (
        f"{agent_path.name}: no paragraph has both a sentence that "
        f"affirmatively names {_SHAPE_LITERAL!r} (naming verb before the "
        "literal, no negation) and a sentence that affirmatively requires "
        "English for docstrings/evidence (no negation)"
    )


def test_ProbenameHelper_SyntheticParagraphs_Discriminates():
    """Attack: pin the discriminating power of
    `_paragraph_names_shape_and_requires_english` itself with three
    synthetic paragraphs, independent of any real agent file — the round-2
    finding was that the OLD check could not tell an affirmative naming
    sentence from a forbidding one. GREEN now: all three cases already
    hold against the current helper."""
    real_adversary_sentence = (
        "Every probe function is named `test_<unit>_<state>_<expected>` — "
        "three underscore-separated parts (unit of work, state under test, "
        "expected behaviour) — and its docstring, and any evidence note "
        "you write, is in English."
    )
    assert _paragraph_names_shape_and_requires_english(real_adversary_sentence), (
        "the real adversary.md naming sentence must pass"
    )

    negated_paragraph = (
        "Probes are never named `test_<unit>_<state>_<expected>`; "
        "docstrings are in English."
    )
    assert not _paragraph_names_shape_and_requires_english(negated_paragraph), (
        "a paragraph that forbids the shape must not pass just because "
        "'in English' appears elsewhere in it"
    )

    literal_no_naming_verb = (
        "The string `test_<unit>_<state>_<expected>` appears in the docs. "
        "Docstrings are in English."
    )
    assert not _paragraph_names_shape_and_requires_english(literal_no_naming_verb), (
        "a paragraph with the literal but no naming verb before it must not pass"
    )


# --- (f) GREEN pin: --list-rules line count ---------------------------------


def test_checker_rulecount_pinned():
    """GREEN pin: `loom_checker.py --list-rules`, resolved inside REPO (not
    the installed plugin cache), prints exactly 27 lines today. A
    regression here means the checker's rule surface moved without this
    change touching it, which is out of scope."""
    assert LOOM_CHECKER.is_file(), f"loom_checker.py not found at {LOOM_CHECKER}"
    result = subprocess.run(
        ["python3", str(LOOM_CHECKER), "--list-rules"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    lines = [l for l in result.stdout.splitlines() if l.strip() != ""]
    assert result.returncode == 0, (
        f"loom_checker.py --list-rules exited {result.returncode}: {result.stderr}"
    )
    assert len(lines) == 27, (
        f"--list-rules printed {len(lines)} non-empty lines, expected 27:\n"
        + "\n".join(lines)
    )


# --- (g) GREEN pin: branch diff stays scoped to this change's own paths ----


def _resolve_base_ref() -> str | None:
    for ref in ("origin/main", "main"):
        probe = subprocess.run(
            ["git", "rev-parse", "--verify", ref],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        if probe.returncode == 0:
            return ref
    return None


def test_branchdiff_scope_clean():
    """GREEN pin: `git diff --name-only <merge-base>..HEAD` must touch no
    path under docs/loom/2026-09-0*/ or docs/loom/intent/ other than one
    containing "2026-09-03-artifact-language-policy". Prefers
    `origin/main` over local `main` — local `main` in this worktree is
    stale (missing 4e459ed0), so a merge-base against it would falsely
    pull in two other already-landed changes' doc paths; `origin/main` is
    caught up and gives the clean, expected diff. Skips (does not fail) if
    neither ref resolves, per the task guard."""
    base_ref = _resolve_base_ref()
    if base_ref is None:
        pytest.skip("neither origin/main nor main resolves in this checkout")

    merge_base = subprocess.run(
        ["git", "merge-base", base_ref, "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    diff = subprocess.run(
        ["git", "diff", "--name-only", f"{merge_base}..HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()

    own_marker = "2026-09-03-artifact-language-policy"
    offenders = [
        p for p in diff
        if (p.startswith("docs/loom/2026-09-0") or p.startswith("docs/loom/intent/"))
        and own_marker not in p
    ]
    assert not offenders, (
        f"branch diff against {base_ref} (merge-base {merge_base[:7]}) touches "
        f"docs/loom paths outside this change: {offenders}"
    )


# --- (h) hidden CJK inside a code span / HTML comment must still count -----


def test_cjkdetector_hidden_caught():
    """Attack (attack-catalogue "forge an artifact" class, adapted to a
    text policy): a CJK character hidden inside a backtick code span or an
    HTML comment inside a template must still be caught by the same
    zero-CJK detector used in probe (a) — a naive implementer might strip
    code spans/comments before scanning (as the sentence-cap oracle in a
    prior change deliberately does for a different purpose) and thereby
    launder a leftover CJK field name past the check. Synthetic string
    only — does not touch any real repo file. GREEN now: this documents
    that CJK_RANGE, used unmodified in probe (a), has no such blind spot
    (it is a raw char-class scan with no code-span/comment stripping)."""
    poisoned = (
        "## Field\n"
        "some english text `欄位: value` more english\n"
        "<!-- 隱藏中文註解 -->\n"
        "rest of the paragraph in english.\n"
    )
    hits = CJK_RANGE.findall(poisoned)
    assert hits, "CJK hidden in a code span and an HTML comment went undetected"
    assert len(hits) >= 6, f"expected to catch all hidden CJK chars, got {hits!r}"
