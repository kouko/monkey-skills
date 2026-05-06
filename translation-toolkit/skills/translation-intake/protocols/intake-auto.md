# intake-auto — auto-detect intake protocol

**Mode**: default (no flag needed)
**Inverse**: see `protocols/intake-explicit.md` (`--explicit` / `-e`)

---

## Purpose

In **auto** mode the intake skill performs a single source-analysis pass that infers all 5 axes plus the skopos statement from source content alone. The user only supplies source text and the source/target locale pair (locale is never inferred — see Axis 4 in the canonical orthogonal-axes reference). Everything else is heuristic-derived and recorded in the audit trail with `inferred=true` so downstream review can spot misfires.

Goal: **zero-friction default**. Power users who want explicit control switch to `--explicit`.

---

## Pipeline

One source-analysis call extracts all 5 axes in a single pass. No multi-round loop, no retries.

### Inputs (from user)

- `source_text` — string (or path to a file the skill reads)
- `source_locale` — BCP-47, REQUIRED (e.g. `en-US`, `ja-JP`, `zh-TW`, `zh-CN`)
- `target_locale` — BCP-47, REQUIRED

### Inferred outputs (5 axes + skopos)

#### 1. domain — top-3 keyword match against the 13-domain taxonomy

Frozen taxonomy (v0.1.0):

```
general              # 通用語彙 — fallback / cross-domain
ui                   # UI strings (buttons, labels, error messages)
tech.software        # 程式語彙 — general programming
tech.web             # web / API / networking
tech.data            # database / data engineering
tech.crypto          # cryptography / security
gov                  # 政府機関 / 役職名
legal                # 法令 / 契約
medical              # 医療
finance              # 金融 / 投資
marketing            # 広告 / コピー
statistics           # 統計
typography           # 排版規則 (meta-section in glossary files)
```

Extract candidate domain keywords from source via the source-analysis call. Score each domain by keyword density. Pick the **most-prevalent domain** as the canonical `intake.domain` value. Record runners-up in `intake.inferred_values.domain_runners_up` so a downstream skill can broaden glossary lookup if the primary domain misses.

A document covering multiple specialties (e.g. a smart-contract audit doc → `tech.crypto` + `tech.software`) may comma-join in the canonical `domain` field. The structured-array form is deferred to schema v0.2.

#### 2. register — formal / neutral / warm / playful

Analyze sentence structure, honorifics, tone markers:

- `formal` — 敬語 / business / academic; 「いたします」「申し上げます」; Latinate / 漢語 vocabulary
- `neutral` — default professional / journalistic; 「です・ます」; "we will…"
- `warm` — friendly / brand-affinity / conversational; 「〜ですよね」; "we're here for you"
- `playful` — witty / casual / emoji-friendly; exclamations, contractions, irony

#### 3. mode hint — literal / faithful / localized / transcreation

Inferred from text genre (priority order — first match wins; matches the rules table in the canonical orthogonal-axes reference):

| Cue in source | mode | rationale |
|---|---|---|
| Marketing CTA ("buy now" / 「今すぐ」 / 「期間限定」 / urgent imperatives) | `transcreation` | persuasion intent is load-bearing |
| Legal / contract ("hereby" / "shall" / 「第N条」 / 「甲乙」) | `literal` | surface fidelity legally significant |
| Technical doc with code blocks / API references / version numbers | `faithful` | balanced — readability + glossary terms |
| UI string with placeholders (`{{var}}` / `%s`) | `faithful` | constrained format, native-target reading |
| Academic / scientific paper (citations, abstract, hedging) | `faithful` | disciplinary register conventions |
| Government / public announcement | `faithful` | citizen-readable + institutional tone |
| Conversational blog / op-ed / informal newsletter | `localized` | idiomatic readability prioritized |
| News article / journalism | `faithful` | standard news register |
| (no specific cues — fallback) | `faithful` | conservative default |

Prose body → `faithful` is the safe default. Ad copy → `transcreation`. Legal text → `literal`.

#### 4. strategy bias — domestication / foreignization

Default to `domestication` unless source contains foreignization-favoring cues:

- `domestication` (default) — target reads native; cultural references substituted
- `foreignization` — preserves source-culture markers (御朱印 / 紅包 / 課長 / 部長); typical for legal mode and academic texts where named-entity preservation matters

Mode-strategy heuristics:
- `literal` → usually `foreignization`
- `transcreation` → usually `domestication`
- `faithful` / `localized` → either; default `domestication`

#### 5. intent (skopos) — best-effort one-liner

Free-form short string answering: **who reads this and what action is expected?** Examples:

- `"App UI strings shown to end-users for app navigation"`
- `"in-app help text for a SaaS settings page"`
- `"landing-page hero CTA for productivity SaaS"`
- `"API reference for backend integrators"`
- `"government white paper for policy researchers"`

Best-effort from source content. If the source signals are weak, leave the field as a generic statement — the user can override in `--explicit` mode.

---

## Audit-trail integration

All inferred values are written via the audit-trail builder per the canonical audit-trail spec:

```python
builder.set_intake(
    mode="faithful",
    register="neutral",
    strategy="domestication",
    source_locale="en-US",
    target_locale="ja-JP",
    domain="ui",
    intent="App UI strings shown to end-users for app navigation",
    inferred={
        "mode": True,
        "register": True,
        "strategy": True,
        "domain": True,
    },
)
```

`source_locale` and `target_locale` carry `inferred=false` implicitly — locale is always user-supplied (never auto-inferred per Axis 4 in orthogonal-axes).

When the user later overrides an auto-inferred axis (re-runs in `--explicit` mode), the override path MUST also call:

```python
builder.add_inferred_value(axis, original_inference)
```

so the audit retains "what auto would have picked" — essential for retrospective heuristic-tuning analysis.

---

## Re-run on dissatisfaction

If the user looks at the inferred 5-axis spec and disagrees, they re-invoke with `--explicit` (or `-e`). The explicit prompt path takes the auto inferences as **seed values**, presenting them to the user for confirmation or override. See `protocols/intake-explicit.md`.

---

## Worked example

**Input**: a 3-paragraph English UI-strings file (e.g. `en.json` with 30 short button / label / error-message keys), `source_locale=en-US`, `target_locale=ja-JP`.

**Source-analysis pass observes**:
- placeholders `{{userName}}`, `%s` → UI-string format
- short imperatives ("Save", "Cancel", "Try again") → button labels
- error-message phrasing ("Could not load…") → app UI
- no marketing / legal / academic cues
- neutral professional tone, no honorifics, no slang

**Inferred intake spec**:

```json
{
  "mode": "faithful",
  "register": "neutral",
  "strategy": "domestication",
  "source_locale": "en-US",
  "target_locale": "ja-JP",
  "domain": "ui",
  "intent": "App UI strings shown to end-users for app navigation",
  "inferred": {
    "mode": true,
    "register": true,
    "strategy": true,
    "domain": true
  }
}
```

The `intake.domain` value here is `"ui"` — the most-prevalent domain. If the source had also contained code-block snippets and API jargon, runners-up `tech.software` would land in `inferred_values.domain_runners_up` for downstream glossary fallthrough.

This spec is then handed off to the next skill in the pipeline (e.g. `translation-i18n` for a `.json` file).

---

## What this protocol does NOT do

- Does **not** auto-infer `source_locale` or `target_locale` — both are user-supplied at invocation time. Auto-detection on short strings is unreliable.
- Does **not** translate any source content — intake captures parameters only. Translation is the next skill's job.
- Does **not** fail on weak signals — falls back to the conservative default `{mode: faithful, register: neutral, strategy: domestication, domain: general}` and lets the user re-run in `--explicit` if dissatisfied.
- Does **not** prompt the user mid-pipeline. The auto pass is non-interactive by design (matches the router's silent-routing contract).
