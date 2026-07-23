"""Tests for wiki_lint_check.py — mechanical wiki lint validator.

Check semantics SSOT: obsidian/skills/wiki-lint/references/lint-checks.md
(L01/L02/L03/L04/L07/L14 + severity map per wiki-lint SKILL.md).
No registered REQ-ids exist for this arc — @req tags intentionally omitted.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "wiki_lint_check.py"


# ---------------------------------------------------------------- helpers

def write_page(wiki_root, rel, text):
    p = wiki_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def run_lint(wiki_root, *extra):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(wiki_root), *extra],
        capture_output=True,
        text=True,
    )


def parse_jsonl(stdout):
    return [json.loads(line) for line in stdout.splitlines() if line.strip()]


def violations_of(records):
    return [r for r in records if r.get("type") == "violation"]


def counters_of(records):
    return [r for r in records if r.get("type") == "counters"]


def build_clean_wiki(tmp_path):
    """Minimal valid wiki: entity + concept + reference, alias link,
    anchor link, display-alias link, and an out-of-wiki `## Source`
    wikilink (L07 exemption)."""
    w = tmp_path / "wiki"
    write_page(w, "entities/acme-corp.md", """---
title: Acme Corp
type: wiki-entity
domain: business
status: developing
updated: 2026-07-01
tags: [company]
sources_count: 1
summary: A demo entity.
aliases: [艾克米公司]
---

## Summary

Acme makes things. See [[bandit-algorithms]].

## Key Facts

- Founded 1990

## Connections

- [[bandit-algorithms]]
""")
    write_page(w, "concepts/bandit-algorithms.md", """---
title: Bandit Algorithms
type: wiki-concept
domain: ml
status: developing
updated: 2026-07-01
tags: [ml]
sources_count: 1
summary: Multi-armed bandit methods.
---

## Summary

Alias link [[艾克米公司]], anchor [[acme-corp#Key Facts]], display [[acme-corp|Acme]].

## Key Facts

- Explore vs exploit

## Connections

- [[acme-corp]]
""")
    write_page(w, "references/2026-01-01-some-source.md", """---
title: Some Source
type: wiki-reference
source_path: references/topic/some-source.md
date: 2026-01-01
ingested: 2026-01-02
contributes_to: [acme-corp]
tags: [source]
summary: Citation record.
---

## Source

[[some-source]]

## TL;DR

Summary of source.

## Key Contributions

- Contributed a fact.
""")
    return w


def build_seeded_wiki(tmp_path):
    """Clean wiki + one seeded violation per covered check."""
    w = build_clean_wiki(tmp_path)
    # L01: missing `domain` and `status`
    write_page(w, "entities/missing-fields.md", """---
title: Missing Fields
type: wiki-entity
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: Fields are missing.
---

## Summary

Body.

## Key Facts

- f

## Connections

- [[acme-corp]]
""")
    # L02: summary > 200 chars
    long_summary = "x" * 250
    write_page(w, "entities/long-summary.md", f"""---
title: Long Summary
type: wiki-entity
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: {long_summary}
---

## Summary

Body.

## Key Facts

- f

## Connections

- [[acme-corp]]
""")
    # L03: missing `## Connections`
    write_page(w, "concepts/no-connections.md", """---
title: No Connections
type: wiki-concept
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: Section missing.
---

## Summary

Body.

## Key Facts

- f
""")
    # L04: path prefix + .md extension + backtick-wrapped (3 violations)
    write_page(w, "concepts/bad-links.md", """---
title: Bad Links
type: wiki-concept
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: Malformed wikilinks.
---

## Summary

Path [[entities/foo]] and ext [[bar.md]] and code `[[acme-corp]]`.

## Key Facts

- f

## Connections

- [[acme-corp]]
""")
    # L07: broken link (no close match) + typo link (Levenshtein 1)
    write_page(w, "concepts/broken-link.md", """---
title: Broken Link
type: wiki-concept
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: Broken wikilinks.
---

## Summary

See [[totally-nonexistent-zzz]] and [[acme-corb]].

## Key Facts

- f

## Connections

- [[acme-corp]]
""")
    # L14 error: path-prefixed source wikilink
    write_page(w, "references/bad-ref.md", """---
title: Bad Ref
type: wiki-reference
source_path: references/foo/bar.md
date: 2026-01-01
ingested: 2026-01-02
contributes_to: [acme-corp]
tags: [source]
summary: Path-prefixed source link.
---

## Source

[[references/foo/bar]]

## TL;DR

t

## Key Contributions

- c
""")
    # L14 error: .md-suffixed source wikilink
    write_page(w, "references/ext-ref.md", """---
title: Ext Ref
type: wiki-reference
source_path: references/topic/ext-source.md
date: 2026-01-01
ingested: 2026-01-02
contributes_to: [acme-corp]
tags: [source]
summary: Extension-suffixed source link.
---

## Source

[[ext-source.md]]

## TL;DR

t

## Key Contributions

- c
""")
    # L14 warning: basename mismatch vs source_path stem
    write_page(w, "references/mismatch-ref.md", """---
title: Mismatch Ref
type: wiki-reference
source_path: references/topic/real-name.md
date: 2026-01-01
ingested: 2026-01-02
contributes_to: [acme-corp]
tags: [source]
summary: Stale source link.
---

## Source

[[wrong-name]]

## TL;DR

t

## Key Contributions

- c
""")
    # L14 warning (missing `## Source`) — also L03 error (required section)
    write_page(w, "references/no-source-ref.md", """---
title: No Source Ref
type: wiki-reference
source_path: references/topic/no-source.md
date: 2026-01-01
ingested: 2026-01-02
contributes_to: [acme-corp]
tags: [source]
summary: Missing Source section.
---

## TL;DR

t

## Key Contributions

- c
""")
    # L14 warning: `## Source` present but contains no wikilink
    write_page(w, "references/empty-source-ref.md", """---
title: Empty Source Ref
type: wiki-reference
source_path: references/topic/empty-source.md
date: 2026-01-01
ingested: 2026-01-02
contributes_to: [acme-corp]
tags: [source]
summary: Source has no wikilink.
---

## Source

plain prose, no link here

## TL;DR

t

## Key Contributions

- c
""")
    return w


EXPECTED_SEEDED = sorted([
    ("L01", "entities/missing-fields.md"),
    ("L02", "entities/long-summary.md"),
    ("L03", "concepts/no-connections.md"),
    ("L04", "concepts/bad-links.md"),
    ("L04", "concepts/bad-links.md"),
    ("L04", "concepts/bad-links.md"),
    ("L07", "concepts/broken-link.md"),
    ("L07", "concepts/broken-link.md"),
    ("L14", "references/bad-ref.md"),
    ("L14", "references/ext-ref.md"),
    ("L14", "references/mismatch-ref.md"),
    ("L14", "references/no-source-ref.md"),
    ("L03", "references/no-source-ref.md"),
    ("L14", "references/empty-source-ref.md"),
])


# ------------------------------------------------------------------ tests

def test_detects_seeded_violations(tmp_path):
    w = build_seeded_wiki(tmp_path)
    r = run_lint(w)
    assert r.returncode == 1, r.stderr
    records = parse_jsonl(r.stdout)
    viols = violations_of(records)
    got = sorted((v["check_id"], v["file"]) for v in viols)
    assert got == EXPECTED_SEEDED
    # JSONL shape: every violation carries the full field set
    for v in viols:
        assert {"type", "check_id", "severity", "file", "line", "detail"} <= set(v)
        assert v["severity"] in ("error", "warning")
    # L01 detail names the missing fields
    l01 = next(v for v in viols if v["check_id"] == "L01")
    assert "domain" in l01["detail"] and "status" in l01["detail"]
    # L07 typo suggestion via Levenshtein <= 2
    l07_details = [v["detail"] for v in viols if v["check_id"] == "L07"]
    assert any("acme-corp" in d for d in l07_details)
    # severity map: L14 basename-mismatch + missing/empty-Source are warnings,
    # path/extension are errors (SKILL.md severity line)
    l14 = {v["file"]: v["severity"] for v in viols if v["check_id"] == "L14"}
    assert l14["references/bad-ref.md"] == "error"
    assert l14["references/ext-ref.md"] == "error"
    assert l14["references/mismatch-ref.md"] == "warning"
    assert l14["references/no-source-ref.md"] == "warning"
    assert l14["references/empty-source-ref.md"] == "warning"
    # summary record is last and its counts add up
    summary = records[-1]
    assert summary["type"] == "summary"
    assert summary["violations"] == len(viols)
    assert summary["errors"] + summary["warnings"] == len(viols)
    assert summary["by_check"]["L04"] == 3


def test_clean_wiki_exits_zero(tmp_path):
    """Clean fixture: alias link, anchor link, display link, and the
    reference `## Source` out-of-wiki link must all pass (L07 alias
    matching + Source-section exemption per SSOT)."""
    w = build_clean_wiki(tmp_path)
    r = run_lint(w)
    assert r.returncode == 0, r.stdout + r.stderr
    records = parse_jsonl(r.stdout)
    assert violations_of(records) == []
    summary = records[-1]
    assert summary["type"] == "summary"
    assert summary["violations"] == 0


def test_l07_filename_alias_collision(tmp_path):
    """A link matching both a filename and another page's alias = 2+
    inventory matches -> collision error listing candidates."""
    w = build_clean_wiki(tmp_path)
    write_page(w, "entities/dup-target.md", """---
title: Dup Target
type: wiki-entity
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: Target page.
---

## Summary

Body [[acme-corp]].

## Key Facts

- f

## Connections

- [[acme-corp]]
""")
    write_page(w, "entities/other-page.md", """---
title: Other Page
type: wiki-entity
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: Carries a colliding alias.
aliases: [dup-target]
---

## Summary

Body [[dup-target]].

## Key Facts

- f

## Connections

- [[acme-corp]]
""")
    r = run_lint(w)
    assert r.returncode == 1
    viols = violations_of(parse_jsonl(r.stdout))
    collisions = [v for v in viols if v["check_id"] == "L07"]
    assert len(collisions) == 1  # the [[dup-target]] link in other-page.md
    v = collisions[0]
    assert v["severity"] == "error"
    assert v["file"] == "entities/other-page.md"
    assert "dup-target.md" in v["detail"]
    assert "other-page.md" in v["detail"]


def test_conservation_counters(tmp_path):
    w = tmp_path / "wiki"
    write_page(w, "entities/tiny.md", """---
title: Tiny
type: wiki-entity
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: Tiny page.
---

## Summary

One two three [[x]].

## Key Facts

- fact

## Connections

none
""")
    r = run_lint(w)
    records = parse_jsonl(r.stdout)
    ctrs = {c["file"]: c for c in counters_of(records)}
    tiny = ctrs["entities/tiny.md"]
    # body tokens: ##,Summary,One,two,three,[[x]].,##,Key,Facts,-,fact,
    #              ##,Connections,none = 14
    assert tiny["words"] == 14
    assert tiny["links"] == 1
    assert tiny["headings"] == 3


def test_help_lists_llm_lane_out_of_scope():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    text = r.stdout.lower()
    assert "out-of-scope" in text or "out of scope" in text
    for check in ("L05", "L06", "L08", "L09", "L10",
                  "L11", "L12", "L13", "L15"):
        assert check.lower() in text, f"--help must list {check}"


def test_empty_and_block_scalar_summary(tmp_path):
    """R2 fix 1: `summary:` with empty value must fire L02 (not silently
    become a list and dodge both L01 and L02); a block-scalar value must
    surface a PARSE violation, never be swallowed as a literal string."""
    w = tmp_path / "wiki"
    write_page(w, "entities/empty-summary.md", """---
title: Empty Summary
type: wiki-entity
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary:
---

## Summary

Body.

## Key Facts

- f

## Connections

none
""")
    write_page(w, "entities/block-scalar.md", """---
title: Block Scalar
type: wiki-entity
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: >-
  a folded block scalar the minimal parser cannot read
---

## Summary

Body.

## Key Facts

- f

## Connections

none
""")
    r = run_lint(w)
    assert r.returncode == 1
    viols = violations_of(parse_jsonl(r.stdout))
    got = {(v["check_id"], v["file"]) for v in viols}
    assert ("L02", "entities/empty-summary.md") in got
    parse_v = [v for v in viols if v["check_id"] == "PARSE"
               and v["file"] == "entities/block-scalar.md"]
    assert len(parse_v) == 1
    assert parse_v[0]["severity"] == "error"
    # PARSE owns the block-scalar defect; L02 must not double-report it
    assert ("L02", "entities/block-scalar.md") not in got


def test_non_utf8_file_isolated(tmp_path):
    """R2 fix 2: a single non-UTF-8 file must yield a PARSE violation for
    that file and the scan must continue — no traceback, no aborted run."""
    w = build_clean_wiki(tmp_path)
    (w / "entities" / "latin1.md").write_bytes(
        b"---\ntitle: caf\xe9\n---\nbody\n")
    r = run_lint(w)
    assert r.returncode == 1, r.stderr
    assert "Traceback" not in r.stderr
    records = parse_jsonl(r.stdout)
    parse_v = [v for v in violations_of(records)
               if v["check_id"] == "PARSE" and v["file"] == "entities/latin1.md"]
    assert len(parse_v) == 1
    assert parse_v[0]["severity"] == "error"
    # the rest of the wiki was still scanned
    scanned = {c["file"] for c in counters_of(records)}
    assert "entities/acme-corp.md" in scanned
    assert records[-1]["type"] == "summary"


def test_nfd_filename_nfc_link(tmp_path):
    """R2 fix 3: macOS stores filenames in NFD; links are typed in NFC.
    Both sides must be NFC-normalized or every CJK/accented link would
    be a false L07 broken-link (and would feed the T3 auto-fixer junk)."""
    import unicodedata
    nfd_slug = unicodedata.normalize("NFD", "café")
    assert nfd_slug != "café"  # sanity: really NFD
    w = tmp_path / "wiki"
    write_page(w, f"entities/{nfd_slug}.md", """---
title: Café
type: wiki-entity
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: Accented page.
---

## Summary

Body [[linker-page]].

## Key Facts

- f

## Connections

- [[linker-page]]
""")
    write_page(w, "concepts/linker-page.md", """---
title: Linker
type: wiki-concept
domain: d
status: developing
updated: 2026-07-01
tags: [t]
sources_count: 0
summary: Links with NFC.
---

## Summary

NFC link: [[café]].

## Key Facts

- f

## Connections

- [[café]]
""")
    r = run_lint(w)
    viols = violations_of(parse_jsonl(r.stdout))
    assert [v for v in viols if v["check_id"] == "L07"] == []
    assert r.returncode == 0, r.stdout


def test_stdlib_only_imports():
    """Plugin self-containment: no third-party and no repo-level imports."""
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "relative (repo-level) import found"
            mods.add(node.module.split(".")[0])
    non_stdlib = mods - set(sys.stdlib_module_names)
    assert not non_stdlib, f"non-stdlib imports: {sorted(non_stdlib)}"
