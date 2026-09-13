# Capture-intent bounded behavioral probe

Date: 2026-09-12
Candidate: working tree after `0bef55bde`
Executor: Claude Code 2.1.268, requested Opus/high
Execution boundary: sandbox-outside runner, `/tmp` working directory, file tools disabled
Cost: unknown — subscription execution exposes no per-run amount

## Scope

This is a bounded concept probe, not a full `dogfood-skill-testing` PASS. The
full protocol's activation corpus, distractor routing, and repeated blind
auditors were intentionally not run because this change authorizes two
representative content-boundary cases, not a new multi-agent evaluation loop.

The packet contained only the candidate rules, one complete engineering case,
one product case with a planted notification-channel ambiguity, and the audit
criteria. The packet was inspected and nothing credential-shaped or
personal-data-shaped was included; that is not a safety verdict. Global Claude
Code initialization could not be enumerated in advance.

## Expected outcomes

- Engineering: draft immediately, preserve every supplied constraint, and add
  no spec, plan, product behaviour, identifier, or checking mechanism.
- Product: ask only whether mute covers email, in-app, or both; do not invent
  Unmute, UI placement, persistence, errors, or state transitions.

## Observed outcomes

- Engineering: `DRAFT`. Claude preserved the supplied outcome and constraints,
  omitted ritual questions, and delegated wording and file choices downstream.
- Product: `ASK`. Claude asked exactly: “When a project is muted, which
  notifications stop — email, in-app, or both?” It explicitly rejected Unmute,
  placement, persistence, failure reactions, and a state machine.
- Neither simulation introduced a new identifier or checking mechanism.

## Independent findings and disposition

1. `RESHAPE` — clarify that question quotas apply only to intake, not existing
   decision points. Accepted and covered by focused tests.
2. Clarify Acceptance versus evidence procedure. Rejected: capture-intent owns
   externally decidable outcomes; evidence sources and procedures belong to
   later verification.
3. State that a material unresolved fork must be asked before confirmation.
   Accepted and covered by focused tests.
4. Define `reopen` as moving the item to Open questions and stopping
   confirmation. Accepted and covered by focused tests.
5. Keep an empty Value case heading for engineering intents. Rejected: the
   shared contract deliberately declares Value case optional.

## Raw verdict excerpt

> Both simulations came out correct against the stated criteria: Case E
> drafted with no ritual question, preserved every constraint, and added no
> product, spec, or plan detail; Case P asked only the channel question and
> promoted none of the unauthorized behaviour; no new identifier or checking
> mechanism was introduced in either.

Claude's overall verdict was `RESHAPE`, because three wording points required
clarification. Those three accepted changes were applied before integration
verification. The result supports the concept on these two cases only; it does
not prove cross-model or broad-domain stability.
