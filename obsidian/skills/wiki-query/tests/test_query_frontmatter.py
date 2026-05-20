"""Tests for wiki-query/scripts/query-frontmatter.py.

query-frontmatter.py is the Tier 1 entry point for wiki-query: walks
the vault's wiki/ subdirectories, extracts frontmatter from each .md
page, scores candidates against caller-supplied keywords, and emits
JSON.

Task 1 covers the English happy-path MVP: ASCII keyword, lowercase
substring scoring (title=3 / tag=2 / summary=1), top-K JSON output.
Multilingual + edge cases land in Task 2.

Fixtures are built in-memory via tmp_path because the skill-folder
hook (validate-skill-folder-structure.sh) forbids nested subfolders
under any skill directory. Persisting tests/fixtures/vault/wiki/...
on disk would violate the convention; tmp_path keeps the same vault
shape without on-disk nesting.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SCRIPT = REPO / "obsidian" / "skills" / "wiki-query" / "scripts" / "query-frontmatter.py"


def _load_module():
    """Load query-frontmatter.py as an importable module despite the hyphen."""
    spec = importlib.util.spec_from_file_location("query_frontmatter", SCRIPT)
    assert spec and spec.loader, f"cannot spec-load {SCRIPT}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _build_vault(root: Path) -> Path:
    """Build a minimal wiki/ fixture under `root/vault/` and return vault path.

    Three pages exercise the title=3 / tag=2 / summary=1 scoring:
      - entities/TSMC.md          title="TSMC" + tag "tsmc"  → max title hit
      - concepts/quant-investing  no TSMC anywhere            → not in results
      - references/2026-04-20-tsmc-earnings.md
                                  title mentions tsmc, tag tsmc, summary
                                  mentions tsmc → all 3 fields hit
    """
    vault = root / "vault"
    wiki = vault / "wiki"
    (wiki / "entities").mkdir(parents=True)
    (wiki / "concepts").mkdir(parents=True)
    (wiki / "references").mkdir(parents=True)
    (wiki / "skills").mkdir(parents=True)
    (wiki / "journal").mkdir(parents=True)
    (wiki / "synthesis").mkdir(parents=True)

    (wiki / "entities" / "TSMC.md").write_text(
        '---\n'
        'title: "TSMC"\n'
        'type: wiki-entity\n'
        'domain: finance\n'
        'status: developing\n'
        'updated: 2026-04-20\n'
        'tags:\n'
        '  - tsmc\n'
        '  - semiconductors\n'
        'sources_count: 3\n'
        'summary: "Largest pure-play foundry; advanced-node leader with CoWoS bottleneck."\n'
        '---\n\n'
        '## Summary\n\nTSMC body content.\n',
        encoding="utf-8",
    )

    (wiki / "concepts" / "quant-investing.md").write_text(
        '---\n'
        'title: "Quantitative Investing"\n'
        'type: wiki-concept\n'
        'domain: finance\n'
        'status: seed\n'
        'updated: 2026-04-15\n'
        'tags:\n'
        '  - quant\n'
        '  - finance\n'
        'sources_count: 2\n'
        'summary: "Systematic rule-based investment approach using statistical models."\n'
        '---\n\n'
        '## Summary\n\nQuant body.\n',
        encoding="utf-8",
    )

    (wiki / "references" / "2026-04-20-tsmc-earnings.md").write_text(
        '---\n'
        'title: "TSMC Q1 2026 earnings call"\n'
        'type: wiki-reference\n'
        'source_path: "references/finance/2026-04-20 TSMC Q1.md"\n'
        'date: 2026-04-20\n'
        'updated: 2026-04-20\n'
        'tags:\n'
        '  - tsmc\n'
        '  - earnings\n'
        'contributes_to: ["[[TSMC]]"]\n'
        'summary: "TSMC reported Q1 revenue beat with CoWoS tight through 2026."\n'
        '---\n\n'
        '## Source\n\n[[2026-04-20 TSMC Q1]]\n',
        encoding="utf-8",
    )

    return vault


def test_happy_path_top_k_by_score(tmp_path):
    """Happy path: keyword 'TSMC' returns TSMC + tsmc-earnings ranked by score.

    Scoring (lowercase substring, title=3 / tag=2 / summary=1):
      - entities/TSMC.md:
          title "TSMC" hits → 3
          tag "tsmc" hits → 2
          summary no "tsmc" → 0
          total = 5
      - references/2026-04-20-tsmc-earnings.md:
          title "TSMC Q1 2026 earnings call" hits → 3
          tag "tsmc" hits → 2
          summary "TSMC reported..." hits → 1
          total = 6
      - concepts/quant-investing.md: no hits → excluded (score 0)

    Expected order: tsmc-earnings (6) first, TSMC (5) second.
    """
    mod = _load_module()
    vault = _build_vault(tmp_path)

    results = mod.query(
        vault_root=vault,
        keywords=["TSMC"],
        top=3,
    )

    assert isinstance(results, list), "query() must return a list"
    assert len(results) == 2, (
        f"expected 2 matches (TSMC + tsmc-earnings), got {len(results)}: {results}"
    )

    # Required schema on each row
    for row in results:
        for key in ("path", "title", "type", "summary", "tags", "score"):
            assert key in row, f"missing key {key!r} in row: {row}"

    # Ranking: tsmc-earnings (6) > TSMC (5)
    assert "tsmc-earnings" in results[0]["path"]
    assert results[1]["path"].endswith("TSMC.md")

    # Pin the documented weights (title=3 / tag=2 / summary=1).
    # tsmc-earnings: title(3) + tag(2) + summary(1) = 6
    # TSMC:          title(3) + tag(2)             = 5
    # If anyone re-weights without updating the spec, these break.
    by_path = {r["path"]: r["score"] for r in results}
    earnings_score = next(s for p, s in by_path.items() if "tsmc-earnings" in p)
    tsmc_score = next(s for p, s in by_path.items() if p.endswith("TSMC.md"))
    assert earnings_score == 6, (
        f"expected tsmc-earnings score = 3+2+1 = 6, got {earnings_score}"
    )
    assert tsmc_score == 5, (
        f"expected TSMC score = 3+2 = 5, got {tsmc_score}"
    )


def test_cli_outputs_valid_json_with_tsmc_first(tmp_path):
    """End-to-end CLI: --keywords TSMC --top 3 returns valid JSON, TSMC ranked.

    Validates the script is callable via `python3 path/to/script.py ...`
    (the SKILL.md Tier 1 invocation form) and emits parseable JSON on
    stdout with the documented row schema.
    """
    vault = _build_vault(tmp_path)

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--keywords", "TSMC",
            "--top", "3",
            "--vault-root", str(vault),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (
        f"script exited {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )

    payload = json.loads(proc.stdout)
    assert isinstance(payload, list), "CLI output must be a JSON array"
    assert len(payload) >= 1, "expected at least one match for 'TSMC'"

    # Each row must carry the documented Tier 1 schema
    for row in payload:
        for key in ("path", "title", "type", "summary", "tags", "score"):
            assert key in row, f"missing {key!r} in CLI row: {row}"

    # TSMC-related rows present and tsmc-earnings ranks first by score
    titles = [r["title"] for r in payload]
    assert any("TSMC" in t for t in titles), f"no TSMC title in {titles}"
    assert payload[0]["score"] >= payload[-1]["score"], "results not sorted desc by score"


# ---------------------------------------------------------------------------
# Task 2 — multilingual + edge cases
# ---------------------------------------------------------------------------


def _build_vault_t2(root: Path) -> Path:
    """Multilingual + edge-case fixture for Task 2.

    Pages:
      - entities/台積電.md      — CJK page; summary mentions "世界最大晶圓代工廠"
      - entities/fullwidth.md   — summary contains fullwidth "ＡＢＣ" (NFKC→"ABC")
      - concepts/missing-summary.md
                                 — frontmatter has NO `summary:` line; must be
                                   skipped from candidates even if title hits
      - references/some-ref.md   — generic reference page used by --type filter
                                   test (excluded when --type entities is set)
    """
    vault = root / "vault"
    wiki = vault / "wiki"
    for sub in ("entities", "concepts", "references", "skills", "journal", "synthesis"):
        (wiki / sub).mkdir(parents=True)

    (wiki / "entities" / "台積電.md").write_text(
        '---\n'
        'title: "台積電"\n'
        'type: wiki-entity\n'
        'domain: finance\n'
        'status: developing\n'
        'updated: 2026-04-20\n'
        'tags:\n'
        '  - 半導體\n'
        '  - foundry\n'
        'sources_count: 3\n'
        'summary: "世界最大晶圓代工廠；先進製程領先 CoWoS 為瓶頸。"\n'
        '---\n\n'
        '## Summary\n\n台積電 body.\n',
        encoding="utf-8",
    )

    (wiki / "entities" / "fullwidth.md").write_text(
        '---\n'
        'title: "Fullwidth Test"\n'
        'type: wiki-entity\n'
        'tags:\n'
        '  - test\n'
        'summary: "Mention of ＡＢＣ in fullwidth form."\n'
        '---\n\n'
        '## Summary\n\nbody.\n',
        encoding="utf-8",
    )

    (wiki / "concepts" / "missing-summary.md").write_text(
        '---\n'
        'title: "TSMC concept page without summary"\n'
        'type: wiki-concept\n'
        'tags:\n'
        '  - tsmc\n'
        '---\n\n'
        '## Summary\n\nbody only — no summary frontmatter field.\n',
        encoding="utf-8",
    )

    (wiki / "references" / "some-ref.md").write_text(
        '---\n'
        'title: "TSMC reference doc"\n'
        'type: wiki-reference\n'
        'tags:\n'
        '  - tsmc\n'
        'summary: "Reference doc mentioning TSMC."\n'
        '---\n\n'
        '## Source\n\nbody.\n',
        encoding="utf-8",
    )

    return vault


def test_nfkc_normalize_fullwidth(tmp_path):
    """Keyword "ABC" must hit summary "...ＡＢＣ..." via NFKC normalization.

    Fullwidth ＡＢＣ (U+FF21 U+FF22 U+FF23) normalizes to halfwidth ABC under
    NFKC; the score function must apply NFKC before substring matching.
    """
    mod = _load_module()
    vault = _build_vault_t2(tmp_path)

    results = mod.query(vault_root=vault, keywords=["ABC"], top=5)

    paths = [r["path"] for r in results]
    assert any("fullwidth.md" in p for p in paths), (
        f"expected fullwidth.md in results (NFKC ＡＢＣ→ABC), got {paths}"
    )


def test_cjk_substring_matches(tmp_path):
    """Keyword '晶圓' must hit '世界最大晶圓代工廠' via Python `in` on NFKC string.

    No tokenizer — CJK substring works because Python `in` operates on the
    full normalized string.

    Regression pin: this assertion was incidentally green against T1's code
    (T1's `.lower()` + `in` already handled CJK; T2's NFKC layer is a no-op
    for these particular code points). Kept as a behavioral pin to lock in
    brief Decision Q3 — guarantees future refactors keep CJK substring
    working even if the normalization pipeline changes.
    """
    mod = _load_module()
    vault = _build_vault_t2(tmp_path)

    results = mod.query(vault_root=vault, keywords=["晶圓"], top=5)

    paths = [r["path"] for r in results]
    assert any("台積電.md" in p for p in paths), (
        f"expected 台積電.md in results for '晶圓', got {paths}"
    )


def test_type_filter_restricts_dir(tmp_path):
    """`--type entities` must exclude pages under references/ (and other dirs).

    Pages with TSMC-matching frontmatter exist in entities/ AND references/.
    With `type='entities'`, only entities/* should appear.
    """
    mod = _load_module()
    vault = _build_vault_t2(tmp_path)

    results = mod.query(
        vault_root=vault,
        keywords=["TSMC"],
        top=10,
        type_filter="entities",
    )

    paths = [r["path"] for r in results]
    # No references/ rows
    assert not any(p.startswith("wiki/references/") for p in paths), (
        f"--type entities leaked references/ rows: {paths}"
    )
    # references/some-ref.md (which would have hit TSMC) is excluded
    assert not any("some-ref.md" in p for p in paths), (
        f"some-ref.md should be filtered out by --type entities, got {paths}"
    )


def test_missing_summary_field_skipped(tmp_path):
    """Pages without `summary:` in frontmatter must NOT appear in candidates.

    concepts/missing-summary.md has title 'TSMC concept page without summary'
    and tag 'tsmc' — both would normally score against keyword 'TSMC' — but
    the absent summary field means the page is incomplete and must be
    skipped from results entirely.
    """
    mod = _load_module()
    vault = _build_vault_t2(tmp_path)

    results = mod.query(vault_root=vault, keywords=["TSMC"], top=10)

    paths = [r["path"] for r in results]
    assert not any("missing-summary.md" in p for p in paths), (
        f"missing-summary.md must be skipped (no summary field), got {paths}"
    )


def test_empty_keywords_returns_empty_array(tmp_path):
    """Empty keyword list (or empty string) must return [] without error.

    Regression pin: this assertion was incidentally green against T1's code
    (the `if not keywords_lc: return []` guard predates T2). Kept as a
    behavioral pin so future refactors can't silently change the empty-input
    contract from `[]` to e.g. all-pages-with-score-0.
    """
    mod = _load_module()
    vault = _build_vault_t2(tmp_path)

    # Empty list
    assert mod.query(vault_root=vault, keywords=[], top=5) == []
    # List of empty strings
    assert mod.query(vault_root=vault, keywords=[""], top=5) == []
