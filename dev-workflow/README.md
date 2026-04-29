# dev-workflow

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Version**: 1.7.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

Developer workflow skills — skill authoring, skill quality scoring,
portable git-backed project memory, and a *critique* line for design
decisions (proposals before code, single changes to existing code).

## Skills

| Skill | Slash cmd | Role |
|-------|-----------|------|
| `skill-creator-advance` | `/skill-creator-advance` | Create new skills and iteratively improve them via eval-driven loop |
| `skill-judge` | — | 8-dimension quality rubric for scoring an existing skill (advisory, 0-120 scale) |
| `git-memory` | — | Portable, tool-agnostic project memory via git commit trailers + PR body `## Memory` section |
| `proposal-critique` | — | Triage a multi-item proposal (list, plan, or prose) into KEEP / DEFER / DROP via evidence grounding + YAGNI |
| `complexity-critique` | `/complexity-critique` | Gate a single proposed change to existing code (refactor, feature add, debt cleanup) through three deletion-first questions before implementing |
| `skill-refactor` | `/skill-refactor` | Token / structure refactor of an existing skill with output equivalence guaranteed via multi-judge ensemble + git ratchet (Phase A of skill-evolution architecture) |
| `skill-tuning` | `/skill-tuning` | Output quality A/B for an existing skill — generate variants with different output traits, run them blind, capture user preference. Constitution as floor; taste as ceiling; preference log accumulates as RLHF-lite dataset (Phase B of skill-evolution architecture) |

### The "critique" line

`proposal-critique` and `complexity-critique` are siblings — same
gate-skill shape, different scope and lifecycle stage:

```
proposal-critique  →  complexity-critique  →  Anthropic simplify
(list / plan       (single change to       (post-implementation
 / prose,           existing code,           diff review)
 before any code)   before implementing
                    the change)
```

Together they cover most of the "is this worth it" decision space
without duplicating the gate logic.

### Skill-evolution architecture (skill-refactor + future skill-tuning)

The dev-workflow plugin is rolling out a four-skill family for
authoring, evaluating, and evolving skills:

```
skill-creator-advance  →  skill-refactor  →  skill-tuning  →  skill-judge
(creation + redesign;     (Phase A: token /    (Phase B: output    (advisory
 spec-first; full         structure refactor;  quality A/B; human  scoring;
 eval loop)               output preserved;    judge; preference   never
                          git ratchet)         log)                modifies)
```

- `skill-refactor` (v1.6.0) handles *behavior-preserving* refactor
  of existing skills
- `skill-tuning` (this PR, v1.7.0) handles taste-sensitive output
  A/B with human judgment + preference log
- The split avoids the LLM-as-judge / Goodhart drift that monolithic
  taste-rubrics produce — see [`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md)
  for the full rationale

### git-memory — three pillars

Memory lives in git artifacts themselves, so any tool that reads git
(Claude Code / Cursor / Codex / aider / human) can reconstruct
project knowledge without a separate store.

1. **Carrier = git artifacts themselves** — commit messages and PR
   bodies are the substrate. `git clone` brings the memory; no
   separate DB, embedding index, or vendor-specific file required.
2. **Structure = commit trailers** — `Decision:` / `Learning:` /
   `Gotcha:` ride in the commit footer alongside `Co-Authored-By:`
   (the `git-interpret-trailers(1)` mechanism). Machine-readable via
   `git log --pretty='%(trailers)'`, human-readable in prose body.
3. **Content = decision context, not code** — record **why**, not
   **what**. The diff already shows what; memory records the
   reasoning, alternatives rejected, and gotchas for future self.

git-memory complements Claude Code's native `~/.claude/.../MEMORY.md`
(user-level preferences). Project-level decisions live in git;
user-level preferences stay in Claude native memory.

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
│   ├── skill-creator-advance.md
│   └── complexity-critique.md
├── docs/
│   └── skill-evolution-architecture.md   ← H1-H4 horizon planning doc
└── skills/
    ├── skill-creator-advance/
    │   ├── SKILL.md
    │   ├── LICENSE               ← AllanYiin + kouko copyright
    │   ├── NOTICE                ← Upstream chain detail
    │   ├── agents/               ← grader / comparator / analyzer
    │   ├── scripts/              ← aggregate_benchmark / run_eval / run_loop / improve_description / package_skill / quick_validate / generate_report
    │   └── references/           ← plugin-conventions / iteration-automation / platform-adaptations / eval-methodology / schemas / mermaid-usage-guidelines
    ├── skill-judge/
    │   ├── SKILL.md              ← 8-dimension rubric (E:A:R + 5-pattern + 9 failure-pattern)
    │   ├── LICENSE / NOTICE      ← upstream attribution
    │   └── README.{en,ja,zh-TW}.md
    ├── git-memory/
    │   ├── SKILL.md
    │   ├── standards/             ← memory-conventions (trailer schema, PR body, diagram venue)
    │   ├── protocols/             ← compose-commit / compose-pr
    │   └── scripts/               ← memory-grep retrieval primitive
    ├── proposal-critique/
    │   ├── SKILL.md               ← single-file gate skill (Iron Law / Gate Function / Triage Matrix)
    │   └── README.{en,ja,zh-TW}.md
    ├── complexity-critique/
    │   ├── SKILL.md               ← single-file gate skill (Iron Law / 3 Questions / Verdict)
    │   ├── LICENSE / NOTICE       ← joshuadavidthomas → softaworks → kouko MIT chain
    │   └── README.{en,ja,zh-TW}.md
    ├── skill-refactor/
    │   ├── SKILL.md               ← Phase A: token / structure refactor with equivalence guarantee
    │   ├── LICENSE / NOTICE       ← original design; design distinctions vs darwin-skill noted
    │   ├── README.{en,ja,zh-TW}.md
    │   ├── references/            ← equivalence-check / multi-judge / refactor-moves / golden-anchor / test-prompts-schema / constitution-schema (canonical SoT for shared conventions)
    │   └── scripts/               ← equivalence_check / multi_judge / golden_compare
    └── skill-tuning/
        ├── SKILL.md               ← Phase B: output quality A/B with human judge + preference log
        ├── LICENSE / NOTICE       ← original design; design distinctions vs darwin-skill noted (9 differences)
        ├── README.{en,ja,zh-TW}.md
        ├── references/            ← ab-harness / constitutional-judging / preference-log-schema / self-trained-judge-pipeline + 3 shared convention bundled functional copies
        └── scripts/               ← ab_harness / preference_log / judge_train_stub
```

## License

MIT — see repository root [`LICENSE`](../LICENSE) and skill-level
[`LICENSE`](skills/skill-creator-advance/LICENSE) / [`NOTICE`](skills/skill-creator-advance/NOTICE).
