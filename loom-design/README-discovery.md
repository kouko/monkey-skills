# loom-discovery

The **problem-space** station of the loom pipeline: establish, with recorded
evidence, what problem exists, for whom, and whether it's worth your time —
*before* `loom-product-principles` / `loom-interface-design` / `loom-spec` /
`loom-code` start turning an idea into a north star, a design, a spec, or
code.

```
DISCOVER (loom-discovery)  →  principles → interface-design → spec → code
 problem/users/worth-it        the rest of the loom pipeline
```

Agent-portable and key-free: the skills drive the host agent's own LLM — no
external runtime, no API key, no install beyond the plugin.

## What it does

Two professionally-isolated member skills, each with its own artifact and its
own agent contract:

- **`business-value`** — an adversarial worth-it check. A Shape Up betting
  register ("is this worth my time budget right now"), not a Cagan business
  viability study. Optional: fires when the outcome is for others / will be
  published or maintained, when multiple ideas compete for the same time
  budget, or when meaningful resources are at stake; silently skipped for
  personal tools or when the user has already decided GO. Re-entrant after
  research. Produces `business-value.md` — why now / why me / opportunity
  cost / a `GO` / `NO-GO` / `NEEDS-MORE-RESEARCH` verdict. Market sizing,
  go-to-market, and revenue modeling are **out of scope** here — that turf
  belongs to `domain-teams:planning-team`; this skill delegates, never
  analyzes inline.
- **`user-insights`** — the core research verb. Maps the opportunity space
  (evidence-linked needs as job stories, contexts, today's workarounds) and
  then proposes a value commitment (which needs to serve, desired outcomes,
  appetite — WHAT never HOW). Opportunity-space mapping is knowledge work
  (research/explore, ground truth in the world); the value commitment is a
  value judgment (ground truth with the user) — the agent presents the
  mapped space with evidence and its own recommendation, and the commitment
  is written only after the user ratifies it. Agents never self-commit on
  the user's behalf. Heavyweight research delegates to
  `research-toolkit:deep-deep-research`; small scopes use inline WebSearch.

Professional isolation is contract-level: the two skills share no artifact
and no agent. `business-value`'s agents may not map needs; `user-insights`'s
agents may not render investment verdicts.

## Artifact home

`docs/loom/discovery/<date>-<slug>/`:

```
docs/loom/discovery/<date>-<slug>/
  user-insights.md      # problem framing / opportunity space / value commitment / risks
  evidence.md            # claims-to-evidence registry (evidence outlives any one report)
  research/              # one intermediate report per research question
  business-value.md      # optional — GO / NO-GO / NEEDS-MORE-RESEARCH (when business-value ran)
```

## Boundary lines

- Market sizing, go-to-market, and revenue modeling → `domain-teams:planning-team`.
  `loom-discovery` never analyzes these inline.
- Heavyweight, multi-source research → delegates to
  `research-toolkit:deep-deep-research`. Small scopes may use inline
  WebSearch instead.
- Constitution-writing (north star, product/design/engineering principles) →
  `loom-product-principles`, downstream of this station's output.
- `loom-code` brainstorming keeps its own feature-granularity Axis 4
  research, untouched by this plugin.

## In / Out (v0.1)

**In**: `using-loom-discovery` family entry, `business-value`,
`user-insights`, the discovery artifact validator.

**Out** (deferred): a discovery-critic panel (BACKLOG, v0.2 candidate);
`loom-pipeline` conductor driving discovery as a batch Workflow segment
(v0.1 is interactive-only); a pre-grill / agent-answerer mechanism for
`loom-code` brainstorming briefs; splitting `business-value` and
`user-insights` into two separate plugins (deferred with named flip
conditions — see the brief).

See `docs/loom/specs/2026-07-09-loom-discovery-station.md` (brief) and
`docs/loom/plans/2026-07-10-loom-discovery-station.md` (plan).

## License

MIT.
