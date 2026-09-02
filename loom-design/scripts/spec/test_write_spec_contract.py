"""write-spec station contract (plan W2-02).

write-spec turns a confirmed intent into `docs/loom/<change-id>/spec.md`
(concept-model §2c), runs decision point ② for product changes, and hands
the spec to loom-code's review station under the spec lens before a plan
exists. These tests pin the cross-plugin invariants a cold reader depends
on and the shapes the contract package owns.

The REQ identifier grammar is READ from `loom-code/contract/manifest.yaml`
rather than restated here: the manifest is the single declaration of the
spec schema (concept-model §11), and a second copy of the grammar in a
loom-design test would be a second drift surface.

Reading loom-code's files from a loom-design TEST is deliberate, exactly
as in `test_capture_intent_contract.py`: the ban on cross-plugin
references is a RUNTIME portability rule for prose contracts. A test runs
in this repository, where both plugins are checked out side by side.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
SKILL = REPO / "loom-design/skills/write-spec/SKILL.md"
CAPTURE_INTENT = REPO / "loom-design/skills/capture-intent/SKILL.md"
WRITE_PLAN = REPO / "loom-code/skills/write-plan/SKILL.md"
MANIFEST = REPO / "loom-code/contract/manifest.yaml"
CHECKER = REPO / "loom-code/scripts/loom_checker.py"
MECHANISMS = REPO / "docs/loom/evidence/mechanisms.yaml"

WORD_CAP = 3500
DESCRIPTION_CAP = 400
SPEC_FORMS_CAP = 900
UI_FLOWS_CAP = 700

# Vocabulary the redesign deletes (concept-model §10) plus the two terms
# this station's own predecessors carried (`expansion`, and the critic
# provenance tags). A station written after the cut reintroduces none.
DELETED_VOCABULARY = (
    "brief",
    "seed",
    "pipeline",
    "conductor",
    "batch",
    "waiver",
    "critic",
    "critic-found",
    "provenance-tagged",
    "expansion",
)

GATE_IDS = (
    "write-spec.product-visible-behaviour-confirmed-before-review",
    "write-spec.no-design-decision-shown-to-user",
)

# UI flow 2 (spec.md): the fixed sentence decision point ② is asked with.
UI_FLOW_2_SENTENCE = "你下 ___ 會看到 ___；___ 的情況會 ___。對嗎？"


def _text() -> str:
    return SKILL.read_text(encoding="utf-8")


def _body(text: str) -> str:
    """The SKILL.md body, frontmatter stripped."""
    parts = text.split("---\n", 2)
    return parts[2] if len(parts) == 3 else text


def _section(text: str, heading: str) -> str:
    m = re.search(rf"^{re.escape(heading)}$.*?(?=^## |\Z)", text, re.M | re.S)
    assert m, f"section {heading!r} missing"
    return m.group(0)


@lru_cache(maxsize=1)
def _checker_usage() -> str:
    """The checker's own usage block — its list of sub-commands."""
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--help"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    return proc.stdout + proc.stderr


@lru_cache(maxsize=1)
def _checker_rule_ids() -> frozenset[str]:
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--list-rules"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert proc.returncode == 0, proc.stderr
    return frozenset(
        line.split("\t", 1)[0].strip()
        for line in proc.stdout.splitlines()
        if line.strip()
    )


def _requirements_grammar() -> str:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    fields = manifest["artifacts"]["spec"]["fields"]
    for field in fields:
        if field["name"] == "Requirements":
            return field["grammar"]
    raise AssertionError("manifest declares no Requirements grammar for spec")


def _grammar_to_regex(grammar: str) -> re.Pattern[str]:
    """Turn the manifest's grammar string into a matcher.

    `<n>` is a number, `<name>` and `…` are free text; everything else —
    the literal `REQ-`, the em dash, the arrow, `Acceptance #` — is
    matched character for character, so a station that writes `REQ1` or
    drops the back-reference fails here.
    """
    pattern = ""
    for token in re.split(r"(<n>|<name>|…)", grammar):
        if token == "<n>":
            pattern += r"\d+"
        elif token == "<name>":
            pattern += r"[^\n]+?"
        elif token == "…":
            pattern += r"[\s\S]+?"
        else:
            pattern += re.escape(token)
    return re.compile(pattern)


def test_skill_file_exists() -> None:
    assert SKILL.is_file(), f"{SKILL} does not exist"


def test_frontmatter_name_and_version() -> None:
    text = _text()
    assert re.search(r"^name: write-spec$", text, re.M)
    assert re.search(r"^version: 1\.0\.0$", text, re.M)


def test_description_within_cap() -> None:
    m = re.search(r"^description: \|\n((?:  .*\n)+)", _text(), re.M)
    assert m, "description must be a block scalar"
    description = " ".join(line.strip() for line in m.group(1).splitlines())
    assert len(description) <= DESCRIPTION_CAP, len(description)


def test_body_within_word_cap() -> None:
    words = len(_body(_text()).split())
    assert words <= WORD_CAP, words


def test_station_summary_is_byte_identical_to_write_plan() -> None:
    ours = _section(_text(), "## Station summary")
    theirs = _section(WRITE_PLAN.read_text(encoding="utf-8"), "## Station summary")
    assert ours == theirs


def test_station_summary_is_byte_identical_to_capture_intent() -> None:
    ours = _section(_text(), "## Station summary")
    theirs = _section(CAPTURE_INTENT.read_text(encoding="utf-8"), "## Station summary")
    assert ours == theirs


def test_what_you_will_be_asked_list_present() -> None:
    section = _section(_text(), "## What you will be asked, in plain words")
    assert "decision point ②" in section or "②" in section


def test_requirement_grammar_follows_the_manifest() -> None:
    """The station shows a REQ line that matches the manifest's grammar."""
    matcher = _grammar_to_regex(_requirements_grammar())
    assert matcher.search(_text()), matcher.pattern


def test_requirement_near_misses_are_not_shown_as_the_form() -> None:
    body = _body(_text())
    for near_miss in (r"\bREQ\d", r"\breq-\d", r"\bR-\d"):
        assert not re.search(near_miss, body), near_miss


def test_gate_markers_present() -> None:
    text = _text()
    for gate_id in GATE_IDS:
        assert f"<!-- gate: {gate_id} -->" in text, gate_id


def test_gate_markers_registered_in_mechanisms() -> None:
    registry = MECHANISMS.read_text(encoding="utf-8")
    for gate_id in GATE_IDS:
        assert f'id: "{gate_id}"' in registry, gate_id


def test_no_deleted_vocabulary() -> None:
    body = _body(_text()).lower()
    found = [w for w in DELETED_VOCABULARY if re.search(rf"\b{re.escape(w)}\b", body)]
    assert not found, found


def test_referenced_relative_paths_exist() -> None:
    """Every bundled path the station cites is skill-dir-relative."""
    skill_dir = SKILL.parent
    cited = set(re.findall(r"`((?:references|assets|scripts)/[^`]+)`", _text()))
    assert cited, "the station cites no bundled file"
    missing = [p for p in cited if not (skill_dir / p).exists()]
    assert not missing, missing


def test_ui_flow_two_sentence_present() -> None:
    assert UI_FLOW_2_SENTENCE in _text()


def test_checker_subcommands_named_exist() -> None:
    usage = _checker_usage()
    named = set(re.findall(r"loom_checker\.py (\w[\w-]*)", _text()))
    assert {"intake", "contract"} <= named, named
    for sub in named:
        assert re.search(rf"loom_checker\.py {re.escape(sub)}\b", usage), sub


def test_checker_rules_named_exist() -> None:
    rules = _checker_rule_ids()
    named = set(re.findall(r"`((?:intake|intent|push|standing|contract)\.[a-z-]+)`", _text()))
    assert {"intake.confirmed", "standing.product-principles-reject"} <= named, named
    unknown = sorted(named - rules)
    assert not unknown, unknown


def test_intake_station_argument_is_this_station() -> None:
    assert "intake write-spec <change-id>" in _text()


def test_hands_spec_to_review_with_the_spec_scope() -> None:
    text = _text()
    assert "loom-code:review" in text
    assert "loom-code:write-plan" in text


def test_reference_files_exist_within_caps() -> None:
    forms = SKILL.parent / "references/spec-forms.md"
    flows = SKILL.parent / "references/ui-flows.md"
    assert forms.is_file() and flows.is_file()
    assert len(forms.read_text(encoding="utf-8").split()) <= SPEC_FORMS_CAP
    assert len(flows.read_text(encoding="utf-8").split()) <= UI_FLOWS_CAP


def test_plugin_declares_requires_contract() -> None:
    data = json.loads(
        (REPO / "loom-design/.claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    assert data["requires-contract"] == ">=1.0"
