# dev-workflow

**Version**: 1.0.4
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

Skill creation and eval workflows — iterative draft → test → review → improve
loop for authoring new Claude skills.

## Skill

| Skill | Slash cmd | Role |
|-------|-----------|------|
| `skill-creator-advance` | `/skill-creator-advance` | Create new skills and iteratively improve them via eval-driven loop |

## Upstream Chain (MIT)

```
Anthropic skill-creator (MIT)
  → AllanYiin (尹相志) skill-creator-advanced (MIT, github.com/AllanYiin/Amon)
    → kouko dev-workflow/skill-creator-advance (MIT)
```

Full license / attribution detail in the skill directory's `LICENSE` and
`NOTICE` files; repo-wide summary in [`../ATTRIBUTION.md`](../ATTRIBUTION.md).

## 7 enhancements added in this distribution

1. monkey-skills ecosystem integration guidance
2. Description best practices (negative triggers, multilingual keywords)
3. Eval flow tiering (quick path vs full path)
4. Existing skill improvement workflow
5. Slash command creation guidance
6. Self-assessment pass (auto-fix obvious defects before human review)
7. Auto-regression detection across iterations

## Design decisions

- Eval results presented **inline + markdown report** (no browser-based eval-viewer; removed Python web server + browser dependency)
- **Token-based budget** (~6,000 tokens) instead of line-based (500 lines)
- Platform adaptations extracted to reference file (optional, loaded on demand)
- Eval methodology grounded with primary-source citations (Fisher 1935, Beck 2002, Hastie et al. 2009, Myers et al. 2011, ISTQB v4.0)

## Repository Structure

```
dev-workflow/
├── .claude-plugin/plugin.json
├── CHANGELOG.md
├── commands/
│   └── skill-creator-advance.md
└── skills/
    └── skill-creator-advance/
        ├── SKILL.md
        ├── LICENSE               ← AllanYiin + kouko copyright
        ├── NOTICE                ← Upstream chain detail
        ├── agents/               ← grader / comparator / analyzer
        ├── scripts/              ← aggregate_benchmark / run_eval / run_loop / improve_description / package_skill / quick_validate / generate_report
        └── references/           ← plugin-conventions / iteration-automation / platform-adaptations / eval-methodology / schemas / mermaid-usage-guidelines
```

## License

MIT — see repository root [`LICENSE`](../LICENSE) and skill-level
[`LICENSE`](skills/skill-creator-advance/LICENSE) / [`NOTICE`](skills/skill-creator-advance/NOTICE).
