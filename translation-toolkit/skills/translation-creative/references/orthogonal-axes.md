# Orthogonal Axes — mode / register / strategy / locale / domain

**Status**: canonical reference (Single Source of Truth in `scripts/canonical/`; functional copies in active skills' `references/`)
**Cross-refs**: [`core-loop.md`](core-loop.md), [`4d-reflection.md`](4d-reflection.md), [`5d-effectiveness.md`](5d-effectiveness.md), [`audit-trail-spec.md`](audit-trail-spec.md)

---

## Why 5 axes (and why orthogonal)

Reference projects conflate these axes into a single "persona" or "country" knob, which makes combinations like "technical doc + warm tone" or "marketing copy + foreignization strategy + zh-TW locale" impossible to express. translation-toolkit treats them as **independent dimensions** so users can mix freely — every cell in the 5-D combination space is reachable.

In **auto** intake mode, all 5 are inferred from the source by an LLM analysis pass and recorded in audit trail. In **explicit** intake mode (`--explicit` / `-e`), the user supplies all 5.

---

## Axis 1 — `mode`

**Values**: `literal | faithful | localized | transcreation`

| Value | Definition | Surface fidelity vs nuance | Typical use |
|---|---|---|---|
| `literal` | Surface fidelity > nuance | High surface match | Legal contracts, regulatory text, code comments |
| `faithful` | Balanced — meaning preserved with idiomatic target | Medium | Technical docs, API references, READMEs |
| `localized` | Nuance > surface — adapt idioms / examples to target | Low surface match, high meaning match | UX copy, user-facing docs, blog posts |
| `transcreation` | Re-create in target culture for the same persuasive intent | Free | Ad copy, slogans, marketing landing pages |

**Mode → strategy bias** (heuristic — see [`4d-reflection.md`](4d-reflection.md) §Vinay-Darbelnet):
- `literal` favors borrowing / calque / literal-translation
- `faithful` adds transposition
- `localized` adds modulation / equivalence
- `transcreation` opens all 7 strategies including adaptation

**Mode → reflection axis count**:
- `literal | faithful | localized` → 4D ([`4d-reflection.md`](4d-reflection.md))
- `transcreation` → 5D, adding Effectiveness ([`5d-effectiveness.md`](5d-effectiveness.md))

**Mode → S1 threshold** ([`verification-gates.md`](verification-gates.md)):
- `literal | faithful` → 0.85 cosine similarity threshold
- `localized` → 0.85 (same as faithful)
- `transcreation` → 0.70 (relaxed; surface deviation expected) AND S1 promoted from SHOULD to MUST

---

## Axis 2 — `register`

**Values**: `formal | neutral | warm | playful`

| Value | Description | Source-side cue | Target-side handling |
|---|---|---|---|
| `formal` | 敬語 / business / academic | 「いたします」「申し上げます」、Latinate vocab in EN | preserve honorifics, preserve Latinate / 漢語 register |
| `neutral` | Default professional / journalistic | 「です・ます」、"we will…" | clean professional tone, no slang |
| `warm` | Friendly, brand-affinity, conversational | 「〜ですよね」、"we're here for you" | conversational target equivalents |
| `playful` | Witty, casual, emoji-friendly | exclamations, contractions, irony | culture-appropriate playfulness; resist over-translating jokes literally |

**Register conflicts surface in Style** (see [`4d-reflection.md`](4d-reflection.md) §Axis 3): a `formal` intake with a draft using タメ語 form is a Style violation; a `playful` intake with a stiff-academic-Latinate target is a Style violation in the opposite direction.

**S2 gate** ([`verification-gates.md`](verification-gates.md)) compares target register against intake-specified register via LLM judge.

---

## Axis 3 — `strategy`

**Values**: `domestication | foreignization`

(Schleiermacher 1813 / Venuti 1995 — translation strategy.)

| Value | Description | Reads like… | Cultural-marker handling |
|---|---|---|---|
| `domestication` | Target reads native | Originally written in target language | Cultural references substituted with target-culture equivalents |
| `foreignization` | Preserves source-culture markers | A translation, foreign flavor intact | Cultural references kept (with explanation if needed) |

**Strategy is independent of mode**. A `faithful + foreignization` translation of JP business writing into EN keeps 課長 / 部長 / 御社 / 弊社 as recognizable foreign markers (perhaps glossed once); a `faithful + domestication` translation maps them to "Department Head" / "Vice President" / "your company" / "our company".

**Mode-strategy compatibility heuristics**:
- `literal` mode is usually `foreignization` (surface fidelity preserves markers)
- `transcreation` mode is usually `domestication` (re-creation in target culture)
- `faithful` and `localized` modes can pair with either; explicit choice matters

---

## Axis 4 — `locale`

**Values**: BCP-47 tags. v0.1.0 first-class set: `ja-JP | zh-TW | zh-CN | en-US`. Extensible via additional pair-glossary files (see plugin-level `docs/glossary-format-spec.md`).

**Both source and target locale required as separate inputs** (no auto-detection of source locale on short strings — too unreliable; per Decision #15 in design spec).

**Pair-file resolution** ([design spec §Glossary Architecture](../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md)):
- Direct pair file `glossary-{lang-A}--{lang-B}.md` (alphabetical) — preferred
- Pivot via `en-US` if no direct pair file exists for the language pair (e.g., `ja-JP ↔ zh-CN`)

**Locale-specific typography rules** live in `typography/jlreq-summary.md` (jp typography) and `typography/clreq-summary.md` (zh typography) — distributed as functional copies into each active skill.

---

## Axis 5 — `domain`

**Values**: one or more from the v0.1.0 frozen taxonomy:

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

**Multiple domains permitted**. A document can be tagged `["tech.software", "tech.crypto"]` if it covers both; glossary lookup will check both sections in the active pair file.

**Domain affects glossary lookup precedence**: when the same source term appears in multiple domain sections, the most-specific declared domain wins (e.g., `tech.crypto` overrides `tech.software` for `key`). See design spec §Lookup algorithm.

**Domain-determined sub-axes** that critics should consider but are not exposed as user-facing axes:
- Domain-specific term inventories (the glossary pair files; per-domain section)
- Domain-specific style conventions (legal: formal + literal; marketing: warm/playful + transcreation; medical: formal + faithful)
- Domain-specific format conventions (legal numbered clauses, medical structured headers, etc.)

---

## Auto-mode inference rules

In auto mode, the LLM analysis pass at Layer 1 sets all 5 axes from the source. Heuristics applied (in priority order — first match wins):

| Cue detected in source | mode | register | strategy | rationale |
|---|---|---|---|---|
| Marketing CTA detected (e.g., "buy now", "limited time", 「今すぐ」, 「期間限定」, exclamatory urgency) | `transcreation` | `warm` or `playful` | `domestication` | Persuasion intent is the load-bearing element; surface fidelity is anti-helpful |
| Legal / contract language ("hereby", "shall", "Article N", 「第N条」, 「甲乙」) | `literal` | `formal` | `foreignization` | Surface fidelity legally significant; markers preserved |
| Technical doc with code blocks / API references / version numbers | `faithful` | `neutral` | `domestication` | Balanced — readability of explanation matters; technical terms via glossary |
| UI string with placeholders (`{{var}}`, `%s`, `<XLIFF>` envelope) | `faithful` | `neutral` | `domestication` | Constrained format; meaning preserved; native-target reading expected |
| Academic / scientific paper (citations, abstract structure, hedging language) | `faithful` | `formal` | `foreignization` | Disciplinary register conventions; named-entity preservation |
| Government / public announcement | `faithful` | `formal` | `domestication` | Citizen-readable; institutional tone preserved |
| Conversational blog / op-ed / informal newsletter | `localized` | `warm` | `domestication` | Idiomatic readability prioritized |
| News article / journalism | `faithful` | `neutral` | `domestication` | Standard news register |
| (no specific cues — fallback) | `faithful` | `neutral` | `domestication` | Conservative default |

**locale**: never auto-inferred. Source and target locales are always supplied explicitly (per service-interface contract). Auto-detection on short strings is unreliable.

**domain**: inferred from top-3 keyword match against the taxonomy. Multiple domains permitted (e.g., a "smart-contract security audit" doc → `["tech.crypto", "tech.software"]`).

**All inferred values** are written to audit trail with `inferred: true` flags so the user can review and re-run in explicit mode if a heuristic misfired. See [`audit-trail-spec.md`](audit-trail-spec.md) §`intake.inferred`.

---

## Combination examples

| Source genre | mode | register | strategy | locale (s→t) | domain |
|---|---|---|---|---|---|
| EN startup landing page → ja-JP | `transcreation` | `warm` | `domestication` | `en-US → ja-JP` | `marketing` |
| JP government white paper → en-US | `faithful` | `formal` | `foreignization` | `ja-JP → en-US` | `gov`, `statistics` |
| ZH academic ML paper → en-US | `faithful` | `formal` | `foreignization` | `zh-CN → en-US` | `tech.data`, `general` |
| EN open-source README → zh-TW | `faithful` | `neutral` | `domestication` | `en-US → zh-TW` | `tech.software` |
| EN press release → ja-JP | `localized` | `formal` | `domestication` | `en-US → ja-JP` | `marketing`, `gov` |
| EN UI strings (PO file) → zh-CN | `faithful` | `neutral` | `domestication` | `en-US → zh-CN` | `ui` |
| JP medical consent form → en-US | `literal` | `formal` | `foreignization` | `ja-JP → en-US` | `legal`, `medical` |

---

## When user override beats auto-inference

The user override wins. If auto-inference says `mode: faithful` but user passes `--mode=transcreation`, transcreation runs. The audit trail records both:

```yaml
intake:
  mode: transcreation
  inferred:
    mode: false  # user override — auto-inferred mode discarded
  inferred_values:
    mode: faithful  # what auto-inference would have chosen
```

This makes user-vs-auto disagreements visible for later review (and for build-up of intuition about when the heuristics misfire).
