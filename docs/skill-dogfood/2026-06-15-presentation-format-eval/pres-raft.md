# PRESENTATION EVAL — seed: Raft (DESCRIPTIVE / explainer — CONTROL, tests over-structuring harm)

Question: How does the Raft consensus algorithm achieve leader election and log replication?
Three arms, SAME claims (see seed-7-raft.md). FLAT / FREE / HINT. This is the control: flat may be fine; an explicit structure HINT should NOT hurt a descriptive question.

---
## ARM FLAT (verbatim)
# How does the Raft consensus algorithm achieve leader election and log replication?
## Summary
Raft partitions time into monotonically increasing terms (logical clocks) so stale leaders/messages are detected and rejected. Leader election: a follower's randomized timeout (150–300ms) expires → increment term, become candidate, self-vote, broadcast parallel RequestVote; a candidate with a strict majority wins and asserts authority via periodic empty AppendEntries heartbeats. Log replication is leader-driven: append locally, fan out AppendEntries, commit once a majority acks, then apply + propagate commit index. Two invariants — Log Matching and Leader Completeness — guarantee committed entries survive leader changes.
## Findings
- **Terms act as logical clocks, detect stale leaders** *(high)*
- **Election: timeout→increment→self-vote→parallel RequestVote→win on majority** *(high)*
- **Randomized timeouts (150–300ms) prevent simultaneous candidacies, resolve split votes** *(high)*
- **One vote per term FCFS; refuse less-up-to-date candidate** *(high)*
- **Heartbeats (empty AppendEntries) suppress new elections** *(high)*
- **Replication: append→fan out→commit on majority→apply+notify commit index** *(high)*
- **Log Matching Property (index+term ⇒ identical prefix; inductive consistency check)** *(high)*
- **Follower repair: find last match, delete suffix, ship missing** *(high)*
- **Leader Completeness: leader in T holds all entries committed <T; enforced at vote-grant** *(high)*
- **etcd ~200ms election on LAN** *(medium)*
## Caveats
Primary claims from Raft paper (2014), stable. etcd latency deployment-specific, not a protocol guarantee. Crash-fail not Byzantine. Membership changes + log compaction not covered.
## Open Questions
- Stale-leader window after partition heals?
- Pre-vote/lease extensions vs randomized timeouts?
- "More up-to-date" vs recent-uncommitted entry?
- Tooling for large follower divergence?

---
## ARM FREE (structure summary — verbatim key elements)
- Confidence header (all 5-0 primary; one secondary latency marked).
- **Sectioned narrative**: "The Core Abstraction: Terms as Logical Clocks" → "Leader Election" (Trigger/Candidacy, Winning, Liveness, Staying in Power) → "Log Replication" with an **ASCII flow diagram** (Client write → Leader appends → AppendEntries → majority → COMMITTED → apply/notify) → "Log Matching Property" → "Follower Repair" → "Leader Completeness Guarantee".
- **An "Operational Reality" markdown TABLE** (Metric | Value | Confidence).
- "What This Does NOT Cover" list.
Spontaneously sectioned-explainer with an ASCII diagram + one small table. Reads as a teaching doc.

---
## ARM HINT (structure summary — verbatim key elements)
- Explicit sectioned explainer (as directed): "Key Terms" → "Leader Election" (Triggering / Winning / Resolving split votes / Maintaining authority) → "Log Replication" (Appending+fanout / Committing / Follower repair) → "Safety Properties" (Log Matching / Leader Completeness) → "Operational Notes".
- Logical/causal order a learner follows; confidence carried in prose; latency marked medium.
- No table (prose-only), clean and complete.
Both FREE and HINT are sectioned explainers; FLAT's findings-list is serviceable but less pedagogically ordered. KEY control check: does HINT (or FREE) OVER-structure a descriptive question (e.g. force an inappropriate table/matrix)? Assess whether flat is actually fine here and whether structure adds or just reorganizes.
