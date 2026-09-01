---
name: 2026-09-01-adjudication-render-always-embeds-mermaid-bundle
description: adjudication_render.py doc mode emits the whole base64 mermaid bundle and its initialize call unconditionally, so a document with zero mermaid fences still ships a multi-megabyte page that is 99% unused script
status: open
origin: 2026-09-01 — measured by the orchestrator on branch loom-script-refactor-phase3 while rendering that arc's brief view
start: event — the next edit to loom-code/scripts/adjudication_render.py, or the next time a rendered document view is too large for the surface it is being delivered on
---

`render_doc()` in `loom-code/scripts/adjudication_render.py` calls
`_load_bundled_mermaid()` on every invocation and interpolates its result
into the page template. That result is a
`<script src="data:application/javascript;base64,…">` carrying the entire
bundled Mermaid library plus a paired `<script>mermaid.initialize(…)</script>`.
Neither the units nor the rendered markdown are consulted first, so the
bundle ships whether or not any unit contains a mermaid fence.

**How it was measured.** The brief view produced for the
`loom-script-refactor-phase3` arc contains no diagrams at all — its
`## Diagrams` section explicitly declares that none are needed — and the
rendered file was still **4,786,423 characters**, of which **4,754,803**
were that one script element: 99.3% of the page. Deleting the script
element and its paired initialize call from the output left **31,541
characters** with the rendered content unchanged and the
`<meta name="generator" content="loom-code-adjudication-render/0.109.0">`
stamp intact. The only residue was a `div.rendition .mermaid` CSS rule in
the stylesheet, which is inert. Reproduce by rendering any diagram-free
units file and comparing the byte count before and after stripping the two
script tags.

**Why it matters.** A 4.8 MB page for a diagram-free document is a real
delivery cost: it is slow to move, awkward to attach or paste, and it can
exceed a surface's size ceiling for content that needs none of it.
Separately, Claude artifacts render Mermaid natively from markdown fences
and `<pre class="mermaid">` blocks, so on that delivery surface the
embedded bundle is redundant even for a document that *does* contain
diagrams.

**Scope — this is a payload-size defect, not a correctness one.** The
rendered document is correct either way; nothing about the content,
escaping, or the generator stamp is wrong. Only the size is.

**What a fix looks like.** Make the emission conditional: inspect the
split units (or the rendered HTML) for a mermaid fence, and interpolate
the bundle plus its initialize call only when one is present, keeping the
two tags emitted together as today so a page never carries the call
without the library. The existing "unreadable bundle → emit neither tag"
path already proves the template tolerates an empty `mermaid_script`. A
per-surface switch (skip the bundle when the target renders Mermaid
itself) is a possible second step, but the unconditional-emission fix is
the one that stands on its own.
