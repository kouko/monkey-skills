# Write README Protocol (Composite: Standard README + Diátaxis)

Write a README.md file following the Standard README specification
(RichardLitt). README is a **composite** document — each section maps to
a different Diátaxis quadrant, but the Standard README spec determines
the structural order and required sections.

**Spec source**: [github.com/RichardLitt/standard-readme](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
**Vocabulary reference**: `standards/diataxis-taxonomy.md`
**Style reference**: `standards/style-conventions.md`
**Pre-writing reference**: `standards/pre-writing-checklist.md` — apply before Phase 0

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

- Named with BCP 47 tags: `README.ja.md`, `README.zh-CN.md`
- Linked from the main README at the top: "Read this in: [English] | [日本語] | [中文]"
- Translations kept in sync when the main README changes (track via
  `last_reviewed` in frontmatter)

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

## Examples

### Example 1: Small Go library (~30 lines)

```markdown
# isoduration

Parse and format ISO 8601 durations in Go. Supports `P3Y6M4DT12H30M5S`
and all valid subsets.

[![Go Reference](https://pkg.go.dev/badge/github.com/org/isoduration.svg)](https://pkg.go.dev/github.com/org/isoduration)

## Install

​```bash
go get github.com/org/isoduration
​```

## Usage

​```go
package main

import (
    "fmt"
    "github.com/org/isoduration"
)

func main() {
    d, _ := isoduration.Parse("P1Y2M3DT4H5M6S")
    fmt.Println(d.Days()) // 428
}
​```

## Contributing

PRs welcome. Run `go test ./...` before submitting.

## License

MIT
```

**Why this works**: 30 lines. One example. Clear scope. Required sections
(Title / Short description / Install / Usage / Contributing / License) all
present, in order, License last. No fluff.

### Example 2: Full-stack application (~70 lines)

```markdown
# Taskflow

> Self-hosted task management with real-time collaboration. Designed for
> teams of 5-50 who outgrew spreadsheets but do not need enterprise
> complexity.

![Build](https://img.shields.io/github/actions/workflow/status/org/taskflow/ci.yml)
![License](https://img.shields.io/github/license/org/taskflow)

## Background

Built because existing tools either cost too much per seat or required a
SaaS dependency we did not want.

## Quickstart

Prerequisites: Docker, Docker Compose

​```bash
git clone https://github.com/org/taskflow.git
cd taskflow
docker-compose up
​```

Open http://localhost:8080. Default login: `admin@example.com` / `changeme`.

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `JWT_SECRET` | Yes | — | Min 32 characters |
| `PORT` | No | `8080` | HTTP server port |

## Architecture

See `docs/architecture.md` for component overview and data flow.

## Contributing

See `CONTRIBUTING.md`. All changes require tests.

## License

GPL-3.0
```

**Why this works**: Quickstart is one command (`docker-compose up`).
Configuration is a table, not prose. Architecture and Contributing are
linked, not inlined. License last.

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
