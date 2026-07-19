---
name: ixbrl-dom-traversal-drops-nested-facts
description: Parsing inline-XBRL (iXBRL = XBRL tags embedded in HTML, e.g. Taiwan MOPS filings) by DOM/HTML-tree traversal silently drops the majority of facts — ix:nonFraction/nonNumeric nested inside <td> are discarded by HTML tree-repair. Extract with regex or iterparse over the ix: tags, never a DOM walk, and guard with an exact whole-file fact-count assertion.
type: gotcha
origin: branch xbrl-tw (2026-07-19) — TW iXBRL ingestion; lxml DOM iter yielded 387 facts for TSMC 2330 2024Q3 vs the true 2002 (~85% dropped)
---

Taiwan financial statements (and iXBRL generally) embed each tagged fact as
`<ix:nonFraction …>value</ix:nonFraction>` **inside table cells**. Feeding
the document to an HTML DOM parser (`lxml.html`, `html.parser` tree) and
walking the tree silently drops ~85% of them — HTML tree-repair discards the
`ix:` elements nested in `<td>`. For TSMC 2330 2024Q3: DOM traversal = **387**
facts; the true count = **2002**. The parser "works" and returns plausible
data, so the loss is invisible without an independent count.

**Why:** a count that looks reasonable (387 is not zero) reads as success;
only an *exact* expected-count assertion against a known filing exposes the
drop. This is the same class as [[count-only-regression-pins-false-confidence]]
but the failure is in the extractor, not the test.

**How to apply:** extract iXBRL facts with **regex or `xml.etree.iterparse`
over the `ix:nonFraction`/`ix:nonNumeric` tags directly** — not a DOM walk.
Pin a test to the exact total fact count of a real committed fixture (e.g.
`assert len(parse(fixture)) == 2002`); that single assertion is the guard
against a silent regression back to tree traversal. Related scaling gotcha:
iXBRL numeric scale is driven by the `scale` attribute, NOT `decimals`
(decimals is precision metadata) — a fact with decimals≠scale breaks
decimals-driven scaling.
