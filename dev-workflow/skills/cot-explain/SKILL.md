---
name: cot-explain
version: 0.1.0
# Over the 250-char soft lint by design: the process-vs-state contrast IS the
# routing surface. Without it the skill fires on "what does this function do",
# where the answer is two sentences, not a generated page. Retained surfaces:
# named-file, this-conversation, process-verbs, and the state counterexample.
description: |
  Explains how something was reasoned — a file the user names, or the work just done here — as a standalone page built around a chain-of-thought diagram, every arrow labeled with why that step follows. Use when the request is about a process: how a conclusion was reached, why a design went one way, what was tried and rejected; or when the user asks for the artifact by name — a CoT diagram, a CoT mermaid chart, a reasoning-chain write-up. A request about a state — what a function does, what a file says — is answered directly without this skill, and a request for a diagram that is not a chain of reasoning belongs to a general Mermaid skill.
---

# CoT Explain

## What this skill does

Takes reasoning that already exists — in a document, a folder of
documents, or this conversation — and renders it as **one self-contained
HTML page** whose core is a chain-of-thought Mermaid diagram following
the house convention in `references/mermaid-cot-spec.md`.

It is a **one-shot generator with no persistent state**. It reads, it
renders, it stops. Nothing is tracked across sessions.

The audience is a **human who was not there**. Every design rule below
serves that: labeled edges so the reader can follow the jump, a handful
of bullets per node so each step is checkable, a rejected-options table
so the reader sees what was ruled out rather than what was never
considered, and a layout chosen by measurement so the whole chain fits
on one screen instead of scrolling sideways.

## When to fire

Fire when the user wants existing reasoning made visible to someone else.
Do not fire to *do* the thinking — this skill explains thinking that has
already happened.

| Situation | Skill |
|---|---|
| Explain reasoning that already exists, as a shareable page | **this skill** |
| Still working the problem out, across sessions, with tracked assumptions | `think-orbit:thinking-session` |
| An assumption behind past reasoning just broke | `think-orbit:break-assumption` |
| Lost the thread mid-conversation, need re-orientation in chat | `dev-workflow:recap-state` |
| Hand session state to a future cold AI reader | `dev-workflow:handoff` |
| A generic Mermaid diagram, any type, no CoT house style | `obsidian:obsidian-mermaid-visualizer` |

## Step 1 — Resolve the source

Two source modes. Determine which from the user's request; if genuinely
ambiguous, ask one line — do not guess, the whole deliverable forks on it.

**File mode** — user names a file, folder, or glob.
Read the target(s) with Read. For a folder, read every `.md`/`.txt` in it
unless the user narrows the set. If the material exceeds what you can
usefully hold, dispatch an Explore agent to return a structured digest of
the reasoning steps (claims + evidence + transitions) and work from that
— never skim and invent the gaps.

**Conversation mode** — user says "這段對話" / "what we just worked out" /
names no target.
Use the conversation as the source. **The chain starts at the request
that opened the current piece of work, not at the first message of the
session** — a session may hold several unrelated arcs, and mixing them
produces a diagram with no through-line. If the session holds more than
one arc, say which one you took.

Include reasoning that reached a conclusion **and** reasoning that was
abandoned — the abandoned branches become the 岔路 table. Your own
reversals belong in the chain: a judgment that was overturned is a node,
and what overturned it is the edge into the next one.

State which mode you chose in one line before proceeding.

## Step 2 — Extract the chain, before drawing anything

Write out, as a working list (not shown to the user):

1. **Nodes** — every distinct reasoning *state*. A node carries a claim.
   A topic heading is not a node.
2. **Edges** — for each consecutive pair, *why* the second follows from
   the first. If you cannot name the why in 4–8 characters, the two
   nodes are actually one node, or a node is missing between them.
3. **Rejected options** — anything considered and ruled out, with the
   reason it was ruled out.
4. **Assumptions** — what the chain rests on that was never tested.
5. **Open questions** — what the source leaves unanswered.
6. **Exceptions and withdrawal conditions** — for each node, does the
   source state a limit on when the claim holds ("correct, but only
   within region X"), or a condition under which the step would be
   dropped ("keep it unless false positives persist")? This is Toulmin's
   *rebuttal*, and a fidelity test found it to be the single most
   damaging thing a summary loses: a reader who receives the measure
   without its scope implements the version the source rejected.

   **Sweep for these node by node, do not wait to notice them** — round
   3 of the fidelity rounds lost a carve-out sitting in plain sight next
   to a mechanism nobody had interrogated, and rounds 1–4 each lost a
   normative clause of some kind (`references/why-these-rules.md`).

   A node **names a mechanism** when it says something will be *built,
   changed, or done* — a check, a rule, a script change, a step someone
   must perform. Nodes that report a fact, an observation, an insight, or
   a rejected option are not mechanisms and need no sweep. When unsure,
   sweep it: the cost is three questions answered "none stated", and the
   cost of skipping is a clause that silently never arrives.

   For every mechanism node, ask all three:

   - **What must it NOT do?** Negative requirements — "no output file
     written", "must not be delivered", "never retried" — are part of the
     specified behaviour. A mechanism described only by what it does is
     half-described.
   - **Who or what is exempt?** Carve-outs — "except when the session is
     developing these scripts" — invert the rule for a case the author
     thought about. Round 3 lost one, and a rule that arrives without the
     case its author deliberately exempted is a rule the reader applies
     where the source said not to.
   - **Under what condition is it withdrawn?** The rebuttal proper.
7. **Co-premises** — does any step work only in conjunction with
   another, so that one alone is inert? Draw both edges into the same
   node; that structure *is* the "linked argument" of the literature,
   and no special edge type is needed for it.
8. **The author's own hedging** — where the source marks its own
   confidence ("my take", "leaning no", "in that order of
   load-bearing-ness"), carry the hedge verbatim. Do **not** rate
   confidence yourself: a slot you fill by copying stays reliable, a
   slot you fill by judging does not.

**Early exit — check this before building anything.** Count the
reasoning states you just listed. **Fewer than 5 and the answer is not a
diagram**: stop, tell the user the material does not have a chain worth
drawing, and answer their question directly instead. A three-box figure
with a page of scaffolding around it is worse than two sentences, and it
costs them a file to open.

This is a net, not the main path. A pre-ship trigger eval over 31
phrasings put the router at 25/31, with every one of its 5 chain-of-
thought requests firing and all 4 generic-diagram requests going
elsewhere; plain state-requests — "what does this function do" —
did not reach here. (Run before shipping; the fixture is not committed,
because `scripts/check-skill-structure.py` reports a `trigger-eval.json`
at a skill root as `CHK-SKL-012` — the PostToolUse hook allows it, so the
two disagree, and the two skills that do ship one currently fail that
check.) So what lands in this check is material that *looked*
like a process and turned out not to be one. Reading it and saying "this
needs a paragraph, not a diagram" is the correct outcome; producing the
page anyway is not.

Above 9, the source usually holds more than one arc: split into one
diagram per arc, each with its own `####` section and its own node
cards.

**When the range and a content rule collide, the content rule wins.**
Reversals are the common case: each one costs two nodes — the judgment
held, and the judgment after it was overturned — so a source with several
can reach 9 while still being a single arc. Do not merge two reversals
into one node, and do not drop one, to fit a number. Split the arc if it
genuinely holds two, otherwise let the count run over and say in your
report that it did and why.

**Do not invent.** If the source contains no rejected options, the 岔路
section is deleted, not filled. A fabricated branch is worse than a
missing one — it misrepresents what actually happened.

**Reversal vs rejected option.** A judgment that was held and then
overturned is a **node** in the chain, with the thing that overturned it
as the edge into the next node. The 岔路 table is for options that were
weighed and never adopted. When something is both, it goes in the chain —
the table is for roads not taken, not for u-turns.

## Step 3 — Build the diagram

Follow `references/mermaid-cot-spec.md` literally. The node styling is
the vault's convention, measured across 7,924 notes. The **layout** is a
deliberate divergence from it, chosen on measured numbers — the spec
carries the table. Do not "restore" the vault's flat `graph LR` on
consistency grounds without re-measuring; it renders 13:1 wide.

The shape:

```
graph TB
subgraph r1["階段標題"]
direction LR
  A["<div style='text-align:left'>標題<br/>━━━━━━<br/>• 條列一<br/>• 條列二<br/>• 條列三</div>"]
  B[...]
  C[...]
end
subgraph r2["階段標題"]
direction LR
  D[...]
end
A -->|邊標籤| B
...
style A fill:#f8f9fa,stroke:#868e96,stroke-width:2px
```

Four sections in order: `graph TB` → subgraph blocks → edges → styles.

The rules that get broken most often:

- `graph TB` outer, with every node inside a `subgraph` row that
  declares **its own `direction LR` line**. That one line is what makes
  the figure roughly square (0.81). Declaring the subgraphs but omitting
  the `direction` line measures 0.14 — worse than useless, since the
  structure is there and buys nothing. (The vault's own flat `graph LR`,
  with no subgraphs at all, is a separate row at 0.07.)
- **Rows of at most 3, as even as possible**: 8 nodes → 3/3/2, 7 → 3/2/2,
  6 → 3/3. On one 8-node chain, rows of 3 measured 0.91 against 0.52 for
  rows of 2 and 0.43 for rows of 4 — 3 is a peak, not a ceiling
  (`references/mermaid-cot-spec.md` appendix).
- The separator is the literal `<br/>━━━━━━<br/>` (six U+2501 `━`).
  Not `---`, not `<hr>`, not a different count.
- `• ` bullets per node, joined with `<br/>`: **as many as the node
  actually has.** Three to five is what that usually comes to — the range
  describes the outcome, it does not set a quota. A node whose source
  gives it two facts gets two bullets and trips a warning, and that is
  the correct result.
  **The tell that you are padding**: you are looking for something else
  to say about a node you have already finished describing. Stop there.
  A number does not need enforcement to distort content — being printed
  is enough, and a cold-read run inflated a node to satisfy this very
  advisory.
- Keep bullets short, but the gate only **warns** here — the single
  widest bullet sets every column's width, so that is the one worth
  shortening. The bullet is a pointer; the full explanation lives in that
  node's card below, which has no width limit.
- **Every** edge carries a label. A bare `A --> B` is a defect.
  Reject empty connectives — `導致` / `然後` / `所以` carry no information.
- `style` lines inline, one per node, after all edges. No `classDef`.

Edge types mean different things: `-->` ordinary derivation, `-.->` weak
or background link, `==>` the culminating step into the conclusion
(typically one per diagram). Node colours follow the role table in the
spec — premise grey, evidence orange, obstacle red, attempt dark-orange,
turning point purple, conclusion cyan.

Before moving on, re-read your diagram against the escaping traps in the
spec: no unescaped `"` in a label, no `|` in an edge label, no literal
newline inside a node.

## Step 4 — Write the markdown

**The markdown is the artifact. The HTML is derived from it.** Never
hand-write the HTML and never hand-edit it afterwards — if the two
disagree, the HTML is wrong by definition.

Copy `assets/cot-report-template.md`, delete its authoring comment
blocks, and fill it in. Its frontmatter follows the vault's note
standard (`title` / `type` / `date` / `tags` / `aliases` / `status`, plus
`language` / `processed_at` / `timezone` / `llm_*` as the vault's own
notes carry), so the file can be moved into an Obsidian vault as-is if it
turns out to be worth keeping. Leave `verified` and `fidelity_checked`
empty; they are filled after the checks in Step 5 and Step 6 actually run.

Structure the converter depends on:

| Markdown | Means |
|---|---|
| `### ` | a page-level section |
| `#### ` | one arc — one reasoning chain, one diagram |
| `##### A — 標題` | one node card |
| ` ```mermaid ` | the diagram of the arc it sits in |

- `### 概述` — its single paragraph is the one-line conclusion, and the
  page styles it as the lede where it stands. State the conclusion
  itself, not "本文探討…".
- One `##### ` card per diagram node, **in diagram order**, giving
  主張 / 依據 / 這一步改變了什麼. No width limit applies here — this is
  where a node's compressed bullets get their full explanation.
- **On a mechanism node, the *what* is quoted or it is absent. Never
  paraphrased.** Put the source's normative sentences in a markdown
  blockquote under the node — `> …`, one or more lines — verbatim, in the
  source's own language. Use the quote syntax rather than a labelled list
  item: a blockquote is what a quotation *is*, it survives into Obsidian
  as one, and the gate checks structure instead of sniffing punctuation —
  which failed badly once (`references/why-these-rules.md`). The rest of the card explains
  **why** that was decided, in the reader's language — that half is
  yours to write. What gets built, where it reads from, how it must
  behave: those are the source's words or nobody's.

  This is a removed freedom, not another thing to remember. **A gap
  sends the reader back to the source; a false fact does not**, and
  paraphrase is how the false fact gets made — a round that paraphrased
  two path rules shipped one that would have failed silently forever
  (`references/why-these-rules.md`).

- **One mechanism, one node.** Several things to build do not merge into
  a single "the decision" node. Merging is what let that distortion in:
  with one mechanism node, the quoting rule covered almost nothing.
- **`例外／失效條件` — include the bullet only when the source states
  one**, and delete the line entirely when it does not. An empty one
  asserts "no exceptions apply", a claim the source did not make. A node
  may carry several; list them as sub-bullets rather than running them
  together.
- **`### 這份結論要求你做什麼`** — duties and contract rules the source
  states ("before X you must Y", "without Z this must not ship"). These
  are not reasoning steps and never become nodes, so without this section
  they vanish — as one did, leaving a reader with every reason for a
  mechanism and none of the obligation that makes it work.
- Delete any section with no content. An empty heading is a defect; an
  absent section is honest.
- **Language: the page follows the language the user asked in; verbatim
  quotes stay in the source's language.** The reader is the person who
  asked. A translated quote cannot be checked against the original, so
  quotes keep the source's wording. Headings and labels are content, not
  fixed chrome — translate them with everything else (推理鏈 → Reasoning
  chain, 岔路 → Roads not taken); a Chinese frame around English body
  text reads unfinished. Record the choice in the frontmatter's
  `language` and say it when you report the file.

- **`source` in the frontmatter takes the absolute path.** The renderer
  turns it into a `file://` link, and only an absolute one still points
  anywhere once the page is opened from a different directory. A relative
  path is left as plain text rather than guessed at — a link that looks
  right and goes nowhere is worse than no link. Conversation mode writes
  本次對話, which is not a path and is not linked.

Write to `${TMPDIR:-/tmp}/cot-explain/<YYYY-MM-DD>-<slug>.md` unless the
user named a path. If that file already exists, overwrite it — the slug
identifies the work, and a directory of `-2`, `-3` variants hides which
one is current. **This is a temporary location**: say so when you
report it, and say how to keep the page — move the `.md` into a vault, or
publish the HTML as an Artifact.

## Step 5 — Convert, verify, then offer to publish

**Three commands, and the third is not optional:**

```
python3 scripts/render_cot_html.py <file>.md
python3 scripts/verify_cot_html.py --render --stamp <file>.html
python3 scripts/render_cot_html.py <file>.md
```

The render runs **twice** because the verifier can only stamp the
markdown, and the HTML is built from the markdown. Skip the third
command and you ship a page whose `verified` reads empty — announcing
未執行 — while the gate actually passed. That is the precise failure the
field exists to prevent, so stopping at "convert, verify" defeats it.

The converter parses with markdown-it-py, the same library
`loom-code/scripts/adjudication_render.py` uses. It **fails loud and
writes nothing** if markdown survives into the output, and stamps every
page with the version of the copy that ran. If it exits non-zero, no
HTML exists — fix the markdown, never the HTML.

The verifier reports two levels. `FAIL` breaks the contract or the
mermaid parser and exits 1. `WARN` costs readability or squareness and
never blocks — weigh it, do not reflexively obey it. A node count outside
5–9 is a content question (Step 2), not a formatting one.

**A reversal-heavy source produces a cluster of warnings, and that is
the correct output** — a correction stated in two clauses gives a node
two bullets. Read a cluster as a description of the source, not a defect
list — the count is an observation about the material, and there is no
number of warnings at which the right move becomes trimming the claims.

`--render` pushes each diagram through the real mermaid parser. Use it:
**mermaid-cli's exit code settles nothing** — it has been recorded
writing an error image and exiting 0, and observed exiting 1 with no
image at all — so
nothing else proves the diagram renders. It needs `npx` and, first time,
network. Without the flag the output says `PASS (text only …)`, so a
text-only pass is never mistaken for a rendered one.

`--stamp` writes the outcome into the markdown's `verified:` field, as
`pass @ <first 12 of the body hash>`. **Never type that field yourself** —
it is written by the script that did the checking, because a
self-reported success signal is exactly what fooled two review agents in
the source this skill was tested against. The hash is why editing the
page afterwards does not leave a stale pass standing: the converter
compares it against the body it is rendering and prints **閘：stale**
instead of the old result.

`fidelity_checked` is not typed either. Step 6 is judgement rather than a
command, so nothing can run it for you — but its verdict must land in a
file beside the page, `<name>.fidelity.md`, whose first lines carry
`verdict: PASS` or `verdict: FAIL`. `--stamp` reads that file and records
the result; with no file the field stays empty and the page says 未執行.
A claimed check nobody can point at is precisely the failure this tool
exists to catch. Both fields render on the page even when empty, in red,
saying 未執行. That is the intended default: a page that skipped its
checks says so, because silence gets read as "fine".

**Publishing.** The local file is the deliverable. Ask once whether to
publish as an Artifact; do not publish unprompted, since that uploads the
content. If yes, re-run the converter with `--artifact` (it drops the
document skeleton and the mermaid CDN script, which Artifacts supply
themselves) and publish that. Load the `artifact-design` skill first, as
the Artifact tool requires.

## Step 6 — Fidelity check, before anything gets shared

Steps 4 and 5 prove the page is well-formed. They prove nothing about
whether it represents the source honestly, and **no mechanical check
can** — every node can be well-shaped and every edge labeled while the
reader still walks away with a conclusion the source refutes.

**Run it before the page goes to anyone who was not there.** It is a
simulatability-style round-trip in three rounds: a fresh agent
reconstructs the reasoning from the page alone; a second compares that
reconstruction against the source **without ever seeing the page**; a
third checks the reverse direction, whether anything in the diagram has
no basis in the source at all. Rounds 1 and 2 measure what was lost; only
round 3 measures what was invented.

The verdict goes in `<name>.fidelity.md` beside the page, opening with
`verdict: PASS` and `reviewed_md_sha256:` — `--stamp` records nothing
without the hash, and refuses again if the markdown changes afterwards.
A verdict that outlives the thing it judged is the same failure as a
stale render.

**Full procedure, what gates, and where the fix cycle stops:
[`references/fidelity-check.md`](references/fidelity-check.md).** Read it
before running the check — the round prompts, the blindness constraints
and the one-cycle stop rule are all there, and none of them survive being
improvised.

## What this page is not

When the source is a **specification** — something written to be built
from — this page explains why the specification decided what it decided.
**It is not the specification, and it does not replace reading it.**

Say the risk the way it actually runs, and update it when the risk
changes — two wordings have already gone stale here, each accurate about
a failure mode the tool had moved past (`references/why-these-rules.md`).
The note now says both, and no more than is true:
**instructions are carried, reasons are abridged, and anything outside a
quotation is this page's rendering of the source, which governs.** If a
later run shows the residue has moved again, move this sentence with it —
an accurate warning about the wrong failure is still a wrong warning.

That limit is measured, not modest: six rounds against one dense brief,
the last of which passed with every clause carried and its residue
entirely in the reasons behind them
(`references/why-these-rules.md`). So when the source is a spec, say so
on the page. The provenance note
should name the source and state plainly that an implementer must work
from it, not from this page. Verbatim `規格原文` quotes narrow the gap;
they do not close it.

None of this applies to what the page is actually for: across every
round the reasoning itself came through intact, and the hallucination
check found nothing invented in any round it ran.

## Failure modes to refuse

- **"Just make the diagram, skip reading the source."** The extraction in
  Step 2 is the work; a diagram drawn from the filename is fiction.
- **Padding to reach 5 nodes.** If the reasoning has three steps, say so
  and offer prose.
- **Unlabeled edges "because the label is obvious."** It is obvious to
  you because you read the source. The reader did not.
