# CoT Explain

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Point it at a document — or at the conversation you just had — and it
> produces one self-contained HTML page whose centrepiece is a
> chain-of-thought Mermaid diagram: every node a reasoning step, every
> arrow labeled with why the step follows.

---

## Overview — what this skill does

Reasoning that lives in a long document, or in a conversation only you
were present for, is invisible to everyone else. This skill makes it
visible.

It reads the source, extracts the actual chain of reasoning — the
claims, what each rests on, and the transition between each pair — and
renders it as a single HTML file:

1. A one-line conclusion
2. The chain-of-thought Mermaid diagram
3. Each node expanded: claim / evidence / what this step changed
4. Options that were considered and rejected, with reasons
5. Assumptions the chain rests on, and questions still open

It is a **one-shot generator**. Nothing is written to a database, nothing
is tracked across sessions. You run it, you get a page, it stops.

---

## The diagram convention

The diagram follows a strict house style rather than generic Mermaid:

```
graph TB
subgraph r1["階段標題"]
direction LR
  A["<div style='text-align:left'>前提<br/>━━━━━━<br/>• 條列一<br/>• 條列二<br/>• 條列三</div>"]
  B[...]
  C[...]
end
A -->|塑造判斷基礎| B
B ==>|匯聚為| C
style A fill:#f8f9fa,stroke:#868e96,stroke-width:2px
```

- Each node: a title, a `━━━━━━` rule, three to five bullets, left-aligned
- **Every** arrow carries a label naming the relationship — an unlabeled
  arrow is treated as a defect, not a shortcut
- Three arrow types: `-->` ordinary derivation, `-.->` background or weak
  link, `==>` the culminating step into the conclusion
- Node colour encodes role: premise, evidence, obstacle, attempt,
  turning point, conclusion

**Layout is measured, not assumed.** A reasoning chain is long and thin;
drawn as a flat `graph LR` it rendered 3061 × 227 px — 13.5:1, useless on
a page. Fifteen variants were rendered with mermaid-cli and measured by
SVG viewBox. The winner is what the spec now mandates: outer `graph TB`,
each row a `subgraph` declaring its own `direction LR`, at most 3 nodes
per row, short bullets — **1022 × 824 px, 0.81 of a square**. The
`direction` line is the load-bearing part: subgraph rows without it
measure 0.14. Tightening `nodeSpacing`/`rankSpacing` moved 13.48:1 to
13.39:1 and is a dead end. Bullet count is a lever too, in the helpful
direction — the figure is wider than tall, so each extra bullet adds
height and moves it towards square (3 → 0.81, 5 → 0.95), which is why
the range is 3–5 rather than a fixed 3.

**Length limits are warnings, not failures.** The single widest bullet
sets the column width for every node, so that one line is what the gate
flags — and it never blocks. A hard character cap makes an author mangle
a sentence to satisfy a number, which is worse than a wide box.

This layout diverges from the vault's own convention (`graph LR`, no
`subgraph`) on purpose — those files hold short chains where 13:1 never
bites. The full contract, with the measurement table, lives in
`references/mermaid-cot-spec.md`.

---

## Output

**The markdown is the artifact; the HTML is derived from it.** The `.md`
carries Obsidian-compatible frontmatter following the vault's own note
standard, so a page worth keeping can be moved into a vault as-is. The
HTML is produced mechanically by `render_cot_html.py`, which parses with
markdown-it-py — the same library this repo's existing markdown renderer
uses — and never gets hand-edited.

Both land in `${TMPDIR:-/tmp}/cot-explain/`, which is **temporary on
purpose**: most of these pages are read once. To keep one, move the `.md`
into a vault or publish the HTML as an Artifact (a private page on
claude.ai you can then choose to share). Publishing is asked for once and
never done unprompted, since it uploads the content. The local HTML loads
`mermaid.js` from a CDN, so first open needs network.

The converter borrows three properties from a brief about a renderer of
exactly this kind that failed silently five times in five days: it
**fails loud and writes nothing** when markdown survives conversion, it
**scopes that check** so mermaid blocks and code spans full of `|` and
`**` are not condemned, and it **stamps every page** with the version of
the copy that actually ran.

---

## Fidelity — the part no gate can check

The verification script proves the page is well-formed. It cannot tell
you whether the page represents the source **honestly**, and nothing
mechanical can: every node can be well-shaped and every edge labeled
while the reader still walks away with a conclusion the source refutes.

That is not hypothetical. A round-trip test on a real English source
found a reader would have come away believing the fix was to "pin to a
specific path" when the source had explicitly derived why a fixed path
fails and specified a self-locating rule instead — they would have built
the rejected variant. The judge's verdict: faithful as an account of
*why*, unusable as an account of *what to do*.

So the skill ships a **Step 6 fidelity check**, run before a page goes
to anyone who was not there. It is a simulatability-style round-trip
(forward simulation, Doshi-Velez & Kim 2017; Leakage-Adjusted
Simulatability, Hase et al. 2020) in three rounds: a fresh agent
reconstructs the reasoning from the page alone; a second agent compares
that reconstruction against the source without ever seeing the page; a
third pass checks the reverse direction, whether anything in the diagram
has no basis in the source at all.

**What it does not do.** When the source is **operative** — written to
be acted on rather than merely read — this page explains why it decided
what it decided; it does not replace reading it. A technical
specification is the obvious case; a policy, a contract, a clinical
protocol, a regulation and a style guide are the same case. That limit is measured. Four
rounds were run against one dense engineering brief: each recovered every
clause the previous round had been told it lost, and each lost different
implementation details nobody had thought to look for — one new miss,
then two, then three. Adding another category to hunt for moved the loss
rather than ending it. Verbatim blockquotes on mechanism nodes narrow
the gap; they do not close it, and the page says so when the source is
operative.

What the page is *for* came through intact in all four rounds — the
reversals, the rejected options with their reasons, the conditional
retreats — and the hallucination check found nothing invented in the last
three.

The fix that came out of it was small on purpose. Node cards gained one
field — `例外／失效條件`, Toulmin's *rebuttal* — because a stated limit
on when a claim holds was the most damaging thing a summary dropped. The
diagram vocabulary did not change. The rule behind that restraint:
**add slots you fill by copying, never slots you fill by judging.** A
field asking what limit the source stated stays reliable across readers;
a field asking how confident a claim is does not.

---

## When to use vs the neighbouring skills

| Situation | What to use |
|---|---|
| Explain reasoning that already exists, as a shareable page | This skill |
| Still working the problem out, across sessions, tracked assumptions | `think-orbit:thinking-session` |
| An assumption behind past reasoning just broke | `think-orbit:break-assumption` |
| Lost the thread mid-conversation, need re-orientation in chat | `dev-workflow:recap-state` |
| Hand session state to a future cold AI reader | `dev-workflow:handoff` |
| Any Mermaid diagram type, no CoT house style | `obsidian:obsidian-mermaid-visualizer` |

The distinction that matters most: **think-orbit is for thinking, this
is for explaining thinking that already happened.** They coexist.

---

## Example invocation phrases

- "把這份文件的思路畫出來"
- "解釋這段對話怎麼推導的"
- "產一份 CoT 說明文件"
- "explain this as a CoT diagram"
- "make an HTML explainer for this"
- "draw the reasoning in `docs/spec.md`"

---

## What it will refuse

- **Drawing without reading the source.** The extraction is the work; a
  diagram inferred from a filename is fiction.
- **Padding to fill the diagram.** Under 5 real reasoning steps, it says
  so and offers prose instead.
- **Inventing rejected options.** If the source considered no
  alternatives, that section is deleted, not filled.

---

## Files

```
cot-explain/
├── README.md           <- English (this file)
├── README.ja.md        <- 日本語
├── README.zh-TW.md     <- 繁體中文
├── SKILL.md            <- operational file (for Claude)
├── assets/
│   └── cot-report-template.md    <- the artifact template (markdown)
├── references/
│   └── mermaid-cot-spec.md       <- diagram syntax + content contract
└── scripts/
    ├── render_cot_html.py        <- markdown → HTML (markdown-it-py); fails loud, writes nothing
    └── verify_cot_html.py        <- gate: FAIL blocks (exit 1), WARN advises; --render parses
```
