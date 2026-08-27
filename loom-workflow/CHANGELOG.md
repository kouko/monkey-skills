# Changelog

All notable changes to the dev-workflow plugin will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [1.0.2] — 2026-08-27 — restore routing and governance dropped by 1.0.1

### Fixed

- `cot-explain`: restored all three routing destinations 1.0.1 dropped —
  `think-orbit:thinking-session`, `think-orbit:break-assumption`, and
  `obsidian:obsidian-mermaid-visualizer`. 1.0.1 kept the prohibition on doing
  the thinking here but removed everywhere to send it.
- `complexity-critique`: restored the mindset SSOT rule — edits land in the
  canonical `code-team/standards/` copies first, and a fifth mindset is
  governed by `mindset-extension-standard.md`.
- Removed the per-file word-count bounds from the `test_*_compaction.py` files.
  They froze the 1.0.1 compaction's own measurement into a permanent contract
  and could not detect a deleted rule; presence assertions now carry that job.
- `complexity-critique`: Q2's `after > before` row now speaks the skill's own
  verdict vocabulary (RESHAPE, or PROCEED-WITH-CAVEAT only when the added
  volume is explicitly justified and costed). Both the pre-1.0.1 wording and
  1.0.1's replacement conflicted with the file's own verdict list.

## [1.0.1] — 2026-08-26 — behavior-preserving skill compaction

### Changed

- Compacted all loom-workflow skill entrypoints with static invariants and
  Claude Code/Codex weak-model A/B evidence.
- Clarified publication-before-fidelity, paid-dispatch staging, and
  cross-host handoff version capture without changing their safety gates.

## [2.27.1] — 2026-08-19 — `cot-explain` stops pinning the anomalous mermaid

### Changed — the CDN pin moves off 11.16.0

The generated page pinned `mermaid@11.16.0`, which is the short-lived line
that honoured a subgraph's `direction` even when a node edge left the
subgraph. While the layout depended on that anomaly the pin was load-bearing
and nobody knew it; that is why the page looked right locally and collapsed
in Obsidian and the VS Code preview.

2.27.0 removed the dependency — rows are joined subgraph-to-subgraph, which
renders identically on every version tested. So the pin has inverted from
crutch to liability: the **11.16.x line** — both 11.16.0 and 11.16.1 — is
where a regression in the row-joining rule would stay invisible, because it
is the only line that tolerates the broken form. Pinned to 11.17.0, which has
mermaid's documented behaviour.

`MERMAID_VER` (mermaid-cli, used by `--render`) stays at 11.16.0 — it is the
latest release, and its comment already records that pinning the CLI does not
pin the library it draws with.

### Added — one memory entry

`widening-a-grammar-leaves-the-old-regexes-covering-half-of-it` — when the
edge grammar gained subgraph ids, two guards kept their `[A-Z]` patterns and
silently covered only half the language. No test failed, because every
existing test used the old shape.

## [2.27.0] — 2026-08-19 — `cot-explain` diagrams render the same everywhere

### Fixed — the layout rested on a two-patch mermaid bug

The rows layout was justified by a measurement: 0.81 squareness against
0.07 for a flat chain, with the per-row `direction LR` line named as the
load-bearing part. The measurement was real; the conclusion was not.

mermaid discards a subgraph's `direction` as soon as one of its nodes has
an edge to anything outside it. A reasoning chain crosses rows by
construction, so on almost every mermaid release that declaration was
being thrown away and the rows were stacking into one narrow column
(242 × 1386, squareness 0.175). The original 0.81 was measured inside a
**two-patch window** — 11.16.0 and 11.16.1 — where mermaid honoured it
anyway; 11.17 restored the documented behaviour. The generated HTML
pinned its CDN inside that window, which is why nothing looked wrong
locally while **Obsidian and the VS Code preview (mermaid 11.13.x)**
rendered the same page as a column.

**The fix is one rule: rows and columns are joined SUBGRAPH to SUBGRAPH
(`r1 -->|…| r2`), never node to node.** Node edges stay inside a row; the
row-to-row edge carries the transition between stages. Verified
byte-identical on 11.13.0 and 11.17.0, so the layout no longer depends on
which mermaid the reader happens to run. The same rule fixes the
branching shape (columns), measured 0.862 against 0.369.

The verifier now refuses any node edge that leaves its subgraph —
including `C -->|…| r2`, which is the case worth naming: it scores
**0.807**, the highest of the three on the fixture it was measured on,
and its rows are stacked. It was briefly adopted on that number before
the node coordinates were read. A reviewer re-running the three forms on
another fixture got a different ranking — which condemns the metric
rather than rescuing it.

### Changed — squareness is no longer trusted on its own

`min(W,H)/max(W,H)` cannot distinguish "the rows are laid out
horizontally" from "the boxes happen to be wide". Every figure in the
spec's appendix is now verified by parsing node coordinates (each row
must share one y and increase in x) and by byte-comparing PNG renders on
two mermaid versions. The old appendix numbers are **withdrawn rather
than adjusted** — they were measured on a diagram shape the spec no
longer permits.

New figures: 5 nodes 0.686, 6 nodes 0.686, 7–9 nodes 0.938; at 8 nodes,
rows of 3 score 0.938 against 0.456 (rows of 2) and 0.512 (rows of 4). A
trailing row holding one node renders correctly and is not a defect — an
earlier note called it a hazard on evidence taken from the broken shape.

### Changed — the `.md` stays in the temp directory

Both outputs now live side by side in `${TMPDIR:-/tmp}/cot-explain/`, and
nothing is moved by default. Keeping the page is a choice the user makes:
publish the HTML as an Artifact, or move the `.md` into a vault — and the
vault route now states plainly that Obsidian runs mermaid 11.13.x.

### Fixed — a pin that pinned nothing

`MERMAID_VER = "11.16.0"` pins mermaid-cli, which declares
`mermaid: ^11.14.0` — so the library it actually draws with floats. Three
places described it as "the pinned mermaid". The comment and the WARN
text now say what is and is not pinned.

## [2.26.1] — 2026-08-19 — `cot-explain` reads as domain-neutral

### Changed — the skill no longer assumes its source is software

The machinery was already domain-neutral: the extraction vocabulary
(claim / evidence / what this step changed / rebuttal / co-premises /
the author's own hedging) is argument analysis, not engineering, and the
verifier only ever checks diagram form. What was not neutral was the
*wording* — the examples and the "What this page is not" section both
assumed the source was a technical specification, which reads as a
restriction that was never implemented.

- A node "names a mechanism" when someone will act on it. That may be a
  code change; it may equally be a policy clause, a contract term, a
  protocol step or an editorial standard.
- "What this page is not" now speaks of an **operative** source —
  written to be acted on rather than merely read — and names the
  specification as the obvious case among policies, contracts, clinical
  protocols and regulations. The warning applies to each word for word.
- "an implementer must work from it" → "anyone acting on it must work
  from it"; "implements the version the source rejected" → "acts on".
- The carve-out and negative-requirement examples gained non-software
  instances beside the existing ones.
- Two references to a `規格原文` label were dropped. The prose described
  an artifact the template has never produced: every revision of
  `assets/cot-report-template.md`, including the first, uses the `>`
  blockquote form, and `規格原文` exists only as a legacy labelled-list
  shape that `verify_cot_html.py` still rejects. It now says "verbatim
  blockquotes", which is what the page actually contains. (The commit
  message for this change says the template "stopped shipping" the
  heading — that is wrong in the same way, caught by a reviewer reading
  git history rather than the current tree; it never shipped it.)

The binding constraint was never the domain — it is the SHAPE of the
text. A source with a chain of reasoning fits, whether it is a court
judgment, an investment memo or a design doc; a purely descriptive
source does not, which is what Step 2's early exit already catches.

No behaviour changed: no script, threshold, or gate was touched, and the
35-test suite is untouched and green. The routing description is also
deliberately unchanged — it was measured at 25/31 on a trigger eval, and
its one software word is a *counter*-example ("what a function does" is
a state request), which does not narrow what routes in.

## [2.26.0] — 2026-08-19 — new skill `cot-explain`

### Added — `cot-explain` v0.1.0: reasoning → one shareable HTML page

A one-shot generator. It takes reasoning that already exists — in a file,
a folder, or the current conversation — and renders it as a single
self-contained HTML page whose centrepiece is a chain-of-thought Mermaid
diagram. No persistent state, nothing tracked across sessions.

Page structure: one-line conclusion → CoT diagram → per-node expansion
(claim / evidence / what this step changed) → rejected options with
reasons → assumptions and open questions. Empty sections are deleted
rather than shipped as bare headings.

The diagram follows a strict house convention rather than generic
Mermaid, documented in `references/mermaid-cot-spec.md` and derived from
~7,924 vault notes that use it:

> **Read this list as the FIRST DRAFT, not as what shipped.** This entry
> is written as a narrative, and two of the bullets below were reversed
> later in it on measured grounds — see *Layout diverges from the vault
> convention* for the axis and the subgraphs, and *Bullet count is 3-5*
> for the counts. What ships is `graph TB` with mandatory `subgraph`
> rows, each declaring its own `direction LR`.

- `graph LR`; node body is
  `["<div style='text-align:left'>TITLE<br/>━━━━━━<br/>• B1<br/>• B2<br/>• B3</div>"]`
- separator is the literal `<br/>━━━━━━<br/>` (six U+2501), **not** `---`
- **every** edge carries a label — a bare `A --> B` is a defect, and
  empty connectives (`導致` / `然後` / `所以`) are rejected
- `-->` derivation, `-.->` background/weak link, `==>` the culminating
  step into the conclusion
- inline per-node `style` lines; no `classDef`, no `subgraph`
- 5–9 nodes: fewer does not earn a diagram, more means multiple arcs

Output landed in the repo at `.claude/cot-explain/` in this first pass;
later in this same entry it moves to a temp directory and the artifact
becomes markdown. The local HTML build loads `mermaid.js` from a CDN
(first open needs network); the Artifact build strips that script block
and the document skeleton, since Artifacts render `<pre class="mermaid">`
natively. Publishing is asked for once, never done unprompted — it
uploads the content.

Boundary against the neighbours, stated in both SKILL.md and the READMEs:
`think-orbit:thinking-session` is for *doing* the thinking with tracked
state across sessions; `cot-explain` is for *explaining* thinking that
already happened. They coexist. `recap-state` re-orients you in chat,
`handoff` writes for a cold AI reader — neither produces a page for a
human audience.

Verification is a script, not a checklist. The first draft gated the
output with four `grep` lines; a cold-reader dogfood run broke all four:
`grep -c` counts matching *lines* and one template line holds two node
labels (7 nodes counted as 6); the edge grep was not scoped to the
mermaid block so the page's own `<!-- ... -->` wrapper added phantom
edges; the labeled-arrow regex `--[>x]` could not match `==>` at all,
so an unlabeled culminating edge — the most important edge in the
diagram — passed silently; and the template's authoring comment
contained a literal `{{PLACEHOLDER}}`, contradicting the skill's own
"must be 0" rule. Replaced by `scripts/verify_cot_html.py`, which parses
the mermaid block after stripping HTML comments and exits 1 with one
`FAIL:` line per violation. A 16-case mutation suite (unlabeled `==>`,
five-`━` separator, literal `---`, dropped bullet, `graph TD`, missing
wrapper, missing/misordered `style`, off-palette fill, empty connective,
`classDef`, `subgraph`, leftover placeholder, retained template comment)
kills all 16.

Dogfooding conversation mode on this session's own reasoning found two
more defects, both now fixed. The default output path
`.claude/cot-explain/` was not in `.gitignore`, so generated explainers
would have been committed into whatever repo they were produced in —
`.claude/handoffs/` was already excluded for the same reason. And the
gate's placeholder check tested for a bare `{{`, which fails any page
whose prose *discusses* templating; it now matches the placeholder shape
`{{UPPER_SNAKE}}` instead. Two regression guards were added to the
mutation suite for legitimate prose that mentions `{{` or an `-->`
arrow, bringing it to 16 kills + 2 no-trip cases.

Step 1 also gained the boundary rule the run exposed: in conversation
mode the chain starts at the request that opened the current piece of
work, not at the first message of the session, and the author's own
overturned judgments are nodes rather than omissions.

#### Layout diverges from the vault convention, on measured grounds

The node styling follows the vault. The **layout does not**, and that was
decided from rendered pixels rather than taste. A reasoning chain is long
and thin: as the vault's flat `graph LR` it rendered **3061 × 227 px —
13.5:1**, unusable on a page. Fifteen variants were rendered with
mermaid-cli and measured by SVG viewBox (`squareness = min/max`, 1.00 = a
square):

| Layout | Size | Squareness |
|---|---|---|
| **`graph TB` + subgraph rows w/ `direction LR`, short bullets** | 1022 × 824 | **0.81** |
| same, long bullets | 1218 × 824 | 0.68 |
| `graph LR` outer + subgraph cols w/ `direction TB` | 1107 × 739 | 0.67 |
| `graph TB` + branching, no subgraph | 421 × 1062 | 0.40 |
| subgraph rows but no `direction` declared | 272 × 1884 | 0.14 |
| `graph LR` linear (vault convention) | 3061 × 227 | 0.07 |
| `graph LR` linear + tightened node/rank spacing | 2956 × 221 | 0.07 |

Three findings now encoded as rules. The **`direction LR` line is what
does the work, not the subgraph** — rows without it give 0.14, and the
grouping buys nothing. **Spacing config is a dead end**: `nodeSpacing` /
`rankSpacing` moved 13.48:1 to 13.39:1. And **bullet length is a layout
lever**, not a style one — same structure, 0.68 long vs 0.81 short —
so titles and bullets now cap at 8 CJK-widths, with the full claim,
evidence and consequence carried by that node's card in the HTML body,
which has no width limit.

Mermaid can ignore a subgraph's inner `direction` when edges cross the
subgraph boundary. That was checked from rendered node `translate(x,y)`
values, not by eye: within each row `y` is constant and `x` increases,
including on the shipped diagram which carries a cross-row `-.->` edge
(rows at y=118 with x 123/463/833, 139/519/891, 130/502). If a future
mermaid regresses this the diagrams collapse to the 0.14 case —
re-measure before blaming the content.

`subgraph` therefore flipped from **forbidden to required** in both the
spec and the gate, and `graph TB` replaced `graph LR`. The gate gained
row-size, row-balance, orphan-node, stranded-node, and width-cap checks;
the mutation suite grew to 22 kills + 3 no-trip guards, all passing.

#### Bullet count is 3-5, and length limits stopped blocking

Counting the vault rather than trusting the sample that seeded the spec:
across 238,764 nodes in 7,924 files, 79.24% carry three bullets, 20.28%
carry two, and 0.48% carry four or more. The original "exactly three"
was inferred from two examples and would have rejected a fifth of what
the vault actually does.

Rendering settles the rest. Bullet count changes node height and leaves
node width byte-identical, and since the figure comes out wider than
tall, each added bullet moves it *towards* square — 2 → 0.736, 3 → 0.807,
4 → 0.877, 5 → 0.948, a flat +0.070 per bullet with no flattening, so six
would overshoot. Hence **3-5, aiming for 4-5**, with an explicit "do not
pad to hit the count".

The width caps flipped from FAIL to WARN. They were also aimed at the
wrong thing: node width is set by the **single widest bullet** in the
diagram, not by every bullet, so the gate now warns once on that one line
and explains that it sets every column. A hard character cap makes an
author mangle a sentence to satisfy a number, which is worse than a wide
box. The gate now reports two levels — `FAIL` breaks the contract or the
parser and exits 1; `WARN` costs readability or squareness and never
blocks. The spec/gate mismatch a dogfood run caught (spec said edge
labels were 4-8 CJK, the code enforced 2-12) is resolved by collapsing
the two bands into one: 4-8 CJK-widths, WARN-only. There is no separate
enforced band — a width has no business failing a build, which is the
same reasoning that moved every other count to WARN.

#### Borrowed from `obsidian:obsidian-mermaid-visualizer`

Two of its design choices proved directly applicable. Its validator
documents that **mermaid-cli does not signal a syntax error through its
exit code — it writes an error SVG and exits 0**, so a purely textual
check can pass a diagram that renders as a red error box. `--render` now
pushes each diagram through the real parser and reads the SVG. Honest
limit: four attempts to construct a diagram that passes the text stage
and fails the parser did not succeed — the quoted-label design makes
labels hard to break — so `--render` is insurance against a documented
mermaid behaviour, not a demonstrated catch. Without the flag the output
reads `PASS (text only …)` so the weaker check is never mistaken for the
stronger one.

Its quirks list also supplied a real trap: a `number. space` run in node
text makes mermaid parse a markdown ordered list and die. That is now a
FAIL, verified by mutation.

#### Width budgets widen for Latin script

A third cold-read dogfood, this one on an **English** source, tripped the
title warning on all seven nodes and forced a real loss of meaning —
"Reversal: the Codex-immune claim was false" had to become "Codex claim
false". The budgets are pixel-width budgets expressed in CJK units, and a
CJK glyph is about twice a Latin one, so a budget that fits 10 Chinese
characters fits only ~20 Latin ones. Latin-heavy text (>60% ASCII
letters/digits) now gets 1.4× the budget. Same source, same page: eight
warnings became one — the one the cold reader had already decided, on its
own judgment, to keep.

That run also settled a fork the skill had left open: the template ships
Chinese section headings and card labels, and Step 4 only said "match the
source's language for all prose", which does not say whether headings
count. They do — Step 4 and the template comment now say so and give the
English wordings.

`--help` printed a traceback instead of the usage text it already had.

One reported defect did **not** survive checking: the run claimed the
text stage has no rule for an HTML-escaped `&lt;div&gt;` wrapper. It does —
`FAIL: missing the <div style='text-align:left'> wrapper`, now pinned by
a mutation case. The claim was an inference the reporter never ran.

Mutation suite: 22 FAIL cases + 4 WARN cases + 6 must-stay-clean guards
+ 3 real generated pages, 35 checks, all correct.

#### Branching DAGs broke the layout rules — investigation record

Every dogfood so far produced a near-linear chain, so branching was
untested. Four synthetic topologies with identical node content — a
diamond, two independent tracks, a 3-way fan-out, and two independent
root premises — exposed two defects and one inversion.

**The fixed 3/3/2 row rule is topology-blind.** It packs nodes by
reading order and never asks what is parallel to what. Rendered
coordinates: in the two-tracks case the genuinely parallel pair D/E did
not share an x, while D accidentally aligned with the unrelated F; in the
fan-out, only two of the three branches shared a row and the third was
visually decoupled. The diamond and two-roots cases looked correct only
because their forks happened to fall inside one declared row — nothing in
the rule guarantees that.

Re-assigning rows by topological rank fixes the grouping completely
(all forks' siblings then share both row and x, verified by coordinates)
but the row-size check rejected all three corrected diagrams: `row sizes
[1,2,2,3] — for 8 nodes the rows should be [3,3,2]`. The rule was
actively refusing correct output.

**Squareness and correctness point in opposite directions.** Same
content, same topology, two layouts: the fixed-row fan-out measures 0.846
squareness with a broken grouping that hides one of three branches; the
topology-aligned one measures 0.571 and shows all three. Optimising for
the number selects the diagram that misrepresents the reasoning. Branched
diagrams are simply taller — a fork stacks vertically inside a row, so
height grows with branching no matter how rows are assigned (0.469 fixed,
0.581 topological, and one case got worse at 0.323 because per-rank rows
added a fourth row without adding width).

**Root cause, named by the user: the layout rules had begun to drive the
extraction rather than follow it.** Six rules were dictating content for
layout reasons — node count 5-9, bullets 3-5 "aiming for 4-5" justified by
squareness, per-edge label widths, title/bullet width caps, one `==>` per
diagram, and the row quota. The third dogfood run stated the inversion in
its own words: it chose 4 bullets rather than 5 "mainly to offset" a
width warning — deciding how much to extract from the source by looking
at a layout metric.

The mechanism underneath is sound: zero edge crossings in any of the
seven branched variants (dagre routes merge edges into separate parallel
bands), and inner `direction` held in every case including single-node
rows. What failed was the quota layer added on top.

#### Resolved: branching reasoning is drawn as columns

Inverting the axis settles it. Outer `graph LR`, one vertical
`direction TB` subgraph per branch, branches side by side: the diamond
measures **0.938** and the 3-way fan **0.930** — the first branched
topologies to beat the linear baseline's 0.807, against 0.469 for the
same content in fixed rows. More importantly the two goals stop
fighting: the column layouts are simultaneously the squarest *and* the
ones where parallel branches read as parallel (verified by coordinates —
each track's nodes share an x and step down in y).

A new mermaid behaviour came out of the w3/w4 comparison and is now a
gate FAIL: **a subgraph whose members have no edges among themselves
gets its declared `direction` ignored**, and mermaid lays them out along
the other axis — three independent branches in one `direction TB` box
rendered as a horizontal row. A subgraph must hold a connected run.

The spec is now organised by **who owns what**: content (which nodes
exist, what each claims, what each edge names) always wins; layout is
derived from the chain's shape, never imposed on it; widths, counts and
squareness are advisory and never block. The gate follows: the fixed
`[3,3,2]` row quota is gone, node and bullet counts and label widths
dropped to `WARN`, and `FAIL` is reserved for mechanical invariants —
the contract, and what mermaid itself requires.

#### Fidelity: the check no gate can perform, and a card field

A round-trip test on a real English source found the well-formedness
gate proves nothing about honesty. The reader came away believing the
fix was to "pin to a specific path" when the source had explicitly
derived why a fixed path fails (`spec:198-208`) and specified a
self-locating rule instead, and believing an unscoped leftover-markdown
check when the source states it must be scoped or it "will condemn every
correct page" (`spec:128-133`). Both would have produced the rejected
implementation. The judge's verdict: faithful as an account of *why*,
unusable as an account of *what to do* — every implementation constraint
carrying engineering risk had been compressed out.

`SKILL.md` gains **Step 6**, a simulatability-style round-trip (forward
simulation, Doshi-Velez & Kim 2017; Leakage-Adjusted Simulatability,
Hase et al. 2020) in three rounds: blind reconstruction from the page
alone, comparison against the source by an agent that never sees the
page, and a hallucination pass in the reverse direction — the previous
design measured only what was lost, never what was invented. The leakage
caveat is recorded too: a page that restates its conclusion verbatim
scores well on naive reconstruction without being faithful.

The vocabulary fix is one card field: **`例外／失效條件`** — Toulmin's
*rebuttal* — present only when the source states one, because an empty
row asserts "no exceptions apply", which is a claim the source did not
make. The diagram vocabulary did not change at all.

That restraint is evidence-backed, not taste. Argument mapping's
demonstrated benefits come from deliberately tiny vocabularies (Rationale
≈ reason/objection/rebuttal; Kialo = pro/con); Suthers (2003) found extra
ontological elements made student diagrams worse through incorrect use;
Buckingham Shum's gIBIS retrospective records cognitive overhead
appearing as soon as types beyond core IBIS were added. This repo's own
`think-orbit` arrived independently at one relation plus one boolean, and
its spec records rejecting auto-invalidating attack edges because
attack-target agreement across corpora was zero — with a separate
double-blind experiment finding richer node taxonomies collapse
inter-annotator agreement.

#### The artifact is markdown; the HTML is derived

The first design had the model hand-fill an HTML template. That put
markup concerns in front of the author at the moment of extracting
meaning — the same inversion as the layout rules, one level down. It also
made every structural addition expensive: a new section meant template
surgery plus new regexes.

Now `assets/cot-report-template.md` is the artifact and
`scripts/render_cot_html.py` derives the HTML. The markdown carries
**Obsidian-compatible frontmatter** following the vault's documented note
standard (`title` / `type` / `date` / `tags` / `aliases` / `status`) plus
the keys its own notes carry (`language`, `processed_at`, `timezone`,
`llm_provider`, `llm_model`), so a page worth keeping moves into a vault
as-is. Structure follows the vault's note shape too: `###` a page
section, `####` one arc with one diagram, `#####` one node card — which
answers the multi-diagram question for free, since the house format
already puts several CoT diagrams in one note.

Output moved to `${TMPDIR:-/tmp}/cot-explain/`. These pages are read once
in the ordinary case; the skill now says so and says how to keep one. The
`.gitignore` entry added for the old in-repo path was removed as dead
config.

**The converter uses markdown-it-py, not a hand-rolled parser.** A
hand-rolled one was written first and failed its own test suite within
the hour: an unsupported `##` heading passed through unconverted *and*
slipped past the leftover-markdown check, because the check matched only
line-start markdown while the stray text had already been wrapped in
`<p>`. Switching to the library — the same one
`loom-code/scripts/adjudication_render.py` already uses — made that
failure mode cease to exist rather than merely be caught. The switch
immediately exposed a second bug it had been masking: the template uses
the vault's `###`/`####`/`#####` levels, markdown-it correctly renders
those as `h3`/`h4`/`h5`, and the CSS and lede-extraction had been written
against `h2`/`h3`/`h4`.

What stayed hand-written are the pipeline properties, all three taken
from the brief this skill has been dogfooding on — a renderer of exactly
this kind that failed silently five times in five days. It **fails loud
and writes nothing** when markdown survives conversion, because a run
that fails but still writes leaves the broken deliverable intact. Its
check is **scoped**, because mermaid blocks and `<code>` spans
legitimately contain `|`, `**` and `#` and an unscoped check condemns
every correct page. And it **stamps** each page with the version of the
copy that actually ran, read from the manifest beside the script rather
than from a working directory, falling back to the literal `unknown`
rather than faking a version. Verified: on unconverted markdown the
postcondition detects five classes of residue; on correct output it is
clean; and the mermaid block, whose edge labels are full of `|`, does not
trip it.

#### Three fidelity rounds, and what each one cost

The check was run three times on the same source, and the record matters
more than the outcome because each round failed differently.

Round 1 (before any of this): "faithful as an account of *why*, unusable
as an account of *what to do*". The reader would have pinned to a fixed
path — the variant the source explicitly derives as broken — and written
an unscoped leftover-markdown check that condemns every correct page.

Round 2, after the extraction contract gained its hunt items: three of
those four repaired, but the delivery-side obligation ("confirm the stamp
before delivering; a page with no stamp must not ship") was absent
entirely. Obligations are not reasoning steps, so they had no node to
live in; the markdown gained a `### 這份結論要求你做什麼` section.

Round 3, on the markdown pipeline: **all four named failures fixed, zero
hallucinations** — the first run where the reverse direction was checked
at all — and still a FAIL, on two clauses nobody had asked for:
`no output file written` (stated twice in the source) and the carve-out
exempting sessions that are developing the scripts themselves.

The diagnosis is worth more than the fix. All three misses share a shape:
**a normative clause attached to a mechanism**. The slots added after
round 2 did not catch them because one was a negative requirement — part
of what the mechanism does, neither an obligation on a person nor an
exception — and the other was an exception sitting on a node whose
exception field nobody had thought to interrogate. A hunt item phrased as
"does the source state a limit" is a passive search; it finds what
announces itself.

Step 2 now sweeps node by node instead. For every node naming a
mechanism: what must it NOT do, who is exempt, and under what condition
is it withdrawn. The cold reader who ran it reported the sweep
"genuinely productive, not redundant — it surfaced the code-span
exemption and the fail-loud withdrawal condition, both of which I would
likely have missed doing a flat read-through."

Round 4 confirmed that: all six named clauses landed, and hallucinations
stayed at zero for a third consecutive round. It still failed, on three
things nobody had looked for — that the version must be read from the
manifest shipped *beside the running copy* (without which a stale copy
stamps the current version and the mechanism inverts into a false
all-clear), that the postcondition's failure is *non-zero exit* as well
as no file written, and the whole reason `${CLAUDE_PLUGIN_ROOT}` was
rejected.

**The trend is the finding.** New misses per round went 4 → 1 → 2 → 3.
Each round repaired everything it had been told about and lost something
else. The first rounds lost whole *categories* — obligations had no node
to live in, exceptions had no field — and adding a slot fixed those for
good. Round 4's losses were different in kind: details *inside* a
mechanism's specification, which is to say ordinary lossy paraphrase.
Another hunt category cannot fix that; it moves the loss.

#### Rounds 5 and 6, and the class that stopped recurring

Round 5 failed differently from every round before it. It stopped
producing gaps and produced **confident wrong answers**: it compressed
"the manifest three levels up, beside the running copy" into "in the same
directory as the script". An implementer following that finds no file,
hits the mandated `unknown` fallback, and ships `unknown` on every page
forever — exit 0, plausible output, no warning. That is a re-run of the
exact bug the source existed to kill, and it is worse than the gaps it
replaced: a gap sends the reader back to the source, a false fact does
not, because they have no reason to look.

The cause was compression. That round had merged three mechanisms into a
single "the decision" node, so the verbatim-quoting rule covered almost
nothing and the path rules were paraphrased. Two changes followed —
**one mechanism, one node**, and the *what* on such a node is quoted or
absent, never paraphrased. The quotation moved out of a labelled bullet
into a markdown blockquote, on the reasoning that a blockquote is what a
quotation *is*, survives into Obsidian as one, and lets the gate check
**structure** rather than sniff punctuation. That last point was not
theoretical: the punctuation check had rejected every plain ASCII `"`,
because markdown-it escapes it to `&quot;` — six characters matching no
quote mark — and told the author they had omitted marks they had typed.

Round 6 passed. Eleven of eleven tracked clauses carried, zero
hallucinations for a third consecutive round, and **zero confident-wrong
statements — the class did not recur**. The residue changed character
too: five omissions, all of them *reasons* rather than clauses, and the
reader detected three of the five unaided. It could build the thing and
could not always defend it. That is a materially safer failure mode, and
the page's self-stated limit was rewritten to describe it honestly —
"instructions are carried, reasons are abridged" — after a judge pointed
out that the previous wording warned about the wrong failure.

#### The pipeline the user took apart

Five questions from the user, each one exposing something the author had
claimed but not done:

**Is this markdown-first or hand-written HTML?** It was hand-written HTML
— markup concerns in front of the author at the moment of extracting
meaning, the same inversion as the layout rules one level down. The
markdown became the artifact and the HTML its derivation.

**Isn't there an existing tool for markdown→HTML?** There was, and this
repo already used it: `loom-code/scripts/adjudication_render.py` runs
markdown-it-py. The hand-rolled converter written first had already
failed its own tests within the hour — an unsupported `##` passed through
unconverted *and* slipped past the leftover check, which only matched
line-start markdown while the stray text sat inside a `<p>`. Switching to
the library made that failure mode cease to exist rather than be caught,
and immediately exposed a second bug it had masked: the template used the
vault's `###`/`####`/`#####` levels, markdown-it correctly rendered them
as `h3`/`h4`/`h5`, and the CSS and lede-extraction had been written
against `h2`/`h3`/`h4`.

**Have you post-processed it?** Yes — three transformations, one of which
deleted a heading. Measured: of twenty headings in the markdown, the old
pipeline altered twelve and dropped 概述 entirely. "Deterministic" had
been mistaken for "faithful"; a deterministic move is still a move.
Everything but the mermaid un-escape (unavoidable — node labels are raw
HTML) became CSS applied where things already stand. Headings in the
HTML now match the markdown exactly, 20 for 20.

**Doesn't the frontmatter carry through?** Nineteen keys reached two, and
one of those two was read under a name the template had since changed, so
the date rendered blank and nothing said so. All nineteen now emit as
`<meta name="cot-*">`.

**Can the quotation use markdown's `>` instead of a list item?** Yes, and
it is better for the reason above.

**Can the paths be absolute and clickable?** Now yes, with two limits
stated in code: only an absolute path is linked, because a guessed base
produces links that look right and go nowhere; and the Artifact build
never links, because it is served over https where `file://` is refused
and the absolute path would carry the author's directory layout to
whoever the page is shared with.

#### Checks that cannot be self-reported, and a fix cycle that terminates

`verified` began as a field the author typed. That is the anti-pattern
the whole source document is about — a self-reported success signal is
what fooled two review agents — and it failed in the milder direction
first: it sat empty through a run that passed, so the page announced
未執行 while the gate said PASS. `--stamp` now writes it, `fail`
included. `fidelity_checked` has no script to run it, so it is written
from a verdict file the Step 6 rounds leave beside the page.

That introduced a staleness of its own: a verdict file can outlive the
page it judged. The verdict now carries `reviewed_md_sha256:` and
`--stamp` refuses to record a verdict whose hash does not match — which
**fired on its own**, unprompted, the first time a page was edited after
a check. The hash covers the body only: an earlier version hashed the
whole file and invalidated a verdict over a path format change, and a
check that fires on harmless edits is one people learn to wave through.

Step 6 gained a convergence contract adapted from
`loom-code:requesting-docs-review`, which faced the same problem of prose
having no test to terminate on. Rounds 1-3 are the only full check; a
gating finding is fixed in the markdown, then confirmed by the **same**
comparator via `SendMessage`, scoped to the delta; `STILL_BLOCKING` after
one cycle STOPs and surfaces to the user. One deliberate divergence:
docs-review forbids auto-fixing because it reviews the user's own prose,
while this page is generated — so fixing is allowed and disclosure is
mandatory. What gates is defined: a belief the source contradicts, a
hallucination, or a dropped clause that changes what gets built. A
dropped *reason* is recorded, not gating.

The cycle was then run for real rather than left as specification. Two
rationale omissions were fixed, a fresh blind reader dispatched
(blindness cannot be delta-scoped — an agent that has read the page is no
longer blind), and the comparator confirmed both. The second confirmation
is the one worth keeping: the reader could not defend the `_render_page`
scope boundary, and the comparator ruled the source *only states* it, so
the page had reproduced a real gap faithfully rather than dropped an
argument. Without asking that question the fix would have been to invent
a justification the source never made — manufacturing the very distortion
the check exists to catch.

Two changes follow. Mechanism nodes now carry a **`規格原文`** line
quoting the source's normative sentence verbatim, in the source's own
language — a quotation cannot silently drop "beside the running copy",
a rewrite can. And the skill now states its own limit: **when the source
is a specification, the page explains why the spec decided what it
decided and does not replace reading it**, and says so on the page.
Verbatim quotes narrow the gap; nothing here closes it.

That limit is worth stating precisely because of what did not fail. In
all four rounds the reasoning itself arrived intact — the reversals, the
rejected options with their reasons, the conditional retreats — and the
reverse-direction check found nothing invented in any round it was run.
Explaining how a conclusion was reached is the job. Being a spec is not.

Two gaps therefore got no syntax at all. "A is inert without B" is the
literature's **linked argument** — two edges into one node already say
it, and no standard system ships an `enables` edge. Epistemic status is
carried only when the source labels itself ("my take", "leaning no"),
never rated. The operative rule, now written into the spec: **add slots
you fill by copying, never slots you fill by judging.**

#### The scripts' regression history became a test suite

Whole-branch review found both scripts carrying their own history in
comments — "an earlier version looked for quotation characters", "failed
its own test suite within the hour" — where nothing re-runs it. Those
comments were the test cases, so they became
`scripts/test_cot_explain_scripts.py` (14 tests). Written first, they
failed 8, and each failure was a real defect the prose had recorded but
not defended:

| Defect | What it did |
|---|---|
| Leftover-markdown scope matched only a bare `<code>` | markdown-it tags fence code with the language, so a ```` ```bash ```` block holding `# install …` was condemned as an unconverted heading |
| `verified` recorded an outcome and nothing about *what* was judged | Any later edit left `pass` standing; the page advertised a gate result for text the gate never saw |
| The Artifact build printed the absolute source path as plain text | It stopped linking the path but still disclosed the author's directory layout to everyone the page reached |
| `subgraph` / `style` were anchored at column zero | An indented diagram — ordinary mermaid style, and already tolerated on `direction` — was reported as having no subgraph rows at all |
| The edge parser consumed each destination | `A -->\|x\| B -->\|y\| C` is one legal line carrying two edges; parsing it as one made the arrow count disagree and reported a malformed arrow in a correct diagram |
| The template-comment check looked for "report template" | The template ships "markdown template" — the check could never fire, and read as coverage |
| The `fidelity_checked` write used `re.sub` | A markdown with no such line took the substitution silently and the run reported writing a field that was not in the file |
| `--sha` with no file indexed `argv[0]` | An IndexError and a traceback, where every other misuse prints a usage line and exits 2 |

Two further changes came from the same review. The mermaid CDN now
initializes with `securityLevel: 'antiscript'` rather than `'loose'` —
node labels are raw HTML by design, but `'loose'` also permits `<script>`
and click handlers inside a label, and label text comes from whatever
source document was summarised. Both frontmatter splitters accept CRLF,
where before a CRLF file silently parsed as having no frontmatter at all.

`verified` now reads `pass @ <12 hex of the body hash>`, matching what
the fidelity verdict file had carried all along. The field that reports
staleness had been the one field exempt from the check.

The rows-per-row claim was also re-measured, because SKILL.md cited a
0.58 figure the appendix did not contain. One run of an 8-node chain,
all three variants rendered together: rows of 2 at 0.523, rows of 3 at
0.907, rows of 4 at 0.430. Three is a peak, not a ceiling — the fall-off
is steep on both sides, which is why a trailing row of 2 costs little
and a row of 4 costs a lot.

#### Two controls sited downstream of what they guard

The second review round found the same mistake made twice, and it is the
mistake this skill exists to prevent.

The converter un-escaped the whole mermaid fence body, because node
labels are raw HTML by design and must reach the browser as markup. That
also delivered `<script>` and `<img onerror=…>` live, from whatever
source document was summarised, into a page built to be shared. The
comment above it named mermaid's `securityLevel` as the mitigation — but
the browser parses `<pre>` content before mermaid initializes, so the
sanitizer sat downstream of the injection point and never saw it.

The un-escape is now an allow-list, and the cut is **`<`, not `>`**: a
lone `>` cannot open a tag, and the diagram is full of legitimate ones,
so `&gt;` is restored everywhere while `&lt;` comes back only inside
`<div style='text-align:left'>`, `</div>` and `<br/>`. Because
markdown-it delivered every `<` escaped, the only literal `<` in the
output are the ones the allow-list introduces — exhaustive by
construction rather than by enumerating what to block. The first attempt
cut `>` as well, which escapes every arrow and leaves mermaid a graph
with no edges; that has its own test now.

The second: the gate judged the HTML while the stamp fingerprinted the
markdown, with nothing tying them together. Editing the markdown without
re-rendering left the checker reading a stale page and recording the new
body's hash, so the page came back announcing `pass` for a conclusion the
gate never saw. The renderer now emits `<meta name="cot-body-sha">` and
the stamp refuses when it disagrees with the markdown on disk — the
guard the fidelity path already had, on the field that had skipped it.

Both false-positive classes are closed too. The leftover-markdown
anchors matched any inline tag's close, so `<em>x</em> - 說明` was
condemned as survived markdown and no file was written; they anchor on a
block-tag open now, and the `**` arm requires a pair, because `2**3` is
arithmetic. Edge labels are stripped before arrows are counted, so
`A -->|前提 ==> 中段| B` no longer reports an arrow that is not malformed.

#### Two inherited facts about mermaid, re-probed and both moved

`number. space` in a node label and "mermaid-cli exits 0 on a syntax
error" both came in from `obsidian:obsidian-mermaid-visualizer`'s quirks
list. Both were load-bearing — one was a `FAIL`, the other the entire
reason `--render` exists — and neither had been run against the version
this branch pins.

- **`number. space` renders cleanly** on mermaid-cli 11.16.0, quoted (the
  form this spec mandates) and unquoted. Demoted to `WARN`: "Step 1. do
  this" is an ordinary sentence, and a gate that rejects it is a gate
  authors route around. The caution survives for older renderers —
  Obsidian bundles its own mermaid — and `--render` answers it for
  whatever parser is actually in play.
- **The exit code is unreliable in both directions.** The same probe saw
  a malformed arrow exit 1 with no image written, where the inherited
  note records an error image and exit 0. `render_check` already read the
  output rather than the status; the prose claiming otherwise is
  corrected in three files.

The lesson, which cost a `FAIL` on correct content: an inherited fact
about an external tool is a claim with a version attached.

#### Round three: the same class, one layer further down

Two reviewers re-ran the fixes above adversarially, and both reported the
same shape again — **each fix correct at the layer it was reported, and
unguarded one layer below it.**

The allow-list defended the browser. But the page delivers the diagram as
text, the browser decodes it to `textContent`, and mermaid then inserts
each label with `innerHTML` — **a second decode**. A `&lt;` surviving the
first stage is a real tag at the second, arriving at mermaid's own
sanitizer as markup, which is the downstream posture the fix existed to
end. Anything meant to read as text now carries one extra level of
escaping, so exactly one decode is consumed per stage. That is right for
fidelity too: a `<div>` in the source is text the reader should see, not
an element that silently vanishes into the label.

`pass --render` was derived from the FLAG, not from a parse. With `npx`
absent, `render_check` warns "nothing was parsed" and returns — and the
run still stamped `pass --render` and printed "PASS (parsed by mermaid)".
The no-downgrade branch added in the previous round then re-affirmed that
false, stronger claim on every later run. The verdict now counts diagrams
the parser actually consumed.

The stamp authenticated the page's own fingerprint, not its content — so
hand-fixing a real FAIL in the HTML would mint a `verified` the source
never earned, and "never hand-edit the HTML" is a convention, not a
control. `--stamp` now rebuilds the page from the markdown and compares,
falling back to the fingerprint (loudly) only where the renderer cannot
be imported.

And `MERMAID_VER = "11"` was a floating range described as "pinned" in
three places — on a branch that ships a memory note titled *an inherited
external-tool fact is a claim with a version attached*. Pinned to
11.16.0, the version the live probes actually ran on.

Two smaller ones, both the "condemns correct input" class: `--stamp`
rewrote a CRLF artifact to LF whole-file, and the body hash counted line
endings as content, which made a CRLF artifact impossible to stamp at
all. Both hashes normalise now, and the stamp writes back the endings it
found.

The suite is 31 tests, and 12 of 12 mutants die — including one that
survived the first battery, where a stronger guard was masking the
fallback beneath it. Two tests force the fallback path directly rather
than letting the primary guard answer for it.

#### Round four: the fix for self-reported success, reporting success

Confirming the round-three fixes, one reviewer found two more — both
inside the code that had just closed the same class.

`pass --render` now required a parse, but the success line printed
`parsed/parsed`: the denominator was the numerator. A per-diagram
timeout or OSError skips a diagram with a WARN and no failure, so a
partial run stamped the strong result and printed `1/1` for it. The
denominator now comes from the block list, and the strong claim requires
EVERY diagram to have parsed.

Both defects survived a mutation battery while sitting inline in
`main()`, where only an end-to-end run with a real parser could reach
them — the run CI cannot do. They are now a pure `render_verdict()` that
the suite exercises directly. (One mutant on the remaining line is
equivalent by construction: inside the true branch the guard makes
`parsed == total`, checked exhaustively rather than argued.)

And `--stamp` had started writing `__pycache__` into the skill folder,
because the new rebuild-and-compare imports the renderer from beside it.
That is the hazard this branch documents twice in its own words — the
test suite moved out of the skill for exactly this reason — reintroduced
from inside the fix. One `sys.dont_write_bytecode` guard closes it, with
a test that fails if a stamp leaves a cache behind.

35 tests. Every substantive mutant dies.

#### The suite moved out of the skill

Run inside `skills/cot-explain/scripts/`, pytest creates `__pycache__/`
and `.pytest_cache/` there — nested subfolders under a skill root, which
this repo's `validate-skill-folder-structure.sh` forbids. The skill's own
tests therefore locked the skill against further editing, three times in
one session. It lives at `dev-workflow/tests/test_cot_explain_scripts.py`
now, beside the shell suite, and CI runs it there with pinned deps.
14 tests became 26.

Files: `skills/cot-explain/{SKILL.md,README.md,README.ja.md,README.zh-TW.md}`,
`assets/cot-report-template.md`,
`references/{mermaid-cot-spec.md,fidelity-check.md,why-these-rules.md}`,
`scripts/{render_cot_html.py,verify_cot_html.py,test_cot_explain_scripts.py}`.

## [2.25.1] — 2026-07-25 — bba description summarizes check-question + repeated-confusion signals

### Fixed — `brief-before-asking`: description-summary gap

The frontmatter `description:` named only 3 reactive signals (lost on
question / explanation / stakes) while the body already carried two more
that #598/#599 added — the check-question guard and the repeated-confusion
meta-trigger (SKILL.md ~:79-92). Not a new mechanism: the description now
also summarizes those two signals, without dropping the original
"lost on the question, the explanation, or the stakes" wording, so both
are discoverable from the one-line summary skill-routing reads.

## [2.25.0] — 2026-07-22

### Added — `brief-before-asking`: pre-send two-line check + check-question signals + experienced-difference requirement

Three evidence-driven additions from the 2026-07 live trigger history
(baseline: `docs/harness-audit/2026-07-22-bba-trigger-baseline.md`, PR #598):

- **Pre-send check** (new section): before sending any briefing, verify
  the first line carries the stakes and the last line ends at the
  decision point; two-line test — first + last line alone must answer
  "what am I deciding" + "what happens next". Adapted from the
  i-have-adhd output-style skill; every delivery-side failure in the
  trigger history had no decision anchor in those two lines.
- **Check-questions count as confusion signals** (guard extension +
  2 Mode Detection rows): a user restating their understanding as a
  verification question is comprehension repair, not a factual query;
  the 2nd consecutive check-question trips the repeated-confusion
  guard — explicitly including after a completion *report*, not only
  after an ask. Live miss documented as `references/EXAMPLES.md` Real
  Case 4.
- **Mental Model must state the experienced difference** (Block 1
  requirement 3): what the reader will see/do differently, not only the
  system analogy — the one recurring content-side follow-up cause.

## [2.24.0] — 2026-07-19

### Added — `git-memory`: close-out privacy gate (fail-closed, two-layer)

`compose-commit.md` and `compose-pr.md` now run a fail-closed two-layer
privacy check over the composed text before it is used: layer 1 is a
deterministic `scripts/privacy-scan.py` (secrets/credential-pattern
scanner plus an optional user-supplied deny-list); layer 2 is a
fresh-context judge over the same composed text per the new
`protocols/privacy-judge-spec.md` (the layer-2 judge SSOT — verdict
shape, escalation, and what counts as a privacy leak beyond
pattern-matchable secrets). `git-memory`'s SKILL.md now points its
privacy bullet at this operational gate instead of prose guidance.

Verification: `dev-workflow/tests/test-privacy-scan.sh`,
`test-privacy-judge-spec.sh`, `test-privacy-gate-compose-commit.sh`,
`test-privacy-gate-compose-pr.sh`, and
`test-git-memory-privacy-gate-ref.sh` all green.

## [2.23.0] — 2026-07-17

### Added — `git-memory`: `--verify-merged` catches the suspicious-empty-body case (#578 live)

PR #578's squash commit on `main` (`2c147cd7`) shipped a body of exactly
one line (the title, ending `(#578)`) even though repo squash settings
were confirmed correct (`PR_TITLE`+`PR_BODY`) and two same-day PRs
carried full bodies. `--verify-merged` exited `0` because its
heading-based check ("no `## Memory` heading → not memory-worthy")
never got a chance to run against a real body — the whole body had
vanished. `memory-grep.sh --verify-merged` now runs a check BEFORE the
heading logic: a title-only body (exactly one non-empty line) whose
title matches the squash-of-PR signature `(#N)` exits `4` immediately
with a stderr message naming the suspicious-empty-body case. A
title-only body WITHOUT a `(#N)` suffix (a routine direct commit) is
unaffected and still exits `0`. Recorded as
`docs/loom/memory/squash-dialog-can-drop-entire-pr-body.md`.

Verification: `for t in dev-workflow/tests/test-*.sh; do bash "$t"; done`
green (8 suites); `test-memory-grep-verify-merged.sh` new cases 6-8
RED-verified against the pre-fix script (case 6 returned 0, expected
4), GREEN against the fix.

## [2.22.1] — 2026-07-17

### Fixed — git-memory raw-trailer-footer mandate overclaim (live-refuted by PR #576)

`git-memory` SKILL.md's squash-merge caveat and `compose-pr.md`'s Step 4
mandate both claimed "PR body ends with the raw trailer footer ⇒
`%(trailers)` parses correctly even on squash `main`." PR #576's squash
merge refuted this: `--verify-strict` exited `4` even though the PR body
ended with the mandated footer, because GitHub's own merge UI appended a
`---------`/`Co-authored-by:` block after the body and hard-wrapped long
trailer lines. Both docs are corrected to best-effort framing — the
mandate's guaranteed floor is grep-level retrieval (`git log --grep`),
not a `%(trailers)` guarantee. The mandate itself (raw footer as the PR
body's absolute last block) is unchanged — it still prevents the #575
in-body-breakage class. Recorded as
`docs/loom/memory/github-ui-squash-appends-coauthor-and-wraps-body.md`.

Verification: `for t in dev-workflow/tests/test-*.sh; do bash "$t"; done`
green (8 suites); `test-git-memory-raw-footer-mandate.sh` Check 5
RED-verified against the pre-fix wording, GREEN against the fix.

## [2.22.0] — 2026-07-17

### Changed — loom-memory hardening (O2/O3/O4/O5/O6b)

`git-memory` carrier doctrine rewritten: the committed file store is now
named the authoritative durable-lesson carrier, with commit trailers as
commit-bound/secondary — plugin-wide sweep for contradicting "durable
substrate" claims. `compose-pr` mechanizes the raw trailer footer as a
distinct required block; `memory-grep.sh` gains `--verify-merged`
(post-squash predicate) and `--verify-strict` (trailer-parse diagnostic).
A post-merge `memory-verify` GitHub Actions workflow runs on push to
main. Orphan shell tests wired into CI.

Verification: `for t in dev-workflow/tests/test-*.sh; do bash "$t"; done`
green.

---

## [2.21.0] — 2026-07-07

### Changed — `brief-before-asking`: hard turn-ordering rule + anti-diagram guidance rescoped

A briefing must never be stacked with an `AskUserQuestion` dialog in the
same turn — end the turn with the briefing as the final text, then ask
inline in a following turn. This recurred (2026-07-03, observed twice)
as a briefing getting buried under the same-turn question dialog.
Anti-diagram guidance is rescoped: explicit visual requests are honored;
option comparisons default to a table instead.

Verification: `loom-pipeline/scripts/test_family_relay.py::test_brief_before_asking_ordering`
passed.

## [2.20.1] — 2026-07-05

### Fixed — `distill-sessions`: Codex dispatch-portability (host-neutral rewrite + reference files)

Following the same class of gap found and fixed in loom-code (#496) and
loom-interface-design/loom-spec (#497), `distill-sessions`'s Stage 3
parallel fan-out and Stage 5c single-dispatch instructions hardcoded
literal Claude-Code `Agent({subagent_type: ..., model: "sonnet", ...})`
call syntax directly in `SKILL.md` and all 3 `agents/*.md` prompt files
— a Codex reader hit syntax it cannot execute. Rewrote `SKILL.md` §Step 2
/ §Step 4b and the "How the orchestrator dispatches this prompt" section
of `agents/prompt-{failure,success}-analysis.md` and
`agents/prompt-advisory-analyst.md` to host-neutral prose, and added new
`references/claude-code-tools.md` + `references/codex-tools.md` carrying
the concrete per-host call shape (including the Claude-Code-specific
`model: "sonnet"` alias gotcha, which has no Codex equivalent — Codex
selects model via a spawned agent's own `~/.codex/agents/*.toml`
profile, not a per-call parameter).

## [2.20.0] — 2026-06-23

### Added — `git-memory`: merge in the trigger surface + verified substrate survival

`dev-workflow:git-memory` now treats branch-close as a memory checkpoint and
verifies — rather than assumes — that decided memory actually lands in a durable
git carrier. Addresses authoring-time under-recording, where memory-worthy PRs
were shipping with an empty git substrate even though the session and Claude-native
`MEMORY.md` had the decisions.

- **P1 — merge joins the gate's trigger surface.** The gate now fires before
  `gh pr merge` (especially `--squash`), not just `git commit` / `gh pr create`.
  Merge is the last checkpoint before a branch closes and the git-side memory
  substrate can end up empty.
- **P2 — substrate survival is verified, not assumed.** A new
  `scripts/memory-grep.sh --verify <ref>` mode confirms a `Decision:` / `Learning:`
  / `Gotcha:` trailer is retrievable by text match (survives squash mid-body):
  exit 0 if found, 4 if the substrate is empty, 1 if no ref is given, 2 if the ref
  is unresolvable. `protocols/compose-pr.md` now REQUIRES the `## Memory` section
  for memory-worthy PRs (the optional framing stays only for non-memory-worthy
  ones) and adds a pre-close dual-carrier verify step. SKILL.md Pillar 2 frames the
  verification as required while keeping the `squash_merge_commit_message=PR_BODY`
  and per-PR merge-commit repo settings genuinely opt-in.

## [2.19.0] — 2026-06-21

### Added — handoff preserves the conversation language (`handoff` 0.2.0 → 0.3.0)

`dev-workflow:handoff` now captures the session's conversation language in the
HANDOFF and carries it across the session boundary. Block 1 frontmatter gains a
`conversation_language` field, and the Resume Launcher embeds a "reply to me in
the conversation language" instruction — the channel actually pasted into the
next session, so the resumed agent continues in the user's language instead of
defaulting to English. Scope is user-facing replies only; subagent / tool output
stays in its source language and is localized before surfacing, as in a normal
session. Fixes the observed bug where a resumed session reverted to English.

## [2.18.0] — 2026-06-20

### Changed — extracted the 5 skill-authoring skills to `skill-dev-toolkit`

`skill-creator-advance`, `skill-judge`, `skill-refactor`, `skill-tuning`, and
`dogfood-skill-testing` moved to the new self-contained `skill-dev-toolkit`
plugin so the skill-authoring lifecycle can be distributed independently.
dev-workflow retains the general developer-workflow tools: git-memory,
brief-before-asking, complexity-critique, proposal-critique, dbt-model-style,
recap-state, handoff, distill-sessions. The description-standard grep guard and
the skill-refactor↔skill-tuning shared-conventions drift gate moved with the skills.

## [2.17.0] — 2026-06-03

### Changed — `dbt-model-style`: close 2 dogfood findings (F1 / F3)

Surfaced by an external-triangulation dogfood (via `dogfood-skill-testing`, a blind
cold-reader on the merged skill — see `docs/skill-dogfood/2026-06-03-dbt-model-style/`):

- **F1 (High)** — the two-block header (§5) is the most-emphasized rule, but its entire
  value rested on **invisible, unverifiable** project tooling (`persist_docs` + a sql→yml
  regex), with no way for a cold user to confirm it is wired up. Added an **"Is it wired
  up? (check once)"** block: a 2-step `persist_docs` + comment-landed check, an explicit
  **degrade-to-readability-only** path when absent, and a note that `validate_header.py`
  checks header *shape*, not persistence. Also glossed `MCP` on first use.
- **F3 (Medium)** — the style-vs-calculation boundary read clean but leaks on real mixed
  edits. Added a **"when a request mixes style and logic"** rule (do the style part, hand
  the logic part back as out-of-scope) and named the one genuinely-blurred case — the
  variant-suffix naming MUST needs a *read* of the computation to verify name-vs-content
  (reading to verify is in scope; changing the computation is not).

## [2.16.0] — 2026-06-03

### Added — `dogfood-skill-testing`: behavioral black-box dogfood for skills-in-development

A **new skill** that exercises a working-tree skill end-to-end before
it ships, across three behavioral axes:

1. **Triggers** — does the skill activate on its intended prompts?
   Runs a real-harness `claude -p` sandbox, with an injection fallback
   when the harness is unavailable.
2. **Output quality** — an executor runs the skill, a **blind
   auditor** scores the result against a rubric built from the skill's
   self-declared contract plus the relevant domain standard.
3. **Cold-start / jargon** — a blind cold-reader surfaces
   activation-description and onboarding friction.

Emits a fix-actionable findings report (with raw outputs) to
`docs/skill-dogfood/`. Ports the `vercel-labs/agent-browser` dogfood
**pattern only** (no code copied — see the skill's `NOTICE`; upstream is
Apache-2.0) onto the skill-testing substrate, filling the
black-box-exploratory gap between `skill-judge` (static),
`skill-creator-advance` (white-box conformance), and `distill-sessions`
(telemetry).

## [2.15.0] — 2026-06-03

### Added — `dbt-model-style`: dbt model style & structure guide

New skill (PR #374): a style + structure guide for dbt models with a
header validator script. See the skill's `SKILL.md`. (Changelog entry
added here for version continuity; the skill landed via #374.)

## [2.14.1] — 2026-05-31

### Changed — `git-memory`: squash-merge retrieval caveat (doc accuracy correction)

Pillar 2 **over-claimed** `%(trailers)` machine-readability. In a
**squash-merge** repo, squash concatenates per-commit messages into the
squash commit's **mid-body**, so per-commit `Decision:` / `Learning:` /
`Gotcha:` trailers are no longer in the footer →
`git log --pretty='%(trailers)'` / `git interpret-trailers --parse` are
**unreliable on the default branch** (they read only the footer). Pillar 2
now carries a squash-merge caveat correcting this.

**Squash-robust retrieval path**: `git log --grep` (TEXT match — survives
squash, still hits the trailers mid-body) **+ the PR `## Memory` section**
(GitHub-hosted, survives squash). `%(trailers)` structured parse stays
reliable on **feature branches** and in **merge-commit / rebase-merge**
repos.

**Two opt-in escape hatches** named for teams needing parseable trailers
on main: (a) set `squash_merge_commit_message = PR_BODY` and end the PR
body with the raw trailer footer; (b) use a **merge-commit** (not squash)
for memory-worthy PRs.

**Doc accuracy correction of a Pillar-2 over-claim — no behavior / config /
workflow change** (the escape hatches are documented as opt-in, not
applied; no repo-setting change, no per-PR merge-strategy mandate). Same
defect class as code-toolkit PR #357 (an accurate-sounding claim that
doesn't hold in the actual environment).

**See also**:
- `docs/loom/specs/2026-05-31-git-memory-squash-retrieval-caveat.md`
  — design brief (squash buries trailers mid-body, `git log --grep` +
  PR `## Memory` retrieval path, two opt-in escape hatches, alternatives
  considered).

## [2.14.0] — 2026-05-31

### Changed — `git-memory`: two readability guardrails for trailer values

`standards/memory-conventions.md` gains **two audience-calibrated
readability guardrails** for trailer values (`Decision:` / `Learning:`
/ `Gotcha:`), calibrated for the future-developer/agent reader doing
`git log` archaeology:

1. **Scannability** — a trailer value leads with its point in the
   first clause; elaboration is pushed to an RFC-822-folded
   continuation line. The existing `Decision:`-only "1-3 sentences"
   cap generalizes into a scannability rule across all trailer types.
   The hard-250 line-length is reframed as a **ceiling, not a
   target** — a value approaching 250 chars wants folding or
   splitting, not a single-line run-on.
2. **Expand session-ephemeral jargon** — a trailer must be legible to
   a reader who was NOT in the session: one-off coinages ("P2",
   cluster names, session-local labels) are expanded or avoided.
   Shared codebase / domain terms (e.g. `gws`) are fine.

**Dual-consumer invariant** (the reason this is a net win, not just a
style nudge): git-memory content serves TWO consumers — the human
archaeologist AND a future **agent** doing `git log --grep='^Decision:'`
retrieval / Phase-3 digest rebuild. The guardrails **restructure, do
not truncate** (point-first + folded elaboration; no facts dropped)
and keep the **machine-parse contract intact** — trailer KEYS stay
line-anchored and continuation lines use standard RFC-822 folding so
`git interpret-trailers` / `%(trailers)` / `--grep` still parse.
Expanding session-ephemeral jargon HELPS the retrieving agent, which
— like the cold human — was not in the session.

A proposed third "diagram venue" guardrail was **dropped**:
`memory-conventions.md` already carries a complete `## Diagram venue`
section (venue table + decision tree), so there was nothing
substantive to add.

**Grounding**: readable-commit canon — Chris Beams,
[How to Write a Git Commit Message](https://cbea.ms/git-commit/)
(body explains what & why, self-contained). The 50/72 subject-line
rule stays out of scope (git-memory owns trailer values + the PR
`## Memory` section, not the commit subject).

**See also**:
- `docs/loom/specs/2026-05-31-git-memory-readability-guardrails.md`
  — design brief (problem framing, dual-consumer invariant, audience
  calibration, dropped diagram-venue guardrail).

## [2.4.0] — 2026-05-22

### Added — `distill-sessions` skill (9th in dev-workflow)

New skill that mines `~/.claude/projects/**/*.jsonl` transcripts and the
existing `/insights` facets to produce **edit proposals** against
existing `dev-workflow:*` and `code-toolkit:*` SKILL.md files. Closes
the empirical-iteration loop: skill author ships v1 → real activations
accumulate in JSONL → mine for missed triggers / false routes /
under-cited references → propose surgical SKILL.md edits → re-ship.

**v0.1 scope (this release)**:

- Read-only telemetry mining — emits proposals, **never auto-edits**
- Targets `dev-workflow:*` and `code-toolkit:*` skills (own + sibling
  plugins under monkey-skills); other plugins out of v0.1 scope
- Pipeline (Stage 1+2 in Python; Stage 3 dispatched to Claude via
  `code-toolkit:dispatching-parallel-agents`; Stage 5 in Python with
  approval gate):
  - Stage 1 (ingest + normalize): `ingest.py`, `facets.py`, `event.py`
  - Stage 1c (signal extraction): `friction_signals.py` (4 detectors
    per Q5 baked thresholds)
  - Stage 2 (aggregate + score + fingerprint): `aggregate.py`
  - Stage 3 entry (subagent payload emit): `main.py`
  - Stage 5 (proposal render + write-back): `propose.py` + `apply.py`
- LLM used only for the final proposal-writeup step; routing,
  aggregation, and proposal selection stay deterministic (Rule 5 of the
  12-rule baseline)

**Pattern**: read-only Mining + LLM-as-judgment-only.
**Knowledge ratio**: E:A:R ~ 60:30:10 (Empirical:Anti-pattern:Reference).

**Differentiation**:
- Heavier than `skill-judge` (which scores a single skill against an
  8-dim rubric without telemetry)
- Lighter than `skill-creator-advance` eval-loop (which generates
  synthetic test queries; this skill uses real activations)
- Lighter than `skill-tuning` (which A/B-tests output quality on a
  single skill; this skill scans the whole `dev-workflow:*` +
  `code-toolkit:*` corpus for drift signals)

**See also**:
- `docs/loom/specs/2026-05-22-distill-sessions-v0.1-brief.md` —
  v0.1 design brief (problem framing, scope decisions, deferred items)
- `docs/loom/specs/2026-05-22-distill-sessions-research.md` —
  background research (JSONL schema, /insights facet anatomy, prior
  telemetry-mining attempts)

## [2.3.0] — 2026-05-14

### Added — `brief-before-asking` skill (8th in dev-workflow)

New skill that enforces a structured briefing before (or in response to)
any complex engineering decision question — a 6-block format with
**Mental Model First** as the load-bearing rule.

The skill addresses a recurring failure mode: when an agent needs the
user to make an engineering call, the agent typically starts at
implementation-level detail with embedded jargon. The user can't land
on the technical content without a system-level mental model first.
`brief-before-asking` enforces the abstraction bridge before the
technical detail.

**Three trigger modes**:

1. **Mode A — Proactive**: agent self-detects an upcoming non-trivial
   decision and delivers the full 6-block briefing before asking
2. **Mode B — Reactive on question**: user says 「看不懂」 / 「什麼意思」
   to a short agent question → agent re-briefs with full 6 blocks +
   re-asks in specific form
3. **Mode C — Reactive on explanation**: user says 「跟不上」 / 「太多術語」
   after a dense agent explanation → agent **retreats** to Mental Model
   + jargon glossary + drill menu, **pauses** (does NOT dump 6 blocks
   again, which would re-drown the user — iteration-4 design insight)

**6-block structure**:

```
Mental Model     1-2 sentences plain English, NO jargon, NO code refs
Situation        Technical state: code refs, metrics, investigation
Why-this-fork    Trigger condition + constraint + cost of not asking
Options          2-4 real options with equal depth (concrete diffs)
My take          Explicit lean + ≥3-step reasoning + conditional reversal
Open ends        What I don't know / would flip my answer / value calls
```

**Resources shipped (v1.0 draft)**:
- `SKILL.md` — the skill spec (235 lines, ~2,530 tokens)
- `test-prompts.json` — 20 test cases (10 from Phase 2 + 10 Mode C /
  ambiguous-"more context" disambiguation cases from Phase 4)
- `trigger-eval.json` — 20-query trigger eval set for description
  optimization (10 should-trigger + 10 should-not-trigger near-miss)
- `references/DESIGN.md` — design rationale + 4-iteration history
- `references/EXAMPLES.md` — bad-vs-good worked examples (Mode C demo)
- `references/IMPLEMENTATION-CHECKLIST.md` — author phase checklist

**Differentiation**:
- Heavier than `proposal-critique` / `complexity-critique` (which gate
  proposals at decision-time without rebuilding context)
- Lighter than full Minto SCQA / formal RFC (which assume cross-team
  audience and post-deliberation cementing)
- Daily-use middleweight for individual complex engineering decisions

**Phase 6 skill-judge advisory grade**: ~105 / 120 (high B, projected
after Top 3 D5/D8/D1 improvements). Pattern: Process. Knowledge ratio
E:A:R ~ 65:30:5.

**Pre-shipped status**: v1.0 draft. Phase 1 (sanity check + 4 friction
patches + rename) / Phase 2 (10-TC test prompts) / Phase 4 (10 more TCs)
/ Phase 6 (skill-judge advisory) complete. Phase 3 (description
auto-optimization) in progress. Phase 7 (skill-tuning A/B variants)
deferred to post-ship feedback.

## [2.2.0] — 2026-05-04

### Added — hardened AskUserQuestion pattern in skill-creator-advance

New reference: `skill-creator-advance/references/asking-user-questions.md`
documenting the empirically-validated 4-hardening pattern for skills that
need structured user input via Anthropic's `AskUserQuestion` tool.

The pattern closes three documented failure modes:
1. **Inline fallback** — model treats question as text instead of tool call
2. **Silent default** — model assumes "(recommended default)" and skips asking
3. **Tool unavailable** — subagent / web client / sandbox contexts have no
   AskUserQuestion; without explicit fallback, model silently defaults

The 4 hardenings (all validated via subagent A/B test on 2026-05-04):

1. **MUST verb** — `MUST call AskUserQuestion` instead of `Use AskUserQuestion`
2. **Args-schema example** — fenced ` ```json ` block showing tool-call args,
   not prose Q&A template
3. **Fallback contract** — explicit clause for tool-unavailable environments
4. **(Recommended) marker** — first option's `label` includes `(Recommended)`

Updates to `skill-creator-advance/SKILL.md`:
- New "Asking the User Structured Questions" subsection in §Skill Writing Guide
- New Pre-Creation Gate 3 ("User-input check") to prompt skill authors to
  apply the hardened pattern when drafting STEPs with user-input branching

Reference file includes:
- The Thariq canonical phrase (load-bearing tokens: `AskUserQuestion`,
  `interview`, `not obvious`)
- Anti-patterns table (7 documented failure modes)
- Copy-paste mandatory-gate template
- Industry references (Anthropic blog, Thariq gist, neonwatty walk-through,
  ClaudeLog, claude-code#9846 plan-mode bug)

Companion to domain-teams v5.6.0's CHK-SKL-014 gate that enforces the
same pattern for domain-team skills.

## [2.1.1] — 2026-05-04

### Fixed — duplicate hooks file load error on Claude Code v2.1.119+

Removed the redundant `"hooks": "./hooks/hooks.json"` field from
`plugin.json`. Claude Code automatically loads the standard
`hooks/hooks.json` location, so declaring the same path in
`manifest.hooks` triggered a duplicate-load error:

```
Failed to load hooks from .../hooks/hooks.json: Duplicate hooks file detected:
./hooks/hooks.json resolves to already-loaded file. The standard
hooks/hooks.json is loaded automatically, so manifest.hooks should
only reference additional hook files.
```

The PostToolUse skill-folder-structure validator added in 2.1.0 still
ships and still fires — only the redundant manifest entry was removed.

## [2.1.0] — 2026-05-03

### Added — plugin-shipped Stop hook for skill folder structure validation

dev-workflow now ships a `PostToolUse` hook on `Write|Edit` that
validates skill folder structure against the Anthropic convention
(subfolders may not themselves contain subfolders). The hook fires
in any project where dev-workflow is installed, catching nested
subdirectory violations the moment they're written.

**Files added**:
- `hooks/hooks.json` — registers `PostToolUse` hook on `Write|Edit`
  matcher pointing to `${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill-folder-structure.sh`
- `scripts/validate-skill-folder-structure.sh` — bash validator. Reads
  PostToolUse JSON from stdin, extracts `tool_input.file_path`, finds
  the affected skill root, runs `find <skill-root> -mindepth 2 -type d`
  to detect nested subdirs. Exit 2 (blocking) on violation, 0 otherwise.

**Plugin manifest** (`.claude-plugin/plugin.json`):
- Added `"hooks": "./hooks/hooks.json"` field

**Coexistence with repo-level hook (no duplicate firing)**:
The script includes explicit dedup logic: if the current repo has
its own `.claude/hooks/validate-skill-folder-structure.sh` (the
"D" pattern from the design discussion), this plugin hook SKIPS
and lets D handle it. This means:

- **In monkey-skills repo** (which ships D as part of its own
  `.claude/hooks/`): D is authoritative, plugin hook (B) defers
- **In any other repo where dev-workflow is installed**: B is the
  only hook, fires normally

Result: zero double-firing in the most common case (you developing
skills inside monkey-skills repo with dev-workflow loaded), AND
extended coverage to the previously-unprotected case (you or others
developing skills outside monkey-skills with dev-workflow installed).

**Test cases verified locally** (all 4 pass):
1. D exists in repo → plugin hook exits 0 (skip, defer to D)
2. No D, valid skill file → exit 0 (no nesting found)
3. No D, synthetic violation in /tmp → exit 2 + clear error message
4. Non-skill file → exit 0 (fast path, doesn't recurse)

**Why bump to 2.1.0** (minor not patch): adding plugin-shipped
hooks materially expands what users get when they install
dev-workflow — they now get runtime enforcement, not just
documentation. New optional capability = minor bump per SemVer.

## [2.0.0] — 2026-04-29

### BREAKING

**`skill-tasting` is renamed to `skill-tuning`.**

- Slash command: `/skill-tasting` → `/skill-tuning`
- Skill directory: `skills/skill-tasting/` → `skills/skill-tuning/`
- All cross-skill forward references updated (skill-creator-advance
  not-trigger; skill-refactor handoff in SKILL.md / READMEs;
  skill-refactor's bundled functional copy headers in 3 shared
  conventions; plugin.json description and keywords; plugin
  READMEs × 3; architecture doc; governance doc; audit runbook;
  telemetry-setup doc; check-shared-conventions-drift.py manifest)
- Migration: anyone using `/skill-tasting` should update to
  `/skill-tuning`. The skill's behavior, frontmatter description
  semantics, gate function, verdict vocabulary (ADOPT / DROP /
  DEFER / REFINE / ESCALATE), and references / scripts are
  otherwise unchanged from v1.7.0.

### Why rename

The "tasting" metaphor (wine/food tasting → subjective judgment)
was chosen in v1.7.0 PR-3 to evoke human-judgment / preference
accumulation and to distinguish from mechanical "testing". In
practice the metaphor proved insufficiently sticky:

- **Mental-model failure** observed: even the original maintainer
  recalled the skill as "skill-testing" rather than "skill-tasting"
  — t/t similarity defeats recognition
- **Multi-language friction**: "tasting" doesn't translate
  naturally; "tuning" maps cleanly via "チューニング" / "調整"
- **Cultural specificity**: wine/food tasting metaphor doesn't
  carry universally
- **Trajectory mismatch**: H4 horizon trains a preference judge
  from the log — that activity is industry-standardly called
  "fine-tuning" / "RLHF tuning". The new name echoes the
  long-term target.
- **Adjacency to anti-trigger**: skill-creator-advance has an
  explicit "Do NOT use /skill-test" anti-trigger; t/t collision
  created ambient confusion

Per the dev-workflow Goodhart audit pattern: when stick failure
is observed, name early and fix early. Cost of renaming at v1 /
single active user is far cheaper than future cross-reference
accumulation.

### Changed (skill-tuning vocabulary)

- Activity-noun replacements throughout skill-tuning's body:
  "tasting reveals" → "tuning reveals"; "tasting session" →
  "tuning session"; "tasting is overkill" → "tuning is overkill";
  "Skill Tasting" → "Skill Tuning"
- **Preserved deliberately**: "taste-sensitive", "Taste is the
  ceiling", "taste does not override", "taste dimension" — these
  use "taste" (the property / abstract concept), not "tasting"
  (the activity). The activity got renamed; the property
  descriptor stays. Skills produce taste-sensitive output; the
  workflow that improves it is now called tuning.
- Trigger keywords expanded with tuning-vocabulary:
  - English: "tune skill", "skill tuning",
    "fine-tune skill output", "preference tuning", "RLHF skill"
  - Chinese: "調整 skill 輸出"
  - Japanese: "スキル チューニング"
  - Multilingual postfix updated: "スキル チューニング" /
    "技能調整"
- Existing triggers preserved: "improve skill output",
  "A/B variants", "output quality", "taste-sensitive skill",
  "改善 skill 輸出", "試不同 phrasing", "出力品質"

### Changed (architecture doc Implementation Status)

`dev-workflow/docs/skill-evolution-architecture.md`:
- Implementation Status table extended with v2.0.0 row
- Note added explaining the rename rationale and that semantics
  / gate function are unchanged from v1.7.0

### Changed (plugin metadata)

- `plugin.json`: 1.9.0 → 2.0.0; description and multilingual
  postfix updated to reference skill-tuning; keywords already
  reflect the rename (set in this commit's bulk replace)
- Plugin READMEs (en/ja/zh-TW): skills table row updated;
  Skill-evolution architecture diagram updated; Repository
  Structure tree updated

### Bump rationale

**Major (1.9.0 → 2.0.0)**: per `skill-governance.md` versioning
policy, "removal of slash command" / "removal of public protocol"
is a major bump. The slash command rename is functionally a removal
of `/skill-tasting` (it no longer triggers anything) plus addition
of `/skill-tuning`. Even though the skill's underlying behavior
is unchanged, the user-facing interface broke.

This is the **first major bump** in dev-workflow's history.
Future breaking changes should follow the same naming-failure-
caught-early pattern: identify, surface, decide quickly, version-
bump rather than letting drift accumulate.

## [1.9.0] — 2026-04-29

### Context

**Final PR of the 5-PR skill-evolution series.** With this release,
H1–H4 horizons from `dev-workflow/docs/skill-evolution-architecture.md`
are all addressed at the scaffolding level. Specifically Layer 0
(foundation telemetry), Layer 5 (closed-loop self-training), and
test-prompts.json bootstrap for the 7 dev-workflow skills.

After this release the skill-evolution rollout is complete at
scaffold level; future work is data-driven (telemetry accumulation
→ audit decisions; preference log accumulation → trained-judge
activation). No further PRs in this series planned.

### Added (Layer 0 — Telemetry foundation)

`scripts/skill-telemetry.py`:
- log / summarize / export operations
- Append skill invocation events to opt-in per-user JSONL log
  (default `~/.claude/skill-telemetry.jsonl`)
- Privacy-conscious by default: prompt content hashed (sha256),
  not stored; prompt_summary opt-in
- Sanitized export with `--strip-*` flags
- Standard library only; standalone executable

`dev-workflow/docs/telemetry-setup.md` (~165 lines):
- Why telemetry (Layer 0 rationale; quarterly audit consumer)
- Privacy stance (local-only, hashed prompts, sanitized export)
- Setup options (manual logging vs hook-driven via Claude Code
  settings.json)
- Running summaries + sanitized export workflows
- Telemetry → quarterly audit integration queries
- What this scaffold does NOT do (no auto-aggregation, no
  cross-skill correlation, no hook event translation — deliberate
  gaps; user chooses what to build on top)
- Troubleshooting + schema versioning

### Changed (Layer 5 — Self-training stub enhancement)

`dev-workflow/skills/skill-tasting/scripts/judge_train_stub.py`:
- Insufficient-data path now prints 6-step activation methodology
  inline (load pairs → 80/20 split → Bradley-Terry training →
  ≥80% held-out gate → vs LLM-judge baseline → deploy as Tier-1
  pre-filter)
- Threshold-met path message now self-documents: reaching this
  path IS the activation signal; open a PR to replace the stub
- Removed version-specific language so the stub ages cleanly
- Reference doc (skill-tasting/references/self-trained-judge-pipeline.md)
  remains the canonical training methodology source; this stub
  output is a tighter pointer

### Added (test-prompts.json bootstrap)

`test-prompts.json` added to all 7 dev-workflow skills:
- skill-creator-advance: build new / redesign existing / vague
  improve (router test)
- skill-judge: 200-line skill scoring / self-referential meta /
  vague request
- git-memory: commit composition with trailers / PR body with
  Memory section / retrieval query
- proposal-critique: 7-item backlog / prose with supporting
  claims / user resistance to triage
- complexity-critique: feature add LOC eval / PAGNI greenfield
  test / vague "make simpler"
- skill-refactor: shrink-skill-creator-advance canonical case /
  taste-sensitive target self-abort / vague target
- skill-tasting: status-report tone / constitution rejection /
  vague output improvement

Each file follows references/test-prompts-schema.md format with
3 prompts (happy / edge / stress categories). These serve dual
purposes:
1. Manual validation by user (closing some validation gates)
2. Future cross-skill regression CI consumer
3. Future self-trained-judge training data

### Changed (architecture doc)

`dev-workflow/docs/skill-evolution-architecture.md`:
- Added "Implementation Status (as of v1.9.0)" section at top
  showing PR-1 through PR-5 status (all merged)
- Horizon coverage table: H1 / H2 / H3 / H4 all marked Complete
  (H4 explicitly noted as scaffolded; training activates at
  ≥1000 preference pairs per skill)
- Outstanding validation gates table: skill-refactor +
  skill-tasting gates noted as audit-tracked, not blocking
- Title bumped from "Planning Doc" to "Planning + Status Doc"
- Status banner: LIVING DOCUMENT
- "Original Planning Doc Begins Below" delimiter so the original
  planning content is preserved verbatim below the new status
  section

### Changed

- `dev-workflow/.claude-plugin/plugin.json`: 1.8.0 → 1.9.0

### Bump rationale

Minor (1.8.0 → 1.9.0): foundation / scaffold additions; no
breaking changes. The telemetry script is opt-in; the trained-
judge stub still fails fast (no behavior change for users who
weren't using it); test-prompts.json files are new artifacts
that don't change skill behavior.

### Final state of the skill-evolution architecture

After this release, dev-workflow ships:

```
proposal-critique  → complexity-critique → skill-creator-advance
(list / plan         (single change gate)   (creation + redesign)
 triage)

skill-judge          skill-refactor        skill-tasting
(advisory score      (Phase A: tokens /    (Phase B: output A/B,
 + drift detection)   structure, output     human judge,
                      preserved; multi-     preference log,
                      judge ensemble +      constitutional
                      git ratchet)          pre-filter)
```

Plus governance infrastructure:
- Cross-skill regression CI (shared-conventions-drift)
- Skill governance doc (SSOT registry, lifecycle states)
- Quarterly audit runbook (7-step checklist)
- Telemetry scaffold (Layer 0)
- Self-trained judge scaffold (Layer 5; activates at threshold)
- test-prompts.json × 7 bootstrap

The 4-skill family (creator / judge / refactor / tasting) +
3 critique skills (proposal / complexity / git-memory) compose to
cover skill creation, evaluation, behavior-preserving refactor,
taste-sensitive A/B, and lifecycle governance — all with explicit
SSOT discipline and same-PR drift rules enforced by CI.

## [1.8.0] — 2026-04-29

### Context

Fourth-of-five PR series (PR-4 of 5) implementing the
skill-evolution architecture. With the Two-Hats split complete in
v1.7.0, this release adds the **governance layer**: cross-skill
regression CI, optional skill-judge drift detection, SSOT registry
documentation, and quarterly audit runbook. The architecture doc
called this "Layer 4 — Governance"; PR-5 will add Layer 0
(telemetry) + Layer 5 (closed-loop self-training judge stub).

### Added (governance & CI)

**Cross-skill regression CI** — `scripts/check-shared-conventions-drift.py`
- Iterates a manifest of (canonical, functional-copies) pairs and
  diffs body content (header blockquote stripped before diff)
- Currently checks 3 conventions (golden-anchor-protocol /
  test-prompts-schema / constitution-schema) between skill-refactor
  (canonical SoT) and skill-tasting (functional copies)
- Verified locally: all 3 in sync at v1.7.0 baseline
- New CI job `shared-conventions-drift` in
  `.github/workflows/skill-structure.yml`; runs on every PR + push
  to main
- Enforces the same-PR drift rule documented in skill-refactor and
  skill-tasting NOTICE files
- Future extension: per-plugin convention manifests; test-prompts
  regression detection when skills have them

**skill-judge score history + drift detection** —
`dev-workflow/skills/skill-judge/scripts/score_history.py`
- New optional companion script (skill-judge remains stateless by
  default; opt-in per skill)
- Operations: append / query / drift
- Drift signal: z-score of most recent vs historical baseline;
  flags if z < -1.0σ (configurable); insufficient-history (<3)
  exits with clear message
- Constant-baseline edge case: absolute drop > 1 point flags
- Drift recommendation: run skill-tasting on flagged skill to
  capture human preference signal
- New "Optional: Score History Tracking (Drift Detection)" section
  in skill-judge SKILL.md (~32 lines added; explains advisory-only
  nature, drift signal mechanics, quick invocation)

**Skill governance documentation** —
`dev-workflow/docs/skill-governance.md`
- SSOT Registry: every shared resource's canonical location,
  functional copies, and CI enforcement mechanism (dev-workflow
  internal + cross-plugin entries)
- Ownership table per skill with attribution chain notes
- Skill Lifecycle States (Active / Deprecated / Retired) with
  transition criteria and current state of all 7 dev-workflow
  skills
- Convention evolution protocol (add / edit / delete)
- Cross-plugin contract reaffirmation
- Versioning policy with examples from dev-workflow history
- Decision authority table
- Anti-patterns

**Quarterly audit runbook** —
`dev-workflow/docs/quarterly-audit-runbook.md`
- 7-step audit checklist:
  1. SSOT registry verification
  2. Skill lifecycle state review
  3. Convention drift inspection
  4. External dependency audit (upstream MIT chains)
  5. Validation gate status
  6. Skill-judge score history drift detection
  7. Documentation freshness
- Audit report template
- Decision matrix for handling each finding type
- Self-extending guidance

### Changed

- `dev-workflow/.claude-plugin/plugin.json`: 1.7.0 → 1.8.0 (minor
  bump for governance additions; no skill behavior changes)

### Validation status carry-over

Outstanding from earlier PRs (now formally documented as audit-
trackable in the runbook):
- skill-refactor: dry-run on ≥2 existing skills, ≥90% equivalence-
  check agreement
- skill-tasting: 1 real-skill walkthrough validating A/B flow
  produces meaningful preference signal

These will be tracked as "Outstanding validation gates" in the
quarterly audit until completion.

### Bump rationale

Minor (1.7.0 → 1.8.0): governance additions (CI, scripts, docs);
no breaking change to skill behavior. The skill-judge SKILL.md
addition is opt-in (script is purely supplemental).

## [1.7.0] — 2026-04-29

### Context

Third-of-five PR series implementing the skill-evolution
architecture (`dev-workflow/docs/skill-evolution-architecture.md`).
PR-1 (v1.5.0) prepared scope; PR-2 (v1.6.0) shipped `skill-refactor`
(Phase A); this PR-3 / v1.7.0 ships `skill-tasting` (Phase B) — the
feature-hat counterpart to refactor's refactor-hat. The Two-Hats
split is now complete.

PR-4 / PR-5 will add governance (cross-skill regression CI,
skill-judge drift detection, audit runbook) and telemetry +
self-training pipeline scaffolding.

### Why skill-tasting exists

Skill outputs have *taste-sensitive dimensions* (style, voice,
tone, rhythm, persuasive force) that LLM-as-judge cannot reliably
evaluate. A skill that "works" can still produce outputs that are
flat, off-tone, or just not what the user wanted.

`skill-tasting` is the **feature hat** counterpart to
skill-refactor's refactor hat: refactor preserves behavior (using
LLM-as-judge to verify equivalence — a binary check LLMs handle
well); tasting deliberately changes behavior to find better outputs
(using human judgment because taste is exactly where LLM-as-judge
fails).

### Added (skill-tasting)

New `dev-workflow/skills/skill-tasting/`:

- **`SKILL.md`** — Iron Law (3-part: constitution honored + human
  preference captured + log updated), Before-You-Begin baseline +
  constitution + goldens prerequisites, 4-phase Gate Function
  (variant generation + constitutional pre-filter + blind A/B
  harness + verdict + log), verdict vocabulary (ADOPT / DROP /
  DEFER / REFINE / ESCALATE) parallel to other dev-workflow
  critique skills, Constitutional Judging mechanic, Preference
  Log → Self-Trained Judge horizon scaffold (H4), Red Flags,
  Rationalization Prevention, 2 worked examples (status-report
  tone improvement + variant rejected by constitution)
- **`commands/skill-tasting.md`** — slash command redirect
- Tasting-specific references (4 files):
  - `references/ab-harness-protocol.md` — variant generation
    rules, random label assignment, side-by-side display, 4-option
    capture, multi-evaluator extension, truncation, atomicity
  - `references/constitutional-judging.md` — how MUST clauses test
    variants in pre-filter; binary satisfied/violated; ambiguity
    handling; reporting filtered variants; constitution evolution
    from tasting; constitutional ratchet
  - `references/preference-log-schema.md` — JSONL format
    (append-only), per-pick entry schema, per-session summary,
    privacy considerations, retention, lifecycle events, querying
  - `references/self-trained-judge-pipeline.md` — H4 horizon
    scaffold; activation thresholds (≥1000 entries); training
    methodology (Bradley-Terry-style); deployment as Tier 1
    pre-filter; cross-skill transfer (research territory)
- Bundled functional copies of 3 shared conventions:
  - `references/golden-anchor-protocol.md`
  - `references/test-prompts-schema.md`
  - `references/constitution-schema.md`
  All carry "bundled functional copy" header blockquote pointing
  to skill-refactor as the canonical SoT for evolution. Same-PR
  drift rule documented in NOTICE.
- Scripts (3 scaffold files):
  - `scripts/ab_harness.py` — Phase 3 blind A/B orchestration
    (variant collection, random labels, side-by-side rendering,
    truncation, atomic decision capture)
  - `scripts/preference_log.py` — JSONL operations (append /
    query / summarize / export-for-training with ≥N threshold)
  - `scripts/judge_train_stub.py` — H4 stub; documents training
    interface; fails fast with "scaffolded, not active in v1.7.0"
- **`LICENSE`** — MIT, single copyright (c) 2026 kouko, original
  design (not a port or fork)
- **`NOTICE`** — 9 enumerated design distinctions vs darwin-skill;
  inspirations (autoresearch, darwin-skill, voice-anchors
  curation, RLHF/preference-modeling literature, Fowler Two Hats,
  internal architecture doc); convention sharing arrangement with
  skill-refactor
- **`README.{en,ja,zh-TW}.md`** — three-language READMEs

### Changed (skill-creator-advance)

- Description: added negative trigger routing output A/B testing
  to `skill-tasting`. The "Improving Existing Skill" router's
  case (b) now hands off to a real skill (was forward-reference
  in PR-1).
- Removed PR-1 transitional note about skill-refactor / skill-
  tasting being "referenced but not yet shipped" — both now ship.
  Case (c) intro text simplified accordingly.

### Changed (skill-refactor)

- All `*(when available)*` parenthetical placeholders next to
  skill-tasting references stripped — skill-tasting is now a
  concrete sibling, not a forward-reference. Affects SKILL.md
  and 3 READMEs.
- 3 shared convention files (golden-anchor-protocol /
  test-prompts-schema / constitution-schema): header blockquotes
  updated to mark skill-refactor as canonical SoT location and
  skill-tasting as functional copy. Same-PR drift rule documented.

### Changed (plugin)

- `plugin.json`: 1.6.0 → 1.7.0; description appended with
  "skill-tasting (blind variants + constitutional pre-filter +
  preference log)"; multilingual postfix updated; keywords gain
  "skill-tasting"
- `README.{en,ja,zh-TW}.md`: skills table adds skill-tasting row;
  Skill-evolution architecture diagram updated (Phase B no longer
  marked planned — it shipped); Repository Structure tree adds
  skill-tasting/ folder

### Cross-skill independence statement

`skill-tasting` is **runtime self-contained**. No cross-plugin
dependency. The 3 shared convention files are bundled functional
copies; runtime works with `dev-workflow` alone (no `domain-teams`,
no `skill-refactor` even — though they compose well together).

The SSOT-and-functional-copy pattern continues from PR #159
(code-team mindsets) and PR-2 (skill-refactor canonical conventions).

### Validation status

⚠️ Validation gate per architecture doc §6: "manually run
skill-tasting through 1 real-skill walkthrough; verify the A/B
flow produces meaningful preference signal."

**OUTSTANDING** — this PR ships before formal validation. PR
description notes the caveat. Recommended first validation
target: a copywriting / status-report style skill where taste-
sensitive output is the natural test case.

### Bump rationale

Minor (1.6.0 → 1.7.0): new skill addition; no breaking change.
skill-creator-advance description gains another not-trigger
(refinement, not behavior change). skill-refactor's
forward-reference cleanup is also a refinement.

## [1.6.0] — 2026-04-29

### Context

Second-of-five PR series implementing the skill-evolution
architecture (see `dev-workflow/docs/skill-evolution-architecture.md`).
PR-1 (v1.5.0 + skill-creator-advance scope tightening) prepared the
ground; this PR-2 / v1.6.0 lands `skill-refactor` — Phase A of the
Two-Hats split — with all H1-H3 features in one shot.

PR-3 will add `skill-tasting` (Phase B); PR-4 / PR-5 add governance,
cross-skill CI, telemetry, and self-training judge scaffolding.

### Why skill-refactor exists

Skills accumulate tokens. SKILL.md files grow over edits. Most
edits are additive — fixing corner cases, adding examples — and
result in larger skills with the same (or worse) output behavior.
Without an explicit gate, every edit defaults additive.

`skill-refactor` is the **refactor hat** applied to skills:
improve structure / shrink tokens **without changing what the skill
does**. Output equivalence is enforced by a multi-judge ensemble +
structured comparison; any behavior-changing edit is out-of-scope
and routes to `skill-creator-advance` (structural redesign) or
`skill-tasting` (output quality, taste-sensitive).

### Added (skill-refactor)

New `dev-workflow/skills/skill-refactor/`:

- **`SKILL.md`** — Iron Law (3-part discipline: equivalence + ≥10%
  token reduction + invariant preservation), Before-You-Begin
  baseline capture, Gate Function (Q1 multi-judge ensemble +
  structured comparison; Q2 token threshold; Q3 invariant snapshot
  diff), verdict vocabulary (PROCEED / RESHAPE / REJECT) parallel
  to `complexity-critique`, refactor moves catalog with risk
  classification, Tier 1/2/3 cascade for ensemble disagreement,
  Red Flags, Rationalization Prevention, 2 worked examples (token
  bloat success + subtle behavior-change rejection)
- **`commands/skill-refactor.md`** — slash command redirect
- **`references/equivalence-check-protocol.md`** — Q1 two-layer
  check details (Layer 1 structural / Layer 2 LLM-judge ensemble);
  consensus matrix; specific-behavior-diff override rule
- **`references/multi-judge-ensemble.md`** — 3-judge spawn protocol
  with varied prompt framing (utility / content / boundary);
  random output labeling for position-bias mitigation
- **`references/refactor-moves-catalog.md`** — Fowler-inspired
  catalog of refactor-hat-safe moves (Low/Medium/High risk);
  out-of-scope moves table routes to other skills
- **`references/golden-anchor-protocol.md`** — *shared convention*
  (also in skill-tasting when shipped); same-PR drift rule
- **`references/test-prompts-schema.md`** — *shared convention*
- **`references/constitution-schema.md`** — *shared convention*
- **`scripts/equivalence_check.py`** — Layer 1 structural
  comparison (5 deterministic checks); standalone Python, stdlib
  only
- **`scripts/multi_judge.py`** — Layer 2 ensemble aggregation +
  consensus rule application; specific-behavior-diff override via
  regex pattern matcher
- **`scripts/golden_compare.py`** — Tier 2 anchor similarity
  comparison (Jaccard + length ratio)
- **`LICENSE`** — MIT, single copyright (c) 2026 kouko, original
  design (not a port or fork)
- **`NOTICE`** — explicit design distinctions vs darwin-skill
  (8 enumerated differences); inspirations acknowledged
  (autoresearch, darwin-skill, Fowler Refactoring); no copyright
  dependencies
- **`README.{en,ja,zh-TW}.md`** — three-language READMEs

### Changed (skill-creator-advance)

- Description: added negative trigger routing token / structure
  refactor work to `skill-refactor`. Held back from PR-1 to avoid
  dangling reference; activated in this PR now that skill-refactor
  exists.

### Changed (plugin)

- `plugin.json`: 1.5.0 → 1.6.0; description appended with
  "skill-refactor (multi-judge ensemble + git ratchet)"; multilingual
  postfix updated (skill リファクタ / skill 重構); keywords gain
  "skill-refactor"
- `README.{en,ja,zh-TW}.md`: skills table adds skill-refactor row;
  "the critique line" diagram extended to show
  skill-refactor / skill-tasting positioning; Repository Structure
  tree adds the new skill folder

### Cross-plugin / inter-skill independence

`skill-refactor` is **runtime self-contained**. No cross-plugin
dependency. The 3 shared convention files (golden-anchor /
test-prompts / constitution) are bundled in the skill's own
`references/` directory. When `skill-tasting` ships in PR-3, the
same 3 convention files will be **functional copies** in that
skill's `references/`, governed by a same-PR drift rule. This
mirrors the SSOT-and-functional-copy pattern established for
code-team mindsets in PR #159.

### Validation status

⚠️ Validation gate per `dev-workflow/docs/skill-evolution-architecture.md`
§6: dry-run on ≥2 existing skills with ≥90% equivalence-check
agreement. **OUTSTANDING** — this PR ships the skill before formal
validation. PR description notes the caveat. Recommended first
validation target: skill-creator-advance itself (already over the
soft cap and a natural test bed).

### Bump rationale

Minor (1.5.0 → 1.6.0): new skill addition; no breaking change to
existing skills' behavior. skill-creator-advance description gains
a not-trigger, which is a refinement, not a behavior change.

## [1.5.0] — 2026-04-29

### Context

dev-workflow's "critique" line previously had one skill —
`proposal-critique` — that operates on multi-item proposals (lists,
plans, prose) **before any code is written**. A second failure mode
sits one stage downstream: a *single proposed change* to *existing
code* (refactor, feature add, debt cleanup) defaults to *additive*
unless something forces the design conversation to ask "what's the
smallest end state and what becomes obsolete".

Anthropic's `simplify` skill catches additive code *after* it is
written; `superpowers:brainstorming` catches greenfield design *with
no existing code as baseline*. The gap was the design-time gate for
*existing-code change decisions*.

`complexity-critique` (this release) closes that gap and forms a
sibling to `proposal-critique` with parallel gate-skill shape but
distinct scope:

```
proposal-critique  →  complexity-critique  →  Anthropic simplify
(list / plan       (single change to       (post-implementation
 / prose,           existing code,           diff review)
 before any code)   before implementing
                    the change)
```

### Added (complexity-critique)

New `dev-workflow/skills/complexity-critique/` — single-file gate
skill (~270 lines SKILL.md + 3-language READMEs) for evaluating any
change to an existing codebase through a deletion-first lens. Three
mechanical questions:

1. **Q1 — smallest end state.** Not the smallest *change* — the
   smallest *result*. Could the feature be deleted entirely? Could
   2 functions replace 14?
2. **Q2 — before/after LOC count.** If after > before, reject the
   change as proposed. The metric is end-state volume, not effort.
3. **Q3 — what becomes obsolete.** Every change makes something
   else available to delete.

Verdict vocabulary parallel to proposal-critique:
- **PROCEED** — change reduces total code; ship.
- **PROCEED-WITH-CAVEAT** — net-neutral or marginal; ship but name
  the trade-off bought ("30 lines bought, exhaustiveness check
  enforced"). Hidden growth is the failure mode this skill exists
  to prevent.
- **RESHAPE** — change adds; Q1 produced a smaller end state; propose
  the alternative.
- **REJECT** — change adds with no end-state justification; redirect
  to deletion.

The body adapts the same idiom as proposal-critique: Iron Law / Gate
Function / Verdict / Red Flags / Rationalization Prevention /
Reference Mindsets / Composes With / Worked Examples (×2: form
validation feature add + type-safety refactor) / When To Apply
(with explicit Not-triggers) / Bottom Line.

Three-language READMEs (en / ja / zh-TW) follow the dev-workflow
pattern with mermaid flow + verdict table + worked example +
relate-to-others + lineage + known limitations.

### Cross-plugin reference

The skill references 4 philosophical mindsets that live in
`domain-teams:code-team/standards/` (released in domain-teams v5.5.0):

- `mindset-data-over-abstractions.md` — Perlis Epigram #9 / Hickey
- `mindset-design-is-taking-apart.md` — Hickey / Out of the Tar Pit
- `mindset-expensive-to-add-later.md` — Willison PAGNI
- `mindset-simplicity-vs-easy.md` — Hickey

Per CLAUDE.md §Cross-Plugin Delegation Contract: paths only, no
content duplication. Mindsets are advisory deepening, not gates;
the three-question gate is self-sufficient when domain-teams is not
installed.

### Upstream chain (MIT)

```
joshuadavidthomas/agent-skills (MIT, original)
  → softaworks/agent-toolkit/skills/reducing-entropy (MIT, fork)
    → kouko monkey-skills/dev-workflow/complexity-critique (this)
```

Renamed from `reducing-entropy` for clearer trigger semantics
("entropy" is jargon; "complexity-critique" parallels the existing
`proposal-critique` skill). The 4 mindsets that lived inside the
upstream skill's `references/` directory are extracted to
`domain-teams:code-team` as separate standards with primary-source
citations rewritten against the underlying books / talks / papers
(Perlis 1982, Hickey 2011/2012, Moseley & Marks 2006, Ousterhout
2018, Brooks 1986, Willison/Plant/Kaplan-Moss 2021). Full chain
detail in `skills/complexity-critique/NOTICE`.

### Modifications vs upstream

- Renamed `reducing-entropy` → `complexity-critique` (rationale above)
- Mindset library extracted to `domain-teams:code-team/standards/`
  with primary-source citation rewrite
- Cross-plugin delegation: skill references mindsets via paths, not
  content duplication
- Added explicit verdict vocabulary (PROCEED / PROCEED-WITH-CAVEAT /
  RESHAPE / REJECT) parallel to proposal-critique
- Restructured frontmatter (negative triggers, multilingual keywords)
  to match dev-workflow conventions
- Scope clarified to *changes to existing codebase*; greenfield
  design and post-implementation review explicitly out of scope and
  delegated to `superpowers:brainstorming` and Anthropic `simplify`
  respectively
- Removed the upstream "load at least one mindset before proceeding"
  hard precondition; mindsets are now advisory deepening
- Added 2 worked examples (form validation feature add demonstrating
  RESHAPE; type-safety refactor demonstrating PROCEED-WITH-CAVEAT)
- Added 3-language READMEs following dev-workflow i18n pattern
- Removed upstream `references/` directory and
  `adding-reference-mindsets.md` meta-skill (replaced by skill-team
  conventions for adding new standards in domain-teams)

### Changed (plugin)

- `plugin.json` — version 1.4.0 → 1.5.0; description and keywords
  updated to include `complexity-critique`
- `README.md` / `README.ja.md` / `README.zh-TW.md` — Skills table
  adds `complexity-critique` row; Repository Structure tree adds
  the new skill directory; version line bumped (also catches up
  the missed bump from PR #158 / v1.4.0 skill-judge release —
  README version field was stuck at 1.0.4)

### Note on missed [1.4.0] CHANGELOG entry

The PR #158 / v1.4.0 release (skill-judge integration, 2026-04-29
earlier today) updated `plugin.json` to 1.4.0 but did not add a
[1.4.0] entry to this CHANGELOG. The [1.4.0] gap between [1.3.0]
and [1.5.0] is intentional in this release; a retroactive [1.4.0]
entry can be added in a separate housekeeping commit if desired.
The skill itself is fully documented in
`skills/skill-judge/README.md` and `skills/skill-judge/NOTICE`.

## [1.3.0] — 2026-04-25

### Context

This session repeatedly demonstrated a recurring failure mode: when
Claude proposes a multi-item plan / backlog / recommendation list,
the default behavior is to over-engineer (7-item P0–P3 lists,
speculative content, YAGNI violations). Without explicit user
pushback ("業界證實了嗎", "可以簡化嗎", "複雜度評估"), bloated
proposals ship as-is. The pattern recurred 4 times in this session
within a single artifact (description-design.md): a 7-item backlog
got triaged to 1 KEEP / 1 DEFER / 5 DROP; a 4-section anti-pattern
duplication got deleted; a "research → apply → reflect → simplify"
4-step pipeline proposal got narrowed to a single post-proposal
checkpoint. The recurring fix had a clear shape — three buckets and
two checks — that's now a skill anyone can invoke.

### Added (proposal-critique)

New `dev-workflow/skills/proposal-critique/` — single-file gate
skill (~215 lines) for triaging proposals into KEEP / DEFER / DROP
via evidence grounding (cited / heuristic / speculative) and YAGNI
(essential / speculative). User-invoked primary mechanism; auto-
trigger on Claude's own list-shape output explicitly **deferred to
Phase 2** until v0.1 dogfood proves user-driven triggering reliable.

The body adapts the `superpowers:verification-before-completion`
idiom: Iron Law / Gate Function / Triage Matrix / Common Failures /
Red Flags / Rationalization Prevention / Composes With / Worked
Examples (×2: list shape + prose shape with DECOMPOSE step) / When
To Apply / Bottom Line.

The skill is **shape-agnostic** — handles list-shaped proposals
(numbered backlog, P0/P1/P2) and prose-shaped proposals
(architecture decisions, strategy memos, single recommendations
with supporting claims) via an `ENUMERATE-OR-DECOMPOSE` first step.

### Changed

`dev-workflow/.claude-plugin/plugin.json` version 1.2.0 → 1.3.0
(minor, additive). `description` extended to name 3 skills.
`dev-workflow/README.md` Skills table extended; directory tree
updated. Repo-root `.claude-plugin/marketplace.json` description
extended (multilingual belt now includes 提案審查).

## [1.2.0] — 2026-04-25

### Context

Distills lessons from the `git-memory` skill's v0.1.5 description rewrite
(monkey-skills PR #142) into reusable guidance for `skill-creator-advance`.
The git-memory rewrite cut its `description` from 650 chars (read-path
triggers only, mechanism prose front-loaded) to 287 chars (Anthropic-aligned
WHAT+WHEN, both write/read paths, "about-to-violate" symptoms). The full
research — covering Anthropic Skills docs, Anthropic best-practices,
Agent Skills spec, and an empirical study of all 14 official superpowers
SKILL.md descriptions — is now reusable for any future skill author via
`skill-creator-advance`.

### Added (skill-creator-advance)

New `references/description-design.md` (~250 lines). Covers:

- How skill discovery actually works (LLM semantic match in the forward
  pass, not regex / fuzzy / vector embedding) and the three implications
- The Anthropic-vs-Superpowers tension resolved: WHAT (outcome) is
  Anthropic-approved; WORKFLOW (process steps) is what Superpowers
  warns against — different phenomena conflated by the rule statement
- Six design principles (WHAT+WHEN front-loading, third-person,
  about-to-violate symptoms, natural keywords, length budget,
  multilingual belt as optional insurance)
- "About-to-violate" symptom catalog drawn from 14 superpowers skills
  (`before writing implementation code`, `before merging`, etc.)
- Length empirics: superpowers median 107 chars, range 79–234, all
  well under 1024-char Agent Skills cap and 1536-char Claude Code
  truncation point
- YAML `>-` block-folded rendered length gotcha
- Validation checklist + anti-patterns table
- Worked example: git-memory v0.1.0 → v0.1.5 before/after rewrite

§Description Best Practices in SKILL.md reorganized into 7 numbered
patterns with a pointer to the new reference for the deep dive.
Existing guidance ("pushy", "negative triggers", "multilingual",
"before/after example") preserved verbatim.

### Changed

`dev-workflow/.claude-plugin/plugin.json` version 1.1.0 → 1.2.0
(minor: additive reference content + reorganized SKILL.md section,
backwards-compatible).

## [1.1.0] — 2026-04-24

### Context

monkey-skills PR #137 added the `git-memory` skill (portable
git-backed project memory via commit trailers + PR `## Memory`
section) to the `dev-workflow` plugin alongside the existing
`skill-creator-advance`. plugin.json version was bumped at PR #140
but the CHANGELOG entry was missed at the time; this entry is
retroactive to mark the additive skill addition.

### Added

`dev-workflow/skills/git-memory/` — portable, tool-agnostic project
memory using git commit messages and PR bodies as the substrate.
Phase 1 MVP includes:

- `SKILL.md` with the three pillars (carrier / structure / content)
- `standards/memory-conventions.md` — trailer schema (`Decision:` /
  `Learning:` / `Gotcha:` / `Related:`), PR body `## Memory`
  section layout, ASCII-vs-Mermaid diagram venue rules
- `protocols/compose-commit.md` + `protocols/compose-pr.md` — Claude
  authoring guidance for the write paths
- `scripts/memory-grep.sh` — retrieval primitive emitting plain or
  JSON output, parses trailers via `git interpret-trailers --parse`
  (added v0.1.2) and validates `--limit` as positive integer (v0.1.3)

dev-workflow plugin description updated to name both skills.

## [1.0.4] — 2026-04-15

### Context

Paired with `domain-teams` v4.21.1 (same PR). Domain-teams made Empty
Invocation Fallback a hard-required SKILL.md section with surface-
orientation synthesis and 5-source sufficient-context check. This
release adds a companion **guidance** (not hard requirement) to
`skill-creator-advance` so authors of generic Claude skills can apply
the same pattern when building conversational or multi-workflow skills.

### Added (skill-creator-advance)

New §Empty-Prompt Onboarding subsection under §Skill Writing Guide
(between "Principle of Lack of Surprise" and "Writing Patterns").

The subsection covers:
- When to include the pattern (recommended for conversational /
  multi-workflow skills; unnecessary for single-shot utility skills)
- 3-element pattern: Surface orientation / Route to intake /
  Sufficient-context skip
- Sufficient-context check must cover 5 sources: current prompt,
  prior conversation, IDE context, plan/memory, upstream handoff
- Common pitfall: triggering orientation on empty-current-prompt
  alone creates friction for returning users
- Cross-reference to `domain-teams/skills/skill-team/standards/skill-md-structure.md`
  §Empty Invocation Fallback Rules as the rigorous domain-team
  version (with §Surface Orientation Format skeleton and CHK-SKL-013
  gate)

+23 lines. No breaking change.

## [1.0.3] — 2026-04-15

### Context

PR #73 was merged at commit bd344a4 (Mermaid guidelines only); the
line→token budget migration commit (d0b1b2c) was not included. This
PATCH restores the dev-workflow portion of that migration.

### Fixed (skill-creator-advance — line→token budget consistency)

Completing the line→token budget migration per `plugin-conventions.md`
§Lightweight SKILL.md canonical guidance ("Use word/token count rather
than line count — lines vary too much in density"):

- `SKILL.md` Key patterns: reference TOC threshold
  ">300 lines" → ">~8,000 tokens"
- `SKILL.md` Working-with-existing-plugin enum:
  "line budgets" → "token budgets"
- `references/plugin-conventions.md` §Lightweight Structure:
  "under 300 lines" → "under ~3,000 tokens"

### Kept as-is (correct current usage)

- `NOTICE:46` — historical migration record
- `references/mermaid-usage-guidelines.md` mentions of "token or line
  count" — accurate discussion of both metrics
- `references/plugin-conventions.md:85` "Use word/token count rather
  than line count" — canonical guidance

## [1.0.2] — 2026-04-15

### Added (skill-creator-advance)
- **New reference**: `references/mermaid-usage-guidelines.md`.
  Generic skill-authoring guidance for when to use Mermaid diagrams
  vs prose. Covers decision criterion (≥3 branch conditions OR ≥4
  state transitions), strong-candidate categories (decision trees,
  state machines with retry loops, routing with failure branches),
  avoid-categories (bibliographies, rationale, corpora, philosophy,
  clean tables, linear sequences), cost-benefit framework, Mermaid
  type selection, syntax conventions, and anti-patterns.
- SKILL.md references/ listing updated to include the new reference.

### Rationale

Complements `domain-teams/skill-team v4.19.0` which shipped the
domain-team-specific version. This version is generic (no gate-system
assumptions) and serves any Claude skill author, not just domain-team
skills.

Empirical finding from the precedent: Mermaid adds clarity to
branching logic but does NOT reduce token/line count when paired
with explanatory prose. The value is eliminating prose ambiguity,
not compression.

## [1.0.1] — 2026-04-14

License compliance: add missing `LICENSE` and `NOTICE` files to the
`skill-creator-advance` skill and correct the upstream attribution
previously misstated in the v1.0.0 CHANGELOG.

### Corrected upstream attribution

v1.0.0 stated "based on Anthropic's skill-creator with 7 enhancements"
and that bundled agents/scripts came "from Anthropic skill-creator."
The accurate upstream chain is:

1. **Anthropic `skill-creator`** (MIT) — the earliest upstream; provides
   the eval-loop concept and file naming for bundled agents (grader,
   comparator, analyzer) and scripts (aggregate_benchmark, run_eval,
   run_loop, improve_description, package_skill, quick_validate,
   generate_report, utils).
   https://github.com/anthropics/skills/tree/main/skills/skill-creator
2. **AllanYiin (尹相志) `skill-creator-advanced`** (MIT, Copyright (c)
   2026 AllanYiin) — **the direct upstream** this plugin adapted from.
   https://github.com/AllanYiin/Amon
   Path: `src/amon/resources/skills/skill-creator-advanced/`
3. **`dev-workflow/skills/skill-creator-advance/`** (MIT, Copyright (c)
   2026 kouko) — this distribution.

The v1.0.0 CHANGELOG incorrectly implied direct derivation from
Anthropic. The direct upstream is Allan's work, which in turn draws
from Anthropic (Allan's own reference files in the upstream
acknowledge "upstream skill-creator").

### Added

- `dev-workflow/skills/skill-creator-advance/LICENSE` — MIT license
  preserving AllanYiin's copyright + adding kouko's copyright for
  modifications, per MIT requirement that upstream notices be retained
  in all copies or substantial portions.
- `dev-workflow/skills/skill-creator-advance/NOTICE` — detailed
  upstream chain, per-version modifications, and link to Allan's
  Facebook announcement of the original skill-creator-advanced.

### Also (repo-root, in the same fix PR)

- Root `LICENSE` (MIT) — corresponding to the MIT declaration in the
  main `README.md` which previously had no license file backing it.
- Root `ATTRIBUTION.md` — summary table of all third-party components
  across all plugins (obsidian kepano skills, obsidian axtonliu visual
  skills, skill-creator-advance lineage).
- `obsidian/skills/README.md` — fixed 3 axtonliu upstream URLs that
  incorrectly pointed to `github.com/anthropics/claude-code-skills`;
  corrected to `github.com/axtonliu/axton-obsidian-visual-skills`.

### Not a breaking change

No skill content modified. Pure license-compliance housekeeping.
v1.0.0 consumers continue to work unchanged; this PATCH only adds
license / attribution files and corrects documentation text.

## [1.0.0] — 2026-04-13

Initial release of the dev-workflow plugin with `skill-creator-advance`.

### Added

- **skill-creator-advance** skill — general-purpose skill creation and
  iterative improvement tool. Adapted from AllanYiin's `skill-creator-
  advanced` (MIT; upstream at github.com/AllanYiin/Amon, path
  src/amon/resources/skills/skill-creator-advanced/), which itself
  draws on Anthropic's upstream `skill-creator`. See LICENSE and NOTICE
  in the skill directory for the full upstream chain. Added the
  following 7 enhancements in this distribution:
  1. monkey-skills ecosystem integration guidance
  2. Description best practices (negative triggers, multilingual keywords)
  3. Eval flow tiering (quick path vs full path)
  4. Existing skill improvement workflow
  5. Slash command creation guidance
  6. Self-assessment pass (auto-fix obvious defects before human review)
  7. Auto-regression detection across iterations

- **Bundled agents**: grader, comparator, analyzer (inherited via
  AllanYiin's skill-creator-advanced, which in turn took the file
  naming convention from Anthropic's upstream skill-creator)

- **Bundled scripts**: aggregate_benchmark, run_eval, run_loop,
  improve_description, package_skill, quick_validate, generate_report
  (same inheritance chain as agents)

- **Reference files**:
  - `plugin-conventions.md` — plugin ecosystem conventions and slash commands
  - `iteration-automation.md` — self-assessment and regression detection protocols
  - `platform-adaptations.md` — Claude.ai and Cowork adjustments
  - `eval-methodology.md` — eval principles with primary source citations
  - `schemas.md` — JSON structures for evals, grading, benchmarks

- **Slash command**: `/skill-creator-advance`

### Design decisions

- Eval results presented **inline + markdown report** instead of browser-based
  eval-viewer (removed dependency on Python web server and browser)
- Token-based budget (~6,000 tokens) instead of line-based (500 lines)
- Platform adaptations extracted to reference file (optional, loaded on demand)
- Eval methodology grounded with primary source citations (Fisher 1935,
  Beck 2002, Hastie et al. 2009, Myers et al. 2011, ISTQB v4.0, etc.)
