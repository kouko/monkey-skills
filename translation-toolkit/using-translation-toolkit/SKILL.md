---
name: using-translation-toolkit
description: Router for translation-toolkit. Routes user translation request to the correct active skill based on input shape and intent. Use when user wants to translate something but hasn't specified which sub-skill.
version: 0.1.0
---

# using-translation-toolkit

The router for translation-toolkit. Pick the right active skill based on user intent and input shape.

## Routing rules

- User provides existing translation + asks to review/audit → invoke `translation-audit`
- User provides PO / JSON / XLIFF / Android `strings.xml` / iOS `.strings` file → invoke `translation-i18n`
- User provides Markdown / `.md` / technical doc → invoke `translation-doc`
- User provides ad copy / marketing brief / headline / tagline → invoke `translation-creative`
- Ambiguous (or short raw text) → invoke `translation-intake` first to clarify the 5 axes (mode / register / strategy / locale / domain), then route per output

## Web search trade-off note

Web search is ON by default across all 4 active translation skills (per spec Decision #7) for max quality. Caveats:

- **Batch i18n runs (1000s of strings)**: per-miss searches multiply cost dramatically. Pass `--web-search=off` to disable for batch.
- **Ad copy creative work**: web search may pull competitor copy that contaminates voice. Consider `--web-search=off` if working with established brand voice.

## Cross-plugin composition

`copywriting-toolkit` will NOT auto-invoke this plugin. If user wants post-translation copy polish (voice / form / ethics), they must explicitly compose: translation-toolkit produces target-language draft → copywriting-toolkit applies its own framework gates.

## Reference

See `../docs/architecture.md` for high-level plugin architecture.
See `../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` for full spec.
