---
name: 2026-08-06-same-type-dispatch-batching-cache-experiment
description: Same-type subagent batching within the cache TTL is theory-supported (identical definition prefixes share API-level cache) but locally unproven — a haiku zero-tool experiment showed no detectable duration effect (warm mean 9.9s vs cold 10.6s, within spread); the JP-measured 2x win used ~119k-token real workloads, so the re-test needs realistic mass
status: OPEN
origin: dispatch-efficiency arc research (docs/loom/research/2026-08-06-subagent-latency-and-cache-research.md §4), pre-registered decision rule "no clear win → backlog with data"
start: re-test with sonnet-tier, tool-using workloads ≥100k tokens (e.g. two identical review arms staggered vs batched), duration + /cost cache fields as metrics
---

# Same-type dispatch batching — cache-sharing re-test

Theory (verified against official docs): same-type subagents have
byte-identical system prefixes (base prompt + agent definition), and
the API cache is keyed on content prefix, so near-in-time dispatches
of one type should share the definition's prefill. Subscription
subagents carry a 5-minute TTL, so the batching window is tight.

Local null result (2026-08-06): haiku + zero-tool exercises, cold
10.6s vs warm 8.2/11.0/9.3/10.9s — no effect distinguishable from
noise. Confounds recorded in the research note §4: partial base-prefix
warmth in the "cold" sample; tiny cacheable mass on written exercises.

The single supporting measurement in the wild (Qiita, 30s→14.3s and
119,194→66,884 tokens for parallel same-type dispatches) is
uncorroborated. Do not legislate batching guidance until the start
condition's re-test shows a reproducible win; if it does, the landing
spot is one sentence in dispatch-hygiene-notes §Dispatch-packet
context.
