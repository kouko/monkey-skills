# Hook: Multi-Perspective Seeding

Deep-mode pre-writing hook — diversify research framing before
Phase 1 collection to counter single-frame bias.

Inspired by Stanford STORM (Shao et al. 2024) — perspective-aware
question generation. Implements the "perspective mining" step only;
omits STORM's simulated expert-writer dialogue.

## When This Applies

- Mode: **deep only** (quick mode skips this hook to preserve
  ~15k token budget)
- Phase: invoked at the **end of Phase 0** (after mode + budget
  setup, before scoping in Phase 1)
- Workflows: applies to any worker-dispatching workflow when
  `mode=deep` (research / academic-research / market-analysis /
  competitive-analysis / stack-evaluation)

## Rule

Worker MUST list **3 distinct stakeholder or contrarian
perspectives** as sub-question seeds before entering Phase 1.

Acceptable dimensions (pick 3 with material differences):
- **user / customer / operator** — who consumes the answer
- **vendor / producer / incumbent** — who supplies or defends
- **regulator / policy / compliance** — what constrains
- **academic / research** — what evidence base says
- **contrarian / skeptic / dissenter** — what the consensus misses

For each perspective: 1 sub-question that this lens uniquely
surfaces. Sub-questions feed Phase 1 source strategy.

## Failure Mode

If the topic is too narrow for 3 distinct perspectives (e.g., a
purely factual lookup masquerading as deep research), worker MUST
note `scope too narrow for multi-perspective` in the artifact and
proceed as single-frame research. Do NOT pad with cosmetic
perspectives.

## Example

Topic: "Should we adopt framework X for our backend?"

Perspectives:
- **operator (developer adopting)**: What's the on-ramp cost for
  our team's current skill set?
- **vendor (X maintainers)**: Is X's roadmap funded and aligned
  with our use case?
- **contrarian**: What teams have tried X and reverted? Why?

Each sub-question drives independent Phase 1 source collection.
