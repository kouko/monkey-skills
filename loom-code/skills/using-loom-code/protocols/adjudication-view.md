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

Modal verbs map to a fixed target-language term per language profile —
never a paraphrase, never a synonym swap, so the adjudicator can
recognize the strength of an obligation on sight. One table per
supported language; forms are transcribed from the shipped profile in
`adjudication_profiles.py` (its `modality_map`), not re-derived here.

### zh-Hant

| English | Chinese |
|---|---|
| must | 必須 |
| should | 應 |
| may | 可 |
| must not | 不得 |
| should not | 不應 |

Verbatim pairs: must→必須 / should→應 / may→可 / must not→不得 /
should not→不應.

### ja

Derived from JIS Z 8301:2019 Clause 7 (Tables 3-5) — read the two
caveats below before treating this table as a standard.

| our source modal | accepted Japanese forms |
|---|---|
| must | しなければならない |
| must not | してはならない / しない |
| should | することが望ましい / するのがよい / することを推奨する |
| should not | 望ましくない / しない方がよい |
| may | してもよい / してよい / 差し支えない |

`must` deliberately carries only 「しなければならない」, narrower than
JIS Table 3, which also lists bare 「する」 and 「とする」. Those two were
dropped: a bare verb ending cannot distinguish obligation from
prohibition — measured, a rendition of "you must execute this" as
「実行しないこととする」 (a PROHIBITION, meaning fully inverted) matched,
because 「とする」 is a substring of that prohibitive construction.
Only 「しなければならない」 lexically encodes obligation on its own, so it
is the sole form kept for `must`.

A related collision is recorded but **not** narrowed the same way:
「しない」 (`must not`) is a literal substring of 「しない方がよい」
(`should not`), so a should-not rendition can silently satisfy a
must-not source. This is carried as a known debt, not fixed — both
forms are brief-mandated JIS entries, so removing one lacks the
"adds no obligation signal" justification that licensed the `must`
narrowing above, and the failure is an obligation-*strength* blur
between two negative-polarity forms, not a direction flip (see the
plan's Decision Log, "T2 debt, both arms agree — carried NOT fixed").

**Two JIS caveats — read before treating this table as a standard:**

1. **参考, not 規定.** JIS Z 8301:2019 labels the English↔Japanese
   correspondence in Clause 7 as 参考 (reference material), stating
   verbatim: 「この規格で規定する事項ではない」 ("not a matter this
   standard prescribes"). The Japanese forms are normative for JIS
   drafting; their pairing to shall/should/may is reference material
   aligned to ISO/IEC Directives Part 2, not itself JIS-normative. So
   this protocol says the table is **derived from** JIS Z 8301:2019 —
   never **per** or **conformant to** it.
2. **Mapped by force, not by spelling.** Our source "must" is used
   colloquially for obligation — semantically ISO's `shall`. JIS's own
   `must` row (Table 7) means an EXTERNAL constraint (statute,
   physical law), not internal obligation — not what our artifacts
   mean. Mapping our "must" onto JIS's literal `must` row would be a
   register error; instead our modals map by FORCE (meaning) onto
   JIS's 要求事項/推奨/許容 tables.

## Negation tier by language

The negation-preservation check runs at a **per-language tier**, not
one tier for every language:

| Language | Tier | Why |
|---|---|---|
| zh-Hant | hard-fail | Chinese negation is a closed character set (`不未無非沒勿`) with no homograph collision — a missing marker reliably means a dropped negation. |
| ja | warning | Japanese negation is inflectional (a kana suffix), not a closed character set, and collides with ordinary vocabulary: 少ない / 危ない / つまらない all end in ない without negating anything. (An earlier pattern also matched 「ず」, which collided with common words like 必ず ("without fail") — that form was already narrowed away for this reason; see the inline comment at the `ja` profile's `negation_pattern` assignment in `adjudication_profiles.py`.) A missing-marker signal is real but unreliable, so it informs the adjudicator — it never blocks. |

The tier is **evidence-derived**, not a placeholder — do not raise `ja`
to hard-fail without new measured evidence (see the inline comment at
the `ja` profile's `negation_tier` assignment in
`adjudication_profiles.py`, and the plan's `## Notes` section
"Japanese negation stays WARNING-tier by design", for the measurements
that set it).

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

- The view fires when the live conversation language is a **supported
  profile**: `zh-Hant` or `ja` (the two entries in
  `adjudication_profiles.py`). An English-speaking session gets no
  view — the artifact itself already serves that reader.
- A non-English language with **no profile** — anything other than
  the two above — is **N/A-loud**: say so, and produce nothing,
  rather than firing the view into machinery that cannot serve it.
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
