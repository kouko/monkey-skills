from pathlib import Path


SKILL = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "dbt-model-style"
    / "SKILL.md"
)


def test_entrypoint_preserves_scope_structure_and_self_check():
    text = SKILL.read_text(encoding="utf-8")

    essence = {
        "bounded style scope": [
            "Style & structure only — not computation.",
            "Do not proactively mass-backfill",
            "part you touch",
            "changing** the computation",
        ],
        "three CTE roles and final": [
            "The three CTE roles",
            "UPPERCASE",
            "lowercase descriptive",
            "one concern per CTE",
            "SELECT * FROM final",
            "final` CTE must contain no business logic",
        ],
        "passthrough": [
            "references/dotstar-passthrough.md",
            "JOINs ≥2 sources",
            "USING (key)",
            "a.*, b.*",
        ],
        "naming and comments": [
            "name matches content",
            "stable prefix, suffix distinguishes the variant",
            "always qualify column references",
            "every `final` column has a purpose comment",
            "3-site comment sync",
        ],
        "two headers": [
            "two separate `/* */` blocks",
            "YAML frontmatter",
            "1–3 sentence unstructured narrative",
            "All layers MUST",
            "Consumer layers",
            "Use `join_on`, not `on`",
            "immediately after the first block and before `config`",
        ],
        "redshift and config": [
            "LISTAGG",
            "UNION ALL",
            "specify the JOIN type explicitly",
            "target.type=='redshift'",
            "materialized",
            "not `materialization`",
        ],
        "final self-check": [
            "After writing / editing",
            "checklists/dbt-model-self-check.md",
            "python scripts/validate_header.py models/",
            "python scripts/validate_header.py --manifest target/manifest.json models/",
            "Ship / open the PR only after it passes.",
        ],
    }
    for contract, needles in essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"
