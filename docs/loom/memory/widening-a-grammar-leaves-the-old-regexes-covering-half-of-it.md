---
name: widening-a-grammar-leaves-the-old-regexes-covering-half-of-it
description: When a language gains a new token class, every regex written against the old class keeps matching and silently stops covering the new half — no test fails, because the old cases still pass; `r1 --> r2 & r3` satisfied BOTH a multi-destination refusal and a boundary check that were each written against `[A-Z]`, and was still wrong; after widening a grammar, grep for every pattern that encodes the old endpoint/token shape and re-decide each one, rather than waiting for the shapes nobody thought to write
type: practice
origin: 2026-08-19 cot-explain arc (dev-workflow 2.27.0) — the diagram edge grammar gained subgraph ids alongside node ids; two guards kept their `[A-Z]` patterns and left the new form unpoliced
---

Widening a grammar feels additive: the old sentences still parse, the old
tests still pass, and the new form works. What is invisible is that every
regex written against the old token shape has quietly become a **partial**
check — it still fires on the cases it always fired on, so nothing looks
broken.

The concrete failure: an edge endpoint used to be a node id, one capital
letter. The language gained subgraph ids (`r1`, `c2`). The parser was
updated. Two guards were not:

- a refusal of mermaid's multi-destination form, matching
  `[A-Z]\s*&\s*[A-Z]`
- a boundary check classifying endpoints by membership in a node-to-group
  map, where "not a node" was treated as "is a subgraph"

`r1 -->|…| r2 & r3` then satisfied both of them and was still wrong — the
multi-destination refusal did not see it, the boundary check saw two
subgraphs and approved, and the third row's edge carried no label at all.
A typo'd id (`r9`) was accepted for the same reason: "not a node" and "does
not exist" were the same branch.

**Why the tests do not catch it.** Every existing test uses the old token
shape, so every one of them still passes. The suite's coverage of the new
half is exactly the tests written for the new feature, and those are written
by the person who just changed the parser — who is thinking about the happy
path, not about which unrelated regex three hundred lines away also encodes
the endpoint shape.

**How to apply:** when a token class is widened, treat it as a sweep, not an
addition. Grep for the old shape as a literal — `[A-Z]`, `\d+`, whatever
encoded it — and for each hit decide explicitly: does this need the wider
class, or is it deliberately narrow? Write that decision down at the site.
And when a classifier tests membership to decide "which kind is this",
check that its domain really has two values — "not an X" is not "is a Y"
once there are three possibilities, one of which is *invalid*.

Related: [[a-stronger-guard-makes-the-fallback-beneath-it-untestable]],
[[changing-what-a-token-is-defeats-downstream-guards]],
[[a-narrowing-that-leaves-a-substring-passes-every-containment-pin]].
