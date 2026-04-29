# Write README Protocol (Composite: Standard README + Diátaxis)

Write a README.md file following the Standard README specification
(RichardLitt). README is a **composite** document — each section maps to
a different Diátaxis quadrant, but the Standard README spec determines
the structural order and required sections.

**Spec source**: [github.com/RichardLitt/standard-readme](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
**Vocabulary reference**: `standards/diataxis-taxonomy.md`
**Style reference**: `standards/style-conventions.md`
**Pre-writing reference**: `standards/pre-writing-checklist.md` — apply before Phase 0
**Worked examples**: `protocols/write-readme-examples.md` (companion file, full mode only)

## README as Composite

A README is the single most-read documentation artifact. It must serve
multiple reader needs at once:

| Section | Diátaxis mode | Reader need |
|---------|---------------|-------------|
| Title + Short description | Explanation (gist) | "What is this?" |
| Background | Explanation | "Why does this exist?" |
| Install | How-to | "How do I get it running?" |
| Usage | Tutorial-lite | "How do I try it?" |
| API | Reference pointer | "Where are the full docs?" |
| Maintainers | Explanation (ownership) | "Who is responsible?" |
| Contributing | How-to | "How do I help?" |
| License | Reference | "Can I use it?" |

Because README sections map to different modes, the **Diátaxis Mode Clarity
gate runs per-section** rather than on the whole file. Each section must be
clean in its own mode.

## Phase 0: Context Discovery

1. **Is there an existing README?** Read it. Identify what's salvageable.
2. **What kind of project is this?** A library, an application, a tool,
   a service, a documentation site? Different kinds need different emphasis.
3. **Who will read this README?** Users of the project? Contributors?
   Both? A library README usually needs strong Install + Usage; a service
   README usually needs strong Background + Contributing.
4. **What exists in `docs/`?** If detailed tutorials and references exist
   elsewhere, the README links to them rather than duplicating.

## Phase 1: Required Sections (Standard README spec)

Every README must include these sections in this order:

### 1. Title

The project name, matching the repo/package name. If the canonical name
differs, italicize the alternate.

### 2. Short Description

**Under 120 characters.** One sentence explaining what the project does.
This is what appears in package manager listings and GitHub summaries.

### 3. Table of Contents

**Required if the README exceeds 100 lines.** Link to every level-2 heading.
Skip for short READMEs.

### 4. Install

A code block showing how to install. For libraries, typically a single
command (`npm install`, `pip install`, `cargo add`). For applications,
may include prerequisites and multiple commands.

Keep this section **minimal**. If installation is complex, the README
shows the basic case and links to a full installation how-to guide.

### 5. Usage

A code block showing the project in action. For libraries, a minimal
import + function call. For applications, a minimal command that
demonstrates the project's purpose.

This is where the README is tutorial-lite: it shows enough for the reader
to verify the project works and understand its shape. Full tutorials live
in `docs/tutorials/`.

### 6. Contributing

Policy for contributions:
- **Questions policy** — where to ask (GitHub Discussions, Slack, email)
- **PR policy** — how to open, what to include, review expectations
- **Code of conduct** — link to CODE_OF_CONDUCT.md if it exists

### 7. License

**Must be the final section.** Specify the SPDX identifier (`MIT`, `Apache-2.0`)
and the copyright holder. Link to the LICENSE file.

## Phase 2: Optional Sections

Optional but common sections, in this order when present:

- **Banner** (hero image or logo) — between title and description
- **Badges** (build status, version, license) — below title
- **Long description / Background** — Explanation mode; answers "why does this exist?"
- **Security** — how to report vulnerabilities
- **API** — inline for tiny libraries; link to separate docs for larger projects
- **Maintainers** — named people or team ownership

## Phase 3: Language and Style

README prose must follow `standards/style-conventions.md`:

- Active voice, second person, present tense
- Sentence-case headings
- Descriptive link text
- Serial comma in lists

Keep each section focused on its mode. The Background section can be
discursive (Explanation mode). The Install section should be imperative
and efficient (How-to mode). The Usage section should have guaranteed
success on first try (Tutorial mode).

## Phase 4: Internationalization

If the project has international users, provide translated READMEs:

- Named with BCP 47 tags. **monkey-skills convention is `en` / `ja` /
  `zh-TW`**: `README.md` (English, default), `README.ja.md`,
  `README.zh-TW.md`. Other projects may use different sets (e.g.
  `README.zh-CN.md`, `README.fr.md`); always match the project's
  existing convention rather than introducing a new one.
- Linked from the main README at the top: e.g. "Read this in:
  [English] | [日本語] | [繁體中文]"
- Translations kept in sync when the main README changes (track via
  `last_reviewed` in frontmatter)
- Use the project's i18n glossary if one exists (monkey-skills uses
  `docs/i18n/glossary-ja.md` and `docs/i18n/glossary-zh-TW.md`) to
  preserve English tech terms (skill, plugin, agent, workflow, gate,
  MUST / SHOULD / MAY, etc.) consistently across translations

## The 30-Second Test

A reader decides whether to keep reading within 30 seconds. The top of
the README must pass:

- [ ] First line says what the project IS, not what language it uses
- [ ] First paragraph explains the problem it solves
- [ ] A visible quickstart (or link to one) appears above the fold
- [ ] Build / version badges appear if the project has CI
- [ ] A screenshot or demo (for UI projects) or a code sample (for
      libraries) appears within the first ~30 lines

## The One-Liner Formula

The first line is a contract. Form: `[Project name]` is `[what it
does]` for `[who uses it]`.

| Bad | Why | Good |
|-----|-----|------|
| "A CLI tool" | Too vague | "A CLI tool for visualizing Docker container resource usage" |
| "React component library" | No differentiator | "React component library with built-in accessibility and dark mode" |
| "The best X" | Marketing, not information | "X with automatic failover and sub-millisecond latency" |

## Quickstart Patterns by Project Type

The right Quickstart shape depends on the project archetype.

### Pattern A: Library or package

Single install command, then a minimal import + function call. No
prerequisites beyond the package manager. See worked Example 1 in the
companion file.

### Pattern B: Application or service

Prerequisites listed first (Docker, Node version, database). Clone +
configure + run. End with a verification step ("Open http://localhost:N").
See worked Example 2 in the companion file.

### Pattern C: CLI tool

Multi-channel install (`curl | sh`, `brew`, package managers). First-run
walk-through showing the canonical command sequence. See worked Example 3
in the companion file.

### Pattern D: Infrastructure or config

Init + plan + apply (Terraform pattern), or render + apply (Helm
pattern). End with a verification command. Backend matrix if applicable.

## Feature Communication

Do not list every feature. Group features by user goal.

**Before** (lists technical components):

```markdown
## Features
- JWT authentication
- Role-based access control
- PostgreSQL support
- Redis caching
- WebSocket support
- Rate limiting
```

**After** (groups by user goal):

```markdown
## Features

**Authentication that stays out of your way**
JWT-based auth with automatic refresh. RBAC built in. No boilerplate.

**Performance by default**
Redis caching, connection pooling, and query optimization out of the box.

**Real-time where you need it**
WebSocket support with automatic fallback to SSE for older clients.
```

## Configuration Documentation

Every environment variable and config option must be documented in a
table — not prose:

```markdown
## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | No | — | Redis for caching. Omit to disable caching. |
| `PORT` | No | `3000` | HTTP server port |
| `LOG_LEVEL` | No | `info` | One of: `debug`, `info`, `warn`, `error` |
```

Rules:
- State the default. If there is no default, say `—` and mark required.
- Explain the unit. Is `TIMEOUT` in seconds or milliseconds?
- Explain the consequence of omission. What breaks if you do not set it?

## Troubleshooting Section

Every error message you have personally debugged belongs here. Place
this section before the FAQ.

```markdown
## Troubleshooting

**Error: `connection refused` on startup**
The database is not running or `DATABASE_URL` is wrong. Verify with
`psql $DATABASE_URL -c "SELECT 1"`.

**Error: `module not found` after install**
You are on an old Node version. Check `node --version` (must be ≥ 20).

**Build fails with `out of memory`**
Increase the Node memory limit:
`NODE_OPTIONS="--max-old-space-size=4096" npm run build`
```

## Badge Strategy

Badges are signals. Use them sparingly and intentionally.

| Badge | When to use | When to skip |
|-------|-------------|--------------|
| Build status | Always | Never |
| Version | Published packages | Internal tools |
| Coverage | Public OSS with CI | Prototype, WIP |
| License | Always | Never |
| Downloads | Libraries, packages | Applications |
| Chat / Discord | Active community | Solo project |

More than 6 badges is badge spam. Group related badges if needed.

## README Length Guide

Match length to project type:

| Project type | Target length |
|--------------|---------------|
| Simple library | 50-100 lines |
| Framework or tool | 100-200 lines |
| Complex application | 200-400 lines |
| Platform or monorepo | 300-500 lines + links to sub-READMEs |

If the README exceeds these bounds, move sections to `docs/` and link
to them.

## Language-Specific Conventions

| Language | Required README content |
|----------|------------------------|
| Go | `go get` install command; complete `main.go` example, not just snippets; document `context.Context` usage patterns |
| Rust | `Cargo.toml` dependency line; feature flags if the crate has them; document MSRV (Minimum Supported Rust Version) |
| Python | `pip install` (or `uv add` / `poetry add` per project); show import + basic usage; document Python version compatibility |
| TypeScript / JavaScript | `npm install` (or `pnpm add` / `yarn add` per lockfile); show both ESM and CommonJS if supporting both; document Node version |

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| No install instructions | Always include install or clone steps |
| Broken quickstart | Test on a clean machine regularly |
| Missing prerequisites | List them before the first command |
| No verification step | Tell the user what success looks like |
| Outdated screenshots | Audit quarterly or use auto-generated diagrams |
| Assuming domain knowledge | Define acronyms on first use |
| Hiding the license | Put LICENSE near the top or badge it |
| Vague feature lists | Group by user goal, not technical component |

## Rules

- **Required sections are required.** Do not skip Install / Usage / Contributing / License.
- **License is always last.** This is a Standard README spec rule.
- **Short description under 120 characters.** Not 121.
- **Every section stays in its mode.** Don't put background history in the
  Install section. Don't put step-by-step tutorials in the Usage section.
- **Link to deeper docs.** README is a landing page, not the full docs.
- **No broken links.** All internal links resolve; external links are valid.

## Output Structure

```markdown
# {Project Name}

> {Short description under 120 characters}

{Badges if applicable}

## Background (optional)

{Explanation mode: why does this exist, what problem does it solve}

## Install

​```bash
{minimal installation command}
​```

## Usage

​```{language}
{minimal usage example with guaranteed success}
​```

## API (optional)

{For small libraries: inline API. For larger projects: link to `docs/reference/`}

## Maintainers (optional)

{Named owners or team}

## Contributing

{Policy for questions, PRs, conduct}

## License

{SPDX identifier} © {copyright holder}

See [LICENSE]({path}) for details.
```

## Worked Examples (Companion File)

Five complete README examples (Go library, full-stack app, CLI tool,
Bad → Good rewrite, Monorepo) live in the companion file:

```
protocols/write-readme-examples.md
```

The `worker` agent loads this companion via the `additional:` field in
full mode. **Quick mode does NOT load it** — quick mode trades example
context for token savings (see `protocols/quick-write.md` §No Companion
Load).

When dispatching a worker for a README task, the main agent passes:

```
- protocol: {base_path}/protocols/write-readme.md
- additional: [{base_path}/protocols/write-readme-examples.md]
```

## Completeness Check

This README passes the README Completeness MUST gate if:

- Title matches repo/package name
- Short description exists and is under 120 characters
- Install section exists with a code block
- Usage section exists with a code block
- Contributing section exists with policy
- License section exists and is the final section
- Table of Contents is present if README exceeds 100 lines
- No broken internal links

## Mode Clarity Per Section

Each section is evaluated against its declared mode:

- **Background**: Explanation mode — discursive, answers "why"
- **Install**: How-to mode — imperative, goal-oriented, efficient
- **Usage**: Tutorial mode — guaranteed success path, no branching
- **API**: Reference pointer — link to exhaustive docs elsewhere
- **Contributing**: How-to mode — imperative policy
- **License**: Reference mode — neutral, factual

The Diátaxis Mode Clarity gate checks each section against its expected mode.

## Sources

- [Standard README spec (RichardLitt)](https://github.com/RichardLitt/standard-readme/blob/main/spec.md) — required sections and order
- [The Good Docs Project — README template](https://www.thegooddocsproject.dev/template) — Diátaxis-aligned alternative
- [Trong-Tra/agent-skills `documentation-specialist`](https://github.com/Trong-Tra/agent-skills/tree/main/documentation-specialist) `readme/SKILL.md` — 30-Second Test, One-Liner Formula, Quickstart Patterns, Feature Communication, Configuration Documentation, Troubleshooting Section, Badge Strategy, README Length Guide, Language-Specific Conventions, Common Pitfalls (all adapted to docs-team's prose style)
