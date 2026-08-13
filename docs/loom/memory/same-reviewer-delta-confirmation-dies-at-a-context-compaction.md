---
name: same-reviewer-delta-confirmation-dies-at-a-context-compaction
description: The repo's standard fix-resolution mechanism — the SAME reviewer confirming a delta via SendMessage rather than a fresh whole-artifact round — is addressable only through handles held in the orchestrator's live context, so a context compaction silently destroys it for every already-completed reviewer; the loss surfaces as "I cannot remember whom to ask", never as an error, and the tempting repairs (a fresh reviewer, or flipping the ledger anyway) each discard exactly what the mechanism was protecting
type: gotcha
origin: brief-item-addressability arc (2026-08-13) — after a compaction, T7's and T8's reviewers were unreachable; ListAgents listed only the one still-running subagent, and no completed reviewer could be resumed
---

Delta confirmation is this repo's standard resolution for a gating
verdict: fix once, then have **the same reviewer** confirm the delta via
`SendMessage`, never a fresh whole-corpus round. Ten-plus live runs made it
standard; `requesting-docs-review`'s Directive 2 encodes it.

It has an unstated lifetime. The reviewer is addressable only by a handle —
its `agentId`, or a `name:` if one was assigned — and that handle lives in
the orchestrator's conversation context. **A context compaction drops it.**
`ListAgents` lists live subagents and peer sessions; it does not enumerate
completed subagents, so after a compaction there is no way to rediscover
whom to ask.

**Why it is dangerous rather than merely inconvenient.** Nothing fails. No
tool errors, no gate blocks. The mechanism's absence presents as the
orchestrator simply not recalling a handle — which reads like a memory lapse
about a detail, not like the loss of a contract. Both repairs that suggest
themselves at that moment are wrong:

- **dispatch a fresh reviewer** — this is precisely the fresh whole-artifact
  round the delta contract exists to prevent, and it re-samples the whole
  corpus, producing new unrelated findings and a new fix round;
- **flip the ledger as though confirmed** — this launders an unconfirmed fix
  into the record, and the fix rounds most needing confirmation are the ones
  whose findings were judgment-bearing.

**How to apply.** Treat reviewer handles as *perishable state*, not as
recall:

1. **Dispatch any reviewer whose verdict may need a fix round with a stable
   `name:`, and record THAT name in the plan** — never the `agentId`. An
   agentId is session-scoped and the harness forbids surfacing it, so writing
   one into a committed artifact is both prohibited and useless: it resolves
   nowhere in a later session. A `name:` is a plain string the dispatcher
   chooses, it survives the agent's completion (a `SendMessage` to the name
   resumes it from its transcript), and it can be written down anywhere.
   This composes with the standing rule "do not add `name:` unless you will
   drive that agent via `SendMessage`" rather than breaking it — delta
   confirmation IS driving via `SendMessage`, so a reviewer that may need
   confirming is exactly the sanctioned case for naming. (Corollary of that
   same rule: a named agent's plain-text reply is not delivered on its own,
   so name reviewers you intend to confirm — not one-shot arms whose verdict
   you simply receive.)
2. Prefer closing the fix→confirm cycle **before** starting unrelated work,
   while the handle is certainly live. A confirmation deferred across other
   tasks is a confirmation gambling on context length.
3. When the handle IS already lost, the honest path is neither repair above:
   let the fix ride into **whole-branch review** — which reads the whole diff
   anyway — and **state in the report that these fixes were never
   delta-confirmed and why**. The disclosure is the load-bearing part; a
   silently unconfirmed fix and a disclosed one differ entirely to whoever
   reads the close-out.

**Contradiction check:** does not contradict
[[agent-contract-edits-do-not-reach-this-sessions-subagents]] — that entry is
about edits to an agent's *contract* not propagating to already-running
subagents; this one is about *addressability of finished ones* not surviving
the orchestrator's own context. Both are session-boundary facts and neither
implies the other. Related:
[[contradicting-reviewer-verdicts-localize-the-defect-to-the-spec]] — when
two reviewers disagree, that disagreement is also context-bound evidence and
wants recording in the artifact for the same reason.
