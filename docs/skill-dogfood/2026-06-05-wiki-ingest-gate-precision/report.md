# Dogfood Report (Round 2) — wiki-ingest gate PRECISION / false-positives

- Date: 2026-06-05
- Target: `obsidian/skills/wiki-ingest` — the STEP-4c unresolved-wikilink gate + `scripts/check-wikilink-targets.py`
- Axis (predict-then-execute): **gate precision / false-positives.** Round 1 proved the gate CATCHES real danglers; it never tested whether the gate AVOIDS false alarms on legitimate links. A false-positive gate is arguably worse than a miss — it corrupts valid content and erodes trust (inducing bypass).
- Probes: script-level adversarial fixture (Bash) + a blind executor that followed the gate instruction literally end-to-end.

## Prediction (written before running)

The gate might false-flag: (a) embedded attachments `![[image.png]]`, (b) alias-only targets, (c) CJK page names, (d) `## Source` cross-layer links, (e) path-prefixed links. Top risk: **embeds** — the extractor regex `\[\[([^\[\]]+?)\]\]` ignores the `!` prefix, and `build_inventory` indexes only `*.md`, so a real attachment can never resolve.

## Result — precision is high EXCEPT embeds

Ran the gate on one page exercising all cases (vault with real targets: an existing concept page + its alias, a CJK page, a real `_attachments/architecture.png`, a source note):

| Link in page | Gate result | Correct? |
|---|---|---|
| `[[exploration-exploitation]]` (exists) | not flagged | ✅ |
| `[[explore-exploit tradeoff]]` (alias) | not flagged | ✅ alias resolution works end-to-end |
| `[[中文概念]]` (CJK page) | not flagged | ✅ CJK works |
| `[[concepts/exploration-exploitation]]` (path-prefix) | not flagged | ✅ |
| `[[#Body]]` (same-note) | not flagged | ✅ exempt |
| `![[exploration-exploitation]]` (embed of existing note) | not flagged | ✅ (incidental — target is .md) |
| `## Source` → `[[2026-06-05 some-source]]` (cross-layer) | not flagged | ✅ exempt |
| `[[Genuinely Missing Page]]` (real dangler) | flagged | ✅ |
| **`![[architecture.png]]` (embed real attachment)** | **flagged** | ❌ **FALSE POSITIVE** |

## G1 🔴 High — gate false-flags attachment embeds, and the downgrade rule then CORRUPTS them

- Category: Output-quality (false-positive → content corruption) / Gate-bypass-inducing
- pass: informed (script execution) + behavioral executor
- Location: `obsidian/skills/wiki-ingest/scripts/check-wikilink-targets.py:53` (`_WIKILINK_RE` ignores the `!` embed prefix) + `:~102-130` (`build_inventory` indexes only `*.md`, so attachments never resolve); compounded by `obsidian/skills/wiki-ingest/SKILL.md:213` (downgrade rule has no embed carve-out).
- Probe: blind executor told to run the STEP-4c gate and apply its instruction literally.
- Expected: `![[architecture.png]]` (a real attachment embed) is left untouched.
- Actual: gate reported `architecture.png` → executor followed SKILL.md:213 ("for each unresolved `[[X]]`, downgrade to `**X**`") → edited `![[architecture.png]]` into `!**architecture.png**`.
- Transcript evidence (executor, verbatim): *"Before: `An embedded image: ![[architecture.png]]` … After: `An embedded image: !**architecture.png**` … no longer an embed. The `[[...]]` is gone, so the leading `!` is now just a literal exclamation mark … the image no longer appears on the page."*
- Root cause: the gate treats embed targets identically to note-link targets. (1) `_WIKILINK_RE` matches the `[[...]]` inside `![[...]]`, ignoring the `!`. (2) The inventory is `.md`-only, so any image/PDF/audio attachment is unconditionally "unresolved." (3) The SKILL.md downgrade rule recognizes only `[[X]]`, so applied to an embed it strips the brackets and orphans the `!`, silently destroying the embed.
- Why static / Round-1 review missed it: Round 1 tested the happy path (link existing, downgrade missing) on text-only Connections; no probe used an embed. Per-task review checked the exemptions it knew about (same-note heading, `## Source`, code span) — embeds were never on the list. The bug only surfaces on the **precision axis** with an attachment embed present.
- Blast radius: any wiki page that embeds an attachment (`![[diagram.png]]`, `![[spec.pdf]]`, `![[clip.mp3]]`). Embeds of existing `.md` notes survive incidentally (their target resolves), but every attachment embed is flagged then mangled. Because the gate is "enforced" (do not advance), a faithful agent WILL corrupt it.
- Suggested fix (code + test + 1-line doc):
  1. `check-wikilink-targets.py`: in the extractor, **drop matches preceded by `!`** (embeds are out of scope for the dangling-NOTE-link gate). Cleanest: change the scan to skip `![[...]]`, e.g. match `(?<!!)\[\[...\]\]` or strip embeds in `_strip_exempt_regions`. Embed integrity (broken image/PDF) is a separate concern, not this gate's job.
  2. Add a test: `![[image.png]]` and `![[existing-note]]` are NOT flagged (regression pin).
  3. `SKILL.md:213`: add embeds to the exemption clause ("...same-note `[[#Heading]]`, `## Source` links, code-span wikilinks, **and `![[…]]` embeds** are already exempt") so the doc matches the script.

## Verdict

The gate is **precise on everything except attachment embeds** — alias, CJK, path-prefix, same-note, and `## Source` cross-layer links all correctly pass (strong true-negative rate). The one false-positive class (embedded attachments) is **High** because the enforced downgrade rule turns it into silent content corruption (a working image embed becomes dead bold text), proven end-to-end by a blind executor. Fix = exempt `![[…]]` embeds in the script + a regression test + a one-line SKILL.md exemption note. Advisory — main agent applies on user approval.
