# Codex subagent-dispatch portability survey — monkey-skills marketplace

**Date:** 2026-07-05
**Trigger:** loom-code (PR #496) and loom-interface-design/loom-spec (PR #497) both had gaps between their subagent-dispatch instructions and Codex CLI's real dispatch primitive (`multi_agent`/`spawn_agent`/`wait_agent`/`close_agent`). This survey checks whether the other 22 marketplace plugins have the same class of gap.
**Method:** all 26 plugins ship a `.codex-plugin/plugin.json` (i.e., all claim dual-host packaging). Grepped every plugin's `skills/` tree for subagent-dispatch keywords (`Agent(`, `subagent`, `dispatch`, `fan-out`, `panel`, `fresh context`), then dispatched one read-only investigation subagent per plugin to classify each real hit.

## Classification key

- **(A) LITERAL-CLAUDE-CODE** — hardcodes `Agent({subagent_type: ..., prompt: ...})` (or equivalent Claude-Code-specific tool syntax) directly in a shared skill body. This is loom-code's *original* problem (fixed in #496): a Codex reader hits literal syntax it can't execute.
- **(B) HOST-NEUTRAL-PROSE** — the dispatch instruction is already written in generic language ("dispatch a fresh-context subagent...") but the plugin has **zero** per-host reference file (`claude-code-tools.md`/`codex-tools.md`) explaining what that resolves to concretely on each host. This is loom-interface-design/loom-spec's problem (fixed in #497).
- **(C) NO-GAP** — doesn't operationally dispatch subagents, or the "dispatch" hits are a different concept entirely (skill-to-skill routing, SQL join fan-out, OOP method dispatch, etc.).

## Findings by plugin

| Plugin | Class | Where | Note |
|---|---|---|---|
| **dev-workflow** | 🔴 (A) | `distill-sessions/SKILL.md:194-196,343-355` + 3 `agents/*.md` prompt files | Most severe hit: literal `Agent({subagent_type: "general-purpose", model: "sonnet", ...})`, plus a Claude-Code-runtime-specific quirk baked in ("`model: "sonnet"` alias... passing the literal model name will fail enum validation"). 5 sites total. |
| **obsidian** | 🔴 (A) | `daily-news-digest/references/heavy-day-dispatch.md:12-14` + `SKILL.md:224-229` | Literal "`Agent`/`Task` calls" + `run_in_background: true` named directly. Obsidian's other wiki skills (wiki-ingest, wiki-cross-linker, etc.) are all single-agent, no gap there. |
| **domain-teams** | 🟡 (B) | `skill-team/standards/agent-interface.md:31` (Worker/Evaluator launch contract) — echoed in **9 of 9** team SKILL.md files | The most foundational instance: this is the canonical worker/evaluator pattern loom-code's own SDD was modeled after. Also: `copywriting-team/protocols/copy-ideation-advanced.md:86` (standalone fan-out) and `research-team/protocols/hook-parallel-fanout.md:36-138` (best-hedged in the plugin — already does capability-detection for "no Agent/Task tool," but the detection check itself hardcodes Claude-Code tool names). |
| **research-toolkit** | 🟡 (B) | All 4 skills: `deep-read`, `fact-check`, `deep-deep-research`, `cite-check` | Already the best-written prose in the survey — explicitly names "Claude Code, Codex, Cursor" and explicitly forbids hardcoding the Workflow tool — but still never resolves to per-host mechanics. |
| **translation-toolkit** | 🟡 (B) | Shared blind-retranslation dispatch step, duplicated verbatim across `translation-doc`/`translation-creative`/`translation-novel`/`translation-audit`/`translation-i18n` | Broadest reach — one shared instruction, 5 skills inherit the gap. |
| **dbt-wiki** | 🟡 (B) | `init/SKILL.md:795-911` (Phase B parallel orchestration) | `redistill/SKILL.md:125-127` explicitly inherits the same gap by reference. |
| **copywriting-toolkit** | 🟡 (B) | `copywriting-ideation/protocols/copy-ideation-parallel.md:46`, `copy-ideation-advanced.md:86`, `SKILL.md:98,140,217` | `copy-ideation-parallel.md` cross-references `loom-code:dispatching-parallel-agents` (now host-aware post-#496) as an **undeclared** external dependency — dangles if loom-code isn't installed. |
| **briefing-toolkit** | 🟡 (B) | `daily-brief/SKILL.md:59-60` (per-platform parallel fan-out) | Side finding: `.codex-plugin/plugin.json`'s own `description` says *"Claude Code CLI only"* — the manifest self-contradicts by existing at all if that's true. Worth a look independent of the dispatch question. |
| **investing-toolkit** | 🟡 (B), borderline A/B | `report-equity-memo/SKILL.md:106-126` (peer-discovery) | Names `"general-purpose"` — a real Claude-Code built-in agent-type name — but no literal `Agent(...)` call syntax, so classed (B) not (A). |
| **deconstruct-toolkit** | 🟢 (C) | — | "Dispatch" = routing to a sibling Skill, not subagent spawning. No gap. |
| **legal-toolkit** | 🟢 (C) | — | The one subagent mention is explicitly a **deferred v0.3.4+ feature**; current version runs in the main session. No live gap. |
| **loom-pipeline** | 🟢 (C) | — | Correctly self-gates: *"Codex hosts: N/A by definition... has no fallback path... report `loom-pipeline: N/A` and stop."* This is the model example of how to handle a genuinely Claude-Code-only primitive (the `Workflow` tool). |
| **loom-product-principles** | 🟢 (C) | — | Doesn't dispatch subagents at all — single in-context authoring skill. |
| **loom-code, loom-interface-design, loom-spec** | ✅ Fixed | — | PR #496 + #497, this session. |
| Not surveyed (no plugin.json Codex-compat claim to test against, or out of scope) | — | — | ascii-graph-toolkit, four-dx-coach, gws-toolkit, philosophers-toolkit, repo-wiki, salesforce-toolkit, skill-dev-toolkit, systems-thinking-toolkit, tsundoku — all ship `.codex-plugin/plugin.json` but returned zero dispatch-keyword hits in the initial scan, so not individually deep-dived. |

## Summary

- **2 plugins have the more severe (A) gap** (dev-workflow, obsidian) — literal Claude-Code tool syntax that simply cannot execute on Codex as written.
- **7 plugins have the (B) gap** (domain-teams, research-toolkit, translation-toolkit, dbt-wiki, copywriting-toolkit, briefing-toolkit, investing-toolkit) — prose is fine or fine-ish, concrete per-host resolution is missing entirely (zero reference files exist in any of them).
- **domain-teams is the highest-leverage single fix**: its Worker/Evaluator launch contract is the pattern most other plugins' team-based workflows are built on.
- No plugin was found silently *broken* in a worse way than "instruction doesn't resolve on Codex" — no data-loss-class bug like the original loom-code `name:` mailbox incident was found elsewhere.
- This is a survey only — no fixes applied. Given the count (9 plugins with a real gap), tackling all of them in one pass would be a large initiative; likely worth prioritizing by usage/stakes rather than doing all 9 at once.
