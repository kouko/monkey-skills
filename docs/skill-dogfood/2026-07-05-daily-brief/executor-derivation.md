# Probe B — executor derivation (informed context)

Context: orchestrator of `daily-brief`, post-0-A Gate. 3 ready platforms:
Slack, Asana, Notion. 0-A Gate already yielded my identity tokens:
- Slack user ID: `U0SLACKSELF`
- Asana GID: `1200000000000123`
- Notion self id: `notion-user-abc123`

Coverage window (from 0-B Intake): today `2026-07-05` + last 48h new items.

## The literal Agent() calls I would issue — ALL IN ONE ASSISTANT MESSAGE

```
Agent({subagent_type: "general-purpose", description: "Slack search",
  prompt: "You are searching Slack for a read-only daily brief. My identity: Slack user ID U0SLACKSELF — do NOT re-derive it. Time window: 2026-07-05 plus new items from the last 48h. FIRST call ToolSearch to load the Slack MCP tool schemas (they are deferred; calling them without a prior ToolSearch fails with InputValidationError). Then search multiple angles: @-mentions of U0SLACKSELF, DMs awaiting my reply, threads I'm in. Return structured markdown: item + canonical permalink deeplink + caveats. Read-only."})

Agent({subagent_type: "general-purpose", description: "Asana search",
  prompt: "You are searching Asana for a read-only daily brief. My identity: Asana GID 1200000000000123 — do NOT re-derive it. Time window: 2026-07-05 plus new items from the last 48h. FIRST call ToolSearch to load the Asana MCP tool schemas (deferred; without a prior ToolSearch they fail with InputValidationError). Then search: tasks assigned to GID 1200000000000123 due soon, tasks awaiting my input. Return structured markdown: item + canonical Asana task deeplink + caveats. Read-only."})

Agent({subagent_type: "general-purpose", description: "Notion search",
  prompt: "You are searching Notion for a read-only daily brief. My identity: Notion self id notion-user-abc123 — do NOT re-derive it. Time window: 2026-07-05 plus new items from the last 48h. FIRST call ToolSearch to load the Notion MCP tool schemas (deferred; without a prior ToolSearch they fail with InputValidationError). Then search: pages mentioning me, recently edited pages I own. Return structured markdown: item + canonical Notion page deeplink + caveats. Read-only."})
```

## Citations — which file/line told me each requirement

(a) **Issue all in ONE assistant message**
- `references/claude-code-tools.md:10-15` — "all issued in the **same
  assistant message** so Claude Code runs them concurrently — Claude Code
  only parallelizes `Agent` calls that appear together in one message;
  sequential calls across separate messages block on each other."
- Reinforced by `SKILL.md:59-60` heading "平行 fan-out(每平台一個
  sub-agent,一次發出)" + "一次性平行發出全部就緒平台的 sub-agent".

(b) **Do NOT add `name:`**
- `references/claude-code-tools.md:23-26` — "**Do not add `name:`** to any
  of these calls … naming turns a one-shot blocking dispatch into a
  persistent mailbox-semantics teammate whose output is never delivered as
  this turn's tool result." (cross-refs
  `loom-code/…/environment-gotchas.md` §A1)

(c) **Embed the pre-fetched identity token directly in each prompt**
- `references/claude-code-tools.md:28-31` — "**Pass the identity token in
  the prompt**, not as a separate lookup — per
  `platform-search-playbook.md` §2, the subagent should never need to
  re-derive Slack user ID / Asana GID / Notion self id / email / GitHub
  login itself."
- Reinforced by `SKILL.md:60` — "把 0-A Gate 已取得的本人身份(Slack user
  ID、Asana GID、Notion self id…)直接寫進每個 agent 的 prompt".

(d) **Each subagent must ToolSearch before calling its platform's MCP tools**
- `references/claude-code-tools.md:32-34` — "**Each subagent must
  `ToolSearch` its own platform's MCP tools before calling them** — these
  tools are deferred; calling them without a prior `ToolSearch` fails with
  `InputValidationError`."
- Reinforced by `SKILL.md:60` — "先用 ToolSearch 載入該平台 MCP 工具的
  schema(這些工具是 deferred,不先載直接呼叫會 InputValidationError)"
  and anti-pattern `SKILL.md:88`.
