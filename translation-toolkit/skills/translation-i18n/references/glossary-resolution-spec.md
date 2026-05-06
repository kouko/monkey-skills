---
purpose: 4-tier glossary resolution algorithm for the LLM at runtime.
applies_to: [translation-i18n, translation-doc, translation-creative, translation-audit]
---

# Glossary resolution — 4-tier fallthrough

Per chunk source-analysis, for each candidate term:

## L1: Project glossary
Path: `<repo>/docs/i18n/glossary-{tgt}.md` (or user-supplied `--glossary-path`).
- Highest authority. Absolute override on conflict.
- Hit → record in audit_trail with `tier: L1`, source = project glossary version.
- Miss → continue to L2.

## L2: Bundled glossary
Per-skill `glossary/glossary-{lang-A}--{lang-B}.md` (functional copies of canonical).
- Standard cross-repo terminology. Use `lib.glossary.lookup(...)` for direct + EN-pivot.
- Hit → record `tier: L2`, source = upstream attribution (pontoon / gnome / jlt / naer / etc).
- Miss → continue to L3.

## L3: Web search (tool abstraction)
Trigger: term flagged in source-analysis as "translation-difficult" AND L1+L2 missed.
- Cap: max 10 web searches per document (cost guard).
- Dedup: same term resolved to same translation across multiple chunks gets cached after first hit.
- Skill prompt directive: "If a web search capability is available, search '<term> <target_lang_full_name> 翻訳 OR translation' and extract candidate translations from the top 3 results."
- Tool mapping: WebSearch (CC) / google_web_search (Gemini) / browser (Codex). The skill prompt says "if available" — graceful skip otherwise.
- Hit → record `tier: L3`, source = top-3 cited URLs.
- Miss / unavailable → continue to L4.

## L4: LLM fallback
- No reference material. The translator role generates a translation based on its own training.
- Always succeeds (the LLM produces *something*).
- Record `tier: L4`, source = "llm-fallback", flagged in audit_trail for human review.

## Optional cache layer (off by default at v0.1)
If user runs `scripts/fetch-microsoft-terms.py` or `scripts/fetch-jpo-utx.py`, those entries land in `~/.cache/translation-toolkit/`. Treat as L2-tier (bundled) once present; skill prompt detects cache presence on startup.
