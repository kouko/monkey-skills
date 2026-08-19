"""RED test for Task 11 — thinking-session SKILL.md core sitting protocol.

brief-item: BI-6
brief-item: BI-7
brief-item: BI-12
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

import dag

SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "thinking-session"
    / "SKILL.md"
)

WORD_CAP = 4500

REQUIRED_LITERALS = (
    "dag.py check <root>",
    "dag.py claims <root>",
    "dag.py render <root>",
    "break-assumption",
    "references/node-schema.md",
    "references/research-rules.md",
    "references/blind-spot-checklist.md",
)

# The three interrupt points: each token must appear in a sentence that also
# carries the interrupt verb ("confirm" / "ask") — naming the token alone is
# not the contract, being an interrupt point is.
INTERRUPT_TOKENS = ("GOAL", "assumption", "DECISION")


# Machine-readable example convention: each fenced example block in SKILL.md is
# preceded by a marker line `<!-- example: <relpath> -->` naming where the block
# belongs inside a project root.
EXAMPLE_BLOCK = re.compile(
    r"<!-- example: (?P<relpath>[^\s>]+) -->\n```[a-z]*\n(?P<content>.*?)```",
    re.DOTALL,
)


def _body(text: str) -> str:
    """Return the SKILL.md body — everything after the YAML frontmatter."""
    _, body = dag.split_frontmatter(text)
    assert body != text, "SKILL.md must open with YAML frontmatter"
    return body


def _sentences(body: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+|\n", body) if s.strip()]


def _asserts_views_prohibition(body: str) -> None:
    """The `views/` read prohibition must be stated, in either word order."""
    assert re.search(r"never read.*views/", body, re.IGNORECASE) or re.search(
        r"views/.*never", body, re.IGNORECASE
    ), "SKILL.md body must state the views/ read prohibition"


def test_thinking_session_skill_names_cli_verbs_interrupts_view_prohibition_and_word_cap():
    # brief-item: BI-6
    text = SKILL_MD.read_text(encoding="utf-8")
    body = _body(text)

    assert len(body.split()) <= WORD_CAP, (
        f"SKILL.md body is {len(body.split())} words, cap is {WORD_CAP}"
    )

    for literal in REQUIRED_LITERALS:
        assert literal in body, f"SKILL.md body must name {literal!r}"

    _asserts_views_prohibition(body)

    sentences = _sentences(body)
    for token in INTERRUPT_TOKENS:
        assert any(
            token in s and re.search(r"confirm|ask", s, re.IGNORECASE)
            for s in sentences
        ), f"no confirm/ask sentence names the interrupt point {token!r}"


def test_thinking_session_minimal_examples_pass_check(tmp_path):
    # brief-item: BI-6
    body = _body(SKILL_MD.read_text(encoding="utf-8"))
    examples = EXAMPLE_BLOCK.findall(body)

    assert len(examples) == 4, (
        "expected the minimal GOAL / CLAIM / assumption examples to carry "
        f"`<!-- example: ... -->` markers, found {len(examples)}"
    )

    for relpath, content in examples:
        target = tmp_path / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    violations = dag.check(dag.load_project(tmp_path))
    assert violations == [], (
        "SKILL.md examples must be gate-clean when written verbatim:\n"
        + "\n".join(violations)
    )


ROUTER_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "using-think-orbit"
    / "SKILL.md"
)

BREAK_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "break-assumption"
    / "SKILL.md"
)

ROUTER_WORD_CAP = 2500

ROUTER_REQUIRED_LITERALS = (
    "thinking-session",
    "break-assumption",
    "dag.py check <root>",
    "dag.py claims <root>",
)


def test_router_skill_routes_to_verbs_and_forbids_views():
    # brief-item: BI-6
    body = _body(ROUTER_SKILL_MD.read_text(encoding="utf-8"))

    assert len(body.split()) <= ROUTER_WORD_CAP, (
        f"SKILL.md body is {len(body.split())} words, cap is {ROUTER_WORD_CAP}"
    )

    for literal in ROUTER_REQUIRED_LITERALS:
        assert literal in body, f"router SKILL.md body must name {literal!r}"

    _asserts_views_prohibition(body)


SILENT_FILE_WRITING = re.compile(r"silent\s+file\s+writing", re.IGNORECASE)


def test_router_states_the_three_kinds_of_speech():
    # brief-item: BI-1
    body = _body(ROUTER_SKILL_MD.read_text(encoding="utf-8"))
    flat = _flat(body)

    assert re.search(r"reasoning[\s-]*aloud", flat, re.IGNORECASE), (
        "router body must require reasoning-aloud, mirroring thinking-session"
    )
    assert re.search(r"progress\s+narration", flat, re.IGNORECASE), (
        "router body must still ban progress narration"
    )
    assert not SILENT_FILE_WRITING.search(flat), (
        "router body must drop the old blanket 'silent file writing' summary "
        "now that reasoning-aloud is required"
    )

    # SSOT stays in thinking-session — the router summarises and points, it
    # does not restate the warrant duty's three parts or the interrupt table.
    # Whitespace-normalized: a phrase that line-wraps mid-word is still a
    # restatement, and pinning against the raw body would silently miss it.
    for restated in (
        r"which\s+upstream\s+node\s+this\s+step\s+stands\s+on",
        r"what\s+this\s+step\s+adds\s+on\s+top\s+of\s+that",
        r"what\s+would\s+collapse\s+it",
    ):
        assert not re.search(restated, flat, re.IGNORECASE), (
            f"router body restates the warrant duty (matches {restated!r}); it "
            "must point at thinking-session instead"
        )

    assert len(body.split()) <= ROUTER_WORD_CAP, (
        f"SKILL.md body is {len(body.split())} words, cap is {ROUTER_WORD_CAP}"
    )


ALL_SKILL_MDS = (SKILL_MD, ROUTER_SKILL_MD, BREAK_SKILL_MD)

# Every CLI mention must be copy-pasteable: a bare `dag.py <verb>` sends the
# reader to a script that is not on their PATH.

DAG_INVOCATION = re.compile(r"dag\.py (?:check|break|claims|render|impact)\b")
FULL_PREFIX = "${CLAUDE_PLUGIN_ROOT}/scripts/"


@pytest.mark.parametrize("skill_md", ALL_SKILL_MDS, ids=lambda p: p.parent.name)
def test_every_skill_always_uses_full_invocation_prefix(skill_md):
    # brief-item: BI-6
    body = _body(skill_md.read_text(encoding="utf-8"))

    bare = [
        body[max(0, m.start() - 60) : m.end()]
        for m in DAG_INVOCATION.finditer(body)
        if not body[: m.start()].endswith(FULL_PREFIX)
    ]
    assert bare == [], (
        "every dag.py invocation must be written "
        f"`{FULL_PREFIX}dag.py <verb> <root>`; bare mentions: {bare}"
    )


def test_router_skill_states_root_resolution_ladder():
    # brief-item: BI-6
    body = _body(ROUTER_SKILL_MD.read_text(encoding="utf-8"))

    for marker in ("current working directory", "ask", "session"):
        assert marker in body, f"root-resolution ladder must mention {marker!r}"


BREAK_WORD_CAP = 2000

BREAK_REQUIRED_LITERALS = (
    "dag.py break <root> <assumption-id>",
    "impact-",
    "direct dependents",
    "full impact",
    "references/node-schema.md",
)


def test_break_assumption_skill_names_break_verb_and_two_followups():
    # brief-item: BI-6
    body = _body(BREAK_SKILL_MD.read_text(encoding="utf-8"))

    assert len(body.split()) <= BREAK_WORD_CAP, (
        f"SKILL.md body is {len(body.split())} words, cap is {BREAK_WORD_CAP}"
    )

    for literal in BREAK_REQUIRED_LITERALS:
        assert literal in body, f"break-assumption SKILL.md must name {literal!r}"

    # The whole point of the skill: the user declares, the agent only asks.
    assert re.search(r"declare", body, re.IGNORECASE), (
        "SKILL.md must state that the user declares the break, not the agent"
    )

    # Nothing downstream is recomputed — the user decides what to re-examine.
    assert re.search(r"recomput", body, re.IGNORECASE), (
        "SKILL.md must state that nothing is recomputed"
    )

    _asserts_views_prohibition(body)



# --- 0.1.1: the plugin is a thinking-and-planning partner, not only a decider ---

def _description(skill_md: Path) -> str:
    """Return the frontmatter `description:` block of a SKILL.md."""
    fm, _ = dag.split_frontmatter(skill_md.read_text(encoding="utf-8"))
    assert fm, f"{skill_md} must open with YAML frontmatter"
    lines = fm.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("description:"))
    out = [lines[start].split(":", 1)[1].strip().lstrip("|").strip()]
    for line in lines[start + 1 :]:
        if re.match(r"^[a-z_]+:", line):
            break
        out.append(line.strip())
    return " ".join(part for part in out if part)


# Entry vocabulary the user must be able to say. Thinking and planning are
# first-class entries; deciding is one of them, not the only one.
ENTRY_VOCABULARY = (
    "幫我想",
    "想清楚",
    "規劃",
    "整理思路",
    "我要決定",
    "think through",
    "plan",
    "help me think",
    "help me decide",
)

ENTRY_SKILLS = (ROUTER_SKILL_MD, SKILL_MD)


@pytest.mark.parametrize("skill_md", ENTRY_SKILLS, ids=lambda p: p.parent.name)
def test_entry_description_covers_thinking_planning_and_deciding(skill_md):
    description = _description(skill_md)

    for token in ENTRY_VOCABULARY:
        assert token in description, (
            f"{skill_md.parent.name} description must fire on {token!r}"
        )

    sentences = [s for s in re.split(r"(?<=[.。])\s+", description.strip()) if s]
    assert len(sentences) <= 2, (
        f"{skill_md.parent.name} description is {len(sentences)} sentences, cap is 2"
    )


def test_thinking_session_states_a_sitting_need_not_end_in_a_decision():
    body = _body(SKILL_MD.read_text(encoding="utf-8"))

    # The framing the user ruled on: a chain that ends in an open question or a
    # plan outline is a complete record; DECISION is one ending among several.
    assert re.search(
        r"(need not|does not have to|no.{0,20}DECISION).{0,120}DECISION|DECISION.{0,160}(one kind of ending|not the only)",
        body,
        re.IGNORECASE | re.DOTALL,
    ), "SKILL.md must state that a sitting need not end in a DECISION"

    for token in ("open question", "plan"):
        assert token in body, (
            f"SKILL.md must name {token!r} as a valid ending of a sitting"
        )


@pytest.mark.parametrize("skill_md", ALL_SKILL_MDS, ids=lambda p: p.parent.name)
def test_no_skill_still_names_the_old_decision_session_slug(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    assert "decision-session" not in text, (
        f"{skill_md} still names the renamed skill `decision-session`"
    )


# --- 0.1.2: dogfood fixes (FINDING-001…012) ---

# How far after a term's first appearance its explanation may sit — roughly
# one paragraph, so a reader meets the definition without scrolling back.
_FIRST_USE_WINDOW = 400

# Prose pins are bounded so deleting the clause they pin fails the test: an
# unbounded `.*` under DOTALL matches across the whole file and pins nothing.
_NEARBY = r".{0,200}"

NODE_SCHEMA_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "thinking-session"
    / "references"
    / "node-schema.md"
)


def test_node_schema_examples_pass_check(tmp_path):
    """node-schema.md's own worked examples must be gate-clean when written
    verbatim into a project root -- same `<!-- example: <relpath> -->` marker
    convention SKILL.md uses, so a shipped example can never silently
    contradict a shipped rule (SKILL.md is covered by
    test_thinking_session_minimal_examples_pass_check; this is node-schema.md's
    counterpart)."""
    text = NODE_SCHEMA_MD.read_text(encoding="utf-8")
    examples = EXAMPLE_BLOCK.findall(text)

    assert len(examples) == 4, (
        "expected node-schema.md's GOAL / CLAIM / assumption / research-note "
        f"examples to carry `<!-- example: ... -->` markers, found {len(examples)}"
    )

    for relpath, content in examples:
        target = tmp_path / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    violations = dag.check(dag.load_project(tmp_path))
    assert violations == [], (
        "node-schema.md examples must be gate-clean when written verbatim:\n"
        + "\n".join(violations)
    )


def test_router_description_owns_intake_and_carries_the_missed_trigger_shapes():
    """FINDING-001/002/010/012 — the router lost every folder-mentioning and
    assumption-broke query because its description described what the plugin is
    rather than that it owns intake and fires on a broken premise."""
    description = _description(ROUTER_SKILL_MD)

    for cue in ("before inspecting", "owns intake"):
        assert cue in description, f"router description must carry the ownership cue {cue!r}"

    for cue in ("假設破了", "情況變了", "前提不成立",
                "an assumption broke", "the situation changed"):
        assert cue in description, f"router description must fire on {cue!r}"

    for cue in ("有結構的思考", "回頭看當初的前提",
                "structured thinking", "trace what it rested on"):
        assert cue in description, f"router description must fire on {cue!r}"

    assert re.search(r"not for .*(casual|one-off)", description), (
        "router description must carry a negative cue against casual one-off choices"
    )
    assert re.search(r"\btaglines?\b", description), (
        "router description must exclude generating names/taglines"
    )


def test_router_body_does_not_explore_a_named_folder_before_intake():
    """FINDING-001 — the observed first move was `ls` on the named folder."""
    body = _body(ROUTER_SKILL_MD.read_text(encoding="utf-8"))

    assert re.search(r"names a folder.*not explore it first", body, re.DOTALL), (
        "router body must say that a named folder is resolved as <root>, not explored first"
    )


def test_router_verb_table_break_row_names_stale_and_weakened():
    """FINDING-009 — `stale` / `weakened` were defined only in break-assumption."""
    body = _body(ROUTER_SKILL_MD.read_text(encoding="utf-8"))

    break_row = next(
        line for line in body.splitlines() if line.startswith("| `break <root>")
    )
    assert re.search(r"\bstale\b", break_row) and re.search(r"\bweakened\b", break_row), (
        f"router break row must distinguish stale from weakened: {break_row!r}"
    )
    assert "load-bearing" in break_row, (
        f"router break row must say stale follows the load-bearing chain: {break_row!r}"
    )


def test_break_assumption_description_applies_mid_conversation_and_states_the_root_ladder():
    """FINDING-002 — standalone `break-assumption` never fired because its
    description promised a flow over an already-visible project."""
    description = _description(BREAK_SKILL_MD)

    assert re.search(r"mid-conversation", description), (
        "break-assumption description must apply whenever a premise changed, "
        "even mid-conversation"
    )
    assert "<root>" in description and "ladder" in description, (
        "break-assumption description must state it resolves <root> via the "
        "router's own ladder when none is known"
    )


def test_thinking_session_description_points_back_at_the_router():
    """FINDING-011 — 3/40 runs entered thinking-session directly, skipping intake."""
    description = _description(SKILL_MD)

    assert "using-think-orbit" in description
    assert re.search(r"entered directly.*ladder", description), (
        "thinking-session description must send a direct entry through the "
        "router's <root> ladder first"
    )


def test_thinking_session_body_states_the_direct_entry_ladder():
    """FINDING-011 — the body's intake note carries the same rule."""
    body = _body(SKILL_MD.read_text(encoding="utf-8"))

    assert re.search(r"entered directly.*ladder", body, re.DOTALL), (
        "thinking-session body must run the router's <root> ladder on direct entry"
    )


def test_thinking_session_gate_is_per_file_not_per_batch():
    """FINDING-003 — the executor wrote 6 FACT nodes then ran `check` once."""
    body = _body(SKILL_MD.read_text(encoding="utf-8"))

    assert re.search(r"one `check` per written or edited file", body), (
        "the gate section must require one check per file"
    )
    assert re.search(r"never one check for a batch of files", body), (
        "the gate section must forbid one check for a batch of files"
    )
    assert "user-visible turn" not in body, (
        "the per-file rule takes no per-turn hedge — a turn may write many files"
    )


def test_thinking_session_lists_an_open_question_ending_as_a_render_milestone():
    """FINDING-003 — the executor found no milestone covering an open ending."""
    body = _body(SKILL_MD.read_text(encoding="utf-8"))

    milestone_sentence = next(
        s for s in _sentences(body) if "milestone" in s and "GOAL confirmed" in s
    )
    assert "sitting ends on an open question" in milestone_sentence, (
        f"render milestones must include an open-question ending: {milestone_sentence!r}"
    )


def test_thinking_session_confirms_a_goal_already_stated_instead_of_re_asking():
    """FINDING-004 — the GOAL interrupt fired although the opening stated the goal."""
    body = _body(SKILL_MD.read_text(encoding="utf-8"))

    assert re.search(
        r"opening message already states the goal.*one-line confirmation",
        body,
        re.DOTALL,
    ), "the first-sitting section must skip re-asking a goal the opening already states"


def test_thinking_session_keeps_inference_out_of_a_fact_body():
    """FINDING-006 — FACT bodies carried 'this means…' tails."""
    body = _body(SKILL_MD.read_text(encoding="utf-8"))

    assert "restates and contextualizes the quote" in body
    assert re.search(r"this means.{0,80}CLAIM", body, re.DOTALL | re.IGNORECASE), (
        "the node-types section must send a 'this means…' inference to a CLAIM"
    )


def test_thinking_session_inlines_the_status_enum_and_defines_load_bearing_at_first_use():
    """FINDING-008 — a cold reader stalled on `status` and met `load_bearing` unexplained."""
    body = _body(SKILL_MD.read_text(encoding="utf-8"))

    assert "status: current | stale" in body and "only break writes stale" in body, (
        "the body must inline the status enum a first-time reader needs"
    )

    first_use = body.index("load_bearing")
    definition = body.index("collapses if")
    assert definition < first_use + _FIRST_USE_WINDOW, (
        "`load_bearing` must be defined where a reader first meets it"
    )


def test_thinking_session_files_a_cross_branch_assumption_project_wide():
    """FINDING-005 — a pivotal premise was forced into one branch by the ≤3 cap."""
    body = _body(SKILL_MD.read_text(encoding="utf-8"))

    assert re.search(r"governs several branches" + _NEARBY + r"project-wide", body, re.DOTALL), (
        "the assumptions section must file a cross-branch premise project-wide"
    )
    assert re.search(r"project-wide" + _NEARBY + r"`inputs`", body, re.DOTALL), (
        "each dependent node must cite the project-wide assumption via `inputs`"
    )


def test_node_schema_documents_optional_branch_and_project_wide_assumptions():
    """FINDING-005 — the schema is the SSOT a writer checks for the field."""
    schema = NODE_SCHEMA_MD.read_text(encoding="utf-8")

    assert re.search(r"`branch`.*optional", schema), (
        "node-schema.md must say an assumption's `branch` is optional"
    )
    assert "project-wide" in schema
    assert re.search(r"project-wide" + _NEARBY + r"(max 3|\bcap\b)", schema, re.DOTALL), (
        "node-schema.md must say the ≤3 cap counts branch-bound assumptions only"
    )


# --- 0.1.4: the transparency contract (both faces) ---

# Prose pins are compared against a whitespace-normalized copy of the file so a
# phrase that wraps across a newline still matches: `"a b"` is not a contiguous
# substring of `"a\nb"`, and pinning the wrapped form would silently pin nothing.
def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


# The four self-describing placeholder bodies BI-5 retires. A worked example is
# prescriptive — an agent copies the shape it is shown, so a placeholder example
# teaches placeholder bodies.
PLACEHOLDER_BODIES = (
    "Body text in short paragraphs",
    "Longer body text explaining the goal",
    "Optional body with more detail",
    "Optional body with supporting detail",
)

# The three parts of the warrant duty, stated in both the protocol (SKILL.md)
# and the field SSOT (node-schema.md).
WARRANT_DUTY_PARTS = (
    "restated in prose",
    "what this step adds",
    "what would collapse it",
)

_EXAMPLE_REF = re.compile(r"ref:\s*([A-Za-z0-9_.-]+)")


def test_thinking_session_states_the_transparency_contract():
    """BI-1 / BI-2 / BI-4 (authoring half) / BI-5 — measured 2/2 vs 0/8.

    Nodes protected by an interrupt narrate their upstream; nodes written
    silently never do, because reasoning that is never spoken is never
    articulated and so has nothing to write into the body.
    """
    body = _body(SKILL_MD.read_text(encoding="utf-8"))
    schema = NODE_SCHEMA_MD.read_text(encoding="utf-8")
    flat_body = _flat(body)
    flat_schema = _flat(schema)

    # (a) progress narration stays banned — the one kind of speech that is noise.
    assert "Progress narration stays banned" in flat_body, (
        "the contract must keep progress narration banned"
    )

    # (b) reasoning-aloud is required, not merely permitted.
    assert "Reasoning-aloud is required" in flat_body, (
        "the contract must REQUIRE reasoning-aloud"
    )

    # (c) granularity: before the action, not after the thought; one or two
    # sentences; never awaiting a reply.
    assert "before the action, not after the thought" in flat_body
    assert "one or two sentences" in flat_body
    assert re.search(r"never wait|without waiting|not wait", flat_body), (
        "reasoning-aloud must not turn into a fourth interrupt"
    )

    # (d) the host-preference exception, stated with its reason.
    assert "deliberate exception to a host-level" in flat_body
    assert "Transparency is the product" in flat_body

    # (e) the blanket silence rule is gone — no parallel version left standing.
    assert "Everything else is" not in flat_body
    assert "silent file writing" not in flat_body
    assert "write silently" not in flat_body

    # (f) the warrant duty and the stands-alone rule, in BOTH documents.
    for name, flat in (("SKILL.md", flat_body), ("node-schema.md", flat_schema)):
        for part in WARRANT_DUTY_PARTS:
            assert part in flat, f"{name} must state the warrant duty part {part!r}"
        assert re.search(
            r"even (though|when) the same reasoning was already spoken", flat
        ), f"{name} must say the file stands alone even after the reasoning was spoken"
    # the prose must not permit what the gate flags: `input-narration` only
    # requires a LOAD-BEARING input's id. A bare "load-bearing" substring
    # check would pass on the unrelated "non-load-bearing" mention in the
    # referral_scales example, so these pin the actual clauses instead.
    assert re.search(r"which load-bearing .{0,40}stands on", flat_body), (
        "SKILL.md's warrant duty must say it names a LOAD-BEARING upstream node"
    )
    assert re.search(r"checks only that a load-bearing input", flat_body), (
        "SKILL.md must say the gate checks a LOAD-BEARING input's id, "
        "matching what `input-narration` actually checks"
    )
    assert re.search(r"at least one load-bearing input", flat_schema), (
        "node-schema.md must say `input-narration` requires a LOAD-BEARING input's id"
    )

    # (g) the branch-opening rule — the authoring half of `branch-has-node`.
    assert "one CLAIM node stating that path's position" in flat_body
    assert "branch-has-node" in flat_body

    # (h) no placeholder example bodies, and at least one example node carries
    # non-empty `inputs` whose body names one of them.
    for placeholder in PLACEHOLDER_BODIES:
        assert placeholder not in flat_body, f"SKILL.md still ships {placeholder!r}"
        assert placeholder not in flat_schema, f"node-schema.md still ships {placeholder!r}"

    # (i) a fork that becomes visible only after one path is under way — the
    # asymmetric case, where three readings give structurally different graphs
    # and `branch-has-node` cannot arbitrate between them.
    assert "Open the branch retroactively" in flat_body
    assert "tag the existing path's nodes" in flat_body

    # (j) the warrant duty does not over-claim for a node with no upstream:
    # it says so and says why, rather than inventing an upstream ref.
    for name, flat in (("SKILL.md", flat_body), ("node-schema.md", flat_schema)):
        assert "says so and says why it has none" in flat, (
            f"{name} must exempt a node with no upstream from naming one"
        )

    # (k) the field's owner states that an assumption body is optional, so the
    # two worked examples stop implying a rule by accident.
    assert "body is optional and ungated" in flat_schema

    narrating = []
    for _relpath, content in EXAMPLE_BLOCK.findall(body):
        front, example_body = dag.split_frontmatter(content)
        refs = _EXAMPLE_REF.findall(front)
        # Whole-id matching via dag's own helper — plain `ref in body` is the
        # containment semantics Task 1 measured and rejected, and shipping it
        # inside our test set invites someone to copy it back out.
        if refs and any(dag._id_named_in(ref, example_body) for ref in refs):
            narrating.append(refs)
        assert example_body.strip(), (
            f"the {_relpath} example ships an empty body — worked examples are "
            "prescriptive, and an empty one teaches empty bodies"
        )
    assert narrating, (
        "at least one SKILL.md example node must carry non-empty `inputs` and "
        "name one of them in its body, so the example set exercises "
        "`input-narration`"
    )
