# Why these rules exist

The rules live in `SKILL.md`. This file holds the evidence behind them —
what was measured, what failed, and what the failure cost. Read it when a
rule looks arbitrary, or before proposing to relax one.

Every rule here was bought by a failure. None was reasoned out in
advance.

## The fidelity rounds

One source — a dense engineering brief — was summarised and checked six
times. Each round: a fresh agent reconstructed the reasoning from the
generated page alone; a second agent compared that reconstruction against
the source without ever seeing the page; a third pass checked the reverse
direction for invention.

| Round | Verdict | What was lost |
|---|---|---|
| 1 | FAIL | The reader would have implemented the variant the source explicitly rejected |
| 2 | FAIL | Three of four repaired; the delivery-side obligation vanished whole |
| 3 | FAIL | All four repaired; lost "no output file written" and a carve-out |
| 4 | FAIL | All six repaired; lost which manifest the version is read from, the exit code, and why a placeholder was rejected |
| 5 | FAIL | **Produced confident wrong answers** rather than gaps |
| 6 | **PASS** | 11/11 clauses; zero hallucinations; residue was *reasons*, not clauses |

New misses per round: 4 → 1 → 2 → 3 → 5 → 5. Every round repaired
everything it had been told about and lost something else. The count
never converged; what changed was the *kind* of loss.

**Rounds 1–4 lost categories.** Obligations had no node to live in;
exceptions had no field. Adding a slot fixed those permanently, and they
have not recurred.

**Round 5 lost precision, and that was worse.** It compressed "the
manifest three levels up, beside the running copy" into "in the same
directory as the script". An implementer following that finds no file,
takes the mandated `unknown` fallback, and ships `unknown` on every page
forever — exit 0, plausible output, no warning. That reproduces the exact
bug the source existed to kill.

The asymmetry that follows is the single most useful thing here:

> **A gap sends the reader back to the source. A false fact does not,
> because they have no reason to look.**

It is why the *what* on a mechanism node is quoted or absent, why a
dropped clause gates and a dropped reason does not, and why the page's
self-stated limit had to be rewritten twice.

**Round 6's residue was reasons, not clauses** — and the reader detected
three of the five unaided. It could build the thing and could not always
defend it. That is a materially safer failure mode, and it is where this
tool currently sits.

## Why compression caused the round-5 distortion

Round 5 had merged three mechanisms into one "the decision" node. The
quoting rule is scoped to mechanism nodes, so with one such node it
covered almost nothing and the path rules were paraphrased. Hence **one
mechanism, one node** — three legs of a fix covering different failure
cases are three reasoning states.

## Why the quotation is a blockquote

It started as a labelled list item whose content was checked for
quotation marks. That check rejected every plain ASCII `"`, because
markdown-it escapes it to `&quot;` — six characters matching no quote
mark — and told the author they had omitted marks they had typed. Eight
correct quotations failed at once, for a reason invisible from the skill
text.

**Structure is checkable; punctuation is not.** A `<blockquote>` either
exists or does not. It is also what a quotation *is*, and it survives
into Obsidian as one.

## Why the layout rules do not own the content

Fifteen layout variants were rendered with mermaid-cli and measured by
SVG viewBox (`squareness = min(W,H)/max(W,H)`). The full tables are in
`mermaid-cot-spec.md`. Two findings drove the layer split:

- A cold-read run stated it chose four bullets rather than five "mainly
  to offset" a width warning — deciding how much to take from the source
  by looking at a layout metric.
- For a branching topology, the squarest diagram (0.846) was the one that
  **hid a whole branch**; the same content laid out correctly measured
  0.571. Optimising the number selects the diagram that misrepresents the
  reasoning.

A later run inflated a one-sentence node "to satisfy the 3–5 advisory".
A number does not need enforcement to distort content — being printed is
enough. Hence: counts describe outcomes, they are never quotas, and the
gate says so in the warning itself.

## Why checks cannot be self-reported

`verified` began as a field the author typed. That is the anti-pattern
the source document is entirely about: a self-reported success signal is
what fooled two review agents into passing a broken page. It failed in
the milder direction first — it sat empty through a run that passed, so
the page announced 未執行 while the gate said PASS.

The verdict file then introduced a staleness of its own: it can outlive
the page it judged. Hence `reviewed_md_sha256:`, which **fired on its
own** the first time a page was edited after a check — no one was testing
it.

`verified` then repeated the verdict file's own mistake. It recorded the
outcome and nothing about *what* had been judged, so any later edit to
the page left `pass` standing and the reader saw a gate result for text
the gate had never seen. It now carries the body hash the same way the
verdict file does, and the converter prints **stale** instead of the old
result — the field that reports staleness had been the one field
exempt from the check.

The hash covers the body only. An earlier version hashed the whole file
and invalidated a verdict over a path format change. **A check that fires
on harmless edits is one people learn to wave through**, which is how a
real warning gets missed — the same lesson as a fifteen-warning run,
arriving on a different mechanism.

## Two decode stages, and the control that has to sit before both

The page delivers the diagram as text inside `<pre class="mermaid">`.
The browser decodes that to `textContent`; mermaid takes the textContent
as the diagram source and then inserts each node label with `innerHTML`,
which decodes **a second time**. Label text comes from whatever document
was summarised.

The first version un-escaped the whole fence body, so a `<script>` in a
source document arrived live. The comment above it named mermaid's
`securityLevel` as the mitigation — but the browser parses `<pre>`
content before mermaid initializes, so that control sat downstream of
the injection point and never saw it.

The fix allow-lists the four tags a label may contain and neutralises
everything else, and the cut is **`<`, not `>`**: a lone `>` cannot open
a tag while arrows are full of legitimate ones. The first attempt cut
both and left mermaid a graph with no edges.

Anything meant to READ as text needs one extra level of escaping, so
that exactly one decode is consumed at each stage. `&amp;lt;` becomes
`&lt;` in textContent, and the character `<` on screen. That is right for
fidelity as well as safety: a `<div>` written in the source is text the
reader should see, not an element that silently vanishes into the label.

Two reviewers found this in two passes — one caught the browser stage,
the next caught the mermaid stage — which is the shape of the whole
class: **each fix is correct at the layer it was reported and unguarded
one layer down.** Three other findings in that round had the same
skeleton: the gate authenticating a fingerprint rather than the content
it fingerprints, `pass --render` derived from the flag rather than from a
parse that happened, and a version claim grounded in a real live run but
attached to a floating `11` range.

## Why the vocabulary stays small

The obvious response to a fidelity failure is more expressive power:
typed edges for attack and support, node shapes per epistemic status.
The evidence says do not.

- Argument mapping's demonstrated benefits come from deliberately tiny
  vocabularies — Rationale ships roughly reason / objection / rebuttal,
  Kialo ships pro / con.
- Suthers (2003) found extra ontological elements made student diagrams
  *worse*, through incorrect use. Scheuer et al. name the costs:
  cognitive overhead, premature commitment to structure.
- Buckingham Shum's gIBIS retrospective records overhead appearing as
  soon as types beyond core IBIS were added.
- This repo's `think-orbit` arrived independently at one relation plus
  one boolean, and records rejecting auto-invalidating attack edges
  because attack-target agreement across corpora was zero. A separate
  double-blind experiment there found richer node taxonomies collapse
  inter-annotator agreement.

The operative rule: **add slots you fill by copying, never slots you fill
by judging.** "What limit did the source state" is copied and stays
reliable across readers. "How confident is this claim" is judged and does
not.

Three things deliberately got no syntax:

| Wanted | Standard name | Why no new syntax |
|---|---|---|
| "A is inert without B" | linked argument / co-premises | Two edges into one node already say it; no standard system ships an `enables` edge |
| "attacks / refutes" | rebutting & undercutting defeaters | Belongs in the rebuttal field as text; typed attack edges are the documented failure mode |
| settled / tentative / superseded | ADR `status`, Carneades statement status | Carried only when the source labels itself; rating it is judging |

## Where the method came from

The round-trip is **forward simulation** (Doshi-Velez & Kim 2017),
refined as **Leakage-Adjusted Simulatability** (Hase et al., Findings of
EMNLP 2020) — whose correction matters here: a page that restates its
conclusion verbatim scores well on naive reconstruction without being
faithful.

The convergence contract is adapted from
`loom-code:requesting-docs-review`, which faced the same problem of prose
having no test to terminate on. One divergence: it forbids auto-fixing,
because it reviews the user's own prose; this page is generated, so
fixing is allowed and disclosure is mandatory.

The `number. space` trap and the fence-rewrite approach come from
`obsidian:obsidian-mermaid-visualizer`, whose validator also documents
the behaviour that makes `--render` necessary: mermaid-cli writing an
error image and exiting 0.

Both of those inherited facts were later probed live against the pinned
parser, and both moved:

- **`number. space` no longer breaks it.** mermaid-cli 11.16.0 rendered
  `標題 1. 第一步` cleanly, quoted and unquoted. The rule was a `FAIL`; it
  is now a `WARN`, because "Step 1. do this" is an ordinary sentence and
  a gate that rejects it is a gate people route around. The caution
  survives only for older renderers — Obsidian bundles its own mermaid.
- **The exit code is unreliable in both directions.** The same probe saw
  a malformed arrow exit 1 with no image written. So `render_check`
  reads the output rather than the status, and counts both "no SVG" and
  "SVG with an error marker" as failure.

The general lesson, which cost a `FAIL` on correct content: **an
inherited fact about an external tool is a claim with a version
attached.** Re-probe it when you pin a version, and again when the pin
moves.
