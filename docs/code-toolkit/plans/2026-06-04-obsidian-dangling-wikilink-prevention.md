# Plan: Obsidian dangling-wikilink prevention (authoring-time)

Source brief: docs/code-toolkit/specs/2026-06-04-obsidian-dangling-wikilink-prevention.md
Total tasks: 6   (width is fine — 3 independent leaves)
Critical-path depth: 3 (≤5)   ← longest chain T1→T2→T3
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-04, 14/14, 3×🟢 nits — citation off-by-one fixed below)

Shared canonical wording (quote verbatim in any task that emits it, to prevent drift):
> Only emit `[[Target]]` when `Target` already resolves to an existing note in the vault
> (bare-basename match, including frontmatter aliases). Otherwise write the term as plain
> bold text (`**Target**`) with its relationship reason. Never emit a wikilink solely to
> create a placeholder. **Exempt:** same-note `[[#Heading]]` / `[[#^block]]` links, and
> reference-page `## Source` cross-layer links — these always resolve.

---

## Task 1 — wikilink-target resolver script (core)
- Description: Create `check-wikilink-targets.py` — a pure-logic CLI/importable function that,
  given a markdown page path + vault root + exclude-dir list, builds the vault note inventory
  (all `*.md` basenames minus `.md`, plus frontmatter `aliases`) and returns the list of
  `[[Target]]` wikilinks in the page whose `Target` does NOT resolve against that inventory.
  Core resolution only: existing→resolved, missing→flagged, alias→resolved, `|alias`/`#heading`
  suffix stripped to base before matching. Mirror `wiki-lint` L07 inventory logic
  (`lint-checks.md:58-66`).
- Module: obsidian/skills/wiki-ingest/scripts
- Files touched: obsidian/skills/wiki-ingest/scripts/check-wikilink-targets.py, obsidian/skills/wiki-ingest/scripts/test_check_wikilink_targets.py
- Context paths:
  - obsidian/skills/wiki-lint/references/lint-checks.md  (L07 inventory algorithm to mirror)
  - obsidian/skills/wiki-ingest/scripts/select-batch.py  (existing script style/conventions)
- Acceptance:
  - RED: test_check_wikilink_targets.py::test_core_resolution — fixtures: a temp vault with
    `Existing.md` (+ alias `Alt`) and a page linking `[[Existing]]`, `[[Missing]]`,
    `[[Existing|disp]]`, `[[Alt]]` → expects only `Missing` flagged.
  - GREEN: `python -m pytest obsidian/skills/wiki-ingest/scripts/test_check_wikilink_targets.py -k core_resolution` passes.
- External surfaces: none (stdlib only — pathlib, re; no third-party).
- Dependencies: none
- Independent: false
- Brief item covered: "add an enforced write-time inventory grep-gate ... downgrades unresolved
  links to plain text" (OQ1 RESOLVED) + Smallest End State L1.

## Task 2 — resolver exemptions + code-span / path-prefix handling
- Description: Extend `check-wikilink-targets.py` to NOT flag the exempt link shapes: same-note
  `[[#Heading]]` and `[[#^block]]` (empty base → skip), wikilinks inside a `## Source` body
  section, and wikilinks inside fenced ``` ``` ``` or inline `` ` `` code spans. Path-prefixed
  forms (`[[dir/Name]]`) resolve on the trailing basename (consistent with Obsidian). These are
  the false-positive guards from the brief's Data/Boundary evidence.
- Module: obsidian/skills/wiki-ingest/scripts
- Files touched: obsidian/skills/wiki-ingest/scripts/check-wikilink-targets.py, obsidian/skills/wiki-ingest/scripts/test_check_wikilink_targets.py
- Context paths:
  - obsidian/skills/wiki-ingest/references/page-format.md  (§Source section + wikilink resolution rules)
  - obsidian/skills/wiki-lint/references/lint-checks.md  (L07 `## Source` exemption, line 66)
- Acceptance:
  - RED: test_check_wikilink_targets.py::test_exemptions — a page with `[[#八、結論]]`,
    a `## Source\n[[some-source-basename]]`, a fenced block containing `[[NotALink]]`, and
    `[[sub/Existing]]` → expects ZERO flagged (all exempt or resolved).
  - GREEN: `python -m pytest obsidian/skills/wiki-ingest/scripts/test_check_wikilink_targets.py` passes (both core + exemptions).
- External surfaces: none (stdlib only).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Exempt: same-note `[[#Heading]]` ... and reference-page `## Source`
  cross-layer links" + Current State Evidence Data/Boundary sub-bullets.

## Task 3 — wire enforced gate + inventory-gated wording into wiki-ingest/SKILL.md
- Description: In `wiki-ingest/SKILL.md`: (a) add an enforced-gate block in STEP 4c that runs
  `scripts/check-wikilink-targets.py` against each just-written page and forbids advancing while
  any unresolved target remains ("downgrade unresolved `[[X]]` to plain `**X**` + reason, re-run
  until empty") — mirror the existing backtick grep-gate prose at `SKILL.md:200-203`; (b) change
  `:190` "`## Connections` — add new wikilinks if discovered" to the inventory-gated wording
  (only link existing; else plain-text candidate for wiki-cross-linker to promote); (c) change
  the checklist line `:345` "At least 1 `[[wikilink]]` in `## Connections`" → "At least 1
  connection (link if the page exists; else plain-text candidate + reason)".
- Module: obsidian/skills/wiki-ingest/SKILL.md
- Files touched: obsidian/skills/wiki-ingest/SKILL.md
- Context paths:
  - obsidian/skills/wiki-ingest/SKILL.md  (lines 185-205, 335, 345)
  - obsidian/skills/wiki-cross-linker/SKILL.md  (promotion seam — line 8, 127)
- Acceptance:
  - RED: `grep -n 'add new wikilinks if discovered' obsidian/skills/wiki-ingest/SKILL.md`
    returns the old line AND `grep -n 'check-wikilink-targets' obsidian/skills/wiki-ingest/SKILL.md`
    is empty (gate not yet wired) — both conditions currently true.
  - GREEN: old phrase gone; `check-wikilink-targets.py` gate block present with "do not advance"
    enforcement; checklist line reworded; `.claude/hooks/validate-skill-folder-structure.sh`
    passes on the edited skill.
- External surfaces: none (prose; references the Task 1/2 script by relative path).
- Dependencies: Task 2 completes first  (gate block invokes the finished script)
- Independent: false
- Brief item covered: Smallest End State L1 ("`## Connections` links only inventory-resolved
  targets ... Relax ... from '≥1 wikilink required' to '≥1 connection'") + What Becomes Obsolete.

## Task 4 — relax Connections spec in wiki-ingest/references/page-format.md
- Description: In `page-format.md` §Connections (`:198-200`), change "At least 1 `[[wikilink]]`
  required" to "At least 1 connection — `[[link]]` if the related page already exists, else a
  plain-text candidate (`**Term**`) with its one-line reason; wiki-cross-linker promotes it once
  the page exists". Keep "Link reason is mandatory". Add a one-line pointer to the same-note-
  heading / `## Source` exemption (already specified in §Wikilink resolution). Use the shared
  canonical wording from the plan header so it stays coherent with Task 3's checklist line.
- Module: obsidian/skills/wiki-ingest/references/page-format.md
- Files touched: obsidian/skills/wiki-ingest/references/page-format.md
- Context paths:
  - obsidian/skills/wiki-ingest/references/page-format.md  (lines 198-201, §Wikilink resolution 254+)
- Acceptance:
  - RED: `grep -n 'At least 1 \[\[wikilink\]\] required' obsidian/skills/wiki-ingest/references/page-format.md`
    returns the old line.
  - GREEN: old line replaced with the "≥1 connection (link if exists else plain-text)" wording;
    "Link reason is mandatory" retained; exemption pointer present.
- External surfaces: none.
- Dependencies: none  (disjoint file from Task 3; coherence enforced by shared canonical wording)
- Independent: true
- Brief item covered: What Becomes Obsolete ("'≥1 wikilink required' Connections rule ... becomes
  obsolete — replaced by inventory-gated linking + plain-text candidates").

## Task 5 — add authoring guardrail to obsidian-markdown (L2)
- Description: In `obsidian-markdown/SKILL.md` §Internal Links (Wikilinks) (`:17-25`), add the
  authoring guardrail (the plan-header canonical wording): only emit `[[Target]]` for a note that
  already exists in the vault; otherwise write `**Target**` plain text. Call out the same-note
  `[[#Heading]]` / TOC exemption explicitly (those always resolve — the `:9-12,24` examples must
  stay valid). This is a behavioral rule for ad-hoc note authoring (Glob/search before emitting),
  not a scripted gate.
- Module: obsidian/skills/obsidian-markdown/SKILL.md
- Files touched: obsidian/skills/obsidian-markdown/SKILL.md
- Context paths:
  - obsidian/skills/obsidian-markdown/SKILL.md  (lines 8, 17-25; TOC 4-15)
- Acceptance:
  - RED: `grep -ni 'only.*exist\|already exist' obsidian/skills/obsidian-markdown/SKILL.md`
    returns nothing in the Internal Links region (no existence rule yet).
  - GREEN: guardrail paragraph present in §Internal Links with the link-only-existing rule +
    same-note-heading exemption; `validate-skill-folder-structure.sh` passes; TOC `[[#Heading]]`
    examples unchanged.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State L2 ("add the rule as an authoring guardrail in §Internal
  Links, with the same-note-heading exemption called out explicitly").

## Task 6 — reframe future-page recommendation in wiki-auto-research (L4)
- Description: In `wiki-auto-research/references/research-note-format.md`, change `:69`
  "`(Optional) Create new page: [[new-concept]]`" to a NON-link form (e.g. inline code
  `` `new-concept` `` or plain text), so the machine-read creation instruction no longer leaks a
  dangling `[[…]]` into `research/`. Add a one-line note that `source_pages` (`:29-31`) stay as
  wikilinks (those pages exist by construction — they surfaced the questions). Confirm the
  `:125` consumption contract (wiki-ingest reads the block) still parses the non-link form.
- Module: obsidian/skills/wiki-auto-research/references/research-note-format.md
- Files touched: obsidian/skills/wiki-auto-research/references/research-note-format.md
- Context paths:
  - obsidian/skills/wiki-auto-research/references/research-note-format.md  (lines 29-31, 61-69, 104-125)
- Acceptance:
  - RED: `grep -n 'Create new page: \[\[new-concept\]\]' obsidian/skills/wiki-auto-research/references/research-note-format.md`
    returns the old line.
  - GREEN: `[[new-concept]]` replaced with a non-link form; `source_pages` wikilinks retained
    with the "these exist" note; consumption contract note added.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State L4 ("`research-note-format.md:69` reframes the 'create
  new page' recommendation to a non-link form ... `source_pages` ... unchanged").

---

## Notes
- Depth = 3 (T1→T2→T3). T4, T5, T6 are independent leaves (disjoint files, no execution-order
  dependency). T4 shares canonical wording with T3's checklist line but is execution-independent;
  drift is prevented by quoting the plan-header wording, not by sequencing.
- L3 detection / 899-link backfill are out of scope per the brief (user-declined).
- Tasks 3–6 are prose edits with grep-diagnostic RED/GREEN (tdd-iron-law §When NOT to Use:
  doc/prose); Tasks 1–2 carry the real pytest RED→GREEN that anchors the enforced gate.
