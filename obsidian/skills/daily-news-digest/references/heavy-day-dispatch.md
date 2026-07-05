# Heavy-day dispatch — subagent execution model for STEP 6/7

Load this file only when STEP 6 routes to the heavy-day path
(`counts.candidates` ≳ 40, OR any single cluster ≳ 6 notes). Light
days never need it — the main agent reads and synthesizes directly.

## Execution model

Reading every clustered note (full bodies, often with long transcripts)
into the main context is the real context cost, so on a heavy day:

- **Dispatch one subagent per story-cluster, in parallel** (all fanned
  out in one round — they're independent; concrete per-host call shape:
  `claude-code-tools.md` / `codex-tools.md` in this folder). Dispatch
  them **blocking — never non-blocking/background**: STEP 8 assembly
  can't start until every subagent returns, so background dispatch buys
  no parallelism and only creates end-of-turn stop-hook contention (real
  failure 2026-07-02: eight consecutive blocked turns after the digest
  was already written, on Claude Code — see `claude-code-tools.md` for
  the host-specific mechanism). If a scheduled wakeup/cron was set to
  wait on results, cancel it as soon as they are collected.
- Give each subagent the cluster's note **paths** + the story angle; it
  reads the full notes and returns the **structured story object**
  (contract below) — the main agent never loads raw transcripts, only
  finished stories.
- The knowledge tier (STEP 7) can be one more subagent, returning each
  sub-category's promoted summaries + CoT node content.
- The **main agent assembles, renders every CoT via
  `$SKILL_DIR/scripts/cot_mermaid.py`, writes the file, and runs the
  digest gate (`digest_check.py`)** — rendering and verification stay
  central for consistency. The main agent owns dedup and the day-level overview
  diagram.

## Subagent return contract

One per story, so the main agent can assemble uniformly — return
JSON-ish:

```
{ heading, category(🌍/📈/🤖/🚀…), tldr,
  cot: {type:"chain", nodes:[{title, bullets:[…]}, …]},   // → cot_mermaid.py
  narrative: ["<para 1>", "<para 2>"],       // inline links as [[stem|short label]]
  table?: "<markdown table or null>",        // ? = optional field
  progression?: { title, milestones:[{date, text}], note },  // Event Arc, evolving only
  sources: [{stem, label}] }                 // for inline links + Source Index
```

The CoT `nodes` carry only content; `cot_mermaid.py` applies the fixed
colours/style centrally.
