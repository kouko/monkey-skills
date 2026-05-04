# deconstruct-toolkit

> Reverse-engineer polished artifacts — surface design blueprints, hidden frameworks, rhetorical mechanisms, and intentional omissions.

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Version**: 0.2.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT
**Cultural-variant scope**: EN / JA / ZH (per [ADR-0004](docs/adr/0004-cultural-lens-variants.md))

## Background

Where `sourceatlas` reverses code and `philosophers-toolkit` clarifies your own thinking, **`deconstruct-toolkit` deconstructs external, polished, non-code artifacts** — marketing copy, document packs, UI flows, long-form arguments, product strategies, organizational artifacts. The goal is not summary; it is **design archaeology** — recovering what the creator decided, what frameworks they borrowed, and what they deliberately omitted.

The toolkit blends three intellectual traditions:

- **Continental philosophy + criticism** — Derrida (deconstruction), Barthes (5 codes / S/Z), Goffman + Lakoff (frame analysis). Methods of revealing binary oppositions, hidden codes, and implicit framing.
- **Anglo-American rhetoric + UX** — Burke (dramatistic pentad), Toulmin (argument model), Bhatia/Swales (genre move analysis), Nielsen-Norman (UX heuristics). Methods of surfacing claims, warrants, and design affordances.
- **Behavioral persuasion science** — Cialdini (7 principles of influence), Brignull (12 dark patterns / deceptive design). Methods of detecting persuasion mechanisms and assigning ethical position.

For Japanese-speaking readers, the toolkit also engages with BCG's value-chain deconstruction (*Blown to Bits*, Evans & Wurster, 2000) and 山口周『武器になる哲学』(2018), where 脱構築 is established as a business-strategy term — not just a philosophical loanword.

### Cultural-variant scope (v0.2.0+)

The 4 culturally-sensitive lenses (rhetoric / persuasion / genre / frame) ship per-language variants for **EN / JA / ZH**. This is a permanent scope decision per [ADR-0004](docs/adr/0004-cultural-lens-variants.md).

| Variant | Anchor sources |
|---|---|
| `-anglo` | Burke / Toulmin / Goffman / Lakoff / Swales/Bhatia / Cialdini / Brignull |
| `-ja` | Hinds / kishōtenketsu / Doi / Yamamoto / 木下是雄 / Markus & Kitayama |
| `-zh` | 劉勰《文心雕龍》六觀 / Hu / Hwang / 行政院公文程式條例 / Peng & Nisbett |

Korean / Vietnamese / Thai / etc. artifacts are **outside this plugin's grounded scope**: they receive an `-anglo` fallback **with explicit caveat** rather than implied coverage. See `protocols/lens-variant-selection.md` for the routing algorithm.

## Boundary

This plugin is for **non-code artifacts only**. Use a different tool when:

| For | Use |
|---|---|
| Codebase reverse-engineering | [`sourceatlas`](https://github.com/kouko/monkey-skills/tree/main/sourceatlas) (impact / flow / overview / pattern / deps) |
| Self-thinking / problem clarification | [`philosophers-toolkit`](https://github.com/kouko/monkey-skills/tree/main/philosophers-toolkit) — operates on `you vs your problem` |
| Dev-artifact critique (proposals / commits / skills) | [`dev-workflow`](https://github.com/kouko/monkey-skills/tree/main/dev-workflow) (proposal-critique / complexity-critique / skill-judge) |
| Forward-direction copy / docs / design **production** | [`copywriting-toolkit`](https://github.com/kouko/monkey-skills/tree/main/copywriting-toolkit), [`docs-team`](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/docs-team), [`design-team`](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/design-team) |
| Investment / equity reverse-engineering | [`investing-toolkit`](https://github.com/kouko/monkey-skills/tree/main/investing-toolkit) |

Why three terms — "deconstruct" vs "teardown" vs "reverse engineering" — are not interchangeable:

| Term | Domain | Semantic core |
|---|---|---|
| **Reverse engineering** | Engineering / hardware / code | Disassemble to **replicate** |
| **Teardown** | Product / consumer apps / hardware | Disassemble to **understand strategy** |
| **Deconstruct** | Philosophy / design criticism / BCG strategy | Reveal **hidden structure & oppositions** |

This plugin is in the third category.

## Install

This plugin lives in the `monkey-skills` marketplace.

```bash
# In Claude Code
/plugin marketplace add kouko/monkey-skills
/plugin install deconstruct-toolkit
```

## Usage

Pick a skill directly when you know which one:

```
/deconstruct-toolkit:artifact-deconstruct
/deconstruct-toolkit:argument-deconstruct
/deconstruct-toolkit:assumption-surface
```

Or let the router pick for you:

```
/deconstruct-toolkit:using-deconstruct-toolkit
```

The router asks one question — "what kind of artifact, what do you want to surface?" — and routes you to the right skill with the right lens preselected.

## Skills (v0.2.0)

### Flagship

#### `artifact-deconstruct`

| Field | Value |
|-------|-------|
| Object | Any polished artifact (copy / document pack / UI / playbook / SOP / advertising / literature) |
| Method | 6-lens library × 6-dimension analysis × ethical-position verdict |
| Lenses | semiotic (Barthes) · rhetoric (Burke + Toulmin) · frame (Goffman + Lakoff) · genre (Swales/Bhatia) · ux (Nielsen-Norman) · persuasion (Cialdini + Brignull) |
| Output | 6-section deconstruction report: surface → design decisions → borrowed frameworks → rhetorical mechanisms (with ethical position) → replicable lessons → weaknesses |
| Use when | "拆解這份" / "為什麼這份寫得這麼好" / "deconstruct this" / "the design behind this" |
| Command | `/deconstruct-toolkit:artifact-deconstruct` |

### Argument-focused

#### `argument-deconstruct`

| Field | Value |
|-------|-------|
| Object | Long-form arguments, op-eds, proposals, political texts, paper introductions |
| Method | Toulmin model (claim / grounds / warrant / backing / rebuttal / qualifier) + Burke pentad ratios + genre move analysis |
| Critical move | Surface hidden warrants — most arguments hide their warrant |
| Output | Argument map (mermaid) + warrant explicitization + missing-rebuttal table + ethical position |
| Use when | "拆解這篇社論的論證" / "這份提案哪裡不對" / "find the hidden assumption in this argument" |
| Command | `/deconstruct-toolkit:argument-deconstruct` |

### Atomic

#### `assumption-surface`

| Field | Value |
|-------|-------|
| Object | Any text where you suspect hidden assumptions (strategy memos, social-media threads, policy briefs) |
| Method | Reverse-Toulmin · symptomatic reading (Althusser-style "what is *not* said") · counterfactual probe · frame audit |
| Output | Assumption table (5–15 rows) with strength rating (foundational / load-bearing / decorative) + falsifiability check per foundational assumption |
| Use when | "揭露這份備忘錄的隱性假設" / "what is this argument *assuming*" / "stress-test these claims before deciding" |
| Command | `/deconstruct-toolkit:assumption-surface` |

### Router

#### `using-deconstruct-toolkit`

| Field | Value |
|-------|-------|
| Skill | Routes user intent to the correct sibling skill |
| Method | One question → artifact-type detection → lens preselection → dispatch |
| Use when | You want to deconstruct something but are not sure which skill or which lens applies |
| Command | `/deconstruct-toolkit:using-deconstruct-toolkit` |

## Design principles

These principles run through every skill in the toolkit:

**Design archaeology, not summary.** Each skill surfaces what was *decided*, not what was *said*. The diff between writing-order and reading-order is the design — that's what we recover.

**Lenses, not a pipeline.** Each artifact deserves a *combination* of lenses chosen to its type. The 6-lens library is selectable, not sequential. A landing page wants persuasion + rhetoric; a playbook wants genre + 6-dimension; a UI wants ux + persuasion.

**Negative space matters.** What is *deliberately omitted* — the missing rebuttal, the absent move, the unsaid assumption — is data, not gap. Every skill includes a negative-space pass.

**Ethical position is mandatory.** When persuasion or UX lenses are applied, every detected mechanism gets one of four positions: 🟢 transparent · 🟡 gray-zone · 🔴 manipulation · ⚫ dark pattern. No neutral description of persuasion mechanisms is allowed.

**Primary-source faithful.** Every lens cites its founding theorist with edition + page number at the top of the lens reference file. Different skills may operationalize the same lens differently — but all must remain faithful to the same primary source. See [ADR-0002](docs/adr/0002-strict-skill-self-containment.md).

**Skill independence.** Each skill is fully self-contained per Anthropic's official skill convention. Lens content may duplicate across skills; this is intentional. See [ADR-0002](docs/adr/0002-strict-skill-self-containment.md).

## Roadmap

See [docs/design-proposal.md](docs/design-proposal.md) §8 for v0.1 → v1.0 path.

| Version | Adds |
|---|---|
| v0.1.0 | router + artifact-deconstruct + argument-deconstruct + assumption-surface |
| **v0.2.0** (this release) | Cultural variants (EN/JA/ZH) for rhetoric / persuasion / genre / frame lenses + variant-selection protocol + 8 JP/ZH fixtures + ADR-0004 |
| v0.3.0 | `product-deconstruct`, `pricing-decode` (business-domain expansion, cultural-variant-aware) |
| v0.4.0 | `frame-reveal`, `bias-audit`, `decision-archaeology` (atomic deepenings) |
| v0.5.0 | `lens-semiotic` + `lens-ux` cultural variants (medium-sensitivity, deferred from v0.2) |
| v1.0.0 | 20+ real-world eval cases, fixture corpus, open-source release |

## Contributing

Contributions welcome. Open an issue first if you are proposing a new skill. Each new skill in this plugin **must** pass two membership gates (see [ADR-0001](docs/adr/0001-convention-b-mixed-naming.md)):

1. **Verb gate** — the skill verb belongs to the deconstruct family (`deconstruct / surface / reveal / audit / decode / expose / archaeology`)
2. **Object gate** — the skill object is an external, polished, non-code artifact

PRs follow [Conventional Commits](https://www.conventionalcommits.org/).

## License

MIT — see [LICENSE](../LICENSE) at the repository root.
