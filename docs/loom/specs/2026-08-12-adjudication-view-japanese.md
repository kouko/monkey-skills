# Brief: adjudication view — Japanese support and an honest firing condition

Date: 2026-08-12
Stage: brainstorming output → writing-plans input
Design-side on-ramp: no criteria row fired (increment to a shipped loom-code mechanism) — no detour offered.
Axis 0 queue check: `## Now` empty (no competing bet); no OPEN backlog entry touches i18n or this mechanism.

## Problem

The adjudication view shipped with a firing condition that claims more
than the machinery delivers: it fires whenever the conversation
language is **not English**, but every downstream component is
Traditional-Chinese-only. The adjudicator works in 中/日/英, so a
Japanese session today walks into a stuck flow rather than a Japanese
view — measured: a faithful Japanese rendition of a negated source
(「書き換えてはいけません」 for "must not be rewritten") hard-fails the
lint with `negation dropped in rendition`, because the negation check
looks for ZH characters that Japanese negation (kana inflection) never
contains. The job: **make the view actually work in the languages the
adjudicator uses, and make its stated trigger true.**

## Users

kouko — sole adjudicator, works in 繁體中文 / 日本語 / English and
switches per project. Reads in the Claude Code chat/terminal (long
artifacts as a side-panel HTML page). Today: Chinese sessions get the
view; Japanese sessions get a lint that blocks on correct output;
English sessions correctly get nothing.

## Smallest End State

A **language profile** layer over the existing single-language
machinery, plus a firing condition that names its supported languages.

1. **`--lang` on both scripts**, defaulting to `zh-Hant` (every current
   invocation keeps working unchanged). `adjudication_lint.py --lang
   {zh-Hant|ja}`, `adjudication_render.py --lang {zh-Hant|ja}`.
2. **Profile table** replacing the three hardcoded constants
   (`_ZH_NEGATION_MARKERS`, `_ZH_NEGATION_PREFIX`, `_MODALITY_MAP`) with
   one dict keyed by language tag. Adding a language becomes adding a
   profile entry, not editing check logic.
3. **Japanese negation check runs at WARNING tier, not hard-fail** —
   the load-bearing design decision, see Alternatives.
4. **Japanese modality per JIS Z 8301:2019 Clause 7** (verification
   result: PARTIAL — reproduced by the kikakurui.com JIS-text mirror,
   Tables 3-7; the JSA original is paywalled and was not read). Two
   findings from verification change the design:
   - **The English column is 参考, not 規定.** JIS states verbatim of
     the English correspondence: 「この規格で規定する事項ではない」. The
     *Japanese* forms are normative for JIS drafting; their pairing to
     shall/should/may is reference material aligned to ISO/IEC
     Directives Part 2. So the table is a well-grounded convention to
     adopt, not a standard we can claim conformance to — the protocol
     must say "derived from" and not "per".
   - **Map by meaning, not by matching the English token.** In
     ISO/JIS register, `shall` = 要求事項 (a requirement of the
     standard) and `must` = an *external* constraint (statute, physical
     law) in its own Table 7. Our source artifacts use "must"
     colloquially for obligation, i.e. semantically ISO's `shall`.
     Mapping our "must" onto JIS's `must` row would be a register
     error. Our modals map to the 要求/推奨/許容 tables by force, not
     by spelling.
   - **Each Japanese modal takes a SET of accepted forms, not one.**
     JIS lists alternatives per table (e.g. 推奨: …することが望ましい /
     …するのがよい / …することを推奨する). The profile value is a tuple
     and the check passes when ANY listed form appears — otherwise a
     translator using a different JIS-sanctioned form gets a false
     warning. The Chinese profile becomes single-element tuples, same
     structure.

   Resulting Japanese table (by force, from Clauses 7 Tables 3-5):

   | our source modal | accepted Japanese forms |
   |---|---|
   | must | しなければならない / する / とする |
   | must not | してはならない / しない |
   | should | することが望ましい / するのがよい / することを推奨する |
   | should not | 望ましくない / しない方がよい |
   | may | してもよい / してよい / 差し支えない |
5. **Renderer emits the right `lang` attribute and font stack** per
   profile (`zh-Hant` + Noto Sans TC / `ja` + Noto Sans JP).
6. **Firing conditions state the supported set**: the view fires when
   the live conversation language is a supported profile; any other
   non-English language is N/A-loud (say so, produce nothing) rather
   than firing into machinery that cannot serve it.

## Current State Evidence

- **Forward** (what fires today): `protocols/adjudication-view.md:95`
  — "The view **fires only when live conversation language is not
  English**". Four wiring pointers repeat the same "not English"
  wording (`requesting-code-review/SKILL.md:118`,
  `references/relay-phrasing.md:28`, `requesting-docs-review/SKILL.md`
  hand-to-user + STILL_BLOCKING, `brainstorming/SKILL.md:219`,
  `writing-plans/SKILL.md:125,145`).
- **Reverse** (who owns the language facts): the three constants are
  module-level in `adjudication_lint.py` —
  `_ZH_NEGATION_MARKERS = "不未無非沒勿"` (:88),
  `_MODALITY_MAP` EN→ZH pairs (:141-147), `_ZH_NEGATION_PREFIX = "不未非"`
  (:153). No config file, no indirection: the checker IS the SSOT for
  the language facts today, which is why a second language has nowhere
  to live.
- **Error** (today's failure mode, measured): Japanese rendition of a
  negated source → `run_checks` returns
  `['u1: negation dropped in rendition', "WARNING u1: expected 「不得」 for 'must not'"]`,
  `exit_code_for` = 1. The hard tier means the flow then regenerates
  once and surfaces to the user — a stuck gate, not a view.
- **Data** (schema impact): none. Units-JSON (`id / heading /
  source_text / anchors / rendition`) is language-neutral; only the
  checks and the render template read language-specific facts.
- **Boundary**: `adjudication_render.py:101` hardcodes
  `<html lang="zh-Hant">` and `:42` the `Noto Sans TC` stack. The
  protocol's `## Fixed modality mapping` (:40-56) presents ONE table
  with no language column.

Evidence paths appendix: loom-code/scripts/adjudication_lint.py; loom-code/scripts/adjudication_render.py; loom-code/skills/using-loom-code/protocols/adjudication-view.md; the four wiring SKILL.md files listed under Forward.

## Alternatives Considered (research-grounded)

Full research is recorded in this session and summarized here; two
independent research arms (EN + JA sources) were run and **disagreed**,
which is itself the finding that shaped the decision.

| Option | What it means | Evidence |
|---|---|---|
| **Morphological analyzer** (MeCab / Sudachi / fugashi / Janome) | Proper POS-aware Japanese negation detection — what every published method uses | Both arms: every evaluated Japanese negation-scope method runs on a morphological analyzer (Matsuyoshi et al., ACL L14-1606, MeCab-tagged; 川添 et al. ANLP2011; 矢野 et al. ANLP2017). **Rejected**: all of them are third-party PyPI packages; Janome is pure-Python but still third-party and still an analyzer. Our stdlib-only contract is not negotiable for a disposable-view lint. |
| **Hard-tier Japanese negation by regex** | Same tier as Chinese: missing negation blocks | **Rejected on measurement.** Japanese negation is inflectional and `〜ない` is a homograph of the い-adjective ending: probed 変更は少ない / この操作は危ない / 説明がつまらない — all match a naive kana regex, none are negations. The false-positive direction is silently permissive (a rendition that dropped the negation but contains 少ない passes), i.e. it breaks exactly the guarantee the check exists for. No regex-only Japanese negation baseline with reported accuracy exists in either arm's search (explicit absence). |
| **Warning-tier Japanese negation (CHOSEN)** | Japanese negation mismatch is reported, never blocks | Respects the evidence: the signal is real but unreliable, so it informs rather than gates. Mirrors the modality check's existing warning tier and the repo's own precedent for observing before hardening. |
| **Japanese modality from a fixed table** | Same shape as the Chinese modality table | Japanese DOES have closed normative sets — JIS Z 8301 maps shall/should/may to fixed Japanese forms (JA arm; secondary source, verification pending), and 法制執務 fixes しなければならない / してはならない / することができる / するものとする (参議院法制局, primary). General technical Japanese has no controlled-language standard fixing modality (explicit absence, both arms). |

Prior-art note carried from the research: **no CAT/QA tool (Trados,
memoQ, Xbench) implements a negation- or modality-preservation check
for any language pair** — both arms confirmed this independently.
Surface-level semantic translation QA is unsolved commercially, which
argues for humility about the tier, not for skipping the check.

**My take:** ship the profile layer with Japanese negation at warning
tier and Japanese modality from the verified normative table.
Conditional reversal: if dogfood shows the Japanese negation warning is
mostly noise (false positives dominate real catches), drop the check to
observation-only in the report rather than adding an い-adjective
exception lexicon — the lexicon is a maintenance surface Chinese never
needed, and its absence is what keeps this cheap.

## Decision

Build the language-profile layer (`--lang`, profile dict, per-profile
render attributes), Japanese profile with JIS-derived modality and
warning-tier negation, and rewrite the firing condition plus the four
wiring pointers to name supported languages instead of "not English".

Do NOT build: an い-adjective exception lexicon (deferred to the
conditional reversal above); morphological analysis of any kind; any
third language; per-language HTML templates (one template, parameterized
attributes); a language auto-detector (the orchestrator knows the
conversation language and passes it).

## Out of Scope

- Korean, or any language beyond zh-Hant + ja
- Changing the units-JSON schema (language-neutral, stays)
- The nine 🟢 debts carried from the previous arc (separate queue)
- Retrofitting the already-shipped Chinese behavior — `--lang zh-Hant`
  must reproduce today's output byte-for-byte

## What Becomes Obsolete

- The "not English" firing condition (replaced, in the protocol and in
  all four wiring pointers — the wording is the defect, so every copy
  moves in this change).
- The three hardcoded language constants (absorbed into profiles).
- The plan Decision Log's note that a 無-form inversion slips the
  polarity warning becomes partially obsolete: the profile table makes
  the ZH prefix set editable in one place, so widening it is a
  one-line change if the arc touches it.

## Open Questions

1. RESOLVED — JIS Z 8301:2019 Clause 7 verified PARTIAL (kikakurui.com
   mirror; JSA original paywalled). Table and its two caveats folded
   into Smallest End State item 4. Residual: the 2008 edition's
   附属書H placement was not confirmed (irrelevant — we cite 2019), and
   the ISO/IEC Directives Part 2 table itself was not read directly
   (iso.org 403); its content rests on well-established public
   knowledge, which is adequate since we adopt the Japanese column.
2. RESOLVED by the set-of-forms design: `should` no longer needs a
   single winner — することが望ましい and するのがよい are both accepted,
   so the normative-register form does not force stiff digest prose.
3. Competing Japanese technical-writing conventions (JEITA, academic
   style guides) were NOT searched — the verification agent's search
   budget ran out. A genuine gap, not a negative finding: if one exists
   and contradicts JIS, the profile table is one dict literal to
   change.
4. Dogfood target: the first Japanese-language session that hits a
   gate. Until one occurs, the Japanese profile ships tested but
   un-exercised on real prose — state that in the close-out rather
   than implying field validation.
