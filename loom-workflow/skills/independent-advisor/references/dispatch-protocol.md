# Dispatch protocol — the packet and the shared card

Referenced from `SKILL.md`. The binding rules for the three roles, for
blindness, and for the two bias controls live in `SKILL.md`; this file carries
the packet's required sections and the normalisation template.

## The dispatch packet

Every dispatch carries these four sections, written out in this order:

1. `decision statement` — what is being decided, in one sentence.
2. `rejected options` — the options already ruled out, each with the reason it
   was rejected.
3. `evidence paths` — the file paths the executor may open.
4. `incumbent proposal` — the current answer being challenged. The `proposer`
   leg's packet is assembled without this section; see `SKILL.md`.

### A missing section holds the request

While any of the four sections is absent, **hold the request**, and
**name the missing section** to the user, and dispatch nothing. Write
**no empty placeholder** in its place, and do not infer its content from the
surrounding material.

### An empty section is written, not left blank

When a decision genuinely has no rejected options, the `rejected options`
section is still present and **explicitly marked empty** — for example, `none:
no option has been ruled out yet`. A blank section reads as a section that was
forgotten, and cannot be told apart from one.

### An evidence path the executor cannot read

Check every listed path against the executor that will run the leg. A path that
executor cannot open is **treated as missing** — the section is incomplete, the
request is held, and that path is named. Never drop it from the list silently
and dispatch the rest.

### A packet that cannot be completed

When the material to complete a section does not exist, state the gap to the
user. The run then **ends without entering any spending path** — no probe, no
dispatch — and **the partial packet is retained** so the user can complete it
later rather than starting over.

## The shared card template

The `normalizer` compresses the incumbent and the challenger into one template,
each field in the same order in both cards:

- `core claim` — what the proposal asserts should be done.
- `key assumptions` — what must hold for the claim to work.
- `failure modes` — how it breaks.
- `cost` — what it takes to do it.

### Normalisation compresses; it never rewrites

The normaliser shortens wording and drops repetition. It
**must not rewrite the substance** of either proposal: a card whose `core claim` says something the
source proposal did not say is rejected and the card is redrafted from the
source. Every claim in the source appears in the card, compressed.

When the two drafts differ greatly in length, compress the longer one further
until the two cards are of **comparable length before anonymisation** — a
length difference is itself a tell that identifies the incumbent — and drop no
claim while doing it.

### When the normaliser authored the incumbent

The normaliser must not be the executor that authored the incumbent proposal.
When no other executor is available and that pairing is used anyway, set
`normalized_by_is_incumbent_author` to true and carry that field into the report
as-is, unsoftened.
