# Axis 4 — Research Protocol (full)

The full protocol behind `SKILL.md` §Axis 4. SKILL.md carries the core rule
(WebSearch the shipped options, minimum EN + JA, end in a recommendation) +
the output format; this file carries the query patterns, the bilingual
rationale, and the edge cases. Also referenced by **router rule #5** (Research
before asking) for decisions that arise OUTSIDE the brainstorming-Axis-4
context — e.g. an SDD implementer asking "which retry strategy?" mid-execution.
Same protocol, same output format.

## Why WebSearch, not memory

The agent's training data is frozen; current consensus may have shifted.
*"Alternatives I can imagine"* is the failure mode this protocol prevents — it
produces alternatives that don't exist (hallucinated libraries, deprecated
patterns, decade-old advice).

## Bilingual query patterns (mix EN + JA every round)

Run at minimum one English AND one Japanese query per Axis-4 round —
single-language search is sampling bias. Use 2-3 patterns, mix-and-match:

| Lang | Pattern | Example for "rate limiting algorithm" |
|---|---|---|
| EN | `<topic> industry best practice <year>` | "rate limiting algorithm industry best practice 2025" |
| EN | `<topic> trade-offs <year>` | "rate limiting algorithm trade-offs 2025" |
| EN | `<topic> open source library` | "rate limiting open source library node.js" |
| EN | `<topic> RFC` / `<topic> spec` | "rate limiting RFC 6585 retry-after" |
| EN | `<vendor> <topic>` | "Cloudflare rate limiting algorithm" |
| JA | `<topic 日本語> 設計 ベストプラクティス <year>` | "レート制限 アルゴリズム 設計 ベストプラクティス 2025" |
| JA | `<topic 日本語> 実装事例 / 採用事例` | "レート制限 Stripe 実装事例" |
| JA | `<vendor 日本語名> <topic 日本語>` | "メルカリ レート制限" / "クックパッド rate limiting" |
| JA | `<topic 日本語> Qiita` / `<topic 日本語> Zenn` | "レート制限 アルゴリズム Qiita" |

## Why both languages

- Japanese engineering blogs (Qiita / Zenn / はてなブログ / 個人 Tech Blog) often
  cover details + 失敗事例 / post-mortems the English web misses.
- Japanese-developed tech (Mercari / Cookpad / LINE / Sansan / SmartHR / freee /
  DeNA) is frequently documented only in Japanese.
- Cross-language consensus is a stronger signal than single-language: when EN +
  JA agree the recommendation is robust; when they disagree, the disagreement is
  itself a finding.
- Domain gap example: for encoding security, English search underrepresents
  文字コード attack vectors that 徳丸本 第 2 版 Ch.6 catches.

Cite sources in **both languages**, each labeled by source language (EN / JA) so
the user can audit coverage at a glance.

**If a Japanese search returns 0 relevant hits**, surface that as a finding —
*"Searched in 日本語 with patterns X, Y; 0 relevant Japanese-language results —
this topic appears to have English-only industry coverage."* The empty result IS
the signal; don't silently skip the language axis.

## If WebSearch is unavailable

Surface the limitation **explicitly** — do NOT silently fall back to imagined
alternatives:

> *"WebSearch is unavailable in this session. I can articulate alternatives from
> memory but my training cutoff is <date> — current industry consensus may have
> shifted. Want me to (a) proceed with from-memory alternatives flagged as
> 'unverified vintage', (b) defer until you can re-run with WebSearch, or (c) you
> research and paste findings?"*

The point is informed consent: the user knows the alternatives weren't verified.

## When ≤3 alternatives genuinely exist

If WebSearch returns "the industry has only ever had 2 approaches to this," that
is a valid output. Document it: *"Searched X, Y, Z; only 2 distinct approaches
found in current industry use; neither has obvious technical advantage."* Don't
pad with bad alternatives to hit 3.

## Anti-patterns

- ❌ **"Alternatives I can think of"** — training data is frozen; use WebSearch.
- ❌ **Single-source research** — if all 3 alternatives come from one blog post,
  the research is shallow. Cross-source.
- ❌ **Single-language coverage** — sampling bias; minimum EN + JA, cite both,
  label each by source language.
- ❌ **Surface options without trade-offs** — 3 algorithm names with no pros/cons
  is decoration, not decision-support.
- ❌ **No "my take"** — research that doesn't end in a recommendation pushes the
  synthesis cost back to the user. Compress research INTO a recommendation,
  surface it, and document the reasoning so the user can override.

## Output format — surfacing alternatives to the user

```
Industry approaches found (3, via WebSearch):

1. <Approach name> — <source citation, e.g. RFC 6585, Cloudflare blog, Stripe API docs>
   • Pros: <2-3 bullets>
   • Cons: <2-3 bullets>
   • Used by: <named vendors / open-source projects>

2. <Approach name> — <source>
   ...

3. <Approach name> — <source>
   ...

My take (given your context):
  Recommend: <approach #N>
  Why: <1-2 sentences tying recommendation to user's brief + constraints>
  Conditional reversal: <if X changes, prefer approach #M instead>
```
