from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "loom-workflow/skills/cot-explain/SKILL.md"
BASELINE_WORDS = 4350


def test_entrypoint_preserves_extraction_render_and_fidelity_gates_under_word_ceiling():
    text = SKILL_PATH.read_text(encoding="utf-8")

    essence = {
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

    words = re.findall(r"\S+", text)
    assert len(words) >= int(BASELINE_WORDS * 0.75), len(words)
    assert len(words) <= 3567, len(words)
