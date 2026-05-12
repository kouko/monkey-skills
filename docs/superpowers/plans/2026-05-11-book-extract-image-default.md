# book-extract: extract images by default + rewrite paths Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `epub_to_markdown.py`'s default behavior **actually preserve images** — extract image files to `<book>/images/` and rewrite all `<img>` references to inline Markdown `![alt](images/<file>)`. `--strip-images` remains the opt-out.

**Architecture:** Two-pass: (a) extract phase — filter EPUB manifest for `media-type^=image/`, write bytes to `<out_dir>/images/<safe-name>` (collision-resolved via SHA-1 suffix), build `dict[zip_abs_path → "images/<safe>"]`. (b) per-chapter rewrite phase — in XHTML BEFORE pandoc, rewrite `<img src="X">` srcs by resolving `X` against the chapter's ZIP directory and looking up the map. Pandoc then naturally emits `![alt](images/<safe>)` GFM syntax. No new CLI flag — `--strip-images` (existing) gates the entire process.

**Tech Stack:** Python stdlib only (`zipfile`, `xml.etree.ElementTree`, `re`, `hashlib`, `pathlib`), pandoc 3.x subprocess (already vendored), pytest for tests.

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `tsundoku/skills/book-extract/scripts/epub_to_markdown.py` | Modify | Add `extract_images()` + `rewrite_image_srcs()`; thread `image_manifest` through `parse_opf` return; wire into main flow |
| `tsundoku/skills/book-extract/tests/test_image_extraction.py` | Create | In-memory EPUB fixture builder + round-trip tests (default extract, `--strip-images` skip, collision handling, external URL pass-through) |
| `tsundoku/skills/book-extract/SKILL.md` | Modify | Update `--strip-images` row in option table (line 85) + quick-start example (line 140) + Known Quirks (line 228) + add new "Images" section explaining default |
| `tsundoku/skills/book-extract/README.md` | Modify | Mirror SKILL.md doc sync (lines 53, 65) |
| `tsundoku/skills/book-extract/README.ja.md` | Modify | Same, JP |
| `tsundoku/skills/book-extract/README.zh-TW.md` | Modify | Same, ZH-TW |

**Folder structure note:** `tests/` is a new single-level subfolder under `skills/book-extract/`, sibling of `scripts/`. Compliant with the project's flat-skill convention (no nested subfolders). All test runs use `PYTHONDONTWRITEBYTECODE=1` to avoid `__pycache__/` directories that would otherwise trip `validate-skill-folder-structure.sh`.

---

## Task 1: Test infrastructure — in-memory EPUB fixture builder

**Files:**
- Create: `tsundoku/skills/book-extract/tests/test_image_extraction.py`

- [ ] **Step 1: Write the fixture helper + first failing test**

Create `tsundoku/skills/book-extract/tests/test_image_extraction.py`:

```python
"""Round-trip tests for book-extract image handling.

Builds minimal EPUBs in-memory (no fixture files committed) and runs
epub_to_markdown.py against them, asserting on the resulting output dir.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from textwrap import dedent

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT = SKILL_DIR / "scripts" / "epub_to_markdown.py"


# ---------- minimal EPUB builder ----------


def _container_xml() -> str:
    return dedent("""\
        <?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
          <rootfiles>
            <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
          </rootfiles>
        </container>
    """)


def _opf(manifest_items: list[tuple[str, str, str]], spine_idrefs: list[str], title: str = "Test Book") -> str:
    """manifest_items: list of (id, href, media-type)."""
    manifest_xml = "\n".join(
        f'    <item id="{i}" href="{h}" media-type="{m}"/>' for (i, h, m) in manifest_items
    )
    spine_xml = "\n".join(f'    <itemref idref="{i}"/>' for i in spine_idrefs)
    return dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
          <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
            <dc:identifier id="bookid">test-book-001</dc:identifier>
            <dc:title>{title}</dc:title>
            <dc:language>en</dc:language>
            <dc:creator>Test Author</dc:creator>
          </metadata>
          <manifest>
            <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        {manifest_xml}
          </manifest>
          <spine toc="ncx">
        {spine_xml}
          </spine>
        </package>
    """)


def _ncx(chapters: list[tuple[str, str]]) -> str:
    """chapters: list of (label, href)."""
    nav_points = "\n".join(
        f"""    <navPoint id="np{i}" playOrder="{i + 1}">
      <navLabel><text>{label}</text></navLabel>
      <content src="{href}"/>
    </navPoint>"""
        for i, (label, href) in enumerate(chapters)
    )
    return dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
          <head><meta name="dtb:uid" content="test-book-001"/></head>
          <docTitle><text>Test Book</text></docTitle>
          <navMap>
        {nav_points}
          </navMap>
        </ncx>
    """)


def _xhtml(title: str, body: str) -> str:
    return dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head><title>{title}</title></head>
        <body>
        <h1>{title}</h1>
        {body}
        </body>
        </html>
    """)


def build_epub(out_path: Path, files: dict[str, bytes]) -> None:
    """Write a ZIP with mimetype first (uncompressed), then the rest."""
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", zipfile.ZIP_STORED)
        for name, data in files.items():
            zf.writestr(name, data)


PNG_1x1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c626001000000050001a5f645400000000049454e44ae42"
    "6082"
)


def make_basic_epub(tmp: Path) -> Path:
    """One chapter with one inline <img> reference."""
    epub = tmp / "basic.epub"
    files = {
        "META-INF/container.xml": _container_xml().encode(),
        "OEBPS/content.opf": _opf(
            manifest_items=[
                ("ch1", "Text/ch01.xhtml", "application/xhtml+xml"),
                ("img1", "Images/cat.png", "image/png"),
            ],
            spine_idrefs=["ch1"],
        ).encode(),
        "OEBPS/toc.ncx": _ncx([("Chapter One", "Text/ch01.xhtml")]).encode(),
        "OEBPS/Text/ch01.xhtml": _xhtml(
            "Chapter One",
            '<p>Here is a picture of a cat:</p>\n<p><img src="../Images/cat.png" alt="cat"/></p>',
        ).encode(),
        "OEBPS/Images/cat.png": PNG_1x1,
    }
    build_epub(epub, files)
    return epub


def run_extract(epub: Path, out_dir: Path, *extra_args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--epub", str(epub), "--out-dir", str(out_dir),
         "--no-subdir", "--quiet", *extra_args],
        capture_output=True, text=True, env=env, check=True,
    )


# ---------- tests ----------


def test_default_extracts_images_and_rewrites_path(tmp_path):
    epub = make_basic_epub(tmp_path)
    out_dir = tmp_path / "out"
    run_extract(epub, out_dir)

    # Image file extracted
    images = list((out_dir / "images").iterdir())
    assert len(images) == 1
    assert images[0].name == "cat.png"
    assert images[0].read_bytes() == PNG_1x1

    # Chapter markdown contains rewritten reference
    chapter_files = sorted(out_dir.glob("*.md"))
    chapter_files = [f for f in chapter_files if f.name != "index.md"]
    assert len(chapter_files) == 1
    md = chapter_files[0].read_text(encoding="utf-8")
    assert "![cat](images/cat.png)" in md
    # No stale relative reference left behind
    assert "../Images/cat.png" not in md
```

- [ ] **Step 2: Run test to verify it fails**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest tsundoku/skills/book-extract/tests/test_image_extraction.py::test_default_extracts_images_and_rewrites_path -v
```

Expected: FAIL — current script produces `out_dir` with no `images/` subdir; the assertion `(out_dir / "images").iterdir()` raises `FileNotFoundError`. Or the path assertion fails because the rewritten `images/cat.png` reference is absent.

- [ ] **Step 3: Add the remaining tests (still failing)**

Append to `test_image_extraction.py`:

```python
def test_strip_images_skips_extraction(tmp_path):
    epub = make_basic_epub(tmp_path)
    out_dir = tmp_path / "out"
    run_extract(epub, out_dir, "--strip-images")

    # No images/ dir created when stripped
    assert not (out_dir / "images").exists()

    # Chapter markdown has no image reference at all
    chapter_files = [f for f in out_dir.glob("*.md") if f.name != "index.md"]
    md = chapter_files[0].read_text(encoding="utf-8")
    assert "![" not in md
    assert "<img" not in md


def test_collision_renames_with_hash_suffix(tmp_path):
    """Two images with same basename at different paths must coexist."""
    epub = tmp_path / "collision.epub"
    files = {
        "META-INF/container.xml": _container_xml().encode(),
        "OEBPS/content.opf": _opf(
            manifest_items=[
                ("ch1", "Text/ch01.xhtml", "application/xhtml+xml"),
                ("img_a", "ImagesA/cover.png", "image/png"),
                ("img_b", "ImagesB/cover.png", "image/png"),
            ],
            spine_idrefs=["ch1"],
        ).encode(),
        "OEBPS/toc.ncx": _ncx([("Chapter One", "Text/ch01.xhtml")]).encode(),
        "OEBPS/Text/ch01.xhtml": _xhtml(
            "Chapter One",
            '<p><img src="../ImagesA/cover.png" alt="A"/></p>\n'
            '<p><img src="../ImagesB/cover.png" alt="B"/></p>',
        ).encode(),
        "OEBPS/ImagesA/cover.png": PNG_1x1,
        "OEBPS/ImagesB/cover.png": PNG_1x1 + b"\x00",  # distinct bytes
    }
    build_epub(epub, files)

    out_dir = tmp_path / "out"
    run_extract(epub, out_dir)

    images = sorted((out_dir / "images").iterdir())
    assert len(images) == 2
    names = [p.name for p in images]
    # One keeps basename, one gets hash suffix
    assert "cover.png" in names
    assert any(re.fullmatch(r"cover-[0-9a-f]{8}\.png", n) for n in names)

    # Markdown references both, with different paths
    md = next(f for f in out_dir.glob("*.md") if f.name != "index.md").read_text(encoding="utf-8")
    assert md.count("![A](images/") == 1
    assert md.count("![B](images/") == 1
    # Two distinct image paths in the markdown
    paths = set(re.findall(r"!\[[AB]\]\((images/[^)]+)\)", md))
    assert len(paths) == 2


def test_external_url_and_data_uri_passthrough(tmp_path):
    """http(s):// and data: URIs must not be rewritten or extracted."""
    epub = tmp_path / "external.epub"
    files = {
        "META-INF/container.xml": _container_xml().encode(),
        "OEBPS/content.opf": _opf(
            manifest_items=[("ch1", "Text/ch01.xhtml", "application/xhtml+xml")],
            spine_idrefs=["ch1"],
        ).encode(),
        "OEBPS/toc.ncx": _ncx([("Chapter One", "Text/ch01.xhtml")]).encode(),
        "OEBPS/Text/ch01.xhtml": _xhtml(
            "Chapter One",
            '<p><img src="https://example.com/remote.jpg" alt="remote"/></p>\n'
            '<p><img src="data:image/png;base64,iVBORw0K" alt="inline"/></p>',
        ).encode(),
    }
    build_epub(epub, files)

    out_dir = tmp_path / "out"
    run_extract(epub, out_dir)

    # No images/ dir (manifest had no image entries)
    assert not (out_dir / "images").exists() or not list((out_dir / "images").iterdir())

    md = next(f for f in out_dir.glob("*.md") if f.name != "index.md").read_text(encoding="utf-8")
    assert "https://example.com/remote.jpg" in md
    assert "data:image/png;base64,iVBORw0K" in md
```

- [ ] **Step 4: Run all tests to verify they fail in the expected ways**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest tsundoku/skills/book-extract/tests/test_image_extraction.py -v
```

Expected: 4 FAILs. The `default_extracts_images` test fails because no `images/` dir is created. `strip_images` test may PASS already (current behavior strips on flag). Collision and external tests fail because no extraction happens. Note any unexpected PASS — those reveal current default is partly correct (e.g., external URLs already pass through pandoc untouched).

- [ ] **Step 5: Commit the failing tests + skeleton**

Skip this step. Tests stay uncommitted until impl lands (Task 2) — commit single green commit per project convention (`feedback_commit_split_detection.md`: each commit green).

---

## Task 2: Image extraction + path rewrite implementation

**Files:**
- Modify: `tsundoku/skills/book-extract/scripts/epub_to_markdown.py:46-583`
- Test: `tsundoku/skills/book-extract/tests/test_image_extraction.py` (from Task 1)

- [ ] **Step 1: Add `hashlib` import + `extract_images()` function**

Modify `epub_to_markdown.py` line 47-57 (imports block). Add `hashlib`:

```python
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
```

Then insert new function immediately AFTER `parse_ncx` (currently ends at line 234) and BEFORE `# ---------- HTML pre-cleaning ----------` (line 237):

```python
# ---------- image extraction ----------


def extract_images(
    zf: zipfile.ZipFile,
    image_manifest: dict[str, str],
    out_dir: Path,
    log,
) -> dict[str, str]:
    """Extract image files from EPUB ZIP to <out_dir>/images/.

    image_manifest: {zip_abs_path: media_type} for items with media-type^=image/.
    Returns: {zip_abs_path: relative_path_from_out_dir} (e.g. "images/cat.png").

    Collisions on basename are resolved by appending an 8-char SHA-1 prefix of
    the full ZIP path (deterministic, stable across re-runs).
    """
    if not image_manifest:
        return {}
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, str] = {}
    used_names: set[str] = set()
    for zip_path in sorted(image_manifest):  # sorted: deterministic naming
        try:
            data = zf.read(zip_path)
        except KeyError:
            log(f"[extract] [skip-image-missing] {zip_path}")
            continue
        basename = Path(zip_path).name
        safe = basename
        if safe in used_names:
            h = hashlib.sha1(zip_path.encode("utf-8")).hexdigest()[:8]
            stem = Path(basename).stem
            ext = Path(basename).suffix
            safe = f"{stem}-{h}{ext}"
        used_names.add(safe)
        (images_dir / safe).write_bytes(data)
        result[zip_path] = f"images/{safe}"
    log(f"[extract] {len(result)} image(s) extracted to {images_dir}")
    return result
```

- [ ] **Step 2: Add `rewrite_image_srcs()` function**

Insert immediately after `extract_images()` (before `# ---------- HTML pre-cleaning ----------`):

```python
_IMG_SRC_RE = re.compile(
    r'(<img\b[^>]*?\bsrc\s*=\s*)(["\'])([^"\']*)(\2)',
    re.IGNORECASE,
)


def rewrite_image_srcs(
    xhtml: str,
    chapter_zip_dir: str,
    image_map: dict[str, str],
) -> str:
    """Rewrite <img src="..."> in XHTML to point at extracted images/ folder.

    Skips external (http/https) and data: URIs. Unknown paths (manifest miss)
    are left untouched. Resolution: relative srcs are joined against the
    chapter's ZIP directory before lookup.
    """
    if not image_map:
        return xhtml

    def replace(m: re.Match) -> str:
        prefix, quote, src, close = m.group(1), m.group(2), m.group(3), m.group(4)
        if not src or src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        abs_src = (
            os.path.normpath(os.path.join(chapter_zip_dir, src))
            if chapter_zip_dir
            else os.path.normpath(src)
        )
        if abs_src in image_map:
            return f"{prefix}{quote}{image_map[abs_src]}{close}"
        return m.group(0)

    return _IMG_SRC_RE.sub(replace, xhtml)
```

- [ ] **Step 3: Update `parse_opf()` to return image manifest**

Modify `parse_opf` signature + body (lines 136-197). The function currently builds `manifest` dict but doesn't expose image entries. Add image filter and return:

Change line 136 from:
```python
def parse_opf(zf: zipfile.ZipFile, opf_path: str) -> tuple[EpubMeta, list[SpineItem], str]:
    """Returns (metadata, spine, ncx_path_or_empty)."""
```
to:
```python
def parse_opf(zf: zipfile.ZipFile, opf_path: str) -> tuple[EpubMeta, list[SpineItem], str, dict[str, str]]:
    """Returns (metadata, spine, ncx_path_or_empty, image_manifest).

    image_manifest: {zip_abs_path: media_type} for items with media-type^=image/.
    """
```

Inside the function, after the existing `manifest` loop (line 168-176), add the image collector. Replace lines 165-176:

```python
    # Manifest: id → (href, mediatype); also collect image entries for extraction
    manifest: dict[str, tuple[str, str]] = {}
    image_manifest: dict[str, str] = {}
    ncx_id = ""
    for item in root.findall("opf:manifest/opf:item", NS):
        item_id = item.get("id") or ""
        href = item.get("href") or ""
        media_type = item.get("media-type") or ""
        manifest[item_id] = (href, media_type)
        if media_type == "application/x-dtbncx+xml":
            ncx_id = item_id
        if item.get("properties", "") == "nav":
            ncx_id = ncx_id or item_id  # EPUB3 nav fallback
        if media_type.startswith("image/"):
            abs_path = os.path.normpath(os.path.join(opf_dir, href)) if opf_dir else href
            image_manifest[abs_path] = media_type
```

Update the return statement (line 197):

```python
    return meta, spine_items, ncx_path, image_manifest
```

- [ ] **Step 4: Wire into `main()` flow**

Modify line 443 of `main()`. Change:
```python
        meta, spine, ncx_path = parse_opf(zf, opf_path)
```
to:
```python
        meta, spine, ncx_path, image_manifest = parse_opf(zf, opf_path)
```

Then immediately AFTER `out_dir.mkdir(parents=True, exist_ok=True)` (line 463) and BEFORE the `chapters: list[ChapterOut] = []` initialization (line 466), add image extraction:

```python
        # Extract images unless explicitly stripped
        image_map: dict[str, str] = {}
        if not args.strip_images:
            image_map = extract_images(zf, image_manifest, out_dir, log)
```

Then in the chapter loop (line 488-499), wire rewrite_image_srcs BETWEEN `preclean_xhtml` and `run_pandoc`. Change:

```python
            cleaned = preclean_xhtml(raw)
            try:
                md = run_pandoc(args.pandoc, cleaned)
```

to:

```python
            cleaned = preclean_xhtml(raw)
            if image_map:
                cleaned = rewrite_image_srcs(
                    cleaned, os.path.dirname(item.abs_path), image_map
                )
            try:
                md = run_pandoc(args.pandoc, cleaned)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest tsundoku/skills/book-extract/tests/test_image_extraction.py -v
```

Expected: 4 PASS.

If `test_default_extracts_images_and_rewrites_path` fails on the `![cat](images/cat.png)` check, inspect what pandoc actually emitted:
```bash
cat /tmp/<tmpdir>/out/01-Chapter-One.md
```
Common causes: pandoc inserted a leading space (`![cat]( images/cat.png )`) or wrapped the line. If found, loosen the assertion to `assert re.search(r'!\[cat\]\(\s*images/cat\.png\s*\)', md)` — but only after confirming via inspection.

- [ ] **Step 6: Smoke-test on a real EPUB**

```bash
ls ~/.cache/tsundoku/downloads/*.epub 2>/dev/null | head -1
# Pick one with images (likely any non-fiction book). If none available, skip.
EPUB=$(ls ~/.cache/tsundoku/downloads/*.epub 2>/dev/null | head -1)
if [ -n "$EPUB" ]; then
  TMPOUT=$(mktemp -d)
  python3 tsundoku/skills/book-extract/scripts/epub_to_markdown.py \
    --epub "$EPUB" --out-dir "$TMPOUT" --no-subdir --quiet
  echo "=== images extracted ==="
  ls -lh "$TMPOUT/images" 2>/dev/null | head -5
  echo "=== sample image references ==="
  grep -oh '!\[[^]]*\](images/[^)]*)' "$TMPOUT"/*.md | head -5
  echo "=== broken/un-rewritten image references (should be empty) ==="
  grep -E '!\[[^]]*\]\([^)]*\.(png|jpg|jpeg|gif|svg|webp)\)' "$TMPOUT"/*.md | \
    grep -v 'images/' | head -5
  rm -rf "$TMPOUT"
fi
```

Expected: `images/` dir populated, all image references in chapter markdown point to `images/<safe-name>`, the "broken/un-rewritten" check returns no rows (or only true external URLs, none).

- [ ] **Step 7: Commit**

```bash
git add tsundoku/skills/book-extract/scripts/epub_to_markdown.py \
        tsundoku/skills/book-extract/tests/test_image_extraction.py
git commit -m "$(cat <<'EOF'
feat(book-extract): extract images by default + rewrite paths to local images/

Previously, running epub_to_markdown.py without --strip-images preserved
image references in the form ![alt](OEBPS/Images/foo.jpg) — pointing at
paths that were never extracted to disk. Result: every chapter shipped
with broken links by default.

Now (default behavior):
- Image files in the EPUB manifest (media-type^=image/) are extracted
  to <out_dir>/images/ with collision-safe naming (SHA-1 suffix on
  basename clash).
- <img src="..."> in XHTML is rewritten to the extracted path before
  pandoc runs; pandoc emits inline ![alt](images/<safe>) GFM syntax.
- External URLs (http/https) and data: URIs are left untouched.
- SVG inline blocks remain stripped (existing behavior).

--strip-images (unchanged) skips the entire extraction + rewrite path,
matching the previous "no image clutter" preset.

Tests cover default extraction, --strip-images skip, basename collision
renaming, and external URL passthrough.
EOF
)"
```

---

## Task 3: Doc sync — SKILL.md

**Files:**
- Modify: `tsundoku/skills/book-extract/SKILL.md:85` (option table)
- Modify: `tsundoku/skills/book-extract/SKILL.md:140` (quick-start example)
- Modify: `tsundoku/skills/book-extract/SKILL.md:228-230` (Known Quirks)
- Modify: `tsundoku/skills/book-extract/SKILL.md` (insert new "Images" subsection under Conversion)

- [ ] **Step 1: Update option table row for `--strip-images`**

Find line 85:
```markdown
| `--strip-images` | drop image references (Markdown + raw `<img>`) — recommended for text-heavy books |
```

Replace with:
```markdown
| `--strip-images` | skip image extraction + drop all `![]()` and raw `<img>` references — for pure-text shipping (LLM distillation, plain-text vault) |
```

- [ ] **Step 2: Update quick-start example**

Find line 138-143:
```bash
bash ${CLAUDE_SKILL_DIR}/scripts/install_pandoc.sh >/dev/null
python3 ${CLAUDE_SKILL_DIR}/scripts/epub_to_markdown.py \
    --epub "$EPUB" --strip-images --strip-frontmatter --quiet
# → creates $TSUNDOKU_MARKDOWN_DIR/<title-slug>-<id8>/index.md + chapter files
# (= ~/.cache/tsundoku/markdown/<title-slug>-<id8>/...)
```

Replace with:
```bash
bash ${CLAUDE_SKILL_DIR}/scripts/install_pandoc.sh >/dev/null
python3 ${CLAUDE_SKILL_DIR}/scripts/epub_to_markdown.py \
    --epub "$EPUB" --strip-frontmatter --quiet
# → creates $TSUNDOKU_MARKDOWN_DIR/<title-slug>-<id8>/index.md + chapter files
# + images/ subdirectory (image references rewritten inline)
# (= ~/.cache/tsundoku/markdown/<title-slug>-<id8>/...)
#
# Pure-text shipping (LLM distillation only): add --strip-images
```

- [ ] **Step 3: Update Known Quirks "Image-only chapters" bullet**

Find line 228-230:
```markdown
- **Image-only chapters**: some EPUBs have a "chapter" that's just a cover
  illustration. With `--strip-images` these become empty (5-20 tokens) and
  may merge with `--merge-small`.
```

Replace with:
```markdown
- **Image-only chapters**: some EPUBs have a "chapter" that's just a cover
  illustration. By default the image is extracted to `images/` and a
  short `![](images/cover.jpg)` line remains. With `--strip-images` these
  chapters become empty (5-20 tokens) and may merge with `--merge-small`.
```

- [ ] **Step 4: Add "Images" subsection**

Insert after the option table (after current line 90) and before `### Output layout` (current line 92):

```markdown
### Images

By default, image files referenced by the EPUB are extracted alongside
the chapter Markdown:

```
out-dir/<book>/
├── images/
│   ├── cover.jpg
│   ├── ch03-fig1.png        ← basename preserved when unique
│   └── cover-9f1c2a3b.svg   ← SHA-1 suffix on basename collision
├── 01-cover.md              ← contains `![](images/cover.jpg)`
├── 03-chapter-01.md         ← contains `![Fig 1](images/ch03-fig1.png)`
...
```

All image references in chapter Markdown use inline GFM syntax
`![alt](images/<file>)`, relative to each chapter file. External URLs
(`http(s)://`) and `data:` URIs are passed through untouched (not
extracted, not rewritten). Inline `<svg>` blocks are stripped (covers
and decorative SVG); SVG referenced via `<img src="cover.svg">` is
extracted normally.

**Disk cost**: typically +5 MB per book; image-heavy design / business
books may reach 50 MB. To opt out for LLM-only distillation use
`--strip-images`.
```

- [ ] **Step 5: Verify rendered markdown looks right**

```bash
grep -n 'strip-images\|images/' tsundoku/skills/book-extract/SKILL.md | head -20
```

Expected: `--strip-images` row matches new text, quick-start example has no `--strip-images` flag, new "Images" subsection present, Known Quirks bullet updated. No stale references to "broken" or "dropped by default".

---

## Task 4: Doc sync — READMEs (× 3 languages)

**Files:**
- Modify: `tsundoku/skills/book-extract/README.md:53,65`
- Modify: `tsundoku/skills/book-extract/README.ja.md:53,65`
- Modify: `tsundoku/skills/book-extract/README.zh-TW.md:53,65`

- [ ] **Step 1: Update `README.md`**

Find line 53 (quick-start fragment):
```bash
    --strip-images --strip-frontmatter
```

Replace with:
```bash
    --strip-frontmatter
```

Find line 65 (option table row):
```markdown
| `--strip-images` | drop image references — recommended for text-heavy books |
```

Replace with:
```markdown
| `--strip-images` | skip image extraction + drop all references — for pure-text shipping |
```

If the README has a separate "Output layout" or "Defaults" section that mentions image handling, also add a one-line note: "Images are extracted to `<book>/images/` by default; opt out with `--strip-images`."

- [ ] **Step 2: Update `README.ja.md`**

Find line 53:
```bash
    --strip-images --strip-frontmatter
```

Replace with:
```bash
    --strip-frontmatter
```

Find line 65:
```markdown
| `--strip-images` | 画像参照を破棄 — 文章中心の本に推奨 |
```

Replace with:
```markdown
| `--strip-images` | 画像の抽出をスキップし参照もすべて削除 — 純テキスト出力用 |
```

Add nearby (in matching section): "画像はデフォルトで `<book>/images/` に抽出されます。LLM 蒸留など純テキストが必要な場合は `--strip-images` を指定してください。"

- [ ] **Step 3: Update `README.zh-TW.md`**

Find line 53:
```bash
    --strip-images --strip-frontmatter
```

Replace with:
```bash
    --strip-frontmatter
```

Find line 65:
```markdown
| `--strip-images` | 丟棄圖片 reference — 文字為主的書建議使用 |
```

Replace with:
```markdown
| `--strip-images` | 跳過圖片萃取並丟棄所有 reference — 純文字輸出用 |
```

Add nearby: "圖片預設會萃取到 `<book>/images/`。若只需要純文字（LLM 蒸餾、純文字 vault），可加上 `--strip-images`。"

- [ ] **Step 4: Verify all three READMEs are in sync**

```bash
grep -n 'strip-images\|images/' tsundoku/skills/book-extract/README*.md
```

Expected: each README has matching structure (quick-start without `--strip-images`, option-table row describing skip behavior, default-behavior note about `images/` directory).

- [ ] **Step 5: Commit**

```bash
git add tsundoku/skills/book-extract/SKILL.md \
        tsundoku/skills/book-extract/README.md \
        tsundoku/skills/book-extract/README.ja.md \
        tsundoku/skills/book-extract/README.zh-TW.md
git commit -m "$(cat <<'EOF'
docs(book-extract): sync SKILL.md + READMEs for image-extraction default

Reflects the new default behavior (image files extracted to
<book>/images/, references rewritten inline as ![alt](images/<file>)).

Changes:
- Option table: --strip-images now described as opt-out for pure-text
  output, not the recommended default.
- Quick-start example: drops --strip-images from the canonical command.
- New "Images" subsection in SKILL.md documenting the images/ layout,
  collision handling, external-URL passthrough, and disk-cost
  expectations.
- Known Quirks "Image-only chapters" bullet updated to reflect new
  default (image extracted, short reference line remains).
- README.md / README.ja.md / README.zh-TW.md mirror the same updates in
  each language, per repo convention (PR #150 i18n rule).
EOF
)"
```

---

## Task 5: Final verification

- [ ] **Step 1: Re-run all tests in worktree**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest tsundoku/skills/book-extract/tests/ -v
```

Expected: 4 PASS, 0 FAIL.

- [ ] **Step 2: Confirm folder structure compliance**

```bash
find tsundoku/skills/book-extract -type d
```

Expected: only `tsundoku/skills/book-extract` itself + `scripts/` + `tests/`. No nested subdirs. No `__pycache__/` leaked.

- [ ] **Step 3: Verify commit log**

```bash
git log --oneline main..HEAD
```

Expected: exactly 2 commits — `feat(book-extract): ...` and `docs(book-extract): ...`. Both with kebab-case scopes per CC convention.

- [ ] **Step 4: Confirm CI scope format**

```bash
git log main..HEAD --format='%s' | while read s; do
  echo "$s" | grep -E '^(feat|fix|docs|chore|refactor|test)\([a-z][a-z0-9-]*\): .+' || echo "BAD: $s"
done
```

Expected: no "BAD:" lines.

---

## Self-Review

**Spec coverage:**
- ✅ Predefault preserves images → Task 2 extracts to `<book>/images/`
- ✅ Inline `![alt](path)` syntax → Task 2 rewrites src in XHTML, pandoc emits GFM inline format
- ✅ Book-level shared `<book>/images/` → Task 2 `images_dir = out_dir / "images"`
- ✅ External URL passthrough → Task 2 `rewrite_image_srcs` skip
- ✅ Collision handling → Task 2 SHA-1 suffix
- ✅ `--strip-images` remains as opt-out → Task 2 guard `if not args.strip_images`
- ✅ SKILL.md sync → Task 3
- ✅ Tri-language README sync → Task 4
- ✅ Tests cover all paths → Task 1

**Placeholder scan:** Done — every step contains exact code, exact line numbers, exact commit messages. No TBDs.

**Type consistency:**
- `extract_images()` returns `dict[str, str]` (zip_abs_path → "images/<file>"); both Task 2 Step 4 wiring and `rewrite_image_srcs` consume it as `image_map: dict[str, str]`. ✅
- `parse_opf()` signature change from 3-tuple to 4-tuple is locked in Task 2 Step 3 and unpacked in Task 2 Step 4. ✅
- Test helper `make_basic_epub` returns `Path`; `run_extract` accepts `Path`. ✅

---

## Execution Notes

- pandoc 3.9.0.2 confirmed available (`/opt/homebrew/bin/pandoc`)
- Worktree branch: `worktree-feat+book-extract-image-default` already created at `.claude/worktrees/feat+book-extract-image-default`
- 2 commits (feat + docs), each green per `feedback_commit_split_detection.md` — no separate test-first commit because that would leave the impl commit testing nothing new
- CI scope `book-extract` is kebab-case ✅
- `PYTHONDONTWRITEBYTECODE=1` everywhere to avoid `__pycache__/` tripping the skill-structure hook (`feedback_pycache_hook_blocks_edits.md`)
