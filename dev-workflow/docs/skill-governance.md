# Skill Governance

How dev-workflow's family of skills is governed: who owns what,
how conventions evolve, when skills retire, and how cross-plugin
contracts are enforced.

This document is the operational counterpart to
`skill-evolution-architecture.md` (which planned the H1–H4
horizons). Where the architecture doc says *what* the family looks
like, this doc says *how it stays healthy over time*.

---

## SSOT Registry

For each shared resource, exactly one location is the canonical
Source of Truth (SSOT). Functional copies elsewhere are managed
via the same-PR drift rule.

### dev-workflow internal SSOT

| Convention / Resource | Canonical Location | Functional Copies | Enforced By |
|---|---|---|---|
| `golden-anchor-protocol` | `skills/skill-refactor/references/golden-anchor-protocol.md` | `skills/skill-tasting/references/golden-anchor-protocol.md` | `scripts/check-shared-conventions-drift.py` (CI) |
| `test-prompts-schema` | `skills/skill-refactor/references/test-prompts-schema.md` | `skills/skill-tasting/references/test-prompts-schema.md` | `scripts/check-shared-conventions-drift.py` (CI) |
| `constitution-schema` | `skills/skill-refactor/references/constitution-schema.md` | `skills/skill-tasting/references/constitution-schema.md` | `scripts/check-shared-conventions-drift.py` (CI) |
| Multi-judge ensemble protocol | `skills/skill-refactor/references/multi-judge-ensemble.md` | (none — skill-refactor specific) | none needed |
| Refactor moves catalog | `skills/skill-refactor/references/refactor-moves-catalog.md` | (none — skill-refactor specific) | none needed |
| Equivalence check protocol | `skills/skill-refactor/references/equivalence-check-protocol.md` | (none — skill-refactor specific) | none needed |
| AB harness protocol | `skills/skill-tasting/references/ab-harness-protocol.md` | (none — skill-tasting specific) | none needed |
| Constitutional judging | `skills/skill-tasting/references/constitutional-judging.md` | (none — skill-tasting specific) | none needed |
| Preference log schema | `skills/skill-tasting/references/preference-log-schema.md` | (none — skill-tasting specific) | none needed |
| Self-trained judge pipeline | `skills/skill-tasting/references/self-trained-judge-pipeline.md` | (none — skill-tasting specific) | none needed |
| Architecture planning doc | `dev-workflow/docs/skill-evolution-architecture.md` | (none — single canonical) | none needed |

### Cross-plugin SSOT

| Convention | Canonical Location | Notes |
|---|---|---|
| Mindset standards (4) | `domain-teams:code-team/standards/mindset-*.md` | Functional copies in dev-workflow:complexity-critique/references/. PR #159 precedent. |
| Mindset extension policy | `domain-teams:code-team/standards/mindset-extension-standard.md` | Single SoT |

---

## Ownership

Each skill has an **owner** responsible for its lifecycle:

| Skill | Owner | Notes |
|---|---|---|
| `skill-creator-advance` | kouko (with AllanYiin upstream attribution) | MIT chain in NOTICE |
| `skill-judge` | kouko (with Leonardo Flores upstream attribution) | MIT chain in NOTICE |
| `git-memory` | kouko | original |
| `proposal-critique` | kouko | original |
| `complexity-critique` | kouko (with joshuadavidthomas/softaworks lineage) | MIT chain in NOTICE |
| `skill-refactor` | kouko | original design (darwin-skill inspiration only) |
| `skill-tasting` | kouko | original design (darwin-skill inspiration only) |

Ownership transfers require:
1. Update LICENSE / NOTICE to reflect new owner
2. Update plugin README ownership tables
3. Update this governance doc registry

---

## Skill Lifecycle States

A skill is always in exactly one of these states:

| State | Definition | Transition criteria |
|---|---|---|
| **Active** | Production-quality; expected to be invoked | New skills land here; default |
| **Deprecated** | Still works but newer alternative recommended | Owner declares; description gains "Use newer-skill instead" not-trigger; subsequent PRs may strip its slash command |
| **Retired** | No longer maintained / removed in next release | Was deprecated for ≥3 months OR explicit decision; removal is breaking change → major version bump |

Annotation in plugin README:

| Skill | State | Since |
|---|---|---|
| skill-creator-advance | Active | 2026-04-13 |
| skill-judge | Active | 2026-04-29 (v1.4.0) |
| git-memory | Active | 2026-04 |
| proposal-critique | Active | 2026-04-25 (v1.3.0) |
| complexity-critique | Active | 2026-04-29 (v1.5.0) |
| skill-refactor | Active | 2026-04-29 (v1.6.0) |
| skill-tasting | Active | 2026-04-29 (v1.7.0) |

(Updated on state transitions; default Active.)

---

## Convention Evolution Protocol

### Adding a new shared convention

1. Identify the need (e.g., a new pattern shared by 2+ skills)
2. Pick canonical SSOT location (typically the skill that uses it
   most, or the first to ship)
3. Write the convention as a reference file in canonical location
4. For each skill that consumes it, copy as functional copy with
   header blockquote pointing to canonical
5. Update `scripts/check-shared-conventions-drift.py`
   `SHARED_CONVENTIONS` manifest to include the new pair
6. Update this governance doc's SSOT Registry section
7. Verify drift CI passes locally

### Editing an existing shared convention

1. **Edit canonical location first**
2. Mirror to all functional copies in the **same PR**
3. CI gate enforces this via `check-shared-conventions-drift.py`
4. Update header blockquote on canonical/copies if SSOT location
   itself moves (rare; requires explicit governance decision)

### Deleting a shared convention

1. Migration path required if any skill depends on the convention
2. Each consuming skill updates SKILL.md / references to no
   longer use the convention
3. Once no skill depends, delete from canonical + all functional
   copies + drift manifest in same PR

---

## Cross-Plugin Contract

Per repo-level `CLAUDE.md` §Cross-Plugin Delegation Contract:

- Plugin-A consuming Plugin-B's resources passes paths, not content
- Single source of truth lives in the authority plugin
- Cross-plugin runtime dependency is acceptable when consumer
  explicitly signals it (e.g., complexity-critique's mindset
  references)
- For zero-runtime-dependency cases, use SSOT-and-functional-copy
  (PR #159 precedent)

dev-workflow internal cross-skill follows the same contract. The
Two-Hats split (skill-refactor / skill-tasting) shares 3
conventions via SSOT-and-functional-copy specifically to preserve
runtime independence (each skill installable / runnable without
the other).

---

## Versioning Policy

Per Semantic Versioning (https://semver.org):

| Bump type | When |
|---|---|
| **Major** | Breaking change to skill behavior, removal of skill, removal of slash command, retirement of public protocol |
| **Minor** | New skill, new convention, new optional feature |
| **Patch** | Bug fix, documentation correction, internal-only refactor |

Examples from dev-workflow history:

- v1.5.0 (PR #159): added complexity-critique → minor
- v1.6.0 (PR-2): added skill-refactor → minor
- v1.7.0 (PR-3): added skill-tasting → minor
- (future) v2.0.0: would be reserved for a breaking change such as
  removing skill-creator-advance description optimization or
  dropping a slash command

Each bump must be accompanied by a corresponding CHANGELOG.md
entry in Keep a Changelog format.

---

## Audit and Review Cadence

Quarterly audits review:

1. **Active skills** — still aligned with current use? Any drift?
2. **Deprecated skills** — ready for retirement? Or should
   deprecation be reversed?
3. **Convention SSOT** — any drift not caught by CI?
4. **External dependencies** — upstream MIT chains still intact?
   New skills derived from external sources properly attributed?
5. **Validation gates outstanding** — skill-refactor / skill-tasting
   still need formal dry-run validation per architecture doc §6;
   audit checks whether validation has been performed

See `dev-workflow/docs/quarterly-audit-runbook.md` for the
operational checklist.

---

## Decision Authority

| Decision Type | Required Authority |
|---|---|
| Add new skill | Plugin owner (kouko) |
| Modify existing skill scope | Plugin owner |
| Change convention SSOT location | Plugin owner + update governance doc |
| Retire skill (Deprecated → Retired) | Plugin owner; >3 month deprecation; major version bump |
| Cross-plugin reorganization | Plugin owner + affected plugin owners |

---

## README Authoring Discipline

dev-workflow follows the repo-wide convention that **skill-internal
READMEs do not require the `docs-team` workflow**. They are written
directly by the skill author against a lighter rule set (language
switcher, English-noun-preservation, no contradiction with `SKILL.md`,
upstream attribution if derivative).

The full convention lives in
`domain-teams:skill-team/standards/file-conventions.md` §Skill-Internal
README Authoring Discipline. dev-workflow inherits that convention.

The 7 dev-workflow skills (skill-creator-advance / skill-judge /
git-memory / proposal-critique / complexity-critique / skill-refactor
/ skill-tuning) follow this lighter discipline. Dev-workflow's
plugin-level READMEs (`dev-workflow/README.{md,ja.md,zh-TW.md}`)
should be authored / updated via `docs-team` per the same convention,
since they are plugin-level not skill-internal.

When a skill-internal README needs significant restructuring (e.g.,
adding architecture-doc-grade content, splitting into Diátaxis
modes), that's a signal it should be promoted to a docs-team
artifact — typically by extracting content into a separate
`docs/` file at plugin level rather than enlarging the
skill-internal README beyond its lighter-discipline scope.

## Anti-Patterns

| Anti-pattern | Why bad |
|---|---|
| Editing a functional copy without updating canonical | Drift; CI catches if drift script is in CI |
| Adding new skill without specifying lifecycle state | Defaults to Active by convention; explicit > implicit |
| Removing slash command without deprecation period | Breaking change; users with stale references confused |
| Skipping NOTICE / LICENSE for derivative skills | Attribution chain breaks; legal compliance risk |
| Letting validation gates remain OUTSTANDING indefinitely | Architecture doc §6 lists validation gates per phase; deferring forever defeats the purpose |
| Not running `check-shared-conventions-drift.py` locally before push | CI catches but developer time wasted on flagging push |
