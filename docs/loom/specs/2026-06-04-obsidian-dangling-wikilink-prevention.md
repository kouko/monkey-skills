# Brief — Obsidian dangling-wikilink prevention (authoring-time)

- Date: 2026-06-04
- Owner: kouko
- Stage: brainstorming → writing-plans
- Scope decision (user-locked): **L1 + L2 + L4 prevention only**; L3 detection/backfill explicitly out.
- Process: full SDD.

## Problem

(Axis 1 — JTBD) When the user generates notes in Obsidian through these skills, the
generated notes frequently contain `[[wikilinks]]` whose target note **does not exist in
the vault**. Obsidian renders these as click-to-create placeholders. The user dislikes the
click-to-create workflow and wants notes to be authored such that **every emitted wikilink
already resolves to a real note** — no dangling links produced at authoring time.

Job story: *When a skill (or Claude) authors an Obsidian note on my behalf, I want every
`[[link]]` it writes to point at a note that already exists, so I never inherit a graph of
phantom placeholders I have to either create or clean up later.*

## Users

(Axis 2) Single user (kouko), Traditional-Chinese/Japanese/English vault at
`/Users/kouko/kouko-obsidian-vault` (9,056 notes, 29,199 wikilinks). Notes are produced by
the `obsidian` plugin skills and by direct Claude authoring. The user is the sole curator and
does not want a forward-linking (先行リンク) graph; they want a clean, fully-resolved link set.

## Current State Evidence

Empirical scan (all paths relative to repo root unless noted; vault paths absolute):

- **Forward (who generates dangling links):** custom scan of the live vault found **899 dangling
  occurrences / 668 unique targets**, distributed: `wiki/` 527 (59%), `research/` 175, `daily/`
  114, `investing/` 29, `references/` 19, `reading_list/` 16, `projects/` 16. Three distinct
  source classes:
  - **S1 wiki pipeline** — `obsidian/skills/wiki-ingest/SKILL.md:190` (`## Connections — add
    new wikilinks if discovered`) and `obsidian/skills/wiki-ingest/references/page-format.md:198-201`
    (Connections spec: `- [[OtherWikiPage]] — one-line reason` / **`At least 1 [[wikilink]]
    required`**). No inventory/existence check before emitting `[[…]]`. → 527 dangling.
  - **S2 general note authoring** — `obsidian/skills/obsidian-markdown/SKILL.md:17-25`
    ("Internal Links (Wikilinks)", `[[Note Name]] — Link to note`) has **no existence rule**;
    `obsidian-markdown/SKILL.md:8,20` only distinguish wikilink-vs-markdown-link.
  - **S3 manual / template** — `obsidian/skills/obsidian-daily/` emits **no** wikilinks (grep
    empty) → the 114 `daily/` + `projects/` danglers are **user-/template-authored**, not
    skill-driven. **No skill change can prevent these** (out of scope — see Out of Scope).
- **Reverse (existing safe seam / SSOT ownership):** `obsidian/skills/wiki-cross-linker/SKILL.md:8`
  ("finds plain-text mentions of **existing** page titles, converts to `[[wikilinks]]`") +
  `:127` ("Does not create new pages (only links to existing ones)"). `wiki-ingest/SKILL.md:335`
  already instructs the user to run `wiki-cross-linker` next → the **promotion seam already
  exists**: ingest can write plain text and cross-linker upgrades it once the page exists.
  There is **no shared wikilink-rule SSOT** — `obsidian-markdown` is a peer in the router table
  (`using-obsidian/SKILL.md:35`), not an inherited base; each skill owns its own format spec.
- **Error (what enforcement exists):** `wiki-ingest/SKILL.md:200-203` is an **enforced grep gate**
  (backtick-wrapped-wikilink check — advisory self-check + enforced grep). `wiki-lint`
  `references/lint-checks.md:58-66` L07 detects broken wikilinks **after the fact**, wiki-scope
  only. No authoring-time existence gate anywhere.
- **Data (link shapes that must be EXEMPTED from any rule):** same-note heading links
  `[[#Heading]]` (`obsidian-markdown/SKILL.md:9-12,24`) and reference-page `## Source`
  cross-layer links (`wiki-lint` L07 exemption, `lint-checks.md:66`; resolve via bare-basename
  to non-`wiki/` source files) always resolve and **must not** be downgraded.
- **Boundary (L4 touch point):** `wiki-auto-research/references/research-note-format.md:29-31`
  `source_pages: [[…]]` reference **pages that surfaced the questions → they exist** (leave
  as-is); `:69` `(Optional) Create new page: [[new-concept]]` is an intentional **future** page
  → this is the dangling-generating line; `:125` shows `wiki-ingest` consumes this block as a
  machine-read creation instruction.

Evidence paths appendix:
- `/Users/kouko/kouko-obsidian-vault` (live vault, scanned read-only)
- `obsidian/skills/wiki-ingest/SKILL.md`, `…/references/page-format.md`
- `obsidian/skills/obsidian-markdown/SKILL.md`
- `obsidian/skills/wiki-auto-research/references/research-note-format.md`
- `obsidian/skills/wiki-cross-linker/SKILL.md`, `obsidian/skills/wiki-lint/references/lint-checks.md`

## Smallest End State

(Axis 3) One authoring rule, applied in three places, plus the spec edits that rule forces:

**The rule:** *When authoring an Obsidian note, only emit `[[Target]]` if `Target` already
resolves to an existing note in the vault (bare-basename match, incl. frontmatter aliases).
Otherwise write the term as plain bold text (`**Target**`) with its relationship reason. Never
emit a wikilink solely to create a placeholder.* **Exempt:** same-note `[[#Heading]]` / block
links, and reference-page `## Source` cross-layer links — these always resolve.

- **L1 `wiki-ingest`** — `## Connections` links only inventory-resolved targets; unresolved
  related entities become plain-text candidates (kept, with reason) for `wiki-cross-linker` to
  promote later. Relax `page-format.md:201` / `SKILL.md:345` from "≥1 **wikilink** required" to
  "≥1 **connection** (link if the page exists; else plain-text candidate + reason)" — preserves
  the force-semantic-linking intent without forcing a dangling link.
- **L2 `obsidian-markdown`** — add the rule as an authoring guardrail in §Internal Links, with
  the same-note-heading exemption called out explicitly.
- **L4 `wiki-auto-research`** — `research-note-format.md:69` reframes the "create new page"
  recommendation to a **non-link** form (plain text / inline code), so the machine-read creation
  instruction no longer leaks a dangling `[[…]]` into `research/`. `source_pages` (`:29-31`)
  unchanged (resolved by construction).

## Decision

We will add a single "link-only-existing, else plain-text" authoring rule and apply it to the
three skill-authoring sources the user selected (L1 wiki-ingest, L2 obsidian-markdown, L4
wiki-auto-research), including the forced spec edit to wiki-ingest's "≥1 wikilink required"
Connections rule and the same-note-heading / `## Source` exemptions. We will **not** build
whole-vault detection or backfill the existing 899 danglers (L3 declined). Prevention is
instruction-based; whether to also add an enforced write-time inventory gate to wiki-ingest
(mirroring the existing backtick grep gate) is an Open Question for the plan.

## Out of Scope

- **L3 whole-vault broken-link detection / cleanup** (extending `wiki-lint` to whole-vault, or
  the `obsidian-vault-organizer` agent) — declined this round.
- **Backfilling the existing 899 dangling links** — not touched.
- **S3 user-/template-authored manual notes** (`daily/`, `projects/`) — no skill can prevent
  these at authoring time; only L3 detection would help, and L3 is out.
- Other obsidian skills that author notes (`obsidian-file-intel`, `obsidian-tldr`, dashboards) —
  not in the selected layers; revisit if they prove to be material sources.
- Changing Obsidian's own settings (Markdown-link mode) — vault-config, not a skill change.

## Alternatives Considered

(Axis 4 — WebSearch EN + JA)

1. **Inventory-gated linking (only link existing; else plain text)** — EN best practice for
   auto-generated notes. [XDA: "I added this one thing to my Claude-Obsidian setup, and my
   wikilinks finally stopped breaking"](https://www.xda-developers.com/added-one-thing-to-claude-obsidian-setup-and-wikilinks-stopped-breaking/)
   (instruction-file safety rule = only link existing); [Obsidian Help — Settings](https://obsidian.md/help/settings).
   • Pros: zero dangling by construction; reuses wiki-cross-linker promotion seam; minimal new
   machinery. • Cons: loses the "intended link" visual signal; conflicts with "≥1 wikilink
   required". **← chosen.**
2. **Stub auto-creation** (build a placeholder page per link target) — JA "Note Auto Creator"
   philosophy ([blog.handlena.me](https://blog.handlena.me/entry/2025/05/obsidian-quick-create-uid-note-link/)).
   • Pros: links always resolve. • Cons: **this is the automated version of the click-to-create
   workflow the user rejects**; floods the vault with low-quality stubs. **← rejected.**
3. **Forward-linking as a feature** — JA Zettelkasten 先行リンク is *deliberate*
   ([LIFEWORK Blog](https://lifework-blog.com/obsidian-internal-links-guide/)). • This is the
   exact divergence: EN auto-gen says prevent; JA manual-Zettelkasten says embrace. The user's
   stated preference resolves it toward EN-prevent. **← rejected on user preference.**

My take: Recommend #1 (inventory-gated). It matches the user's preference and reuses the
existing cross-linker promotion seam. Conditional reversal: if the user later wants a connected
graph with placeholders, #2 (auto-stub) becomes preferable — but that contradicts the current ask.

## What Becomes Obsolete

(Axis 5) `wiki-ingest`'s "add new wikilinks if discovered" free-invention (`SKILL.md:190`) and
the "≥1 **wikilink** required" Connections rule (`page-format.md:201`, `SKILL.md:345`) become
obsolete — replaced by inventory-gated linking + plain-text candidates. The
`research-note-format.md:69` `[[new-concept]]` form becomes obsolete (→ non-link). All edits
should land in the same change so no skill keeps emitting the old dangling-forcing guidance.

## Open Questions

1. ~~Enforcement strength for L1~~ **RESOLVED (user, 2026-06-04): instruction + enforced
   write-time inventory grep-gate** in `wiki-ingest` (mirror the backtick gate at
   `SKILL.md:200-203` — advisory self-check + enforced grep that downgrades unresolved links to
   plain text). L2 (`obsidian-markdown`) and L4 (`wiki-auto-research`) stay instruction-only —
   no pipeline to gate.
2. **How does L1 build the "existing notes" inventory at authoring time** — reuse wiki-lint
   L07's filename-inventory approach (`wiki/{cat}/*.md` basenames + aliases), or a broader
   vault glob? wiki-ingest already scans the vault (`scripts/scan-vault.sh`); confirm reuse.
3. **L2 obsidian-markdown existence check mechanism** — it's ad-hoc authoring with no pipeline;
   the rule is a behavioral guardrail (Glob/search before emitting). Confirm phrasing keeps it
   actionable without a script.
