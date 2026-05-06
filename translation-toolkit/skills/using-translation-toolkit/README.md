# using-translation-toolkit

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Router skill for translation-toolkit — inspects intent + input shape and dispatches to the right specialist.
> Does not translate.

Part of the [translation-toolkit](../..) plugin. Operational spec Claude
loads is [`SKILL.md`](SKILL.md); this README is for humans choosing
whether and how to invoke the router.

## Why a router

The toolkit ships five worker skills that overlap on locale pair but
diverge sharply on input shape, gate matrix, and core-loop variant
(4D vs 5D, S1 SHOULD vs MUST, full pipeline vs audit). Picking the
wrong specialist produces silent quality regressions — for example,
running `translation-i18n` on a markdown doc skips the AST protect-pass
and corrupts code fences; running `translation-doc` on a PO file
ignores the cross-string consistency batch.

The router exists so the user does not have to memorize that matrix.
A single entry point inspects the request, applies one routing rule
(input shape wins over intent), and hands off.

## What it routes between

| Specialist | Lands here when |
|---|---|
| [`translation-intake`](../translation-intake) | Brief is ambiguous, no format / domain hint, or `--explicit` requested |
| [`translation-i18n`](../translation-i18n) | Input is `.po` / `.json` / `.xliff` / `strings.xml` / `.strings` |
| [`translation-doc`](../translation-doc) | Input is `.md` / `.mdx` / `.markdown` or technical-doc prose |
| [`translation-creative`](../translation-creative) | Input is ad copy / headline / tagline / catchphrase / brand brief |
| [`translation-audit`](../translation-audit) | Both source AND existing target supplied with review intent |

## Routing rule

```
input-shape signal > intent signal
```

An attached PO file routes to `translation-i18n` even if the user
says "creative". A `(source, target)` pair routes to `translation-audit`
even if the format is i18n. See [`SKILL.md`](SKILL.md) §"Routing rules"
for the full disambiguation table.

## When to use this router

- User asks for a translation between `en-US` / `ja-JP` / `zh-TW` / `zh-CN`
  and has not named a specific specialist
- User pastes translatable content but no explicit pipeline
- Trigger phrases (any locale): "translate / 翻訳して / 翻譯一下 / 翻译",
  "i18n / localize / 本地化 / ローカライズ", "audit translation /
  翻訳レビュー / 翻譯審核", "transcreation / トランスクリエーション"

## When NOT to use

- User explicitly names a downstream skill — call it directly
- Task is outside translation scope:
  - Original-language copywriting → [`copywriting-toolkit`](../../../copywriting-toolkit)
  - Original-language doc authoring → [`domain-teams:docs-team`](../../../domain-teams)
  - Original-language drafting in target locale → [`domain-teams:copywriting-team`](../../../domain-teams)
- Locale pair outside the v0.1.0 supported set (en-US ↔ ja-JP ↔ zh-TW ↔ zh-CN)

## Cross-plugin composition

`copywriting-toolkit` and `translation-toolkit` represent **orthogonal**
quality dimensions (translation fidelity ≠ copywriting persuasion / form
/ ethics). Neither auto-invokes the other. If you want post-translation
copy polish, chain them explicitly:

```
translation-toolkit  →  target-language draft + audit-trail + gate verdicts
                            ↓ (user explicitly requests)
copywriting-toolkit  →  voice / form / ethics gates applied to the draft
```

This is opt-in by design — the router never reaches across the plugin
boundary unprompted.

## What this skill does NOT do

- **Does not translate.** If you paste source text into a router
  conversation expecting a target, the router tells you which specialist
  applies and waits for the harness to invoke it.
- **Does not invoke specialists via the Skill tool.** It describes the
  routing decision; the runtime / harness performs the actual chained
  invocation.
- **Does not decide locale pair or strategy.** That is
  [`translation-intake`](../translation-intake)'s job.
- **Does not audit translations.** That is
  [`translation-audit`](../translation-audit)'s job.

## Web search default

All four active translation skills run with web search **ON** by default
(spec Decision #7). The router documents two cases that warrant
`--web-search=off`:

1. **Batch i18n runs (1000s of strings)** — per-miss searches multiply
   cost and latency
2. **Locked brand voice** — competitor copy may contaminate the register

See [`SKILL.md`](SKILL.md) §"Web search trade-off note" for the policy
the four downstreams inherit.

## See also

- [`SKILL.md`](SKILL.md) — operational spec (routing rules, disambiguation
  examples, roles vocabulary, cross-plugin contract)
- [`../../README.md`](../../README.md) — plugin-level overview (4-tier
  glossary, 5-gate verification, locales supported)
- [`../../docs/architecture.md`](../../docs/architecture.md) — 5-layer
  pipeline + 4-tier glossary fallthrough
- Sibling skill READMEs:
  [`translation-intake`](../translation-intake) ·
  [`translation-i18n`](../translation-i18n) ·
  [`translation-doc`](../translation-doc) ·
  [`translation-creative`](../translation-creative) ·
  [`translation-audit`](../translation-audit)
- Design spec: [`docs/superpowers/specs/2026-05-06-translation-toolkit-design.md`](../../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md)
