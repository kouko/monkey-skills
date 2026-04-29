# Pre-Writing Checklist (Shared Standard)

LLM-specific defensive reading rules. Documentation has no safe defaults —
every assumption is a potential error. This standard codifies what to read
before writing and which defaults are dangerous.

Primary source: observed LLM failure modes in documentation generation
(synthesized from [Trong-Tra/agent-skills `documentation-specialist`](https://github.com/Trong-Tra/agent-skills/tree/main/documentation-specialist)
v1 prescriptive rules — specifically `AGENTS.md` §Read Before You Write
and §Never Assume Defaults — plus Anthropic agent skills failure
patterns).

## Why This Standard Exists

Human writers learn project conventions by osmosis. LLM writers do not —
they will confidently invent a license, choose `npm install` for a `pnpm`
project, or use `examples.md` when the project's convention is `cases.md`.

Quick mode skips MUST/SHOULD gates, so this defensive reading is the only
remaining safeguard. Full mode also benefits — pre-writing catches errors
that gates only flag retroactively.

## Mandatory Pre-Writing Checklist

Before producing any documentation artifact, verify each item:

- [ ] **Read the existing root README** (if present) — establishes project
      voice, audience, and tone register
- [ ] **Read any AGENTS.md / CLAUDE.md / GEMINI.md** — establishes
      machine-author conventions
- [ ] **List all existing docs in the target directory** — match file
      naming, heading style, code-block languages
- [ ] **Check for `LICENSE` file** — DO NOT add a license if none exists
      and the user has not asked for one
- [ ] **Check lockfiles to determine package manager**:
      - `pnpm-lock.yaml` → `pnpm install`
      - `yarn.lock` → `yarn install`
      - `package-lock.json` → `npm install`
      - `bun.lockb` → `bun install`
      - `Cargo.lock` → `cargo` workflow
      - `uv.lock` / `poetry.lock` / `requirements.txt` → match accordingly
- [ ] **Check for existing frontmatter convention** — match it; do not
      invent new frontmatter fields
- [ ] **Note heading hierarchy depth** — match what exists; do not jump
      from H1 to H3 if the project consistently uses H2 ladders

If you have read fewer than three existing files in the repository, you
are not ready to write. Read more first.

## Never Assume Defaults

Every assumption is a potential error. Always verify against actual repo state.

| Do Not Assume | Why It Fails | What To Do Instead |
|---------------|--------------|-------------------|
| **License** | Author may not want one, or may want GPL / Apache / proprietary / none | Check for `LICENSE` file. If absent, ask. Never add unprompted. |
| **Package manager** | `npm install` is wrong for a `pnpm` or `yarn` project | Check lockfiles in repo root |
| **File naming convention** | Projects use `examples.md` / `cases.md` / `patterns.md` / `snippets.md` differently | List existing files; match the convention exactly |
| **Tone register** | Corporate / casual / academic / aggressive depends on the author | Read the existing README; match the voice |
| **Frontmatter fields** | Some projects use `last_reviewed`; others use `last_updated`; others have none | Check existing docs in same directory |
| **Tech stack labels** | "Node project" may actually be Deno / Bun; "Python" may be 3.8 vs 3.12 | Check `package.json` / `deno.json` / `pyproject.toml` |
| **Quickstart commands** | Generic install commands often fail | Verify against actual project setup |
| **Badge presence** | Not every project wants badges | Check existing README; follow suit |
| **Internationalization** | Project conventions vary: `README.zh-TW.md` (Taiwan / monkey-skills default), `README.zh-CN.md` (Mainland), `README.zh.md` (locale-neutral); same applies to `ja` vs `ja-JP` | Match the project's existing translation file naming exactly. monkey-skills convention is `en` / `ja` / `zh-TW` |
| **Diátaxis directory layout** | `docs/tutorials/` vs `docs/guides/` vs `docs/learn/` varies | Check existing layout |

## When in Doubt, Ask

The right response when convention is unclear is **not** to guess. It is:

1. State what you found (e.g. "I see `pnpm-lock.yaml` so I'll use `pnpm install`")
2. Confirm the inferred convention with the user before producing the artifact
3. Document the inference in your output so the user can correct it

Asking once is cheaper than producing a wrong artifact and revising later.

## Failure Modes Prevented

This checklist is grounded in observed LLM failure modes:

1. **License invention**: LLM adds `MIT License` because "open-source projects usually have one"; the project is private or had no license decision
2. **Package manager mismatch**: LLM writes `npm install` for a `pnpm` workspace, breaking the lockfile
3. **File-naming drift**: LLM creates `examples.md` when the project's existing convention is `samples.md`
4. **Tone whiplash**: LLM uses corporate-friendly tone in a project whose existing voice is dry-academic
5. **Frontmatter invention**: LLM adds `description: …` and `categories: …` fields that don't exist anywhere else in the project
6. **Diátaxis directory hallucination**: LLM creates `docs/tutorials/` when the project uses `docs/learn/`

Each failure type listed has been observed in practice. The checklist is
defensive, not pedantic.

## Integration With Workflows

### Quick mode (mandatory)

`protocols/quick-write.md` Phase 0 requires this checklist. Quick mode skips
gates, so pre-writing is the only safeguard. Skipping it is reckless.

### Full mode (recommended)

`protocols/write-{tutorial,how-to,reference,explanation,readme,adr}.md`
Phase 0 (Context Discovery) should incorporate this checklist. Gates will
catch some failures retroactively, but pre-writing catches them
preemptively at lower cost.

### Codebase assessment

`protocols/codebase-assessment.md` already does directory scanning as part
of its Step 2 high-entropy file prioritization. This checklist is
satisfied implicitly when codebase assessment runs first.

## Sources

- Synthesized from [Trong-Tra/agent-skills `documentation-specialist`](https://github.com/Trong-Tra/agent-skills/tree/main/documentation-specialist)
  prescriptive rules — specifically `AGENTS.md` §Read Before You Write
  and §Never Assume Defaults table
- LLM failure-mode patterns observed across documentation generation tasks
- `standards/docs-as-code.md` — review checklist for PR reviewers (this
  standard is its pre-write counterpart)
