"""Round-trip tests for book-extract image handling.

Builds minimal EPUBs in-memory (no fixture files committed) and runs
epub_to_markdown.py against them, asserting on the resulting output dir.
"""
from __future__ import annotations

import filecmp
import hashlib
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT = SKILL_DIR / "scripts" / "epub_to_markdown.py"


# ---------- minimal EPUB builder ----------
#
# Plain string concatenation, no textwrap.dedent — f-string interpolation of
# multi-line substitutions breaks dedent's common-prefix computation.


def _container_xml() -> str:
    return (
        '<?xml version="1.0"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '  <rootfiles>\n'
        '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
        '  </rootfiles>\n'
        '</container>\n'
    )


def _opf(manifest_items: list[tuple[str, str, str]], spine_idrefs: list[str], title: str = "Test Book") -> str:
    """manifest_items: list of (id, href, media-type)."""
    manifest_xml = "\n".join(
        f'    <item id="{i}" href="{h}" media-type="{m}"/>' for (i, h, m) in manifest_items
    )
    spine_xml = "\n".join(f'    <itemref idref="{i}"/>' for i in spine_idrefs)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">\n'
        '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        '    <dc:identifier id="bookid">test-book-001</dc:identifier>\n'
        f'    <dc:title>{title}</dc:title>\n'
        '    <dc:language>en</dc:language>\n'
        '    <dc:creator>Test Author</dc:creator>\n'
        '  </metadata>\n'
        '  <manifest>\n'
        '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>\n'
        f'{manifest_xml}\n'
        '  </manifest>\n'
        '  <spine toc="ncx">\n'
        f'{spine_xml}\n'
        '  </spine>\n'
        '</package>\n'
    )


def _ncx(chapters: list[tuple[str, str]]) -> str:
    """chapters: list of (label, href)."""
    nav_points = "\n".join(
        f'  <navPoint id="np{i}" playOrder="{i + 1}">\n'
        f'    <navLabel><text>{label}</text></navLabel>\n'
        f'    <content src="{href}"/>\n'
        f'  </navPoint>'
        for i, (label, href) in enumerate(chapters)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n'
        '  <head><meta name="dtb:uid" content="test-book-001"/></head>\n'
        '  <docTitle><text>Test Book</text></docTitle>\n'
        '  <navMap>\n'
        f'{nav_points}\n'
        '  </navMap>\n'
        '</ncx>\n'
    )


def _xhtml(title: str, body: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml">\n'
        f'<head><title>{title}</title></head>\n'
        '<body>\n'
        f'<h1>{title}</h1>\n'
        f'{body}\n'
        '</body>\n'
        '</html>\n'
    )


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
        "OEBPS/ImagesB/cover.png": PNG_1x1 + b"\x00",
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


def test_svg_wrapped_image_unwrapped_to_inline_md(tmp_path):
    """EPUBs commonly wrap images in <svg><image xlink:href="..."/></svg>.
    These must survive the SVG-kill and end up as ![alt](images/<file>)."""
    epub = tmp_path / "svg_wrapped.epub"
    files = {
        "META-INF/container.xml": _container_xml().encode(),
        "OEBPS/content.opf": _opf(
            manifest_items=[
                ("ch1", "Text/ch01.xhtml", "application/xhtml+xml"),
                ("img1", "Images/fig.png", "image/png"),
            ],
            spine_idrefs=["ch1"],
        ).encode(),
        "OEBPS/toc.ncx": _ncx([("Chapter One", "Text/ch01.xhtml")]).encode(),
        "OEBPS/Text/ch01.xhtml": _xhtml(
            "Chapter One",
            '<p>Figure below:</p>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink" '
            'version="1.1" width="100%" height="100%" viewBox="0 0 1417 2000">\n'
            '  <image width="1417" height="2000" xlink:href="../Images/fig.png"/>\n'
            '</svg>',
        ).encode(),
        "OEBPS/Images/fig.png": PNG_1x1,
    }
    build_epub(epub, files)

    out_dir = tmp_path / "out"
    run_extract(epub, out_dir)

    # Image extracted
    assert (out_dir / "images" / "fig.png").read_bytes() == PNG_1x1

    # Markdown has inline image syntax (NOT broken / NOT raw <svg> surviving)
    md = next(f for f in out_dir.glob("*.md") if f.name != "index.md").read_text(encoding="utf-8")
    assert re.search(r"!\[[^\]]*\]\(images/fig\.png\)", md), \
        f"expected ![](images/fig.png), got:\n{md}"
    assert "<svg" not in md.lower()
    assert "xlink:href" not in md


def test_img_with_extra_attrs_normalized(tmp_path):
    """<img src="X" class="fit" role="presentation"/> must produce ![](images/X)
    in markdown — pandoc otherwise preserves class/role as raw HTML <img>."""
    epub = tmp_path / "attrs.epub"
    files = {
        "META-INF/container.xml": _container_xml().encode(),
        "OEBPS/content.opf": _opf(
            manifest_items=[
                ("ch1", "Text/ch01.xhtml", "application/xhtml+xml"),
                ("img1", "Images/fig.png", "image/png"),
            ],
            spine_idrefs=["ch1"],
        ).encode(),
        "OEBPS/toc.ncx": _ncx([("Chapter One", "Text/ch01.xhtml")]).encode(),
        "OEBPS/Text/ch01.xhtml": _xhtml(
            "Chapter One",
            '<p><img src="../Images/fig.png" class="fit" role="presentation" alt="diagram"/></p>',
        ).encode(),
        "OEBPS/Images/fig.png": PNG_1x1,
    }
    build_epub(epub, files)

    out_dir = tmp_path / "out"
    run_extract(epub, out_dir)

    md = next(f for f in out_dir.glob("*.md") if f.name != "index.md").read_text(encoding="utf-8")
    assert "![diagram](images/fig.png)" in md, \
        f"expected ![diagram](images/fig.png), got:\n{md}"
    # No raw <img> survivors carrying class/role attributes
    assert "<img" not in md.lower()


def test_anchor_wrapped_image_unwraps_to_nested_md(tmp_path):
    """<a class="ref" id="..."><img src="..."/></a> footnote-glyph pattern.
    Pandoc preserves <a> with class as raw HTML, dragging <img> with it.
    Must normalize <a> to bare href so pandoc emits [![alt](src)](href)."""
    epub = tmp_path / "anchor.epub"
    files = {
        "META-INF/container.xml": _container_xml().encode(),
        "OEBPS/content.opf": _opf(
            manifest_items=[
                ("ch1", "Text/ch01.xhtml", "application/xhtml+xml"),
                ("img1", "Images/note.jpg", "image/jpeg"),
            ],
            spine_idrefs=["ch1"],
        ).encode(),
        "OEBPS/toc.ncx": _ncx([("Chapter One", "Text/ch01.xhtml")]).encode(),
        "OEBPS/Text/ch01.xhtml": _xhtml(
            "Chapter One",
            '<p>See footnote <a href="A-32.xhtml#foot-21" id="back-21" class="ref">'
            '<img src="../Images/note.jpg" class="pw" role="presentation"/></a>.</p>',
        ).encode(),
        "OEBPS/Images/note.jpg": PNG_1x1,
    }
    build_epub(epub, files)

    out_dir = tmp_path / "out"
    run_extract(epub, out_dir)

    md = next(f for f in out_dir.glob("*.md") if f.name != "index.md").read_text(encoding="utf-8")
    # Image reference appears in nested-link markdown form
    assert "[![](images/note.jpg)](A-32.xhtml#foot-21)" in md, \
        f"expected nested markdown image-link, got:\n{md}"
    # No raw <img> or <a class= survivors
    assert "<img" not in md.lower()
    assert 'class="ref"' not in md


def test_extracted_image_bytes_match_source(tmp_path):
    """Extracted image file must be byte-for-byte identical to the EPUB
    manifest entry — no transcoding, no truncation."""
    epub = tmp_path / "bytes.epub"
    # Use a non-trivial blob (PNG_1x1 + appended bytes) so any truncation
    # or encoding artifact would be detectable.
    blob = PNG_1x1 + b"trailing-marker-bytes-\x00\x01\x02\xff"
    files = {
        "META-INF/container.xml": _container_xml().encode(),
        "OEBPS/content.opf": _opf(
            manifest_items=[
                ("ch1", "Text/ch01.xhtml", "application/xhtml+xml"),
                ("img1", "Images/blob.png", "image/png"),
            ],
            spine_idrefs=["ch1"],
        ).encode(),
        "OEBPS/toc.ncx": _ncx([("Chapter One", "Text/ch01.xhtml")]).encode(),
        "OEBPS/Text/ch01.xhtml": _xhtml(
            "Chapter One",
            '<p><img src="../Images/blob.png" alt="blob"/></p>',
        ).encode(),
        "OEBPS/Images/blob.png": blob,
    }
    build_epub(epub, files)

    out_dir = tmp_path / "out"
    run_extract(epub, out_dir)

    extracted = (out_dir / "images" / "blob.png").read_bytes()
    assert extracted == blob
    assert hashlib.sha256(extracted).hexdigest() == hashlib.sha256(blob).hexdigest()


def test_idempotent_rerun_same_epub(tmp_path):
    """Running twice on the same EPUB into separate out_dirs must produce
    byte-identical output (chapter md, images, metadata.json, index.md)."""
    epub = make_basic_epub(tmp_path)
    out_a = tmp_path / "out_a"
    out_b = tmp_path / "out_b"
    run_extract(epub, out_a)
    run_extract(epub, out_b)

    # Compare directory trees recursively
    cmp = filecmp.dircmp(out_a, out_b)
    assert cmp.left_only == [], f"only in run A: {cmp.left_only}"
    assert cmp.right_only == [], f"only in run B: {cmp.right_only}"
    assert cmp.diff_files == [], f"differing files: {cmp.diff_files}"
    # Confirm sub-dirs (images/) match too
    sub_cmp = filecmp.dircmp(out_a / "images", out_b / "images")
    assert sub_cmp.diff_files == [], f"differing image files: {sub_cmp.diff_files}"


def test_same_image_referenced_from_multiple_chapters(tmp_path):
    """One image referenced from N chapters — extracted once, all chapter
    md files reference the same images/<file> path."""
    epub = tmp_path / "shared.epub"
    files = {
        "META-INF/container.xml": _container_xml().encode(),
        "OEBPS/content.opf": _opf(
            manifest_items=[
                ("ch1", "Text/ch01.xhtml", "application/xhtml+xml"),
                ("ch2", "Text/ch02.xhtml", "application/xhtml+xml"),
                ("ch3", "Text/ch03.xhtml", "application/xhtml+xml"),
                ("img1", "Images/shared.png", "image/png"),
            ],
            spine_idrefs=["ch1", "ch2", "ch3"],
        ).encode(),
        "OEBPS/toc.ncx": _ncx([
            ("Chapter One", "Text/ch01.xhtml"),
            ("Chapter Two", "Text/ch02.xhtml"),
            ("Chapter Three", "Text/ch03.xhtml"),
        ]).encode(),
        "OEBPS/Text/ch01.xhtml": _xhtml("Chapter One", '<p><img src="../Images/shared.png" alt="s"/></p>').encode(),
        "OEBPS/Text/ch02.xhtml": _xhtml("Chapter Two", '<p><img src="../Images/shared.png" alt="s"/></p>').encode(),
        "OEBPS/Text/ch03.xhtml": _xhtml("Chapter Three", '<p><img src="../Images/shared.png" alt="s"/></p>').encode(),
        "OEBPS/Images/shared.png": PNG_1x1,
    }
    build_epub(epub, files)

    out_dir = tmp_path / "out"
    run_extract(epub, out_dir)

    # Image extracted exactly once
    images = list((out_dir / "images").iterdir())
    assert len(images) == 1
    assert images[0].name == "shared.png"

    # All 3 chapter mds reference it
    chapter_files = sorted(f for f in out_dir.glob("*.md") if f.name != "index.md")
    assert len(chapter_files) == 3
    for f in chapter_files:
        assert "![s](images/shared.png)" in f.read_text(encoding="utf-8")


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
