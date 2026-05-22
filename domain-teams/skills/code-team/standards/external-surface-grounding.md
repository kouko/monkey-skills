# External Surface Grounding

Any **non-stdlib external surface** invoked in production code MUST
cite a **grounding source** in the test docstring, commit message, or
PR body. External surfaces — function names, parameter shapes, CLI
flags, MCP tool fields — are where LLM code most often hallucinates,
because the agent's training-data snapshot disagrees with the
surface's current shape. The rule converts that risk into a cite.

## Primary Sources

- **Jain, N. et al. (2024) *On Mitigating Code LLM Hallucinations with API Documentation*, Amazon Science / NAACL'24.** Empirical paper showing Documentation Augmented Generation (DAG) materially reduces API-name and signature hallucination vs base LLM. https://assets.amazon.science/8f/83/7407a5634a80a39e82b52ae935fe/on-mitigating-code-llm-hallucinations-with-api-documentation.pdf
- **Trend Micro (2025-07) "Slopsquatting: When AI Agents Hallucinate Malicious Packages".** Measured that agent-style coders cut package-name hallucination by ~50% vs base LLM — meaning **half the residual still hallucinates** even in agent mode. https://www.trendmicro.com/ja_jp/research/25/g/slopsquatting-when-ai-agents-hallucinate-malicious-packages.html
- **Osmani, A. (2026) "My LLM coding workflow going into 2026".** Practitioner workflow: *"If you're using a niche library or a brand-new API, paste in the official docs or README so the AI isn't flying blind."* https://addyosmani.com/blog/ai-coding-workflow/
- **Zenn — assign (2026)「AIエージェントに使わせる CLI の設計原則 8 選」.** JP industry note emphasizing schema-first contract discipline for any surface an LLM agent invokes; pairs with this standard's CLI-flag category. https://zenn.dev/assign/articles/b3d1d07d385b87

## The Rule

Production code that invokes a non-stdlib external surface MUST have a
grounding cite for that call. The cite lives in the test docstring,
the commit message that introduces the call, or the PR body.

"Non-stdlib" means anything not in the language's own standard library
— third-party packages, OS binaries, network services, MCP tools, and
other skills' internal contracts within this repo. Pure stdlib calls
(`os.path`, `Array.prototype.map`, `time.Sleep`) are exempt.

## Five Surface Categories

Each category needs a cite when invoked. Examples are real surfaces
this repo touches.

1. **HTTP API** — third-party REST/GraphQL endpoint.
   Example: `POST https://api.notion.com/v1/pages` (Notion API).
2. **SDK package** — third-party language package wrapping a service or
   library. Example: `@anthropic-ai/sdk` `client.messages.create({...})`.
3. **MCP tool** — Model Context Protocol tool exposed in this session.
   Example: `mcp__claude_ai_Asana__create_tasks`.
4. **CLI flag** — external binary invocation with specific flags.
   Example: `gh pr create --base main --head feat/foo` or `pandoc
   --from=epub --to=gfm`.
5. **Internal sibling-team contract** — a surface this repo authors but
   the calling skill does not own. Example: `wiki-ingest`'s page-schema
   headings consumed by `wiki-lint`'s L03 check, or `scan-vault.sh`'s
   abs-path stdout consumed by `select-batch.py`'s rel-path stdin.

## Four Grounding Sources (preference order)

A cite MUST name which source backs it. Sources in descending
preference:

(a) **Live verification** in *this session* — `WebFetch` of the
   official doc URL, `Read` of installed source under `node_modules/`
   / `site-packages/` / `vendor/` (cite `file:line`), or `<cli> --help`
   output captured this session.
   Example: `WebFetch https://docs.anthropic.com/en/api/messages` for
   `@anthropic-ai/sdk` v0.40 `client.messages.create`.

(b) **MCP schema** — the in-context tool schema from system reminder or
   `claude mcp test`. The schema itself is the cite.
   Example: `claude_ai_Asana__create_tasks` — grounding: in-context
   tool schema.

(c) **Pinned reference** — a `references/<surface>.md` file in the
   skill containing the doc snippet, source URL, and `capture-date`.
   `capture-date` is informational only (v1 has no staleness check).
   Example: `references/gh-pr-create.md` capturing `gh pr create
   --help` with `capture-date: 2026-05-22`.

(d) **In-repo evidence** — an existing working call to the same surface
   in this repo, cited as `file:line`. Weakest grounding (in-repo
   callers can themselves be wrong); acceptable when live verification
   was unavailable.
   Example: `salesforce-toolkit/scripts/upsert.py:42` already calls
   `sObjects/Contact/External_Id__c` so this PR mirrors it.

## Anti-Patterns (rationalizations to refuse)

Refuse these phrasings — they are the failure mode the rule exists to
catch:

- ❌ *"I know this API"* — training-data drift is the whole problem;
  what you remember may have been renamed or removed (ICSE 2025 Wang
  et al. on deprecated APIs).
- ❌ *"The SDK probably has this method"* — *probably* is hallucination;
  verify before calling.
- ❌ *"The CLI usually accepts --foo"* — CLI tools add/rename flags;
  `--help` output is one command away.
- ❌ *"The MCP tool I used last week"* — MCP schemas shift on
  Anthropic-side updates; the in-context schema this session is the
  only authoritative shape.

## Severity (delegated to reviewer rubric)

Severity rules live in the reviewer prompts — see **D7 "External
Surface Grounding"** in `code-toolkit/agents/code-quality-reviewer.md`
(per-task) and `code-toolkit/agents/code-reviewer.md` (whole-branch).
Calibration per §Resolved Decisions Q4 of the brief:

- **🔴 fatal MUST** — categories 1-4 (HTTP API / SDK package / MCP tool
  / CLI flag) invoked without a grounding cite.
- **🟡 should-fix SHOULD** — category 5 (internal sibling-team contract)
  invoked without a cite. Harder to objectively audit; tracked under
  whole-branch reviewer's cross-task-coherence dimension.

## Per-Task vs Whole-Branch Scope

**Per-task code-quality-reviewer** evaluates one task's diff and is
**structurally blind** to sibling tasks in the same branch. It cannot
detect that task A and task B call the same MCP tool with conflicting
parameter shapes.

**Whole-branch code-reviewer** owns cross-task surface-consistency.
Two tasks calling the same surface with diverging endpoints, version
pins, or parameter shapes is a 🟡 should-fix at the whole-branch layer
(per §Resolved Decisions Q3 of the brief).

Per-task reviewer evaluates "does this task's call have a cite?" — not
"does this task agree with its siblings?". The latter is out of scope
at the per-task layer by construction.
