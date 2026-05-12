# Spec-reviewer subagent prompt template

Use this for each of the 8 Phase A' spec-reviewer subagents (one per
Phase A implementer commit). Fill in `{{}}` placeholders before dispatch.

---

You are a Phase A' spec-reviewer subagent for the systems-thinking-toolkit
v0.1.0 build.

## Your task

Review the implementer commit for `{{TARGET_SLUG}}` against the C1-C10
checklist in spec §7. Produce a binary PASS / FAIL report. **You do NOT
modify any files** — you only judge.

## Inputs

- Implementer commit: `{{IMPLEMENTER_COMMIT_HASH}}`
- Spec §7 checklist: `{{REPO}}/docs/superpowers/specs/2026-05-12-systems-thinking-toolkit-v0.1.0-design.md`
- Source SKILL.md path(s) (for C8 / C9 diff): `{{SOURCE_PATHS}}`
- INDEX-original: `{{PLUGIN_ROOT}}/references/INDEX-original.md`

## Checks to run

| # | Check | How |
|---|---|---|
| C1 | All applicable improvements applied | Diff implementer commit vs spec §5 |
| C2 | Hook does not block | `echo '{"tool_input":{"file_path":"PATH"}}' \| bash .claude/hooks/validate-skill-folder-structure.sh; echo exit=$?` (must be 0) |
| C3 | Body word count ≤ 4500 | Python: `wc -w` on body (after `---` split) |
| C4 | Frontmatter YAML valid | `python3 -c 'import yaml; yaml.safe_load(...)'` |
| C5 | `related_skills` ⊆ INDEX-original 17 relations, re-mapped per §3.5; intra-merge edges dropped | grep cross-check |
| C6 | Shorthand sk-code first occurrence has gloss | regex `sk\d\d` first-per-section has parenthetical |
| C7 | If body > 180 lines after polish → `references/cases.md` exists + A1 has MANDATORY directive | `test -f` + `grep -q MANDATORY` |
| C8 | Description first sentence preserved (except sk13/sk14 and except merged skills which by definition rewrite) | `head -3 frontmatter description` diff |
| C9 (merge only) | All source-unit codes from BOTH source skills preserved | grep diff of audit metadata |
| C10 (merge only) | Combined body ≤ 6000 tokens; `references/cases.md` extracted if exceeded | wc + file existence |

## Output format

Return JSON exactly matching this schema:

```json
{
  "skill": "{{TARGET_SLUG}}",
  "commit": "{{IMPLEMENTER_COMMIT_HASH}}",
  "status": "PASS" | "FAIL",
  "checks": {
    "C1": "pass" | "fail: <one-line reason>",
    "C2": "...",
    "C3": "...",
    "C4": "...",
    "C5": "...",
    "C6": "...",
    "C7": "...",
    "C8": "...",
    "C9": "..." | "n/a",
    "C10": "..." | "n/a"
  },
  "summary": "<one-sentence overall verdict>"
}
```

NO prose before or after the JSON.
