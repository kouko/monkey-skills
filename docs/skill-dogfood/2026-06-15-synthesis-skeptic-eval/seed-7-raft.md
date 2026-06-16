# SEED 7 — Raft consensus (DESCRIPTIVE, clean control / precision test)

## QUESTION
How does the Raft consensus algorithm achieve leader election and log replication?

## CONFIRMED CLAIMS BLOCK
### [0] Raft divides time into terms; terms act as logical clocks. (5-0, primary raft.pdf, high)
### [1] Election: increment term, become candidate, vote self, send RequestVote in parallel. (5-0, primary, high)
### [2] Randomized election timeouts (150–300 ms) resolve split votes. (5-0, primary, high)
### [3] Candidate wins on majority of full cluster; one vote per term, first-come-first-served. (5-0, primary, high)
### [4] Leader sends empty AppendEntries as heartbeats to suppress new elections. (5-0, primary, high)
### [5] Replicate: append locally, fan out AppendEntries; committed once on a majority. (5-0, primary, high)
### [6] Log Matching Property: same index+term ⇒ logs identical up through that index. (5-0, primary, high)
### [7] Leader Completeness: leader in term T holds all entries committed in terms <T. (5-0, primary, high)
### [8] Follower repair: leader finds last match, overwrites subsequent entries. (5-0, primary, high)
### [9] Committed = replicated to majority; leader applies + notifies via AppendEntries. (5-0, primary, high)
### [10] etcd: election typically <1s (≈200ms) on LAN, timeout-dependent. (4-1, secondary, medium)

(Full quotes/sources in the dispatch; this is a CLEAN seed — claims mutually consistent, mostly 5-0 primary, no planted tension.)

## ARM A — SINGLE-PASS SYNTHESIS
SUMMARY: Raft achieves consensus through two tightly coupled mechanisms. Leader election uses randomized timeouts and term-based logical clocks to elect a single authoritative leader per term: when a follower times out, it increments its term, becomes a candidate, and wins by collecting votes from a majority of the cluster, with each server casting at most one vote per term first-come-first-served. Log replication is driven exclusively by the leader, which appends client commands locally, fans out AppendEntries RPCs concurrently, and marks an entry committed once a majority acknowledges it, after which followers apply it. Two invariants — Log Matching and Leader Completeness — guarantee committed entries are never lost across leader changes. In practice on a LAN, the full election-to-commit cycle completes in well under one second.

FINDINGS:
- [high] Terms partition time, act as logical clocks to detect stale leaders/messages. | §5.1, 5-0.
- [high] Election triggered by timeout: increment term, candidate, self-vote, parallel RequestVote; win on strict majority; one vote/term FCFS; randomized timeouts (150–300ms) prevent simultaneous candidacies + resolve split votes. | §5.2, 5-0 all sub-claims.
- [high] Leader asserts authority via periodic empty AppendEntries heartbeats, suppressing new elections while live. | §5.2, 5-0.
- [high] Replication: append locally, fan out AppendEntries; committed + safe to apply once majority acks; leader applies + notifies commit index via subsequent AppendEntries. | §5.3, 5-0.
- [high] Log Matching: same index+term ⇒ identical up to that index; enforced by AppendEntries consistency check (inductive). | §5.3, 5-0.
- [high] Follower repair: leader finds last match, deletes subsequent, ships missing → follower becomes prefix-match. | §5.3, 5-0.
- [high] Leader Completeness: leader in T holds all entries committed in <T; enforced at vote-grant (refuse less-up-to-date candidate). | §5.4.1, 5-0.
- [medium] Operational latency: etcd ~200ms election on stable LAN w/ defaults; tuning/network-sensitive, not a protocol guarantee. | secondary, 4-1.

CAVEATS: All primary claims from the original Raft paper (2014); unchanged at this abstraction so currency not a concern. etcd latency is deployment-specific, not a protocol bound. Correctness assumes crash-fail (not Byzantine). Membership changes (joint consensus) + log compaction (snapshots) are extensions not covered here.

OPEN QUESTIONS:
- How does Raft handle the stale-leader window after a partition heals, and worst-case stale-read duration?
- Are there topologies where pre-vote/lease-based extensions (etcd) materially improve availability over randomized timeouts?
- How does "up-to-date" (last-log-term then index) interact with a recent-but-uncommitted entry from a failed leader?
- What tooling exists to inspect/recover a follower with large divergence backlog?
