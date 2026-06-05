# Dogfood Report — wiki-ingest gate + obsidian-markdown guardrail

- Date: 2026-06-05
- Targets: `obsidian/skills/wiki-ingest` (new STEP-4c unresolved-wikilink gate + Connections rule), `obsidian/skills/obsidian-markdown` (new authoring guardrail)
- Scope: behavioral dogfood of the dangling-wikilink-prevention change (branch `fix/obsidian-dangling-wikilink-prevention`)
- Probes run: B (executor + behavioral follow-through) + C (blind cold-reader). **Probe A (triggering) intentionally skipped** — the change touched no `description:` field, so a trigger regression is impossible by construction; the high-risk untested axis is "does an agent FOLLOW the new rule," not "does it trigger."
- Fixture: minimal real vault `/tmp/dogfood-wi.<rand>/vault` — one existing wiki page (`exploration-exploitation`), one source note mentioning it + 3 non-existent concepts (Thompson Sampling, Bayesian optimization, regret bounds).

## Severity summary

| Severity | Count | Findings |
|---|---|---|
| 🔴 High | 1 | F1 (obsidian-markdown Complete Example violates its own new rule) |
| 🟡 Medium | 3 | F2 (`python` vs `python3`), F3 (Workflow Step 4 omits existence precondition), F4 (no worked Connections line in SKILL.md) |
| 🟢 Low | 1 | F5 (alias-match mechanism under-specified) |
| ✅ Behavioral PASS | 2 | wiki-ingest gate followed + caught a real bug end-to-end; obsidian-markdown guardrail followed incl. the no-vault-access fallback |

## Behavioral results (Probe B) — the core validation

**B1 — wiki-ingest executor (informed, ran the skill end-to-end on the fixture): PASS.**
A blind executor given the full SKILL.md + bundle, told "user has NOT installed this — execute as invoked," generated the wiki page and:
- Linked `[[exploration-exploitation]]` (resolves) and wrote `**Thompson Sampling**` / `**Bayesian optimization**` / `**regret bounds**` as plain bold (no page) — exactly the inventory-gated rule.
- **Ran the gate** (`python3 scripts/check-wikilink-targets.py <page> <wiki-root>`) as STEP 4c instructs.
- The gate **caught a real bug end-to-end**: the executor's first `## Source` link pointed at the source-note basename (spaces, in excluded `inbox/`) instead of the reference page → gate exit 1 → executor fixed it → re-ran to exit 0. The enforced gate did its job on an agent it had never coached.

**B2 — obsidian-markdown executor (informed, authored a note with unverifiable references): PASS.**
Asked to write a note referencing "Markov Decision Process" + "Q-Learning" with NO vault access:
- Wrote BOTH as `**plain bold**`, explicitly citing SKILL.md:78 "If the vault is not accessible in your current context, default to the plain-text `**Target**` form rather than guessing."
- Wrote the TOC `[[#Overview]]` / `[[#Key Ideas]]` as wikilinks, citing the same-note exemption (SKILL.md:80).
- The orchestrator-added no-vault-access fallback clause (T5 review fix) is load-bearing and was used verbatim.

## Findings (Probe C — blind cold-reader)

### F1 🔴 High — obsidian-markdown's Complete Example violates the rule it teaches
- Category: Convention-violation / Output-quality (worked-example-contradicts-rule)
- pass: blind (cold-reader, zero context)
- Location: `obsidian/skills/obsidian-markdown/SKILL.md:196` (Complete Example)
- Probe: cold-reader asked "does the rule contradict other guidance?"
- Actual: line 196 `This project aims to [[improve workflow]] using modern techniques.` — `[[improve workflow]]` is a wikilink to a non-existent placeholder note, **exactly what the new rule (line 76) forbids**. A reader who reproduces the canonical example immediately breaks the rule.
- Why static review missed it: the example is ~120 lines from the rule; per-file review read the rule region, not the example region. Same class as the repo's own worked-example-is-prescriptive lesson — a worked example is read as the output to reproduce.
- Suggested fix: change `[[improve workflow]]` to plain `**improving the workflow**`, OR to a heading link, OR add an inline note that example links assume their targets exist. (Lines 204 `[[Algorithm Notes#Sorting]]` / 208 `[[Meeting Notes 2024-01-10#Decisions]]` read more plausibly as real notes — lower exposure, but consider a one-line "examples assume these notes exist" caveat.)

### F2 🟡 Medium — gate command uses `python`, rest of skill uses `python3`
- Category: Convention-violation (portability)
- pass: blind (cold-reader) — also a latent runtime bug
- Location: `obsidian/skills/wiki-ingest/SKILL.md:207` (gate block) vs `:121` (`python3 ... select-batch.py`)
- Actual: the new gate block says `python scripts/check-wikilink-targets.py ...`; STEP 3 says `python3`. On stock macOS / many Linux distros `python` is unmapped or Python 2 → the gate fails to run, silently defeating the enforced check.
- Why static review missed it: reviewers verified the CLI signature against the script, not the interpreter token against sibling commands in the same file.
- Suggested fix: change `python` → `python3` at SKILL.md:207 (and the comment line if it repeats it) for consistency with `:121`.

### F3 🟡 Medium — Workflow Step 4 + the wikilink-vs-markdown blockquote omit the existence precondition
- Category: Workflow-drift / Cold-start
- pass: blind (cold-reader)
- Location: `obsidian/skills/obsidian-markdown/SKILL.md:15` (Workflow step 4) + `:20` (blockquote)
- Actual: both frame the link choice as purely internal-vs-external (`[[wikilinks]]` for vault notes, `[text](url)` for URLs) with NO mention of "must already exist." A reader following the Workflow top-to-bottom emits wikilinks freely and never reaches the new §Internal Links rule. Two co-located policies disagree.
- Suggested fix: add a half-sentence + cross-pointer at Step 4 / line 20: "...for notes that already exist — see §Internal Links for the existence rule."

### F4 🟡 Medium — no worked example of a finished/downgraded `## Connections` line in wiki-ingest SKILL.md
- Category: Progressive-disclosure / Cold-start
- pass: blind (cold-reader)
- Location: `obsidian/skills/wiki-ingest/SKILL.md` §Connections region (190, 205-213)
- Actual: the rule describes the downgraded form in prose (`**Target**` + reason) but shows no literal line; the cold-reader could not tell whether it is `- **X** — reason` vs `- **X**: reason`, nor whether resolved links keep a reason. Mitigation: `page-format.md` §Connections DOES show `- [[OtherWikiPage]] — one-line reason`; the B1 executor inferred the em-dash form correctly, so real-world impact is low — but the SKILL.md region is self-incomplete.
- Suggested fix: add a 2-line worked example showing one resolved `- [[X]] — reason` and one downgraded `- **Y** — reason` line, or point to page-format.md §Connections by name.

### F5 🟢 Low — obsidian-markdown "Glob/search ... including frontmatter aliases" under-specifies alias matching
- Category: Cold-start
- pass: blind (cold-reader)
- Location: `obsidian/skills/obsidian-markdown/SKILL.md:78`
- Actual: `Glob` matches filenames, not YAML `aliases:` inside files; the rule says to honor aliases but not how to find them, so a naive check yields false "doesn't exist." Softened by the explicit "behavioral check, not a scripted gate" disclaimer.
- Suggested fix: optional — "(alias match needs a content search of frontmatter `aliases:`, not just a filename glob)".

## Raw outputs appendix

- **B1 (wiki-ingest executor)** generated `wiki/concepts/multi-armed-bandits.md` + `wiki/references/2026-06-05-multi-armed-bandit-notes.md`; Connections section verbatim: `- [[exploration-exploitation]] — ...` + `- **Thompson Sampling** — ...` + `- **Bayesian optimization** — ...` + `- **regret bounds** — ...`. Gate run 1 → exit 1 (caught the Source-link bug); after fix → exit 0.
- **B2 (obsidian-markdown executor)** wrote "Reinforcement Learning Basics" with `**Markov Decision Process**` + `**Q-Learning**` (plain, cited line 78) and `[[#Overview]]`/`[[#Key Ideas]]` (TOC, cited line 80).
- **C1 (wiki-ingest cold-reader)** flagged F2 (`python`/`python3`) + F4 (no worked Connections line) + jargon (inventory/cross-layer/bare-basename).
- **C2 (obsidian-markdown cold-reader)** flagged F1 (Complete Example `[[improve workflow]]` violates rule) + F3 (Workflow Step 4 omits existence precondition) + F5 (alias matching).

## Verdict

**Behavior: validated.** Both new rules were followed faithfully by blind executors with no coaching, and the wiki-ingest gate caught a real dangling bug end-to-end. The implementation works.
**Documentation: 1 High + 3 Medium clarity findings**, the sharpest being F1 (the obsidian-markdown Complete Example contradicts its own new rule — a repeat of the repo's worked-example-is-prescriptive lesson). None break behavior; all are cheap edits. This report is advisory — the main agent applies the fixes the user approves.
