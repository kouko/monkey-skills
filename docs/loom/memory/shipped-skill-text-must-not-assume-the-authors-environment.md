---
name: shipped-skill-text-must-not-assume-the-authors-environment
description: A skill authored from a personal design note inherits that note's ENVIRONMENT, not just its vocabulary — the tool the author happens to keep their files in becomes a stated premise ("typically inside their Obsidian vault") and, worse, the JUSTIFICATION a mechanical rule cites ("matching the vault's own writing convention"). Neither survives contact with a user who does not have that tool: the premise is merely noise, but the justification points at nothing, so a cold reader cannot check whether the rule applies to them. Grep the shipped text for every proper noun naming a tool, vault, directory layout, or house convention that is the AUTHOR's rather than the PRODUCT's, and either delete it or state the rule without borrowed authority.
type: practice
origin: think-orbit 0.1.3 (2026-08-19) — the user, reading the installed 0.1.2, asked 「我發現當前 think orbit 有一段關於把產生的檔案放在 Obsidian Vault 的敘述？」 and ruled 「這個 plugin 不應該以 有 Obsidian vault 為前提」; three references had shipped through a full SDD arc, three review rounds, a whole-branch review and a behavioral dogfood without any of them flagging it
---

think-orbit's design SSOT was a set of notes in the user's own Obsidian
vault, and the vault came along into the shipped contract in two shapes.

The first was **descriptive**: `<root>` was "a folder the user owns,
typically inside their Obsidian vault", and the node-schema invariant
repeated the parenthetical. Harmless in effect — the intake ladder never
defaults to a vault path and explicitly forbids inventing one — but it is
still an unearned prior about how the reader lives.

The second was **load-bearing prose**: the `paragraph-form` rule (2–4
sentences per body paragraph) justified itself as "matching the vault's
own writing convention". That rule runs in every project, including ones
with no vault at all. For those readers the justification has no referent,
so the one question they need answered — *does this rule apply to me, and
why this number?* — is unanswerable from the text. A rule whose stated
reason is unverifiable reads as either arbitrary or as evidence the tool
was not built for them.

**Why it survived everything:** no gate looks for this. Tests exercise
`dag.py`, whose behavior is correct and vault-free; the skill-structure
check validates layout; per-task and whole-branch reviews compare the
artifact against a spec that was itself written from the same vault notes,
so the premise is invisible from inside — reviewer and spec share it. The
behavioral dogfood measured triggering and workflow, not whether the prose
assumes a world. It took the first real user reading the installed plugin.

**How to apply:**
1. Before shipping any skill authored from a personal design note, grep
   the whole plugin for proper nouns naming the author's own tooling,
   vault, directory layout, or house conventions (`Obsidian`, `vault`, a
   specific app name, a private repo path). Every hit is a candidate.
2. Separate the two shapes, because they need different fixes. A
   descriptive aside is deleted. A rule that BORROWS the environment as
   its rationale must either state the rule on its own authority — the
   rule was checkable without it here, so the clause simply went — or
   earn a rationale that holds for any reader.
3. Do not replace a deleted rationale with an invented one. "Because the
   author's notes do it this way" is bad; a freshly made-up justification
   is worse, because it cannot be traced to anything either.
4. This is the same leak as [[entry-triggers-follow-the-purpose-not-the-most-concrete-verb]]
   one layer down: there the design note's worked EXAMPLE narrowed the
   entry vocabulary; here the design note's ENVIRONMENT became a premise.
   When one is found, grep for the other — a plugin written from a
   personal SSOT tends to carry both.
