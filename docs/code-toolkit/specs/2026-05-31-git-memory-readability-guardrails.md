# Brief — git-memory readability guardrails for trailer values + `## Memory`

Date: 2026-05-31 · Stage: brainstorming output → `writing-plans`
Target: `dev-workflow:git-memory` (NOT code-toolkit — git-memory is a dev-workflow skill).

## Problem (Axis 1 — JTBD)

git-memory's commit trailers (`Decision:` / `Learning:` / `Gotcha:`) drift in practice
toward (a) **dense multi-clause run-ons** and (b) **session-ephemeral jargon** ("P2",
"redundancy-trap pair", "SPLIT ensemble verdict"), making them hard to **scan in
`git log`** and **opaque to a reader who wasn't in the session**. The convention
currently *tolerates* this — it caps `Decision:` at "1-3 sentences" but has no
scannability rule, and its line-length allowance (soft 100 / **hard 250**) actively
permits a 250-char single-value run-on. Job: a future developer doing git archaeology
should grasp each trailer in one scan, without having been in the room.

## Users (Axis 2)

- **The reader = a future developer doing `git log` / PR archaeology** — often kouko
  himself months later (cold), sometimes a teammate. **Technical**, **shares the
  codebase's domain vocabulary**, but does **NOT** share terms coined inside a single
  session/PR. This audience is DIFFERENT from asking-the-user's "warm interrupted human
  deciding in chat" — see Decision for why that matters.

## Smallest End State (Axis 3)

Add **two audience-calibrated readability guardrails** to `git-memory`'s convention
(`standards/memory-conventions.md`, where the format rules live), + one before/after
worked example:

1. **Scannability** — a trailer value leads with its point in the **first clause**;
   elaboration goes to an **RFC-822-folded continuation line** (the convention already
   supports folding), not a breathless multi-clause run-on. Reframe the existing
   "1-3 sentences" (currently `Decision:`-only) as a **general scannability rule across
   all trailer types**, and add a caveat that the hard-250 line-length is a ceiling, not
   a target — if a value needs 250 chars it probably needs folding or splitting.
2. **Expand session-ephemeral jargon** — a trailer must be legible to a reader who was
   NOT in the session: expand or avoid one-off coinages ("P2", cluster names, session-
   local labels). **Shared codebase / domain terms are fine** (the existing good example
   uses `gws` correctly). This is the audience-calibrated form of "translate jargon."

> **Dropped — diagram venue (was guardrail 3):** the user asked to add ASCII-commit /
> Mermaid-PR diagram guidance, but recon (plan-document-reviewer round 2) found
> `memory-conventions.md` **already has a complete `## Diagram venue` section** (venue
> table + decision tree: ASCII-commit / Mermaid-PR-only / only-when-arch-flow-state /
> "specialized tool, not default"). The request was already 100% implemented → nothing
> substantive to add → guardrail 3 dropped. (Recon lesson: read the section before
> treating a one-line mention as a stub.)

Plus a **before/after worked example** (a real dense+jargon trailer → scannable form).

## Current State Evidence

- `dev-workflow/skills/git-memory/standards/memory-conventions.md`:
  - §Commit trailers table — `Decision:` "Why…, **1-3 sentences**"; `Learning:` "Something
    discovered…a **future reader** would want to know." (the why-focus is right; no
    scannability/jargon rule).
  - §Format rules — line length "**soft 100, hard 250**" + RFC-822 folding example
    (folding exists but isn't tied to a scannability rule; 250 tolerates run-ons).
  - Good/bad examples ban what-not-why / vague / ALL-CAPS / redundant-with-diff — but
    NOT density or ephemeral-jargon.
- Real evidence (this session's own merged trailers, `git log` monkey-skills):
  - Dense run-on: `Learning: a 3x3 variance re-test distinguished a position-induced
    regression from generation noise on the ambiguous exemption-boundary prompt (P2)…`
    (60+ words, multi-clause, "(P2)" unexpanded).
  - Gold standard (already good): `Gotcha: gws flag -s is a service filter, not a scope
    specifier; use --scopes=<URL> for scope elevation.` (scannable, self-contained).
- `dev-workflow/skills/git-memory/SKILL.md` frames trailers as "machine-readable" — true,
  but human scannability in `git log` is the complementary need this brief addresses.

## Decision

Add the two guardrails (scannability + expand-session-ephemeral-jargon) + a worked
example to `memory-conventions.md`, calibrated for git-memory's **future-developer**
audience. (A proposed third "diagram venue" guardrail was dropped — already fully
present in the existing `## Diagram venue` section; see Smallest End State note.) **Explicitly do NOT import code-toolkit's asking-the-user three-gate / plain-
language rules** — that audience (cold human deciding in chat) differs, and key rules
mis-transfer: `outcome-not-mechanism` is *wrong* for a trailer (its content IS the
why/mechanism); `state-anchor-inside-question-field` has no analog; gates ① (whether to
ask) and ② (bring a recommendation) don't apply (git-memory writes, doesn't ask).
Importing wholesale would be the reader-audience-inheritance bug
([[feedback_dogfood_revealed_reader_audience_inheritance]]). Only the audience-invariant
core transfers: scannable / self-contained / numbers-carry-meaning / expand-the-jargon-
your-reader-doesn't-share — which is exactly these two guardrails.

## Alternatives Considered (Axis 4 — industry, EN + JA agree)

Readable-commit canon: [Chris Beams "How to Write a Git Commit Message"](https://cbea.ms/git-commit/)
(50/72, imperative subject, **body explains what & why, not how**), Google CL descriptions
(first line summary + why), Conventional Commits; JA mirror ([みんなシステムズ](https://minna-systems.co.jp/blogs/3077/),
[Qiita translation](https://qiita.com/siida36/items/ed3103e27e0f6ac531f2)) — 件名≤50 命令形,
本文 why+what, 「code/docs に表れない、簡潔に伝える」. The invariant: **subject = scannable
one-liner; body = self-contained why.** Note: the **50/72 subject rule is OUT of git-memory's
scope** — git-memory owns trailer VALUES + the PR `## Memory` section, not the commit subject
line (that's general commit writing / the repo's Conventional-Commits prefix). So we apply the
"scannable + self-contained why" core to trailer values, not the subject-length rule.

## What Becomes Obsolete (Axis 5)

Nothing removed. The `Decision:`-only "1-3 sentences" generalizes to all trailer types as
"scannability"; the hard-250 line-length gains a "ceiling-not-target / prefer folding"
caveat. Both are tightenings, not removals.

## Dual-consumer invariant (REQUIRED — protects agent retrieval)

git-memory content has TWO consumers: the human archaeologist AND a future **agent**
doing `git log --grep='^Decision:'` retrieval / the Phase-3 digest rebuild
(`git log --trailer` + PR `## Memory`). The readability guardrails MUST NOT degrade
the machine/agent consumer. Enforced invariants:

1. **Restructure, do NOT truncate.** "Scannable" = point-first + elaboration folded to
   continuation lines; it must NOT mean "shorter / fewer facts." All retrievable signal
   is preserved (reordered, not removed). An implementer/reviewer who shortens a trailer
   by dropping detail has violated this.
2. **Keep the machine contract intact.** Trailer KEYS stay line-anchored (`Decision:` at
   line start → `git log --grep='^Decision:'` still matches); continuation uses standard
   RFC-822 folding (leading space) so `git interpret-trailers` / `%(trailers)` unfold the
   value correctly. The guardrails change wording/structure, never the key vocabulary or
   the folding mechanism.
3. **Net effect on the agent consumer is neutral-to-positive**: expanding session-
   ephemeral jargon (guardrail 2) HELPS the retrieving agent, which — like the cold human
   — was not in the session and cannot resolve one-off coinages. Self-containment serves
   both consumers identically.

The plan must carry these as explicit acceptance/review checks (the change is a NET WIN
for agent retrieval only if #1 and #2 hold).

## Out of Scope

- **Commit subject line** (50/72, Conventional-Commits prefix) — general commit writing,
  not git-memory's scope.
- **Importing asking-the-user gate ③ rules wholesale** — audience mismatch (see Decision).
- **The git-memory enforcement hook** (Phase-2 reminder-before-commit) — that's a separate
  *invocation/enforcement* concern; this brief is about *writing quality of the output*.
- code-toolkit's own skills — unaffected.

## Open Questions

1. Version bump: dev-workflow minor (current ~2.13.x → 2.14.0?) — confirm actual current
   version at plan time.
2. Placement: guardrails belong in `standards/memory-conventions.md` (format rules home);
   confirm whether a one-line pointer in `SKILL.md` Pillar-2 is also warranted.
3. Behavioral validation = doc-prose, grep-diagnostic + dogfood; confirm the scannability
   caveat doesn't contradict the existing soft-100/hard-250 line-length (it qualifies it,
   not conflicts).
