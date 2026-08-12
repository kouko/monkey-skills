# Adjudication view — protocol SSOT

> Companion to [`../SKILL.md`](../SKILL.md). This is the shared-rules
> SSOT for both objects the touchpoints wire into: the **document
> view** (plan / brief full text, at the plan review gate and brief
> sign-off) and the **verdict digest** (review findings, at whole-branch
> and docs-review presentation moments). Later tasks (splitter, lint,
> renderer, wiring) implement against this file — do not fork the
> rules into a second copy.

## Why this exists

The human adjudicator reads and judges English artifacts (plan, brief,
review verdict) natively in Traditional Chinese. The artifacts also
serve two other readers — validators (exact string match) and
downstream agents (unambiguous, greppable English) — and the current
format optimizes those two at the human reader's expense. This
protocol governs a **view**: a disposable, regenerated-per-render
rendition that lets the adjudicator read in their language without
touching the machine-precise artifact underneath.

## The unit-1:1 rule

**Exactly one rendition unit per source unit.** A source unit is a document
section/task block (document view) or one finding (verdict view). The
split is mechanical (script-driven), so unit count equals source-unit
count by construction — this holds for both objects.

- Omissions must be explicitly marked 「已略」 in the unit's rendition —
  never silently dropped.
- Compression is allowed only **within** a unit (a unit's rendition may
  be shorter than its source_text); it must never merge two source
  units into one rendition unit, and never split one source unit
  across two rendition units.
- Every rendition is regenerated from the artifact, every time — never
  digest-of-digest (a rendition is never itself the input to a later
  rendition). This is what keeps a stale view from silently drifting
  from the underlying artifact across edits.

## Fixed modality mapping

Modal verbs map to a single fixed Chinese term — never a paraphrase,
never a synonym swap, so the adjudicator can recognize the strength of
an obligation on sight:

| English | Chinese |
|---|---|
| must | 必須 |
| should | 應 |
| may | 可 |
| must not | 不得 |
| should not | 不應 |

Verbatim pairs: must→必須 / should→應 / may→可 / must not→不得 /
should not→不應.

## Verbatim carry-through

These never get translated, paraphrased, or re-derived — they carry
through the rendition byte-for-byte:

- **Technical nouns and enum tokens** (status values like
  `done(<sha>)`, dimension names, class labels, file paths, identifiers)
  stay in English verbatim.
- **Severity emoji** (🔴🟡🟢) are carried verbatim from the source
  finding — a rendition never re-grades severity; the emoji is copied,
  not recomputed.

## Translator additions — provenance-tagged

Any content the translation step adds beyond a faithful rendition of
the source (a clarifying gloss, an expanded acronym, context the
reader needs) must be tagged with 「譯注」 so the adjudicator can tell,
at a glance, what came from the artifact and what the translator
added.

## Units-JSON schema

The structured intermediate between split and render. Fields:
`unit id`, `heading`, `source_text`, `anchors`, `rendition`.

- `unit id` — stable identifier for the unit (section heading / task ID
  for documents; `where` + `dimension` for findings).
- `heading` — the unit's human-readable title.
- `source_text` — the unit's original English text, verbatim.
- `anchors` — the verbatim tokens (numbers, enum tokens, backticked
  terms, identifiers) extracted from `source_text` that the rendition
  must echo — this is what the lint step checks against.
- `rendition` — the Chinese rendering of the unit, filled in by the
  orchestrator-side LLM translate step (deterministic scripts never
  fill this field).

## Firing conditions

- The view **fires only when live conversation language is not English**
  — an English-speaking session gets no view; the artifact itself
  already serves that reader.
- Likewise, verdict mode fires only when findings ≥ 1 — a clean PASS
  with zero findings is already localized by the family rollup card,
  so no verdict digest is produced for it.

## Lint-failure rule

Unit count parity holds by construction at split time — the mechanical
split emits exactly one unit per source unit, including the preamble
unit when non-blank content precedes the first H2 (see the unit-1:1
rule above). The zero-token lint then checks each unit's rendition
(anchor echo, negation presence, modality-mapping warning) after
translation. On failure: **regenerate once, no revision loop.** If the
regenerated rendition fails lint a second time, surface the failure to
the user rather than looping — do not keep retrying silently.

## Delivery adapters

Delivery differs by object, not just by host:

- **Document view** (plan / brief full text): rendered to scratchpad
  HTML.
  - **Claude Code**: side-panel render of that HTML.
  - **Codex**: no side-panel surface exists — print the rendered path
    and an `open <path>` hint instead. This is an
    **environmental-absence fallback**, not a delivery gap: the view
    is still produced and still reachable, only the presentation
    channel differs by host.
- **Verdict digest** (review findings): an inline markdown table in
  chat by DEFAULT. The HTML rendition (same scratchpad/side-panel path
  as the document view) is used only via `--html`, when findings are
  numerous or on request — not the default for this object.

## Machine-precise boundary

The underlying artifact (plan file, brief file, verdict block on disk)
and any verdict block already emitted are **never rewritten** by this
protocol — views are purely additive. Views are:

- **disposable** — regenerated from the artifact on demand, never
  treated as a durable record;
- **scratchpad-only** — written under the session scratchpad, never
  under a path the repo tracks;
- **never committed to git** — a view must not appear in any commit
  this protocol's machinery produces.
