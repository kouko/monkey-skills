# Writing Lean — authoring-time compression

Skills accumulate token bloat through additive edits. Cheaper than
cutting later: don't write the bloat. Five principles, in the order
you should apply them while drafting.

## 1. The model is already smart

Only add context the model doesn't already have. Claude knows what
JSON is, how git works, what a code review looks for — restating
pre-trained knowledge costs tokens and buys nothing. Anthropic's
agent-skills best practices (platform.claude.com) put it directly:
assume a capable reader and challenge every paragraph's token cost —
if removing it wouldn't change behavior, it shouldn't be there.

## 2. Leading words

Name the pre-trained concept instead of re-teaching it. "Apply
Fowler's Feature Envy test" recruits the model's whole prior for the
price of three words; a paragraph paraphrasing that smell costs 50×
more and lands weaker. Named concepts (design patterns, book-anchored
rules like Beck's Child Test, RFC terms) are compression handles —
prefer them wherever a stable name exists. The refactor-side
counterpart is the Leading-Word Substitution move in skill-refactor's
refactor-moves catalog: what that move does to existing prose, this
principle does at the keyboard.

## 3. Bloat-taxonomy self-review

After drafting, sweep each section against five bloat categories:

1. **No-op sentences** — assert nothing checkable ("be thoughtful
   about quality"). Delete.
2. **Sediment** — leftovers from superseded revisions that no longer
   connect to any current step. Delete.
3. **Negative instructions** — "don't do X" names the forbidden
   behavior and can trigger it. Rephrase as the positive behavior
   you want.
4. **Premature completion claims** — text announcing success before
   verification ("this ensures correctness"). Delete or convert to a
   check.
5. **Duplication with a reference** — body prose restating what a
   bundled reference already says. Keep the pointer, cut the restatement.

## 4. Thin orchestrator over thick reference

The named design dimension behind lean skill bodies: SKILL.md body =
steps plus a table of contents; knowledge lives in `references/`
files loaded on demand. This names what §Progressive Disclosure in
the main skill already implements — the three-level loading system is
the mechanism, thin-orchestrator-over-thick-reference is the design
stance that tells you which side of the line any given paragraph
belongs on. When drafting, ask per section: is this a step the model
must execute now (body), or knowledge it might need (reference)?

## 5. Weak-tier floor

Compression has a model-tier floor. Anthropic warns that "what works
perfectly for Opus might need more detail for Haiku" — a leading word
that recruits a rich prior on a strong model may recruit nothing on a
weak one, and this repo's own evidence shows explicit contracts are
load-bearing at weak tiers. When in doubt, test the drafted skill on
the weakest tier that will run it in production, and let that run —
not the strongest model's — decide how much detail stays.

## Attribution

Distilled from Matt Pocock's `mattpocock/skills` repository,
`writing-great-skills` (MIT License, © 2026 Matt Pocock) and his
aihero.dev writing, combined with Anthropic's skill-authoring best
practices (platform.claude.com). Pocock's techniques generate lean
candidates; this repo's skill-refactor equivalence gate verifies
them — each supplies what the other lacks.
