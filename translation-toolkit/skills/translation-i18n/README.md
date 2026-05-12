# translation-i18n

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Translate i18n strings — PO / JSON / XLIFF / Android `strings.xml` / iOS `.strings`.
> Preserves placeholders, keys, plurals, and project glossary.

Part of the [translation-toolkit](../..) plugin. Operational spec
Claude loads is [`SKILL.md`](SKILL.md); this README is for humans.

## Why a dedicated i18n skill

UI strings have constraints prose does not — placeholders (`{name}`,
`%(count)s`, ICU `{n, plural, ...}`, Android `<plurals>`) must
round-trip with exact count and arity, keys cannot drift,
`translatable="false"` and PO `msgctxt` must be honored, and entries
under one key namespace need cross-string consistency (`Cancel` cannot
be both キャンセル and 中止 within one app).

`translation-i18n` is purpose-built: protect every placeholder,
translate the whole file in one batch context, run a lean gate matrix
tuned for short strings, write back to the original format with
byte-level fidelity.

## Pipeline

```
intake-spec (from translation-intake)
        │
Layer 2 — Preparation
        ├── parse format (PO / JSON / XLIFF / Android / iOS)
        ├── protect-pass: mask placeholders as ⟦P:NN⟧ tokens
        ├── source analysis: extract candidate difficult terms
        └── glossary resolve (4-tier: L1 project → L2 bundled → L3 web → L4 LLM)
        │
Layer 3 — Core loop (DRAFT → REFLECT 4D → IMPROVE)
        │   └── single-batch context: all entries see siblings via <CONTEXT>;
        │       active entry wrapped in <TRANSLATE_THIS>
        │
Layer 4 — Verification (M1 + M2 only; S1 / S2 SKIPPED for short strings)
        │
Layer 5 — Output
        ├── restore ⟦P:NN⟧ → original placeholder bytes
        ├── write back to original format (preserve key order, comments,
        │   msgctxt, msgid_plural, <plurals>, translatable="false")
        └── emit audit-trail.json
```

## Format support

Auto-detected by extension first, then by content sniffing.

| Extension | Format | Notes |
|---|---|---|
| `.po` | gettext PO | `msgctxt` / `msgid_plural` / plural forms preserved |
| `.json` | JSON key-value | Recurses nested objects; dot-notation key paths |
| `.xliff` / `.xlf` | XLIFF 2.x | `<unit>` / `<segment>` / `<source>` / `<target>` |
| `strings.xml` | Android | `<string>` / `<plurals>` / `<string-array>`; `translatable="false"` skipped |
| `.strings` | iOS | `"key" = "value";` lines; `/* */` comments preserved |

Per-format read+write algorithms in
[`protocols/format-roundtrip.md`](protocols/format-roundtrip.md).
8-item preflight in
[`checklists/i18n-format-checklist.md`](checklists/i18n-format-checklist.md)
runs MUST before parse.

## Verification gate matrix

The leanest of the four format specialists — only M1 + M2 are HARD;
S1 / S2 are SKIPPED because per-string i18n payloads are too short
for back-translation similarity or register-classification gates to
produce meaningful signal.

| Gate | Tier | What it checks |
|---|---|---|
| **M1** | HARD | Placeholder integrity — `⟦P:NN⟧` count + ID set parity between source and target. Deterministic regex check. |
| **M2** | HARD | Project glossary compliance — every L1-mandated source term renders as its mapped target form. PASS_ADVISORY for `notes: context-dependent` entries. |
| **S1** | SKIPPED | Back-translation — UI strings too short for embedding-cosine similarity to be meaningful. |
| **S2** | SKIPPED | Register preservation — too few tokens per string; UI register pinned by format conventions (button text, dialog title) anyway. |
| **I1** | INFO | Untranslatability flagging — runs only when source-analysis flags a phrase. Non-interactive: records borrow / explain / approximate decisions; never blocks. |

**Implication for callers**: M2 is the dominant quality lever for i18n.
Invest in `<repo>/docs/i18n/glossary-{target_locale}.md` rather than
relying on post-translation similarity gates that won't fire here.

When invoked through [`translation-audit`](../translation-audit) against
an existing translation pair, the full M1 + M2 + S1 + S2 + I1 matrix
applies per audit's stricter semantics — i18n's local skip is for
**forward-translation** runs only.

## Cross-string consistency

The distinguishing trait vs the other format specialists: **the entire
file is one batch context**, even though entries are independent at the
format level.

- All entries from one source file translate as a single batch in one
  LLM context
- Per-entry prompts wrap the active entry in `<TRANSLATE_THIS>...</TRANSLATE_THIS>`;
  surrounding entries appear as `<CONTEXT>` only
- Files exceeding the 2000-token chunk threshold split on entry boundaries
  (never inside an entry); within a batch all entries see each other

This costs tokens but pays back in vocabulary consistency and reduces
project-glossary churn.

## Web search policy

ON by default (spec Decision #15). Override to OFF for batch i18n
runs (1000s of strings) where per-miss searches multiply cost and
latency:

```
--web-search=off
```

When OFF, glossary resolution stops at L2 (bundled) — L3 (web) is
skipped, L4 (LLM-fallback) still runs. Spot-check a sample with web
search re-enabled on a follow-up pass; do not ship a full untriaged batch.

## What this skill does NOT do

- **Does not run intake.** Hand off to [`translation-intake`](../translation-intake)
  (or use `--intake` to run it inline)
- **Does not translate Markdown** ([`translation-doc`](../translation-doc)),
  **generate transcreation variants** ([`translation-creative`](../translation-creative)),
  or **audit existing pairs** ([`translation-audit`](../translation-audit))
- **Does not bypass M1 / M2.** No `--bypass-gates` flag (anti-pattern per
  spec Decision #15). Fix the underlying issue and re-run.
- **Does not prompt during I1.** Untranslatability decisions are recorded,
  not asked.

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/placeholder-protect.md`](protocols/placeholder-protect.md) ·
  [`protocols/format-roundtrip.md`](protocols/format-roundtrip.md) ·
  [`checklists/i18n-format-checklist.md`](checklists/i18n-format-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/protect-pass-spec.md`](references/protect-pass-spec.md)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
