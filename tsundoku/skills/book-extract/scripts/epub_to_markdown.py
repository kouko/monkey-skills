#!/usr/bin/env python3
"""Convert an EPUB into chunked-by-chapter Markdown for LLM ingestion.

Designed for 400+ page expository books where chapter-level chunking matters
for two-pass distillation (outline → skill).

Pipeline:
  1. Open EPUB as ZIP.
  2. Find OPF via META-INF/container.xml.
  3. Read OPF spine + manifest (ordered list of XHTML files).
  4. Read NCX (or EPUB3 nav) for chapter labels.
  5. For each spine item:
       - extract XHTML
       - pre-clean HTML noise (kobo spans, svgs, scripts, empty divs)
       - run pandoc XHTML → GFM Markdown
       - post-clean (collapse blank lines, drop image references if asked)
       - write to <out_dir>/NN-<slug>.md with H1 = chapter label
  6. Write index.md (TOC w/ links + token estimates) + metadata.json.

Usage:
  epub_to_markdown.py --epub PATH --out-dir DIR [options]

Options:
  --pandoc PATH         pandoc binary (default: $PANDOC or `pandoc` on PATH)
  --strip-images        drop image references in Markdown
  --strip-frontmatter   skip spine items whose label matches common
                        front-matter patterns (書封 / 目錄 / 版權 / cover /
                        copyright / contents / dedication / colophon /
                        publication / 出版資訊 / 出版品)
  --strip-backmatter    skip spine items whose label matches common
                        back-matter patterns (索引 / 附錄 / 譯後記 / 致謝 /
                        index / acknowledg / about-the-author)
                        NOTE: 附錄 / 譯後記 are kept by default for
                        non-fiction (often essential to the argument);
                        explicit flag required to drop.
  --merge-small N       merge chapters smaller than N tokens into the
                        previous chapter (default: 0 = no merging)
  --quiet               only print final summary to stdout

Exit codes:
  0 success
  1 conversion error
  2 argument or precondition error
"""
from __future__ import annotations

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


# ---------- helpers ----------


NS = {
    "container": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
    "ncx": "http://www.daisy.org/z3986/2005/ncx/",
    "xhtml": "http://www.w3.org/1999/xhtml",
}

FRONT_MATTER_PAT = re.compile(
    r"(書封|封面|目錄|目次|版權|出版資訊|出版品|cover|toc|contents|"
    r"dedication|colophon|frontmatter|publication|copyright)",
    re.IGNORECASE,
)
BACK_MATTER_PAT = re.compile(
    r"(索引|致謝|謝辭|index|acknowledg|about[-_ ]the[-_ ]author)",
    re.IGNORECASE,
)


def slugify(text: str, max_len: int = 60) -> str:
    """Filename-safe slug. Keeps CJK, drops punctuation/spaces."""
    text = unicodedata.normalize("NFKC", text or "").strip()
    text = re.sub(r"[/\\:?\"<>|*\s]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len] or "untitled"


def estimate_tokens(text: str) -> int:
    """Rough CJK-aware token estimate.

    Heuristic: CJK char ~ 0.6 tokens, ASCII word ~ 1.3 tokens.
    Good enough for budget planning.
    """
    cjk = sum(
        1
        for ch in text
        if 0x3000 <= ord(ch) <= 0x9FFF or 0xAC00 <= ord(ch) <= 0xD7A3
    )
    ascii_chars = sum(1 for ch in text if ord(ch) < 128)
    ascii_words = ascii_chars / 5  # avg word ~5 chars including space
    return int(cjk * 0.6 + ascii_words * 1.3)


# ---------- EPUB structure ----------


@dataclass
class SpineItem:
    idref: str
    href: str  # relative to OPF dir
    abs_path: str  # zip path
    label: str = ""  # from NCX/nav, may be empty
    order: int = 0


@dataclass
class EpubMeta:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    language: str = ""
    publisher: str = ""
    identifier: str = ""
    date: str = ""


def find_opf(zf: zipfile.ZipFile) -> str:
    with zf.open("META-INF/container.xml") as f:
        tree = ET.parse(f)
    rootfile = tree.find(".//container:rootfile", NS)
    if rootfile is None:
        raise RuntimeError("META-INF/container.xml has no rootfile")
    return rootfile.get("full-path") or ""


def parse_opf(zf: zipfile.ZipFile, opf_path: str) -> tuple[EpubMeta, list[SpineItem], str, dict[str, str]]:
    """Returns (metadata, spine, ncx_path_or_empty, image_manifest).

    image_manifest: {zip_abs_path: media_type} for items with media-type^=image/.
    """
    with zf.open(opf_path) as f:
        tree = ET.parse(f)
    root = tree.getroot()
    opf_dir = os.path.dirname(opf_path)

    # Metadata
    meta = EpubMeta()
    md = root.find("opf:metadata", NS)
    if md is not None:
        for elem in md:
            tag = elem.tag.split("}")[-1]
            text = (elem.text or "").strip()
            if not text:
                continue
            if tag == "title":
                meta.title = meta.title or text
            elif tag == "creator":
                meta.authors.append(text)
            elif tag == "language":
                meta.language = text
            elif tag == "publisher":
                meta.publisher = text
            elif tag == "identifier":
                meta.identifier = meta.identifier or text
            elif tag == "date":
                meta.date = meta.date or text

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

    # Spine: ordered list of idrefs
    spine_items: list[SpineItem] = []
    spine = root.find("opf:spine", NS)
    if spine is None:
        raise RuntimeError("OPF has no spine")
    spine_ncx_id = spine.get("toc") or ncx_id
    for i, ref in enumerate(spine.findall("opf:itemref", NS)):
        idref = ref.get("idref") or ""
        if idref not in manifest:
            continue
        href, _ = manifest[idref]
        abs_path = os.path.normpath(os.path.join(opf_dir, href)) if opf_dir else href
        spine_items.append(SpineItem(idref=idref, href=href, abs_path=abs_path, order=i))

    ncx_path = ""
    if spine_ncx_id and spine_ncx_id in manifest:
        ncx_href, _ = manifest[spine_ncx_id]
        ncx_path = os.path.normpath(os.path.join(opf_dir, ncx_href)) if opf_dir else ncx_href

    return meta, spine_items, ncx_path, image_manifest


def parse_ncx(zf: zipfile.ZipFile, ncx_path: str) -> dict[str, str]:
    """Return mapping of href (with optional #anchor stripped) → label."""
    result: dict[str, str] = {}
    if not ncx_path:
        return result
    try:
        with zf.open(ncx_path) as f:
            tree = ET.parse(f)
    except KeyError:
        return result
    ncx_dir = os.path.dirname(ncx_path)
    # NCX (EPUB2)
    for nav_point in tree.findall(".//ncx:navPoint", NS):
        label_node = nav_point.find("ncx:navLabel/ncx:text", NS)
        content_node = nav_point.find("ncx:content", NS)
        if label_node is None or content_node is None:
            continue
        label = (label_node.text or "").strip()
        src = content_node.get("src") or ""
        href = src.split("#")[0]
        abs_href = os.path.normpath(os.path.join(ncx_dir, href)) if ncx_dir else href
        if abs_href and abs_href not in result:
            result[abs_href] = label

    # EPUB3 nav (also try, harmless if NCX path was actually nav)
    for a in tree.findall(".//xhtml:nav//xhtml:a", NS):
        href = a.get("href") or ""
        href = href.split("#")[0]
        if not href:
            continue
        abs_href = os.path.normpath(os.path.join(ncx_dir, href)) if ncx_dir else href
        label = "".join(a.itertext()).strip()
        if abs_href and abs_href not in result and label:
            result[abs_href] = label
    return result


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


_IMG_TAG_RE = re.compile(r"<img\b([^>]*?)/?>", re.IGNORECASE)
_ATTR_RE = re.compile(r'\b([\w:-]+)\s*=\s*(["\'])(.*?)\2', re.DOTALL)


def _extract_attr(attrs: str, name: str) -> str:
    """Return the value of `name` attribute (case-insensitive), or empty."""
    name_lower = name.lower()
    for m in _ATTR_RE.finditer(attrs):
        if m.group(1).lower() == name_lower:
            return m.group(3)
    return ""


def _html_attr_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def rewrite_image_srcs(
    xhtml: str,
    chapter_zip_dir: str,
    image_map: dict[str, str],
) -> str:
    """Rewrite + normalize <img> tags so pandoc emits clean ![alt](src) syntax.

    - Resolves relative src against chapter's ZIP dir, then looks up image_map.
    - Skips external (http/https) and data: URIs (no rewrite, no extraction).
    - Strips all attributes except src + alt — pandoc preserves <img> as raw
      HTML when extra attrs (class, role, style, width, ...) are present,
      which would defeat the inline ![alt](src) requirement.
    - Unknown src (not in image_map, not external) is preserved untouched but
      attributes are still stripped so the tag converts cleanly.
    """
    def replace(m: re.Match) -> str:
        attrs = m.group(1)
        src = _extract_attr(attrs, "src")
        if not src:
            return m.group(0)
        alt = _extract_attr(attrs, "alt")
        # Decide final src
        if src.startswith(("http://", "https://", "data:")):
            final_src = src
        else:
            abs_src = (
                os.path.normpath(os.path.join(chapter_zip_dir, src))
                if chapter_zip_dir
                else os.path.normpath(src)
            )
            final_src = image_map.get(abs_src, src)
        return f'<img src="{_html_attr_escape(final_src)}" alt="{_html_attr_escape(alt)}"/>'

    return _IMG_TAG_RE.sub(replace, xhtml)


# ---------- HTML pre-cleaning ----------


_SVG_WITH_IMAGE_RE = re.compile(
    r'<svg\b[^>]*>\s*<image\b[^>]*?(?:xlink:)?href\s*=\s*["\']([^"\']+)["\'][^>]*/?>\s*</svg>',
    re.DOTALL | re.IGNORECASE,
)
_ANCHOR_WRAPPING_IMG_RE = re.compile(
    r'<a\b([^>]*?)>(\s*<img\b[^>]*?/?>\s*)</a>',
    re.DOTALL | re.IGNORECASE,
)
_HREF_ATTR_RE = re.compile(r'\bhref\s*=\s*(["\'])(.*?)\1', re.IGNORECASE | re.DOTALL)


def preclean_xhtml(xhtml: str) -> str:
    """Strip kobo-specific markup, SVG blocks, scripts, empty wrappers."""
    # 1. Unwrap <svg><image xlink:href="X"/></svg> → <img src="X"/> so the
    #    SVG-kill below doesn't destroy image references. EPUBs commonly
    #    embed images this way to control aspect ratio; without this hoist,
    #    the image file gets extracted but no Markdown reference survives.
    xhtml = _SVG_WITH_IMAGE_RE.sub(
        lambda m: f'<img src="{m.group(1)}" alt=""/>', xhtml
    )
    # 2. Strip non-href attrs from <a> tags wrapping a single <img>. EPUBs
    #    use <a class="ref" id="back-N"><img/></a> for footnote-glyph links;
    #    pandoc preserves <a> with class as raw HTML, dragging <img> with
    #    it. With only href left, pandoc emits clean [![alt](src)](href).
    def _strip_anchor_attrs(m: re.Match) -> str:
        href_m = _HREF_ATTR_RE.search(m.group(1))
        if not href_m:
            return m.group(0)
        return f'<a href="{href_m.group(2)}">{m.group(2)}</a>'
    xhtml = _ANCHOR_WRAPPING_IMG_RE.sub(_strip_anchor_attrs, xhtml)
    # kill remaining (decorative) SVG blocks
    xhtml = re.sub(r"<svg\b[^>]*>.*?</svg>", "", xhtml, flags=re.DOTALL | re.IGNORECASE)
    xhtml = re.sub(r"<image\b[^/>]*/?>", "", xhtml, flags=re.IGNORECASE)
    # kill scripts and styles
    xhtml = re.sub(r"<script\b[^>]*>.*?</script>", "", xhtml, flags=re.DOTALL | re.IGNORECASE)
    xhtml = re.sub(r"<style\b[^>]*>.*?</style>", "", xhtml, flags=re.DOTALL | re.IGNORECASE)
    # unwrap koboSpan
    xhtml = re.sub(
        r"<span\b[^>]*\bclass=\"koboSpan\"[^>]*>(.*?)</span>",
        r"\1",
        xhtml,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return xhtml


# ---------- pandoc invocation ----------


def run_pandoc(pandoc: str, xhtml: str) -> str:
    """Run pandoc once, XHTML → GFM Markdown."""
    proc = subprocess.run(
        [
            pandoc,
            "--from=html",
            "--to=gfm",
            "--wrap=none",
            "--markdown-headings=atx",
        ],
        input=xhtml,
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


# ---------- markdown post-cleaning ----------


def postclean_markdown(md: str, strip_images: bool) -> str:
    # FIRST: strip leading full-width / NBSP / half-width indents
    md = re.sub(r"^[　  ]+", "", md, flags=re.MULTILINE)
    # THEN: strip pandoc hard-linebreak markers (lines that are only `\`)
    md = re.sub(r"^\\\s*$", "", md, flags=re.MULTILINE)
    if strip_images:
        md = re.sub(r"!\[[^\]]*\]\([^)]*\)\n?", "", md)
        md = re.sub(r"<img\b[^>]*/?>(?:</img>)?", "", md, flags=re.IGNORECASE)
    # strip stray empty html wrappers pandoc passes through
    md = re.sub(r"<div\b[^>]*>\s*", "", md)
    md = re.sub(r"\s*</div>", "", md)
    md = re.sub(r"<span[^>]*></span>", "", md)
    md = re.sub(r"<span\b[^>]*>(.*?)</span>", r"\1", md, flags=re.DOTALL)
    md = re.sub(r"^\{[^\}]*\}\s*$", "", md, flags=re.MULTILINE)  # pandoc attr blocks
    # collapse 3+ blank lines into 2 (last, after all stripping)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


# ---------- per-chapter writer ----------


@dataclass
class ChapterOut:
    index: int
    label: str
    href: str
    filename: str
    tokens: int
    chars: int
    skipped: str = ""  # reason if skipped


def write_chapter(
    out_dir: Path,
    idx: int,
    label: str,
    href: str,
    md_body: str,
    strip_images: bool,
) -> ChapterOut:
    md_body = postclean_markdown(md_body, strip_images=strip_images)
    if not label:
        label = Path(href).stem
    title_line = f"# {label}\n\n"
    if not md_body.startswith("# "):
        md_body = title_line + md_body
    fname = f"{idx:02d}-{slugify(label)}.md"
    path = out_dir / fname
    path.write_text(md_body, encoding="utf-8")
    return ChapterOut(
        index=idx,
        label=label,
        href=href,
        filename=fname,
        tokens=estimate_tokens(md_body),
        chars=len(md_body),
    )


# ---------- index renderer ----------


def render_index(meta: EpubMeta, chapters: list[ChapterOut]) -> str:
    parts = [f"# {meta.title or 'Untitled'}"]
    if meta.authors:
        parts.append(f"**Author(s)**: {', '.join(meta.authors)}")
    bits = []
    if meta.publisher:
        bits.append(f"**Publisher**: {meta.publisher}")
    if meta.date:
        bits.append(f"**Date**: {meta.date[:10]}")
    if meta.language:
        bits.append(f"**Language**: {meta.language}")
    if meta.identifier:
        bits.append(f"**ID**: `{meta.identifier}`")
    if bits:
        parts.append(" | ".join(bits))
    parts.append("")
    parts.append(f"**Chapters**: {len(chapters)}")
    total_tokens = sum(c.tokens for c in chapters if not c.skipped)
    parts.append(f"**Estimated total tokens**: {total_tokens:,}")
    parts.append("")
    parts.append("## Contents")
    parts.append("")
    parts.append("| # | Chapter | Tokens | File |")
    parts.append("|---|---------|--------|------|")
    for c in chapters:
        if c.skipped:
            parts.append(f"| {c.index} | _{c.label}_ | — | _skipped: {c.skipped}_ |")
        else:
            parts.append(
                f"| {c.index} | {c.label} | {c.tokens:,} | "
                f"[{c.filename}]({c.filename}) |"
            )
    parts.append("")
    return "\n".join(parts)


# ---------- main ----------


def main() -> int:
    p = argparse.ArgumentParser(
        description="EPUB → chunked Markdown for LLM ingestion.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--epub", required=True, help="path to .epub file")
    p.add_argument("--out-dir", default=None,
                   help="output ROOT directory; per-book subdir is auto-created "
                        "(see --no-subdir to disable). "
                        "Default: $TSUNDOKU_MARKDOWN_DIR or "
                        "$TSUNDOKU_ROOT/cache/markdown or "
                        "$XDG_CACHE_HOME/tsundoku/markdown or "
                        "~/.cache/tsundoku/markdown")
    p.add_argument("--no-subdir", action="store_true",
                   help="disable per-book subdir; write straight into --out-dir")
    p.add_argument("--pandoc", default=os.environ.get("PANDOC", "pandoc"))
    p.add_argument("--strip-images", action="store_true")
    p.add_argument("--strip-frontmatter", action="store_true")
    p.add_argument("--strip-backmatter", action="store_true")
    p.add_argument("--merge-small", type=int, default=0,
                   help="merge chapters smaller than N tokens (default 0 = off)")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    epub_path = Path(args.epub).resolve()
    if not epub_path.exists():
        print(f"error: epub not found: {epub_path}", file=sys.stderr)
        return 2

    # Resolve out_dir: explicit --out-dir wins; else TSUNDOKU_MARKDOWN_DIR;
    # else XDG cache fallback chain.
    if args.out_dir:
        out_root = Path(args.out_dir).resolve()
    elif "TSUNDOKU_MARKDOWN_DIR" in os.environ:
        out_root = Path(os.environ["TSUNDOKU_MARKDOWN_DIR"]).resolve()
    elif "TSUNDOKU_ROOT/cache" in os.environ:
        out_root = (Path(os.environ["TSUNDOKU_ROOT/cache"]) / "markdown").resolve()
    else:
        cache_home = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
        out_root = (Path(cache_home) / "tsundoku" / "markdown").resolve()
    # out_dir is finalized AFTER parsing metadata so the per-book subdir
    # name can come from the EPUB's title.
    out_dir: Path = out_root

    # Locate pandoc
    if subprocess.run(["which", args.pandoc], capture_output=True).returncode != 0:
        if not Path(args.pandoc).exists():
            print(f"error: pandoc not found at {args.pandoc}", file=sys.stderr)
            print("       brew install pandoc, or download from", file=sys.stderr)
            print("       https://github.com/jgm/pandoc/releases/latest", file=sys.stderr)
            return 2

    log = (lambda *a, **kw: None) if args.quiet else (lambda *a, **kw: print(*a, **kw, file=sys.stderr))

    log(f"[extract] reading {epub_path}")
    with zipfile.ZipFile(epub_path) as zf:
        opf_path = find_opf(zf)
        log(f"[extract] OPF: {opf_path}")
        meta, spine, ncx_path, image_manifest = parse_opf(zf, opf_path)
        log(f"[extract] {len(spine)} spine items, NCX: {ncx_path or '(none)'}")
        ncx_labels = parse_ncx(zf, ncx_path) if ncx_path else {}
        log(f"[extract] NCX labels: {len(ncx_labels)}")

        # Annotate spine with NCX labels
        for item in spine:
            item.label = ncx_labels.get(item.abs_path, "")

        # Resolve final out_dir (per-book subdir unless --no-subdir).
        # Slug priority: title (+ kobodl id8 suffix if present in filename),
        #                fall back to EPUB filename stem.
        if args.no_subdir:
            out_dir = out_root
        else:
            slug_base = slugify(meta.title) if meta.title else slugify(epub_path.stem)
            id8_match = re.search(r"\b([0-9a-f]{8})$", epub_path.stem)
            if id8_match:
                slug_base = f"{slug_base}-{id8_match.group(1)}"
            out_dir = out_root / slug_base
        out_dir.mkdir(parents=True, exist_ok=True)
        log(f"[extract] output dir: {out_dir}")

        # Extract images unless explicitly stripped
        image_map: dict[str, str] = {}
        if not args.strip_images:
            image_map = extract_images(zf, image_manifest, out_dir, log)

        chapters: list[ChapterOut] = []
        idx = 0
        for item in spine:
            label = item.label or Path(item.href).stem
            # filter front/back matter if requested
            if args.strip_frontmatter and FRONT_MATTER_PAT.search(label):
                log(f"[extract] [skip-front] {label}")
                idx += 1
                chapters.append(ChapterOut(
                    index=idx, label=label, href=item.href, filename="",
                    tokens=0, chars=0, skipped="frontmatter",
                ))
                continue
            if args.strip_backmatter and BACK_MATTER_PAT.search(label):
                log(f"[extract] [skip-back] {label}")
                idx += 1
                chapters.append(ChapterOut(
                    index=idx, label=label, href=item.href, filename="",
                    tokens=0, chars=0, skipped="backmatter",
                ))
                continue

            try:
                with zf.open(item.abs_path) as f:
                    raw = f.read().decode("utf-8", errors="replace")
            except KeyError:
                log(f"[extract] [skip-missing] {item.abs_path}")
                continue
            cleaned = preclean_xhtml(raw)
            if image_map:
                cleaned = rewrite_image_srcs(
                    cleaned, os.path.dirname(item.abs_path), image_map
                )
            try:
                md = run_pandoc(args.pandoc, cleaned)
            except subprocess.CalledProcessError as e:
                log(f"[extract] [pandoc-error] {item.href}: {e.stderr.strip()[:200]}")
                continue

            if not md.strip():
                log(f"[extract] [skip-empty] {label}")
                continue

            idx += 1
            ch = write_chapter(
                out_dir, idx, label, item.href, md, strip_images=args.strip_images
            )
            log(f"[extract] [chapter] {idx:02d}. {label} → {ch.filename} ({ch.tokens:,} tok)")
            chapters.append(ch)

    # Optional merge of small chapters
    if args.merge_small > 0 and len(chapters) > 1:
        merged: list[ChapterOut] = []
        for ch in chapters:
            if (
                merged
                and not ch.skipped
                and not merged[-1].skipped
                and ch.tokens < args.merge_small
            ):
                # Append ch's content into merged[-1]'s file
                prev = merged[-1]
                prev_path = out_dir / prev.filename
                ch_path = out_dir / ch.filename
                if prev_path.exists() and ch_path.exists():
                    extra = ch_path.read_text(encoding="utf-8")
                    prev_path.write_text(
                        prev_path.read_text(encoding="utf-8").rstrip() + "\n\n" + extra,
                        encoding="utf-8",
                    )
                    ch_path.unlink()
                    prev.tokens += ch.tokens
                    prev.chars += ch.chars
                    log(f"[extract] [merged] {ch.label} → {prev.label}")
                    continue
            merged.append(ch)
        chapters = merged
        # reindex sequentially
        for i, ch in enumerate(chapters, 1):
            ch.index = i

    # Write index.md
    index_md = render_index(meta, chapters)
    (out_dir / "index.md").write_text(index_md, encoding="utf-8")

    # Write metadata.json
    md_meta = {
        "title": meta.title,
        "authors": meta.authors,
        "language": meta.language,
        "publisher": meta.publisher,
        "identifier": meta.identifier,
        "date": meta.date,
        "source_epub": str(epub_path),
        "chapters": [
            {
                "index": c.index,
                "label": c.label,
                "filename": c.filename,
                "tokens": c.tokens,
                "chars": c.chars,
                "skipped": c.skipped,
            }
            for c in chapters
        ],
        "total_tokens": sum(c.tokens for c in chapters if not c.skipped),
    }
    (out_dir / "metadata.json").write_text(
        json.dumps(md_meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Final summary
    total_chap = sum(1 for c in chapters if not c.skipped)
    total_tok = sum(c.tokens for c in chapters if not c.skipped)
    print(f"output: {out_dir}")
    print(f"chapters: {total_chap} written, {len(chapters) - total_chap} skipped")
    print(f"total tokens (estimate): {total_tok:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
