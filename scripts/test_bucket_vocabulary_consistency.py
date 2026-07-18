"""Drift guard: the three-bucket research-routing vocabulary (craft /
domain-convention / project-local) across the five plugins that carry it —
loom-code, loom-spec, loom-discovery, loom-product-principles,
loom-interface-design.

Source: docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md task 5,
extended by task 11 + §Notes §Pinned bucket vocabulary. By design there is no
shared physical file between plugins (see the plan's "Contract surface vs
per-station freedom" — each skill restates its own minimal copy, precedent:
per-plugin references/{claude-code,codex}-tools.md). This file is the
grep-level CI drift guard replacing a shared file: it pins the vocabulary
spelling and, for the files that transcribe the full pin block verbatim
(PIN_CARRIER_FILES), pins their byte-identity to each other and to the
plan's own fenced source.

Stdlib only.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PLAN_PATH = (
    REPO_ROOT / "docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md"
)
RESEARCH_ESCALATION = (
    REPO_ROOT
    / "loom-code/skills/subagent-driven-development/references/research-escalation.md"
)
DOMAIN_TAG_TRIAGE = (
    REPO_ROOT / "loom-spec/skills/spec-expansion/references/domain-tag-triage.md"
)
EVIDENCE_TEMPLATE = (
    REPO_ROOT / "loom-discovery/skills/user-insights/assets/evidence-template.md"
)
PRODUCT_PRINCIPLES_TRIAGE = (
    REPO_ROOT
    / "loom-product-principles/skills/product-principles/references/knowledge-triage.md"
)
INTERACTION_FLOWS_TRIAGE = (
    REPO_ROOT
    / "loom-interface-design/skills/interaction-flows/references/knowledge-triage.md"
)
DESIGN_SYSTEM_TRIAGE = (
    REPO_ROOT
    / "loom-interface-design/skills/design-system/references/knowledge-triage.md"
)

# All carrier files must use the three exact bucket-name spellings.
CARRIER_FILES = {
    "loom-code/research-escalation.md": RESEARCH_ESCALATION,
    "loom-spec/domain-tag-triage.md": DOMAIN_TAG_TRIAGE,
    "loom-discovery/evidence-template.md": EVIDENCE_TEMPLATE,
    "loom-product-principles/knowledge-triage.md": PRODUCT_PRINCIPLES_TRIAGE,
    "loom-interface-design/interaction-flows/knowledge-triage.md": INTERACTION_FLOWS_TRIAGE,
    "loom-interface-design/design-system/knowledge-triage.md": DESIGN_SYSTEM_TRIAGE,
}

# These transcribe the FULL pin block verbatim (evidence-template.md carries
# just the source-type legend, no fenced pin block — see the plan's
# §Pin usage rules: "Each consuming task transcribes the fenced block...").
PIN_CARRIER_FILES = {
    "loom-code/research-escalation.md": RESEARCH_ESCALATION,
    "loom-spec/domain-tag-triage.md": DOMAIN_TAG_TRIAGE,
    "loom-product-principles/knowledge-triage.md": PRODUCT_PRINCIPLES_TRIAGE,
    "loom-interface-design/interaction-flows/knowledge-triage.md": INTERACTION_FLOWS_TRIAGE,
    "loom-interface-design/design-system/knowledge-triage.md": DESIGN_SYSTEM_TRIAGE,
}

BUCKET_NAMES = ("craft", "domain-convention", "project-local")

# Variant spellings that must never appear in a TAG/VALUE context. Prose like
# "the business domain's rule" or an earlier draft's loose wording is fine —
# these are only checked inside the scoped tag/value neighborhood computed by
# _scoped_tag_text (see docs/loom/memory/grep-tests-scope-to-measured-
# neighborhood.md: whole-file substring checks go false-green when the
# checked phrase pre-exists in unrelated prose).
VARIANT_SPELLINGS = ("domain_convention", "project_local", "domain convention")


# The pin block's own first words — the anchor that picks the RIGHT fence
# even if a file later gains an earlier unrelated code fence, and that makes
# an empty-but-well-formed fence fail loud instead of comparing '' == ''.
PIN_ANCHOR = "Three buckets"


def _fenced_block(text: str) -> str | None:
    """The ```...``` fenced block whose content starts with PIN_ANCHOR,
    or None if no such block exists (empty fences never match)."""
    for match in re.finditer(r"```\n(.*?)\n```", text, re.DOTALL):
        if match.group(1).lstrip().startswith(PIN_ANCHOR):
            return match.group(1)
    return None


def _scoped_tag_text(text: str) -> str:
    """Text narrowed to tag/value contexts: the fenced pin block (if any),
    any line naming the `evidence_needed` tag, and — for evidence-template.md
    — the claim-table row and the "Source type legend" section. Anchored to
    real anchor strings in the actual carrier files, not generic terms, per
    the grep-tests-scope-to-measured-neighborhood gotcha.
    """
    parts = []

    fence = _fenced_block(text)
    if fence:
        parts.append(fence)

    for line in text.splitlines():
        if "evidence_needed" in line:
            parts.append(line)

    legend = re.search(r"## Source type legend\n(.*?)\n##", text, re.DOTALL)
    if legend:
        parts.append(legend.group(1))

    table = re.search(r"\| Claim id \|.*?\n((?:\|.*\n?)+)", text)
    if table:
        parts.append(table.group(1))

    return "\n".join(parts)


def _pin_block(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    fence = _fenced_block(text)
    assert fence, (
        f"{path} pin block is empty or missing — no fenced block starting "
        f"with {PIN_ANCHOR!r}"
    )
    return fence


def _plan_pin_block() -> str:
    return _pin_block(PLAN_PATH)


# --- 1. all three bucket-name spellings present in every carrier file ------


def test_carrier_files_contain_all_three_bucket_names():
    for label, path in CARRIER_FILES.items():
        text = path.read_text(encoding="utf-8")
        for name in BUCKET_NAMES:
            assert name in text, f"{label} missing bucket name {name!r}"


# --- 2. anti-variant: no misspelled bucket name in a tag/value context -----


def test_carrier_files_have_no_variant_spelling_in_tag_context():
    for label, path in CARRIER_FILES.items():
        scoped = _scoped_tag_text(path.read_text(encoding="utf-8"))
        for variant in VARIANT_SPELLINGS:
            assert variant not in scoped, (
                f"{label} uses variant spelling {variant!r} in a tag/value "
                "context (evidence_needed line, table row, or legend)"
            )


def test_scoped_tag_text_catches_an_injected_variant():
    """Proves the anti-variant check above is load-bearing, not vacuous —
    the real carrier files currently contain zero variants, so the file-level
    test alone would stay green even if _scoped_tag_text were broken (e.g.
    scoped to nothing). This fixture injects a variant into a tag context and
    shows the scoping function actually surfaces it.
    """
    fixture = (
        "Some intro prose here.\n"
        "\n"
        "```\n"
        "Tag format: `evidence_needed: domain_convention`\n"
        "```\n"
    )
    scoped = _scoped_tag_text(fixture)
    assert any(variant in scoped for variant in VARIANT_SPELLINGS)


def test_scoped_tag_text_excludes_legitimate_prose_mention():
    """Negative control for the same helper: a variant-looking phrase used as
    ordinary prose (not a tag/value) must NOT be swept into scope, else the
    anti-variant check would false-positive on legitimate writing like "the
    business domain's own convention" (explicitly flagged as fine in the
    task brief).
    """
    fixture = (
        "The business domain's rule is sometimes called a domain convention "
        "in casual prose, not a tag value.\n"
        "\n"
        "## Some Other Section\n"
        "content unrelated to tags\n"
    )
    scoped = _scoped_tag_text(fixture)
    assert "domain convention" not in scoped


# --- 3. pin-identity: the two full-transcription carriers match each other -
#        and match the plan's own fenced §Pinned bucket vocabulary block ----


def test_pin_block_identical_across_research_escalation_and_domain_tag_triage():
    blocks = {label: _pin_block(path) for label, path in PIN_CARRIER_FILES.items()}
    values = list(blocks.values())
    assert values[0] == values[1], (
        f"pin block drifted between {list(blocks.keys())[0]} and "
        f"{list(blocks.keys())[1]}"
    )


def test_pin_block_identical_to_plan_source():
    plan_pin = _plan_pin_block()
    for label, path in PIN_CARRIER_FILES.items():
        assert _pin_block(path) == plan_pin, (
            f"{label}'s pin block drifted from the plan's "
            "§Pinned bucket vocabulary source"
        )


# --- 5. RED-proof: the pin-identity check is load-bearing against mutation -


def test_pin_identity_check_is_load_bearing_against_mutated_copy(tmp_path):
    """Mutate ONE character in a temp copy of the real pin block (never the
    committed files) and show the identity assertion would fail — the
    positive tests above only prove the real files currently agree; this
    proves the check actually discriminates drift, per grep-tests-scope-to-
    measured-neighborhood's mutation-check requirement.
    """
    real_pin = _pin_block(RESEARCH_ESCALATION)
    mutated = real_pin.replace("craft", "craftx", 1)
    assert mutated != real_pin, "sanity: mutation must actually change the text"

    mutated_file = tmp_path / "mutated-research-escalation.md"
    mutated_file.write_text(f"```\n{mutated}\n```\n", encoding="utf-8")

    assert _pin_block(mutated_file) != _plan_pin_block()


# --- sanity: every path this file depends on must exist ---------------------


def test_all_referenced_paths_exist():
    for path in (PLAN_PATH, *CARRIER_FILES.values()):
        assert path.is_file(), f"missing carrier/plan file: {path}"
