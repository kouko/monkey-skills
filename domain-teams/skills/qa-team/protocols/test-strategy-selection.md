# Test Strategy Selection Protocol

Choose a **test strategy framework** — the high-level heuristic that guides
how much testing happens at each level of the system. The wrong framework
produces test suites that are slow, brittle, or gap-ridden.

Invoked during test-plan-writing Phase 2 (Test Type/Level Selection) or
standalone when a team needs to document strategy rationale.

## When to Use

- Authoring a new TEST-PLAN.md and needing to pick a strategy
- Auditing an existing test suite that has grown organically without a stated strategy
- When a team disagrees about the right ratio of unit/integration/E2E tests
- When migrating from one framework to another (e.g., frontend adopting Trophy)

## When NOT to Use

- The organization mandates a specific framework by policy — skip selection,
  just document the mandated choice
- Single-file bug fixes where strategy is not in scope

## Available Frameworks

| Framework | Best for | Primary source |
|-----------|---------|----------------|
| **Practical Test Pyramid** (Fowler / Vocke) | Backend, systems, API services | [martinfowler.com/articles/practical-test-pyramid.html](https://martinfowler.com/articles/practical-test-pyramid.html) |
| **Testing Trophy** (Kent C. Dodds, 2018) | Frontend, JavaScript/TypeScript applications | [kentcdodds.com/blog/the-testing-trophy-and-testing-classifications](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications) |
| **Small/Medium/Large Sizes** (Google Testing Grouplet, 2006) | Large monorepos, organizations that mechanically enforce test constraints | [testing.googleblog.com/2010/12/test-sizes.html](https://testing.googleblog.com/2010/12/test-sizes.html) |

## Phase 1: Project Classification

Answer these questions with evidence from the codebase and project context:

1. **What is the dominant layer being tested?**
   - Backend / server-side business logic → lean Pyramid
   - Frontend UI / user interactions → lean Trophy
   - Both equally → consider which has more risk concentration
2. **What is the team's testing infrastructure?**
   - Can enforce test constraints mechanically (sandbox, annotations, resource limits)? → Sizes viable
   - Only advisory enforcement? → Pyramid or Trophy
3. **What is the language/ecosystem?**
   - JavaScript/TypeScript frontend with React/Vue/Svelte → Trophy (Dodds' original context)
   - Statically-typed backend (Go, Java, Rust, C#) → Pyramid (many unit tests cheap to write)
   - Polyglot monorepo at Google scale → Sizes
4. **How expensive are the test tiers?**
   - Unit tests cheap and fast → Pyramid-shaped distribution possible
   - Unit tests require heavy mocking (brittle) → Trophy (integration-heavy) or RITE
   - Integration environment cheap → move weight toward integration

## Phase 2: Framework Selection

Apply the decision tree:

```
Is the system primarily backend / API / service-oriented?
├── YES → Practical Test Pyramid
│         (Fowler / Vocke: different granularity, fewer high-level tests)
└── NO
    ├── Is the system primarily frontend JavaScript/TypeScript?
    │   └── YES → Testing Trophy
    │             (Dodds: static → unit → integration (biggest) → E2E)
    └── NO
        └── Is the system a Google-scale monorepo with mechanical test enforcement?
            ├── YES → Small/Medium/Large Sizes
            │         (Google: constraints enforced by infrastructure)
            └── NO → Default to Practical Test Pyramid as the most broadly applicable heuristic
```

## Phase 3: Document Rationale

In TEST-PLAN.md §5 (Test strategy / approach), record:

```
## Strategy Framework

**Chosen framework**: {Practical Test Pyramid | Testing Trophy | Small/Medium/Large Sizes}
**Primary source**: {URL}
**Rationale**: {1-2 sentences explaining why this framework fits the project}

**Target distribution**:
- {Framework-specific distribution, e.g.:
   Pyramid: ~70% unit / ~20% integration / ~10% E2E
   Trophy: ~10% static / ~20% unit / ~50% integration / ~20% E2E
   Sizes: constraint-based, not percentage-based}

**Known trade-offs**:
- {What this framework is weak at; what cases will still fall through}
```

## Rules

- **Cite the primary source** — every TEST-PLAN.md that uses a framework must link
  to the original publication. This makes the decision auditable and recoverable.
- **One framework per plan** — don't mix Pyramid and Trophy in the same TEST-PLAN.md
  without explicit justification; split into sub-plans if genuinely necessary.
- **Distribution is advisory, not absolute** — percentages are starting points.
  Deviate with rationale, not silently.
- **Do not invent new frameworks** — if none of the three fit, document the
  misfit explicitly and pick the closest. Inventing "your team's test shape"
  without peer review loses the benefit of industry consensus.
