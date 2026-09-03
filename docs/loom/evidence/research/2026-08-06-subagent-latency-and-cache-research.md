# Research: subagent latency, dispatch-packet context, and cache behavior

Date: 2026-08-06
Arc: dispatch-efficiency trio (loom-code 0.64.0)
Method: cross-project transcript mining + EN/JP industry survey + a
hypothesis-verification round against official docs + one local
experiment. Full source URLs inline; the raw scan tables and the
scanning script are committed as the appendix file
`2026-08-06-subagent-timing-scan-raw.md` — the durable record.

## 1. Cross-project latency scan (local measurement)

Scanned 386 transcript files under ~/.claude/projects/ (spanning 42
project directories, 13 of which contained ≥1 completion record) —
10,054 subagent-completion records, 0 parse failures (script: see
`2026-08-06-subagent-timing-scan-raw.md` §Regeneration appendix). The scan
globbed `~/.claude/projects/*/*.jsonl` — each project's top-level
session transcripts (source: `scan_subagent_timing.py:27,38`, quoted
in the appendix). 386 files matched the glob, 93 contained ≥1
completion record; the tree holds ~6,403 `.jsonl` in total including
nested per-task transcript files the glob deliberately excludes.

Headline: duration scales near-linearly with tool_uses at a
**~10-11s-per-tool-call floor** (buckets ≥6 calls; the 1-5 bucket
reads 15.1s/call from fixed-overhead dominance). Median durations by
project sit 60-500s; monkey-skills is mid-pack (10.0s/call, median
114.8s, n=5,287). Outlier: an icon-generation project at 18.9s/call ×
median 27 calls (external-tool latency, not orchestration).

| tool_uses bucket | n | median duration | sec/call |
|---|---|---|---|
| 0 | 71 | 12.5s | — |
| 1-5 | 1,995 | 41.2s | 15.1 |
| 6-15 | 3,886 | 107.2s | 10.0 |
| 16-30 | 2,900 | 221.1s | 10.3 |
| >30 | 1,202 | 472.5s | 11.2 |

Implication: the universal lever is reducing per-agent tool
round-trips — which the 0.64.0 §Dispatch-packet context rules target.

## 2. Industry survey (EN + JP)

- Anthropic multi-agent research system: lead agent gives each
  subagent "an objective, an output format, guidance on the tools and
  sources to use, and clear task boundaries"; vague packets measured
  to cause duplicated work; parallelism cut research time up to 90% at
  ~15x tokens. https://www.anthropic.com/engineering/multi-agent-research-system
- Cognition, "Don't Build Multi-Agents": full traces for agents whose
  outputs must compose ("actions carry implicit decisions").
  https://cognition.com/blog/dont-build-multi-agents
- Manus context engineering: "KV-cache hit rate is the single most
  important metric for a production-stage AI agent"; stable prefixes,
  append-only context. https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- LangGraph handoffs: warns against full-history handoffs; pass
  curated summaries. https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs
- Claude Code subagents: own context window; dispatch prompt is the
  only parent→child channel; return summaries.
  https://code.claude.com/docs/en/sub-agents
- JP practice clusters at "paths + error messages + rationale written
  into the prompt" (minimal-sufficient), file-based hand-off via plan
  files; one measured parallel-dispatch cache-sharing win (30s→14.3s,
  119,194→66,884 tokens) — single source, uncorroborated.
  https://qiita.com/tamashiro_nobuyuki/items/ff9004b66b7761c4d34c
  (survey also: https://blog.serverworks.co.jp/claude-code-subagents-guide,
  https://tech.algomatic.jp/entry/2025/10/15/172110,
  https://unimon.co.th/ja/blog/agentic-latency-budgeting)

## 3. Caching-theory verification (C1-C7)

| Claim | Verdict | Anchor |
|---|---|---|
| C1 API prefix caching, breakpoints, TTLs | CONFIRMED (1h-TTL write is 2x, not 1.25x) | Anthropic API docs |
| C2 Claude Code auto-caches subagent calls | CONFIRMED | https://code.claude.com/docs/en/prompt-caching |
| C3 same-type agents share definition prefix | PARTIAL — agent .md = its system prompt; identical prefixes share cache; assembly order inferred, not documented | sub-agents + prompt-caching docs |
| C4 skills enter the message stream; cached within a conversation, never inherited by siblings | CONFIRMED both halves | prompt-caching doc |
| C5 compaction invalidates the whole cache | PARTIAL — conversation layer only; system layer + reloaded context still cache | prompt-caching doc |
| C6 OpenAI auto prompt caching; Codex subagents | PARTIAL — caching confirmed (90% discount current-gen; explicit breakpoints new); Codex collab community-documented only | developers.openai.com prompt-caching; openai.com/index/unrolling-the-codex-agent-loop |
| C7 same-type batching saves ~2x | UNVERIFIABLE — single JP source; one opposing-direction datapoint (fan-out overhead 4.2x, different question) | see §4 |

Also measured elsewhere: subscription subagents get 5-min TTL (1h is
parent-only); a 76-min idle gap cost $0.49→$3.65 (7.5x) with hit rate
97.4%→64.5% (https://zenn.dev/studist/articles/claude-code-prompt-cache-cost-analysis).

## 4. Lever-② experiment (same-type batch cache sharing) — null result

Protocol: loom-code:implementer + haiku + zero-tool written exercises;
one cold dispatch (>5 min since last same-type), then three parallel
warm, then one sequential warm. Durations from task notifications
(cache_read fields not observable at this surface — duration is the
decision variable).

| sample | condition | duration |
|---|---|---|
| C1 | cold | 10.6s |
| W1-W3 | warm, parallel | 8.2s / 11.0s / 9.3s |
| W4 | warm, sequential | 10.9s |

Warm mean 9.9s vs cold 10.6s — within intra-group spread. **No
detectable effect at this scale.** Named confounds: (a) C1 was not
globally cold — other agent types ran within TTL, so the shared base
prefix was likely warm and only the implementer-definition segment
(~1-2s of haiku prefill) was truly cold; (b) the JP 2x claim was
measured on ~119k-token real workloads; our 36k-token written
exercises have little cacheable mass. Disposition per the
pre-registered rule: NOT legislated; parked as backlog entry
2026-08-06-same-type-dispatch-batching-cache-experiment with a
re-test start condition.

## 5. What shipped from this research

loom-code 0.64.0: §Dispatch-packet context (string anchors, inline
provenance, locate-arm threshold + file-map valve, reviewer
independence); implementer rule 13 (scoped inner-loop tests); plan-
format lane-usage guidance. Lever ② parked. Report-length discipline
(reviewer evidence-to-file) noted as a future-arc candidate, not
built here.
