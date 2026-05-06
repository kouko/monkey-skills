# Glossary Format Spec (Project-Level Override)

This document specifies the canonical pair-file schema used by
translation-toolkit. Authoring a project-level glossary at
`<your-repo>/docs/i18n/glossary-{target-locale}.md` lets you override the
bundled (L2) glossary entries shipped with this plugin.

## 1. Purpose

translation-toolkit resolves terminology through a 4-tier fallthrough chain:

```
L1 project glossary  (your repo, highest priority)
   ↓
L2 bundled glossary  (this plugin, vendor-attributed)
   ↓
L3 web search        (runtime, when L1+L2 miss)
   ↓
L4 LLM fallback      (last resort, flagged for review)
```

This spec covers **L1 authoring**: how to write a project glossary file that
the toolkit will recognize and prefer over the bundled entries.

## 2. File Naming

Files are named:

```
glossary-{lang-A}--{lang-B}.md
```

Rules:

- `lang-A` and `lang-B` use **BCP-47** tags (`en-US`, `ja-JP`, `zh-TW`, etc.).
- The two tags are **alphabetically sorted** (lowercase compare).
- Separator is a **double hyphen** (`--`).

Examples:

```
glossary-en-US--ja-JP.md
glossary-en-US--zh-TW.md
glossary-ja-JP--zh-TW.md
```

## 3. Frontmatter Schema

Each file MUST start with a YAML frontmatter block:

```yaml
---
pair: [en-US, ja-JP]            # BCP-47, alphabetical
version: 0.1.0                  # SemVer for the glossary file itself
sources: [project-glossary]     # provenance hint; free-form list
domains_supported: [general, ui, tech.software]
---
```

Field rules:

| Field               | Required | Notes                                           |
|---------------------|----------|-------------------------------------------------|
| `pair`              | yes      | Two BCP-47 tags, alphabetical order.            |
| `version`           | yes      | SemVer string. Bump on every published change.  |
| `sources`           | yes      | Provenance markers; `project-glossary` is fine. |
| `domains_supported` | yes      | Subset of the 13 domains (see §6).              |

## 4. Body Structure

After the frontmatter, the body is organized as:

```markdown
## meta

(Optional typography rules, punctuation conventions, capitalization
preferences. Plain prose or short bullets.)

## domain: general

(One table per domain section, using the schema in §5.)

## domain: ui

(...)

## domain: tech.software

(...)
```

- A `## meta` section is **optional** but recommended for typography overrides.
- Each domain gets its own `## domain: <name>` section.
- Domain section names MUST match the 13-domain taxonomy in §6.

## 5. Table Format

Each domain section contains a 4-column table:

| `<lang-A>`              | `<lang-B>`              | source            | notes                          |
|-------------------------|-------------------------|-------------------|--------------------------------|
| Term in language A      | Term in language B      | provenance marker | optional disambiguation/usage  |

Example (en-US ↔ ja-JP, domain: tech.software):

```markdown
## domain: tech.software

| en-US      | ja-JP        | source            | notes                              |
|------------|--------------|-------------------|------------------------------------|
| repository | リポジトリ   | project-glossary  | preserve katakana; do not 倉庫     |
| commit     | コミット     | project-glossary  | verb form: コミットする            |
| pull request | プルリクエスト | project-glossary | abbrev OK: PR (英字保持)         |
```

## 6. 13-Domain Taxonomy

The toolkit recognizes these domain values:

1. `general`           — everyday vocabulary
2. `ui`                — UI labels, buttons, microcopy
3. `tech.software`     — software engineering / SDK / API
4. `tech.hardware`     — hardware / electronics / chips
5. `tech.ai-ml`        — AI / ML / data science
6. `business`          — business / finance / accounting
7. `legal`             — legal / contracts / compliance
8. `medical`           — medical / clinical
9. `academic`          — academic / scholarly
10. `creative`         — creative / literary / narrative
11. `marketing`        — marketing / advertising
12. `government`       — government / public sector
13. `media`            — media / journalism / broadcasting

A glossary file may declare any subset in `domains_supported`, but section
names MUST come from this list.

## 7. Cross-Language Pivot Rule

When the toolkit needs a pair that has no direct file (e.g. `ja-JP ↔ ko-KR`
when only `en-US ↔ ja-JP` and `en-US ↔ ko-KR` exist), it will:

1. Check for a direct pair file (`glossary-ja-JP--ko-KR.md`).
2. If absent, **pivot through `en-US`**: look up `ja-JP → en-US`, then
   `en-US → ko-KR`.
3. If the pivot produces an entry, the toolkit emits it with a
   `via_pivot: en-US` note for reviewer awareness.
4. If pivot fails, fall through to L3 (web search) and finally L4 (LLM).

You can suppress pivot for a sensitive term by adding a direct pair file with
a `notes: do-not-pivot` marker in the row.

## 8. Example Starter Template

Copy this into `<your-repo>/docs/i18n/glossary-en-US--ja-JP.md` and edit:

```markdown
---
pair: [en-US, ja-JP]
version: 0.1.0
sources: [project-glossary]
domains_supported: [general, ui, tech.software]
---

## meta

- Preserve English technical nouns; do not over-translate to kanji.
- Use 全角 punctuation in Japanese body text.
- Keep product names in their original capitalization.

## domain: general

| en-US     | ja-JP      | source           | notes                |
|-----------|------------|------------------|----------------------|
| user      | ユーザー   | project-glossary | not 利用者 in UI     |
| feature   | 機能       | project-glossary |                      |

## domain: ui

| en-US     | ja-JP      | source           | notes                |
|-----------|------------|------------------|----------------------|
| Save      | 保存       | project-glossary | imperative           |
| Cancel    | キャンセル | project-glossary |                      |
| Delete    | 削除       | project-glossary | imperative           |

## domain: tech.software

| en-US        | ja-JP            | source           | notes                       |
|--------------|------------------|------------------|-----------------------------|
| repository   | リポジトリ       | project-glossary | preserve katakana           |
| commit       | コミット         | project-glossary | verb: コミットする          |
| pull request | プルリクエスト   | project-glossary | abbrev: PR (英字保持)       |
| branch       | ブランチ         | project-glossary |                             |
| merge        | マージ           | project-glossary | verb: マージする            |
```

## See Also

- `../NOTICES.md` — bundled (L2) glossary source attributions
- `architecture.md` — full toolkit architecture overview
- `../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` —
  full design spec (Decision #10, #11, #14)
