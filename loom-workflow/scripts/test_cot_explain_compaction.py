from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "loom-workflow/skills/cot-explain/SKILL.md"


def test_entrypoint_preserves_extraction_render_and_fidelity_gates():
    text = SKILL_PATH.read_text(encoding="utf-8")

    essence = {
        # Restored in the #740 follow-up after the compaction deleted the routing
        # destinations while keeping the prohibition. Pinned so a re-deletion
        # fails instead of going green under the word band's slack.
        "active-reasoning routing": [
            "think-orbit:thinking-session",
            "think-orbit:break-assumption",
            "obsidian:obsidian-mermaid-visualizer",
        ],
        "source selection": ["File mode", "Conversation mode", "State which mode"],
        "extraction net": [
            "Rejected options",
            "Assumptions",
            "Open questions",
            "Exceptions and withdrawal conditions",
            "Co-premises",
            "author's own hedging",
        ],
        "early exit": ["Fewer than 5", "stop", "answer their question directly"],
        "layout invariants": [
            "graph TB",
            "direction LR",
            "r1 -->|",
            "Rows of at most 3",
            "Every** edge carries a label",
        ],
        "markdown authority": [
            "markdown is the artifact",
            "hand-write the HTML",
            "assets/cot-report-template.md",
        ],
        "render verify render": [
            "python3 scripts/render_cot_html.py <file>.md",
            "python3 scripts/verify_cot_html.py --render --stamp <file>.html",
        ],
        "fidelity gate": [
            "before anything gets shared",
            "references/fidelity-check.md",
            "<name>.fidelity.md",
            "reviewed_md_sha256:",
        ],
        "temporary paths and publishing consent": [
            "${TMPDIR:-/tmp}/cot-explain/",
            "both are temporary",
            "Ask once",
            "do not publish unprompted",
        ],
    }
    for contract, needles in essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    commands = "\n".join(
        [
            "python3 scripts/render_cot_html.py <file>.md",
            "python3 scripts/verify_cot_html.py --render --stamp <file>.html",
            "python3 scripts/render_cot_html.py <file>.md",
        ]
    )
    assert commands in text

