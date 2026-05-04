# Changelog

All notable changes to deconstruct-toolkit are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-04

Initial release. Plugin established as a reverse-engineering toolkit for
non-code artifacts (copy / document packs / UI / arguments / products /
organizations) — surfacing design blueprints, hidden frameworks, rhetorical
mechanisms, and intentional omissions.

### Added

#### Skills (4)
- **`using-deconstruct-toolkit`** — router. Two-axis routing (artifact-type
  default + user-intent override) + 3 filters (length / information-only /
  multi-modal) + 3 boundary checks (sourceatlas / philosophers-toolkit /
  forward-production plugins).
- **`artifact-deconstruct`** — flagship. 6-step workflow (type → lens select →
  6-dim run → lens apply → report → self-check) over a 6-lens library
  (semiotic / rhetoric / frame / genre / ux / persuasion) × 6-dimension
  analysis × ethical-position verdict.
- **`argument-deconstruct`** — argument-focused deep dive. Toulmin model
  (with 8 hidden-warrant patterns catalogued) + Burke pentad ratio analysis
  + mermaid argument map with hidden-warrant emphasis.
- **`assumption-surface`** — atomic skill. Reverse-Toulmin + Althusser-
  influenced symptomatic reading + 3-tier strength classification
  (foundational / load-bearing / decorative) + falsifiability tests.

#### Lens references (9)
- 6 in `artifact-deconstruct/references/`: semiotic (Barthes 1970), rhetoric
  (Burke 1945 + Toulmin 1958), frame (Goffman 1974 + Lakoff 1980), genre
  (Swales 1990 + Bhatia 1993), ux (Norman 1988/2013 + Nielsen 1994/2020),
  persuasion (Cialdini 2021 + Brignull 2024).
- 2 in `argument-deconstruct/references/`: lens-toulmin, lens-burke-pentad
  (split from artifact-deconstruct's combined lens-rhetoric for deeper
  argument focus).
- 1 in `assumption-surface/references/`: lens-symptomatic-reading
  (Althusser 1968/1970 *Reading Capital*, simplified-and-operationalized).

Each lens reference opens with a version-locked primary-source citation
per [ADR-0002](docs/adr/0002-strict-skill-self-containment.md) §5.3.1.

#### Eval suite (7 cases)
- 3 cases for `artifact-deconstruct`: Dropbox landing 2024, Notion onboarding
  pack, Stripe signup flow.
- 2 cases for `argument-deconstruct`: op-ed on AI regulation (synthetic),
  VC pitch memo (synthetic Series A).
- 2 cases for `assumption-surface`: Q3 SaaS strategy memo (synthetic), tweet
  thread on productivity (synthetic).

Each case is a YAML spec in `eval/cases/`. Each fixture has a
`## Annotations for evaluator` block specifying must_find expectations
as ground truth.

#### Tooling
- `scripts/check-eval-cases.py` — structural validator. Verifies eval YAMLs
  well-formed, fixtures exist + have annotation blocks, lens references
  have primary-source citations, skill folders are flat. CI-runnable, no
  PyPI dependency. Exit 1 on any failure.

#### Documentation
- [README.md](README.md) / [README.ja.md](README.ja.md) /
  [README.zh-TW.md](README.zh-TW.md) — tri-language plugin documentation.
  JP version anchors with BCG「バリュー・チェーンの脱構築」(Evans &
  Wurster, 2000) and 山口周『武器になる哲学』(2018); ZH version with
  Derrida → BCG/山口周 中文 lineage.
- [docs/design-proposal.md](docs/design-proposal.md) — full v0.1.0 design
  blueprint with 14 sections, 11 design decisions resolved, 7 eval cases
  spec.
- [docs/adr/0001-convention-b-mixed-naming.md](docs/adr/0001-convention-b-mixed-naming.md)
  — naming convention decision record.
- [docs/adr/0002-strict-skill-self-containment.md](docs/adr/0002-strict-skill-self-containment.md)
  — lens cross-skill strategy decision record (strict self-containment +
  4 anti-drift mechanisms).
- [eval/README.md](eval/README.md) — eval suite documentation including
  manual LLM-eval workflow until v1.0 runner.

#### Glossary entries (cross-plugin)
- 22 zh-TW + 24 ja terms added to `monkey-skills/docs/i18n/glossary-{ja,zh-TW}.md`
  under new "文物解構域 / 文物脱構築領域" sections. Locked terms include
  deconstruct / artifact / lens / frame + Toulmin set + UX set + Burke set
  + symptomatic-reading + boundary terms (teardown / reverse-engineering
  marked as **not used** in this plugin to enforce semantic precision).

### Design decisions

11 decisions resolved on 2026-05-04 (full record in
`docs/design-proposal.md` §12 Resolved Decisions):

- Eval fixtures: real public artifacts (URL + access date + fair-use)
- `assets/samples/` nesting: flat (`assets/sample-<name>.md`) — zero hook risk
- MVP: 4 skills (router + artifact + argument + assumption)
- `lens` term: keep English in body across all 3 languages
- Fixtures storage: in-repo Markdown (≤5KB each, CI runs offline)
- `marketplace.json`: same PR
- Convention B (mixed naming) accepted → ADR-0001
- Boundary fences accepted including exclusion of `enterprise-rollout-pack`
- 10 primary-source grounding accepted
- Strict skill self-containment over SSOT pattern → ADR-0002
- Tri-language description draft accepted

### Roadmap

See [README.md §Roadmap](README.md#roadmap) for v0.1 → v1.0 path.
Next minor version (v0.2.0) adds `product-deconstruct` and `pricing-decode`
(business-domain expansion).

[0.1.0]: https://github.com/kouko/monkey-skills/releases/tag/deconstruct-toolkit-v0.1.0
