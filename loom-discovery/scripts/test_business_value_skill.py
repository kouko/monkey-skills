"""Structural grep-test guarding the business-value SKILL.md + template.

SKILL.md is a prompt artifact, not executable code (tdd-iron-law exemption,
same class as the sibling loom-spec / loom-product-principles skill tests).
Its correctness is the PRESENCE of the load-bearing, easily-lost rules the
brief pins: the Shape-Up betting register (NOT Cagan viability), the decidable
trigger AND skip enumerations, the planning-team delegation boundary, the
re-entrant checkpoint framing, the agent behavioral contract, and the verdict
enum GO / NO-GO / NEEDS-MORE-RESEARCH carried by the artifact template.

Checks assert on load-bearing PHRASES (intent), tolerant of wording variation.
Stdlib only (pathlib + re). Resolve paths relative to this test file.
"""

import re
from pathlib import Path

SKILL_DIR = Path(__file__).parents[1] / "skills" / "business-value"
SKILL = SKILL_DIR / "SKILL.md"
TEMPLATE = SKILL_DIR / "assets" / "business-value-template.md"


def _skill() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _template() -> str:
    assert TEMPLATE.is_file(), f"template is absent at {TEMPLATE}"
    return TEMPLATE.read_text(encoding="utf-8")


# --- files exist ------------------------------------------------------------

def test_skill_and_template_exist():
    # Why: the skill is inert without both the instructions and the artifact
    # shape it emits; a missing template silently drops the audit trail.
    assert SKILL.is_file(), f"SKILL.md missing at {SKILL}"
    assert TEMPLATE.is_file(), f"template missing at {TEMPLATE}"


# --- YAML frontmatter -------------------------------------------------------

def test_yaml_frontmatter_name_and_description():
    text = _skill()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "SKILL.md must open with a YAML frontmatter block (--- ... ---)"
    front = m.group(1)
    assert re.search(r"^name:\s*business-value\s*$", front, re.MULTILINE), \
        "frontmatter must declare 'name: business-value'"


def test_description_present_and_within_budget():
    # Why: the harness silently evicts descriptions over the 1536-char
    # per-skill budget → the skill stops auto-triggering (repo memory
    # skill-triggering-diagnose-listing-before-text).
    text = _skill()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "frontmatter block required"
    front = m.group(1)
    dm = re.search(r"^description:\s*(?:\|\s*\n((?:[ \t].*\n?)+)|(\S.*))",
                   front, re.MULTILINE)
    assert dm, "frontmatter must carry a non-empty 'description:'"
    desc = (dm.group(1) or dm.group(2)).strip()
    assert desc, "description must be non-empty"
    assert len(desc) <= 1536, \
        f"description is {len(desc)} chars — must be <=1536 (listing eviction)"


def test_description_triggers_and_scope_guard():
    # Why: triggers must fire on the worth-it intent across the three working
    # languages, and the scope guard must redirect heavy analysis to
    # planning-team so the skill stays a lightweight one-pager.
    front = _skill().split("---", 2)[1].lower()
    assert "worth it" in front, "description must trigger on 'worth it?'"
    assert "should i build" in front, \
        "description must trigger on 'should I build this'"
    assert "值不值得做" in front or "商業價值" in front, \
        "description must carry a Traditional-Chinese trigger"
    assert "ビジネスバリュー" in front, \
        "description must carry a Japanese trigger"
    assert "planning-team" in front, \
        "description scope guard must name planning-team for heavier analysis"


# --- register: Shape Up betting, NOT Cagan viability ------------------------

def test_shape_up_register_not_cagan():
    text = _skill()
    low = text.lower()
    assert "shape up" in low or "shape-up" in low, \
        "must anchor the register in Shape Up betting"
    assert "cagan" in low, "must explicitly contrast against Cagan viability"
    # the contrast must be a NEGATION of Cagan (not Cagan business viability)
    found_not_cagan = False
    for line in low.splitlines():
        if "cagan" in line and ("not" in line or "never" in line):
            found_not_cagan = True
            break
    assert found_not_cagan, \
        "must state the register is NOT Cagan business viability"
    # betting / time-budget framing
    assert "time budget" in low or "time-budget" in low, \
        "must frame the bet as 'worth my time budget'"


def test_one_question_at_a_time_interrogation():
    low = _skill().lower()
    assert "one question at a time" in low or "one-question-at-a-time" in low, \
        "must specify adversarial one-question-at-a-time interrogation"
    # value-judgment axes: why now / why me / opportunity cost
    assert "why now" in low, "interrogation must cover 'why now'"
    assert "why me" in low, "interrogation must cover 'why me'"
    assert "opportunity cost" in low, \
        "interrogation must cover opportunity cost (what the time does NOT go to)"


# --- trigger AND skip conditions as enumerated lists ------------------------

def test_trigger_conditions_enumerated():
    # Why: weak-model sessions must decide fire/skip WITHOUT judgment; the
    # three fire conditions must be an enumerated (a)/(b)/(c) list.
    text = _skill()
    low = text.lower()
    assert "trigger" in low or "fire when" in low or "fires when" in low, \
        "must name the trigger conditions"
    # enumerated markers (a)(b)(c) present
    for marker in ("(a)", "(b)", "(c)"):
        assert marker in text, f"trigger enumeration must carry marker {marker}"
    # the three fire conditions' semantics
    assert "for others" in low or "published" in low or "maintained" in low, \
        "trigger (a): outcome for others / published / maintained"
    assert "compete" in low or "competing" in low or "multiple ideas" in low, \
        "trigger (b): multiple ideas compete for one time budget"
    assert "resource spend" in low or "meaningful" in low, \
        "trigger (c): meaningful resource spend"


def test_skip_conditions_enumerated():
    low = _skill().lower()
    assert "skip" in low, "must name the skip (negative-guard) conditions"
    # silent skip framing — negative-guard, no noise
    assert "silent" in low or "silently" in low, \
        "skip must be SILENT (negative-guard style, no noise)"
    assert "personal tool" in low, "skip: personal tool for self"
    assert "already" in low and ("go" in low or "decided" in low), \
        "skip: GO already decided by the user"


# --- re-entrant checkpoint, not one-way gate --------------------------------

def test_re_entrant_checkpoint():
    low = _skill().lower()
    assert "re-entrant" in low or "reentrant" in low or "revisit" in low, \
        "must state the skill is re-entrant / may be revisited"
    assert "checkpoint" in low, "must frame it as a checkpoint"
    assert "not a one-way gate" in low or "not a gate" in low \
        or "one-way gate" in low, \
        "must contrast checkpoint against a one-way gate"


# --- jurisdiction boundary: delegate to planning-team, never inline ---------

def test_planning_team_delegation_boundary():
    text = _skill()
    low = text.lower()
    assert "planning-team" in text, "must name domain-teams:planning-team"
    assert "domain-teams:planning-team" in text, \
        "must use the plugin-qualified delegation target"
    # market sizing / GTM / revenue → delegate
    assert "market" in low and ("gtm" in low or "revenue" in low), \
        "must scope market sizing / GTM / revenue as planning-team turf"
    # never inline
    found_never_inline = False
    for line in low.splitlines():
        if "inline" in line and ("never" in line or "not" in line):
            found_never_inline = True
            break
    assert found_never_inline, \
        "must state market/GTM/revenue is NEVER done inline (delegate)"
    # cross-plugin delegation contract: pass paths + seed context
    assert "seed context" in low or "pass paths" in low or "paths" in low, \
        "delegation must follow the pass-paths + seed-context contract"


# --- agent behavioral contract ----------------------------------------------

def test_agent_behavioral_contract():
    low = _skill().lower()
    # business-value agents render the worth-it verdict
    assert "verdict" in low, "agents render the worth-it verdict"
    # they may NOT map user needs (user-insights' profession)
    found_may_not = False
    for line in low.splitlines():
        if ("may not" in line or "must not" in line or "never" in line) \
                and "need" in line:
            found_may_not = True
            break
    assert found_may_not, \
        "agent contract: business-value agents may NOT map user needs"
    assert "user-insights" in low, \
        "must name user-insights as the profession that maps needs"


# --- verdict enum GO / NO-GO / NEEDS-MORE-RESEARCH ---------------------------

def test_verdict_enum_in_skill():
    text = _skill()
    for verdict in ("GO", "NO-GO", "NEEDS-MORE-RESEARCH"):
        assert verdict in text, f"SKILL.md must name the verdict '{verdict}'"


def test_verdict_enum_in_template():
    text = _template()
    for verdict in ("GO", "NO-GO", "NEEDS-MORE-RESEARCH"):
        assert verdict in text, f"template must carry the verdict '{verdict}'"


# --- artifact template sections ---------------------------------------------

def test_template_sections():
    text = _template()
    low = text.lower()
    assert "why now" in low, "template must have a Why now section"
    assert "why me" in low, "template must have a Why me section"
    assert "opportunity cost" in low, \
        "template must have an Opportunity cost section"
    assert "evidence" in low, "template must have an Evidence consulted section"
    assert "recommendation" in low, \
        "template must have a Recommendation section"
    # the template may cite user-insights.md when it exists
    assert "user-insights" in low, \
        "Evidence section must allow citing user-insights.md"


def test_skill_references_template_relatively():
    # Why: bundled files resolve relative to the skill dir (repo convention);
    # an absolute or nested path breaks resolution / the folder-structure hook.
    text = _skill()
    assert "assets/business-value-template.md" in text, \
        "SKILL.md must reference the template by its relative path"


def test_skipped_means_implicit_go_no_empty_file():
    low = _skill().lower()
    # when skipped, proceeding downstream is the implicit GO (no empty artifact)
    assert "implicit go" in low or "implicit go" in low.replace("-", " "), \
        "must state that when skipped, proceeding downstream is the implicit GO"
    found_no_empty = False
    for line in low.splitlines():
        if "empty" in line and ("no" in line or "not" in line or "never" in line):
            found_no_empty = True
            break
    assert found_no_empty, "skipped case must NOT write an empty file"


# --- flat folder structure (Anthropic skill convention, hook-enforced) ------

def test_no_nested_subfolders():
    # Why: .claude/hooks/validate-skill-folder-structure.sh blocks a subfolder
    # inside any skill subfolder; a nested dir would be rejected on Write.
    assert SKILL_DIR.is_dir(), f"skill dir absent at {SKILL_DIR}"
    for child in SKILL_DIR.iterdir():
        if child.is_dir():
            for grandchild in child.iterdir():
                assert not grandchild.is_dir(), (
                    f"nested subfolder not allowed: {grandchild} "
                    f"(skill subfolders must be single-level)"
                )
