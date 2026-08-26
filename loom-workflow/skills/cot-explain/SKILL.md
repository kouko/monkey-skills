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

The audience is a **human who was not there**. Labeled edges, checkable
nodes, rejected options, and a measured layout must make the reasoning
followable without prior context.

## When to fire

Fire when the user wants existing reasoning made visible to someone else.
Do not fire to *do* the thinking — this skill explains thinking that has
already happened.

Route active reasoning elsewhere; use `loom-workflow:recap-state` for
in-chat re-orientation, `loom-workflow:handoff` for future-session state,
and a general Mermaid skill for diagrams that are not reasoning chains.

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
This declaration makes the page's evidence boundary explicit to its reader.

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
6. **Exceptions and withdrawal conditions** — sweep every node for limits
   on when its claim holds or conditions under which it is dropped.
   A summary that carries a measure without its scope invites the reader
   to act on a version the source rejected. Do this node by node rather
   than waiting to notice a nearby carve-out.

   A node **names a mechanism** when it says something will be built,
   changed, or done: code, policy, contract, protocol, or standard.
   Facts, observations, insights, and rejected options are not mechanisms.

   **A duty the source places on the reader is not a mechanism node.** Put
   obligations such as "before X you must Y" in
   `### 這份結論要求你做什麼` (Step 4). When unsure, sweep it.
   The distinction is positional: a mechanism is a reasoning state the
   chain arrived at; an obligation is what the conclusion asks the reader
   to do. This keeps duties visible without presenting them as premises.

   For every mechanism node, ask all three:

   - **What must it NOT do?** Capture negative requirements.
   - **Who or what is exempt?** Capture every carve-out.
   - **Under what condition is it withdrawn?** The rebuttal proper.
7. **Co-premises** — does any step work only in conjunction with
   another, so that one alone is inert? Draw both edges into the same
   node; that structure *is* the "linked argument" of the literature,
   and no special edge type is needed for it.
8. **The author's own hedging** — carry source confidence markers
   verbatim; do **not** rate confidence yourself.

**Early exit — check this before building anything.** Count the
reasoning states you just listed. **Fewer than 5 and the answer is not a
diagram**: stop, tell the user the material does not have a chain worth
drawing, and answer their question directly instead. A three-box figure
with a page of scaffolding around it is worse than two sentences, and it
costs them a file to open.

Above 9, the source usually holds more than one arc: split into one
diagram per arc, each with its own `####` section and its own node
cards.

**When the range and a content rule collide, content wins.** A reversal
uses two nodes: the judgment held and the overturned judgment. Never
merge or drop reversals to fit the range; split only a genuinely separate
arc, otherwise report why the count runs over.

**Do not invent.** If the source contains no rejected options, the 岔路
section is deleted, not filled. A fabricated branch is worse than a
missing one — it misrepresents what actually happened.

**Reversal vs rejected option.** An overturned judgment is a node; 岔路
contains only options weighed but never adopted. If both, keep it in the
chain.

## Step 3 — Build the diagram

Follow `references/mermaid-cot-spec.md` literally. A linear chain uses
rows; parallel tracks use the spec's Shape 2 columns. Do not replace the
measured layout with flat `graph LR`.

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
r1 -->|邊標籤| r2
style A fill:#f8f9fa,stroke:#868e96,stroke-width:2px
```

Four sections in order: `graph TB` → subgraph blocks → edges → styles.

The rules that get broken most often:

- `graph TB` outer, with every node inside a `subgraph` row that
  declares **its own `direction LR` line**.
- **Join rows subgraph to subgraph — `r1 -->|…| r2` — never node to node
  across rows.** Node edges stay inside a row; label the row transition
  with the Step 2 "why." Put direct cross-links and co-premises in one
  row, or record the relation as prose in the node's 依據.
  Mermaid discards a row's `direction` when one of its nodes points
  outside the row, collapsing the layout into a narrow column. The
  subgraph-to-subgraph edge preserves the row and carries the transition
  that otherwise would have crossed it.
- **Rows of at most 3, as even as possible**: 8 → 3/3/2, 7 → 3/2/2,
  6 → 3/3. A trailing one-node row is fine.
- The separator is the literal `<br/>━━━━━━<br/>` (six U+2501 `━`).
  Not `---`, not `<hr>`, not a different count.
- `• ` bullets per node, joined with `<br/>`: use only as many as the
  source supports. Three to five is descriptive, not a quota; warnings
  do not justify padding.
  Padding begins when you look for another statement after the node is
  already fully described. Stop there: a two-fact node should have two
  bullets even when the verifier warns.
- Keep bullets short; the gate only **warns**. Full explanations belong
  in the node cards.
- **Every** edge carries a label. A bare `A --> B` is a defect.
  Reject empty connectives — `導致` / `然後` / `所以` carry no information.
  The label must state why the next reasoning state follows; the reader
  did not see the source and cannot supply the missing inference.
- `style` lines inline, one per node, after all edges. No `classDef`.

Edge types mean different things: `-->` ordinary derivation, `-.->` weak
or background link, `==>` the culminating step into the conclusion
(typically one per diagram). Node colours follow the role table in the
spec — premise grey, evidence orange, obstacle red, attempt dark-orange,
turning point purple, conclusion cyan.

Check the spec's escaping traps: no unescaped `"` in a label, `|` in an
edge label, or literal newline inside a node.

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
- **On a mechanism node, the *what* is quoted or absent, never
  paraphrased.** Put normative source sentences verbatim, in the source
  language, in `> …` blockquotes. Explain **why** in the reader's
  language. Requirements, actors, conditions, and prohibitions must be
  the source's words.
  Use blockquote structure rather than a labelled list item so the quote
  remains identifiable in Markdown and Obsidian. A missing clause sends
  the reader back to the source; a confident paraphrase can instead send
  them forward with a false rule.

- **One mechanism, one node.** Do not merge distinct mechanisms.
- **`例外／失效條件` — include the bullet only when the source states
  one.** Otherwise delete the line; list multiple conditions as sub-bullets.
  An empty line would assert that no exception applies, which the source
  may never have claimed.
- **`### 這份結論要求你做什麼`** — source-stated duties and contract
  rules. They are not reasoning steps and never become nodes.
- Delete any section with no content. An empty heading is a defect; an
  absent section is honest.
- **Language: follow the user's language; verbatim quotes stay in the
  source's language.** Translate headings and labels too. Record the
  choice in frontmatter `language` and in the file report.
  A translated quote cannot be checked directly against the original;
  keeping its wording preserves that verification path.

- **`source` frontmatter takes the absolute path.** Relative paths remain
  plain text. Conversation mode writes 本次對話, which is not linked.

Write to `${TMPDIR:-/tmp}/cot-explain/<YYYY-MM-DD>-<slug>.md` unless the
user named a path. If that file already exists, overwrite it — the slug
identifies the work, and a directory of `-2`, `-3` variants hides which
one is current. The `.md` and the `.html` live side by side there;
**both are temporary**, so say so when you report the paths.

Do not move the `.md` by default. If asked to keep it, publish the HTML
as an Artifact or move the `.md` into a vault. For the vault route, state
that Obsidian and VS Code preview use mermaid 11.13.x; the Step 3 layout
is compatible with it.

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

The converter parses with markdown-it-py. It **fails loud and writes
nothing** if markdown survives into the output, and stamps every page with
the version of the copy that ran. If it exits non-zero, no HTML exists — fix
the markdown, never the HTML.

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

**Publishing intent.** The local file is the deliverable. Ask once whether the
user wants an Artifact; do not publish unprompted. Record the answer only:
Step 6 must pass before conversion or publication for anyone else.

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

After a PASS, honor the recorded publishing choice. Re-run the converter with
`--artifact` (it drops the document skeleton and mermaid CDN script supplied by
Artifacts), load `artifact-design` as required by the Artifact tool, and publish.
On FAIL, do not convert or publish the Artifact.

## What this page is not

When the source is **operative** — written to be acted on rather than
merely read — this page explains why it decided what it decided. **It is
not that document, and it does not replace reading it.** A technical
specification is the obvious case; a policy, a contract, a clinical
protocol, a regulation and a style guide are the same case, and the
warning below applies word for word to each.

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
(`references/why-these-rules.md`). So when the source is operative, say
so on the page. The provenance note should name the source and state
plainly that anyone acting on it must work from it, not from this page.
Verbatim blockquotes narrow the gap; they do not close it.

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
