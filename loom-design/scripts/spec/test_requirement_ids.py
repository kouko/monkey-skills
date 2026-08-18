"""Doc-schema tests for `requirement-identifiers.md` — the SSOT of the
`REQ-<n>` convention (BI-9, Task 10 of
`docs/loom/plans/2026-08-18-requirement-identity-hybrid.md`).

requirement-identifiers.md is a prompt/contract artifact, not executable
code: nothing importable observes whether a spec author picks `REQ-<n>`
correctly. This file IS the schema the author reads, so its correctness
condition is that the declared properties (form, authored-not-derived,
monotonic-never-reused, scope, adoption, language) and their failure modes
are stated INSIDE the section that owns them.

Shaped after `loom-code/scripts/test_brief_item_ids.py` (`:47` `_section_body`,
`:117/:176/:347/:396` the four assertions), reusing its fence-aware slicer
SHAPE rather than importing `adjudication_split` — that module lives under
`loom-code/scripts/`, a sibling package this file's pytest rootdir
(`loom-design/scripts/spec/`) does not put on `sys.path`, so a local
minimal H2 slicer is reimplemented here instead of reaching cross-package.

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

REQUIREMENT_IDENTIFIERS_MD = (
    Path(__file__).parents[2]
    / "skills"
    / "spec-expansion"
    / "references"
    / "requirement-identifiers.md"
)

FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
H2_RE = re.compile(r"^## (.+)$")


def _split_h2_sections(text: str) -> list[tuple[str, str]]:
    """Split `text` into (heading, body) pairs on unfenced `## ` lines.

    Fence-aware: a `## `-prefixed line inside a fenced code block is
    content, not a section boundary — a fence-blind scan would truncate a
    section that ever fences an example header. The doc today uses inline
    backtick spans, not fences — the guard is defensive, so a future fenced
    `### Requirement: REQ-<n> — <name>` example cannot silently truncate a
    section.
    """
    sections: list[tuple[str, list[str]]] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines():
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
        if not in_fence:
            heading_match = H2_RE.match(line)
            if heading_match:
                sections.append((heading_match.group(1).strip(), []))
                continue
        if sections:
            sections[-1][1].append(line)
        # else: preamble before the first H2 — irrelevant to this file's tests
    return [(heading, "\n".join(body)) for heading, body in sections]


def _section_body(text: str, heading_text: str) -> str:
    sections = [
        body for heading, body in _split_h2_sections(text) if heading == heading_text
    ]
    assert len(sections) == 1, (
        f"the document must carry exactly one '## {heading_text}' section; "
        f"found {len(sections)}"
    )
    return sections[0]


def _doc_text() -> str:
    assert REQUIREMENT_IDENTIFIERS_MD.is_file(), (
        f"requirement-identifiers.md is absent at {REQUIREMENT_IDENTIFIERS_MD}"
    )
    return REQUIREMENT_IDENTIFIERS_MD.read_text(encoding="utf-8")


def test_section_slicer_is_fence_aware() -> None:
    fixture = """\
## Target

before the fence

```markdown
## Form

## Scope
```

after the fence

## Next section

body of the next section
"""
    body = _section_body(fixture, "Target")
    assert "after the fence" in body
    assert "body of the next section" not in body


def test_convention_declares_form_minting_and_all_or_nothing() -> None:
    text = _doc_text()

    form = _section_body(text, "Form")
    assert "`REQ-<n> — <name>`" in form, (
        "the Form section must state the id-first shape literally as "
        "`REQ-<n> — <name>`"
    )
    for non_form in ("REQ1", "req-1", "R-1"):
        assert non_form in form, (
            f"the Form section must name {non_form!r} as a non-form"
        )

    monotonic = _section_body(text, "Monotonic, never renumbered, never reused")
    assert "--next-req-id" in monotonic, (
        "the minting rule must name the `--next-req-id` helper"
    )
    assert "never renumbered" in monotonic
    assert "never reused" in monotonic
    assert "split" in monotonic and "merge" in monotonic and (
        "retires both sides" in monotonic
    ), "the minting rule must state that split/merge retires both sides"

    adoption = _section_body(
        text, "Adoption is all-or-nothing per spec file"
    )
    assert "all-or-nothing" in adoption
    assert "not deprecated" in adoption, (
        "the adoption section must state that legacy prose-only files are "
        "not deprecated"
    )


def test_scope_states_shared_grammar_and_living_spec_may_omit_name() -> None:
    text = _doc_text()
    scope = _section_body(text, "Scope")

    assert "specs/*/spec.md" in scope, (
        "the Scope section must name the change-folder `specs/*/spec.md` shape"
    )
    assert "share the grammar" in scope, (
        "the Scope section must state that change-folder and living-spec "
        "headers share the grammar"
    )
    assert "may omit" in scope and "— <name>" in scope, (
        "the Scope section must state that a living-spec header may omit "
        "the ` — <name>` half"
    )


def test_anti_patterns_cover_the_requirement_id_failure_modes() -> None:
    text = _doc_text()
    anti_patterns = _section_body(text, "Anti-patterns")

    for entry in (
        "Skipping an id in an id-mode file",
        "Renumbering on insert",
        "Reusing a retired number",
        "Deriving the id from the name",
        "Minting an id from inside an implementer",
    ):
        assert f"❌ **{entry}" in anti_patterns, (
            f"the Anti-patterns section must carry an ❌ entry for {entry!r}"
        )


def test_language_and_parser_pointers() -> None:
    text = _doc_text()

    language = _section_body(text, "Language")
    assert "English" in language, (
        "the Language section must state that id + name are English"
    )
    assert "machine-executed precision content" in language, (
        "the Language section must state the rationale: machine-executed "
        "precision content"
    )

    parsers = _section_body(text, "Parsers")
    for path in (
        "validate_spec_output.py",
        "check_scenario_coverage.py",
        "check-living-spec-index.py",
    ):
        assert path in parsers, f"the Parsers section must point at {path}"

    # Never restate the regexes: no capture-group syntax anywhere in the doc.
    assert "(?P<" not in text, (
        "the document must point at the parsers by path, never restate "
        "their regexes"
    )
