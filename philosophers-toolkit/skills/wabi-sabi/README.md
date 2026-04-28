# Wabi-Sabi Skill

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Assess imperfection through three lenses to judge when something is
"good enough" and counter over-engineering and perfectionism.

## The Three Lenses

| Lens | Japanese | Core Question | Purpose |
|------|----------|---------------|---------|
| Wabi | 侘 | What can be removed without losing essence? | Simplicity and austerity |
| Sabi | 寂 | What imperfections tell a story or add character? | Patina of age and use |
| Incompleteness | 不完全の美 | What unfinished elements invite growth? | Beauty of deliberate incompleteness |

## Method Type

Framework-driven analysis (three independent lenses applied sequentially,
then synthesized into a "good enough" judgment).

## Applied to Software / Product

| Lens | Over-engineering | Wabi-Sabi |
|------|-----------------|-----------|
| Wabi | 20 unused features | 5 features users need daily |
| Wabi | 50 API endpoints | 10 versatile endpoints |
| Wabi | 3 abstraction layers | Direct implementation until needed |
| Sabi | Generic 500 error | Context-aware helpful error messages |
| Sabi | Sudden API deprecation | Gradual deprecation with migration guide |
| Sabi | Outdated UI rewrite | Familiar UX patterns users rely on |
| Incompleteness | All future requirements anticipated | Extension points ready, implementation later |
| Incompleteness | Everything built into core | Core + plugin architecture |
| Incompleteness | 100-field template | Minimal template + user customization |

## Key Distinction: Quality vs Over-Quality

| | Low Quality (not wabi-sabi) | Sufficient Quality (wabi-sabi) | Over-Quality (also not wabi-sabi) |
|--|----------------------------|-------------------------------|----------------------------------|
| Definition | Missing essential function | Essential function present, non-essential removed | Polish beyond what context requires |
| Example | Broken search | Search works, no autocomplete | Search with ML-powered suggestions for 5 users |
| Action | Fix it | Ship it | Strip it |

## Examples in SKILL.md

| Example | Domain | Key Insight |
|---------|--------|-------------|
| MVP release decision | SaaS Product | Remove non-core features (Gantt, dashboard), improve error messages, add status customization |
| UI polish decision | Internal tool | 5-user internal tool needs no animations or themes; fix the one actual complaint instead |

## Additional Cases

See `references/wabi-sabi-cases.md` for more examples:
API design simplification, technical debt assessment, documentation scope.

## Connections to Other Skills

| Skill | Relationship |
|-------|-------------|
| design-team (Kansei Engineering) | Wabi-sabi informs what to leave out; kansei informs what must stay for emotional resonance |
| code-team (YAGNI) | Wabi (simplicity) aligns with YAGNI; incompleteness aligns with extension points |
| hegelian-dialectics | When "ship vs polish" becomes a binary, dialectics finds the synthesis; wabi-sabi provides the lens |
