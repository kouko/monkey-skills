# External Surface Grounding Discipline — brainstorm brief

**Date**: 2026-05-22
**Author**: kouko (orchestrated via code-toolkit:brainstorming)
**Plugin under change**: `code-toolkit`
**Consumed by**: `writing-plans` (next stage)

---

## Problem

**Job (JTBD format)**:
> When my code-toolkit pipeline implements code that touches an **external surface I don't author** — third-party HTTP API, npm/pip/cargo package, MCP server tool, CLI binary, internal sibling-team library — I want the generated code to use **functions / parameters / flags / fields that actually exist in that surface's current version**, so that I don't burn discovery cycles on hallucinated APIs at runtime / review / production.

**Why this is real, not theoretical**:
- Industry signal: Trend Micro (2025-07) measured **agent-style coders cut package-name hallucination ~50%** vs base LLM — meaning **half the residual still hallucinate** even in agent mode. ([source](https://www.trendmicro.com/ja_jp/research/25/g/slopsquatting-when-ai-agents-hallucinate-malicious-packages.html))
- Industry signal: Amazon Science paper on **Documentation Augmented Generation (DAG)** explicitly frames doc-RAG as the mitigation for "Code LLMs should likewise consult [API docs] under uncertainty." ([source](https://assets.amazon.science/8f/83/7407a5634a80a39e82b52ae935fe/on-mitigating-code-llm-hallucinations-with-api-documentation.pdf))
- Industry signal: ICSE 2025 paper on **deprecated API usage** in LLM coders — the problem is not just *non-existent* APIs but *existed-once-but-removed* APIs. ([source](https://yebof.github.io/assets/pdf/wang2025icse.pdf))
- Practitioner signal: Addy Osmani's 2026 workflow — *"If you're using a niche library or a brand-new API, paste in the official docs or README so the AI isn't flying blind."* ([source](https://medium.com/@addyosmani/my-llm-coding-workflow-going-into-2026-52fe1681325e))
- Practitioner signal (JA): Re-BIRTH note explicitly names Claude Code's "実際には存在しないライブラリ・関数・APIをさも実在するかのように提案する現象". ([source](https://note.com/re_birth_ai/n/n8bd8fceb0d0b))

**Failure mode mechanics** (why current code-toolkit doesn't catch this):
- `tdd-iron-law` forces RED-first → implementer's test stubs/mocks the external surface → mock matches implementer's *imagination* of the API → GREEN passes → runtime fails.
- `spec-reviewer` compares artifact to spec → spec rarely names exact external function signatures → no mismatch detected.
- `code-quality-reviewer` (current 6 dimensions: security / architecture / correctness / naming / tests / refactoring) → **none** of the dimensions explicitly check "does this external symbol/flag/field actually exist?".
- `code-reviewer` (whole-branch, 7 dimensions including cross-task-coherence) → same gap.
- Zero current mentions of "third-party / external / library / API verification" in `agents/*.md` / `rubrics/*.md` / `writing-plans/references/*.md` — confirmed by grep at 2026-05-22.

---

## Users

**Primary user**: kouko (project owner of monkey-skills), running code-toolkit pipeline against projects that frequently touch:

| External surface type | Concrete recent examples in this repo |
|---|---|
| **Third-party HTTP API** | Salesforce REST, Asana API, Slack API, Gmail API, GCal API, Notion API, FRED API, BOJ Tankan, NDC, ECOS, NBS new-SPA |
| **Third-party SDK / package** | `@anthropic-ai/sdk`, `googleapiclient`, `kobodl`, `pandoc`, `defuddle`, `hatchling`, `pytest`, `bats` |
| **MCP server tool** | `chrome-devtools`, `claude_ai_Asana`, `claude_ai_Notion`, `claude_ai_Google_Calendar`, `claude_ai_Gmail`, `obsidian-cli` |
| **CLI tool / flags** | `gh pr ...`, `git filter-branch`, `pandoc --to ...`, `kobodl ...`, `jq -e ...`, `bats`, `pytest --co -q`, `claude mcp ...` |
| **Internal sibling-team contract** | wiki-ingest ↔ wiki-lint heading schema (PR #320 root cause; see `feedback_cross_skill_schema_rename_blind_spot`) |

**Conditions**:
- Working solo (single user, single brain, no peer-review backstop besides code-toolkit's own subagents).
- SDD pipeline frequently dispatches 4-10 subagents per task across long sessions — manual "did you check the docs?" question doesn't scale.
- Many surfaces evolve fast (Anthropic SDK ~weekly; Asana / Notion MCP shape shifts on Anthropic-side updates; CLI tools add flags).
- WebFetch / WebSearch is **usually** available but not guaranteed (some sessions restrict).

**What kouko already does manually today** (the workaround this skill is meant to systematize):
- After SDD declares DONE, occasionally spot-check by running `<cli> --help` or grep'ing `node_modules/<pkg>` — but ad-hoc, no gate.
- Reads MCP tool schemas in conversation reminders to sanity-check the agent's calls — but only when an error surfaces.

---

## Smallest End State

The **minimum** intervention that meaningfully reduces external-surface hallucination, without bloating every task with friction.

### What we WILL build (Option B, "Plan-time declaration + Review-time gate")

**Three artifacts, additive only**:

1. **New standard** (canonical SSOT): `domain-teams/skills/code-team/standards/external-surface-grounding.md` (target ≤120 lines) — functional copy at `code-toolkit/skills/subagent-driven-development/standards/external-surface-grounding.md` auto-generated by `scripts/distribute.py` with new ROUTE entry
   - Defines the rule: **any non-stdlib external surface invoked in production code MUST cite a grounding source in the test docstring / commit message / PR body**.
   - Defines the four valid grounding sources (in order of preference):
     a. **Live verification**: `WebFetch` of official doc URL captured in this session, OR `Read` of installed source under `node_modules/` / `site-packages/` / `vendor/`, OR `<cli> --help` output captured.
     b. **MCP schema**: for MCP-tool calls, the in-context tool schema (from system reminder or `claude mcp test`) counts as grounding.
     c. **Pinned reference**: a `references/<surface>.md` file in the skill with the captured doc snippet + URL + capture date (>30 days old triggers re-capture warning).
     d. **In-repo evidence**: existing working call to the same surface in the same repo (cite `file:line`).
   - Enumerates surface categories: HTTP API / SDK package / MCP tool / CLI flag / sibling-team contract.
   - Names the **explicit anti-patterns** (the rationalizations to refuse): *"I know this API"*, *"the SDK probably has this"*, *"the CLI usually accepts --foo"*, *"the MCP tool I used last week"* (note: surface may have updated).
   - Grounded in: Amazon Science DAG paper (Jain et al.); Addy Osmani 2026 workflow blog; Trend Micro slopsquatting report.

2. **New review dimension**: add **D7 External Surface Grounding** to `code-toolkit/agents/code-quality-reviewer.md` AND `code-toolkit/agents/code-reviewer.md`:
   - Per-task reviewer checks: every external-surface call in the diff has a grounding cite.
   - Whole-branch reviewer checks: cross-task surface usage is consistent (no two tasks calling the same MCP tool with conflicting param shapes).
   - Severity:
     - 🔴 fatal: external call with **no** grounding cite AND surface category is HTTP API / SDK / MCP / CLI flag.
     - 🟡 should-fix: cite present but stale reference (>30 days) AND surface is fast-moving (Anthropic SDK / MCP tools).
     - 🟢 nit: cite uses in-repo evidence when live verification was available.

3. **New atomic-task field**: add `External surfaces:` field (optional but populated when applicable) to `code-toolkit/skills/writing-plans/SKILL.md` task template + `code-toolkit/skills/writing-plans/references/plan-format.md` schema (direct-edit; writing-plans is code-toolkit-only, not SSOT-distributed). `spec-reviewer` enforcement comes via a new check row in `domain-teams/skills/code-team/checklists/spec-consistency.md` (canonical SSOT) propagated to its functional copy. Field shape:
   ```
   External surfaces:
     - <surface category>: <name> — grounding: <method>
       e.g.
     - SDK package: @anthropic-ai/sdk@0.40 client.messages.create — grounding: WebFetch https://docs.anthropic.com/en/api/messages
     - MCP tool: claude_ai_Asana__create_tasks — grounding: in-context tool schema
     - CLI flag: gh pr create --base — grounding: gh pr create --help (captured 2026-05-22)
   ```

**LOC budget**: ≤500 LOC delta total (1 new standard + 2 agent diffs + 1 SKILL.md diff + 1 spec-consistency.md checklist diff).

### What we will NOT build (deferred / out of scope)

- **No new gate-skill** like `grounding-external-surfaces`. The discipline lives inside existing skills as additive rules, not a new pipeline stage. (Reason: orthogonal to TDD ordering; lives at review-time, not at execution-time.)
- **No hard pre-implementation block** ("implementer MUST WebFetch before RED"). Too noisy for tasks that touch already-grounded surfaces. The review-time gate catches misses.
- **No automated reference-pinning subsystem** (`references/<surface>.md` snapshot harness). Manual capture is the v1; if drift becomes painful we can automate later.
- **No context7-style MCP integration enforcement**. context7 / DeepWiki / GitMCP are great tools but live in user's environment setup, not in the skill prompt. The new standard will *mention* them as recommended environment additions but won't require them.
- **No retroactive sweep** of past code-toolkit-generated code in monkey-skills repos. Forward-looking only.
- **No new "External Surface Audit" skill in `domain-teams:code-team`**. Functional-copy sync can happen later if the discipline proves out.

---

## Current State Evidence

**Forward** (entry points touched):
- `code-toolkit/agents/implementer.md:1-280` — implementer prompt, no current external-surface guidance ([grep confirmed 0 hits](code-toolkit/agents/implementer.md))
- `code-toolkit/agents/code-quality-reviewer.md:1-363` — 6 review dimensions today ([code-quality-reviewer.md](code-toolkit/agents/code-quality-reviewer.md))
- `code-toolkit/agents/code-reviewer.md:1-376` — 7 whole-branch dimensions today ([code-reviewer.md](code-toolkit/agents/code-reviewer.md))
- `code-toolkit/agents/spec-reviewer.md:1-314` — spec-reviewer ([spec-reviewer.md](code-toolkit/agents/spec-reviewer.md))
- `code-toolkit/skills/subagent-driven-development/standards/` — 7 standards today, none cover external surfaces ([listing](code-toolkit/skills/subagent-driven-development/standards/))
- `code-toolkit/skills/subagent-driven-development/rubrics/quality-gate.md` — 7 dimensions (Beck/Martin/Fowler grounded), no external-surface dim ([quality-gate.md](code-toolkit/skills/subagent-driven-development/rubrics/quality-gate.md))
- `code-toolkit/skills/writing-plans/SKILL.md` — atomic-task field set, no External surfaces field ([SKILL.md](code-toolkit/skills/writing-plans/SKILL.md))
- `code-toolkit/skills/subagent-driven-development/checklists/spec-consistency.md` — 11 spec-consistency checks, none for external-surface declaration ([spec-consistency.md](code-toolkit/skills/subagent-driven-development/checklists/spec-consistency.md))

**Reverse** (SSOT chain — corrected 2026-05-22 after inspecting `scripts/distribute.py` docstring):
- **Canonical SSOT lives in `domain-teams/skills/code-team/{standards,checklists,rubrics}/`** — NOT in code-toolkit. code-toolkit holds functional copies generated by `code-toolkit/scripts/distribute.py`. Any new standard MUST land canonically in domain-teams first, then propagate via distribute.
- `code-toolkit/scripts/distribute.py` ROUTE table maps each canonical file to its consuming-skill destinations (e.g. `standards/tdd-standard.md` → `code-toolkit/skills/{tdd-iron-law,subagent-driven-development}/standards/tdd-standard.md`). New standard requires a new ROUTE entry in the same commit.
- `code-toolkit/scripts/verify-drift.py` runs in CI; any byte-diff between expected (canonical+header) and on-disk functional copy fails the gate.
- Agent prompts (`code-toolkit/agents/{implementer,spec-reviewer,code-quality-reviewer,code-reviewer}.md`) are **direct-edit** for the dimension tables / reviewer logic; only the `<!-- BEGIN baseline-v1 -->` block and reviewer-discipline block inside each agent are SSOT-distributed from `scripts/_baseline.md` + `scripts/_reviewer-discipline.md`.

**Error** (failure modes already observed):
- PR #320 wiki-ingest v3.14.0 — schema-rename in skill A broke enumeration in sibling skill B → exactly the "internal sibling-team contract" surface category. Caught by whole-branch reviewer ONLY when prompt explicitly directed wiki-lint compatibility check. ([memory ref](feedback_cross_skill_schema_rename_blind_spot))
- PR #310 wiki-ingest v3.11.1 — `scan-vault.sh` (abs path output) ↔ `select-batch.py` (rel path input) contract mismatch → "cross-script pipe semantics" surface category. ([memory ref](feedback_per_task_review_misses_pipe_semantics))
- Both incidents are **internal external-surface** cases — same failure mode as third-party hallucination, different surface. The new standard intentionally covers both.

**Data**:
- 7 existing standards average ~150 lines. New standard target ≤120 lines fits the norm.
- 30 example MCP tools in current `<system-reminder>` (per this session) — schema-loading already happens, the discipline only requires the agent to *cite* what's loaded.

**Boundary**:
- SSOT chain (corrected, see Reverse above): canonical edits in `domain-teams/skills/code-team/` → `scripts/distribute.py` materializes functional copies in `code-toolkit/skills/<consumer>/` → `verify-drift.py` byte-checks in CI. Change MUST land in the canonical location AND have a ROUTE entry in `distribute.py` in the same commit; otherwise verify-drift fails.
- `code-toolkit/skills/writing-plans/` is code-toolkit-only (not distributed, no canonical sibling) — direct-edit.
- Agent dimension tables (in `code-toolkit/agents/*.md`) are direct-edit — only the `BEGIN baseline-v1 / END baseline-v1` block within each agent file is distributed from `scripts/_baseline.md`.
- `code-toolkit` is **not** a Python package per memory's [pyproject-no-build-system-for-cc-plugins](memory ref) — no `[build-system]` in pyproject.toml. Changes are markdown + Python ROUTE-dict edits only.

**Evidence paths appendix**:
- `code-toolkit/skills/subagent-driven-development/standards/*.md`
- `code-toolkit/skills/subagent-driven-development/rubrics/{quality-gate,arch-gate}.md`
- `code-toolkit/skills/subagent-driven-development/checklists/{spec-consistency,security-checklist}.md`
- `code-toolkit/skills/writing-plans/SKILL.md`
- `code-toolkit/agents/{implementer,spec-reviewer,code-quality-reviewer,code-reviewer}.md`
- `code-toolkit/scripts/{distribute.py,verify-drift.py}`

---

## Decision

**What we will build**: Option B — **Plan-time declaration + Review-time gate**, three artifacts (1 new standard + 2 agent dimensions + 1 plan-template field), ≤500 LOC additive delta, distributed via `scripts/distribute.py` to `domain-teams:code-team` for SSOT consistency.

**What we will NOT build**: hard pre-implementation block; new gate-skill; automated reference-snapshot harness; retroactive sweep; mandatory context7-MCP enforcement. (Each deferred for documented reasons — see §Smallest End State above.)

**Why this shape**:
- Matches code-toolkit's existing architecture (standards + rubrics + agent dimensions + plan fields) — no new patterns invented.
- Distributes both the discipline (standard) and the enforcement (review dimensions) so cost ≠ all on implementer.
- Plan-time declaration makes the failure mode **visible at plan-review** before any implementer wastes a subagent call on a hallucinated surface.
- Review-time gate is the safety net: catches misses where plan didn't declare but code touched anyway.
- Severity calibration (🔴 fatal for HTTP/SDK/MCP/CLI; 🟡 for stale-reference) prevents over-firing on internal stdlib-shaped calls.

---

## Out of Scope

- Building a context7-style MCP-doc-server ourselves (use existing community ones; out of monkey-skills scope).
- Auto-snapshotting `<cli> --help` / `pip show <pkg>` output into `references/` (manual capture v1; automate later if drift painful).
- Domain-teams code-team gate workflow changes (functional-copy via distribute.py is enough; the team-team gates inherit the new standard automatically).
- Cross-language coverage of the standard's body itself (English-only standard, matches existing 7 standards which are all English).
- A new pressure-test under `code-toolkit/tests/` for this discipline. (May add in v2; v1 is the discipline itself, not a test for it.)

---

## Alternatives Considered

Three industry approaches were evaluated via WebSearch (EN + JA on 2026-05-22):

### Approach 1 — Documentation Augmented Generation (RAG-of-docs)

- Source: [Amazon Science / Jain et al. (NAACL'24)](https://assets.amazon.science/8f/83/7407a5634a80a39e82b52ae935fe/on-mitigating-code-llm-hallucinations-with-api-documentation.pdf); also [context7 MCP](https://github.com/upstash/context7)
- **Pros**: Highest fidelity; doc snippet directly in context at generation time; closest to "no possibility of hallucination."
- **Cons**: Requires infrastructure (MCP server / RAG index) that lives outside the skill prompt; user must set up; doc index must be maintained; cost (token bloat in context).
- **Used by**: context7 MCP (Upstash), DeepWiki, GitMCP, Cursor `@docs`.
- **Fit for code-toolkit**: PARTIAL. Out-of-band tooling; skill can recommend but can't enforce. → folded into the new standard as "preferred grounding method (4a)".

### Approach 2 — Prompt-level "if unsure, ask" discipline (Voiceflow / Zep)

- Source: [Voiceflow blog](https://www.voiceflow.com/blog/prevent-llm-hallucinations); [Zep guide](https://www.getzep.com/ai-agents/reducing-llm-hallucinations/); also Trend Micro's finding that agent-style coders already halve hallucination via inherent reasoning loops.
- **Pros**: Zero infrastructure; pure prompt; ships in minutes.
- **Cons**: Trend Micro empirically shows this gets **half** the win; residual still hallucinates ~25% of cases. Insufficient alone.
- **Used by**: Almost every published LLM-prompt guide of the last 2 years; clearly necessary-but-not-sufficient.
- **Fit for code-toolkit**: BASELINE only. Add a sentence to implementer prompt but don't rely on it.

### Approach 3 — Plan-time declaration + Review-time gate (chosen)

- Source: pattern derived from code-toolkit's existing architecture (standards + review dimensions + plan-template fields) — same shape as TDD iron-law, security-checklist, etc.; JA inspiration from [Zenn — AIエージェント CLI 設計原則](https://zenn.dev/assign/articles/b3d1d07d385b87) emphasizing **schema-first contract** discipline.
- **Pros**: Matches existing skill architecture; distributes cost (plan declares, review verifies); declarative artifact serves as audit log; works without external infrastructure; functional-copies through distribute.py to domain-teams:code-team.
- **Cons**: Adds friction to plan + review steps; requires honest declaration (a hallucinating implementer could declare a hallucinated grounding source — but reviewer's job is to spot-check the cite).
- **Used by**: This is the same shape code-toolkit already uses for TDD-iron-law / security-checklist / spec-consistency. Internal precedent, not external industry.
- **Fit for code-toolkit**: BEST. Picked.

**My take**: Recommend **Approach 3 as primary + Approach 1 referenced as preferred grounding source + Approach 2 as baseline implementer-prompt sentence**. Conditional reversal: if Approach 3 in practice fires too many 🔴 false-positives on legitimate stdlib-shaped internal calls, the standard's severity calibration needs tuning before considering hard pre-implementation gates.

---

## What Becomes Obsolete

**Honest answer**: Not much, because this is additive review discipline (same as TDD iron-law was additive). However:

- **Implicit assumption that "agent training data is current enough"** → explicit refusal in the new standard. (Not deletable code, but deletable rationalization.)
- **Ad-hoc post-DONE spot-checking by user** (the manual workaround in §Users) → systematized into the review dimension. Free the user from doing it manually.
- **Memory entry [`feedback_cross_skill_schema_rename_blind_spot`](memory ref) lessons** → folded into the standard's "sibling-team contract" surface category, so the lesson is enforced not just remembered.
- **Memory entry [`feedback_per_task_review_misses_pipe_semantics`](memory ref) lessons** → same fold; cross-script contract is an "internal external surface" case the new standard covers.

If nothing else obsoletes, that's a YAGNI flag per brainstorming's Axis 5. Acknowledged honestly: this passes the YAGNI sniff-test because (a) the failure mode is observed (industry signal + 2 in-repo incidents) and (b) the intervention shape matches the toolkit's existing additive-discipline pattern (TDD / security-checklist) which themselves don't delete anything but earn their keep.

---

## Resolved Decisions

All 5 open questions resolved 2026-05-22 by kouko before writing-plans:

1. **Distribution scope** — **Same PR**. code-toolkit changes + `scripts/distribute.py` invocation + `domain-teams:code-team` functional copy all land atomically in one PR. `verify-drift.py` CI passes in one shot, no drift window.
2. **Stale-reference threshold** — **v1 ships without staleness check**. `capture-date` is recorded inside the `references/<surface>.md` body for informational purposes only; no reviewer rule fires on age. Revisit in v2 if stale-cite-causes-pain pattern emerges in practice.
3. **Cross-task surface-consistency ownership** — **Whole-branch reviewer only**. Per-task `code-quality-reviewer` is structurally blind to sibling tasks and the standard will say so explicitly. Whole-branch `code-reviewer` owns the dimension under its existing cross-task-coherence umbrella.
4. **Gate strictness per surface category** — **Tiered**:
   - 🔴 fatal MUST: HTTP API / SDK package / MCP tool / CLI flag (the 4 external categories)
   - 🟡 should-fix SHOULD: internal sibling-team contract (harder to objectively audit; lives in whole-branch reviewer's cross-task-coherence dim, doesn't gate per-task)
5. **References file lifecycle** — **Lazy refresh, no contract**. Any task may read or write `references/<surface>.md`. `capture-date` exists in the body as informational signal. The next implementer touching the same surface refreshes opportunistically. No background sweep, no scheduled audit, no "owner" assignment.

---

## Sources

**English**:
- [On Mitigating Code LLM Hallucinations with API Documentation — Nihal Jain et al., Amazon Science](https://assets.amazon.science/8f/83/7407a5634a80a39e82b52ae935fe/on-mitigating-code-llm-hallucinations-with-api-documentation.pdf)
- [LLMs Meet Library Evolution: Evaluating Deprecated API Usage in LLM-based Code — Wang et al., ICSE 2025](https://yebof.github.io/assets/pdf/wang2025icse.pdf)
- [My LLM coding workflow going into 2026 — Addy Osmani](https://addyosmani.com/blog/ai-coding-workflow/)
- [Reducing LLM Hallucinations — Zep](https://www.getzep.com/ai-agents/reducing-llm-hallucinations/)
- [How to Prevent LLM Hallucinations: 5 Proven Strategies — Voiceflow](https://www.voiceflow.com/blog/prevent-llm-hallucinations)
- [Claude Code Cheat Sheet 2026 — TechBytes](https://techbytes.app/posts/claude-code-2026-cheat-sheet-hooks-mcp-commands/)

**Japanese (日本語)**:
- [スロップスクワッティング — トレンドマイクロ 2025-07](https://www.trendmicro.com/ja_jp/research/25/g/slopsquatting-when-ai-agents-hallucinate-malicious-packages.html)
- [Claude Codeの幻想（ハルシネーション）問題：実務的な対策完全ガイド — Re-BIRTH note](https://note.com/re_birth_ai/n/n8bd8fceb0d0b)
- [AIエージェントに使わせるCLIの設計原則8選 — Zenn](https://zenn.dev/assign/articles/b3d1d07d385b87)
- [AIプログラミングの落とし穴：ハルシネーションとコード不整合 — トレンドマイクロ](https://www.trendmicro.com/ja_jp/research/24/h/the-mirage-of-ai-programming-hallucinations-and-code-integrity.html)
- [AI駆動開発セキュリティ実践ガイド — クラウドエース](https://cloud-ace.jp/column/detail538/)
- [AIエージェントの「手」はCLIかMCPか — ITmedia オルタナティブ・ブログ](https://blogs.itmedia.co.jp/osonoi/2026/05/aiclimcp.html)
